"""
Tests for Persistent Meeting Memory, Cross-Meeting Graph Relations, and Retrieval.
"""

from hermes_meeting_intelligence.memory.relations import MeetingGraphAnalyzer
from hermes_meeting_intelligence.memory.retriever import MeetingMemoryRetriever
from hermes_meeting_intelligence.models.schema import (
    ActionItem,
    ActionStatus,
    Decision,
    MeetingRecord,
    RelationshipType,
)


def test_save_and_retrieve_meeting(in_memory_store, sample_meeting_record):
    mid = in_memory_store.save_meeting(sample_meeting_record)
    assert mid == sample_meeting_record.meeting_id

    loaded = in_memory_store.get_meeting(mid)
    assert loaded is not None
    assert loaded.title == sample_meeting_record.title
    assert len(loaded.decisions) == len(sample_meeting_record.decisions)

    # Test list_meetings
    meetings_list = in_memory_store.list_meetings()
    assert len(meetings_list) == 1
    assert meetings_list[0]["meeting_id"] == mid


def test_cross_meeting_relationships(in_memory_store, sample_meeting_record):
    in_memory_store.save_meeting(sample_meeting_record)

    m2 = MeetingRecord(
        meeting_id="mtg_test_002",
        title="Followup Architecture",
        decisions=[Decision(description="Implement vector memory")],
        action_items=[ActionItem(description="Run benchmarks", status=ActionStatus.PENDING)],
    )
    in_memory_store.save_meeting(m2)

    # Add relationship
    in_memory_store.add_relationship(
        source_meeting_id="mtg_test_002",
        target_meeting_id=sample_meeting_record.meeting_id,
        relationship_type=RelationshipType.CONTINUES,
        description="Continuation of kickoff topics",
    )

    retriever = MeetingMemoryRetriever(in_memory_store)
    lineage = retriever.get_related_lineage("mtg_test_002")
    assert len(lineage["outgoing_relations"]) == 1
    assert lineage["outgoing_relations"][0]["target_meeting_id"] == sample_meeting_record.meeting_id


def test_retriever_decisions_and_actions(in_memory_store, sample_meeting_record):
    in_memory_store.save_meeting(sample_meeting_record)
    retriever = MeetingMemoryRetriever(in_memory_store)

    decisions = retriever.search_decisions("SQLite")
    assert len(decisions) >= 1
    assert "SQLite" in decisions[0]["description"]

    actions = retriever.search_open_actions()
    assert len(actions) >= 1
    assert actions[0]["status"] == "pending"


def test_owner_correction_audit(in_memory_store, sample_meeting_record):
    in_memory_store.save_meeting(sample_meeting_record)

    corr = in_memory_store.record_correction(
        meeting_id=sample_meeting_record.meeting_id,
        target_field="decisions[0].decided_by",
        original_value="Alice Chen & Bob Martin",
        corrected_value="Alice Chen (Consensus Lead)",
        reason="Owner clarified role attribution",
    )
    assert corr.corrected_by == "owner"

    updated = in_memory_store.get_meeting(sample_meeting_record.meeting_id)
    assert len(updated.owner_corrections) == 1
    assert updated.owner_corrections[0].corrected_value == "Alice Chen (Consensus Lead)"


def test_graph_analyzer_overlap(sample_meeting_record):
    m2 = MeetingRecord(
        meeting_id="mtg_test_002",
        title="Database Optimization",
        topics=["Storage Architecture", "Performance"],
    )
    overlaps = MeetingGraphAnalyzer.find_topic_overlaps(sample_meeting_record, m2)
    assert "storage architecture" in overlaps
