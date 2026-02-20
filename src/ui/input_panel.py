from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
)
from PyQt6.QtCore import pyqtSignal
import logging

from .theme import SECTION_TITLE_STYLE
from src.domain.db import get_connection
from src.domain.scenario_input.service import list_scenarios


class InputPanel(QWidget):
    """
    입력 패널: 시나리오명 + 시나리오 목록
    """

    # 시나리오 선택 시그널: 선택된 표시명(display_name) 전달 → 불러오기 시 동일 표시명으로 id 보정
    scenario_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 시나리오명
        title = QLabel("시나리오")
        title.setStyleSheet(SECTION_TITLE_STYLE)
        layout.addWidget(title)

        layout.addSpacing(8)

        self.scenario_name = QLineEdit("시나리오")
        layout.addWidget(QLabel("시나리오명"))
        layout.addWidget(self.scenario_name)

        layout.addSpacing(16)

        # 일반관리비율
        overhead_label = QLabel("일반관리비율(%)")
        layout.addWidget(overhead_label)
        self.overhead_rate = QLineEdit("10")
        layout.addWidget(self.overhead_rate)

        layout.addSpacing(8)

        # 이윤율
        profit_label = QLabel("이윤율(%)")
        layout.addWidget(profit_label)
        self.profit_rate = QLineEdit("10")
        layout.addWidget(self.profit_rate)

        layout.addSpacing(16)

        # 시나리오 목록
        list_title = QLabel("저장된 시나리오")
        list_title.setStyleSheet("font-weight: bold;")
        layout.addWidget(list_title)

        self.scenario_list = QListWidget()
        self.scenario_list.setMaximumHeight(200)
        # 더블클릭 또는 엔터키로 시나리오 로드
        self.scenario_list.itemActivated.connect(self._on_item_activated)
        layout.addWidget(self.scenario_list)

        # 선택 버튼
        button_layout = QHBoxLayout()

        self.select_button = QPushButton("선택")
        self.select_button.clicked.connect(self._on_select_clicked)
        self.select_button.setEnabled(False)

        self.refresh_button = QPushButton("새로고침")
        self.refresh_button.clicked.connect(self.refresh_scenario_list)

        button_layout.addWidget(self.select_button)
        button_layout.addWidget(self.refresh_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        layout.addStretch()

        # 선택 상태 추적
        self.scenario_list.itemSelectionChanged.connect(self._on_selection_changed)

        # 초기 목록 로드
        self.refresh_scenario_list()

    def get_values(self) -> dict:
        # 비숫자 입력 방지: 파싱 실패 시 기본값 사용
        try:
            overhead = float(self.overhead_rate.text() or "10")
        except ValueError:
            overhead = 10.0

        try:
            profit = float(self.profit_rate.text() or "10")
        except ValueError:
            profit = 10.0

        return {
            "scenario_name": self.scenario_name.text().strip(),
            "overhead_rate": overhead,
            "profit_rate": profit,
        }

    def set_values(self, values: dict) -> None:
        self.scenario_name.setText(values.get("scenario_name", ""))
        self.overhead_rate.setText(str(values.get("overhead_rate", 10)))
        self.profit_rate.setText(str(values.get("profit_rate", 10)))

    def on_change(self, callback) -> None:
        self.scenario_name.textChanged.connect(callback)
        self.overhead_rate.textChanged.connect(callback)
        self.profit_rate.textChanged.connect(callback)

    def refresh_scenario_list(self):
        """데이터베이스에서 시나리오 목록 불러오기 (표시명으로 표시, 저장된 _display_name 사용)"""
        self.scenario_list.clear()

        try:
            conn = get_connection()
            try:
                scenarios = list_scenarios(conn)
            finally:
                conn.close()

            # 목록에 표시명으로 추가 (불러오기 시 같은 표시명으로 id 보정됨)
            for scenario_id, display_name in scenarios:
                item = QListWidgetItem(display_name)
                self.scenario_list.addItem(item)

        except Exception as e:
            logging.exception("시나리오 목록 로드 실패")
            QMessageBox.warning(
                self,
                "오류",
                f"시나리오 목록을 불러오는 중 오류가 발생했습니다.\n{e}",
            )

    def _on_selection_changed(self):
        """선택 상태 변경 시 버튼 활성화/비활성화"""
        has_selection = len(self.scenario_list.selectedItems()) > 0
        self.select_button.setEnabled(has_selection)

    def _on_select_clicked(self):
        """선택 버튼 클릭 시 시나리오 로드"""
        selected_items = self.scenario_list.selectedItems()
        if not selected_items:
            return

        scenario_id = selected_items[0].text()
        self.scenario_selected.emit(scenario_id)

    def _on_item_activated(self, item: QListWidgetItem):
        """시나리오 더블클릭 또는 엔터키 시 바로 로드"""
        scenario_id = item.text()
        self.scenario_selected.emit(scenario_id)

    def get_selected_scenario(self) -> str | None:
        """현재 선택된 시나리오 ID 반환"""
        selected_items = self.scenario_list.selectedItems()
        if not selected_items:
            return None
        return selected_items[0].text()
