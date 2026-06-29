"""
Spotify Music Discovery — Phase 3: Insight Synthesis
====================================================

Turns the tagged reviews (Phase 2) into a research report answering:

  1. Why do users struggle to discover new music?
  2. What are the most common frustrations with recommendations?
  3. What listening behaviors are users trying to achieve?
  4. What causes users to repeatedly listen to the same content?
  5. Which user segments experience different discovery challenges?
  6. What unmet needs emerge consistently across reviews?

Method (map-reduce, so it stays within Groq's free-tier rate limits and stays
grounded in the actual reviews):

  - MAP    : summarize each discovery sub-theme cluster separately
             (frustrations, goals, unmet needs, verbatim quotes).
  - STATS  : exact counts/cross-tabs computed in Python (not by the model),
             so every number in the report is real.
  - REDUCE : synthesize the cluster summaries + stats into the final report,
             answering each of the six questions with evidence.

Input  : spotify_discovery_reviews_tagged.csv   (Phase 2 output)
Output : discovery_insights_report.md
         discovery_stats.csv   (the quantitative tables, for your appendix)

Setup
-----
    pip install groq pandas python-dotenv
    # GROQ_API_KEY in .env (same key used for Phase 2)
    python analyze_discovery_reviews.py
"""

from __future__ import annotations

import os
import sys
import time

import pandas as pd

try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass

MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
# Optionally pass a different tagged CSV as the first argument, e.g.
#   python analyze_discovery_reviews.py spotify_discovery_reviews_v2_tagged.csv
INPUT_CSV = sys.argv[1] if len(sys.argv) > 1 else "spotify_discovery_reviews_tagged.csv"
_suffix = "_2000" if "2000" in INPUT_CSV else ("_v2" if "_v2" in INPUT_CSV else "")
REPORT_MD = f"discovery_insights_report{_suffix}.md"
STATS_CSV = f"discovery_stats{_suffix}.csv"
CALL_DELAY = 2.0

RESEARCH_QUESTIONS = [
    "Why do users struggle to discover new music?",
    "What are the most common frustrations with recommendations?",
    "What listening behaviors are users trying to achieve?",
    "What causes users to repeatedly listen to the same content?",
    "Which user segments experience different discovery challenges?",
    "What unmet needs emerge consistently across reviews?",
]


def _build_client():
    if not os.environ.get("GROQ_API_KEY"):
        print("ERROR: GROQ_API_KEY is not set (check your .env file).", file=sys.stderr)
        return None
    try:
        from groq import Groq

        return Groq()
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: could not initialize Groq client: {exc}", file=sys.stderr)
        return None


