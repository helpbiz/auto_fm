from typing import Any

from src.domain.masterdata.repo import JobRole


def normalize_job_inputs(
    scenario_input: dict,
    job_roles: list[JobRole],
) -> dict[str, dict[str, float]]:
    """
    시나리오 입력을 직무코드 기반의 표준 구조로 정규화한다.
    """
    inputs = scenario_input.get("inputs", scenario_input)

    labor_inputs = inputs.get("labor", {})
    job_inputs = labor_inputs.get("job_inputs") or inputs.get("job_inputs") or {}
    active_roles = [role for role in job_roles if role.is_active]

    work_days = _read_float(
        inputs.get("monthly_workdays")
        or labor_inputs.get("monthly_workdays")
        or inputs.get("work_days")
        or labor_inputs.get("work_days")
        or 0
    )
    work_hours = _read_float(
        inputs.get("daily_work_hours")
        or labor_inputs.get("daily_work_hours")
        or inputs.get("work_hours")
        or labor_inputs.get("work_hours")
        or 0
    )
    overtime_hours = _read_float(
        inputs.get("overtime_hours")
        or labor_inputs.get("overtime_hours")
        or 0
    )
    holiday_work_hours = _read_float(
        inputs.get("holiday_work_hours")
        or labor_inputs.get("holiday_work_hours")
        or 0
    )

    normalized: dict[str, dict[str, float]] = {}
    for role in active_roles:
        headcount = _read_float(job_inputs.get(role.job_code, 0))
        normalized[role.job_code] = {
            "headcount": headcount,
            "work_days": work_days,
            "work_hours": work_hours,
            "overtime_hours": overtime_hours,
            "holiday_work_hours": holiday_work_hours,
        }

    if normalized and any(line["headcount"] > 0 for line in normalized.values()):
        return normalized

    legacy_headcount = _read_float(inputs.get("headcount", 0))
    if legacy_headcount <= 0:
        return normalized

    legacy_target = None
    for role in active_roles:
        if role.job_code == "role":
            legacy_target = role.job_code
            break
    if legacy_target is None and len(active_roles) == 1:
        legacy_target = active_roles[0].job_code

    if legacy_target:
        normalized[legacy_target] = {
            "headcount": legacy_headcount,
            "work_days": work_days,
            "work_hours": work_hours,
            "overtime_hours": overtime_hours,
            "holiday_work_hours": holiday_work_hours,
        }

    return normalized


def _read_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
