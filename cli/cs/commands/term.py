from __future__ import annotations

import typer

from cs.api_client import APIClientError, create_client_from_obj
from cs.formatters import print_json, print_mapping, print_table


app = typer.Typer(no_args_is_help=True, help="Term commands")


@app.command("list")
def list_terms(
    ctx: typer.Context,
    language: str | None = typer.Option(None, "--language", help="Filter by language."),
    search: str | None = typer.Option(
        None, "--search", help="Filter by term text search."
    ),
    page: int = typer.Option(1, min=1),
    per_page: int = typer.Option(20, min=1, max=100),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    client = create_client_from_obj(ctx.obj)
    try:
        response = client.get(
            "/api/v1/terms",
            params={
                "language": language,
                "search": search,
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

    items = response.get("items", response)
    rows = [
        [
            item.get("id"),
            item.get("surface_form"),
            item.get("language"),
            item.get("field_hint"),
            len(item.get("concept_ids", [])),
        ]
        for item in items
    ]
    print_table("Terms", ["ID", "Surface Form", "Language", "Field Hint", "Concepts"], rows)


@app.command("get")
def get_term(
    ctx: typer.Context,
    term_id: str,
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    client = create_client_from_obj(ctx.obj)
    try:
        response = client.get(f"/api/v1/terms/{term_id}")
    except APIClientError as exc:
        _exit_from_error(exc)
    finally:
        client.close()

    if as_json:
        print_json(response)
        return
    print_mapping("Term", response)


@app.command("create")
def create_term(
    ctx: typer.Context,
    surface_form: str = typer.Option(..., "--surface-form", help="Term surface form."),
    language: str = typer.Option("en", "--language", help="Term language code."),
    field_hint: str | None = typer.Option(
        None, "--field-hint", help="Optional field hint."
    ),
    concepts: list[str] | None = typer.Option(
        None,
        "--concept",
        "--concept-id",
        help="Related concept identifier. Repeat the option to add multiple values.",
    ),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    body = {
        "surface_form": surface_form,
        "language": language,
        "field_hint": field_hint,
        "concept_ids": concepts or [],
    }
    client = create_client_from_obj(ctx.obj)
    try:
        response = client.post("/api/v1/terms", json_body=body)
    except APIClientError as exc:
        _exit_from_error(exc)
    finally:
        client.close()

    if as_json:
        print_json(response)
        return
    typer.echo(f"Created term {response.get('id')}")


def _exit_from_error(exc: APIClientError) -> None:
    typer.echo(str(exc), err=True)
    raise typer.Exit(code=1)
