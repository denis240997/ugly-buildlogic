import os
import psycopg2
from contextlib import contextmanager
from enum import Enum

from fastapi import UploadFile
import pandas as pd

from app.config import get_settings
from logic.src.database import (
    create_tables,
    drop_all_tables,
    drop_table,
    insert_from_csv,
    export_table_to_csv,
    insert_results_to_table,
)
from logic.src.algorithms import (
    cpm,
    rcpm,
    ssgs,
    prepare_operations,
    check_resource_conflicts,
    check_precedence_relations,
    local_ssgs,
)
from logic.src.analytics import (
    calculate_completion_percentage,
    detect_project_delays,
)
from logic.src.plot import plot_gantt_chart, plot_gantt_and_resource_chart


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
    # Delete all static files except for the .gitignore file
    for file in os.listdir(static_dir):
        if file == ".gitignore":
            continue
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


def compute_cpm() -> tuple[list[str], int]:
    with db_connection() as conn:
        df_operations = pd.read_sql("SELECT * FROM operations", conn)
        operations = prepare_operations(df_operations)
        critical_path, total_duration = cpm(operations)
        insert_results_to_table(conn.cursor(), operations)
    return critical_path, total_duration


def compute_rcpm() -> tuple[list[str], int]:
    with db_connection() as conn:
        df_operations = pd.read_sql("SELECT * FROM operations", conn)
        df_resources = pd.read_sql("SELECT * FROM resources", conn)
        operations = prepare_operations(df_operations)
        critical_path, total_duration = rcpm(operations, df_resources)

        check_resource_conflicts(operations, df_resources)  # Проверка конфликт ресурсов
        check_precedence_relations(operations)  # Проверка конфликт предшествования

        insert_results_to_table(conn.cursor(), operations)
    return critical_path, total_duration


def compute_ssgs() -> tuple[list[str], int]:
    with db_connection() as conn:
        df_operations = pd.read_sql("SELECT * FROM operations", conn)
        df_resources = pd.read_sql("SELECT * FROM resources", conn)
        operations = prepare_operations(df_operations)
        critical_path, total_duration = ssgs(operations, df_resources)

        check_resource_conflicts(operations, df_resources)
        check_precedence_relations(operations)

        insert_results_to_table(conn.cursor(), operations)
    return critical_path, total_duration


def compute_rcpm_with_local_sgs(
    selected_tasks: list[str], use_pr: bool
) -> tuple[list[str], int]:
    with db_connection() as conn:
        df_operations = pd.read_sql("SELECT * FROM operations", conn)
        df_resources = pd.read_sql("SELECT * FROM resources", conn)
        operations = prepare_operations(df_operations)
        critical_path, _ = rcpm(operations, df_resources)
        total_duration = local_ssgs(
            operations, df_resources, selected_tasks, use_pr=use_pr
        )

        check_resource_conflicts(operations, df_resources)
        check_precedence_relations(operations)

        insert_results_to_table(conn.cursor(), operations)
    return critical_path, total_duration


def get_completion_percentage() -> float:
    with db_connection() as conn:
        df_current_status = pd.read_sql("SELECT * FROM current_status", conn)
    return calculate_completion_percentage(df_current_status)


def get_gantt_chart() -> str:
    result_path = os.path.join(get_settings().static_dir, "gantt_chart.png")
    with db_connection() as conn:
        df_results = pd.read_sql("SELECT * FROM results", conn)
    plot_gantt_chart(df_results, result_path)
    return result_path


def get_gantt_with_resource_chart() -> str:
    result_path = os.path.join(
        get_settings().static_dir, "gantt_with_resource_chart.png"
    )
    with db_connection() as conn:
        df_results = pd.read_sql("SELECT * FROM results", conn)
        df_resources = pd.read_sql("SELECT * FROM resources", conn)
    plot_gantt_and_resource_chart(df_results, df_resources, result_path)
    return result_path


def detect_delays() -> str:
    with db_connection() as conn:
        df_results = pd.read_sql("SELECT * FROM results", conn)
        df_current_status = pd.read_sql("SELECT * FROM current_status", conn)
    return detect_project_delays(df_results, df_current_status)
