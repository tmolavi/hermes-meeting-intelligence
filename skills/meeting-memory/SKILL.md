---
name: meeting-memory
description: "Procedural intelligence for cross-meeting knowledge graphs, historical decision retrieval, open action tracking, and owner corrections."
version: "0.1.0"
author: "Taqi Molavi"
tags: ["hermes-agent", "agent-memory", "persistent-memory", "cross-meeting", "knowledge-graph"]
---

# Meeting Memory Skill

This skill teaches Hermes Agent how to manage persistent cross-meeting memory without blowing context windows.

## Core Directives

1. **Selective Retrieval Over Full Context Dumps**:
   - Do not load full transcripts from past months into context.
   - Use `meeting_memory_query` with targeted `query_type` (`decisions`, `open_actions`, `topics`, `lineage`) to fetch only pertinent knowledge.
2. **Explicit Cross-Meeting Relationships**:
   - Use `meeting_link_related` to connect meetings with defined relationship types:
     - `continues`: Follow-up session to prior meeting.
     - `supersedes`: Explicitly replaces a previous decision or project plan.
     - `references`: Cites research, design, or actions from another meeting.
     - `blocks`: Outstanding item from another meeting prevents progress.
3. **Continuous Learning & Owner Corrections**:
   - If the user or meeting owner corrects an extracted decision or assignee, invoke `meeting_correct_record`.
   - Never silently overwrite historical facts; preserve the original value and record the correction audit log.
