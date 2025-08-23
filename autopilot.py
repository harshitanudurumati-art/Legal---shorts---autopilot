import os
import json
import random
import requests
import time
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import subprocess

# Configuration
LEGAL_TOPICS = [
    "Consumer Rights Protection Laws",
    "Digital Privacy and Data Protection", 
    "Employment Law Basics",
    "Tenant Rights and Housing Laws",
    "Intellectual Property Rights",
    "Contract Law Fundamentals",
    "Criminal Law Basics",
    "Family Law Essentials"
]

def log_step(message, status="INFO"):
    """Enhanced logging for debugging"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")
    sys.stdout.flush()

def check_dependencies():
    """Check if all required dependencies are available"""
    log_step("Checking system dependencies...")
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            log_step("✅ FFmpeg is available")
            return True
        else:
            log_step("❌ FFmpeg not working properly", "ERROR")
            return False
    except Exception as e:
        log_step(f"❌ FFmpeg check failed: {e}", "ERROR")
        return False

def create_simple_background_video():
    """Create a simple animated background that works reliably"""
    try:
        log_step("Creating simple background video...")
        output_path = "background.mp4"
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', 'color=size=1080x1920:duration=60:rate=25:color=#1e3c72',
            '-vf', (
                'geq='
                'r=128+100*sin(2*PI*t/8):'
                'g=128+80*cos(2*PI*t/10):'
                'b=200+60*sin(2*PI*t/6)'
            ),
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-crf', '28',
            '-t', '60',
            '-pix_fmt', 'yuv420p',
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            log_step(f"✅ Background created: {output_path} ({file_size} bytes)")
            return output_path
        else:
            log_step(f"❌ Background creation failed: {result.stderr[:200]}", "ERROR")
            return create_static_background()
    except Exception as e:
        log_step(f"❌ Error creating background: {e}", "ERROR")
        return create_static_background()

def create_static_background():
    """Create static background as fallback"""
    try:
        log_step("Creating static background fallback...")
        output_path = "static_bg.mp4"
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', 'color=size=1080x1920:duration=60:rate=25:color=#2E86AB',
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-t', '60',
            '-pix_fmt', 'yuv420p',
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        if result.returncode == 0 and os.path.exists(output_path):
            log_step(f"✅ Static background created: {output_path}")
            return output_path
        else:
            log_step(f"❌ Static background failed: {result.stderr[:200]}", "ERROR")
            return None
    except Exception as e:
        log_step(f"❌ Static background error: {e}", "ERROR")
        return None

def generate_content(topic):
    """Generate content with fallback"""
    try:
        log_step(f"Generating content for: {topic}")
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("HF_API_KEY")
        if api_key:
            try:
                headers = {'Authorization': f'Bearer {api_key}','Content-Type': 'application/json'}
                data = {
                    "model": "gpt-3.5-turbo",
                    "messages": [{
                        "role": "user", 
                        "content": f"Create a 50-second YouTube Shorts script about {topic}. Make it engaging with recent examples. Start with 'Did you know' and end with 'Follow for more legal tips!'"
                    }],
                    "max_tokens": 200,
                    "temperature": 0.7
                }
                response = requests.post('https://api.openai.com/v1/chat/completions', 
                                       headers=headers, json=data, timeout=15)
                if response.status_code == 200:
                    content = response.json()['choices'][0]['message']['content'].strip()
                    log_step("✅ Content generated via API")
                    return content
            except Exception as e:
                log_step(f"API failed: {e}", "WARN")
        return get_fallback_content(topic)
    except Exception as e:
        log_step(f"Content generation error: {e}", "ERROR")
        return get_fallback_content(topic)

def get_fallback_content(topic):
    log_step("✅ Using fallback content")
    return f"Did you know about {topic}? Follow for more legal tips!"

def create_audio_with_gtts(text, output_path):
    """Create audio narration"""
    try:
        log_step("Creating audio narration...")
        from gtts import gTTS
        clean_text = text.replace('\n\n', '. ').replace('\n', ' ').strip()
        tts = gTTS(text=clean_text, lang='en', slow=False)
        tts.save(output_path)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            log_step(f"✅ Audio created: {output_path}")
            return True
        else:
            log_step("❌ Audio file too small or missing", "ERROR")
            return False
    except Exception as e:
        log_step(f"❌ Audio creation failed: {e}", "ERROR")
        return False

def create_final_video(background_path, audio_path, text_content, output_path):
    """Create final video with text overlay"""
    log_step(f"DEBUG: Entering create_final_video with background={background_path}, audio={audio_path}")
    try:
        if not background_path or not os.path.exists(background_path):
            log_step("❌ No background video available", "ERROR")
            return False
        if not audio_path or not os.path.exists(audio_path):
            log_step("DEBUG: Bailing because no audio found", "ERROR")
            return False
        # normal ffmpeg code omitted for brevity …
        return False
    except Exception as e:
        log_step(f"❌ Video creation error: {e}", "ERROR")
        return False

def main():
    try:
        log_step("🚀 STARTING LEGAL VIDEO GENERATION")
        if not check_dependencies():
            return
        topic = random.choice(LEGAL_TOPICS)
        log_step(f"📚 Selected topic: {topic}")
        content = generate_content(topic)
        background_path = create_simple_background_video()
        audio_path = "narration.mp3"
        if not create_audio_with_gtts(content, audio_path):
            log_step("❌ Audio creation failed - continuing without audio", "WARN")
            audio_path = None
        log_step(f"DEBUG: audio_path after creation = {audio_path}, exists={os.path.exists(audio_path) if audio_path else 'False'}")
        video_path = f"legal_shorts_test.mp4"
        if create_final_video(background_path, audio_path, content, video_path):
            log_step("✅ VIDEO CREATION SUCCESSFUL!")
        else:
            log_step("❌ VIDEO CREATION FAILED", "ERROR")
    except Exception as e:
        log_step(f"❌ MAIN EXECUTION ERROR: {e}", "ERROR")

if __name__ == "__main__":
    main()
