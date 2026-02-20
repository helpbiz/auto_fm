#!/usr/bin/env python3
"""
노무비 금액 검산 스크립트.
- DB 시나리오 1건 로드 후 LaborCostCalculator로 계산
- 동일 입력으로 수식대로 수동 계산하여 비교
"""
import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from decimal import Decimal, ROUND_FLOOR

from src.domain.db import get_connection
from src.domain.migration_runner import run_migrations
from src.domain.masterdata.repo import MasterDataRepo
from src.domain.scenario_input.service import get_scenario_input
from src.domain.context.calc_context import CalcContext
from src.domain.calculator.labor import LaborCostCalculator
from src.domain.result.service import DEFAULT_WEEKLY_HOLIDAY_DAYS, DEFAULT_ANNUAL_LEAVE_DAYS
from src.domain.constants.rounding import drop_under_1_won


def floor_wan(x):
    return int(Decimal(str(x)).to_integral_value(rounding=ROUND_FLOOR))


def verify_one_role(job_code: str, job_name: str, wage_day: int, work_days: float, work_hours: float,
                    overtime_hours: float, holiday_hours: float, headcount: int):
    """1개 직무에 대해 수동 계산 vs LaborCostCalculator 결과 비교."""
    wage_day = Decimal(str(wage_day))
    work_days = Decimal(str(work_days))
    work_hours = Decimal(str(work_hours))
    overtime_hours = Decimal(str(overtime_hours))
    holiday_hours = Decimal(str(holiday_hours))

    # 1인당 일급 (인원 1명 기준 검산)
    daily_wage_total = wage_day

    # --- 수동 계산 (1인 기준) ---
    base_salary_man = floor_wan(daily_wage_total * work_days)
    bonus_man = floor_wan(Decimal(base_salary_man) * Decimal("4") / Decimal("12"))
    # 통상시간급
    hourly_wage = floor_wan(daily_wage_total / work_hours)
    bonus_per_hour = floor_wan(Decimal(bonus_man) / Decimal("209"))
    ordinary_hourly_wage = Decimal(floor_wan(hourly_wage + bonus_per_hour))
    # 제수당
    weekly_allowance = floor_wan(ordinary_hourly_wage * work_hours * DEFAULT_WEEKLY_HOLIDAY_DAYS)
    annual_leave_allowance = floor_wan(ordinary_hourly_wage * work_hours * DEFAULT_ANNUAL_LEAVE_DAYS)
    overtime_allowance = floor_wan(ordinary_hourly_wage * overtime_hours)
    holiday_work_allowance = floor_wan(ordinary_hourly_wage * holiday_hours)
    allowance_man = floor_wan(
        weekly_allowance + annual_leave_allowance + overtime_allowance + holiday_work_allowance
    )
    retirement_man = floor_wan(
        (Decimal(base_salary_man) + Decimal(allowance_man) + Decimal(bonus_man)) / Decimal("12")
    )
    labor_subtotal_man = floor_wan(
        base_salary_man + allowance_man + bonus_man + retirement_man
    )
    insurance_base = base_salary_man + allowance_man + bonus_man
    # 보험 요율 (CalcContext와 동일)
    industrial = floor_wan(Decimal(insurance_base) * Decimal("0.009"))
    national_pension = floor_wan(Decimal(insurance_base) * Decimal("0.045"))
    employment = floor_wan(Decimal(insurance_base) * Decimal("0.0115"))
    health = floor_wan(Decimal(insurance_base) * Decimal("0.03545"))
    long_term_care = floor_wan(Decimal(health) * Decimal("0.1281"))
    wage_bond = floor_wan(Decimal(insurance_base) * Decimal("0.0006"))
    asbestos = floor_wan(Decimal(insurance_base) * Decimal("0.00004"))
    insurance_total_man = industrial + national_pension + employment + health + long_term_care + wage_bond + asbestos
    total_man = floor_wan(labor_subtotal_man + insurance_total_man)

    # --- Calculator 호출 ---
    context = CalcContext(
        project_name=job_name,
        year=2025,
        manpower={job_code: Decimal(headcount)},
        wage_rate={job_code: wage_day},
        monthly_workdays=work_days,
        daily_work_hours=work_hours,
        weekly_holiday_days=DEFAULT_WEEKLY_HOLIDAY_DAYS,
        annual_leave_days=DEFAULT_ANNUAL_LEAVE_DAYS,
        expenses={},
        overtime_hours=overtime_hours,
        holiday_work_hours=holiday_hours,
    )
    context.job_name_map = {job_code: job_name}
    calc_result = LaborCostCalculator(context).calculate()

    lines = calc_result.get("job_lines", [])
    if not lines:
        return False, ["job_lines 없음"], {}

    line = lines[0]
    scale = max(int(headcount), 1)
    base_salary_calc_1 = line.base_salary // scale
    allowance_calc_1 = line.allowances // scale
    labor_subtotal_calc_1 = line.labor_subtotal // scale
    insurance_calc_1 = line.insurance_total // scale
    total_calc = line.total  # 인건비+보험 전체
    total_calc_1 = total_calc // scale

    ok = True
    msgs = []
    if base_salary_man != base_salary_calc_1:
        ok = False
        msgs.append(f"기본급: 수동={base_salary_man:,} 계산기(1인)={base_salary_calc_1:,}")
    if allowance_man != allowance_calc_1:
        ok = False
        msgs.append(f"제수당: 수동={allowance_man:,} 계산기(1인)={allowance_calc_1:,}")
    if labor_subtotal_man != labor_subtotal_calc_1:
        ok = False
        msgs.append(f"인건비소계: 수동={labor_subtotal_man:,} 계산기(1인)={labor_subtotal_calc_1:,}")
    if insurance_total_man != insurance_calc_1:
        ok = False
        msgs.append(f"보험료: 수동={insurance_total_man:,} 계산기(1인)={insurance_calc_1:,}")
    if total_man != total_calc_1:
        ok = False
        msgs.append(f"산정금액(1인, 인건비+보험): 수동={total_man:,} 계산기(1인)={total_calc_1:,}")

    return ok, msgs, {
        "job_name": job_name,
        "wage_day": int(wage_day),
        "work_days": float(work_days),
        "headcount": headcount,
        "manual": {"base_salary": base_salary_man, "allowance": allowance_man, "labor_subtotal": labor_subtotal_man, "insurance": insurance_total_man, "total_1p": total_man},
        "calc_total": total_calc,
    }


