TOP_N_JOB_ROLES = 5


def build_job_breakdown_rows(snapshot: dict) -> list[list]:
    rows = []
    for line in snapshot.get("job_breakdown", []):
        rows.append(
            [
                line.get("job_code", ""),
                line.get("job_name", ""),
                line.get("headcount", 0),
                line.get("work_days", 0),
                line.get("base_wage", 0),
                line.get("allowance", 0),
                line.get("overtime", 0),
                line.get("total", 0),
            ]
        )
    return rows


def build_top_job_summary(snapshot: dict, top_n: int = TOP_N_JOB_ROLES) -> list[tuple[str, int, str]]:
    rows = []
    for line in snapshot.get("job_breakdown", []):
        rows.append(
            (
                line.get("job_name", ""),
                int(line.get("total", 0)),
                line.get("job_code", ""),
            )
        )
    rows.sort(key=lambda x: (-x[1], x[2]))
    return rows[:top_n]


def build_detail_job_rows(snapshot: dict) -> list[list]:
    rows = []
    for line in snapshot.get("job_breakdown", []):
        rows.append(
            [
                line.get("job_code", ""),
                line.get("job_name", ""),
                line.get("headcount", 0),
                line.get("work_days", 0),
                line.get("base_wage", 0),
                line.get("allowance", 0),
                line.get("overtime", 0),
                line.get("total", 0),
            ]
        )
    return rows
