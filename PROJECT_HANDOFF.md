\# Project Handoff — Nykaa Fashion Wishlist-to-Purchase Case Study



Compiled from an existing chat conversation. Every item below is labeled:

\- \*\*\[VERIFIED]\*\* — confirmed fact, tested code, or content directly sourced/checked in this conversation

\- \*\*\[HYPOTHESIS]\*\* — a testable proposition raised in-chat, not yet confirmed against real data

\- \*\*\[INFERENCE]\*\* — a reasoned conclusion drawn from evidence in-chat, not independently confirmed

\- \*\*\[PROPOSED]\*\* — a plan, suggestion, or next step raised in-chat, not yet executed or finalized



Nothing below has been added, reinterpreted, or extended beyond what appears in the source conversation.



\---



\## 1. Project Brief



\*\*\[VERIFIED]\*\* — Full brief was uploaded in-chat as a document. Key points:

\- Choose one product: Myntra, AJIO, or Nykaa Fashion. Role: PM on the Growth Team.

\- Business goal: increase the % of users who purchase at least one wishlisted item within 30 days of adding it.

\- Constraint: solutions \*\*cannot use monetary incentives\*\* (no discounts/coupons/deals).

\- The underlying user problem is \*\*not given\*\* — must be discovered through research.

\- Required parts, in order: (1) AI Discovery Engine, (2) business-metric decomposition, (3) primary research — 5–6 user interviews, (4) problem definition, (5) MVP deployed to production, (6) success metrics, (7) risks \& mitigation.

\- Deliverables: a link to a testable AI Discovery Engine (plus one dedicated slide explaining it), a 10-slide PDF deck, and a link to a publicly accessible deployed MVP.

\- Deck rules: fellow's name must not appear anywhere in the deck; 10 slides max; font size 14 strictly; slide titles must state the key finding, not a generic label; colorblind-safe color use; every supporting link must be reader-accessible.

\- \*\*Deadline: September 5, 2026, 3:59:00 PM IST — no late submissions accepted, even by seconds.\*\*



\---



\## 2. Prior Benchmark Research (context that shaped the approach — not part of this project's deliverables)



\*\*\[VERIFIED]\*\* — Two prior fellowship submissions on an unrelated case (a Blinkit AOV/growth problem) were analyzed in this chat purely to extract process lessons:



\- \*\*Gaurav Kumar's deck\*\*: scored 249.41/300 (83.13%), cleared the 208.57 cutoff. Scored above median on Creativity (86.19/100 vs. 67.83 median) and Depth (87.75/100 vs. 81.36 median). Every embedded hyperlink checked in-chat led to real, live content. Market claims (customer growth, AOV figures, a CEO quote) were verified against public sources found via web search. RICE-score arithmetic in the deck was independently recalculated and confirmed correct.

\- \*\*Your ("Prince Lakra") BasketBridge deck\*\*: scored 176.11/300 (58.7%), did \*\*not\*\* clear the 208.57 cutoff. Below median on Clarity/Depth (57.07 vs. 81.36) and Creativity (45.9 vs. 67.83); above median on Presentation (49.66 vs. 46.05). Of roughly nine button-styled "citation" elements in the deck, only \*\*3 links in the entire PDF had a working URL behind them\*\* (a private Google Drive file, plus a GitHub repo and a Streamlit app, the repo linked twice) — the rest were unlinked visual buttons. Internal numeric consistency was strong: 1,455 + 778 = 2,233 and 365 + 1,868 = 2,233 both matched the stated total of 2,233 structured insights; source counts (1,369 + 576 + 186 + 157 + 5) summed exactly to the stated 2,293.



\*\*\[INFERENCE]\*\* — Reasoned explanation (not confirmed by any actual grader) for the score gap between the two decks: the lower-scoring deck lacked (a) market/business-context grounding with real external numbers, (b) visible alternative solutions considered before committing to one, and (c) a GTM/rollout plus risk-mitigation section — all three of which were present in the higher-scoring deck, along with a correctly computed RICE comparison across three candidate solutions.



