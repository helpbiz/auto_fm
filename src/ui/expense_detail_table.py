from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem


def _fmt_row_total(value) -> str:
    """행 합계 값을 천 단위 콤마로 표시."""
    try:
        n = int(float(str(value).replace(",", "").strip() or 0))
        return f"{n:,}"
    except (ValueError, TypeError):
        return "0"


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

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            [
                "구분",
                "항목명",
                "월계",
                "연간합계",
                "유형",
            ]
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

    def update_rows(self, rows: list[dict], total_headcount: int = 1) -> None:
        self.table.setRowCount(0)
        if not rows:
            return
        try:
            total_headcount = max(0, int(total_headcount))
        except (TypeError, ValueError):
            total_headcount = 1

        # 피복비, 식대, 건강검진비, 의약품비 = 1인당 월액 → 월계/연간에 인원수 곱함
        PER_PERSON_EXP_CODES = {"FIX_WEL_CLOTH", "FIX_WEL_MEAL", "FIX_WEL_CHECKUP", "FIX_WEL_MEDICINE"}
        # 변동경비·대행비: row_total이 연간합계 금액이므로 월계=연간/12, 연간합계=row_total 그대로 표시
        ANNUAL_BASED_TYPES = ("변동경비", "대행비")

        total_monthly = 0
        total_annual = 0

        for row in rows:
            if not isinstance(row, dict):
                continue
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row.get("category", ""))))

            expense_name = str(row.get("name", ""))
            self.table.setItem(row_idx, 1, QTableWidgetItem(expense_name))

            try:
                raw_total = str(row.get("row_total", 0)).replace(",", "").strip() or "0"
                row_total = int(float(raw_total))
            except (ValueError, TypeError):
                row_total = 0

            row_type = row.get("type", "")
            is_annual_based = row_type in ANNUAL_BASED_TYPES

            if is_annual_based:
                # 변동경비·대행비: row_total = 연간합계 → 월계 = 연간/12
                monthly_val = row_total // 12
                annual_val = row_total
            else:
                # 고정경비: row_total = 1인당 월계. 피복비/식대/건강검진비/의약품비는 인원수 곱해서 월계·연간 반영
                exp_code = row.get("exp_code", "")
                if exp_code in PER_PERSON_EXP_CODES:
                    monthly_val = row_total * total_headcount
                    annual_val = row_total * total_headcount * 12
                else:
                    monthly_val = row_total
                    annual_val = row_total * 12

            monthly_item = QTableWidgetItem(_fmt_row_total(monthly_val))
            if row_type in ("대행비", "Pass-through"):
                monthly_item.setForeground(
                    monthly_item.foreground().color().fromRgb(21, 101, 192)
                )
            self.table.setItem(row_idx, 2, monthly_item)

            annual_item = QTableWidgetItem(_fmt_row_total(annual_val))
            if row_type in ("대행비", "Pass-through"):
                annual_item.setForeground(
                    annual_item.foreground().color().fromRgb(21, 101, 192)
                )
            self.table.setItem(row_idx, 3, annual_item)

            type_display = "대납비" if row_type == "대행비" else str(row_type)
            self.table.setItem(row_idx, 4, QTableWidgetItem(type_display))

            total_monthly += monthly_val
            total_annual += annual_val

        # 합계 행 추가
        if rows:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)

            from PyQt6.QtGui import QFont, QColor

            def create_bold_item(text):
                item = QTableWidgetItem(text)
                font = QFont()
                font.setBold(True)
                item.setFont(font)
                item.setBackground(QColor(240, 240, 240))
                return item

            self.table.setItem(row_idx, 0, create_bold_item("합계"))
            self.table.setItem(row_idx, 1, create_bold_item(""))
            self.table.setItem(row_idx, 2, create_bold_item(f"{int(total_monthly):,}"))
            self.table.setItem(row_idx, 3, create_bold_item(f"{int(total_annual):,}"))
            self.table.setItem(row_idx, 4, create_bold_item(""))
