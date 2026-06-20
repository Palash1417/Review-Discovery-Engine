"""
Spotify Music Discovery — Phase 2 (Groq edition): AI Tagging
============================================================

Same job as tag_discovery_reviews.py, but uses Groq's free API instead of the
Anthropic API. Groq serves open models (not Claude); this defaults to
Llama 3.3 70B, which handles this classification task well.

Adds three columns to each discovery review:
    discovery_subtheme : which facet of music discovery the review is about
    sentiment          : positive | negative | mixed | neutral
    pain_point         : one-sentence extracted pain point (or "none")

Input  : spotify_discovery_reviews.csv   (Phase 1 output)
Output : spotify_discovery_reviews_tagged.csv

How it works
------------
- Calls Groq's OpenAI-compatible chat API in JSON mode, then validates each
  response against a Pydantic schema (so bad output is caught, not silently saved).
- Resumable: writes incrementally and skips already-tagged rows.
- Free-tier friendly: a short delay between calls keeps you under the rate limit,
  and the SDK auto-retries on 429.

Setup
-----
    pip install groq pandas
    setx GROQ_API_KEY "gsk_..."          # then reopen the terminal
    python tag_discovery_reviews_groq.py

Get a free key at https://console.groq.com/keys
"""

from __future__ import annotations

import json
import os
import sys
import time

import pandas as pd
from pydantic import BaseModel, Field, ValidationError, field_validator

# Load keys from a local .env file (so you never paste them on the command line).
try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass  # fall back to real environment variables if python-dotenv isn't installed

# Default to a capable free Groq model; override with GROQ_MODEL if you like.
MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
INPUT_CSV = "spotify_discovery_reviews.csv"
OUTPUT_CSV = "spotify_discovery_reviews_tagged.csv"
CALL_DELAY = 2.0  # seconds between calls — keeps free tier under 30 req/min

NEW_COLUMNS = ["discovery_subtheme", "sentiment", "pain_point"]

SUBTHEMES = [
    "recommendation_quality",
    "repetition_filter_bubble",
    "discovery_features",
    "playlist_curation",
    "search_and_navigation",
    "algorithm_personalization",
    "catalog_availability",
    "other",
]
SENTIMENTS = ["positive", "negative", "mixed", "neutral"]

SYSTEM_PROMPT = f"""You are a research assistant labeling user reviews of Spotify \
for a study on music discovery. For each review, classify it along three \
dimensions, judging ONLY by what the review text actually says, and reply with a \
single JSON object.

The JSON object must have exactly these keys:

"discovery_subtheme": one of {SUBTHEMES}
  - recommendation_quality: quality of recommended/suggested songs or artists
  - repetition_filter_bubble: hearing the same songs repeatedly, feeling stuck, \
no variety, an echo chamber
  - discovery_features: specific discovery features (Discover Weekly, Radio, \
Release Radar, autoplay, Smart Shuffle)
  - playlist_curation: editorial or user playlists, how music is organized/curated
  - search_and_navigation: finding specific music, browsing, the discovery UI
  - algorithm_personalization: how well the algorithm learns/reflects the user's taste
  - catalog_availability: whether the music the user wants exists on the platform
  - other: discovery-adjacent but none of the above fit

"sentiment": one of {SENTIMENTS} — the user's overall attitude in this review

"pain_point": one concise sentence (max ~20 words) naming the core discovery \
frustration, in your own words. If the review expresses no discovery-related \
frustration, use exactly "none".

Base every label strictly on the review text. Do not invent details. \
Reply with ONLY the JSON object, no extra text."""


class ReviewTags(BaseModel):
    discovery_subtheme: str = Field(...)
    sentiment: str = Field(...)
    pain_point: str = Field(...)

    @field_validator("discovery_subtheme")
    @classmethod
    def _check_theme(cls, v: str) -> str:
        v = v.strip()
        return v if v in SUBTHEMES else "other"

    @field_validator("sentiment")
    @classmethod
    def _check_sentiment(cls, v: str) -> str:
        v = v.strip().lower()
        return v if v in SENTIMENTS else "neutral"


