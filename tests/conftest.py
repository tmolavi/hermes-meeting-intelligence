"""
Shared pytest fixtures.
"""

import json
import os

import pytest

from hermes_meeting_intelligence.memory.store import MeetingMemoryStore
from hermes_meeting_intelligence.models.schema import MeetingRecord
from hermes_meeting_intelligence.pipeline.extractor import MeetingPipeline
from hermes_meeting_intelligence.providers.mock_provider import (
    MockExtractionProvider,
    MockSTTProvider,
)
from hermes_meeting_intelligence.providers.router import ProviderRouter


@pytest.fixture
def in_memory_store():
    return MeetingMemoryStore(":memory:")


@pytest.fixture
def mock_router():
    stt = {"mock": MockSTTProvider()}
    ext = {"mock": MockExtractionProvider()}
    return ProviderRouter(stt_providers=stt, extraction_providers=ext)


@pytest.fixture
def mock_pipeline(mock_router):
    return MeetingPipeline(router=mock_router)


@pytest.fixture
def sample_meeting_json_path():
    path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "examples",
        "synthetic_meetings",
        "meeting_01_kickoff_decision.json",
    )
    return os.path.abspath(path)


@pytest.fixture
def sample_meeting_record(sample_meeting_json_path):
    with open(sample_meeting_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return MeetingRecord.model_validate(data)
