#!/usr/bin/env python3
"""
Quickstart Example: End-to-End Meeting Transcription & Extraction Pipeline.

Demonstrates ingesting a transcript, extracting structured decisions,
action items, and topics, and persisting them to a local SQLite database.
"""

import asyncio

from hermes_meeting_intelligence import MeetingMemoryStore, MeetingPipeline

SAMPLE_TRANSCRIPT = """
[Alice Chen]: We need to finalize our memory strategy today. We agreed on using SQLite with full-text indexing for meeting records.
[Bob Martin]: Agreed. SQLite ensures zero external dependencies and fast local queries.
[Alice Chen]: Bob, please implement the schema migration script and tests by Thursday.
[Bob Martin]: Will do. I'll make sure tests run on standard CPU runners without GPU requirements.
"""


async def main() -> None:
    print("=== Hermes Meeting Intelligence Quickstart ===")

    # 1. Initialize Pipeline (defaults to deterministic offline mock provider)
    pipeline = MeetingPipeline()

    # 2. Extract Structured Intelligence
    print("\n1. Processing sample meeting transcript...")
    record = await pipeline.process_transcript(
        transcript_text=SAMPLE_TRANSCRIPT,
        title="Engineering Architecture Sync",
        language="en",
    )

    print(f"\n✓ Generated MeetingRecord (ID: {record.meeting_id})")
    print(f"  Title: {record.title}")
    print(f"  Topics: {', '.join(record.topics)}")
    print(f"  Decisions Extracted ({len(record.decisions)}):")
    for d in record.decisions:
        print(f"    - {d.description}")
    print(f"  Action Items Extracted ({len(record.action_items)}):")
    for a in record.action_items:
        print(f"    - {a.description} (Assignee: {a.assignee or 'Unassigned'})")

    # 3. Save to In-Memory / SQLite Store
    print("\n2. Storing record into Meeting Memory...")
    store = MeetingMemoryStore(":memory:")
    meeting_id = store.save_meeting(record)
    print(f"✓ Saved to store with meeting ID: {meeting_id}")

    # 4. Verify Retrieval
    stored = store.get_meeting(meeting_id)
    assert stored is not None
    print(
        f"✓ Verified storage integrity: retrieved {stored.title} with {len(stored.decisions)} decision(s)."
    )
    print("\n=== Quickstart Finished Successfully ===")


if __name__ == "__main__":
    asyncio.run(main())
