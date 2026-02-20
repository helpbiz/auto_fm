"""
직무코드 추가 스크립트
사용법: python add_job_codes.py
"""
import json
from pathlib import Path
from src.domain.db import get_connection
from src.domain.migration_runner import run_migrations

def update_job_mapping():
    """job_mapping.json 업데이트"""
    mapping_file = Path("data/job_mapping.json")

    # 기존 매핑 로드
    if mapping_file.exists():
        with open(mapping_file, 'r', encoding='utf-8') as f:
            mapping = json.load(f)
    else:
        mapping = {}

    # 새 직무코드 추가
    new_jobs = {
        "M102": {"title": "부소장", "grade": "고급기술자"},
        "T301": {"title": "안전관리자", "grade": "중급기술자"},
        "T302": {"title": "품질관리자", "grade": "중급기술자"},
        "D201": {"title": "운전기사", "grade": "단순노무종사원"},
        "E502": {"title": "청소원", "grade": "단순노무종사원"},
    }

    mapping.update(new_jobs)

    # 저장
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    print(f"[OK] job_mapping.json 업데이트 완료 ({len(mapping)}개 직무)")
    print(f"     파일 위치: {mapping_file.absolute()}")

def main():
    print("="*60)
    print("직무코드 추가 스크립트")
    print("="*60 + "\n")

    # 1. job_mapping.json 업데이트
    print("[1] job_mapping.json 업데이트")
    update_job_mapping()
    print()

    # 2. 마이그레이션 실행
    print("[2] DB 마이그레이션 실행")
    conn = get_connection()
    try:
        run_migrations(conn)
        print("[OK] 마이그레이션 완료")
    finally:
        conn.close()
    print()

    # 3. 결과 확인
    print("[3] 추가된 직무코드 확인")
    conn = get_connection()
    try:
        cursor = conn.execute("""
            SELECT scenario_id, job_code, job_name, wage_day
            FROM md_job_role
            JOIN md_job_rate USING (scenario_id, job_code)
            WHERE scenario_id = 'year_2025'
            ORDER BY sort_order
        """)
        rows = cursor.fetchall()

        print("\n2025년 직무코드 목록:")
        print("-" * 60)
        for scenario_id, job_code, job_name, wage_day in rows:
            print(f"  {job_code:6s} | {job_name:12s} | {wage_day:>10,}원/일")
        print("-" * 60)
        print(f"  총 {len(rows)}개 직무")

    finally:
        conn.close()

    print("\n" + "="*60)
    print("완료! 앱을 재시작하면 새 직무코드를 사용할 수 있습니다.")
    print("="*60)

if __name__ == "__main__":
    main()
