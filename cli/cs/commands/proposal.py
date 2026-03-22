from __future__ import annotations

import typer

from cs.api_client import APIClientError, create_client_from_obj
from cs.formatters import print_json, print_table


app = typer.Typer(no_args_is_help=True, help="Proposal and review commands")


@app.command("list")
def list_proposals(
    ctx: typer.Context,
    status: str | None = typer.Option(
        None, "--status", help="Filter by proposal status."
    ),
    proposal_type: str | None = typer.Option(
        None, "--type", help="Filter by proposal type."
    ),
    proposed_by: str | None = typer.Option(
        None, "--proposed-by", help="Filter by actor ID."
    ),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    client = create_client_from_obj(ctx.obj)
    try:
        response = client.get(
            "/api/v1/proposals",
            params={
                "status": status,
                "proposal_type": proposal_type,
                "proposed_by": proposed_by,
            },
        )
    except APIClientError as exc:
        _exit_from_error(exc)
    finally:
        client.close()

    if as_json:
        print_json(response)
        return

    rows = [
        [
            item.get("id"),
            item.get("proposal_type"),
            item.get("status"),
            (item.get("proposed_by") or {}).get("name", ""),
            item.get("created_at"),
        ]
        for item in response.get("items", [])
    ]
    print_table("Proposals", ["ID", "Type", "Status", "Proposed By", "Created"], rows)


@app.command("review")
def review_proposal(
    ctx: typer.Context,
    proposal_id: str,
    approve: bool = typer.Option(False, "--approve", help="Approve the proposal."),
    reject: bool = typer.Option(False, "--reject", help="Reject the proposal."),
    request_changes: bool = typer.Option(
        False, "--request-changes", help="Request changes."
    ),
    comment: str | None = typer.Option(
        None, "--comment", help="Optional review comment."
    ),
    confidence: float | None = typer.Option(None, "--confidence", min=0.0, max=1.0),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    decision = _resolve_decision(
        approve=approve, reject=reject, request_changes=request_changes
    )
    if decision == "reject" and not comment:
        typer.echo("--comment is required when rejecting a proposal", err=True)
        raise typer.Exit(code=1)

    client = create_client_from_obj(ctx.obj)
    try:
        response = client.post(
            f"/api/v1/proposals/{proposal_id}/review",
            json_body={
                "decision": decision,
                "comment": comment,
                "confidence": confidence,
            },
        )
    except APIClientError as exc:
        _exit_from_error(exc)
    finally:
        client.close()

    if as_json:
        print_json(response)
        return
    typer.echo(f"Recorded {decision} review for proposal {proposal_id}")


def _resolve_decision(*, approve: bool, reject: bool, request_changes: bool) -> str:
    selected = [
        name
        for name, enabled in {
            "approve": approve,
            "reject": reject,
            "request_changes": request_changes,
        }.items()
        if enabled
    ]
    if len(selected) != 1:
        typer.echo(
            "Select exactly one of --approve, --reject, or --request-changes", err=True
        )
        raise typer.Exit(code=1)
    return selected[0]


def _exit_from_error(exc: APIClientError) -> None:
    typer.echo(str(exc), err=True)
    raise typer.Exit(code=1)
