"""Validate the v2 Discovery Engine data contract against the frozen 365-record pilot.

This is a read-only analysis of the pilot CSV. It does not call an LLM, change raw
or pilot inputs, assign human labels, or claim that candidate classifications are
validated. The candidate-pattern rules intentionally mirror the browser layer.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "data" / "processed" / "pilot" / "classification_output.csv"
REPORT = ROOT / "analysis" / "engine_pilot_validation.md"

REQUIRED = [
    "record_id", "source", "source_type", "raw_text", "evidence_type",
    "journey_stage", "wishlist_link", "outcome_signal", "barrier_theme",
    "discovery_trigger", "confidence", "model", "prompt_version",
    "human_review_status", "human_label", "include_in_quantitative_analysis",
]


def read_rows() -> list[dict[str, str]]:
    with PILOT.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def is_candidate(row: dict[str, str]) -> bool:
    return (
        row.get("include_in_quantitative_analysis", "").lower() != "no"
        and row.get("evidence_type") in {"direct_wishlist_behavior", "pre_purchase_hesitation"}
        and row.get("wishlist_link") in {"explicit_direct", "explicit_pre_purchase"}
        and row.get("barrier_theme", "other/unclear") != "other/unclear"
    )


def table(counter: Counter[str]) -> str:
    if not counter:
        return "| *(none)* | 0 |\n|---|---:|"
    return "\n".join(f"| `{key or '(blank)'}` | {count} |" for key, count in counter.most_common())


def main() -> None:
    rows = read_rows()
    headers = set(rows[0]) if rows else set()
    missing_columns = [field for field in REQUIRED if field not in headers]
    duplicate_ids = [record_id for record_id, count in Counter(r.get("record_id", "") for r in rows).items() if count > 1]
    pending = sum(r.get("human_review_status") == "pending" for r in rows)
    labels = sum(bool(r.get("human_label", "").strip()) for r in rows)
    candidate_rows = [r for r in rows if is_candidate(r)]

    source_counts = Counter(r.get("source", "") for r in rows)
    evidence_counts = Counter(r.get("evidence_type", "") for r in rows)
    journey_counts = Counter(r.get("journey_stage", "") for r in rows)
    wishlist_counts = Counter(r.get("wishlist_link", "") for r in rows)
    source_theme: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        source_theme[row.get("source", "")][row.get("barrier_theme", "")] += 1

    heuristic_actual = Counter((r.get("heuristic_relevance", "(none)"), r.get("evidence_type", "(blank)")) for r in rows)
    potential_filter_conflicts = [
        r for r in rows
        if r.get("heuristic_relevance") in {"HIGH", "MEDIUM"}
        and r.get("evidence_type") in {"post_purchase_complaint", "irrelevant_or_unclear"}
    ]
    ambiguous = [
        r for r in rows
        if r.get("evidence_type") == "irrelevant_or_unclear"
        or r.get("wishlist_link") == "inferred_or_ambiguous"
    ]
    patterns: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in candidate_rows:
        patterns[row.get("barrier_theme", "other/unclear")].append(row)

    lines = [
        "# Discovery Engine pilot validation",
        "",
        "This report was generated from `data/processed/pilot/classification_output.csv` using the v2 browser-layer candidate rules. It is a technical/data-contract validation, not human adjudication and not a final research conclusion.",
        "",
        "## Coverage and governance checks",
        "",
        f"- Pilot records processed: **{len(rows)}**",
        f"- Required columns missing: **{', '.join(missing_columns) if missing_columns else 'none'}**",
        f"- Duplicate record IDs: **{len(duplicate_ids)}**",
        f"- Records with `human_review_status=pending`: **{pending}/{len(rows)}**",
        f"- Non-empty `human_label` values: **{labels}** (must remain 0 until adjudication)",
        f"- Candidate wishlist-linked direct/pre-purchase records: **{len(candidate_rows)}**",
        "- Human agreement, accuracy, and validation metrics: **not computed**",
        "",
        "## Funnel counts",
        "",
        "| Stage | Count |",
        "|---|---:|",
        f"| Research | {len(rows)} |",
        f"| Relevance (raw text plus source/relevance context) | {sum(bool(r.get('raw_text')) and bool(r.get('heuristic_relevance') or r.get('source_type')) for r in rows)} |",
        f"| Evidence type | {sum(bool(r.get('evidence_type')) for r in rows)} |",
        f"| Journey stage | {sum(bool(r.get('journey_stage')) for r in rows)} |",
        f"| Wishlist linkage | {sum(bool(r.get('wishlist_link')) for r in rows)} |",
        f"| Primary intent (available or conservatively mapped) | {sum(bool(r.get('intent_signal')) or r.get('outcome_signal') == 'considering_or_waiting' for r in rows)} |",
        f"| Outcome | {sum(bool(r.get('outcome_signal')) for r in rows)} |",
        f"| Barrier | {sum(bool(r.get('barrier_theme')) for r in rows)} |",
        f"| Trigger | {sum(bool(r.get('discovery_trigger')) for r in rows)} |",
        f"| User context/segment fields captured | {sum(bool(r.get('respondent_id') or r.get('question_field') or r.get('user_context')) for r in rows)} |",
        f"| Evidence strength/confidence | {sum(bool(r.get('confidence')) for r in rows)} |",
        f"| Candidate cross-source patterns | {sum(len({r.get('source') for r in group}) > 1 for group in patterns.values())} |",
        f"| Candidate patterns | {len(patterns)} |",
        f"| Candidate problem hypotheses | {len(patterns)} |",
        "",
        "## Counts by source",
        "",
        "| Source | Records |",
        "|---|---:|",
        table(source_counts),
        "",
        "## Counts by evidence type",
        "",
        "| Evidence type | Records |",
        "|---|---:|",
        table(evidence_counts),
        "",
        "## Counts by journey stage",
        "",
        "| Journey stage | Records |",
        "|---|---:|",
        table(journey_counts),
        "",
        "## Counts by wishlist linkage",
        "",
        "| Wishlist linkage | Records |",
        "|---|---:|",
        table(wishlist_counts),
        "",
        "## Theme distribution by source",
        "",
    ]
    for source in sorted(source_theme):
        lines.extend([f"### {source}", "", "| Barrier theme | Records |", "|---|---:|", table(source_theme[source]), ""])

    lines.extend([
        "## Heuristic relevance versus candidate classification",
        "",
        "| Heuristic relevance | Evidence type | Records |",
        "|---|---|---:|",
    ])
    lines.extend(f"| `{h}` | `{e}` | {n} |" for (h, e), n in sorted(heuristic_actual.items()))
    lines.extend([
        "",
        "The table describes deterministic pilot labels; it does not establish that the heuristic or the classification is correct.",
        "",
        "## Potential keyword-filter false positives",
        "",
        "These are review-priority examples where HIGH/MEDIUM heuristic relevance co-occurs with a contextual or unclear candidate evidence type. They are not confirmed false positives until human review.",
        "",
        "| Record ID | Source | Heuristic | Candidate type | Raw text excerpt |",
        "|---|---|---|---|---|",
    ])
    for row in potential_filter_conflicts[:20]:
        excerpt = row.get("raw_text", "").replace("|", "\\|").replace("\n", " ")[:180]
        lines.append(f"| `{row.get('record_id')}` | {row.get('source')} | {row.get('heuristic_relevance')} | {row.get('evidence_type')} | {excerpt} |")
    if not potential_filter_conflicts:
        lines.append("| *(none identified by this rule)* | | | | |")

    lines.extend([
        "",
        "## Candidate wishlist-specific barriers",
        "",
        "The following are candidate pattern rows produced by the funnel rule: explicit wishlist linkage, direct/pre-purchase evidence type, included record, and non-unclear barrier. Every row remains pending human review.",
        "",
        "| Candidate theme | Records | Sources | Status | Trace IDs |",
        "|---|---:|---|---|---|",
    ])
    for theme, group in sorted(patterns.items(), key=lambda item: (-len(item[1]), item[0])):
        sources = sorted({r.get("source", "") for r in group})
        ids = ", ".join(r.get("record_id", "") for r in group[:8])
        status = "HYPOTHESIS — pending human review"
        lines.append(f"| {theme} | {len(group)} | {', '.join(sources)} | {status} | `{ids}` |")

    lines.extend([
        "",
        "## Ambiguous/unclear records",
        "",
        f"- Records selected for review under the conservative ambiguity rule: **{len(ambiguous)}**.",
        "- No ambiguous record was recoded or excluded by this validation script.",
        "",
        "## Contradictory evidence",
        "",
        "No contradiction claim is made. The pilot has candidate labels only, no human adjudication, and no explicit contradiction-resolution protocol. Reviewers should compare direct/pre-purchase records against contextual/post-purchase records without treating the latter as wishlist causality.",
        "",
        "## Human review required",
        "",
        "- Review all direct wishlist records and the random controls in `human_review_queue.csv`.",
        "- Adjudicate evidence type, wishlist linkage, barrier theme, confidence, and include/exclude status.",
        "- Record human labels in a separate review artifact; do not overwrite candidate labels or populate review fields automatically.",
        "- Recompute patterns and cross-source checks only after adjudication.",
    ])
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Validated {len(rows)} records; wrote {REPORT}")


if __name__ == "__main__":
    main()
