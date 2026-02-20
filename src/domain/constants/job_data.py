# src/domain/constants/job_data.py
"""
직무 마스터 데이터 구조 및 lookup.
DB(md_job_role)에서 조회한 목록을 JOB_DATA 형식으로 변환해 UI 자동완성·표시에 사용.
data/job_mapping.json 로드로 직무명·기술등급 즉시 표시.
"""

import json
from pathlib import Path
from typing import Optional

# 미등록 코드 입력 시 표시 문구
UNREGISTERED_LABEL = "미등록 코드"

# 직무코드 → 직무명(title)·기술등급(grade) 매핑 (UI 표시 및 기술등급 라벨용, fallback)
JOB_META: dict[str, dict[str, str]] = {
    "M101": {"title": "소장", "grade": "고급기술자"},
    "E501": {"title": "환경원", "grade": "단순노무종사원"},
}


def get_job_mapping_from_file(data_dir: Optional[Path] = None) -> dict[str, dict[str, str]]:
    """
    data/job_mapping.json에서 직무코드 → {title, grade} 로드.
    형식: {"M101": {"title": "소장", "grade": "고급기술자"}, ...}
    실패 시 JOB_META 반환.
    """
    if data_dir is None:
        from src.utils.path_helper import get_data_dir
        data_dir = get_data_dir()
    path = data_dir / "job_mapping.json"
    if not path.exists():
        return dict(JOB_META)
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except Exception:
        return dict(JOB_META)
    if not isinstance(raw, dict):
        return dict(JOB_META)
    out = {}
    for k, v in raw.items():
        code = (k or "").strip()
        if not code:
            continue
        if isinstance(v, dict):
            title = (v.get("title") or "").strip()
            grade = (v.get("grade") or "").strip()
        elif isinstance(v, str):
            title = v.strip()
            grade = "-"
        else:
            continue
        out[code] = {"title": title or code, "grade": grade or "-"}
    return out if out else dict(JOB_META)


def enrich_roles_with_meta(roles: list[dict]) -> list[dict]:
    """
    DB 조회 roles에 JOB_META의 title/grade 반영.
    반환: job_name·tech_grade가 보강된 복사본 (표시용).
    """
    out = []
    for r in roles:
        row = dict(r)
        code = (row.get("job_code") or "").strip()
        if code in JOB_META:
            row["job_name"] = JOB_META[code]["title"]
            row["tech_grade"] = JOB_META[code]["grade"]
        else:
            row.setdefault("tech_grade", "-")
        out.append(row)
    return out


def build_job_data_lookup(roles: list[dict]) -> dict[str, dict]:
    """
    roles: [{"job_code", "job_name", "tech_grade", "wage_day"?, "wage_hour"?}, ...]
    반환: { job_code: {"job_name", "tech_grade", "wage_day", "wage_hour"}, ... }
    """
    lookup = {}
    for r in roles:
        code = (r.get("job_code") or "").strip()
        if not code:
            continue
        lookup[code] = {
            "job_name": (r.get("job_name") or "").strip(),
            "tech_grade": (r.get("tech_grade") or "-").strip() or "-",
            "wage_day": int(r.get("wage_day", 0)) if r.get("wage_day") is not None else 0,
            "wage_hour": int(r.get("wage_hour", 0)) if r.get("wage_hour") is not None else 0,
        }
    return lookup


def job_codes_for_completer(roles: list[dict]) -> list[str]:
    """자동완성용 직무코드 목록. DB 역할 목록 + JOB_META( job_mapping ) 코드를 합쳐 항상 추천 리스트 제공."""
    codes = {r.get("job_code", "").strip() for r in roles if (r.get("job_code") or "").strip()}
    codes.update(JOB_META.keys())
    return sorted(codes)
