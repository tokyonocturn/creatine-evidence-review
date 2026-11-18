# Methodology

## 1. Question and scope

This review asks five practical questions:

1. Does creatine supplementation improve muscle growth, strength, power, recovery,
   or exercise performance in humans?
2. Does it have cognitive, neurological, or other health benefits, and how strong
   is that evidence?
3. What dose, loading strategy, timing, and consistency are supported?
4. Is long-term use safe, and what are the real risks versus the commonly repeated
   ones?
5. Across real products, which formulations, brands, and certifications offer the
   best quality and value per effective daily dose?

The unit of analysis is **oral creatine supplementation in humans**, with a
primary focus on creatine monohydrate powder because that is the form used in
almost all efficacy and safety research.

## 2. Evidence sources

Searches were run in November 2026 across PubMed/PMC, journal publisher sites
(Journal of the International Society of Sports Nutrition, Nutrients, Sports
Medicine, Nutrition Reviews, British Journal of Nutrition, Journal of Strength and
Conditioning Research), and the reference lists of recent systematic reviews.
Additional sources:

- Position stands and government evidence reviews (ISSN 2017; U.S. DoD TBI Center
  of Excellence 2025).
- Certifier databases and programme documentation (NSF Certified for Sport,
  Informed Sport, Informed Choice).
- Independent laboratory testing and market surveys (ConsumerLab, SuppCo, the
  peer-reviewed *Food Chemistry* survey by Moret et al.).
- Brand storefronts and retailer listings for price snapshots.

Search terms combined `creatine` with `monohydrate`, `hydrochloride`, `buffered`,
`ethyl ester`, `nitrate`, `micronized`, `strength`, `power`, `hypertrophy`,
`lean mass`, `cognition`, `memory`, `depression`, `traumatic brain injury`,
`kidney`, `creatinine`, `liver`, `hydration`, `cramp`, `hair`, `DHT`, `women`,
`older adults`, `vegetarian`, `heavy metals`, `contamination`, `certification`,
`cost`, and `interaction`.

## 3. Inclusion and exclusion

**Included**

- Randomised controlled trials in humans.
- Systematic reviews and meta-analyses of RCTs.
- Position stands and narrative reviews used for mechanism, dosing, or safety
  context, not as standalone proof of efficacy.
- Independent laboratory testing and peer-reviewed product surveys.
- Certifier programme documentation for what a seal does and does not verify.

**Excluded from efficacy conclusions**

- Animal-only studies (used only to explain mechanism).
- Uncontrolled case reports, conference abstracts without data, and vendor blogs.
- Studies without a creatine-only arm when the question is about creatine itself
  (multi-ingredient blends are treated separately).

No language other than English was searched. There was no publication-date cut-off;
foundational physiology from the 1990s is retained, while efficacy and safety
claims prioritise 2015–2026 syntheses.

## 4. Evidence grading

Each row in [`data/evidence.csv`](../data/evidence.csv) has two independent axes.

**Certainty** (GRADE-style):

| Level | Meaning |
| --- | --- |
| High | Further research is unlikely to change confidence in the estimate. |
| Moderate | Further research may change the estimate or the conclusion. |
| Low | Further research is likely to change the estimate. |
| Very low | The estimate is very uncertain. |

**Status**:

| Status | Meaning |
| --- | --- |
| Established | Multiple consistent RCTs or a meta-analysis, plausible mechanism, no serious unresolved contradiction. |
| Emerging | Human data exist but samples are small, results inconsistent, or certainty is very low. |
| Mixed | Direction depends on outcome, population, or protocol. |
| Unsupported | Claim is marketed or repeated but controlled human evidence does not support it. |

Certainty and importance are separate. A pooled 0.3 kg difference can be
statistically robust and still be too small for an individual to notice.

### Handling contradictions

Where syntheses disagreed, both estimates are reported and the disagreement is
explained rather than averaged. Examples:

- **Strength effect size.** A 2024 meta-analysis of adults under 50 reported
  +4.43 kg upper-body and +11.35 kg lower-body strength, while a broader 2025
  meta-analysis of 69 studies reported smaller pooled effects (+1.43 kg bench,
  +5.64 kg squat). The difference is explained by inclusion criteria, training
  status, and how "strength" was pooled. Both agree on direction and on a small
  average effect.
- **Kidney function.** One 2026 meta-analysis found a non-significant eGFR change
  of -5.2 mL/min; another found -10.75 mL/min by creatinine-based estimation but
  no change using chromium-51 EDTA. The discrepancy is the point: creatinine-based
  estimation is biased by creatine intake, while tracer measurement is not.
