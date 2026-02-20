# src/domain/data_manager.py
"""
data/wages_master.json(연도별 기술등급 단가)와 data/job_mapping.json(직무코드→기술등급) 참조.
직무코드·연도로 일급 조회 및 job_rates 병합 API 제공.
"""
import json
import logging
from pathlib import Path
from typing import Optional

from src.utils.path_helper import get_data_dir


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.warning("DataManager: 로드 실패 %s: %s", path, e)
        return {}


class DataManager:
    """
    data/wages_master.json: { "2023": {"고급기술자": 293753, ...}, "2024": {...}, ... }
    data/job_mapping.json: { "M101": {"title": "...", "grade": "고급기술자", ...}, ... }
    """

    def __init__(self, data_dir: Optional[Path] = None):
        self._data_dir = data_dir or get_data_dir()
        self._job_mapping: dict = {}
        self._wages_master: dict = {}
        self._load()

    def _load(self) -> None:
        self._load_job_mapping()
        self._load_wages_master()

    def _load_job_mapping(self) -> None:
        path = self._data_dir / "job_mapping.json"
        raw = _load_json(path)
        if isinstance(raw, dict):
            self._job_mapping = {str(k).strip(): v for k, v in raw.items() if k}
        else:
            self._job_mapping = {}

    def _normalize_wage_map(self, d: dict) -> dict[str, int]:
        """등급명 → 일급(원) 맵으로 정규화."""
        if not isinstance(d, dict):
            return {}
        return {
            str(k).strip(): int(v) if isinstance(v, (int, float)) else 0
            for k, v in d.items()
        }

    def _load_wages_master(self) -> None:
        path = self._data_dir / "wages_master.json"
        raw = _load_json(path)
        if not isinstance(raw, dict):
            self._wages_master = {}
            return
        self._wages_master = {}

        # 단일 연도 형식: { "year": 2024, "data": { "고급기술자": 293753, ... } }
        if "year" in raw and "data" in raw and isinstance(raw.get("data"), dict):
            year = raw.get("year")
            try:
                y = int(year)
                self._wages_master[y] = self._normalize_wage_map(raw["data"])
            except (TypeError, ValueError):
                pass
            return

        # 연도별 형식: { "2023": {...}, "2024": {...} } 또는 "2024": { "year": 2024, "data": {...} }
        for year_str, grades_dict in raw.items():
            if not isinstance(grades_dict, dict):
                continue
            try:
                year = int(year_str)
            except (TypeError, ValueError):
                continue
            # 래핑 형식: { "year": 2024, "data": { ... } }
            if "data" in grades_dict and isinstance(grades_dict.get("data"), dict):
                self._wages_master[year] = self._normalize_wage_map(grades_dict["data"])
            else:
                self._wages_master[year] = self._normalize_wage_map(grades_dict)

    def _grade_for_job(self, job_code: str) -> Optional[str]:
        entry = self._job_mapping.get(str(job_code).strip())
        if entry is None:
            return None
        if isinstance(entry, dict):
            return (entry.get("grade") or "").strip() or None
        if isinstance(entry, str):
            return entry.strip() or None
        return None

    def get_wage(self, job_code: str, year: int) -> Optional[int]:
        """
        직무코드와 연도로 일급(원) 반환.
        job_mapping에서 기술등급을 찾고, wages_master에서 해당 연도·등급 단가 반환.
        """
        if not job_code or not year:
            return None
        grade = self._grade_for_job(job_code)
        if not grade:
            return None
        wages = self._wages_master.get(year, {})
        return wages.get(grade)

    def get_wages_for_year(self, year: int) -> dict[str, int]:
        """지정 연도의 기술등급별 일급 맵 반환."""
        return dict(self._wages_master.get(year, {}))

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
        """wages_master에서 연도 목록 (내림차순)."""
        return sorted(self._wages_master.keys(), reverse=True)

    def reload(self) -> None:
        """JSON 재로드."""
        self._load()
