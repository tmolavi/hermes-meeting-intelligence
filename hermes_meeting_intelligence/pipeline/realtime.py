"""
Real-time Meeting Audio Buffer & Low-Latency Stream Coordinator.
"""

from __future__ import annotations

from typing import Callable, List, Optional

from hermes_meeting_intelligence.models.schema import SpeakerSegment
from hermes_meeting_intelligence.providers.base import BaseSTTProvider


class RealtimeMeetingStream:
    """Manages chunked streaming audio ingestion and low-latency transcript callback dispatch."""

    def __init__(
        self,
        stt_provider: BaseSTTProvider,
        chunk_duration_seconds: float = 2.0,
        sample_rate: int = 16000,
    ):
        self.stt_provider = stt_provider
        self.chunk_duration_seconds = chunk_duration_seconds
        self.sample_rate = sample_rate
        self.segments: List[SpeakerSegment] = []
        self._is_active: bool = False

    async def start(self) -> None:
        self._is_active = True

    async def stop(self) -> List[SpeakerSegment]:
        self._is_active = False
        return self.segments

    async def ingest_chunk(
        self,
        chunk_bytes: bytes,
        on_segment_ready: Optional[Callable[[SpeakerSegment], None]] = None,
    ) -> List[SpeakerSegment]:
        """Processes an incoming audio chunk, extracting real-time segments."""
        if not self._is_active:
            raise RuntimeError("RealtimeMeetingStream must be started before ingesting chunks.")

        # Transcribe chunk
        new_segments = await self.stt_provider.transcribe(chunk_bytes)
        for seg in new_segments:
            self.segments.append(seg)
            if on_segment_ready:
                on_segment_ready(seg)
        return new_segments
