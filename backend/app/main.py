from __future__ import annotations

import os
from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.agent import LLMConfig, create_llm_client
from app.api import api_router
from app.api.errors import register_exception_handlers
from app.events import EventStore
from app.events.models import EventStoreBase
from app.models import Base
from app.services import (
    ActorService,
    ClaimService,
    ConceptService,
    ContextService,
    EvidenceService,
    ProposalService,
    ReviewService,
    SearchService,
    TermService,
)


SERVICE_STATE_KEYS = (
    "actor_service",
    "event_store",
    "claim_service",
    "concept_service",
    "context_service",
    "evidence_service",
    "term_service",
    "proposal_service",
    "review_service",
    "linking_agent",
    "search_service",
    "llm_config",
)


def _build_engine():
    database_url = os.getenv("DATABASE_URL", "sqlite:///./collective_science.db")
    if database_url.startswith("sqlite"):
        return create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    return create_engine(database_url, pool_pre_ping=True)


def _wire_services(session_factory):
    """Wire all service instances using the given session factory."""
    event_store = EventStore(session_factory)
    actor_service = ActorService(session_factory)
    claim_service = ClaimService(session_factory, event_store)
    concept_service = ConceptService(session_factory, event_store)
    context_service = ContextService(session_factory, event_store)
    evidence_service = EvidenceService(session_factory, event_store)
    term_service = TermService(session_factory, event_store)
    proposal_service = ProposalService(session_factory, event_store)
    review_service = ReviewService(session_factory, event_store)
    search_service = SearchService(session_factory)

    from app.agent import (
        CandidateGenerator,
        CandidateSearch,
        ContextCollector,
        LinkingAgent,
        ProposalFormatter,
    )

    async def _noop_llm(prompt: str):
        return {"candidates": []}

    llm_config = LLMConfig.from_env()
    llm_callable = _noop_llm
    if llm_config.api_key:
        llm_client = create_llm_client(llm_config)
        llm_callable = llm_client.generate

    collector = ContextCollector(
        claim_service=claim_service,
        concept_service=concept_service,
        context_loader=context_service.get,
        evidence_loader=evidence_service.get,
        term_loader=term_service.get,
    )
    candidate_search = CandidateSearch(
        claim_service=claim_service,
        concept_service=concept_service,
        context_loader=context_service.get,
        term_loader=term_service.get,
    )
    candidate_generator = CandidateGenerator(llm_client=llm_callable)
    proposal_formatter = ProposalFormatter(proposal_service=proposal_service)
    linking_agent = LinkingAgent(
        claim_service=claim_service,
        concept_service=concept_service,
        proposal_service=proposal_service,
        collector=collector,
        candidate_search=candidate_search,
        candidate_generator=candidate_generator,
        proposal_formatter=proposal_formatter,
    )

    return {
        "actor_service": actor_service,
        "event_store": event_store,
        "claim_service": claim_service,
        "concept_service": concept_service,
        "context_service": context_service,
        "evidence_service": evidence_service,
        "term_service": term_service,
        "proposal_service": proposal_service,
        "review_service": review_service,
        "search_service": search_service,
        "linking_agent": linking_agent,
        "llm_config": llm_config,
    }


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    engine = _build_engine()
    Base.metadata.create_all(engine)
    EventStoreBase.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    services = _wire_services(session_factory)
    for key, value in services.items():
        setattr(app.state, key, value)
    yield
    engine.dispose()


def create_app(service_overrides: Mapping[str, object] | None = None) -> FastAPI:
    app = FastAPI(
        title="CollectiveScience API",
        version="0.1.0",
        lifespan=lifespan if not service_overrides else None,
    )
    for key in SERVICE_STATE_KEYS:
        setattr(app.state, key, None)

    for key, value in (service_overrides or {}).items():
        setattr(app.state, key, value)

    allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(api_router)
    return app


app = create_app()
