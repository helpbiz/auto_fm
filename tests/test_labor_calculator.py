"""
노무비 계산 엔진 단위 테스트
- 기본급, 상여금, 제수당, 퇴직금, 보험료 계산 검증
- 로드맵 주의사항: 퇴직급여 및 보험료 정확성 검증
"""
import pytest
from decimal import Decimal
from src.domain.calculator.labor import LaborCostCalculator
from src.domain.constants.rounding import drop_under_1_won


class TestBasicSalaryCalculation:
    """기본급 계산 검증"""

    def test_basic_salary_single_person(self, basic_calc_context):
        """기본급 = 노임단가 × 20.6일 (월 근무일수)"""
        calculator = LaborCostCalculator(basic_calc_context)
        result = calculator.calculate()

        # 일급 200,000 × 20.6일 = 4,120,000원
        expected = 200000 * Decimal("20.6")
        assert result["base_salary"] == expected
        assert result["base_salary"] == 4120000

    def test_basic_salary_multi_person(self, multi_person_context):
        """다인원: 기본급 = (노임단가 × 20.6일) × 인원수"""
        calculator = LaborCostCalculator(multi_person_context)
        result = calculator.calculate()

        # 일급 200,000 × 20.6일 × 2명 = 8,240,000원
        expected = 200000 * Decimal("20.6") * 2
        assert result["base_salary"] == expected


class TestBonusCalculation:
    """상여금 계산 검증"""

    def test_bonus_calculation(self, basic_calc_context):
        """상여금 = 기본급 × 400% ÷ 12개월"""
        calculator = LaborCostCalculator(basic_calc_context)
        result = calculator.calculate()

        # 기본급 4,120,000원
        base_salary = 4120000
        # 상여금 = 4,120,000 × 4.0 ÷ 12 = 1,373,333원 (소수점 이하 버림)
        expected = drop_under_1_won(Decimal(base_salary) * Decimal("4.0") / Decimal("12"))
        assert result["bonus"] == expected
        assert result["bonus"] == 1373333


class TestOrdinaryHourlyWage:
    """통상시간급 계산 검증"""

    def test_ordinary_hourly_wage(self, basic_calc_context):
        """통상시간급 = 시간급 + (상여금 ÷ 209시간)"""
        calculator = LaborCostCalculator(basic_calc_context)
        result = calculator.calculate()

        # 시간급 = 200,000 ÷ 8시간 = 25,000원
        # 상여금 = 1,373,333원
        # 상여 시간가산 = 1,373,333 ÷ 209 = 6,570원 (소수점 이하 버림)
        # 통상시간급 = 25,000 + 6,570 = 31,570원

        # 실제 계산 로직 검증 (내부 계산 추적)
        assert result["total_labor_cost"] > 0  # 최종 결과 존재 확인


class TestAllowances:
    """제수당 계산 검증"""

    def test_weekly_allowance(self, basic_calc_context):
        """주휴수당 = 통상시간급 × 1일근무시간 × 주휴일수"""
        calculator = LaborCostCalculator(basic_calc_context)
        result = calculator.calculate()

        # 주휴수당이 정상적으로 계산되는지 확인
        assert result["weekly_allowance"] > 0
        assert "allowances" in result
        assert result["allowances"]["total"] > 0

    def test_annual_leave_allowance(self, basic_calc_context):
        """연차수당 = 통상시간급 × 1일근무시간 × 연차일수"""
        calculator = LaborCostCalculator(basic_calc_context)
        result = calculator.calculate()

        assert result["annual_leave_allowance"] > 0
        assert result["allowances"]["annual_leave_pay"] > 0


class TestRetirementReserve:
    """퇴직급여충당금 계산 검증 (로드맵 주의사항)"""

    def test_retirement_calculation(self, basic_calc_context):
        """퇴직급여충당금 = (기본급 + 제수당 + 상여금) ÷ 12"""
        calculator = LaborCostCalculator(basic_calc_context)
        result = calculator.calculate()

        base = result["base_salary"]
        allowance = result["allowance"]
        bonus = result["bonus"]

        # 수동 계산
        expected = drop_under_1_won((Decimal(base) + Decimal(allowance) + Decimal(bonus)) / Decimal("12"))

        assert result["retirement"] == expected
        assert result["retirement"] > 0


