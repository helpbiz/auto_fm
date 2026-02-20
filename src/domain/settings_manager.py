# src/domain/settings_manager.py
"""
config.json 기반 설정 관리.
앱 실행 시 파일 없으면 기본값으로 생성, 있으면 로드.
"""
import json
import logging
from decimal import Decimal
from pathlib import Path
from typing import Any

from src.domain.db import get_db_path


CONFIG_FILENAME = "config.json"

# 보험 요율 키 (config 및 CalcContext 속성명과 일치)
INSURANCE_RATE_KEYS = [
    "industrial_accident",
    "national_pension",
    "employment_insurance",
    "health_insurance",
    "long_term_care",
    "wage_bond",
    "asbestos_relief",
]


def get_config_path() -> Path:
    """config.json 경로 (DB와 동일 디렉터리)."""
    return get_db_path().parent / CONFIG_FILENAME


def get_default_config() -> dict[str, Any]:
    """기본 설정 딕셔너리."""
    return {
        "labor": {
            "standard_monthly_hours": 209,
            "bonus_annual_rate": 4.0,
            "months_per_year": 12,
        },
        "insurance_rates": {
            "industrial_accident": 0.009,
            "national_pension": 0.045,
            "employment_insurance": 0.0115,
            "health_insurance": 0.03545,
            "long_term_care": 0.1281,
            "wage_bond": 0.0006,
            "asbestos_relief": 0.00004,
        },
        "indirect": {
            "general_admin_max": 0.10,
            "profit_max": 0.10,
        },
        "safety": {
            "safety_management_rate": 0.0186,  # 안전관리비 지급요율 (예: 1.86% → 0.0186)
        },
        "technician_daily_rates": {},
    }


def _ensure_config_dir() -> None:
    get_config_path().parent.mkdir(parents=True, exist_ok=True)


def load() -> dict[str, Any]:
    """
    설정 로드. config.json 없으면 기본값으로 파일 생성 후 반환.
    """
    path = get_config_path()
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return _merge_with_defaults(data)
        except Exception as e:
            logging.warning("config.json 로드 실패, 기본값 사용: %s", e)

    default = get_default_config()
    save(default)
    return default


def _merge_with_defaults(data: dict[str, Any]) -> dict[str, Any]:
    """기본값과 병합해 누락 키 보완."""
    default = get_default_config()
    out = {}
    for section, section_default in default.items():
        if section not in data or not isinstance(data[section], dict):
            out[section] = dict(section_default)
            continue
        merged = dict(section_default)
        merged.update({k: v for k, v in data[section].items() if k in section_default or section == "technician_daily_rates"})
        out[section] = merged
    return out


def save(config: dict[str, Any]) -> None:
    """설정 저장."""
    _ensure_config_dir()
    path = get_config_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    # 캐시 갱신 (재귀 방지: load() 호출하지 않고 저장된 config로 직접 갱신)
    _cache.clear()
    _cache.update(config)
    logging.info("config 저장 완료: %s", path)


# 메모리 캐시 (load 한 번만 호출)
_cache: dict[str, Any] = {}


def _get_cached() -> dict[str, Any]:
    if not _cache:
        _cache.update(load())
    return _cache


def reload() -> dict[str, Any]:
    """캐시 무시하고 파일에서 다시 로드."""
    _cache.clear()
    return load()


# ---- getters (Decimal/float 반환, 계산 로직에서 사용) ----

def get_standard_monthly_hours() -> Decimal:
    return Decimal(str(_get_cached()["labor"]["standard_monthly_hours"]))


def get_bonus_annual_rate() -> Decimal:
    return Decimal(str(_get_cached()["labor"]["bonus_annual_rate"]))


def get_months_per_year() -> Decimal:
    return Decimal(str(_get_cached()["labor"]["months_per_year"]))


def get_insurance_rate(key: str) -> Decimal:
    """key: industrial_accident, national_pension, ... """
    rates = _get_cached().get("insurance_rates", {})
    return Decimal(str(rates.get(key, get_default_config()["insurance_rates"][key])))


def get_all_insurance_rates() -> dict[str, Decimal]:
    return {k: get_insurance_rate(k) for k in INSURANCE_RATE_KEYS}


def get_general_admin_max() -> Decimal:
    return Decimal(str(_get_cached()["indirect"]["general_admin_max"]))


def get_profit_max() -> Decimal:
    return Decimal(str(_get_cached()["indirect"]["profit_max"]))


def get_technician_daily_rates() -> dict[str, int]:
    """job_code -> 일급(원). """
    raw = _get_cached().get("technician_daily_rates") or {}
    return {k: int(v) for k, v in raw.items() if isinstance(v, (int, float))}


def get_safety_management_rate() -> Decimal:
    """안전관리비 지급요율 (직접노무비 합계 × 이 요율 = 안전관리비)."""
    raw = _get_cached().get("safety", {}) or {}
    return Decimal(str(raw.get("safety_management_rate", get_default_config()["safety"]["safety_management_rate"])))


def get_full_config() -> dict[str, Any]:
    """전체 설정 딕셔너리 (설정 UI 편집용)."""
    return dict(_get_cached())
