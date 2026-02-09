def build_breakdown(agg, labor_rows: list[dict]) -> tuple[dict, dict]:
    values = {
        "labor_total": agg.labor_total,
        "fixed_expense_total": agg.fixed_expense_total,
        "variable_expense_total": agg.variable_expense_total,
        "passthrough_expense_total": agg.passthrough_expense_total,
        "overhead_cost": agg.overhead_cost,
        "profit": agg.profit,
    }
    labels = {
        "labor_total": "노무비 합계",
        "fixed_expense_total": "고정경비 합계",
        "variable_expense_total": "변동경비 합계",
        "passthrough_expense_total": "대행비 합계",
        "overhead_cost": "일반관리비",
        "profit": "이윤",
    }

    for line in labor_rows:
        job_code = line.get("job_code", "")
        job_name = line.get("role", job_code)
        if not job_code:
            continue
        key = f"labor.job.{job_code}"
        values[key] = line.get("role_total", 0)
        labels[key] = f"노무비(직종) - {job_name}"

    return values, labels


def get_top_drivers(values_a: dict, values_b: dict, labels: dict, n: int = 3) -> list[dict]:
    keys = set(values_a.keys()) | set(values_b.keys())
    rows = []
    for key in keys:
        a_val = values_a.get(key, 0)
        b_val = values_b.get(key, 0)
        delta = b_val - a_val
        rows.append(
            {
                "key": key,
                "label": labels.get(key, key),
                "a": a_val,
                "b": b_val,
                "delta": delta,
                "abs_delta": abs(delta),
            }
        )
    rows.sort(key=lambda x: x["abs_delta"], reverse=True)
    return [r for r in rows if r["abs_delta"] > 0][:n]
