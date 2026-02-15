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

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(
            [
                "직무/직책",
                "인원",
                "기본급",
                "상여금",
                "제수당",
                "퇴직급여 충당금",
                "인건비 소계",
                "산정 금액",
            ]
        )
        # 직무/직책·인원은 직무별 인원입력에서만 입력, 여기는 표시 전용. 기본급·상여금·제수당 등 자동계산 컬럼은 데이터 입력 불가
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

    def _safe_int(self, value, default: int = 0) -> int:
        """금액/인원 등 숫자 필드 안전 변환 (Decimal/float/None 대비)."""
        if value is None:
            return default
        try:
            return int(round(float(value)))
        except (TypeError, ValueError):
            return default

    def update_rows(self, rows: list[dict]) -> None:
        """노무비 상세 테이블 갱신. 기본급·상여금·제수당·퇴직급여 충당금·인건비 소계·산정 금액은 자동계산 결과로 표시."""
        self.table.setRowCount(0)

        total_headcount = 0
        total_base_salary = 0
        total_bonus = 0
        total_allowances = 0
        total_retirement = 0
        total_labor_subtotal = 0
        total_role_total = 0

        for row in rows:
            if not isinstance(row, dict):
                continue
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            role = str(row.get("role", "") or row.get("job_name", ""))
            headcount = self._safe_int(row.get("headcount"), 0)
            base_salary = self._safe_int(row.get("base_salary"), 0)
            bonus = self._safe_int(row.get("bonus"), 0)
            allowances = self._safe_int(
                row.get("allowances") if row.get("allowances") is not None else row.get("allowance"),
                0,
            )
            retirement = self._safe_int(row.get("retirement"), 0)
            labor_subtotal = self._safe_int(row.get("labor_subtotal"), 0)
            role_total = self._safe_int(
                row.get("role_total") if row.get("role_total") is not None else row.get("total"),
                0,
            )

            self.table.setItem(row_idx, 0, QTableWidgetItem(role))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(headcount)))
            self.table.setItem(row_idx, 2, QTableWidgetItem(f"{base_salary:,}"))
            self.table.setItem(row_idx, 3, QTableWidgetItem(f"{bonus:,}"))
            self.table.setItem(row_idx, 4, QTableWidgetItem(f"{allowances:,}"))
            self.table.setItem(row_idx, 5, QTableWidgetItem(f"{retirement:,}"))
            self.table.setItem(row_idx, 6, QTableWidgetItem(f"{labor_subtotal:,}"))
            self.table.setItem(row_idx, 7, QTableWidgetItem(f"{role_total:,}"))

            total_headcount += headcount
            total_base_salary += base_salary
            total_bonus += bonus
            total_allowances += allowances
            total_retirement += retirement
            total_labor_subtotal += labor_subtotal
            total_role_total += role_total

        # 합계 행 추가 (데이터가 있을 때만)
        if rows:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)

            # 합계 행 스타일링을 위한 아이템 생성
            from PyQt6.QtGui import QFont, QColor
            from PyQt6.QtCore import Qt

            def create_bold_item(text):
                item = QTableWidgetItem(text)
                font = QFont()
                font.setBold(True)
                item.setFont(font)
                item.setBackground(QColor(240, 240, 240))
                return item

            self.table.setItem(row_idx, 0, create_bold_item("합계"))
            self.table.setItem(row_idx, 1, create_bold_item(str(int(total_headcount))))
            self.table.setItem(row_idx, 2, create_bold_item(f"{int(total_base_salary):,}"))
            self.table.setItem(row_idx, 3, create_bold_item(f"{int(total_bonus):,}"))
            self.table.setItem(row_idx, 4, create_bold_item(f"{int(total_allowances):,}"))
            self.table.setItem(row_idx, 5, create_bold_item(f"{int(total_retirement):,}"))
            self.table.setItem(row_idx, 6, create_bold_item(f"{int(total_labor_subtotal):,}"))
            self.table.setItem(row_idx, 7, create_bold_item(f"{int(total_role_total):,}"))
