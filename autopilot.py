import json
import datetime
import os
import requests
from gtts import gTTS
from moviepy.editor import *

# Step 1: Pick today's topic from topics.json
with open("topics.json", "r") as f:
    topics = json.load(f)

today = datetime.date.today()
topic_index = today.toordinal() % len(topics)
topic = topics[topic_index]

# Step 2: Fetch updates (placeholder - can connect to legal API later)
updates = f"Latest case law and news about {topic} (auto-updated placeholder)."

# Step 3: Write script
script = f"""
Today's Legal Insight:
Topic: {topic}

Recent Update:
{updates}

Stay tuned for more legal shorts daily!
"""

# Step 4: Generate audio
tts = gTTS(script)
os.makedirs("output", exist_ok=True)
audio_path = f"output/{topic}_audio.mp3"
tts.save(audio_path)

# Step 5: Generate video
txt_clip = TextClip(script, fontsize=40, color="white", size=(720,1280), method='caption')
txt_clip = txt_clip.set_duration(30)

audio = AudioFileClip(audio_path)
final = txt_clip.set_audio(audio)

video_path = f"output/{topic}_video.mp4"
final.write_videofile(video_path, fps=24)

print("✅ Video generated:", video_path)
