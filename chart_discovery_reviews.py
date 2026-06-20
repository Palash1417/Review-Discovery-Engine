"""
Spotify Music Discovery — Charts for presentation
=================================================

Generates presentation-ready bar charts from the tagged reviews:

  1. chart_subtheme_frequency.png  — how many reviews fall in each sub-theme
  2. chart_pct_negative.png        — % negative by sub-theme (which hurt most)
  3. chart_rating_segments.png     — low (1-2*) vs high (4-5*) raters by sub-theme
  4. chart_sentiment_overall.png   — overall sentiment split

Input : spotify_discovery_reviews_tagged.csv  (Phase 2 output)
        (override with the first command-line argument)

    python chart_discovery_reviews.py [tagged_csv]
"""

from __future__ import annotations

import sys

import matplotlib
matplotlib.use("Agg")  # headless: write PNGs, no display needed
import matplotlib.pyplot as plt
import pandas as pd

INPUT_CSV = sys.argv[1] if len(sys.argv) > 1 else "spotify_discovery_reviews_tagged.csv"
PREFIX = sys.argv[2] if len(sys.argv) > 2 else ""  # e.g. "v2_" to avoid overwriting

# Simple, readable styling.
plt.rcParams.update({"figure.autolayout": True, "font.size": 11})
SPOTIFY_GREEN = "#1DB954"
RED = "#E03B3B"
GREY = "#9AA0A6"


def _label(theme: str) -> str:
    return theme.replace("_", " ")


def chart_subtheme_frequency(df: pd.DataFrame) -> None:
    counts = df["discovery_subtheme"].value_counts().sort_values()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.barh([_label(t) for t in counts.index], counts.values, color=SPOTIFY_GREEN)
    for i, v in enumerate(counts.values):
        ax.text(v + 0.4, i, str(v), va="center", fontsize=10)
    ax.set_title("Discovery reviews by sub-theme", fontweight="bold")
    ax.set_xlabel("number of reviews")
    fig.savefig(f"{PREFIX}chart_subtheme_frequency.png", dpi=150)
    plt.close(fig)


def chart_pct_negative(df: pd.DataFrame) -> None:
    g = (
        df.assign(neg=df["sentiment"].eq("negative"))
        .groupby("discovery_subtheme")
        .agg(pct_neg=("neg", "mean"), n=("neg", "size"))
        .sort_values("pct_neg")
    )
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.barh([_label(t) for t in g.index], (g["pct_neg"] * 100).values, color=RED)
    for i, (pct, n) in enumerate(zip(g["pct_neg"], g["n"])):
        ax.text(pct * 100 + 1, i, f"{pct:.0%} (n={n})", va="center", fontsize=9)
    ax.set_title("% negative sentiment by sub-theme", fontweight="bold")
    ax.set_xlabel("% of reviews labeled negative")
    ax.set_xlim(0, 115)
    fig.savefig(f"{PREFIX}chart_pct_negative.png", dpi=150)
    plt.close(fig)


def chart_rating_segments(df: pd.DataFrame) -> None:
    if "rating" not in df.columns:
        return
    rated = df.dropna(subset=["rating"])
    low = rated[rated["rating"] <= 2]["discovery_subtheme"].value_counts()
    high = rated[rated["rating"] >= 4]["discovery_subtheme"].value_counts()
    themes = df["discovery_subtheme"].value_counts().index.tolist()
    low = low.reindex(themes, fill_value=0)
    high = high.reindex(themes, fill_value=0)

    y = range(len(themes))
    fig, ax = plt.subplots(figsize=(8.5, 5))
    h = 0.4
    ax.barh([i + h / 2 for i in y], low.values, height=h, color=RED,
            label="low raters (1-2★)")
    ax.barh([i - h / 2 for i in y], high.values, height=h, color=SPOTIFY_GREEN,
            label="high raters (4-5★)")
    ax.set_yticks(list(y))
    ax.set_yticklabels([_label(t) for t in themes])
    ax.invert_yaxis()
    ax.set_title("Discovery sub-themes: frustrated vs. satisfied users",
                 fontweight="bold")
    ax.set_xlabel("number of reviews")
    ax.legend()
    fig.savefig(f"{PREFIX}chart_rating_segments.png", dpi=150)
    plt.close(fig)


def chart_sentiment_overall(df: pd.DataFrame) -> None:
    order = ["negative", "mixed", "positive"]
    counts = df["sentiment"].value_counts().reindex(order, fill_value=0)
    colors = {"negative": RED, "mixed": GREY, "positive": SPOTIFY_GREEN}
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(order, counts.values, color=[colors[s] for s in order])
    total = counts.sum()
    for b, v in zip(bars, counts.values):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.5,
                f"{v}\n({v/total:.0%})", ha="center", fontsize=10)
    ax.set_title("Overall sentiment of discovery reviews", fontweight="bold")
    ax.set_ylabel("number of reviews")
    ax.set_ylim(0, counts.max() * 1.2)
    fig.savefig(f"{PREFIX}chart_sentiment_overall.png", dpi=150)
    plt.close(fig)


def main() -> int:
    df = pd.read_csv(INPUT_CSV)
    df = df[df["discovery_subtheme"].notna()].copy()
    chart_subtheme_frequency(df)
    chart_pct_negative(df)
    chart_rating_segments(df)
    chart_sentiment_overall(df)
    print(f"Wrote 4 charts from {INPUT_CSV} ({len(df)} reviews):")
    for name in ["chart_subtheme_frequency.png", "chart_pct_negative.png",
                 "chart_rating_segments.png", "chart_sentiment_overall.png"]:
        print(f"  {PREFIX}{name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
