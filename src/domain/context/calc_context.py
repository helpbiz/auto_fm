from dataclasses import dataclass
from decimal import Decimal
from typing import Dict


@dataclass
class CalcContext:
    project_name: str
    year: int       

    # 근무 기준 (월 기준)
    monthly_workdays: Decimal      # 20.6
    daily_work_hours: Decimal      # 8

    # 인원 / 단가 (일급)
    manpower: Dict[str, Decimal]   # 직무 → 인원
    wage_rate: Dict[str, Decimal]  # 직무 → 일급(MD)

    # 제수당 기준 (월 환산)
    weekly_holiday_days: Decimal   # 52 / 12 (주휴일수)
    annual_leave_days: Decimal     # 15 / 12 (연차일수)

    # 인력보험료율 (이미지 기준)
    INDUSTRIAL_ACCIDENT_RATE = Decimal("0.009")  # 산재보험료 0.9%
    NATIONAL_PENSION_RATE = Decimal("0.045")  # 국민연금 4.5%
    EMPLOYMENT_INSURANCE_RATE = Decimal("0.0115")  # 고용보험료 1.15%
    HEALTH_INSURANCE_RATE = Decimal("0.03545")  # 국민건강보험료 3.545%
    LONG_TERM_CARE_RATE = Decimal("0.1281")  # 노인장기요양보험료 12.81%
    WAGE_BOND_RATE = Decimal("0.0006")  # 임금채권보장보험료 0.06%
    ASBESTOS_RELIEF_RATE = Decimal("0.00004")  # 석면피해구제분담금 0.004%
    
    # 경비
    expenses: Dict[str, Decimal]        # 경비명 -> 금액

    # 추가 수당 기준 (시간 단위)
    overtime_hours: Decimal = Decimal("0")
    holiday_work_hours: Decimal = Decimal("0")