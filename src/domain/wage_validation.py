# src/domain/wage_validation.py
"""
wages_master.json 키(기술등급명)와 JSON 파일(job_mapping 등)에 정의된 기술등급 이름 일치 여부 검사.
"""
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from src.utils.path_helper import get_data_dir


@dataclass
class GradeValidationResult:
    """기술등급 유효성 검사 결과."""
    valid: bool
    """모든 매핑 등급이 wages 쪽에 존재하면 True."""
    valid_grade_names: set[str]
    """wages_master(또는 wages_*.json)에 정의된 기술등급명 집합."""
    grades_in_mapping: set[str]
    """매핑 파일에 사용된 기술등급명 집합."""
    missing_grades: set[str]
    """매핑에는 있으나 wages에 없는 등급명 (불일치 목록)."""
    extra_in_wages: set[str]
    """wages에는 있으나 매핑에서 미사용인 등급명 (참고용)."""


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def get_valid_grade_names_from_wages_master(raw: dict) -> set[str]:
    """
    wages_master.json 로드 결과에서 모든 연도에 걸쳐 등장하는 기술등급명(키) 집합 반환.
    형식: { "2023": {"고급기술자": 293753, ...}, "2024": {...} } 또는
          { "year": 2024, "data": { "고급기술자": 293753, ... } }
    """
    names: set[str] = set()
    if not isinstance(raw, dict):
        return names
    # 단일 연도 형식
    if "year" in raw and "data" in raw and isinstance(raw.get("data"), dict):
        for k in raw["data"].keys():
            if k and str(k).strip():
                names.add(str(k).strip())
        return names
    # 연도별 형식
    for _year_key, grades_dict in raw.items():
        if not isinstance(grades_dict, dict):
            continue
        if "data" in grades_dict and isinstance(grades_dict.get("data"), dict):
            d = grades_dict["data"]
        else:
            d = grades_dict
        for k in d.keys():
            if k and str(k).strip():
                names.add(str(k).strip())
    return names


def get_valid_grade_names_from_wages_year_files(data_dir: Path) -> set[str]:
    """
    data/wages_YYYY.json 파일들에서 모든 기술등급명(키) 집합 반환.
    """
    import re
    names: set[str] = set()
    for f in data_dir.glob("wages_*.json"):
        if not re.match(r"wages_\d{4}\.json", f.name):
            continue
        data = _load_json(f)
        if not isinstance(data, dict):
            continue
        if "data" in data and isinstance(data.get("data"), dict):
            d = data["data"]
        else:
            d = data
        for k in d.keys():
            if k and str(k).strip():
                names.add(str(k).strip())
    return names


def get_grade_names_from_job_mapping(raw: dict) -> set[str]:
    """
    job_mapping.json 로드 결과에서 사용된 기술등급(grade) 이름 집합 반환.
    형식: { "M101": {"title": "...", "grade": "고급기술자"}, ... } 또는 { "M101": "고급기술자" }
    """
    names: set[str] = set()
    if not isinstance(raw, dict):
        return names
    for _code, entry in raw.items():
        if entry is None:
            continue
        if isinstance(entry, dict):
            grade = (entry.get("grade") or "").strip()
        elif isinstance(entry, str):
            grade = (entry or "").strip()
        else:
            continue
        if grade:
            names.add(grade)
    return names


def validate_grade_names(
    valid_grade_names: set[str],
    grades_to_check: set[str],
) -> GradeValidationResult:
    """
    매핑 쪽 등급명이 wages 쪽 키(유효 등급명)와 일치하는지 검사.

    :param valid_grade_names: wages_master.json(또는 wages_*.json)에 정의된 기술등급명 집합.
    :param grades_to_check: 검사 대상 등급명 집합(예: job_mapping에서 추출한 grade 목록).
    :return: 검사 결과(일치 여부, 불일치 목록 등).
    """
    missing = grades_to_check - valid_grade_names
    extra = valid_grade_names - grades_to_check
    return GradeValidationResult(
        valid=len(missing) == 0,
        valid_grade_names=set(valid_grade_names),
        grades_in_mapping=set(grades_to_check),
        missing_grades=missing,
        extra_in_wages=extra,
    )


def validate_wage_data(
    data_dir: Optional[Path] = None,
    *,
    use_wages_master: bool = True,
    use_wages_year_files: bool = False,
) -> GradeValidationResult:
    """
    data 디렉터리의 wages_master.json(또는 wages_*.json)과 job_mapping.json을 읽어
    job_mapping에 정의된 기술등급명이 wages 쪽 키와 일치하는지 검사.

    :param data_dir: 데이터 디렉터리. None이면 get_data_dir() 사용.
    :param use_wages_master: True면 data/wages_master.json 기준으로 유효 등급 수집.
    :param use_wages_year_files: True면 data/wages_YYYY.json 파일들 기준으로 유효 등급 수집.
    :return: 기술등급 일치 여부 결과.
    """
    data_dir = data_dir or get_data_dir()
    valid_grade_names: set[str] = set()

    if use_wages_master:
        path = data_dir / "wages_master.json"
        raw = _load_json(path)
        valid_grade_names |= get_valid_grade_names_from_wages_master(raw)

    if use_wages_year_files:
        valid_grade_names |= get_valid_grade_names_from_wages_year_files(data_dir)

    path = data_dir / "job_mapping.json"
    mapping_raw = _load_json(path)
    grades_in_mapping = get_grade_names_from_job_mapping(mapping_raw)

    return validate_grade_names(valid_grade_names, grades_in_mapping)
