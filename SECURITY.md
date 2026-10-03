# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability within **Hermes Meeting Intelligence**, please report it responsibly by contacting the maintainer directly:

- **Email**: `contact@molavi.pro`
- **PGP/Encrypted Communications**: Available upon request via email.

Please do not open public GitHub issues for security vulnerabilities. We will review and acknowledge all reports within 48 hours.

---

## Sensitive Meeting Data & Privacy Safeguards

Meeting audio, transcripts, and decision logs frequently contain confidential business conversations, proprietary IP, and personal data. We follow strict defense-in-depth principles:

### 1. API Keys & Credentials
- All remote API keys (`OPENAI_API_KEY`, `GROQ_API_KEY`, `DEEPGRAM_API_KEY`) must be supplied via environment variables or secure Hermes runtime configuration.
- The repository enforces `.gitignore` rules preventing keys or `.env` files from ever entering git commits.
- Keys are never logged in debug outputs or stored inside the SQLite database.

### 2. Voice Biometrics & Speaker Enrollment
- Voice embeddings and speaker diarization profiles should only be retained with explicit participant knowledge and opt-in consent.
- By default, diarization produces anonymized identifier tags (`speaker_0`, `speaker_1`) rather than biometric persistent identities.

### 3. Trust Boundaries & Provider Leakage
- When configuring cloud providers (e.g. OpenAI, Groq, Deepgram), review your organization's data-processing agreements (DPAs) regarding whether audio data is used for model training.
- For air-gapped or confidential environments, use `LocalWhisperProvider` (`local-stt` extra) and local LLM backends to ensure zero data leaves your local network.

### 4. Prompt & Tool Injection Defense
- Unsanitized speech transcripts fed into extraction LLMs can theoretically contain adversarial prompt injections (e.g. a speaker reciting system prompt overrides).
- Hermes Meeting Intelligence isolates system prompts, enforces rigid Pydantic JSON schemas, and validates extraction integrity before persisting records to memory.

### 5. Local Database & Audit Integrity
- The local SQLite store records provenance and owner corrections. Ground truth is immutable: historical meeting records are never silently mutated without an explicit `OwnerCorrection` log entry.
