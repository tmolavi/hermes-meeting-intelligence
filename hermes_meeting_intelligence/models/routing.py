"""
Routing Models and Priorities for Real-time and Batch Meeting Intelligence.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class RoutingStrategy(str, Enum):
    LATENCY = "LATENCY"  # Prioritize fastest TTFT (Time to First Token) & low-latency audio stream
    COST = "COST"  # Prioritize local models or free tier / lower-cost APIs
    QUALITY = "QUALITY"  # Prioritize highest accuracy model regardless of latency or cost
    BALANCED = "BALANCED"  # Weighted trade-off between latency, accuracy, and cost


class ProviderCapability(str, Enum):
    STT = "stt"
    LIVE_STREAMING_STT = "live_streaming_stt"
    DIARIZATION = "diarization"
    EXTRACTION = "extraction"
    EMBEDDING = "embedding"


class ProviderInfo(BaseModel):
    name: str = Field(
        ..., description="Provider identifier (e.g., 'groq', 'deepgram', 'openai', 'local_whisper')"
    )
    capabilities: List[ProviderCapability] = Field(default_factory=list)
    latency_ms_estimate: int = Field(default=500, description="Estimated processing latency in ms")
    cost_per_minute_usd: float = Field(
        default=0.0, description="Estimated audio cost per minute in USD"
    )
    requires_gpu: bool = Field(default=False)
    is_local: bool = Field(default=False)
    available: bool = Field(default=True)
    notes: Optional[str] = Field(None)


class RoutingDecision(BaseModel):
    stt_provider: str
    extraction_provider: str
    strategy_used: RoutingStrategy
    estimated_latency_ms: int
    estimated_cost_usd: float
    rationale: str
