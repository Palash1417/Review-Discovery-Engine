"""
Builds a self-contained, KEY-FREE Google Colab notebook for the Spotify
discovery pipeline. Testers need no API key: the no-API steps (collection,
filtering, charts) run live, and the AI steps display pre-computed results that
are committed to the repo. An optional cell lets anyone re-run the AI live with
their own free Groq key.

Run:  python build_colab_notebook.py  ->  Spotify_Discovery_Pipeline_Colab.ipynb
"""
import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []
md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell

cells.append(md(
"""# 🎵 Spotify Music Discovery — Review Analysis Pipeline

An AI-powered pipeline that mines Spotify reviews to answer:
*Why do users struggle to discover new music? What frustrates them about
recommendations? What makes them replay the same songs? What unmet needs recur?*

**Pipeline:** collect reviews → filter to music-discovery content → AI-tag each
review (theme · sentiment · pain point) → synthesize findings → charts.

### How to run — no API key needed
Just **Runtime → Run all**. The data-collection, filtering, and charting steps
run live; the AI tagging + findings are shown from results already committed to
this repo, so **you do not need any API key to test the workflow.**

*(Optional: the last section lets you re-run the AI live if you have a free
Groq key from https://console.groq.com/keys.)*
"""))

cells.append(md("## 1 · Install dependencies & load the project"))
cells.append(code(
"!pip install -q google-play-scraper groq pandas matplotlib requests"))
cells.append(code(
'''# Clone this project so the pre-computed results + report are available.
# After you create your GitHub repo, set GITHUB_REPO to "<username>/<repo>".
GITHUB_REPO = "YOUR_USERNAME/spotify-discovery-pipeline"

import os
repo = GITHUB_REPO.split("/")[-1]
if not os.path.exists(repo):
    !git clone -q https://github.com/{GITHUB_REPO}.git
if os.path.isdir(repo):
    os.chdir(repo)
print("Working dir:", os.getcwd())
print("Files:", [f for f in os.listdir() if f.endswith((".csv", ".md", ".py"))])'''))

cells.append(md("## 2 · Phase 1 — Collect reviews (live · Google Play + Apple App Store)\n"
                "Free, no-auth sources. Reddit is omitted (it needs private API credentials)."))
cells.append(code(
'''from datetime import datetime, timedelta, timezone

TARGET_PER_SOURCE = 250
MONTHS_BACK = 12
CUTOFF = datetime.now(timezone.utc) - timedelta(days=MONTHS_BACK*30)
APP_STORE_ID = "324684580"
PLAY_PKG = "com.spotify.music"
print("Collecting reviews from the last", MONTHS_BACK, "months (since", CUTOFF.date(), ")")'''))
cells.append(code(
'''import requests, time, pandas as pd
from datetime import datetime, timezone

def _utc(dt):
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)

def collect_play():
    rows=[]
    try:
        from google_play_scraper import Sort, reviews
        res,_ = reviews(PLAY_PKG, lang="en", country="us", sort=Sort.NEWEST, count=TARGET_PER_SOURCE*3)
        for r in res:
            d=r.get("at")
            if isinstance(d,datetime):
                d=_utc(d)
                if d<CUTOFF: continue
            rows.append({"source":"play_store","date":d.isoformat() if isinstance(d,datetime) else "",
                         "text":(r.get("content") or "").strip(),"rating":r.get("score"),
                         "url":f"https://play.google.com/store/apps/details?id={PLAY_PKG}"})
            if len(rows)>=TARGET_PER_SOURCE: break
    except Exception as e:
        print("Play Store failed:", e)
    print(f"Play Store: {len(rows)} reviews")
    return rows

def collect_appstore():
    rows=[]; h={"User-Agent":"Mozilla/5.0 (research)"}
    try:
        for page in range(1,11):
            url=(f"https://itunes.apple.com/us/rss/customerreviews/page={page}/id={APP_STORE_ID}/sortby=mostrecent/json")
            entries=requests.get(url,headers=h,timeout=30).json().get("feed",{}).get("entry",[])
            revs=[e for e in entries if "im:rating" in e]
            if not revs: break
            for e in revs:
                try: d=_utc(datetime.fromisoformat(e.get("updated",{}).get("label","")))
                except ValueError: d=None
                if d and d<CUTOFF: continue
                rows.append({"source":"app_store","date":d.isoformat() if d else "",
                             "text":(e.get("title",{}).get("label","")+". "+e.get("content",{}).get("label","")).strip(". "),
                             "rating":int(e.get("im:rating",{}).get("label") or 0) or None,
                             "url":e.get("author",{}).get("uri",{}).get("label","")})
                if len(rows)>=TARGET_PER_SOURCE: break
            if len(rows)>=TARGET_PER_SOURCE: break
            time.sleep(0.5)
    except Exception as e:
        print("App Store failed (often Colab IP throttling):", e)
    print(f"App Store: {len(rows)} reviews")
    return rows

raw = pd.DataFrame(collect_play()+collect_appstore(), columns=["source","date","text","rating","url"])
raw["text"]=raw["text"].fillna("").str.strip()
raw = raw[raw["text"]!=""].drop_duplicates(subset=["source","text"]).reset_index(drop=True)
print("Total raw reviews collected live:", len(raw))
raw.head()'''))

