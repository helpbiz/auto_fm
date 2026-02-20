from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QFrame,
)
from PyQt6.QtCore import Qt

from .theme import (
    SECTION_TITLE_STYLE, CARD_STYLE, CARD_TITLE_STYLE,
    CARD_VALUE_STYLE, CARD_VALUE_SUCCESS, CARD_VALUE_ERROR,
)


class _SummaryCard(QFrame):
    """단일 요약 카드 (타이틀 + 값)."""

    def __init__(self, title: str, initial: str = "0"):
        super().__init__()
        self.setStyleSheet(CARD_STYLE)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)

        self._title = QLabel(title)
        self._title.setStyleSheet(CARD_TITLE_STYLE)
        layout.addWidget(self._title)

        self._value = QLabel(initial)
        self._value.setStyleSheet(CARD_VALUE_STYLE)
        layout.addWidget(self._value)

    def set_value(self, text: str, style: str | None = None) -> None:
        self._value.setText(text)
        if style:
            self._value.setStyleSheet(style)


class SummaryPanel(QWidget):
    """
    집계 결과 표시 패널: 상단 3카드 + 하단 합계 그리드
    """

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        title = QLabel("집계 요약")
        title.setStyleSheet(SECTION_TITLE_STYLE)
        layout.addWidget(title)

        # 카드 3개
        card_row = QHBoxLayout()
        self.card_total = _SummaryCard("월간 총액 (원)")
        self.card_per_capita = _SummaryCard("인당 평균 단가 (원)")
        self.card_yoy = _SummaryCard("전년 대비 증감액 (원)")
        card_row.addWidget(self.card_total)
        card_row.addWidget(self.card_per_capita)
        card_row.addWidget(self.card_yoy)
        layout.addLayout(card_row)

        layout.addSpacing(8)

        # 합계 그리드
        self.labels = {}
        grid = QGridLayout()

        rows = [
            ("labor_total", "노무비 합계"),
            ("fixed_expense_total", "고정경비 합계"),
            ("variable_expense_total", "변동경비 합계"),
            ("passthrough_expense_total", "대행비 합계"),
            ("overhead_cost", "일반관리비"),
            ("profit", "이윤"),
            ("grand_total", "총계(VAT 제외)"),
        ]

        for row, (key, label_text) in enumerate(rows):
            label = QLabel(label_text)
            value = QLabel("0")
            value.setStyleSheet("font-weight: bold;")
            value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            grid.addWidget(label, row, 0)
            grid.addWidget(value, row, 1)
            self.labels[key] = value

        layout.addLayout(grid)
        layout.addStretch()

    def update_summary(self, aggregator, pdf_grand_total: int = 0) -> None:
        self.labels["labor_total"].setText(f"{aggregator.labor_total:,}")
        self.labels["fixed_expense_total"].setText(f"{aggregator.fixed_expense_total:,}")
        self.labels["variable_expense_total"].setText(f"{aggregator.variable_expense_total:,}")
        self.labels["passthrough_expense_total"].setText(f"{aggregator.passthrough_expense_total:,}")
        self.labels["overhead_cost"].setText(f"{aggregator.overhead_cost:,}")
        self.labels["profit"].setText(f"{aggregator.profit:,}")
        self.labels["grand_total"].setText(f"{aggregator.grand_total:,}")

        # 카드 업데이트
        self.card_total.set_value(f"{aggregator.grand_total:,}", CARD_VALUE_STYLE)

        # 인당 평균: grand_total이 있고 headcount 정보가 있으면 계산
        headcount = getattr(aggregator, "total_headcount", 0) or 0
        if headcount > 0:
            per_capita = aggregator.grand_total // headcount
            self.card_per_capita.set_value(f"{per_capita:,}", CARD_VALUE_STYLE)
        else:
            self.card_per_capita.set_value("-", CARD_VALUE_STYLE)

        # 전년 대비 (아직 비교 데이터 없을 때)
        prev = getattr(aggregator, "prev_grand_total", None)
        if prev is not None and prev > 0:
            diff = aggregator.grand_total - prev
            sign = "+" if diff >= 0 else ""
            style = CARD_VALUE_ERROR if diff < 0 else CARD_VALUE_SUCCESS
            self.card_yoy.set_value(f"{sign}{diff:,}", style)
        else:
            self.card_yoy.set_value("-", CARD_VALUE_STYLE)
