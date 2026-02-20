"""경비 group_code → 3분류 매핑 상수.

유지보수: 경비코드는 3개 그룹(FIXED, VARIABLE, PASSTHROUGH)으로 구분하며,
그룹별 코드 접두사와 표시 순서를 여기서 일괄 관리한다.
"""

# 그룹 코드 상수 (코드/DB에서 사용)
GROUP_FIXED = "FIXED"
GROUP_VARIABLE = "VARIABLE"
GROUP_PASSTHROUGH = "PASSTHROUGH"

# 표시 순서 (콤보·목록 정렬용)
EXPENSE_GROUP_ORDER: tuple[str, ...] = (GROUP_FIXED, GROUP_VARIABLE, GROUP_PASSTHROUGH)

# 그룹별 경비코드 접두사 (신규 코드 부여 시 참고)
GROUP_CODE_PREFIX: dict[str, str] = {
    GROUP_FIXED: "FIX_",
    GROUP_VARIABLE: "VAR_",
    GROUP_PASSTHROUGH: "PASS_",
}

# group_code → category 매핑
EXPENSE_GROUP_MAP: dict[str, str] = {
    GROUP_FIXED: "fixed",
    GROUP_VARIABLE: "variable",
    GROUP_PASSTHROUGH: "passthrough",
}

# 매핑되지 않는 group_code의 기본 분류 (하위호환)
DEFAULT_CATEGORY = "fixed"

# 카테고리 한글 라벨 (UI 표시용)
CATEGORY_LABELS: dict[str, str] = {
    "fixed": "고정경비",
    "variable": "변동경비",
    "passthrough": "대행비",
}

# group_code → 한글 라벨 (콤보 등에서 그룹명 표시)
GROUP_LABELS: dict[str, str] = {
    GROUP_FIXED: "고정경비",
    GROUP_VARIABLE: "변동경비",
    GROUP_PASSTHROUGH: "대행비",
}


def group_display_order(group_code: str) -> int:
    """그룹 표시 순서(0,1,2). 알 수 없는 그룹은 마지막."""
    try:
        return EXPENSE_GROUP_ORDER.index(group_code.upper())
    except ValueError:
        return len(EXPENSE_GROUP_ORDER)


def classify_expense(group_code: str) -> str:
    """group_code를 3분류 카테고리로 변환한다."""
    return EXPENSE_GROUP_MAP.get(group_code.upper(), DEFAULT_CATEGORY)


def category_label(category: str) -> str:
    """카테고리 코드를 한글 라벨로 변환한다."""
    return CATEGORY_LABELS.get(category, "고정경비")
