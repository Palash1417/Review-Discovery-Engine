"""
Fetch at least 2,000 *filtered* (music-discovery) Spotify reviews.

The discovery filter keeps ~9% of reviews, so this deep-paginates the Google
Play reviews feed (newest-first, via continuation tokens), filtering as it goes,
until it has TARGET_FILTERED discovery-relevant reviews. Apple App Store RSS is
added as a small top-up.

Outputs:
  spotify_reviews_raw_large.csv          (everything collected)
  spotify_discovery_reviews_2000.csv     (filtered to >= TARGET_FILTERED)
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone

import pandas as pd
from google_play_scraper import Sort, reviews

TARGET_FILTERED = 2000
MAX_RAW = 60000                 # safety cap so it can't run forever
MONTHS_BACK = 12
BATCH = 400                     # reviews per pagination call
PLAY_PKG = "com.spotify.music"
APP_STORE_ID = "324684580"
# Many English-language storefronts; Google caps pagination depth per
# country/sort (~1.7k each), so breadth across stores + two sort orders is how
# we reach the volume needed for 2,000 filtered reviews.
PLAY_COUNTRIES = ["us", "gb", "ca", "au", "in", "ie", "nz", "za", "sg",
                  "ph", "my", "ng", "ke", "pk"]
SORTS = [Sort.NEWEST, Sort.MOST_RELEVANT]
CUTOFF = datetime.now(timezone.utc) - timedelta(days=MONTHS_BACK * 30)

# Canonical discovery filter (same keyword set as the main pipeline).
FILTER_KEYWORDS = [
    "discover", "recommend", "algorithm", "new music", "suggestion", "playlist",
    "radio", "similar", "explore", "bubble", "repeat", "same songs", "boring",
    "tired", "stuck", "discovery", "find music", "find new",
]
PATTERN = "|".join(k.replace(" ", r"\s+") for k in FILTER_KEYWORDS)


def _utc(dt):
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def is_discovery(text: str) -> bool:
    import re
    return bool(re.search(PATTERN, text or "", re.IGNORECASE))


def main() -> int:
    seen_texts: set[str] = set()
    rows: list[dict] = []
    filtered_rows: list[dict] = []

    def consider(row):
        t = row["text"].strip()
        if not t or t in seen_texts:
            return
        seen_texts.add(t)
        rows.append(row)
        if is_discovery(t):
            filtered_rows.append(row)

    # ---- Google Play: deep pagination per (country, sort) ----
    for country in PLAY_COUNTRIES:
        if len(filtered_rows) >= TARGET_FILTERED or len(rows) >= MAX_RAW:
            break
        for sort in SORTS:
            if len(filtered_rows) >= TARGET_FILTERED or len(rows) >= MAX_RAW:
                break
            token = None
            first = True
            while True:
                try:
                    if first:
                        batch, token = reviews(PLAY_PKG, lang="en", country=country,
                                               sort=sort, count=BATCH)
                        first = False
                    else:
                        batch, token = reviews(PLAY_PKG, continuation_token=token)
                except Exception as exc:  # noqa: BLE001
                    print(f"  [{country}/{sort}] stopped: {exc}")
                    break
                if not batch:
                    break
                for r in batch:
                    d = r.get("at")
                    if isinstance(d, datetime):
                        d = _utc(d)
                        if d < CUTOFF:
                            continue
                    consider({
                        "source": "play_store",
                        "date": d.isoformat() if isinstance(d, datetime) else "",
                        "text": (r.get("content") or "").strip(),
                        "rating": r.get("score"),
                        "url": f"https://play.google.com/store/apps/details?id={PLAY_PKG}",
                    })
                if len(filtered_rows) >= TARGET_FILTERED or len(rows) >= MAX_RAW or token is None:
                    break
                time.sleep(0.2)
            print(f"  [{country.upper()}/{getattr(sort,'name',sort)}] "
                  f"raw={len(rows)} filtered={len(filtered_rows)}")

    # ---- Apple App Store RSS top-up ----
    if len(filtered_rows) < TARGET_FILTERED:
        import requests
        h = {"User-Agent": "Mozilla/5.0 (research)"}
        try:
            for page in range(1, 11):
                url = (f"https://itunes.apple.com/us/rss/customerreviews/"
                       f"page={page}/id={APP_STORE_ID}/sortby=mostrecent/json")
                entries = requests.get(url, headers=h, timeout=30).json().get("feed", {}).get("entry", [])
                revs = [e for e in entries if "im:rating" in e]
                if not revs:
                    break
                for e in revs:
                    try:
                        d = _utc(datetime.fromisoformat(e.get("updated", {}).get("label", "")))
                    except ValueError:
                        d = None
                    if d and d < CUTOFF:
                        continue
                    consider({
                        "source": "app_store",
                        "date": d.isoformat() if d else "",
                        "text": (e.get("title", {}).get("label", "") + ". " +
                                 e.get("content", {}).get("label", "")).strip(". "),
                        "rating": int(e.get("im:rating", {}).get("label") or 0) or None,
                        "url": e.get("author", {}).get("uri", {}).get("label", ""),
                    })
                time.sleep(0.4)
        except Exception as exc:  # noqa: BLE001
            print(f"App Store top-up stopped: {exc}")

    cols = ["source", "date", "text", "rating", "url"]
    pd.DataFrame(rows, columns=cols).to_csv("spotify_reviews_raw_large.csv", index=False, encoding="utf-8-sig")
    filt = pd.DataFrame(filtered_rows, columns=cols)
    filt.to_csv("spotify_discovery_reviews_2000.csv", index=False, encoding="utf-8-sig")

    print("\n" + "=" * 56)
    print("FETCH COMPLETE")
    print("=" * 56)
    print(f"Raw reviews collected : {len(rows)}")
    print(f"Discovery (filtered)  : {len(filtered_rows)}  (target {TARGET_FILTERED})")
    print(f"Filter pass rate      : {len(filtered_rows)/max(1,len(rows)):.1%}")
    print("By source (filtered):")
    for s, n in filt["source"].value_counts().items():
        print(f"  {s}: {n}")
    print("=" * 56)
    print("Output -> spotify_discovery_reviews_2000.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
