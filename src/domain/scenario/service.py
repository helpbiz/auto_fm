import sqlite3

from ..migration_runner import run_migrations
from ..db import get_connection
from ..masterdata.service import apply_seed_if_needed, copy_masterdata, choose_base_scenario


def create_scenario(scenario_id: str) -> None:
    conn = get_connection()
    try:
        run_migrations(conn)
        apply_seed_if_needed(conn)

        base_id = choose_base_scenario(conn)
        if base_id is None:
            raise ValueError("no base scenario available")

        conn.execute("BEGIN")
        copy_masterdata(conn, base_id, scenario_id)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def clone_scenario(source_id: str, target_id: str) -> None:
    conn = get_connection()
    try:
        run_migrations(conn)
        conn.execute("BEGIN")
        copy_masterdata(conn, source_id, target_id)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
