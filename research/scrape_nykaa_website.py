"""
Nykaa Fashion website scraper — v3, fixed robots.txt handling + sitemap discovery
=====================================================================================
Two REAL bugs were found and fixed in this version (both reproduced and proven
against Python's actual stdlib behavior, not guessed):

BUG 1 — false "everything disallowed":
`urllib.robotparser.RobotFileParser.read()` internally calls
`urllib.request.urlopen(self.url)` with NO custom headers, so it sends
Python's default User-Agent ("Python-urllib/3.x") — a very commonly
blocked bot signature. If that request gets HTTP 401/403 back, the stdlib
SILENTLY sets `self.disallow_all = True` with no exception raised, which
makes every later `can_fetch()` call return False regardless of the real
rules. This is almost certainly why the previous version reported every
seed URL as "disallowed" even though the real robots.txt says `Allow: /`.
FIX: fetch robots.txt ourselves via `requests` (a real header, the same
approach that already works for every other page in this project), then
hand the raw text to our own parser — never call `.read()`.

BUG 2 — Disallow rules silently ignored even when the enforced fetch is fixed:
Python's stdlib `Entry.allowance()` walks rules in FILE ORDER and returns
the FIRST matching rule — it does NOT implement "most specific / longest
match wins" (the real standard, and what every actual crawler including
Googlebot does). Since this robots.txt lists `Allow: /` BEFORE the specific
`Disallow:` lines, and `/` matches every path as a prefix, `can_fetch()`
returns True for literally everything, including `/all-reviews` and
`/gateway-api/` — verified directly against the real robots.txt text in
this session; this is a real, reproducible stdlib limitation, not a guess.
FIX: implement our own longest-prefix-match rule resolution
(`robots_allows()` below), verified against the real rules to correctly
return False for `/all-reviews`, `/gateway-api/`, etc., and True for
product/category paths.

CONFIRMED VERIFIED robots.txt (from the user's real diagnostic run):
    User-agent: *
    Allow: /
    Disallow: /ndsxadm/
    Disallow: /catalogsearch/
    Disallow: /widget-listing/
    Disallow: /all-reviews
    Disallow: /gateway-api/
    Disallow: /rest/appapi/V2/
    Sitemap: https://www.nykaafashion.com/sitemap-v2/sitemap-index.xml

Setup:
    pip install requests beautifulsoup4 pandas

Run:
    python scrape_nykaa_website.py --max-products 20 --request-delay 2

Outputs:
    nykaa_website_raw.csv
    Appends a "## Nykaa Fashion" section to scraping_summary.md

STILL TRUE: this script was written and logic-tested in an environment with
no network access to nykaafashion.com. It has NOT been run against the live
site by the author. Every fixture used to test it below is synthetic and
clearly labeled as such. Real validation must happen on your machine.
"""

import argparse
import csv
import json
import re
import time
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE = "https://www.nykaafashion.com"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research-script/1.0 (educational case study)"
FALLBACK_SITEMAP_URL = "https://www.nykaafashion.com/sitemap-v2/sitemap-index.xml"

PRIORITY_KEYWORDS = [
    "women-products", "men-products", "kids-products", "designers-products",
    "home-products", "gadgets-and-tech-accessories-products",
    "sports-and-fitness-equipment-products", "generic",
]

RAW_FIELDS = [
    "source", "page_type", "source_url", "collected_at", "status", "error",
    "product_name", "brand", "price", "currency", "mrp", "discount_percent",
    "rating", "rating_count", "category", "color", "pattern", "material", "fit",
    "size_options", "availability", "description", "wishlist_signal",
    "purchase_discovery_ux_text",
]


class RunStats:
    def __init__(self):
        self.sitemap_url_used = ""
        self.sitemaps_discovered = 0
        self.sitemaps_fetched_ok = 0
        self.product_urls_discovered = 0
        self.product_urls_attempted = 0
        self.successful_pages = 0
        self.blocked_pages = 0
        self.errors = 0
        self.robots_skipped = 0
        self.products_parsed = 0
        self.fields_seen = set()
        self.fields_missing = set()


