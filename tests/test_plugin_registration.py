"""
Tests for Hermes Agent Plugin Registration and Tool Handlers.
"""

import pytest

from hermes_meeting_intelligence.plugin import register
from hermes_meeting_intelligence.schemas import ALL_SCHEMAS
from hermes_meeting_intelligence.tools import (
    handle_meeting_correct_record,
    handle_meeting_extract,
    handle_meeting_memory_query,
    handle_meeting_route_select,
    handle_meeting_transcribe,
)


class MockHermesContext:
    """Simulates Hermes Agent plugin loading context."""

    def __init__(self):
        self.registered_tools = []
        self.config = {"db_path": ":memory:"}

    def register_tool(self, schema, handler):
        self.registered_tools.append({"schema": schema, "handler": handler})


def test_hermes_plugin_register():
    ctx = MockHermesContext()
    register(ctx)

    assert len(ctx.registered_tools) == len(ALL_SCHEMAS)
    registered_names = [t["schema"]["function"]["name"] for t in ctx.registered_tools]
    assert "meeting_transcribe" in registered_names
    assert "meeting_extract" in registered_names
    assert "meeting_memory_query" in registered_names
    assert "meeting_memory_store" in registered_names
    assert "meeting_link_related" in registered_names
    assert "meeting_correct_record" in registered_names
    assert "meeting_route_select" in registered_names


@pytest.mark.asyncio
async def test_tool_handlers_end_to_end():
    # 1. Transcribe mock
    trans_res = await handle_meeting_transcribe(
        audio_path="[Alice]: We decided to launch v0.1.0 on Monday."
    )
    assert trans_res["segment_count"] == 1

    # 2. Extract and store
    ext_res = await handle_meeting_extract(
        transcript=trans_res["full_text"],
        title="Launch Alignment",
        save_to_memory=True,
    )
    meeting_id = ext_res["meeting_id"]
    assert meeting_id is not None
    assert ext_res["decisions_count"] >= 1

    # 3. Query
    query_res = await handle_meeting_memory_query(query_type="decisions", query_term="v0.1.0")
    assert len(query_res["results"]) >= 1

    # 4. Route selection
    route_res = await handle_meeting_route_select(strategy="LATENCY")
    assert route_res["strategy_used"] == "LATENCY"

    # 5. Correction
    corr_res = await handle_meeting_correct_record(
        meeting_id=meeting_id,
        target_field="decisions[0].description",
        original_value="Launch v0.1.0 on Monday",
        corrected_value="Launch v0.1.0 on Tuesday after CI checks",
        reason="Owner rescheduled due to QA gate",
    )
    assert corr_res["status"] == "corrected"
