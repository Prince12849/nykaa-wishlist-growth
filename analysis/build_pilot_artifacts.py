"""Build the approved read-only pilot artifacts from existing source files.

The cleaned workbook is read through artifact-tool before this script runs and
passed as a temporary JSON export. The script never writes to raw sources.
"""
import csv
import hashlib
import json
import random
import re
from collections import Counter
from pathlib import Path

ROOT = Path(r"C:\Users\princ\Desktop\My project\nykaa-wishlist-growth")
OUT = ROOT / "data" / "processed" / "pilot"
SURVEY_VALUES = Path(r"C:\Users\princ\AppData\Local\Temp\nykaa-wishlist-readonly-audit\survey_values.json")
MODEL = "NOT_RUN — deterministic pre-label only; Anthropic engine not executed"
PROMPT_VERSION = "research/classification-prompt.md | pilot-taxonomy-v0.1"
METHOD = "Existing Discovery Engine schema/prompt; deterministic pre-label for workflow testing only; human review pending"

FIELDS = [
    "age_range", "current_city", "online_fashion_shopping_frequency",
    "preferred_platform_clothing", "preferred_platform_footwear", "preferred_platform_accessories",
    "nykaa_fashion_usage_frequency", "wishlist_saved_items_usage", "wishlist_item_types",
    "purchased_after_wishlist", "last_wishlisted_product_outcome", "purchase_barriers",
    "purchase_likelihood", "purchase_triggers", "one_thing_to_help_purchase_wishlist",
]
FIELD_LABELS = {f: f.replace("_", " ").title() for f in FIELDS}
DIRECT_FIELDS = {"wishlist_saved_items_usage", "wishlist_item_types", "purchased_after_wishlist", "last_wishlisted_product_outcome"}
PRE_FIELDS = {"purchase_barriers", "purchase_likelihood", "purchase_triggers", "one_thing_to_help_purchase_wishlist"}

T = {
    "value": "value/price assessment", "fit": "fit/size confidence",
    "quality": "quality/material confidence", "info": "review/product-information confidence",
    "trust": "trust/authenticity", "stock": "availability/stock",
    "comparison": "comparison/alternative", "occasion": "occasion/styling",
    "memory": "deprioritization/memory", "ux": "wishlist/UX discoverability",
    "unclear": "other/unclear",
}
E = {
    "direct": "direct_wishlist_behavior", "pre": "pre_purchase_hesitation",
    "general": "general_shopping_friction", "post": "post_purchase_complaint",
    "context": "competitor_product_context", "unclear": "irrelevant_or_unclear",
}

