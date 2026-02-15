"""시나리오 계산결과에서 관리팀장 제수당 조회. 사용법: python scripts/show_scenario_allowance.py [시나리오명]"""
import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

from src.domain.db import get_connection
from src.domain.scenario_input.service import resolve_scenario_id, list_scenarios
from src.domain.result.service import get_result_snapshot, calculate_result


def _sanitize(name: str) -> str:
    return "".join(c for c in name if c.isalnum() or c in "-_") or "scenario"


def main():
    # 인자: 시나리오명 또는 scenario_id. 없으면 '2023_설계' 또는 목록에서 2023 포함 첫 항목 사용
    conn = get_connection()
    scenarios = list_scenarios(conn)
    scenario_id = None
    if len(sys.argv) > 1:
        scenario_id = resolve_scenario_id(conn, sys.argv[1], _sanitize)
        scenario_name = sys.argv[1]
    else:
        scenario_name = "2023_설계"
        scenario_id = resolve_scenario_id(conn, scenario_name, _sanitize)
        if not any(s[0] == scenario_id for s in scenarios):
            for sid, dname in scenarios:
                if "2023" in sid or "2023" in dname:
                    scenario_id = sid
                    scenario_name = dname
                    break

    out_lines = []
    try:
        out_lines.append(f"시나리오명: {scenario_name!r} → scenario_id: {scenario_id!r}")
        out_lines.append("저장된 시나리오: " + ", ".join(f"{sid}({dname})" for sid, dname in scenarios[:15]))

        snapshot = get_result_snapshot(scenario_id, conn)
        if not snapshot:
            out_lines.append("저장된 계산결과 없음. 계산 실행 중...")
            result = calculate_result(scenario_id, conn)
            labor_rows = result.get("labor_rows", [])
        else:
            labor_rows = snapshot.get("labor_rows", [])

        for row in labor_rows:
            if row.get("job_code") == "MGR02" or row.get("role") == "관리팀장":
                out_lines.append("")
                out_lines.append("========== 관리팀장 제수당 계산결과 ==========")
                out_lines.append(f"  직무(job_code): {row.get('job_code')}")
                out_lines.append(f"  직무명(role):   {row.get('role')}")
                out_lines.append(f"  인원:          {row.get('headcount')}명")
                out_lines.append(f"  기본급:        {row.get('base_salary', 0):,} 원")
                out_lines.append(f"  제수당:        {row.get('allowances', 0):,} 원")
                out_lines.append(f"  상여금:        {row.get('bonus', 0):,} 원")
                out_lines.append(f"  퇴직급여충당금: {row.get('retirement', 0):,} 원")
                out_lines.append(f"  인건비 소계:   {row.get('labor_subtotal', 0):,} 원")
                out_lines.append(f"  산정 금액:     {row.get('role_total', 0):,} 원")
                conn.close()
                text = "\n".join(out_lines)
                out_path = root / "logs" / "scenario_allowance_result.txt"
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(text, encoding="utf-8")
                print(text)
                return

        out_lines.append("")
        out_lines.append("해당 시나리오 노무비 상세에 '관리팀장'(MGR02) 직무가 없습니다.")
        if labor_rows:
            out_lines.append("등록된 직무: " + ", ".join(str(r.get("role")) for r in labor_rows))
    finally:
        conn.close()

    text = "\n".join(out_lines)
    out_path = root / "logs" / "scenario_allowance_result.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
