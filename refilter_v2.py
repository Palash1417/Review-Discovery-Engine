"""
Spotify Music Discovery — Filter v2 (tighter, discovery-specific)
=================================================================

The Phase 1 filter was broad (it kept any review mentioning "playlist",
"radio", "boring", "stuck", "repeat", etc.), which pulled in a lot of generic
ads / billing / UI complaints — visible as the oversized "other" cluster (~30%).

This re-filters the RAW collection with a tighter, discovery-specific keyword
set, producing a cleaner dataset. It reuses tags already produced in Phase 2
(matched by review text) so it costs almost no Groq tokens — only genuinely new
rows are sent to the model.

Inputs  : spotify_reviews_raw.csv                (Phase 1 raw)
          spotify_discovery_reviews_tagged.csv   (Phase 2 tags, reused)
Outputs : spotify_discovery_reviews_v2.csv         (tight-filtered, untagged)
          spotify_discovery_reviews_v2_tagged.csv  (tight-filtered + tags)
"""

from __future__ import annotations

import os
import sys
import time

import pandas as pd

import tag_discovery_reviews_groq as tagger  # reuse client + tag_review

RAW_CSV = "spotify_reviews_raw.csv"
V1_TAGGED = "spotify_discovery_reviews_tagged.csv"
V2_CSV = "spotify_discovery_reviews_v2.csv"
V2_TAGGED = "spotify_discovery_reviews_v2_tagged.csv"

# Tighter, discovery-specific keywords/phrases. Deliberately drops broad terms
# (bare "playlist", "radio", "boring", "tired", "stuck", "repeat") that were
# catching ads/billing/UI complaints unrelated to discovery.
TIGHT_KEYWORDS = [
    "discover", "discovery", "discover weekly", "release radar",
    "recommend", "recommendation", "recommended",
    "algorithm", "suggest", "suggestion", "suggested",
    "new music", "new songs", "new artist", "fresh music",
    "explore", "exploration",
    "similar artist", "similar song", "similar music", "songs like", "music like",
    "find new", "find music", "finding new music",
    "filter bubble", "echo chamber",
    "same songs", "same music", "same artists", "on repeat", "repetitive",
    "smart shuffle", "autoplay", "song radio", "radio station",
    "personalized", "personalised", "for you", "my taste", "music taste",
    "variety", "rotation",
]


def tight_filter(df: pd.DataFrame) -> pd.DataFrame:
    pattern = "|".join(k.replace(" ", r"\s+") for k in TIGHT_KEYWORDS)
    mask = df["text"].fillna("").str.contains(pattern, case=False, regex=True)
    return df[mask].reset_index(drop=True)


def main() -> int:
    if not os.path.exists(RAW_CSV):
        print(f"ERROR: {RAW_CSV} not found.", file=sys.stderr)
        return 1

    raw = pd.read_csv(RAW_CSV)
    raw["text"] = raw["text"].fillna("").str.strip()
    raw = raw[raw["text"] != ""].drop_duplicates(subset=["source", "text"])

    v2 = tight_filter(raw)
    v2.to_csv(V2_CSV, index=False, encoding="utf-8-sig")
    print(f"Tight filter: {len(v2)} reviews kept (from {len(raw)} raw).")

    # Carry over Phase 2 tags by exact text match.
    for col in tagger.NEW_COLUMNS:
        v2[col] = pd.NA
    carried = 0
    if os.path.exists(V1_TAGGED):
        v1 = pd.read_csv(V1_TAGGED)
        tag_map = {
            str(r["text"]): (r["discovery_subtheme"], r["sentiment"], r["pain_point"])
            for _, r in v1.iterrows()
            if pd.notna(r.get("discovery_subtheme"))
        }
        for i in v2.index:
            t = str(v2.at[i, "text"])
            if t in tag_map:
                sub, sent, pain = tag_map[t]
                v2.at[i, "discovery_subtheme"] = sub
                v2.at[i, "sentiment"] = sent
                v2.at[i, "pain_point"] = pain
                carried += 1
    print(f"Carried over {carried} existing tags; "
          f"{len(v2) - carried} new rows need tagging.")

    # Tag only the genuinely new rows via Groq.
    todo = v2[v2["discovery_subtheme"].isna()].index.tolist()
    if todo:
        client = tagger._build_client()
        if client is None:
            print("WARNING: no Groq client; saving with untagged new rows.",
                  file=sys.stderr)
        else:
            done = 0
            for i in todo:
                text = str(v2.at[i, "text"]).strip()
                if not text:
                    continue
                try:
                    tags = tagger.tag_review(client, text)
                    v2.at[i, "discovery_subtheme"] = tags.discovery_subtheme
                    v2.at[i, "sentiment"] = tags.sentiment
                    v2.at[i, "pain_point"] = tags.pain_point.strip()
                    done += 1
                except Exception as exc:  # noqa: BLE001
                    print(f"  row {i}: tagging failed ({exc})", file=sys.stderr)
                if done % 10 == 0:
                    v2.to_csv(V2_TAGGED, index=False, encoding="utf-8-sig")
                time.sleep(tagger.CALL_DELAY)
            print(f"Newly tagged {done} rows.")

    v2.to_csv(V2_TAGGED, index=False, encoding="utf-8-sig")

    tagged = v2[v2["discovery_subtheme"].notna()]
    print("\n" + "=" * 56)
    print("FILTER v2 RESULT")
    print("=" * 56)
    print(f"Reviews (v2): {len(v2)}  |  tagged: {len(tagged)}")
    print("\nNew sub-theme distribution (v2):")
    for theme, n in tagged["discovery_subtheme"].value_counts().items():
        print(f"  {theme:<26}: {n} ({n/len(tagged):.0%})")
    print("=" * 56)
    print(f"Output -> {V2_TAGGED}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
