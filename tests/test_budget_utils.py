
import pytest

from src.utils.budget_utils import (
    calculate_budget,
    extract_budget,
    extract_costs_from_text,
    format_budget_analysis,
)


def test_within_budget():
    result = calculate_budget(15000, {
        "Travel": 3000,
        "Hotel": 4000,
        "Food": 2500,
    })

    assert result["estimated_total"] == 9500
    assert result["remaining_budget"] == 5500
    assert result["status"] == "WITHIN BUDGET"


def test_slightly_over_budget():
    result = calculate_budget(15000, {
        "Travel": 5000,
        "Hotel": 6000,
        "Food": 5000,
    })

    assert result["estimated_total"] == 16000
    assert result["difference"] == 1000
    assert result["status"] == "SLIGHTLY OVER BUDGET"


def test_significantly_over_budget():
    result = calculate_budget(15000, {
        "Travel": 8000,
        "Hotel": 10000,
        "Food": 5000,
    })

    assert result["estimated_total"] == 23000
    assert result["status"] == "SIGNIFICANTLY OVER BUDGET"


def test_exact_budget():
    result = calculate_budget(10000, {"Travel": 6000, "Hotel": 4000})

    assert result["estimated_total"] == 10000
    assert result["remaining_budget"] == 0
    assert result["status"] == "WITHIN BUDGET"


def test_extract_budget():
    assert extract_budget("Plan a trip within a budget of ₹15,000") == 15000


def test_extract_budget_in_thousands():
    assert extract_budget("My budget is ₹15k") == 15000


def test_negative_budget_is_rejected():
    with pytest.raises(ValueError):
        calculate_budget(-1000, {"Travel": 500})


def test_negative_cost_is_rejected():
    with pytest.raises(ValueError):
        calculate_budget(10000, {"Travel": -500})


def test_extract_costs_from_text():
    text = """Round-trip transportation: ₹3,000
Accommodation: ₹4,000
Food: ₹2,500
Local transportation: ₹1,000
Activities and entry fees: ₹1,000
Taxes and miscellaneous: ₹500
Contingency: ₹1,000"""

    costs = extract_costs_from_text(text)

    assert len(costs) == 7
    assert costs["Accommodation"] == 4000
    assert costs["Food"] == 2500


def test_missing_budget_is_reported():
    report = format_budget_analysis(None, {})

    assert "no explicit budget was provided" in report