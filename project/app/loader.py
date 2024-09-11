import os
import psycopg2
from contextlib import contextmanager
from enum import Enum

from fastapi import UploadFile

from app.config import get_settings
from logic.src.database import (
    create_tables,
    drop_all_tables,
    drop_table,
    insert_from_csv,
    export_table_to_csv,
)


@contextmanager
def db_connection():
    settings = get_settings()
    conn = psycopg2.connect(
        host=settings.db_host,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        port=settings.db_port,
    )
    conn.autocommit = True
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def db_cursor():
    with db_connection() as conn:
        cur = conn.cursor()
        try:
            yield cur
        finally:
            cur.close()


def init_project():
    with db_cursor() as cur:
        create_tables(cur)


def clear_static_dir():
    static_dir = get_settings().static_dir
    for file in os.listdir(static_dir):
        os.remove(os.path.join(static_dir, file))


def clear_project():
    with db_cursor() as cur:
        drop_all_tables(cur)

    clear_static_dir()


class Table(str, Enum):
    operations = "operations"
    resources = "resources"
    additional_info = "additional_info"
    current_status = "current_status"
    results = "results"


def drop_table_by_name(table_name: Table):
    with db_cursor() as cur:
        drop_table(cur, table_name.value)


def save_file(file: UploadFile) -> str:
    static_dir = get_settings().static_dir
    file_path = os.path.join(static_dir, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return file_path


class UploadableTable(str, Enum):
    operations = "operations"
    resources = "resources"


def load_table_from_file(file: UploadFile, table_name: UploadableTable):
    file_path = save_file(file)
    with db_cursor() as cur:
        insert_from_csv(cur, file_path, table_name.value)


def export_table(table_name: Table) -> str:
    with db_connection() as conn:
        result_path = os.path.join(get_settings().static_dir, f"{table_name.value}.csv")
        export_table_to_csv(conn, table_name.value, result_path)

    return result_path
