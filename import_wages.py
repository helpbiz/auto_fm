#!/usr/bin/env python
"""
연도별 노임단가 데이터를 JSON에서 데이터베이스로 임포트하는 CLI 도구

사용법:
    python import_wages.py 2025
    python import_wages.py 2024
"""
import sys
import logging
from pathlib import Path

# 프로젝트 경로 추가
sys.path.insert(0, str(Path(__file__).parent / "src"))

from domain.db import get_connection
from utils.json_importer import import_wage_data_for_year

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)


def main():
    if len(sys.argv) < 2:
        print("사용법: python import_wages.py <연도>")
        print("예시: python import_wages.py 2025")
        sys.exit(1)
    
    year = sys.argv[1]
    
    print(f"\n{'='*60}")
    print(f"  연도별 노임단가 임포트 도구")
    print(f"{'='*60}\n")
    print(f"[대상 연도] {year}")
    print(f"[데이터 소스] data/wages_master.json, data/job_mapping.json\n")
    
    try:
        # 데이터베이스 연결
        conn = get_connection()
        
        # 임포트 실행
        import_wage_data_for_year(conn, year)
        
        # 결과 확인
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM md_job_role WHERE scenario_id = ?
        """, (f"year_{year}",))
        count = cursor.fetchone()[0]
        
        print(f"\n{'='*60}")
        print(f"  [OK] 임포트 완료!")
        print(f"{'='*60}")
        print(f"  시나리오 ID: year_{year}")
        print(f"  등록된 직무: {count}개")
        print(f"\n[참고] Auto FM에서 시나리오 'year_{year}'로 불러와서 사용하세요.\n")
        
    except FileNotFoundError as e:
        print(f"\n[오류] 오류: {e}")
        print("\n💡 data/wages_master.json 및 data/job_mapping.json 파일을 확인하세요.")
        sys.exit(1)
    except ValueError as e:
        print(f"\n[오류] 오류: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[오류] 예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
