"""제수당 계산내역(주휴/연차/연장/휴일근로) 조회. 사용법: python scripts/show_allowance_detail.py [시나리오_id] [job_code]"""
import sys
from pathlib import Path
from decimal import Decimal

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

from src.domain.db import get_connection
from src.domain.scenario_input.service import list_scenarios, get_scenario_input
from src.domain.masterdata.repo import MasterDataRepo
from src.domain.context.calc_context import CalcContext
from src.domain.calculator.labor import LaborCostCalculator
from src.domain.result.service import (
    DEFAULT_WEEKLY_HOLIDAY_DAYS,
    DEFAULT_ANNUAL_LEAVE_DAYS,
)
from src.domain.wage_manager import WageManager


def main():
    conn = get_connection()
    scenarios = list_scenarios(conn)
    scenario_id = None
    job_code = sys.argv[2] if len(sys.argv) > 2 else "MGR02"
    if len(sys.argv) > 1:
        scenario_id = sys.argv[1]
    else:
        for sid, dname in scenarios:
            if "2023" in sid or "2023" in dname:
                scenario_id = sid
                break
        if not scenario_id and scenarios:
            scenario_id = scenarios[0][0]

    if not scenario_id:
        print("시나리오가 없습니다.")
        conn.close()
        return

    canonical = get_scenario_input(scenario_id, conn)
    repo = MasterDataRepo(conn)
    job_roles = repo.get_job_roles(scenario_id)
    rates_source = repo.get_job_rates(scenario_id)
    job_rates = {r.job_code: r.wage_day for r in (rates_source.values() if isinstance(rates_source, dict) else rates_source or [])}
    labor_inputs = canonical.get("labor", {}).get("job_roles", {})
    wage_year = int(canonical.get("wage_year") or canonical.get("base_year") or 2025)
    wage_manager = WageManager()

    role = next((r for r in job_roles if r.job_code == job_code and r.is_active), None)
    if not role:
        print(f"시나리오 {scenario_id}에 직무 {job_code}가 없습니다. 직무: {[r.job_code for r in job_roles]}")
        conn.close()
        return

    values = labor_inputs.get(role.job_code) or {}
    headcount = Decimal(str(values.get("headcount", 0)))
    if headcount == 0:
        print(f"직무 {job_code}({role.job_name}) 인원이 0입니다.")
        conn.close()
        return

    work_days = Decimal(str(values.get("work_days", 0)))
    work_hours = Decimal(str(values.get("work_hours", 0)))
    overtime_hours = Decimal(str(values.get("overtime_hours", 0)))
    holiday_work_days = Decimal(str(values.get("holiday_work_days", values.get("holiday_work_hours", 0))))

    md_basic = wage_manager.get_md_basic(role.job_code, wage_year)
    wage_day = Decimal(md_basic) if md_basic is not None else Decimal(str(job_rates.get(role.job_code, 0)))

    context = CalcContext(
        project_name=role.job_name,
        year=2025,
        manpower={role.job_code: headcount},
        wage_rate={role.job_code: wage_day},
        monthly_workdays=work_days,
        daily_work_hours=work_hours,
        weekly_holiday_days=DEFAULT_WEEKLY_HOLIDAY_DAYS,
        annual_leave_days=DEFAULT_ANNUAL_LEAVE_DAYS,
        expenses={},
        overtime_hours=overtime_hours,
        holiday_work_days=holiday_work_days,
    )
    context.job_name_map = {role.job_code: role.job_name}

    labor_result = LaborCostCalculator(context).calculate()
    conn.close()

    # 제수당 계산식 (labor.py 기준)
    lines = []
    lines.append("=" * 50)
    lines.append("제수당 계산식 (src/domain/calculator/labor.py)")
    lines.append("=" * 50)
    lines.append("  제수당 = 주휴수당 + 연차수당 + 연장수당 + 휴일근로수당")
    lines.append("")
    lines.append("  1) 주휴수당(월) = 통상시간급 × 1일근무시간 × 주휴일수(월환산) × 0  → 현재 모든 직급 0 적용")
    lines.append("  2) 연차수당(월) = 통상시간급 × 1일근무시간 × 연차일수(월환산)")
    lines.append("  3) 연장수당      = 통상시간급 × 연장시간")
    lines.append("  4) 휴일근로수당 = 통상일급(통상시간급×8) × 휴일근로일수 × 150%")
    lines.append("")

    a = labor_result.get("allowances", {})
    weekly = labor_result.get("weekly_allowance", 0)
    annual = labor_result.get("annual_leave_allowance", 0)
    lines.append(f"시나리오: {scenario_id}  /  직무: {job_code} ({role.job_name})  /  인원: {int(headcount)}명")
    lines.append("")
    lines.append("입력값 (해당 직무)")
    lines.append(f"  월 근무일수:     {work_days}")
    lines.append(f"  1일 근무시간:   {work_hours}h")
    lines.append(f"  연차일수(월환산): {context.annual_leave_days}")
    lines.append(f"  주휴일수(월환산): {context.weekly_holiday_days} (계산 시 0 적용)")
    lines.append(f"  연장시간:       {overtime_hours}h")
    lines.append(f"  휴일근로일수:   {holiday_work_days}일")
    lines.append(f"  일급(M/D):      {int(wage_day):,} 원")
    lines.append("")
    lines.append("제수당 계산내역 (1인 기준)")
    lines.append(f"  주휴수당:       {weekly:>12,} 원  (현재 0 적용)")
    lines.append(f"  연차수당:       {annual:>12,} 원")
    lines.append(f"  연장수당:       {a.get('overtime_pay', 0):>12,} 원")
    lines.append(f"  휴일근로수당:   {a.get('holiday_work_pay', 0):>12,} 원")
    lines.append("  " + "-" * 30)
    lines.append(f"  제수당 합계:    {labor_result.get('allowance', 0):>12,} 원")
    if headcount != 1:
        tot = labor_result.get("allowance", 0) * int(headcount)
        lines.append(f"  × 인원 {int(headcount)}명 = {tot:,} 원")
    lines.append("")

    text = "\n".join(lines)
    out_path = root / "logs" / "allowance_detail.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
