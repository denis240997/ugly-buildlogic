import psycopg2
from contextlib import contextmanager

from app.config import get_settings
from logic.src.database import create_tables, drop_all_tables


@contextmanager
def connect_db():
    settings = get_settings()
    conn = psycopg2.connect(
        host=settings.db_host,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        port=settings.db_port,
    )
    conn.autocommit = True
    cur = conn.cursor()
    try:
        yield cur
    finally:
        cur.close()
        conn.close()


def init_project():
    with connect_db() as cur:
        create_tables(cur)


def clear_project():
    with connect_db() as cur:
        drop_all_tables(cur)
