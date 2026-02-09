from decimal import Decimal
from typing import Dict

from src.domain.context.calc_context import CalcContext
from src.domain.calculator.labor_job_line import LaborJobLine
from src.domain.constants.rounding import drop_under_1_won

# 계산식 기준 상수
STANDARD_MONTHLY_HOURS = Decimal("209")  # 통상 월 근로시간(209시간)
BONUS_ANNUAL_RATE = Decimal("4.0")  # 상여금 400%
MONTHS_PER_YEAR = Decimal("12")



class LaborCostCalculator:
    """
    노무비 계산 전담 클래스
    """

    def __init__(self, context: CalcContext):
        self.context = context

    def calculate(self) -> Dict[str, int]:
        # 다인원일 경우: 1인 기준 계산 후 인원수만큼 합산
        total_headcount = sum(self.context.manpower.values())
        if len(self.context.manpower) > 1 or total_headcount != 1:
            return self._calculate_aggregated_by_headcount()

        # 1) 일급 합계 (단일 인원)
        daily_wage_total = self._calculate_daily_wage_total()
        result = self._calculate_from_daily_wage_total(daily_wage_total)
        job_code = next(iter(self.context.manpower.keys()), "role")
        job_line = self._build_job_line(job_code, 1, result)
        result["job_lines"] = [job_line]
        return result

    def _calculate_aggregated_by_headcount(self) -> Dict[str, int]:
        result = self._empty_result()
        job_lines = []

        job_order = getattr(self.context, "job_order", None)
        if job_order:
            job_codes = [job_code for job_code in job_order if job_code in self.context.manpower]
        else:
            job_codes = sorted(self.context.manpower.keys())

        for job in job_codes:
            headcount = self.context.manpower.get(job, 0)
            if headcount == 0:
                continue
            wage = self.context.wage_rate.get(job, Decimal("0"))
            per_person = self._calculate_from_daily_wage_total(wage)
            scale = int(headcount)
            self._accumulate_scaled(result, per_person, scale)
            job_lines.append(self._build_job_line(job, scale, per_person))

        result["job_lines"] = job_lines
        return result

    def _calculate_from_daily_wage_total(self, daily_wage_total: Decimal) -> Dict[str, int]:

        # 2) 기본급(월)
        base_salary = drop_under_1_won(
            daily_wage_total * self.context.monthly_workdays
        )

        # 3) 상여금(월) = 기본급 × 400% ÷ 12
        bonus = drop_under_1_won(
            base_salary * BONUS_ANNUAL_RATE / MONTHS_PER_YEAR
        )

        # 4) 통상시간급
        ordinary_hourly_wage = self._calculate_ordinary_hourly_wage(
            daily_wage_total,
            bonus,
        )

        # 5) 주휴수당
        weekly_allowance = drop_under_1_won(
            ordinary_hourly_wage
            * self.context.daily_work_hours
            * self.context.weekly_holiday_days
        )

        # 6) 연차수당
        annual_leave_allowance = drop_under_1_won(
            ordinary_hourly_wage
            * self.context.daily_work_hours
            * self.context.annual_leave_days
        )

        # 6-1) 연장수당 (시간 단위, 없으면 0)
        overtime_hours = getattr(self.context, "overtime_hours", Decimal("0"))
        overtime_allowance = drop_under_1_won(
            ordinary_hourly_wage * overtime_hours
        )

        # 6-2) 휴일근로수당 (시간 단위, 없으면 0)
        holiday_work_hours = getattr(self.context, "holiday_work_hours", Decimal("0"))
        holiday_work_allowance = drop_under_1_won(
            ordinary_hourly_wage * holiday_work_hours
        )

        # 7) 제수당 합계
        allowance = drop_under_1_won(
            weekly_allowance
            + annual_leave_allowance
            + overtime_allowance
            + holiday_work_allowance
        )

        # 8) 퇴직급여충당금 = (기본급 + 제수당 + 상여금) ÷ 12
        retirement = drop_under_1_won(
            (base_salary + allowance + bonus) / MONTHS_PER_YEAR
        )

        # 9) 인건비 소계
        labor_subtotal = drop_under_1_won(
            base_salary + allowance + bonus + retirement
        )

        # 10) 보험료 산정 기준
        insurance_base = base_salary + allowance + bonus

        industrial_accident = drop_under_1_won(
            insurance_base * CalcContext.INDUSTRIAL_ACCIDENT_RATE
        )
        national_pension = drop_under_1_won(
            insurance_base * CalcContext.NATIONAL_PENSION_RATE
        )
        employment_insurance = drop_under_1_won(
            insurance_base * CalcContext.EMPLOYMENT_INSURANCE_RATE
        )
        health_insurance = drop_under_1_won(
            insurance_base * CalcContext.HEALTH_INSURANCE_RATE
        )
        # 노인장기요양보험료 = 건강보험료 × 노인장기요양보험료율
        long_term_care = drop_under_1_won(
            health_insurance * CalcContext.LONG_TERM_CARE_RATE
        )
        wage_bond = drop_under_1_won(
            insurance_base * CalcContext.WAGE_BOND_RATE
        )
        asbestos_relief = drop_under_1_won(
            insurance_base * CalcContext.ASBESTOS_RELIEF_RATE
        )

        insurance_total = drop_under_1_won(
            industrial_accident
            + national_pension
            + employment_insurance
            + health_insurance
            + long_term_care
            + wage_bond
            + asbestos_relief
        )

        # 11) 총합
        total = drop_under_1_won(
            labor_subtotal + insurance_total
        )

        return {
            "base_salary": base_salary,
            "weekly_allowance": weekly_allowance,
            "annual_leave_allowance": annual_leave_allowance,
            "allowance": allowance,
            "bonus": bonus,
            "retirement": retirement,
            "labor_subtotal": labor_subtotal,
            "industrial_accident": industrial_accident,
            "national_pension": national_pension,
            "employment_insurance": employment_insurance,
            "health_insurance": health_insurance,
            "long_term_care": long_term_care,
            "wage_bond": wage_bond,
            "asbestos_relief": asbestos_relief,
            "insurance_total": insurance_total,
            "total_labor_cost": total,
            "allowances": {
                "annual_leave_pay": annual_leave_allowance,
                "overtime_pay": overtime_allowance,
                "holiday_work_pay": holiday_work_allowance,
                "total": allowance,
            },
            "bonus_monthly": bonus,
            "retirement_reserve": retirement,
            "insurance": {
                "industrial_accident": industrial_accident,
                "national_pension": national_pension,
                "employment": employment_insurance,
                "health": health_insurance,
                "long_term_care": long_term_care,
                "wage_bond": wage_bond,
                "asbestos": asbestos_relief,
                "total": insurance_total,
            },
        }

    def _empty_result(self) -> Dict[str, int]:
        return {
            "base_salary": 0,
            "weekly_allowance": 0,
            "annual_leave_allowance": 0,
            "allowance": 0,
            "bonus": 0,
            "retirement": 0,
            "labor_subtotal": 0,
            "industrial_accident": 0,
            "national_pension": 0,
            "employment_insurance": 0,
            "health_insurance": 0,
            "long_term_care": 0,
            "wage_bond": 0,
            "asbestos_relief": 0,
            "insurance_total": 0,
            "total_labor_cost": 0,
            "allowances": {
                "annual_leave_pay": 0,
                "overtime_pay": 0,
                "holiday_work_pay": 0,
                "total": 0,
            },
            "bonus_monthly": 0,
            "retirement_reserve": 0,
            "insurance": {
                "industrial_accident": 0,
                "national_pension": 0,
                "employment": 0,
                "health": 0,
                "long_term_care": 0,
                "wage_bond": 0,
                "asbestos": 0,
                "total": 0,
            },
        }

    def _accumulate_scaled(
        self,
        target: Dict[str, int],
        source: Dict[str, int],
        scale: int,
    ) -> None:
        for key in [
            "base_salary",
            "weekly_allowance",
            "annual_leave_allowance",
            "allowance",
            "bonus",
            "retirement",
            "labor_subtotal",
            "industrial_accident",
            "national_pension",
            "employment_insurance",
            "health_insurance",
            "long_term_care",
            "wage_bond",
            "asbestos_relief",
            "insurance_total",
            "total_labor_cost",
            "bonus_monthly",
            "retirement_reserve",
        ]:
            target[key] += source[key] * scale

        for key in ["annual_leave_pay", "overtime_pay", "holiday_work_pay", "total"]:
            target["allowances"][key] += source["allowances"][key] * scale

        for key in [
            "industrial_accident",
            "national_pension",
            "employment",
            "health",
            "long_term_care",
            "wage_bond",
            "asbestos",
            "total",
        ]:
            target["insurance"][key] += source["insurance"][key] * scale

    def _build_job_line(self, job_code: str, headcount: int, per_person: Dict[str, int]) -> LaborJobLine:
        job_name_map = getattr(self.context, "job_name_map", {})
        job_name = job_name_map.get(job_code, job_code)
        work_days = float(getattr(self.context, "monthly_workdays", Decimal("0")))
        overtime = per_person["allowances"].get("overtime_pay", 0) * headcount
        total = per_person["total_labor_cost"] * headcount
        return LaborJobLine(
            job_code=job_code,
            headcount=headcount,
            job_name=job_name,
            work_days=work_days,
            base_wage=per_person["base_salary"] * headcount,
            allowance=per_person["allowance"] * headcount,
            overtime=overtime,
            total=total,
            base_salary=per_person["base_salary"] * headcount,
            allowances=per_person["allowance"] * headcount,
            insurance_total=per_person["insurance_total"] * headcount,
            labor_subtotal=per_person["labor_subtotal"] * headcount,
            role_total=per_person["labor_subtotal"] * headcount,
        )


    def _calculate_daily_wage_total(self) -> Decimal:
        """
        일급 합계 = 직무별(인원 × 일급) 합산
        """
        total = Decimal("0")

        for job, headcount in self.context.manpower.items():
            # 직무별 일급이 없으면 0으로 처리
            wage = self.context.wage_rate.get(job, Decimal("0"))
            total += headcount * wage

        return total

    def _calculate_base_salary(self, daily_wage_total: Decimal) -> Decimal:
        """
        기본급(월) = 일급 합계 × 월 근무일수(예: 20.6일)
        """
        return daily_wage_total * self.context.monthly_workdays

    def _calculate_bonus(self, base_salary: Decimal) -> Decimal:
        """
        상여금(월) = 기본급 × 400% ÷ 12개월
        """
        return base_salary * BONUS_ANNUAL_RATE / MONTHS_PER_YEAR

    def _calculate_ordinary_hourly_wage(
        self,
        daily_wage_total: Decimal,
        bonus: Decimal,
    ) -> Decimal:
        """
        통상시간급 = 시간급 + (상여금 ÷ 209시간)
        """
        # 시간급 = 일급 합계 ÷ 1일 근무시간 (즉시 절사)
        if self.context.daily_work_hours == 0:
            hourly_wage = Decimal("0")
        else:
            hourly_wage = Decimal(
                drop_under_1_won(daily_wage_total / self.context.daily_work_hours)
            )

        # 상여 시간가산 = 상여금 ÷ 209시간 (즉시 절사)
        if STANDARD_MONTHLY_HOURS == 0:
            bonus_per_hour = Decimal("0")
        else:
            bonus_per_hour = Decimal(
                drop_under_1_won(bonus / STANDARD_MONTHLY_HOURS)
            )

        # 통상시간급 = 시간급 + 상여 시간가산 (즉시 절사)
        return Decimal(
            drop_under_1_won(hourly_wage + bonus_per_hour)
        )

    def _calculate_weekly_allowance(self, ordinary_hourly_wage: Decimal) -> Decimal:
        """
        주휴수당(월) = 통상시간급 × 1일근무시간 × 주휴일수(월 환산)
        """
        return (
            ordinary_hourly_wage
            * self.context.daily_work_hours
            * self.context.weekly_holiday_days
        )

    def _calculate_annual_leave_allowance(self, ordinary_hourly_wage: Decimal) -> Decimal:
        """
        연차수당(월) = 통상시간급 × 1일근무시간 × 연차일수(월 환산)
        """
        return (
            ordinary_hourly_wage
            * self.context.daily_work_hours
            * self.context.annual_leave_days
        )

    def _calculate_retirement(
        self,
        base_salary: Decimal,
        allowance: Decimal,
        bonus: Decimal,
    ) -> Decimal:
        """
        퇴직급여충당금(월) = (기본급 + 제수당 + 상여금) ÷ 12
        """
        retirement_base = base_salary + allowance + bonus
        return retirement_base / MONTHS_PER_YEAR
