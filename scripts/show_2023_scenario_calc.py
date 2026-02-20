#!/usr/bin/env python3
"""
'2023_설계' 시나리오에 노임단가 기준년도 2023이 적용될 때 실제 계산된 내용을 출력합니다.
- 시나리오 ID: 시나리오명 "2023_설계" → sanitize 시 "2023_" (한글 제거)
- wage_year=2023 → wages_master.json 2023년 md_basic 적용
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.domain.db import get_connection
from src.domain.migration_runner import run_migrations
from src.domain.scenario_input.service import get_scenario_input, list_scenario_ids
from src.domain.result.service import calculate_result
from src.domain.wage_manager import WageManager


def sanitize(name: str) -> str:
    return "".join(ch for ch in name if ch.isalnum() or ch in ("-", "_")) or "scenario"


def main():
    scenario_name = "2023_설계"
    scenario_id = sanitize(scenario_name)  # "2023_"
    wage_year = 2023

    conn = get_connection()
    try:
        run_migrations(conn)
        ids = list_scenario_ids(conn)
        if scenario_id not in ids:
            print(f"[안내] 시나리오 ID '{scenario_id}' (이름: {scenario_name})가 DB에 없습니다.")
            print(f"       등록된 시나리오: {ids}")
            print()
            print("=== 2023년 노임단가(md_basic) 적용표 (wages_master.json) ===")
            wm = WageManager()
            raw = wm.get_raw_grade_data(wage_year)
            for grade, data in sorted(raw.items()):
                if isinstance(data, dict) and "md_basic" in data:
                    print(f"  {grade}: {data['md_basic']:,} 원/일")
            print()
            print("=== 직무별 2023 md_basic (job_mapping 기준) ===")
            import json
            job_path = ROOT / "data" / "job_mapping.json"
            if job_path.exists():
                job_mapping = json.loads(job_path.read_text(encoding="utf-8"))
                for code, info in sorted(job_mapping.items()):
                    if isinstance(info, dict) and "grade" in info and "title" in info:
                        g = info["grade"]
                        md = wm.get_md_basic(code, wage_year)
                        print(f"  {code} {info['title']} ({g}): {md or 0:,} 원/일")
            return

        canonical = get_scenario_input(scenario_id, conn)
        actual_wage_year = canonical.get("wage_year") or canonical.get("base_year") or 2025
        actual_wage_year = int(actual_wage_year) if actual_wage_year else 2025

        print(f"시나리오: {scenario_name} (ID: {scenario_id})")
        print(f"노임단가 기준년도: {actual_wage_year}")
        print()

        result = calculate_result(scenario_id, conn)
        labor_rows = result["labor_rows"]
        aggregator = result["aggregator"]

        wm = WageManager()
        print("=" * 70)
        print("노무비 상세 탭 계산 결과 (적용 일급 = 해당 연도 md_basic)")
        print("=" * 70)
        for row in labor_rows:
            role = row.get("role", "")
            job_code = row.get("job_code", "")
            headcount = row.get("headcount", 0)
            applied_md_basic = wm.get_md_basic(job_code, actual_wage_year) if job_code else None
            print(f"\n▶ {role} (직무코드: {job_code}, 인원: {headcount})")
            print(f"    적용 일급(md_basic, {actual_wage_year}년): {applied_md_basic or 0:,} 원/일")
            print(f"    기본급(월):     {row.get('base_salary', 0):,} 원")
            print(f"    상여금(월):     {row.get('bonus', 0):,} 원")
            print(f"    제수당(월):     {row.get('allowances', 0):,} 원")
            print(f"    퇴직급여충당금: {row.get('retirement', 0):,} 원")
            print(f"    인건비 소계:    {row.get('labor_subtotal', 0):,} 원")
            print(f"    산정 금액:      {row.get('role_total', 0):,} 원")

        print()
        print("=" * 70)
        print("집계 합계")
        print("=" * 70)
        a = aggregator
        print(f"  노무비 합계:     {a.labor_total:,} 원")
        print(f"  경비(고정):      {a.fixed_expense_total:,} 원")
        print(f"  경비(변동):      {a.variable_expense_total:,} 원")
        print(f"  경비(통과):      {a.passthrough_expense_total:,} 원")
        print(f"  간접비:         {a.overhead_cost:,} 원")
        print(f"  이익:           {a.profit:,} 원")
        print(f"  총계:           {a.grand_total:,} 원")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
