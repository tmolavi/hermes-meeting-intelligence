"""
Tests for STT, Extraction, and Routing Providers.
"""

import pytest

from hermes_meeting_intelligence.models.routing import RoutingStrategy
from hermes_meeting_intelligence.providers.deepgram_provider import DeepgramProvider
from hermes_meeting_intelligence.providers.groq_provider import GroqProvider
from hermes_meeting_intelligence.providers.local_whisper import LocalWhisperProvider
from hermes_meeting_intelligence.providers.mock_provider import (
    MockExtractionProvider,
    MockSTTProvider,
)
from hermes_meeting_intelligence.providers.openai_provider import OpenAIProvider
from hermes_meeting_intelligence.providers.router import ProviderRouter


@pytest.mark.asyncio
async def test_mock_stt_transcription():
    stt = MockSTTProvider()
    assert stt.is_available is True
    assert stt.name == "mock"

    raw_dialogue = "[Alice]: We decided to deploy.\n[Bob]: I agree."
    segments = await stt.transcribe(raw_dialogue)
    assert len(segments) == 2
    assert segments[0].speaker_id == "Alice"
    assert segments[0].text == "We decided to deploy."
    assert segments[1].speaker_id == "Bob"


@pytest.mark.asyncio
async def test_mock_extraction_heuristics():
    ext = MockExtractionProvider()
    assert ext.is_available is True

    transcript = "[Alice]: We decided to use SQLite for memory.\n[Bob]: Bob will implement the database by Friday."
    data = await ext.extract_intelligence(transcript=transcript)

    assert len(data["decisions"]) >= 1
    assert "SQLite" in data["decisions"][0]["description"]
    assert len(data["action_items"]) >= 1
    assert "Friday" in data["action_items"][0]["description"]
    assert "SQLite" in [e["name"] for e in data["entities"]]


def test_missing_api_key_safety():
    openai = OpenAIProvider(api_key=None)
    assert openai.is_available is False

    groq = GroqProvider(api_key=None)
    assert groq.is_available is False

    dg = DeepgramProvider(api_key=None)
    assert dg.is_available is False


@pytest.mark.asyncio
async def test_missing_api_key_call_raises():
    openai = OpenAIProvider(api_key="")
    with pytest.raises(ValueError, match="OpenAI API key is missing"):
        await openai.transcribe("dummy.wav")


def test_provider_router_selection_and_catalog():
    router = ProviderRouter()
    catalog = router.get_provider_catalog()
    assert len(catalog) >= 4

    # Default router with no API keys should safely fallback to mock
    decision = router.select_route(RoutingStrategy.LATENCY)
    assert decision.stt_provider in ["groq", "deepgram", "mock"]
    assert decision.strategy_used == RoutingStrategy.LATENCY

    cost_decision = router.select_route(RoutingStrategy.COST)
    assert cost_decision.strategy_used == RoutingStrategy.COST
    assert cost_decision.estimated_cost_usd == 0.0

    stt = router.get_stt_provider("mock")
    assert stt.name == "mock"


def test_local_whisper_availability_check():
    local = LocalWhisperProvider()
    # It shouldn't crash regardless of whether faster_whisper is installed
    assert isinstance(local.is_available, bool)
