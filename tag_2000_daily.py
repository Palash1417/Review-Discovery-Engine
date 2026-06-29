"""
Daily, resumable AI-tagging for the 2,033-review discovery dataset.

Groq's free tier allows ~100K tokens/day, which is roughly ~150 reviews. This
script tags up to DAILY_LIMIT reviews per run and then stops, so you can simply
run it once a day until all 2,033 are tagged. It is fully resumable: already
tagged rows are skipped, and tags are also reused (for free) from any review
text already labeled in spotify_discovery_reviews_tagged.csv.

Run daily:
    python tag_2000_daily.py
Override the per-run cap:
    set DAILY_LIMIT=120  &&  python tag_2000_daily.py     (Windows)
"""

from __future__ import annotations

import math
import os
import sys
import time

import pandas as pd

import tag_discovery_reviews_groq as tg  # reuse client + tag_review + columns

INPUT_CSV = "spotify_discovery_reviews_2000.csv"
OUTPUT_CSV = "spotify_discovery_reviews_2000_tagged.csv"
REUSE_FROM = "spotify_discovery_reviews_tagged.csv"   # 161 already-tagged rows
DAILY_LIMIT = int(os.environ.get("DAILY_LIMIT", "150"))
COLS = tg.NEW_COLUMNS


def _is_daily_cap(exc: Exception) -> bool:
    s = str(exc).lower()
    return ("tokens per day" in s or "tpd" in s or
            ("rate_limit" in s and "day" in s))


def main() -> int:
    if not os.path.exists(INPUT_CSV):
        print(f"ERROR: {INPUT_CSV} not found.", file=sys.stderr)
        return 1
    client = tg._build_client()
    if client is None:
        return 1

    df = pd.read_csv(INPUT_CSV)

    # Resume: load prior tagged output.
    if os.path.exists(OUTPUT_CSV):
        prior = pd.read_csv(OUTPUT_CSV)
        for c in COLS:
            if c in prior.columns:
                df[c] = prior[c]
    for c in COLS:
        if c not in df.columns:
            df[c] = pd.NA

    # Free reuse: carry over tags from the existing tagged file by exact text.
    if os.path.exists(REUSE_FROM):
        ref = pd.read_csv(REUSE_FROM)
        tmap = {str(r["text"]): (r["discovery_subtheme"], r["sentiment"], r["pain_point"])
                for _, r in ref.iterrows() if pd.notna(r.get("discovery_subtheme"))}
        reused = 0
        for i in df[df["discovery_subtheme"].isna()].index:
            t = str(df.at[i, "text"])
            if t in tmap:
                df.at[i, "discovery_subtheme"], df.at[i, "sentiment"], df.at[i, "pain_point"] = tmap[t]
                reused += 1
        if reused:
            print(f"Reused {reused} tags for free from {REUSE_FROM}.")
            df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    total = len(df)
    already = int(df["discovery_subtheme"].notna().sum())
    todo = df[df["discovery_subtheme"].isna()].index.tolist()
    print(f"Total {total} | already tagged {already} | remaining {len(todo)}")
    print(f"Tagging up to {DAILY_LIMIT} this run...\n")

    done = failed = 0
    capped = False
    for i in todo:
        if done >= DAILY_LIMIT:
            break
        text = str(df.at[i, "text"]).strip()
        if not text:
            continue
        try:
            tags = tg.tag_review(client, text)
            df.at[i, "discovery_subtheme"] = tags.discovery_subtheme
            df.at[i, "sentiment"] = tags.sentiment
            df.at[i, "pain_point"] = tags.pain_point.strip()
            done += 1
        except Exception as exc:  # noqa: BLE001
            if _is_daily_cap(exc):
                print(f"\nGroq daily token cap reached after {done} new tags this run.")
                print("Progress saved — just run this script again tomorrow.")
                capped = True
                break
            failed += 1
            print(f"  row {i}: failed ({exc})", file=sys.stderr)
        if done and done % 10 == 0:
            df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
            print(f"  ...{done} new this run")
        time.sleep(tg.CALL_DELAY)

    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    tagged_now = int(df["discovery_subtheme"].notna().sum())
    remaining = total - tagged_now
    print("\n" + "=" * 56)
    print("DAILY TAGGING SUMMARY")
    print("=" * 56)
    print(f"New tags this run : {done}   (failures {failed})")
    print(f"Total tagged      : {tagged_now} / {total}")
    print(f"Remaining         : {remaining}")
    if remaining > 0:
        days = math.ceil(remaining / max(1, DAILY_LIMIT))
        print(f"At {DAILY_LIMIT}/day, ~{days} more daily run(s) to finish"
              + ("  (cap hit — resume tomorrow)" if capped else ""))
    else:
        print("ALL REVIEWS TAGGED 🎉")
    print("=" * 56)
    print(f"Output -> {OUTPUT_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
