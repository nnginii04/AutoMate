from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()

connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _ensure_execution_log_columns() -> None:
    if not settings.database_url.startswith("sqlite"):
        return
    with engine.begin() as conn:
        columns = {
            row[1]
            for row in conn.execute(text("PRAGMA table_info(execution_logs)")).fetchall()
        }
        if "requires_clarification" not in columns:
            conn.execute(
                text(
                    "ALTER TABLE execution_logs "
                    "ADD COLUMN requires_clarification BOOLEAN NOT NULL DEFAULT 0"
                )
            )


def init_db() -> None:
    from app.models import execution_log, scenario_run_log  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _ensure_execution_log_columns()
