"""
OpenAI & OpenAI-compatible STT and Structured Extraction Provider.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import httpx

from hermes_meeting_intelligence.models.schema import SpeakerSegment
from hermes_meeting_intelligence.providers.base import BaseExtractionProvider, BaseSTTProvider


class OpenAIProvider(BaseSTTProvider, BaseExtractionProvider):
    """Integrates OpenAI Whisper audio endpoints and GPT structured completion."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.openai.com/v1",
        stt_model: str = "whisper-1",
        extraction_model: str = "gpt-4o-mini",
        timeout_seconds: float = 60.0,
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url.rstrip("/")
        self.stt_model = stt_model
        self.extraction_model = extraction_model
        self.timeout_seconds = timeout_seconds

    @property
    def name(self) -> str:
        return "openai"

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
                "OpenAI API key is missing. Set OPENAI_API_KEY environment variable or config."
            )

        headers = {"Authorization": f"Bearer {self.api_key}"}
        url = f"{self.base_url}/audio/transcriptions"

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            files = {}
            if isinstance(audio_path_or_bytes, str):
                files["file"] = (
                    os.path.basename(audio_path_or_bytes),
                    open(audio_path_or_bytes, "rb"),
                )
            else:
                files["file"] = ("audio.wav", audio_path_or_bytes)

            data = {
                "model": self.stt_model,
                "response_format": "verbose_json",
            }
            if language:
                data["language"] = language

            resp = await client.post(url, headers=headers, files=files, data=data)
            resp.raise_for_status()
            res_json = resp.json()

            segments: List[SpeakerSegment] = []
            raw_segments = res_json.get("segments", [])
            if raw_segments:
                for idx, seg in enumerate(raw_segments):
                    segments.append(
                        SpeakerSegment(
                            segment_id=f"seg_{idx + 1}",
                            start=float(seg.get("start", 0.0)),
                            end=float(seg.get("end", 0.0)),
                            speaker_id="speaker_unknown",
                            text=seg.get("text", "").strip(),
                            confidence=0.95,
                        )
                    )
            else:
                text = res_json.get("text", "").strip()
                segments.append(
                    SpeakerSegment(
                        segment_id="seg_1",
                        start=0.0,
                        end=float(res_json.get("duration", 0.0)),
                        speaker_id="speaker_1",
                        text=text,
                        confidence=0.95,
                    )
                )
            return segments

    async def extract_intelligence(
        self,
        transcript: str,
        speaker_segments: Optional[List[SpeakerSegment]] = None,
        meeting_title: Optional[str] = None,
        language: str = "en",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        if not self.is_available:
            raise ValueError(
                "OpenAI API key is missing. Set OPENAI_API_KEY environment variable or config."
            )

        system_prompt = (
            "You are an expert meeting intelligence assistant. Given a meeting transcript, extract structured data:\n"
            "- decisions: list of {description, decided_by, evidence_quote}\n"
            "- proposals: list of {description, proposed_by, status}\n"
            "- disagreements: list of {topic, parties, points_of_view, resolution_status}\n"
            "- questions: list of {question, asked_by, is_answered, answer}\n"
            "- action_items: list of {description, assignee, due_date, status, source_quote}\n"
            "- topics: list of key themes\n"
            "- entities: list of {name, entity_type, mentions_count}\n"
            "Return valid JSON only matching these keys."
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.extraction_model,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Title: {meeting_title or 'Untitled Meeting'}\nLanguage: {language}\n\nTranscript:\n{transcript}",
                },
            ],
            "temperature": 0.1,
        }

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions", headers=headers, json=payload
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            parsed: Dict[str, Any] = json.loads(content)
            return parsed
