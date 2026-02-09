from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout


class SummaryPanel(QWidget):
    """
    집계 결과 표시 패널
    """

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        title = QLabel("집계 요약")
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)

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
            grid.addWidget(label, row, 0)
            grid.addWidget(value, row, 1)
            self.labels[key] = value

        layout.addLayout(grid)

        self.pdf_title = QLabel("PDF 비교")
        self.pdf_title.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.pdf_title)

        self.pdf_expected = QLabel("PDF 총계: 0")
        self.pdf_actual = QLabel("계산 총계: 0")
        self.pdf_status = QLabel("상태: 비교값 없음")
        self.pdf_status.setStyleSheet("color: #666666; font-weight: bold;")

        layout.addWidget(self.pdf_expected)
        layout.addWidget(self.pdf_actual)
        layout.addWidget(self.pdf_status)

    def update_summary(self, aggregator, pdf_grand_total: int) -> None:
        self.labels["labor_total"].setText(f"{aggregator.labor_total:,}")
        self.labels["fixed_expense_total"].setText(f"{aggregator.fixed_expense_total:,}")
        self.labels["variable_expense_total"].setText(f"{aggregator.variable_expense_total:,}")
        self.labels["passthrough_expense_total"].setText(f"{aggregator.passthrough_expense_total:,}")
        self.labels["overhead_cost"].setText(f"{aggregator.overhead_cost:,}")
        self.labels["profit"].setText(f"{aggregator.profit:,}")
        self.labels["grand_total"].setText(f"{aggregator.grand_total:,}")

        self.pdf_expected.setText(f"PDF 총계: {pdf_grand_total:,}")
        self.pdf_actual.setText(f"계산 총계: {aggregator.grand_total:,}")

        if pdf_grand_total <= 0:
            self.pdf_status.setText("상태: 비교값 없음")
            self.pdf_status.setStyleSheet("color: #666666; font-weight: bold;")
        elif aggregator.grand_total == pdf_grand_total:
            self.pdf_status.setText("상태: 일치")
            self.pdf_status.setStyleSheet("color: #2e7d32; font-weight: bold;")
        else:
            self.pdf_status.setText("상태: 불일치")
            self.pdf_status.setStyleSheet("color: #c62828; font-weight: bold;")
