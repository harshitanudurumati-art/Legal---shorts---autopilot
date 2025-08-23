import os
import json
import random
import subprocess
from datetime import datetime
import moviepy.editor as mp
from gtts import gTTS

# ===================== CONFIG =====================
TARGET_DURATION = 60  # seconds
OUTPUT_FILE = "final.mp4"
BG_VIDEO = "bg_gradient.mp4"
TOPICS_FILE = "topics.json"
DEBUG = True

# ===================== HELPER FUNCTIONS =====================
def debug_print(msg):
    if DEBUG:
        print(f"[DEBUG] {msg}")

def run_ffmpeg(cmd):
    debug_print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        debug_print(f"FFmpeg error:\n{result.stderr}")
        return False
    return True

def create_gradient_bg(output_file=BG_VIDEO, duration=TARGET_DURATION):
    debug_print("Creating gradient background video...")
    cmd = (
        f"ffmpeg -y -f lavfi -i color=c=blue:s=1080x1920:d={duration}:r=30 "
        f"-vf format=yuv420p {output_file}"
    )
    if not run_ffmpeg(cmd):
        debug_print("Failed to create gradient background, using blank fallback.")
        # fallback: create 1s blank video repeated
        cmd_fb = (
            f"ffmpeg -y -f lavfi -i color=c=black:s=1080x1920:d=1 "
            f"-vf format=yuv420p,loop=60:1:0 {output_file}"
        )
        run_ffmpeg(cmd_fb)
    return output_file

def pick_topic():
    debug_print("Picking a random topic...")
    if not os.path.exists(TOPICS_FILE):
        debug_print(f"{TOPICS_FILE} missing!")
        return "General Law Topic"
    with open(TOPICS_FILE, "r") as f:
        topics = json.load(f)
    if not topics:
        return "General Law Topic"
    topic = random.choice(topics)
    debug_print(f"Selected Topic: {topic}")
    return topic

def generate_script(topic):
    debug_print(f"Generating script for topic: {topic}")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        prompt = (
            f"Explain the topic '{topic}' in an interesting way with examples, "
            f"for a 1-minute narrated video."
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )
        text = response.choices[0].message.content.strip()
        if len(text.split()) < 20:
            raise Exception("Too short")
    except Exception as e:
        debug_print(f"OpenAI failed: {e}")
        text = (
            f"{topic} is an important topic in law. "
            f"Understanding it can help people protect their rights. "
            f"For example, if a tenant faces unfair treatment by a landlord, "
            f"knowing their rights allows them to take appropriate action legally. "
            f"Always consult proper legal guidance for your situations."
        )
    debug_print(f"Generated script ({len(text.split())} words)")
    return text

def create_narration(script, filename="narration.mp3"):
    debug_print("Generating narration audio...")
    tts = gTTS(text=script, lang="en")
    tts.save(filename)
    return filename

def overlay_text_on_video(bg_path, script, out_file=OUTPUT_FILE):
    debug_print("Creating final video with text overlay...")
    video_clip = mp.VideoFileClip(bg_path).subclip(0, TARGET_DURATION)
    
    txt_clip = mp.TextClip(
        script,
        fontsize=50,
        color='white',
        method='caption',
        size=(video_clip.w - 100, None),
        align='center'
    ).set_position(("center","bottom")).set_duration(TARGET_DURATION)
    
    final_clip = mp.CompositeVideoClip([video_clip, txt_clip])
    
    return final_clip

def create_video(bg_path, narration_path, script, out_file=OUTPUT_FILE):
    final_clip = overlay_text_on_video(bg_path, script, out_file)
    
    # Add audio
    audio_clip = mp.AudioFileClip(narration_path).subclip(0, TARGET_DURATION)
    final_clip = final_clip.set_audio(audio_clip)
    
    debug_print(f"Writing final video to {out_file}...")
    final_clip.write_videofile(
        out_file, 
        fps=30,
        codec="libx264",
        audio_codec="aac"
    )
    return out_file

# ===================== MAIN =====================
def main():
    debug_print("=== Autopilot run started ===")
    topic = pick_topic()
    script = generate_script(topic)
    bg_video = create_gradient_bg()
    narration = create_narration(script)
    final_video = create_video(bg_video, narration, script)
    debug_print(f"Video creation completed: {final_video}")

if __name__ == "__main__":
    main()
