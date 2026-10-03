"""
Meeting Intelligence Extractor Pipeline.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, List, Optional

from hermes_meeting_intelligence.models.schema import (
    ActionItem,
    ActionStatus,
    Decision,
    Disagreement,
    DisagreementStatus,
    Entity,
    MeetingRecord,
    Participant,
    Proposal,
    ProposalStatus,
    ProvenanceMetadata,
    Question,
    SpeakerSegment,
)
from hermes_meeting_intelligence.pipeline.validator import MeetingValidator
from hermes_meeting_intelligence.providers.base import BaseExtractionProvider, BaseSTTProvider
from hermes_meeting_intelligence.providers.router import ProviderRouter


class MeetingPipeline:
    """Orchestrates audio transcription, intelligence extraction, and schema building."""

    def __init__(
        self,
        router: Optional[ProviderRouter] = None,
        stt_provider: Optional[BaseSTTProvider] = None,
        extraction_provider: Optional[BaseExtractionProvider] = None,
    ):
        self.router = router or ProviderRouter()
        self._stt = stt_provider
        self._ext = extraction_provider

    async def process_transcript(
        self,
        transcript_text: str,
        title: str = "Untitled Meeting",
        language: str = "en",
        participants: Optional[List[Participant]] = None,
        speaker_segments: Optional[List[SpeakerSegment]] = None,
    ) -> MeetingRecord:
        """Extracts structured intelligence from a given text transcript."""
        ext_provider = self._ext or self.router.get_extraction_provider()

        raw_intel = await ext_provider.extract_intelligence(
            transcript=transcript_text,
            speaker_segments=speaker_segments,
            meeting_title=title,
            language=language,
        )

        decisions = [
            Decision(
                description=d.get("description", ""),
                decided_by=d.get("decided_by"),
                timestamp_offset=d.get("timestamp_offset"),
                evidence_quote=d.get("evidence_quote"),
            )
            for d in raw_intel.get("decisions", [])
            if d.get("description")
        ]

        proposals = [
            Proposal(
                description=p.get("description", ""),
                proposed_by=p.get("proposed_by"),
                status=ProposalStatus(p.get("status", "proposed")),
            )
            for p in raw_intel.get("proposals", [])
            if p.get("description")
        ]

        disagreements = [
            Disagreement(
                topic=dis.get("topic", "Unspecified topic"),
                parties=dis.get("parties", []),
                points_of_view=dis.get("points_of_view", []),
                resolution_status=DisagreementStatus(dis.get("resolution_status", "unresolved")),
                resolution_notes=dis.get("resolution_notes"),
            )
            for dis in raw_intel.get("disagreements", [])
            if dis.get("topic")
        ]

        questions = [
            Question(
                question=q.get("question", ""),
                asked_by=q.get("asked_by"),
                is_answered=q.get("is_answered", False),
                answer=q.get("answer"),
            )
            for q in raw_intel.get("questions", [])
            if q.get("question")
        ]

        action_items = [
            ActionItem(
                description=a.get("description", ""),
                assignee=a.get("assignee"),
                due_date=a.get("due_date"),
                status=ActionStatus(a.get("status", "pending")),
                source_quote=a.get("source_quote"),
            )
            for a in raw_intel.get("action_items", [])
            if a.get("description")
        ]

        entities = [
            Entity(
                name=e.get("name", ""),
                entity_type=e.get("entity_type", "generic"),
                mentions_count=int(e.get("mentions_count", 1)),
            )
            for e in raw_intel.get("entities", [])
            if e.get("name")
        ]

        topics = raw_intel.get("topics", [])

        source_hash = hashlib.sha256(transcript_text.encode("utf-8")).hexdigest()

        record = MeetingRecord(
            title=title,
            started_at=datetime.now(timezone.utc),
            language=language,
            participants=participants or [],
            speaker_segments=speaker_segments or [],
            transcript=transcript_text,
            topics=topics,
            entities=entities,
            decisions=decisions,
            proposals=proposals,
            disagreements=disagreements,
            questions=questions,
            action_items=action_items,
            provenance=ProvenanceMetadata(
                pipeline_version="0.1.0",
                extraction_provider=ext_provider.name,
                source_hash=source_hash,
            ),
        )

        valid, issues = MeetingValidator.validate_audit_integrity(record)
        if not valid:
            raise ValueError(f"Extracted MeetingRecord failed validation: {issues}")

        return record

    async def process_audio(
        self,
        audio_source: Any,
        title: str = "Audio Meeting",
        language: Optional[str] = None,
        diarize: bool = True,
    ) -> MeetingRecord:
        """Transcribes audio with STT provider and extracts structured intelligence."""
        stt_provider = self._stt or self.router.get_stt_provider()
        segments = await stt_provider.transcribe(audio_source, language=language, diarize=diarize)

        transcript_lines = [f"[{s.speaker_id}]: {s.text}" for s in segments]
        full_transcript = "\n".join(transcript_lines)

        record = await self.process_transcript(
            transcript_text=full_transcript,
            title=title,
            language=language or "en",
            speaker_segments=segments,
        )
        record.provenance.stt_provider = stt_provider.name
        return record
