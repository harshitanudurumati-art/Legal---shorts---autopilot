import os
import json
import random
import requests
import time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import subprocess
import tempfile
import textwrap

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

# Background video URLs (free stock videos)
BACKGROUND_VIDEOS = [
    "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
]

def download_background_video():
    """Download a random background video"""
    try:
        video_url = "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4"
        response = requests.get(video_url, stream=True, timeout=30)
        
        if response.status_code == 200:
            with open("bg_video.mp4", "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return "bg_video.mp4"
        else:
            # Create animated gradient background instead
            return create_animated_background()
    except:
        return create_animated_background()

def create_animated_background():
    """Create animated gradient background using FFmpeg"""
    try:
        # Create animated gradient background
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', 'color=size=1080x1920:duration=60:rate=30:color=#1e3c72',
            '-vf', 'geq=r=\'128+100*sin(2*PI*t/10)\':g=\'128+100*cos(2*PI*t/10)\':b=\'200+50*sin(2*PI*t/5)\'',
            '-t', '60',
            'animated_bg.mp4'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return "animated_bg.mp4"
        else:
            # Fallback to static background
            return create_static_background()
    except:
        return create_static_background()

def create_static_background():
    """Create static professional background"""
    try:
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', 'color=size=1080x1920:duration=60:rate=30:color=#2E86AB',
            '-vf', 'drawbox=x=0:y=0:w=1080:h=1920:color=#A23B72@0.3:t=fill',
            'static_bg.mp4'
        ]
        
        subprocess.run(cmd, capture_output=True)
        return "static_bg.mp4"
    except:
        return None

def download_background_music():
    """Download copyright-free background music"""
    try:
        # Using a royalty-free music API or direct link
        music_urls = [
            "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav",
            "https://file-examples.com/storage/fe68c2b69d66d818a89f2dd/2017/11/file_example_MP3_700KB.mp3"
        ]
        
        for url in music_urls:
            try:
                response = requests.get(url, stream=True, timeout=20)
                if response.status_code == 200:
                    extension = url.split('.')[-1]
                    filename = f"bg_music.{extension}"
                    
                    with open(filename, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    # Convert to mp3 if needed
                    if extension != 'mp3':
                        subprocess.run([
                            'ffmpeg', '-y', '-i', filename, 
                            '-acodec', 'mp3', '-ab', '128k', 
                            'bg_music.mp3'
                        ], capture_output=True)
                        return "bg_music.mp3"
                    
                    return filename
            except:
                continue
                
        # Create simple tone as fallback
        return create_simple_music()
        
    except Exception as e:
        print(f"Error downloading music: {e}")
        return create_simple_music()

def create_simple_music():
    """Create simple background music tone"""
    try:
        # Create a simple sine wave tone
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', 'sine=frequency=440:duration=60',
            '-af', 'volume=0.1',
            'simple_music.mp3'
        ]
        
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode == 0:
            return "simple_music.mp3"
        return None
    except:
        return None

def create_text_overlay_video(text_content, duration=55):
    """Create text overlay with animated text"""
    try:
        # Split content into sentences for animated display
        sentences = text_content.split('. ')
        
        # Create text file for FFmpeg
        text_parts = []
        time_per_sentence = duration / len(sentences) if sentences else duration
        
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                start_time = i * time_per_sentence
                end_time = (i + 1) * time_per_sentence
                
                # Wrap text for better display
                wrapped_text = textwrap.fill(sentence.strip(), width=25)
                
                text_parts.append({
                    'text': wrapped_text,
                    'start': start_time,
                    'end': end_time
                })
        
        return text_parts
        
    except Exception as e:
        print(f"Error creating text overlay: {e}")
        return [{'text': text_content[:100], 'start': 0, 'end': duration}]

