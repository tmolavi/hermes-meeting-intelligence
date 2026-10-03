"""
Cross-Meeting Context Retriever.

Enables Hermes Agent to query prior decisions, open action items, and relevant
meeting history without blindly loading massive transcripts into context.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from hermes_meeting_intelligence.memory.store import MeetingMemoryStore


class MeetingMemoryRetriever:
    """Retrieves relevant meeting memory and context."""

    def __init__(self, store: MeetingMemoryStore):
        self.store = store

    def search_decisions(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Finds decisions matching search terms."""
        with self.store._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT d.decision_id, d.meeting_id, d.description, d.decided_by, d.evidence_quote, m.title as meeting_title, m.started_at
                FROM decisions d
                JOIN meetings m ON d.meeting_id = m.meeting_id
                WHERE d.description LIKE ? OR d.evidence_quote LIKE ?
                ORDER BY m.started_at DESC LIMIT ?
            """,
                (f"%{query}%", f"%{query}%", limit),
            )
            return [dict(r) for r in cursor.fetchall()]

    def search_open_actions(
        self, assignee: Optional[str] = None, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Finds pending or in-progress action items across all meetings."""
        with self.store._get_connection() as conn:
            cursor = conn.cursor()
            if assignee:
                cursor.execute(
                    """
                    SELECT a.action_id, a.meeting_id, a.description, a.assignee, a.due_date, a.status, m.title as meeting_title
                    FROM action_items a
                    JOIN meetings m ON a.meeting_id = m.meeting_id
                    WHERE a.status IN ('pending', 'in_progress', 'blocked') AND a.assignee LIKE ?
                    ORDER BY a.due_date ASC, m.started_at DESC LIMIT ?
                """,
                    (f"%{assignee}%", limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT a.action_id, a.meeting_id, a.description, a.assignee, a.due_date, a.status, m.title as meeting_title
                    FROM action_items a
                    JOIN meetings m ON a.meeting_id = m.meeting_id
                    WHERE a.status IN ('pending', 'in_progress', 'blocked')
                    ORDER BY a.due_date ASC, m.started_at DESC LIMIT ?
                """,
                    (limit,),
                )
            return [dict(r) for r in cursor.fetchall()]

    def search_topics(self, topic: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Finds meetings discussing a specific topic or entity."""
        with self.store._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT DISTINCT m.meeting_id, m.title, m.started_at, m.language
                FROM meetings m
                LEFT JOIN topics t ON m.meeting_id = t.meeting_id
                LEFT JOIN entities e ON m.meeting_id = e.meeting_id
                WHERE t.topic LIKE ? OR e.name LIKE ? OR m.title LIKE ?
                ORDER BY m.started_at DESC LIMIT ?
            """,
                (f"%{topic}%", f"%{topic}%", f"%{topic}%", limit),
            )
            return [dict(r) for r in cursor.fetchall()]

    def get_related_lineage(self, meeting_id: str) -> Dict[str, Any]:
        """Retrieves direct parents, children, and typed links for a meeting."""
        with self.store._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT target_meeting_id, relationship_type, description, created_at
                FROM meeting_relationships WHERE source_meeting_id = ?
            """,
                (meeting_id,),
            )
            outgoing = [dict(r) for r in cursor.fetchall()]

            cursor.execute(
                """
                SELECT source_meeting_id, relationship_type, description, created_at
                FROM meeting_relationships WHERE target_meeting_id = ?
            """,
                (meeting_id,),
            )
            incoming = [dict(r) for r in cursor.fetchall()]

            meeting = self.store.get_meeting(meeting_id)

            return {
                "meeting_id": meeting_id,
                "title": meeting.title if meeting else None,
                "outgoing_relations": outgoing,
                "incoming_relations": incoming,
            }
