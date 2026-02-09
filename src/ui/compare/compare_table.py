from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem
from PyQt6.QtGui import QColor


class CompareTable(QWidget):
    """
    시나리오 비교 테이블
    """

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        title = QLabel("시나리오 비교")
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["항목", "A", "Δ (B-A)", "B"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

    def update_rows(self, rows: list[dict], highlight_labels: set[str] | None = None) -> None:
        highlight_labels = highlight_labels or set()
        self.table.setRowCount(0)
        for row in rows:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)

            label_item = QTableWidgetItem(row["label"])
            a_item = QTableWidgetItem(f"{row['a']:,}")
            b_item = QTableWidgetItem(f"{row['b']:,}")
            self.table.setItem(row_idx, 0, label_item)
            self.table.setItem(row_idx, 1, a_item)
            self.table.setItem(row_idx, 3, b_item)

            delta_item = QTableWidgetItem(f"{row['delta']:,}")
            if row["delta"] > 0:
                delta_item.setForeground(QColor(198, 40, 40))
            elif row["delta"] < 0:
                delta_item.setForeground(QColor(46, 125, 50))
            self.table.setItem(row_idx, 2, delta_item)

            if row["label"] in highlight_labels:
                for item in (label_item, a_item, delta_item, b_item):
                    item.setBackground(QColor(255, 243, 205))
