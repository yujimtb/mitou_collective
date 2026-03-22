from __future__ import annotations

from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.events import EventStore
from app.events.models import EventStoreBase
from app.models import Base


@pytest.fixture
def engine():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    EventStoreBase.metadata.create_all(engine)
    yield engine
    EventStoreBase.metadata.drop_all(engine)
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def session_factory(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


@pytest.fixture
def event_store(session_factory):
    return EventStore(session_factory)


@pytest.fixture
def db_session(engine) -> Iterator[Session]:
    connection = engine.connect()
    transaction = connection.begin()
    session_local = sessionmaker(bind=connection, autoflush=False, autocommit=False, future=True)
    session = session_local()
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
