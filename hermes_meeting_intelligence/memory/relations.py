"""
Cross-Meeting Graph Analysis and Relationship Linker.
"""

from __future__ import annotations

from typing import List, Set, Tuple

from hermes_meeting_intelligence.models.schema import MeetingRecord, RelationshipType


class MeetingGraphAnalyzer:
    """Discovers automatic and topological connections across meeting records."""

    @staticmethod
    def find_entity_overlaps(record1: MeetingRecord, record2: MeetingRecord) -> Set[str]:
        """Finds common entity names between two meetings."""
        e1 = {ent.name.lower() for ent in record1.entities}
        e2 = {ent.name.lower() for ent in record2.entities}
        return e1.intersection(e2)

    @staticmethod
    def find_topic_overlaps(record1: MeetingRecord, record2: MeetingRecord) -> Set[str]:
        """Finds common topics between two meetings."""
        t1 = {t.lower() for t in record1.topics}
        t2 = {t.lower() for t in record2.topics}
        return t1.intersection(t2)

    @staticmethod
    def infer_potential_relationships(
        current: MeetingRecord, historical: List[MeetingRecord]
    ) -> List[Tuple[str, RelationshipType, str]]:
        """Suggests relationship edges based on unresolved actions, shared decisions, and topics."""
        suggestions: List[Tuple[str, RelationshipType, str]] = []

        for past in historical:
            if past.meeting_id == current.meeting_id:
                continue

            shared_topics = MeetingGraphAnalyzer.find_topic_overlaps(current, past)
            shared_entities = MeetingGraphAnalyzer.find_entity_overlaps(current, past)

            # Check if current meeting resolves an action item from a previous meeting
            for past_action in past.action_items:
                if any(
                    past_action.description.lower() in d.description.lower()
                    for d in current.decisions
                ):
                    suggestions.append(
                        (
                            past.meeting_id,
                            RelationshipType.FOLLOWS_UP,
                            f"Current meeting decision resolves prior action '{past_action.description}' from {past.title}",
                        )
                    )

            if shared_topics or shared_entities:
                overlap_str = ", ".join(list(shared_topics.union(shared_entities))[:3])
                suggestions.append(
                    (
                        past.meeting_id,
                        RelationshipType.RELATED_TO,
                        f"Shared conceptual focus: {overlap_str}",
                    )
                )

        return suggestions
