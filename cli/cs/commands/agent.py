from __future__ import annotations

import typer

from cs.api_client import APIClientError, create_client_from_obj
from cs.formatters import print_json, print_table, shorten


app = typer.Typer(no_args_is_help=True, help="AI linking agent commands")


@app.command("suggest")
def suggest(
    ctx: typer.Context,
    concept: str | None = typer.Option(None, "--concept", help="Source concept ID."),
    claim: str | None = typer.Option(None, "--claim", help="Source claim ID."),
    target_field: str | None = typer.Option(
        None, "--target-field", help="Restrict target field."
    ),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    if (concept is None) == (claim is None):
        typer.echo("Provide exactly one of --concept or --claim", err=True)
        raise typer.Exit(code=1)

    source_entity_type = "concept" if concept is not None else "claim"
    source_entity_id = concept or claim

    client = create_client_from_obj(ctx.obj)
    try:
        response = client.post(
            "/api/v1/agent/suggest-connections",
            json_body={
                "source_entity_type": source_entity_type,
                "source_entity_id": source_entity_id,
                "target_field": target_field,
            },
        )
    except APIClientError as exc:
        _exit_from_error(exc)
    finally:
        client.close()

    if as_json:
        print_json(response)
        return
    typer.echo(f"Started suggestion job {response.get('job_id')}")


@app.command("suggestions")
def suggestions(
    ctx: typer.Context,
    status: str | None = typer.Option(
        None, "--status", help="Filter by suggestion status."
    ),
    min_confidence: float | None = typer.Option(
        None, "--min-confidence", min=0.0, max=1.0
    ),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    client = create_client_from_obj(ctx.obj)
    try:
        response = client.get(
            "/api/v1/agent/suggestions",
            params={"status": status, "min_confidence": min_confidence},
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
            item.get("status"),
            item.get("proposal_type"),
            item.get("payload", {}).get("confidence", ""),
            shorten(item.get("rationale"), width=40),
        ]
        for item in response.get("items", [])
    ]
    print_table(
        "Agent Suggestions", ["ID", "Status", "Type", "Confidence", "Rationale"], rows
    )


def _exit_from_error(exc: APIClientError) -> None:
    typer.echo(str(exc), err=True)
    raise typer.Exit(code=1)
