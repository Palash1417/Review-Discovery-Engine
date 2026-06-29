# Architecture (the easy version)

The system is a **pipeline** — like an assembly line. Reviews go in one end, and
insights come out the other. Each stage does one job and hands its result to the
next stage.

## The assembly line

```
   SOURCES                  THE PIPELINE (one stage feeds the next)                 OUTPUTS
 ┌───────────┐
 │ Google    │
 │ Play      │──┐      ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌─────────────────┐
 │ Store     │  │      │ 1.       │   │ 2.       │   │ 3.       │   │ 4.       │   │  spotify_*.csv  │
 └───────────┘  ├────► │ COLLECT  ├──►│ FILTER   ├──►│ AI TAG   ├──►│ ANALYZE  ├──►│  *.xlsx         │
 ┌───────────┐  │      │ reviews  │   │ keep     │   │ topic +  │   │ find     │   │  report.md      │
 │ Apple App │  │      │          │   │ discovery│   │ feeling +│   │ patterns │   │  chart_*.png    │
 │ Store     │──┘      └──────────┘   └──────────┘   └────┬─────┘   └────┬─────┘   └─────────────────┘
 └───────────┘          ~1,800          ~160              │              │
                        reviews        reviews            ▼              ▼
                                                    ┌───────────────────────────┐
                                                    │   🤖 AI BRAIN (Groq /      │
                                                    │   Llama 3.3 70B)           │
                                                    │   reads & understands text │
                                                    └───────────────────────────┘
```

## The 4 stages = 4 scripts

| Stage | Script | Plain-English job | Hand-off |
|-------|--------|-------------------|----------|
| 1. Collect | `collect_spotify_reviews.py` | Download reviews from the app stores | a big list of ~1,800 reviews |
| 2. Filter | (in the same step) | Throw away reviews not about discovering music | ~160 relevant reviews |
| 3. AI Tag | `tag_discovery_reviews_groq.py` | Ask the AI to label each review (topic, feeling, complaint) | reviews + labels |
| 4. Analyze | `analyze_discovery_reviews.py` | Group the labels, count them, write a findings report | report + stats |
| (extra) Charts | `chart_discovery_reviews.py` | Turn the numbers into bar charts | PNG images |
| (extra) Excel | `export_reviews_to_excel.py` | Put everything into one workbook | `Spotify_Reviews.xlsx` |

## The one outside helper: the "AI brain"

Stages 3 and 4 don't understand language on their own — they phone a friend. That
friend is a **large language model (Llama 3.3 70B)** hosted by **Groq**, reached
over the internet with a free key. The pipeline sends it a review and a question;
the model sends back a clear answer. Everything else (downloading, filtering,
counting, charting) is ordinary Python that runs on your machine.

## Two ways to run the exact same pipeline

```
        Your computer                          Anybody's browser
   ┌──────────────────────┐              ┌──────────────────────────┐
   │ Run the .py scripts   │              │ Open the Colab notebook   │
   │ Key lives in .env     │              │ (no key needed — it shows │
   │ (private, gitignored) │              │  pre-computed results)    │
   └──────────┬───────────┘              └─────────────┬────────────┘
              │                                         │
              └──────────────┬──────────────────────────┘
                             ▼
                    Same logic, same outputs
```

- **Local:** you run the scripts; your secret Groq key sits in a private `.env`
  file that is never uploaded.
- **Cloud (Colab):** anyone opens the notebook link and runs it in their browser.
  The AI steps display results already saved in the repo, so testers need no key.

## How data flows (follow one review)

1. A review is **downloaded** → *"the shuffle plays the same songs"*
2. It **passes the filter** (mentions "shuffle") → kept
3. The **AI labels it** → topic: repetition · feeling: negative · complaint: "shuffle isn't random"
4. It gets **counted** with similar reviews → "100% of repetition reviews are negative"
5. That fact lands in the **report, charts, and Excel** you read at the end

## One-line summary
> A straight-line pipeline — **Collect → Filter → AI-Tag → Analyze** — where
> plain Python moves the data and an AI model does the reading, producing a
> report, charts, and an Excel file. It runs the same way on your computer or in
> a browser via Colab.
