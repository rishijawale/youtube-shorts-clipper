# 🎬 YouTube Shorts Highlight Clipper

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FFmpeg Supported](https://img.shields.io/badge/FFmpeg-NVENC%20%2F%20x264-red.svg)](https://ffmpeg.org/)
[![YouTube Most Replayed](https://img.shields.io/badge/Detection-Viewer%20Heatmap-FF0000.svg)](https://github.com/yt-dlp/yt-dlp)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/rishijawale/youtube-shorts-clipper/pulls)

An open-source CLI tool and agent skill that automatically detects highlight moments in YouTube videos based on viewer replay heatmaps and engagement spikes, converts them into 9:16 vertical video (1080x1920 Full HD), and burns in high-contrast Shorts-style subtitles.

---

## ⚡ Why YouTube Shorts Clipper vs Paid SaaS?

| Feature | Paid SaaS (Opus Clip, Klap, Vidyo) | **YouTube Shorts Clipper** |
|:---|:---:|:---:|
| **Cost** | \$15 – \$50 / month | **100% Free & Open-Source** |
| **Video Processing Limits** | Capped minutes per month | **Unlimited** |
| **Data Privacy** | Cloud uploads / server storage | **Runs 100% Locally on your PC** |
| **Highlight Detection** | AI guesswork / hallucinated hooks | **YouTube's real viewer replay heatmap** |
| **Watermarks** | Yes (on free/cheap tiers) | **Never** |
| **Speed** | Cloud queue wait times | **Instant local GPU (NVIDIA NVENC)** |
| **API Keys Required** | Yes (OpenAI / proprietary credits) | **None required** |

---

## ✨ Features

- 🔥 **Automated Highlight Detection**: Leverages YouTube's official **"Most Replayed"** heatmap metrics to extract the exact timestamps where viewers replayed or rewound the most.
- 📐 **9:16 Vertical Framing**:
  - `blur` *(Default)*: Crisp centered 16:9 widescreen video with a dynamically blurred, zoomed background (ideal for podcasts, gameplay, and streams).
  - `crop`: Direct center crop for portrait-style focus.
  - `fit`: Clean letterbox framing.
- 💬 **Dynamic High-Contrast Captions**:
  - Downloads YouTube auto-generated or manual subtitles.
  - Chunks speech into punchy 2–4 word viral captions (TikTok/Shorts retention style).
  - High-visibility yellow lettering with heavy black outline and drop shadow placed safely above YouTube Shorts navigation controls.
- ⚡ **Hardware Accelerated Encoding**: Auto-detects NVIDIA NVENC (`h264_nvenc`) for blazing fast exports, falling back cleanly to `libx264`.

---

## 🛠️ Architecture

```
YouTube URL ──► yt-dlp Metadata & Heatmap ──► Peak Detection Algorithm
                                                        │
                      ┌─────────────────────────────────┴─────────────────────────────────┐
                      ▼                                                                   ▼
       Download Video Segment (yt-dlp)                                     Fetch & Chunk Subtitles (VTT)
                      │                                                                   │
                      └─────────────────────────────────┬─────────────────────────────────┘
                                                        ▼
                                       FFmpeg Filtergraph (9:16 Crop + Blur)
                                                        │
                                            Burn-in ASS Captions
                                                        │
                                         GPU NVENC / H.264 Encoder
                                                        │
                                                        ▼
                                       Exported YouTube Short (.mp4)
```

---

## 📦 Prerequisites

1. **Python 3.8+**
2. **FFmpeg** installed and accessible via system `PATH`.
   - Windows: `winget install Gyan.FFmpeg`
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`
3. **yt-dlp** (installed via requirements)

---

## 🚀 Installation

```bash
git clone https://github.com/rishijawale/youtube-shorts-clipper.git
cd youtube-shorts-clipper
pip install -r requirements.txt
```

---

## 💻 Usage

Run the clipper directly via Python:

```bash
python scripts/clipper.py "<YOUTUBE_URL>" [options]
```

### Options & Arguments

| Parameter | Type | Default | Description |
|---|---|---|---|
| `url` | Positional | *Required* | YouTube video URL |
| `--duration` | Float | `45.0` | Target clip duration in seconds (15 to 60s) |
| `--top-n` | Int | `1` | Number of top highlight peaks to export |
| `--mode` | Choice | `blur` | Framing mode: `blur`, `crop`, or `fit` |
| `--output-dir` | String | `./output` | Destination directory for exported clips |
| `--no-captions` | Flag | `False` | Disable subtitle extraction and burn-in |
| `--start` | Float | `None` | Manually override start timestamp (seconds) |
| `--end` | Float | `None` | Manually override end timestamp (seconds) |

---

## 💡 Examples

### Clip Top Highlight with Blurred Background (30 seconds)
```bash
python scripts/clipper.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --duration 30 --mode blur
```

### Generate Top 3 Highlights from a Long Video
```bash
python scripts/clipper.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --top-n 3 --duration 45
```

### Direct Vertical Center Crop
```bash
python scripts/clipper.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --mode crop --duration 40
```

---

## ❓ Frequently Asked Questions (FAQ)

#### Do I need a YouTube API key?
**No.** The tool extracts heatmap data and metadata without requiring Google Cloud or YouTube API keys.

#### Does it work on Mac and Linux?
**Yes.** While a `.bat` launcher is provided for Windows, the Python core (`scripts/clipper.py`) works identically on macOS and Linux.

#### What if a video doesn't have subtitles?
If manual or auto-generated YouTube subtitles are not enabled on the video, the tool clips the highlight video cleanly and alerts you.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to open an issue or submit a Pull Request.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
