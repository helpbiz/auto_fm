from PyQt6.QtWidgets import QWidget, QFormLayout, QLineEdit, QLabel


class InputPanel(QWidget):
    """
    최소 입력 패널 (계산 로직 없음)
    """

    def __init__(self):
        super().__init__()
        layout = QFormLayout(self)

        title = QLabel("입력값")
        title.setStyleSheet("font-weight: bold;")
        layout.addRow(title)

        self.scenario_name = QLineEdit("시나리오")
        layout.addRow("시나리오명", self.scenario_name)

    def get_values(self) -> dict:
        return {
            "scenario_name": self.scenario_name.text().strip(),
        }

    def set_values(self, values: dict) -> None:
        self.scenario_name.setText(values.get("scenario_name", ""))
 
    def on_change(self, callback) -> None:
        self.scenario_name.textChanged.connect(callback)
