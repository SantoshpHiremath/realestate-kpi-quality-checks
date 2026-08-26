import pytest

from src.kpi_definitions import capital_growth, income_return, total_return, total_expense_ratio


def test_capital_growth_basic():
    # value grows from 100 to 110, no capex -> 10% growth
    assert capital_growth(100, 110, 0) == pytest.approx(0.10)


def test_capital_growth_nets_out_capex():
    # value grows from 100 to 110, but 5 of that was capex spend, not
    # organic growth -> only 5% real growth
    assert capital_growth(100, 110, 5) == pytest.approx(0.05)


def test_capital_growth_zero_opening_value_raises():
    with pytest.raises(ValueError):
        capital_growth(0, 100, 0)


def test_income_return_basic():
    assert income_return(5, 100) == pytest.approx(0.05)


def test_income_return_zero_opening_value_raises():
    with pytest.raises(ValueError):
        income_return(5, 0)


def test_total_return_is_additive_per_msci_methodology():
    """The specific, checkable claim: MSCI decomposes total return as
    capital growth + income return, additively — not compounded."""
    assert total_return(0.03, 0.05) == pytest.approx(0.08)


def test_total_return_matches_manual_calculation_on_realistic_numbers():
    cg = capital_growth(42_000_000, 43_500_000, 800_000)
    ir = income_return(1_850_000, 42_000_000)
    tr = total_return(cg, ir)
    # Manual calculation: (43.5M - 42M - 0.8M) / 42M + 1.85M / 42M
    expected = (700_000 / 42_000_000) + (1_850_000 / 42_000_000)
    assert tr == pytest.approx(expected)


def test_total_expense_ratio_basic():
    assert total_expense_ratio(50_000, 1_000_000) == pytest.approx(0.05)


def test_total_expense_ratio_zero_nav_raises():
    with pytest.raises(ValueError):
        total_expense_ratio(50_000, 0)
