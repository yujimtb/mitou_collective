from __future__ import annotations

from typing import Any


DEFAULT_EVENT_TYPE_LABELS: dict[str, str] = {
    "ClaimCreated": "Claim作成",
    "ClaimUpdated": "Claim更新",
    "ClaimRetracted": "Claim撤回",
    "ClaimTrustChanged": "信頼状態変更",
    "EvidenceLinkedToClaim": "Evidence紐付け",
    "EvidenceCreated": "Evidence作成",
    "EvidenceUpdated": "Evidence更新",
    "ConceptCreated": "Concept作成",
    "ConceptUpdated": "Concept更新",
    "ContextCreated": "Context作成",
    "ContextUpdated": "Context更新",
    "ProposalCreated": "提案作成",
    "ProposalApproved": "提案承認",
    "ProposalRejected": "提案却下",
    "CrossFieldLinkProposed": "分野横断リンク提案",
    "CrossFieldLinkApproved": "分野横断リンク承認",
    "CrossFieldLinkRejected": "分野横断リンク却下",
}


def event_kind(event_type: str) -> str:
    words: list[str] = []
    current = ""
    for char in event_type:
        if char.isupper() and current:
            words.append(current.lower())
            current = char
        else:
            current += char
    if current:
        words.append(current.lower())
    return "_".join(words)


def event_title(event_type: str, labels: dict[str, str] | None = None) -> str:
    resolved_labels = labels or DEFAULT_EVENT_TYPE_LABELS
    return resolved_labels.get(event_type, event_type)


def summarize_event(event_type: str, payload: dict[str, Any]) -> str:
    if event_type == "ClaimCreated":
        statement = payload.get("statement")
        return f"「{statement}」を作成" if statement else "Claimを作成"

    if event_type == "ClaimUpdated":
        changes = payload.get("changes")
        if isinstance(changes, dict) and changes:
            change_names = ", ".join(sorted(str(key) for key in changes))
            return f"更新項目: {change_names}"
        return "Claimを更新"

    if event_type == "ClaimRetracted":
        reason = payload.get("reason")
        return f"撤回理由: {reason}" if reason else "Claimを撤回"

    if event_type == "ClaimTrustChanged":
        previous_status = payload.get("previous_status")
        new_status = payload.get("new_status")
        if previous_status and new_status:
            return f"信頼状態を {previous_status} から {new_status} に変更"
        return "信頼状態を変更"

    if event_type == "EvidenceLinkedToClaim":
        claim_id = payload.get("claim_id")
        relationship = payload.get("relationship")
        if claim_id and relationship:
            return f"Claim {claim_id} に {relationship} として紐付け"
        return "ClaimにEvidenceを紐付け"

    if event_type == "EvidenceCreated":
        title = payload.get("title")
        return f"「{title}」を登録" if title else "Evidenceを作成"

    if event_type == "EvidenceUpdated":
        return "Evidenceを更新"

    if event_type == "ConceptCreated":
        label = payload.get("label")
        return f"「{label}」を作成" if label else "Conceptを作成"

    if event_type == "ConceptUpdated":
        return "Conceptを更新"

    if event_type == "ContextCreated":
        name = payload.get("name")
        return f"「{name}」を作成" if name else "Contextを作成"

    if event_type == "ContextUpdated":
        return "Contextを更新"

    if event_type == "ProposalCreated":
        rationale = payload.get("rationale")
        return str(rationale) if rationale else "提案を作成"

    if event_type == "ProposalApproved":
        notes = payload.get("notes")
        return f"承認メモ: {notes}" if notes else "提案を承認"

    if event_type == "ProposalRejected":
        reason = payload.get("reason")
        return f"却下理由: {reason}" if reason else "提案を却下"

    if event_type == "CrossFieldLinkProposed":
        connection_type = payload.get("connection_type")
        return f"{connection_type} リンクを提案" if connection_type else "分野横断リンクを提案"

    if event_type == "CrossFieldLinkApproved":
        return "分野横断リンクを承認"

    if event_type == "CrossFieldLinkRejected":
        reason = payload.get("reason")
        return f"却下理由: {reason}" if reason else "分野横断リンクを却下"

    return "変更を記録"


def event_href(aggregate_type: str, aggregate_id: str, proposal_id: str | None = None) -> str:
    if aggregate_type == "claim":
        return f"/claims/{aggregate_id}"
    if aggregate_type == "concept":
        return f"/concepts/{aggregate_id}"
    if aggregate_type == "context":
        return f"/contexts/{aggregate_id}"
    if aggregate_type == "evidence":
        return f"/evidence/{aggregate_id}"
    if aggregate_type == "proposal":
        return "/review"
    if aggregate_type == "cross_field_connection":
        return "/review" if proposal_id else "/suggestions"
    return "/"
