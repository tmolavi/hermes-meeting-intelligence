"""
Deepgram Nova Speech-to-Text & Diarization Provider.
"""

from __future__ import annotations

import os
from typing import Any, List, Optional

import httpx

from hermes_meeting_intelligence.models.schema import SpeakerSegment
from hermes_meeting_intelligence.providers.base import BaseSTTProvider


class DeepgramProvider(BaseSTTProvider):
    """Integrates Deepgram API for high-accuracy STT with native speaker diarization."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "nova-2",
        timeout_seconds: float = 60.0,
    ):
        self.api_key = api_key or os.getenv("DEEPGRAM_API_KEY")
        self.model = model
        self.timeout_seconds = timeout_seconds

    @property
    def name(self) -> str:
        return "deepgram"

    @property
    def is_available(self) -> bool:
        return bool(self.api_key)

    async def transcribe(
        self,
        audio_path_or_bytes: Any,
        language: Optional[str] = None,
        diarize: bool = True,
        **kwargs: Any,
    ) -> List[SpeakerSegment]:
        if not self.is_available:
            raise ValueError(
                "Deepgram API key is missing. Set DEEPGRAM_API_KEY environment variable or config."
            )

        params = {
            "model": self.model,
            "diarize": "true" if diarize else "false",
            "punctuate": "true",
            "utterances": "true",
        }
        if language:
            params["language"] = language

        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "audio/wav",
        }

        url = "https://api.deepgram.com/v1/listen"

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            if isinstance(audio_path_or_bytes, str):
                with open(audio_path_or_bytes, "rb") as f:
                    audio_data = f.read()
            else:
                audio_data = audio_path_or_bytes

            resp = await client.post(url, headers=headers, params=params, content=audio_data)
            resp.raise_for_status()
            res_json = resp.json()

            segments: List[SpeakerSegment] = []
            results = res_json.get("results", {})
            utterances = results.get("utterances", [])

            if utterances:
                for idx, utt in enumerate(utterances):
                    segments.append(
                        SpeakerSegment(
                            segment_id=f"dg_seg_{idx + 1}",
                            start=float(utt.get("start", 0.0)),
                            end=float(utt.get("end", 0.0)),
                            speaker_id=f"speaker_{utt.get('speaker', 0)}",
                            text=utt.get("transcript", "").strip(),
                            confidence=float(utt.get("confidence", 0.95)),
                        )
                    )
            else:
                channels = results.get("channels", [])
                if channels and channels[0].get("alternatives"):
                    alt = channels[0]["alternatives"][0]
                    transcript = alt.get("transcript", "")
                    segments.append(
                        SpeakerSegment(
                            segment_id="dg_seg_1",
                            start=0.0,
                            end=float(res_json.get("metadata", {}).get("duration", 0.0)),
                            speaker_id="speaker_0",
                            text=transcript,
                            confidence=float(alt.get("confidence", 0.95)),
                        )
                    )

            return segments
