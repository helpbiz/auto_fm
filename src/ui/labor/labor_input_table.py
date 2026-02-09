from decimal import Decimal, InvalidOperation

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem


class LaborInputTable(QTableWidget):
    def __init__(self):
        super().__init__(0, 3)
        self.setHorizontalHeaderLabels(["직무", "인원", "일급"])

    def add_row(self, job="", headcount="", wage=""):
        row = self.rowCount()
        self.insertRow(row)
        self.setItem(row, 0, QTableWidgetItem(job))
        self.setItem(row, 1, QTableWidgetItem(str(headcount)))
        self.setItem(row, 2, QTableWidgetItem(str(wage)))

    def get_data(self):
        manpower = {}
        wage_rate = {}

        for row in range(self.rowCount()):
            job_item = self.item(row, 0)
            if job_item is None:
                continue
            job = job_item.text().strip()
            if not job:
                continue

            headcount = self._to_decimal(self.item(row, 1))
            wage = self._to_decimal(self.item(row, 2))
            manpower[job] = headcount
            wage_rate[job] = wage

        return manpower, wage_rate

    def _to_decimal(self, item):
        if item is None:
            return Decimal("0")
        text = item.text().strip()
        if not text:
            return Decimal("0")
        try:
            return Decimal(text)
        except InvalidOperation:
            return Decimal("0")