def _build_client():
    """Construct the Groq client, or print guidance and return None."""
    if not os.environ.get("GROQ_API_KEY"):
        print(
            "ERROR: GROQ_API_KEY is not set.\n"
            "Phase 2 needs a (free) Groq API key.\n"
            "  1. Get a free key at https://console.groq.com/keys\n"
            "  2. setx GROQ_API_KEY \"gsk_...\"   (then reopen the terminal)\n"
            "  3. python tag_discovery_reviews_groq.py\n",
            file=sys.stderr,
        )
        return None
    try:
        from groq import Groq

        return Groq()  # reads GROQ_API_KEY from env
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: could not initialize Groq client: {exc}", file=sys.stderr)
        return None


def tag_review(client, text: str) -> ReviewTags:
    """Classify a single review via Groq JSON mode; SDK auto-retries 429/5xx."""
    resp = client.chat.completions.create(
        model=MODEL,
        max_tokens=300,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f'Review:\n"""\n{text}\n"""'},
        ],
    )
    raw = resp.choices[0].message.content
    data = json.loads(raw)
    return ReviewTags(**data)


def main() -> int:
    if not os.path.exists(INPUT_CSV):
        print(f"ERROR: {INPUT_CSV} not found. Run Phase 1 first.", file=sys.stderr)
        return 1

    client = _build_client()
    if client is None:
        return 1

    df = pd.read_csv(INPUT_CSV)

    # Resume support: carry over any rows already tagged in a prior run.
    if os.path.exists(OUTPUT_CSV):
        prior = pd.read_csv(OUTPUT_CSV)
        for col in NEW_COLUMNS:
            if col in prior.columns:
                df[col] = prior[col]
    for col in NEW_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA

    total = len(df)
    todo = df[df["discovery_subtheme"].isna()].index.tolist()
    print(f"Tagging {len(todo)} of {total} reviews with Groq model '{MODEL}' "
          f"({total - len(todo)} already done)...")

    done = 0
    failed = 0
    for i in todo:
        text = str(df.at[i, "text"]).strip()
        if not text:
            continue
        try:
            tags = tag_review(client, text)
            df.at[i, "discovery_subtheme"] = tags.discovery_subtheme
            df.at[i, "sentiment"] = tags.sentiment
            df.at[i, "pain_point"] = tags.pain_point.strip()
            done += 1
        except (json.JSONDecodeError, ValidationError) as exc:
            failed += 1
            print(f"  row {i}: bad model output ({exc})", file=sys.stderr)
        except Exception as exc:  # noqa: BLE001 — keep going, save progress
            failed += 1
            print(f"  row {i}: tagging failed ({exc})", file=sys.stderr)

        if (done + failed) % 10 == 0:
            df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
            print(f"  ...{done} tagged so far")

        time.sleep(CALL_DELAY)  # stay within free-tier rate limits

    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    # ----- Summary -----
    print("\n" + "=" * 60)
    print("PHASE 2 TAGGING SUMMARY (Groq)")
    print("=" * 60)
    print(f"Model                   : {MODEL}")
    print(f"Reviews tagged this run : {done}")
    print(f"Failures this run       : {failed}")
    tagged = df[df["discovery_subtheme"].notna()]
    print(f"Total tagged rows       : {len(tagged)} / {total}")
    if not tagged.empty:
        print("\nDiscovery sub-theme distribution:")
        for theme, n in tagged["discovery_subtheme"].value_counts().items():
            print(f"  {theme:<26}: {n}")
        print("\nSentiment distribution:")
        for sent, n in tagged["sentiment"].value_counts().items():
            print(f"  {sent:<26}: {n}")
    print("=" * 60)
    print(f"Output -> {OUTPUT_CSV}")
    print("=" * 60 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
