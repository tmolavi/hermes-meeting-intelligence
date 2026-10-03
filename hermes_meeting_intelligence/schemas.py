"""
Hermes Agent Tool Schemas for Meeting Intelligence.

Follows official Hermes plugin schema conventions for function calling.
"""

from typing import Any, Dict, List

MEETING_TRANSCRIBE_SCHEMA: Dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "meeting_transcribe",
        "description": "Transcribes meeting audio using configured STT provider (local CPU/GPU or remote API) with optional speaker diarization.",
        "parameters": {
            "type": "object",
            "properties": {
                "audio_path": {
                    "type": "string",
                    "description": "Path to audio file (or raw transcript text for mock testing).",
                },
                "language": {
                    "type": "string",
                    "description": "Language code (e.g., 'en', 'fa', 'tr', 'az', 'ar').",
                },
                "diarize": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to perform speaker diarization.",
                },
                "provider": {
                    "type": "string",
                    "enum": ["mock", "groq", "deepgram", "openai", "local_whisper"],
                    "description": "Override default STT provider.",
                },
            },
            "required": ["audio_path"],
        },
    },
}

MEETING_EXTRACT_SCHEMA: Dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "meeting_extract",
        "description": "Extracts structured intelligence (decisions, proposals, disagreements, questions, action items, evidence, entities, topics) from a transcript.",
        "parameters": {
            "type": "object",
            "properties": {
                "transcript": {
                    "type": "string",
                    "description": "Full meeting transcript text.",
                },
                "title": {
                    "type": "string",
                    "description": "Descriptive title for the meeting.",
                },
                "language": {
                    "type": "string",
                    "default": "en",
                    "description": "Language of transcript.",
                },
                "save_to_memory": {
                    "type": "boolean",
                    "default": True,
                    "description": "Automatically persist the extracted MeetingRecord to SQLite meeting memory.",
                },
            },
            "required": ["transcript", "title"],
        },
    },
}

MEETING_MEMORY_STORE_SCHEMA: Dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "meeting_memory_store",
        "description": "Saves a validated MeetingRecord JSON object into persistent meeting memory.",
        "parameters": {
            "type": "object",
            "properties": {
                "meeting_record_json": {
                    "type": "string",
                    "description": "Valid JSON representation of a MeetingRecord.",
                },
            },
            "required": ["meeting_record_json"],
        },
    },
}

MEETING_MEMORY_QUERY_SCHEMA: Dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "meeting_memory_query",
        "description": "Queries meeting memory for prior decisions, open actions, topics, or meeting summaries.",
        "parameters": {
            "type": "object",
            "properties": {
                "query_type": {
                    "type": "string",
                    "enum": ["decisions", "open_actions", "topics", "recent_meetings", "lineage"],
                    "description": "Type of memory query to perform.",
                },
                "query_term": {
                    "type": "string",
                    "description": "Search term, topic name, or meeting_id depending on query_type.",
                },
                "assignee": {
                    "type": "string",
                    "description": "Filter by participant name for open_actions query.",
                },
                "limit": {
                    "type": "integer",
                    "default": 10,
                    "description": "Maximum number of results to return.",
                },
            },
            "required": ["query_type"],
        },
    },
}

MEETING_LINK_RELATED_SCHEMA: Dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "meeting_link_related",
        "description": "Explicitly links two meetings with a typed relationship (continues, supersedes, references, follows_up, blocks, related_to).",
        "parameters": {
            "type": "object",
            "properties": {
                "source_meeting_id": {
                    "type": "string",
                    "description": "ID of source meeting.",
                },
                "target_meeting_id": {
                    "type": "string",
                    "description": "ID of target meeting to connect.",
                },
                "relationship_type": {
                    "type": "string",
                    "enum": [
                        "continues",
                        "supersedes",
                        "references",
                        "follows_up",
                        "blocks",
                        "related_to",
                    ],
                    "default": "related_to",
                },
                "description": {
                    "type": "string",
                    "description": "Contextual note explaining why meetings are linked.",
                },
            },
            "required": ["source_meeting_id", "target_meeting_id"],
        },
    },
}

MEETING_CORRECT_RECORD_SCHEMA: Dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "meeting_correct_record",
        "description": "Applies an owner correction to an existing meeting record, logging provenance and maintaining audit immutability.",
        "parameters": {
            "type": "object",
            "properties": {
                "meeting_id": {
                    "type": "string",
                    "description": "Target meeting ID.",
                },
                "target_field": {
                    "type": "string",
                    "description": "Field name to correct (e.g., 'decisions[0].decided_by').",
                },
                "original_value": {
                    "type": "string",
                    "description": "Previous value.",
                },
                "corrected_value": {
                    "type": "string",
                    "description": "Authoritative corrected value.",
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for correction.",
                },
            },
            "required": ["meeting_id", "target_field", "original_value", "corrected_value"],
        },
    },
}

MEETING_ROUTE_SELECT_SCHEMA: Dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "meeting_route_select",
        "description": "Determines optimal STT and extraction provider based on current meeting strategy (LATENCY, COST, QUALITY, BALANCED).",
        "parameters": {
            "type": "object",
            "properties": {
                "strategy": {
                    "type": "string",
                    "enum": ["LATENCY", "COST", "QUALITY", "BALANCED"],
                    "default": "BALANCED",
                },
            },
        },
    },
}

ALL_SCHEMAS: List[Dict[str, Any]] = [
    MEETING_TRANSCRIBE_SCHEMA,
    MEETING_EXTRACT_SCHEMA,
    MEETING_MEMORY_STORE_SCHEMA,
    MEETING_MEMORY_QUERY_SCHEMA,
    MEETING_LINK_RELATED_SCHEMA,
    MEETING_CORRECT_RECORD_SCHEMA,
    MEETING_ROUTE_SELECT_SCHEMA,
]
