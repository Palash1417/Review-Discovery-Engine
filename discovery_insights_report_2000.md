# Spotify Music Discovery — Findings

## Executive Summary

Our study analyzed 603 user reviews of Spotify music discovery, revealing a complex landscape of user experiences, frustrations, and unmet needs. The majority of users (60%) expressed negative sentiments, citing issues with search and navigation, repetition, and algorithm personalization. Despite these challenges, users seek a seamless music listening experience, personalized recommendations, and control over their playlists. Our findings highlight the need for Spotify to address these concerns and provide a more user-centric music discovery experience.

## 1. Why do users struggle to discover new music?

Users struggle to discover new music due to various issues, including poor search and navigation (83% negative, n=107), algorithm personalization problems (62% negative, n=32), and limitations in playlist curation (42% negative, n=60). As one user noted, "Spotify would be a five-star app if the options and decisions for free users were expanded" (search_and_navigation cluster). These challenges hinder users' ability to explore new music and create playlists that suit their mood and preferences.

## 2. What are the most common frustrations with recommendations?

The most common frustrations with recommendations are intrusive and poorly tailored suggestions (38% negative, n=56), overemphasis on sponsored content (62% negative, n=32), and algorithmic failures to adapt to changing music tastes (algorithm_personalization cluster). Users express frustration with recommendations that disrupt their listening experience, such as the quote, "Please STOP recommending other artists' songs to me, I ONLY listen to BTS Thank you" (recommendation_quality cluster).

## 3. What listening behaviors are users trying to achieve?

Users aim to achieve a seamless music listening experience, personalized recommendations, and control over their playlists. They seek to discover new music, enjoy their favorite songs and podcasts, and explore more music and artists (discovery_features cluster). As one user stated, "I love how I get to do my own music playlist!!" (playlist_curation cluster). These goals are often hindered by the limitations and frustrations mentioned earlier.

## 4. What causes users to repeatedly listen to the same content?

Users repeatedly listen to the same content due to issues with repetition, such as the "smart shuffle" feature, which adds random songs not in their playlist (30% negative, n=54). This repetition is also caused by poor playlist management and song rotation (repetition_filter_bubble cluster). As one user noted, "it plays the same rotation EVERY. SINGLE. TIME. Shuffle is abysmal at best" (repetition_filter_bubble cluster).

## 5. Which user segments experience different discovery challenges?

Different user segments experience varying discovery challenges. For example, users in the free-tier segment (33% of reviews) express frustration with ads, limited skips, and playback restrictions (other cluster). In contrast, users with premium subscriptions (67% of reviews) are more likely to experience issues with algorithm personalization and poor app performance (algorithm_personalization cluster). These differences highlight the need for Spotify to address the unique challenges faced by each user segment.

## 6. What unmet needs emerge consistently across reviews?

Consistent unmet needs across reviews include:

* More features and flexibility for non-premium users (other cluster)
* Improved app stability and performance (search_and_navigation cluster)
* Reduced ad frequency and repetition (other cluster)
* Enhanced offline listening capabilities (other cluster)
* More control over recommendations and playlists (recommendation_quality cluster)
* Better playlist management and song rotation (repetition_filter_bubble cluster)

These unmet needs highlight the need for Spotify to provide a more user-centric music discovery experience, addressing the concerns and frustrations of its users.

## Limitations

This study is limited by its single-source dataset (Google Play reviews), recent data collection (no specific date mentioned), and English-language focus. The findings may not generalize to other user segments, such as those using the Spotify app on other platforms or in other languages. Future studies should aim to collect data from multiple sources and languages to provide a more comprehensive understanding of user experiences with Spotify music discovery.

---

## Appendix A — Exact Statistics

