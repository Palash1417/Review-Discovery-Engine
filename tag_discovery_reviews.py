"""
Spotify Music Discovery — Phase 2: AI Tagging of Discovery Reviews
==================================================================

Enriches each discovery-relevant review with three AI-generated columns using
Claude Opus 4.8 (claude-opus-4-8) via the Anthropic Messages API:

    discovery_subtheme : which facet of music discovery the review is about
    sentiment          : positive | negative | mixed | neutral
    pain_point         : one-sentence extracted pain point (or "none")

Input  : spotify_discovery_reviews.csv   (Phase 1 output)
Output : spotify_discovery_reviews_tagged.csv

Design notes
------------
- Uses `client.messages.parse()` with a Pydantic schema so every response is a
  validated object — no brittle JSON string-parsing.
- The taxonomy/system prompt is stable and marked with cache_control, so the
  161 per-row calls reuse it from cache (~0.1x input cost after the first call).
- Writes results incrementally and skips already-tagged rows, so the run is
  resumable: if it's interrupted or rate-limited out, just run it again.
- API key is read from the ANTHROPIC_API_KEY environment variable. If it's
  missing, the script explains how to set it and exits without doing damage.

Setup
-----
    pip install anthropic pandas
    setx ANTHROPIC_API_KEY "sk-ant-..."     # then reopen the terminal
    python tag_discovery_reviews.py
"""

from __future__ import annotations

import os
import sys
from typing import Literal

import pandas as pd
from pydantic import BaseModel, Field

# Load keys from a local .env file (so you never paste them on the command line).
try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass  # fall back to real environment variables if python-dotenv isn't installed

MODEL = "claude-opus-4-8"
INPUT_CSV = "spotify_discovery_reviews.csv"
OUTPUT_CSV = "spotify_discovery_reviews_tagged.csv"

NEW_COLUMNS = ["discovery_subtheme", "sentiment", "pain_point"]

# Sub-themes grounded in the music-discovery research focus.
SUBTHEMES = [
    "recommendation_quality",     # how good/bad Claude's suggestions are
    "repetition_filter_bubble",   # same songs on repeat, stuck in a bubble
    "discovery_features",         # Discover Weekly, Radio, Release Radar, autoplay
    "playlist_curation",          # editorial / user playlists, organization
    "search_and_navigation",      # finding specific music, UI for browsing
    "algorithm_personalization",  # personalization quality, taste profiling
    "catalog_availability",       # whether desired music exists on the platform
    "other",                      # discovery-adjacent but none of the above
]

SYSTEM_PROMPT = f"""You are a research assistant labeling user reviews of Spotify \
for a study on music discovery. For each review you are given, classify it along \
three dimensions, judging ONLY by what the review text actually says.

1. discovery_subtheme — the single best-fitting facet of music discovery:
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

2. sentiment — the user's overall attitude in THIS review:
   positive | negative | mixed | neutral

3. pain_point — one concise sentence (max ~20 words) naming the core frustration \
about discovery, in your own words. If the review expresses no discovery-related \
frustration, return exactly "none".

Base every label strictly on the review text. Do not invent details."""


class ReviewTags(BaseModel):
    discovery_subtheme: Literal[
        "recommendation_quality",
        "repetition_filter_bubble",
        "discovery_features",
        "playlist_curation",
        "search_and_navigation",
        "algorithm_personalization",
        "catalog_availability",
        "other",
    ] = Field(description="Best-fitting music-discovery facet for this review.")
    sentiment: Literal["positive", "negative", "mixed", "neutral"] = Field(
        description="Overall attitude expressed in the review."
    )
    pain_point: str = Field(
        description='One short sentence naming the core discovery frustration, or "none".'
    )


def _build_client():
    """Construct the Anthropic client, or print guidance and return None."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "ERROR: ANTHROPIC_API_KEY is not set.\n"
            "Phase 2 needs an Anthropic API key to call Claude.\n"
            "  1. Get a key at https://console.anthropic.com/settings/keys\n"
            "  2. setx ANTHROPIC_API_KEY \"sk-ant-...\"   (then reopen the terminal)\n"
            "  3. python tag_discovery_reviews.py\n",
            file=sys.stderr,
        )
        return None
    try:
        import anthropic

        return anthropic.Anthropic()
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: could not initialize Anthropic client: {exc}", file=sys.stderr)
        return None


def tag_review(client, text: str) -> ReviewTags:
    """Classify a single review. The SDK auto-retries 429/5xx with backoff."""
    response = client.messages.parse(
        model=MODEL,
        max_tokens=512,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},  # reuse across all rows
            }
        ],
        messages=[{"role": "user", "content": f"Review:\n\"\"\"\n{text}\n\"\"\""}],
        output_format=ReviewTags,
    )
    return response.parsed_output


def main() -> int:
    if not os.path.exists(INPUT_CSV):
        print(f"ERROR: {INPUT_CSV} not found. Run Phase 1 first.", file=sys.stderr)
        return 1

    client = _build_client()
    if client is None:
        return 1

    df = pd.read_csv(INPUT_CSV)

    # Resume support: load prior tagged output and carry over completed rows.
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
    print(f"Tagging {len(todo)} of {total} reviews with {MODEL} "
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
        except Exception as exc:  # noqa: BLE001 — keep going, save progress
            failed += 1
            print(f"  row {i}: tagging failed ({exc})", file=sys.stderr)

        # Incremental save every 10 rows so progress survives interruption.
        if (done + failed) % 10 == 0:
            df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
            print(f"  ...{done} tagged so far")

    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    # ----- Summary -----
    print("\n" + "=" * 60)
    print("PHASE 2 TAGGING SUMMARY")
    print("=" * 60)
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
