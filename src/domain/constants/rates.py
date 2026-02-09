from decimal import Decimal

# 법정 보험료율
NATIONAL_PENSION = Decimal("0.045")  # 국민연금
HEALTH_INSURANCE = Decimal("0.0343")  # 건강보험
LONG_TERM_CARE = Decimal("0.1281")  # 노인장기요양 (건강보험의 12.81%)
EMPLOYMENT_INSURANCE = Decimal("0.0105")  # 고용보험 (최소)
INDUSTRIAL_ACCIDENT = Decimal("0.009")  # 산재보험

# 간접비 상한
GENERAL_ADMIN_MAX = Decimal("0.10")  # 일반관리비 10%
PROFIT_MAX = Decimal("0.10")  # 이윤 10%
