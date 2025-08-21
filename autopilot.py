import os
import json
import random
import datetime
import requests
import moviepy.editor as mp
import gtts
from openai import OpenAI

# Load API Keys
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Pick today’s topic
with open("topics.json") as f:
    topics = json.load(f)["topics"]
topic = topics[datetime.datetime.now().day % len(topics)]

# Ask ChatGPT for script
prompt = f"Write a 2-minute YouTube video script on: {topic}. Use facts, references, and clear explanation. Avoid predictions."
resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.4,
)
script = resp.choices[0].message.content.strip()

# Save script
with open("script.txt", "w") as f:
    f.write(script)

# Convert script to audio
tts = gtts.gTTS(script, lang="en")
tts.save("voice.mp3")

# Download background music (local file needed)
bg_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
bg_file = "bg_music.mp3"
if not os.path.exists(bg_file):
    r = requests.get(bg_url)
    with open(bg_file, "wb") as f:
        f.write(r.content)

# Merge voice + bg music
voice = mp.AudioFileClip("voice.mp3")
bg_music = mp.AudioFileClip(bg_file).subclip(0, min(60, voice.duration + 5))
final_audio = mp.CompositeAudioClip([voice.volumex(1.0), bg_music.volumex(0.2)])
final_audio.write_audiofile("final_audio.mp3")

# Create video with text
clips = []
for line in script.split("."):
    line = line.strip()
    if not line:
        continue
    txt_clip = mp.TextClip(
        line,
        fontsize=40,
        color="white",
        bg_color="black",
        size=(1280, 720),
    ).set_duration(3)
    clips.append(txt_clip)

video = mp.concatenate_videoclips(clips)
video = video.set_audio(mp.AudioFileClip("final_audio.mp3"))
video.write_videofile("final_video.mp4", fps=24)

# Send to Telegram
url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
with open("final_video.mp4", "rb") as vid:
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID}, files={"video": vid})
