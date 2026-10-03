"""
Hermes Meeting Intelligence package.

Open-source meeting intelligence skills and tools for Hermes Agent:
speaker-aware meetings, persistent meeting memory, cross-meeting context,
and provider-agnostic real-time AI workflows.
"""

from hermes_meeting_intelligence.memory.retriever import MeetingMemoryRetriever
from hermes_meeting_intelligence.memory.store import MeetingMemoryStore
from hermes_meeting_intelligence.models.schema import (
    ActionItem,
    Decision,
    Disagreement,
    Entity,
    MeetingRecord,
    MeetingRelationship,
    Participant,
    Proposal,
    Question,
    SpeakerSegment,
)
from hermes_meeting_intelligence.pipeline.extractor import MeetingPipeline
from hermes_meeting_intelligence.plugin import register

__version__ = "0.1.0"
__author__ = "Taqi Molavi"

__all__ = [
    "register",
    "MeetingRecord",
    "Participant",
    "SpeakerSegment",
    "Decision",
    "Proposal",
    "Disagreement",
    "Question",
    "ActionItem",
    "Entity",
    "MeetingRelationship",
    "MeetingMemoryStore",
    "MeetingMemoryRetriever",
    "MeetingPipeline",
    "__version__",
    "__author__",
]
