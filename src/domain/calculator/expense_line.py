from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class ExpenseSubLine:
    """경비 세부 항목 1행"""
    sub_code: str       # 세부 코드
    sub_name: str       # 세부 항목명
    spec: str           # 규격
    unit: str           # 단위
    quantity: float     # 수량
    unit_price: int     # 단가(원)
    amount: int         # 금액 = quantity × unit_price
    remark: str         # 비고


@dataclass
class ExpenseLine:
    exp_code: str       # 경비코드
    exp_name: str       # 항목명
    group_code: str     # 원본 group_code
    category: str       # 분류 결과: "fixed" | "variable" | "passthrough"
    unit_price: int     # 단가(원) - 월 합계 단가
    quantity: Decimal   # 수량 (1이면 월 정액)
    row_total: int      # 행 합계 = drop_under_1_won(unit_price × quantity)
    sub_lines: list[ExpenseSubLine] = field(default_factory=list)
