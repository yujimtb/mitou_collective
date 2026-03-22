from __future__ import annotations

import asyncio

from sqlalchemy.orm import sessionmaker

from app.schemas import ActorCreate, ActorType, ActorUpdate, TrustLevel
from app.services import ActorService


def make_service(engine) -> ActorService:
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    return ActorService(session_factory)


def test_actor_service_create_and_get(engine) -> None:
    service = make_service(engine)
    created = asyncio.run(
        service.create(
            ActorCreate(
                actor_type=ActorType.HUMAN,
                name="Alice",
                trust_level=TrustLevel.REVIEWER,
            )
        )
    )

    fetched = asyncio.run(service.get(created.id))

    assert fetched.id == created.id
    assert fetched.name == "Alice"
    assert fetched.trust_level is TrustLevel.REVIEWER


def test_actor_service_list_filters(engine) -> None:
    service = make_service(engine)
    asyncio.run(
        service.create(
            ActorCreate(
                actor_type=ActorType.HUMAN,
                name="Alice Reviewer",
                trust_level=TrustLevel.REVIEWER,
            )
        )
    )
    asyncio.run(
        service.create(
            ActorCreate(
                actor_type=ActorType.AI_AGENT,
                name="Agent Bob",
                trust_level=TrustLevel.CONTRIBUTOR,
                agent_model="gpt-5.4",
            )
        )
    )

    filtered = asyncio.run(service.list(actor_type=ActorType.AI_AGENT, per_page=10))

    assert filtered.total_count >= 1
    assert all(item.actor_type is ActorType.AI_AGENT for item in filtered.items)


def test_actor_service_update(engine) -> None:
    service = make_service(engine)
    created = asyncio.run(
        service.create(
            ActorCreate(
                actor_type=ActorType.HUMAN,
                name="Carol",
                trust_level=TrustLevel.CONTRIBUTOR,
            )
        )
    )

    updated = asyncio.run(
        service.update(
            created.id,
            ActorUpdate(trust_level=TrustLevel.ADMIN, name="Carol Admin"),
        )
    )

    assert updated.trust_level is TrustLevel.ADMIN
    assert updated.name == "Carol Admin"