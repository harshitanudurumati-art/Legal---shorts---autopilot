#!/usr/bin/env python3
import os, sys, datetime, requests, moviepy.editor as mp, gtts
from textwrap import wrap

# ---------------------------
# Config
# ---------------------------
HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODELS = [
    "google/flan-t5-small"  # Stable free model
]

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not HF_API_KEY:
    print("WARNING: HF_API_KEY not set. Will use fallback script.")

# ---------------------------
# Hugging Face text generation
# ---------------------------
def hf_generate_text(prompt, max_new_tokens=300, temperature=0.7, retries=3):
    """Try generating text using HF model, safely handle empty or invalid responses."""
    model = HF_MODELS[0]
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": max_new_tokens, "temperature": temperature}}
    
    for attempt in range(1, retries+1):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            try:
                data = resp.json()
            except ValueError:
                raise RuntimeError(f"HF API returned empty or invalid response: {resp.text}")
            if isinstance(data, list) and "generated_text" in data[0]:
                print(f"INFO: Model {model} succeeded on attempt {attempt}")
                return data[0]["generated_text"]
            else:
                raise RuntimeError(f"Unexpected response from {model}: {data}")
        except Exception as e:
            print(f"WARNING: Attempt {attempt} failed: {e}", file=sys.stderr)
    # fallback
    print("INFO: Using fallback script after retries")
    return f"Fallback script for prompt: {prompt}"

# ---------------------------
# Main flow
# ---------------------------
def main():
    # Topics
    topics = ["Right to Privacy in India", "AI and Copyright Issues",
              "Latest Supreme Court Judgments", "Consumer Protection Rights",
              "Cybersecurity and Law"]
    topic = topics[datetime.datetime.now().day % len(topics)]
    print("INFO: Generating script for topic:", topic)

    prompt = f"Write a clear, factual 2-minute YouTube video script on: {topic}."
    
    # Generate script (fallback if HF fails)
    script = hf_generate_text(prompt) if HF_API_KEY else f"Fallback script for topic: {topic}"

    # Save script
    with open("script.txt", "w", encoding="utf-8") as f: f.write(script)
    print("INFO: Script saved to script.txt")

    # Convert to audio via gTTS
    tts = gtts.gTTS(script, lang="en")
    tts.save("voice.mp3")
    print("INFO: voice.mp3 created")

    # Background music
    bg_file = "bg_music.mp3"
    if not os.path.exists(bg_file):
        try:
            r = requests.get("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", timeout=30)
            r.raise_for_status()
            with open(bg_file, "wb") as f: f.write(r.content)
            print("INFO: bg_music.mp3 downloaded")
        except Exception as e:
            print(f"WARNING: Could not download bg music: {e}", file=sys.stderr)

    # Merge audio
    voice = mp.AudioFileClip("voice.mp3")
    if os.path.exists(bg_file):
        bg_music = mp.AudioFileClip(bg_file).subclip(0, min(60, voice.duration+5))
        final_audio = mp.CompositeAudioClip([voice.volumex(1.0), bg_music.volumex(0.18)])
    else:
        final_audio = voice
    final_audio.write_audiofile("final_audio.mp3")
    print("INFO: final_audio.mp3 written")

    # Create video with text
    clips = []
    for sentence in script.split("."):
        line = sentence.strip()
        if not line: continue
        wrapped = "\n".join(wrap(line, width=40))
        duration = max(2.5, min(6.0, 2.5 + len(line.split())/6.0))
        txt_clip = mp.TextClip(wrapped, fontsize=40, color="white",
                               bg_color="black", size=(1280,720),
                               method="caption").set_duration(duration)
        clips.append(txt_clip)

    video = mp.concatenate_videoclips(clips, method="compose")
    video = video.set_audio(mp.AudioFileClip("final_audio.mp3"))
    video.write_videofile("final_video.mp4", fps=24)
    print("INFO: final_video.mp4 created")

    # Send to Telegram
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            tg_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
            with open("final_video.mp4", "rb") as vid:
                resp = requests.post(tg_url, data={"chat_id": TELEGRAM_CHAT_ID}, files={"video": vid}, timeout=120)
            if resp.status_code != 200:
                print(f"WARNING: Telegram API returned {resp.status_code}: {resp.text}", file=sys.stderr)
            else:
                print("INFO: Video sent to Telegram successfully.")
        except Exception as e:
            print(f"ERROR sending to Telegram: {e}", file=sys.stderr)
    else:
        print("INFO: Telegram credentials missing; skipping send step.")

if __name__ == "__main__":
    main()
