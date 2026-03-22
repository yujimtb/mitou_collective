from __future__ import annotations

from collections.abc import Mapping

from fastapi import FastAPI

from app.api import api_router
from app.api.errors import register_exception_handlers


SERVICE_STATE_KEYS = (
    "actor_service",
    "claim_service",
    "concept_service",
    "context_service",
    "evidence_service",
    "term_service",
    "proposal_service",
    "review_service",
    "linking_agent",
    "search_service",
)


def create_app(service_overrides: Mapping[str, object] | None = None) -> FastAPI:
    app = FastAPI(title="CollectiveScience API", version="0.1.0")
    for key in SERVICE_STATE_KEYS:
        setattr(app.state, key, None)

    for key, value in (service_overrides or {}).items():
        setattr(app.state, key, value)

    register_exception_handlers(app)
    app.include_router(api_router)
    return app


app = create_app()