"""
노무비 상세 계산 예시
예시: 소장 1명, 일급 400,000원
"""
from decimal import Decimal

def drop_under_1_won(value):
    """원 미만 절사"""
    return int(value)

# ========== 입력 값 ==========
print("=" * 60)
print("노무비 상세 계산 예시")
print("=" * 60)

# 직무 정보
job_name = "소장"
daily_wage = Decimal("400000")  # 일급
headcount = 1  # 인원

# 근무 조건
monthly_workdays = Decimal("20.6")  # 월 근무일수
daily_work_hours = Decimal("8")  # 1일 근무시간
overtime_hours = Decimal("0")  # 연장근로시간 (월)
holiday_work_hours = Decimal("0")  # 휴일근로시간 (월)

# 수당 계산용
weekly_holiday_days = Decimal("4.345")  # 주휴일수 (월 환산)
annual_leave_days = Decimal("1.25")  # 연차일수 (월 환산)

# 보험료율 (2024년 기준)
insurance_rates = {
    "industrial_accident": Decimal("0.0178"),  # 산재보험 1.78%
    "national_pension": Decimal("0.045"),  # 국민연금 4.5%
    "employment_insurance": Decimal("0.009"),  # 고용보험 0.9%
    "health_insurance": Decimal("0.03545"),  # 건강보험 3.545%
    "long_term_care": Decimal("0.1295"),  # 장기요양 12.95%
    "wage_bond": Decimal("0.0025"),  # 임금채권 0.25%
    "asbestos_relief": Decimal("0.0002"),  # 석면피해구제 0.02%
}

print(f"\n【기본 정보】")
print(f"직무: {job_name}")
print(f"일급: {daily_wage:,}원")
print(f"인원: {headcount}명")
print(f"월 근무일수: {monthly_workdays}일")
print(f"1일 근무시간: {daily_work_hours}시간")

# ========== 계산 시작 ==========
print(f"\n{'=' * 60}")
print("【노무비 계산】")
print(f"{'=' * 60}")

# 1) 일급 합계
daily_wage_total = daily_wage * headcount
print(f"\n[1] 일급 합계")
print(f"   = {daily_wage:,}원 × {headcount}명")
print(f"   = {daily_wage_total:,}원")

# 2) 기본급(월)
base_salary = drop_under_1_won(daily_wage_total * monthly_workdays)
print(f"\n[2] 기본급(월)")
print(f"   = {daily_wage_total:,}원 × {monthly_workdays}일")
print(f"   = {base_salary:,}원")

# 3) 상여금(월) = 기본급 × 400% ÷ 12
bonus_annual_rate = Decimal("4.0")
months_per_year = Decimal("12")
bonus = drop_under_1_won(base_salary * bonus_annual_rate / months_per_year)
print(f"\n[3] 상여금(월)")
print(f"   = {base_salary:,}원 × {bonus_annual_rate * 100}% ÷ {months_per_year}개월")
print(f"   = {bonus:,}원")

# 4) 통상시간급
# 4-1) 시간급
hourly_wage = drop_under_1_won(daily_wage_total / daily_work_hours)
print(f"\n[4] 통상시간급 계산")
print(f"   4-1) 시간급")
print(f"        = {daily_wage_total:,}원 ÷ {daily_work_hours}시간")
print(f"        = {hourly_wage:,}원")

# 4-2) 상여 시간가산
standard_monthly_hours = Decimal("209")  # 통상월근로시간
bonus_per_hour = drop_under_1_won(bonus / standard_monthly_hours)
print(f"   4-2) 상여 시간가산")
print(f"        = {bonus:,}원 ÷ {standard_monthly_hours}시간")
print(f"        = {bonus_per_hour:,}원")

# 4-3) 통상시간급
ordinary_hourly_wage = drop_under_1_won(Decimal(hourly_wage) + Decimal(bonus_per_hour))
print(f"   4-3) 통상시간급")
print(f"        = {hourly_wage:,}원 + {bonus_per_hour:,}원")
print(f"        = {ordinary_hourly_wage:,}원")

# 5) 주휴수당
weekly_allowance = drop_under_1_won(
    Decimal(ordinary_hourly_wage) * daily_work_hours * weekly_holiday_days
)
print(f"\n5  주휴수당(월)")
print(f"   = {ordinary_hourly_wage:,}원 × {daily_work_hours}시간 × {weekly_holiday_days}일")
print(f"   = {weekly_allowance:,}원")

