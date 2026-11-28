"""Stage the published Shi et al. (2026) evidence tables and restricted-source references.

No network access, no model fitting, no copying restricted articles. Table 1 is
transcribed from the CC BY 4.0 article; reference identifiers and DOIs come from
its bibliography. The staged CSVs are a structured transcription, not publisher
download bytes or individual participant data.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
from typing import Any

import yaml

SLUG = "shi-2026-ssb-adhd-study-estimates"
TITLE = "Shi et al. 2026: sugar-sweetened beverages and ADHD-related outcomes"
SOURCE = "https://doi.org/10.3389/fnut.2026.1858738"
HTML = "https://www.frontiersin.org/journals/nutrition/articles/10.3389/fnut.2026.1858738/full"
LICENSE = "https://creativecommons.org/licenses/by/4.0/"
RETRIEVED = "2026-11-28"
CITATION = (
    "Shi B, Ma MJ, Yang M, Li YQ (2026), Sugar-sweetened beverage consumption "
    "and attention-deficit/hyperactivity disorder symptoms in children and adolescents: "
    "a systematic review and meta-analysis of observational studies. Frontiers in Nutrition "
    "13:1858738. doi:10.3389/fnut.2026.1858738. Table 1, section 2.3–2.5, section 3.2; "
    "CC BY 4.0. Transcribed and reformatted into separate study and estimate tables; "
    "no original effect estimates recalculated."
)

STUDY_FIELDS = (
    "study_id", "review_reference", "year", "primary_doi", "region", "design",
    "n_study", "age_range", "mean_age_years", "exposure", "exposure_contrast",
    "contrast_type", "reporter", "outcome_group", "instrument", "adjustment_codes",
    "quality_score", "quality_max",
)
# One row per study. All fields are from Table 1 or its cited bibliography,
# except normalized labels, stable IDs, and summing Yu's 173 cases and 159 controls.
STUDIES: tuple[tuple[str | int | float, ...], ...] = (
    ("geng-2020", 29, 2020, "10.1016/j.jad.2020.01.076", "China",
     "cross-sectional", 27200, "3–6 years", 4.5, "ssb", ">=2/day vs <1/day",
     "categorical", "parent", "hyperactivity", "SDQ", "1;2;5;6;8;9;10;12;18;19", 8, 11),
    ("kim-2018", 32, 2018, "10.1016/j.appet.2018.05.004", "South Korea",
     "cross-sectional", 16831, "6–12 years", 9.29, "soft-drinks", ">=1/day vs never",
     "categorical", "parent", "adhd-specific", "K-ARS", "2;5;6;11", 8, 11),
    ("kim-2024", 12, 2024, "10.1159/000539458", "South Korea",
     "cohort", 365236, "18–24 months", 1.75, "ssb", ">=200 mL/day vs <200 mL/day",
     "categorical", "parent", "adhd-specific", "ICD-10", "5;11;12;21;23;27;28", 9, 9),
    ("lien-2006", 33, 2006, "10.2105/AJPH.2004.059477", "Norway",
     "cross-sectional", 5498, "15–16 years", 15.5, "soft-drinks", ">4 glasses/day vs 1–6 glasses/week",
     "categorical", "self", "hyperactivity", "SDQ", "6;7;13;14;15;17;20;24", 7, 11),
    ("yu-2016", 10, 2016, "10.3390/ijerph13070678", "Taiwan",
     "case-control", 332, "4–15 years", "", "ssb", ">=7/week vs 0/week",
     "categorical", "parent", "adhd-specific", "DSM-IV-TR", "1;6;14;22;25;26", 9, 9),
    ("schwartz-2015", 34, 2015, "10.1016/j.acap.2014.11.006", "United States",
     "cross-sectional", 1649, "6–18 years", 12.4, "ssb", "per additional drink/day",
     "continuous", "self", "hyperactivity", "SDQ", "2;3;5;7;11;16", 9, 11),
    ("zhang-2023", 13, 2023, "10.3390/nu15041034", "China",
     "cross-sectional", 6541, "6–12 years", 8.6, "ssb", ">=2/week vs 0/week",
     "categorical", "parent", "hyperactivity", "CTRS-R:S", "2;5;7;10;11;12;13;14;17", 9, 11),
    ("zhang-2021", 30, 2021, "10.3389/fpsyt.2021.573168", "China",
     "cross-sectional", 30188, "6–18 years", 12.4, "ssb", "high vs low frequency",
     "categorical", "mixed", "hyperactivity", "SDQ", "1;4;5;6;28;29", 8, 11),
    ("zhou-2022", 31, 2022, "10.16835/j.cnki.1000-9817.2022.01.015", "China",
     "cross-sectional", 7634, "3–6 years", 4.69, "ssb", ">=2/day vs <1/day",
     "categorical", "parent", "hyperactivity", "SDQ", "2;5;6;8;9;10;11;12", 7, 11),
)
EFFECT_FIELDS = (
    "study_id", "stratum", "adjusted_or_as_reported", "ci95_lower", "ci95_upper",
    "original_metric_status", "n_stratum", "source_locator",
)
# The cohort OR was converted by the review from a hazard ratio. The other
# entries are the review's adjusted ORs, not an independent primary-source audit.
# Sex-specific sample sizes are not given in Table 1; never duplicate study n.
EFFECTS: tuple[tuple[str | float, ...], ...] = (
    ("geng-2020", "overall", 1.11, 0.99, 1.26, "review-reported-or", "", "Table 1 ref 29"),
    ("kim-2018", "overall", 1.75, 1.33, 2.29, "review-reported-or", "", "Table 1 ref 32"),
    ("kim-2024", "overall", 1.17, 1.08, 1.28, "review-converted-hr-to-or", "", "Table 1 ref 12; section 2.3"),
    ("lien-2006", "boys", 1.99, 1.23, 3.24, "review-reported-or", "", "Table 1 ref 33"),
    ("lien-2006", "girls", 0.99, 0.47, 2.10, "review-reported-or", "", "Table 1 ref 33"),
    ("yu-2016", "overall", 3.69, 1.29, 10.60, "review-reported-or", "", "Table 1 ref 10"),
    ("schwartz-2015", "overall", 1.14, 1.06, 1.22, "review-reported-or", "", "Table 1 ref 34"),
    ("zhang-2023", "overall", 1.07, 0.82, 1.39, "review-reported-or", "", "Table 1 ref 13"),
    ("zhang-2021", "overall", 1.03, 0.93, 1.14, "review-reported-or", "", "Table 1 ref 30"),
    ("zhou-2022", "overall", 1.15, 1.00, 1.32, "review-reported-or", "", "Table 1 ref 31"),
)
BENCHMARK = {
    "status": "published-summary-not-independent-replication",
    "source_locator": "sections 2.3–2.5, 3.2, 3.4",
    "study_count": 9, "participant_count": 461109,
    "method": "Paule-Mandel random effects; Hartung-Knapp confidence interval",
    "pooled_or": 1.23, "ci95": [1.02, 1.48], "pi95": [0.79, 1.90],
    "i2_percent": 63.3, "tau_squared_log_or": 0.0434,
    "leave_out_kim_2018": {"or": 1.16, "ci95": [1.00, 1.34], "i2_percent": 42.1},
    "lfk_index": 3.37, "cohort_conversion_baseline_risk_approx": 0.02,
    "yu_2016_cases": 173, "yu_2016_controls": 159,
    "yu_2016_mean_age_cases": 9.2, "yu_2016_mean_age_controls": 8.9,
    "stratified_combination": "inverse variance on log OR; Lien 2006",
}
REFERENCES = (
    ("wolraich-1995-sugar-behaviour-meta-analysis",
     "Wolraich et al. (1995): controlled sugar challenges and children's behaviour/cognition",
     "Wolraich ML, Wilson DB, White JW; JAMA",
     "https://doi.org/10.1001/jama.1995.03530200053037",
     "https://pubmed.ncbi.nlm.nih.gov/7474248/",
     "Abstract confirms 16 reports, 23 within-subject studies and 14 outcome constructs; "
     "weighted estimates range from -0.14 to +0.30 and all pooled 95% CIs include zero. "
     "Full outcome estimates, variances, individual study estimates and paired correlations not recovered. "
     "Do not replace missing estimates with zero or reconstruct intervals from significance alone."),
    ("hoover-milich-1994-sugar-expectancies",
     "Hoover and Milich (1994): sugar-expectancy experiment",
     "Hoover DW, Milich R; Journal of Abnormal Child Psychology",
     "https://doi.org/10.1007/BF02168088", "https://doi.org/10.1007/BF02168088",
     "Expectation manipulation, not a sugar treatment contrast. Obtain report-level statistics "
     "if lawful access permits; keep separate from behavioural sugar intervention estimates."),
    ("wolraich-1994-sucrose-diet-trial",
     "Wolraich et al. (1994): sucrose and comparison diets in children",
     "Wolraich ML et al.; New England Journal of Medicine",
     "https://doi.org/10.1056/NEJM199402033300501", "https://doi.org/10.1056/NEJM199402033300501",
     "Controlled crossover diet study. Check whether it was included in the 1995 review; "
     "do not add it independently without resolving overlap and eligibility."),
    ("de-ruyter-2012-drink-trial",
     "de Ruyter et al. (2012): beverage substitution and body weight in children",
     "de Ruyter JC, Olthof MR, Seidell JC, Katan MB; New England Journal of Medicine",
     "https://doi.org/10.1056/NEJMoa1203034", "https://pubmed.ncbi.nlm.nih.gov/22998340/",
     "Randomized 18-month trial, 641 children; imputed analysis reports "
     "BMI z-score changes 0.02 vs 0.15 and weight gain 6.35 vs 7.37 kg "
     "(sugar-free minus sugar contrast); alternative measured sample less conclusive "
     "for BMI z-score. Physical health context, never pooled with behaviour."),
    ("farsad-naeimi-2020-sugar-adhd-review",
     "Farsad-Naeimi et al. (2020): sugar and ADHD observational evidence",
     "Farsad-Naeimi A et al.; Complementary Therapies in Medicine",
     "https://doi.org/10.1016/j.ctim.2020.102512", "https://doi.org/10.1016/j.ctim.2020.102512",
     "Earlier observational synthesis; use only for context until study overlap and "
     "exposure definitions are checked. Do not meta-analyze it with the 2026 summary."),
    ("who-2015-free-sugars-guideline",
     "WHO (2015): sugars intake for adults and children",
     "World Health Organization",
     "https://www.who.int/publications/i/item/9789241549028",
     "https://www.who.int/publications/i/item/9789241549028",
     "Guideline, not an independent study. Use for definition of free sugars, "
     "dental-caries and weight-gain evidence context; do not mirror the guideline."),
)


def csv_bytes(fields: tuple[str, ...], rows: tuple[tuple[Any, ...], ...]) -> bytes:
    """Serialize a stable UTF-8 table with LF line endings and an explicit header."""
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(fields)
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def json_bytes(value: Any) -> bytes:
    """Serialize source facts in deterministic, human-readable JSON."""
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def validate_tables(
    studies: tuple[tuple[Any, ...], ...] = STUDIES,
    effects: tuple[tuple[Any, ...], ...] = EFFECTS,
) -> None:
    """Reject duplicate studies, invalid effects and accidental cohort double counting."""
    if len(studies) != 9 or len(effects) != 10:
        raise ValueError("Expected 9 independent studies and 10 reported effects")
    if any(len(row) != len(STUDY_FIELDS) for row in studies):
        raise ValueError("Unexpected study field count")
    if any(len(row) != len(EFFECT_FIELDS) for row in effects):
        raise ValueError("Unexpected effect field count")
    ids = {row[0] for row in studies}
    if len(ids) != 9 or len({row[1] for row in studies}) != 9:
        raise ValueError("Duplicate study/reference")
    if any(type(row[5]) is not str or type(row[6]) is not int or row[6] <= 0 for row in studies):
        raise ValueError("Invalid study sample size")
    if sum(row[6] for row in studies) != 461109:
        raise ValueError("Study participant count does not match published total")
    if len({(row[0], row[1]) for row in effects}) != len(effects):
        raise ValueError("Duplicate study/stratum estimate")
    for study_id, stratum, estimate, lower, upper, metric, n_stratum, _ in effects:
        if study_id not in ids or stratum not in {"overall", "boys", "girls"}:
            raise ValueError("Unknown study or stratum")
        if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in (estimate, lower, upper)):
            raise ValueError("Non-finite effect estimate")
        if not 0 < lower < estimate < upper:
            raise ValueError("Invalid effect interval")
        expected_metric = "review-converted-hr-to-or" if study_id == "kim-2024" else "review-reported-or"
        if metric != expected_metric or n_stratum != "":
            raise ValueError("Unexpected source metric or invented stratum sample size")
    for study_id in ids:
        strata = {row[1] for row in effects if row[0] == study_id}
        expected = {"boys", "girls"} if study_id == "lien-2006" else {"overall"}
        if strata != expected:
            raise ValueError(f"Incorrect within-study strata: {study_id}")


def stage(root: Path) -> None:
    """Stage reviewed transcription and metadata; refuse overwrites."""
    validate_tables()
    target = root / "datasets" / SLUG
    policy_path = root / "reports" / "canonical-adoption-policy.json"
    adoption = json.loads(policy_path.read_text(encoding="utf-8"))
    references = [root / "external" / row[0] for row in REFERENCES]
    if target.exists() or any(path.exists() for path in references):
        raise ValueError("Existing registration; refusing overwrite")
    if any(entry["dataset_id"] == SLUG for entry in adoption["exemptions"]):
        raise ValueError("Existing adoption exemption")
    raw = target / "raw"
    raw.mkdir(parents=True, exist_ok=False)
    payloads = {
        "studies.csv": (csv_bytes(STUDY_FIELDS, STUDIES), "csv", 9,
                        "Structured transcription of Table 1 and reference DOIs; one row per study."),
        "effects.csv": (csv_bytes(EFFECT_FIELDS, EFFECTS), "csv", 10,
                         "Table 1 adjusted ORs and 95% CIs; two strata for Lien 2006."),
        "published_summary.json": (json_bytes(BENCHMARK), "json", None,
                                  "Source-reported benchmarks and design facts, not model output."),
    }
    files: list[dict[str, Any]] = []
    for name, (payload, fmt, count, note) in payloads.items():
        (raw / name).write_bytes(payload)
        entry: dict[str, Any] = {
            "path": f"raw/{name}", "role": "raw", "format": fmt, "encoding": "utf-8",
            "sha256": hashlib.sha256(payload).hexdigest(),
            "notes": note + " Locally transcribed representation; not publisher byte snapshot.",
        }
        if count is not None:
            entry["row_count"] = count
        files.append(entry)
    metadata = {
        "schema_version": 1, "id": SLUG, "title": TITLE,
        "description": "Nine observational studies; ten published adjusted OR estimates. "
                       "Separate study denominators, sex strata and published summary benchmarks.",
        "domain": ["public-health", "nutrition", "epidemiology", "adhd"],
        "source": {"publisher": "Shi, Ma, Yang and Li; Frontiers in Nutrition",
                   "url": HTML, "retrieved_at": RETRIEVED,
                   "snapshot": "Article DOI 10.3389/fnut.2026.1858738, published 2026-09-16; "
                               "Table 1 and methods/results transcribed 2026-11-28"},
        "license": {"name": "CC BY 4.0 (article and attributed table transcription)",
                    "url": LICENSE, "redistribution": "allowed"},
        "citation": {"text": CITATION, "url": SOURCE},
        "files": files, "lineage": [],
    }
    (target / "metadata.yaml").write_text(
        yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True), encoding="utf-8")
    (target / "README.md").write_text(
        f"# {TITLE}\n\n{CITATION}\n\n"
        f"Source: {HTML}\n\n"
        "The three files preserve selected reported facts from Table 1, its references and sections 2–3 "
        "in a normalized, versioned form. SHA-256 covers these UTF-8 representations, not the upstream article. "
        "Original article copyright © 2026 Shi, Ma, Yang and Li. "
        f"[CC BY 4.0]({LICENSE}); [Frontiers copyright policy]"
        "(https://www.frontiersin.org/legal/copyright-statement). Attribution is required.\n\n"
        "## Interpretation\n\n"
        "- Count participants once per study, not per effect. Lien has two strata with unknown stratum n.\n"
        "- The cohort OR is the review's conversion of an HR using an approximately 2% baseline risk. "
        "Do not convert it again. Primary-source effect metrics and conversions are not independently audited.\n"
        "- Exposure definitions include soft drinks, heterogeneous frequency/volume thresholds and a continuous contrast. "
        "Do not interpret the pooled result as a uniform intervention or causal effect.\n"
        "- Adjustment codes refer to Table 1's footnote; they are not harmonized covariate names. "
        "The sex/gender codes are retained separately. Quality scales have different maxima by design.\n"
        "- Yu's study size is 173 cases plus 159 controls; separate mean ages are in the summary JSON. "
        "No age or sex-specific counts have been imputed.\n"
        "- Article narrative states an upper age of 16, while Table 1 reports two studies spanning 6–18 years; "
        "the table's ranges are retained. The source remains authoritative for inconsistencies.\n"
        "- Pooled statistics are published benchmarks. An independent reproduction requires "
        "log-OR standard errors, within-study combination, Paule-Mandel and Hartung-Knapp; "
        "rounding can cause discrepancies.\n"
        "- No restricted source PDFs or individual participant data are stored.\n",
        encoding="utf-8")
    for slug, title, publisher, url, evidence, note in REFERENCES:
        folder = root / "external" / slug
        folder.mkdir(parents=True, exist_ok=False)
        external = {
            "schema_version": 1, "status": "external-reference", "id": slug,
            "title": title, "publisher": publisher, "source_url": url,
            "redistribution": "unresolved", "storage": "authoritative-upstream",
            "usage": {"storage": "authoritative-upstream", "redistribution": "unresolved",
                      "attribution_required": True, "note": note},
            "consumers": ["medium-blog/sugar-rush-evidence-audit"],
            "resolution": {"review_status": "actionable", "last_reviewed": RETRIEVED,
                           "blocker_category": "redistribution-rights",
                           "blocker_summary": "No explicit redistribution permission established for this source. Metadata only.",
                           "evidence": [evidence], "reviewer_note": note,
                           "next_action": "Verify source access and article-specific reuse terms before mirroring any bytes.",
                           "terminal": False},
        }
        (folder / "metadata.yaml").write_text(
            yaml.safe_dump(external, sort_keys=False, allow_unicode=True), encoding="utf-8")
        (folder / "README.md").write_text(
            f"# {title}\n\nSource: {url}\n\n{note}\n\n"
            "External reference only; full-text/data redistribution rights not established. "
            "No source files are mirrored. The named research consumer is planned.\n",
            encoding="utf-8")
    adoption["exemptions"].append({
        "dataset_id": SLUG,
        "rationale": "Registration precedes the planned Medium-Blog/sugar-rush-evidence-audit "
                     "consumer; remove when implemented consumer pins the merged registry revision and hashes.",
    })
    policy_path.write_bytes(json_bytes(adoption))


def main() -> None:
    """Stage the data into an existing registry checkout."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    stage(parser.parse_args().root)


if __name__ == "__main__":
    main()
