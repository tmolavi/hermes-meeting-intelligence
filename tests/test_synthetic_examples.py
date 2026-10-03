"""
Tests verifying integrity and lineage of synthetic meeting example fixtures.
"""

import glob
import json
import os

from hermes_meeting_intelligence.memory.retriever import MeetingMemoryRetriever
from hermes_meeting_intelligence.memory.store import MeetingMemoryStore
from hermes_meeting_intelligence.models.schema import MeetingRecord
from hermes_meeting_intelligence.pipeline.validator import MeetingValidator


def test_all_synthetic_fixtures_valid():
    fixtures_pattern = os.path.join(
        os.path.dirname(__file__), "..", "examples", "synthetic_meetings", "*.json"
    )
    files = glob.glob(fixtures_pattern)
    assert len(files) == 3, f"Expected 3 synthetic meeting files, found {len(files)}"

    store = MeetingMemoryStore(":memory:")

    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        record = MeetingRecord.model_validate(data)
        valid, issues = MeetingValidator.validate_audit_integrity(record)
        assert valid is True, f"Validation failed for {file_path}: {issues}"
        store.save_meeting(record)

    retriever = MeetingMemoryRetriever(store)
    # Check decision search across all 3
    decisions = retriever.search_decisions("SQLite")
    assert len(decisions) >= 1

    # Check meeting 3 links back to meeting 1 and meeting 2
    lineage = retriever.get_related_lineage("mtg_synth_003")
    target_ids = [rel["target_meeting_id"] for rel in lineage["outgoing_relations"]]
    assert "mtg_synth_001" in target_ids
    assert "mtg_synth_002" in target_ids
