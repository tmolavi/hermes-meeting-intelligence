# Contributing to Hermes Meeting Intelligence

Thank you for your interest in contributing to **Hermes Meeting Intelligence**.

We welcome contributions from developers, researchers, and practitioners passionate about open, auditable, and reproducible agent architectures.

## Core Philosophy

1. **Useful before promotional.**
2. **Evidence before claims.**
3. **Learn → Teach → Create something that lasts.**

---

## Development Setup

### Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13
- [`uv`](https://docs.astral.sh/uv/) or standard Python `venv` + `pip`
- Git

### Initializing Environment

```bash
# 1. Clone repository
git clone https://github.com/tmolavi/hermes-meeting-intelligence.git
cd hermes-meeting-intelligence

# 2. Create virtual environment using uv
uv venv --python 3.12 .venv
source .venv/bin/activate

# 3. Install in editable mode with development dependencies
uv pip install -e ".[dev]"
```

---

## Running Tests & Linters

All pull requests must pass tests, linting, and formatting checks before merging:

```bash
# Run pytest test suite
pytest

# Run linter and formatting checks
ruff check .
ruff format --check .

# Run static type checking
mypy hermes_meeting_intelligence
```

---

## Adding a New Provider

To add a new Speech-to-Text or Extraction provider:
1. Subclass `BaseSTTProvider` or `BaseExtractionProvider` in `hermes_meeting_intelligence/providers/`.
2. Implement property `is_available` and asynchronous methods `transcribe` or `extract_intelligence`.
3. Register the new provider in `ProviderRouter` in `hermes_meeting_intelligence/providers/router.py`.
4. Add deterministic unit tests mocking network calls in `tests/test_providers.py`. Ordinary CI should never call paid external endpoints.

---

## Adding or Improving Skills

Hermes Skills are stored under `skills/<skill-name>/SKILL.md` following the [agentskills.io](https://agentskills.io) standard:
- Ensure the frontmatter contains valid `name`, `description`, and `version`.
- Write clear procedural instructions without claiming unverified capabilities.

---

## Pull Request Guidelines

1. **Atomic Commits**: Write clear, descriptive commit messages.
2. **Reproducibility**: If introducing new heuristics or benchmarks, provide full test methodology, environment details, and sample data.
3. **No Secrets / Checkpoints**: Never commit API keys, audio dumps of private meetings, or binary model weights.
