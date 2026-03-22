from __future__ import annotations

import typer

from cs.config import CSConfig, load_config, resolve_api_url, save_config


app = typer.Typer(no_args_is_help=True, help="Authentication commands")


@app.command("login")
def login(
    ctx: typer.Context,
    token: str | None = typer.Option(
        None, "--token", help="API bearer token to store."
    ),
    api_url: str | None = typer.Option(None, "--api-url", help="API base URL to save."),
) -> None:
    config = load_config()
    resolved_token = token or typer.prompt("API token", hide_input=True)
    resolved_api_url = resolve_api_url(config, api_url or _api_override(ctx))
    path = save_config(CSConfig(api_url=resolved_api_url, token=resolved_token))
    typer.echo(f"Saved credentials to {path}")


def _api_override(ctx: typer.Context) -> str | None:
    if isinstance(ctx.obj, dict):
        return ctx.obj.get("api_url_override")
    return None
