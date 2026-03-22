from __future__ import annotations

import typer

from cs.commands.agent import app as agent_app
from cs.commands.auth import app as auth_app
from cs.commands.claim import app as claim_app
from cs.commands.concept import app as concept_app
from cs.commands.proposal import app as proposal_app
from cs.commands.search import query as search_command


app = typer.Typer(no_args_is_help=True, help="CollectiveScience command line interface")
app.add_typer(auth_app, name="auth")
app.add_typer(claim_app, name="claim")
app.add_typer(concept_app, name="concept")
app.add_typer(proposal_app, name="proposal")
app.add_typer(agent_app, name="agent")
app.command("search")(search_command)


@app.callback()
def main(
    ctx: typer.Context,
    api_url: str | None = typer.Option(
        None,
        "--api-url",
        help="Override the API base URL for this invocation.",
    ),
) -> None:
    if ctx.obj is None:
        ctx.obj = {}
    if not isinstance(ctx.obj, dict):
        raise typer.BadParameter("CLI context must be a mapping")
    if api_url:
        ctx.obj["api_url_override"] = api_url
