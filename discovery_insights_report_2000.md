# Spotify Music Discovery — Findings

## Executive Summary

This study analyzed 753 user reviews of Spotify's music discovery features, revealing a complex landscape of user frustrations, goals, and unmet needs. The majority of users (60%) expressed negative sentiments, citing issues with ads, algorithm personalization, and limited free features. Despite these challenges, users seek to discover new music, enjoy seamless listening experiences, and have control over their playlists. Our findings highlight areas for improvement in Spotify's music discovery features.

## 1. Why do users struggle to discover new music?

Users struggle to discover new music due to various factors, including:

* Limited control over playlists and skipping songs (search_and_navigation cluster, 83% negative, n=134)
* Repetitive song playback, even with shuffle activated (repetition_filter_bubble cluster, 90% negative, n=62)
* Poor algorithm personalization, leading to irrelevant recommendations (algorithm_personalization cluster, 63% negative, n=41)
* Forced ads and premium features, disrupting the listening experience (catalog_availability cluster, 50% negative, n=70)

As one user noted, "I'm tired of these adds. I can't even select my favourite song after skipping 6 songs in 1 hour it aks for premium but remember spotify i will never take premium."

## 2. What are the most common frustrations with recommendations?

Users are frustrated with recommendations due to:

* Excessive ads and promotional content (recommendation_quality cluster, 41% negative, n=69)
* Poor song recommendations, with others finding them too repetitive or irrelevant (recommendation_quality cluster, 41% negative, n=69)
* Limited skips or inability to skip songs (repetition_filter_bubble cluster, 90% negative, n=62)
* Forced ads and premium features, disrupting the listening experience (catalog_availability cluster, 50% negative, n=70)

A user expressed their frustration with recommendations, saying, "Please STOP recommending other artists' songs to me, I ONLY listen to BTS Thank you."

## 3. What listening behaviors are users trying to achieve?

Users aim to:

* Discover new music and artists (discovery_features cluster, 67 reviews)
* Enjoy a seamless and uninterrupted listening experience (repetition_filter_bubble cluster, 62 reviews)
* Create and customize playlists that suit their mood and preferences (playlist_curation cluster, 72 reviews)
* Have control over their playlists, including skipping songs and choosing what to listen to (search_and_navigation cluster, 134 reviews)

As one user noted, "I love how I get to do my own music playlist!!"

## 4. What causes users to repeatedly listen to the same content?

Users repeatedly listen to the same content due to:

* Repetitive song playback, even with shuffle activated (repetition_filter_bubble cluster, 90% negative, n=62)
* Limited skips or inability to skip songs (repetition_filter_bubble cluster, 90% negative, n=62)
* Poor algorithm personalization, leading to irrelevant recommendations (algorithm_personalization cluster, 63% negative, n=41)
* Forced ads and premium features, disrupting the listening experience (catalog_availability cluster, 50% negative, n=70)

A user expressed their frustration with repetitive playback, saying, "it plays the same 100 songs they need to work on their rotation of songs that are played its a joke"

## 5. Which user segments experience different discovery challenges?

Different user segments experience different discovery challenges, including:

* Free-tier users, who face limitations in features and ads (catalog_availability cluster, 50% negative, n=70)
* Users with limited skips or inability to skip songs (repetition_filter_bubble cluster, 90% negative, n=62)
* Users with poor algorithm personalization, leading to irrelevant recommendations (algorithm_personalization cluster, 63% negative, n=41)
* Users seeking to discover new music and artists (discovery_features cluster, 67 reviews)

## 6. What unmet needs emerge consistently across reviews?

Consistent unmet needs across reviews include:

* More control over playlists and skipping songs (search_and_navigation cluster, 134 reviews)
* Improved algorithm personalization, leading to more accurate recommendations (algorithm_personalization cluster, 41 reviews)
* Reduced ads and promotional content (recommendation_quality cluster, 69 reviews)
* Better playlist management and song rotation (repetition_filter_bubble cluster, 62 reviews)
* More flexible skip and playback options for free users (other cluster, 238 reviews)

## Limitations

This study is limited by its single-source dataset from Google Play, which may not be representative of the broader user population. Additionally, the dataset is recent, and the findings may not generalize to users who have experienced different versions of the Spotify app. Furthermore, the dataset is English-language only, which may limit the generalizability of the findings to non-English speaking users.

---

## Appendix A — Exact Statistics

