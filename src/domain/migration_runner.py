import sqlite3
from pathlib import Path
import importlib.resources as resources

from .db import get_connection


def _ensure_schema_migrations(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
          version TEXT PRIMARY KEY,
          applied_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )


def _applied_versions(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute("SELECT version FROM schema_migrations").fetchall()
    return {row[0] for row in rows}


def _load_migration_sql(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _list_migration_files() -> list[Path]:
    files = []
    try:
        pkg = resources.files(__package__ + ".migrations")
        for entry in pkg.iterdir():
            if entry.name.endswith(".sql"):
                files.append(Path(str(entry)))
    except Exception:
        pass

    if not files:
        fs_dir = Path(__file__).resolve().parent / "migrations"
        if fs_dir.exists():
            files = list(fs_dir.glob("*.sql"))

    return sorted(files, key=lambda p: p.name)


def _embedded_migrations() -> list[tuple[str, str]]:
    return [
        (
            "001_masterdata.sql",
            """
            PRAGMA foreign_keys=ON;

            CREATE TABLE IF NOT EXISTS md_job_role (
              scenario_id TEXT NOT NULL,
              job_code    TEXT NOT NULL,
              job_name    TEXT NOT NULL,
              sort_order  INTEGER NOT NULL DEFAULT 0,
              is_active   INTEGER NOT NULL DEFAULT 1,
              PRIMARY KEY (scenario_id, job_code)
            );

            CREATE TABLE IF NOT EXISTS md_job_rate (
              scenario_id TEXT NOT NULL,
              job_code    TEXT NOT NULL,
              wage_day    INTEGER NOT NULL,
              wage_hour   INTEGER NOT NULL,
              allowance_rate_json TEXT NOT NULL,
              PRIMARY KEY (scenario_id, job_code),
              FOREIGN KEY (scenario_id, job_code) REFERENCES md_job_role(scenario_id, job_code) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS md_expense_item (
              scenario_id TEXT NOT NULL,
              exp_code    TEXT NOT NULL,
              exp_name    TEXT NOT NULL,
              group_code  TEXT NOT NULL,
              sort_order  INTEGER NOT NULL DEFAULT 0,
              is_active   INTEGER NOT NULL DEFAULT 1,
              PRIMARY KEY (scenario_id, exp_code)
            );

            CREATE TABLE IF NOT EXISTS md_expense_pricebook (
              scenario_id TEXT NOT NULL,
              exp_code    TEXT NOT NULL,
              unit_price  INTEGER NOT NULL,
              unit        TEXT NOT NULL,
              effective_from TEXT NOT NULL,
              effective_to   TEXT,
              PRIMARY KEY (scenario_id, exp_code, effective_from),
              FOREIGN KEY (scenario_id, exp_code) REFERENCES md_expense_item(scenario_id, exp_code) ON DELETE CASCADE
            );
            """,
        )
        ,
        (
            "20260209_01_scenario_input.sql",
            """
            CREATE TABLE IF NOT EXISTS scenario_input (
              scenario_id TEXT PRIMARY KEY,
              input_json  TEXT NOT NULL,
              updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
            );
            """,
        ),
        (
            "20260209_02_calculation_result.sql",
            """
            CREATE TABLE IF NOT EXISTS calculation_result (
              scenario_id TEXT PRIMARY KEY,
              result_json TEXT NOT NULL,
              updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
            );
            """,
        ),
    ]


def run_migrations(conn: sqlite3.Connection | None = None) -> None:
    external_conn = conn is not None
    if conn is None:
        conn = get_connection()
    else:
        conn.execute("PRAGMA foreign_keys=ON;")
    try:
        _ensure_schema_migrations(conn)
        applied = _applied_versions(conn)
        files = _list_migration_files()
        if files:
            for path in files:
                version = path.name
                if version in applied:
                    continue
                sql = _load_migration_sql(path)
                conn.executescript(sql)
                conn.execute(
                    "INSERT INTO schema_migrations(version) VALUES (?)",
                    (version,),
                )
                conn.commit()
        else:
            for version, sql in _embedded_migrations():
                if version in applied:
                    continue
                conn.executescript(sql)
                conn.execute(
                    "INSERT INTO schema_migrations(version) VALUES (?)",
                    (version,),
                )
                conn.commit()
    finally:
        if not external_conn:
            conn.close()
