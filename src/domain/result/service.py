import json
from decimal import Decimal

from src.domain.context.calc_context import CalcContext
from src.domain.calculator.labor import LaborCostCalculator
from src.domain.calculator.expense import ExpenseCostCalculator
from src.domain.aggregator import Aggregator
from src.domain.masterdata.repo import MasterDataRepo
from src.domain.constants.expense_groups import category_label
from src.domain.scenario_input.service import get_scenario_input
from src.domain.db import get_connection
from src.domain.settings_manager import get_safety_management_rate
from src.domain.wage_manager import WageManager


DEFAULT_WEEKLY_HOLIDAY_DAYS = Decimal("4.33")
DEFAULT_ANNUAL_LEAVE_DAYS = Decimal("1.25")


def calculate_result(scenario_id: str, conn=None, overhead_rate: float = 0.0, profit_rate: float = 0.0) -> dict:
    external_conn = conn is not None
    if conn is None:
        conn = get_connection()
    canonical = get_scenario_input(scenario_id, conn)
    # canonical에 저장된 비율을 파라미터 미지정 시 fallback으로 사용
    if overhead_rate == 0.0 and canonical.get("overhead_rate"):
        overhead_rate = float(canonical["overhead_rate"])
    if profit_rate == 0.0 and canonical.get("profit_rate"):
        profit_rate = float(canonical["profit_rate"])
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

    # 세부 항목 로드 (exp_code별 그룹핑)
    all_sub_items = repo.get_expense_sub_items(scenario_id)
    sub_items_map: dict[str, list] = {}
    for si in all_sub_items:
        sub_items_map.setdefault(si.exp_code, []).append(si)

    labor_rows, labor_total, job_breakdown, insurance_aggregate = _calculate_labor(
        canonical, job_roles, job_rates
    )
    insurance_by_exp_code = _build_insurance_by_exp_code(insurance_aggregate)
    expense_rows, fixed_total, variable_total, passthrough_total = _calculate_expenses(
        canonical, expense_items, pricebook, sub_items_map,
        labor_total=labor_total,
        insurance_by_exp_code=insurance_by_exp_code,
        expense_items=expense_items,
    )

    # Calculate overhead and profit based on rates
    # Overhead base: labor + fixed expenses
    overhead_base = labor_total + fixed_total
    overhead_cost = int(overhead_base * overhead_rate / 100)

    # Profit base: labor + fixed expenses + overhead
    profit_base = labor_total + fixed_total + overhead_cost
    profit = int(profit_base * profit_rate / 100)

    aggregator = Aggregator(
        labor_total=labor_total,
        fixed_expense_total=fixed_total,
        variable_expense_total=variable_total,
        passthrough_expense_total=passthrough_total,
        overhead_cost=overhead_cost,
        profit=profit,
    )

    result = {
        "aggregator": aggregator,
        "labor_rows": labor_rows,
        "expense_rows": expense_rows,
        "job_breakdown": job_breakdown,
        "insurance_by_exp_code": insurance_by_exp_code,
    }
    _save_result_snapshot(conn, scenario_id, result)
    if not external_conn:
        conn.close()
    return result


# 노무비 인적보험 항목별 키 → 경비코드(exp_code) 매핑
LABOR_INSURANCE_TO_EXP_CODE = {
    "industrial_accident": "FIX_INS_INDUST",
    "national_pension": "FIX_INS_PENSION",
    "employment": "FIX_INS_EMPLOY",
    "health": "FIX_INS_HEALTH",
    "long_term_care": "FIX_INS_LONGTERM",
    "wage_bond": "FIX_INS_WAGE",
    "asbestos": "FIX_INS_ASBESTOS",
}