\*\*\[PROPOSED]\*\* — An 8-step process for this new project, derived from that comparison: (1) pick a company with a provable, numbers-backed tension; (2) open the deck with the business case before user research; (3) layer AI-assisted research with real interviews; (4) build one clean, MECE user segmentation; (5) score three or more candidate solutions before picking one; (6) ship something clickable and confirm the link actually works; (7) design metrics with guardrails and a correctly specified experiment; (8) close with rollout/risk content and do a final link/number QA pass before submitting.



\---



\## 3. Company Selection



\*\*\[VERIFIED, via web search cited in-chat]\*\*

\- Nykaa Fashion's Q1 FY27 results (reported August 4, 2026): fashion GMV grew 53% to ₹1,471 crore; net sales value (NSV) rose 54% to ₹451 crore; the fashion segment's EBITDA margin turned positive for the first time. Cumulative fashion customer base grew 34% to 12 million. Category growth: women's +40%, men's +83%, kids' +57%.

\- Nykaa has publicly described a "GMV-to-NSV funnel" and a "reduction in leakages" — company language describing a gap between what's selected/intended and what converts to net sales.

\- Nykaa Fashion's Virtual Closet AI tool (launched around May 2026) was reported to drive roughly 2x higher conversion among users who tried it.

\- AJIO: retail analysts confirmed that Reliance does not disclose standalone AJIO revenue, GMV, or order-volume figures — only qualitative growth percentages are made public.

\- Myntra: reports only via annual RoC filings (not quarterly); most recent public data available as of this chat was FY25 (described in-chat as "filed \~17 months ago"), broken out by business stream (logistics/marketplace/ads) rather than by GMV or customer count.



\*\*\[DECISION — confirmed by user]\*\* — Nykaa Fashion was selected. User's exact confirmation in-chat: \*"lets buid our project based on nykaa."\*



\---



\## 4. Deck Structure Plan



\*\*\[PROPOSED]\*\* — 10-slide mapping onto the brief's 7 required parts. No deck file has been created yet.

1\. Cover / the tension — KPI and real numbers stated as the title's key message

2\. Business metric decomposition

3\. AI discovery engine — the brief's required dedicated "how it works" slide

4\. Discovery engine findings

5\. Primary research (5–6 interviews)

6\. Problem definition — root cause chain, JTBD, and the explicit arc: Business Metric → Product Outcomes → AI Discovery → Primary Research → Problem

7\. Solution rationale — 2–3 non-monetary options scored transparently

8\. MVP — what was built, plus the deployment link

9\. Success metrics — north star, supporting metrics, guardrails

10\. Risks \& mitigation



\---



\## 5. Compliance Requirements



\*\*\[VERIFIED — directly from brief]\*\*

\- Fellow's name must not appear anywhere in the deck, including file metadata (Title/Author fields). \*(Flagged in-chat based on metadata inspection of the two benchmark PDFs, both of which had anonymized author IDs rather than real names.)\*

\- Font size 14pt, strictly, no exceptions anywhere in the deck.

\- Colorblind-safe palette — do not rely on color alone to distinguish states.

\- Slide titles must state the finding, not a generic section label.

\- Every supporting link must be reader-accessible (view permission, not edit-only) — test in an incognito window before submitting.

\- 10 slides maximum.

\- Deadline: September 5, 2026, 3:59:00 PM IST.



\---



\## 6. Artifacts / Code Built



All items in this section are \*\*\[VERIFIED]\*\* — created and tested (syntax and/or logic) within this conversation. Current file locations were confirmed on disk at the time this handoff was written.



\### `nykaa-wishlist-discovery-engine.html`

Self-contained HTML/CSS/JS tool. The user pastes a text snippet plus a source tag; the tool calls the Anthropic API directly from the browser (model `claude-sonnet-4-6`, no API key required inside the artifact) and classifies the snippet against a fixed JSON schema: `barrier`, `discovery\_trigger`, `underlying\_need`, `category`, `intent\_signal`, `evidence\_note`, `confidence`. Results render as a live dashboard: a processing funnel (pasted/classified/unclear/failed counts), percentage bar breakdowns for barrier/intent/category (each with an "n= classified, X unclear/failed excluded" footnote), and individual result cards styled as garment tags.