cells.append(md("## 3 · Filter to music-discovery content (live)"))
cells.append(code(
'''import re
FILTER_KEYWORDS = ["discover","discovery","recommend","recommendation","algorithm","suggest",
    "suggestion","new music","new songs","new artist","explore","similar artist","similar song",
    "songs like","find new","find music","filter bubble","echo chamber","same songs","same music",
    "on repeat","repetitive","smart shuffle","autoplay","personalized","personalised","for you",
    "my taste","music taste","radio","playlist"]
pattern = "|".join(re.escape(k) for k in FILTER_KEYWORDS)
disc = raw[raw["text"].str.contains(pattern, case=False, regex=True)].reset_index(drop=True)
print(f"{len(disc)} of {len(raw)} live-collected reviews are discovery-relevant")
disc.head()'''))

cells.append(md("## 4 · Phase 2 — AI tagging (results)\n"
                "Each discovery review was tagged with a **discovery sub-theme**, **sentiment**, "
                "and an extracted **pain point** using a free Groq model (Llama 3.3 70B). "
                "Because AI tagging needs an API key/quota, the committed results are shown here. "
                "*(Re-run it live yourself in the optional section at the end.)*"))
cells.append(code(
'''import pandas as pd
tagged = pd.read_csv("spotify_discovery_reviews_tagged.csv")
print("Pre-computed tagged reviews:", tagged.shape[0])
print("\\nDiscovery sub-themes:\\n", tagged["discovery_subtheme"].value_counts().to_string())
print("\\nSentiment:\\n", tagged["sentiment"].value_counts().to_string())
tagged[["source","rating","discovery_subtheme","sentiment","pain_point","text"]].head(10)'''))

cells.append(md("## 5 · Charts (rendered live from the tagged data)"))
cells.append(code(
'''import matplotlib.pyplot as plt
GREEN,RED,GREY="#1DB954","#E03B3B","#9AA0A6"
def lab(t): return t.replace("_"," ")

vc=tagged["discovery_subtheme"].value_counts().sort_values()
plt.figure(figsize=(8,4)); plt.barh([lab(t) for t in vc.index],vc.values,color=GREEN)
plt.title("Discovery reviews by sub-theme"); plt.xlabel("reviews"); plt.tight_layout(); plt.show()

g=tagged.assign(neg=tagged["sentiment"].eq("negative")).groupby("discovery_subtheme")["neg"].mean().sort_values()
plt.figure(figsize=(8,4)); plt.barh([lab(t) for t in g.index],(g*100).values,color=RED)
plt.title("% negative by sub-theme"); plt.xlabel("% negative"); plt.xlim(0,110); plt.tight_layout(); plt.show()

order=["negative","mixed","positive"]; sc=tagged["sentiment"].value_counts().reindex(order,fill_value=0)
plt.figure(figsize=(5,3.5)); plt.bar(order,sc.values,color=[RED,GREY,GREEN])
plt.title("Overall sentiment"); plt.ylabel("reviews"); plt.tight_layout(); plt.show()'''))

cells.append(md("## 6 · Phase 3 — Findings report (answers the research questions)"))
cells.append(code(
'''from IPython.display import Markdown, display
display(Markdown(open("discovery_insights_report.md", encoding="utf-8").read()))'''))

cells.append(md("## (Optional) Re-run the AI live with your own free Groq key\n"
                "Skip this unless you have a key from https://console.groq.com/keys — the "
                "results above already demonstrate the full workflow."))
cells.append(code(
'''import os, json
from getpass import getpass
key = getpass("Groq API key (leave blank to skip): ").strip()
if not key:
    print("Skipped — using the pre-computed results shown above.")
else:
    os.environ["GROQ_API_KEY"]=key
    from groq import Groq
    client=Groq()
    SUB=["recommendation_quality","repetition_filter_bubble","discovery_features","playlist_curation",
         "search_and_navigation","algorithm_personalization","catalog_availability","other"]
    SENT=["positive","negative","mixed","neutral"]
    SYS=("You label Spotify reviews for a music-discovery study. Reply with ONE JSON object: "
         "discovery_subtheme (one of "+str(SUB)+"), sentiment (one of "+str(SENT)+"), pain_point "
         '(one short sentence or "none"). Judge only from the text.')
    def tag(t):
        r=client.chat.completions.create(model="llama-3.3-70b-versatile",max_tokens=300,temperature=0,
            response_format={"type":"json_object"},
            messages=[{"role":"system","content":SYS},{"role":"user","content":f'Review:\\n{t}'}])
        d=json.loads(r.choices[0].message.content); return d
    demo = disc.head(5).copy()   # tag 5 freshly-collected reviews live
    import time
    for _,row in demo.iterrows():
        out=tag(str(row["text"])[:400])
        print(f"[{out.get('discovery_subtheme')} | {out.get('sentiment')}] {str(row['text'])[:80]}")
        print("   pain:", out.get("pain_point")); time.sleep(2)'''))

cells.append(md(
"""## ✅ Done

You ran the full pipeline end-to-end: **live collection → live filtering →
AI tagging results → live charts → synthesized findings** — without needing any
API key. This mirrors the local Python pipeline in this repo
(`collect_spotify_reviews.py`, `tag_discovery_reviews_groq.py`,
`analyze_discovery_reviews.py`, `chart_discovery_reviews.py`)."""))

nb["cells"]=cells
nb["metadata"]={"colab":{"provenance":[],"toc_visible":True},
                "kernelspec":{"name":"python3","display_name":"Python 3"},
                "language_info":{"name":"python"}}
out="Spotify_Discovery_Pipeline_Colab.ipynb"
with open(out,"w",encoding="utf-8") as f:
    nbf.write(nb,f)
print("Wrote", out, "with", len(cells), "cells")
