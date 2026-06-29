# How the Review Discovery Engine Works (in plain English)

Think of it as a **research assistant that reads thousands of Spotify reviews
for you and tells you what people are complaining about** — automatically, in
minutes instead of weeks.

## The big picture

Imagine you hired an intern to read every Spotify review, highlight the ones
about *finding new music*, sort them into buckets, and write you a summary.
This project is that intern — but automated.

## The 5 steps

### 1. Gather the reviews (Collect)
The tool pulls recent Spotify reviews from the Google Play Store and Apple App
Store — about 1,800 of them — into one big list, along with each review's star
rating and date. (Like copy-pasting every review into one notebook.)

### 2. Keep only the relevant ones (Filter)
Most reviews are about random things ("app crashes," "love it!"). The tool keeps
only reviews that mention music *discovery* — words like "recommend," "discover,"
"same songs," "playlist," "shuffle." That narrows ~1,800 down to ~160 reviews
that actually matter for the question.

### 3. Read and label each one (AI Tagging) — *the "AI" part*
Each surviving review is handed to an AI language model (Llama, running free on
Groq). For every review, the AI answers three questions:
- **What's this about?** → a category, like "repetition" or "bad recommendations"
- **How does this person feel?** → positive, negative, or mixed
- **What's the core complaint?** → one short sentence

So a messy review like *"ugh the shuffle just plays the same 20 songs over and
over"* becomes a neat row: **topic = repetition, feeling = negative,
complaint = "shuffle isn't random."** It's like the AI puts a highlighter and a
sticky note on every review.

### 4. Find the patterns (Synthesize)
With every review labeled, the tool steps back and looks at the whole pile. It
groups reviews by topic, counts them, and asks the AI to write up the findings —
answering questions like *"Why do people struggle to discover music?"* with
evidence and real quotes. This becomes the findings report.

### 5. Draw the pictures (Charts) + save (Excel)
Finally it makes simple bar charts (which complaints are most common, which are
most negative) and saves everything into an Excel file and a report.

## Why it's useful
A human reading 1,800 reviews is slow, gets tired, and misses patterns. This
pipeline does it consistently and fast, and turns vague griping into
**countable insights** — e.g., "100% of reviews about repetition are negative,"
or "the biggest unmet need is real playback control, not better algorithms."

## The one-sentence version
> It **collects** Spotify reviews, **filters** to the ones about discovering
> music, uses **AI to label** each one (topic + feeling + complaint), then
> **summarizes** the patterns into a report and charts.

## A fair caveat (its limits)
It's only as good as the reviews it reads — these came mostly from Google Play,
are recent, and are in English. So it's a sharp **snapshot**, not the complete
global picture. And the AI labels are very good but not perfect — like a smart
intern who occasionally miscategorizes one.
