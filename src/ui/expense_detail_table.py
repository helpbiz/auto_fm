from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem


class ExpenseDetailTable(QWidget):
    """
    경비 상세 테이블 (표시 전용)
    """

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        title = QLabel("경비 상세")
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            [
                "구분",
                "항목명",
                "드라이버",
                "단가",
                "수량",
                "행 합계",
                "유형",
            ]
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

    def update_rows(self, rows: list[dict]) -> None:
        self.table.setRowCount(0)
        for row in rows:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(row["category"]))
            self.table.setItem(row_idx, 1, QTableWidgetItem(row["name"]))
            self.table.setItem(row_idx, 2, QTableWidgetItem(row["driver"]))
            self.table.setItem(row_idx, 3, QTableWidgetItem(row["unit_cost"]))
            self.table.setItem(row_idx, 4, QTableWidgetItem(row["quantity"]))
            total_item = QTableWidgetItem(row["row_total"])
            if row.get("type") == "Pass-through":
                total_item.setForeground(
                    total_item.foreground().color().fromRgb(198, 40, 40)
                )
            self.table.setItem(row_idx, 5, total_item)
            self.table.setItem(row_idx, 6, QTableWidgetItem(row["type"]))
