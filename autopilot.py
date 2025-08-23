import os
import json
import random
import subprocess
import logging
from datetime import datetime
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip, concatenate_videoclips
from gtts import gTTS
from openai import OpenAI

# ---------------- CONFIG ---------------- #
TOPICS_FILE = "topics.json"
TARGET_DURATION = 60  # seconds
BG_VIDEO_FILE = "bg_gradient.mp4"
FINAL_VIDEO_FILE = "final.mp4"

# Logging
logging.basicConfig(level=logging.DEBUG, format='[DEBUG] %(message)s')

# Initialize OpenAI client
logging.debug("Initializing OpenAI client...")
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
logging.debug("OpenAI client initialized ✅")

# ---------------- HELPERS ---------------- #
def load_topics():
    logging.debug("Loading topics from JSON...")
    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        topics = data.get("topics", [])
        if not topics:
            raise ValueError("topics.json is empty or missing 'topics' key")
        logging.debug(f"Loaded {len(topics)} topics")
        return topics

def pick_topic():
    topics = load_topics()
    topic = random.choice(topics)
    logging.debug(f"Selected Topic: {topic}")
    return topic

def run_ffmpeg(cmd):
    logging.debug(f"Running ffmpeg command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logging.debug(f"FFmpeg stderr: {result.stderr}")
        raise RuntimeError(f"FFmpeg failed: {result.stderr}")
    return result

def create_background():
    logging.debug("Creating background video...")
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "color=size=1080x1920:rate=30:duration=60:color=#1e3c72",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-r", "30",
        BG_VIDEO_FILE
    ]
    try:
        run_ffmpeg(cmd)
        logging.debug(f"Background video created: {BG_VIDEO_FILE}")
    except RuntimeError as e:
        logging.debug(f"Background creation failed: {e}")
        # fallback to blank video
        logging.debug("Creating fallback blank background")
        with open(BG_VIDEO_FILE, "wb") as f:
            f.write(b"")  # minimal placeholder
    return BG_VIDEO_FILE

def generate_narration(script_text, lang="en"):
    logging.debug("Generating audio narration...")
    tts = gTTS(script_text, lang=lang)
    audio_file = "narration.mp3"
    tts.save(audio_file)
    logging.debug(f"Audio saved: {audio_file}")
    return audio_file

def generate_script(topic):
    logging.debug(f"Generating script for topic: {topic}")
    prompt = f"Give a 1-minute interesting explanation, example, or fact about '{topic}' in simple language."
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        script_text = response.choices[0].message.content.strip()
        logging.debug(f"Generated script ({len(script_text.split())} words)")
        return script_text
    except Exception as e:
        logging.debug(f"OpenAI API failed: {e}")
        # fallback minimal script
        return f"This is an interesting fact about {topic}."

def create_video(bg_path, audio_path, script_text, out_file):
    logging.debug("Creating final video with text overlay and narration...")
    video_clip = VideoFileClip(bg_path).subclip(0, TARGET_DURATION)
    audio_clip = AudioFileClip(audio_path)

    # Split script into chunks for overlay
    lines = script_text.split(". ")
    text_clips = []
    duration_per_line = TARGET_DURATION / max(len(lines), 1)
    for i, line in enumerate(lines):
        txt_clip = TextClip(line, fontsize=50, color="white", method="caption", size=(1080, None))
        txt_clip = txt_clip.set_position("center").set_start(i * duration_per_line).set_duration(duration_per_line)
        text_clips.append(txt_clip)

    final = CompositeVideoClip([video_clip, *text_clips])
    final = final.set_audio(audio_clip)
    final.write_videofile(out_file, fps=30, codec="libx264", audio_codec="aac")
    logging.debug(f"Final video created: {out_file}")
    return out_file

# ---------------- MAIN ---------------- #
def main():
    logging.debug("=== Autopilot run started ===")
    topic = pick_topic()
    script = generate_script(topic)
    narration = generate_narration(script)
    bg_video = create_background()
    final_video = create_video(bg_video, narration, script, FINAL_VIDEO_FILE)
    logging.debug("=== Autopilot run finished ===")
    logging.debug(f"Video saved at: {final_video}")

if __name__ == "__main__":
    main()
