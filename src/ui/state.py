def build_canonical_input(job_inputs: dict, expense_inputs: dict) -> dict:
    labor_roles = {}
    for job_code, values in job_inputs.items():
        if not isinstance(values, dict):
            continue
        headcount = float(values.get("headcount", 0) or 0)
        work_days = float(values.get("work_days", 0) or 0)
        work_hours = float(values.get("work_hours", 0) or 0)
        overtime_hours = float(values.get("overtime_hours", 0) or 0)
        holiday_work_hours = float(values.get("holiday_work_hours", 0) or 0)
        if any(v != 0 for v in (headcount, overtime_hours, holiday_work_hours)):
            labor_roles[job_code] = {
                "headcount": headcount,
                "work_days": work_days,
                "work_hours": work_hours,
                "overtime_hours": overtime_hours,
                "holiday_work_hours": holiday_work_hours,
            }

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

    return {
        "labor": {"job_roles": labor_roles},
        "expenses": {"items": expense_items},
    }


def compute_action_state(is_dirty: bool, has_result: bool) -> dict:
    return {
        "save_enabled": is_dirty,
        "calculate_enabled": not is_dirty,
        "export_enabled": (not is_dirty) and has_result,
    }
