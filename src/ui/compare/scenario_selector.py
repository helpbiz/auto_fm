from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox

from src.domain.db import get_connection
from src.domain.scenario_input.service import list_scenario_ids, get_scenario_input


class ScenarioSelector(QWidget):
    """
    시나리오 선택 컴포넌트
    """

    def __init__(self, label: str):
        super().__init__()
        layout = QHBoxLayout(self)

        self.label = QLabel(label)
        self.combo = QComboBox()
        self.combo.setMinimumWidth(180)
        self.refresh_button = QPushButton("새로고침")
        self.load_button = QPushButton("불러오기")

        self.refresh_button.clicked.connect(self.refresh)
        self.load_button.clicked.connect(self._emit_load)

        layout.addWidget(self.label)
        layout.addWidget(self.combo)
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.load_button)

        self._on_load_callback = None
        self.refresh()

    def on_load(self, callback):
        self._on_load_callback = callback

    def refresh(self):
        self.combo.clear()
        conn = get_connection()
        try:
            for scenario_id in list_scenario_ids(conn):
                self.combo.addItem(scenario_id, scenario_id)
        finally:
            conn.close()

    def _emit_load(self):
        if self._on_load_callback is None:
            return
        scenario_id = self.combo.currentData()
        if not scenario_id:
            QMessageBox.information(self, "시나리오", "선택된 시나리오가 없습니다.")
            return
        self._on_load_callback(str(scenario_id))

    def load_scenario(self, scenario_id: str) -> dict:
        conn = get_connection()
        try:
            return {
                "scenario_id": scenario_id,
                "inputs": get_scenario_input(scenario_id, conn),
            }
        finally:
            conn.close()