# ---------------------------------------------------------------------------
# Fixed robots.txt handling (see BUG 1 / BUG 2 notes above)
# ---------------------------------------------------------------------------

def fetch_robots_txt(session):
    """Fetch robots.txt with a real header via requests — never RobotFileParser.read()."""
    try:
        resp = session.get(urljoin(BASE, "/robots.txt"), headers={"User-Agent": USER_AGENT}, timeout=15)
        if resp.status_code == 200:
            return resp.text
        print(f"robots.txt fetch returned HTTP {resp.status_code} — proceeding with no rules parsed "
              f"(hard-coded conservative fallback still applies).")
        return ""
    except Exception as e:
        print(f"robots.txt fetch failed ({e}) — proceeding with no rules parsed "
              f"(hard-coded conservative fallback still applies).")
        return ""


def parse_robots_rules(text):
    """Returns (rules, sitemap_urls). rules = list of (path, is_allow) for User-agent: *."""
    rules, sitemaps = [], []
    applies = False
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        field, _, value = line.partition(":")
        field, value = field.strip().lower(), value.strip()
        if field == "user-agent":
            applies = (value == "*")
        elif field in ("disallow", "allow") and applies:
            rules.append((value, field == "allow"))
        elif field == "sitemap":
            sitemaps.append(value)
    return rules, sitemaps


# Hard-coded conservative fallback: used ONLY if robots.txt cannot be fetched
# at all this run. Matches the verified rules exactly, as a safety net.
FALLBACK_DISALLOW = ["/ndsxadm/", "/catalogsearch/", "/widget-listing/",
                      "/all-reviews", "/gateway-api/", "/rest/appapi/V2/"]


def robots_allows(path, rules):
    if not rules:
        return not any(path.startswith(d) for d in FALLBACK_DISALLOW)
    best_match, best_len = None, -1
    for rule_path, is_allow in rules:
        if rule_path == "":
            continue
        if path.startswith(rule_path) and len(rule_path) > best_len:
            best_len, best_match = len(rule_path), is_allow
    return True if best_match is None else best_match


def allowed(rules, url):
    path = url[len(BASE):] if url.startswith(BASE) else url
    return robots_allows(path, rules)


# ---------------------------------------------------------------------------
# HTTP helper
# ---------------------------------------------------------------------------

def http_get(url, session, timeout=15):
    try:
        resp = session.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
        return resp, None
    except requests.exceptions.Timeout:
        return None, "Timeout"
    except requests.exceptions.ConnectionError as e:
        return None, f"Connection error: {e}"
    except Exception as e:
        return None, f"Unexpected error: {e}"


# ---------------------------------------------------------------------------
# Sitemap discovery
# ---------------------------------------------------------------------------

def extract_locs(xml_text):
    return re.findall(r"<loc>\s*(.*?)\s*</loc>", xml_text, re.IGNORECASE | re.DOTALL)


def is_sitemap_index(xml_text):
    return "<sitemapindex" in xml_text.lower()


def is_valid_product_url(url):
    """STEP 3: validate structure, don't just assume /p/<id> is enough."""
    if not re.search(r"/p/\d+", url):
        return False
    if not url.startswith("https://www.nykaafashion.com/"):
        return False
    if any(url[len(BASE):].startswith(d) for d in FALLBACK_DISALLOW):
        return False
    return True