def main():
    conn = get_connection()
    try:
        run_migrations(conn)
        repo = MasterDataRepo(conn)
        # default 시나리오에 입력이 있으면 사용, 없으면 가상 입력으로 검산
        canonical = get_scenario_input("default", conn)
        job_roles = repo.get_job_roles("default")
        rates = repo.get_job_rates("default")
        job_rates = {code: r.wage_day for code, r in rates.items()}

        labor = canonical.get("labor", {}).get("job_roles", {})
        verified = 0
        failed = []
        for role in job_roles:
            if not getattr(role, "is_active", 1):
                continue
            values = labor.get(role.job_code)
            if not isinstance(values, dict):
                continue
            hc = int(values.get("headcount", 0))
            if hc == 0:
                continue
            wage = job_rates.get(role.job_code, 0)
            wd = float(values.get("work_days", 20.6))
            wh = float(values.get("work_hours", 8))
            ot = float(values.get("overtime_hours", 0))
            hw = float(values.get("holiday_work_hours", 0))
            ok, msg_or_msgs, detail = verify_one_role(
                role.job_code, role.job_name, wage, wd, wh, ot, hw, hc
            )
            if ok:
                verified += 1
                print(f"[OK] {role.job_name}({role.job_code}) 인원={hc} 일급={wage:,}원 → 산정금액(총)={detail['calc_total']:,}원")
            else:
                failed.append((role.job_name, msg_or_msgs))
                print(f"[FAIL] {role.job_name}({role.job_code})")
                for m in msg_or_msgs:
                    print("  ", m)

        if not labor or (verified == 0 and len(failed) == 0):
            # DB에 직무 입력이 없거나 인원 있는 직무가 없으면 가상 입력으로 1건 검산
            print("시나리오 입력 없음 또는 인원 0 -> 관리소장(MGR01) 가상 입력으로 검산")
            wage = job_rates.get("MGR01", 240340)  # 2025 기술사 md_basic
            ok, msg_or_msgs, detail = verify_one_role(
                "MGR01", "관리소장", wage, 20.6, 8, 0, 0, 1
            )
            if ok:
                verified += 1
                print(f"[OK] 관리소장(가상) 일급={wage:,}원 -> 산정금액(1인)={detail['manual']['total_1p']:,}원 (수동=계산기 일치)")
            else:
                failed.append(("관리소장(가상)", msg_or_msgs))
                print("[FAIL]", msg_or_msgs)

        print("---")
        print(f"검산 완료: 통과 {verified}건, 실패 {len(failed)}건")
        if verified > 0 and len(failed) == 0:
            print("결론: 수식대로 금액이 정상 산출됩니다.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
