def build_canonical_input(
    job_inputs: dict,
    expense_inputs: dict,
    overhead_rate: float = 0.0,
    profit_rate: float = 0.0,
    base_year: int | None = None,
    wage_year: int | None = None,
    wage_half: str | None = None,
    holiday_work_days_calc: dict | None = None,
) -> dict:
    """UI 입력을 canonical 시나리오 입력 형식으로 변환.
    모든 직무의 인원·근무일 등은 저장하여 불러오기 시 그대로 복원됨.
    quantity가 0인 경비 항목은 expenses.items에 포함하지 않음.
    기준연도·노임단가 기준년도·반기도 저장하여 불러오기 시 복원됨.
    """
    import logging
    labor_roles = {}
    skipped = 0
    for job_code, values in job_inputs.items():
        if not isinstance(values, dict):
            skipped += 1
            continue
        headcount = float(values.get("headcount", 0) or 0)
        work_days = float(values.get("work_days", 0) or 0)
        work_hours = float(values.get("work_hours", 0) or 0)
        overtime_hours = float(values.get("overtime_hours", 0) or 0)
        holiday_work_days = float(values.get("holiday_work_days", values.get("holiday_work_hours", 0)) or 0)
        labor_roles[job_code] = {
            "headcount": headcount,
            "work_days": work_days,
            "work_hours": work_hours,
            "overtime_hours": overtime_hours,
            "holiday_work_days": holiday_work_days,
        }
    if skipped:
        logging.warning("[저장] canonical 변환 시 직무입력 %d건 제외(비 dict), 반영 직무수=%d", skipped, len(labor_roles))

    expense_items = {}
    for exp_code, values in expense_inputs.items():
        if not isinstance(values, dict):
            continue
        quantity = float(values.get("quantity", 0) or 0)
        unit_price = values.get("unit_price", 0)
        if quantity != 0:
            expense_items[exp_code] = {
                "quantity": quantity,
                "unit_price": int(unit_price),
            }

    out = {
        "labor": {"job_roles": labor_roles},
        "expenses": {"items": expense_items},
        "overhead_rate": overhead_rate,
        "profit_rate": profit_rate,
    }
    if base_year is not None:
        out["base_year"] = base_year
    if wage_year is not None:
        out["wage_year"] = wage_year
    if wage_half is not None:
        out["wage_half"] = wage_half
    if holiday_work_days_calc is not None and isinstance(holiday_work_days_calc, dict):
        hw = {
            "annual_holiday_work_days": float(holiday_work_days_calc.get("annual_holiday_work_days", 0)),
        }
        if "year" in holiday_work_days_calc:
            hw["year"] = int(holiday_work_days_calc["year"])
        if "public_holidays_by_month" in holiday_work_days_calc:
            arr = holiday_work_days_calc.get("public_holidays_by_month") or []
            if not isinstance(arr, list):
                arr = []
            hw["public_holidays_by_month"] = [
                int(arr[i]) if i < len(arr) else 0 for i in range(12)
            ]
        if "monthly_work_days" in holiday_work_days_calc:
            hw["monthly_work_days"] = float(holiday_work_days_calc["monthly_work_days"])
        if "statutory_holidays" in holiday_work_days_calc:
            hw["statutory_holidays"] = int(holiday_work_days_calc["statutory_holidays"])
        if "substitute_holidays" in holiday_work_days_calc:
            hw["substitute_holidays"] = int(holiday_work_days_calc["substitute_holidays"])
        if "center_count" in holiday_work_days_calc:
            hw["center_count"] = max(1, min(10, int(holiday_work_days_calc["center_count"])))
        if holiday_work_days_calc.get("shift_type") in ("미운영", "2교대", "3교대"):
            hw["shift_type"] = holiday_work_days_calc["shift_type"]
        if holiday_work_days_calc.get("crew_size_3shift") in (1, 2, 3):
            hw["crew_size_3shift"] = int(holiday_work_days_calc["crew_size_3shift"])
        if "headcount_excl_manager" in holiday_work_days_calc:
            hw["headcount_excl_manager"] = int(holiday_work_days_calc["headcount_excl_manager"])
        out["holiday_work_days_calc"] = hw
    return out


def compute_action_state(is_dirty: bool, has_result: bool) -> dict:
    return {
        "save_enabled": is_dirty,
        "calculate_enabled": not is_dirty,
        "export_enabled": (not is_dirty) and has_result,
    }