def clean(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()

def themes(text):
    t = text.lower()
    rules = [
        (T["value"], r"price|discount|afford|expensive|cost|value"),
        (T["fit"], r"size|fit|fitting|sizing|runs small|runs big"),
        (T["quality"], r"quality|fabric|material|cloth|damage|poor product"),
        (T["info"], r"review|rating|photo|video|information|description"),
        (T["trust"], r"fake|authentic|fraud|legit|trust"),
        (T["stock"], r"out of stock|stocked out|back in stock|available|availability"),
        (T["comparison"], r"compar|alternative|elsewhere|similar product|other app"),
        (T["occasion"], r"occasion|style|styling|wedding|birthday"),
        (T["memory"], r"forgot|forget|remember|depriorit|discard"),
        (T["ux"], r"wishlist|wish list|saved|save for later|organis|scroll|notification|chatbot"),
    ]
    result = []
    for label, pattern in rules:
        if re.search(pattern, t) and label not in result:
            result.append(label)
    return result or [T["unclear"]]

def trigger(text):
    t = text.lower()
    if re.search(r"price drop|price falls|price lowered|discount", t): return "Price Drop Alert"
    if re.search(r"back.?in.?stock|size becomes available|available", t): return "Push Notification"
    if re.search(r"search|compar|review|rating|photo|video|information", t): return "Search Revisit"
    if re.search(r"styling|occasion|wedding|influencer", t): return "Social or Influencer Prompt"
    if re.search(r"wishlist|wish list|saved", t): return "Browsing Wishlist Directly"
    return "Not Mentioned"

def outcome(text):
    t = text.lower()
    if re.search(r"purchased|bought it|i bought|ordered", t): return "purchased"
    if re.search(r"out of stock|stocked out|unavailable", t): return "unavailable_or_out_of_stock"
    if re.search(r"similar product elsewhere|better product elsewhere|other app", t): return "alternative_purchase"
    if re.search(r"still considering|still thinking|waiting|not sure", t): return "considering_or_waiting"
    if re.search(r"decided not|changed my mind|forgot|discard", t): return "not_purchased_or_deprioritized"
    if re.search(r"return|refund|wrong product|delivery|order", t): return "post_purchase_issue"
    return "unknown"

def classify_survey(r):
    field, text = r["question_field"], r["raw_text"]
    if field in DIRECT_FIELDS:
        et, stage, link = E["direct"], ("post_wishlist_outcome" if field == "last_wishlisted_product_outcome" else "wishlist_behavior"), "explicit_direct"
        include, exclusion = ("yes", "") if text else ("no", "blank response")
    elif field in PRE_FIELDS:
        et, stage, link = E["pre"], "pre_purchase", "explicit_pre_purchase"
        include, exclusion = ("yes", "") if text else ("no", "blank response")
    elif text:
        et, stage, link, include, exclusion = E["unclear"], "context", "not_mentioned", "no", "context or non-evidence field"
    else:
        et, stage, link, include, exclusion = E["unclear"], "unknown", "not_mentioned", "no", "blank response"
    ts = themes(text)
    out = outcome(text)
    if field == "purchased_after_wishlist": out = "purchased_after_wishlist_reported" if "yes" in text.lower() else "rare_or_not_reported"
    if field == "purchase_likelihood": out = "self_reported_likelihood_only"
    return et, stage, link, out, ts, trigger(text), ("reduce uncertainty before buying" if et == E["pre"] else "retain and act on wishlist intent" if et == E["direct"] else "context only"), ("Low" if not text or et == E["unclear"] else "High"), include, exclusion, "Field-aware survey coding; not a causal or 30-day outcome label"

def classify_review(text):
    t = text.lower()
    false_saved = bool(re.search(r"saved (my )?(payment|card|details)|save(d)? (my )?(payment|card)", t))
    explicit = bool(re.search(r"\bwish\s*list\b|\bsaved\b|\bsave for later\b", t)) and not false_saved
    post = bool(re.search(r"return|refund|wrong product|received|delivery|order|customer care|support|courier|pickup|shipped", t))
    pre = bool(re.search(r"still deciding|still thinking|waiting for|not sure|compar|price drop|size chart|out of stock|better product elsewhere", t))
    general = bool(re.search(r"price|discount|quality|fit|size|fabric|material|review|rating|fake|authentic|delivery|search|notification|wishlist", t))
    if false_saved:
        et, stage, link, reason = E["unclear"], "non-wishlist_saved_reference", "not_wishlist", "keyword match refers to saved payment/card details, not wishlist behavior"
    elif explicit and not post:
        et, stage, link, reason = E["direct"], "wishlist_behavior_or_revisit", "explicit_direct", ""
    elif pre and not post:
        et, stage, link, reason = E["pre"], "pre_purchase", ("explicit_pre_purchase" if re.search(r"wish\s*list|saved|save for later", t) else "inferred_or_ambiguous"), ""
    elif post:
        et, stage, link, reason = E["post"], "post_purchase", ("explicit_direct" if explicit else "not_mentioned"), ""
    elif general:
        et, stage, link, reason = E["general"], "general_shopping", "not_mentioned", ""
    else:
        et, stage, link, reason = E["unclear"], "unknown", "not_mentioned", "insufficient signal for journey-stage classification"
    ts = themes(text)
    conf = "Low" if et == E["unclear"] else "High" if et in {E["direct"], E["post"]} else "Medium"
    inc = "yes" if et in {E["direct"], E["pre"]} else "no"
    return et, stage, link, outcome(text), ts, trigger(text), ("retain and act on wishlist intent" if et == E["direct"] else "reduce uncertainty before buying" if et == E["pre"] else "context only"), conf, inc, reason, ("Heuristic false-positive candidate" if false_saved else "Public review classification; no causal wishlist inference")

def sid(source, date, rating, text, index):
    value = f"{source}|{date}|{rating}|{text}|{index}".encode("utf-8")
    return source.lower().replace(" ", "_") + "_" + hashlib.sha256(value).hexdigest()[:16]

def read_csv(path, source):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return [{"record_id": sid(source, r.get("date", ""), r.get("rating", ""), r.get("text", ""), i), "source": source, "source_type": "public_app_review", "respondent_id": "", "question_field": "", "question_label": "", "original_response": r.get("text", ""), "raw_text": clean(r.get("text", "")), "rating": r.get("rating", ""), "heuristic_relevance": r.get("relevance", ""), "sample_stratum": "", "source_file": path.relative_to(ROOT).as_posix(), "published_at": r.get("date", "")} for i, r in enumerate(csv.DictReader(f))]

def pick(pool, available, selected, n, label, seed):
    candidates = [r for r in pool if r["record_id"] in available]
    random.Random(seed).shuffle(candidates)
    for r in candidates[:n]:
        available.remove(r["record_id"])
        selected.append({**r, "sample_stratum": label})

def csv_write(path, rows, columns):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)

