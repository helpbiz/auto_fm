"""
세부 경비 항목 입력 테이블.
작업자가 세부 경비(sub_code)를 입력하고, 시나리오 저장 시 DB(md_expense_sub_item)에 반영된다.
노무비에서 이미 계산되는 인적보험료 7개 항목은 세부 입력 대상에서 제외한다.
경비코드는 3개 그룹(고정/변동/대행비)으로 구분하여 콤보에 표시한다.
경비코드 선택 시 해당 코드에 대한 세부 항목이 없으면 default 시나리오 기본 내용을 불러온다.
"""
import logging
from typing import Callable, Optional
from src.domain.constants.expense_groups import GROUP_LABELS, group_display_order
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QPushButton,
    QAbstractItemView,
    QStyledItemDelegate,
)
from PyQt6.QtCore import Qt, QRegularExpression, pyqtSignal
from PyQt6.QtGui import QColor, QDoubleValidator, QIntValidator, QRegularExpressionValidator

# 노무비에서 계산되는 인적보험료(세부 경비 입력 불필요)
EXP_CODES_FROM_LABOR = frozenset({
    "FIX_INS_INDUST",   # 산재보험료
    "FIX_INS_PENSION",  # 국민연금
    "FIX_INS_EMPLOY",   # 고용보험료
    "FIX_INS_HEALTH",   # 국민건강보험료
    "FIX_INS_LONGTERM", # 노인장기요양보험료
    "FIX_INS_WAGE",     # 임금채권보장보험료
    "FIX_INS_ASBESTOS", # 석면피해구제분담금
})

# 수량 = 연간 실제 지급수량. 저장·계산 시 입력값÷12 로 월 단위 변환
EXP_CODES_QUANTITY_ANNUAL = frozenset({
    "FIX_WEL_CLOTH",    # 피복비 (착/년)
    "FIX_WEL_CHECKUP",  # 건강검진비 (회/년)
    "FIX_TRAINING",     # 교육훈련비 (인원 수/년 → ÷12 저장)
})
# 수량 = 연간 정수 입력. 저장·계산 시 입력값÷12÷합계인원 (직무별 인원 합계)
EXP_CODES_QUANTITY_ANNUAL_PER_HEAD = frozenset({"FIX_WEL_MEDICINE"})  # 의약품비 (SET/년)
# 경비코드별 기본 규격·단위 (표시/저장 시 빈 값일 때 사용)
EXP_DEFAULT_SPEC_UNIT: dict[str, tuple[str, str]] = {
    "FIX_WEL_MEDICINE": ("SET", "년"),   # 의약품비
    "FIX_WEL_CHECKUP": ("회", "년"),     # 건강검진비
}
# 수량 컬럼 표시명 "인원 수", 정수 입력, 비고는 파이썬 계산
EXP_CODES_QUANTITY_HEADCOUNT = frozenset({"FIX_TRAINING", "FIX_TRAVEL"})  # 교육훈련비, 출장여비

# 컬럼 인덱스
COL_EXP_CODE = 0
COL_SUB_CODE = 1


def _fmt_comma(value: int | float) -> str:
    """원 단위 값을 콤마 구분 문자열로 표시 (예: 1798000 -> "1,798,000")."""
    if value is None or (isinstance(value, (int, float)) and value == 0):
        return "0"
    return f"{int(round(float(value))):,}"


def _parse_comma(text: str) -> int:
    """콤마 구분 문자열을 원 단위 정수로 변환 (예: "1,798,000" -> 1798000)."""
    if not text or not str(text).strip():
        return 0
    s = str(text).replace(",", "").strip()
    if not s:
        return 0
    try:
        return int(round(float(s)))
    except (ValueError, TypeError):
        return 0