def discover_product_urls(rules, session, stats, sitemap_index_url, max_products, request_delay, max_depth=3):
    to_visit = [(sitemap_index_url, 0)]
    visited = set()
    product_urls = []

    while to_visit and len(product_urls) < max_products:
        sitemap_url, depth = to_visit.pop(0)
        if sitemap_url in visited:
            continue
        visited.add(sitemap_url)

        if not allowed(rules, sitemap_url):
            print(f"  robots.txt disallows sitemap URL, skipping: {sitemap_url}")
            continue

        stats.sitemaps_discovered += 1
        print(f"Fetching sitemap: {sitemap_url}")
        resp, err = http_get(sitemap_url, session)
        time.sleep(request_delay)
        if err or resp is None or resp.status_code != 200:
            stats.errors += 1
            print(f"  Failed: {err or ('HTTP ' + str(resp.status_code) if resp else 'no response')}")
            continue
        stats.sitemaps_fetched_ok += 1

        xml_text = resp.text
        locs = extract_locs(xml_text)

        if is_sitemap_index(xml_text):
            # DEBUG: print the raw, unfiltered child <loc> list every time we
            # see an index. Every prior run silently discarded 100% of these
            # at the PRIORITY_KEYWORDS check below and never printed them, so
            # nobody could see whether the guessed keyword list was even
            # close to the real filenames. This print happens unconditionally,
            # before any filtering, so a bad keyword list can never hide it.
            print(f"  This is a sitemap INDEX with {len(locs)} child <loc> entries (raw, unfiltered):")
            for raw_loc in locs[:30]:
                print(f"    - {raw_loc}")
            if len(locs) > 30:
                print(f"    ... and {len(locs) - 30} more")

            matched, unmatched = [], []
            for loc in locs:
                if depth >= max_depth or loc in visited:
                    continue
                if depth == 0 and any(k in loc for k in PRIORITY_KEYWORDS):
                    matched.append(loc)
                else:
                    unmatched.append(loc)

            # FIX: PRIORITY_KEYWORDS previously *discarded* every child that
            # didn't match a guessed keyword. If none matched (e.g. the real
            # filenames don't contain "women-products" etc.), every run since
            # has silently visited only the index and nothing else -- which
            # is exactly the "sitemaps discovered: 1, product URLs: 0"
            # pattern in every prior scraping_summary.md entry. Priority
            # matches are now just visited FIRST; everything else is still
            # queued afterward instead of being dropped.
            if depth == 0 and unmatched and not matched:
                print(f"  WARNING: 0 of {len(locs)} child sitemaps matched PRIORITY_KEYWORDS "
                      f"{PRIORITY_KEYWORDS} -- the keyword list looks wrong for this site's real "
                      f"filenames (see raw list above). Falling back to visiting all of them.")
            for loc in matched + unmatched:
                to_visit.append((loc, depth + 1))
        else:
            before = len(product_urls)
            for loc in locs:
                if is_valid_product_url(loc):
                    product_urls.append(loc)
            print(f"  This is a sitemap URLSET with {len(locs)} <loc> entries "
                  f"({len(product_urls) - before} matched is_valid_product_url()).")
            if locs and (len(product_urls) - before) == 0:
                # DEBUG: show a few raw entries so a URL-pattern mismatch in
                # is_valid_product_url() (not just an empty sitemap) is
                # visible immediately instead of silently reading as "0
                # products, must be nothing here."
                print(f"    0 matched -- first 5 raw <loc> entries for comparison against "
                      f"is_valid_product_url()'s /p/\\d+ pattern:")
                for raw_loc in locs[:5]:
                    print(f"      - {raw_loc}")

    deduped = list(dict.fromkeys(product_urls))
    stats.product_urls_discovered = len(deduped)
    return deduped[:max_products]


# ---------------------------------------------------------------------------
# Product page parsing — JSON-LD first, then meta tags, then regex fallback
# ---------------------------------------------------------------------------

def extract_jsonld_product(soup):
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "{}")
        except Exception:
            continue
        candidates = data if isinstance(data, list) else [data]
        for c in candidates:
            if isinstance(c, dict) and c.get("@type") in ("Product", "product"):
                return c
    return None


