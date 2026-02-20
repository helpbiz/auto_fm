"""
JSON 파일에서 연도별 노임단가 및 직무 매핑 데이터를 SQLite로 임포트
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any
import sqlite3


class WageDataImporter:
    """연도별 노임단가 JSON 데이터를 데이터베이스로 임포트"""
    
    def __init__(self, db_conn: sqlite3.Connection):
        self.conn = db_conn
        self.logger = logging.getLogger(__name__)
    
    def import_from_json(
        self, 
        wages_json_path: str, 
        job_mapping_json_path: str,
        target_year: str = "2025"
    ) -> None:
        """
        JSON 파일에서 데이터를 로드하여 데이터베이스에 저장
        
        Args:
            wages_json_path: 연도별 노임단가 JSON 파일 경로
            job_mapping_json_path: 직무 매핑 JSON 파일 경로
            target_year: 임포트할 연도 (기본: 2025)
        """
        # 1. JSON 파일 로드
        wages_master = self._load_json(wages_json_path)
        job_mapping = self._load_json(job_mapping_json_path)
        
        if target_year not in wages_master:
            raise ValueError(f"연도 {target_year}의 노임단가 데이터가 없습니다.")
        
        wages_for_year = wages_master[target_year]
        
        # 2. 시나리오 ID 생성 (연도 기반)
        scenario_id = f"year_{target_year}"
        
        # 3. 데이터베이스에 임포트
        self._import_job_roles(scenario_id, job_mapping, wages_for_year)
        
        self.logger.info(f"✅ {target_year}년 노임단가 데이터 임포트 완료 (시나리오: {scenario_id})")
    
    def _load_json(self, file_path: str) -> Dict[str, Any]:
        """JSON 파일 로드"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"JSON 파일을 찾을 수 없습니다: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _import_job_roles(
        self, 
        scenario_id: str, 
        job_mapping: Dict[str, Any],
        wages_for_year: Dict[str, int]
    ) -> None:
        """직무 정보 및 노임단가를 데이터베이스에 저장"""
        
        cursor = self.conn.cursor()
        
        # 기존 데이터 삭제 (시나리오 단위)
        cursor.execute("DELETE FROM md_job_rate WHERE scenario_id = ?", (scenario_id,))
        cursor.execute("DELETE FROM md_job_role WHERE scenario_id = ?", (scenario_id,))
        
        sort_order = 0
        
        for job_code, job_info in job_mapping.items():
            grade = job_info["grade"]
            title = job_info["title"]
            
            # 해당 등급의 노임단가 조회
            if grade not in wages_for_year:
                self.logger.warning(f"⚠️ {job_code} ({grade})의 노임단가 정보 없음. 건너뜀.")
                continue
            
            wage_day = wages_for_year[grade]
            wage_hour = int(wage_day / 8)  # 시간급 = 일급 ÷ 8시간
            
            # md_job_role 삽입
            cursor.execute("""
                INSERT INTO md_job_role (scenario_id, job_code, job_name, sort_order, is_active)
                VALUES (?, ?, ?, ?, 1)
            """, (scenario_id, job_code, title, sort_order))
            
            # md_job_rate 삽입
            cursor.execute("""
                INSERT INTO md_job_rate (scenario_id, job_code, wage_day, wage_hour, allowance_rate_json)
                VALUES (?, ?, ?, ?, '{}')
            """, (scenario_id, job_code, wage_day, wage_hour))
            
            self.logger.debug(f"  ✓ {job_code}: {title} ({grade}) - {wage_day:,}원/일")
            sort_order += 1
        
        self.conn.commit()
        self.logger.info(f"  → 총 {sort_order}개 직무 임포트 완료")


def import_wage_data_for_year(db_conn: sqlite3.Connection, year: str = "2025") -> None:
    """
    편의 함수: 지정된 연도의 노임단가 데이터를 임포트
    
    Args:
        db_conn: SQLite 데이터베이스 연결
        year: 임포트할 연도 (기본: 2025)
    """
    importer = WageDataImporter(db_conn)
    
    # JSON 파일 경로 (프로젝트 루트 기준)
    project_root = Path(__file__).parent.parent.parent
    wages_json = project_root / "data" / "wages_master.json"
    job_mapping_json = project_root / "data" / "job_mapping.json"
    
    importer.import_from_json(
        str(wages_json),
        str(job_mapping_json),
        target_year=year
    )