def _fmt_quantity_comma(value: int | float) -> str:
    """수량 값을 소수점 1자리까지 올린 뒤 천 단위 콤마로 표시 (예: 1234.56 -> "1,234.6")."""
    if value is None:
        return "0.0"
    try:
        x = float(value)
    except (ValueError, TypeError):
        return "0.0"
    if x != x:  # nan
        return "0.0"
    x = round(x, 1)
    return f"{x:,.1f}"


COL_SUB_NAME = 2
COL_SPEC = 3
COL_UNIT = 4
COL_QUANTITY = 5
COL_UNIT_PRICE = 6
COL_AMOUNT = 7
COL_REMARK = 8
COL_SORT_ORDER = 9


def _sub_item_to_dict(si) -> dict:
    """ExpenseSubItem or dict -> dict."""
    if hasattr(si, "__dataclass_fields__"):
        return {
            "exp_code": getattr(si, "exp_code", ""),
            "sub_code": getattr(si, "sub_code", ""),
            "sub_name": getattr(si, "sub_name", ""),
            "spec": getattr(si, "spec", ""),
            "unit": getattr(si, "unit", "식"),
            "quantity": float(getattr(si, "quantity", 0)),
            "unit_price": int(getattr(si, "unit_price", 0)),
            "amount": int(getattr(si, "amount", 0)),
            "remark": getattr(si, "remark", ""),
            "sort_order": int(getattr(si, "sort_order", 0)),
            "is_active": int(getattr(si, "is_active", 1)),
        }
    if isinstance(si, dict):
        return {
            "exp_code": si.get("exp_code", ""),
            "sub_code": si.get("sub_code", ""),
            "sub_name": si.get("sub_name", ""),
            "spec": si.get("spec", ""),
            "unit": si.get("unit", "식"),
            "quantity": float(si.get("quantity", 0)),
            "unit_price": int(si.get("unit_price", 0)),
            "amount": int(si.get("amount", 0)),
            "remark": si.get("remark", ""),
            "sort_order": int(si.get("sort_order", 0)),
            "is_active": int(si.get("is_active", 1)),
        }
    return {}


