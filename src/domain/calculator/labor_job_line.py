from dataclasses import dataclass


@dataclass
class LaborJobLine:
    job_code: str
    headcount: int
    job_name: str
    work_days: float
    base_wage: int
    allowance: int
    overtime: int
    total: int
    base_salary: int
    bonus: int
    allowances: int
    retirement: int
    labor_subtotal: int
    role_total: int
