---
name: realtime-routing
description: "Decision matrix and procedural intelligence for dynamic provider selection during live, latency-critical meeting interactions."
version: "0.1.0"
author: "Taqi Molavi"
tags: ["hermes-agent", "realtime-routing", "low-latency", "cost-optimization"]
---

# Real-Time Routing Skill

This skill guides Hermes Agent in dynamically choosing STT and LLM inference providers during active meetings.

## Optimization Profiles

1. **`LATENCY`**:
   - Ideal for live spoken turn-taking, interrupting, or real-time avatar / voice interaction.
   - Provider preference: Groq LPU Whisper & LLaMA-3 (100–150ms TTFT) or Deepgram Streaming STT.
2. **`COST`**:
   - Ideal for large batch processing of historical meetings or zero-cloud-spend environments.
   - Provider preference: Local Faster-Whisper on CPU/GPU or local Ollama / vLLM.
3. **`QUALITY`**:
   - Ideal for high-stakes executive meetings requiring nuanced multi-page synthesis, complex legal terms, or strict multilingual translation.
   - Provider preference: OpenAI GPT-4o + Whisper Large.
4. **`BALANCED`**:
   - Standard default balancing sub-second responsiveness with high extraction accuracy.

## Failover Policy

- If a remote provider encounters a network timeout or 429 rate limit, immediately fallback to the next available tier without interrupting the meeting session.
