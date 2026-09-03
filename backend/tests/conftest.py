"""Test fixtures and configuration."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import backend.main as main_module
from backend.database import get_session, sync_material_library
from backend.main import app

# Use in-memory SQLite with StaticPool so all threads share the same connection
test_engine = create_engine(
    "sqlite://",
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture(autouse=True)
def _offline_startup_fetch(monkeypatch):
    """The lifespan schedules a real collect_prices() on every TestClient start.

    Unpatched, that costs ~1.2 s per test and writes live quotes into the
    developer's comet.db from inside the test run.
    """

    async def offline(source: str | None = None) -> dict:
        return {}

    monkeypatch.setattr(main_module, "collect_prices", offline)


@pytest.fixture(name="session")
def session_fixture():
    """Create test DB tables and provide a session."""
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        sync_material_library(session, force=True)
        yield session
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Override the DB session dependency for tests."""

    def get_test_session():
        yield session

    app.dependency_overrides[get_session] = get_test_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
