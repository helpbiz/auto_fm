"""
인원 산정과 노무비 상세 계산 테스트 스크립트
"""
import sys
from decimal import Decimal
from src.domain.db import get_connection
from src.domain.result.service import calculate_result, calculate_result_live
from src.domain.scenario_input.service import post_scenario_input
from src.domain.wage_manager import WageManager

def test_calculation():
    print("=== 노무비 계산 테스트 ===\n")

    conn = get_connection()
    wage_manager = WageManager()
    wage_year = 2025

    # 테스트 시나리오 생성
    scenario_id = "test_scenario"
    test_input = {
        "labor": {
            "job_roles": {
                "M101": {  # 소장
                    "headcount": 1.0,
                    "work_days": 20.6,
                    "work_hours": 8.0,
                    "overtime_hours": 0.0,
                    "holiday_work_hours": 0.0
                },
                "E501": {  # 환경원
                    "headcount": 2.0,
                    "work_days": 20.6,
                    "work_hours": 8.0,
                    "overtime_hours": 0.0,
                    "holiday_work_hours": 0.0
                }
            }
        },
        "expenses": {
            "items": {}
        },
        "overhead_rate": 0.1,
        "profit_rate": 0.1
    }

    print(f"1. 시나리오 저장: {scenario_id}")
    print(f"   - M101(소장): 인원 1명")
    print(f"   - E501(환경원): 인원 2명")
    print()

    # 시나리오 저장
    post_scenario_input(test_input, scenario_id, conn)
    print("[OK] 시나리오 저장 완료\n")

    # 계산 실행
    print(f"2. 계산 실행 (연도: {wage_year})")
    result = calculate_result(
        scenario_id,
        conn,
        wage_year=wage_year,
        wage_manager=wage_manager
    )

    print("\n=== 계산 결과 ===\n")

    # 집계 결과
    agg = result["aggregator"]
    print(f"노무비 합계: {agg.labor_total:,}원")
    print(f"경비 합계: {agg.fixed_expense_total:,}원")
    print(f"일반관리비: {agg.overhead_cost:,}원")
    print(f"이윤: {agg.profit:,}원")
    print(f"총계: {agg.grand_total:,}원")
    print()

    # 노무비 상세
    print("=== 노무비 상세 ===\n")
    labor_rows = result["labor_rows"]
    print(f"총 {len(labor_rows)}개 직무:")
    for row in labor_rows:
        print(f"\n직무: {row['role']} ({row['job_code']})")
        print(f"  인원: {row['headcount']}명")
        print(f"  기본급: {row['base_salary']:,}원")
        print(f"  상여금: {row.get('bonus', 0):,}원")
        print(f"  제수당: {row['allowances']:,}원")
        print(f"  퇴직급여: {row.get('retirement', 0):,}원")
        print(f"  인건비 소계: {row['labor_subtotal']:,}원")
        print(f"  산재보험: {row.get('industrial_accident', 0):,}원")
        print(f"  보험료 합계: {row['insurance_total']:,}원")
        print(f"  노무비 합계: {row['role_total']:,}원")

    conn.close()

    # 결과 검증
    print("\n\n=== 결과 검증 ===")
    if agg.labor_total > 0:
        print("[OK] 노무비 계산 성공!")
    else:
        print("[FAIL] 노무비가 0입니다. 계산 실패!")
        return False

    if len(labor_rows) == 2:
        print(f"[OK] 직무별 상세 데이터 생성 완료 ({len(labor_rows)}개)")
    else:
        print(f"[FAIL] 직무별 상세 데이터 개수 오류: {len(labor_rows)}개 (예상: 2개)")
        return False

    print("\n모든 테스트 통과!")
    return True

if __name__ == "__main__":
    try:
        success = test_calculation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