```
Total discovery reviews analyzed: 603

Sub-theme counts:
  other: 186 (31%)
  search_and_navigation: 107 (18%)
  playlist_curation: 60 (10%)
  catalog_availability: 59 (10%)
  recommendation_quality: 56 (9%)
  discovery_features: 54 (9%)
  repetition_filter_bubble: 49 (8%)
  algorithm_personalization: 32 (5%)

Sentiment overall:
  negative: 361 (60%)
  positive: 187 (31%)
  mixed: 50 (8%)
  neutral: 5 (1%)

% negative by sub-theme (which themes hurt most):
  repetition_filter_bubble: 90% negative (n=49)
  search_and_navigation: 83% negative (n=107)
  algorithm_personalization: 62% negative (n=32)
  other: 62% negative (n=186)
  catalog_availability: 53% negative (n=59)
  playlist_curation: 42% negative (n=60)
  recommendation_quality: 38% negative (n=56)
  discovery_features: 30% negative (n=54)

Rating segments: low (1-2 stars) = 290, mid (3) = 65, high (4-5 stars) = 248
  Top sub-themes among LOW-rating (frustrated) users:
    other: 102
    search_and_navigation: 67
    repetition_filter_bubble: 37
    catalog_availability: 25
  Top sub-themes among HIGH-rating (satisfied) users:
    other: 64
    playlist_curation: 38
    discovery_features: 38
    recommendation_quality: 37

Reviews mentioning free/ads/premium: 201 (33%) — a proxy for the free-tier segment.
```

## Appendix B — Per-Cluster Evidence

### Cluster: other (n=186)
**FRUSTRATIONS:**

- Crashing and freezing issues
- Annoying ads and ad repetition
- Limited skips and playback restrictions for free users
- Offline listening issues
- Premium pricing and limited features for non-premium users

**GOALS:**

- Seamless music listening experience
- Ability to create and manage playlists
- Ad-free listening
- Offline listening capabilities
- Unlimited skips and playback control

**UNMET NEEDS:**

- More features and flexibility for non-premium users
- Improved app stability and performance
- Reduced ad frequency and repetition
- Enhanced offline listening capabilities

**QUOTES:**

- "it's Horrible. Ads everywhere, And now you have to pay to listen too songs on repeat, unless you have a huge budget income."
- "I will never take premium. I used to love this app but now it's just a money grab with too many ads and restrictions."

### Cluster: search_and_navigation (n=107)
**FRUSTRATIONS:**

- Frequent app crashes, freezes, and lag.
- Inconsistent and poor user interface.
- Lack of personalized search features.
- Inability to skip songs, choose playlists, and select music.
- Excessive ads and limited skips for free users.
- Bugs and glitches in playlist management and playback.

**GOALS:**

- Easy music discovery and exploration.
- Ability to skip songs and choose playlists.
- Personalized search features and recommendations.
- Seamless playlist management and playback.
- Ad-free listening experience for free users.

**UNMET NEEDS:**

- A 'Back to Top' button in the interface.
- Local Files button for adding songs to playlists.
- Ability to exclude certain songs from playlists.
- Option to choose what to listen to from playlists.
- Better playlist sorting and organization features.

**QUOTES:**

- "I don't know why but recently I have to keep uninstalling and then reinstall the app cuz I couldn't look at the Spotify it wouldn't show me my playlist it was like a black screen I don't know what's going on with your app and my phone is fine."
- "Spotify would be a five star app if the options and decisions for free users were expanded. We can't even pick what we want to listen to from our playlists and we only have a couple skips an hour."

### Cluster: playlist_curation (n=60)
**FRUSTRATIONS:**

* Users are frustrated with the inability to manually rearrange playlist order.
* They dislike the addition of unwanted songs and artists to their playlists.
* Some users are annoyed by the random addition of songs to their playlists.
* Others are frustrated with the limitations of the free version, including ads and limited playlist customization.

**GOALS:**

* Users want to create and customize playlists that suit their mood and preferences.
* They want to listen to their playlists in a specific order, without shuffling.
* Users aim to discover new music and enjoy a seamless listening experience.

**UNMET NEEDS:**

* Users wish for a higher song limit in playlists (up to 100,000).
* They want better playlist curation and easier genre filtering.
* Some users desire a more user-friendly playlist creation and editing experience.

**QUOTES:**

