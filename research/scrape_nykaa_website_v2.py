"""
Nykaa Fashion website scraper — robust sitemap-driven version
==============================================================

Purpose:
    Collect public product-page evidence from Nykaa Fashion for a research
    / product case study.

Verified site facts used by this script:
    User-agent: *
    Allow: /
    Disallow: /ndsxadm/
    Disallow: /catalogsearch/
    Disallow: /widget-listing/
    Disallow: /all-reviews
    Disallow: /gateway-api/
    Disallow: /rest/appapi/V2/
    Sitemap:
        https://www.nykaafashion.com/sitemap-v2/sitemap-index.xml

Discovery:
    sitemap index -> priority product sitemaps -> product URLs -> product pages

Install:
    pip install -U requests beautifulsoup4 pandas urllib3

Run:
    python scrape_nykaa_website.py --max-products 20 --request-delay 2

Notes:
    - This script does NOT log in, access private wishlists, solve CAPTCHAs,
      use proxies/IP rotation, or bypass access controls.
    - It checks robots.txt and also enforces the verified disallowed paths.
    - 403/429 responses are recorded as blocked; the script does not attempt
      anti-bot evasion.
"""

import argparse
import csv
import gzip
import json
import re
import time
import urllib.robotparser
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests import Response
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


BASE = "https://www.nykaafashion.com"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "research-script/1.0 (educational case study)"
)

# Verified from the user's live diagnostic run.
SITEMAP_INDEX_URL = urljoin(BASE, "/sitemap-v2/sitemap-index.xml")

# These are the sitemap names we actually want for product/catalog research.
PRIORITY_KEYWORDS = [
    "women-products",
    "men-products",
    "kids-products",
    "designers-products",
    "generic",
    "home-products",
    "gadgets-and-tech-accessories-products",
    "sports-and-fitness-equipment-products",
]

# Independent safety net for the verified robots.txt restrictions.
EXPLICITLY_DISALLOWED_SUBSTRINGS = [
    "/ndsxadm/",
    "/catalogsearch/",
    "/widget-listing/",
    "/all-reviews",
    "/gateway-api/",
    "/rest/appapi/V2/",
]

RAW_FIELDS = [
    "source",
    "page_type",
    "source_url",
    "collected_at",
    "status",
    "error",
    "product_name",
    "brand",
    "category",
    "price",
    "mrp",
    "discount_pct",
    "currency",
    "rating",
    "rating_count",
    "availability",
    "size_information",
    "color",
    "material",
    "fit_information",
    "pattern",
    "description",
    "wishlist_information",
    "notification_information",
    "purchase_discovery_ux_text",
]


class RunStats:
    def __init__(self) -> None:
        self.sitemap_files_discovered = 0
        self.sitemap_files_fetched_ok = 0
        self.product_urls_discovered = 0
        self.duplicate_urls_removed = 0
        self.pages_attempted = 0
        self.pages_successful = 0
        self.pages_blocked = 0
        self.errors = 0
        self.products_parsed = 0
        self.fields_seen: Set[str] = set()
        self.fields_missing: Set[str] = set()


