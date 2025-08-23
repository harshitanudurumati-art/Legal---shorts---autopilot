import os
import random
import requests
import subprocess
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip

# Config
TARGET_DURATION = 30  # seconds
OUTPUT_VIDEO = "final_output.mp4"

TOPICS = [
    "Consumer Rights Protection Laws",
    "Digital Privacy and Data Protection",
    "Employment Law Basics",
    "Tenant Rights and Housing Laws",
    "Intellectual Property Rights",
    "Contract Law Fundamentals",
]

HF_API_KEY = os.getenv("HF_API_KEY")
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ----------------- FFmpeg helper -----------------
def run_ffmpeg(cmd):
    print("Running:", " ".join(cmd))
    return subprocess.run(cmd, capture_output=True)

# ----------------- Background generator -----------------
def create_legal_themed_background():
    out = "legal_bg.mp4"
    vf = (
        "geq=r='128+90*sin(2*PI*t/9)':g='128+80*cos(2*PI*t/11)':b='200+50*sin(2*PI*t/7)',"
        "format=yuv420p,"
        "drawbox=x=0:y=0:w=iw:h=ih:color=black@0.18:t=fill"
    )
    cmd = [
        "ffmpeg","-y",
        "-f","lavfi","-i",f"color=size=1080x1920:rate=30:duration={TARGET_DURATION}:color=#1e3c72",
        "-vf", vf,
        "-c:v","libx264","-preset","fast","-crf","23","-r","30", out
    ]
    res = run_ffmpeg(cmd)
    return out if res.returncode == 0 else None

# ----------------- AI text generator -----------------
def generate_script(topic):
    if not HF_API_KEY:
        print("No HF_API_KEY found, using fallback text.")
        return f"Here are quick legal insights about {topic}. Stay informed, stay empowered!"

    url = "https://api-inference.huggingface.co/models/gpt2"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": f"Write a simple 3-sentence educational video script on: {topic}"}
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=30)
        data = res.json()
        return data[0]["generated_text"] if isinstance(data, list) else payload["inputs"]
    except Exception as e:
        print("HF API failed:", e)
        return f"Here are quick legal insights about {topic}. Stay informed, stay empowered!"

# ----------------- TTS generator -----------------
def generate_voiceover(text):
    out = "voice.mp3"
    gTTS(text).save(out)
    return out

# ----------------- Combine video & audio -----------------
def combine_video_audio(bg_video, audio_file):
    video = VideoFileClip(bg_video)
    audio = AudioFileClip(audio_file)
    final = CompositeVideoClip([video.set_audio(audio)])
    final.set_duration(min(video.duration, audio.duration)).write_videofile(
        OUTPUT_VIDEO, codec="libx264", audio_codec="aac"
    )
    return OUTPUT_VIDEO

# ----------------- Telegram upload -----------------
def send_to_telegram(video_path):
    if not TG_TOKEN or not TG_CHAT_ID:
        print("Telegram config missing, skipping upload.")
        return
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendVideo"
    with open(video_path, "rb") as f:
        res = requests.post(url, data={"chat_id": TG_CHAT_ID}, files={"video": f})
    print("Telegram upload status:", res.text)

# ----------------- Main -----------------
def main():
    topic = random.choice(TOPICS)
    print("Selected Topic:", topic)

    bg = create_legal_themed_background()
    script = generate_script(topic)
    voice = generate_voiceover(script)
    final = combine_video_audio(bg, voice)

    send_to_telegram(final)

if __name__ == "__main__":
    main()
