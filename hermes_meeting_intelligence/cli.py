"""
Command-line Interface for Hermes Meeting Intelligence (`hermes-meeting`).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys

from hermes_meeting_intelligence.memory.retriever import MeetingMemoryRetriever
from hermes_meeting_intelligence.memory.store import MeetingMemoryStore
from hermes_meeting_intelligence.models.schema import MeetingRecord
from hermes_meeting_intelligence.pipeline.extractor import MeetingPipeline
from hermes_meeting_intelligence.pipeline.validator import MeetingValidator


def cmd_ingest(args: argparse.Namespace) -> None:
    """Ingests a transcript file or raw audio into meeting memory."""
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)

    with open(args.input_file, "r", encoding="utf-8") as f:
        content = f.read()

    pipeline = MeetingPipeline()
    title = args.title or os.path.basename(args.input_file).rsplit(".", 1)[0]

    async def run() -> MeetingRecord:
        return await pipeline.process_transcript(
            transcript_text=content,
            title=title,
            language=args.language,
        )

    record = asyncio.run(run())
    store = MeetingMemoryStore(args.db)
    meeting_id = store.save_meeting(record)

    print(f"✓ Ingested meeting '{record.title}' (ID: {meeting_id})")
    print(f"  Decisions: {len(record.decisions)}")
    print(f"  Action Items: {len(record.action_items)}")
    print(f"  Topics: {', '.join(record.topics)}")
    print(f"  Saved to database: {args.db}")


def cmd_query(args: argparse.Namespace) -> None:
    """Queries meeting memory."""
    store = MeetingMemoryStore(args.db)
    retriever = MeetingMemoryRetriever(store)

    if args.type == "decisions":
        results = retriever.search_decisions(args.term or "")
        print(f"Found {len(results)} decision(s):")
        for d in results:
            print(
                f"- [{d['meeting_title']}] {d['description']} (By: {d.get('decided_by') or 'Consensus'})"
            )
    elif args.type == "actions":
        results = retriever.search_open_actions(assignee=args.term)
        print(f"Found {len(results)} open action item(s):")
        for a in results:
            print(
                f"- [{a['meeting_title']}] {a['description']} (Assignee: {a.get('assignee') or 'Unassigned'}, Due: {a.get('due_date') or 'N/A'}, Status: {a['status']})"
            )
    elif args.type == "topics":
        results = retriever.search_topics(args.term or "")
        print(f"Found {len(results)} meeting(s) for topic '{args.term}':")
        for m in results:
            print(f"- [{m['started_at'][:10]}] {m['title']} (ID: {m['meeting_id']})")
    elif args.type == "lineage":
        if not args.term:
            print("Error: Meeting ID is required for lineage query.", file=sys.stderr)
            sys.exit(1)
        res = retriever.get_related_lineage(args.term)
        print(f"Lineage for {res['title']} ({res['meeting_id']}):")
        print(f"  Outgoing links: {len(res['outgoing_relations'])}")
        for r in res["outgoing_relations"]:
            print(
                f"    → ({r['relationship_type']}) to {r['target_meeting_id']}: {r.get('description')}"
            )
        print(f"  Incoming links: {len(res['incoming_relations'])}")
        for r in res["incoming_relations"]:
            print(
                f"    ← ({r['relationship_type']}) from {r['source_meeting_id']}: {r.get('description')}"
            )


def cmd_list(args: argparse.Namespace) -> None:
    """Lists recent meetings."""
    store = MeetingMemoryStore(args.db)
    meetings = store.list_meetings(limit=args.limit)
    print(f"Stored Meetings ({len(meetings)}):")
    for m in meetings:
        print(f"- {m['started_at'][:10]} | {m['meeting_id']} | {m['title']} ({m['language']})")


def cmd_validate(args: argparse.Namespace) -> None:
    """Validates a MeetingRecord JSON file against the schema and audit rules."""
    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found.", file=sys.stderr)
        sys.exit(1)

    with open(args.file, "r", encoding="utf-8") as f:
        data = json.load(f)

    try:
        record = MeetingRecord.model_validate(data)
        valid, issues = MeetingValidator.validate_audit_integrity(record)
        if valid:
            print(f"✓ '{args.file}' is a valid MeetingRecord (ID: {record.meeting_id})")
        else:
            print(f"✗ Validation errors in '{args.file}':", file=sys.stderr)
            for iss in issues:
                print(f"  - {iss}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"✗ Schema validation failed: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="hermes-meeting",
        description="Hermes Meeting Intelligence CLI: Ingest, Query, and Audit Meeting Memory",
    )
    parser.add_argument(
        "--db",
        default=os.getenv("HERMES_MEETING_DB_PATH", "~/.hermes/meeting_memory.sqlite"),
        help="Path to SQLite meeting memory database",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Ingest
    p_ingest = subparsers.add_parser(
        "ingest", help="Ingest a transcript text file into meeting memory"
    )
    p_ingest.add_argument("input_file", help="Path to transcript file")
    p_ingest.add_argument("--title", help="Meeting title")
    p_ingest.add_argument("--language", default="en", help="Language code")
    p_ingest.set_defaults(func=cmd_ingest)

    # Query
    p_query = subparsers.add_parser("query", help="Query meeting memory")
    p_query.add_argument(
        "type", choices=["decisions", "actions", "topics", "lineage"], help="Query type"
    )
    p_query.add_argument("term", nargs="?", default="", help="Search term or meeting ID")
    p_query.set_defaults(func=cmd_query)

    # List
    p_list = subparsers.add_parser("list", help="List stored meetings")
    p_list.add_argument("--limit", type=int, default=20, help="Max results")
    p_list.set_defaults(func=cmd_list)

    # Validate
    p_val = subparsers.add_parser("validate", help="Validate a MeetingRecord JSON file")
    p_val.add_argument("file", help="Path to JSON file")
    p_val.set_defaults(func=cmd_validate)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
