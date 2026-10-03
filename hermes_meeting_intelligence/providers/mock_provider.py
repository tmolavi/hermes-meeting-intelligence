"""
Deterministic Mock Provider for offline testing, CI environments, and zero-cost verification.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from hermes_meeting_intelligence.models.schema import (
    SpeakerSegment,
)
from hermes_meeting_intelligence.providers.base import BaseExtractionProvider, BaseSTTProvider


class MockSTTProvider(BaseSTTProvider):
    """Deterministic offline STT provider that parses structured text or returns fixture segments."""

    def __init__(self, name: str = "mock"):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_available(self) -> bool:
        return True

    async def transcribe(
        self,
        audio_path_or_bytes: Any,
        language: Optional[str] = None,
        diarize: bool = True,
        **kwargs: Any,
    ) -> List[SpeakerSegment]:
        """If audio_path_or_bytes is a string containing transcript text, parse it directly."""
        if isinstance(audio_path_or_bytes, str):
            lines = [
                line.strip() for line in audio_path_or_bytes.strip().split("\n") if line.strip()
            ]
            segments: List[SpeakerSegment] = []
            current_time = 0.0
            for idx, line in enumerate(lines):
                speaker = "speaker_1"
                text = line
                match = re.match(r"^\[?([a-zA-Z0-9_\s]+)\]?:\s*(.*)$", line)
                if match:
                    speaker = match.group(1).strip()
                    text = match.group(2).strip()

                seg = SpeakerSegment(
                    segment_id=f"mock_seg_{idx + 1}",
                    start=current_time,
                    end=current_time + 4.0,
                    speaker_id=speaker,
                    text=text,
                    confidence=0.98,
                )
                segments.append(seg)
                current_time += 4.5
            return segments

        # Return default mock dialogue if binary/dummy input
        return [
            SpeakerSegment(
                segment_id="mock_1",
                start=0.0,
                end=3.5,
                speaker_id="speaker_alice",
                text="We decided to migrate the data layer to SQLite and use vector indexing for memory.",
                confidence=0.99,
            ),
            SpeakerSegment(
                segment_id="mock_2",
                start=4.0,
                end=8.0,
                speaker_id="speaker_bob",
                text="I disagree with pure in-memory caches because persistence across restarts is mandatory.",
                confidence=0.97,
            ),
            SpeakerSegment(
                segment_id="mock_3",
                start=8.5,
                end=12.0,
                speaker_id="speaker_alice",
                text="Bob, can you finish the schema validator and CI workflow by Friday?",
                confidence=0.98,
            ),
        ]


class MockExtractionProvider(BaseExtractionProvider):
    """Heuristic / Rule-based extraction provider for offline testing and deterministic verification."""

    def __init__(self, name: str = "mock"):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_available(self) -> bool:
        return True

    async def extract_intelligence(
        self,
        transcript: str,
        speaker_segments: Optional[List[SpeakerSegment]] = None,
        meeting_title: Optional[str] = None,
        language: str = "en",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Extracts structured fields using pattern matching and keyword heuristics."""
        decisions: List[Dict[str, Any]] = []
        proposals: List[Dict[str, Any]] = []
        disagreements: List[Dict[str, Any]] = []
        questions: List[Dict[str, Any]] = []
        action_items: List[Dict[str, Any]] = []
        evidence: List[Dict[str, Any]] = []
        topics: List[str] = []
        entities: List[Dict[str, Any]] = []

        lines = transcript.split("\n") if transcript else []
        if not lines and speaker_segments:
            lines = [f"[{s.speaker_id}]: {s.text}" for s in speaker_segments]

        # Look for typical decision keywords
        for line in lines:
            lower = line.lower()
            if any(
                k in lower
                for k in [
                    "decided",
                    "agree to",
                    "agreed on",
                    "consensus is",
                    "تصمیم گرفته شد",
                    "قرار شد",
                    "karar verildi",
                ]
            ):
                decisions.append(
                    {
                        "description": line.split(":", 1)[-1].strip()
                        if ":" in line
                        else line.strip(),
                        "evidence_quote": line.strip(),
                    }
                )
            elif any(k in lower for k in ["propose", "suggest", "how about", "پیشنهاد", "önermek"]):
                proposals.append(
                    {
                        "description": line.split(":", 1)[-1].strip()
                        if ":" in line
                        else line.strip(),
                        "status": "proposed",
                    }
                )
            elif any(
                k in lower
                for k in ["disagree", "oppose", "differ", "مخالف", "muhalif", "katılmıyorum"]
            ):
                disagreements.append(
                    {
                        "topic": "Architecture and Design discussion",
                        "points_of_view": [line.strip()],
                        "resolution_status": "unresolved",
                    }
                )
            elif "?" in line or any(
                k in lower for k in ["can you", "could you", "would you", "آیا", "nasıl"]
            ):
                questions.append(
                    {
                        "question": line.split(":", 1)[-1].strip() if ":" in line else line.strip(),
                        "is_answered": False,
                    }
                )

            if any(
                k in lower
                for k in [
                    "action item",
                    "todo",
                    "by friday",
                    "by monday",
                    "will implement",
                    "مسئولیت",
                    "görev",
                ]
            ):
                action_items.append(
                    {
                        "description": line.split(":", 1)[-1].strip()
                        if ":" in line
                        else line.strip(),
                        "status": "pending",
                        "source_quote": line.strip(),
                    }
                )

        # Heuristic entity detection
        tech_keywords = [
            "SQLite",
            "Chroma",
            "Python",
            "Hermes",
            "Whisper",
            "Groq",
            "FastAPI",
            "OpenAI",
        ]
        for kw in tech_keywords:
            if kw.lower() in (transcript or "").lower():
                entities.append({"name": kw, "entity_type": "technology", "mentions_count": 1})
                if kw not in topics:
                    topics.append(kw)

        if not topics:
            topics = ["General Engineering", "Meeting Intelligence"]

        return {
            "decisions": decisions,
            "proposals": proposals,
            "disagreements": disagreements,
            "questions": questions,
            "action_items": action_items,
            "evidence": evidence,
            "topics": topics,
            "entities": entities,
        }
