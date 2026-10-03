"""
Tests for End-to-End Meeting Pipeline and Validator.
"""

import pytest

from hermes_meeting_intelligence.models.schema import MeetingRecord
from hermes_meeting_intelligence.pipeline.validator import MeetingValidator


@pytest.mark.asyncio
async def test_pipeline_transcript_processing(mock_pipeline):
    transcript = (
        "[Alice]: We decided to finalize the API design.\n"
        "[Bob]: I propose we add OpenAPI schema validation.\n"
        "[Alice]: Agreed. Bob, please create the pull request by Friday."
    )
    record = await mock_pipeline.process_transcript(
        transcript_text=transcript,
        title="API Design Sync",
        language="en",
    )

    assert isinstance(record, MeetingRecord)
    assert record.title == "API Design Sync"
    assert len(record.decisions) >= 1
    assert len(record.action_items) >= 1
    assert record.provenance.source_hash is not None
    assert record.provenance.pipeline_version == "0.1.0"


def test_validator_detects_empty_title():
    record = MeetingRecord(
        meeting_id="m1",
        title="  ",  # invalid whitespace title
    )
    # The pydantic model enforces min_length=1, but if constructed with whitespace:
    valid, issues = MeetingValidator.validate_audit_integrity(record)
    assert valid is False
    assert any("title" in i.lower() for i in issues)
