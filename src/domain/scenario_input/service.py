import json
import logging
import os
import sqlite3
from dataclasses import dataclass
from typing import Any

from src.domain.masterdata.repo import MasterDataRepo, JobRole, ExpenseItem, ExpensePrice
from src.domain.normalization import normalize_job_inputs
from src.domain.db import get_db_path, handle_disk_io_error


@dataclass
class ValidationError:
    code: str
    field_path: str
    message: str


class ScenarioInputValidationError(ValueError):
    def __init__(self, errors: list[ValidationError]):
        super().__init__("scenario_input validation failed")
        self.errors = errors


MAX_HEADCOUNT = 10_000.0
MAX_WORK_DAYS = 31.0
MAX_WORK_HOURS = 24.0
MAX_OVERTIME_HOURS = 200.0
MAX_HOLIDAY_WORK_DAYS = 31.0
MAX_QUANTITY = 1_000_000.0
MAX_UNIT_PRICE = 100_000_000


def post_scenario_input(
    raw: dict,
    scenario_id: str,
    conn,
) -> dict:
    canonical = normalize_scenario_input(raw, scenario_id, conn)
    errors = validate_scenario_input(canonical)
    if errors:
        raise ScenarioInputValidationError(errors)
    _save_canonical(conn, scenario_id, canonical)
    return canonical


def save_canonical_direct(conn, scenario_id: str, canonical: dict) -> None:
    """집계 시 사용한 canonical을 그대로 DB에 저장. normalize/validate 없이 직렬화만 수행."""
    errors = validate_scenario_input(canonical)
    if errors:
        raise ScenarioInputValidationError(errors)
    _save_canonical(conn, scenario_id, canonical)


def get_scenario_input(scenario_id: str, conn) -> dict:
    row = conn.execute(
        "SELECT input_json FROM scenario_input WHERE scenario_id=?",
        (scenario_id,),
    ).fetchone()
    if row is None:
        return _empty_canonical()

    try:
        stored = json.loads(row[0])
    except (TypeError, ValueError):
        stored = {}

    if _is_canonical(stored):
        return stored

    canonical = normalize_scenario_input(stored, scenario_id, conn)
    _save_canonical(conn, scenario_id, canonical)
    return canonical


def list_scenario_ids(conn) -> list[str]:
    rows = conn.execute(
        "SELECT scenario_id FROM scenario_input ORDER BY scenario_id",
    ).fetchall()
    return [row[0] for row in rows]


def list_scenarios(conn) -> list[tuple[str, str]]:
    """(scenario_id, display_name) 목록. display_name은 input_json의 _display_name, 없으면 scenario_id."""
    rows = conn.execute(
        "SELECT scenario_id, input_json FROM scenario_input ORDER BY scenario_id",
    ).fetchall()
    result = []
    for scenario_id, input_json in rows:
        display_name = scenario_id
        try:
            data = json.loads(input_json) if input_json else {}
            if isinstance(data, dict) and data.get("_display_name"):
                display_name = str(data["_display_name"]).strip() or scenario_id
        except (TypeError, ValueError):
            pass
        result.append((scenario_id, display_name))
    return result


def resolve_scenario_id(conn, scenario_name: str, sanitize_fn) -> str:
    """불러오기 시 사용할 scenario_id. 한글 제거 등으로 id가 달라져도 저장된 시나리오를 찾도록 보정."""
    sid = sanitize_fn(scenario_name) if scenario_name else ""
    if not sid:
        return "default"
    row = conn.execute(
        "SELECT 1 FROM scenario_input WHERE scenario_id = ?",
        (sid,),
    ).fetchone()
    if row is not None:
        return sid
    # 예: "2023설계" -> "2023", 저장된 id는 "2023_" 인 경우
    alt = sid + "_"
    row2 = conn.execute(
        "SELECT 1 FROM scenario_input WHERE scenario_id = ?",
        (alt,),
    ).fetchone()
    if row2 is not None:
        return alt
    return sid


