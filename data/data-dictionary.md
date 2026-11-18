# Data dictionary

All datasets are UTF-8 CSV with a single header row. They are the source of truth
for the report; the Markdown tables under `docs/generated/` are rendered from them
by `analysis/build_tables.py`.

## `products.csv`

| Column | Type | Meaning |
| --- | --- | --- |
| `id` | slug | Stable identifier used in prose and tables. |
| `brand` | text | Brand name as sold. |
| `product` | text | Product and pack size. |
| `form` | enum | `monohydrate`, `monohydrate_micronized`, `monohydrate_creapure`, `hcl`, `buffered`, `blend`, `gummies`. |
| `format` | enum | `powder`, `capsules`, `gummies`. |
| `creatine_mg_per_serving` | number | Milligrams of creatine (not salt mass) per label serving. For monohydrate this equals the monohydrate mass on the label; for HCl it is the salt mass as labelled, and the chemistry correction is applied separately in the report. |
| `serving_size_g` | number | Total powder or capsule mass per serving, in grams. |
| `servings_per_container` | integer | Label servings per pack. |
| `package_g` | number or blank | Net weight in grams when stated. Blank when the retailer does not state a net weight. |
| `price_usd` | number | One-time retail price in US dollars, excluding tax and shipping. |
| `price_channel` | text | Where the price came from (`Brand store`, `Retail listing`, `Third-party price check`, or a derived figure explicitly labelled as such). |
| `price_date` | ISO date | Date the price was observed. |
| `price_source_url` | https URL | Page used for the price. |
| `certification` | enum | `NSF Certified for Sport`, `Informed Sport`, `Informed Choice`, `NSF Contents Certified`, `None documented`. |
| `micronized` | yes/no | Whether the product explicitly claims micronisation. |
| `single_ingredient` | yes/no | Whether creatine is the only active ingredient. |
| `other_ingredients` | text | Active co-ingredients, or `None`. |
| `notes` | text | Provenance and caveats. |

### Derived fields (not stored in the CSV)

`analysis/build_tables.py` computes:

- `creatine_g` = mg per serving / 1000
- `equivalent_g` = creatine per serving expressed as monohydrate equivalent; for
  HCl, multiplied by 0.7824 / 0.8792 because the salt is less creatine-dense
- `total_creatine_g` = monohydrate-equivalent creatine per container
- `cost_per_5g` = price x 5 / total monohydrate-equivalent creatine
- `cost_per_year` = cost per 5 g x 365
- `cost_loading_7d` = cost per 5 g x 4 x 7
- `sport_certified` = certification is NSF Certified for Sport or Informed Sport

`cost_per_5g` is the cost of a **5 g monohydrate-equivalent dose**, which is the
dose used in most trials. A gram of creatine HCl contains less creatine than a gram
of monohydrate (78.2% vs 87.9%), so HCl products are corrected before comparison.
A 750 mg HCl capsule supplies about 587 mg creatine, and about 7.5 capsules match a
5 g monohydrate dose.

## `evidence.csv`

| Column | Meaning |
| --- | --- |
| `id` | Stable evidence-row identifier. |
| `domain` | One of `performance`, `hypertrophy`, `recovery`, `cognition`, `clinical`, `safety`, `special_populations`, `dosing`, `product_quality`. |
| `question` | The practical question being answered. |
| `outcome` | The measured outcome. |
| `population` | Who was studied. |
| `evidence_type` | Design and size of the evidence base. |
| `studies_participants` | Number of studies and participants where reported. |
| `pooled_effect` | The pooled estimate, in the units used by the source. |
| `ci` | Confidence interval, where reported. |
| `certainty` | GRADE-style certainty: `High`, `Moderate`, `Low`, `Very low`, `Not graded`. |
| `status` | `Established`, `Emerging`, `Mixed`, `Unsupported`. |
| `source_ids` | Semicolon-separated reference IDs from `references.csv`. |
| `notes` | Caveats. |

## `claims.csv`

| Column | Meaning |
| --- | --- |
| `id` | Stable claim identifier. |
| `claim` | The claim as commonly stated. |
| `category` | Marketing, safety, performance, formulation, or cost. |
| `verdict` | `Supported`, `Partially supported`, `Unsupported`, `False`. |
| `explanation` | What the evidence actually shows. |
| `source_ids` | Semicolon-separated reference IDs. |

## `references.csv`

| Column | Meaning |
| --- | --- |
| `id` | `R01`-style identifier used in every other dataset. |
| `authors` | Author list as transcribed; blank when not transcribed. |
| `year` | Publication year. |
| `title` | Article or programme title. |
| `journal` | Journal, publisher, or programme. |
| `identifier` | DOI, PMID/PMC, or report number where available. |
| `url` | Stable https link to the record. |
| `type` | Evidence type. |

## Certainty scheme

Certainty is a judgement, not a statistical output. It combines risk of bias,
inconsistency, indirectness, imprecision, and publication bias, following the
logic of GRADE:

- **High**: further research is unlikely to change confidence in the estimate.
- **Moderate**: further research may change the estimate and could change the conclusion.
- **Low**: further research is likely to change the estimate.
- **Very low**: the estimate is very uncertain.

`Status` is separate and describes the state of the claim, not its certainty:
a small effect can be `Established` with `Moderate` certainty, while a plausible
mechanism with only pilot data is `Emerging` with `Very low` certainty.
