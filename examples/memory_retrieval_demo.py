#!/usr/bin/env python3
"""
Memory Retrieval Demo: Sequential Synthetic Meeting Ingestion and Cross-Meeting Query.

Demonstrates:
1. Ingesting Meeting 1 (Kickoff decision).
2. Ingesting Meeting 2 (Followup disagreement & action item).
3. Ingesting Meeting 3 (Resolution and action completion).
4. Performing cross-meeting queries for decisions, unresolved actions, and lineage.
"""

import json
import os

from hermes_meeting_intelligence import (
    MeetingMemoryRetriever,
    MeetingMemoryStore,
    MeetingRecord,
)

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "synthetic_meetings")


def load_meeting(filename: str) -> MeetingRecord:
    path = os.path.join(EXAMPLES_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return MeetingRecord.model_validate(data)


def main() -> None:
    print("=== Hermes Cross-Meeting Memory Retrieval Demo ===")

    store = MeetingMemoryStore(":memory:")
    retriever = MeetingMemoryRetriever(store)

    # 1. Ingest Synthetic Meetings
    m1 = load_meeting("meeting_01_kickoff_decision.json")
    m2 = load_meeting("meeting_02_followup_disagreement.json")
    m3 = load_meeting("meeting_03_resolution_and_actions.json")

    print("\n1. Ingesting 3 sequential synthetic meetings...")
    store.save_meeting(m1)
    store.save_meeting(m2)
    store.save_meeting(m3)
    print(f"✓ Stored meetings: {m1.meeting_id}, {m2.meeting_id}, {m3.meeting_id}")

    # 2. Query Decisions across all meetings
    print("\n2. Searching all decisions involving 'SQLite' or 'chunking'...")
    decisions = retriever.search_decisions("SQLite")
    for d in decisions:
        print(f"  • [{d['meeting_title']}]: {d['description']}")

    # 3. Query Actions
    print("\n3. Querying open action items...")
    actions = retriever.search_open_actions()
    for a in actions:
        print(
            f"  • [{a['status'].upper()}] {a['description']} (Assignee: {a.get('assignee') or 'Unassigned'})"
        )

    # 4. Query Meeting Lineage
    print(f"\n4. Inspecting lineage for Meeting 3 ({m3.meeting_id})...")
    lineage = retriever.get_related_lineage(m3.meeting_id)
    print(f"  Meeting: {lineage['title']}")
    print("  Outgoing Links:")
    for rel in lineage["outgoing_relations"]:
        print(
            f"    → [{rel['relationship_type']}] target: {rel['target_meeting_id']} ({rel.get('description')})"
        )

    print("\n=== Memory Retrieval Demo Finished Successfully ===")


if __name__ == "__main__":
    main()