def now_utc() -> str:
    """Return a consistent UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def make_session() -> requests.Session:
    """
    Create a requests session.

    Retries only temporary server-side failures. It deliberately does NOT
    retry 403/429, because repeated requests are not an appropriate response
    to explicit blocking/rate limiting.
    """
    session = requests.Session()

    retry = Retry(
        total=2,
        connect=2,
        read=2,
        status=2,
        backoff_factor=1.0,
        status_forcelist=(500, 502, 503, 504),
        raise_on_status=False,
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    session.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
    )

    return session


def get_robots_parser(session: requests.Session) -> Optional[urllib.robotparser.RobotFileParser]:
    """
    Fetch robots.txt with requests and parse it manually.

    IMPORTANT:
    urllib.robotparser.RobotFileParser.read() uses urllib's default
    Python-urllib User-Agent. If a WAF returns 403 for that request,
    RobotFileParser silently sets disallow_all=True. That previously caused
    every Nykaa URL to appear disallowed even though the real robots.txt
    contains Allow: /.

    Using requests here avoids that silent failure mode.
    """
    robots_url = urljoin(BASE, "/robots.txt")

    try:
        response = session.get(robots_url, timeout=15)

        if response.status_code != 200:
            print(
                f"WARNING: robots.txt returned HTTP {response.status_code}. "
                "Using the verified hard-coded Disallow list only."
            )
            return None

        parser = urllib.robotparser.RobotFileParser()
        parser.parse(response.text.splitlines())

        # Defensive check: never accept a parser that internally decided
        # everything is disallowed because of a fetch failure.
        if getattr(parser, "disallow_all", False):
            print(
                "WARNING: robot parser reported disallow_all=True. "
                "Using hard-coded verified restrictions only."
            )
            return None

        return parser

    except requests.RequestException as exc:
        print(
            f"WARNING: failed to fetch robots.txt ({exc}). "
            "Using the verified hard-coded Disallow list only."
        )
        return None


def allowed(
    robots_parser: Optional[urllib.robotparser.RobotFileParser],
    url: str,
) -> bool:
    """
    Return whether the URL is permitted for this research scraper.

    The explicit substring check is intentionally independent of
    RobotFileParser because Python's robotparser has limitations around
    Allow/Disallow ordering.
    """
    lower_url = url.lower()

    if any(path.lower() in lower_url for path in EXPLICITLY_DISALLOWED_SUBSTRINGS):
        return False

    if robots_parser is None:
        # We still enforce the verified hard-coded restrictions above.
        return True

    try:
        return robots_parser.can_fetch(USER_AGENT, url)
    except Exception:
        # If parser evaluation itself fails, fail open only because the
        # independently verified disallow list remains enforced.
        return True


def http_get(
    url: str,
    session: requests.Session,
    timeout: int = 20,
) -> Tuple[Optional[Response], Optional[str]]:
    """
    Fetch one URL.

    Returns:
        (Response, None) on an HTTP response
        (None, error_message) when a request could not obtain a response
    """
    try:
        response = session.get(url, timeout=timeout)
        return response, None

    except requests.exceptions.Timeout:
        return None, "Timeout"

    except requests.exceptions.ConnectionError as exc:
        return None, f"Connection error: {exc}"

    except requests.exceptions.RequestException as exc:
        return None, f"Request error: {exc}"

    except Exception as exc:
        return None, f"Unexpected error: {exc}"


def extract_locs(xml_text: str) -> List[str]:
    """
    Extract <loc> values.

    Kept as a small fallback helper; normal sitemap parsing uses ElementTree.
    """
    return [
        value.strip()
        for value in re.findall(
            r"<loc>\s*(.*?)\s*</loc>",
            xml_text,
            re.IGNORECASE | re.DOTALL,
        )
    ]


def parse_sitemap_locs(content: bytes) -> Tuple[str, List[str]]:
    """
    Parse a sitemap document defensively.

    Nykaa can return XML with namespaces, gzip compression, or (during
    bot/WAF protection) an HTML response with HTTP 200. We therefore:
      1. decompress gzip when necessary,
      2. try XML parsing,
      3. fall back to regex,
      4. fall back to BeautifulSoup's XML/HTML parsing.

    Returns:
        ("index", locations)
        ("urlset", locations)
        ("unknown", locations)
    """
    raw = content

    if raw[:2] == b"\x1f\x8b":
        try:
            raw = gzip.decompress(raw)
        except OSError:
            pass

    text = raw.decode("utf-8", errors="ignore").lstrip("\ufeff \t\r\n")

    # XML parser: handles namespaces correctly.
    try:
        root = ET.fromstring(raw)
        root_name = root.tag.split("}")[-1].lower()

        locs: List[str] = []
        for element in root.iter():
            if element.tag.split("}")[-1].lower() == "loc":
                if element.text and element.text.strip():
                    locs.append(element.text.strip())

        if root_name == "sitemapindex":
            return "index", locs

        if root_name == "urlset":
            return "urlset", locs

        if locs:
            return "unknown", locs

    except ET.ParseError:
        pass

    # Regex fallback.
    locs = extract_locs(text)
    lower = text.lower()

    if locs:
        if "<sitemapindex" in lower:
            return "index", locs
        if "<urlset" in lower:
            return "urlset", locs
        return "unknown", locs

    # Last-resort BeautifulSoup parsing.
    try:
        soup = BeautifulSoup(text, "xml")
        soup_locs = [
            tag.get_text(strip=True)
            for tag in soup.find_all("loc")
            if tag.get_text(strip=True)
        ]

        if soup_locs:
            root = soup.find()
            root_name = root.name.lower() if root and root.name else ""

            if root_name == "sitemapindex":
                return "index", soup_locs
            if root_name == "urlset":
                return "urlset", soup_locs

            return "unknown", soup_locs

    except Exception:
        pass

    return "unknown", []

def is_product_url(url: str) -> bool:
    """
    Nykaa Fashion product URLs observed in the project use /p/<numeric-id>.
    """
    return re.search(r"/p/\d+(?:[/?#]|$)", url) is not None


def discover_product_urls(
    robots_parser: Optional[urllib.robotparser.RobotFileParser],
    session: requests.Session,
    stats: RunStats,
    max_products: int,
    request_delay: float,
    max_recursion_depth: int = 3,
) -> List[str]:
    """
    Discover product URLs from Nykaa's verified sitemap index.

    Top-level sitemap files are filtered using PRIORITY_KEYWORDS.
    Nested sitemap indexes are followed up to max_recursion_depth.
    """
    queue: List[Tuple[str, int]] = [(SITEMAP_INDEX_URL, 0)]
    visited_sitemaps: Set[str] = set()
    product_urls: List[str] = []

    while queue and len(product_urls) < max_products:
        sitemap_url, depth = queue.pop(0)

        if sitemap_url in visited_sitemaps:
            continue

        visited_sitemaps.add(sitemap_url)

        if not allowed(robots_parser, sitemap_url):
            print(f"  robots.txt disallows sitemap URL, skipping: {sitemap_url}")
            continue

        stats.sitemap_files_discovered += 1
        print(f"Fetching sitemap: {sitemap_url}")

        response, error = http_get(sitemap_url, session)
        time.sleep(request_delay)

        if error:
            stats.errors += 1
            print(f"  Failed: {error}")
            continue

        if response is None:
            stats.errors += 1
            print("  Failed: no response received")
            continue

        if response.status_code in (403, 429):
            stats.pages_blocked += 1
            print(f"  Blocked: HTTP {response.status_code}")
            continue

        if response.status_code != 200:
            stats.errors += 1
            print(f"  Failed: HTTP {response.status_code}")
            continue

        stats.sitemap_files_fetched_ok += 1

        sitemap_type, locs = parse_sitemap_locs(response.content)

        print(
            f"  HTTP {response.status_code} | "
            f"Content-Type: {response.headers.get('Content-Type', '')} | "
            f"Bytes: {len(response.content)} | "
            f"Parsed type: {sitemap_type} | "
            f"<loc> count: {len(locs)}"
        )

        if not locs:
            preview = response.content[:500].decode("utf-8", errors="replace")
            print("  WARNING: sitemap returned no <loc> entries.")
            print("  Response preview:")
            print("  " + " ".join(preview.split())[:500])

        if sitemap_type == "index":
            for loc in locs:
                if depth >= max_recursion_depth:
                    continue

                # Only apply keyword filtering at the verified top-level
                # sitemap index. Nested indexes are followed normally.
                if depth == 0:
                    loc_lower = loc.lower()
                    if not any(
                        keyword in loc_lower
                        for keyword in PRIORITY_KEYWORDS
                    ):
                        continue

                if loc not in visited_sitemaps:
                    queue.append((loc, depth + 1))

        elif sitemap_type == "urlset":
            before = len(product_urls)

            for loc in locs:
                if is_product_url(loc):
                    product_urls.append(loc)

                    # Stop collecting once the requested limit is reached.
                    if len(product_urls) >= max_products:
                        break

            extracted = len(product_urls) - before
            print(f"  Extracted {extracted} product URLs from this sitemap.")

        else:
            # If the XML structure is unusual, still attempt to recover
            # product URLs from <loc> values.
            before = len(product_urls)

            for loc in locs:
                if is_product_url(loc):
                    product_urls.append(loc)

                    if len(product_urls) >= max_products:
                        break

            extracted = len(product_urls) - before
            print(f"  Unknown sitemap type; recovered {extracted} product URLs.")

    deduped = list(dict.fromkeys(product_urls))

    stats.duplicate_urls_removed = len(product_urls) - len(deduped)
    stats.product_urls_discovered = len(deduped)

    return deduped[:max_products]


def extract_jsonld_product(soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
    """
    Find a Product JSON-LD object.

    Handles:
        - one Product object
        - a list of objects
        - @graph containers
    """
    for script in soup.find_all("script", type="application/ld+json"):
        raw = script.string or script.get_text()

        if not raw:
            continue

        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            continue

        candidates: List[Any] = []

        if isinstance(data, list):
            candidates.extend(data)

        elif isinstance(data, dict):
            candidates.append(data)

            graph = data.get("@graph")
            if isinstance(graph, list):
                candidates.extend(graph)

        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue

            product_type = candidate.get("@type")

            if isinstance(product_type, list):
                if any(str(value).lower() == "product" for value in product_type):
                    return candidate

            elif str(product_type).lower() == "product":
                return candidate

    return None


def first_meta_content(
    soup: BeautifulSoup,
    *,
    property_name: Optional[str] = None,
    name: Optional[str] = None,
) -> str:
    """Safely retrieve the content of a meta tag."""
    if property_name is not None:
        tag = soup.find("meta", attrs={"property": property_name})
    elif name is not None:
        tag = soup.find("meta", attrs={"name": name})
    else:
        return ""

    if not tag:
        return ""

    content = tag.get("content")
    return str(content).strip() if content else ""


def clean_value(value: Any) -> str:
    """Convert a parsed value to a clean string."""
    if value is None:
        return ""

    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)

    return str(value).strip()


def parse_product_page(
    html: str,
    url: str,
    stats: RunStats,
) -> Dict[str, str]:
    """
    Extract public product/catalog evidence from one product page.
    """
    soup = BeautifulSoup(html, "html.parser")

    row: Dict[str, str] = {field: "" for field in RAW_FIELDS}

    row["source"] = "Nykaa Fashion"
    row["page_type"] = "product"
    row["source_url"] = url
    row["collected_at"] = now_utc()
    row["status"] = "success"
    row["error"] = ""

    jsonld = extract_jsonld_product(soup)

    # ---------------------------------------------------------------
    # Product name
    # ---------------------------------------------------------------
    row["product_name"] = first_meta_content(
        soup,
        property_name="og:title",
    )

    if not row["product_name"] and jsonld:
        row["product_name"] = clean_value(jsonld.get("name"))

    # ---------------------------------------------------------------
    # Price / currency
    # ---------------------------------------------------------------
    row["price"] = first_meta_content(
        soup,
        property_name="product:price:amount",
    )

    row["currency"] = first_meta_content(
        soup,
        property_name="product:price:currency",
    )

    # ---------------------------------------------------------------
    # JSON-LD product fields
    # ---------------------------------------------------------------
    if jsonld:
        brand = jsonld.get("brand")

        if isinstance(brand, dict):
            row["brand"] = clean_value(brand.get("name"))
        else:
            row["brand"] = clean_value(brand)

        offers = jsonld.get("offers")

        if isinstance(offers, list):
            offers = offers[0] if offers else None

        if isinstance(offers, dict):
            if not row["price"]:
                row["price"] = clean_value(offers.get("price"))

            if not row["currency"]:
                row["currency"] = clean_value(offers.get("priceCurrency"))

            row["availability"] = clean_value(
                offers.get("availability")
            )

        aggregate_rating = jsonld.get("aggregateRating")

        if isinstance(aggregate_rating, dict):
            row["rating"] = clean_value(
                aggregate_rating.get("ratingValue")
            )

            row["rating_count"] = clean_value(
                aggregate_rating.get(
                    "reviewCount",
                    aggregate_rating.get("ratingCount"),
                )
            )

        description_ld = clean_value(jsonld.get("description"))

        if description_ld:
            row["description"] = description_ld[:400]

    body_text = soup.get_text(" ", strip=True)

    # ---------------------------------------------------------------
    # MRP
    # ---------------------------------------------------------------
    mrp_patterns = [
        r"MRP\s*[:\-]?\s*[₹Rs.]?\s*([\d,]+(?:\.\d+)?)",
        r"MRP\s*[₹]?\s*([\d,]+(?:\.\d+)?)",
    ]

    for pattern in mrp_patterns:
        match = re.search(pattern, body_text, flags=re.IGNORECASE)

        if match:
            row["mrp"] = match.group(1).replace(",", "")
            break

    # ---------------------------------------------------------------
    # Discount
    # ---------------------------------------------------------------
    discount_match = re.search(
        r"(\d{1,3})\s*%\s*(?:Off|OFF)",
        body_text,
        flags=re.IGNORECASE,
    )

    if discount_match:
        row["discount_pct"] = discount_match.group(1)

    # ---------------------------------------------------------------
    # Availability
    # ---------------------------------------------------------------
    if not row["availability"]:
        if re.search(r"\bnotify\s*me\b", body_text, flags=re.IGNORECASE):
            row["availability"] = "Out of stock (Notify Me shown)"

        elif re.search(r"\badd\s+to\s+bag\b", body_text, flags=re.IGNORECASE):
            row["availability"] = "In stock (Add to Bag shown)"

    # ---------------------------------------------------------------
    # Wishlist / notification signals
    # ---------------------------------------------------------------
    if re.search(r"\bnotify\s*me\b", body_text, flags=re.IGNORECASE):
        row["notification_information"] = (
            "Notify Me / back-in-stock mechanism present"
        )

    if re.search(r"\bwishlist\b", body_text, flags=re.IGNORECASE):
        row["wishlist_information"] = (
            "Wishlist/save mechanism present on page"
        )

    # ---------------------------------------------------------------
    # Discovery / purchase UX signals
    # ---------------------------------------------------------------
    ux_patterns = [
        "similar",
        "you may also like",
        "recommended for you",
        "customers also bought",
        "size chart",
        "true to size",
        "delivery in",
        "easy returns",
        "cash on delivery",
    ]

    ux_hits: List[str] = []

    for phrase in ux_patterns:
        if re.search(re.escape(phrase), body_text, flags=re.IGNORECASE):
            ux_hits.append(phrase)

    if ux_hits:
        row["purchase_discovery_ux_text"] = "; ".join(ux_hits)

    # ---------------------------------------------------------------
    # Size information
    # ---------------------------------------------------------------
    sizes = re.findall(
        r"\b(XXXS|XXS|XS|S|M|L|XL|XXL|XXXL|2XL|3XL|4XL|Free Size)\b",
        body_text,
        flags=re.IGNORECASE,
    )

    if sizes:
        unique_sizes: List[str] = []

        for size in sizes:
            normalized = size.upper()

            if normalized not in unique_sizes:
                unique_sizes.append(normalized)

        row["size_information"] = ", ".join(unique_sizes)[:200]

    # ---------------------------------------------------------------
    # Attribute extraction
    # ---------------------------------------------------------------
    attribute_patterns = {
        "fit_information": r"\bFit\s*[:\-]?\s*([A-Za-z][A-Za-z &/-]{1,40})",
        "pattern": r"\bPattern\s*[:\-]?\s*([A-Za-z][A-Za-z &/-]{1,40})",
        "material": r"\bMaterial\s*[:\-]?\s*([A-Za-z0-9 %][A-Za-z0-9 %&/-]{1,50})",
        "color": r"\bColou?r\s*[:\-]?\s*([A-Za-z][A-Za-z &/-]{1,30})",
        "category": r"\bSub\s*[Cc]ategory\s*[:\-]?\s*([A-Za-z][A-Za-z &/-]{1,50})",
    }

    for field, pattern in attribute_patterns.items():
        match = re.search(pattern, body_text)

        if match:
            row[field] = match.group(1).strip()

    # ---------------------------------------------------------------
    # Description fallback
    # ---------------------------------------------------------------
    if not row["description"]:
        row["description"] = first_meta_content(
            soup,
            name="description",
        )[:400]

    # ---------------------------------------------------------------
    # Field coverage statistics
    # ---------------------------------------------------------------
    metadata_fields = {
        "status",
        "error",
        "source",
        "page_type",
        "source_url",
        "collected_at",
    }

    for field in RAW_FIELDS:
        if field in metadata_fields:
            continue

        if row[field]:
            stats.fields_seen.add(field)
        else:
            stats.fields_missing.add(field)

    return row


def empty_row(
    url: str,
    status: str,
    error: str,
) -> Dict[str, str]:
    """Create a consistent CSV row for skipped/failed URLs."""
    return {
        **{field: "" for field in RAW_FIELDS},
        "source": "Nykaa Fashion",
        "page_type": "product",
        "source_url": url,
        "collected_at": now_utc(),
        "status": status,
        "error": error,
    }


def write_csv(rows: List[Dict[str, str]], path: str) -> None:
    """Write all rows using the fixed schema."""
    with open(path, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=RAW_FIELDS,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def append_summary(stats: RunStats, path: str) -> str:
    """Append a real run summary; values are never hard-coded."""
    fields_never_captured = sorted(
        set(RAW_FIELDS)
        - {
            "source",
            "page_type",
            "source_url",
            "collected_at",
            "status",
            "error",
        }
        - stats.fields_seen
    )

    summary = f"""## Nykaa Fashion
