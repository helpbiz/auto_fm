"""
Domain models for the 4-step workflow.
No PyQt, no DB access. Used by services and controllers.
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class BaseData:
    """Step 2: Base data input only. No computed results."""
    labor: dict  # {"job_roles": {job_code: {headcount, work_days, work_hours, ...}}}
    expenses: dict  # {"items": {exp_code: {quantity, unit_price}}}
    params: dict = field(default_factory=dict)  # optional: base_year, etc.

    def to_canonical(self) -> dict:
        """Canonical form for calculation (same as scenario_input)."""
        return {
            "labor": self.labor,
            "expenses": self.expenses,
        }


@dataclass
class ResultSnapshot:
    """
    Step 3 output: pure computation result.
    Mirrors what is stored in calculation_result.result_json.
    """
    labor_total: int | float
    fixed_expense_total: int | float
    variable_expense_total: int | float
    passthrough_expense_total: int | float
    overhead_cost: int | float
    profit: int | float
    labor_rows: list[dict]
    expense_rows: list[dict]
    job_breakdown: list[dict]
    insurance_by_exp_code: dict[str, int]
    created_at: str | None = None
    hash: str | None = None

    @property
    def grand_total(self) -> float:
        return (
            float(self.labor_total)
            + float(self.fixed_expense_total)
            + float(self.variable_expense_total)
            + float(self.passthrough_expense_total)
            + float(self.overhead_cost)
            + float(self.profit)
        )

    def to_dict(self) -> dict:
        """For persistence and UI (aggregator-style)."""
        return {
            "aggregator": {
                "labor_total": self.labor_total,
                "fixed_expense_total": self.fixed_expense_total,
                "variable_expense_total": self.variable_expense_total,
                "passthrough_expense_total": self.passthrough_expense_total,
                "overhead_cost": self.overhead_cost,
                "profit": self.profit,
                "grand_total": self.grand_total,
            },
            "labor_rows": self.labor_rows,
            "expense_rows": self.expense_rows,
            "job_breakdown": self.job_breakdown,
            "insurance_by_exp_code": self.insurance_by_exp_code,
        }

    @classmethod
    def from_result_dict(cls, result: dict) -> "ResultSnapshot":
        """Build from existing calculate_result() output (aggregator may be object or dict)."""
        agg = result.get("aggregator")
        if agg is None:
            raise ValueError("result must contain 'aggregator'")
        if hasattr(agg, "labor_total"):
            labor_total, fixed_total, variable_total = agg.labor_total, agg.fixed_expense_total, agg.variable_expense_total
            passthrough_total, overhead_cost, profit = agg.passthrough_expense_total, agg.overhead_cost, agg.profit
        else:
            labor_total = agg.get("labor_total", 0)
            fixed_total = agg.get("fixed_expense_total", 0)
            variable_total = agg.get("variable_expense_total", 0)
            passthrough_total = agg.get("passthrough_expense_total", 0)
            overhead_cost = agg.get("overhead_cost", 0)
            profit = agg.get("profit", 0)
        return cls(
            labor_total=labor_total,
            fixed_expense_total=fixed_total,
            variable_expense_total=variable_total,
            passthrough_expense_total=passthrough_total,
            overhead_cost=overhead_cost,
            profit=profit,
            labor_rows=result.get("labor_rows") or [],
            expense_rows=result.get("expense_rows") or [],
            job_breakdown=result.get("job_breakdown") or [],
            insurance_by_exp_code=result.get("insurance_by_exp_code") or {},
        )


@dataclass
class Scenario:
    """Current scenario context: id, name, base data, and optional result snapshot."""
    id: str
    name: str
    base_data: BaseData | None = None
    result_snapshot: ResultSnapshot | None = None
    meta: dict = field(default_factory=dict)
    version: int = 1