def delete_scenario(scenario_id: str, conn) -> None:
    """시나리오 ID에 해당하는 DB 데이터를 모두 삭제한다. (FK 순서 준수)"""
    if not scenario_id or scenario_id.strip() == "":
        raise ValueError("scenario_id가 비어 있습니다.")
    # default 시나리오는 삭제 불가
    if scenario_id.strip().lower() == "default":
        raise ValueError("default 시나리오는 삭제할 수 없습니다.")
    # FK 순서: sub_item → pricebook → expense_item, job_rate → job_role → calculation_result → scenario_input
    conn.execute("DELETE FROM md_expense_sub_item WHERE scenario_id=?", (scenario_id,))
    conn.execute("DELETE FROM md_expense_pricebook WHERE scenario_id=?", (scenario_id,))
    conn.execute("DELETE FROM md_expense_item WHERE scenario_id=?", (scenario_id,))
    conn.execute("DELETE FROM md_job_rate WHERE scenario_id=?", (scenario_id,))
    conn.execute("DELETE FROM md_job_role WHERE scenario_id=?", (scenario_id,))
    conn.execute("DELETE FROM calculation_result WHERE scenario_id=?", (scenario_id,))
    conn.execute("DELETE FROM scenario_input WHERE scenario_id=?", (scenario_id,))
    conn.commit()
    logging.info("시나리오 삭제 완료: %s", scenario_id)


def normalize_scenario_input(raw: dict, scenario_id: str, conn) -> dict:
    repo = MasterDataRepo(conn)
    job_roles = repo.get_job_roles(scenario_id)
    expense_items = repo.get_expense_items(scenario_id)
    expense_pricebook = repo.get_expense_pricebook(scenario_id)

    labor_job_roles = _normalize_labor(raw, job_roles)
    expense_items_map = _normalize_expenses(raw, expense_items, expense_pricebook)

    result = {
        "labor": {"job_roles": labor_job_roles},
        "expenses": {"items": expense_items_map},
    }
    # 저장/로드 시 복원할 선택 항목 보존
    for key in (
        "overhead_rate",
        "profit_rate",
        "base_year",
        "wage_year",
        "wage_half",
        "_display_name",
        "holiday_work_days_calc",
    ):
        if key in raw and raw[key] is not None:
            result[key] = raw[key]
    return result


def validate_scenario_input(canonical: dict) -> list[ValidationError]:
    errors: list[ValidationError] = []

    labor = canonical.get("labor", {})
    job_roles = labor.get("job_roles", {})
    for job_code, values in job_roles.items():
        headcount = values.get("headcount")
        work_days = values.get("work_days")
        work_hours = values.get("work_hours", 0.0)
        overtime_hours = values.get("overtime_hours", 0.0)
        holiday_work_days = values.get("holiday_work_days", values.get("holiday_work_hours", 0.0))

        _validate_float(
            errors,
            headcount,
            f"labor.job_roles.{job_code}.headcount",
            0.0,
            MAX_HEADCOUNT,
        )
        _validate_float(
            errors,
            work_days,
            f"labor.job_roles.{job_code}.work_days",
            0.0,
            MAX_WORK_DAYS,
        )
        _validate_float(
            errors,
            work_hours,
            f"labor.job_roles.{job_code}.work_hours",
            0.0,
            MAX_WORK_HOURS,
        )
        _validate_float(
            errors,
            overtime_hours,
            f"labor.job_roles.{job_code}.overtime_hours",
            0.0,
            MAX_OVERTIME_HOURS,
        )
        _validate_float(
            errors,
            holiday_work_days,
            f"labor.job_roles.{job_code}.holiday_work_days",
            0.0,
            MAX_HOLIDAY_WORK_DAYS,
        )

    expenses = canonical.get("expenses", {})
    items = expenses.get("items", {})
    for exp_code, values in items.items():
        quantity = values.get("quantity")
        unit_price = values.get("unit_price")

        _validate_float(
            errors,
            quantity,
            f"expenses.items.{exp_code}.quantity",
            0.0,
            MAX_QUANTITY,
        )

        if not isinstance(unit_price, int):
            errors.append(
                ValidationError(
                    code="INVALID_TYPE",
                    field_path=f"expenses.items.{exp_code}.unit_price",
                    message="unit_price must be integer",
                )
            )
        else:
            _validate_int(
                errors,
                unit_price,
                f"expenses.items.{exp_code}.unit_price",
                0,
                MAX_UNIT_PRICE,
            )

    return errors


