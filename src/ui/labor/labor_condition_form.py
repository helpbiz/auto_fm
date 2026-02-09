from PyQt6.QtWidgets import QWidget, QFormLayout, QLineEdit
from decimal import Decimal


class LaborConditionForm(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout()

        self.monthly_workdays = QLineEdit("20.6")
        self.daily_work_hours = QLineEdit("8")
        self.weekly_holiday_days = QLineEdit("4.33")
        self.annual_leave_days = QLineEdit("1.25")

        layout.addRow("월 근무일수", self.monthly_workdays)
        layout.addRow("1일 근무시간", self.daily_work_hours)
        layout.addRow("주휴일수(월)", self.weekly_holiday_days)
        layout.addRow("연차일수(월)", self.annual_leave_days)

        self.setLayout(layout)

    def get_data(self):
        return {
            "monthly_workdays": Decimal(self.monthly_workdays.text()),
            "daily_work_hours": Decimal(self.daily_work_hours.text()),
            "weekly_holiday_days": Decimal(self.weekly_holiday_days.text()),
            "annual_leave_days": Decimal(self.annual_leave_days.text()),
        }