- **Cognitive effects.** Memory meta-analyses show a small pooled benefit driven
  by older adults; the largest single young-adult trial found only a small,
  mostly non-significant signal. Both are reported.

## 5. Product sampling and pricing

### Sampling

Twenty products were selected purposively to cover:

- the dominant form (monohydrate) at budget, mid, and premium prices;
- micronised and non-micronised monohydrate;
- Creapure-branded ingredient;
- HCl, buffered creatine, and multi-ingredient blends;
- capsules and gummies as format comparators;
- products with NSF Certified for Sport, Informed Sport, Informed Choice, NSF
  Contents Certified, and no documented certification.

This is **not** a random or exhaustive market sample. It is large enough to show
the shape of the market and the cost spread, not to rank every brand.

### Price rules

- US one-time retail price in USD, excluding tax and shipping.
- Brand storefront is preferred. Retail listings are used where the brand does not
  sell direct or the product is sold only through retailers.
- Subscription, auto-ship, coupon, and marketplace prices are excluded because
  they are volatile and often gated.
- Each row records `price_date`, `price_channel`, and `price_source_url`.
- Prices were collected 2026-11-06 to 2026-11-17.

### Cost model

Cost is normalised to **5 g of creatine**, the maintenance dose used in most
trials, then annualised at 365 doses. This avoids the trap of comparing pack
prices across different tub sizes.

For HCl and buffered products, the label does not deliver 5 g of creatine per
serving. The chemistry correction is explicit:

- creatine monohydrate is 87.9% creatine by mass;
- creatine HCl is 78.2% creatine by mass;
- a 750 mg HCl capsule supplies about 587 mg creatine, so about 7.5 capsules are
  needed to match a 5 g monohydrate dose.

Cost per 5 g for those products therefore reflects the amount of product a
consumer must actually buy to match a monohydrate dose, not the label's suggested
serving. This is the only fair basis for a value comparison.

## 6. Verification performed

- **Arithmetic:** serving mass, package weight, total creatine, cost per 5 g, and
  annual cost are recomputed by script; invalid or implausible values fail the
  build.
- **Cross-references:** every evidence and claim row must point to an existing
  reference ID; the validator fails on dangling citations.
- **Effect sizes:** each pooled estimate was checked against the abstract, table,
  or results section of the cited record.
- **Certification claims:** checked against the certifier's public listing or
  programme documentation where available, and recorded as "None documented"
  rather than assumed absent when no listing was found.
- **Contamination claims:** triangulated across a peer-reviewed market survey and
  two independent commercial testing programmes; where they disagree (for example,
  specific gummy brands), the disagreement is stated.
- **Generated output:** CI reruns the generator and fails if the committed tables
  differ from the data.

## 7. Limitations

1. **Single-reviewer, AI-assisted.** No duplicate independent screening or
   extraction. This is the largest methodological limitation.
2. **Paywalls.** Some independent testing detail (ConsumerLab) is member-only;
   only public summaries are cited. That limits product-level specificity.
3. **Publication and funding bias.** Many creatine trials are small and some are
   industry-funded. Positive results are more likely to be published.
4. **Heterogeneity.** Populations, doses, training programs, and outcome tests
   differ. Pooled estimates are averages across dissimilar studies.
5. **Price volatility.** Prices, pack sizes, and certifications change. The
   dataset is a dated snapshot, not a live price feed.
6. **Certification ≠ efficacy.** A seal says something about contamination and
   label accuracy, not about whether the product builds muscle.
7. **Product sample is purposive.** It illustrates value tiers; it does not
   establish market-wide failure rates.
8. **No new laboratory testing.** Contamination conclusions rely on published
   assays, which may not reflect the current lot of any specific product.
9. **Generalisation.** Trial populations are mostly healthy, relatively young
   adults; frail, clinical, pregnant, and paediatric populations are
   under-represented.

## 8. Conflicts of interest and funding

None. No brand paid for inclusion, no affiliate links are used, and no product was
supplied by a manufacturer. The author has no financial interest in any supplement
brand.

## 9. AI-assistance disclosure and corrections

This review was assembled with AI assistance under human direction. Numeric claims
were checked against cited sources, and the datasets are machine-validated. It has
not been peer reviewed. If you find an error, open an issue with the exact claim,
the source, and the correction; substantive corrections will be recorded in
[`CHANGELOG.md`](../CHANGELOG.md).
