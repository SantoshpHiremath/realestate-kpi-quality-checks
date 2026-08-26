"""
Synthetic real estate property portfolio, modeled as if migrated from a
legacy system to a new one — deliberately including realistic migration
discrepancies (a property present in one system but not the other, a
value mismatch beyond rounding, a missing income figure), the same kind
of gap the posting's "testing and validating data and reports across
legacy and new systems" task describes.

Not real PIMCO, Allianz, or any company's property data.
"""

from dataclasses import dataclass


@dataclass
class PropertyRecord:
    property_id: str
    name: str
    opening_value_eur: float
    closing_value_eur: float
    net_capex_eur: float
    net_income_eur: float


def build_legacy_portfolio():
    """The 'old system' export."""
    return {
        "PRE-001": PropertyRecord("PRE-001", "Munich Office Tower", 42_000_000, 43_500_000, 800_000, 1_850_000),
        "PRE-002": PropertyRecord("PRE-002", "Frankfurt Logistics Park", 28_000_000, 27_600_000, 200_000, 1_400_000),
        "PRE-003": PropertyRecord("PRE-003", "Berlin Retail Center", 19_500_000, 20_100_000, 150_000, 980_000),
        "PRE-004": PropertyRecord("PRE-004", "Hamburg Residential", 33_000_000, 34_200_000, 500_000, 1_320_000),
        "PRE-005": PropertyRecord("PRE-005", "Stuttgart Mixed-Use", 24_800_000, 25_000_000, 100_000, 1_050_000),
        "PRE-006": PropertyRecord("PRE-006", "Cologne Office Park", 21_000_000, 21_400_000, 300_000, 890_000),
    }


def build_new_system_portfolio():
    """The 'new system' export, post-migration — with realistic gaps:
    PRE-006 is missing entirely (not yet migrated), PRE-003's closing
    value has a discrepancy beyond rounding (a real migration bug, not
    a rounding artifact), and PRE-005's net income is missing (blank
    field on migration)."""
    return {
        "PRE-001": PropertyRecord("PRE-001", "Munich Office Tower", 42_000_000, 43_500_000, 800_000, 1_850_000),
        "PRE-002": PropertyRecord("PRE-002", "Frankfurt Logistics Park", 28_000_000, 27_600_000, 200_000, 1_400_000),
        "PRE-003": PropertyRecord("PRE-003", "Berlin Retail Center", 19_500_000, 20_450_000, 150_000, 980_000),  # closing value discrepancy
        "PRE-004": PropertyRecord("PRE-004", "Hamburg Residential", 33_000_000, 34_200_000, 500_000, 1_320_000),
        "PRE-005": PropertyRecord("PRE-005", "Stuttgart Mixed-Use", 24_800_000, 25_000_000, 100_000, 0),  # missing income
        # PRE-006 intentionally absent — not yet migrated.
    }
