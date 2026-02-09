from dataclasses import dataclass
from typing import Union

Number = Union[int, float]


@dataclass
class Aggregator:
    """
    비용 집계 전담 클래스 (UI 독립)
    """

    labor_total: Number
    fixed_expense_total: Number
    variable_expense_total: Number
    passthrough_expense_total: Number
    overhead_cost: Number
    profit: Number

    @property
    def overhead_base(self) -> Number:
        # 간접비 산정 기준: 노무비 + 고정경비
        return self.labor_total + self.fixed_expense_total

    @property
    def profit_base(self) -> Number:
        # 이윤 산정 기준: 노무비 + 고정경비 + 간접비
        return self.labor_total + self.fixed_expense_total + self.overhead_cost

    @property
    def grand_total(self) -> Number:
        # 총합(VAT 제외)
        return (
            self.labor_total
            + self.fixed_expense_total
            + self.variable_expense_total
            + self.passthrough_expense_total
            + self.overhead_cost
            + self.profit
        )
