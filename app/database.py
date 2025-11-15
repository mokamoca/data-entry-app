from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, scoped_session, sessionmaker

Base = declarative_base()

engine = None
SessionLocal = None


def _build_database_url(config) -> str:
    database_url = config.get("DATABASE_URL")
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
        return database_url

    db_path = Path(config.get("DB_PATH", "production_log_v3.db")).expanduser()
    return f"sqlite:///{db_path}"


def init_app(app):
    """Initialise SQLAlchemy engine and session factory."""
    global engine, SessionLocal

    if engine is not None:
        return engine

    database_url = _build_database_url(app.config)
    engine_kwargs = {"echo": app.config.get("SQL_ECHO", False), "future": True}
    if database_url.startswith("sqlite:///"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    engine = create_engine(database_url, **engine_kwargs)
    SessionLocal = scoped_session(
        sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    )
    return engine


def create_all():
    if engine is None:
        raise RuntimeError("Database engine is not initialised.")
    Base.metadata.create_all(bind=engine)


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    if SessionLocal is None:
        raise RuntimeError("Session factory is not initialised.")

    session: Optional[Session] = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def session_cleanup(exc=None):
    if SessionLocal is not None:
        SessionLocal.remove()
