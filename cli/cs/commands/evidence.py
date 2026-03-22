from __future__ import annotations

import typer

from cs.api_client import APIClientError, create_client_from_obj
from cs.formatters import print_json, print_mapping, print_table, shorten


app = typer.Typer(no_args_is_help=True, help="Evidence commands")


@app.command("list")
def list_evidence(
    ctx: typer.Context,
    evidence_type: str | None = typer.Option(
        None, "--type", help="Filter by evidence type."
    ),
    page: int = typer.Option(1, min=1),
    per_page: int = typer.Option(20, min=1, max=100),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    client = create_client_from_obj(ctx.obj)
    try:
        response = client.get(
            "/api/v1/evidence",
            params={"evidence_type": evidence_type, "page": page, "per_page": per_page},
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
            item.get("title"),
            item.get("evidence_type"),
            item.get("reliability"),
            len(item.get("claim_links", [])),
            shorten(item.get("source")),
        ]
        for item in items
    ]
    print_table(
        "Evidence",
        ["ID", "Title", "Type", "Reliability", "Claims", "Source"],
        rows,
    )


@app.command("get")
def get_evidence(
    ctx: typer.Context,
    evidence_id: str,
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    client = create_client_from_obj(ctx.obj)
    try:
        response = client.get(f"/api/v1/evidence/{evidence_id}")
    except APIClientError as exc:
        _exit_from_error(exc)
    finally:
        client.close()

    if as_json:
        print_json(response)
        return
    print_mapping("Evidence", response)


@app.command("create")
def create_evidence(
    ctx: typer.Context,
    title: str = typer.Option(..., "--title", help="Evidence title."),
    evidence_type: str = typer.Option(..., "--type", help="Evidence type."),
    source: str = typer.Option(..., "--source", help="Evidence source."),
    excerpt: str | None = typer.Option(None, "--excerpt", help="Evidence excerpt."),
    reliability: str = typer.Option(
        "unverified", "--reliability", help="Evidence reliability level."
    ),
    claims: list[str] | None = typer.Option(
        None,
        "--claim",
        "--claim-id",
        help="Claim identifier to link. Repeat the option to add multiple values.",
    ),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    body = {
        "title": title,
        "evidence_type": evidence_type,
        "source": source,
        "excerpt": excerpt,
        "reliability": reliability,
        "claim_links": [{"claim_id": claim_id} for claim_id in (claims or [])],
    }
    client = create_client_from_obj(ctx.obj)
    try:
        response = client.post("/api/v1/evidence", json_body=body)
    except APIClientError as exc:
        _exit_from_error(exc)
    finally:
        client.close()

    if as_json:
        print_json(response)
        return
    typer.echo(f"Created evidence {response.get('id')}")


def _exit_from_error(exc: APIClientError) -> None:
    typer.echo(str(exc), err=True)
    raise typer.Exit(code=1)
