# Creatine: An Independent Evidence Review and Product Database

A source-linked review of creatine supplementation — what it does, what it does
not do, how to dose it, who should be cautious, and what 20 real products cost per
effective daily dose. Built as a reproducible repository: every quantitative
claim traces to a reference, and every table is generated from the CSV datasets
in [`data/`](data/).

**No brand funding, affiliate links, or sponsorship.** Prices were collected in
November 2026 and will change.

---

## Bottom line

**Creatine monohydrate is genuinely beneficial, but narrowly.** It reliably
increases strength and power, and it adds about 1 kg of lean mass when combined
with resistance training. It is not a fat burner, a replacement for training, or
a proven cognitive enhancer for healthy young adults.

| Question | Answer | Confidence |
| --- | --- | --- |
| Does it work for strength and power? | Yes. Pooled gains of about **+4.4 kg upper-body 1RM**, **+11.4 kg leg press**, and **+48 W Wingate peak power** versus placebo plus training. | Moderate |
| Does it build muscle? | Yes, with training: about **+1.1 kg lean mass** and **-0.7 kg fat mass** over a training block. Without training, the effect is about zero. | Moderate |
| Does it help cognition? | Small memory effect overall (SMD 0.29), larger in older adults (SMD 0.88), but the evidence is low certainty. Not proven in healthy young adults. | Low |
| Which form? | **Monohydrate.** HCl, buffered, ethyl ester, and nitrate are not superior and usually cost more. | Moderate–High |
| How much? | **3–5 g/day** (about 0.03 g/kg). Loading with 20 g/day for 5–7 days is optional and only speeds saturation. | High |
| Is it safe? | Yes for healthy people at recommended doses; trials run up to 5 years. Kidney "damage" is usually a creatinine lab artefact. | High |
| Who should be cautious? | People with kidney disease, those taking nephrotoxic drugs or diuretics, pregnancy/breastfeeding, bipolar disorder, and minors without clinical advice. | Moderate–Low |
| Best value? | **BulkSupplements 1 kg at $29.97** — about **$0.15 per 5 g**, and NSF Certified for Sport. | Price snapshot |
| Worst value? | HCl, buffered, and gummy formats: **$1.39–$3.12 per 5 g**, 9–21× the cheapest powder, without better outcomes. | Price snapshot |

The detailed argument, caveats, and citations are in the
[full report](report/creatine-scientific-report.md).

---

## What is in this repository

| Path | Contents |
| --- | --- |
| [`report/creatine-scientific-report.md`](report/creatine-scientific-report.md) | Comprehensive scientific report: mechanisms, efficacy, dosing, safety, populations, products, cost, conclusions. |
| [`docs/methodology.md`](docs/methodology.md) | Search strategy, inclusion rules, grading scheme, pricing method, verification, limitations, AI disclosure. |
| [`docs/dosage-guide.md`](docs/dosage-guide.md) | Practical protocols by body weight, timing, mixing, missed doses, special populations. |
| [`docs/safety-assessment.md`](docs/safety-assessment.md) | Risk-by-risk safety review, including kidney, liver, hair, hydration, pregnancy, medications. |
| [`docs/forms-and-quality.md`](docs/forms-and-quality.md) | Monohydrate vs HCl vs buffered vs other forms; contamination, testing, certifications, micronisation, blends. |
| [`docs/brand-comparison.md`](docs/brand-comparison.md) | How to read the product data, value tiers, and buying guidance. |
| [`docs/generated/brand-comparison.md`](docs/generated/brand-comparison.md) | Generated 20-product cost table, sport-certified table, loading costs, form chemistry. |
| [`docs/generated/evidence-tables.md`](docs/generated/evidence-tables.md) | 59 graded evidence rows across nine domains. |
| [`docs/generated/claims-table.md`](docs/generated/claims-table.md) | 30 common claims adjudicated as supported, partial, unsupported, or false. |
| [`docs/references.md`](docs/references.md) | 64 references with DOI or stable URL. |
| [`data/products.csv`](data/products.csv) | Product database (price, dose, servings, certification, ingredients). |
| [`data/evidence.csv`](data/evidence.csv) | Evidence table with effect sizes, certainty, and status. |
| [`data/claims.csv`](data/claims.csv) | Claim adjudication dataset. |
| [`data/references.csv`](data/references.csv) | Reference metadata. |
| [`data/data-dictionary.md`](data/data-dictionary.md) | Column definitions and grading scheme. |
| [`analysis/build_tables.py`](analysis/build_tables.py) | Validates the datasets, computes cost metrics, regenerates all tables. |

---

## Reproduce it

Requires Python 3.10+ and no third-party packages.

```bash
python analysis/build_tables.py           # validate + regenerate tables
python analysis/build_tables.py --check   # fail if data or tables are stale
```

The `--check` command runs in CI on every push
([`.github/workflows/validate.yml`](.github/workflows/validate.yml)). It verifies:

- required columns and allowed categorical values;
- unique IDs and resolvable cross-references between evidence, claims, and references;
- plausible serving mass, package weight, and price arithmetic;
- that the generated Markdown is byte-identical to what the data produces.

### Derived cost model

```
creatine per serving      = creatine_mg_per_serving / 1000
total creatine per pack   = creatine per serving x servings_per_container
cost per 5 g              = price x 5 / total creatine per pack
cost per year             = cost per 5 g x 365
7-day loading cost        = cost per 5 g x 4 x 7      # 20 g/day
```

Creatine salt chemistry (creatine fraction of molar mass) is calculated in the
same script, not copied from marketing material.

---

## How the evidence was handled

- **Established** findings have multiple consistent RCTs or a meta-analysis, with
  a plausible mechanism and no serious unresolved contradiction.
- **Emerging** findings have human data but small samples, inconsistency, or very
  low certainty.
- **Mixed** means the pooled direction is unclear or depends on outcome.
- **Unsupported** means the claim is marketed or repeated but is not supported by
  controlled human evidence.

Certainty is graded High / Moderate / Low / Very low using GRADE logic. The two
axes are deliberately separate: a real but tiny effect can be *established* and
still be clinically unimportant.

Full details, including how contradictions were resolved, are in
[`docs/methodology.md`](docs/methodology.md).

---

## What this review is not

- **Not medical advice.** Creatine is a supplement, not a treatment. People with
  kidney or liver disease, diabetes, heart disease, bipolar disorder, who are
  pregnant or breastfeeding, or who take prescription medication should talk to a
  clinician.
- **Not a primary laboratory study.** Product-quality conclusions come from
  published independent testing (ConsumerLab, SuppCo, peer-reviewed market
  surveys) and certifier databases; this project did not commission new assays.
- **Not exhaustive.** Twenty products are a purposive sample across price tiers,
  forms, formats, and certifications, not a census of the market.
- **Not free of uncertainty.** Supplement research is funded partly by industry,
  publication bias is real, and many trials are small. Effect estimates should be
  read as best current approximations.

### AI-assistance disclosure

This review was assembled with AI assistance under human direction. Every
numeric claim was checked against the cited abstract, table, or dataset; the
datasets and generated tables are machine-validated. It has **not** been peer
reviewed. Treat it as a well-documented starting point, not a substitute for the
primary literature or clinical judgement.

Corrections are welcome: open an issue with the claim, the source, and the
proposed change. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## Citation and license

Citation metadata is in [`CITATION.cff`](CITATION.cff).

- **Text and data:** CC BY 4.0 — share and adapt with attribution.
- **Code:** MIT.

See [`NOTICE`](NOTICE) for the full content-license and medical disclaimer.