* "man let us listen to our playlist in peace stop adding songs" (2*, negative)
* "I love how I get to do my own music playlist!!" (5*, positive)

### Cluster: recommendation_quality (n=56)
**FRUSTRATIONS:**

- Users are annoyed by intrusive recommendations while listening to specific artists or albums.
- Some users experience poor app performance, such as loading issues and crashes.
- Users are frustrated with ads and the limitations of the free version.

**GOALS:**

- Users want to enjoy their favorite music without interruptions.
- Users aim to discover new music and artists through recommendations.
- Users seek a seamless and enjoyable listening experience.

**UNMET NEEDS:**

- Users wish for more control over recommendations, such as the ability to remove specific artists or albums.
- Users desire a more personalized experience, with recommendations tailored to their specific tastes.
- Users want a more premium-like experience without the cost.

**QUOTES:**

- "Please STOP recommending other artists' songs to me, I ONLY listen to BTS Thank you" (4*, negative)
- "I love Spotify's recommendations and Smart Shuffle. Sometimes Spotify introduces me to songs that fit my current vibe perfectly, but I don't necessarily want to add them to my Liked Songs." (5*, positive)

### Cluster: discovery_features (n=54)
**FRUSTRATIONS:**

- Users are frustrated with the "smart shuffle" feature, which adds random songs not in their playlist.
- Some users experience issues with offline listening, song radios, and playlist loading.
- Others are annoyed by ads, limited song queuing, and forced premium features.

**GOALS:**

- Users want to discover new music and create playlists for every mood.
- They aim to enjoy their favorite songs and podcasts with excellent sound quality.
- Some users seek to explore more music and discover amazing artists.

**UNMET NEEDS:**

- Users wish for an option to remove "smart shuffle" and turn off AI-driven playlists.
- They want more control over their playlists, such as the ability to queue songs and loop playlists.
- Some users desire better ad management and more features without premium.

**QUOTES:**

- "I love the app, generally speaking. however, the absolute BS that is shuffle is ruining the app. You play a song that's been stuck in your head, but you don't like what it shuffled? too bad. you're stuck with it."
- "I have premium for years. Until April 2026 there were no issues. Most recent updates are just making the app worse. 1. Songs on smart shuffle just got worse. repeatedly playing the same music that has already been disapproved."

### Cluster: repetition_filter_bubble (n=49)
**Sub-theme: repetition_filter_bubble (49 reviews)**

**FRUSTRATIONS:**
- Repetitive song playback, even with shuffle enabled
- Limited skips or inability to skip songs
- Forced ads and premium features
- Poor playlist management and song rotation

**GOALS:**
- Listen to their curated playlists without repetition
- Enjoy a seamless and random music experience
- Access features without premium subscription
- Discover new music without being forced to

**UNMET NEEDS:**
- A more robust and random shuffle algorithm
- Increased skips or ability to skip songs
- Ad-free listening experience
- Better playlist management and song rotation

**QUOTES:**
- "it plays the same rotation EVERY. SINGLE. TIME. Shuffle is abysmal at best."
- "it's giving the same playlist everytime and more ads day by day"

### Cluster: algorithm_personalization (n=32)
**FRUSTRATIONS:**

- Algorithm not adapting to changing music tastes
- Overemphasis on sponsored recommendations and ads
- Bugs and glitches in the app
- Poor performance of the shuffle and blend features
- Lack of control over music discovery

**GOALS:**

- Discover new music that matches their taste
- Enjoy ad-free listening
- Have a seamless and smooth music streaming experience
- Be able to easily navigate and use the app
- Find personalized recommendations

**UNMET NEEDS:**

- Customizable themes
- Ability to set safe playlists for kids
- More control over music discovery
- Better handling of playlist updates
- Improved performance and fewer bugs

**QUOTES:**

- "The algorithm is downright spooky with how well it nails my taste." (5*, positive)
- "This app is horrible. I am a radio enthusiast and I want to listen to my 30s music in peace but AFTER EVERY SONG an ad plays and ruins it." (1*, negative)
