import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import OperationalError

from db import DATABASE_URL
from models import Base


def ensure_database_exists(db_url_str: str) -> None:
    url = make_url(db_url_str)
    database = url.database

    # Try connect; if fails, create database via default 'postgres' database
    try:
        engine = create_engine(db_url_str, future=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine.dispose()
        return
    except Exception:
        admin_url = url.set(database="postgres")
        admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT", future=True)
        with admin_engine.connect() as conn:
            # Use template0 to avoid collation version mismatch on Windows
            conn.execute(text(
                f"CREATE DATABASE \"{database}\" TEMPLATE template0 ENCODING 'UTF8'"
            ))
        admin_engine.dispose()


def create_tables(db_url_str: str) -> None:
    engine = create_engine(db_url_str, future=True)
    Base.metadata.create_all(bind=engine)
    engine.dispose()


def main():
    db_url = os.getenv("DATABASE_URL", DATABASE_URL)
    ensure_database_exists(db_url)
    create_tables(db_url)
    print("PostgreSQL database and tables are ready.")


if __name__ == "__main__":
    main()


