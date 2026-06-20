"""
Spotify Music Discovery — Phase 1: Data Collection & Preprocessing
==================================================================

Collects user reviews/posts about Spotify from 4 sources, merges them into a
single CSV, then filters to music-discovery-relevant content.

Sources
-------
1. Apple App Store  — Spotify reviews (App ID 324684580)      [app-store-scraper]
2. Google Play Store — Spotify reviews (com.spotify.music)     [google-play-scraper]
3. Reddit subreddits — r/spotify, r/ifyoulikeblank, r/Music, r/listentothis  [PRAW]
4. Reddit keyword search — discover, recommend, algorithm, ...  [PRAW]

Output
------
- spotify_reviews_raw.csv        : everything collected (before filtering)
- spotify_discovery_reviews.csv  : filtered to discovery-relevant rows

Reddit credentials
------------------
PRAW needs an app registration (https://www.reddit.com/prefs/apps).
Provide credentials via environment variables before running:

    setx REDDIT_CLIENT_ID      "your_client_id"
    setx REDDIT_CLIENT_SECRET  "your_client_secret"
    setx REDDIT_USER_AGENT     "spotify-discovery-research by u/yourname"

If they are not set, the Reddit sources are skipped (logged), and the script
still produces output from the App Store and Play Store.
"""

from __future__ import annotations

import logging
import os
import sys
import time
from datetime import datetime, timedelta, timezone

import pandas as pd

# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------

TARGET_PER_SOURCE = 250                 # rows to aim for per source (pre-filter)
MONTHS_BACK = 12                        # date window
REDDIT_CALL_DELAY = 2.0                 # seconds between Reddit API calls

APP_STORE_ID = "324684580"              # Spotify on the App Store
PLAY_STORE_PACKAGE = "com.spotify.music"

# Reddit needs an authenticated app (anonymous access is blocked). When no
# credentials are supplied we proceed without it and instead maximise store
# collection across multiple English-language storefronts (free, no-auth).
APP_STORE_COUNTRIES = ["us", "gb", "ca"]            # gentle: Apple RSS throttles per IP
PLAY_STORE_COUNTRIES = ["us", "gb", "ca", "au", "in", "ie"]
PLAY_COUNT_PER_COUNTRY = 2000           # deep pagination; Spotify has huge review volume
STORE_MAX_PER_SOURCE = 3000             # cap per store source after dedup
APP_STORE_PAGE_DELAY = 1.5              # seconds between Apple RSS pages

REDDIT_SUBREDDITS = ["spotify", "ifyoulikeblank", "Music", "listentothis"]
REDDIT_SEARCH_KEYWORDS = [
    "discover", "recommend", "algorithm", "new music",
    "same songs", "repeat", "boring", "discovery",
]

# Keywords used to keep discovery-relevant rows (case-insensitive substring match)
FILTER_KEYWORDS = [
    "discover", "recommend", "algorithm", "new music", "suggestion",
    "playlist", "radio", "similar", "explore", "bubble", "repeat",
    "same songs", "boring", "tired", "stuck", "discovery",
    "find music", "find new",
]

COLUMNS = ["source", "date", "text", "rating", "url"]

RAW_OUTPUT = "spotify_reviews_raw.csv"
FILTERED_OUTPUT = "spotify_discovery_reviews.csv"

CUTOFF_DATE = datetime.now(timezone.utc) - timedelta(days=MONTHS_BACK * 30)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("spotify-collector")


