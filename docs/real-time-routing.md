# Real-Time Routing Strategy

Meeting intelligence applications vary dramatically across real-time conversational agents, live avatars, post-meeting summaries, and batch historical archives.

## Strategy Profiles

### 1. `LATENCY`
- **Target Response Time**: < 200 ms TTFT.
- **Use Case**: Active meeting interruption, conversational avatars, spoken turn-taking.
- **Provider Preference**: Groq LPU Whisper & LLaMA-3 or Deepgram Nova Streaming.
- **Rationale**: Human conversational turn-taking breaks down when agent latency exceeds 350ms.

### 2. `COST`
- **Target Expense**: $0.00 / minute API fee.
- **Use Case**: Continuous background transcription of internal developer pair sessions or budget-constrained nodes.
- **Provider Preference**: `LocalWhisperProvider` (`int8` on CPU) + local LLMs or rule-based heuristics.

### 3. `QUALITY`
- **Target Accuracy**: Maximum semantic precision, formal multi-stakeholder nuance, deep multilingual translation.
- **Use Case**: Legal reviews, board meetings, cross-lingual executive debriefs.
- **Provider Preference**: OpenAI `whisper-1` + `gpt-4o`.

### 4. `BALANCED` (Default)
- **Target**: Balanced compromise between 300–400ms turnaround and robust entity extraction.
