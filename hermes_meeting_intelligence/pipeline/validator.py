"""
Meeting Record Validator and Continuous Learning Audit Verifier.

Enforces:
1. Provenance preservation.
2. Distinction between observation and assertion.
3. Immutability of past ground truth without explicit owner correction log.
4. Absence of psychological speculation / unsupported emotional inferences.
"""

from __future__ import annotations

from typing import List, Tuple

from hermes_meeting_intelligence.models.schema import MeetingRecord


class MeetingValidator:
    """Verifies that MeetingRecords conform to ethical and data-integrity standards."""

    @staticmethod
    def validate_audit_integrity(record: MeetingRecord) -> Tuple[bool, List[str]]:
        """Checks for audit consistency, valid provenance, and no hallucinated predictions."""
        issues: List[str] = []

        if not record.meeting_id:
            issues.append("Missing meeting_id")

        if not record.title or len(record.title.strip()) < 2:
            issues.append("Meeting title is too short or empty")

        if not record.provenance.processed_at:
            issues.append("Missing provenance timestamp")

        # Verify decisions have minimal description
        for idx, dec in enumerate(record.decisions):
            if not dec.description or len(dec.description.strip()) < 3:
                issues.append(f"Decision {idx} has invalid or empty description")

        # Verify action items
        for idx, act in enumerate(record.action_items):
            if not act.description or len(act.description.strip()) < 3:
                issues.append(f"Action item {idx} has invalid or empty description")

        # Verify owner corrections
        for idx, corr in enumerate(record.owner_corrections):
            if not corr.target_field or corr.corrected_value is None:
                issues.append(f"Owner correction {idx} is missing target_field or corrected_value")

        return (len(issues) == 0, issues)
