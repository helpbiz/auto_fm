"""시트별 셀 좌표 상수 — auto_fm_fin.xlsx 템플릿 기준."""

# ---------------------------------------------------------------------------
# 갑지
# ---------------------------------------------------------------------------
GAPJI_CELLS = {
    "total_3year": "L11",   # 총액(3개년)
    "year1": "L14",         # 1차분(2024년)
    "year2": "L17",         # 2차분(2025년)
    "year3": "L20",         # 3차분(2026년)
}

# ---------------------------------------------------------------------------
# 용역원가집계
# ---------------------------------------------------------------------------
SERVICE_COST_SUMMARY_CELLS = {
    "y1_monthly": "B8",  "y1_months": "C8",  "y1_annual": "D8",
    "y2_monthly": "B9",  "y2_months": "C9",  "y2_annual": "D9",
    "y3_monthly": "B10", "y3_months": "C10", "y3_annual": "D10",
    "grand_total": "D12",
}

# ---------------------------------------------------------------------------
# 용역원가(XX년) — 공통 상단 행 (G열=월, H열=연)
# ---------------------------------------------------------------------------
YEARLY_COMMON_ROWS: dict[str, int] = {
    "base_salary": 7,
    "allowances_subtotal": 11,
    "bonus": 12,
    "retirement": 13,
    "labor_total": 14,
    # 보험료 7종
    "ins_indust": 15,
    "ins_pension": 16,
    "ins_employ": 17,
    "ins_health": 18,
    "ins_longterm": 19,
    "ins_wage": 20,
    "ins_asbestos": 21,
    # 복리후생비
    "welfare": 22,
    # 기타 고정경비
    "safety": 23,
    "training": 24,
    "supplies": 25,
    "travel": 26,
    "telecom": 27,
}

# 용역원가(XX년) — 하단 행 오프셋 (시트별 차이)
YEARLY_BOTTOM_OFFSETS: dict[str, dict[str, int]] = {
    "용역원가(24년)": {
        "fixed_subtotal": 28,
        "net_service": 29,
        "overhead": 30,
        "profit": 31,
        "service_cost": 32,
        "contingency": 33,
        "fixed_grand": 34,
        "var_material": 35,
        "var_repair": 36,
        "var_inspect": 37,
        "var_safety_agent": 38,
        "var_vehicle": 39,
        "var_security": 40,
        "var_transport": 41,
        "var_subtotal": 42,
        "var_service": 43,
        "var_contingency": 44,
        "var_grand": 45,
        "pass_electric": 46,
        "pass_water": 47,
        "pass_facility": 48,
        "pass_subtotal": 49,
        "all_grand": 50,
        "total": 51,
    },
    "용역원가(25년) ": {
        "fixed_subtotal": 29,
        "net_service": 30,
        "overhead": 31,
        "profit": 32,
        "service_cost": 33,
        "contingency": 34,
        "fixed_grand": 35,
        "var_material": 36,
        "var_repair": 37,
        "var_inspect": 38,
        "var_safety_agent": 39,
        "var_vehicle": 40,
        "var_security": 41,
        "var_transport": 42,
        "var_subtotal": 43,
        "var_service": 44,
        "var_contingency": 45,
        "var_grand": 46,
        "pass_electric": 47,
        "pass_water": 48,
        "pass_facility": 49,
        "pass_subtotal": 50,
        "all_grand": 51,
        "total": 52,
    },
    "용역원가(26년)": {
        "fixed_subtotal": 28,
        "net_service": 29,
        "overhead": 30,
        "profit": 31,
        "service_cost": 32,
        "contingency": 33,
        "fixed_grand": 34,
        "var_material": 35,
        "var_repair": 36,
        "var_inspect": 37,
        "var_safety_agent": 38,
        "var_vehicle": 39,
        "var_security": 40,
        "var_transport": 41,
        "var_subtotal": 42,
        "var_service": 43,
        "var_contingency": 44,
        "var_grand": 45,
        "pass_electric": 46,
        "pass_water": 47,
        "pass_facility": 48,
        "pass_subtotal": 49,
        "all_grand": 50,
        "total": 51,
    },
}

