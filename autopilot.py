import os
import json
import datetime
import requests
import moviepy.editor as mp
import gtts
from textwrap import wrap

# Load secrets
DEEPINFRA_API_KEY = os.getenv("DEEPINFRA_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Pick today’s topic
with open("topics.json") as f:
    topics = json.load(f)["topics"]
topic = topics[datetime.datetime.now().day % len(topics)]

# Ask DeepInfra for script
def get_script_from_deepinfra(prompt: str) -> str:
    url = "https://api.deepinfra.com/v1/openai/chat/completions"  # fixed endpoint
    headers = {
        "Authorization": f"Bearer {DEEPINFRA_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "meta-llama/Meta-Llama-3-8B-Instruct",  # valid DeepInfra model
        "messages": [
            {"role": "system", "content": "You are a clear, factual legal explainer bot."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()

prompt = f"Write a 2-minute YouTube video script on: {topic}. Use facts, references, and clear explanation. Avoid predictions."
script = get_script_from_deepinfra(prompt)

# Save script
with open("script.txt", "w") as f:
    f.write(script)

# Convert script to audio
tts = gtts.gTTS(script, lang="en")
tts.save("voice.mp3")

# Download background music (only once, reuse file)
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
    # Wrap long lines so they fit on screen
    wrapped = "\n".join(wrap(line, width=40))
    txt_clip = mp.TextClip(
        wrapped,
        fontsize=40,
        color="white",
        bg_color="black",
        size=(1280, 720),
        method="caption"
    ).set_duration(3)
    clips.append(txt_clip)

video = mp.concatenate_videoclips(clips)
video = video.set_audio(mp.AudioFileClip("final_audio.mp3"))
video.write_videofile("final_video.mp4", fps=24)

# Send to Telegram
url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
with open("final_video.mp4", "rb") as vid:
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID}, files={"video": vid})