- Run at: {now_utc()}
- Discovery method: sitemap-first
- Sitemap index: {SITEMAP_INDEX_URL}
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
- Fields never captured: {", ".join(fields_never_captured) or "none"}

"""

    with open(path, "a", encoding="utf-8") as file:
        file.write(summary)

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scrape public Nykaa Fashion product pages."
    )

    parser.add_argument(
        "--max-products",
        type=int,
        default=500,
        help="Maximum number of unique product pages to visit.",
    )

    parser.add_argument(
        "--request-delay",
        type=float,
        default=2.0,
        help="Seconds to wait between requests.",
    )

    args = parser.parse_args()

    if args.max_products <= 0:
        parser.error("--max-products must be greater than 0")

    if args.request_delay < 0:
        parser.error("--request-delay cannot be negative")

    stats = RunStats()
    session = make_session()

    robots_parser = get_robots_parser(session)

    if robots_parser is None:
        print(
            "WARNING: live robots.txt could not be parsed this run. "
            "The verified hard-coded restrictions are still enforced."
        )

    print(
        f"\n=== Discovering product URLs via sitemap "
        f"(max {args.max_products}) ==="
    )

    product_urls = discover_product_urls(
        robots_parser=robots_parser,
        session=session,
        stats=stats,
        max_products=args.max_products,
        request_delay=args.request_delay,
    )

    print(
        f"\nDiscovered {len(product_urls)} candidate product URLs "
        f"({stats.duplicate_urls_removed} duplicates removed)."
    )

    rows: List[Dict[str, str]] = []

    print(f"\n=== Fetching {len(product_urls)} product pages ===")

    for index, url in enumerate(product_urls, start=1):
        if not allowed(robots_parser, url):
            print(
                f"[{index}/{len(product_urls)}] "
                f"robots.txt disallows, skipping: {url}"
            )

            rows.append(
                empty_row(
                    url,
                    "skipped_robots",
                    "Disallowed by robots.txt",
                )
            )
            continue

        stats.pages_attempted += 1

        print(f"[{index}/{len(product_urls)}] {url}")

        response, error = http_get(
            url,
            session,
        )

        time.sleep(args.request_delay)

        # IMPORTANT:
        # Explicit None check removes the Pylance "possibly None" errors
        # around response.status_code and response.text.
        if response is None:
            stats.errors += 1

            rows.append(
                empty_row(
                    url,
                    "error",
                    error or "No response received",
                )
            )
            continue

        if error:
            stats.errors += 1

            rows.append(
                empty_row(
                    url,
                    "error",
                    error,
                )
            )
            continue

        if response.status_code in (403, 429):
            stats.pages_blocked += 1

            rows.append(
                empty_row(
                    url,
                    "blocked",
                    f"HTTP {response.status_code}",
                )
            )

            print(f"  Blocked: HTTP {response.status_code}")
            continue

        if response.status_code != 200:
            stats.errors += 1

            rows.append(
                empty_row(
                    url,
                    "error",
                    f"HTTP {response.status_code}",
                )
            )

            print(f"  Error: HTTP {response.status_code}")
            continue

        stats.pages_successful += 1

        row = parse_product_page(
            response.text,
            url,
            stats,
        )

        stats.products_parsed += 1
        rows.append(row)

    output_csv = "nykaa_website_raw.csv"
    summary_file = "scraping_summary.md"

    write_csv(rows, output_csv)

    summary = append_summary(
        stats,
        summary_file,
    )

    print("\n" + "=" * 60)
    print("RUN COMPLETE")
    print("=" * 60)
    print(summary)
    print(f"CSV written: {output_csv}")
    print(f"Summary updated: {summary_file}")


if __name__ == "__main__":
    main()
