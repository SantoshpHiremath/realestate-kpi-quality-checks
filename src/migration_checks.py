"""
Data migration / go-live validation checks: comparing a legacy-system
export against a new-system export for completeness, accuracy, and
consistency — the posting's own language for the "data migration and
system go-live" task.
"""

VALUE_MISMATCH_TOLERANCE_EUR = 1.0  # anything beyond this is a real
                                     # discrepancy, not floating-point noise


def find_missing_in_new_system(legacy, new):
    """Properties present in the legacy export but absent from the new
    one — a completeness gap, likely an unmigrated record."""
    return sorted(set(legacy) - set(new))


def find_missing_in_legacy(legacy, new):
    """The reverse direction — present in new but not legacy. Less
    common in a migration but worth checking both ways rather than
    assuming the legacy system is always the ground truth."""
    return sorted(set(new) - set(legacy))


def find_value_discrepancies(legacy, new, tolerance=VALUE_MISMATCH_TOLERANCE_EUR):
    """For properties present in both systems, flag any numeric field
    that differs beyond a small floating-point tolerance — this is the
    'accuracy and consistency' half of the check, distinct from the
    completeness check above."""
    discrepancies = []
    common_ids = set(legacy) & set(new)
    for pid in sorted(common_ids):
        l, n = legacy[pid], new[pid]
        fields = ["opening_value_eur", "closing_value_eur", "net_capex_eur", "net_income_eur"]
        for field in fields:
            l_val, n_val = getattr(l, field), getattr(n, field)
            if abs(l_val - n_val) > tolerance:
                discrepancies.append({
                    "property_id": pid,
                    "field": field,
                    "legacy_value": l_val,
                    "new_value": n_val,
                    "difference": round(n_val - l_val, 2),
                })
    return discrepancies


def find_suspicious_zero_or_missing_fields(new, fields=("net_income_eur",)):
    """A field that's exactly zero where a legacy record had a real
    value is a common migration bug (blank-field-defaulted-to-zero), not
    a real business event — flagged separately from a genuine value
    discrepancy because the fix is different (recover a missing value,
    not reconcile two different real numbers)."""
    flagged = []
    for pid, rec in sorted(new.items()):
        for field in fields:
            if getattr(rec, field) == 0:
                flagged.append({"property_id": pid, "field": field})
    return flagged


def migration_validation_report(legacy, new):
    missing_in_new = find_missing_in_new_system(legacy, new)
    missing_in_legacy = find_missing_in_legacy(legacy, new)
    value_discrepancies = find_value_discrepancies(legacy, new)
    suspicious_zeros = find_suspicious_zero_or_missing_fields(new)

    total_checked = len(set(legacy) | set(new))

    # A single property can trip more than one check at once (e.g.
    # PRE-005 has both a value discrepancy AND a suspicious-zero flag for
    # the same underlying migration bug) — the flagged-property count
    # must be deduplicated by property ID, not by summing check counts,
    # or a property gets subtracted twice and the clean count comes out
    # too low. Caught during testing: an early version of this function
    # did exactly that and undercounted clean properties by 1.
    flagged_ids = (
        set(missing_in_new)
        | set(missing_in_legacy)
        | {d["property_id"] for d in value_discrepancies}
        | {f["property_id"] for f in suspicious_zeros}
    )
    clean = total_checked - len(flagged_ids)

    return {
        "total_properties_checked": total_checked,
        "missing_in_new_system": missing_in_new,
        "missing_in_legacy_system": missing_in_legacy,
        "value_discrepancies": value_discrepancies,
        "suspicious_zero_fields": suspicious_zeros,
        "flagged_properties": sorted(flagged_ids),
        "clean_properties": max(clean, 0),
    }
