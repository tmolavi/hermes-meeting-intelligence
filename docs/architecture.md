# Architecture & Component Flow

Hermes Meeting Intelligence provides a modular, provider-agnostic system designed to turn spoken meeting audio or raw transcripts into structured, queryable, persistent intelligence for **Hermes Agent**.

```
                           Audio Stream / Meeting Transcript
                                          │
                                          ▼
                      ┌───────────────────────────────────────┐
                      │            Provider Router            │
                      │  (LATENCY | COST | QUALITY | BALANCED)│
                      └───────────────────┬───────────────────┘
                                          │
                   ┌──────────────────────┴──────────────────────┐
                   ▼                                             ▼
        ┌─────────────────────┐                       ┌─────────────────────┐
        │    STT Providers    │                       │ Extraction Providers│
        │ ├── Mock            │                       │ ├── Mock (Rules)    │
        │ ├── Groq Whisper    │                       │ ├── Groq LLaMA-3    │
        │ ├── Deepgram Nova   │                       │ └── OpenAI GPT-4o   │
        │ ├── OpenAI Whisper  │                       └──────────┬──────────┘
        │ └── Local Whisper   │                                  │
        └──────────┬──────────┘                                  │
                   │                                             │
                   └──────────────────────┬──────────────────────┘
                                          ▼
                      ┌───────────────────────────────────────┐
                      │       Meeting Pipeline & Schema       │
                      │      (Decisions, Actions, Topics)     │
                      └───────────────────┬───────────────────┘
                                          │
                                          ▼
                      ┌───────────────────────────────────────┐
                      │    Persistent SQLite Memory Store     │
                      │    (Relational Tables + Inverted FTS) │
                      └───────────────────┬───────────────────┘
                                          │
                                          ▼
                      ┌───────────────────────────────────────┐
                      │    Cross-Meeting Context Retriever    │
                      │   (Decisions, Actions, Graph Lineage) │
                      └───────────────────┬───────────────────┘
                                          │
                                          ▼
                      ┌───────────────────────────────────────┐
                      │             Hermes Agent              │
                      │  (Reasoning & Autonomous Execution)   │
                      └───────────────────────────────────────┘
```

## Layer Separation

### 1. Provider & Tool Layer
- **Speech-to-Text (STT)**: Decoupled adapters convert audio bytes into timestamped `SpeakerSegment` records. Supports both local CPU execution and high-throughput cloud endpoints.
- **Extraction**: Formats raw conversational turns into atomic decisions, proposals, disagreements, questions, action items, entities, and evidence references.

### 2. Hermes Skills vs. Plugins
- **Skills (`skills/`)**: Declarative procedural guidelines (following `agentskills.io` standard) that instruct Hermes how to reason about meetings, detect unresolved friction, navigate memory, and avoid psychological speculation.
- **Plugin (`plugin.yaml` & `tools.py`)**: The executable Python code registering tool schemas (`meeting_transcribe`, `meeting_extract`, `meeting_memory_query`, `meeting_memory_store`, `meeting_link_related`, `meeting_correct_record`, `meeting_route_select`) with Hermes Agent runtime.

### 3. Persistent Memory & Cross-Meeting Graph
- Stores full `MeetingRecord` instances inside SQLite with dedicated index tables for fast relational filtering.
- Implements topological relationship tracking (`continues`, `supersedes`, `references`, `follows_up`, `blocks`, `related_to`).
- Supports **Owner Corrections** with complete audit provenance to ensure ground-truth accuracy is never silently modified.
