# Hardware & Compute Guide

Hermes Meeting Intelligence is architected with a **CPU-first design philosophy**. You do not need a discrete NVIDIA GPU to use this package or run tests.

## Hardware Profiles

### 1. Minimal / CPU-Only Mode (Recommended for general testing and standard servers)
- **CPU**: 2+ Cores (x86_64 or Apple Silicon ARM64)
- **RAM**: 2 GB+
- **Disk**: < 100 MB for core installation and SQLite store.
- **Provider Recommendation**: Cloud APIs (Groq / OpenAI / Deepgram) or lightweight local Faster-Whisper `base` model in `int8` quantization.

### 2. Local Air-Gapped / Self-Hosted Mode
- **CPU**: 4+ Cores (or NVIDIA GPU with CUDA for large models)
- **RAM**: 8 GB+ (16 GB for `whisper-large-v3`)
- **Package Extra**: `pip install "hermes-meeting-intelligence[local-stt]"`
- **Provider**: `LocalWhisperProvider`

## Avoiding Heavyweight Downloads

The core package **never downloads multi-gigabyte models silently**. When using local providers, model caching is directed to standard huggingface/whisper cache directories only upon explicit configuration.
