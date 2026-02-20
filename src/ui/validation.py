# src/ui/validation.py
"""
숫자 입력 필드 유효성 검사: 문자/음수 입력 시 테마 오류 색 테두리 + 툴팁.
"""
import re

from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import QLineEdit, QTableWidgetItem
from PyQt6.QtCore import Qt

from .theme import STYLE_INVALID, STYLE_VALID, COLOR_VALIDATION_ERROR_BG


TOOLTIP_INVALID = "숫자만 입력 가능합니다"


def is_valid_non_negative_number(text: str, allow_float: bool = True) -> bool:
    """비어 있거나, 0 이상의 숫자(정수/실수)면 True."""
    if not (text or "").strip():
        return True
    try:
        cleaned = re.sub(r"[^0-9.\-]", "", text.strip().replace(",", "."))
        if not cleaned:
            return False
        v = float(cleaned)
        return v >= 0
    except (ValueError, TypeError):
        return False


def apply_line_edit_validation(edit: QLineEdit, allow_float: bool = True) -> None:
    """QLineEdit에 textChanged 시 숫자(0 이상) 검사, 잘못되면 붉은 테두리 + 툴팁."""

    def check():
        t = edit.text()
        if is_valid_non_negative_number(t, allow_float):
            edit.setStyleSheet(STYLE_VALID)
            edit.setToolTip("")
        else:
            edit.setStyleSheet(STYLE_INVALID)
            edit.setToolTip(TOOLTIP_INVALID)

    edit.textChanged.connect(check)
    check()


def apply_table_cell_validation(item: QTableWidgetItem, allow_float: bool = True) -> None:
    """테이블 셀 아이템의 텍스트가 유효하면 배경/툴팁 제거, 아니면 붉은 배경 + 툴팁."""
    if item is None:
        return
    t = item.text() if item.text() else ""
    if is_valid_non_negative_number(t, allow_float):
        item.setBackground(QBrush(Qt.GlobalColor.white))
        item.setToolTip("")
    else:
        item.setBackground(QBrush(QColor(COLOR_VALIDATION_ERROR_BG)))
        item.setToolTip(TOOLTIP_INVALID)
