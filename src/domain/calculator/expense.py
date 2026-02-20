from dataclasses import dataclass
from decimal import Decimal
from typing import Dict

from src.domain.constants.rounding import drop_under_1_won
from src.domain.constants.expense_groups import classify_expense
from src.domain.calculator.expense_line import ExpenseLine, ExpenseSubLine


@dataclass
class ExpenseResult:
    lines: list[ExpenseLine]
    fixed_total: int
    variable_total: int
    passthrough_total: int
    grand_total: int


# 안전관리비: 설정의 지급요율 적용 (직접노무비 합계 × 지급요율)
EXP_CODE_SAFETY = "FIX_SAFETY"


class ExpenseCostCalculator:
    """경비 계산 전담 클래스 - 세부 항목(sub_items) 지원, 안전관리비는 직접노무비×지급요율"""

    def __init__(
        self,
        items: list,
        inputs: Dict[str, dict],
        price_map: Dict[str, int],
        sub_items_map: Dict[str, list] = None,
        labor_total: int = 0,
        safety_management_rate: float | Decimal = 0,
    ):
        self.items = items
        self.inputs = inputs
        self.price_map = price_map
        self.sub_items_map = sub_items_map or {}
        self.labor_total = labor_total
        self.safety_management_rate = Decimal(str(safety_management_rate))

    def calculate(self) -> ExpenseResult:
        lines: list[ExpenseLine] = []
        totals: Dict[str, int] = {"fixed": 0, "variable": 0, "passthrough": 0}

        for item in self.items:
            if not item.is_active:
                continue

            category = classify_expense(item.group_code)
            sub_items = self.sub_items_map.get(item.exp_code, [])

            # 안전관리비: 직접노무비 합계 × 설정의 지급요율 (세부 항목 무시)
            if item.exp_code == EXP_CODE_SAFETY and self.safety_management_rate and self.labor_total:
                row_total = int(
                    drop_under_1_won(Decimal(self.labor_total) * self.safety_management_rate)
                )
                lines.append(
                    ExpenseLine(
                        exp_code=item.exp_code,
                        exp_name=item.exp_name,
                        group_code=item.group_code,
                        category=category,
                        unit_price=row_total,
                        quantity=Decimal("1"),
                        row_total=row_total,
                        sub_lines=[],
                    )
                )
                totals[category] += row_total
                continue

            if sub_items:
                # 세부 항목이 있으면 세부 항목의 합으로 계산
                sub_lines, sub_total = self._calculate_sub_items(sub_items)
                if sub_total == 0:
                    continue

                lines.append(
                    ExpenseLine(
                        exp_code=item.exp_code,
                        exp_name=item.exp_name,
                        group_code=item.group_code,
                        category=category,
                        unit_price=sub_total,
                        quantity=Decimal("1"),
                        row_total=sub_total,
                        sub_lines=sub_lines,
                    )
                )
                totals[category] += sub_total
            else:
                # 세부 항목 없으면 기존 방식 (단가 × 수량)
                values = self.inputs.get(item.exp_code, {})
                quantity = Decimal(str(values.get("quantity", 0)))
                unit_price = int(
                    values.get("unit_price", self.price_map.get(item.exp_code, 0))
                )

                if quantity == 0 and unit_price == 0:
                    continue

                row_total = drop_under_1_won(quantity * Decimal(str(unit_price)))

                lines.append(
                    ExpenseLine(
                        exp_code=item.exp_code,
                        exp_name=item.exp_name,
                        group_code=item.group_code,
                        category=category,
                        unit_price=unit_price,
                        quantity=quantity,
                        row_total=row_total,
                    )
                )
                totals[category] += row_total

        return ExpenseResult(
            lines=lines,
            fixed_total=totals["fixed"],
            variable_total=totals["variable"],
            passthrough_total=totals["passthrough"],
            grand_total=totals["fixed"] + totals["variable"] + totals["passthrough"],
        )

    def _calculate_sub_items(
        self, sub_items: list
    ) -> tuple[list[ExpenseSubLine], int]:
        """세부 항목 리스트를 계산하여 (sub_lines, total) 반환"""
        sub_lines: list[ExpenseSubLine] = []
        total = 0

        for si in sub_items:
            is_active = getattr(si, 'is_active', 1) if hasattr(si, 'is_active') else si.get('is_active', 1)
            if not is_active:
                continue

            qty = float(getattr(si, 'quantity', 0) if hasattr(si, 'quantity') else si.get('quantity', 0))
            price = int(getattr(si, 'unit_price', 0) if hasattr(si, 'unit_price') else si.get('unit_price', 0))
            amount = drop_under_1_won(Decimal(str(qty)) * Decimal(str(price)))

            def _attr(obj, name, default=''):
                if hasattr(obj, name):
                    return getattr(obj, name, default)
                return obj.get(name, default)

            sub_lines.append(
                ExpenseSubLine(
                    sub_code=_attr(si, 'sub_code'),
                    sub_name=_attr(si, 'sub_name'),
                    spec=_attr(si, 'spec'),
                    unit=_attr(si, 'unit'),
                    quantity=qty,
                    unit_price=price,
                    amount=amount,
                    remark=_attr(si, 'remark'),
                )
            )
            total += amount

        return sub_lines, total