def _chat(client, system: str, user: str, max_tokens: int = 1200) -> str:
    resp = client.chat.completions.create(
        model=MODEL,
        max_tokens=max_tokens,
        temperature=0.2,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return resp.choices[0].message.content.strip()


# ----------------------------------------------------------------------------
# Quantitative layer — exact numbers computed in Python
# ----------------------------------------------------------------------------

def compute_stats(df: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    """Return (human-readable stats block, a tidy stats DataFrame for CSV)."""
    n = len(df)
    lines = [f"Total discovery reviews analyzed: {n}"]

    # Sub-theme counts
    theme_counts = df["discovery_subtheme"].value_counts()
    lines.append("\nSub-theme counts:")
    for theme, c in theme_counts.items():
        lines.append(f"  {theme}: {c} ({c / n:.0%})")

    # Sentiment overall
    sent_counts = df["sentiment"].value_counts()
    lines.append("\nSentiment overall:")
    for s, c in sent_counts.items():
        lines.append(f"  {s}: {c} ({c / n:.0%})")

    # Sentiment by sub-theme (% negative is the key signal)
    lines.append("\n% negative by sub-theme (which themes hurt most):")
    neg_by_theme = (
        df.assign(is_neg=df["sentiment"].eq("negative"))
        .groupby("discovery_subtheme")["is_neg"]
        .mean()
        .sort_values(ascending=False)
    )
    for theme, frac in neg_by_theme.items():
        lines.append(f"  {theme}: {frac:.0%} negative (n={int(theme_counts[theme])})")

    # Rating-based segments
    if "rating" in df.columns:
        rated = df.dropna(subset=["rating"])
        if not rated.empty:
            low = rated[rated["rating"] <= 2]
            high = rated[rated["rating"] >= 4]
            lines.append(
                f"\nRating segments: low (1-2 stars) = {len(low)}, "
                f"mid (3) = {len(rated) - len(low) - len(high)}, "
                f"high (4-5 stars) = {len(high)}"
            )
            lines.append("  Top sub-themes among LOW-rating (frustrated) users:")
            for theme, c in low["discovery_subtheme"].value_counts().head(4).items():
                lines.append(f"    {theme}: {c}")
            lines.append("  Top sub-themes among HIGH-rating (satisfied) users:")
            for theme, c in high["discovery_subtheme"].value_counts().head(4).items():
                lines.append(f"    {theme}: {c}")

    # Free-tier vs premium mentions (a real, recoverable segment signal)
    text_lc = df["text"].fillna("").str.lower()
    free_mask = text_lc.str.contains(r"\bfree\b|\bads?\b|advert|premium")
    lines.append(
        f"\nReviews mentioning free/ads/premium: {int(free_mask.sum())} "
        f"({free_mask.mean():.0%}) — a proxy for the free-tier segment."
    )

    # Tidy CSV: sub-theme x sentiment crosstab
    crosstab = pd.crosstab(df["discovery_subtheme"], df["sentiment"])
    crosstab["total"] = crosstab.sum(axis=1)
    crosstab = crosstab.sort_values("total", ascending=False)

    return "\n".join(lines), crosstab


# ----------------------------------------------------------------------------
# Map stage — per sub-theme cluster summaries
# ----------------------------------------------------------------------------

MAP_SYSTEM = (
    "You are a UX researcher analyzing Spotify reviews about music discovery. "
    "You summarize a cluster of reviews precisely and only from the text given."
)


MAP_SAMPLE = 40  # max reviews per cluster summary (keeps calls within rate limits)


def summarize_cluster(client, theme: str, sub: pd.DataFrame) -> str:
    n_total = len(sub)
    samples = []
    for _, r in sub.head(MAP_SAMPLE).iterrows():
        rating = r.get("rating")
        rtxt = f"{int(rating)}*" if pd.notna(rating) else "?*"
        samples.append(f"- ({rtxt}, {r['sentiment']}) {str(r['text'])[:240]}")
    block = "\n".join(samples)
    user = (
        f"Sub-theme: {theme} ({len(sub)} reviews).\n\n"
        f"Reviews:\n{block}\n\n"
        "Summarize this cluster in 4 short labeled parts:\n"
        "FRUSTRATIONS: the core complaints.\n"
        "GOALS: what listening behavior/outcome users are trying to achieve.\n"
        "UNMET NEEDS: what they wish existed.\n"
        "QUOTES: 2 short verbatim quotes (exact text) that best represent the cluster.\n"
        "Be concise and specific."
    )
    return f"### Cluster: {theme} (n={len(sub)})\n" + _chat(client, MAP_SYSTEM, user, 700)


# ----------------------------------------------------------------------------
# Reduce stage — final report answering the six questions
# ----------------------------------------------------------------------------

REDUCE_SYSTEM = (
    "You are a senior UX researcher writing the findings section of a study on "
    "Spotify music discovery. Write in clear markdown. Ground every claim in the "
    "provided cluster summaries and statistics. Use real quotes where helpful. "
    "Do not invent numbers — use only the statistics given. Be specific, not generic."
)


def build_report(client, stats_block: str, cluster_summaries: str) -> str:
    questions = "\n".join(f"{i+1}. {q}" for i, q in enumerate(RESEARCH_QUESTIONS))
    user = (
        "STATISTICS (exact — use these for all numbers):\n"
        f"{stats_block}\n\n"
        "CLUSTER SUMMARIES (qualitative evidence):\n"
        f"{cluster_summaries}\n\n"
        "Write a research report titled '# Spotify Music Discovery — Findings'. "
        "Open with a 3-4 sentence executive summary. Then answer EACH of the "
        "following questions as its own '## ' section, citing themes, stats, and "
        "quotes as evidence. End with a '## Limitations' section noting the dataset "
        "is single-source (Google Play), recent, and English-language.\n\n"
        f"Questions:\n{questions}"
    )
    return _chat(client, REDUCE_SYSTEM, user, 2600)


def main() -> int:
    if not os.path.exists(INPUT_CSV):
        print(f"ERROR: {INPUT_CSV} not found. Run Phase 2 first.", file=sys.stderr)
        return 1
    client = _build_client()
    if client is None:
        return 1

    df = pd.read_csv(INPUT_CSV)
    df = df[df["discovery_subtheme"].notna()].copy()
    print(f"Analyzing {len(df)} tagged reviews with '{MODEL}'...")

    stats_block, crosstab = compute_stats(df)
    crosstab.to_csv(STATS_CSV, encoding="utf-8-sig")
    print(f"Stats written -> {STATS_CSV}")

    # MAP: summarize each sub-theme cluster (largest first)
    summaries = []
    themes = df["discovery_subtheme"].value_counts().index.tolist()
    for theme in themes:
        sub = df[df["discovery_subtheme"] == theme]
        print(f"  summarizing cluster '{theme}' (n={len(sub)})...")
        try:
            summaries.append(summarize_cluster(client, theme, sub))
        except Exception as exc:  # noqa: BLE001
            print(f"    cluster '{theme}' failed: {exc}", file=sys.stderr)
        time.sleep(CALL_DELAY)

    cluster_summaries = "\n\n".join(summaries)

    # REDUCE: final report
    print("  synthesizing final report...")
    try:
        report_body = build_report(client, stats_block, cluster_summaries)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: report synthesis failed: {exc}", file=sys.stderr)
        return 1

    full = (
        report_body
        + "\n\n---\n\n## Appendix A — Exact Statistics\n\n```\n"
        + stats_block
        + "\n```\n\n## Appendix B — Per-Cluster Evidence\n\n"
        + cluster_summaries
        + "\n"
    )
    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write(full)

    print("\n" + "=" * 60)
    print("PHASE 3 ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"Report -> {REPORT_MD}")
    print(f"Stats  -> {STATS_CSV}")
    print("=" * 60 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
