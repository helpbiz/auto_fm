# src/ui/wage_compare_dialog.py
"""연도별 노임단가 분개·비교 다이얼로그."""
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPushButton,
    QAbstractItemView,
)
from PyQt6.QtCore import Qt

from src.domain.wage_manager import WageManager


_GRADE_ORDER = [
    "기술사", "특급기술자", "고급기술자", "중급기술자", "초급기술자",
    "고급숙련기술자", "중급숙련기술자", "초급숙련기술자", "단순노무종사원",
]


def _fmt(val) -> str:
    return f"{val:,}"


class WageCompareDialog(QDialog):
    """노임단가 일급분개 · 연도별 비교 다이얼로그."""

    def __init__(self, wage_manager: WageManager, parent=None):
        super().__init__(parent)
        self._wm = wage_manager
        self.setWindowTitle("노임단가 분개 · 연도별 비교")
        self.setMinimumSize(1100, 650)
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # 상단: 직종 선택
        top = QHBoxLayout()
        top.addWidget(QLabel("직종:"))
        self._grade_combo = QComboBox()
        grades = self._wm.list_grades()
        ordered = [g for g in _GRADE_ORDER if g in grades]
        ordered += [g for g in grades if g not in ordered]
        self._grade_combo.addItems(ordered)
        self._grade_combo.currentTextChanged.connect(self._refresh)
        top.addWidget(self._grade_combo)
        top.addStretch()
        layout.addLayout(top)

        # 연도별 비교 테이블
        self._table = QTableWidget()
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        layout.addWidget(self._table)

        # 하단 닫기
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("닫기")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def _refresh(self):
        grade = self._grade_combo.currentText()
        if not grade:
            return
        rows = self._wm.compare_grades_by_year(grade)
        if not rows:
            self._table.setRowCount(0)
            self._table.setColumnCount(0)
            return

        # 행 정의 (항목명) — 정부고시 일당은 원본 govt_daily 사용
        row_labels = [
            ("정부고시 일당", "govt_daily"),
            ("M/D 기본급", "md_basic"),
            ("시간급", "hourly_wage"),
            ("통상시간급", "tongsan_hourly"),
            ("통상일급", "tongsan_daily"),
            ("", None),  # separator
            ("기본급(월)", "base_salary"),
            ("연차수당", "annual_leave"),
            ("주휴수당", "weekly_holiday"),
            ("제수당 소계", "allowance"),
            ("상여금(월)", "bonus"),
            ("퇴직급여충당금", "retirement"),
            ("인건비 소계", "salary_subtotal"),
            ("", None),  # separator
            ("산재보험", "insurance.accident"),
            ("국민연금", "insurance.national"),
            ("고용보험", "insurance.employ"),
            ("건강보험", "insurance.health"),
            ("장기요양보험", "insurance.longterm"),
            ("임금채권보장", "insurance.wage_bond"),
            ("석면피해구제", "insurance.asbestos"),
            ("보험료 합계", "insurance.total"),
            ("", None),  # separator
            ("월 합계", "monthly_total"),
        ]

        years = [r["year"] for r in rows]
        num_years = len(years)

        # 열: 항목 | 연도1 | 연도2 | ... | 증감(마지막-처음)
        has_diff = num_years >= 2
        col_count = 1 + num_years + (1 if has_diff else 0)
        self._table.setRowCount(len(row_labels))
        self._table.setColumnCount(col_count)

        headers = ["항목"] + [f"{y}년" for y in years]
        if has_diff:
            headers.append(f"증감({years[-1]}-{years[0]})")
        self._table.setHorizontalHeaderLabels(headers)

        for ri, (label, key) in enumerate(row_labels):
            # 항목명
            item = QTableWidgetItem(label)
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self._table.setItem(ri, 0, item)

            if key is None:
                continue

            values = []
            for ci, row_data in enumerate(rows):
                val = self._get_nested(row_data, key)
                values.append(val)
                cell = QTableWidgetItem(_fmt(val) if val else "")
                cell.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self._table.setItem(ri, 1 + ci, cell)

            if has_diff and len(values) >= 2 and values[0] and values[-1]:
                diff = values[-1] - values[0]
                pct = (diff / values[0] * 100) if values[0] != 0 else 0
                sign = "+" if diff > 0 else ""
                text = f"{sign}{_fmt(diff)} ({sign}{pct:.1f}%)"
                cell = QTableWidgetItem(text)
                cell.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self._table.setItem(ri, col_count - 1, cell)

        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        for c in range(1, col_count):
            self._table.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeMode.Stretch)

    @staticmethod
    def _get_nested(data: dict, key: str):
        parts = key.split(".")
        val = data
        for p in parts:
            if isinstance(val, dict):
                val = val.get(p)
            else:
                return None
        return val
