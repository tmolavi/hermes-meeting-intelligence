"""
Abstract Provider Interfaces for Speech-to-Text, Diarization, and Meeting Intelligence Extraction.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from hermes_meeting_intelligence.models.schema import SpeakerSegment


class BaseSTTProvider(ABC):
    """Abstract interface for Speech-to-Text inference."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if the provider is configured with valid credentials or binaries."""
        pass

    @abstractmethod
    async def transcribe(
        self,
        audio_path_or_bytes: Any,
        language: Optional[str] = None,
        diarize: bool = True,
        **kwargs: Any,
    ) -> List[SpeakerSegment]:
        """Transcribes audio and returns a list of SpeakerSegment objects."""
        pass


class BaseDiarizationProvider(ABC):
    """Abstract interface for Speaker Diarization and Voice Biometrics."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    async def diarize(
        self, audio_path_or_bytes: Any, num_speakers: Optional[int] = None, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """Performs speaker diarization returning speaker intervals."""
        pass


class BaseExtractionProvider(ABC):
    """Abstract interface for extracting structured intelligence from transcripts."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    async def extract_intelligence(
        self,
        transcript: str,
        speaker_segments: Optional[List[SpeakerSegment]] = None,
        meeting_title: Optional[str] = None,
        language: str = "en",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Extracts decisions, proposals, disagreements, questions, action items, entities, topics."""
        pass
