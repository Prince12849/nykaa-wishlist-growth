# Project Status — Nykaa Fashion Wishlist-to-Purchase Case Study

Audit date: 28 August 2026 (IST)

This status file records the state of the workspace after reading `PROJECT_HANDOFF.md` completely and inspecting the project directory recursively. It distinguishes what is directly present on disk from what the handoff says was created in an earlier conversation. The handoff is treated as a record of prior claims, not as a substitute for missing source files, raw data, or research evidence.

## Current State

The workspace now contains the recovered AI Discovery Engine HTML, its extracted classification prompt, and four source-collection scripts. The three project documents are also present. There are still no collected datasets, classification outputs, interview records, screenshots, exported files, MVP deployment, or final deck.

The recovered files are research infrastructure/prototypes. They can support the next milestone—**real data → AI classification → quantified patterns**—after the technical blockers below are resolved and the taxonomy is kept explicitly as a hypothesis.

The project tree under `C:\Users\princ\Desktop\My project` contains nine files: one HTML file, five Markdown files including the prompt and project documents, and four Python files. No Gemini-specific artifact or separate research output was found.

Directories created during this audit because they map to the planned evidence-to-delivery flow:

- `data/raw/` — immutable source exports or captured source material.
- `data/processed/` — normalized and classified data derived from raw inputs.
- `research/interviews/` — interview plan, notes, transcripts, and consent-safe excerpts.
- `analysis/` — reproducible analysis and evidence matrices.
- `sources/` — source registry, URLs, retrieval dates, and supporting references.
- `mvp/` — eventual product prototype and deployment configuration.
- `deck/` — eventual deck source and final export.

These directories are intentionally empty. Empty directories may not be retained by every version-control system until they contain a file.

## Existing Artifacts

### Present on disk

| Path | Purpose | Current status |
|---|---|---|
| `mvp/nykaa-wishlist-discovery-engine.html` | Browser UI for adding snippets, importing CSV rows, calling Anthropic, rendering classifications, and copying CSV/JSON output. | Reusable local prototype. Embedded JavaScript parses successfully; browser E2E and public deployment are unverified. |
| `research/classification-prompt.md` | Human-readable classifier prompt, schema, parameters, and reuse notes. | Reusable prompt artifact; exact text match with the HTML prompt. Taxonomy remains a hypothesis. |
| `research/scrape_nykaa_reviews.py` | Play Store review collection and keyword relevance tagging. | Capable of real collection with dependency/network setup; not run. |
| `research/scrape_appstore_reviews.py` | App Store review collection and keyword relevance tagging. | Capable of real collection with dependency/network setup; not run. |
| `research/scrape_reddit.py` | Reddit post/comment collection and keyword relevance tagging. | Capable after credentials and user-agent setup; not run. |
| `research/scrape_youtube_comments.py` | YouTube comment collection from manually supplied URLs. | Capable after URLs and dependency setup; not run. |
| `PROJECT_HANDOFF.md` | Prior brief, decisions, claims, hypotheses, inferences, and proposed work. | Documentation/provenance record, not raw evidence. |
| `PROJECT_STATUS.md` | Current artifact and evidence audit. | Updated by this audit. |
| `README.md` | Objective, research-first principles, architecture, and data flow. | Updated by this audit. |
| `.qodo/agents/` | Tooling-related directory. | Present, empty. No agent configuration found. |
| `.qodo/workflows/` | Tooling-related directory. | Present, empty. No workflow definition found. |
| `data/raw/` | Planned raw-data landing area. | Created in this audit; empty. |
| `data/processed/` | Planned normalized/classified-data area. | Created in this audit; empty. |
| `research/interviews/` | Planned primary-research area. | Created in this audit; empty. |
| `analysis/` | Planned analysis area. | Created in this audit; empty. |
| `sources/` | Planned source/reference registry. | Created in this audit; empty. |
| `mvp/` | Planned MVP area. | Created in this audit; empty. |
| `deck/` | Planned presentation area. | Created in this audit; empty. |

### Handoff-described items now recovered or still absent

