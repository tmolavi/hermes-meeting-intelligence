"""
Providers package for Hermes Meeting Intelligence.
"""

from hermes_meeting_intelligence.providers.base import (
    BaseDiarizationProvider,
    BaseExtractionProvider,
    BaseSTTProvider,
)
from hermes_meeting_intelligence.providers.deepgram_provider import DeepgramProvider
from hermes_meeting_intelligence.providers.groq_provider import GroqProvider
from hermes_meeting_intelligence.providers.local_whisper import LocalWhisperProvider
from hermes_meeting_intelligence.providers.mock_provider import (
    MockExtractionProvider,
    MockSTTProvider,
)
from hermes_meeting_intelligence.providers.openai_provider import OpenAIProvider
from hermes_meeting_intelligence.providers.router import ProviderRouter

__all__ = [
    "BaseSTTProvider",
    "BaseExtractionProvider",
    "BaseDiarizationProvider",
    "MockSTTProvider",
    "MockExtractionProvider",
    "OpenAIProvider",
    "GroqProvider",
    "DeepgramProvider",
    "LocalWhisperProvider",
    "ProviderRouter",
]