# 변동경비 행 키 → exp_code 매핑 (용역원가 시트 변동 섹션용)
YEARLY_VAR_KEYS_TO_EXP_CODE: list[tuple[str, str]] = [
    ("var_material", "VAR_MATERIAL"),
    ("var_repair", "VAR_REPAIR"),
    ("var_inspect", "VAR_INSPECT"),
    ("var_safety_agent", "VAR_SAFETY_AGENT"),
    ("var_vehicle", "VAR_VEHICLE"),
    ("var_security", "VAR_SECURITY"),
    ("var_transport", "VAR_TRANSPORT"),
]

YEARLY_PASS_KEYS_TO_EXP_CODE: list[tuple[str, str]] = [
    ("pass_electric", "PASS_ELECTRIC"),
    ("pass_water", "PASS_WATER"),
    ("pass_facility", "PASS_FACILITY_INS"),
]

# ---------------------------------------------------------------------------
# 인건비집계
# ---------------------------------------------------------------------------
LABOR_SUMMARY_COLS = {
    "base_per_person": "F",  "base_headcount": "G",  "base_amount": "H",
    "allow_per_person": "I", "allow_headcount": "J",  "allow_amount": "K",
    "bonus_per_person": "L", "bonus_headcount": "M",  "bonus_amount": "N",
    "retire_per_person": "O","retire_headcount": "P",  "retire_amount": "Q",
    "total_per_person": "R", "total_headcount": "S",  "total_amount": "T",
}
LABOR_DATA_START_ROW = 8
LABOR_TOTAL_ROW = 25

# ---------------------------------------------------------------------------
# 경비집계
# ---------------------------------------------------------------------------
# 행 → exp_code 매핑 (F열에 월액 기입)
EXPENSE_SUMMARY_ROW_MAP: dict[int, str | list[str]] = {
    7: "FIX_INS_INDUST",
    8: "FIX_INS_PENSION",
    9: "FIX_INS_EMPLOY",
    10: "FIX_INS_HEALTH",
    11: "FIX_INS_LONGTERM",
    12: "FIX_INS_WAGE",
    13: "FIX_INS_ASBESTOS",
    # 14 = 보험소계 (sum 7~13)
    15: ["FIX_WEL_CLOTH", "FIX_WEL_MEAL", "FIX_WEL_CHECKUP", "FIX_WEL_MEDICINE"],
    16: "FIX_SAFETY",
    17: "FIX_TRAINING",
    18: "FIX_SUPPLIES",
    19: "FIX_TRAVEL",
    20: "FIX_TELECOM",
    # 22 = 고정경비계
    23: "VAR_MATERIAL",
    24: "VAR_REPAIR",
    25: "VAR_INSPECT",
    26: "VAR_SAFETY_AGENT",
    27: "VAR_VEHICLE",
    28: "VAR_SECURITY",
    29: "VAR_TRANSPORT",
    # 30 = 변동경비계
    31: "PASS_ELECTRIC",
    32: "PASS_WATER",
    33: "PASS_FACILITY_INS",
    # 34 = 대행비계
    # 35 = 합계
}
EXPENSE_SUMMARY_COL = "F"
EXPENSE_INS_SUBTOTAL_ROW = 14
EXPENSE_FIXED_TOTAL_ROW = 22
EXPENSE_VAR_TOTAL_ROW = 30
EXPENSE_PASS_TOTAL_ROW = 34
EXPENSE_GRAND_TOTAL_ROW = 35

# ---------------------------------------------------------------------------
# 일반관리비
# ---------------------------------------------------------------------------
OVERHEAD_CELLS = {
    "labor": "B8",
    "fixed": "C8",
    "sum": "D8",
    "rate": "E8",
    "amount": "F8",
    "total": "F10",
}

# ---------------------------------------------------------------------------
# 이윤
# ---------------------------------------------------------------------------
PROFIT_CELLS = {
    "labor": "B8",
    "fixed": "C8",
    "overhead": "D8",
    "sum": "E8",
    "rate": "F8",
    "amount": "G8",
    "total": "G10",
}
