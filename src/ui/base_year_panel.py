"""기준년도 입력 패널: 적용 연도·노임단가 기준년도/반기를 선택하는 탭."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
    QFrame, QFormLayout, QComboBox,
)
from PyQt6.QtCore import Qt, QDate

from .theme import SECTION_TITLE_STYLE, CARD_STYLE


class BaseYearPanel(QWidget):
    """기준년도 입력 패널 (기준 연도, 노임단가 기준년도/반기)."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        title = QLabel("기준년도")
        title.setStyleSheet(SECTION_TITLE_STYLE)
        layout.addWidget(title)

        # 카드 프레임
        frame = QFrame()
        frame.setStyleSheet(CARD_STYLE)
        form = QFormLayout(frame)

        today = QDate.currentDate()

        # 기준 연도
        self.year_spin = QSpinBox()
        self.year_spin.setRange(2020, 2040)
        self.year_spin.setValue(today.year())
        form.addRow("기준 연도", self.year_spin)

        # 노임단가 기준년도
        self.wage_year_spin = QSpinBox()
        self.wage_year_spin.setRange(2020, 2040)
        self.wage_year_spin.setValue(today.year())
        form.addRow("노임단가 기준년도", self.wage_year_spin)

        # 노임단가 반기
        self.wage_half = QComboBox()
        self.wage_half.addItems(["상반기", "하반기"])
        if today.month() > 6:
            self.wage_half.setCurrentIndex(1)
        form.addRow("노임단가 반기", self.wage_half)

        layout.addWidget(frame)
        layout.addStretch()

    def get_values(self) -> dict:
        return {
            "base_year": self.year_spin.value(),
            "wage_year": self.wage_year_spin.value(),
            "wage_half": self.wage_half.currentText(),
        }

    def set_values(self, values: dict) -> None:
        if "base_year" in values:
            self.year_spin.setValue(values["base_year"])
        if "wage_year" in values:
            self.wage_year_spin.setValue(values["wage_year"])
        if "wage_half" in values:
            idx = self.wage_half.findText(values["wage_half"])
            if idx >= 0:
                self.wage_half.setCurrentIndex(idx)

    def on_change(self, callback) -> None:
        self.year_spin.valueChanged.connect(lambda _: callback())
        self.wage_year_spin.valueChanged.connect(lambda _: callback())
        self.wage_half.currentTextChanged.connect(lambda _: callback())