def _normalize_labor(raw: dict, job_roles: list[JobRole]) -> dict[str, dict[str, float]]:
    if _is_canonical(raw):
        job_roles_raw = raw.get("labor", {}).get("job_roles", {})
        return _coerce_labor_job_roles(job_roles_raw)

    normalized = normalize_job_inputs(raw, job_roles)
    labor_job_roles: dict[str, dict[str, float]] = {}
    for role in job_roles:
        if not role.is_active:
            continue
        values = normalized.get(role.job_code, {})
        headcount = _read_float(values.get("headcount"))
        work_days = _read_float(values.get("work_days"))
        work_hours = _read_float(values.get("work_hours"))
        overtime_hours = _read_float(values.get("overtime_hours"))
        holiday_work_days = _read_float(values.get("holiday_work_days", values.get("holiday_work_hours")))
        if _is_non_zero_labor(
            headcount,
            work_days,
            work_hours,
            overtime_hours,
            holiday_work_days,
        ):
            labor_job_roles[role.job_code] = {
                "headcount": headcount,
                "work_days": work_days,
                "work_hours": work_hours,
                "overtime_hours": overtime_hours,
                "holiday_work_days": holiday_work_days,
            }
    return labor_job_roles


def _normalize_expenses(
    raw: dict,
    expense_items: list[ExpenseItem],
    pricebook: list[ExpensePrice],
) -> dict[str, dict[str, Any]]:
    price_map = _price_map(pricebook)
    if _is_canonical(raw):
        items_raw = raw.get("expenses", {}).get("items", {})
        return _coerce_expense_items(items_raw, price_map)

    inputs = raw.get("inputs", raw)
    expense_inputs = (
        inputs.get("expense_inputs")
        or inputs.get("expenses")
        or {}
    )

    normalized: dict[str, dict[str, Any]] = {}
    for item in expense_items:
        if not item.is_active:
            continue
        quantity = _read_float(expense_inputs.get(item.exp_code))
        if quantity > 0:
            normalized[item.exp_code] = {
                "quantity": quantity,
                "unit_price": price_map.get(item.exp_code, 0),
            }
    return normalized


def _coerce_labor_job_roles(raw: dict) -> dict[str, dict[str, float]]:
    normalized: dict[str, dict[str, float]] = {}
    for job_code, values in raw.items():
        if not isinstance(values, dict):
            continue
        headcount = _read_float(
            values.get(
                "headcount",
                values.get("count", values.get("person_count")),
            )
        )
        work_days = _read_float(values.get("work_days"))
        work_hours = _read_float(values.get("work_hours"))
        overtime_hours = _read_float(values.get("overtime_hours"))
        holiday_work_days = _read_float(values.get("holiday_work_days", values.get("holiday_work_hours")))
        if _is_non_zero_labor(
            headcount,
            work_days,
            work_hours,
            overtime_hours,
            holiday_work_days,
        ):
            normalized[job_code] = {
                "headcount": headcount,
                "work_days": work_days,
                "work_hours": work_hours,
                "overtime_hours": overtime_hours,
                "holiday_work_days": holiday_work_days,
            }
    return normalized


