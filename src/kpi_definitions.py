"""
Real estate portfolio KPI definitions, based on publicly documented MSCI
and INREV methodology — not invented metrics.

This module implements the well-established, publicly documented core
relationships, not a full reproduction of either organization's complete
methodology (both run to many pages of detailed rules on things like
transaction-cost treatment, currency effects, and valuation timing that
this module deliberately does not attempt to replicate).

MSCI property/real estate index methodology decomposes total return into
two additive components each period:
    total_return = capital_growth + income_return
(source: MSCI Property Indexes Methodology, msci.com)

INREV's fee/expense-ratio guidance centers on a Total Expense Ratio (TER):
    TER = total_fund_expenses / average_NAV
(source: INREV Fee and Expense Metrics guidelines, inrev.org)

Both formulas below are the standard, publicly documented core
calculation — this module applies them to a small synthetic portfolio,
it does not claim to reproduce MSCI's or INREV's full index construction
or governance process.
"""


def capital_growth(opening_value, closing_value, net_capex):
    """
    Capital growth for a period: the change in property value, net of
    capital expenditure during the period (capex is not "growth" — it's
    money put in), expressed as a fraction of opening value.
    """
    if opening_value == 0:
        raise ValueError("opening_value must be non-zero to compute a growth rate")
    return (closing_value - opening_value - net_capex) / opening_value


def income_return(net_income, opening_value):
    """Income return for a period: net rental income received, as a
    fraction of opening value."""
    if opening_value == 0:
        raise ValueError("opening_value must be non-zero to compute a return rate")
    return net_income / opening_value


def total_return(cap_growth, inc_return):
    """MSCI's core decomposition: total return = capital growth + income
    return. This additive relationship is the actual, checkable claim
    this module makes about MSCI methodology."""
    return cap_growth + inc_return


def total_expense_ratio(total_fund_expenses, average_nav):
    """INREV TER: total fund expenses as a fraction of average NAV over
    the period."""
    if average_nav == 0:
        raise ValueError("average_nav must be non-zero to compute a ratio")
    return total_fund_expenses / average_nav
