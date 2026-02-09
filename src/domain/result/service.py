from decimal import Decimal

from src.domain.context.calc_context import CalcContext
from src.domain.calculator.labor import LaborCostCalculator
from src.domain.aggregator import Aggregator
from src.domain.masterdata.repo import MasterDataRepo
import json

from src.domain.scenario_input.service import get_scenario_input
from src.domain.db import get_connection


DEFAULT_WEEKLY_HOLIDAY_DAYS = Decimal("4.33")
DEFAULT_ANNUAL_LEAVE_DAYS = Decimal("1.25")


def calculate_result(scenario_id: str, conn=None) -> dict:
    external_conn = conn is not None
    if conn is None:
        conn = get_connection()
    canonical = get_scenario_input(scenario_id, conn)
    repo = MasterDataRepo(conn)
    job_roles = repo.get_job_roles(scenario_id)
    rates_source = repo.get_job_rates(scenario_id)
    if isinstance(rates_source, dict):
        rates_iter = rates_source.values()
    else:
        rates_iter = rates_source
    job_rates = {r.job_code: r.wage_day for r in rates_iter}
    expense_items = repo.get_expense_items(scenario_id)
    pricebook = repo.get_expense_pricebook(scenario_id)

    labor_rows, labor_total, job_breakdown = _calculate_labor(
        canonical, job_roles, job_rates
    )
    expense_rows, expense_total = _calculate_expenses(
        canonical, expense_items, pricebook
    )

    aggregator = Aggregator(
        labor_total=labor_total,
        fixed_expense_total=expense_total,
        variable_expense_total=0,
        passthrough_expense_total=0,
        overhead_cost=0,
        profit=0,
    )

    result = {
        "aggregator": aggregator,
        "labor_rows": labor_rows,
        "expense_rows": expense_rows,
        "job_breakdown": job_breakdown,
    }
    _save_result_snapshot(conn, scenario_id, result)
    if not external_conn:
        conn.close()
    return result


def _calculate_labor(canonical: dict, job_roles: list, job_rates: dict) -> tuple[list[dict], int, list[dict]]:
    labor_inputs = canonical.get("labor", {}).get("job_roles", {})
    total = 0
    rows: list[dict] = []
    job_breakdown: list[dict] = []

    for role in job_roles:
        if not role.is_active:
            continue
        values = labor_inputs.get(role.job_code)
        if not isinstance(values, dict):
            continue

        headcount = Decimal(str(values.get("headcount", 0)))
        work_days = Decimal(str(values.get("work_days", 0)))
        work_hours = Decimal(str(values.get("work_hours", 0)))
        overtime_hours = Decimal(str(values.get("overtime_hours", 0)))
        holiday_work_hours = Decimal(str(values.get("holiday_work_hours", 0)))
        if headcount == 0:
            continue

        wage_day = Decimal(str(job_rates.get(role.job_code, 0)))
        context = CalcContext(
            project_name=role.job_name,
            year=2025,
            manpower={role.job_code: headcount},
            wage_rate={role.job_code: wage_day},
            monthly_workdays=work_days,
            daily_work_hours=work_hours,
            weekly_holiday_days=DEFAULT_WEEKLY_HOLIDAY_DAYS,
            annual_leave_days=DEFAULT_ANNUAL_LEAVE_DAYS,
            expenses={},
            overtime_hours=overtime_hours,
            holiday_work_hours=holiday_work_hours,
        )
        context.job_name_map = {role.job_code: role.job_name}

        labor_result = LaborCostCalculator(context).calculate()
        total += labor_result["total_labor_cost"]

        for line in labor_result.get("job_lines", []):
            rows.append(
                {
                    "job_code": line.job_code,
                    "role": role.job_name,
                    "headcount": line.headcount,
                    "base_salary": line.base_salary,
                    "allowances": line.allowances,
                    "insurance_total": line.insurance_total,
                    "labor_subtotal": line.labor_subtotal,
                    "role_total": line.total,
                }
            )
            job_breakdown.append(
                {
                    "job_code": line.job_code,
                    "job_name": line.job_name,
                    "headcount": line.headcount,
                    "work_days": line.work_days,
                    "base_wage": line.base_wage,
                    "allowance": line.allowance,
                    "overtime": line.overtime,
                    "total": line.total,
                }
            )

    return rows, total, job_breakdown


def _calculate_expenses(canonical: dict, items: list, pricebook: list) -> tuple[list[dict], int]:
    inputs = canonical.get("expenses", {}).get("items", {})
    price_map = _price_map(pricebook)
    total = 0
    rows: list[dict] = []

    for item in items:
        if not item.is_active:
            continue
        values = inputs.get(item.exp_code, {})
        quantity = Decimal(str(values.get("quantity", 0)))
        unit_price = int(values.get("unit_price", price_map.get(item.exp_code, 0)))
        row_total = int(quantity * Decimal(str(unit_price)))
        if quantity == 0 and unit_price == 0:
            continue

        total += row_total
        rows.append(
            {
                "category": item.group_code,
                "name": item.exp_name,
                "driver": "quantity",
                "unit_cost": str(unit_price),
                "quantity": str(quantity),
                "row_total": str(row_total),
                "type": "Expense",
            }
        )

    return rows, total


def _price_map(pricebook: list) -> dict[str, int]:
    result: dict[str, int] = {}
    for price in pricebook:
        if price.exp_code not in result:
            result[price.exp_code] = int(price.unit_price)
    return result


def get_result_snapshot(scenario_id: str, conn=None) -> dict | None:
    external_conn = conn is not None
    if conn is None:
        conn = get_connection()
    try:
        row = conn.execute(
            "SELECT result_json FROM calculation_result WHERE scenario_id=?",
            (scenario_id,),
        ).fetchone()
        if row is None:
            return None
        return json.loads(row[0])
    finally:
        if not external_conn:
            conn.close()


def _save_result_snapshot(conn, scenario_id: str, result: dict) -> None:
    snapshot = {
        "aggregator": {
            "labor_total": result["aggregator"].labor_total,
            "fixed_expense_total": result["aggregator"].fixed_expense_total,
            "variable_expense_total": result["aggregator"].variable_expense_total,
            "passthrough_expense_total": result["aggregator"].passthrough_expense_total,
            "overhead_cost": result["aggregator"].overhead_cost,
            "profit": result["aggregator"].profit,
            "grand_total": result["aggregator"].grand_total,
        },
        "labor_rows": result["labor_rows"],
        "expense_rows": result["expense_rows"],
        "job_breakdown": result["job_breakdown"],
    }
    payload = json.dumps(snapshot, ensure_ascii=True)
    conn.execute(
        """
        INSERT INTO calculation_result (scenario_id, result_json, updated_at)
        VALUES (?, ?, datetime('now'))
        ON CONFLICT(scenario_id) DO UPDATE SET
          result_json=excluded.result_json,
          updated_at=datetime('now')
        """,
        (scenario_id, payload),
    )
    conn.commit()
