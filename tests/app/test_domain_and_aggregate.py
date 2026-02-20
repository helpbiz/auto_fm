"""
Unit tests for app domain models and aggregate snapshot (no PyQt, no DB).
"""
import pytest
from app.domain.models import BaseData, ResultSnapshot


# ----- fixtures (small, no DB) -----

@pytest.fixture
def minimal_base_data():
    return BaseData(
        labor={"job_roles": {"J1": {"headcount": 2, "work_days": 20.6, "work_hours": 8}}},
        expenses={"items": {"FIX_INS_INDUST": {"quantity": 1, "unit_price": 10000}}},
    )


@pytest.fixture
def result_dict_fixture():
    """Minimal result dict as returned by calculate_result (aggregator is object-like dict)."""
    return {
        "aggregator": {
            "labor_total": 1000000,
            "fixed_expense_total": 500000,
            "variable_expense_total": 0,
            "passthrough_expense_total": 0,
            "overhead_cost": 0,
            "profit": 0,
        },
        "labor_rows": [{"job_code": "J1", "role_total": 1000000}],
        "expense_rows": [{"exp_code": "FIX_INS", "row_total": "500000"}],
        "job_breakdown": [],
        "insurance_by_exp_code": {"FIX_INS_INDUST": 10000},
    }


# ----- BaseData -----

def test_base_data_to_canonical(minimal_base_data):
    c = minimal_base_data.to_canonical()
    assert "labor" in c
    assert "expenses" in c
    assert c["labor"]["job_roles"]["J1"]["headcount"] == 2


# ----- ResultSnapshot -----

def test_result_snapshot_from_result_dict(result_dict_fixture):
    snap = ResultSnapshot.from_result_dict(result_dict_fixture)
    assert snap.labor_total == 1000000
    assert snap.fixed_expense_total == 500000
    assert len(snap.labor_rows) == 1
    assert snap.insurance_by_exp_code["FIX_INS_INDUST"] == 10000


def test_result_snapshot_grand_total(result_dict_fixture):
    snap = ResultSnapshot.from_result_dict(result_dict_fixture)
    assert snap.grand_total == 1000000 + 500000


def test_result_snapshot_to_dict(result_dict_fixture):
    snap = ResultSnapshot.from_result_dict(result_dict_fixture)
    d = snap.to_dict()
    assert "aggregator" in d
    assert d["aggregator"]["labor_total"] == 1000000
    assert d["labor_rows"] == result_dict_fixture["labor_rows"]
