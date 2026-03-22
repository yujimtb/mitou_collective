from __future__ import annotations

from copy import deepcopy
from typing import Any


class ProjectionEngine:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self._contexts: dict[str, dict[str, object]] = {}
        self._claims: dict[str, dict[str, object]] = {}
        self._claim_list: dict[str, dict[str, object]] = {}
        self._concepts: dict[str, dict[str, object]] = {}
        self._graph_edges: dict[tuple[str, str, str], dict[str, object]] = {}
        self._proposals: dict[str, dict[str, object]] = {}
        self._pending_proposals: dict[str, dict[str, object]] = {}
        self._connections: dict[str, dict[str, object]] = {}

    def apply(self, event: dict[str, object]) -> None:
        handler = getattr(self, f"_on_{event['event_type']}", None)
        if handler is not None:
            handler(event)

    def rebuild(self, events: list[dict[str, object]]) -> dict[str, object]:
        self.reset()
        for event in sorted(events, key=lambda item: int(item["sequence_number"])):
            self.apply(event)
        return self.snapshot()

    def snapshot(self) -> dict[str, object]:
        return {
            "claim_list": [deepcopy(item) for item in self._claim_list.values()],
            "claim_details": deepcopy(self._claims),
            "concept_graph": {
                "nodes": [deepcopy(item) for item in self._concepts.values()]
                + [
                    {
                        "id": claim_id,
                        "kind": "claim",
                        "label": claim["statement"],
                        "trust_status": claim["trust_status"],
                    }
                    for claim_id, claim in self._claims.items()
                ],
                "edges": [deepcopy(item) for item in self._graph_edges.values()],
            },
            "proposal_queue": [deepcopy(item) for item in self._pending_proposals.values()],
            "cross_field_connections": [deepcopy(item) for item in self._connections.values()],
        }

    def get_claim_detail(self, claim_id: str) -> dict[str, object] | None:
        claim = self._claims.get(claim_id)
        return deepcopy(claim) if claim is not None else None

    def get_pending_proposals(self) -> list[dict[str, object]]:
        return [deepcopy(item) for item in self._pending_proposals.values()]

    def get_cross_field_connections(self) -> list[dict[str, object]]:
        return [deepcopy(item) for item in self._connections.values()]

    def get_graph_view(self) -> dict[str, object]:
        return deepcopy(self.snapshot()["concept_graph"])

    def _on_ClaimCreated(self, event: dict[str, object]) -> None:
        payload = self._payload(event)
        claim_id = str(event["aggregate_id"])
        detail = {
            "id": claim_id,
            "statement": payload.get("statement", ""),
            "claim_type": payload.get("claim_type"),
            "trust_status": payload.get("trust_status"),
            "version": payload.get("version", 1),
            "context_ids": list(payload.get("context_ids", [])),
            "context_names": list(payload.get("context_names", [])),
            "concept_ids": list(payload.get("concept_ids", [])),
            "evidence_ids": list(payload.get("evidence_ids", [])),
            "cir_id": payload.get("cir_id"),
            "retracted": False,
            "history": [],
        }
        self._claims[claim_id] = detail
        self._refresh_claim_summary(claim_id)
        self._append_history(claim_id, event)

    def _on_ClaimUpdated(self, event: dict[str, object]) -> None:
        claim = self._ensure_claim(str(event["aggregate_id"]))
        payload = self._payload(event)
        changes = payload.get("changes", {})
        if isinstance(changes, dict):
            for key, value in changes.items():
                if key in {
                    "context_ids",
                    "context_names",
                    "concept_ids",
                    "evidence_ids",
                } and isinstance(value, list):
                    claim[key] = list(value)
                else:
                    claim[key] = value
        if payload.get("version") is not None:
            claim["version"] = payload["version"]
        self._refresh_claim_summary(str(event["aggregate_id"]))
        self._append_history(str(event["aggregate_id"]), event)

    def _on_ClaimTrustChanged(self, event: dict[str, object]) -> None:
        claim_id = str(event["aggregate_id"])
        claim = self._ensure_claim(claim_id)
        payload = self._payload(event)
        claim["trust_status"] = payload.get("new_status")
        if payload.get("version") is not None:
            claim["version"] = payload["version"]
        self._refresh_claim_summary(claim_id)
        self._append_history(claim_id, event)

    def _on_ClaimRetracted(self, event: dict[str, object]) -> None:
        claim_id = str(event["aggregate_id"])
        claim = self._ensure_claim(claim_id)
        claim["retracted"] = True
        self._refresh_claim_summary(claim_id)
        self._append_history(claim_id, event)

    def _on_ConceptCreated(self, event: dict[str, object]) -> None:
        payload = self._payload(event)
        concept_id = str(event["aggregate_id"])
        self._concepts[concept_id] = {
            "id": concept_id,
            "kind": "concept",
            "label": payload.get("label", ""),
            "description": payload.get("description", ""),
            "field": payload.get("domain_field"),
            "term_ids": list(payload.get("term_ids", [])),
            "referent_id": payload.get("referent_id"),
        }

    def _on_ConceptUpdated(self, event: dict[str, object]) -> None:
        concept_id = str(event["aggregate_id"])
        concept = self._concepts.setdefault(
            concept_id, {"id": concept_id, "kind": "concept", "label": ""}
        )
        changes = self._payload(event).get("changes", {})
        if isinstance(changes, dict):
            concept.update(changes)

    def _on_ConceptLinkedToClaim(self, event: dict[str, object]) -> None:
        concept_id = str(event["aggregate_id"])
        claim_id = str(self._payload(event)["claim_id"])
        self._graph_edges[(concept_id, claim_id, "linked_to_claim")] = {
            "source": concept_id,
            "target": claim_id,
            "type": "linked_to_claim",
        }
        claim = self._claims.get(claim_id)
        if claim is not None and concept_id not in claim["concept_ids"]:
            claim["concept_ids"].append(concept_id)
            self._refresh_claim_summary(claim_id)

    def _on_EvidenceCreated(self, event: dict[str, object]) -> None:
        payload = self._payload(event)
        evidence_id = str(event["aggregate_id"])
        for link in payload.get("claim_links", []):
            claim_id = str(link.get("claim_id"))
            self._link_evidence_to_claim(claim_id, evidence_id)

    def _on_EvidenceLinkedToClaim(self, event: dict[str, object]) -> None:
        evidence_id = str(event["aggregate_id"])
        claim_id = str(self._payload(event)["claim_id"])
        self._link_evidence_to_claim(claim_id, evidence_id)

    def _on_ContextCreated(self, event: dict[str, object]) -> None:
        payload = self._payload(event)
        context_id = str(event["aggregate_id"])
        self._contexts[context_id] = {
            "id": context_id,
            "name": payload.get("name", ""),
            "description": payload.get("description", ""),
            "field": payload.get("domain_field"),
            "assumptions": list(payload.get("assumptions", [])),
            "parent_context_id": payload.get("parent_context_id"),
        }

    def _on_ContextUpdated(self, event: dict[str, object]) -> None:
        context_id = str(event["aggregate_id"])
        context = self._contexts.setdefault(context_id, {"id": context_id})
        changes = self._payload(event).get("changes", {})
        if isinstance(changes, dict):
            context.update(changes)

    def _on_ProposalCreated(self, event: dict[str, object]) -> None:
        payload = self._payload(event)
        proposal_id = str(event["aggregate_id"])
        proposal = {
            "id": proposal_id,
            "proposal_type": payload.get("proposal_type"),
            "target_entity_type": payload.get("target_entity_type"),
            "target_entity_id": payload.get("target_entity_id"),
            "payload": dict(payload.get("payload", {})),
            "rationale": payload.get("rationale", ""),
            "status": payload.get("status", "pending"),
        }
        self._proposals[proposal_id] = proposal
        if proposal["status"] == "pending":
            self._pending_proposals[proposal_id] = deepcopy(proposal)

    def _on_ProposalApproved(self, event: dict[str, object]) -> None:
        self._set_proposal_status(str(event["aggregate_id"]), "approved")

    def _on_ProposalRejected(self, event: dict[str, object]) -> None:
        self._set_proposal_status(str(event["aggregate_id"]), "rejected")

    def _on_CrossFieldLinkProposed(self, event: dict[str, object]) -> None:
        payload = self._payload(event)
        connection_id = str(event["aggregate_id"])
        self._connections[connection_id] = {
            "id": connection_id,
            "source_claim_id": payload.get("source_claim_id"),
            "target_claim_id": payload.get("target_claim_id"),
            "connection_type": payload.get("connection_type"),
            "description": payload.get("description"),
            "confidence": payload.get("confidence"),
            "status": payload.get("status", "pending"),
        }

    def _on_CrossFieldLinkApproved(self, event: dict[str, object]) -> None:
        connection = self._connections.get(str(event["aggregate_id"]))
        if connection is not None:
            connection["status"] = "approved"

    def _on_CrossFieldLinkRejected(self, event: dict[str, object]) -> None:
        connection = self._connections.get(str(event["aggregate_id"]))
        if connection is not None:
            connection["status"] = "rejected"

    def _payload(self, event: dict[str, object]) -> dict[str, Any]:
        payload = event.get("payload", {})
        return payload if isinstance(payload, dict) else {}

    def _ensure_claim(self, claim_id: str) -> dict[str, object]:
        if claim_id not in self._claims:
            self._claims[claim_id] = {
                "id": claim_id,
                "statement": "",
                "claim_type": None,
                "trust_status": None,
                "version": 1,
                "context_ids": [],
                "context_names": [],
                "concept_ids": [],
                "evidence_ids": [],
                "cir_id": None,
                "retracted": False,
                "history": [],
            }
        return self._claims[claim_id]

    def _append_history(self, claim_id: str, event: dict[str, object]) -> None:
        claim = self._ensure_claim(claim_id)
        claim["history"].append(
            {
                "sequence_number": event.get("sequence_number"),
                "event_type": event.get("event_type"),
                "payload": deepcopy(self._payload(event)),
                "created_at": event.get("created_at"),
            }
        )

    def _refresh_claim_summary(self, claim_id: str) -> None:
        claim = self._ensure_claim(claim_id)
        self._claim_list[claim_id] = {
            "id": claim_id,
            "statement": claim["statement"][:80],
            "claim_type": claim["claim_type"],
            "trust_status": claim["trust_status"],
            "context_names": list(claim["context_names"]),
            "concept_count": len(claim["concept_ids"]),
            "evidence_count": len(claim["evidence_ids"]),
            "retracted": claim["retracted"],
            "version": claim["version"],
        }

    def _link_evidence_to_claim(self, claim_id: str, evidence_id: str) -> None:
        claim = self._claims.get(claim_id)
        if claim is None:
            return
        if evidence_id not in claim["evidence_ids"]:
            claim["evidence_ids"].append(evidence_id)
            self._refresh_claim_summary(claim_id)

    def _set_proposal_status(self, proposal_id: str, status: str) -> None:
        proposal = self._proposals.get(proposal_id)
        if proposal is not None:
            proposal["status"] = status
        self._pending_proposals.pop(proposal_id, None)
