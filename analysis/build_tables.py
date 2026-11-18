#!/usr/bin/env python3
"""Validate the creatine review datasets and regenerate every derived table.

The repository treats the CSV files in ``data/`` as the source of truth. This
script performs schema and arithmetic checks, computes cost-per-dose metrics,
and renders the Markdown tables used by the documentation.

Usage
-----
    python analysis/build_tables.py           # validate and regenerate
    python analysis/build_tables.py --check   # validate; fail if outputs stale

Only the Python standard library is required (Python 3.10+).
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import re
import sys
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
GEN = ROOT / "docs" / "generated"

# Molar masses (g/mol) used for the stoichiometry table.
MOLAR_MASS = {
    "Creatine (anhydrous)": 131.13,
    "Creatine monohydrate": 149.15,
    "Creatine hydrochloride": 167.59,
}
CREATINE_MOLAR_MASS = MOLAR_MASS["Creatine (anhydrous)"]
CREATINE_FRACTION_MONOHYDRATE = CREATINE_MOLAR_MASS / MOLAR_MASS["Creatine monohydrate"]
CREATINE_FRACTION_HCL = CREATINE_MOLAR_MASS / MOLAR_MASS["Creatine hydrochloride"]

FORMS = {
    "monohydrate",
    "monohydrate_micronized",
    "monohydrate_creapure",
    "hcl",
    "buffered",
    "blend",
    "gummies",
}
FORMATS = {"powder", "capsules", "gummies"}
CERTIFICATIONS = {
    "NSF Certified for Sport",
    "Informed Sport",
    "Informed Choice",
    "NSF Contents Certified",
    "None documented",
}
DOMAINS = {
    "performance",
    "hypertrophy",
    "recovery",
    "cognition",
    "clinical",
    "safety",
    "special_populations",
    "dosing",
    "product_quality",
}
CERTAINTY = {"High", "Moderate", "Low", "Very low", "Not graded"}
EVIDENCE_STATUS = {"Established", "Emerging", "Mixed", "Unsupported"}
VERDICTS = {"Supported", "Partially supported", "Unsupported", "False"}

PRODUCT_COLUMNS = [
    "id",
    "brand",
    "product",
    "form",
    "format",
    "creatine_mg_per_serving",
    "serving_size_g",
    "servings_per_container",
    "package_g",
    "price_usd",
    "price_channel",
    "price_date",
    "price_source_url",
    "certification",
    "micronized",
    "single_ingredient",
    "other_ingredients",
    "notes",
]
EVIDENCE_COLUMNS = [
    "id",
    "domain",
    "question",
    "outcome",
    "population",
    "evidence_type",
    "studies_participants",
    "pooled_effect",
    "effect_measure",
    "ci",
    "certainty",
    "status",
    "source_ids",
    "notes",
]
CLAIM_COLUMNS = ["id", "claim", "category", "verdict", "explanation", "source_ids"]
REFERENCE_COLUMNS = ["id", "authors", "year", "title", "journal", "identifier", "url", "type"]

URL_RE = re.compile(r"^https://\S+$")
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{2,60}$")
REF_ID_RE = re.compile(r"^R\d{2}$")


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def read_csv(path: Path, columns: list[str], report: Report) -> list[dict[str, str]]:
    if not path.exists():
        report.error(f"{path.relative_to(ROOT)}: file is missing")
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames or []
        missing = [c for c in columns if c not in header]
        if missing:
            report.error(f"{path.name}: missing columns {missing}")
            return []
        rows = []
        for line, row in enumerate(reader, start=2):
            cleaned = {(k or "").strip(): (v or "").strip() for k, v in row.items()}
            cleaned["_line"] = str(line)
            rows.append(cleaned)
    if not rows:
        report.error(f"{path.name}: no data rows")
    return rows


def as_float(row: dict[str, str], field: str, report: Report) -> float:
    raw = row.get(field, "")
    try:
        return float(raw)
    except (TypeError, ValueError):
        report.error(f"{row.get('id', '?')}: {field} must be numeric, got {raw!r}")
        return float("nan")


def as_int(row: dict[str, str], field: str, report: Report) -> int:
    value = as_float(row, field, report)
    if value != value:  # NaN
        return 0
    if abs(value - round(value)) > 1e-9:
        report.error(f"{row.get('id', '?')}: {field} must be a whole number")
    return int(round(value))


def load_products(report: Report) -> list[dict[str, object]]:
    rows = read_csv(DATA / "products.csv", PRODUCT_COLUMNS, report)
    seen: set[str] = set()
    products: list[dict[str, object]] = []
    today = dt.date.today()

    for row in rows:
        pid = row["id"]
        if not ID_RE.match(pid):
            report.error(f"{pid or '(blank)'}: id must be lowercase slug text")
        if pid in seen:
            report.error(f"{pid}: duplicate product id")
        seen.add(pid)

        if row["form"] not in FORMS:
            report.error(f"{pid}: form {row['form']!r} not in {sorted(FORMS)}")
        if row["format"] not in FORMATS:
            report.error(f"{pid}: format {row['format']!r} not in {sorted(FORMATS)}")
        if row["certification"] not in CERTIFICATIONS:
            report.error(f"{pid}: certification {row['certification']!r} is not an allowed value")
        for flag in ("micronized", "single_ingredient"):
            if row[flag] not in {"yes", "no"}:
                report.error(f"{pid}: {flag} must be yes or no")
        if not URL_RE.match(row["price_source_url"]):
            report.error(f"{pid}: price_source_url must be an https URL")

        try:
            price_date = dt.date.fromisoformat(row["price_date"])
            if price_date > today:
                report.error(f"{pid}: price_date is in the future")
        except ValueError:
            report.error(f"{pid}: price_date must be ISO YYYY-MM-DD")
            price_date = today

        mg = as_float(row, "creatine_mg_per_serving", report)
        serving_g = as_float(row, "serving_size_g", report)
        servings = as_int(row, "servings_per_container", report)
        price = as_float(row, "price_usd", report)

        if mg < 100 or mg > 25_000:
            report.error(f"{pid}: creatine_mg_per_serving outside plausible range")
        if serving_g <= 0:
            report.error(f"{pid}: serving_size_g must be positive")
        if servings <= 0:
            report.error(f"{pid}: servings_per_container must be positive")
        if price <= 1:
            report.error(f"{pid}: price_usd must be greater than 1")

        if mg == mg and serving_g == serving_g and serving_g > 0:
            if mg > serving_g * 1000 * 1.001:
                report.error(f"{pid}: creatine per serving exceeds total serving mass")

        package_g = row.get("package_g", "")
        package_value = None
        if package_g:
            package_value = as_float(row, "package_g", report)
            if package_value <= 0:
                report.error(f"{pid}: package_g must be positive when supplied")
            elif row["format"] == "powder":
                expected = serving_g * servings
                if abs(package_value - expected) / package_value > 0.05:
                    report.error(
                        f"{pid}: package_g={package_value} differs from "
                        f"serving_size*servings={expected:.0f} by more than 5%"
                    )

        if mg != mg or servings == 0 or price != price or price <= 0:
            continue

        creatine_g = mg / 1000
        # Cost is expressed per 5 g monohydrate-equivalent dose. A gram of
        # creatine HCl supplies less creatine than a gram of monohydrate, so the
        # labelled salt mass is converted to its monohydrate equivalent.
        equivalent_g = creatine_g
        if row["form"] == "hcl":
            equivalent_g = creatine_g * (
                CREATINE_FRACTION_HCL / CREATINE_FRACTION_MONOHYDRATE
            )
        total_equiv_g = equivalent_g * servings
        cost_per_5g = price * 5 / total_equiv_g
        products.append(
            {
                **row,
                "creatine_g": creatine_g,
                "equivalent_g": equivalent_g,
                "total_creatine_g": total_equiv_g,
                "cost_per_5g": cost_per_5g,
                "cost_per_30d": cost_per_5g * 30,
                "cost_per_year": cost_per_5g * 365,
                "cost_loading_7d": cost_per_5g * 4 * 7,
                "cost_per_100g": price / total_equiv_g * 100,
                "package_g_value": package_value,
                "sport_certified": row["certification"]
                in {"NSF Certified for Sport", "Informed Sport"},
                "any_certified": row["certification"] != "None documented",
                "price_date_value": price_date,
            }
        )

    products.sort(key=lambda p: float(p["cost_per_5g"]))
    for rank, product in enumerate(products, start=1):
        product["rank"] = rank
    return products


def load_evidence(report: Report, ref_ids: set[str]) -> list[dict[str, str]]:
    rows = read_csv(DATA / "evidence.csv", EVIDENCE_COLUMNS, report)
    seen: set[str] = set()
    for row in rows:
        eid = row["id"]
        if not ID_RE.match(eid):
            report.error(f"{eid or '(blank)'}: evidence id must be lowercase slug text")
        if eid in seen:
            report.error(f"{eid}: duplicate evidence id")
        seen.add(eid)
        if row["domain"] not in DOMAINS:
            report.error(f"{eid}: unknown domain {row['domain']!r}")
        if row["certainty"] not in CERTAINTY:
            report.error(f"{eid}: unknown certainty {row['certainty']!r}")
        if row["status"] not in EVIDENCE_STATUS:
            report.error(f"{eid}: unknown status {row['status']!r}")
        ids = [s for s in row["source_ids"].split(";") if s]
        if not ids:
            report.error(f"{eid}: at least one source id is required")
        for ref in ids:
            if ref not in ref_ids:
                report.error(f"{eid}: source id {ref} is not in references.csv")
    return rows


def load_claims(report: Report, ref_ids: set[str]) -> list[dict[str, str]]:
    rows = read_csv(DATA / "claims.csv", CLAIM_COLUMNS, report)
    seen: set[str] = set()
    for row in rows:
        cid = row["id"]
        if not ID_RE.match(cid):
            report.error(f"{cid or '(blank)'}: claim id must be lowercase slug text")
        if cid in seen:
            report.error(f"{cid}: duplicate claim id")
        seen.add(cid)
        if row["verdict"] not in VERDICTS:
            report.error(f"{cid}: unknown verdict {row['verdict']!r}")
        ids = [s for s in row["source_ids"].split(";") if s]
        if not ids:
            report.error(f"{cid}: at least one source id is required")
        for ref in ids:
            if ref not in ref_ids:
                report.error(f"{cid}: source id {ref} is not in references.csv")
    return rows


def load_references(report: Report) -> tuple[list[dict[str, str]], set[str]]:
    rows = read_csv(DATA / "references.csv", REFERENCE_COLUMNS, report)
    seen: set[str] = set()
    for row in rows:
        rid = row["id"]
        if not REF_ID_RE.match(rid):
            report.error(f"{rid or '(blank)'}: reference id must match R00")
        if rid in seen:
            report.error(f"{rid}: duplicate reference id")
        seen.add(rid)
        if not URL_RE.match(row["url"]):
            report.error(f"{rid}: url must be an https URL")
        if not row["title"] or not row["journal"]:
            report.error(f"{rid}: title and journal are required")
        if not row["year"].isdigit() or not (1900 <= int(row["year"]) <= 2100):
            report.error(f"{rid}: year must be a four-digit year")
    return rows, seen


def money(value: object) -> str:
    return f"${float(value):.2f}"


def render_products(products: list[dict[str, object]]) -> str:
    lines = [
        "<!-- Generated by analysis/build_tables.py. Do not edit by hand. -->",
        "",
        "# Brand and product comparison tables",
        "",
        "Prices are US one-time retail snapshots collected from the source named in",
        "`data/products.csv`; they exclude tax and shipping and will change.",
        "Cost per 5 g is normalised to a 5 g monohydrate-equivalent maintenance dose.",
        "HCl products are corrected for the lower creatine fraction of the salt.",
        "Cost per year assumes 365 daily 5 g doses. Loading cost assumes 20 g/day",
        "for 7 days (4 x the 5 g cost).",
        "",
        f"Products: **{len(products)}**. Price snapshot range: "
        f"{min(p['price_date_value'] for p in products)} to "
        f"{max(p['price_date_value'] for p in products)}.",
        "",
        "## All products ranked by cost per 5 g of creatine",
        "",
        "| Rank | Brand | Product | Form | Format | Creatine/serving | Servings | Pack price | Cost per 5 g equiv. | Cost/year | Certification |",
        "| ---: | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for p in products:
        lines.append(
            "| {rank} | {brand} | {product} | {form} | {format} | {mg:.0f} mg | {srv} | {price} | {c5} | {cy} | {cert} |".format(
                rank=p["rank"],
                brand=p["brand"],
                product=p["product"],
                form=str(p["form"]).replace("_", " "),
                format=p["format"],
                mg=float(p["creatine_mg_per_serving"]),
                srv=p["servings_per_container"],
                price=money(p["price_usd"]),
                c5=money(p["cost_per_5g"]),
                cy=money(p["cost_per_year"]),
                cert=p["certification"],
            )
        )

    powders = [p for p in products if p["format"] == "powder"]
    gummies = [p for p in products if p["format"] == "gummies"]
    capsules = [p for p in products if p["format"] == "capsules"]
    certified = [p for p in products if p["sport_certified"]]
    cheapest = products[0]
    cheapest_powder = powders[0] if powders else cheapest
    cheapest_certified = certified[0] if certified else None
    priciest = products[-1]

    lines += [
        "",
        "## Value summary",
        "",
        "| Metric | Product | Cost per 5 g | Cost per year |",
        "| --- | --- | ---: | ---: |",
        f"| Cheapest overall | {cheapest['brand']} {cheapest['product']} | {money(cheapest['cost_per_5g'])} | {money(cheapest['cost_per_year'])} |",
        f"| Cheapest powder | {cheapest_powder['brand']} {cheapest_powder['product']} | {money(cheapest_powder['cost_per_5g'])} | {money(cheapest_powder['cost_per_year'])} |",
    ]
    if cheapest_certified:
        lines.append(
            f"| Cheapest sport-certified | {cheapest_certified['brand']} {cheapest_certified['product']} | {money(cheapest_certified['cost_per_5g'])} | {money(cheapest_certified['cost_per_year'])} |"
        )
    lines += [
        f"| Most expensive overall | {priciest['brand']} {priciest['product']} | {money(priciest['cost_per_5g'])} | {money(priciest['cost_per_year'])} |",
        "",
        "Median cost per 5 g by format:",
        "",
        "| Format | Products | Median cost per 5 g | Range |",
        "| --- | ---: | ---: | --- |",
    ]
    for label, group in (("Powder", powders), ("Capsules", capsules), ("Gummies", gummies)):
        if group:
            costs = [float(p["cost_per_5g"]) for p in group]
            lines.append(
                f"| {label} | {len(group)} | {money(median(costs))} | {money(min(costs))} - {money(max(costs))} |"
            )

    if gummies and cheapest_powder:
        multiple = float(median([p["cost_per_5g"] for p in gummies])) / float(
            cheapest_powder["cost_per_5g"]
        )
        lines += [
            "",
            f"Median gummy cost is **{multiple:.1f}x** the cheapest powder per 5 g of creatine.",
        ]

    lines += [
        "",
        "## Sport-certified products only",
        "",
        "Certification verifies the finished product and manufacturing process; it does not",
        "change the molecule or the expected training effect. `Informed Choice` is retail",
        "monitoring rather than batch-by-batch release testing, so it is shown separately.",
        "",
        "| Brand | Product | Certification | Cost per 5 g | Cost/year |",
        "| --- | --- | --- | ---: | ---: |",
    ]
    for p in sorted(products, key=lambda x: float(x["cost_per_5g"])):
        if not p["any_certified"]:
            continue
        lines.append(
            f"| {p['brand']} | {p['product']} | {p['certification']} | {money(p['cost_per_5g'])} | {money(p['cost_per_year'])} |"
        )

    lines += [
        "",
        "Sport certification (NSF Certified for Sport or Informed Sport) is a stronger",
        "batch-level signal than Informed Choice or NSF Contents Certified, which cover",
        "retail monitoring or content/purity rather than banned-substance screening of",
        "every batch.",
    ]

    lines += [
        "",
        "## Loading-phase cost",
        "",
        "A 5-7 day load at 20 g/day costs four times the daily maintenance figure.",
        "",
        "| Product | Cost per 5 g | 7-day load at 20 g/day |",
        "| --- | ---: | ---: |",
    ]
    for p in products:
        lines.append(f"| {p['brand']} {p['product']} | {money(p['cost_per_5g'])} | {money(p['cost_loading_7d'])} |")

    lines += [
        "",
        "## Form chemistry",
        "",
        "Creatine salts contain less creatine per gram than anhydrous creatine or",
        "monohydrate. The fractions below are calculated from molar masses, not from",
        "label claims.",
        "",
        "| Form | Molar mass (g/mol) | Creatine fraction | Grams needed for 5 g creatine |",
        "| --- | ---: | ---: | ---: |",
    ]
    for name, mass in MOLAR_MASS.items():
        fraction = CREATINE_MOLAR_MASS / mass
        lines.append(f"| {name} | {mass:.2f} | {fraction * 100:.1f}% | {5 / fraction:.2f} g |")
    caps_per_mono_dose = 5 * CREATINE_FRACTION_MONOHYDRATE / (
        0.75 * CREATINE_FRACTION_HCL
    )
    caps_per_5g_creatine = 5 / (0.75 * CREATINE_FRACTION_HCL)
    lines += [
        "",
        "A 750 mg creatine HCl capsule therefore supplies about "
        f"{0.75 * CREATINE_FRACTION_HCL * 1000:.0f} mg of creatine. "
        f"Matching a 5 g monohydrate dose (about 4.40 g creatine) takes about "
        f"{caps_per_mono_dose:.1f} capsules; supplying 5 g of pure creatine takes about "
        f"{caps_per_5g_creatine:.1f} capsules.",
        "",
        "## Data quality flags",
        "",
    ]
    uncertified = [p for p in products if not p["any_certified"]]
    blends = [p for p in products if p["single_ingredient"] == "no"]
    lines.append(f"- {len(uncertified)} of {len(products)} products have no documented third-party certification.")
    lines.append(f"- {len(blends)} of {len(products)} products are multi-ingredient blends.")
    lines.append("- Prices are snapshots, not live quotes; re-run the source URLs before purchasing.")
    lines.append("")
    return "\n".join(lines)


def render_evidence(evidence: list[dict[str, str]]) -> str:
    lines = [
        "<!-- Generated by analysis/build_tables.py. Do not edit by hand. -->",
        "",
        "# Evidence tables",
        "",
        "Certainty reflects the strength and consistency of the underlying evidence",
        "(GRADE-style judgement), not the size of the effect. `Status` separates",
        "established findings from emerging or unsupported ones.",
        "",
    ]
    titles = {
        "performance": "Exercise performance and power",
        "hypertrophy": "Muscle mass and body composition",
        "recovery": "Recovery and training tolerance",
        "cognition": "Cognition and brain health",
        "clinical": "Clinical and therapeutic applications",
        "safety": "Safety and risk",
        "special_populations": "Sex, age, and diet differences",
        "dosing": "Dosing, timing, and protocols",
        "product_quality": "Product quality and contamination",
    }
    for domain in titles:
        subset = [e for e in evidence if e["domain"] == domain]
        if not subset:
            continue
        lines += [
            f"## {titles[domain]}",
            "",
            "| Question | Outcome | Evidence base | Pooled result | Certainty | Status | Sources |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        for e in subset:
            effect = e["pooled_effect"]
            if e["ci"]:
                effect = f"{effect} ({e['ci']})"
            sources = ", ".join(e["source_ids"].split(";"))
            base = e["evidence_type"]
            detail = e["studies_participants"]
            if detail and detail.lower() not in base.lower():
                base = f"{base}; {detail}"
            lines.append(
                f"| {e['question']} | {e['outcome']} | {base} | {effect} | {e['certainty']} | {e['status']} | {sources} |"
            )
        lines.append("")
    return "\n".join(lines)


def render_claims(claims: list[dict[str, str]]) -> str:
    lines = [
        "<!-- Generated by analysis/build_tables.py. Do not edit by hand. -->",
        "",
        "# Claim adjudication table",
        "",
        "Every claim below was checked against the cited evidence. `Partially supported`",
        "means a kernel of truth exists but the claim as commonly stated overstates it.",
        "",
        "| # | Claim | Verdict | What the evidence shows | Sources |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for i, c in enumerate(claims, start=1):
        lines.append(
            f"| {i} | {c['claim']} | **{c['verdict']}** | {c['explanation']} | {', '.join(c['source_ids'].split(';'))} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_references(refs: list[dict[str, str]]) -> str:
    lines = [
        "<!-- Generated by analysis/build_tables.py. Do not edit by hand. -->",
        "",
        "# References",
        "",
        "Identifiers resolve to the publisher record. Where an author list was not",
        "transcribed, the title is given first and the DOI or stable URL identifies the",
        "record. Accessed November 2026.",
        "",
    ]
    for ref in sorted(refs, key=lambda r: r["id"]):
        authors = ref["authors"].strip()
        prefix = f"{authors} " if authors else ""
        identifier = ref["identifier"].strip()
        ident = f" {identifier}." if identifier else ""
        lines.append(
            f"- **[{ref['id']}]** {prefix}({ref['year']}). *{ref['title']}*. {ref['journal']}.{ident} <{ref['url']}>"
        )
    lines.append("")
    return "\n".join(lines)


def check_doc_links(report: Report) -> None:
    """Ensure every relative Markdown link resolves to a file in the repository."""
    candidates = [ROOT / "README.md", ROOT / "CONTRIBUTING.md", ROOT / "CHANGELOG.md"]
    candidates += sorted((ROOT / "docs").rglob("*.md"))
    candidates += sorted((ROOT / "report").rglob("*.md"))
    for path in candidates:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for target in LINK_RE.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            relative = target.split("#", 1)[0]
            if not relative:
                continue
            if not (path.parent / relative).exists():
                report.error(
                    f"{path.relative_to(ROOT)}: broken relative link {target!r}"
                )


def write_outputs(outputs: dict[Path, str]) -> None:
    GEN.mkdir(parents=True, exist_ok=True)
    for path, text in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if generated files are stale")
    args = parser.parse_args()

    report = Report()
    refs, ref_ids = load_references(report)
    products = load_products(report)
    evidence = load_evidence(report, ref_ids)
    claims = load_claims(report, ref_ids)
    check_doc_links(report)

    outputs = {
        GEN / "brand-comparison.md": render_products(products),
        GEN / "evidence-tables.md": render_evidence(evidence),
        GEN / "claims-table.md": render_claims(claims),
        ROOT / "docs" / "references.md": render_references(refs),
    }

    if args.check:
        stale = []
        for path, text in outputs.items():
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                stale.append(str(path.relative_to(ROOT)))
        for item in stale:
            report.error(f"{item}: generated output is stale; run python analysis/build_tables.py")
    else:
        write_outputs(outputs)

    print("Creatine evidence repository validation")
    print(f"  products:   {len(products)}")
    print(f"  evidence:   {len(evidence)} rows")
    print(f"  claims:     {len(claims)} rows")
    print(f"  references: {len(refs)} entries")
    print(f"  warnings:   {len(report.warnings)}")
    print(f"  errors:     {len(report.errors)}")
    for warning in report.warnings:
        print(f"  WARN  {warning}")
    for error in report.errors:
        print(f"  ERROR {error}", file=sys.stderr)
    if report.errors:
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
