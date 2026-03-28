from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def apply_sqlite_migrations() -> None:
    """Добавляет колонки в SQLite при обновлении модели (create_all их не меняет)."""
    url = str(engine.url)
    if not url.startswith("sqlite"):
        return
    with engine.begin() as conn:
        rows = conn.execute(text("PRAGMA table_info(transactions)")).fetchall()
        cols = {r[1] for r in rows}
        if not cols:
            return
        if "source" not in cols:
            conn.execute(
                text("ALTER TABLE transactions ADD COLUMN source VARCHAR NOT NULL DEFAULT 'manual'")
            )
        if "external_id" not in cols:
            conn.execute(text("ALTER TABLE transactions ADD COLUMN external_id VARCHAR"))
        if "occurred_at" not in cols:
            conn.execute(text("ALTER TABLE transactions ADD COLUMN occurred_at DATETIME"))

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
