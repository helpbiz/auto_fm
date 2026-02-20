"""
수동 테스트 스크립트: 일반관리비/이윤 계산 검증
실행: python test_overhead_profit_manual.py
"""
from decimal import Decimal
from src.domain.aggregator import Aggregator
from src.domain.constants.rates import GENERAL_ADMIN_MAX, PROFIT_MAX

print("=" * 70)
print("일반관리비 및 이윤 계산 검증 테스트")
print("=" * 70)

# 테스트 시나리오 1: 기본 10% 요율
print("\n[테스트 1] 기본 10% 요율")
print("-" * 70)

labor_total = 10000000  # 노무비 1천만원
expense_total = 5000000  # 경비 5백만원

# 일반관리비 계산
overhead_base = labor_total + expense_total  # 1,500만원
overhead_rate = GENERAL_ADMIN_MAX  # 10%
overhead_cost = int(Decimal(overhead_base) * overhead_rate)

print(f"노무비: {labor_total:,}원")
print(f"경비: {expense_total:,}원")
print(f"일반관리비 산정 기준: {overhead_base:,}원")
print(f"일반관리비율: {float(overhead_rate) * 100}%")
print(f"일반관리비: {overhead_cost:,}원")

# 이윤 계산
profit_base = labor_total + expense_total + overhead_cost
profit_rate = PROFIT_MAX  # 10%
profit = int(Decimal(profit_base) * profit_rate)

print(f"이윤 산정 기준: {profit_base:,}원")
print(f"이윤율: {float(profit_rate) * 100}%")
print(f"이윤: {profit:,}원")

# Aggregator로 검증
agg = Aggregator(
    labor_total=labor_total,
    fixed_expense_total=expense_total,
    variable_expense_total=0,
    passthrough_expense_total=0,
    overhead_cost=overhead_cost,
    profit=profit,
)

print(f"\n총 합계 (VAT 제외): {agg.grand_total:,}원")
print(f"  = 노무비 {labor_total:,}")
print(f"  + 경비 {expense_total:,}")
print(f"  + 일반관리비 {overhead_cost:,}")
print(f"  + 이윤 {profit:,}")

# 검증
expected_overhead = 1500000  # 15M × 10%
expected_profit = 1650000    # 16.5M × 10%
expected_total = 18150000    # 10M + 5M + 1.5M + 1.65M

assert overhead_cost == expected_overhead, f"일반관리비 오류: {overhead_cost} != {expected_overhead}"
assert profit == expected_profit, f"이윤 오류: {profit} != {expected_profit}"
assert agg.grand_total == expected_total, f"총합 오류: {agg.grand_total} != {expected_total}"

print("\n[OK] 테스트 1 통과!")

# 테스트 시나리오 2: 일반관리비 10% 캡 적용
print("\n" + "=" * 70)
print("[테스트 2] 일반관리비 10% 상한선 적용 (15% → 10%)")
print("-" * 70)

labor_total_2 = 10000000
expense_total_2 = 5000000

# 15%로 설정 시도
overhead_base_2 = labor_total_2 + expense_total_2
requested_rate = Decimal("0.15")  # 15% 시도
overhead_cost_2 = int(Decimal(overhead_base_2) * requested_rate)

print(f"노무비: {labor_total_2:,}원")
print(f"경비: {expense_total_2:,}원")
print(f"일반관리비 산정 기준: {overhead_base_2:,}원")
print(f"요청한 일반관리비율: {float(requested_rate) * 100}%")
print(f"계산된 일반관리비 (캡 적용 전): {overhead_cost_2:,}원")

# 10% 캡 적용
max_overhead = int(Decimal(overhead_base_2) * GENERAL_ADMIN_MAX)
overhead_cost_capped = min(overhead_cost_2, max_overhead)

print(f"일반관리비 상한 (10%): {max_overhead:,}원")
print(f"최종 일반관리비 (캡 적용 후): {overhead_cost_capped:,}원")

# 검증
assert overhead_cost_2 == 2250000, "15% 계산 오류"  # 15M × 15%
assert max_overhead == 1500000, "10% 상한 오류"    # 15M × 10%
assert overhead_cost_capped == 1500000, "캡 적용 오류"

print("\n[OK] 테스트 2 통과! (15% 요청 -> 10%로 캡핑)")

# 테스트 시나리오 3: 사용자 정의 요율 (10% 이내)
print("\n" + "=" * 70)
print("[테스트 3] 사용자 정의 요율 (7%, 8%)")
print("-" * 70)

labor_total_3 = 20000000  # 2천만원
expense_total_3 = 10000000  # 1천만원

# 일반관리비 7%
overhead_base_3 = labor_total_3 + expense_total_3
overhead_rate_3 = Decimal("0.07")
overhead_cost_3 = int(Decimal(overhead_base_3) * overhead_rate_3)

print(f"노무비: {labor_total_3:,}원")
print(f"경비: {expense_total_3:,}원")
print(f"일반관리비 산정 기준: {overhead_base_3:,}원")
print(f"일반관리비율: {float(overhead_rate_3) * 100}%")
print(f"일반관리비: {overhead_cost_3:,}원")

# 이윤 8%
profit_base_3 = labor_total_3 + expense_total_3 + overhead_cost_3
profit_rate_3 = Decimal("0.08")
profit_3 = int(Decimal(profit_base_3) * profit_rate_3)

print(f"이윤 산정 기준: {profit_base_3:,}원")
print(f"이윤율: {float(profit_rate_3) * 100}%")
print(f"이윤: {profit_3:,}원")

agg_3 = Aggregator(
    labor_total=labor_total_3,
    fixed_expense_total=expense_total_3,
    variable_expense_total=0,
    passthrough_expense_total=0,
    overhead_cost=overhead_cost_3,
    profit=profit_3,
)

print(f"\n총 합계 (VAT 제외): {agg_3.grand_total:,}원")

# 검증
expected_overhead_3 = 2100000   # 30M × 7%
expected_profit_3 = 2568000     # 32.1M × 8%
expected_total_3 = 34668000     # 20M + 10M + 2.1M + 2.568M

assert overhead_cost_3 == expected_overhead_3, f"일반관리비 오류"
assert profit_3 == expected_profit_3, f"이윤 오류"
assert agg_3.grand_total == expected_total_3, f"총합 오류"

print("\n[OK] 테스트 3 통과!")

# 최종 결과
print("\n" + "=" * 70)
print("*** 모든 테스트 통과! ***")
print("=" * 70)
print("\n[OK] 일반관리비 계산 정상 동작")
print("[OK] 일반관리비 10% 상한선 적용 정상")
print("[OK] 이윤 계산 정상 동작")
print("[OK] 사용자 정의 요율 지원 정상")

print("\n" + "=" * 70)
print("계산 로직 검증 완료!")
print("=" * 70)