def create_professional_video(background_path, audio_path, text_content, output_path, music_path=None):
    """Create professional YouTube Shorts video with text overlays and background music"""
    try:
        # Get text overlays
        text_overlays = create_text_overlay_video(text_content)
        
        # Build FFmpeg filter complex
        filter_parts = []
        
        # Base video scaling and formatting
        if background_path:
            filter_parts.append(f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[bg]")
        else:
            # Create solid color background if no video
            filter_parts.append("[0:v]color=size=1080x1920:duration=60:rate=30:color=#2E86AB[bg]")
        
        # Add text overlays
        current_input = "[bg]"
        for i, text_data in enumerate(text_overlays):
            text_escaped = text_data['text'].replace("'", "\\'").replace(":", "\\:")
            
            text_filter = (
                f"{current_input}drawtext="
                f"text='{text_escaped}':"
                f"fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf':"
                f"fontsize=60:"
                f"fontcolor=white:"
                f"bordercolor=black:"
                f"borderw=3:"
                f"x=(w-text_w)/2:"
                f"y=(h-text_h)/2:"
                f"enable='between(t,{text_data['start']},{text_data['end']})'[text{i}]"
            )
            filter_parts.append(text_filter)
            current_input = f"[text{i}]"
        
        # Build FFmpeg command
        cmd = ['ffmpeg', '-y']
        
        # Input files
        if background_path and os.path.exists(background_path):
            cmd.extend(['-i', background_path])
        else:
            cmd.extend(['-f', 'lavfi', '-i', 'color=size=1080x1920:duration=60:rate=30:color=#2E86AB'])
        
        cmd.extend(['-i', audio_path])
        
        if music_path and os.path.exists(music_path):
            cmd.extend(['-i', music_path])
        
        # Add filter complex
        cmd.extend(['-filter_complex', ';'.join(filter_parts)])
        
        # Audio mixing
        if music_path and os.path.exists(music_path):
            cmd.extend([
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-af', '[1:a][2:a]amix=inputs=2:duration=first:dropout_transition=2[a]',
                '-map', current_input.replace('[', '').replace(']', ''),
                '-map', '[a]',
                '-t', '55',
                '-r', '30',
                output_path
            ])
        else:
            cmd.extend([
                '-c:v', 'libx264',
                '-preset', 'fast', 
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-map', current_input.replace('[', '').replace(']', ''),
                '-map', '1:a',
                '-t', '55',
                '-r', '30',
                output_path
            ])
        
        print(f"Running FFmpeg command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Professional video created: {output_path}")
            return True
        else:
            print(f"FFmpeg error: {result.stderr}")
            # Try simpler version
            return create_simple_video_fallback(background_path, audio_path, output_path)
            
    except Exception as e:
        print(f"Error creating professional video: {e}")
        return create_simple_video_fallback(background_path, audio_path, output_path)

def create_simple_video_fallback(background_path, audio_path, output_path):
    """Fallback simple video creation"""
    try:
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi', '-i', 'color=size=1080x1920:duration=55:rate=30:color=#4158D0',
            '-i', audio_path,
            '-vf', 'drawtext=text=\'LEGAL KNOWLEDGE\':fontsize=80:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2',
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-t', '55',
            '-shortest',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
        
    except Exception as e:
        print(f"Fallback video creation failed: {e}")
        return False

def generate_content_with_openai(topic):
    """Generate engaging content for YouTube Shorts"""
    try:
        headers = {
            'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY", os.getenv("HF_API_KEY"))}',
            'Content-Type': 'application/json'
        }
        
        prompt = f"""Create an engaging 45-second YouTube Shorts script about {topic}. 
        Format: Hook + 3 Key Points + Call to Action
        Make it punchy, use simple language, include specific examples.
        Start with "Did you know..." or "Here's what you need to know about..."
        End with "Follow for more legal tips!"
        Keep sentences short for better text display."""
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 200,
            "temperature": 0.7
        }
        
        response = requests.post('https://api.openai.com/v1/chat/completions', 
                               headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            return content.strip()
        else:
            return generate_fallback_content(topic)
            
    except Exception as e:
        print(f"Error with OpenAI: {e}")
        return generate_fallback_content(topic)

def generate_fallback_content(topic):
    """Generate engaging fallback content"""
    hooks = [
        "Did you know your rights might be stronger than you think?",
        "Here's what every person should know about",
        "Don't get caught off guard! Learn about",
        "Protect yourself by understanding"
    ]
    
    content_data = {
        "Consumer Rights Protection Laws": f"{random.choice(hooks)} consumer protection! You can return defective products within warranty periods. Companies cannot use misleading advertising. You have the right to fair pricing and quality products. Always keep your receipts as proof of purchase. Know your local consumer laws. Follow for more legal tips!",
        
        "Digital Privacy and Data Protection": f"{random.choice(hooks)} your digital privacy! Companies must tell you what data they collect about you. You can request to see your personal data. You have the right to delete your information. Read privacy policies before agreeing. Use strong passwords and two-factor authentication. Follow for more legal tips!",
        
        "Employment Law Basics": f"{random.choice(hooks)} workplace rights! You deserve fair wages for your work. Employers must provide safe working conditions. Discrimination based on race, gender, or age is illegal. You have the right to organize with coworkers. Document any workplace violations. Follow for more legal tips!",
        
        "Tenant Rights and Housing Laws": f"{random.choice(hooks)} tenant rights! Landlords must give 24-hour notice before entering your home. They cannot evict you without proper legal procedures. You have the right to livable housing conditions. Security deposits must be returned within legal timeframes. Document everything in writing. Follow for more legal tips!"
    }
    
    return content_data.get(topic, f"{random.choice(hooks)} {topic.lower()}! This is crucial legal knowledge that can protect your rights and interests. Understanding these laws helps you make informed decisions and avoid legal problems. Stay informed and know your rights. Follow for more legal tips!")

def create_audio_with_gtts(text, output_path):
    """Create audio with better pacing for YouTube Shorts"""
    try:
        from gtts import gTTS
        
        # Clean text for better speech
        clean_text = text.replace('!', '. ').replace('?', '. ')
        
        tts = gTTS(text=clean_text, lang='en', slow=False)
        temp_audio = "temp_audio.mp3"
        tts.save(temp_audio)
        
        # Adjust audio speed and add slight echo for better sound
        cmd = [
            'ffmpeg', '-y',
            '-i', temp_audio,
            '-af', 'atempo=1.1,aecho=0.8:0.88:60:0.4',
            '-c:a', 'mp3',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True)
        
        # Cleanup
        if os.path.exists(temp_audio):
            os.remove(temp_audio)
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error creating audio: {e}")
        return False

def send_to_telegram(video_path, content_text, topic):
    """Send professional video package to Telegram"""
    try:
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            print("Telegram credentials not found")
            return False
        
        # Create YouTube-ready caption
        youtube_caption = f"""🎯 NEW LEGAL SHORTS VIDEO READY!

📚 Topic: {topic}
⏱️ Duration: 55 seconds  
📱 Format: YouTube Shorts (9:16)
🎬 Ready to upload!

💡 SUGGESTED TITLE: "Know Your Rights: {topic} Explained in 60 Seconds"

📝 DESCRIPTION:
{content_text[:200]}...

#LegalTips #Rights #Law #Education #Shorts #Legal #KnowYourRights #LegalAdvice

🔥 UPLOAD TIME: 7:30 PM IST for maximum engagement!"""
        
        with open(video_path, 'rb') as video:
            url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
            files = {'video': video}
            data = {
                'chat_id': chat_id,
                'caption': youtube_caption
            }
            
            response = requests.post(url, files=files, data=data, timeout=60)
            return response.status_code == 200
            
    except Exception as e:
        print(f"Error sending to Telegram: {e}")
        return False

def main():
    """Main execution with professional video creation"""
    print("🚀 Starting Professional Legal Shorts Generation...")
    
    try:
        # Select topic
        topic = random.choice(LEGAL_TOPICS)
        print(f"📚 Topic: {topic}")
        
        # Generate content
        print("✍️ Generating engaging content...")
        content = generate_content_with_openai(topic)
        print(f"Content preview: {content[:100]}...")
        
        # Download/create background
        print("🎬 Setting up background video...")
        background_path = download_background_video()
        
        # Download background music
        print("🎵 Setting up background music...")
        music_path = download_background_music()
        
        # Create audio
        print("🎤 Creating professional audio...")
        audio_path = "narration.mp3"
        if not create_audio_with_gtts(content, audio_path):
            print("❌ Audio creation failed")
            return
        
        # Create professional video
        print("🎥 Creating professional YouTube Shorts video...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_path = f"legal_shorts_{timestamp}.mp4"
        
        if create_professional_video(background_path, audio_path, content, video_path, music_path):
            print(f"✅ Professional video created: {video_path}")
            
            # Send to Telegram
            print("📤 Sending to Telegram with YouTube package...")
            if send_to_telegram(video_path, content, topic):
                print("✅ Successfully sent to Telegram!")
            
            # Save metadata
            metadata = {
                "topic": topic,
                "content": content,
                "timestamp": timestamp,
                "video_file": video_path,
                "youtube_title": f"Know Your Rights: {topic} Explained in 60 Seconds",
                "youtube_description": content,
                "hashtags": "#LegalTips #Rights #Law #Education #Shorts #Legal #KnowYourRights #LegalAdvice",
                "upload_time": "7:30 PM IST",
                "status": "ready_for_youtube"
            }
            
            with open(f"youtube_package_{timestamp}.json", 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print("🎉 PROFESSIONAL YOUTUBE SHORTS VIDEO READY!")
            print(f"📱 Upload at 7:30 PM IST for maximum engagement!")
            
        else:
            print("❌ Video creation failed")
    
    except Exception as e:
        print(f"❌ Error in main execution: {e}")
    
    finally:
        # Cleanup temporary files
        temp_files = ["bg_video.mp4", "animated_bg.mp4", "static_bg.mp4", "narration.mp3", "bg_music.mp3", "simple_music.mp3"]
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass

if __name__ == "__main__":
    main()
