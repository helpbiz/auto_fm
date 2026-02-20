"""
종합 UI 테스트 스크립트
모든 UI 요소, 탭, 버튼을 체계적으로 테스트
"""
import sys
import logging
from pathlib import Path

# PyQt6 임포트
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer
except ImportError:
    print("[FAIL] PyQt6가 설치되지 않았습니다.")
    sys.exit(1)

from src.domain.db import get_connection
from src.domain.scenario_input.service import post_scenario_input
from src.domain.wage_manager import WageManager
from src.ui.main_window import MainWindow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UITester:
    """UI 종합 테스트"""

    def __init__(self, window: MainWindow):
        self.window = window
        self.tests_passed = 0
        self.tests_failed = 0
        self.wage_year = 2025

    def run_all_tests(self):
        """모든 테스트 실행"""
        print("\n" + "="*60)
        print("UI 종합 테스트 시작")
        print("="*60 + "\n")

        # 1. UI 컴포넌트 초기화 테스트
        self.test_ui_initialization()

        # 2. 입력 패널 테스트
        self.test_input_panel()

        # 3. 데이터 입력 및 계산 테스트
        self.test_data_input_and_calculation()

        # 4. 탭 전환 테스트
        self.test_tab_switching()

        # 5. 결과 표시 테스트
        self.test_result_display()

        # 6. 버튼 기능 테스트
        self.test_button_functions()

        # 결과 출력
        print("\n" + "="*60)
        print(f"테스트 결과: {self.tests_passed} 성공, {self.tests_failed} 실패")
        print("="*60 + "\n")

        # 3초 후 종료
        QTimer.singleShot(3000, QApplication.quit)

    def assert_true(self, condition, message):
        """조건 검증"""
        if condition:
            print(f"[OK] {message}")
            self.tests_passed += 1
        else:
            print(f"[FAIL] {message}")
            self.tests_failed += 1

    def assert_not_none(self, obj, message):
        """객체 존재 검증"""
        self.assert_true(obj is not None, message)

    def test_ui_initialization(self):
        """UI 컴포넌트 초기화 테스트"""
        print("\n[1] UI 컴포넌트 초기화 테스트")
        print("-" * 60)

        # 메인 윈도우
        self.assert_not_none(self.window, "메인 윈도우 생성")
        self.assert_true(self.window.isVisible(), "메인 윈도우 표시")

        # 입력 패널
        self.assert_not_none(self.window.input_panel, "입력 패널 생성")
        self.assert_not_none(self.window.input_panel.scenario_name, "시나리오명 입력 필드")
        self.assert_not_none(self.window.input_panel.year_combo, "연도 선택 콤보박스")

        # 테이블
        self.assert_not_none(self.window.job_role_table, "직무 입력 테이블 생성")
        self.assert_not_none(self.window.expense_input_table, "경비 입력 테이블 생성")

        # 결과 패널
        self.assert_not_none(self.window.summary_panel, "요약 패널 생성")
        self.assert_not_none(self.window.labor_detail, "노무비 상세 테이블 생성")
        self.assert_not_none(self.window.expense_detail, "경비 상세 테이블 생성")

        # 탭
        self.assert_not_none(self.window.tabs, "탭 위젯 생성")
        self.assert_true(self.window.tabs.count() == 4, "탭 개수 확인 (4개)")

        # 버튼
        self.assert_not_none(self.window.calculate_button, "집계 실행 버튼")
        self.assert_not_none(self.window.save_button, "시나리오 저장 버튼")
        self.assert_not_none(self.window.load_button, "시나리오 불러오기 버튼")
        self.assert_not_none(self.window.export_json_button, "시나리오 JSON 저장 버튼")
        self.assert_not_none(self.window.export_pdf_button, "요약 PDF 내보내기 버튼")
        self.assert_not_none(self.window.export_excel_button, "상세 Excel 내보내기 버튼")

    def test_input_panel(self):
        """입력 패널 테스트"""
        print("\n[2] 입력 패널 테스트")
        print("-" * 60)

        # 시나리오명 설정
        test_scenario_name = "UI_테스트_시나리오"
        self.window.input_panel.scenario_name.setText(test_scenario_name)
        actual_name = self.window.input_panel.scenario_name.text()
        self.assert_true(
            actual_name == test_scenario_name,
            f"시나리오명 설정 ({actual_name})"
        )

        # 연도 선택
        year_count = self.window.input_panel.year_combo.count()
        self.assert_true(year_count > 0, f"연도 목록 로드 ({year_count}개)")

        # 일반관리비율, 이윤율 확인
        overhead = self.window.input_panel.overhead_rate.text()
        profit = self.window.input_panel.profit_rate.text()
        self.assert_not_none(overhead, f"일반관리비율 설정 ({overhead}%)")
        self.assert_not_none(profit, f"이윤율 설정 ({profit}%)")

    def test_data_input_and_calculation(self):
        """데이터 입력 및 계산 테스트"""
        print("\n[3] 데이터 입력 및 계산 테스트")
        print("-" * 60)

        # 테스트 데이터 저장
        scenario_id = "ui_test"
        test_input = {
            "labor": {
                "job_roles": {
                    "M101": {
                        "headcount": 1.0,
                        "work_days": 20.6,
                        "work_hours": 8.0,
                        "overtime_hours": 0.0,
                        "holiday_work_hours": 0.0
                    }
                }
            },
            "expenses": {"items": {}},
            "overhead_rate": 0.1,
            "profit_rate": 0.1
        }

        conn = get_connection()
        try:
            post_scenario_input(test_input, scenario_id, conn)
            print("[OK] 테스트 데이터 저장 완료")

            # 계산 실행
            from src.domain.result.service import calculate_result
            wage_manager = WageManager()
            result = calculate_result(
                scenario_id,
                conn,
                wage_year=self.wage_year,
                wage_manager=wage_manager
            )

            # 결과 검증
            agg = result["aggregator"]
            labor_rows = result["labor_rows"]

            self.assert_true(
                agg.labor_total > 0,
                f"노무비 계산 성공 ({agg.labor_total:,}원)"
            )
            self.assert_true(
                len(labor_rows) > 0,
                f"노무비 상세 데이터 생성 ({len(labor_rows)}개)"
            )
            self.assert_true(
                agg.grand_total > 0,
                f"총계 계산 성공 ({agg.grand_total:,}원)"
            )

            # UI에 결과 반영
            self.window.last_aggregator = agg
            self.window.last_labor_rows = labor_rows
            self.window.last_expense_rows = result["expense_rows"]

        finally:
            conn.close()

    def test_tab_switching(self):
        """탭 전환 테스트"""
        print("\n[4] 탭 전환 테스트")
        print("-" * 60)

        tab_names = [
            "요약",
            "노무비 상세",
            "경비 상세",
            "시나리오 비교"
        ]

        for i, name in enumerate(tab_names):
            self.window.tabs.setCurrentIndex(i)
            current_index = self.window.tabs.currentIndex()
            self.assert_true(
                current_index == i,
                f"{name} 탭 전환 (인덱스: {i})"
            )

    def test_result_display(self):
        """결과 표시 테스트"""
        print("\n[5] 결과 표시 테스트")
        print("-" * 60)

        if self.window.last_aggregator is None:
            print("[SKIP] 계산 결과 없음")
            return

        # 요약 패널 업데이트
        agg = self.window.last_aggregator
        labor_rows = self.window.last_labor_rows or []
        total_headcount = sum(int(r.get("headcount", 0)) for r in labor_rows)

        self.window.summary_panel.update_summary(
            agg,
            pdf_grand_total=0,
            total_headcount=total_headcount
        )

        # 요약 패널 검증
        labor_label = self.window.summary_panel.labels.get("labor_total")
        if labor_label:
            self.assert_true(
                labor_label.text() != "0",
                f"요약 패널 노무비 표시 ({labor_label.text()})"
            )

        grand_label = self.window.summary_panel.labels.get("grand_total")
        if grand_label:
            self.assert_true(
                grand_label.text() != "0",
                f"요약 패널 총계 표시 ({grand_label.text()})"
            )

        # 노무비 상세 업데이트
        self.window.labor_detail.update_rows(labor_rows)
        labor_row_count = self.window.labor_detail.table.rowCount()
        self.assert_true(
            labor_row_count > 0,
            f"노무비 상세 테이블 행 수 ({labor_row_count}개)"
        )

        # 경비 상세 업데이트
        expense_rows = self.window.last_expense_rows or []
        self.window.expense_detail.update_rows(expense_rows)
        print(f"[OK] 경비 상세 테이블 업데이트 ({len(expense_rows)}개)")

    def test_button_functions(self):
        """버튼 기능 테스트"""
        print("\n[6] 버튼 기능 테스트")
        print("-" * 60)

        # 버튼 활성화 상태 확인
        buttons = [
            ("집계 실행", self.window.calculate_button),
            ("시나리오 저장", self.window.save_button),
            ("시나리오 불러오기", self.window.load_button),
            ("시나리오 JSON 저장", self.window.export_json_button),
            ("요약 PDF 내보내기", self.window.export_pdf_button),
            ("상세 Excel 내보내기", self.window.export_excel_button),
        ]

        for name, button in buttons:
            if button:
                # 버튼이 존재하고 표시되는지 확인
                self.assert_true(
                    button.isVisible(),
                    f"{name} 버튼 표시"
                )
                print(f"  - 활성화: {button.isEnabled()}")


def main():
    """메인 함수"""
    app = QApplication(sys.argv)

    # 메인 윈도우 생성 및 표시
    window = MainWindow()
    window.resize(1200, 700)
    window.show()

    # 테스터 생성 및 실행
    tester = UITester(window)

    # UI가 완전히 로드된 후 테스트 실행
    QTimer.singleShot(500, tester.run_all_tests)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
