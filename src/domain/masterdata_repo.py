import sqlite3
from dataclasses import dataclass
from typing import Optional

from .db import get_connection


@dataclass
class JobRole:
    scenario_id: str
    job_code: str
    job_name: str
    sort_order: int
    is_active: int


@dataclass
class JobRate:
    scenario_id: str
    job_code: str
    wage_day: int
    wage_hour: int
    allowance_rate_json: str


@dataclass
class ExpenseItem:
    scenario_id: str
    exp_code: str
    exp_name: str
    group_code: str
    sort_order: int
    is_active: int


@dataclass
class ExpensePrice:
    scenario_id: str
    exp_code: str
    unit_price: int
    unit: str
    effective_from: str
    effective_to: Optional[str]


class MasterDataRepo:
    def __init__(self):
        self._conn = get_connection()

    def close(self) -> None:
        self._conn.close()

    def scenario_exists(self, scenario_id: str) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM md_job_role WHERE scenario_id=? LIMIT 1",
            (scenario_id,),
        ).fetchone()
        return row is not None

    def get_job_roles(self, scenario_id: str) -> list[JobRole]:
        rows = self._conn.execute(
            """
            SELECT scenario_id, job_code, job_name, sort_order, is_active
            FROM md_job_role
            WHERE scenario_id=?
            ORDER BY sort_order, job_code
            """,
            (scenario_id,),
        ).fetchall()
        return [JobRole(*row) for row in rows]

    def get_job_rates(self, scenario_id: str) -> list[JobRate]:
        rows = self._conn.execute(
            """
            SELECT scenario_id, job_code, wage_day, wage_hour, allowance_rate_json
            FROM md_job_rate
            WHERE scenario_id=?
            """,
            (scenario_id,),
        ).fetchall()
        return [JobRate(*row) for row in rows]

    def get_expense_items(self, scenario_id: str) -> list[ExpenseItem]:
        rows = self._conn.execute(
            """
            SELECT scenario_id, exp_code, exp_name, group_code, sort_order, is_active
            FROM md_expense_item
            WHERE scenario_id=?
            ORDER BY sort_order, exp_code
            """,
            (scenario_id,),
        ).fetchall()
        return [ExpenseItem(*row) for row in rows]

    def get_expense_pricebook(self, scenario_id: str) -> list[ExpensePrice]:
        rows = self._conn.execute(
            """
            SELECT scenario_id, exp_code, unit_price, unit, effective_from, effective_to
            FROM md_expense_pricebook
            WHERE scenario_id=?
            ORDER BY exp_code, effective_from DESC
            """,
            (scenario_id,),
        ).fetchall()
        return [ExpensePrice(*row) for row in rows]

    def clone_scenario(self, source_id: str, target_id: str) -> None:
        if source_id == target_id:
            return
        self._conn.execute(
            """
            INSERT INTO md_job_role (scenario_id, job_code, job_name, sort_order, is_active)
            SELECT ?, job_code, job_name, sort_order, is_active
            FROM md_job_role
            WHERE scenario_id=?
            """,
            (target_id, source_id),
        )
        self._conn.execute(
            """
            INSERT INTO md_job_rate (scenario_id, job_code, wage_day, wage_hour, allowance_rate_json)
            SELECT ?, job_code, wage_day, wage_hour, allowance_rate_json
            FROM md_job_rate
            WHERE scenario_id=?
            """,
            (target_id, source_id),
        )
        self._conn.execute(
            """
            INSERT INTO md_expense_item (scenario_id, exp_code, exp_name, group_code, sort_order, is_active)
            SELECT ?, exp_code, exp_name, group_code, sort_order, is_active
            FROM md_expense_item
            WHERE scenario_id=?
            """,
            (target_id, source_id),
        )
        self._conn.execute(
            """
            INSERT INTO md_expense_pricebook (scenario_id, exp_code, unit_price, unit, effective_from, effective_to)
            SELECT ?, exp_code, unit_price, unit, effective_from, effective_to
            FROM md_expense_pricebook
            WHERE scenario_id=?
            """,
            (target_id, source_id),
        )
        self._conn.commit()
