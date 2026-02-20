# src/domain/wage_decomposer.py
"""
엔지니어링 노임단가 일급분개·기본급추정 계산기.

정부고시 일당(M/D Rate) → M/D기본급 역산 → 기본급추정표 산출

두 가지 방식 지원:
  1. decompose_estimation(): M/D기본급을 입력으로 기본급추정표 전체 산출 (순방향)
  2. find_md_basic():        정부고시 일당에서 M/D기본급을 역산 (일급분개 Goal Seek)
"""
from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN
from typing import Optional


def _round0(val) -> int:
    """ROUND(val, 0) — Excel ROUND 방식."""
    return int(Decimal(str(val)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _trunc0(val) -> int:
    """TRUNC(val, 0) — Excel TRUNC 방식."""
    return int(Decimal(str(val)).to_integral_value(rounding=ROUND_DOWN))


def _rd10(val) -> int:
    """ROUNDDOWN(val, -1) — 10원 단위 절사 (일급분개 방식)."""
    return int(int(val) // 10 * 10)


# ──────────────────────────────────────────────────────────────
# 1. 기본급추정표 방식 (순방향): M/D기본급 → 전체 비용 산출
# ──────────────────────────────────────────────────────────────

DEFAULT_INSURANCE_RATES = {
    "accident": Decimal("0.009"),
    "national": Decimal("0.045"),
    "employ": Decimal("0.0115"),
    "health": Decimal("0.03545"),
    "longterm": Decimal("0.1281"),
    "wage_bond": Decimal("0.0006"),
    "asbestos": Decimal("0.00004"),
}


def decompose_estimation(
    md_basic: int,
    workdays: Decimal = Decimal("20.6"),
    insurance_rates: Optional[dict] = None,
) -> dict:
    """
    기본급추정표 방식 순방향 계산.

    Args:
        md_basic:  일(M/D)당 기본급 (원)
        workdays:  월평균근무일수 (기본 20.6)
        insurance_rates: 보험요율 override (없으면 DEFAULT_INSURANCE_RATES)

    Returns:
        기본급추정표 전체 항목 dict
    """
    rates = dict(DEFAULT_INSURANCE_RATES)
    if insurance_rates:
        for k, v in insurance_rates.items():
            if k in rates and v is not None:
                rates[k] = Decimal(str(v))

    md = int(md_basic)
    wd = float(workdays)

    base = _round0(md * wd)                          # 기본급(월)
    bonus = _round0(base * 4 / 12)                    # 상여금(월)
    hourly = _round0(md / 8)                          # 시간급
    tongsan_hourly = _round0(hourly + bonus / 209)    # 통상시간급
    tongsan_daily = tongsan_hourly * 8                 # 통상일급

    annual = _trunc0(tongsan_daily * 15 / 12)         # 연차수당
    weekly = _trunc0(tongsan_daily * 52 / 12)         # 주휴수당
    allowance = annual + weekly                       # 제수당 소계

    retire = _round0((base + allowance + bonus) / 12) # 퇴직급여충당금
    subtotal = base + allowance + bonus + retire      # 인건비 소계

    # 보험기준: 산재=(기본급+제수당+상여), 나머지=인건비소계(E18)
    ins_base_accident = base + allowance + bonus
    ins_base_others = subtotal

    accident = _round0(float(ins_base_accident) * float(rates["accident"]))
    national = _round0(float(ins_base_others) * float(rates["national"]))
    employ = _round0(float(ins_base_others) * float(rates["employ"]))
    health = _round0(float(ins_base_others) * float(rates["health"]))
    longterm = _round0(float(health) * float(rates["longterm"]))
    wage_bond = _round0(float(ins_base_others) * float(rates["wage_bond"]))
    asbestos = _round0(float(ins_base_others) * float(rates["asbestos"]))
    ins_total = accident + national + employ + health + longterm + wage_bond + asbestos

    monthly_total = subtotal + ins_total
    daily_rate = _round0(monthly_total / wd)

    return {
        "md_basic": md,
        "base_salary": base,
        "bonus": bonus,
        "hourly_wage": hourly,
        "tongsan_hourly": tongsan_hourly,
        "tongsan_daily": tongsan_daily,
        "annual_leave": annual,
        "weekly_holiday": weekly,
        "allowance": allowance,
        "retirement": retire,
        "salary_subtotal": subtotal,
        "insurance": {
            "accident": accident,
            "national": national,
            "employ": employ,
            "health": health,
            "longterm": longterm,
            "wage_bond": wage_bond,
            "asbestos": asbestos,
            "total": ins_total,
        },
        "monthly_total": monthly_total,
        "daily_rate": daily_rate,
    }


# ──────────────────────────────────────────────────────────────
# 2. 일급분개 방식: 정부고시 일당 → M/D기본급 역산 (Goal Seek)
# ──────────────────────────────────────────────────────────────

def _decompose_ilgup(md: int, wd: float = 20.6) -> int:
    """일급분개 방식(ROUNDDOWN -1)으로 월계→일당 산출. 반환: 일당."""
    base = _rd10(md * wd)
    bonus = _rd10(base * 4 / 12)
    weekly = _rd10(md * 52 / 12)
    tongsan = _rd10((base + weekly + bonus) / 209)
    annual = _rd10(tongsan * 8 * 15 / 12)
    allowance = weekly + annual
    retire = _rd10((base + allowance + bonus) / 12)
    subtotal = base + allowance + bonus + retire
    ins_base = base + allowance + bonus
    ins = (
        _rd10(ins_base * 0.045)
        + _rd10(ins_base * 0.03545)
        + _rd10(ins_base * 0.009)
        + _rd10(ins_base * 0.0115)
        + _rd10(_rd10(ins_base * 0.03545) * 0.1281)
        + _rd10(ins_base * 0.0006)
        + _rd10(ins_base * 0.00004)
    )
    monthly = subtotal + ins
    return _rd10(monthly / wd)


def find_md_basic(
    govt_daily_rate: int,
    workdays: Decimal = Decimal("20.6"),
) -> int:
    """
    정부고시 일당에서 M/D기본급을 역산 (이진탐색 + 근방 스캔).

    일급분개 시트의 ROUNDDOWN(-1) 절사 특성상 정확한 1:1 역산이
    불가능한 경우가 있음. 월계/20.6 ≤ govt_daily_rate인 최대 M/D를 반환.

    Args:
        govt_daily_rate: 정부고시 엔지니어링 일당 (원)
        workdays: 월평균근무일수

    Returns:
        M/D기본급 (원)
    """
    target = int(govt_daily_rate)
    wd = float(workdays)

    lo, hi = 1, target
    best = lo
    for _ in range(200):
        if lo > hi:
            break
        mid = (lo + hi) // 2
        daily = _decompose_ilgup(mid, wd)
        if daily <= target:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1

    # 일급분개의 10원 단위 절사 특성상 정확한 매치가 어려울 수 있음.
    # 근방 ±10 범위 스캔으로 target에 가장 가까운 M/D를 찾음.
    best_diff = abs(_decompose_ilgup(best, wd) - target)
    for cand in range(max(1, best - 10), best + 11):
        d = _decompose_ilgup(cand, wd)
        diff = abs(d - target)
        if diff < best_diff or (diff == best_diff and d <= target):
            best = cand
            best_diff = diff
        if d == target:
            best = cand
            break

    return best


# ──────────────────────────────────────────────────────────────
# 3. 연도별 비교 유틸
# ──────────────────────────────────────────────────────────────

def compare_years(
    grade_data: dict[int, dict[str, int]],
    grade: str,
    workdays: Decimal = Decimal("20.6"),
    insurance_rates: Optional[dict] = None,
) -> list[dict]:
    """
    동일 직종의 연도별 기본급추정표 비교.

    Args:
        grade_data: {year: {grade_name: md_basic, ...}, ...}
        grade: 직종명 (예: "고급기술자")
        workdays: 월평균근무일수
        insurance_rates: 보험요율 (생략 시 기본값)

    Returns:
        연도별 decompose_estimation 결과 리스트 (year 키 포함)
    """
    results = []
    for year in sorted(grade_data.keys()):
        md = grade_data[year].get(grade)
        if md is None:
            continue
        row = decompose_estimation(int(md), workdays, insurance_rates)
        row["year"] = year
        results.append(row)
    return results