def _coerce_expense_items(
    raw: dict,
    price_map: dict[str, int],
) -> dict[str, dict[str, Any]]:
    normalized: dict[str, dict[str, Any]] = {}
    for exp_code, values in raw.items():
        if not isinstance(values, dict):
            continue
        quantity = _read_float(values.get("quantity"))
        unit_price = _read_int_or_value(values.get("unit_price"))
        if quantity > 0 or exp_code in price_map:
            normalized[exp_code] = {
                "quantity": quantity,
                "unit_price": unit_price if unit_price is not None else price_map.get(exp_code, 0),
            }
    return normalized


def _price_map(pricebook: list[ExpensePrice]) -> dict[str, int]:
    result: dict[str, int] = {}
    for price in pricebook:
        if price.exp_code not in result:
            result[price.exp_code] = int(price.unit_price)
    return result


def _is_canonical(raw: dict) -> bool:
    if not isinstance(raw, dict):
        return False
    labor = raw.get("labor")
    expenses = raw.get("expenses")
    if not isinstance(labor, dict) or not isinstance(expenses, dict):
        return False
    return isinstance(labor.get("job_roles", {}), dict) and isinstance(
        expenses.get("items", {}), dict
    )


def _empty_canonical() -> dict:
    return {
        "labor": {"job_roles": {}},
        "expenses": {"items": {}},
    }


def _save_canonical(conn, scenario_id: str, canonical: dict) -> None:
    payload = json.dumps(canonical, ensure_ascii=True)
    changes_before = conn.total_changes
    conn.execute(
        """
        INSERT INTO scenario_input (scenario_id, input_json, updated_at)
        VALUES (?, ?, datetime('now'))
        ON CONFLICT(scenario_id) DO UPDATE SET
          input_json=excluded.input_json,
          updated_at=datetime('now')
        """,
        (scenario_id, payload),
    )
    try:
        conn.commit()
        changes_after = conn.total_changes
        db_path = get_db_path()
        size = os.path.getsize(db_path) if os.path.exists(db_path) else -1
        logging.info(
            "시나리오 입력 DB 반영 완료: 시나리오=%s 반영행=%s db크기=%s",
            scenario_id,
            changes_after - changes_before,
            size,
        )
    except sqlite3.OperationalError as exc:
        logging.error("시나리오 입력 DB 반영 실패: 시나리오=%s (%s)", scenario_id, exc)
        if "disk I/O error" in str(exc).lower():
            handle_disk_io_error(get_db_path())
        raise


def _read_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _read_int_or_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        try:
            if "." in value:
                return value
            return int(value)
        except ValueError:
            return value
    return value


def _is_non_zero_labor(
    headcount: float,
    work_days: float,
    work_hours: float,
    overtime_hours: float,
    holiday_work_days: float,
) -> bool:
    return any(
        value != 0
        for value in (
            headcount,
            overtime_hours,
            holiday_work_days,
        )
    )


def _validate_float(
    errors: list[ValidationError],
    value: Any,
    field_path: str,
    min_value: float,
    max_value: float,
) -> None:
    if not isinstance(value, (int, float)):
        errors.append(
            ValidationError(
                code="INVALID_TYPE",
                field_path=field_path,
                message="value must be numeric",
            )
        )
        return

    if value < min_value:
        errors.append(
            ValidationError(
                code="VALUE_TOO_SMALL",
                field_path=field_path,
                message=f"value must be >= {min_value}",
            )
        )
    if value > max_value:
        errors.append(
            ValidationError(
                code="VALUE_TOO_LARGE",
                field_path=field_path,
                message=f"value must be <= {max_value}",
            )
        )


def _validate_int(
    errors: list[ValidationError],
    value: int,
    field_path: str,
    min_value: int,
    max_value: int,
) -> None:
    if value < min_value:
        errors.append(
            ValidationError(
                code="VALUE_TOO_SMALL",
                field_path=field_path,
                message=f"value must be >= {min_value}",
            )
        )
    if value > max_value:
        errors.append(
            ValidationError(
                code="VALUE_TOO_LARGE",
                field_path=field_path,
                message=f"value must be <= {max_value}",
            )
        )
