from __future__ import annotations

from typing import Any

import typer

from cs.api_client import APIClientError, create_client_from_obj
from cs.formatters import print_json, print_mapping, print_table, shorten


app = typer.Typer(no_args_is_help=True, help="Claim commands")


@app.command("list")
def list_claims(
    ctx: typer.Context,
    context: str | None = typer.Option(
        None, "--context", help="Filter by context name."
    ),
    field: str | None = typer.Option(None, "--field", help="Filter by field name."),
    trust: str | None = typer.Option(None, "--trust", help="Filter by trust status."),
    claim_type: str | None = typer.Option(None, "--type", help="Filter by claim type."),
    page: int = typer.Option(1, min=1),
    per_page: int = typer.Option(20, min=1, max=100),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    client = create_client_from_obj(ctx.obj)
    try:
        response = client.get(
            "/api/v1/claims",
            params={
                "context": context,
                "field": field,
                "trust_status": trust,
                "claim_type": claim_type,
                "page": page,
                "per_page": per_page,
            },
        )
    except APIClientError as exc:
        _exit_from_error(exc)
    finally:
        client.close()

    if as_json:
        print_json(response)
        return

    items = response.get("items", [])
    rows = [
        [
            item.get("id"),
            shorten(item.get("statement"), width=50),
            item.get("claim_type"),
            item.get("trust_status"),
            ", ".join(item.get("context_ids", [])),
        ]
        for item in items
    ]
    print_table("Claims", ["ID", "Statement", "Type", "Trust", "Contexts"], rows)


@app.command("get")
def get_claim(
    ctx: typer.Context,
    claim_id: str,
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    client = create_client_from_obj(ctx.obj)
    try:
        response = client.get(f"/api/v1/claims/{claim_id}")
    except APIClientError as exc:
        _exit_from_error(exc)
    finally:
        client.close()

    if as_json:
        print_json(response)
        return
    print_mapping("Claim", response)


@app.command("create")
def create_claim(
    ctx: typer.Context,
    statement: str = typer.Option(..., "--statement", help="Claim statement."),
    claim_type: str = typer.Option(..., "--type", help="Claim type."),
    contexts: list[str] | None = typer.Option(None, "--context", "--context-id"),
    concepts: list[str] | None = typer.Option(None, "--concept", "--concept-id"),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    body = {
        "statement": statement,
        "claim_type": claim_type,
        "context_ids": contexts or [],
        "concept_ids": concepts or [],
    }
    client = create_client_from_obj(ctx.obj)
    try:
        response = client.post("/api/v1/claims", json_body=body)
    except APIClientError as exc:
        _exit_from_error(exc)
    finally:
        client.close()

    if as_json:
        print_json(response)
        return
    typer.echo(f"Created claim {response.get('id')}")


@app.command("history")
def claim_history(
    ctx: typer.Context,
    claim_id: str,
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    client = create_client_from_obj(ctx.obj)
    try:
        response = client.get(f"/api/v1/claims/{claim_id}/history")
    except APIClientError as exc:
        _exit_from_error(exc)
    finally:
        client.close()

    if as_json:
        print_json(response)
        return

    rows = [
        [
            event.get("created_at"),
            event.get("event_type"),
            event.get("actor_id"),
            shorten(event.get("payload"), width=60),
        ]
        for event in response
    ]
    print_table("Claim History", ["Created At", "Event", "Actor", "Summary"], rows)


def _exit_from_error(exc: APIClientError) -> None:
    typer.echo(str(exc), err=True)
    raise typer.Exit(code=1)
