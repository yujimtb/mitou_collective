from __future__ import annotations

import typer

from cs.api_client import APIClientError, create_client_from_obj
from cs.formatters import print_json, print_mapping, print_table, shorten


app = typer.Typer(no_args_is_help=True, help="Context commands")


@app.command("list")
def list_contexts(
    ctx: typer.Context,
    field: str | None = typer.Option(None, "--field", help="Filter by field name."),
    page: int = typer.Option(1, min=1),
    per_page: int = typer.Option(20, min=1, max=100),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    client = create_client_from_obj(ctx.obj)
    try:
        response = client.get(
            "/api/v1/contexts",
            params={"field": field, "page": page, "per_page": per_page},
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
            item.get("name"),
            item.get("field"),
            shorten(item.get("description")),
            len(item.get("assumptions", [])),
        ]
        for item in items
    ]
    print_table("Contexts", ["ID", "Name", "Field", "Description", "Assumptions"], rows)


@app.command("get")
def get_context(
    ctx: typer.Context,
    context_id: str,
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    client = create_client_from_obj(ctx.obj)
    try:
        response = client.get(f"/api/v1/contexts/{context_id}")
    except APIClientError as exc:
        _exit_from_error(exc)
    finally:
        client.close()

    if as_json:
        print_json(response)
        return
    print_mapping("Context", response)


@app.command("create")
def create_context(
    ctx: typer.Context,
    name: str = typer.Option(..., "--name", help="Context name."),
    field: str = typer.Option(..., "--field", help="Context field."),
    description: str = typer.Option(..., "--description", help="Context description."),
    assumptions: list[str] | None = typer.Option(
        None,
        "--assumptions",
        help="Context assumption. Repeat the option to add multiple values.",
    ),
    parent: str | None = typer.Option(
        None, "--parent", help="Optional parent context identifier."
    ),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    body = {
        "name": name,
        "field": field,
        "description": description,
        "assumptions": assumptions or [],
        "parent_context_id": parent,
    }
    client = create_client_from_obj(ctx.obj)
    try:
        response = client.post("/api/v1/contexts", json_body=body)
    except APIClientError as exc:
        _exit_from_error(exc)
    finally:
        client.close()

    if as_json:
        print_json(response)
        return
    typer.echo(f"Created context {response.get('id')}")


def _exit_from_error(exc: APIClientError) -> None:
    typer.echo(str(exc), err=True)
    raise typer.Exit(code=1)
