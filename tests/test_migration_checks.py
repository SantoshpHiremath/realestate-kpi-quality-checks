from src.portfolio_data import PropertyRecord, build_legacy_portfolio, build_new_system_portfolio
from src.migration_checks import (
    find_missing_in_new_system, find_missing_in_legacy, find_value_discrepancies,
    find_suspicious_zero_or_missing_fields, migration_validation_report,
)


def _rec(pid, opening=100, closing=110, capex=0, income=5):
    return PropertyRecord(pid, f"Test {pid}", opening, closing, capex, income)


class TestCompletenessChecks:
    def test_finds_property_missing_from_new_system(self):
        legacy = {"A": _rec("A"), "B": _rec("B")}
        new = {"A": _rec("A")}
        assert find_missing_in_new_system(legacy, new) == ["B"]

    def test_finds_property_missing_from_legacy_system(self):
        legacy = {"A": _rec("A")}
        new = {"A": _rec("A"), "C": _rec("C")}
        assert find_missing_in_legacy(legacy, new) == ["C"]

    def test_no_missing_properties_when_sets_match(self):
        legacy = {"A": _rec("A"), "B": _rec("B")}
        new = {"A": _rec("A"), "B": _rec("B")}
        assert find_missing_in_new_system(legacy, new) == []
        assert find_missing_in_legacy(legacy, new) == []


class TestValueDiscrepancies:
    def test_detects_closing_value_mismatch_beyond_tolerance(self):
        legacy = {"A": _rec("A", closing=110)}
        new = {"A": _rec("A", closing=115)}
        discrepancies = find_value_discrepancies(legacy, new)
        assert len(discrepancies) == 1
        assert discrepancies[0]["field"] == "closing_value_eur"
        assert discrepancies[0]["difference"] == 5

    def test_tiny_floating_point_difference_within_tolerance_not_flagged(self):
        legacy = {"A": _rec("A", closing=110.0000001)}
        new = {"A": _rec("A", closing=110.0000002)}
        assert find_value_discrepancies(legacy, new) == []

    def test_identical_records_produce_no_discrepancies(self):
        legacy = {"A": _rec("A")}
        new = {"A": _rec("A")}
        assert find_value_discrepancies(legacy, new) == []

    def test_multiple_field_discrepancies_on_same_property_all_reported(self):
        legacy = {"A": _rec("A", opening=100, closing=110)}
        new = {"A": _rec("A", opening=105, closing=120)}
        discrepancies = find_value_discrepancies(legacy, new)
        fields = {d["field"] for d in discrepancies}
        assert fields == {"opening_value_eur", "closing_value_eur"}


class TestSuspiciousZeroFields:
    def test_flags_zero_income_field(self):
        new = {"A": _rec("A", income=0)}
        flagged = find_suspicious_zero_or_missing_fields(new)
        assert flagged == [{"property_id": "A", "field": "net_income_eur"}]

    def test_nonzero_income_not_flagged(self):
        new = {"A": _rec("A", income=500)}
        assert find_suspicious_zero_or_missing_fields(new) == []


class TestMigrationValidationReport:
    def test_report_runs_on_sample_portfolio(self):
        legacy = build_legacy_portfolio()
        new = build_new_system_portfolio()
        report = migration_validation_report(legacy, new)
        assert report["total_properties_checked"] == 6

    def test_known_injected_gaps_all_caught(self):
        """Spot-check the three deliberately-injected migration problems
        by name, not just aggregate counts."""
        legacy = build_legacy_portfolio()
        new = build_new_system_portfolio()
        report = migration_validation_report(legacy, new)
        assert "PRE-006" in report["missing_in_new_system"]
        assert any(d["property_id"] == "PRE-003" for d in report["value_discrepancies"])
        assert any(f["property_id"] == "PRE-005" for f in report["suspicious_zero_fields"])

    def test_clean_properties_count_does_not_double_subtract_a_property_flagged_by_two_checks(self):
        """Regression test for a real bug found during development: an
        earlier version summed the length of each check's flagged list
        and subtracted all of them from the total, so a property tripping
        two checks at once (PRE-005: both a value discrepancy AND a
        suspicious-zero flag) was subtracted twice, undercounting clean
        properties by 1 (reported 2 instead of the correct 3). Fixed by
        deduplicating flagged property IDs into a single set before
        subtracting."""
        legacy = build_legacy_portfolio()
        new = build_new_system_portfolio()
        report = migration_validation_report(legacy, new)
        # PRE-001, PRE-002, PRE-004 are the only properties with zero
        # flags across every check.
        assert report["clean_properties"] == 3
        assert set(report["flagged_properties"]) == {"PRE-003", "PRE-005", "PRE-006"}

    def test_flagged_and_clean_counts_always_sum_to_total(self):
        legacy = build_legacy_portfolio()
        new = build_new_system_portfolio()
        report = migration_validation_report(legacy, new)
        assert report["clean_properties"] + len(report["flagged_properties"]) == report["total_properties_checked"]
