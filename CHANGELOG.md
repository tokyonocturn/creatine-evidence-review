# Changelog

All notable changes to the datasets, generated tables, and report are recorded here.
The format follows Keep a Changelog; versions use semantic versioning.

## [1.0.0] - 2026-11-18

### Added

- Comprehensive scientific report covering mechanisms, formulations, performance,
  hypertrophy, cognition, other health outcomes, dosing, safety, sex and age
  differences, product quality, certification, cost, and medication precautions.
- `data/products.csv`: 20 products priced 2026-11-06 to 2026-11-17, normalised to
  cost per 5 g of creatine.
- `data/evidence.csv`: 59 graded evidence rows across nine domains.
- `data/claims.csv`: 30 claims adjudicated as supported, partially supported,
  unsupported, or false.
- `data/references.csv`: 64 references with DOI or stable URL.
- `analysis/build_tables.py`: schema validation, cost model, salt chemistry,
  generated Markdown, relative-link checking, and a `--check` mode for CI.
- GitHub Actions workflow that validates the datasets on every push.
- Practical dosage guide, safety assessment, formulation and quality review, and
  brand comparison.

### Notes

- Prices are US one-time retail snapshots and exclude tax and shipping.
- No new laboratory testing was commissioned; contamination conclusions rely on
  published independent testing and peer-reviewed market surveys.
- The review is AI-assisted and has not been peer reviewed. See
  `docs/methodology.md`.

## Correction policy

Substantive corrections are recorded here with the date, the affected row or claim,
and the source that justified the change. Generated tables are never edited by hand;
they are rebuilt from the CSVs and verified in CI.
