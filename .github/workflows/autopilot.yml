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
    
    # Check FFmpeg
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
        
        # Create simple gradient animation
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
        
        log_step(f"Running: {' '.join(cmd[:10])}...")
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
        
        # Try OpenAI API first
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("HF_API_KEY")
        if api_key:
            try:
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
                
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
        
        # Fallback content
        return get_fallback_content(topic)
        
    except Exception as e:
        log_step(f"Content generation error: {e}", "ERROR")
        return get_fallback_content(topic)

def get_fallback_content(topic):
    """Reliable fallback content"""
    
    content_library = {
        "Consumer Rights Protection Laws": """Did you know consumers recovered over 12 billion dollars in 2023?

Here are your key rights you need to know.

You have 30 days to return most defective products.

Companies cannot use fake reviews to trick you.

Always keep receipts as your proof of purchase.

You can report scams to the FTC online easily.

If there's a warranty, they must honor it completely.

Know your consumer rights and save money.

Follow for more legal tips!""",
        
        "Digital Privacy and Data Protection": """Did you know 22 billion records were breached in 2023?

Here's how to protect your digital privacy.

Companies must tell you what data they collect.

You can request to see all your information.

You have the right to delete your data.

Use different passwords for every single account.

Enable two factor authentication on everything important.

Read privacy policies before you click agree.

Your data is valuable so protect it well.

Follow for more legal tips!""",
        
        "Employment Law Basics": """Did you know workers won 2.4 billion in wage theft cases?

Here are your essential workplace rights.

You must be paid at least minimum wage.

Overtime kicks in after 40 hours per week.

Employers cannot discriminate based on age race or gender.

You have the right to a completely safe workplace.

Document any violations you see in writing.

You can file complaints completely anonymously.

Know your worth and demand fair treatment always.

Follow for more legal tips!"""
    }
    
    content = content_library.get(topic, f"""Did you know understanding {topic.lower()} can save you money?

Here's what you need to know right now.

Legal knowledge is power in today's world.

Know your rights before problems happen to you.

Document everything important in writing always.

Seek professional help when you need it most.

Prevention is better than expensive legal battles.

Stay informed and stay protected every day.

Follow for more legal tips!""")
    
    log_step("✅ Using fallback content")
    return content

