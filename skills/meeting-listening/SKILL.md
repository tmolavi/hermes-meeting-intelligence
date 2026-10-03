---
name: meeting-listening
description: "Guidelines and procedural intelligence for active listening, chunk buffering, and real-time transcription during live or recorded meetings."
version: "0.1.0"
author: "Taqi Molavi"
tags: ["hermes-agent", "meeting-intelligence", "speech-to-text", "audio"]
---

# Meeting Listening Skill

This skill teaches Hermes Agent how to handle incoming audio streams and recorded meeting files effectively.

## Core Principles

1. **Speech-to-Text Abstraction**:
   - Never assume a single monolithic STT model is bundled.
   - Use `meeting_transcribe` tool to delegate speech recognition to the active provider (e.g. local CPU/GPU Faster-Whisper, Groq Whisper, Deepgram Nova, or OpenAI Whisper).
2. **Buffering & Chunking**:
   - For real-time sessions, process speech in 2 to 5-second acoustic chunks to preserve conversational cadence without lagging behind the discussion.
3. **Multilingual Audio**:
   - Explicitly specify the spoken language if known (e.g., `fa`, `tr`, `az`, `ar`, `en`), or allow the provider's auto-detect to establish language context.

## Workflow

1. Ingest audio stream / file using `meeting_transcribe`.
2. Review generated `SpeakerSegment` list.
3. Check confidence scores. If confidence is below threshold (< 0.70), flag segments as low-confidence for human owner review.
4. Pass transcribed text and segments downstream to `meeting-extraction`.
