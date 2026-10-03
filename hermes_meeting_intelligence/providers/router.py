"""
Smart Multi-Provider Router for Meeting Speech-to-Text and Extraction.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from hermes_meeting_intelligence.models.routing import (
    ProviderCapability,
    ProviderInfo,
    RoutingDecision,
    RoutingStrategy,
)
from hermes_meeting_intelligence.providers.base import BaseExtractionProvider, BaseSTTProvider
from hermes_meeting_intelligence.providers.deepgram_provider import DeepgramProvider
from hermes_meeting_intelligence.providers.groq_provider import GroqProvider
from hermes_meeting_intelligence.providers.local_whisper import LocalWhisperProvider
from hermes_meeting_intelligence.providers.mock_provider import (
    MockExtractionProvider,
    MockSTTProvider,
)
from hermes_meeting_intelligence.providers.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)


class ProviderRouter:
    """Selects and manages STT and Extraction providers based on latency, cost, and availability."""

    def __init__(
        self,
        default_strategy: RoutingStrategy = RoutingStrategy.BALANCED,
        stt_providers: Optional[Dict[str, BaseSTTProvider]] = None,
        extraction_providers: Optional[Dict[str, BaseExtractionProvider]] = None,
    ):
        self.default_strategy = default_strategy

        self.stt_providers: Dict[str, BaseSTTProvider] = stt_providers or {
            "mock": MockSTTProvider(),
            "groq": GroqProvider(),
            "deepgram": DeepgramProvider(),
            "openai": OpenAIProvider(),
            "local_whisper": LocalWhisperProvider(),
        }

        self.extraction_providers: Dict[str, BaseExtractionProvider] = extraction_providers or {
            "mock": MockExtractionProvider(),
            "groq": GroqProvider(),
            "openai": OpenAIProvider(),
        }

    def get_provider_catalog(self) -> List[ProviderInfo]:
        """Returns catalog of known providers and their status."""
        catalog = [
            ProviderInfo(
                name="mock",
                capabilities=[ProviderCapability.STT, ProviderCapability.EXTRACTION],
                latency_ms_estimate=5,
                cost_per_minute_usd=0.0,
                requires_gpu=False,
                is_local=True,
                available=True,
                notes="Deterministic offline mock provider for zero-cost testing and CI.",
            ),
            ProviderInfo(
                name="groq",
                capabilities=[ProviderCapability.STT, ProviderCapability.EXTRACTION],
                latency_ms_estimate=120,
                cost_per_minute_usd=0.001,
                requires_gpu=False,
                is_local=False,
                available=self.stt_providers.get("groq", MockSTTProvider()).is_available,
                notes="Ultra-fast LPU inference for real-time meetings.",
            ),
            ProviderInfo(
                name="deepgram",
                capabilities=[
                    ProviderCapability.STT,
                    ProviderCapability.LIVE_STREAMING_STT,
                    ProviderCapability.DIARIZATION,
                ],
                latency_ms_estimate=250,
                cost_per_minute_usd=0.0043,
                requires_gpu=False,
                is_local=False,
                available=self.stt_providers.get("deepgram", MockSTTProvider()).is_available,
                notes="Production-grade streaming STT with built-in diarization.",
            ),
            ProviderInfo(
                name="openai",
                capabilities=[ProviderCapability.STT, ProviderCapability.EXTRACTION],
                latency_ms_estimate=800,
                cost_per_minute_usd=0.006,
                requires_gpu=False,
                is_local=False,
                available=self.stt_providers.get("openai", MockSTTProvider()).is_available,
                notes="Whisper & GPT models with high semantic accuracy.",
            ),
            ProviderInfo(
                name="local_whisper",
                capabilities=[ProviderCapability.STT],
                latency_ms_estimate=1500,
                cost_per_minute_usd=0.0,
                requires_gpu=False,
                is_local=True,
                available=self.stt_providers.get("local_whisper", MockSTTProvider()).is_available,
                notes="Self-hosted Faster-Whisper on local CPU/GPU.",
            ),
        ]
        return catalog

    def select_route(self, strategy: Optional[RoutingStrategy] = None) -> RoutingDecision:
        strat = strategy or self.default_strategy
        available_stt = [k for k, v in self.stt_providers.items() if v.is_available]
        available_ext = [k for k, v in self.extraction_providers.items() if v.is_available]

        if not available_stt:
            available_stt = ["mock"]
        if not available_ext:
            available_ext = ["mock"]

        if strat == RoutingStrategy.LATENCY:
            stt = (
                "groq"
                if "groq" in available_stt
                else ("deepgram" if "deepgram" in available_stt else available_stt[0])
            )
            ext = "groq" if "groq" in available_ext else available_ext[0]
            rationale = "Selected lowest latency provider path for real-time interaction."
            latency = 150
            cost = 0.002
        elif strat == RoutingStrategy.COST:
            stt = "local_whisper" if "local_whisper" in available_stt else "mock"
            ext = "mock"
            rationale = "Selected zero-API-cost provider path."
            latency = 1200
            cost = 0.0
        elif strat == RoutingStrategy.QUALITY:
            stt = (
                "openai"
                if "openai" in available_stt
                else ("deepgram" if "deepgram" in available_stt else available_stt[0])
            )
            ext = "openai" if "openai" in available_ext else available_ext[0]
            rationale = "Selected maximum reasoning accuracy provider path."
            latency = 900
            cost = 0.015
        else:  # BALANCED
            stt = (
                "groq"
                if "groq" in available_stt
                else ("openai" if "openai" in available_stt else available_stt[0])
            )
            ext = (
                "groq"
                if "groq" in available_ext
                else ("openai" if "openai" in available_ext else available_ext[0])
            )
            rationale = "Balanced speed, accuracy, and operational cost."
            latency = 350
            cost = 0.005

        return RoutingDecision(
            stt_provider=stt,
            extraction_provider=ext,
            strategy_used=strat,
            estimated_latency_ms=latency,
            estimated_cost_usd=cost,
            rationale=rationale,
        )

    def get_stt_provider(self, name: Optional[str] = None) -> BaseSTTProvider:
        if name and name in self.stt_providers:
            return self.stt_providers[name]
        route = self.select_route()
        return self.stt_providers.get(route.stt_provider, self.stt_providers["mock"])

    def get_extraction_provider(self, name: Optional[str] = None) -> BaseExtractionProvider:
        if name and name in self.extraction_providers:
            return self.extraction_providers[name]
        route = self.select_route()
        return self.extraction_providers.get(
            route.extraction_provider, self.extraction_providers["mock"]
        )
