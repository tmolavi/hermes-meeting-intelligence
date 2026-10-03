# Provider & Model Requirement Matrix

This matrix outlines provider dependencies, execution modes, hardware requirements, and cost classifications.

| Provider / Adapter | Purpose | Execution Mode | CPU Capable | GPU Recommended | Cost Classification | License / Terms | Default Tested Model |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Mock Provider** | STT & Extraction | Local / In-Process | Yes | No | **Free (Zero cost)** | Apache-2.0 | Rule Heuristics |
| **Local Faster-Whisper** | STT | Local Self-Hosted | Yes | Yes (for speed) | **Free (Compute only)** | MIT / Apache-2.0 | `whisper-base` / `large-v3` |
| **Groq API** | STT & Fast Extraction | Remote Cloud API | Yes (API client) | No (Cloud LPU) | **Paid / Free Tier** | Proprietary API | `whisper-large-v3`, `llama-3.3-70b` |
| **Deepgram Nova** | STT & Diarization | Remote Cloud API | Yes (API client) | No (Cloud GPU) | **Paid / Free Tier** | Proprietary API | `nova-2` |
| **OpenAI API** | STT & Reasoning | Remote Cloud API | Yes (API client) | No (Cloud GPU) | **Paid API** | Proprietary API | `whisper-1`, `gpt-4o-mini` |

## Cost Clarifications

- **Free**: No API billing, run entirely on your local CPU or GPU.
- **Free Tier**: Remote vendor offers initial promotional credits or rate-limited free tiers.
- **Paid**: Usage-based billing per audio minute or LLM token.
- **License Restricted**: Third-party models (e.g. model weights) may have specific usage restrictions distinct from this repository's Apache-2.0 software license.
