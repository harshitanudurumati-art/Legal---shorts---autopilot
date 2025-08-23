import os
import json
import random
import requests
from datetime import datetime
import subprocess
import textwrap

# -----------------------------
# Config
# -----------------------------
LEGAL_TOPICS = [
    "Consumer Rights Protection Laws",
    "Digital Privacy and Data Protection", 
    "Employment Law Basics",
    "Tenant Rights and Housing Laws",
    "Intellectual Property Rights",
    "Contract Law Fundamentals",
    "Criminal Law Basics",
    "Family Law Essentials"
]

BACKGROUND_VIDEO_SOURCES = {
    "Consumer Rights Protection Laws": [
        "https://cdn.pixabay.com/vimeo/41758/retail-41758-1920x1080.mp4",
        "https://cdn.pixabay.com/vimeo/28745/money-28745-1280x720.mp4",
    ],
    "Digital Privacy and Data Protection": [
        "https://cdn.pixabay.com/vimeo/41062/cyber-41062-1920x1080.mp4",
        "https://cdn.pixabay.com/vimeo/27693/data-27693-1920x1080.mp4",
    ],
    "Employment Law Basics": [
        "https://cdn.pixabay.com/vimeo/34521/office-34521-1920x1080.mp4",
        "https://cdn.pixabay.com/vimeo/28934/meeting-28934-1920x1080.mp4",
    ],
    "Tenant Rights and Housing Laws": [
        "https://cdn.pixabay.com/vimeo/39847/housing-39847-1920x1080.mp4",
        "https://cdn.pixabay.com/vimeo/25698/home-25698-1920x1080.mp4",
    ],
    "default": [
        "https://cdn.pixabay.com/vimeo/15197/justice-15197-1920x1080.mp4",
        "https://cdn.pixabay.com/vimeo/28745/money-28745-1280x720.mp4",
    ],
}

TARGET_DURATION = 58  # seconds

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119 Safari/537.36"}