| Described item | Intended purpose | What can be reused now |
|---|---|---|
| Discovery Engine HTML | Browser-based Anthropic classification tool and dashboard. | Recovered at `mvp/nykaa-wishlist-discovery-engine.html`; local prototype only. |
| Four scraper scripts | Public-source collection and keyword relevance tagging. | Recovered under `research/`; not run. |
| Classification prompt | Prompt used by the Discovery Engine to emit structured JSON. | Recovered at `research/classification-prompt.md`; matches the HTML prompt. |
| Dashboard | Funnel and barrier/intent/category breakdowns embedded in the HTML tool. | Recovered as part of the HTML; no real data loaded. |
| Scraping/data workflow | Scrapers → CSV → bulk import → classification → dashboard. | Recovered as a compatible design, not yet executed end-to-end. |
| `nykaa_reviews_tagged.csv` and other scraper CSVs | Tagged collection outputs. | Still absent; no dataset exists. |
| 10-slide deck/PDF | Final case-study deliverable. | No source, PDF, or public link is present. |
| Public deployment | Testable public Discovery Engine and later deployed MVP. | No URL or deployment configuration is present. |
| Interview materials | Required 5–6 user interviews. | Still absent: no participant plan, screener, guide, notes, transcripts, or quotes. |

The handoff names a file `nykaa-wishlist-project-handoff.md`, but the file actually present is `PROJECT_HANDOFF.md`. No duplicate handoff file was created.

## Artifact Comparison Against the Handoff

The handoff description is substantially consistent with the recovered implementation:

- The HTML contains manual source entry, six example snippets, CSV import, a processing funnel, barrier/intent/category breakdowns, result cards, CSV/JSON clipboard export, retry-on-parse-failure logic, `window.storage` persistence attempts, and an Anthropic Messages API call using `claude-sonnet-4-6`.
- The Markdown classification prompt is an exact text match with the HTML `SYSTEM_PROMPT`.
- All four collectors normalize text, deduplicate by text, apply HIGH/MEDIUM/LOW keyword relevance tags, and write CSV columns compatible with the HTML import (`text`, `source`, `relevance` plus other fields).

The following implementation details were not visible in the handoff and matter before use:

- The HTML request sends only `Content-Type`; it contains no `x-api-key` or `anthropic-version` header and makes a direct browser request to `https://api.anthropic.com/v1/messages`.
- Model responses are parsed but not validated against the full required schema or enum values.
- The dashboard marks an item unclear only when its barrier is `Unclear`. The prompt notes say an unclear barrier or intent should be excluded, but intent aggregation can include `intent_signal === "Unclear"` rows.
- The six seed snippets are synthetic examples and must not be used as evidence.
- Scraper outputs use relative paths and omit stable source IDs, URLs/permalinks, retrieval timestamps, and other provenance fields.
- The Play Store script can divide by zero after writing an empty output if no usable rows are returned.

## Functional vs Prototype-Only

### Functional/reusable now

- The HTML is a coherent local research UI; its embedded JavaScript passes a non-executing syntax parse. Browser end-to-end behavior was not tested.
- The prompt is reusable and synchronized with the HTML.
- Each scraper has a complete collection loop, normalization, text deduplication, CSV writing, and summary logic.
- The four output schemas are compatible with the HTML's basic bulk-import fields.

### Prototype-only or unvalidated

- The Discovery Engine is not a production/public service and has no verified public URL.
- Anthropic authentication and browser cross-origin behavior are unresolved.
- The dashboard is descriptive tooling, not evidence of a representative sample or a causal user problem.
- The keyword relevance labels and all taxonomy labels are hypotheses.
- No scraper has been run against live data and no output has been human-reviewed.

## Real-Data Collection Capability

| Source | Script capability | Required setup | Current status |
|---|---|---|---|
| Play Store | Calls `google_play_scraper.reviews_all` for the configured app. | Python package and network access; no user API credential in the script. | Not run. |
| App Store | Calls `app-store-scraper` for the configured app ID/name and country. | Python package, compatible `requests`/`urllib3`, and network access. | Not run; the script documents a possible dependency conflict. |
| Reddit | Searches configured subreddits/terms and expands comments. | `praw`, Reddit client ID/secret, valid user agent, and network access. | Not runnable until credentials are configured. |
| YouTube | Downloads comments for each URL in `VIDEO_URLS`. | `youtube-comment-downloader`, network access, and manually supplied URLs. | Not runnable until at least one URL is supplied. |

No script collects first-party wishlist events or 30-day purchase outcomes. These sources can provide language/context only, not the business-metric baseline.

## Dependencies, Credentials, and Security/Privacy

- Python 3 plus `google-play-scraper`, `app-store-scraper`, `praw`, and `youtube-comment-downloader` are required for the collectors.
- The current bundled Python runtime can parse the scripts, but all four collector packages are missing. No collector was executed.
- The HTML requires Anthropic API access and a secure authentication boundary. Do not place a reusable API key in a public HTML file.
- The HTML sends raw user-provided/public text to an external model. Define PII minimization/redaction, retention, and disclosure rules before classification.
- Imported CSV values are untrusted; some source values are interpolated into HTML without escaping, creating a local HTML-injection concern.
- Respect platform access rules, rate limits, terms, and privacy expectations.