# 6) 연차수당
annual_leave_allowance = drop_under_1_won(
    Decimal(ordinary_hourly_wage) * daily_work_hours * annual_leave_days
)
print(f"\n6  연차수당(월)")
print(f"   = {ordinary_hourly_wage:,}원 × {daily_work_hours}시간 × {annual_leave_days}일")
print(f"   = {annual_leave_allowance:,}원")

# 6-1) 연장수당
overtime_allowance = drop_under_1_won(Decimal(ordinary_hourly_wage) * overtime_hours)
if overtime_hours > 0:
    print(f"\n6-1) 연장수당")
    print(f"   = {ordinary_hourly_wage:,}원 × {overtime_hours}시간")
    print(f"   = {overtime_allowance:,}원")

# 6-2) 휴일근로수당
holiday_work_allowance = drop_under_1_won(Decimal(ordinary_hourly_wage) * holiday_work_hours)
if holiday_work_hours > 0:
    print(f"\n6-2) 휴일근로수당")
    print(f"   = {ordinary_hourly_wage:,}원 × {holiday_work_hours}시간")
    print(f"   = {holiday_work_allowance:,}원")

# 7) 제수당 합계
allowance = drop_under_1_won(
    Decimal(weekly_allowance)
    + Decimal(annual_leave_allowance)
    + Decimal(overtime_allowance)
    + Decimal(holiday_work_allowance)
)
print(f"\n7  제수당 합계")
print(f"   = 주휴수당 + 연차수당 + 연장수당 + 휴일근로수당")
print(f"   = {weekly_allowance:,}원 + {annual_leave_allowance:,}원 + {overtime_allowance:,}원 + {holiday_work_allowance:,}원")
print(f"   = {allowance:,}원")

# 8) 퇴직급여충당금
retirement = drop_under_1_won(
    (Decimal(base_salary) + Decimal(allowance) + Decimal(bonus)) / months_per_year
)
print(f"\n8  퇴직급여충당금(월)")
print(f"   = (기본급 + 제수당 + 상여금) ÷ {months_per_year}개월")
print(f"   = ({base_salary:,}원 + {allowance:,}원 + {bonus:,}원) ÷ 12")
print(f"   = {retirement:,}원")

# 9) 인건비 소계
labor_subtotal = drop_under_1_won(
    Decimal(base_salary) + Decimal(allowance) + Decimal(bonus) + Decimal(retirement)
)
print(f"\n9  인건비 소계")
print(f"   = 기본급 + 제수당 + 상여금 + 퇴직급여충당금")
print(f"   = {base_salary:,}원 + {allowance:,}원 + {bonus:,}원 + {retirement:,}원")
print(f"   = {labor_subtotal:,}원")

# 10) 보험료 계산
print(f"\n🔟 4대보험 및 기타 보험료")
insurance_base = Decimal(base_salary) + Decimal(allowance) + Decimal(bonus)
print(f"   보험료 산정 기준액 = {insurance_base:,}원")

industrial_accident = drop_under_1_won(insurance_base * insurance_rates["industrial_accident"])
print(f"   • 산재보험 ({insurance_rates['industrial_accident'] * 100}%)")
print(f"     = {insurance_base:,}원 × {insurance_rates['industrial_accident'] * 100}%")
print(f"     = {industrial_accident:,}원")

national_pension = drop_under_1_won(insurance_base * insurance_rates["national_pension"])
print(f"   • 국민연금 ({insurance_rates['national_pension'] * 100}%)")
print(f"     = {insurance_base:,}원 × {insurance_rates['national_pension'] * 100}%")
print(f"     = {national_pension:,}원")

employment_insurance = drop_under_1_won(insurance_base * insurance_rates["employment_insurance"])
print(f"   • 고용보험 ({insurance_rates['employment_insurance'] * 100}%)")
print(f"     = {insurance_base:,}원 × {insurance_rates['employment_insurance'] * 100}%")
print(f"     = {employment_insurance:,}원")