def create_audio_with_gtts(text, output_path):
    """Create audio narration"""
    try:
        log_step("Creating audio narration...")
        
        from gtts import gTTS
        
        # Clean text
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
    try:
        log_step("Creating final video...")
        
        if not background_path or not os.path.exists(background_path):
            log_step("❌ No background video available", "ERROR")
            return False
            
        if not audio_path or not os.path.exists(audio_path):
            log_step("❌ No audio available", "ERROR")
            return False
        
        # Clean text for overlay
        text_lines = [line.strip() for line in text_content.split('\n') if line.strip()]
        display_text = ' | '.join(text_lines[:3])  # First 3 lines only
        safe_text = display_text.replace("'", "\\'").replace(":", "\\:")[:150]
        
        cmd = [
            'ffmpeg', '-y',
            '-i', background_path,
            '-i', audio_path,
            '-vf', (
                f'drawtext='
                f'text=\'{safe_text}\':'
                f'fontsize=50:'
                f'fontcolor=white:'
                f'bordercolor=black:'
                f'borderw=3:'
                f'x=(w-text_w)/2:'
                f'y=(h-text_h)/2'
            ),
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-shortest',
            '-t', '55',
            '-r', '25',
            output_path
        ]
        
        log_step("Running final video creation...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            log_step(f"✅ Video created: {output_path} ({file_size} bytes)")
            return True
        else:
            log_step(f"❌ Video creation failed: {result.stderr[:300]}", "ERROR")
            return create_simple_fallback_video(output_path, text_content)
            
    except Exception as e:
        log_step(f"❌ Video creation error: {e}", "ERROR")
        return create_simple_fallback_video(output_path, text_content)

def create_simple_fallback_video(output_path, text_content):
    """Create very simple video as last resort"""
    try:
        log_step("Creating simple fallback video...")
        
        # Just text on colored background
        simple_text = text_content.split('\n')[0][:50] if text_content else "Legal Knowledge"
        safe_text = simple_text.replace("'", "\\'").replace(":", "\\:")
        
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', 'color=size=1080x1920:duration=55:rate=25:color=#1e3c72',
            '-vf', f'drawtext=text=\'{safe_text}\':fontsize=80:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2',
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-t', '55',
            '-an',  # No audio
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and os.path.exists(output_path):
            log_step(f"✅ Simple fallback video created: {output_path}")
            return True
        else:
            log_step(f"❌ Even simple video failed: {result.stderr[:200]}", "ERROR")
            return False
            
    except Exception as e:
        log_step(f"❌ Simple fallback failed: {e}", "ERROR")
        return False

def send_to_telegram(video_path, content, topic):
    """Send video to Telegram"""
    try:
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            log_step("❌ Telegram credentials missing", "ERROR")
            return False
        
        log_step("Sending to Telegram...")
        
        caption = f"""🎬 Legal Shorts Video Created!

📚 Topic: {topic}
⏱️ Duration: 55 seconds
📱 Format: YouTube Shorts Ready

Content Preview:
{content[:200]}...

#LegalTips #YouTubeShorts #Law #Rights"""
        
        with open(video_path, 'rb') as video:
            url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
            files = {'video': video}
            data = {'chat_id': chat_id, 'caption': caption}
            
            response = requests.post(url, files=files, data=data, timeout=120)
            
            if response.status_code == 200:
                log_step("✅ Successfully sent to Telegram!")
                return True
            else:
                log_step(f"❌ Telegram send failed: {response.text[:200]}", "ERROR")
                return False
                
    except Exception as e:
        log_step(f"❌ Telegram error: {e}", "ERROR")
        return False

def main():
    """Main execution with comprehensive error handling"""
    try:
        log_step("🚀 STARTING LEGAL VIDEO GENERATION")
        log_step("=" * 50)
        
        # Check dependencies first
        if not check_dependencies():
            log_step("❌ Dependencies check failed - aborting", "ERROR")
            return
        
        # Select topic
        topic = random.choice(LEGAL_TOPICS)
        log_step(f"📚 Selected topic: {topic}")
        
        # Generate content
        content = generate_content(topic)
        log_step(f"📝 Content length: {len(content)} characters")
        
        # Create background video
        background_path = create_simple_background_video()
        if not background_path:
            log_step("❌ Failed to create any background video", "ERROR")
            return
        
        # Create audio
        audio_path = "narration.mp3"
        if not create_audio_with_gtts(content, audio_path):
            log_step("❌ Audio creation failed - continuing without audio", "WARN")
            audio_path = None
        
        # Create final video
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_path = f"legal_shorts_{timestamp}.mp4"
        
        if create_final_video(background_path, audio_path, content, video_path):
            log_step("✅ VIDEO CREATION SUCCESSFUL!")
            
            # Verify video file
            if os.path.exists(video_path):
                file_size = os.path.getsize(video_path)
                log_step(f"📊 Final video: {video_path} ({file_size} bytes)")
                
                if file_size > 10000:  # At least 10KB
                    # Send to Telegram
                    send_to_telegram(video_path, content, topic)
                    
                    # Save metadata
                    metadata = {
                        "timestamp": timestamp,
                        "topic": topic,
                        "content": content,
                        "video_file": video_path,
                        "file_size": file_size,
                        "status": "success"
                    }
                    
                    with open(f"video_metadata_{timestamp}.json", 'w') as f:
                        json.dump(metadata, f, indent=2)
                    
                    log_step("🎉 PROCESS COMPLETED SUCCESSFULLY!")
                    
                else:
                    log_step(f"❌ Video file too small: {file_size} bytes", "ERROR")
            else:
                log_step("❌ Video file not found after creation", "ERROR")
        else:
            log_step("❌ VIDEO CREATION FAILED", "ERROR")
    
    except Exception as e:
        log_step(f"❌ MAIN EXECUTION ERROR: {e}", "ERROR")
        import traceback
        log_step(f"Traceback: {traceback.format_exc()}", "ERROR")
    
    finally:
        log_step("🔄 Cleaning up temporary files...")
        temp_files = ["background.mp4", "static_bg.mp4", "narration.mp3"]
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    log_step(f"Removed: {temp_file}")
                except:
                    pass

if __name__ == "__main__":
    main()
