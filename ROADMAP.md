# Project Roadmap

This document outlines planned milestones and ongoing research directions for **Hermes Meeting Intelligence**.

## Capability Status Overview

| Capability | Current Status | Target Milestone | Description |
| :--- | :--- | :--- | :--- |
| **Meeting Record Schema (Pydantic v2)** | Available | v0.1.0 | Standardized data contract for decisions, actions, evidence. |
| **Persistent SQLite Meeting Store** | Available | v0.1.0 | Relational and full-text search indexing of meetings. |
| **Hermes Plugin Tool Integration** | Available | v0.1.0 | Tools registered via `plugin.yaml` and `register(ctx)`. |
| **Bundled Hermes Skills (5 skills)** | Available | v0.1.0 | Procedural knowledge in `skills/` following `agentskills.io`. |
| **Multi-Provider STT & Router** | Available | v0.1.0 | Mock, OpenAI, Groq, Deepgram, Local Faster-Whisper. |
| **Offline Test Suite & CI** | Available | v0.1.0 | Comprehensive unit, schema, and CLI tests. |
| **Multilingual Documentation (5 langs)** | Available | v0.1.0 | English, Persian, Turkish, Azerbaijani, Arabic. |
| **Native Vector Embeddings in SQLite** | Experimental | v0.2.0 | Hybrid BM25 + dense vector semantic retrieval with sqlite-vec. |
| **Automated Speaker Profile Enrollment** | Planned | v0.3.0 | Secure, opt-in speaker voice embedding enrollment. |
| **Real-Time WebSocket Streaming Gateway** | Planned | v0.3.0 | Full duplex audio streaming gateway for conversational avatars. |
| **Live Multi-Speaker Meeting Summaries** | Planned | v0.4.0 | Continuous rolling summaries with mid-meeting catchup skill. |