Also includes: 6 built-in example snippets for testing without needing real data first; a bulk CSV import feature (accepts `text`/`source`/`relevance` columns, with a configurable row-import limit); CSV/JSON export via clipboard; and session persistence via `window.storage` (personal, non-shared).

JS syntax was verified with `node --check` after every edit made in this chat.

\*\*Not yet deployed to a public URL\*\* — currently exists only as a local file output from this chat session.



\### `scrape\_nykaa\_reviews.py`

Scrapes Play Store reviews for Nykaa Fashion using the `google-play-scraper` library. Confirmed via web search that the correct Play Store package ID is `com.fsn.nds` (distinct from `com.fsn.nykaa`, which is the separate Nykaa beauty app). Tags each review HIGH/MEDIUM/LOW relevance by keyword match (wishlist-adjacent terms → HIGH; fit/trust/styling terms → MEDIUM; else → LOW). Outputs `nykaa\_reviews\_tagged.csv`, sorted HIGH→LOW, with a printed relevance-split summary.

Library install and import were tested successfully in this chat's sandbox. \*\*The live scrape itself was not run\*\* — this sandbox's network cannot reach play.google.com — so script logic and syntax were verified, but no actual review data has been pulled yet.



\### `scrape\_appstore\_reviews.py`

Same relevance-tagging approach for App Store reviews, using `app\_store\_scraper`. Confirmed via web search that the correct App Store ID is `1439872423`. \*\*Known issue found and fixed in-chat\*\*: this library pins an old `requests==2.23.0`, which caused an import error in the sandbox; resolved by running `pip install --upgrade requests urllib3`. The same fix may be needed on the user's own machine.

Import and syntax verified in-chat; live scrape not run here.



\### `scrape\_reddit.py`