def md_table(counter, h1, h2="Records"):
    lines = [f"| {h1} | {h2} |", "|---|---:|"]
    lines += [f"| {k.replace('|', '\\|')} | {v} |" for k, v in counter.most_common()]
    return "\n".join(lines)

values = json.loads(SURVEY_VALUES.read_text(encoding="utf-8"))
headers = [str(x or "") for x in values[0]]
survey_rows = [dict(zip(headers, ["" if x is None else str(x) for x in row])) for row in values[1:]]
pilot = []
for i, row in enumerate(survey_rows, 1):
    rid = f"survey_r{i:03d}"
    for field in FIELDS:
        original = row.get(field, "")
        pilot.append({"record_id": f"{rid}_{field}", "source": "survey", "source_type": "primary_research", "respondent_id": rid, "question_field": field, "question_label": FIELD_LABELS[field], "original_response": original, "raw_text": clean(original), "rating": "", "heuristic_relevance": "", "sample_stratum": "all_survey_responses", "source_file": "data/processed/survey/Fashion Shopping & Wishlist Preferences (Responses) - cleaned.xlsx", "published_at": ""})

review_pool = read_csv(ROOT / "nykaa_reviews_tagged.csv", "Play Store") + read_csv(ROOT / "nykaa_appstore_reviews_tagged.csv", "App Store")
available = {r["record_id"] for r in review_pool}; selected = []
play = [r for r in review_pool if r["source"] == "Play Store"]; app = [r for r in review_pool if r["source"] == "App Store"]
explicit = re.compile(r"\bwish\s*list\b|\bsaved\b|\bsave for later\b", re.I)
pre = re.compile(r"still deciding|still thinking|waiting for|not sure|compar|price drop|size chart|out of stock|better product elsewhere", re.I)
general = re.compile(r"price|discount|quality|fit|size|fabric|material|review|rating|fake|authentic|delivery|search|notification|wishlist", re.I)
post = re.compile(r"return|refund|wrong product|received|delivery|order|customer care|support|courier|pickup|shipped", re.I)
pick([r for r in play if explicit.search(r["raw_text"])], available, selected, 20, "explicit_wishlist_keyword", 101)
pick([r for r in play if pre.search(r["raw_text"]) and not explicit.search(r["raw_text"])], available, selected, 8, "pre_purchase_hesitation_keyword", 102)
pick([r for r in app if pre.search(r["raw_text"]) and not explicit.search(r["raw_text"])], available, selected, 2, "pre_purchase_hesitation_keyword_appstore", 105)
pick([r for r in play if general.search(r["raw_text"]) and not pre.search(r["raw_text"]) and not explicit.search(r["raw_text"])], available, selected, 8, "general_friction_keyword", 103)
pick([r for r in app if general.search(r["raw_text"]) and not pre.search(r["raw_text"]) and not explicit.search(r["raw_text"])], available, selected, 2, "general_friction_keyword_appstore", 106)
pick([r for r in play if post.search(r["raw_text"]) and not pre.search(r["raw_text"]) and not explicit.search(r["raw_text"])], available, selected, 8, "post_purchase_complaint_keyword", 104)
pick([r for r in app if post.search(r["raw_text"]) and not pre.search(r["raw_text"]) and not explicit.search(r["raw_text"])], available, selected, 2, "post_purchase_complaint_keyword_appstore", 107)
for rel, seed in [("HIGH", 201), ("MEDIUM", 202), ("LOW", 203)]:
    pick([r for r in play if r["heuristic_relevance"] == rel], available, selected, 3, f"random_control_{rel}", seed)
    pick([r for r in app if r["heuristic_relevance"] == rel], available, selected, 2, f"random_control_{rel}_appstore", seed + 50)