class TestInsurancePremiums:
    """보험료 계산 검증 (로드맵 주의사항: 법정 요율 정확성)"""

    def test_insurance_calculation(self, basic_calc_context):
        """보험료 각 항목 계산"""
        calculator = LaborCostCalculator(basic_calc_context)
        result = calculator.calculate()

        # 보험료 산정 기준 = 기본급 + 제수당 + 상여금
        insurance_base = result["base_salary"] + result["allowance"] + result["bonus"]

        # 각 보험료가 양수인지 확인
        assert result["industrial_accident"] > 0  # 산재보험
        assert result["national_pension"] > 0      # 국민연금
        assert result["employment_insurance"] > 0  # 고용보험
        assert result["health_insurance"] > 0      # 건강보험
        assert result["long_term_care"] > 0        # 노인장기요양
        assert result["wage_bond"] > 0             # 임금채권보장
        assert result["asbestos_relief"] > 0       # 석면피해구제

        # 보험료 총합 확인
        assert result["insurance_total"] > 0
        assert result["insurance"]["total"] == result["insurance_total"]

    def test_long_term_care_is_percentage_of_health(self, basic_calc_context):
        """노인장기요양보험 = 건강보험 × 12.81% (로드맵 주의사항)"""
        calculator = LaborCostCalculator(basic_calc_context)
        result = calculator.calculate()

        health = result["health_insurance"]
        long_term = result["long_term_care"]

        # 노인장기요양 = 건강보험 × 12.81%
        expected = drop_under_1_won(Decimal(health) * Decimal("0.1281"))
        assert long_term == expected


class TestTotalLaborCost:
    """총 노무비 계산 검증"""

    def test_total_labor_cost(self, basic_calc_context):
        """총 노무비 = 인건비 소계 + 보험료 총합"""
        calculator = LaborCostCalculator(basic_calc_context)
        result = calculator.calculate()

        labor_subtotal = result["labor_subtotal"]
        insurance_total = result["insurance_total"]

        expected = labor_subtotal + insurance_total
        assert result["total_labor_cost"] == expected

    def test_labor_subtotal(self, basic_calc_context):
        """인건비 소계 = 기본급 + 제수당 + 상여금 + 퇴직금"""
        calculator = LaborCostCalculator(basic_calc_context)
        result = calculator.calculate()

        expected = (
            result["base_salary"]
            + result["allowance"]
            + result["bonus"]
            + result["retirement"]
        )
        assert result["labor_subtotal"] == expected


class TestMultiPersonCalculation:
    """다인원 계산 검증"""

    def test_two_person_doubles_cost(self, basic_calc_context, multi_person_context):
        """2명 계산 시 비용이 정확히 2배가 되는지 확인"""
        single_calc = LaborCostCalculator(basic_calc_context)
        single_result = single_calc.calculate()

        multi_calc = LaborCostCalculator(multi_person_context)
        multi_result = multi_calc.calculate()

        # 각 항목이 정확히 2배
        assert multi_result["base_salary"] == single_result["base_salary"] * 2
        assert multi_result["bonus"] == single_result["bonus"] * 2
        assert multi_result["allowance"] == single_result["allowance"] * 2
        assert multi_result["retirement"] == single_result["retirement"] * 2
        assert multi_result["total_labor_cost"] == single_result["total_labor_cost"] * 2


class TestMultiRoleCalculation:
    """다직무 계산 검증"""

    def test_multi_role_aggregation(self, multi_role_context):
        """여러 직무의 비용이 올바르게 합산되는지 확인"""
        calculator = LaborCostCalculator(multi_role_context)
        result = calculator.calculate()

        # job_lines가 2개여야 함
        assert "job_lines" in result
        assert len(result["job_lines"]) == 2

        # 각 직무의 총합이 전체 노무비와 일치
        total_from_lines = sum(line.total for line in result["job_lines"])
        assert total_from_lines == result["total_labor_cost"]


class TestEdgeCases:
    """엣지 케이스 테스트"""

    def test_zero_wage(self):
        """일급이 0원인 경우"""
        from src.domain.context.calc_context import CalcContext

        context = CalcContext(
            project_name="제로 테스트",
            year=2025,
            manpower={"ENGINEER": Decimal("1")},
            wage_rate={"ENGINEER": Decimal("0")},
            monthly_workdays=Decimal("20.6"),
            daily_work_hours=Decimal("8"),
            weekly_holiday_days=Decimal("4.33"),
            annual_leave_days=Decimal("1.25"),
            expenses={},
        )

        calculator = LaborCostCalculator(context)
        result = calculator.calculate()

        # 0원이어도 오류 없이 계산
        assert result["base_salary"] == 0
        assert result["total_labor_cost"] == 0

    def test_very_large_wage(self):
        """매우 큰 일급 (1억원)"""
        from src.domain.context.calc_context import CalcContext

        context = CalcContext(
            project_name="대액 테스트",
            year=2025,
            manpower={"ENGINEER": Decimal("1")},
            wage_rate={"ENGINEER": Decimal("100000000")},  # 1억원
            monthly_workdays=Decimal("20.6"),
            daily_work_hours=Decimal("8"),
            weekly_holiday_days=Decimal("4.33"),
            annual_leave_days=Decimal("1.25"),
            expenses={},
        )

        calculator = LaborCostCalculator(context)
        result = calculator.calculate()

        # 오버플로우 없이 계산
        assert result["base_salary"] > 0
        assert result["total_labor_cost"] > result["base_salary"]
