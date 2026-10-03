"""
Local CPU/GPU Faster-Whisper Provider.

Designed for self-hosted, offline, or air-gapped Hermes Agent setups.
Does NOT download models silently without explicit user configuration.
"""

from __future__ import annotations

import logging
from typing import Any, List, Optional

from hermes_meeting_intelligence.models.schema import SpeakerSegment
from hermes_meeting_intelligence.providers.base import BaseSTTProvider

logger = logging.getLogger(__name__)


class LocalWhisperProvider(BaseSTTProvider):
    """Local faster-whisper adapter with CPU-first configuration."""

    def __init__(
        self,
        model_size_or_path: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
        download_root: Optional[str] = None,
    ):
        self.model_size_or_path = model_size_or_path
        self.device = device
        self.compute_type = compute_type
        self.download_root = download_root
        self._model: Any = None
        self._is_pkg_installed: bool = False

        try:
            import faster_whisper  # type: ignore # noqa: F401

            self._is_pkg_installed = True
        except ImportError:
            self._is_pkg_installed = False

    @property
    def name(self) -> str:
        return "local_whisper"

    @property
    def is_available(self) -> bool:
        return self._is_pkg_installed

    def _load_model(self) -> Any:
        if not self._is_pkg_installed:
            raise ImportError(
                "faster-whisper is not installed. Install with: pip install 'hermes-meeting-intelligence[local-stt]'"
            )
        if self._model is None:
            from faster_whisper import WhisperModel

            logger.info(
                f"Loading local Whisper model '{self.model_size_or_path}' on {self.device} ({self.compute_type})..."
            )
            self._model = WhisperModel(
                self.model_size_or_path,
                device=self.device,
                compute_type=self.compute_type,
                download_root=self.download_root,
            )
        return self._model

    async def transcribe(
        self,
        audio_path_or_bytes: Any,
        language: Optional[str] = None,
        diarize: bool = True,
        **kwargs: Any,
    ) -> List[SpeakerSegment]:
        model = self._load_model()
        segments_gen, info = model.transcribe(
            audio_path_or_bytes,
            language=language,
            beam_size=kwargs.get("beam_size", 5),
            vad_filter=kwargs.get("vad_filter", True),
        )

        segments: List[SpeakerSegment] = []
        for idx, s in enumerate(segments_gen):
            segments.append(
                SpeakerSegment(
                    segment_id=f"local_seg_{idx + 1}",
                    start=float(s.start),
                    end=float(s.end),
                    speaker_id="speaker_local",
                    text=s.text.strip(),
                    confidence=float(getattr(s, "avg_logprob", 0.9)),
                )
            )
        return segments
