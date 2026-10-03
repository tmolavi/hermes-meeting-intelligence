# Meeting Record Schema Reference

The core data contract of Hermes Meeting Intelligence is the portable `MeetingRecord` schema.

## Specification

```json
{
  "meeting_id": "mtg_01j9x...",
  "title": "Engineering Architecture Sync",
  "started_at": "2026-10-01T09:00:00Z",
  "ended_at": "2026-10-01T09:45:00Z",
  "language": "en",
  "participants": [
    {
      "speaker_id": "speaker_alice",
      "name": "Alice Chen",
      "role": "Lead Architect",
      "email": "alice@example.com"
    }
  ],
  "speaker_segments": [
    {
      "segment_id": "seg_001",
      "start": 0.0,
      "end": 12.5,
      "speaker_id": "speaker_alice",
      "text": "We decided to migrate the memory store to SQLite.",
      "confidence": 0.99
    }
  ],
  "transcript": "[Alice Chen]: We decided to migrate the memory store to SQLite.",
  "topics": ["Storage Architecture", "SQLite"],
  "entities": [
    {
      "name": "SQLite",
      "entity_type": "database",
      "mentions_count": 1
    }
  ],
  "decisions": [
    {
      "decision_id": "dec_001",
      "description": "Migrate meeting memory storage layer to SQLite.",
      "decided_by": "Alice Chen",
      "timestamp_offset": 10.0,
      "evidence_quote": "We decided to migrate the memory store to SQLite."
    }
  ],
  "proposals": [
    {
      "proposal_id": "prop_001",
      "description": "Adopt SQLite as local relational store",
      "proposed_by": "Alice Chen",
      "status": "accepted"
    }
  ],
  "disagreements": [
    {
      "disagreement_id": "dis_001",
      "topic": "Streaming buffer size",
      "parties": ["Clara", "Bob"],
      "points_of_view": ["1.5s for low latency", "3.0s for CPU safety"],
      "resolution_status": "resolved",
      "resolution_notes": "Resolved via adaptive router"
    }
  ],
  "questions": [
    {
      "question_id": "q_001",
      "question": "What is the CPU throughput overhead?",
      "asked_by": "Alice Chen",
      "is_answered": true,
      "answer": "Negligible for 3.0s chunks"
    }
  ],
  "action_items": [
    {
      "action_id": "act_001",
      "description": "Implement SQLite memory store by Friday",
      "assignee": "Bob Martin",
      "due_date": "2026-10-05",
      "status": "completed",
      "source_quote": "Bob will implement the memory store."
    }
  ],
  "evidence": [
    {
      "evidence_id": "ev_001",
      "claim": "SQLite has zero external daemon overhead",
      "quote": "SQLite has zero external daemon overhead and allows full offline local verification.",
      "segment_id": "seg_002",
      "speaker_id": "speaker_bob",
      "confidence": 0.98
    }
  ],
  "referenced_documents": ["RFC-0042"],
  "owner_corrections": [
    {
      "correction_id": "corr_001",
      "target_field": "decisions[0].decided_by",
      "original_value": "Alice Chen",
      "corrected_value": "Engineering Consensus",
      "corrected_by": "owner",
      "corrected_at": "2026-10-01T10:00:00Z",
      "reason": "Clarified consensus attribution"
    }
  ],
  "provenance": {
    "pipeline_version": "0.1.0",
    "stt_provider": "mock",
    "extraction_provider": "mock",
    "processed_at": "2026-10-01T09:46:00Z",
    "source_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  },
  "related_meetings": [
    {
      "target_meeting_id": "mtg_000",
      "relationship_type": "continues",
      "description": "Follow up to previous roadmap sync"
    }
  ]
}
```
