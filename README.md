# 🎵 Spotify Music Discovery — AI Review Analysis Pipeline

An AI-powered pipeline that collects Spotify user reviews, filters them to
music-discovery content, tags each review with a theme / sentiment / pain point
using a free LLM, and synthesizes findings that answer key research questions.

## ▶️ Try it in Google Colab — no API key needed

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Palash1417/Review-Discovery-Engine/blob/main/Spotify_Discovery_Pipeline_Colab.ipynb)

Open the notebook and choose **Runtime → Run all**. Collection, filtering, and
charts run live; the AI tagging + findings are shown from results committed in
this repo, so testers need **no API key**. (An optional cell lets anyone re-run
the AI live with their own free [Groq key](https://console.groq.com/keys).)

## Research questions this answers
1. Why do users struggle to discover new music?
2. What are the most common frustrations with recommendations?
3. What listening behaviors are users trying to achieve?
4. What causes users to repeatedly listen to the same content?
5. Which user segments experience different discovery challenges?
6. What unmet needs emerge consistently across reviews?

➡️ See **[`discovery_insights_report.md`](discovery_insights_report.md)** for the findings.

## Pipeline

| Phase | Script | What it does |
|------|--------|--------------|
| 1 — Collect | `collect_spotify_reviews.py` | Google Play + Apple App Store (free, no-auth) + Reddit (optional, needs PRAW keys). Merges to `spotify_discovery_reviews.csv`. |
| 2 — Tag | `tag_discovery_reviews_groq.py` | Labels each review with `discovery_subtheme`, `sentiment`, `pain_point` via Groq (Llama 3.3 70B). Anthropic/Claude version: `tag_discovery_reviews.py`. |
| 2b — Refine | `refilter_v2.py` | Tighter discovery filter, reusing existing tags. |
| 3 — Analyze | `analyze_discovery_reviews.py` | Map-reduce synthesis → `discovery_insights_report.md`. |
| 4 — Chart | `chart_discovery_reviews.py` | Bar charts (PNG) of themes, sentiment, segments. |

## Run locally

```bash
pip install -r requirements.txt

# Put your free Groq key in a .env file (this file is gitignored):
#   GROQ_API_KEY=gsk_...

python collect_spotify_reviews.py        # Phase 1
python tag_discovery_reviews_groq.py     # Phase 2
python analyze_discovery_reviews.py      # Phase 3
python chart_discovery_reviews.py        # charts
```

## Outputs
- `spotify_discovery_reviews.csv` — filtered discovery reviews
- `spotify_discovery_reviews_tagged.csv` — + AI tags
- `discovery_insights_report.md` — findings report
- `chart_*.png` — charts

## Security
API keys live in `.env`, which is **gitignored** — never commit keys. The
public Colab demo runs key-free by using the committed result files.

## Limitations
Dataset is single-source (Google Play dominates; Apple App Store throttles
cloud IPs), recent (high review volume compresses the date range), and
English-language. Reddit is excluded unless PRAW credentials are supplied.
