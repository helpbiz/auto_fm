"""
보험료율 정확성 검증 테스트
로드맵 주의사항: 법정 요율이 정확히 반영되는지 검증
"""
import pytest
from decimal import Decimal
from src.domain.context.calc_context import CalcContext


class TestInsuranceRatesCompliance:
    """법정 보험료율 정확성 검증"""

    def test_industrial_accident_rate(self):
        """산재보험료율 = 0.9%"""
        assert CalcContext.INDUSTRIAL_ACCIDENT_RATE == Decimal("0.009")

    def test_national_pension_rate(self):
        """국민연금료율 = 4.5%"""
        assert CalcContext.NATIONAL_PENSION_RATE == Decimal("0.045")

    def test_employment_insurance_rate(self):
        """고용보험료율 = 1.15%"""
        assert CalcContext.EMPLOYMENT_INSURANCE_RATE == Decimal("0.0115")

    def test_health_insurance_rate(self):
        """건강보험료율 = 3.545%"""
        assert CalcContext.HEALTH_INSURANCE_RATE == Decimal("0.03545")

    def test_long_term_care_rate(self):
        """노인장기요양보험료율 = 12.81% (건강보험의)"""
        assert CalcContext.LONG_TERM_CARE_RATE == Decimal("0.1281")

    def test_wage_bond_rate(self):
        """임금채권보장보험료율 = 0.06%"""
        assert CalcContext.WAGE_BOND_RATE == Decimal("0.0006")

    def test_asbestos_relief_rate(self):
        """석면피해구제보험료율 = 0.004%"""
        assert CalcContext.ASBESTOS_RELIEF_RATE == Decimal("0.00004")


class TestInsuranceCalculationAccuracy:
    """보험료 계산 정확성 검증"""

    def test_industrial_accident_calculation(self, basic_calc_context):
        """산재보험 = 보험료 산정 기준 × 0.9%"""
        from src.domain.calculator.labor import LaborCostCalculator
        from src.domain.constants.rounding import drop_under_1_won

        calculator = LaborCostCalculator(basic_calc_context)
        result = calculator.calculate()

        insurance_base = result["base_salary"] + result["allowance"] + result["bonus"]
        expected = drop_under_1_won(Decimal(insurance_base) * CalcContext.INDUSTRIAL_ACCIDENT_RATE)

        assert result["industrial_accident"] == expected

    def test_national_pension_calculation(self, basic_calc_context):
        """국민연금 = 보험료 산정 기준 × 4.5%"""
        from src.domain.calculator.labor import LaborCostCalculator
        from src.domain.constants.rounding import drop_under_1_won

        calculator = LaborCostCalculator(basic_calc_context)
        result = calculator.calculate()

        insurance_base = result["base_salary"] + result["allowance"] + result["bonus"]
        expected = drop_under_1_won(Decimal(insurance_base) * CalcContext.NATIONAL_PENSION_RATE)

        assert result["national_pension"] == expected

    def test_employment_insurance_calculation(self, basic_calc_context):
        """고용보험 = 보험료 산정 기준 × 1.15%"""
        from src.domain.calculator.labor import LaborCostCalculator
        from src.domain.constants.rounding import drop_under_1_won

        calculator = LaborCostCalculator(basic_calc_context)
        result = calculator.calculate()

        insurance_base = result["base_salary"] + result["allowance"] + result["bonus"]
        expected = drop_under_1_won(Decimal(insurance_base) * CalcContext.EMPLOYMENT_INSURANCE_RATE)

        assert result["employment_insurance"] == expected

    def test_health_insurance_calculation(self, basic_calc_context):
        """건강보험 = 보험료 산정 기준 × 3.545%"""
        from src.domain.calculator.labor import LaborCostCalculator
        from src.domain.constants.rounding import drop_under_1_won

        calculator = LaborCostCalculator(basic_calc_context)
        result = calculator.calculate()

        insurance_base = result["base_salary"] + result["allowance"] + result["bonus"]
        expected = drop_under_1_won(Decimal(insurance_base) * CalcContext.HEALTH_INSURANCE_RATE)

        assert result["health_insurance"] == expected

    def test_long_term_care_is_based_on_health_insurance(self, basic_calc_context):
        """노인장기요양보험 = 건강보험 × 12.81% (로드맵 주의사항)"""
        from src.domain.calculator.labor import LaborCostCalculator
        from src.domain.constants.rounding import drop_under_1_won

        calculator = LaborCostCalculator(basic_calc_context)
        result = calculator.calculate()

        health_insurance = result["health_insurance"]
        expected = drop_under_1_won(Decimal(health_insurance) * CalcContext.LONG_TERM_CARE_RATE)

        assert result["long_term_care"] == expected

    def test_wage_bond_calculation(self, basic_calc_context):
        """임금채권보장 = 보험료 산정 기준 × 0.06%"""
        from src.domain.calculator.labor import LaborCostCalculator
        from src.domain.constants.rounding import drop_under_1_won

        calculator = LaborCostCalculator(basic_calc_context)
        result = calculator.calculate()

        insurance_base = result["base_salary"] + result["allowance"] + result["bonus"]
        expected = drop_under_1_won(Decimal(insurance_base) * CalcContext.WAGE_BOND_RATE)

        assert result["wage_bond"] == expected

    def test_asbestos_relief_calculation(self, basic_calc_context):
        """석면피해구제 = 보험료 산정 기준 × 0.004%"""
        from src.domain.calculator.labor import LaborCostCalculator
        from src.domain.constants.rounding import drop_under_1_won

        calculator = LaborCostCalculator(basic_calc_context)
        result = calculator.calculate()

        insurance_base = result["base_salary"] + result["allowance"] + result["bonus"]
        expected = drop_under_1_won(Decimal(insurance_base) * CalcContext.ASBESTOS_RELIEF_RATE)

        assert result["asbestos_relief"] == expected


class TestInsuranceTotalSum:
    """보험료 총합 검증"""

    def test_insurance_total_equals_sum_of_all_premiums(self, basic_calc_context):
        """보험료 총합 = 각 보험료의 합계"""
        from src.domain.calculator.labor import LaborCostCalculator

        calculator = LaborCostCalculator(basic_calc_context)
        result = calculator.calculate()

        expected_total = (
            result["industrial_accident"]
            + result["national_pension"]
            + result["employment_insurance"]
            + result["health_insurance"]
            + result["long_term_care"]
            + result["wage_bond"]
            + result["asbestos_relief"]
        )

        assert result["insurance_total"] == expected_total
        assert result["insurance"]["total"] == expected_total
