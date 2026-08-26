# Real Estate Portfolio KPIs & Data Migration Validation

A small, real, tested Python project applying MSCI- and INREV-style real
estate performance KPIs to a synthetic property portfolio, with data
migration validation checks (legacy vs. new system) — built to close a
narrow, specific gap for PIMCO Prime Real Estate's "Intern in Data & AI"
posting: real estate-specific KPI frameworks (MSCI, INREV) were the one
substantive gap in an otherwise strong match, since the rest of the
posting's tasks (Power BI, data migration/go-live validation, discrepancy
investigation, cross-team coordination) were already covered by prior
project and work evidence.

This is intentionally a small, focused addition, not a full new project —
the gap itself is narrow (a specific industry KPI framework), and it
didn't need more than that to close honestly.

## What this is (read before citing anywhere)

**I have no real estate industry experience**, and this project doesn't
change that — it demonstrates that I can pick up a specific domain's KPI
definitions and data-quality discipline quickly, on a system I could
build and check myself. The portfolio data (`src/portfolio_data.py`) is
entirely synthetic — six fictional properties, not real PIMCO, Allianz,
or any company's holdings.

**The KPI formulas are based on publicly documented MSCI and INREV
methodology, not invented.** `src/kpi_definitions.py` implements the
well-established, publicly documented core relationships:

- MSCI property index methodology decomposes total return additively:
  `total_return = capital_growth + income_return` (source: MSCI Property
  Indexes Methodology, msci.com).
- INREV's fee/expense-ratio guidance centers on a Total Expense Ratio:
  `TER = total_fund_expenses / average_NAV` (source: INREV Fee and
  Expense Metrics guidelines, inrev.org).

Both organizations' full methodologies run to many pages covering things
like transaction-cost treatment, currency effects, and valuation timing
— this module implements the core, publicly documented calculation, not
a full reproduction of either standard's complete ruleset. If asked in
an interview: I looked up MSCI's and INREV's actual published
methodology before building this rather than guessing at plausible-
sounding formulas, and what's here is the real core relationship, at the
scope I could verify myself.

## What this models

- **`src/kpi_definitions.py`** — capital growth, income return, total
  return (MSCI-style), and total expense ratio (INREV-style).
- **`src/portfolio_data.py`** — a synthetic 6-property portfolio, in two
  versions: a "legacy system" export and a "new system" export with
  three deliberately injected migration problems (one property not yet
  migrated, one closing-value discrepancy beyond rounding, one field
  that went blank/zero during migration).
- **`src/migration_checks.py`** — the posting's "testing and validating
  data and reports across legacy and new systems to ensure completeness,
  accuracy, and consistency" task: completeness checks (missing in
  either direction), value-discrepancy detection with a floating-point
  tolerance, and a separate "suspicious zero field" check for the
  distinct blank-field-on-migration failure mode.
- **`src/pipeline.py`** — runs the validation report, then computes KPIs
  for every property, explicitly flagging any property whose KPI is
  computed on data that failed validation — a genuinely useful discipline
  (a report shouldn't quietly present a KPI built on unverified data as
  equally trustworthy as one that passed validation).

## A real bug found and fixed during development

The first version of `migration_validation_report`'s clean-property count
summed the length of each individual check's flagged-property list and
subtracted all of them from the total. One property (PRE-005) tripped
two different checks at once — a value discrepancy AND a suspicious-zero
flag, both stemming from the same underlying migration bug (its income
field went blank) — so it got subtracted twice, undercounting clean
properties as 2 instead of the correct 3. Fixed by deduplicating flagged
property IDs into a single set before subtracting, and locked in with a
dedicated regression test
(`test_clean_properties_count_does_not_double_subtract_a_property_flagged_by_two_checks`)
plus an invariant test that flagged + clean counts always sum to the
total checked.

## Verification

22 tests (`pytest tests/ -v`), including:

- KPI formula tests, including a manual-calculation cross-check on
  realistic property-value numbers, not just round test inputs.
- Migration-check tests covering both directions of completeness
  (missing-in-new AND missing-in-legacy), a floating-point tolerance test
  (tiny differences aren't false positives), and multi-field discrepancy
  detection on a single property.
- A spot-check of the three specific, deliberately-injected migration
  problems by property ID, not just aggregate counts.
- The regression test for the double-subtraction bug described above.

## Running it

```bash
pip install -r requirements.txt   # no dependencies beyond pytest — stdlib only
python3 -m src.pipeline            # migration validation report + KPI summary
pytest tests/ -v                   # 22 tests
```

## What this doesn't demonstrate

This project doesn't use real property or fund data, doesn't reproduce
MSCI's or INREV's full published methodology (transaction costs,
currency effects, valuation-timing rules, and more are out of scope), and
doesn't integrate with any real portfolio management or reporting
system. It demonstrates that I can look up and correctly apply a
specific industry's core KPI definitions, and that I bring the same
data-quality discipline (checking for both directions of a discrepancy,
not double-counting overlapping issues, flagging KPIs computed on
unverified data) to a genuinely new domain — on a system I could
construct and verify myself.