pilot += selected

classifications = []
for r in pilot:
    labels = classify_survey(r) if r["source"] == "survey" else classify_review(r["raw_text"])
    et, stage, link, out, ts, trig, need, conf, inc, reason, notes = labels
    classifications.append({**r, "evidence_type": et, "journey_stage": stage, "wishlist_link": link, "outcome_signal": out, "barrier_theme": ts[0], "secondary_theme": " | ".join(ts[1:]), "discovery_trigger": trig, "underlying_need": need, "confidence": conf, "model": MODEL, "prompt_version": PROMPT_VERSION, "human_review_status": "pending", "human_label": "", "include_in_quantitative_analysis": inc, "exclusion_reason": reason, "classification_method": METHOD, "classification_notes": notes})

queue = []
for r in classifications:
    reasons = []
    if r["evidence_type"] == E["direct"]: reasons.append("all direct wishlist behavior")
    if r["confidence"] == "High": reasons.append("high confidence")
    if r["confidence"] == "Low" or r["wishlist_link"] == "inferred_or_ambiguous" or r["evidence_type"] == E["unclear"]: reasons.append("uncertain/unclear")
    if r["source"] != "survey" and r["heuristic_relevance"] == "HIGH" and r["evidence_type"] not in {E["direct"], E["pre"]}: reasons.append("heuristic conflict")
    if r["sample_stratum"].startswith("random_control"): reasons.append("random control")
    queue.append({**r, "review_priority": "P1" if any(x != "random control" for x in reasons) else "P2", "review_reason": "; ".join(reasons) or "pilot record", "reviewer_label": "", "reviewer_notes": "", "review_status": "pending"})

pilot_cols = ["record_id", "source", "source_type", "respondent_id", "question_field", "question_label", "original_response", "raw_text", "rating", "heuristic_relevance", "sample_stratum", "source_file", "published_at"]
class_cols = ["record_id", "source", "source_type", "respondent_id", "question_field", "raw_text", "rating", "heuristic_relevance", "evidence_type", "journey_stage", "wishlist_link", "outcome_signal", "barrier_theme", "secondary_theme", "discovery_trigger", "underlying_need", "confidence", "model", "prompt_version", "human_review_status", "human_label", "include_in_quantitative_analysis", "exclusion_reason", "classification_method", "classification_notes", "sample_stratum", "source_file", "published_at"]
queue_cols = class_cols + ["review_priority", "review_reason", "reviewer_label", "reviewer_notes", "review_status"]
OUT.mkdir(parents=True, exist_ok=True)
csv_write(OUT / "pilot_dataset.csv", pilot, pilot_cols)
csv_write(OUT / "classification_output.csv", classifications, class_cols)
csv_write(OUT / "human_review_queue.csv", queue, queue_cols)

