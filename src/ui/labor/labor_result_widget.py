from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame


class LaborResultWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout()

        self.labels = {
            "base_salary": QLabel(),
            "allowance": QLabel(),
            "bonus": QLabel(),
            "retirement": QLabel(),
            "total_labor_cost": QLabel(),
        }

        title = QLabel("노무비 요약")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)

        for label in self.labels.values():
            layout.addWidget(label)

        self.setLayout(layout)

    def update_result(self, result: dict):
        self.labels["base_salary"].setText(f"기본급: {result['base_salary']:,} 원")
        self.labels["allowance"].setText(f"제수당: {result['allowance']:,} 원")
        self.labels["bonus"].setText(f"상여금: {result['bonus']:,} 원")
        self.labels["retirement"].setText(f"퇴직충당금: {result['retirement']:,} 원")
        self.labels["total_labor_cost"].setText(
            f"노무비 합계: {result['total_labor_cost']:,} 원"
        )
