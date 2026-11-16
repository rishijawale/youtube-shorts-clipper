#!/usr/bin/env python3
"""
YouTube Shorts Highlight Clipper
Automatically detects viewer replay heatmap peaks or audio energy spikes,
clips the highlight moment, formats into 9:16 vertical video (1080x1920),
and burns in high-contrast Shorts-style subtitles (via YouTube VTT or local faster-whisper AI).
"""

import os
import sys
import json
import re
import math
import argparse
import subprocess
from pathlib import Path

def run_cmd(cmd, check=True, capture=True, cwd=None):
    """Run system command and return output."""
    res = subprocess.run(cmd, stdout=subprocess.PIPE if capture else None,
                         stderr=subprocess.PIPE if capture else None,
                         text=True, encoding="utf-8", errors="replace", cwd=cwd)
    if check and res.returncode != 0:
        err = res.stderr if capture else "Command failed"
        raise RuntimeError(f"Command failed ({res.returncode}): {' '.join(cmd)}\n{err}")
    return res

def check_nvenc():
    """Check if h264_nvenc actually initializes with current Nvidia driver."""
    try:
        cmd = ["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=c=black:s=64x64:d=0.1", "-c:v", "h264_nvenc", "-f", "null", "-"]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return res.returncode == 0
    except Exception:
        return False

def get_video_info(url):
    """Extract metadata, duration, heatmap and subtitle info using yt-dlp."""
    print(f"[*] Fetching metadata and heatmap from: {url}")
    cmd = [
        "yt-dlp",
        "--dump-single-json",
        "--skip-download",
        "--no-warnings",
        url
    ]
    res = run_cmd(cmd)
    try:
        data = json.loads(res.stdout)
        return data
    except Exception as e:
        raise ValueError(f"Failed to parse yt-dlp JSON output: {e}")

