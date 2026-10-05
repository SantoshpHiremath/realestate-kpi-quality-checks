# Real Estate Portfolio KPIs & Data Migration Validation

A small, tested Python project that applies MSCI- and INREV-style real
estate performance KPIs to a synthetic property portfolio, with data
migration validation checks (legacy vs. new system). It covers the
real estate-specific KPI frameworks (MSCI, INREV) alongside the
data-quality side of a migration: go-live validation, discrepancy
investigation, and reporting on data that has been checked.

## What it does

- **`src/kpi_definitions.py`** — capital growth, income return, total
  return (MSCI-style), and total expense ratio (INREV-style).
- **`src/portfolio_data.py`** — a synthetic 6-property portfolio, in two
  versions: a "legacy system" export and a "new system" export with
  three deliberately injected migration problems (one property not yet
  migrated, one closing-value discrepancy beyond rounding, one field
  that went blank/zero during migration).
- **`src/migration_checks.py`** — testing and validating data across
  legacy and new systems for completeness, accuracy, and consistency:
  completeness checks (missing in either direction), value-discrepancy
  detection with a floating-point tolerance, and a separate "suspicious
  zero field" check for the distinct blank-field-on-migration failure
  mode.
- **`src/pipeline.py`** — runs the validation report, then computes KPIs
  for every property, explicitly flagging any property whose KPI is
  computed on data that failed validation, so a KPI built on unverified
  data is never presented as equally trustworthy as one that passed.

## Scope

The portfolio data (`src/portfolio_data.py`) is synthetic: six fictional
properties, not any real company's holdings. The KPI formulas are based on
publicly documented MSCI and INREV methodology, and `src/kpi_definitions.py`
implements the well-established core relationships:

- MSCI property index methodology decomposes total return additively:
  `total_return = capital_growth + income_return` (source: MSCI Property
  Indexes Methodology, msci.com).
- INREV's fee/expense-ratio guidance centers on a Total Expense Ratio:
  `TER = total_fund_expenses / average_NAV` (source: INREV Fee and
  Expense Metrics guidelines, inrev.org).

I worked from MSCI's and INREV's published methodology rather than
plausible-sounding formulas. The module implements the core, publicly
documented calculation; transaction-cost treatment, currency effects, and
valuation timing are outside its scope.

## Results

The first version of `migration_validation_report`'s clean-property count
summed the length of each individual check's flagged-property list and
subtracted all of them from the total. One property (PRE-005) tripped
two different checks at once, a value discrepancy and a suspicious-zero
flag, both stemming from the same underlying migration bug (its income
field went blank), so it was subtracted twice and clean properties were
undercounted as 2 instead of the correct 3. I fixed it by deduplicating
flagged property IDs into a single set before subtracting, and locked it
in with a dedicated regression test
(`test_clean_properties_count_does_not_double_subtract_a_property_flagged_by_two_checks`)
plus an invariant test that flagged + clean counts always sum to the
total checked.

## Tests

22 tests (`pytest tests/ -v`), including:

- KPI formula tests, including a manual-calculation cross-check on
  realistic property-value numbers, not just round test inputs.
- Migration-check tests covering both directions of completeness
  (missing-in-new AND missing-in-legacy), a floating-point tolerance test
  (tiny differences aren't false positives), and multi-field discrepancy
  detection on a single property.
- A spot-check of the three specific, deliberately-injected migration
  problems by property ID, not just aggregate counts.
- The regression test for the double-counting fix described above.

## Running it

```bash
pip install -r requirements.txt   # no dependencies beyond pytest — stdlib only
python3 -m src.pipeline            # migration validation report + KPI summary
pytest tests/ -v                   # 22 tests
```

## Possible extensions

- Run the same checks against real property or fund exports.
- Extend the KPI module with transaction costs, currency effects, and
  valuation-timing rules from the full MSCI and INREV methodologies.
- Connect the validation report to a portfolio management or reporting
  system.
