# Web Scraping Layer — Nykaa Fashion / Myntra / AJIO

Three scrapers for public product-page evidence, built for the wishlist-to-purchase
case study. Written after actually inspecting live pages from all three sites in
this session — not from guessed selectors — but with real, stated limits on what
that inspection could confirm. Read "Known limitations" before trusting the output.

## 1. Installation

```
pip install -r requirements-web-scraping.txt
playwright install chromium
```
The second command downloads a real Chromium browser (~150-300MB) that Playwright
drives — required for the Myntra and AJIO scrapers. The Nykaa scraper doesn't need it.

## 2. How to run each scraper

Place all three `.py` files in your project's `research/` folder alongside your
existing files, then from that folder:

```
python scrape_nykaa_website.py --max-pages 5 --max-products 200 --request-delay 1.5
python scrape_myntra_website.py --max-scrolls 6 --max-products 150 --request-delay 2
python scrape_ajio_website.py --max-scrolls 6 --max-products 150 --request-delay 2
```

Run them one at a time, not simultaneously — easier to read the output and diagnose
any blocking.

## 3. Expected outputs

Each scraper writes two CSVs plus appends a section to a shared summary file:
- `nykaa_website_raw.csv` / `nykaa_website_reviews.csv`
- `myntra_website_raw.csv` / `myntra_website_reviews.csv`
- `ajio_website_raw.csv` / `ajio_website_reviews.csv`
- `scraping_summary.md` — created on first run, appended to by each subsequent one.
  Every number in it is generated live by the script that ran, not written by hand.

The `*_reviews.csv` files will likely be **sparse or empty** for all three sites —
none of the three showed individual review text in server/rendered page content
during inspection; only aggregate rating values (via JSON-LD, when present) were
found to be realistically extractable from public pages. This is expected, not
a bug — see Section 6.

## 4. Configuration options

| Flag | Meaning | Applies to |
|---|---|---|
| `--max-pages` | Pagination pages per seed category | Nykaa only |
| `--max-scrolls` | Scroll-load increments per seed page (infinite-scroll proxy for "pages") | Myntra, AJIO |
| `--max-products` | Total product pages to visit | All three |
| `--request-delay` | Seconds between requests | All three |
| `--headless` | `true`/`false` — run browser visibly for debugging | Myntra, AJIO |

## 5. Rate limits / politeness

- All three scrapers sleep `--request-delay` seconds between requests (default
  1.5-2s) — increase this if you see more blocking, especially on Myntra.
- Nykaa's scraper checks `robots.txt` before each request via Python's built-in
  `urllib.robotparser` and skips disallowed paths.
- None of the scrapers use proxies, IP rotation, CAPTCHA-solving services, or
  browser-fingerprint spoofing beyond a standard desktop user-agent string — by
  design, per the project's compliance rules. If a site blocks a real browser
  with a normal user-agent, the scraper reports the block and stops for that URL
  rather than escalating to evasion techniques.

## 6. Known limitations — read this before trusting the data

**Confirmed by direct inspection in this session:**
- **Nykaa Fashion**: category and product pages are largely server-rendered —
  product name, brand, price, MRP, discount%, size options, and structured
  attributes (fit, material, etc.) are genuinely scrapable. **Individual review
  text and per-review ratings were NOT present in server-rendered product pages**
  — only aggregate rating data (if present via JSON-LD) is captured.
- **Myntra**: a plain HTTP request returned a fake "Site Maintenance" page —
  confirmed active bot-detection. The Playwright version should get further, but
  this was not verified end-to-end against a live block-free run in this session.
- **AJIO**: a plain HTTP request returned only the site's navigation menu, no
  product data — confirmed client-side-rendered SPA. Playwright is required and
  is used, but the rendered-DOM selectors were written from a confirmed product
  URL pattern found via search, not from directly viewing AJIO's live rendered
  product grid — expect to need selector adjustments after your first run.

**What this means practically:**
- Treat `nykaa_website_raw.csv` as the most reliable of the three on a first run.
- Treat `myntra_website_raw.csv` and `ajio_website_raw.csv` as first drafts —
  check the `error` column and the `scraping_summary.md` block/error counts after
  running them. A high blocked-count or low field-capture rate means the
  selectors need re-inspection (open the site in a real browser, use devtools to
  find the actual product-tile/detail selectors, and adjust the regex patterns
  near the top of the relevant script) — not that the site can't be scraped at all.

## 7. What cannot be scraped (by design, not by limitation)

- Any user's actual private wishlist contents (requires login — not attempted).
- Anything behind a login wall.
- Anything behind a CAPTCHA challenge (scripts stop and report, don't solve).
- Anything a site's `robots.txt` disallows (Nykaa scraper checks and skips this
  automatically; Myntra/AJIO scrapers should have the same check added if you
  want it enforced there too — not yet implemented in this version).

## 8. Combining with your existing dataset

These new files use a different schema (product/catalog-level fields) than your
existing `all_reviews.csv` (review-text-level fields from Play Store/App
Store/YouTube). Recommended approach:
1. Keep them as separate files — don't try to force-merge into `all_reviews.csv`.
2. Use `all_reviews.csv` for **review-text volume and language** (what people say).
3. Use the `*_website_raw.csv` files for **catalog/UX evidence** — pricing,
   sizing, wishlist/notify mechanisms, discovery structure, availability
   patterns — the parts of the wishlist-to-purchase journey that aren't
   captured in review text at all.
4. Feed both into your AI classification step (per `classification-prompt.md`)
   as separate labeled sources, not a single blended file.
