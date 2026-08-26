"""
End-to-end runner: builds the legacy and new-system synthetic portfolios,
runs the migration validation report, and computes MSCI-style KPIs for
every property in the (validated) new-system export.
"""

from src.portfolio_data import build_legacy_portfolio, build_new_system_portfolio
from src.migration_checks import migration_validation_report
from src.kpi_definitions import capital_growth, income_return, total_return


def run():
    legacy = build_legacy_portfolio()
    new = build_new_system_portfolio()

    report = migration_validation_report(legacy, new)

    print("=" * 70)
    print("DATA MIGRATION VALIDATION — LEGACY vs. NEW SYSTEM")
    print("=" * 70)
    print(f"\nProperties checked: {report['total_properties_checked']}")
    print(f"Clean (no discrepancies): {report['clean_properties']}")
    print(f"Flagged: {report['flagged_properties']}")

    if report["missing_in_new_system"]:
        print(f"\nMissing from new system (not yet migrated): {report['missing_in_new_system']}")
    if report["value_discrepancies"]:
        print("\nValue discrepancies:")
        for d in report["value_discrepancies"]:
            print(f"  {d['property_id']} / {d['field']}: legacy={d['legacy_value']:,.0f} "
                  f"new={d['new_value']:,.0f} (diff {d['difference']:+,.0f})")
    if report["suspicious_zero_fields"]:
        print("\nSuspicious zero/missing fields (likely blank-on-migration bugs):")
        for f in report["suspicious_zero_fields"]:
            print(f"  {f['property_id']} / {f['field']}")

    print("\n" + "=" * 70)
    print("PORTFOLIO KPIs (MSCI-style total return decomposition, new-system data)")
    print("=" * 70)
    for pid, rec in sorted(new.items()):
        cg = capital_growth(rec.opening_value_eur, rec.closing_value_eur, rec.net_capex_eur)
        ir = income_return(rec.net_income_eur, rec.opening_value_eur)
        tr = total_return(cg, ir)
        flag = "  [DATA QUALITY ISSUE — verify before trusting this KPI]" if pid in report["flagged_properties"] else ""
        print(f"  {pid} {rec.name:28s} capital_growth={cg:+.2%}  income_return={ir:+.2%}  "
              f"total_return={tr:+.2%}{flag}")


if __name__ == "__main__":
    run()
