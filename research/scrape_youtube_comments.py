"""
YouTube comment scraper — Nykaa Fashion haul/review videos
=============================================================
Setup:
    pip install youtube-comment-downloader
(no API key needed)

How to use:
    1. Go to YouTube and search "Nykaa Fashion haul", "Nykaa Fashion review",
       "Nykaa Fashion try on" etc.
    2. Pick 5-10 videos with a decent number of comments and paste their
       URLs into the VIDEO_URLS list below.

Run:
    python scrape_youtube_comments.py

Output:
    youtube_comments_tagged.csv
"""

import csv
import re
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR

VIDEO_URLS = [
   "https://www.youtube.com/watch?v=x-7eFM4KAhM",
   "https://www.youtube.com/watch?v=LBC5mN_cewc",
   "https://www.youtube.com/watch?v=-1B8U4O44fc",
   "https://www.youtube.com/watch?v=umn6g8ylmDU",
   "https://www.youtube.com/watch?v=3-Or0m04CRU",
   

]

MAX_COMMENTS_PER_VIDEO = 500

OUTPUT_FILE = "youtube_comments_tagged.csv"

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
    if not VIDEO_URLS:
        print("Add at least one video URL to VIDEO_URLS first — see instructions at the top of this file.")
        return

    downloader = YoutubeCommentDownloader()
    rows, seen = [], set()

    for url in VIDEO_URLS:
        print(f"Fetching comments from {url} ...")
        count = 0
        try:
            for comment in downloader.get_comments_from_url(url, sort_by=SORT_BY_POPULAR):
                if count >= MAX_COMMENTS_PER_VIDEO:
                    break
                text = clean(comment.get("text", ""))
                if not text or text in seen or len(text) < 10:
                    continue
                seen.add(text)
                rows.append({
                    "source": "YouTube comment",
                    "rating": "",
                    "date": comment.get("time", ""),
                    "text": text,
                    "relevance": tag_relevance(text),
                })
                count += 1
        except Exception as e:
            print(f"  Failed on {url}: {e}")

    rows.sort(key=lambda x: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}[x["relevance"]])

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["source", "rating", "date", "text", "relevance"])
        writer.writeheader()
        writer.writerows(rows)

    high = sum(1 for r in rows if r["relevance"] == "HIGH")
    med = sum(1 for r in rows if r["relevance"] == "MEDIUM")
    low = sum(1 for r in rows if r["relevance"] == "LOW")
    total = max(len(rows), 1)
    print(f"\nTotal collected: {len(rows)}")
    print(f"HIGH: {high} ({high/total*100:.1f}%)  MEDIUM: {med} ({med/total*100:.1f}%)  LOW: {low} ({low/total*100:.1f}%)")
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
