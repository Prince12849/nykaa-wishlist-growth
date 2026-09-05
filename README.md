# Nykaa Fashion Wishlist-to-Purchase Case Study

## Project objective

Increase the percentage of users who purchase at least one item from their wishlist within 30 days of adding it, without using discounts, coupons, deals, or other monetary incentives.

The underlying user problem is not known yet. This repository is being set up to discover and validate it before selecting a solution or building the final MVP.

## Research-first philosophy

This project will not treat a taxonomy label, an AI classification, an example snippet, a public complaint, or an intuition as a validated user problem.

Every important claim should be marked as one of:

- **VERIFIED** — directly supported by a reproducible artifact, source, dataset, or primary-research record.
- **HYPOTHESIS** — a testable proposition that has not been validated.
- **INFERENCE** — a reasoned interpretation of evidence, not direct evidence itself.
- **PROPOSED** — a plan, design, or future decision that has not been executed.

The recovered Discovery Engine, classification prompt, four public-source collectors, and the existing pilot evidence assets are present. They are research infrastructure/prototypes, not a validated problem selector or production MVP. AI labels remain candidate classifications and human adjudication remains a separate state. See [PROJECT_STATUS.md](PROJECT_STATUS.md) for the current audit.

## Planned architecture

The planned system is an evidence pipeline, not an automatic problem selector:

1. Define the business metric, denominator, cohort, and product outcomes.
2. Register permissible public sources and collect raw material with provenance.
3. Normalize source records into a common schema while retaining the original text.
4. Apply a versioned AI Discovery Engine taxonomy and classification prompt.
5. Preserve unclear and failed classifications, then human-review a sample for quality.
6. Quantify patterns with counts, denominators, exclusions, and segment context.
7. Use those patterns to design and conduct 5–6 primary-user interviews.
8. Synthesize evidence into a validated problem definition.
9. Compare non-monetary solution candidates, select an evidence-backed MVP, and deploy it.
10. Instrument success metrics and guardrails, then communicate the evidence trail in the final deck.

## Planned data flow

```text
Public sources
    ↓
data/raw/  ── source URL, retrieval date, source type, original text
    ↓
data/processed/  ── normalized records, taxonomy version, model output, uncertainty
    ↓
analysis/  ── quantified patterns, QA checks, evidence matrix
    ↓
research/interviews/  ── screener, guide, notes, transcripts, consent-safe excerpts
    ↓
Validated problem definition
    ↓
Candidate non-monetary solutions → MVP in mvp/
    ↓
Success metrics, guardrails, risks, and final deck in deck/
```

## Recovered research tooling

- `mvp/nykaa-wishlist-discovery-engine.html` — static browser UI for the embedded pilot, deterministic evidence validation, manual snippets and CSV import, candidate AI classification, descriptive breakdowns, human adjudication, and export.
- `mvp/data/nykaa_discovery_bundle.js` — generated static deployment asset containing the existing pilot, classification, automated-validation, and current human-adjudication CSV rows; it is loaded with a script tag and requires no runtime fetch or API call.
- `analysis/automated_validation_output.csv` — generated, provenance-preserving deterministic validation layer. It is derived from the existing pilot/classification/human-adjudication inputs and is not a replacement for human review.
- `research/build_discovery_bundle.mjs` — reproducible bundle/validation builder that reads the authoritative CSVs and verifies record-ID alignment before writing the deployment asset and validation output.
- `research/classification-prompt.md` — synchronized copy of the HTML classifier prompt and schema.
- `research/scrape_nykaa_reviews.py` — Play Store review collector.
- `research/scrape_appstore_reviews.py` — App Store review collector.
- `research/scrape_reddit.py` — Reddit collector requiring API credentials.
- `research/scrape_youtube_comments.py` — YouTube collector requiring manually supplied URLs.

The collectors have not been run. The default reviewer path is static-host compatible: the HTML loads the generated bundle beside it, without runtime file fetches, browser-origin dependencies, or an API call. The default analysis uses the generated deterministic validation layer; ambiguous records remain flagged and human decisions take precedence where present. The optional researcher controls retain manual CSV import and API classification for local experimentation; do not place a reusable API key in a public HTML file. Rebuild the bundle from the authoritative CSVs with the project runtime when those source assets intentionally change.

## How the Discovery Engine will connect to research

The AI Discovery Engine is intended to accelerate discovery by organizing real language into a transparent, reviewable structure. It is not intended to prove why users do or do not purchase.

The proposed flow is:

- collect real public records and preserve raw provenance;
- classify them into a versioned schema, including an uncertainty path;
- review a sample and quantify only what the corpus supports;
- turn patterns into interview probes and falsifiable hypotheses;
- combine classified public evidence with primary research before defining the problem.

The taxonomy currently described in the handoff—such as value uncertainty, fit/quality doubt, trust, styling/occasion uncertainty, comparison shopping, bookmark-only intent, and deprioritization—is a proposed framework. It is not an established list of Nykaa Fashion user barriers and may be incomplete or wrong.

## How research data, analysis, interviews, the MVP, and the deck connect

Analysis should show what is present in the data and what remains unknown. Interviews should test the important uncertainties and identify the context behind observed language. Only after both streams support a coherent problem should the project define a product opportunity.

The MVP should be the smallest non-monetary intervention that addresses that validated problem. Its success metrics should connect to the 30-day wishlist-to-purchase business metric, with leading indicators and guardrails. The final deck should make the chain visible:

`Business Metric → Product Outcomes → AI Discovery → Primary Research → Problem → Solution → MVP → Success Metrics → Risks`

All claims in the deck should link to reader-accessible sources or to reproducible project artifacts. Example or synthetic data may be used for tool testing, but it must never be presented as real user evidence.

## Repository layout

- `PROJECT_HANDOFF.md` — prior conversation handoff and provenance notes.
- `PROJECT_STATUS.md` — current audit, evidence classification, gaps, and recommended sequence.
- `data/raw/` — source material preserved before transformation.
- `data/processed/` — normalized and classified records.
- `research/interviews/` — primary-research materials.
- `analysis/` — analysis outputs and evidence matrices.
- `sources/` — source registry and supporting references.
- `mvp/` — eventual prototype and deployment files.
- `deck/` — eventual presentation source and export.

## Immediate milestone

**Real data → AI classification → quantified patterns → user interviews → validated problem.**

The final user problem, solution, and MVP remain intentionally undecided until this milestone is completed.