class ExpenseSubItemTable(QWidget):
    """세부 경비 항목을 경비코드별로 입력·편집하는 위젯. 경비코드별 '저장' 시 해당 항목만 DB 반영."""

    save_requested = pyqtSignal()
    save_current_expense_requested = pyqtSignal()
    apply_edit_applied = pyqtSignal()  # 경비입력 수정 반영 시 (상태 메시지용)
    quantity_or_price_changed = pyqtSignal()  # 수량/단가 셀 변경 시 (경비상세 자동 재계산용)

    def __init__(self):
        super().__init__()
        self.dirty = False
        self._external_on_change = None
        self._sub_items_by_exp: dict[str, list[dict]] = {}
        self._exp_codes: list[str] = []
        self._current_exp_code: str | None = None
        self._exp_name_map: dict[str, str] = {}
        self._group_map: dict[str, str] = {}
        self._total_headcount: int = 1  # 직무별 인원입력 합계 (의약품비 등 ÷합계인원 시 사용)
        self._fetch_default_sub_items: Optional[Callable[[str], list]] = None  # exp_code -> list[dict|ExpenseSubItem]

        layout = QVBoxLayout(self)
        title = QLabel("경비입력")
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)

        row = QHBoxLayout()
        row.addWidget(QLabel("경비코드"))
        self.exp_combo = QComboBox()
        self.exp_combo.setMinimumWidth(280)
        self.exp_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.exp_combo.currentTextChanged.connect(self._on_exp_code_changed)
        row.addWidget(self.exp_combo, 1)
        self.exp_select_btn = QPushButton("경비코드 선택")
        self.exp_select_btn.setToolTip("선택한 경비코드의 세부 항목을 테이블에 표시합니다.")
        self.exp_select_btn.clicked.connect(self._on_exp_select_clicked)
        row.addWidget(self.exp_select_btn)
        layout.addLayout(row)

        self._default_headers = [
            "경비코드", "세부코드", "항목명", "규격", "단위", "수량", "단가", "금액", "비고", "정렬",
        ]
        self.table = QTableWidget(0, 10)
        self.table.setHorizontalHeaderLabels(self._default_headers)
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.SelectedClicked
            | QAbstractItemView.EditTrigger.EditKeyPressed
            | QAbstractItemView.EditTrigger.AnyKeyPressed
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._ensure_editable()

        class IntDelegate(QStyledItemDelegate):
            def createEditor(self, parent, option, index):
                from PyQt6.QtWidgets import QLineEdit
                e = QLineEdit(parent)
                e.setValidator(QIntValidator(0, 100_000_000))
                return e

        class ThousandDelegate(QStyledItemDelegate):
            """숫자와 콤마만 허용 (예: 1,798,000)."""
            def createEditor(self, parent, option, index):
                from PyQt6.QtWidgets import QLineEdit
                e = QLineEdit(parent)
                e.setValidator(QRegularExpressionValidator(QRegularExpression(r"[\d,]+")))
                return e

        class FloatDelegate(QStyledItemDelegate):
            def createEditor(self, parent, option, index):
                from PyQt6.QtWidgets import QLineEdit
                e = QLineEdit(parent)
                e.setValidator(QDoubleValidator(0.0, 1e9, 6))
                return e

        self._quantity_int_delegate = IntDelegate(self.table)
        self._quantity_float_delegate = FloatDelegate(self.table)
        self.table.setItemDelegateForColumn(COL_QUANTITY, self._quantity_float_delegate)
        self.table.setItemDelegateForColumn(COL_UNIT_PRICE, ThousandDelegate(self.table))
        self.table.setItemDelegateForColumn(COL_SORT_ORDER, IntDelegate(self.table))
        self.table.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self.table)

        btn_row = QHBoxLayout()
        self.add_row_btn = QPushButton("행 추가")
        self.add_row_btn.setToolTip("빈 행을 추가합니다. 세부코드를 입력한 행만 저장됩니다.")
        self.add_row_btn.clicked.connect(self._add_row)
        self.del_row_btn = QPushButton("행 삭제")
        self.del_row_btn.setToolTip("선택한 행을 삭제합니다.")
        self.del_row_btn.clicked.connect(self._delete_row)
        self.apply_edit_btn = QPushButton("경비입력 수정")
        self.apply_edit_btn.setToolTip(
            "현재 테이블 편집 내용을 선택한 경비코드에 반영합니다. 반영 후 '시나리오 저장'을 누르면 저장됩니다."
        )
        self.apply_edit_btn.clicked.connect(self._on_apply_edit_clicked)
        self.save_btn = QPushButton("경비코드 저장")
        self.save_btn.setToolTip("선택한 경비코드의 세부 항목만 DB에 저장합니다. 집계 실행 없이 사용 가능.")
        self.save_btn.clicked.connect(self._on_save_clicked)
        btn_row.addWidget(self.add_row_btn)
        btn_row.addWidget(self.del_row_btn)
        btn_row.addWidget(self.apply_edit_btn)
        btn_row.addWidget(self.save_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

    def _on_apply_edit_clicked(self) -> None:
        """현재 테이블 편집 내용을 선택한 경비코드에 반영. 시나리오 저장 시 함께 저장됨."""
        self._save_table_to_current_exp()
        self.apply_edit_applied.emit()
        if self._external_on_change:
            self._external_on_change()

    def _on_save_clicked(self) -> None:
        """선택한 경비코드만 DB 저장 요청 (해당 경비항목만 반영, 집계 실행과 별개)."""
        self.save_current_expense_requested.emit()

    def on_change(self, callback) -> None:
        self._external_on_change = callback

    def _on_item_changed(self, item) -> None:
        if item.column() in (COL_QUANTITY, COL_UNIT_PRICE):
            self._update_amount_row(item.row())
        if item.column() == COL_UNIT_PRICE:
            # 단가 셀 편집 후 천 단위 콤마 포맷 적용
            try:
                price_val = _parse_comma((item.text() or "").strip())
                if price_val >= 0:
                    self.table.blockSignals(True)
                    try:
                        item.setText(_fmt_comma(price_val))
                    finally:
                        self.table.blockSignals(False)
            except (ValueError, TypeError):
                pass
        if item.column() == COL_QUANTITY:
            try:
                raw = (item.text() or "").replace(",", "").strip() or "0"
                qty_num = round(float(raw), 1)  # 소수점 1자리까지
                self.table.blockSignals(True)
                try:
                    if self._current_exp_code in EXP_CODES_QUANTITY_HEADCOUNT:
                        headcount = int(round(qty_num))
                        remark_text = f"{headcount}인×1회/년÷12개월"
                        remark_item = self.table.item(item.row(), COL_REMARK)
                        if remark_item:
                            remark_item.setText(remark_text)
                    # 수량 셀 소수점 1자리·천 단위 콤마로 갱신
                    item.setText(_fmt_quantity_comma(qty_num))
                finally:
                    self.table.blockSignals(False)
            except (ValueError, TypeError):
                pass
        self.dirty = True
        if item.column() in (COL_QUANTITY, COL_UNIT_PRICE):
            self.quantity_or_price_changed.emit()
        if self._external_on_change:
            self._external_on_change()

    def _update_amount_row(self, row: int) -> None:
        qty_item = self.table.item(row, COL_QUANTITY)
        price_item = self.table.item(row, COL_UNIT_PRICE)
        amount_item = self.table.item(row, COL_AMOUNT)
        if amount_item is None:
            return
        self.table.blockSignals(True)
        try:
            qty_input = float((qty_item.text() or "").replace(",", "").strip() or "0")
            if self._current_exp_code in EXP_CODES_QUANTITY_ANNUAL:
                qty_for_calc = qty_input / 12  # 연간 지급수량 → 월 단위로 계산
            elif self._current_exp_code in EXP_CODES_QUANTITY_ANNUAL_PER_HEAD:
                qty_for_calc = qty_input / 12 / max(self._total_headcount, 1)  # 연간 SET ÷12 ÷합계인원
            elif self._current_exp_code in EXP_CODES_QUANTITY_HEADCOUNT:
                qty_for_calc = qty_input / 12  # 인원 수(연간) → 월 단위로 계산
            else:
                qty_for_calc = qty_input
            price_원 = _parse_comma((price_item.text() or "").strip())
            amount_원 = int(qty_for_calc * price_원)
            amount_item.setText(_fmt_comma(amount_원))
        except (ValueError, TypeError):
            amount_item.setText("0")
        finally:
            self.table.blockSignals(False)

    def load_sub_items(
        self,
        sub_items_by_exp: dict[str, list],
        expense_items: list[dict],
        total_headcount: int = 1,
    ) -> None:
        """DB에서 읽은 세부 항목(exp_code별)과 경비 항목 목록으로 위젯을 채운다.
        total_headcount: 직무별 인원입력 합계인원 (의약품비 등 수량 표시/계산용)
        """
        self._total_headcount = max(int(total_headcount), 1)
        self._sub_items_by_exp = {}
        for exp_code, items in sub_items_by_exp.items():
            self._sub_items_by_exp[exp_code] = [_sub_item_to_dict(si) for si in items]
        filtered_items = list(expense_items)
        # 그룹 순서 → sort_order → exp_code 순으로 정렬
        def sort_key(item: dict) -> tuple:
            g = item.get("group_code", "")
            return (
                group_display_order(g),
                item.get("sort_order", 0),
                item.get("exp_code", ""),
            )
        filtered_items.sort(key=sort_key)
        self._exp_codes = [i["exp_code"] for i in filtered_items]
        self._exp_name_map = {i["exp_code"]: i.get("exp_name", "") for i in filtered_items}
        self._group_map = {i["exp_code"]: i.get("group_code", "") for i in filtered_items}

        self.exp_combo.blockSignals(True)
        try:
            self.exp_combo.clear()
            for item in filtered_items:
                exp_code = item["exp_code"]
                name = item.get("exp_name", "")
                group_code = item.get("group_code", "")
                group_label = GROUP_LABELS.get(group_code, group_code)
                display = f"[{group_label}] {exp_code} - {name}" if name else f"[{group_label}] {exp_code}"
                self.exp_combo.addItem(display, exp_code)

            prev_exp_code = self._current_exp_code  # 이전 선택 기억
            self._current_exp_code = None
            if self._exp_codes:
                # 이전 선택 코드가 여전히 존재하면 그대로 복원, 없으면 첫 비보험 코드 선택
                target_idx = 0
                if prev_exp_code and prev_exp_code in self._exp_codes:
                    target_idx = self._exp_codes.index(prev_exp_code)
                else:
                    for i, code in enumerate(self._exp_codes):
                        if code not in EXP_CODES_FROM_LABOR:
                            target_idx = i
                            break
                # setCurrentIndex도 시그널 블록 안에서 실행 (불필요한 _on_exp_code_changed 방지)
                self.exp_combo.setCurrentIndex(target_idx)
                self._current_exp_code = self._exp_codes[target_idx]
        finally:
            self.exp_combo.blockSignals(False)

        if self._current_exp_code:
            self._fill_table(self._sub_items_by_exp.get(self._current_exp_code, []))
            self._update_quantity_header_and_delegate()
        else:
            self.exp_combo.addItem("(경비코드 없음 — 시나리오 불러오기 후 표시됨)", "")
            self._fill_table([])
        self.dirty = False

    def _fill_table(self, rows: list[dict]) -> None:
        self.table.blockSignals(True)
        try:
            self.table.setRowCount(0)
            for r in rows:
                row_idx = self.table.rowCount()
                self.table.insertRow(row_idx)
                self._set_row(row_idx, r)
        finally:
            self.table.blockSignals(False)
        self._ensure_editable()

    def _ensure_editable(self) -> None:
        """테이블과 뷰포트가 편집 가능한 상태인지 보장한다."""
        self.table.setEnabled(True)
        self.table.viewport().setEnabled(True)
        self.table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.table.viewport().setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.SelectedClicked
            | QAbstractItemView.EditTrigger.EditKeyPressed
            | QAbstractItemView.EditTrigger.AnyKeyPressed
        )

    def _set_row(self, row_idx: int, r: dict) -> None:
        for col, key in [
            (COL_EXP_CODE, "exp_code"),
            (COL_SUB_CODE, "sub_code"),
            (COL_SUB_NAME, "sub_name"),
            (COL_SPEC, "spec"),
            (COL_UNIT, "unit"),
            (COL_QUANTITY, "quantity"),
            (COL_UNIT_PRICE, "unit_price"),
            (COL_AMOUNT, "amount"),
            (COL_REMARK, "remark"),
            (COL_SORT_ORDER, "sort_order"),
        ]:
            # exp_code는 r에 없으면 현재 선택된 경비코드 사용
            if key == "exp_code":
                val = r.get(key, self._current_exp_code or "")
            else:
                val = r.get(key, 0 if key in ("quantity", "unit_price", "amount", "sort_order") else "")

            if col == COL_UNIT_PRICE or col == COL_AMOUNT:
                display = _fmt_comma(val)
            elif col == COL_QUANTITY and self._current_exp_code in EXP_CODES_QUANTITY_ANNUAL:
                # 연간 지급수량으로 표시 (저장값 × 12), 소수점 1자리
                x = round(float(val or 0) * 12, 1)
                display = _fmt_quantity_comma(x)
            elif col == COL_QUANTITY and self._current_exp_code in EXP_CODES_QUANTITY_ANNUAL_PER_HEAD:
                # 연간 SET, 표시 = 저장값 × 12 × 합계인원, 소수점 1자리
                x = round(float(val or 0) * 12 * max(self._total_headcount, 1), 1)
                display = _fmt_quantity_comma(x)
            elif col == COL_QUANTITY and self._current_exp_code in EXP_CODES_QUANTITY_HEADCOUNT:
                # 교육훈련비/출장여비: 인원 수(정수)로 표시, 소수점 1자리 형식
                display = _fmt_quantity_comma(round(float(val or 0) * 12, 1))
            elif col == COL_REMARK and self._current_exp_code in EXP_CODES_QUANTITY_HEADCOUNT:
                # 교육훈련비 비고: 파이썬 계산으로 표시
                headcount = int(round(float(r.get("quantity", 0) or 0) * 12))
                display = f"{headcount}인×1회/년÷12개월"
            elif col == COL_QUANTITY:
                # 일반 수량: 소수점 1자리, 천 단위 콤마 표시
                display = _fmt_quantity_comma(round(float(val) if val != "" else 0, 1))
            elif col == COL_SPEC and self._current_exp_code in EXP_DEFAULT_SPEC_UNIT and not (val or "").strip():
                display = EXP_DEFAULT_SPEC_UNIT[self._current_exp_code][0]
            elif col == COL_UNIT and self._current_exp_code in EXP_DEFAULT_SPEC_UNIT and not (val or "").strip():
                display = EXP_DEFAULT_SPEC_UNIT[self._current_exp_code][1]
            else:
                display = str(val)
            item = QTableWidgetItem(display)

            # 경비코드 컬럼은 항상 읽기 전용
            if col == COL_EXP_CODE:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            if col == COL_AMOUNT:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if col == COL_REMARK and self._current_exp_code in EXP_CODES_QUANTITY_HEADCOUNT:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if self._current_exp_code in EXP_CODES_FROM_LABOR:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            # 시각적 구분: 읽기 전용 → 회색, 수량/단가 편집 가능 → 연한 파란색
            is_readonly = not (item.flags() & Qt.ItemFlag.ItemIsEditable)
            if is_readonly:
                item.setBackground(QColor("#F0F0F0"))
            elif col in (COL_QUANTITY, COL_UNIT_PRICE):
                item.setBackground(QColor("#E8F0FE"))

            self.table.setItem(row_idx, col, item)

    def _update_quantity_header_and_delegate(self) -> None:
        """경비코드에 따라 수량 컬럼 헤더·입력 방식을 변경 (교육훈련비: 인원 수, 정수)."""
        headers = list(self._default_headers)
        if self._current_exp_code in EXP_CODES_QUANTITY_HEADCOUNT:
            headers[COL_QUANTITY] = "인원 수"
            self.table.setItemDelegateForColumn(COL_QUANTITY, self._quantity_int_delegate)
        else:
            headers[COL_QUANTITY] = "수량"
            self.table.setItemDelegateForColumn(COL_QUANTITY, self._quantity_float_delegate)
        self.table.setHorizontalHeaderLabels(headers)

    def _on_exp_select_clicked(self) -> None:
        """경비코드 선택 버튼: 현재 콤보 선택을 적용해 해당 경비코드 세부 항목을 테이블에 표시."""
        self._on_exp_code_changed(self.exp_combo.currentText() or "")

    def set_fetch_default_sub_items(self, fn: Optional[Callable[[str], list]]) -> None:
        """경비코드 선택 시 세부 항목이 없을 때 default 시나리오에서 불러올 콜백 설정. fn(exp_code) -> list[dict|ExpenseSubItem]"""
        self._fetch_default_sub_items = fn

    def _on_exp_code_changed(self, display_text: str) -> None:
        exp_code = self.exp_combo.currentData()
        if exp_code is None:
            exp_code = (display_text.split(" - ")[0] if " - " in display_text else display_text).strip()
        if not exp_code:
            return
        self._save_table_to_current_exp()
        self._current_exp_code = exp_code
        if exp_code not in self._sub_items_by_exp:
            self._sub_items_by_exp[exp_code] = []
        # 세부 항목이 비어 있으면 default 시나리오 기본 내용 불러오기
        if not self._sub_items_by_exp[exp_code] and self._fetch_default_sub_items:
            try:
                default_list = self._fetch_default_sub_items(exp_code)
                if default_list:
                    self._sub_items_by_exp[exp_code] = [_sub_item_to_dict(si) for si in default_list]
                    self.dirty = True
                    if self._external_on_change:
                        self._external_on_change()
            except Exception as e:
                logging.exception("경비코드 기본 내용 불러오기 실패: %s", e)
        self._fill_table(self._sub_items_by_exp[exp_code])
        self._update_quantity_header_and_delegate()

    def _save_table_to_current_exp(self) -> None:
        if self._current_exp_code is None:
            return
        rows = []
        for row_idx in range(self.table.rowCount()):
            r = self._get_row(row_idx)
            if r is None:
                continue
            logging.info("[_save_table] row %d: sub_code=%s qty=%s price=%s amount=%s",
                         row_idx, r.get("sub_code"), r.get("quantity"), r.get("unit_price"), r.get("amount"))
            # 세부코드가 입력된 행만 저장 (빈 행은 추가되지 않음)
            if not (r.get("sub_code") or "").strip():
                continue
            rows.append(r)
        self._sub_items_by_exp[self._current_exp_code] = rows
        logging.info("[_save_table] exp_code=%s → %d rows saved to dict", self._current_exp_code, len(rows))

    def _get_row(self, row_idx: int) -> dict | None:
        def cell(col: int) -> str:
            it = self.table.item(row_idx, col)
            return (it.text() or "").strip() if it else ""

        try:
            qty_input = float(cell(COL_QUANTITY).replace(",", "") or "0")
            if self._current_exp_code in EXP_CODES_QUANTITY_ANNUAL:
                qty = qty_input / 12  # 연간 지급수량 → 월 단위로 저장
            elif self._current_exp_code in EXP_CODES_QUANTITY_ANNUAL_PER_HEAD:
                qty = qty_input / 12 / max(self._total_headcount, 1)  # 연간 SET ÷12 ÷합계인원
            elif self._current_exp_code in EXP_CODES_QUANTITY_HEADCOUNT:
                qty = qty_input / 12  # 인원 수(연간) → 월 단위로 저장
            else:
                qty = qty_input
            # 연간→월 변환 값은 소수 6자리 유지(5→5/12≈0.4167, 복원 시 5로 표시). 그 외는 1자리
            if self._current_exp_code in (
                EXP_CODES_QUANTITY_ANNUAL | EXP_CODES_QUANTITY_ANNUAL_PER_HEAD | EXP_CODES_QUANTITY_HEADCOUNT
            ):
                qty = round(qty, 6)
            else:
                qty = round(qty, 1)
            price = _parse_comma(cell(COL_UNIT_PRICE))
            amount = int(qty * price)
        except (ValueError, TypeError):
            qty, price, amount = 0, 0, 0
        if self._current_exp_code in EXP_CODES_QUANTITY_HEADCOUNT:
            remark = f"{int(round(qty * 12))}인×1회/년÷12개월"
        else:
            remark = cell(COL_REMARK)
        _spec_default, _unit_default = EXP_DEFAULT_SPEC_UNIT.get(self._current_exp_code, ("", "식"))
        return {
            "exp_code": self._current_exp_code or "",  # 경비코드 추가
            "sub_code": cell(COL_SUB_CODE),
            "sub_name": cell(COL_SUB_NAME),
            "spec": cell(COL_SPEC) or _spec_default,
            "unit": cell(COL_UNIT) or _unit_default,
            "quantity": qty,
            "unit_price": price,
            "amount": amount,
            "remark": remark,
            "sort_order": int(cell(COL_SORT_ORDER).replace(",", "") or "0"),
            "is_active": 1,
        }

    def _add_row(self) -> None:
        if self._current_exp_code is None:
            return
        if self._current_exp_code not in self._sub_items_by_exp:
            self._sub_items_by_exp[self._current_exp_code] = []
        row_idx = self.table.rowCount()
        self.table.insertRow(row_idx)
        row_data: dict = {"sort_order": row_idx + 1}
        if self._current_exp_code in EXP_DEFAULT_SPEC_UNIT:
            row_data["spec"], row_data["unit"] = EXP_DEFAULT_SPEC_UNIT[self._current_exp_code]
        self._set_row(row_idx, row_data)
        self.dirty = True
        if self._external_on_change:
            self._external_on_change()

    def _delete_row(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            return
        self.table.removeRow(row)
        self.dirty = True
        if self._external_on_change:
            self._external_on_change()

    def get_current_exp_sub_items(self, total_headcount: int = 1) -> tuple[str | None, list[dict]]:
        """현재 선택한 경비코드의 테이블을 반영한 뒤, (exp_code, 세부 항목 리스트) 반환.
        해당 경비항목만 DB 저장할 때 사용. 인적보험 7종(노무비 자동계산)은 저장 대상 아님 → (None, [])."""
        self._total_headcount = max(int(total_headcount), 1)
        self._save_table_to_current_exp()
        exp_code = self._current_exp_code
        if not exp_code or exp_code in EXP_CODES_FROM_LABOR:
            return None, []
        sub_list = self._sub_items_by_exp.get(exp_code, [])
        return exp_code, list(sub_list)

    def get_all_sub_items(self, total_headcount: int = 1) -> dict[str, list[dict]]:
        """현재 편집 중인 경비코드 테이블을 반영한 뒤, 경비코드별 세부 항목 dict 반환 (저장용).
        인적보험 7개(노무비에서 계산)는 제외하여 DB에 저장하지 않음."""
        self._total_headcount = max(int(total_headcount), 1)
        self._save_table_to_current_exp()
        return {
            k: v for k, v in self._sub_items_by_exp.items()
            if k not in EXP_CODES_FROM_LABOR
        }


def _labor_insurance_row(exp_code: str, exp_name: str, amount: int) -> dict:
    """노무비에서 계산된 인적보험 세부 1행 (UI 표시용)."""
    return {
        "exp_code": exp_code,
        "sub_code": exp_code,
        "sub_name": exp_name or exp_code,
        "spec": "",
        "unit": "원/월",
        "quantity": 1,
        "unit_price": amount,
        "amount": amount,
        "remark": "노무비에서 계산",
        "sort_order": 0,
        "is_active": 1,
    }


def build_sub_items_by_exp(
    repo,
    scenario_id: str,
    labor_insurance_by_exp_code: dict[str, int] | None = None,
    expense_items: list | None = None,
):
    """MasterDataRepo와 scenario_id로 exp_code별 세부 항목 dict 생성.
    labor_insurance_by_exp_code가 있으면 인적보험 7개에 대해 1행씩 자동 채움."""
    all_sub = repo.get_expense_sub_items(scenario_id)
    by_exp: dict[str, list] = {}
    for si in all_sub:
        by_exp.setdefault(si.exp_code, []).append(si)

    # labor_insurance_by_exp_code가 None이 아니면 보험 7종을 매핑 (빈 dict면 0원으로 반영)
    if labor_insurance_by_exp_code is not None and expense_items:
        item_map = {
            (i.get("exp_code") if isinstance(i, dict) else getattr(i, "exp_code", "")): (
                i.get("exp_name", "") if isinstance(i, dict) else getattr(i, "exp_name", "")
            )
            for i in expense_items
        }
        for exp_code in EXP_CODES_FROM_LABOR:
            amount = labor_insurance_by_exp_code.get(exp_code, 0) or 0
            by_exp[exp_code] = [
                _labor_insurance_row(exp_code, item_map.get(exp_code, exp_code), int(amount))
            ]
    return by_exp
