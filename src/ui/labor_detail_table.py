from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem


class LaborDetailTable(QWidget):
    """
    노무비 상세 테이블 (표시 전용)
    """

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        title = QLabel("노무비 상세")
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            [
                "직무/직책",
                "인원",
                "기본급",
                "제수당",
                "보험료",
                "인건비 소계",
                "직무 합계",
            ]
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

    def update_rows(self, rows: list[dict]) -> None:
        self.table.setRowCount(0)
        for row in rows:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(row["role"]))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(row["headcount"])))
            self.table.setItem(row_idx, 2, QTableWidgetItem(f"{row['base_salary']:,}"))
            self.table.setItem(row_idx, 3, QTableWidgetItem(f"{row['allowances']:,}"))
            self.table.setItem(row_idx, 4, QTableWidgetItem(f"{row['insurance_total']:,}"))
            self.table.setItem(row_idx, 5, QTableWidgetItem(f"{row['labor_subtotal']:,}"))
            self.table.setItem(row_idx, 6, QTableWidgetItem(f"{row['role_total']:,}"))