# -----------------------------
# Utilities
# -----------------------------
def safe_download(url, out_path, expect_content_prefix=None, timeout=45):
    try:
        with requests.get(url, stream=True, headers=UA, timeout=timeout, allow_redirects=True) as r:
            ct = r.headers.get("Content-Type", "")
            if expect_content_prefix and not ct.startswith(expect_content_prefix):
                return False
            if r.status_code != 200:
                return False
            with open(out_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        return os.path.getsize(out_path) > 100*1024  # >100KB
    except Exception:
        return False

def run_ffmpeg(cmd):
    # Helpful during debugging: add "-loglevel", "error" to reduce noise or "debug" to increase it.
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("FFmpeg FAILED\n", result.stderr[:4000])
    return result

# -----------------------------
# Background video
# -----------------------------
def download_relevant_background_video(topic):
    print(f"🎬 Getting background for: {topic}")
    urls = BACKGROUND_VIDEO_SOURCES.get(topic, BACKGROUND_VIDEO_SOURCES["default"])
    for i, url in enumerate(urls, 1):
        fn = f"bg_{i}.mp4"
        if safe_download(url, fn, expect_content_prefix="video/"):
            ok, prepped = prepare_background_video(fn)
            if ok:
                return prepped
    # Fallback:
    return create_legal_themed_background()

def prepare_background_video(video_path):
    """Scale/crop to 9:16 and add a subtle dark overlay for text readability."""
    out = "prepared_bg.mp4"
    vf = (
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,setsar=1,"
        "eq=contrast=1.05:saturation=1.05:brightness=-0.02,"
        "drawbox=x=0:y=0:w=iw:h=ih:color=black@0.28:t=fill,"
        "format=yuv420p"
    )
    cmd = ["ffmpeg", "-y", "-i", video_path, "-t", str(TARGET_DURATION), "-vf", vf,
           "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "23", out]
    res = run_ffmpeg(cmd)
    try:
        os.remove(video_path)
    except Exception:
        pass
    return (res.returncode == 0 and os.path.exists(out)), out

def create_legal_themed_background():
    """Emoji removed (font issues). Pure animated gradient + soft vignette."""
    out = "legal_bg.mp4"
    vf = (
        "geq=r='128+90*sin(2*PI*t/9)':g='128+80*cos(2*PI*t/11)':b='200+50*sin(2*PI*t/7)',"
        "format=yuv420p,"
        "drawbox=x=0:y=0:w=iw:h=ih:color=black@0.18:t=fill"
    )
    cmd = ["ffmpeg","-y","-f","lavfi","-i",f"color=size=1080x1920:rate=30:duration={TARGET_DURATION}:color=#1e3c72",
           "-vf", vf,
           "-c:v","libx264","-preset","fast","-crf","23","-r","30", out]
    res = run_ffmpeg(cmd)
    return out if res.returncode == 0 else None

# -----------------------------
# Music (optional)
# -----------------------------
def download_background_music():
    # If this fails, we’ll proceed without audio mix.
    candidates = [
        "https://file-examples.com/storage/fe68c2b69d66d818a89f2dd/2017/11/file_example_MP3_700KB.mp3"
    ]
    for url in candidates:
        if safe_download(url, "bgm.mp3", expect_content_prefix="audio/"):
            return "bgm.mp3"
    # Ambient fallback
    cmd = [
        "ffmpeg","-y",
        "-f","lavfi","-i",f"sine=frequency=220:duration={TARGET_DURATION}",
        "-f","lavfi","-i",f"sine=frequency=330:duration={TARGET_DURATION}",
        "-filter_complex","[0:a][1:a]amix=inputs=2,volume=0.05[aout]",
        "-map","[aout]","-c:a","aac","ambient.mp3"
    ]
    res = run_ffmpeg(cmd)
    return "ambient.mp3" if res.returncode == 0 else None

# -----------------------------
# Content
# -----------------------------
def generate_fallback_sentences(topic):
    hook = "Did you know your rights might be stronger than you think?"
    tips = [
        "Keep all receipts and emails as proof.",
        "File complaints on official portals if needed.",
        "Read terms before you accept.",
        "Follow for more legal tips!"
    ]
    body = [
        f"Here’s what to know about {topic}.",
        "Use simple documentation to defend your rights.",
        "Avoid scams by verifying sellers and sites.",
    ]
    lines = [hook] + body + tips
    return lines

# -----------------------------
# Text overlays video (fixed)
# -----------------------------
def create_sentence_synced_video(bg_path, sentences, out_path, music_path=None):
    """
    Safer version of your previous word-by-word. Shows one sentence at a time,
    properly maps labeled outputs, and guarantees TARGET_DURATION seconds.
    """
    if not bg_path or not os.path.exists(bg_path):
        bg_path = create_legal_themed_background()

    # Timing
    total = TARGET_DURATION
    n = max(1, len(sentences))
    per = total / n

    # Build filter graph segments
    parts = []
    parts.append("[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
                 "crop=1080:1920,setsar=1,format=yuv420p[base]")

    cur = "[base]"
    for i, s in enumerate(sentences):
        start = round(i*per, 3)
        end   = round((i+1)*per, 3)
        wrapped = textwrap.fill(s.strip(), width=26)
        escaped = wrapped.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
        seg = (f"{cur}drawtext=text='{escaped}':"
               f"fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
               f"fontsize=60:fontcolor=white:bordercolor=black:borderw=4:"
               f"box=1:boxcolor=black@0.35:boxborderw=20:"
               f"x=(w-text_w)/2:y=(h-text_h)/2:"
               f"enable='between(t,{start},{end})'[t{i}]")
        parts.append(seg)
        cur = f"[t{i}]"
    parts[-1] = parts[-1].replace(f"[t{n-1}]", "[vout]")  # last label -> [vout]

    cmd = ["ffmpeg","-y","-i", bg_path]
    if music_path and os.path.exists(music_path):
        cmd += ["-i", music_path]

    # Build filter_complex for video; audio (if any) mixed to [aout]
    filter_complex = ";".join(parts)
    if music_path and os.path.exists(music_path):
        filter_complex += ";[1:a]volume=0.18[aout]"

    cmd += ["-filter_complex", filter_complex,
            "-map","[vout]"]

    if music_path and os.path.exists(music_path):
        cmd += ["-map","[aout]","-c:a","aac","-b:a","128k"]
    else:
        cmd += ["-an"]

    cmd += ["-t", str(TARGET_DURATION),
            "-r","30",
            "-c:v","libx264","-preset","medium","-crf","23",
            out_path]

    res = run_ffmpeg(cmd)
    return res.returncode == 0 and os.path.exists(out_path)

# -----------------------------
# Telegram (unchanged idea)
# -----------------------------
def send_to_telegram(video_path, sentences, topic):
    bot = os.getenv("TELEGRAM_BOT_TOKEN")
    chat = os.getenv("TELEGRAM_CHAT_ID")
    if not bot or not chat:
        print("Telegram creds missing; skipping upload.")
        return False
    caption = f"""🔥 LEGAL SHORT READY

📚 {topic}
⏱️ {TARGET_DURATION}s
💬 Text-synced sentences

{" ".join(sentences)[:300]}...

#LegalTips #Law #Shorts #KnowYourRights
"""
    import requests
    with open(video_path, "rb") as f:
        resp = requests.post(f"https://api.telegram.org/bot{bot}/sendVideo",
                             data={"chat_id": chat, "caption": caption},
                             files={"video": f}, timeout=120)
    ok = resp.status_code == 200
    print("Telegram upload:", "OK" if ok else resp.text[:400])
    return ok

# -----------------------------
# Main
# -----------------------------
def main():
    topic = random.choice(LEGAL_TOPICS)
    print("Topic:", topic)

    # Generate content (you can plug your API call here; fallback used for stability).
    sentences = generate_fallback_sentences(topic)
    print(f"Sentences: {len(sentences)}")

    bg = download_relevant_background_video(topic)
    music = download_background_music()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = f"legal_shorts_fixed_{ts}.mp4"

    ok = create_sentence_synced_video(bg, sentences, out, music)
    if not ok:
        print("❌ Video creation failed.")
        return

    print("✅ Created:", out)
    send_to_telegram(out, sentences, topic)

if __name__ == "__main__":
    main()
