"""
Hermes Agent Tool Handlers for Meeting Intelligence.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

from hermes_meeting_intelligence.memory.retriever import MeetingMemoryRetriever
from hermes_meeting_intelligence.memory.store import MeetingMemoryStore
from hermes_meeting_intelligence.models.routing import RoutingStrategy
from hermes_meeting_intelligence.models.schema import MeetingRecord, RelationshipType
from hermes_meeting_intelligence.pipeline.extractor import MeetingPipeline
from hermes_meeting_intelligence.providers.router import ProviderRouter

_global_store: Optional[MeetingMemoryStore] = None
_global_router: Optional[ProviderRouter] = None
_global_pipeline: Optional[MeetingPipeline] = None


def get_store(db_path: Optional[str] = None) -> MeetingMemoryStore:
    global _global_store
    if _global_store is None:
        path = db_path or os.getenv("HERMES_MEETING_DB_PATH") or "~/.hermes/meeting_memory.sqlite"
        _global_store = MeetingMemoryStore(path)
    return _global_store


def get_router() -> ProviderRouter:
    global _global_router
    if _global_router is None:
        _global_router = ProviderRouter()
    return _global_router


def get_pipeline() -> MeetingPipeline:
    global _global_pipeline
    if _global_pipeline is None:
        _global_pipeline = MeetingPipeline(router=get_router())
    return _global_pipeline


async def handle_meeting_transcribe(
    audio_path: str,
    language: Optional[str] = None,
    diarize: bool = True,
    provider: Optional[str] = None,
) -> Dict[str, Any]:
    router = get_router()
    stt = router.get_stt_provider(provider)
    segments = await stt.transcribe(audio_path, language=language, diarize=diarize)
    return {
        "provider": stt.name,
        "segment_count": len(segments),
        "segments": [s.model_dump() for s in segments],
        "full_text": "\n".join([f"[{s.speaker_id}]: {s.text}" for s in segments]),
    }


async def handle_meeting_extract(
    transcript: str,
    title: str,
    language: str = "en",
    save_to_memory: bool = True,
) -> Dict[str, Any]:
    pipeline = get_pipeline()
    record = await pipeline.process_transcript(
        transcript_text=transcript,
        title=title,
        language=language,
    )

    if save_to_memory:
        store = get_store()
        store.save_meeting(record)

    return {
        "meeting_id": record.meeting_id,
        "title": record.title,
        "decisions_count": len(record.decisions),
        "action_items_count": len(record.action_items),
        "topics": record.topics,
        "record": record.model_dump(),
    }


async def handle_meeting_memory_store(meeting_record_json: str) -> Dict[str, Any]:
    record_dict = (
        json.loads(meeting_record_json)
        if isinstance(meeting_record_json, str)
        else meeting_record_json
    )
    record = MeetingRecord.model_validate(record_dict)
    store = get_store()
    meeting_id = store.save_meeting(record)
    return {"status": "saved", "meeting_id": meeting_id}


async def handle_meeting_memory_query(
    query_type: str,
    query_term: Optional[str] = None,
    assignee: Optional[str] = None,
    limit: int = 10,
) -> Dict[str, Any]:
    store = get_store()
    retriever = MeetingMemoryRetriever(store)
    results: Any = None

    if query_type == "decisions":
        results = retriever.search_decisions(query_term or "", limit=limit)
    elif query_type == "open_actions":
        results = retriever.search_open_actions(assignee=assignee or query_term, limit=limit)
    elif query_type == "topics":
        results = retriever.search_topics(query_term or "", limit=limit)
    elif query_type == "recent_meetings":
        results = store.list_meetings(limit=limit)
    elif query_type == "lineage":
        if not query_term:
            return {"error": "query_term containing meeting_id is required for lineage query"}
        results = retriever.get_related_lineage(query_term)
    else:
        return {"error": f"Unknown query_type: {query_type}"}

    return {"query_type": query_type, "results": results}


async def handle_meeting_link_related(
    source_meeting_id: str,
    target_meeting_id: str,
    relationship_type: str = "related_to",
    description: Optional[str] = None,
) -> Dict[str, Any]:
    store = get_store()
    rel_type = RelationshipType(relationship_type)
    success = store.add_relationship(
        source_meeting_id=source_meeting_id,
        target_meeting_id=target_meeting_id,
        relationship_type=rel_type,
        description=description,
    )
    return {
        "status": "linked" if success else "failed",
        "source_meeting_id": source_meeting_id,
        "target_meeting_id": target_meeting_id,
        "relationship_type": rel_type.value,
    }


async def handle_meeting_correct_record(
    meeting_id: str,
    target_field: str,
    original_value: str,
    corrected_value: str,
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    store = get_store()
    corr = store.record_correction(
        meeting_id=meeting_id,
        target_field=target_field,
        original_value=original_value,
        corrected_value=corrected_value,
        reason=reason,
    )
    return {
        "status": "corrected",
        "correction_id": corr.correction_id,
        "meeting_id": meeting_id,
        "target_field": target_field,
        "corrected_at": corr.corrected_at.isoformat(),
    }


async def handle_meeting_route_select(strategy: str = "BALANCED") -> Dict[str, Any]:
    router = get_router()
    strat_enum = RoutingStrategy(strategy)
    decision = router.select_route(strat_enum)
    return decision.model_dump()
