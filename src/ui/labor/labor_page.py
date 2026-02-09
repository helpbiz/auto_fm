from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton

from src.domain.context.calc_context import CalcContext
from src.domain.calculator.labor import LaborCostCalculator
from .labor_result_widget import LaborResultWidget
from .labor_input_table import LaborInputTable
from .labor_condition_form import LaborConditionForm


class LaborPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.condition_form = LaborConditionForm()
        self.input_table = LaborInputTable()
        self.result_widget = LaborResultWidget()
        self.calculate_button = QPushButton("노무비 계산")

        self.calculate_button.clicked.connect(self.calculate)

        top_row = QHBoxLayout()
        top_row.addWidget(self.condition_form)
        top_row.addWidget(self.input_table)

        layout.addLayout(top_row)
        layout.addWidget(self.calculate_button)
        layout.addWidget(self.result_widget)

        self.setLayout(layout)

    def calculate(self):
        manpower, wage_rate = self.input_table.get_data()
        cond = self.condition_form.get_data()

        context = CalcContext(
            project_name="자동집하시설",
            year=2025,
            manpower=manpower,
            wage_rate=wage_rate,
            monthly_workdays=cond["monthly_workdays"],
            daily_work_hours=cond["daily_work_hours"],
            weekly_holiday_days=cond["weekly_holiday_days"],
            annual_leave_days=cond["annual_leave_days"],
            expenses={},
        )

        result = LaborCostCalculator(context).calculate()
        self.result_widget.update_result(result)