source_counts = Counter(r["source"] for r in classifications)
etype_counts = Counter(r["evidence_type"] for r in classifications)
stage_counts = Counter(r["journey_stage"] for r in classifications)
link_counts = Counter(r["wishlist_link"] for r in classifications)
review_rows = [r for r in classifications if r["source"] != "survey"]
comparison = Counter(f"{r['heuristic_relevance'] or '(blank)'} -> {r['evidence_type']}" for r in review_rows)
candidate = [r for r in classifications if r["include_in_quantitative_analysis"] == "yes" and r["evidence_type"] in {E["direct"], E["pre"]}]
false_positive = [r for r in review_rows if r["heuristic_relevance"] == "HIGH" and r["evidence_type"] not in {E["direct"], E["pre"]}][:8]
ambiguous = [r for r in classifications if r["evidence_type"] == E["unclear"] or r["wishlist_link"] == "inferred_or_ambiguous"][:8]

manifest = f"""# Pilot provenance/source manifest

Pilot build date: 2 September 2026 (IST)

This pilot uses existing on-disk files only. No scraper was run and no raw file was modified.

| Source file | Role | Records used | Notes |
|---|---|---:|---|
| 'data/processed/survey/Fashion Shopping & Wishlist Preferences (Responses) - cleaned.xlsx' | Primary research | 20 respondents / 300 field units | All 20 respondents; 15 substantive fields per respondent. Timestamp and blank email field were not evidence units. |
| 'nykaa_reviews_tagged.csv' | Nykaa Play Store public reviews | {source_counts['Play Store']} | Existing heuristic-tagged corpus; no stable review IDs or URLs. |
| 'nykaa_appstore_reviews_tagged.csv' | Nykaa App Store public reviews | {source_counts['App Store']} | Existing heuristic-tagged corpus; no stable review IDs or URLs. |
| 'research/all_reviews.csv' | Excluded | 0 | Derived combined snapshot intentionally excluded. |
| AJIO/Myntra files | Excluded from this pilot | 0 | AJIO blocked; Myntra frozen contextual evidence. |

## Sampling strata

The Nykaa review sample uses deterministic seeded selection for explicit wishlist/saved-item matches, pre-purchase hesitation, general friction, post-purchase complaints, and five controls from each HIGH/MEDIUM/LOW heuristic group.

## Classification provenance

The output schema follows the existing Discovery Engine prompt and taxonomy structure. The browser Anthropic engine was not executed because no API credential or secure backend is available. Labels are deterministic pre-labels for workflow testing only and remain human-review-pending; they are not AI classifications or validated findings.
"""
(OUT / "provenance_source_manifest.md").write_text(manifest, encoding="utf-8")

