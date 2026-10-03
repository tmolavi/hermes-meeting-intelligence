"""
Hermes Agent Plugin Registration Entrypoint.
"""

from __future__ import annotations

import logging
from typing import Any

from hermes_meeting_intelligence.schemas import (
    MEETING_CORRECT_RECORD_SCHEMA,
    MEETING_EXTRACT_SCHEMA,
    MEETING_LINK_RELATED_SCHEMA,
    MEETING_MEMORY_QUERY_SCHEMA,
    MEETING_MEMORY_STORE_SCHEMA,
    MEETING_ROUTE_SELECT_SCHEMA,
    MEETING_TRANSCRIBE_SCHEMA,
)
from hermes_meeting_intelligence.tools import (
    get_store,
    handle_meeting_correct_record,
    handle_meeting_extract,
    handle_meeting_link_related,
    handle_meeting_memory_query,
    handle_meeting_memory_store,
    handle_meeting_route_select,
    handle_meeting_transcribe,
)

logger = logging.getLogger(__name__)


def register(ctx: Any) -> None:
    """Hermes Agent plugin registration callback."""
    logger.info("Initializing Hermes Meeting Intelligence plugin...")

    # Optional config extraction if provided by Hermes context
    if hasattr(ctx, "config") and isinstance(ctx.config, dict):
        db_path = ctx.config.get("db_path")
        if db_path:
            get_store(db_path)

    # Register each tool schema with its corresponding handler
    ctx.register_tool(MEETING_TRANSCRIBE_SCHEMA, handle_meeting_transcribe)
    ctx.register_tool(MEETING_EXTRACT_SCHEMA, handle_meeting_extract)
    ctx.register_tool(MEETING_MEMORY_STORE_SCHEMA, handle_meeting_memory_store)
    ctx.register_tool(MEETING_MEMORY_QUERY_SCHEMA, handle_meeting_memory_query)
    ctx.register_tool(MEETING_LINK_RELATED_SCHEMA, handle_meeting_link_related)
    ctx.register_tool(MEETING_CORRECT_RECORD_SCHEMA, handle_meeting_correct_record)
    ctx.register_tool(MEETING_ROUTE_SELECT_SCHEMA, handle_meeting_route_select)

    logger.info("Hermes Meeting Intelligence tools successfully registered.")
