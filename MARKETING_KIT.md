# 🚀 Open-Source Marketing Kit: `youtube-shorts-clipper`

Use this kit to distribute and announce **`youtube-shorts-clipper`** across developer and creator communities to earn GitHub stars, users, and contributors.

---

## 1. ⚙️ GitHub Repository Metadata (Do this first)

Go to **[github.com/rishijawale/youtube-shorts-clipper](https://github.com/rishijawale/youtube-shorts-clipper)** and click the **⚙️ (Edit repository details)** button next to "About":

* **Description**:
  ```text
  Free, local, open-source YouTube Shorts highlight clipper powered by viewer replay heatmaps, 9:16 vertical crop, and animated captions.
  ```
* **Website**:
  ```text
  https://github.com/rishijawale/youtube-shorts-clipper
  ```
* **Topics (paste and press enter for each)**:
  ```text
  youtube, youtube-shorts, ffmpeg, yt-dlp, opusclip-alternative, tiktok, reels, python, video-editing, highlight-detector, video-clipping, open-source
  ```

---

## 2. 🔴 Reddit Launch Posts

### Post A: For `r/selfhosted` & `r/opensource`
**Subreddits**: [r/selfhosted](https://reddit.com/r/selfhosted), [r/opensource](https://reddit.com/r/opensource)

**Title**:
> Tired of paying $20/mo for OpusClip? I made a free, local tool to clip YouTube Shorts using viewer replay heatmaps.

**Body**:
```markdown
Hey everyone,

I was frustrated with paid SaaS video clippers (Opus Clip, Klap, etc.) that charge $20 to $50 a month, limit your monthly processing minutes, put watermarks on free tiers, and often guess random moments using hallucinated LLM hooks.

So I built **YouTube Shorts Highlight Clipper** — a completely free, local, open-source tool.

### How it works:
1. **Replay Heatmap Detection**: Instead of guessing where the "hook" is, it queries YouTube's official **"Most Replayed"** heatmap metrics via `yt-dlp` to pinpoint the exact timestamps where real viewers rewound and replayed the most.
2. **Shorts 9:16 Vertical Formatting**: Automatically renders 1080x1920 vertical video using FFmpeg with either a blurred widescreen backdrop or center crop.
3. **High-Contrast Subtitles**: Parses the subtitles, chunks speech into punchy 2-4 word viral phrases, and burns in bold yellow/black outlined captions.
4. **Hardware NVENC GPU Acceleration**: Fast rendering using your local NVIDIA GPU.
5. **No API keys or cloud accounts needed**: Runs 100% locally on your computer.

It includes an interactive `.bat` launcher for Windows as well as a clean Python CLI for Linux/macOS.

Check it out on GitHub:
👉 https://github.com/rishijawale/youtube-shorts-clipper

Would love your feedback, feature ideas, or PRs!
```

---

### Post B: For `r/Python`
**Subreddit**: [r/Python](https://reddit.com/r/Python)

**Title**:
> I built an open-source tool that clips high-engagement YouTube Shorts using viewer heatmaps and FFmpeg [Code on GitHub]

**Body**:
```markdown
Hi all!

I wanted to share a project I built: **YouTube Shorts Highlight Clipper**.

It automates the tedious pipeline of turning long YouTube videos into ready-to-upload YouTube Shorts / TikToks / Reels without using paid cloud APIs.

### Technical highlights:
- **Heatmap Parsing**: Analyzes the 100-point engagement graph returned by `yt-dlp` to detect local peak intensity derivatives while ignoring early load bias.
- **Dynamic ASS Subtitle Engine**: Converts VTT transcripts into styled Advanced SubStation Alpha (`.ass`) events with safe-zone margins and word-by-word chunking.
- **FFmpeg Filtergraph**: Multi-layered split filtergraph for blurred background scaling, cropping, overlaying, and burning captions.
- **GPU Encoding**: Probes for `h264_nvenc` availability and falls back to `libx264`.

GitHub: https://github.com/rishijawale/youtube-shorts-clipper

I’d appreciate any feedback on the codebase or contributions!
```

---

### Post C: For `r/NewTubers` & `r/youtubers`
**Subreddits**: [r/NewTubers](https://reddit.com/r/NewTubers), [r/youtubers](https://reddit.com/r/youtubers)

**Title**:
> Made a 100% free desktop tool to turn your long YouTube videos into Shorts (no subscription / no watermarks)

**Body**:
```markdown
Hey creators,

Repurposing long videos or podcast streams into Shorts/Reels usually requires either hours of manual editing or paying $20–$40 every month for tools like OpusClip or Munch.

I built a free tool you can run directly on your own computer:

- It finds your video's "Most Replayed" moments automatically (using the actual audience engagement graph).
- Clips a 30–60 second highlight.
- Formats it to vertical 9:16 (blurred backdrop or cropped).
- Generates bold yellow Shorts-style captions.
- Completely free and open-source, no watermarks, unlimited videos.

For Windows users, there is a simple double-click file where you just paste your link and hit Enter.

Repo link: https://github.com/rishijawale/youtube-shorts-clipper

Hope this saves you time and money on your channel!
```

---

## 3. 🟠 Hacker News (Show HN)

Submit at **[news.ycombinator.com/show](https://news.ycombinator.com/show)**:

**Title**:
> Show HN: YouTube Shorts Clipper – Free, local tool to clip videos based on heatmaps

**Text**:
```text
I built YouTube Shorts Clipper, an open-source tool that automatically clips highlight moments from long YouTube videos and converts them into 9:16 vertical video with styled captions.

Instead of running heavy LLM prompts to guess highlights, it uses YouTube’s native 100-point viewer replay heatmap via yt-dlp to find the moments viewers actually rewatched the most.

Features:
- 1080x1920 vertical video with blurred background or center crop
- Chunked viral captions burned into safe zones via FFmpeg libass
- Fast local NVIDIA NVENC encoding
- Zero subscriptions, accounts, or API keys

Repo: https://github.com/rishijawale/youtube-shorts-clipper

I’d love to hear your thoughts and suggestions!
```

---

## 4. 🐦 X (Twitter) & LinkedIn Post

### X / Twitter Post:
```text
Why pay $30/mo for AI clipping tools with minute limits? ✂️

I built an open-source tool that turns long YouTube videos into ready-to-post Shorts & Reels:

🔥 Uses YouTube's real "Most Replayed" heatmap
📐 9:16 vertical crop + blurred background
💬 Auto-generates styled yellow captions
⚡ 100% Free, local & GPU-accelerated

GitHub (Star ⭐ if you like it):
https://github.com/rishijawale/youtube-shorts-clipper

#Python #OpenSource #FFmpeg #BuildInPublic #YouTubeShorts
```

---

## 5. 🌐 List on AlternativeTo

Submit your project to **[AlternativeTo.net](https://alternativeto.net/software/new/)**:
* **Name**: YouTube Shorts Highlight Clipper
* **Category**: Video Editing / Video Conversion
* **License**: Open Source (MIT)
* **Platforms**: Windows, macOS, Linux
* **Alternative to**: Opus Clip, Klap, Vidyo.ai, Munch
