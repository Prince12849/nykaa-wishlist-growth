"""
Nykaa Fashion App Store (iOS) review scraper
==============================================
Setup:
    pip install app-store-scraper

If you hit a "requests==2.23.0" conflict error, also run:
    pip install --upgrade requests urllib3
(app-store-scraper pins an old requests version but works fine with newer ones)

Run:
    python scrape_appstore_reviews.py

Output:
    nykaa_appstore_reviews_tagged.csv
"""

import csv
import re
from app_store_scraper import AppStore

APP_NAME = "nykaa-fashion-shopping-app"
APP_ID = 1439872423
COUNTRY = "in"
HOW_MANY = 2000  # it will stop early if fewer exist
OUTPUT_FILE = "nykaa_appstore_reviews_tagged.csv"

HIGH_RELEVANCE = [
    "wishlist", "wish list", "saved", "save for later", "still deciding",
    "haven't bought", "havent bought", "not sure if", "waiting for",
    "price drop", "still thinking", "comparing", "compare price",
]
MEDIUM_RELEVANCE = [
    "size chart", "true to size", "runs small", "runs big", "fit", "fitting",
    "occasion", "styling", "authentic", "fake", "quality of fabric",
    "material feels", "reviews before", "trust",
]

def tag_relevance(text: str) -> str:
    t = text.lower()
    if any(k in t for k in HIGH_RELEVANCE):
        return "HIGH"
    if any(k in t for k in MEDIUM_RELEVANCE):
        return "MEDIUM"
    return "LOW"

def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()

def main():
    print(f"Fetching App Store reviews for {APP_NAME} (id {APP_ID})...")
    app = AppStore(country=COUNTRY, app_name=APP_NAME, app_id=APP_ID)
    app.review(how_many=HOW_MANY)
    print(f"Fetched {len(app.reviews)} reviews.")

    rows, seen = [], set()
    for r in app.reviews:
        text = clean(r.get("review", ""))
        if not text or text in seen:
            continue
        seen.add(text)
        rows.append({
            "source": "App Store",
            "rating": r.get("rating"),
            "date": str(r.get("date")),
            "text": text,
            "relevance": tag_relevance(text),
        })

    rows.sort(key=lambda x: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}[x["relevance"]])

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["source", "rating", "date", "text", "relevance"])
        writer.writeheader()
        writer.writerows(rows)

    high = sum(1 for r in rows if r["relevance"] == "HIGH")
    med = sum(1 for r in rows if r["relevance"] == "MEDIUM")
    low = sum(1 for r in rows if r["relevance"] == "LOW")
    total = max(len(rows), 1)
    print(f"\nHIGH: {high} ({high/total*100:.1f}%)  MEDIUM: {med} ({med/total*100:.1f}%)  LOW: {low} ({low/total*100:.1f}%)")
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
