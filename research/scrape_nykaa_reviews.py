"""
Nykaa Fashion website scraper — v2, sitemap-driven discovery
=================================================================
Rebuilt from VERIFIED robots.txt rules (confirmed by the user's own
diagnostic run against the live site, not guessed):

    User-agent: *
    Allow: /
    Disallow: /ndsxadm/
    Disallow: /catalogsearch/
    Disallow: /widget-listing/
    Disallow: /all-reviews
    Disallow: /gateway-api/
    Disallow: /rest/appapi/V2/
    Sitemap: https://www.nykaafashion.com/sitemap-v2/sitemap-index.xml

Category pages, product pages (/p/...), and the sitemap under
/pub/media/sitemap-index.xml are all confirmed ALLOWED. /all-reviews and
/gateway-api/ are confirmed DISALLOWED and this script will not touch them.

DISCOVERY STRATEGY: sitemap-first, not category-crawl-first. This is more
reliable (sitemaps are meant for exactly this) and avoids re-deriving
pagination logic that was never verified against live rendered HTML.

Setup:
    pip install requests beautifulsoup4 pandas

Run:
    python scrape_nykaa_website.py --max-products 500 --request-delay 2

Validation run used in this project:
    python scrape_nykaa_website.py --max-products 20 --request-delay 2

Outputs:
    research/nykaa_website_raw.csv
    Appends a "## Nykaa Fashion" section to research/scraping_summary.md

IMPORTANT: this script was built and syntax-verified in an environment that
cannot reach nykaafashion.com (network egress restricted to package
registries only) — it has NOT been run against the live site by the author.
Logic was checked against synthetic sitemap/product XML+HTML fixtures only.
Real validation must happen on a machine with real internet access.
"""

import argparse
import csv
import json
import re
import time
import urllib.robotparser
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE = "https://www.nykaafashion.com"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research-script/1.0 (educational case study)"

SITEMAP_INDEX_URL = urljoin(BASE, "/pub/media/sitemap-index.xml")

PRIORITY_KEYWORDS = [
    "women-products", "men-products", "kids-products", "designers-products",
    "generic", "home-products", "gadgets-and-tech-accessories-products",
    "sports-and-fitness-equipment-products",
]

EXPLICITLY_DISALLOWED_SUBSTRINGS = [
    "/ndsxadm/", "/catalogsearch/", "/widget-listing/", "/all-reviews", "/gateway-api/", "/rest/appapi/V2/",
]

RAW_FIELDS = [
    "source", "page_type", "source_url", "collected_at", "status", "error",
    "product_name", "brand", "category", "price", "mrp", "discount_pct", "currency",
    "rating", "rating_count", "availability", "size_information", "color", "material",
    "fit_information", "pattern", "description", "wishlist_information",
    "notification_information", "purchase_discovery_ux_text",
]


class RunStats:
    def __init__(self):
        self.sitemap_files_discovered = 0
        self.sitemap_files_fetched_ok = 0
        self.product_urls_discovered = 0
        self.duplicate_urls_removed = 0
        self.pages_attempted = 0
        self.pages_successful = 0
        self.pages_blocked = 0
        self.errors = 0
        self.products_parsed = 0
        self.fields_seen = set()
        self.fields_missing = set()


def get_robots_parser():
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(urljoin(BASE, "/robots.txt"))
    try:
        rp.read()
        return rp
    except Exception:
        return None


def allowed(rp, url):
    if any(sub in url for sub in EXPLICITLY_DISALLOWED_SUBSTRINGS):
        return False
    if rp is None:
        return True
    try:
        return rp.can_fetch(USER_AGENT, url)
    except Exception:
        return True


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


def extract_locs(xml_text):
    return re.findall(r"<loc>\s*(.*?)\s*</loc>", xml_text, re.IGNORECASE | re.DOTALL)


def is_sitemap_index(xml_text):
    return "<sitemapindex" in xml_text.lower()