## Gemini Research Audit

### VERIFIED filesystem result

No Gemini-generated research output, notes, prompt, dataset, screenshot, export, or evidence file exists anywhere under `C:\Users\princ\Desktop\My project` based on the recursive inventory and text search in this audit.

The handoff contains prior-chat claims, hypotheses, inferences, and proposed work, but does not identify them as Gemini outputs. They must not be relabeled as Gemini research.

### HYPOTHESIS

None attributable to Gemini because no Gemini artifact was found.

### INFERENCE

None attributable to Gemini because no Gemini artifact was found.

### PROPOSED work

None attributable to Gemini because no Gemini artifact was found.

There is no Gemini research whose trustworthiness or relevance can be evaluated. Any future Gemini output should preserve its prompt, model/date context, source inputs, and evidence-status labels separately from verified user research.

## Evidence Available

### Directly verified in this audit

- The recovered HTML, prompt, and four scraper files exist at the paths listed above.
- The embedded HTML JavaScript parses successfully without executing the application.
- The Markdown prompt exactly matches the HTML's embedded `SYSTEM_PROMPT`.
- All four Python files pass AST parsing using the bundled Python runtime.
- A recursive file inventory found no CSV/JSON dataset, interview notes, screenshots, exported file, Gemini output, deck, or deployment artifact.
- No scraper or classifier was run during this audit.
- The project brief recorded in the handoff states the business goal: increase the percentage of users who purchase at least one wishlisted item within 30 days of adding it.
- The recorded constraint is non-monetary: no discounts, coupons, or deals.
- The handoff explicitly states that the underlying user problem is not given and must be discovered through research.

### Recorded in the handoff, but not independently auditable from this workspace

The handoff labels the following as previously verified or tested. They are retained here as provenance notes, not as newly verified evidence:

- Nykaa Fashion was selected by the user for this case study.
- Public-company and market-context claims were reportedly found through web search, including Q1 FY27 Fashion GMV/NSV/customer figures and a Virtual Closet conversion claim. The underlying URLs and captured source excerpts are not present in this workspace, so these claims must be re-sourced before appearing in a final deck.
- Public review content was reportedly found to skew toward post-purchase problems, with no genuine Nykaa Fashion wishlist-stage hesitation content found in the searches described by the handoff. This is a source-coverage observation, not proof that wishlist-stage barriers do not exist.
- General wishlist-psychology conversations were reportedly found, but the handoff states that they were not India- or Nykaa-specific.
- The handoff's prior test claims are retained as provenance; this audit independently confirmed HTML JavaScript parsing and Python AST parsing, but not live execution.

No item above is a quantified finding about Nykaa Fashion wishlist users. No dominant barrier, causal explanation, interview result, user quote, conversion baseline, or validated problem currently exists in the workspace.

## Evidence Missing

- Real Nykaa Fashion wishlist-stage data, including the population, time window, source, retrieval date, and relevant denominator.
- Raw exports from Play Store, App Store, Reddit, YouTube, or other public sources, with source URLs and provenance preserved.
- A real classification run record: taxonomy version, model/version, run date, input corpus, output corpus, and error/unclear records.
- Human review or quality checks showing whether AI labels are reliable enough for directional analysis.
- Quantified patterns such as counts, shares, segment differences, timing patterns, or recurrence. These must be calculated from real records, not from the example snippets described in the handoff.
- 5–6 primary-user interviews, including recruitment criteria, screener, guide, notes/transcripts, consent-safe quotes, and synthesis.
- A validated link between observed language/behavior and the 30-day wishlist-to-purchase metric.
- A baseline metric definition and value, cohort rules, event definitions, and instrumentation availability.
- A problem statement supported by both behavioral evidence and primary research.
- Candidate solutions, trade-off analysis, MVP scope, production deployment, success metrics, experiment design, and risk mitigations.
- Reader-accessible supporting links and a final deck metadata/link/format QA record.

## Research Gaps

These questions remain unanswered. They are research questions, not assumptions about users:

