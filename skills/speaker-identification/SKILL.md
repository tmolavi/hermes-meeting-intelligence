---
name: speaker-identification
description: "Guidelines and workflows for speaker diarization, voice enrollment privacy, and mapping speaker turns to known participants."
version: "0.1.0"
author: "Taqi Molavi"
tags: ["hermes-agent", "speaker-diarization", "speaker-id", "privacy", "voice-biometrics"]
---

# Speaker Identification Skill

This skill guides Hermes Agent in attributing spoken turns to participants responsibly.

## Privacy and Biometric Guidelines

1. **Explicit Enrollment Only**:
   - Voice biometric embeddings must never be stored without explicit participant notice and opt-in.
   - For local or privacy-sensitive setups, use synthetic or anonymous speaker tags (e.g., `speaker_0`, `speaker_1`).
2. **Diarization Providers**:
   - Remote: Deepgram Nova (native diarization) or PyAnnote cloud endpoints.
   - Local: PyAnnote-audio (GPU recommended) or heuristic time-window chunking.
3. **Attribution Disambiguation**:
   - When mapping unverified speaker tags to known participants, rely on self-identification in the transcript (e.g., "This is Taqi speaking...") or manual owner verification.
