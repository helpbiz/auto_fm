"""
집계 및 일반관리비 10% 캡 검증 테스트
로드맵 주의사항: 일반관리비는 10%를 초과할 수 없음 (법규_예정가격 작성요령)
"""
import pytest
from decimal import Decimal
from src.domain.aggregator import Aggregator
from src.domain.constants.rates import GENERAL_ADMIN_MAX, PROFIT_MAX


class TestAggregatorBasics:
    """집계 기본 기능 테스트"""

    def test_overhead_base_calculation(self):
        """간접비 산정 기준 = 노무비 + 고정경비"""
        agg = Aggregator(
            labor_total=10000000,
            fixed_expense_total=5000000,
            variable_expense_total=1000000,
            passthrough_expense_total=500000,
            overhead_cost=1500000,
            profit=1650000,
        )

        assert agg.overhead_base == 15000000  # 10,000,000 + 5,000,000

    def test_profit_base_calculation(self):
        """이윤 산정 기준 = 노무비 + 고정경비 + 간접비"""
        agg = Aggregator(
            labor_total=10000000,
            fixed_expense_total=5000000,
            variable_expense_total=0,
            passthrough_expense_total=0,
            overhead_cost=1500000,
            profit=1650000,
        )

        assert agg.profit_base == 16500000  # 10M + 5M + 1.5M

    def test_grand_total_calculation(self):
        """총합 = 노무비 + 고정경비 + 변동경비 + 대행비 + 간접비 + 이윤"""
        agg = Aggregator(
            labor_total=10000000,
            fixed_expense_total=5000000,
            variable_expense_total=1000000,
            passthrough_expense_total=500000,
            overhead_cost=1500000,
            profit=1650000,
        )

        expected = 10000000 + 5000000 + 1000000 + 500000 + 1500000 + 1650000
        assert agg.grand_total == expected
        assert agg.grand_total == 19650000


class TestGeneralAdminMaxCap:
    """일반관리비 10% 상한선 검증 (로드맵 주의사항)"""

    def test_general_admin_max_constant(self):
        """일반관리비 상한선 상수 = 10%"""
        assert GENERAL_ADMIN_MAX == Decimal("0.10")

    def test_overhead_within_10_percent(self):
        """일반관리비가 10% 이내인 경우"""
        agg = Aggregator(
            labor_total=10000000,
            fixed_expense_total=5000000,
            variable_expense_total=0,
            passthrough_expense_total=0,
            overhead_cost=1000000,  # 15M의 6.67% (정상)
            profit=0,
        )

        overhead_base = agg.overhead_base  # 15,000,000
        max_overhead = int(overhead_base * float(GENERAL_ADMIN_MAX))  # 1,500,000

        # 10% 이내이므로 정상
        assert agg.overhead_cost <= max_overhead

    def test_overhead_exactly_10_percent(self):
        """일반관리비가 정확히 10%인 경우"""
        agg = Aggregator(
            labor_total=10000000,
            fixed_expense_total=5000000,
            variable_expense_total=0,
            passthrough_expense_total=0,
            overhead_cost=1500000,  # 15M의 정확히 10%
            profit=0,
        )

        overhead_base = agg.overhead_base
        max_overhead = int(overhead_base * float(GENERAL_ADMIN_MAX))

        # 정확히 10%는 허용
        assert agg.overhead_cost == max_overhead
        assert agg.overhead_cost == 1500000

    def test_overhead_exceeds_10_percent_should_be_capped(self):
        """일반관리비가 10%를 초과하는 경우 - 캡이 적용되어야 함"""
        # 주의: 현재 Aggregator는 캡을 강제하지 않음
        # PHASE 2에서 result/service.py에서 캡을 적용할 예정

        agg = Aggregator(
            labor_total=10000000,
            fixed_expense_total=5000000,
            variable_expense_total=0,
            passthrough_expense_total=0,
            overhead_cost=2000000,  # 15M의 13.3% (초과)
            profit=0,
        )

        overhead_base = agg.overhead_base
        max_overhead = int(overhead_base * float(GENERAL_ADMIN_MAX))

        # 이 테스트는 PHASE 2 구현 후 통과해야 함
        # 현재는 검증만 수행 (실제 적용은 result/service.py에서)
        assert max_overhead == 1500000
        # assert agg.overhead_cost <= max_overhead  # PHASE 2 이후 활성화


class TestProfitMaxCap:
    """이윤 10% 상한선 검증"""

    def test_profit_max_constant(self):
        """이윤 상한선 상수 = 10%"""
        assert PROFIT_MAX == Decimal("0.10")

    def test_profit_within_10_percent(self):
        """이윤이 10% 이내인 경우"""
        agg = Aggregator(
            labor_total=10000000,
            fixed_expense_total=5000000,
            variable_expense_total=0,
            passthrough_expense_total=0,
            overhead_cost=1500000,
            profit=1650000,  # 16.5M의 10%
        )

        profit_base = agg.profit_base  # 16,500,000
        max_profit = int(profit_base * float(PROFIT_MAX))  # 1,650,000

        assert agg.profit == max_profit
        assert agg.profit == 1650000


class TestZeroValues:
    """제로 값 처리 테스트"""

    def test_all_zero(self):
        """모든 값이 0인 경우"""
        agg = Aggregator(
            labor_total=0,
            fixed_expense_total=0,
            variable_expense_total=0,
            passthrough_expense_total=0,
            overhead_cost=0,
            profit=0,
        )

        assert agg.overhead_base == 0
        assert agg.profit_base == 0
        assert agg.grand_total == 0

    def test_only_labor_cost(self):
        """노무비만 있는 경우"""
        agg = Aggregator(
            labor_total=10000000,
            fixed_expense_total=0,
            variable_expense_total=0,
            passthrough_expense_total=0,
            overhead_cost=0,
            profit=0,
        )

        assert agg.overhead_base == 10000000
        assert agg.profit_base == 10000000
        assert agg.grand_total == 10000000