Uses `praw`. Requires the user's own free Reddit API credentials (client ID/secret from reddit.com/prefs/apps, "script" app type) — the script has placeholder fields for these, not filled in. Searches a fixed list of subreddits (`IndianFashionAddicts`, `india`, `twoxindia`, `IndianSkincareAddicts`) and search terms (`Nykaa Fashion`, `online fashion shopping wishlist`, `haven't bought yet clothes`, `wishlist clothes India`, `Myntra AJIO Nykaa`) across both posts and comments, using the same HIGH/MEDIUM/LOW tagging.

Import and syntax verified in-chat; not run against live Reddit data (no credentials available in this session).



\### `scrape\_youtube\_comments.py`

Uses `youtube\_comment\_downloader` (no API key required). Requires the user to manually find and paste in YouTube video URLs — the script does not perform video search itself. Same HIGH/MEDIUM/LOW tagging and CSV output format.

Import and syntax verified in-chat; not run against live YouTube data.



All four scraper scripts output CSVs in the same schema (`source, rating, date, text, relevance`), designed to feed directly into the Discovery Engine's bulk-import feature.



\### `nykaa-wishlist-project-handoff.md`

This document.



\---



\## 7. Research Findings Specific to This Project



\*\*\[VERIFIED — found via web search, cited in-chat]\*\*

\- Public review/complaint content specifically about Nykaa Fashion (App Store and similar aggregator-type sources) skews heavily toward \*\*post-purchase\*\* issues: wrong size or color shipped, damaged or used items arriving, refund delays (over a month in some reported cases), and products differing from their photos. No genuine wishlist-stage hesitation content specific to Nykaa Fashion was found in the searches run during this chat.

\- This was flagged in-chat as a real, usable finding in its own right — mirroring the "absence bias" pattern identified in the Blinkit benchmark decks, where non-buyers who never transact are systematically underrepresented in review-site data.



\*\*\[VERIFIED, but not Nykaa- or India-specific — general wishlist psychology, falls under the brief's "other publicly available conversations" source category]\*\*

\- A Mumsnet-style forum discussion: some shoppers deliberately keep wishlists instead of buying, as a self-control strategy.

\- A Substack post on slow fashion: the wishlist framed as a deliberate "holding stage" between liking an item and deciding to buy it, not a to-do list.

\- A Vice-style article: wishlisting/cart-adding described as giving a "pretend buying" satisfaction on its own; some people screenshot items instead of adding to cart, to check later whether the desire was genuine.

\- A source in the "considered purchase" / waiting-period vein was also surfaced.

\- Explicitly noted in-chat: none of this is India- or Nykaa-specific. Closing that gap was left to the planned 5–6 user interviews (brief Part 3), not yet conducted.



\*\*\[HYPOTHESIS — not yet tested against real Nykaa user data]\*\*

\- The barrier taxonomy built into the Discovery Engine's classification schema — \*Price/Value Uncertainty; Fit, Size or Quality Doubt; Trust/Authenticity Concern; Styling or Occasion Uncertainty; Comparison Shopping; Bookmark Only/No Real Intent; Forgot/Deprioritized; Other; Unclear\* — is a proposed classification framework only. It has not yet been run against a real corpus of Nykaa Fashion wishlist-stage language.

\- \*\*No barrier has yet been identified as the actual dominant reason Nykaa Fashion wishlist items go unpurchased.\*\* This remains undetermined as of this handoff.



\---



\## 8. Decisions Made



\*\*\[VERIFIED — confirmed as having occurred in this chat]\*\*

\- Company: Nykaa Fashion (user-confirmed).

\- No monetary-incentive solutions will be considered, per the brief's constraint.

\- Part 1 approach: build a Claude-API-powered classification tool (the HTML artifact) as the primary "engine," rather than a fully automated end-to-end scrape-to-dashboard pipeline, supplemented by separate scraper scripts feeding data into it.

\- Scraping priority order proposed in-chat: Play Store and App Store first (lowest setup effort, already tested), Reddit second (best expected signal quality, worth the \~2-minute credential setup), YouTube last/optional (requires manual video-URL hunting).



\---



\## 9. Known Gaps / Unresolved Items



\*\*\[VERIFIED as unresolved — explicitly flagged in-chat]\*\*

\- No real user data — scraped or interview-based — has actually been analyzed yet. Everything built so far is infrastructure/tooling, not findings.

\- The Discovery Engine has not been published to a public URL.

\- No actual 10-slide deck file has been created yet.

\- Brief Parts 2–7 (metric decomposition, primary research, problem definition, MVP, success metrics, risks \& mitigation) have not been started.

\- The user mentioned doing parallel work in ChatGPT. As of this handoff, that work has not been shared into or reconciled with this chat.

\- Live scrapes were never executed in this sandbox, due to network restrictions on the tooling environment — only library installation, imports, and script syntax were verified here. Real output volume and content from any scraper are unknown until the scripts are run on the user's own machine.

\- Exact source URLs for some cited research (e.g., the general wishlist-psychology sources in Section 7) were referenced by platform/publication name in-chat but literal URL strings were not preserved in the visible conversation record.



\---



\## 10. Next Steps



\*\*\[PROPOSED — not yet executed]\*\*

\- Run `scrape\_nykaa\_reviews.py` and/or `scrape\_appstore\_reviews.py` locally to produce a real tagged CSV.

\- Bulk-import that CSV into the Discovery Engine and run classification; review the resulting barrier breakdown.

\- Share and reconcile any ChatGPT-side work with this project thread.

\- Use real classification output to begin Part 2 (metric decomposition).

\- Conduct the 5–6 required user interviews (Part 3), informed by whatever the engine surfaces.

\- Deploy the Discovery Engine to a public URL (Netlify Drop or GitHub Pages were suggested in-chat as low-effort options).

\- Build the actual 10-slide deck file once problem definition (Part 4) is settled.



\---



\*End of handoff. Source: single continuous chat conversation. Compiled without adding new research, hypotheses, or decisions beyond what the conversation already contains.\*

