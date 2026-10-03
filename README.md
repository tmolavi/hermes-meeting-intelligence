# Hermes Meeting Intelligence

> Reusable meeting intelligence skills, tools, and persistent memory for Hermes Agent.

<p align="center">
  <a href="README.md"><b>English</b></a> •
  <a href="README.fa.md"><b>فارسی</b></a> •
  <a href="README.tr.md"><b>Türkçe</b></a> •
  <a href="README.az.md"><b>Azərbaycan dili</b></a> •
  <a href="README.ar.md"><b>العربية</b></a>
</p>

<p align="center">
  <a href="https://github.com/tmolavi/hermes-meeting-intelligence/actions/workflows/ci.yml"><img src="https://github.com/tmolavi/hermes-meeting-intelligence/actions/workflows/ci.yml/badge.svg" alt="CI Status"></a>
  <a href="https://pypi.org/project/hermes-meeting-intelligence/"><img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg" alt="Python Versions"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-green.svg" alt="License"></a>
</p>

---

**Hermes Meeting Intelligence** is an open-source, provider-agnostic framework and official plugin for [Hermes Agent](https://github.com/NousResearch/hermes-agent). It provides modular speech transcription, structured intelligence extraction (decisions, proposals, disagreements, action items, evidence), persistent cross-meeting SQLite memory, and latency-aware real-time routing.

---

## Why this project exists

Modern digital visibility is no longer only about ranking web pages. AI systems and answer engines increasingly retrieve, interpret, connect, remember, and cite information.

My work in SEO, Generative Engine Optimization (GEO), and AI Visibility therefore increasingly involves understanding how information is structured, retrieved, evaluated, remembered, and surfaced by intelligent systems.

Meeting intelligence presents identical foundational information architecture challenges:
- *Who said what?*
- *What concrete decisions were finalized?*
- *What evidence or quotations support each claim?*
- *How does this discussion relate to decisions made three meetings ago?*
- *What information is authoritative versus speculative?*

This project emerged from engineering and research around structured information retrieval, entity understanding, and persistent agent memory. When a reusable component solves a real problem, I prefer to document and publish it so others do not have to spend the same time solving it again.

---

## What it does

- **Structured Intelligence Extraction**: Transforms conversational meeting dialogue into strongly typed `MeetingRecord` objects capturing decisions, proposals, disagreements, questions, action items, entities, and verbatim evidence quotes.
- **Persistent Cross-Meeting Memory**: Stores meeting records in a local, zero-daemon SQLite database with dedicated relational tables for cross-meeting querying without overloading LLM context windows.
- **Topological Lineage & Relations**: Explicitly links related sessions (`continues`, `supersedes`, `references`, `follows_up`, `blocks`, `related_to`).
- **Owner Corrections with Audit Provenance**: Allows meeting owners to correct extracted data while preserving complete audit logs of original values and reasons.
- **Pluggable Multi-Provider Architecture**: Decoupled adapters for OpenAI, Groq, Deepgram, and local Faster-Whisper, with deterministic offline mock fallbacks for testing and CI.
- **Hermes Agent Plugin & Skills**: Installs as a native Hermes Agent plugin exposing 7 tools and 5 bundled procedural skills following the `agentskills.io` standard.

---

## What it does not do

- **Does NOT bundle heavy model weights**: No multi-gigabyte checkpoints or binary models are committed to this repository. All inference runs via user-selected local or remote providers.
- **Does NOT perform psychological or emotional profiling**: The extraction engine sticks strictly to explicit statements, consensus, and evidence. It does not speculate on unspoken intentions or personality traits.
- **Does NOT silently overwrite historical records**: Past meeting truth is immutable. Any owner update creates a traceable `OwnerCorrection` entry.
- **Does NOT mandate cloud APIs or GPUs**: The core system is fully functional on standard CPU environments using local or mock providers.

---

## Architecture

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

---

## Skills, Tools, Providers and Models

An important architectural distinction in this repository:

- **Skill**: What Hermes learns to do (procedural workflow and heuristics defined in `skills/`).
- **Tool / Plugin**: Executable Python handlers registered with the Hermes Agent runtime.
- **Model**: The neural network architecture performing inference (e.g. `whisper-large-v3`, `gpt-4o`).
- **Provider**: The endpoint supplying model inference (e.g. Groq, OpenAI, local CPU).

| Capability | Hermes Skill | Tool / Plugin | Model / Provider Required | CPU / GPU | Cost Notes | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Audio Ingestion & STT** | `meeting-listening` | `meeting_transcribe` | Mock, Faster-Whisper, Groq, Deepgram, OpenAI | CPU-first (GPU optional) | Free (local/mock) or paid API | **Available** |
| **Structured Intelligence** | `meeting-extraction` | `meeting_extract` | Mock Heuristics, Groq LLaMA-3, OpenAI GPT-4o | CPU-first | Free (local/mock) or paid API | **Available** |
| **Persistent Meeting Store** | `meeting-memory` | `meeting_memory_store` | SQLite (Zero external daemons) | CPU | Free | **Available** |
| **Cross-Meeting Retrieval** | `meeting-memory` | `meeting_memory_query` | Relational + FTS Queries | CPU | Free | **Available** |
| **Meeting Lineage Linking** | `meeting-memory` | `meeting_link_related` | Graph schema | CPU | Free | **Available** |
| **Audit & Owner Correction** | `meeting-memory` | `meeting_correct_record` | Schema validator | CPU | Free | **Available** |
| **Adaptive Route Selection** | `realtime-routing` | `meeting_route_select` | Latency / Cost Router | CPU | Free | **Available** |
| **Speaker Diarization** | `speaker-identification` | `meeting_transcribe` | Deepgram Nova or PyAnnote | GPU rec. for local | Free tier / Paid API | **Available (Provider-dependent)** |
| **Dense Vector Embeddings** | `meeting-memory` | `meeting_memory_query` | `sqlite-vec` / sentence-transformers | CPU / GPU | Free (local) | **Experimental** |
| **Live Avatar WebSockets** | `realtime-routing` | N/A | Bidirectional Gateway | CPU / GPU | Free / Custom | **Planned** |

---

## Current capabilities

- **Deterministic Verification**: Mock providers execute 100% offline in CI environments with zero cost.
- **Pydantic v2 Schema**: Complete data validation and serialization.
- **Multilingual Support**: Primary support for English (`en`), Persian (`fa`), Turkish (`tr`), Azerbaijani (`az`), and Arabic (`ar`).
- **Audit Immutability**: Full provenance tracking (pipeline version, provider, source hash, timestamp).

---

## Installation

### 1. As a Hermes Agent Plugin

Install directly using the Hermes CLI:

```bash
hermes plugins install tmolavi/hermes-meeting-intelligence
```

Or clone into your local Hermes plugins directory:

```bash
git clone https://github.com/tmolavi/hermes-meeting-intelligence.git ~/.hermes/plugins/hermes-meeting-intelligence
```

### 2. Standalone Python Package via `pip` or `uv`

```bash
# Core package (CPU-first, zero heavy dependencies)
pip install hermes-meeting-intelligence

# With local Faster-Whisper support
pip install "hermes-meeting-intelligence[local-stt]"

# Development dependencies (testing, linting)
pip install "hermes-meeting-intelligence[dev]"
```

---

## Quick Start

### Python API

```python
import asyncio
from hermes_meeting_intelligence import MeetingPipeline, MeetingMemoryStore


async def main():
    # 1. Initialize pipeline (defaults to offline deterministic provider)
    pipeline = MeetingPipeline()

    # 2. Extract intelligence from a transcript
    transcript = """
    [Alice Chen]: We decided to use SQLite for long-term meeting memory.
    [Bob Martin]: Agreed. Bob will implement the schema and test suite by Friday.
    """
    record = await pipeline.process_transcript(transcript, title="Architecture Sync")

    # 3. Store in persistent memory
    store = MeetingMemoryStore("~/.hermes/meeting_memory.sqlite")
    meeting_id = store.save_meeting(record)
    print(f"Stored meeting {meeting_id} with {len(record.decisions)} decision(s).")


if __name__ == "__main__":
    asyncio.run(main())
```

### CLI (`hermes-meeting`)

```bash
# Ingest a meeting transcript text file
hermes-meeting ingest transcript.txt --title "Q4 Planning"

# Query prior decisions
hermes-meeting query decisions "SQLite"

# Query open action items
hermes-meeting query actions

# Validate a MeetingRecord JSON file
hermes-meeting validate examples/synthetic_meetings/meeting_01_kickoff_decision.json
```

---

## Example: Sequential Cross-Meeting Intelligence

The repository includes a 3-meeting synthetic scenario in `examples/synthetic_meetings/`:

1. **Meeting 1 (`meeting_01_kickoff_decision.json`)**:
   - Decision made: Migrate memory storage layer to SQLite.
   - Action item assigned: Bob to implement memory store by Friday.
2. **Meeting 2 (`meeting_02_followup_disagreement.json`)**:
   - Disagreement: Clara proposes 1.5s real-time buffer; Bob objects due to CPU limitations.
   - Tabled awaiting benchmark evidence. Linked to Meeting 1.
3. **Meeting 3 (`meeting_03_resolution_and_actions.json`)**:
   - Resolution: Clara presents benchmarks; team adopts adaptive chunking (1.5s for cloud LPU, 3.0s for local CPU).
   - Verification: Action item from Meeting 1 verified completed. Linked to Meetings 1 and 2.

Run the demo:
```bash
python examples/memory_retrieval_demo.py
```

---

## Meeting Record Schema

Every meeting is serialized into a portable JSON structure. See [docs/schema-reference.md](docs/schema-reference.md) for full details.

```json
{
  "meeting_id": "mtg_synth_001",
  "title": "Project Kickoff",
  "started_at": "2026-10-01T09:00:00Z",
  "language": "en",
  "participants": [{"speaker_id": "speaker_alice", "name": "Alice Chen"}],
  "speaker_segments": [{"start": 0.0, "end": 12.5, "speaker_id": "speaker_alice", "text": "..."}],
  "decisions": [{"decision_id": "dec_001", "description": "Adopt SQLite", "evidence_quote": "..."}],
  "action_items": [{"action_id": "act_001", "description": "Implement store", "assignee": "Bob", "status": "pending"}],
  "owner_corrections": [],
  "provenance": {"pipeline_version": "0.1.0", "stt_provider": "mock"}
}
```

---

## Real-Time Routing

Configure routing priorities based on operational needs:

- **`LATENCY`**: Uses Groq LPU Whisper / LLaMA-3 or Deepgram Nova for sub-200ms TTFT in active spoken interaction.
- **`COST`**: Uses local CPU Faster-Whisper and local models for $0.00 cloud spend.
- **`QUALITY`**: Uses OpenAI GPT-4o / Whisper for high-stakes executive analysis.
- **`BALANCED`**: Optimal compromise between turnaround and semantic precision.

See [docs/real-time-routing.md](docs/real-time-routing.md) for details.

---

## Privacy and Security

- **API Keys**: Loaded from environment variables (`OPENAI_API_KEY`, `GROQ_API_KEY`, `DEEPGRAM_API_KEY`) or Hermes configuration. Never written to git or database.
- **Biometric Notice**: Voice embeddings require explicit participant opt-in.
- **Air-Gapped Compatibility**: Full support for local CPU Faster-Whisper and local LLMs without external network calls.
- See [SECURITY.md](SECURITY.md) for vulnerability reporting and security posture.

---

## Benchmarks & Reproducibility

- **Test Suite**: 100% offline unit tests verifying schema integrity, router fallbacks, memory linking, and CLI commands.
- **Synthetic Data Only**: All fixtures in `examples/` are synthetic. No private corporate recordings are included.
- **CI Verification**: GitHub Actions runs automated tests, Ruff linter, and MyPy type checks across Python 3.10–3.13.

---

## Limitations

- Native local speaker diarization currently requires optional external libraries (e.g. `pyannote-audio`), which require discrete GPU compute for optimal performance.
- Dense vector semantic search is currently experimental; production defaults use SQLite relational and inverted text search.

---

## Roadmap

- **v0.2.0**: Native SQLite vector extension (`sqlite-vec`) integration for hybrid dense/sparse retrieval.
- **v0.3.0**: Real-time duplex WebSocket gateway for live conversational avatars.
- **v0.4.0**: Autonomous rolling summary skills for long multi-hour conferences.

See [ROADMAP.md](ROADMAP.md) for details.

---

## Learn, Teach, Build Something That Lasts

Professional knowledge compounds when practical solutions are documented and shared openly.

We all lose time solving problems someone else has already solved. When I build something reusable during my research or engineering work, I try to document and release the reusable part.

No gatekeeping. No inflated claims. Learn from others, teach what you verify, and leave behind something useful.

---

## About the Author

Created and maintained by **Taqi Molavi (Taghi Molavi)**.

My primary work focuses on SEO, Generative Engine Optimization (GEO), AI Visibility, AI Search, and measurement systems. That work increasingly overlaps with structured retrieval, entity understanding, evidence verification, agent memory, and intelligent information architectures.

- Website: [molavi.pro](https://molavi.pro)
- GitHub: [@tmolavi](https://github.com/tmolavi)

---

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before submitting pull requests.

---

## License

This project is licensed under the **Apache-2.0 License**. See the [LICENSE](LICENSE) file for details. Third-party provider APIs and optional local model weights are subject to their respective vendor licenses.

---

## Citation

If you use Hermes Meeting Intelligence in your research or software, please cite:

```bibtex
@software{molavi2026hermesmeeting,
  author = {Molavi, Taqi},
  title = {Hermes Meeting Intelligence: Reusable Meeting Intelligence Skills and Cross-Meeting Memory for Hermes Agent},
  year = {2026},
  url = {https://github.com/tmolavi/hermes-meeting-intelligence}
}
```
