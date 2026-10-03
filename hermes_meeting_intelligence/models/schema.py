"""
Core Portable Meeting Record Schema.

Defines standard Pydantic models for structured meeting intelligence,
including speaker segments, decisions, proposals, disagreements, action items,
evidence references, owner corrections, and cross-meeting relationships.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class RelationshipType(str, Enum):
    CONTINUES = "continues"
    SUPERSEDES = "supersedes"
    REFERENCES = "references"
    FOLLOWS_UP = "follows_up"
    BLOCKS = "blocks"
    RELATED_TO = "related_to"


class ActionStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class ProposalStatus(str, Enum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    DEFERRED = "deferred"


class DisagreementStatus(str, Enum):
    UNRESOLVED = "unresolved"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    TABLED = "tabled"


class Participant(BaseModel):
    speaker_id: str = Field(
        ..., description="Unique speaker identifier (e.g., 'speaker_1', 'tmolavi')"
    )
    name: Optional[str] = Field(default=None, description="Known or enrolled human name")
    role: Optional[str] = Field(default=None, description="Role or organization in the meeting")
    email: Optional[str] = Field(default=None, description="Participant contact email if known")


class SpeakerSegment(BaseModel):
    segment_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    start: float = Field(..., ge=0.0, description="Start time in seconds from recording start")
    end: float = Field(..., ge=0.0, description="End time in seconds from recording start")
    speaker_id: str = Field(..., description="Speaker identifier for this segment")
    text: str = Field(..., description="Transcribed spoken text")
    confidence: Optional[float] = Field(
        default=None, ge=0.0, le=1.0, description="ASR confidence score"
    )

    @field_validator("end")
    @classmethod
    def validate_duration(cls, v: float, info: Any) -> float:
        start = info.data.get("start")
        if start is not None and v < start:
            raise ValueError(
                f"Segment end time ({v}s) cannot be earlier than start time ({start}s)"
            )
        return v


class Decision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"dec_{uuid.uuid4().hex[:6]}")
    description: str = Field(..., min_length=3, description="Exact decision reached")
    decided_by: Optional[str] = Field(default=None, description="Participant name or consensus")
    timestamp_offset: Optional[float] = Field(
        default=None, description="Offset seconds in meeting when decided"
    )
    evidence_quote: Optional[str] = Field(
        default=None, description="Direct quote from transcript supporting decision"
    )


class Proposal(BaseModel):
    proposal_id: str = Field(default_factory=lambda: f"prop_{uuid.uuid4().hex[:6]}")
    description: str = Field(..., min_length=3, description="Proposed idea or direction")
    proposed_by: Optional[str] = Field(
        default=None, description="Participant who made the proposal"
    )
    status: ProposalStatus = Field(default=ProposalStatus.PROPOSED)


class Disagreement(BaseModel):
    disagreement_id: str = Field(default_factory=lambda: f"dis_{uuid.uuid4().hex[:6]}")
    topic: str = Field(..., description="Subject matter of disagreement")
    parties: List[str] = Field(
        default_factory=list, description="Participants involved in differing viewpoints"
    )
    points_of_view: List[str] = Field(
        default_factory=list, description="Contrasting perspectives expressed"
    )
    resolution_status: DisagreementStatus = Field(default=DisagreementStatus.UNRESOLVED)
    resolution_notes: Optional[str] = Field(
        default=None, description="How the disagreement was resolved or tabled"
    )


class Question(BaseModel):
    question_id: str = Field(default_factory=lambda: f"q_{uuid.uuid4().hex[:6]}")
    question: str = Field(..., description="The question asked")
    asked_by: Optional[str] = Field(default=None, description="Participant who raised question")
    is_answered: bool = Field(default=False)
    answer: Optional[str] = Field(
        default=None, description="Answer provided during meeting if resolved"
    )


class ActionItem(BaseModel):
    action_id: str = Field(default_factory=lambda: f"act_{uuid.uuid4().hex[:6]}")
    description: str = Field(..., min_length=3, description="Concrete task to be completed")
    assignee: Optional[str] = Field(default=None, description="Assigned participant name or role")
    due_date: Optional[str] = Field(
        default=None, description="Agreed deadline (ISO date or human term)"
    )
    status: ActionStatus = Field(default=ActionStatus.PENDING)
    source_quote: Optional[str] = Field(
        default=None, description="Transcript quotation assigning the task"
    )


class EvidenceReference(BaseModel):
    evidence_id: str = Field(default_factory=lambda: f"ev_{uuid.uuid4().hex[:6]}")
    claim: str = Field(..., description="Fact or assertion made in meeting")
    quote: str = Field(..., description="Verbatim transcript quote")
    segment_id: Optional[str] = Field(default=None, description="Corresponding SpeakerSegment ID")
    speaker_id: Optional[str] = Field(default=None, description="Speaker asserting the claim")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class Entity(BaseModel):
    name: str = Field(
        ..., description="Entity name (e.g. project, product, organization, technology)"
    )
    entity_type: str = Field(
        default="generic", description="e.g., 'project', 'person', 'tool', 'metric'"
    )
    mentions_count: int = Field(default=1, ge=1)


class OwnerCorrection(BaseModel):
    correction_id: str = Field(default_factory=lambda: f"corr_{uuid.uuid4().hex[:6]}")
    target_field: str = Field(..., description="Field corrected (e.g. 'decisions[0].decided_by')")
    original_value: Any = Field(..., description="Previous extracted or observed value")
    corrected_value: Any = Field(..., description="Authoritative user-corrected value")
    corrected_by: str = Field(default="owner", description="Author of correction")
    corrected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reason: Optional[str] = Field(default=None, description="Explanation for correction")


class ProvenanceMetadata(BaseModel):
    pipeline_version: str = Field(default="0.1.0")
    stt_provider: Optional[str] = Field(
        default=None, description="Provider used for speech-to-text"
    )
    stt_model: Optional[str] = Field(
        default=None, description="Model name for STT (e.g. 'whisper-large-v3')"
    )
    extraction_provider: Optional[str] = Field(
        default=None, description="Provider used for intelligence extraction"
    )
    extraction_model: Optional[str] = Field(default=None, description="Model used for extraction")
    processed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    audio_duration_seconds: Optional[float] = Field(default=None, ge=0.0)
    source_hash: Optional[str] = Field(
        default=None, description="SHA-256 hash of source audio or transcript"
    )


class MeetingRelationship(BaseModel):
    target_meeting_id: str = Field(..., description="ID of the related meeting")
    relationship_type: RelationshipType = Field(..., description="Semantic relation")
    description: Optional[str] = Field(
        default=None, description="Context of how meetings are related"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MeetingRecord(BaseModel):
    meeting_id: str = Field(default_factory=lambda: f"mtg_{uuid.uuid4().hex[:8]}")
    title: str = Field(..., min_length=1, description="Descriptive meeting title")
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ended_at: Optional[datetime] = Field(default=None)
    language: str = Field(
        default="en", description="Primary spoken language (e.g., 'en', 'fa', 'tr', 'az', 'ar')"
    )
    participants: List[Participant] = Field(default_factory=list)
    speaker_segments: List[SpeakerSegment] = Field(default_factory=list)
    transcript: str = Field(default="", description="Full contiguous transcript text")
    topics: List[str] = Field(default_factory=list)
    entities: List[Entity] = Field(default_factory=list)
    decisions: List[Decision] = Field(default_factory=list)
    proposals: List[Proposal] = Field(default_factory=list)
    disagreements: List[Disagreement] = Field(default_factory=list)
    questions: List[Question] = Field(default_factory=list)
    action_items: List[ActionItem] = Field(default_factory=list)
    evidence: List[EvidenceReference] = Field(default_factory=list)
    referenced_documents: List[str] = Field(default_factory=list)
    owner_corrections: List[OwnerCorrection] = Field(default_factory=list)
    provenance: ProvenanceMetadata = Field(default_factory=lambda: ProvenanceMetadata())
    related_meetings: List[MeetingRelationship] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def generate_full_transcript_if_empty(self) -> str:
        """Populates transcript field from speaker_segments if transcript is empty."""
        if not self.transcript and self.speaker_segments:
            lines = []
            for seg in self.speaker_segments:
                speaker_tag = seg.speaker_id
                # Check if we have a known participant name
                for p in self.participants:
                    if p.speaker_id == seg.speaker_id and p.name:
                        speaker_tag = p.name
                        break
                lines.append(f"[{speaker_tag}]: {seg.text}")
            self.transcript = "\n".join(lines)
        return self.transcript
