# pytest configuration and fixtures
import pytest
from decimal import Decimal
from src.domain.context.calc_context import CalcContext


@pytest.fixture
def basic_calc_context():
    """기본 계산 컨텍스트 - 1명, 일급 20만원"""
    return CalcContext(
        project_name="테스트 프로젝트",
        year=2025,
        manpower={"ENGINEER": Decimal("1")},
        wage_rate={"ENGINEER": Decimal("200000")},  # 일급 20만원
        monthly_workdays=Decimal("20.6"),
        daily_work_hours=Decimal("8"),
        weekly_holiday_days=Decimal("4.33"),
        annual_leave_days=Decimal("1.25"),
        expenses={},
    )


@pytest.fixture
def multi_person_context():
    """다인원 계산 컨텍스트 - 2명"""
    return CalcContext(
        project_name="다인원 테스트",
        year=2025,
        manpower={"ENGINEER": Decimal("2")},
        wage_rate={"ENGINEER": Decimal("200000")},
        monthly_workdays=Decimal("20.6"),
        daily_work_hours=Decimal("8"),
        weekly_holiday_days=Decimal("4.33"),
        annual_leave_days=Decimal("1.25"),
        expenses={},
    )


@pytest.fixture
def multi_role_context():
    """다직무 계산 컨텍스트"""
    return CalcContext(
        project_name="다직무 테스트",
        year=2025,
        manpower={
            "TECH_A": Decimal("1"),
            "TECH_B": Decimal("1"),
        },
        wage_rate={
            "TECH_A": Decimal("300000"),  # 일급 30만원
            "TECH_B": Decimal("150000"),  # 일급 15만원
        },
        monthly_workdays=Decimal("20.6"),
        daily_work_hours=Decimal("8"),
        weekly_holiday_days=Decimal("4.33"),
        annual_leave_days=Decimal("1.25"),
        expenses={},
    )
