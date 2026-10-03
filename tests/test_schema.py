"""
Unit tests for MeetingRecord schema, Pydantic validation, serialization, and edge cases.
"""

import pytest
from pydantic import ValidationError

from hermes_meeting_intelligence.models.schema import (
    ActionItem,
    ActionStatus,
    Decision,
    MeetingRecord,
    OwnerCorrection,
    Participant,
    SpeakerSegment,
)


def test_valid_meeting_record():
    record = MeetingRecord(
        title="Weekly Sprint Sync",
        language="en",
        participants=[
            Participant(speaker_id="spk_1", name="Alice"),
            Participant(speaker_id="spk_2", name="Bob"),
        ],
        speaker_segments=[
            SpeakerSegment(
                start=0.0,
                end=5.0,
                speaker_id="spk_1",
                text="Let us begin the architecture review.",
            )
        ],
        decisions=[
            Decision(
                description="Adopt SQLite storage",
                decided_by="Alice",
                evidence_quote="Let us begin",
            )
        ],
        action_items=[
            ActionItem(
                description="Write unit tests",
                assignee="Bob",
                status=ActionStatus.PENDING,
            )
        ],
    )
    assert record.title == "Weekly Sprint Sync"
    assert len(record.participants) == 2
    assert len(record.decisions) == 1
    assert record.decisions[0].description == "Adopt SQLite storage"

    # Test auto-generation of transcript
    full_text = record.generate_full_transcript_if_empty()
    assert "[Alice]: Let us begin the architecture review." in full_text


def test_speaker_segment_invalid_duration():
    with pytest.raises(ValidationError):
        SpeakerSegment(
            start=10.0,
            end=5.0,  # Invalid: end earlier than start
            speaker_id="spk_1",
            text="Invalid segment",
        )


def test_empty_title_validation():
    with pytest.raises(ValidationError):
        MeetingRecord(title="")


def test_owner_correction_audit_structure():
    corr = OwnerCorrection(
        target_field="decisions[0].decided_by",
        original_value="Bob",
        corrected_value="Alice",
        corrected_by="lead_owner",
        reason="Transcription attributed agreement to incorrect participant",
    )
    assert corr.corrected_by == "lead_owner"
    assert corr.original_value == "Bob"
    assert corr.corrected_value == "Alice"


def test_json_roundtrip(sample_meeting_record):
    dumped = sample_meeting_record.model_dump_json()
    loaded = MeetingRecord.model_validate_json(dumped)
    assert loaded.meeting_id == sample_meeting_record.meeting_id
    assert loaded.title == sample_meeting_record.title
    assert len(loaded.decisions) == len(sample_meeting_record.decisions)
