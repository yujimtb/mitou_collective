from __future__ import annotations

import typer

from cs.api_client import APIClientError, create_client_from_obj
from cs.formatters import print_json, print_table, shorten


app = typer.Typer(no_args_is_help=True, help="Cross-entity search commands")


@app.command("query")
def query(
    ctx: typer.Context,
    text: str = typer.Argument(..., help="Search query."),
    scope: str | None = typer.Option(None, "--scope", help="Restrict entity scope."),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    client = create_client_from_obj(ctx.obj)
    try:
        response = client.get("/api/v1/search", params={"q": text, "scope": scope})
    except APIClientError as exc:
        _exit_from_error(exc)
    finally:
        client.close()

    if as_json:
        print_json(response)
        return

    rows = [
        [
            item.get("entity_type"),
            item.get("entity_id"),
            item.get("title"),
            item.get("score"),
            shorten(item.get("snippet"), width=50),
        ]
        for item in response.get("items", [])
    ]
    print_table("Search Results", ["Type", "ID", "Title", "Score", "Snippet"], rows)


def _exit_from_error(exc: APIClientError) -> None:
    typer.echo(str(exc), err=True)
    raise typer.Exit(code=1)