def find_audio_spikes(url, total_duration, clip_duration=45.0, top_n=1, temp_dir="./temp"):
    """
    Fallback when heatmap is unavailable:
    Downloads low-bitrate audio, decodes via FFmpeg to raw PCM,
    and analyzes RMS energy to detect excitement/screaming/action peaks.
    """
    import numpy as np
    os.makedirs(temp_dir, exist_ok=True)
    temp_audio = os.path.join(temp_dir, "temp_probe_audio.m4a")

    print("[*] Heatmap unavailable. Scanning audio energy spikes (reactions/hype)...")
    if os.path.exists(temp_audio):
        try:
            os.remove(temp_audio)
        except Exception:
            pass

    dl_cmd = [
        "yt-dlp",
        "-f", "139/249/ba[abr<70]/ba",
        "-o", temp_audio,
        "--no-warnings",
        url
    ]
    run_cmd(dl_cmd)

    found_files = list(Path(temp_dir).glob("temp_probe_audio*"))
    if not found_files:
        raise FileNotFoundError("Audio probe file could not be downloaded")
    audio_file = str(found_files[0])

    sr = 16000
    ff_cmd = ["ffmpeg", "-v", "error", "-i", audio_file, "-f", "s16le", "-ac", "1", "-ar", str(sr), "-"]
    proc = subprocess.run(ff_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    raw = np.frombuffer(proc.stdout, dtype=np.int16)

    try:
        os.remove(audio_file)
    except Exception:
        pass

    if len(raw) == 0:
        return []

    num_secs = len(raw) // sr
    rms = np.zeros(num_secs, dtype=np.float32)
    for i in range(num_secs):
        chunk = raw[i * sr : (i + 1) * sr].astype(np.float32)
        rms[i] = np.sqrt(np.mean(chunk**2))

    intro_cutoff = min(30, int(total_duration * 0.05))
    rms[:intro_cutoff] = 0

    sorted_indices = np.argsort(rms)[::-1]

    spikes = []
    for idx in sorted_indices:
        peak_time = float(idx)
        peak_val = float(rms[idx])

        if any(abs(peak_time - s["peak_time"]) < clip_duration * 0.8 for s in spikes):
            continue

        start_t = max(0.0, peak_time - (clip_duration * 0.50))
        end_t = min(total_duration, start_t + clip_duration)
        if (end_t - start_t) < clip_duration and start_t > 0:
            start_t = max(0.0, end_t - clip_duration)

        spikes.append({
            "peak_time": peak_time,
            "peak_val": peak_val / (np.max(rms) + 1e-6),
            "start_time": start_t,
            "end_time": end_t,
            "duration": end_t - start_t
        })
        if len(spikes) >= top_n:
            break

    return spikes

def find_heatmap_spikes(heatmap, total_duration, clip_duration=45.0, top_n=1):
    """
    Analyze YouTube's 'Most Replayed' heatmap data to find local peaks.
    Avoids the initial 0-10% of the video if it's artificially high due to intro loads.
    """
    if not heatmap or len(heatmap) < 5:
        return []

    points = []
    for item in heatmap:
        st = float(item.get("start_time", 0))
        et = float(item.get("end_time", st + 1))
        val = float(item.get("value", 0))
        mid = (st + et) / 2.0
        points.append((mid, val, st, et))

    cutoff_time = min(15.0, total_duration * 0.05) if total_duration > 60 else 0
    valid_points = [p for p in points if p[0] >= cutoff_time]
    if not valid_points:
        valid_points = points

    peaks = []
    n = len(valid_points)
    for i in range(1, n - 1):
        prev_val = valid_points[i - 1][1]
        curr_val = valid_points[i][1]
        next_val = valid_points[i + 1][1]
        if curr_val >= prev_val and curr_val >= next_val and curr_val > 0.05:
            peaks.append(valid_points[i])

    if not peaks:
        peaks = sorted(valid_points, key=lambda x: x[1], reverse=True)[:5]

    peaks = sorted(peaks, key=lambda x: x[1], reverse=True)

    selected_spikes = []
    for p in peaks:
        peak_time = p[0]
        peak_val = p[1]
        if any(abs(peak_time - s["peak_time"]) < clip_duration * 0.8 for s in selected_spikes):
            continue

        start_t = max(0.0, peak_time - (clip_duration * 0.55))
        end_t = min(total_duration, start_t + clip_duration)
        if (end_t - start_t) < clip_duration and start_t > 0:
            start_t = max(0.0, end_t - clip_duration)

        selected_spikes.append({
            "peak_time": peak_time,
            "peak_val": peak_val,
            "start_time": start_t,
            "end_time": end_t,
            "duration": end_t - start_t
        })
        if len(selected_spikes) >= top_n:
            break

    return selected_spikes

def parse_vtt_timestamp(ts_str):
    """Convert VTT timestamp (HH:MM:SS.mmm or MM:SS.mmm) to seconds."""
    parts = ts_str.strip().split(":")
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)
    elif len(parts) == 2:
        m, s = parts
        return int(m) * 60 + float(s)
    return float(ts_str)

def format_ass_timestamp(seconds):
    """Format seconds into ASS timestamp H:MM:SS.cc"""
    if seconds < 0:
        seconds = 0
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def clean_vtt_text(text):
    """Remove HTML/VTT tags and styling."""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    return text.strip()

