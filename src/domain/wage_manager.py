# src/domain/wage_manager.py
"""
연도별 단가 JSON(data/wages_[year].json)과 직무코드→기술등급 매핑(data/job_mapping.json) 로드.
직무코드 입력 시 해당 연도의 기술등급 단가를 반환.

wages_master.json 확장 포맷 지원:
  - 기존: {"등급명": 정부고시일당}
  - 확장: {"등급명": {"govt_daily": 정부고시일당, "md_basic": M/D기본급}}
"""
import json
import logging
import re
from pathlib import Path
from typing import Optional

from src.utils.path_helper import get_data_dir
from src.domain.wage_decomposer import decompose_estimation


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.warning("WageManager: 로드 실패 %s: %s", path, e)
        return {}


class WageManager:
    """
    data/wages_[year].json: 연도별 기술등급 일급
    data/job_mapping.json: 직무코드 → 기술등급 매핑
    """

    def __init__(self, data_dir: Optional[Path] = None):
        self._data_dir = data_dir or get_data_dir()
        self._job_mapping: dict[str, str] = {}
        self._wages_by_year: dict[int, dict[str, int]] = {}
        self._load_job_mapping()
        self._scan_wage_years()

    def _load_job_mapping(self) -> None:
        path = self._data_dir / "job_mapping.json"
        raw = _load_json(path)
        if not isinstance(raw, dict):
            self._job_mapping = {}
            return
        self._job_mapping = {}
        for k, v in raw.items():
            if not k:
                continue
            code = str(k).strip()
            if isinstance(v, dict):
                grade = (v.get("grade") or "").strip() if v.get("grade") else None
            elif isinstance(v, str):
                grade = v.strip() or None
            else:
                grade = None
            if grade:
                self._job_mapping[code] = grade

    def _scan_wage_years(self) -> None:
        self._wages_by_year.clear()
        # 1) wages_master.json (연도별 키 래핑: {"2023": {...}, "2024": {...}})
        master_path = self._data_dir / "wages_master.json"
        master = _load_json(master_path)
        if isinstance(master, dict):
            for key, val in master.items():
                if re.match(r"\d{4}$", str(key)) and isinstance(val, dict):
                    year = int(key)
                    self._wages_by_year[year] = self._normalize_wage_data(val)
        # 2) wages_[year].json (개별 연도 파일 — master보다 우선)
        for f in self._data_dir.glob("wages_*.json"):
            m = re.match(r"wages_(\d{4})\.json", f.name)
            if m:
                year = int(m.group(1))
                data = _load_json(f)
                self._wages_by_year[year] = self._normalize_wage_data(data)

    def _get_wages_for_year(self, year: int) -> dict[str, int]:
        if year in self._wages_by_year:
            return self._wages_by_year[year]
        path = self._data_dir / f"wages_{year}.json"
        data = _load_json(path)
        self._wages_by_year[year] = self._normalize_wage_data(data)
        return self._wages_by_year[year]

    def _normalize_wage_data(self, data) -> dict[str, int]:
        """단가 JSON을 등급명→일급(원) 맵으로 정규화.
        지원 형식:
          - {"등급명": 정부고시일당}                          (기존)
          - {"등급명": {"govt_daily": N, "md_basic": M}}      (확장)
          - {"year": ..., "data": {...}}                      (래핑)
        반환값은 항상 등급명→M/D기본급(인건비계산용) 맵.
        """
        if not isinstance(data, dict):
            return {}
        if "data" in data and isinstance(data.get("data"), dict):
            data = data["data"]
        result = {}
        for k, v in data.items():
            grade = str(k).strip()
            if isinstance(v, dict):
                # 확장 형식: md_basic 우선, 없으면 govt_daily
                result[grade] = int(v.get("md_basic") or v.get("govt_daily") or 0)
            elif isinstance(v, (int, float)):
                result[grade] = int(v)
            else:
                result[grade] = 0
        return result

    def get_wages_for_year(self, year: int) -> dict[str, int]:
        """해당 연도의 기술등급별 일급(원) 표를 반환. 저장 스냅샷용."""
        return dict(self._get_wages_for_year(year))

    def get_wage(self, job_code: str, year: int) -> Optional[int]:
        """
        직무코드와 연도로 일급(원) 반환.
        job_mapping에서 기술등급을 찾고, wages_[year].json에서 해당 등급 단가 반환.
        없으면 None (DB 단가 사용 유지).
        """
        if not job_code or not year:
            return None
        grade = self._job_mapping.get(str(job_code).strip())
        if not grade:
            return None
        wages = self._get_wages_for_year(year)
        return wages.get(grade)

    def get_md_basic(self, job_code: str, year: int) -> Optional[int]:
        """
        wages_master.json(또는 wages_{year}.json)에서 해당 직무의 기술등급 md_basic(원/일)만 반환.
        노무비 상세 기본급 계산용. 원본에 md_basic이 없으면 None.
        """
        if not job_code or not year:
            return None
        grade = self._job_mapping.get(str(job_code).strip())
        if not grade:
            return None
        raw = self.get_raw_grade_data(year)
        grade_data = raw.get(grade) if isinstance(raw.get(grade), dict) else None
        if grade_data is not None and grade_data.get("md_basic") is not None:
            return int(grade_data["md_basic"])
        return None

    def merge_job_rates_for_year(
        self, job_rates: dict[str, int], job_codes: list[str], year: int
    ) -> dict[str, int]:
        """
        기존 job_rates(DB 등)에 연도별 단가를 병합.
        job_mapping에 있고 해당 연도 단가가 있으면 덮어씀.
        """
        out = dict(job_rates)
        for code in job_codes:
            w = self.get_wage(code, year)
            if w is not None and w > 0:
                out[code] = w
        return out

    def list_available_years(self) -> list[int]:
        """wages_*.json 에서 추출한 연도 목록 (내림차순)."""
        if not self._wages_by_year:
            self._scan_wage_years()
        return sorted(self._wages_by_year.keys(), reverse=True)

    def get_grade_detail(self, grade: str, year: int) -> Optional[dict]:
        """등급명과 연도로 상세 분개 결과(기본급추정표) 반환."""
        md = self._get_wages_for_year(year).get(grade)
        if md is None or md == 0:
            return None
        return decompose_estimation(md)

    def get_all_grade_details(self, year: int) -> dict[str, dict]:
        """해당 연도의 모든 등급 상세 분개 결과."""
        wages = self._get_wages_for_year(year)
        return {
            grade: decompose_estimation(md)
            for grade, md in wages.items()
            if md > 0
        }

    def compare_grades_by_year(self, grade: str) -> list[dict]:
        """동일 등급의 연도별 비교 (기본급추정표 산출).
        정부고시 일당은 원본(wages_master 등)의 govt_daily를 사용하고,
        원본에 없을 때만 decompose_estimation의 daily_rate(월합계÷근무일)를 쓴다.
        """
        results = []
        for year in sorted(self._wages_by_year.keys()):
            md = self._wages_by_year[year].get(grade)
            if md is None or md == 0:
                continue
            row = decompose_estimation(md)
            row["year"] = year
            raw = self.get_raw_grade_data(year)
            grade_raw = raw.get(grade) if isinstance(raw.get(grade), dict) else None
            if grade_raw and grade_raw.get("govt_daily") is not None:
                row["govt_daily"] = int(grade_raw["govt_daily"])
            else:
                row["govt_daily"] = row.get("daily_rate")
            results.append(row)
        return results

    def get_raw_grade_data(self, year: int) -> dict:
        """연도별 원본 데이터(govt_daily + md_basic) 반환."""
        path = self._data_dir / f"wages_{year}.json"
        if not path.exists():
            path = self._data_dir / "wages_master.json"
        raw = _load_json(path)
        if not isinstance(raw, dict):
            return {}
        # wages_master.json은 {year: {grade: ...}} 구조
        year_key = str(year)
        if year_key in raw and isinstance(raw[year_key], dict):
            return raw[year_key]
        return raw

    def list_grades(self, year: Optional[int] = None) -> list[str]:
        """사용 가능한 등급명 목록."""
        if year:
            return sorted(self._get_wages_for_year(year).keys())
        all_grades = set()
        for wages in self._wages_by_year.values():
            all_grades.update(wages.keys())
        return sorted(all_grades)

    def reload(self) -> None:
        """job_mapping·연도 목록 재로드."""
        self._load_job_mapping()
        self._wages_by_year.clear()
        self._scan_wage_years()
