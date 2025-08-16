import os, json, random, datetime, requests, openai, moviepy.editor as mp, gtts

# Load API Keys
openai.api_key = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Pick today’s topic
with open("topics.json") as f:
    topics = json.load(f)["topics"]
topic = topics[datetime.datetime.now().day % len(topics)]

# Ask ChatGPT for script
prompt = f"Write a 2-minute YouTube video script on: {topic}. Use facts, references, and clear explanation. Avoid predictions."
response = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}]
)
script = response["choices"][0]["message"]["content"]

# Save script
with open("script.txt", "w") as f:
    f.write(script)

# Convert script to audio
tts = gtts.gTTS(script, lang="en")
tts.save("voice.mp3")

# Background music (royalty free)
bg_music = mp.AudioFileClip("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3").subclip(0,60)

# Merge voice + bg music
voice = mp.AudioFileClip("voice.mp3")
final_audio = mp.CompositeAudioClip([voice.volumex(1.0), bg_music.volumex(0.2)])
final_audio.write_audiofile("final_audio.mp3")

# Create video with text
clips = []
for line in script.split("."):
    txt_clip = mp.TextClip(line.strip(), fontsize=40, color="white", bg_color="black", size=(1280,720))
    txt_clip = txt_clip.set_duration(3)
    clips.append(txt_clip)

video = mp.concatenate_videoclips(clips)
video = video.set_audio(mp.AudioFileClip("final_audio.mp3"))
video.write_videofile("final_video.mp4", fps=24)

# Send to Telegram
url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
with open("final_video.mp4", "rb") as vid:
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID}, files={"video": vid})
