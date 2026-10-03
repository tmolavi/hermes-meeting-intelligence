# Changelog

All notable changes to **Hermes Meeting Intelligence** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2026-10-03

### Added
- **Core Schema**: Portable Pydantic v2 `MeetingRecord` schema supporting structured decisions, proposals, disagreements, questions, action items, evidence quotes, and owner corrections.
- **Provider Layer**:
  - `MockSTTProvider` and `MockExtractionProvider` for deterministic, zero-cost offline testing and CI.
  - `OpenAIProvider` for cloud Whisper STT and GPT-4o structured extraction.
  - `GroqProvider` for ultra-low latency LPU Whisper transcription and fast LLaMA extraction.
  - `DeepgramProvider` for streaming STT with native speaker diarization.
  - `LocalWhisperProvider` for self-hosted CPU/GPU Faster-Whisper execution.
  - `ProviderRouter` for strategy-based routing (`LATENCY`, `COST`, `QUALITY`, `BALANCED`).
- **Meeting Memory**:
  - Persistent SQLite store (`MeetingMemoryStore`) with relational indexes for decisions, actions, topics, and entities.
  - Cross-meeting query and retrieval engine (`MeetingMemoryRetriever`).
  - Meeting graph analyzer (`MeetingGraphAnalyzer`) for automated cross-meeting lineage discovery.
- **Hermes Agent Plugin**:
  - `plugin.yaml` manifest and entrypoint registration (`register(ctx)`).
  - 7 native tool schemas: `meeting_transcribe`, `meeting_extract`, `meeting_memory_store`, `meeting_memory_query`, `meeting_link_related`, `meeting_correct_record`, `meeting_route_select`.
- **Hermes Skills**:
  - `skills/meeting-listening/SKILL.md`
  - `skills/meeting-extraction/SKILL.md`
  - `skills/meeting-memory/SKILL.md`
  - `skills/speaker-identification/SKILL.md`
  - `skills/realtime-routing/SKILL.md`
- **CLI & Utilities**:
  - `hermes-meeting` command-line tool with `ingest`, `query`, `list`, and `validate` subcommands.
- **Synthetic Examples & Verification**:
  - 3 sequential synthetic meeting fixtures illustrating kickoff, disagreement, and cross-meeting resolution.
  - Quickstart and memory retrieval demo scripts.
- **Documentation & Governance**:
  - Multilingual READMEs: English (canonical), Persian (`README.fa.md`), Turkish (`README.tr.md`), Azerbaijani (`README.az.md`), and Arabic (`README.ar.md`).
  - Architecture, schema reference, provider matrix, hardware guide, and real-time routing documentation.
  - Full CI test suite across Python 3.10–3.13.
