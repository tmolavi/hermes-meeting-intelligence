"""
Persistent SQLite Meeting Memory Store.

Stores complete MeetingRecord models and maintains relational tables and
indexes for decisions, action items, entities, topics, and cross-meeting links.
"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from hermes_meeting_intelligence.models.schema import (
    MeetingRecord,
    MeetingRelationship,
    OwnerCorrection,
    RelationshipType,
)


class MeetingMemoryStore:
    """Manages long-term meeting memory in a zero-external-dependency SQLite database."""

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = os.path.expanduser(db_path) if db_path != ":memory:" else db_path
        self._mem_conn: Optional[sqlite3.Connection] = None
        if self.db_path == ":memory:":
            self._mem_conn = sqlite3.connect(":memory:")
            self._mem_conn.row_factory = sqlite3.Row
        else:
            os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        if self._mem_conn is not None:
            return self._mem_conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS meetings (
                    meeting_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    language TEXT,
                    transcript TEXT,
                    raw_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS decisions (
                    decision_id TEXT PRIMARY KEY,
                    meeting_id TEXT NOT NULL,
                    description TEXT NOT NULL,
                    decided_by TEXT,
                    timestamp_offset REAL,
                    evidence_quote TEXT,
                    FOREIGN KEY (meeting_id) REFERENCES meetings(meeting_id) ON DELETE CASCADE
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS action_items (
                    action_id TEXT PRIMARY KEY,
                    meeting_id TEXT NOT NULL,
                    description TEXT NOT NULL,
                    assignee TEXT,
                    due_date TEXT,
                    status TEXT NOT NULL,
                    source_quote TEXT,
                    FOREIGN KEY (meeting_id) REFERENCES meetings(meeting_id) ON DELETE CASCADE
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS topics (
                    topic_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    meeting_id TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    FOREIGN KEY (meeting_id) REFERENCES meetings(meeting_id) ON DELETE CASCADE
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entities (
                    entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    meeting_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    mentions_count INTEGER DEFAULT 1,
                    FOREIGN KEY (meeting_id) REFERENCES meetings(meeting_id) ON DELETE CASCADE
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS meeting_relationships (
                    rel_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_meeting_id TEXT NOT NULL,
                    target_meeting_id TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (source_meeting_id) REFERENCES meetings(meeting_id) ON DELETE CASCADE
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS owner_corrections (
                    correction_id TEXT PRIMARY KEY,
                    meeting_id TEXT NOT NULL,
                    target_field TEXT NOT NULL,
                    original_value TEXT NOT NULL,
                    corrected_value TEXT NOT NULL,
                    corrected_by TEXT NOT NULL,
                    corrected_at TEXT NOT NULL,
                    reason TEXT,
                    FOREIGN KEY (meeting_id) REFERENCES meetings(meeting_id) ON DELETE CASCADE
                )
            """)
            conn.commit()

    def save_meeting(self, record: MeetingRecord) -> str:
        """Persists a MeetingRecord into the SQLite database with full index population."""
        record.generate_full_transcript_if_empty()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Upsert into meetings
            cursor.execute(
                """
                INSERT OR REPLACE INTO meetings (
                    meeting_id, title, started_at, ended_at, language, transcript, raw_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    record.meeting_id,
                    record.title,
                    record.started_at.isoformat(),
                    record.ended_at.isoformat() if record.ended_at else None,
                    record.language,
                    record.transcript,
                    record.model_dump_json(),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

            # Clear old sub-records if replacing
            cursor.execute("DELETE FROM decisions WHERE meeting_id = ?", (record.meeting_id,))
            cursor.execute("DELETE FROM action_items WHERE meeting_id = ?", (record.meeting_id,))
            cursor.execute("DELETE FROM topics WHERE meeting_id = ?", (record.meeting_id,))
            cursor.execute("DELETE FROM entities WHERE meeting_id = ?", (record.meeting_id,))
            cursor.execute(
                "DELETE FROM meeting_relationships WHERE source_meeting_id = ?",
                (record.meeting_id,),
            )

            for dec in record.decisions:
                cursor.execute(
                    """
                    INSERT INTO decisions (decision_id, meeting_id, description, decided_by, timestamp_offset, evidence_quote)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        dec.decision_id,
                        record.meeting_id,
                        dec.description,
                        dec.decided_by,
                        dec.timestamp_offset,
                        dec.evidence_quote,
                    ),
                )

            for act in record.action_items:
                cursor.execute(
                    """
                    INSERT INTO action_items (action_id, meeting_id, description, assignee, due_date, status, source_quote)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        act.action_id,
                        record.meeting_id,
                        act.description,
                        act.assignee,
                        act.due_date,
                        act.status.value,
                        act.source_quote,
                    ),
                )

            for t in record.topics:
                cursor.execute(
                    "INSERT INTO topics (meeting_id, topic) VALUES (?, ?)", (record.meeting_id, t)
                )

            for ent in record.entities:
                cursor.execute(
                    """
                    INSERT INTO entities (meeting_id, name, entity_type, mentions_count)
                    VALUES (?, ?, ?, ?)
                """,
                    (record.meeting_id, ent.name, ent.entity_type, ent.mentions_count),
                )

            for rel in record.related_meetings:
                cursor.execute(
                    """
                    INSERT INTO meeting_relationships (source_meeting_id, target_meeting_id, relationship_type, description, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        record.meeting_id,
                        rel.target_meeting_id,
                        rel.relationship_type.value,
                        rel.description,
                        rel.created_at.isoformat(),
                    ),
                )

            for corr in record.owner_corrections:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO owner_corrections (
                        correction_id, meeting_id, target_field, original_value, corrected_value, corrected_by, corrected_at, reason
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        corr.correction_id,
                        record.meeting_id,
                        corr.target_field,
                        json.dumps(corr.original_value),
                        json.dumps(corr.corrected_value),
                        corr.corrected_by,
                        corr.corrected_at.isoformat(),
                        corr.reason,
                    ),
                )

            conn.commit()
        return record.meeting_id

    def get_meeting(self, meeting_id: str) -> Optional[MeetingRecord]:
        """Loads a MeetingRecord by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT raw_json FROM meetings WHERE meeting_id = ?", (meeting_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return MeetingRecord.model_validate_json(row["raw_json"])

    def list_meetings(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns summarized metadata of meetings."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT meeting_id, title, started_at, language, length(transcript) as transcript_length
                FROM meetings ORDER BY started_at DESC LIMIT ?
            """,
                (limit,),
            )
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def add_relationship(
        self,
        source_meeting_id: str,
        target_meeting_id: str,
        relationship_type: RelationshipType = RelationshipType.RELATED_TO,
        description: Optional[str] = None,
    ) -> bool:
        """Links two existing meetings."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO meeting_relationships (source_meeting_id, target_meeting_id, relationship_type, description, created_at)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    source_meeting_id,
                    target_meeting_id,
                    relationship_type.value,
                    description,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            conn.commit()

            # Update cached raw_json in meetings table for source meeting
            source = self.get_meeting(source_meeting_id)
            if source:
                source.related_meetings.append(
                    MeetingRelationship(
                        target_meeting_id=target_meeting_id,
                        relationship_type=relationship_type,
                        description=description,
                    )
                )
                self.save_meeting(source)
            return True

    def record_correction(
        self,
        meeting_id: str,
        target_field: str,
        original_value: Any,
        corrected_value: Any,
        corrected_by: str = "owner",
        reason: Optional[str] = None,
    ) -> OwnerCorrection:
        """Applies an owner correction, persisting audit trail and updating the record."""
        correction = OwnerCorrection(
            target_field=target_field,
            original_value=original_value,
            corrected_value=corrected_value,
            corrected_by=corrected_by,
            reason=reason,
        )
        record = self.get_meeting(meeting_id)
        if not record:
            raise ValueError(f"Meeting with ID {meeting_id} not found.")

        record.owner_corrections.append(correction)
        self.save_meeting(record)
        return correction
