import os
import random
import subprocess
import textwrap
from datetime import datetime

import moviepy.editor as mp
import requests
from gtts import gTTS
from openai import OpenAI

# -----------------------------
# Config
# -----------------------------
TARGET_DURATION = 60  # seconds

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
    "Consumer Rights Protection Laws": ["videos/consumer1.mp4", "videos/consumer2.mp4"],
    "Digital Privacy and Data Protection": ["videos/privacy1.mp4", "videos/privacy2.mp4"],
    "Employment Law Basics": ["videos/employment1.mp4", "videos/employment2.mp4"],
    "Tenant Rights and Housing Laws": ["videos/tenant1.mp4", "videos/tenant2.mp4"],
    "Intellectual Property Rights": ["videos/ipr1.mp4", "videos/ipr2.mp4"],
    "Contract Law Fundamentals": ["videos/contract1.mp4", "videos/contract2.mp4"],
    "Criminal Law Basics": ["videos/criminal1.mp4", "videos/criminal2.mp4"],
    "Family Law Essentials": ["videos/family1.mp4", "videos/family2.mp4"],
    "default": ["videos/default1.mp4"]
}

UA = {"User-Agent": "Mozilla/5.0"}

# -----------------------------
# Utilities
# -----------------------------
def run_ffmpeg(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("[ERROR] FFmpeg failed:", result.stderr[:4000])
    return result

def safe_download(url, out_path, expect_content_prefix=None, timeout=45):
    try:
        with requests.get(url, stream=True, headers=UA, timeout=timeout) as r:
            if expect_content_prefix and not r.headers.get("Content-Type", "").startswith(expect_content_prefix):
                return False
            if r.status_code != 200:
                return False
            with open(out_path, "wb") as f:
                for chunk in r.iter_content(8192):
                    if chunk:
                        f.write(chunk)
        return os.path.getsize(out_path) > 50*1024
    except Exception:
        return False

# -----------------------------
# AI Script Generation
# -----------------------------
def generate_script(topic, client):
    print(f"[DEBUG] Generating script for topic: {topic}")
    prompt = f"""
    Write a 1-minute educational video script (~150-200 words) explaining {topic}.
    Include a simple explanation, at least one interesting example or fact,
    and end with a takeaway encouraging viewers to follow legal tips.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("[ERROR] OpenAI API failed:", e)
        # fallback
        return f"This is a short informative video about {topic}. Always know your rights!"

# -----------------------------
# Background video selection
# -----------------------------
def select_background_video(topic):
    sources = BACKGROUND_VIDEO_SOURCES.get(topic, BACKGROUND_VIDEO_SOURCES["default"])
    for path in sources:
        if os.path.exists(path):
            return path
    return create_gradient_background()

def create_gradient_background():
    out = "bg_gradient.mp4"
    vf = (
        "geq=r='128+90*sin(2*PI*t/9)':g='128+80*cos(2*PI*t/11)':b='200+50*sin(2*PI*t/7)',"
        "format=yuv420p,"
        "drawbox=x=0:y=0:w=iw:h=ih:color=black@0.18:t=fill"
    )
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=size=1080x1920:rate=30:duration={TARGET_DURATION}:color=#1e3c72",
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-r", "30",
        out
    ]
    res = run_ffmpeg(cmd)
    return out if res.returncode == 0 else None

# -----------------------------
# TTS Narration
# -----------------------------
def generate_narration(script_text):
    tts = gTTS(text=script_text, lang="en")
    tts_file = "narration.mp3"
    tts.save(tts_file)
    return tts_file

# -----------------------------
# Video creation
# -----------------------------
def create_video(bg_path, narration_path, script_text, out_path):
    video_clip = mp.VideoFileClip(bg_path).subclip(0, TARGET_DURATION)
    audio_clip = mp.AudioFileClip(narration_path)
    video_clip = video_clip.set_audio(audio_clip).set_duration(audio_clip.duration)

    wrapped_text = textwrap.fill(script_text, width=30)
    txt_clip = mp.TextClip(
        wrapped_text, fontsize=50, color="white", bg_color="black", method="caption", size=video_clip.size
    ).set_position(("center", "bottom")).set_duration(audio_clip.duration)

    final = mp.CompositeVideoClip([video_clip, txt_clip])
    final.write_videofile(out_path, fps=24, codec="libx264", audio_codec="aac")
    return out_path

# -----------------------------
# Telegram upload
# -----------------------------
def send_to_telegram(video_path, topic):
    bot = os.getenv("TELEGRAM_BOT_TOKEN")
    chat = os.getenv("TELEGRAM_CHAT_ID")
    if not bot or not chat:
        print("[DEBUG] Telegram credentials missing, skipping upload.")
        return False
    caption = f"🔥 LEGAL SHORT\n📚 {topic}\n⏱️ {TARGET_DURATION}s\n#LegalTips #Law #KnowYourRights"
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
    print("[DEBUG] Initializing OpenAI client...")
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    print("[DEBUG] Picking a random topic...")
    topic = random.choice(LEGAL_TOPICS)
    print(f"[DEBUG] Selected Topic: {topic}")

    script = generate_script(topic, client)
    print(f"[DEBUG] Generated script ({len(script.split())} words)")

    bg_video = select_background_video(topic)
    narration = generate_narration(script)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = f"legal_short_{ts}.mp4"

    print("[DEBUG] Creating video...")
    final_video = create_video(bg_video, narration, script, out_file)
    print(f"[DEBUG] Video created: {final_video}")

    send_to_telegram(final_video, topic)
    print("[DEBUG] Autopilot run finished ✅")

if __name__ == "__main__":
    main()
