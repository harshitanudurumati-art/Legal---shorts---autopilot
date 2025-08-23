import os
import json
import random
import datetime
import requests
import subprocess
import sys
from gtts import gTTS
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from openai import OpenAI

# ========= DEBUG UTIL ==========
def debug(msg):
    print(f"[DEBUG] {msg}", flush=True)

# ========= CONFIG ==========
HF_API_KEY = os.getenv("HF_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

TOPICS_FILE = "topics.json"
OUTPUT_TEXT = "output.txt"
OUTPUT_AUDIO = "output.mp3"
OUTPUT_VIDEO = "final.mp4"

# ========= CLIENTS ==========
client = None
if OPENAI_API_KEY:
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        debug("OpenAI client initialized ✅")
    except Exception as e:
        debug(f"Failed to init OpenAI client: {e}")

# ========= STEP 1: PICK TOPIC ==========
def pick_topic():
    debug("Picking topic...")
    if not os.path.exists(TOPICS_FILE):
        topics = [
            "Consumer Rights in India",
            "Digital Privacy Laws",
            "Employment Law Basics",
            "Tenant Rights",
            "Intellectual Property Rights",
            "Contract Law"
        ]
    else:
        with open(TOPICS_FILE, "r") as f:
            topics = json.load(f)

    topic = random.choice(topics)
    debug(f"Picked topic: {topic}")
    return topic

# ========= STEP 2: GENERATE TEXT ==========
def generate_text(topic):
    debug("Generating text...")
    if client:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"Explain {topic} in simple terms (150 words)."}]
            )
            text = response.choices[0].message.content.strip()
            debug("Got response from OpenAI ✅")
            return text
        except Exception as e:
            debug(f"OpenAI generation failed: {e}")

    if HF_API_KEY:
        try:
            url = "https://api-inference.huggingface.co/models/gpt2"
            headers = {"Authorization": f"Bearer {HF_API_KEY}"}
            payload = {"inputs": f"Explain {topic} in simple terms."}
            r = requests.post(url, headers=headers, json=payload, timeout=60)
            data = r.json()
            text = data[0]["generated_text"]
            debug("Got response from HuggingFace ✅")
            return text
        except Exception as e:
            debug(f"HuggingFace generation failed: {e}")

    debug("Fallback text used")
    return f"{topic} is an important legal topic everyone should know about."

# ========= STEP 3: SAVE TEXT ==========
def save_text(text):
    with open(OUTPUT_TEXT, "w", encoding="utf-8") as f:
        f.write(text)
    debug(f"Saved text to {OUTPUT_TEXT}")

# ========= STEP 4: TTS ==========
def text_to_speech(text):
    debug("Generating audio...")
    try:
        tts = gTTS(text=text, lang="en")
        tts.save(OUTPUT_AUDIO)
        debug(f"Saved audio to {OUTPUT_AUDIO}")
        return OUTPUT_AUDIO
    except Exception as e:
        debug(f"TTS failed: {e}")
        return None

# ========= STEP 5: VIDEO CREATION ==========
def create_video(audio_file, text):
    debug("Creating video with subtitles...")
    try:
        audio = AudioFileClip(audio_file)
        duration = audio.duration

        # Background image
        img = "background.jpg"
        if not os.path.exists(img):
            debug("No background.jpg found, using black background")
            img = "black.jpg"
            from PIL import Image
            Image.new("RGB", (1280, 720), (0, 0, 0)).save(img)

        clip = ImageClip(img).set_duration(duration).set_audio(audio)

        # FFmpeg subtitles overlay
        with open("subs.txt", "w", encoding="utf-8") as f:
            f.write(text)

        # Just attach subtitles using drawtext
        cmd = [
            "ffmpeg", "-y",
            "-i", audio_file,
            "-loop", "1", "-i", img,
            "-vf", f"drawtext=textfile=subs.txt:fontcolor=white:fontsize=28:x=(w-text_w)/2:y=h-100",
            "-shortest", OUTPUT_VIDEO
        ]
        debug(f"Running ffmpeg: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        debug(f"Video saved to {OUTPUT_VIDEO}")
        return OUTPUT_VIDEO
    except Exception as e:
        debug(f"Video creation failed: {e}")
        return None

# ========= STEP 6: SEND TO TELEGRAM ==========
def send_to_telegram(file):
    debug("Uploading video to Telegram...")
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
        with open(file, "rb") as f:
            r = requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID}, files={"video": f})
        if r.status_code == 200:
            debug("Video sent to Telegram ✅")
        else:
            debug(f"Telegram upload failed: {r.text}")
    except Exception as e:
        debug(f"Telegram error: {e}")

# ========= MAIN ==========
def main():
    debug("=== Autopilot run started ===")
    topic = pick_topic()
    text = generate_text(topic)
    save_text(text)
    audio = text_to_speech(text)
    if not audio:
        debug("No audio generated, aborting.")
        sys.exit(1)
    video = create_video(audio, text)
    if video:
        send_to_telegram(video)
    else:
        debug("No video generated.")
    debug("=== Autopilot run finished ===")

if __name__ == "__main__":
    main()
