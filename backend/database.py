"""Database engine and session setup."""

from sqlmodel import Session, SQLModel, create_engine

from backend.config import settings

engine = create_engine(settings.database_url, echo=settings.debug)


def create_db_and_tables() -> None:
    """Create all tables defined by SQLModel metadata."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Yield a database session for dependency injection."""
    with Session(engine) as session:
        yield session