def convert_vtt_to_shorts_ass(vtt_path, ass_path, clip_start, clip_end):
    """
    Parse VTT subtitles, slice to [clip_start, clip_end], chunk into punchy
    Shorts-style lines (2-4 words per cue), and output stylized ASS subtitles.
    """
    if not os.path.exists(vtt_path):
        return False

    with open(vtt_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    cue_pattern = re.compile(
        r"((?:\d{1,2}:)?\d{2}:\d{2}[\.,]\d{3})\s*-->\s*((?:\d{1,2}:)?\d{2}:\d{2}[\.,]\d{3})[^\r\n]*\r?\n([\s\S]*?)(?=\n\n|\n\r\n|\Z)"
    )

    cues = []
    last_text = ""
    for match in cue_pattern.finditer(content):
        st = parse_vtt_timestamp(match.group(1).replace(",", "."))
        et = parse_vtt_timestamp(match.group(2).replace(",", "."))
        raw_text = clean_vtt_text(match.group(3))
        lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
        text = " ".join(lines)

        if not text or text == last_text:
            continue
        last_text = text

        if et > clip_start and st < clip_end:
            rel_st = max(0.0, st - clip_start)
            rel_et = min(clip_end - clip_start, et - clip_start)
            if rel_et > rel_st:
                cues.append((rel_st, rel_et, text))

    if not cues:
        return False

    chunked_cues = []
    for st, et, text in cues:
        words = text.split()
        if len(words) <= 4:
            chunked_cues.append((st, et, text.upper()))
        else:
            chunk_size = 3
            num_chunks = math.ceil(len(words) / chunk_size)
            chunk_dur = (et - st) / num_chunks
            for i in range(0, len(words), chunk_size):
                sub_words = words[i:i + chunk_size]
                chunk_st = st + (i // chunk_size) * chunk_dur
                chunk_et = min(et, chunk_st + chunk_dur)
                chunked_cues.append((chunk_st, chunk_et, " ".join(sub_words).upper()))

    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ShortsStyle,Impact,62,&H0000FFFF,&H00000000,&H00000000,&H90000000,1,0,0,0,100,100,1,0,1,5,3,2,60,60,340,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for st, et, text in chunked_cues:
        st_str = format_ass_timestamp(st)
        et_str = format_ass_timestamp(et)
        events.append(f"Dialogue: 0,{st_str},{et_str},ShortsStyle,,0,0,0,,{text}")

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(events) + "\n")

    return True

def transcribe_with_whisper(media_path, ass_path):
    """
    AI Speech-to-Text Fallback using faster-whisper.
    Used when YouTube has no uploaded subtitles.
    """
    try:
        from faster_whisper import WhisperModel
        print("[*] Transcribing speech using local AI Whisper model...")
        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, info = model.transcribe(media_path, beam_size=5, word_timestamps=True)

        cues = []
        for segment in segments:
            words = list(segment.words or [])
            if not words:
                txt = segment.text.strip().upper()
                if txt:
                    cues.append((segment.start, segment.end, txt))
                continue

            chunk_size = 3
            for i in range(0, len(words), chunk_size):
                chunk = words[i:i + chunk_size]
                st = chunk[0].start
                et = chunk[-1].end
                txt = " ".join(w.word.strip() for w in chunk).strip().upper()
                if txt:
                    cues.append((st, et, txt))

        if not cues:
            return False

        ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ShortsStyle,Impact,62,&H0000FFFF,&H00000000,&H00000000,&H90000000,1,0,0,0,100,100,1,0,1,5,3,2,60,60,340,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        events = []
        for st, et, text in cues:
            events.append(f"Dialogue: 0,{format_ass_timestamp(st)},{format_ass_timestamp(et)},ShortsStyle,,0,0,0,,{text}")

        with open(ass_path, "w", encoding="utf-8") as f:
            f.write(ass_header + "\n".join(events) + "\n")

        print(f"[+] AI Whisper generated {len(cues)} subtitle cues!")
        return True
    except Exception as e:
        print(f"[-] Whisper transcription fallback error: {e}")
        return False

def clip_and_format(url, spike, output_path, mode="blur", burn_subs=True, ass_path=None, temp_dir="./temp"):
    """
    Download specified time section and render into 1080x1920 vertical format with subtitles.
    """
    os.makedirs(temp_dir, exist_ok=True)
    start_s = spike["start_time"]
    end_s = spike["end_time"]
    raw_video = os.path.join(temp_dir, "raw_clip.mp4")

    if os.path.exists(raw_video):
        try:
            os.remove(raw_video)
        except Exception:
            pass

    print(f"[*] Downloading segment {start_s:.1f}s -> {end_s:.1f}s ({spike['duration']:.1f}s)...")
    downloaded = False
    try:
        g_cmd = [
            "yt-dlp", "-g",
            "-f", "bv*[height<=1080][ext=mp4]+ba*[language=en]/bv*[height<=1080]+ba*/b[height<=1080]/b",
            url
        ]
        res = run_cmd(g_cmd)
        urls = [u.strip() for u in res.stdout.strip().splitlines() if u.strip()]
        if urls:
            if len(urls) >= 2:
                v_url, a_url = urls[0], urls[1]
                ff_cut = [
                    "ffmpeg", "-y",
                    "-ss", f"{start_s:.2f}", "-to", f"{end_s:.2f}", "-i", v_url,
                    "-ss", f"{start_s:.2f}", "-to", f"{end_s:.2f}", "-i", a_url,
                    "-c", "copy",
                    raw_video
                ]
            else:
                ff_cut = [
                    "ffmpeg", "-y",
                    "-ss", f"{start_s:.2f}", "-to", f"{end_s:.2f}", "-i", urls[0],
                    "-c", "copy",
                    raw_video
                ]
            run_cmd(ff_cut, capture=False)
            if os.path.exists(raw_video) and os.path.getsize(raw_video) > 10000:
                downloaded = True
    except Exception as e:
        print(f"[-] Fast stream cut fallback: {e}")

    if not downloaded:
        dl_cmd = [
            "yt-dlp",
            "--download-sections", f"*{start_s:.2f}-{end_s:.2f}",
            "-f", "bv*[height<=1080][ext=mp4]+ba*[language=en]/bv*[height<=1080]+ba*/b[height<=1080]/b",
            "-o", raw_video,
            "--no-warnings",
            url
        ]
        run_cmd(dl_cmd)

    if not os.path.exists(raw_video):
        files = list(Path(temp_dir).glob("raw_clip*"))
        if files:
            raw_video = str(files[0])
        else:
            raise FileNotFoundError(f"Downloaded clip not found in {temp_dir}")

    # Fallback to local AI Whisper if no YouTube subtitles were provided
    if burn_subs and (not ass_path or not os.path.exists(ass_path)):
        whisper_ass = os.path.join(temp_dir, "whisper_subs.ass")
        if transcribe_with_whisper(raw_video, whisper_ass):
            ass_path = whisper_ass

    has_nvenc = check_nvenc()
    vcodec = "h264_nvenc" if has_nvenc else "libx264"
    codec_flags = ["-c:v", vcodec, "-cq", "20", "-preset", "p5"] if has_nvenc else ["-c:v", "libx264", "-crf", "18", "-preset", "fast"]

    print(f"[*] Rendering to 9:16 vertical (1080x1920) via FFmpeg using encoder: {vcodec}...")

    sub_filter = ""
    if burn_subs and ass_path and os.path.exists(ass_path):
        ass_filename = os.path.basename(ass_path)
        sub_filter = f",subtitles='{ass_filename}'"

    if mode == "blur":
        vf = (
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bg];"
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=decrease[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2{sub_filter}[v]"
        )
    elif mode == "crop":
        vf = f"[0:v]scale=-1:1920,crop=1080:1920:(in_w-1080)/2:0{sub_filter}[v]"
    else: # fit
        vf = f"[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(1080-iw)/2:(1920-ih)/2:black{sub_filter}[v]"

    ff_cmd = [
        "ffmpeg", "-y",
        "-i", os.path.abspath(raw_video),
        "-filter_complex", vf,
        "-map", "[v]",
        "-map", "0:a?",
        *codec_flags,
        "-c:a", "aac",
        "-b:a", "192k",
        "-r", "30",
        "-pix_fmt", "yuv420p",
        os.path.abspath(output_path)
    ]

    run_cmd(ff_cmd, capture=False, cwd=temp_dir)
    print(f"[+] Successfully exported clip to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="YouTube Shorts Highlight Clipper")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--duration", type=float, default=45.0, help="Target clip duration in seconds (15-60s, default: 45)")
    parser.add_argument("--top-n", type=int, default=1, help="Number of top spikes to clip (default: 1)")
    parser.add_argument("--mode", choices=["blur", "crop", "fit"], default="blur", help="Framing mode: 'blur' (blurred background), 'crop' (center crop), 'fit' (letterboxed)")
    parser.add_argument("--output-dir", default="./output", help="Directory to save generated Shorts")
    parser.add_argument("--no-captions", action="store_true", help="Disable caption burning")
    parser.add_argument("--start", type=float, default=None, help="Manual start time override (seconds)")
    parser.add_argument("--end", type=float, default=None, help="Manual end time override (seconds)")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    temp_dir = os.path.join(args.output_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True)

    info = get_video_info(args.url)
    title = info.get("title", "clip")
    total_dur = float(info.get("duration", 0))
    heatmap = info.get("heatmap") or []

    print(f"\n[+] Video: {title}")
    print(f"[+] Total Duration: {total_dur:.1f}s ({total_dur/60:.1f} mins)")
    print(f"[+] Heatmap points detected: {len(heatmap)}")

    ass_path = None
    vtt_temp = None
    if not args.no_captions:
        print("[*] Downloading video subtitles / auto-captions...")
        try:
            sub_prefix = os.path.join(temp_dir, "subtitles")
            sub_cmd = [
                "yt-dlp",
                "--write-auto-sub",
                "--write-sub",
                "--sub-lang", "en.*,en",
                "--sub-format", "vtt",
                "--skip-download",
                "-o", sub_prefix,
                "--no-warnings",
                args.url
            ]
            run_cmd(sub_cmd, check=False)
            vtt_files = list(Path(temp_dir).glob("subtitles*.vtt"))
            if vtt_files:
                vtt_temp = str(vtt_files[0])
                print(f"[+] Found subtitle file: {vtt_temp}")
            else:
                print("[-] No subtitles found on YouTube. Will use local Whisper AI.")
        except Exception as e:
            print(f"[-] Subtitle fetch warning: {e}")

    if args.start is not None and args.end is not None:
        spikes = [{
            "peak_time": (args.start + args.end) / 2.0,
            "peak_val": 1.0,
            "start_time": args.start,
            "end_time": args.end,
            "duration": args.end - args.start
        }]
    else:
        if heatmap:
            spikes = find_heatmap_spikes(heatmap, total_dur, clip_duration=args.duration, top_n=args.top_n)
        else:
            spikes = find_audio_spikes(args.url, total_dur, clip_duration=args.duration, top_n=args.top_n, temp_dir=temp_dir)

    if not spikes:
        print("[-] Fallback to highlight window from 30% mark.")
        start_t = min(30.0, total_dur * 0.3)
        end_t = min(total_dur, start_t + args.duration)
        spikes = [{
            "peak_time": (start_t + end_t) / 2.0,
            "peak_val": 0.5,
            "start_time": start_t,
            "end_time": end_t,
            "duration": end_t - start_t
        }]

    print(f"\n[+] Selected {len(spikes)} highlight moment(s):")
    for i, s in enumerate(spikes, 1):
        m, sec = divmod(s['peak_time'], 60)
        print(f"  Clip #{i}: Peak at {int(m)}m {int(sec)}s ({s['peak_time']:.1f}s, Intensity: {s['peak_val']:.2f}) | Window: {s['start_time']:.1f}s -> {s['end_time']:.1f}s ({s['duration']:.1f}s)")

    for idx, spike in enumerate(spikes, 1):
        safe_title = re.sub(r'[\\/*?:"<>|]', "", title)[:30].strip()
        out_filename = f"{safe_title}_short_{idx}.mp4"
        out_path = os.path.join(args.output_dir, out_filename)

        clip_ass = None
        if not args.no_captions and vtt_temp and os.path.exists(vtt_temp):
            clip_ass = os.path.join(temp_dir, f"clip_{idx}.ass")
            converted = convert_vtt_to_shorts_ass(vtt_temp, clip_ass, spike["start_time"], spike["end_time"])
            if not converted:
                clip_ass = None

        clip_and_format(args.url, spike, out_path, mode=args.mode, burn_subs=(not args.no_captions), ass_path=clip_ass, temp_dir=temp_dir)

    print("\n[🎉] Done! All YouTube Shorts clips are ready in:", os.path.abspath(args.output_dir))

if __name__ == "__main__":
    main()