```
Total discovery reviews analyzed: 753

Sub-theme counts:
  other: 238 (32%)
  search_and_navigation: 134 (18%)
  playlist_curation: 72 (10%)
  catalog_availability: 70 (9%)
  recommendation_quality: 69 (9%)
  discovery_features: 67 (9%)
  repetition_filter_bubble: 62 (8%)
  algorithm_personalization: 41 (5%)

Sentiment overall:
  negative: 449 (60%)
  positive: 235 (31%)
  mixed: 63 (8%)
  neutral: 6 (1%)

% negative by sub-theme (which themes hurt most):
  repetition_filter_bubble: 90% negative (n=62)
  search_and_navigation: 83% negative (n=134)
  algorithm_personalization: 63% negative (n=41)
  other: 61% negative (n=238)
  catalog_availability: 50% negative (n=70)
  recommendation_quality: 41% negative (n=69)
  playlist_curation: 38% negative (n=72)
  discovery_features: 30% negative (n=67)

Rating segments: low (1-2 stars) = 364, mid (3) = 80, high (4-5 stars) = 309
  Top sub-themes among LOW-rating (frustrated) users:
    other: 128
    search_and_navigation: 86
    repetition_filter_bubble: 48
    catalog_availability: 28
  Top sub-themes among HIGH-rating (satisfied) users:
    other: 84
    playlist_curation: 47
    discovery_features: 47
    recommendation_quality: 44

Reviews mentioning free/ads/premium: 264 (35%) — a proxy for the free-tier segment.
```

## Appendix B — Per-Cluster Evidence

### Cluster: other (n=238)
**FRUSTRATIONS:**

- Crashing and freezing issues
- Annoying ads and ad repetition
- Limited skips and playback restrictions for free users
- Slow app performance and startup times
- Offline playback issues and data usage concerns

**GOALS:**

- Seamless music playback and discovery
- Ability to create and manage playlists without restrictions
- Ad-free listening experience
- Offline access to music and playlists
- Easy and efficient app performance

**UNMET NEEDS:**

- More flexible skip and playback options for free users
- Improved app stability and performance
- Reduced ad frequency and repetition
- Enhanced offline playback capabilities
- More control over data usage and storage

**QUOTES:**

- "it's Horrible. Ads everywhere, And now you have to pay to listen too songs on repeat, unless you have a huge budget income."
- "I'm tired of these adds. I can't even select my favourite song after skipping 6 songs in 1 hour it aks for premium but remember spotify i will never take premium."

### Cluster: search_and_navigation (n=134)
**FRUSTRATIONS:**

- The new update has caused various issues such as lag, freezing, and bugs.
- Users are frustrated with the lack of control over their playlists, including skipping songs and choosing what to listen to.
- The new widget design is problematic, with issues such as constant "offline" messages and unresponsive tapping.
- Users are annoyed with the ads in the free version and the limitations that come with it.

**GOALS:**

- Users want to be able to easily find and play their favorite songs and playlists.
- They want to be able to skip songs and choose what to listen to in their playlists.
- Users aim to have a seamless and lag-free listening experience.
- They want to be able to customize their playlists and have more control over their music.

**UNMET NEEDS:**

- Users wish for a more personalized search feature and the ability to choose what to listen to in their playlists.
- They want a more intuitive and user-friendly interface for editing playlists.
- Users desire a more consistent and reliable experience across different devices and platforms.
- They wish for more control over their music, including the ability to exclude certain songs from playlists.

**QUOTES:**

- "I don't know why but recently I have to keep uninstalling and then reinstall the app cuz I couldn't look at the Spotify it wouldn't show me my playlist it was like a black screen I don't know what's going on with your app and my phone is fine."
- "Spotify would be a five star app if the options and decisions for free users were expanded. We can't even pick what we want to listen to from our playlists and we only have a couple skips an hour."

### Cluster: playlist_curation (n=72)
**FRUSTRATIONS:**

- Users are frustrated with the inability to manually rearrange playlist order.
- They dislike the random addition of songs to their playlists.
- Some users experience issues with ads, playlist organization, and skipping songs.
- Others are unhappy with the limited functionality in the free version.

**GOALS:**

- Users want to create and customize playlists that suit their mood and preferences.
- They aim to listen to music in a specific order, without interruptions or random additions.
- Some users seek to discover new music through personalized playlists and recommendations.

**UNMET NEEDS:**

- Users wish for a higher song limit in playlists (up to 100,000 songs).
- They desire better playlist curation and organization options.
- Some users want to be able to choose which songs to play in a playlist, without ads or interruptions.

**QUOTES:**

- "man let us listen to our playlist in peace stop adding songs" (2*, negative)
- "I love how I get to do my own music playlist!!" (5*, positive)

### Cluster: catalog_availability (n=70)
**FRUSTRATIONS:**

- Limited music playback without Premium subscription
- Frequent ads disrupting the listening experience
- Music removal from playlists and library
- Difficulty in discovering new music due to AI-generated content

**GOALS:**

