# Synthetic Meeting Intelligence Examples

This directory contains synthetic (fictional) datasets and executable Python scripts demonstrating Hermes Meeting Intelligence workflows.

> [!NOTE]
> All recordings, transcripts, names, and organizations in this directory are 100% synthetic and created exclusively for testing, reproducibility, and demonstration purposes. No private or real meeting data is included.

## Contents

- `synthetic_meetings/`:
  - `meeting_01_kickoff_decision.json`: Demonstrates a kickoff discussion establishing architectural choices (SQLite, Pydantic) and assigning an initial action item.
  - `meeting_02_followup_disagreement.json`: Demonstrates a follow-up meeting with a technical disagreement over audio chunk buffer sizes and a tabled resolution awaiting benchmarks.
  - `meeting_03_resolution_and_actions.json`: Demonstrates resolution of the disagreement via benchmark evidence, completion of previous action items, and linking back to meetings 1 and 2.
- `quickstart_pipeline.py`: A self-contained script demonstrating transcript ingestion, extraction, and SQLite persistence.
- `memory_retrieval_demo.py`: Demonstrates loading sequential synthetic meetings and querying cross-meeting decisions, open actions, and lineage graphs.

## Running Examples

Execute directly with Python:

```bash
# Run quickstart pipeline
python examples/quickstart_pipeline.py

# Run cross-meeting memory query demo
python examples/memory_retrieval_demo.py
```
