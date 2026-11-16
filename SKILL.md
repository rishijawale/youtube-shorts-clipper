---
name: youtube-shorts-clipper
description: Automatically clip YouTube videos into 9:16 vertical Shorts based on viewer replay heatmaps and engagement spikes, with stylish burned-in captions and high quality rendering.
---

# YouTube Shorts Highlight Clipper

This skill extracts the most replayed and engaging highlight moments from YouTube videos based on YouTube's "Most Replayed" viewer interaction heatmap data and converts them into YouTube Shorts (1080x1920 vertical video) with high-contrast, animated-style captions.

## How It Works

1. **Viewer Heatmap & Spike Detection**:
   - Queries YouTube's "Most Replayed" engagement graph using `yt-dlp`.
   - Locates local peaks and high-engagement retention spikes where viewers replayed or rewound the most.
   - Calculates the optimal video clip window around the spike (with contextual build-up and reaction).

2. **Format Conversion (1080×1920 9:16 Vertical)**:
   - **`blur` (Default & Recommended)**: Blurred 9:16 zoomed background with centered crisp original 16:9 video. Perfect for widescreen podcasts, gaming, and reaction videos.
   - **`crop`**: Direct center 9:16 crop for single-subject/vlog style.
   - **`fit`**: Letterboxed with black padding.

3. **Shorts-Style Captions**:
   - Downloads subtitle tracks (manual or auto-generated English/multilingual).
   - Chunks dialogue into punchy 2-4 word phrases.
   - Formats into Advanced SubStation Alpha (`.ass`) with bold yellow lettering (`Impact`/`Arial Black`), deep black stroke outline, drop shadow, and safe-zone vertical margin.
   - Burns captions cleanly into the video stream using FFmpeg `libass`.

4. **Hardware-Accelerated Encoding**:
   - Uses `h264_nvenc` (NVIDIA GPU hardware encoder) for fast rendering, or falls back to `libx264`.

---

## Quick Usage

Run the clipper script via Python:

```bash
python scripts\clipper.py "<YOUTUBE_URL>" [options]
```

### Options

| Flag | Default | Description |
|---|---|---|
| `--duration <sec>` | `45.0` | Target clip duration (15 to 60 seconds). |
| `--top-n <count>` | `1` | Number of highlight clips to generate from top spikes. |
| `--mode <blur\|crop\|fit>` | `blur` | Vertical framing layout (`blur`, `crop`, or `fit`). |
| `--output-dir <path>` | `./output` | Destination folder for the exported Shorts. |
| `--no-captions` | `False` | Disable caption burning. |
| `--start <sec>` | `None` | Manually specify clip start timestamp. |
| `--end <sec>` | `None` | Manually specify clip end timestamp. |

---

## Example Commands

### 1. Clip Top Highlight with Blurred Background & Captions (30 seconds)
```bash
python scripts\clipper.py "https://www.youtube.com/watch?v=VIDEO_ID" --duration 30 --mode blur
```

### 2. Clip Top 3 Highlights from a Podcast or Long Stream
```bash
python scripts\clipper.py "https://www.youtube.com/watch?v=VIDEO_ID" --top-n 3 --duration 45
```

### 3. Center Crop Format (e.g. for vlogs or single-speaker videos)
```bash
python scripts\clipper.py "https://www.youtube.com/watch?v=VIDEO_ID" --mode crop --duration 40
```