def _calculate_labor(canonical: dict, job_roles: list, job_rates: dict) -> tuple[list[dict], int, list[dict], dict]:
    labor_inputs = canonical.get("labor", {}).get("job_roles", {})
    total = 0
    rows: list[dict] = []
    job_breakdown: list[dict] = []
    insurance_aggregate: dict[str, int] = {
        k: 0 for k in LABOR_INSURANCE_TO_EXP_CODE
    }
    # 노무비 상세 기본급 계산 시 일급: data/wages_master.json의 md_basic 적용 (있으면), 없으면 DB 단가
    wage_year = canonical.get("wage_year") or canonical.get("base_year") or 2025
    wage_year = int(wage_year) if wage_year else 2025
    wage_manager = WageManager()

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
        holiday_work_days = Decimal(str(values.get("holiday_work_days", values.get("holiday_work_hours", 0))))
        if headcount == 0:
            continue

        md_basic = wage_manager.get_md_basic(role.job_code, wage_year)
        if md_basic is not None:
            wage_day = Decimal(md_basic)
        else:
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
            holiday_work_days=holiday_work_days,
        )
        context.job_name_map = {role.job_code: role.job_name}

        labor_result = LaborCostCalculator(context).calculate()
        total += labor_result["total_labor_cost"]
        ins = labor_result.get("insurance", {})
        for key in insurance_aggregate:
            insurance_aggregate[key] += ins.get(key, 0)

        for line in labor_result.get("job_lines", []):
            # 노무비 상세 테이블용: role(직무명), headcount, 기본급, 제수당, 보험료, 인건비 소계, 산정 금액
            def _v(obj, key, default=0):
                if hasattr(obj, key):
                    return getattr(obj, key, default)
                return obj.get(key, default) if isinstance(obj, dict) else default
            rows.append(
                {
                    "job_code": _v(line, "job_code", ""),
                    "role": _v(line, "job_name", "") or role.job_name,
                    "headcount": int(_v(line, "headcount", 0)),
                    "base_salary": int(_v(line, "base_salary", 0)),
                    "bonus": int(_v(line, "bonus", 0)),
                    "allowances": int(_v(line, "allowances", 0)),
                    "retirement": int(_v(line, "retirement", 0)),
                    "labor_subtotal": int(_v(line, "labor_subtotal", 0)),
                    "role_total": int(_v(line, "role_total", 0) or _v(line, "total", 0)),
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

    return rows, total, job_breakdown, insurance_aggregate


def _build_insurance_by_exp_code(insurance_aggregate: dict) -> dict[str, int]:
    """노무비 인적보험 집계 → exp_code별 금액 dict."""
    return {
        exp_code: insurance_aggregate.get(labor_key, 0)
        for labor_key, exp_code in LABOR_INSURANCE_TO_EXP_CODE.items()
    }


def _virtual_sub_item_row(exp_code: str, exp_name: str, amount: int) -> dict:
    """노무비에서 계산된 인적보험 1행 (세부 입력 자동 채움용)."""
    return {
        "sub_code": exp_code,
        "sub_name": exp_name or exp_code,
        "spec": "",
        "unit": "원/월",
        "quantity": 1,
        "unit_price": amount,
        "amount": amount,
        "remark": "노무비에서 계산",
        "sort_order": 0,
        "is_active": 1,
    }


def _merge_labor_insurance_into_sub_items(
    sub_items_map: dict,
    insurance_by_exp_code: dict[str, int],
    expense_items: list,
) -> None:
    """인적보험 7개에 대해 노무비 계산값으로 세부 1행씩 병합 (in-place)."""
    if not sub_items_map:
        sub_items_map.clear()
    def _exp_code(i):
        return getattr(i, "exp_code", i.get("exp_code") if isinstance(i, dict) else "")
    def _exp_name(i):
        return getattr(i, "exp_name", i.get("exp_name", "") if isinstance(i, dict) else "")
    item_map = {_exp_code(i): _exp_name(i) for i in expense_items}
    for exp_code, amount in insurance_by_exp_code.items():
        if amount is None:
            continue
        sub_items_map[exp_code] = [
            _virtual_sub_item_row(exp_code, item_map.get(exp_code, exp_code), int(amount))
        ]


def _calculate_expenses(
    canonical: dict, items: list, pricebook: list,
    sub_items_map: dict = None,
    labor_total: int = 0,
    insurance_by_exp_code: dict = None,
    expense_items: list = None,
) -> tuple[list[dict], int, int, int]:
    inputs = canonical.get("expenses", {}).get("items", {})
    price_map = _price_map(pricebook)
    safety_rate = get_safety_management_rate()
    sub_items_map = dict(sub_items_map) if sub_items_map else {}
    if insurance_by_exp_code and expense_items is not None:
        _merge_labor_insurance_into_sub_items(
            sub_items_map, insurance_by_exp_code, expense_items
        )

    calculator = ExpenseCostCalculator(
        items, inputs, price_map, sub_items_map,
        labor_total=labor_total,
        safety_management_rate=safety_rate,
    )
    result = calculator.calculate()

    rows: list[dict] = []
    for line in result.lines:
        sub_rows = []
        for sl in line.sub_lines:
            sub_rows.append({
                "sub_code": sl.sub_code,
                "sub_name": sl.sub_name,
                "spec": sl.spec,
                "unit": sl.unit,
                "quantity": sl.quantity,
                "unit_price": sl.unit_price,
                "amount": sl.amount,
                "remark": sl.remark,
            })

        rows.append(
            {
                "exp_code": line.exp_code,
                "category": line.group_code,
                "name": line.exp_name,
                "driver": "quantity",
                "unit_cost": str(line.unit_price),
                "quantity": str(line.quantity),
                "row_total": str(line.row_total),
                "type": category_label(line.category),
                "sub_items": sub_rows,
            }
        )

    return rows, result.fixed_total, result.variable_total, result.passthrough_total


def _price_map(pricebook: list) -> dict[str, int]:
    result: dict[str, int] = {}
    for price in pricebook:
        if price.exp_code not in result:
            result[price.exp_code] = int(price.unit_price)
    return result


def get_expense_rows_for_display(
    scenario_id: str,
    conn,
    sub_items_by_exp: dict[str, list],
    labor_total: int,
) -> list[dict]:
    """현재 경비 세부(sub_items_by_exp)와 노무비 합계로 경비 상세 테이블용 expense_rows 생성.
    직무 변경 시 경비입력과 동일한 보험 7종이 경비 상세에도 반영되도록 호출."""
    canonical = get_scenario_input(scenario_id, conn)
    repo = MasterDataRepo(conn)
    expense_items = repo.get_expense_items(scenario_id)
    pricebook = repo.get_expense_pricebook(scenario_id)
    expense_rows, _, _, _ = _calculate_expenses(
        canonical,
        expense_items,
        pricebook,
        sub_items_map=sub_items_by_exp,
        labor_total=labor_total,
        insurance_by_exp_code=None,
        expense_items=expense_items,
    )
    return expense_rows


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


def get_insurance_by_exp_code_for_scenario(scenario_id: str, conn) -> dict[str, int]:
    """시나리오의 직무/인원·단가로 노무비 보험료 7종 금액을 계산해 exp_code별 dict로 반환. (스냅샷 없을 때 경비입력 보험 7종 표시용)"""
    try:
        canonical = get_scenario_input(scenario_id, conn)
        repo = MasterDataRepo(conn)
        job_roles = repo.get_job_roles(scenario_id)
        rates_source = repo.get_job_rates(scenario_id)
        if isinstance(rates_source, dict):
            rates_iter = rates_source.values()
        else:
            rates_iter = rates_source
        job_rates = {r.job_code: r.wage_day for r in rates_iter}
        _, _, _, insurance_aggregate = _calculate_labor(canonical, job_roles, job_rates)
        return _build_insurance_by_exp_code(insurance_aggregate)
    except Exception:
        return {}


def get_insurance_by_exp_code_from_ui(job_inputs: dict, scenario_id: str, conn, wage_year: int = None) -> dict[str, int]:
    """현재 UI의 직무별 입력(job_inputs)과 DB의 job_roles/rates로 보험료 7종 계산. DB 반영 없이 경비입력 탭 갱신용."""
    try:
        repo = MasterDataRepo(conn)
        job_roles = repo.get_job_roles(scenario_id)
        if not job_roles and job_inputs:
            from types import SimpleNamespace
            job_roles = [
                SimpleNamespace(job_code=jc, job_name=jc, is_active=1)
                for jc in job_inputs
            ]
        rates_source = repo.get_job_rates(scenario_id)
        if isinstance(rates_source, dict):
            rates_iter = rates_source.values()
        else:
            rates_iter = rates_source
        job_rates = {r.job_code: getattr(r, "wage_day", 0) for r in rates_iter} if rates_source else {}
        canonical = {"labor": {"job_roles": job_inputs}}
        if wage_year is not None:
            canonical["wage_year"] = wage_year
        _, _, _, insurance_aggregate = _calculate_labor(canonical, job_roles, job_rates)
        return _build_insurance_by_exp_code(insurance_aggregate)
    except Exception:
        return {}


def get_labor_rows_from_ui(job_inputs: dict, scenario_id: str, conn, wage_year: int = None) -> list[dict]:
    """현재 UI의 직무별 입력(job_inputs)과 DB의 job_roles/rates로 노무비 상세(labor_rows) 계산. DB 반영 없이 노무비 상세 탭 갱신용."""
    try:
        repo = MasterDataRepo(conn)
        job_roles = repo.get_job_roles(scenario_id)
        if not job_roles and job_inputs:
            from types import SimpleNamespace
            job_roles = [
                SimpleNamespace(job_code=jc, job_name=jc, is_active=1)
                for jc in job_inputs
            ]
        rates_source = repo.get_job_rates(scenario_id)
        if isinstance(rates_source, dict):
            job_rates = {code: getattr(r, "wage_day", 0) for code, r in rates_source.items()}
        else:
            rates_iter = rates_source if rates_source else []
            job_rates = {getattr(r, "job_code", ""): getattr(r, "wage_day", 0) for r in rates_iter}
        canonical = {"labor": {"job_roles": job_inputs}}
        if wage_year is not None:
            canonical["wage_year"] = wage_year
        labor_rows, _, _, _ = _calculate_labor(canonical, job_roles, job_rates)
        return labor_rows
    except Exception:
        return []


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
        "insurance_by_exp_code": result.get("insurance_by_exp_code") or {},
    }
    def _json_default(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

    payload = json.dumps(snapshot, ensure_ascii=True, default=_json_default)
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
