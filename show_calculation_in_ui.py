"""
UI에 노무비 계산 결과를 표시하는 예제
"""
import sys
from decimal import Decimal

# PyQt6 임포트
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QTableWidget, QTableWidgetItem, QPushButton
from PyQt6.QtCore import Qt

# 계산 로직 임포트
from src.domain.context.calc_context import CalcContext
from src.domain.calculator.labor import LaborCostCalculator


def create_sample_calculation():
    """샘플 노무비 계산"""

    # 계산 컨텍스트 생성 (소장 1명)
    context = CalcContext(
        manpower={"소장": 1},
        wage_rate={"소장": Decimal("400000")},
        monthly_workdays=Decimal("20.6"),
        daily_work_hours=Decimal("8"),
        weekly_holiday_days=Decimal("4.345"),
        annual_leave_days=Decimal("1.25"),
        overtime_hours=Decimal("0"),
        holiday_work_hours=Decimal("0"),
    )

    # 노무비 계산기
    calculator = LaborCostCalculator(context)
    result = calculator.calculate()

    return result


class LaborCalculationWindow(QMainWindow):
    """노무비 계산 결과 표시 창"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("노무비 상세 계산 결과")
        self.setGeometry(100, 100, 900, 700)

        # 메인 위젯
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # 제목
        title = QLabel("노무비 상세 계산 결과")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # 기본 정보
        info_label = QLabel("직무: 소장 | 인원: 1명 | 일급: 400,000원 | 월 근무일수: 20.6일")
        info_label.setStyleSheet("padding: 5px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(info_label)

        # 계산 버튼
        calc_button = QPushButton("계산 실행")
        calc_button.clicked.connect(self.show_calculation)
        calc_button.setStyleSheet("padding: 10px; font-size: 14px; background-color: #4CAF50; color: white;")
        layout.addWidget(calc_button)

        # 결과 테이블
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(2)
        self.result_table.setHorizontalHeaderLabels(["항목", "금액"])
        self.result_table.horizontalHeader().setStretchLastSection(True)
        self.result_table.setAlternatingRowColors(True)
        layout.addWidget(self.result_table)

        # 총 노무비 라벨
        self.total_label = QLabel()
        self.total_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px; background-color: #e3f2fd; border-radius: 5px;")
        layout.addWidget(self.total_label)

    def show_calculation(self):
        """계산 결과를 테이블에 표시"""
        # 계산 실행
        result = create_sample_calculation()

        # 표시할 데이터
        data = [
            ("1. 기본급(월)", result["base_salary"]),
            ("   - 일급 합계 × 월 근무일수", f"{400000:,}원 × 20.6일"),
            ("", ""),
            ("2. 상여금(월)", result["bonus"]),
            ("   - 기본급 × 400% ÷ 12", ""),
            ("", ""),
            ("3. 제수당 합계", result["allowance"]),
            ("   - 주휴수당", result["weekly_allowance"]),
            ("   - 연차수당", result["annual_leave_allowance"]),
            ("   - 연장수당", result["allowances"]["overtime_pay"]),
            ("   - 휴일근로수당", result["allowances"]["holiday_work_pay"]),
            ("", ""),
            ("4. 퇴직급여충당금(월)", result["retirement"]),
            ("   - (기본급 + 제수당 + 상여금) ÷ 12", ""),
            ("", ""),
            ("━━━━━━━━━━━━━━━━━━━━", "━━━━━━━━━━━━━━"),
            ("5. 인건비 소계", result["labor_subtotal"]),
            ("━━━━━━━━━━━━━━━━━━━━", "━━━━━━━━━━━━━━"),
            ("", ""),
            ("6. 4대보험 및 기타", ""),
            ("   - 산재보험", result["industrial_accident"]),
            ("   - 국민연금", result["national_pension"]),
            ("   - 고용보험", result["employment_insurance"]),
            ("   - 건강보험", result["health_insurance"]),
            ("   - 장기요양보험", result["long_term_care"]),
            ("   - 임금채권보장", result["wage_bond"]),
            ("   - 석면피해구제", result["asbestos_relief"]),
            ("━━━━━━━━━━━━━━━━━━━━", "━━━━━━━━━━━━━━"),
            ("7. 보험료 합계", result["insurance_total"]),
            ("━━━━━━━━━━━━━━━━━━━━", "━━━━━━━━━━━━━━"),
        ]

        # 테이블 업데이트
        self.result_table.setRowCount(len(data))

        for row, (item, value) in enumerate(data):
            item_cell = QTableWidgetItem(item)

            if isinstance(value, int):
                value_cell = QTableWidgetItem(f"{value:,}원")
                value_cell.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            elif isinstance(value, str):
                value_cell = QTableWidgetItem(value)
            else:
                value_cell = QTableWidgetItem("")

            # 구분선 스타일
            if "━━━" in item:
                item_cell.setBackground(Qt.GlobalColor.lightGray)
                value_cell.setBackground(Qt.GlobalColor.lightGray)

            # 소계/합계 강조
            if any(x in item for x in ["소계", "합계", "총 노무비"]):
                font = item_cell.font()
                font.setBold(True)
                item_cell.setFont(font)
                value_cell.setFont(font)

            self.result_table.setItem(row, 0, item_cell)
            self.result_table.setItem(row, 1, value_cell)

        # 총 노무비 표시
        total = result["total_labor_cost"]
        self.total_label.setText(f"💰 총 노무비: {total:,}원")

        # 열 너비 조정
        self.result_table.resizeColumnToContents(0)


def main():
    """메인 함수"""
    app = QApplication(sys.argv)

    # 윈도우 생성 및 표시
    window = LaborCalculationWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