def _to_utc(dt: datetime) -> datetime:
    """Ensure a datetime is timezone-aware (UTC)."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


# ----------------------------------------------------------------------------
# Source 1 — Apple App Store
# ----------------------------------------------------------------------------

def collect_app_store() -> list[dict]:
    """Collect Spotify reviews from the Apple App Store via the official RSS feed.

    Apple exposes a free, no-auth customer-reviews RSS feed:
        https://itunes.apple.com/{country}/rss/customerreviews/page={n}/id={id}/sortby=mostrecent/json
    Up to 10 pages x 50 reviews are available. This replaces the unmaintained
    `app-store-scraper` package, whose token-scraping endpoint Apple now blocks.
    """
    import requests

    rows: list[dict] = []
    headers = {"User-Agent": "Mozilla/5.0 (spotify-discovery-research)"}

    # Fast throttle probe: Apple soft-throttles per IP by returning HTTP 200 with
    # an empty feed, and that cooldown can last a long time. Probe once before
    # committing to the (slow) per-storefront backoff loop. If throttled, skip
    # App Store cleanly this run rather than burning ~17 minutes retrying.
    probe_url = (
        f"https://itunes.apple.com/us/rss/customerreviews/"
        f"page=1/id={APP_STORE_ID}/sortby=mostrecent/json"
    )
    try:
        probe = requests.get(probe_url, headers=headers, timeout=30)
        if not probe.json().get("feed", {}).get("entry", []):
            log.warning(
                "App Store: Apple is throttling this IP (empty feed). Skipping App "
                "Store this run. Re-run later or from another network to collect it."
            )
            return rows
    except Exception as exc:  # noqa: BLE001
        log.error("App Store probe failed: %s — skipping App Store this run.", exc)
        return rows

    for country in APP_STORE_COUNTRIES:
        country_count = 0
        try:
            for page in range(1, 11):  # max 10 pages of 50 per storefront
                url = (
                    f"https://itunes.apple.com/{country}/rss/customerreviews/"
                    f"page={page}/id={APP_STORE_ID}/sortby=mostrecent/json"
                )
                # Apple soft-throttles per IP by returning HTTP 200 with an empty
                # feed. On page 1, retry with exponential backoff until it
                # recovers; on later pages an empty feed just means "no more".
                entries: list = []
                attempts = 8 if page == 1 else 1
                for attempt in range(attempts):
                    resp = requests.get(url, headers=headers, timeout=30)
                    resp.raise_for_status()
                    entries = resp.json().get("feed", {}).get("entry", [])
                    if entries or page > 1:
                        break
                    wait = min(60, 10 * (attempt + 1))  # 10,20,...,60s
                    log.info("App Store [%s] throttled (empty feed); retry in %ds", country.upper(), wait)
                    time.sleep(wait)

                # First entry on page 1 is app metadata (no im:rating) — skip.
                review_entries = [e for e in entries if "im:rating" in e]
                if not review_entries:
                    break

                for e in review_entries:
                    updated = e.get("updated", {}).get("label", "")
                    try:
                        review_date = _to_utc(datetime.fromisoformat(updated))
                    except ValueError:
                        review_date = None
                    if review_date and review_date < CUTOFF_DATE:
                        continue

                    title = e.get("title", {}).get("label", "")
                    content = e.get("content", {}).get("label", "")
                    rating = e.get("im:rating", {}).get("label")
                    link = e.get("author", {}).get("uri", {}).get("label", "")

                    rows.append({
                        "source": "app_store",
                        "date": review_date.isoformat() if review_date else "",
                        "text": (title + ". " + content).strip(". ").strip(),
                        "rating": int(rating) if rating and rating.isdigit() else None,
                        "url": link or f"https://apps.apple.com/{country}/app/spotify/id{APP_STORE_ID}",
                    })
                    country_count += 1

                if len(rows) >= STORE_MAX_PER_SOURCE:
                    break
                time.sleep(APP_STORE_PAGE_DELAY)  # be polite between pages

            log.info("App Store [%s]: %d reviews", country.upper(), country_count)
            if len(rows) >= STORE_MAX_PER_SOURCE:
                break
        except Exception as exc:  # noqa: BLE001 — keep other storefronts/sources alive
            log.error("App Store [%s] failed: %s", country.upper(), exc)

    log.info("App Store: collected %d reviews total (within last %d months)", len(rows), MONTHS_BACK)
    return rows


# ----------------------------------------------------------------------------
# Source 2 — Google Play Store
# ----------------------------------------------------------------------------

def collect_play_store() -> list[dict]:
    """Collect Spotify reviews from the Google Play Store."""
    rows: list[dict] = []
    from google_play_scraper import Sort, reviews

    for country in PLAY_STORE_COUNTRIES:
        country_count = 0
        try:
            result, _ = reviews(
                PLAY_STORE_PACKAGE,
                lang="en",
                country=country,
                sort=Sort.NEWEST,
                count=PLAY_COUNT_PER_COUNTRY,  # deep pull; filter by date + dedup later
            )

            for r in result:
                review_date = r.get("at")
                if isinstance(review_date, datetime):
                    review_date = _to_utc(review_date)
                    if review_date < CUTOFF_DATE:
                        continue
                rows.append({
                    "source": "play_store",
                    "date": review_date.isoformat() if isinstance(review_date, datetime) else "",
                    "text": (r.get("content") or "").strip(),
                    "rating": r.get("score"),
                    "url": f"https://play.google.com/store/apps/details?id={PLAY_STORE_PACKAGE}",
                })
                country_count += 1

            log.info("Play Store [%s]: %d reviews", country.upper(), country_count)
            if len(rows) >= STORE_MAX_PER_SOURCE:
                break
        except Exception as exc:  # noqa: BLE001 — keep other storefronts/sources alive
            log.error("Play Store [%s] failed: %s", country.upper(), exc)

    log.info("Play Store: collected %d reviews total (within last %d months)", len(rows), MONTHS_BACK)
    return rows


# ----------------------------------------------------------------------------
# Reddit helpers
# ----------------------------------------------------------------------------

def _get_reddit_client():
    """Build a read-only PRAW client from environment variables, or None."""
    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    user_agent = os.environ.get("REDDIT_USER_AGENT", "spotify-discovery-research")

    if not client_id or not client_secret:
        log.warning(
            "Reddit credentials not found (REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET). "
            "Skipping Reddit sources. Set them and re-run to collect sources 3 & 4."
        )
        return None

    try:
        import praw

        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
            check_for_async=False,
        )
        reddit.read_only = True
        # Touch the API once to validate credentials early.
        _ = reddit.user.me()  # returns None in read-only mode but forces auth
        log.info("Reddit client initialized (read-only).")
        return reddit
    except Exception as exc:  # noqa: BLE001
        log.error("Reddit authentication failed: %s", exc)
        return None


def _submission_to_row(sub, source: str) -> dict:
    created = datetime.fromtimestamp(sub.created_utc, tz=timezone.utc)
    body = sub.selftext or ""
    text = (sub.title + ". " + body).strip(". ").strip()
    return {
        "source": source,
        "date": created.isoformat(),
        "text": text,
        "rating": None,  # Reddit posts have no star rating; score lives elsewhere
        "url": f"https://www.reddit.com{sub.permalink}",
    }


# ----------------------------------------------------------------------------
# Source 3 — Reddit subreddits
# ----------------------------------------------------------------------------

def collect_reddit_subreddits(reddit) -> list[dict]:
    rows: list[dict] = []
    if reddit is None:
        return rows

    per_sub = max(1, TARGET_PER_SOURCE // len(REDDIT_SUBREDDITS))
    for name in REDDIT_SUBREDDITS:
        try:
            log.info("Reddit r/%s: fetching newest ~%d posts", name, per_sub)
            for sub in reddit.subreddit(name).new(limit=per_sub * 2):
                created = datetime.fromtimestamp(sub.created_utc, tz=timezone.utc)
                if created < CUTOFF_DATE:
                    continue
                rows.append(_submission_to_row(sub, "reddit_subreddit"))
            time.sleep(REDDIT_CALL_DELAY)
        except Exception as exc:  # noqa: BLE001
            log.error("Reddit r/%s failed: %s", name, exc)

    # Trim toward target while keeping variety across subreddits.
    log.info("Reddit subreddits: collected %d posts", len(rows))
    return rows[:TARGET_PER_SOURCE]


# ----------------------------------------------------------------------------
# Source 4 — Reddit keyword search
# ----------------------------------------------------------------------------

def collect_reddit_search(reddit) -> list[dict]:
    rows: list[dict] = []
    if reddit is None:
        return rows

    seen_ids: set[str] = set()
    per_kw = max(1, TARGET_PER_SOURCE // len(REDDIT_SEARCH_KEYWORDS))
    for kw in REDDIT_SEARCH_KEYWORDS:
        try:
            query = f'spotify {kw}'
            log.info("Reddit search: '%s' (~%d results)", query, per_kw)
            for sub in reddit.subreddit("all").search(
                query, sort="new", time_filter="year", limit=per_kw * 2
            ):
                if sub.id in seen_ids:
                    continue
                created = datetime.fromtimestamp(sub.created_utc, tz=timezone.utc)
                if created < CUTOFF_DATE:
                    continue
                seen_ids.add(sub.id)
                rows.append(_submission_to_row(sub, "reddit_search"))
            time.sleep(REDDIT_CALL_DELAY)
        except Exception as exc:  # noqa: BLE001
            log.error("Reddit search '%s' failed: %s", kw, exc)

    log.info("Reddit search: collected %d posts", len(rows))
    return rows[:TARGET_PER_SOURCE]


# ----------------------------------------------------------------------------
# Filtering
# ----------------------------------------------------------------------------

def filter_discovery(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only rows whose text contains a discovery keyword (case-insensitive)."""
    if df.empty:
        return df
    pattern = "|".join(pd.Series(FILTER_KEYWORDS).map(lambda k: k.replace(" ", r"\s+")))
    mask = df["text"].fillna("").str.contains(pattern, case=False, regex=True)
    return df[mask].reset_index(drop=True)


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main() -> int:
    log.info("Starting Spotify discovery data collection (cutoff: %s)", CUTOFF_DATE.date())

    reddit = _get_reddit_client()

    collected = {
        "app_store": collect_app_store(),
        "play_store": collect_play_store(),
        "reddit_subreddit": collect_reddit_subreddits(reddit),
        "reddit_search": collect_reddit_search(reddit),
    }

    all_rows = [row for rows in collected.values() for row in rows]
    df = pd.DataFrame(all_rows, columns=COLUMNS)

    # Drop empty-text rows and exact-duplicate texts before saving.
    df["text"] = df["text"].fillna("").str.strip()
    df = df[df["text"] != ""]
    df = df.drop_duplicates(subset=["source", "text"]).reset_index(drop=True)

    df.to_csv(RAW_OUTPUT, index=False, encoding="utf-8-sig")

    filtered = filter_discovery(df)
    filtered.to_csv(FILTERED_OUTPUT, index=False, encoding="utf-8-sig")

    # ----- Summary -----
    print("\n" + "=" * 60)
    print("COLLECTION SUMMARY")
    print("=" * 60)
    print("Rows collected per source (raw, deduped, within 12 months):")
    raw_counts = df["source"].value_counts().to_dict()
    for src in ["app_store", "play_store", "reddit_subreddit", "reddit_search"]:
        print(f"  {src:<18}: {raw_counts.get(src, 0)}")
    print(f"  {'TOTAL (raw)':<18}: {len(df)}")
    print("-" * 60)
    print("Rows after discovery filter:")
    filt_counts = filtered["source"].value_counts().to_dict() if not filtered.empty else {}
    for src in ["app_store", "play_store", "reddit_subreddit", "reddit_search"]:
        print(f"  {src:<18}: {filt_counts.get(src, 0)}")
    print(f"  {'TOTAL (filtered)':<18}: {len(filtered)}")
    print("=" * 60)
    print(f"Raw data      -> {RAW_OUTPUT}")
    print(f"Filtered data -> {FILTERED_OUTPUT}")
    print("=" * 60 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