- Who adds items to a wishlist, in which categories, and with what apparent intent?
- What happens between wishlist addition, revisit, and purchase—or non-purchase—within 30 days?
- What reasons do real users give for delaying or abandoning a wishlisted item?
- Are the relevant reasons about value, fit/quality, trust, styling/occasion, comparison, memory/priority, or something outside the proposed taxonomy?
- Which user or item segments have materially different 30-day outcomes?
- What events or contexts cause a wishlist item to become purchase-ready?
- Does the existing proposed taxonomy cover the data, and where does it force ambiguous labels?
- How much of the observed public conversation is post-purchase rather than wishlist-stage, and what non-buyers are systematically missing?
- What product intervention could address the validated problem without monetary incentives?
- What baseline, guardrails, and experiment duration are needed to evaluate an intervention safely?

## Technical Gaps

- The HTML makes a direct browser-to-Anthropic request but contains no API-key or API-version header. A secure authentication boundary, CORS behavior, abuse/cost controls, and public deployment path must be resolved.
- The HTML attempts to use non-standard `window.storage`; behavior outside the original environment is unverified.
- Model responses are not validated against the full schema/enums. The unclear-denominator behavior for intent does not match the prompt notes.
- No reproducible dependency file, environment setup, or automated test suite exists.
- The collectors' live scraping behavior, rate limits, terms of use, pagination, duplicate handling, and output volume remain unverified.
- Reddit collection requires user-supplied API credentials and a meaningful user agent; YouTube collection requires manually supplied video URLs.
- Collector outputs use relative paths and omit stable source IDs, URLs/permalinks, retrieval timestamps, and other provenance fields.
- The Play Store script can divide by zero after writing an empty output if no usable reviews are returned.
- Imported source values are interpolated into some HTML templates without escaping, creating a local HTML-injection concern.
- No raw-to-processed data contract, immutable raw-data policy, schema versioning, provenance fields, or classification QA workflow exists.
- No public URL exists for either the Discovery Engine or the eventual MVP.
- No production hosting, deployment configuration, observability, or rollback plan exists.
- The project is not currently recognized as a Git repository, so version history and reproducible change review are unavailable from this workspace.

## Assignment Requirements

| Requirement | Status | Current basis |
|---|---|---|
| Business goal and non-monetary constraint | Complete as a recorded brief | Stated in `PROJECT_HANDOFF.md`; no product work yet. |
| Business metric decomposition | Missing | Not started. |
| AI Discovery Engine | Partial | Local prototype and prompt exist; authentication, browser E2E, and public link are unresolved. |
| Dedicated Discovery Engine slide | Missing | No deck exists. |
| Real data before conclusions | Missing | No real dataset or classification output is present. |
| 5–6 primary-user interviews | Missing | No interview materials or results are present. |
| Problem definition | Missing | Intentionally not decided before research. |
| Non-monetary solution selection | Missing | Intentionally not decided before problem validation. |
| MVP | Missing | No MVP has been built. |
| Public MVP deployment | Missing | No deployment or URL exists. |
| Success metrics | Missing | No baseline, experiment, or guardrails are defined. |
| Risks and mitigation | Missing | Not started. |
| 10-slide PDF deck | Missing | No deck source or PDF exists. |
| Reader-accessible links and final QA | Missing | No final artifact exists to test. |
| Deadline tracking | Partial | The deadline is recorded in the handoff; no execution calendar or final QA checkpoint exists. |

Required journey status:

`Business Metric` — Partial (goal is recorded; decomposition is missing) → `Product Outcomes` — Missing → `AI Discovery` — Partial (local prototype exists) → `Primary Research` — Missing → `Problem Definition` — Missing → `Solution` — Missing → `MVP` — Missing → `Success Metrics` — Missing → `Risks` — Missing.

## Recommended Execution Sequence

1. Resolve the collector dependencies and secure Anthropic authentication/deployment boundary.
2. Define raw-data schema/provenance fields and route outputs to `data/raw/` or another documented location.
3. Collect a small, permissible Play Store/App Store batch first; retain enough non-relevant material to measure keyword-filter bias.
4. Classify real records with a versioned prompt/model configuration, preserving raw inputs, raw outputs, and unclear/failed states.
5. Human-review a sample, record taxonomy gaps, and keep the taxonomy labeled as a hypothesis.
6. Quantify descriptive patterns with explicit denominators, source composition, exclusions, and limitations—without choosing the final problem.
7. Design and conduct the required 5–6 interviews to test and potentially falsify the observed hypotheses.
8. Define the problem only after evidence and interviews converge; then compare non-monetary solutions, select an MVP, and proceed to deployment/metrics/risk work.

The immediate next milestone is therefore: **real data → AI classification → quantified patterns → user interviews → validated problem**. No final MVP or final user problem should be chosen before that sequence produces evidence.