health_insurance = drop_under_1_won(insurance_base * insurance_rates["health_insurance"])
print(f"   • 건강보험 ({insurance_rates['health_insurance'] * 100}%)")
print(f"     = {insurance_base:,}원 × {insurance_rates['health_insurance'] * 100}%")
print(f"     = {health_insurance:,}원")

long_term_care = drop_under_1_won(Decimal(health_insurance) * insurance_rates["long_term_care"])
print(f"   • 장기요양보험 (건강보험료 × {insurance_rates['long_term_care'] * 100}%)")
print(f"     = {health_insurance:,}원 × {insurance_rates['long_term_care'] * 100}%")
print(f"     = {long_term_care:,}원")

wage_bond = drop_under_1_won(insurance_base * insurance_rates["wage_bond"])
print(f"   • 임금채권보장 ({insurance_rates['wage_bond'] * 100}%)")
print(f"     = {insurance_base:,}원 × {insurance_rates['wage_bond'] * 100}%")
print(f"     = {wage_bond:,}원")

asbestos_relief = drop_under_1_won(insurance_base * insurance_rates["asbestos_relief"])
print(f"   • 석면피해구제 ({insurance_rates['asbestos_relief'] * 100}%)")
print(f"     = {insurance_base:,}원 × {insurance_rates['asbestos_relief'] * 100}%")
print(f"     = {asbestos_relief:,}원")

insurance_total = drop_under_1_won(
    Decimal(industrial_accident)
    + Decimal(national_pension)
    + Decimal(employment_insurance)
    + Decimal(health_insurance)
    + Decimal(long_term_care)
    + Decimal(wage_bond)
    + Decimal(asbestos_relief)
)
print(f"\n   ▶ 보험료 합계: {insurance_total:,}원")

# 11) 총 노무비
total_labor_cost = drop_under_1_won(Decimal(labor_subtotal) + Decimal(insurance_total))

print(f"\n{'=' * 60}")
print(f"【최종 결과】")
print(f"{'=' * 60}")
print(f"\n인건비 소계:    {labor_subtotal:>15,}원")
print(f"보험료 합계:    {insurance_total:>15,}원")
print(f"{'─' * 60}")
print(f"총 노무비:      {total_labor_cost:>15,}원")
print(f"{'=' * 60}")

# 상세 내역 요약
print(f"\n\n【상세 내역 요약표】")
print(f"{'─' * 60}")
print(f"{'구분':<20} {'금액':>20}")
print(f"{'─' * 60}")
print(f"{'기본급(월)':<20} {base_salary:>20,}원")
print(f"{'  ∟ 주휴수당':<20} {weekly_allowance:>20,}원")
print(f"{'  ∟ 연차수당':<20} {annual_leave_allowance:>20,}원")
if overtime_hours > 0:
    print(f"{'  ∟ 연장수당':<20} {overtime_allowance:>20,}원")
if holiday_work_hours > 0:
    print(f"{'  ∟ 휴일근로수당':<20} {holiday_work_allowance:>20,}원")
print(f"{'상여금(월)':<20} {bonus:>20,}원")
print(f"{'퇴직급여충당금(월)':<20} {retirement:>20,}원")
print(f"{'─' * 60}")
print(f"{'인건비 소계':<20} {labor_subtotal:>20,}원")
print(f"{'─' * 60}")
print(f"{'산재보험':<20} {industrial_accident:>20,}원")
print(f"{'국민연금':<20} {national_pension:>20,}원")
print(f"{'고용보험':<20} {employment_insurance:>20,}원")
print(f"{'건강보험':<20} {health_insurance:>20,}원")
print(f"{'장기요양보험':<20} {long_term_care:>20,}원")
print(f"{'임금채권보장':<20} {wage_bond:>20,}원")
print(f"{'석면피해구제':<20} {asbestos_relief:>20,}원")
print(f"{'─' * 60}")
print(f"{'보험료 합계':<20} {insurance_total:>20,}원")
print(f"{'=' * 60}")
print(f"{'💰 총 노무비':<20} {total_labor_cost:>20,}원")
print(f"{'=' * 60}")

print(f"\n✅ 계산 완료!")
print(f"\n※ 모든 금액은 원 미만 절사 처리됩니다.")
print(f"※ 일급 {daily_wage:,}원 기준 1인 월 노무비: {total_labor_cost:,}원")