def parse_product_page(html, url, stats):
    soup = BeautifulSoup(html, "html.parser")
    row = {f: "" for f in RAW_FIELDS}
    row.update({
        "source": "Nykaa Fashion", "page_type": "product", "source_url": url,
        "collected_at": datetime.now(timezone.utc).isoformat(), "status": "success", "error": "",
    })

    jsonld = extract_jsonld_product(soup)

    # Strategy 1: JSON-LD
    if jsonld:
        row["product_name"] = jsonld.get("name", "")
        brand = jsonld.get("brand")
        row["brand"] = brand.get("name", "") if isinstance(brand, dict) else (brand or "")
        offers = jsonld.get("offers")
        if isinstance(offers, dict):
            row["price"] = str(offers.get("price", ""))
            row["currency"] = str(offers.get("priceCurrency", ""))
            row["availability"] = str(offers.get("availability", ""))
        agg = jsonld.get("aggregateRating")
        if isinstance(agg, dict):
            row["rating"] = str(agg.get("ratingValue", ""))
            row["rating_count"] = str(agg.get("reviewCount", agg.get("ratingCount", "")))
        if jsonld.get("description"):
            row["description"] = jsonld["description"][:400]

    # Strategy 2: OpenGraph / structured meta tags (fills gaps JSON-LD missed)
    if not row["product_name"]:
        t = soup.find("meta", property="og:title")
        row["product_name"] = t["content"].strip() if t and t.get("content") else ""
    if not row["price"]:
        t = soup.find("meta", property="product:price:amount")
        row["price"] = t["content"].strip() if t and t.get("content") else ""
    if not row["currency"]:
        t = soup.find("meta", property="product:price:currency")
        row["currency"] = t["content"].strip() if t and t.get("content") else ""
    if not row["description"]:
        t = soup.find("meta", attrs={"name": "description"})
        row["description"] = t["content"][:400] if t and t.get("content") else ""

    # Strategy 3: visible-text regex fallback for fields with no structured source
    body_text = soup.get_text(" ", strip=True)

    mrp_match = re.search(r"MRP\s*₹\s*([\d,]+)", body_text)
    if mrp_match:
        row["mrp"] = mrp_match.group(1).replace(",", "")
    disc_match = re.search(r"(\d{1,3})%\s*Off", body_text)
    if disc_match:
        row["discount_percent"] = disc_match.group(1)

    if not row["availability"]:
        if re.search(r"notify me", body_text, re.I):
            row["availability"] = "Out of stock (Notify Me shown)"
        elif re.search(r"add to bag", body_text, re.I):
            row["availability"] = "In stock (Add to Bag shown)"

    if re.search(r"wishlist", body_text, re.I):
        row["wishlist_signal"] = "Wishlist/save mechanism present on page"

    ux_hits = [p for p in ["similar", "you may also like", "recommended for you",
                            "customers also bought", "size chart", "true to size",
                            "delivery in", "easy returns", "cash on delivery", "notify me"]
               if re.search(p, body_text, re.I)]
    if ux_hits:
        row["purchase_discovery_ux_text"] = "; ".join(ux_hits)

    sizes = re.findall(r"\b(XXS|XS|S|M|L|XL|XXL|XXXL|2XL|3XL|4XL|Free Size)\b", body_text)
    if sizes:
        row["size_options"] = ", ".join(sorted(set(sizes)))[:200]

    for label, field in [("Fit", "fit"), ("Pattern", "pattern"), ("Material", "material"), ("Colou?r", "color")]:
        m = re.search(rf"\b{label}\s*[:\-]?\s*([A-Za-z0-9 %]{{2,40}})", body_text)
        if m and not row[field]:
            row[field] = m.group(1).strip()

    cat_match = re.search(r"Sub\s*[Cc]ategory\s*[:\-]?\s*([A-Za-z &]{2,40})", body_text)
    if cat_match and not row["category"]:
        row["category"] = cat_match.group(1).strip()

    for f in RAW_FIELDS:
        if f in ("status", "error", "source", "page_type", "source_url", "collected_at"):
            continue
        (stats.fields_seen if row[f] else stats.fields_missing).add(f)

    return row


