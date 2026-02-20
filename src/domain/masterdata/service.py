import sqlite3
from pathlib import Path
import importlib.resources as resources


def _scenario_has_masterdata(conn: sqlite3.Connection, scenario_id: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM md_job_role WHERE scenario_id=? LIMIT 1",
        (scenario_id,),
    ).fetchone()
    return row is not None


def _any_masterdata_exists(conn: sqlite3.Connection) -> bool:
    row = conn.execute("SELECT 1 FROM md_job_role LIMIT 1").fetchone()
    return row is not None


def _list_seed_files() -> list[Path]:
    files = []
    try:
        pkg = resources.files(__package__ + ".seeds")
        for entry in pkg.iterdir():
            if entry.name.endswith(".sql"):
                files.append(Path(str(entry)))
    except Exception:
        pass

    if not files:
        fs_dir = Path(__file__).resolve().parent / "seeds"
        if fs_dir.exists():
            files = list(fs_dir.glob("*.sql"))

    return sorted(files, key=lambda p: p.name)


def apply_seed_if_needed(conn: sqlite3.Connection) -> None:
    if _any_masterdata_exists(conn):
        return

    for path in _list_seed_files():
        sql = path.read_text(encoding="utf-8")
        conn.executescript(sql)
        conn.commit()


def copy_masterdata(conn: sqlite3.Connection, from_scenario_id: str, to_scenario_id: str) -> None:
    if from_scenario_id == to_scenario_id:
        raise ValueError("source and target scenario_id must be different")

    if _scenario_has_masterdata(conn, to_scenario_id):
        raise ValueError("target scenario already has master data")

    conn.execute(
        """
        INSERT INTO md_job_role (scenario_id, job_code, job_name, sort_order, is_active)
        SELECT ?, job_code, job_name, sort_order, is_active
        FROM md_job_role
        WHERE scenario_id=?
        """,
        (to_scenario_id, from_scenario_id),
    )
    conn.execute(
        """
        INSERT INTO md_job_rate (scenario_id, job_code, wage_day, wage_hour, allowance_rate_json)
        SELECT ?, job_code, wage_day, wage_hour, allowance_rate_json
        FROM md_job_rate
        WHERE scenario_id=?
        """,
        (to_scenario_id, from_scenario_id),
    )
    conn.execute(
        """
        INSERT INTO md_expense_item (scenario_id, exp_code, exp_name, group_code, sort_order, is_active)
        SELECT ?, exp_code, exp_name, group_code, sort_order, is_active
        FROM md_expense_item
        WHERE scenario_id=?
        """,
        (to_scenario_id, from_scenario_id),
    )
    conn.execute(
        """
        INSERT INTO md_expense_pricebook (scenario_id, exp_code, unit_price, unit, effective_from, effective_to)
        SELECT ?, exp_code, unit_price, unit, effective_from, effective_to
        FROM md_expense_pricebook
        WHERE scenario_id=?
        """,
        (to_scenario_id, from_scenario_id),
    )
    # 경비 세부 항목 복사
    conn.execute(
        """
        INSERT OR IGNORE INTO md_expense_sub_item
          (scenario_id, exp_code, sub_code, sub_name, spec, unit,
           quantity, unit_price, amount, remark, sort_order, is_active)
        SELECT ?, exp_code, sub_code, sub_name, spec, unit,
               quantity, unit_price, amount, remark, sort_order, is_active
        FROM md_expense_sub_item
        WHERE scenario_id=?
        """,
        (to_scenario_id, from_scenario_id),
    )


def choose_base_scenario(conn: sqlite3.Connection) -> str | None:
    if _scenario_has_masterdata(conn, "default"):
        return "default"

    row = conn.execute(
        """
        SELECT scenario_id
        FROM md_job_role
        ORDER BY rowid DESC
        LIMIT 1
        """
    ).fetchone()
    return row[0] if row else None