analysis = f"""# AI Discovery Engine pilot analysis

Status: PILOT ONLY — no final problem statement or MVP decision.

## Execution caveat

The browser Discovery Engine was not executed because ANTHROPIC_API_KEY is absent and the HTML has no secure credential/backend boundary. Browser-engine AI coverage: 0%. Deterministic pre-label coverage: {len(classifications)}/{len(pilot)} ({len(classifications)/len(pilot)*100:.1f}%). All records remain human-review-pending.

## Pilot size

- Total pilot records: **{len(pilot)}**
- Survey field-aware units: **{source_counts['survey']}**
- Nykaa Play Store review units: **{source_counts['Play Store']}**
- Nykaa App Store review units: **{source_counts['App Store']}**
- Full survey respondent count represented: **20**

## Records by source

{md_table(source_counts, 'Source')}

## Records by evidence type

{md_table(etype_counts, 'Evidence type')}

## Records by journey stage

{md_table(stage_counts, 'Journey stage')}

## Records by wishlist linkage

{md_table(link_counts, 'Wishlist linkage')}

## Theme distribution by source

### Survey

{md_table(Counter(r['barrier_theme'] for r in classifications if r['source'] == 'survey'), 'Theme label', 'Field units')}

### Play Store

{md_table(Counter(r['barrier_theme'] for r in classifications if r['source'] == 'Play Store'), 'Theme label')}

### App Store

{md_table(Counter(r['barrier_theme'] for r in classifications if r['source'] == 'App Store'), 'Theme label')}

These are deterministic pre-label counts, not AI-validated user findings. Survey counts reflect field units, not unique respondents; public-review counts reflect a stratified sample, not platform prevalence.

## Heuristic relevance versus pilot classification

{md_table(comparison, 'Heuristic relevance -> evidence type')}

The existing HIGH/MEDIUM/LOW field is a keyword prefilter, not a causal or wishlist-specific label.

## False-positive candidates

{chr(10).join('- ' + r['record_id'] + ' — ' + r['raw_text'][:220] for r in false_positive) or '- None selected.'}

## Ambiguous/unclear examples

{chr(10).join('- ' + r['record_id'] + ' — ' + r['evidence_type'] + '; ' + r['wishlist_link'] + '; ' + r['raw_text'][:220] for r in ambiguous) or '- None selected.'}

## Contradictory evidence

No contradiction should be declared from fallback labels alone. Reviewers should check cases where a respondent reports prior wishlist purchase but the most recent wishlisted item is still being considered, forgotten, abandoned, or unavailable. These may represent different episodes rather than logical errors.

## Candidate wishlist-specific barriers

These are hypotheses for human review, not validated barriers.

{md_table(Counter(r['barrier_theme'] for r in candidate), 'Candidate theme')}

## Human review requirements

- Review all direct_wishlist_behavior records.
- Review all HIGH-confidence records.
- Review all LOW-confidence and ambiguous records.
- Review HIGH-heuristic records classified as general, post-purchase, or unclear.
- Review every random control for keyword-filter bias.
- Record adjudicated labels and disagreement notes in human_review_queue.csv.

## Readiness

**Not ready to scale.** The taxonomy and workflow require an actual model run plus human review, especially because the browser engine was not executed, deterministic pre-labels are not AI classifications, public records lack stable provenance, and the current taxonomy does not natively encode evidence type or wishlist linkage.
"""
(OUT / "pilot_analysis_summary.md").write_text(analysis, encoding="utf-8")

taxonomy = """# Pilot taxonomy recommendation

Status: PROPOSED refinement only. This is not a validated finding and is not approval to scale.

## Keep

- direct_wishlist_behavior
- pre_purchase_hesitation
- general_shopping_friction
- post_purchase_complaint
- irrelevant_or_unclear

These categories prevent post-purchase or generic reviews from being misrepresented as wishlist causality.

## Merge

No barrier categories should be merged at this stage. The pilot is not human-reviewed, and the survey contains distinct concepts such as price, fit, quality, stock, comparison, and memory.

## Split

- Test the existing Fit, Size or Quality Doubt hypothesis as separate fit/size confidence and quality/material confidence labels.
- Test Price / Value Uncertainty separately from product-information uncertainty.

These are refinement candidates, not validated changes.

## Remove

Nothing should be removed from the hypothesis set yet. discovery_trigger remains a separate dimension and is not a barrier.

## Add for the next review round

- availability/stock
- review/product-information confidence
- wishlist/UX discoverability
- other/unclear with an explicit reason

## Required workflow refinement

Add evidence_type, journey_stage, wishlist_link, outcome_signal, include_in_quantitative_analysis, and human adjudication fields before scaling. The existing barrier taxonomy remains HYPOTHESIS until human review and cross-source comparison support it.
"""
(OUT / "taxonomy_recommendation.md").write_text(taxonomy, encoding="utf-8")

print(json.dumps({"total_pilot_records": len(pilot), "survey_units": source_counts["survey"], "play_store_units": source_counts["Play Store"], "app_store_units": source_counts["App Store"], "browser_engine_coverage": 0, "fallback_classification_coverage": len(classifications), "output": str(OUT)}, indent=2))
