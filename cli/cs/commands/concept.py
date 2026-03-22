from __future__ import annotations

import typer

from cs.api_client import APIClientError, create_client_from_obj
from cs.formatters import print_json, print_mapping, print_table, shorten


app = typer.Typer(no_args_is_help=True, help="Concept commands")


@app.command("list")
def list_concepts(
    ctx: typer.Context,
    field: str | None = typer.Option(None, "--field", help="Filter by field name."),
    search: str | None = typer.Option(None, "--search", help="Filter by label search."),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    client = create_client_from_obj(ctx.obj)
    try:
        response = client.get(
            "/api/v1/concepts", params={"field": field, "search": search}
        )
    except APIClientError as exc:
        _exit_from_error(exc)
    finally:
        client.close()

    if as_json:
        print_json(response)
        return

    items = response.get("items", response)
    rows = [
        [
            item.get("id"),
            item.get("label"),
            item.get("field"),
            shorten(item.get("description")),
        ]
        for item in items
    ]
    print_table("Concepts", ["ID", "Label", "Field", "Description"], rows)


@app.command("get")
def get_concept(
    ctx: typer.Context,
    concept_id: str,
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    client = create_client_from_obj(ctx.obj)
    try:
        response = client.get(f"/api/v1/concepts/{concept_id}")
    except APIClientError as exc:
        _exit_from_error(exc)
    finally:
        client.close()

    if as_json:
        print_json(response)
        return
    print_mapping("Concept", response)


@app.command("connections")
def concept_connections(
    ctx: typer.Context,
    concept_id: str,
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    client = create_client_from_obj(ctx.obj)
    try:
        response = client.get(f"/api/v1/concepts/{concept_id}/connections")
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
            item.get("connection_type"),
            item.get("source_claim_id"),
            item.get("target_claim_id"),
        ]
        for item in response
    ]
    print_table(
        "Concept Connections", ["ID", "Type", "Source Claim", "Target Claim"], rows
    )


def _exit_from_error(exc: APIClientError) -> None:
    typer.echo(str(exc), err=True)
    raise typer.Exit(code=1)