def discover_product_urls(rp, session, stats, max_products, request_delay, max_recursion_depth=3):
    to_visit = [SITEMAP_INDEX_URL]
    visited_sitemaps = set()
    product_urls = []
    depth_map = {SITEMAP_INDEX_URL: 0}

    while to_visit and len(product_urls) < max_products:
        sitemap_url = to_visit.pop(0)
        if sitemap_url in visited_sitemaps:
            continue
        visited_sitemaps.add(sitemap_url)
        depth = depth_map.get(sitemap_url, 0)

        if not allowed(rp, sitemap_url):
            print(f"  robots.txt disallows sitemap URL, skipping: {sitemap_url}")
            continue

        stats.sitemap_files_discovered += 1
        print(f"Fetching sitemap: {sitemap_url}")
        resp, err = http_get(sitemap_url, session)
        time.sleep(request_delay)
        if err or resp is None or resp.status_code != 200:
            stats.errors += 1
            print(f"  Failed: {err or ('HTTP ' + str(resp.status_code) if resp else 'no response')}")
            continue
        stats.sitemap_files_fetched_ok += 1

        xml_text = resp.text
        locs = extract_locs(xml_text)

        if is_sitemap_index(xml_text):
            for loc in locs:
                if depth >= max_recursion_depth:
                    continue
                if depth == 0 and not any(k in loc for k in PRIORITY_KEYWORDS):
                    continue
                if loc not in visited_sitemaps:
                    to_visit.append(loc)
                    depth_map[loc] = depth + 1
        else:
            before = len(product_urls)
            for loc in locs:
                if re.search(r"/p/\d+", loc):
                    product_urls.append(loc)
            print(f"  Extracted {len(product_urls) - before} product URLs from this sitemap.")

    deduped = list(dict.fromkeys(product_urls))
    stats.duplicate_urls_removed = len(product_urls) - len(deduped)
    stats.product_urls_discovered = len(deduped)
    return deduped[:max_products]


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
    row["source"] = "Nykaa Fashion"
    row["page_type"] = "product"
    row["source_url"] = url
    row["collected_at"] = datetime.now(timezone.utc).isoformat()
    row["status"] = "success"
    row["error"] = ""

    jsonld = extract_jsonld_product(soup)

    title_tag = soup.find("meta", property="og:title")
    row["product_name"] = (title_tag["content"].strip() if title_tag and title_tag.get("content")
                            else (jsonld.get("name", "") if jsonld else ""))

    price_tag = soup.find("meta", property="product:price:amount")
    row["price"] = price_tag["content"].strip() if price_tag and price_tag.get("content") else ""
    currency_tag = soup.find("meta", property="product:price:currency")
    row["currency"] = currency_tag["content"].strip() if currency_tag and currency_tag.get("content") else ""

    if jsonld:
        brand = jsonld.get("brand")
        row["brand"] = brand.get("name", "") if isinstance(brand, dict) else (brand or "")
        offers = jsonld.get("offers")
        if isinstance(offers, dict):
            row["price"] = row["price"] or str(offers.get("price", ""))
            row["currency"] = row["currency"] or str(offers.get("priceCurrency", ""))
            row["availability"] = str(offers.get("availability", ""))
        agg = jsonld.get("aggregateRating")
        if isinstance(agg, dict):
            row["rating"] = str(agg.get("ratingValue", ""))
            row["rating_count"] = str(agg.get("reviewCount", agg.get("ratingCount", "")))
        desc_ld = jsonld.get("description")
        if desc_ld:
            row["description"] = desc_ld[:400]

    body_text = soup.get_text(" ", strip=True)

    mrp_match = re.search(r"MRP\s*₹\s*([\d,]+)", body_text)
    if mrp_match:
        row["mrp"] = mrp_match.group(1).replace(",", "")
    disc_match = re.search(r"(\d{1,3})%\s*Off", body_text)
    if disc_match:
        row["discount_pct"] = disc_match.group(1)

    if not row["availability"]:
        if re.search(r"notify me", body_text, re.I):
            row["availability"] = "Out of stock (Notify Me shown)"
        elif re.search(r"add to bag", body_text, re.I):
            row["availability"] = "In stock (Add to Bag shown)"

    if re.search(r"notify me", body_text, re.I):
        row["notification_information"] = "Notify Me / back-in-stock mechanism present"
    if re.search(r"wishlist", body_text, re.I):
        row["wishlist_information"] = "Wishlist/save mechanism present on page"

    ux_hits = []
    for phrase in ["similar", "you may also like", "recommended for you", "customers also bought",
                   "size chart", "true to size", "delivery in", "easy returns", "cash on delivery"]:
        if re.search(phrase, body_text, re.I):
            ux_hits.append(phrase)
    if ux_hits:
        row["purchase_discovery_ux_text"] = "; ".join(ux_hits)

    sizes = re.findall(r"\b(XXS|XS|S|M|L|XL|XXL|XXXL|2XL|3XL|4XL|Free Size)\b", body_text)
    if sizes:
        row["size_information"] = ", ".join(sorted(set(sizes)))[:200]

    fit_match = re.search(r"\bFit\s*[:\-]?\s*([A-Za-z ]{2,30})", body_text)
    if fit_match:
        row["fit_information"] = fit_match.group(1).strip()
    pattern_match = re.search(r"\bPattern\s*[:\-]?\s*([A-Za-z ]{2,30})", body_text)
    if pattern_match:
        row["pattern"] = pattern_match.group(1).strip()
    material_match = re.search(r"\bMaterial\s*[:\-]?\s*([A-Za-z0-9 %]{2,40})", body_text)
    if material_match:
        row["material"] = material_match.group(1).strip()
    color_match = re.search(r"\bColou?r\s*[:\-]?\s*([A-Za-z ]{2,25})", body_text)
    if color_match:
        row["color"] = color_match.group(1).strip()

    cat_match = re.search(r"Sub\s*[Cc]ategory\s*[:\-]?\s*([A-Za-z &]{2,40})", body_text)
    if cat_match:
        row["category"] = cat_match.group(1).strip()

    if not row["description"]:
        desc_meta = soup.find("meta", attrs={"name": "description"})
        row["description"] = (desc_meta["content"][:400] if desc_meta and desc_meta.get("content") else "")

    for f in RAW_FIELDS:
        if f in ("status", "error", "source", "page_type", "source_url", "collected_at"):
            continue
        (stats.fields_seen if row[f] else stats.fields_missing).add(f)

    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-products", type=int, default=500)
    ap.add_argument("--request-delay", type=float, default=2.0)
    args = ap.parse_args()

    stats = RunStats()
    session = requests.Session()
    rp = get_robots_parser()
    if rp is None:
        print("WARNING: could not fetch/parse robots.txt live this run. "
              "Falling back to the hard-coded verified Disallow list only. Proceeding cautiously.")

    print(f"\n=== Discovering product URLs via sitemap (max {args.max_products}) ===")
    product_urls = discover_product_urls(rp, session, stats, args.max_products, args.request_delay)
    print(f"\nDiscovered {len(product_urls)} candidate product URLs "
          f"({stats.duplicate_urls_removed} duplicates removed).")

    rows = []
    print(f"\n=== Fetching {len(product_urls)} product pages ===")
    for i, url in enumerate(product_urls, 1):
        stats.pages_attempted += 1
        if not allowed(rp, url):
            print(f"[{i}/{len(product_urls)}] robots.txt disallows, skipping: {url}")
            rows.append({**{f: "" for f in RAW_FIELDS}, "source": "Nykaa Fashion", "page_type": "product",
                         "source_url": url, "collected_at": datetime.now(timezone.utc).isoformat(),
                         "status": "skipped_robots", "error": "Disallowed by robots.txt"})
            continue

        print(f"[{i}/{len(product_urls)}] {url}")
        resp, err = http_get(url, session)
        time.sleep(args.request_delay)

        if err:
            stats.errors += 1
            rows.append({**{f: "" for f in RAW_FIELDS}, "source": "Nykaa Fashion", "page_type": "product",
                         "source_url": url, "collected_at": datetime.now(timezone.utc).isoformat(),
                         "status": "error", "error": err})
            continue
        if resp.status_code in (403, 429):
            stats.pages_blocked += 1
            rows.append({**{f: "" for f in RAW_FIELDS}, "source": "Nykaa Fashion", "page_type": "product",
                         "source_url": url, "collected_at": datetime.now(timezone.utc).isoformat(),
                         "status": "blocked", "error": f"HTTP {resp.status_code}"})
            continue
        if resp.status_code != 200:
            stats.errors += 1
            rows.append({**{f: "" for f in RAW_FIELDS}, "source": "Nykaa Fashion", "page_type": "product",
                         "source_url": url, "collected_at": datetime.now(timezone.utc).isoformat(),
                         "status": "error", "error": f"HTTP {resp.status_code}"})
            continue

        stats.pages_successful += 1
        row = parse_product_page(resp.text, url, stats)
        stats.products_parsed += 1
        rows.append(row)

    with open("nykaa_website_raw.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=RAW_FIELDS)
        w.writeheader()
        w.writerows(rows)

    summary = f"""## Nykaa Fashion
- Run at: {datetime.now(timezone.utc).isoformat()}
- Discovery method: sitemap-first (verified robots.txt Allow:/, sitemap index at /pub/media/sitemap-index.xml)
- Sitemap files discovered: {stats.sitemap_files_discovered}
- Sitemap files successfully fetched: {stats.sitemap_files_fetched_ok}
- Product URLs discovered: {stats.product_urls_discovered}
- Duplicate URLs removed: {stats.duplicate_urls_removed}
- Product pages attempted: {stats.pages_attempted}
- Successful pages: {stats.pages_successful}
- Blocked pages: {stats.pages_blocked}
- Errors: {stats.errors}
- Products successfully parsed: {stats.products_parsed}
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
