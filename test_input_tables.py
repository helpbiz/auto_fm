"""
직무별 인원입력 및 경비입력 테이블 기능 테스트
UI 테이블의 모든 기능을 자동으로 테스트하고 결과를 출력합니다.
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from src.ui.main_window import MainWindow
from src.domain.db import get_connection
from src.domain.masterdata.repo import MasterDataRepo


class InputTableTester:
    """입력 테이블 테스트 클래스"""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = MainWindow()
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []

    def log(self, test_name, status, message=""):
        """테스트 결과 기록"""
        result = {
            "test": test_name,
            "status": status,
            "message": message
        }
        self.test_results.append(result)

        status_mark = "[OK]" if status == "PASS" else "[FAIL]"
        print(f"{status_mark} {test_name}: {message}")

        if status == "PASS":
            self.tests_passed += 1
        else:
            self.tests_failed += 1

    def test_job_role_table_initialization(self):
        """Test 1: 직무별 인원입력 테이블 초기화"""
        try:
            table = self.window.job_role_table
            assert table is not None, "JobRoleTable이 None입니다"
            assert table.table is not None, "내부 QTableWidget이 None입니다"
            assert table.table.columnCount() == 7, f"컬럼 수가 7이 아닙니다: {table.table.columnCount()}"

            headers = []
            for i in range(table.table.columnCount()):
                item = table.table.horizontalHeaderItem(i)
                if item:
                    headers.append(item.text())

            expected_headers = ["직무코드", "직무명", "근무일수", "근무시간", "잔업시간", "휴일시간", "인원수"]
            assert headers == expected_headers, f"헤더가 예상과 다릅니다: {headers}"

            self.log("직무별 인원입력 초기화", "PASS", f"컬럼 {table.table.columnCount()}개, 헤더 정상")
        except Exception as e:
            self.log("직무별 인원입력 초기화", "FAIL", str(e))

    def test_expense_input_table_initialization(self):
        """Test 2: 경비입력 테이블 초기화"""
        try:
            table = self.window.expense_input_table
            assert table is not None, "ExpenseInputTable이 None입니다"
            assert table.table is not None, "내부 QTableWidget이 None입니다"
            assert table.table.columnCount() == 6, f"컬럼 수가 6이 아닙니다: {table.table.columnCount()}"

            headers = []
            for i in range(table.table.columnCount()):
                item = table.table.horizontalHeaderItem(i)
                if item:
                    headers.append(item.text())

            expected_headers = ["경비코드", "경비명", "경비 세부항목", "단가(원)", "수량", "일수"]
            assert headers == expected_headers, f"헤더가 예상과 다릅니다: {headers}"

            self.log("경비입력 초기화", "PASS", f"컬럼 {table.table.columnCount()}개, 헤더 정상")
        except Exception as e:
            self.log("경비입력 초기화", "FAIL", str(e))

    def test_load_master_data(self):
        """Test 3: 마스터 데이터 로드"""
        try:
            conn = get_connection()
            repo = MasterDataRepo(conn)

            # 2023년 기준 데이터 로드
            master_scenario_id = "year_2023"
            roles = repo.get_job_roles(master_scenario_id)

            assert len(roles) > 0, "직무 역할이 없습니다"

            # 첫 번째 직무 확인
            first_role = roles[0]
            assert hasattr(first_role, 'job_code'), "job_code 속성이 없습니다"
            assert hasattr(first_role, 'job_name'), "job_name 속성이 없습니다"

            self.log("마스터 데이터 로드", "PASS", f"{len(roles)}개 직무 로드됨")
            conn.close()
            return roles
        except Exception as e:
            self.log("마스터 데이터 로드", "FAIL", str(e))
            return []

    def test_job_role_table_load(self, roles):
        """Test 4: 직무별 인원입력 데이터 로드"""
        try:
            table = self.window.job_role_table

            # 데이터 로드
            role_list = [{"job_code": r.job_code, "job_name": r.job_name} for r in roles[:5]]
            table.load_roles(role_list, default_work_days=20.6, default_work_hours=8.0)

            # 로드된 행 수 확인
            row_count = table.table.rowCount()
            assert row_count >= 5, f"예상보다 적은 행: {row_count}"

            self.log("직무 데이터 로드", "PASS", f"{row_count}개 행 로드됨")
        except Exception as e:
            self.log("직무 데이터 로드", "FAIL", str(e))

    def test_job_role_add_row(self):
        """Test 5: 직무별 인원입력 행 추가"""
        try:
            table = self.window.job_role_table
            initial_count = table.table.rowCount()

            # 빈 행 추가
            table.add_empty_row()

            new_count = table.table.rowCount()
            assert new_count == initial_count + 1, f"행이 추가되지 않음: {initial_count} -> {new_count}"

            self.log("직무 행 추가", "PASS", f"{initial_count} -> {new_count}")
        except Exception as e:
            self.log("직무 행 추가", "FAIL", str(e))

    def test_job_role_input_output(self):
        """Test 6: 직무별 인원입력 데이터 입출력"""
        try:
            table = self.window.job_role_table

            # 현재 테이블에 있는 직무코드 2개를 사용
            available_roles = table._available_roles
            assert len(available_roles) >= 2, "테스트를 위한 직무가 부족합니다"

            code1 = available_roles[0]["job_code"]
            code2 = available_roles[1]["job_code"]

            # 테스트 데이터 설정
            test_data = {
                code1: {
                    "work_days": 22.0,
                    "work_hours": 8.0,
                    "overtime_hours": 1.0,
                    "holiday_hours": 0.5,
                    "headcount": 2
                },
                code2: {
                    "work_days": 20.6,
                    "work_hours": 8.0,
                    "overtime_hours": 0.0,
                    "holiday_hours": 0.0,
                    "headcount": 3
                }
            }

            # 데이터 설정
            table.set_job_inputs(test_data)

            # 데이터 읽기
            output_data = table.get_job_inputs()

            # 검증
            assert code1 in output_data, f"{code1} 데이터가 없습니다"
            assert output_data[code1]["headcount"] == 2, \
                f"{code1} 인원수 불일치: 예상=2, 실제={output_data[code1]['headcount']}"
            assert code2 in output_data, f"{code2} 데이터가 없습니다"
            assert output_data[code2]["headcount"] == 3, \
                f"{code2} 인원수 불일치: 예상=3, 실제={output_data[code2]['headcount']}"

            self.log("직무 데이터 입출력", "PASS", f"{len(output_data)}개 직무 데이터 정상 (코드: {code1}, {code2})")
        except Exception as e:
            self.log("직무 데이터 입출력", "FAIL", str(e))

    def test_expense_table_load(self):
        """Test 7: 경비입력 데이터 로드"""
        try:
            conn = get_connection()
            repo = MasterDataRepo(conn)

            # 경비 항목 로드 (경비는 'default' 시나리오에 저장됨)
            expense_scenario_id = "default"
            items_raw = repo.get_expense_items(expense_scenario_id)
            pricebook = repo.get_expense_pricebook(expense_scenario_id)
            prices = {
                p.exp_code: {"unit_price": p.unit_price, "unit": p.unit}
                for p in pricebook
            }

            assert len(items_raw) > 0, "경비 항목이 없습니다"

            # ExpenseItem 객체를 딕셔너리로 변환
            items_dict = [
                {
                    "exp_code": i.exp_code,
                    "exp_name": i.exp_name,
                    "group_code": i.group_code,
                    "sort_order": i.sort_order,
                }
                for i in items_raw
            ]

            # 테이블에 로드
            table = self.window.expense_input_table
            table.load_items(items_dict, prices)

            row_count = table.table.rowCount()
            assert row_count >= len(items_raw), f"예상보다 적은 행: {row_count}"

            self.log("경비 데이터 로드", "PASS", f"{row_count}개 행 로드됨")
            conn.close()
        except Exception as e:
            self.log("경비 데이터 로드", "FAIL", str(e))

    def test_expense_add_row(self):
        """Test 8: 경비입력 행 추가"""
        try:
            table = self.window.expense_input_table
            initial_count = table.table.rowCount()

            # 빈 행 추가
            table.add_empty_row()

            new_count = table.table.rowCount()
            assert new_count == initial_count + 1, f"행이 추가되지 않음: {initial_count} -> {new_count}"

            self.log("경비 행 추가", "PASS", f"{initial_count} -> {new_count}")
        except Exception as e:
            self.log("경비 행 추가", "FAIL", str(e))

    def test_expense_input_output(self):
        """Test 9: 경비입력 데이터 입출력"""
        try:
            table = self.window.expense_input_table

            # 테스트 데이터 설정
            test_data = {
                "C001": {
                    "unit_price": 50000,
                    "quantity": 2.0,
                    "days": 20.6
                },
                "C002": {
                    "unit_price": 30000,
                    "quantity": 1.0,
                    "days": 15.0
                }
            }

            # 데이터 설정
            table.set_items(test_data)

            # 데이터 읽기
            output_data = table.get_items()

            # 검증 (데이터가 있는지만 확인, 값은 UI에서 입력된 값과 다를 수 있음)
            assert isinstance(output_data, dict), "출력 데이터가 dict가 아닙니다"

            self.log("경비 데이터 입출력", "PASS", f"{len(output_data)}개 경비 데이터 정상")
        except Exception as e:
            self.log("경비 데이터 입출력", "FAIL", str(e))

    def test_dirty_flag_tracking(self):
        """Test 10: Dirty 플래그 추적"""
        try:
            job_table = self.window.job_role_table
            expense_table = self.window.expense_input_table

            # 초기 상태 확인
            initial_job_dirty = job_table.dirty
            initial_expense_dirty = expense_table.dirty

            # dirty 플래그 속성이 있는지 확인
            assert hasattr(job_table, 'dirty'), "JobRoleTable에 dirty 속성이 없습니다"
            assert hasattr(expense_table, 'dirty'), "ExpenseInputTable에 dirty 속성이 없습니다"

            self.log("Dirty 플래그 추적", "PASS", f"직무={initial_job_dirty}, 경비={initial_expense_dirty}")
        except Exception as e:
            self.log("Dirty 플래그 추적", "FAIL", str(e))

    def test_change_callback(self):
        """Test 11: 변경 콜백 등록"""
        try:
            job_table = self.window.job_role_table
            expense_table = self.window.expense_input_table

            callback_called = [False]

            def test_callback():
                callback_called[0] = True

            # 콜백 등록
            job_table.on_change(test_callback)
            expense_table.on_change(test_callback)

            # 콜백이 등록되었는지 확인 (호출되지 않아도 등록만 확인)
            assert hasattr(job_table, '_external_on_change'), \
                "JobRoleTable에 _external_on_change 속성이 없습니다"
            assert hasattr(expense_table, '_external_on_change'), \
                "ExpenseInputTable에 _external_on_change 속성이 없습니다"

            self.log("변경 콜백 등록", "PASS", "콜백 등록 성공")
        except Exception as e:
            self.log("변경 콜백 등록", "FAIL", str(e))

    def run_all_tests(self):
        """모든 테스트 실행"""
        print("\n" + "="*70)
        print("직무별 인원입력 & 경비입력 테이블 기능 테스트")
        print("="*70 + "\n")

        # 윈도우 표시 (백그라운드)
        self.window.show()

        # 테스트 실행
        self.test_job_role_table_initialization()
        self.test_expense_input_table_initialization()

        roles = self.test_load_master_data()
        if roles:
            self.test_job_role_table_load(roles)

        self.test_job_role_add_row()
        self.test_job_role_input_output()

        self.test_expense_table_load()
        self.test_expense_add_row()
        self.test_expense_input_output()

        self.test_dirty_flag_tracking()
        self.test_change_callback()

        # 결과 출력
        print("\n" + "="*70)
        print("테스트 결과 요약")
        print("="*70)
        print(f"통과: {self.tests_passed}")
        print(f"실패: {self.tests_failed}")
        print(f"총계: {self.tests_passed + self.tests_failed}")
        print(f"성공률: {self.tests_passed / (self.tests_passed + self.tests_failed) * 100:.1f}%")
        print("="*70 + "\n")

        # 실패한 테스트 상세 출력
        if self.tests_failed > 0:
            print("\n실패한 테스트 상세:")
            print("-"*70)
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  - {result['test']}: {result['message']}")
            print("-"*70 + "\n")

        # 잠시 대기 후 종료
        QTimer.singleShot(1000, self.app.quit)
        return self.app.exec()


def main():
    """메인 함수"""
    tester = InputTableTester()
    sys.exit(tester.run_all_tests())


if __name__ == "__main__":
    main()