def blank_row(url, status, error):
    row = {f: "" for f in RAW_FIELDS}
    row.update({
        "source": "Nykaa Fashion", "page_type": "product", "source_url": url,
        "collected_at": datetime.now(timezone.utc).isoformat(), "status": status, "error": error,
    })
    return row


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-products", type=int, default=500)
    ap.add_argument("--request-delay", type=float, default=2.0)
    ap.add_argument("--max-pages", type=int, default=0,
                     help="Unused for sitemap-first discovery; kept for CLI compatibility.")
    args = ap.parse_args()

    stats = RunStats()
    session = requests.Session()

    print("=== STEP: fetch + parse robots.txt (fixed method — requests, not RobotFileParser.read) ===")
    robots_text = fetch_robots_txt(session)
    rules, sitemap_directives = parse_robots_rules(robots_text) if robots_text else ([], [])
    sitemap_index_url = sitemap_directives[0] if sitemap_directives else FALLBACK_SITEMAP_URL
    stats.sitemap_url_used = sitemap_index_url
    print(f"Sitemap URL to use: {sitemap_index_url}")
    if robots_text:
        print(f"Parsed {len(rules)} robots.txt rules for User-agent: *")
    else:
        print("Could not fetch robots.txt this run — using hard-coded conservative fallback disallow list.")

    print(f"\n=== STEP: discover product URLs via sitemap (max {args.max_products}) ===")
    product_urls = discover_product_urls(rules, session, stats, sitemap_index_url,
                                          args.max_products, args.request_delay)
    print(f"\nDiscovered {stats.product_urls_discovered} unique, validated product URLs.")

    rows = []
    print(f"\n=== STEP: fetch {len(product_urls)} product pages ===")
    for i, url in enumerate(product_urls, 1):
        stats.product_urls_attempted += 1
        if not allowed(rules, url):
            print(f"[{i}/{len(product_urls)}] robots.txt disallows, skipping: {url}")
            stats.robots_skipped += 1
            rows.append(blank_row(url, "skipped_robots", "Disallowed by robots.txt"))
            continue

        print(f"[{i}/{len(product_urls)}] {url}")
        resp, err = http_get(url, session)
        time.sleep(args.request_delay)

        if err:
            stats.errors += 1
            rows.append(blank_row(url, "error", err))
            continue
        if resp.status_code in (403, 429):
            stats.blocked_pages += 1
            rows.append(blank_row(url, "blocked", f"HTTP {resp.status_code}"))
            continue
        if resp.status_code != 200:
            stats.errors += 1
            rows.append(blank_row(url, "error", f"HTTP {resp.status_code}"))
            continue

        stats.successful_pages += 1
        row = parse_product_page(resp.text, url, stats)
        stats.products_parsed += 1
        rows.append(row)

    with open("nykaa_website_raw.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=RAW_FIELDS)
        w.writeheader()
        w.writerows(rows)

    summary = f"""## Nykaa Fashion
- Run timestamp: {datetime.now(timezone.utc).isoformat()}
- Sitemap URL used: {stats.sitemap_url_used}
- Sitemaps discovered: {stats.sitemaps_discovered}
- Sitemaps fetched OK: {stats.sitemaps_fetched_ok}
- Product URLs discovered: {stats.product_urls_discovered}
- Product URLs attempted: {stats.product_urls_attempted}
- Successful pages: {stats.successful_pages}
- Blocked pages: {stats.blocked_pages}
- Errors: {stats.errors}
- Robots-skipped pages: {stats.robots_skipped}
- Products parsed: {stats.products_parsed}
- Fields captured at least once: {", ".join(sorted(stats.fields_seen)) or "none"}
- Fields never captured: {", ".join(sorted(stats.fields_missing - stats.fields_seen)) or "none"}
"""
    with open("scraping_summary.md", "a", encoding="utf-8") as f:
        f.write(summary)

    print("\n" + "=" * 50)
    print("RUN COMPLETE")
    print("=" * 50)
    print(summary)


if __name__ == "__main__":
    main()
