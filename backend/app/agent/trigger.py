from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class TriggerKind(StrEnum):
    NEW_CLAIM = "new_claim"
    NEW_CONCEPT = "new_concept"
    MANUAL = "manual"


@dataclass(slots=True)
class LinkingTrigger:
    trigger_kind: TriggerKind
    source_entity_type: str
    source_entity_id: str
    target_field: str | None = None
    requested_by: str | None = None

    def to_job_payload(self) -> dict[str, str]:
        payload = {
            "trigger_kind": self.trigger_kind.value,
            "source_entity_type": self.source_entity_type,
            "source_entity_id": self.source_entity_id,
        }
        if self.target_field is not None:
            payload["target_field"] = self.target_field
        if self.requested_by is not None:
            payload["requested_by"] = self.requested_by
        return payload


def claim_created_trigger(claim_id: str, *, target_field: str | None = None) -> LinkingTrigger:
    return LinkingTrigger(
        trigger_kind=TriggerKind.NEW_CLAIM,
        source_entity_type="claim",
        source_entity_id=claim_id,
        target_field=target_field,
    )


def concept_created_trigger(concept_id: str, *, target_field: str | None = None) -> LinkingTrigger:
    return LinkingTrigger(
        trigger_kind=TriggerKind.NEW_CONCEPT,
        source_entity_type="concept",
        source_entity_id=concept_id,
        target_field=target_field,
    )


def manual_trigger(
    *,
    source_entity_type: str,
    source_entity_id: str,
    requested_by: str,
    target_field: str | None = None,
) -> LinkingTrigger:
    return LinkingTrigger(
        trigger_kind=TriggerKind.MANUAL,
        source_entity_type=source_entity_type,
        source_entity_id=source_entity_id,
        target_field=target_field,
        requested_by=requested_by,
    )
