---
name: meeting-extraction
description: "Extract structured intelligence (decisions, proposals, disagreements, questions, action items, evidence) from meeting transcripts."
version: "0.1.0"
author: "Taqi Molavi"
tags: ["hermes-agent", "meeting-intelligence", "extraction", "decision-log", "action-items"]
---

# Meeting Extraction Skill

This skill defines Hermes Agent's procedural intelligence for converting unstructured conversational dialogue into high-integrity structured meeting records.

## Intelligence Extraction Taxonomy

When processing a meeting transcript, Hermes must extract the following distinct entities:

1. **Decisions**: Explicit consensus or authoritative rulings made during the meeting. Must include exact wording and supporting evidence quote.
2. **Proposals**: Suggestions or options considered, along with current disposition (`proposed`, `accepted`, `rejected`, `deferred`).
3. **Disagreements / Friction**: Points where participants differed in opinion or technical approach, documenting multiple perspectives and resolution status (`resolved`, `unresolved`, `tabled`).
4. **Questions**: Unanswered inquiries or technical doubts requiring investigation.
5. **Action Items**: Explicit work commitments with assignee, clear definition of done, and deadline where stated.
6. **Evidence References**: Verbatim quotes linking claims to specific speakers and timestamped segments.
7. **Entities & Topics**: Named systems, APIs, clients, metrics, and topics discussed.

## Quality Constraints

- **Observation vs. Fact**: Always cite the speaker who stated a claim rather than asserting it as unverified fact.
- **No Psychological Speculation**: Do not infer hidden emotions, personality traits, or unsupported intent. Stick strictly to verbatim statements and explicit agreements.
- **Completeness**: Never drop unresolved disagreements; preserving friction points is essential for downstream context.
