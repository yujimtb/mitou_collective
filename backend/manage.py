"""Management commands for the CollectiveScience backend."""
from __future__ import annotations

import json
import os
import sys


def seed():
    """Seed the database with the entropy demo dataset."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from app.events.models import EventStoreBase
    from app.models import Base
    from app.seeds.entropy_dataset import seed_entropy_dataset

    database_url = os.getenv("DATABASE_URL", "sqlite:///./collective_science.db")
    engine = create_engine(
        database_url,
        **({"connect_args": {"check_same_thread": False}} if database_url.startswith("sqlite") else {}),
    )
    Base.metadata.create_all(engine)
    EventStoreBase.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with factory() as session:
        summary = seed_entropy_dataset(session)
    print(json.dumps({
        "contexts": summary.contexts,
        "terms": summary.terms,
        "concepts": summary.concepts,
        "claims": summary.claims,
        "evidence": summary.evidence,
        "connections": summary.connections,
        "cir": summary.cir,
    }, indent=2))
    print("Seed complete.")


def create_admin():
    """Create an admin actor and print a JWT token for it."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from app.events.models import EventStoreBase
    from app.models import Actor, Base
    from app.schemas import ActorRead, ActorType, TrustLevel
    from app.auth.jwt import create_access_token

    database_url = os.getenv("DATABASE_URL", "sqlite:///./collective_science.db")
    engine = create_engine(
        database_url,
        **({"connect_args": {"check_same_thread": False}} if database_url.startswith("sqlite") else {}),
    )
    Base.metadata.create_all(engine)
    EventStoreBase.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with factory() as session:
        actor = Actor(
            actor_type=ActorType.HUMAN,
            name="Admin",
            trust_level=TrustLevel.ADMIN,
        )
        session.add(actor)
        session.commit()
        session.refresh(actor)
        actor_read = ActorRead(
            id=str(actor.id),
            actor_type=actor.actor_type,
            name=actor.name,
            trust_level=actor.trust_level,
            agent_model=actor.agent_model,
            created_at=actor.created_at,
        )
        token = create_access_token(actor_read)
    print(f"Actor ID: {actor_read.id}")
    print(f"Token:    {token.access_token}")


def serve():
    """Run the development server."""
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host=host, port=port, reload=True)


COMMANDS = {
    "seed": seed,
    "create-admin": create_admin,
    "serve": serve,
}


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(f"Usage: python manage.py <{'|'.join(COMMANDS)}>")
        sys.exit(1)
    COMMANDS[sys.argv[1]]()
