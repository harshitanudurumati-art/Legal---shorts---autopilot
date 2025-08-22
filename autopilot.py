#!/usr/bin/env python3
"""
autopilot.py -- uses Hugging Face Inference API to generate a script,
converts it to speech, makes a short video, and sends it to Telegram.

Before running in GitHub Actions:
  - Add secret HF_API_KEY (your Hugging Face access token) to your repo secrets.
  - (Optional) Set HF_MODEL env var to a different HF model slug (default: "gpt2").
"""

import os
import sys
import json
import datetime
import time
import requests
import moviepy.editor as mp
import gtts
from textwrap import wrap

# ---------------------------
# Config / environment
# ---------------------------
HF_API_KEY = os.getenv("HF_API_KEY") or os.getenv("HUGGINGFACE_API_KEY")
HF_MODEL = os.getenv("HF_MODEL", "gpt2")   # change via env if you want a different model
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Quick sanity checks
if not HF_API_KEY:
    print("ERROR: HF_API_KEY not set. Add Hugging Face token to env or GitHub Secrets (HF_API_KEY).", file=sys.stderr)
    sys.exit(1)

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    print("WARNING: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set. Telegram step will fail if not provided.", file=sys.stderr)

# ---------------------------
# Helpers
# ---------------------------
def hf_generate_text(prompt: str, max_new_tokens: int = 300, temperature: float = 0.4) -> str:
    """
    Call Hugging Face Inference API (text-generation style) and return generated text.
    Tries to handle different response formats returned by HF.
    """
    api_url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    headers = {"Authorization": f"Bearer {HF_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": max_new_tokens, "temperature": temperature, "return_full_text": False},
        # Some models respect 'options' to reduce latency / caching; we won't set here.
    }

    try:
        resp = requests.post(api_url, headers=headers, json=payload, timeout=60)
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Hugging Face request failed: {e}") from e

    # Check for HTTP errors
    if resp.status_code != 200:
        # Provide helpful message
        try:
            err = resp.json()
        except Exception:
            err = resp.text
        raise RuntimeError(f"Hugging Face API error {resp.status_code}: {err}")

    # Parse response flexibly
    try:
        data = resp.json()
    except ValueError:
        # Not JSON (some models return plain text)
        return resp.text.strip()

    # If data is a dict with 'error'
    if isinstance(data, dict) and "error" in data:
        raise RuntimeError(f"Hugging Face returned error: {data['error']}")

    # If data is a list (most generation models return a list of outputs)
    if isinstance(data, list) and len(data) > 0:
        first = data[0]
        if isinstance(first, dict) and "generated_text" in first:
            return first["generated_text"].strip()
        # some models return {"generated_text": "..."} nested or alternative keys
        if isinstance(first, dict) and "text" in first:
            return first["text"].strip()
        # fallback: try converting first dict to string
        return json.dumps(first).strip()

    # If data is dict with 'generated_text' top-level
    if isinstance(data, dict) and "generated_text" in data:
        return data["generated_text"].strip()

    # Fallback to stringified JSON
    return json.dumps(data).strip()

# ---------------------------
# Main flow
# ---------------------------
def main():
    # Load topics
    topics = None
    try:
        with open("topics.json", "r", encoding="utf-8") as f:
            topics = json.load(f).get("topics", [])
    except FileNotFoundError:
        print("WARNING: topics.json not found — using default topics.", file=sys.stderr)
        topics = [
            "Right to Privacy in India",
            "AI and Copyright Issues",
            "Latest Supreme Court Judgments",
            "Consumer Protection Rights",
            "Cybersecurity and Law"
        ]
    except Exception as e:
        print(f"ERROR reading topics.json: {e}", file=sys.stderr)
        sys.exit(1)

    if not topics:
        print("ERROR: topics list is empty.", file=sys.stderr)
        sys.exit(1)

    topic = topics[datetime.datetime.now().day % len(topics)]
    prompt = f"Write a clear, factual 2-minute YouTube video script on: {topic}. Use facts, references, and clear explanation. Avoid predictions."

    print("INFO: Generating script with Hugging Face model:", HF_MODEL)
    try:
        script = hf_generate_text(prompt, max_new_tokens=350, temperature=0.4)
    except Exception as e:
        print(f"ERROR generating text: {e}", file=sys.stderr)
        sys.exit(1)

    # Save script
    try:
        with open("script.txt", "w", encoding="utf-8") as f:
            f.write(script)
        print("INFO: Script saved to script.txt")
    except Exception as e:
        print(f"ERROR saving script.txt: {e}", file=sys.stderr)

    # Convert to audio via gTTS
    try:
        tts = gtts.gTTS(script, lang="en")
        tts.save("voice.mp3")
        print("INFO: voice.mp3 created")
    except Exception as e:
        print(f"ERROR generating TTS: {e}", file=sys.stderr)
        sys.exit(1)

    # Download background music if missing
    bg_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
    bg_file = "bg_music.mp3"
    try:
        if not os.path.exists(bg_file):
            print("INFO: Downloading background music...")
            r = requests.get(bg_url, timeout=30)
            r.raise_for_status()
            with open(bg_file, "wb") as f:
                f.write(r.content)
            print("INFO: bg_music.mp3 downloaded")
    except Exception as e:
        print(f"WARNING: Could not download background music: {e}", file=sys.stderr)

    # Merge voice + bg music
    try:
        voice = mp.AudioFileClip("voice.mp3")
        # If bg music exists, add a subclip; otherwise just use voice
        if os.path.exists(bg_file):
            bg_music = mp.AudioFileClip(bg_file).subclip(0, min(60, voice.duration + 5))
            final_audio = mp.CompositeAudioClip([voice.volumex(1.0), bg_music.volumex(0.18)])
        else:
            final_audio = voice
        final_audio.write_audiofile("final_audio.mp3")
        print("INFO: final_audio.mp3 written")
    except Exception as e:
        print(f"ERROR creating/merging audio: {e}", file=sys.stderr)
        sys.exit(1)

    # Create video with text clips
    try:
        clips = []
        # Split by sentence punctuation more robustly: split on periods and newlines
        sentences = []
        for part in script.replace("!\n", ".\n").replace("?\n", ".\n").split("."):
            part = part.strip()
            if part:
                sentences.append(part)

        if not sentences:
            sentences = [script]

        for line in sentences:
            wrapped = "\n".join(wrap(line, width=40))
            # Duration: base 3s + extra based on words
            words = len(line.split())
            duration = max(2.5, min(6.0, 2.5 + words / 6.0))
            txt_clip = mp.TextClip(
                wrapped,
                fontsize=40,
                color="white",
                bg_color="black",
                size=(1280, 720),
                method="caption"
            ).set_duration(duration)
            clips.append(txt_clip)

        if not clips:
            print("ERROR: no text clips generated", file=sys.stderr)
            sys.exit(1)

        video = mp.concatenate_videoclips(clips, method="compose")
        video = video.set_audio(mp.AudioFileClip("final_audio.mp3"))
        video.write_videofile("final_video.mp4", fps=24)
        print("INFO: final_video.mp4 created")
    except Exception as e:
        print(f"ERROR creating video: {e}", file=sys.stderr)
        sys.exit(1)

    # Send to Telegram (if tokens available)
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