- Unlimited music playback without restrictions
- Ad-free listening experience
- Easy access to favorite songs and playlists
- Discovery of new music without AI-generated content

**UNMET NEEDS:**

- Clear labeling of AI-generated music
- Ability to filter out AI-generated music
- More transparent music licensing issues
- Romanized song titles and artist names for non-English songs

**QUOTES:**

1. "USELESS APP!! switching up to jiosaavn, there are so many problems! like after a couple of songs we cannot play our favourite song cuz we don't have "premium membership" like what is this app supposed to do,huh if it stops us from playing our favourite songs."
2. "I don't know where i would put this request, If possible give the title of the songs and the artist's name in Romanized form, for many Japanese songs for e.g. for Monogatari Series it is not in Romanized form, making it harder to search in Spotify."

### Cluster: recommendation_quality (n=69)
**FRUSTRATIONS:**
- Users are annoyed by excessive ads and promotional content.
- Some users experience poor song recommendations, with others finding them too repetitive or irrelevant.
- Users are frustrated with limitations in the free version, such as inability to play downloaded music without internet connection.

**GOALS:**
- Users want to discover new music and artists.
- They aim to enjoy a seamless music streaming experience with minimal interruptions.
- Users seek to customize their music experience, including removing unwanted recommendations.

**UNMET NEEDS:**
- Users wish for more control over ads and promotional content.
- They desire better song recommendation algorithms that cater to their individual tastes.
- Users want more flexibility in the free version, such as the ability to play downloaded music offline.

**QUOTES:**
- "Please STOP recommending other artists' songs to me, I ONLY listen to BTS Thank you" (4*, negative)
- "Spotify is an excellent music streaming app with a huge collection of songs and podcasts. The interface is easy to use, and the recommendations are very accurate." (5*, positive)

### Cluster: discovery_features (n=67)
**FRUSTRATIONS:**

- Random song additions without user interaction
- Annoying ads and limited free features
- Poor performance of song radios and offline listening
- Forced premium for essential features

**GOALS:**

- Discover new music and artists
- Create personalized playlists and mixes
- Enjoy high-quality sound and offline listening
- Explore various genres and moods

**UNMET NEEDS:**

- Option to remove or customize "smart shuffle" feature
- Ability to turn off AI-generated content in playlists
- More control over playlist organization and looping
- Better performance and reliability of song radios and offline listening

**QUOTES:**

- "I love the app, generally speaking. however, the absolute BS that is shuffle is ruining the app. You play a song that's been stuck in your head, but you don't like what it shuffled? too bad. you're stuck with it."
- "Money hungry app forces you to get premium just so you can turn off smart shuffle and actually play the songs you have in your playlist in order instead of playing songs that arent in your playlist"

### Cluster: repetition_filter_bubble (n=62)
**Sub-theme: repetition_filter_bubble (62 reviews)**

**FRUSTRATIONS:**
- Repetitive song playback, even with shuffle activated
- Limited skips or inability to skip songs
- Forced ads and premium features
- Poor playlist management and song rotation

**GOALS:**
- Listen to a diverse selection of songs from their playlists
- Enjoy a seamless and uninterrupted listening experience
- Discover new music without being forced to listen to ads or premium content

**UNMET NEEDS:**
- A more effective shuffle algorithm that doesn't repeat the same songs
- Increased skips or the ability to skip songs without restrictions
- Ad-free listening experience for free users
- Better playlist management and song rotation

**QUOTES:**
- "it plays the same 100 songs they need to work on their rotation of songs that are played its a joke" 
- "I want to listen to the songs on my playlist not recommendations. after all that's why I made a playlist of songs I want to hear."

### Cluster: algorithm_personalization (n=41)
**FRUSTRATIONS:**

- Users are frustrated with the algorithm's inability to understand their musical preferences.
- They experience issues with the shuffle feature, playlist refresh, and algorithm-driven recommendations.
- Some users are annoyed by ads, AI-driven content, and the promotion of sponsored recommendations.

**GOALS:**

- Users want to discover new music that matches their taste.
- They aim to enjoy seamless music streaming with minimal interruptions.
- Some users seek to maintain control over their listening experience, including the ability to block or remove unwanted content.

**UNMET NEEDS:**

- Users wish for a more accurate and personalized algorithm that understands their musical preferences.
- They desire better control over their listening experience, including the ability to exclude certain playlists or genres from metrics.
- Some users want to see improvements in the shuffle feature, playlist refresh, and overall app performance.

**QUOTES:**

1. "The algorithm is downright spooky with how well it nails my taste." (5*, positive)
2. "I used to really love this service, but the influx and subsequent promotion of ai slop is really disappointing." (1*, negative)
