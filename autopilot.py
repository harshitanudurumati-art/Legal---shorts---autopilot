import os
import json
import random
import requests
import time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import subprocess
import tempfile
import re

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

# External video resources for backgrounds (royalty-free)
BACKGROUND_VIDEO_SOURCES = {
    "Consumer Rights Protection Laws": [
        "https://pixabay.com/videos/download/video-41758_source.mp4?attachment",  # Shopping/retail
        "https://pixabay.com/videos/download/video-28745_source.mp4?attachment"   # Money/finance
    ],
    "Digital Privacy and Data Protection": [
        "https://pixabay.com/videos/download/video-41062_source.mp4?attachment",  # Technology/cyber
        "https://pixabay.com/videos/download/video-27693_source.mp4?attachment"   # Digital/data
    ],
    "Employment Law Basics": [
        "https://pixabay.com/videos/download/video-34521_source.mp4?attachment",  # Office/work
        "https://pixabay.com/videos/download/video-28934_source.mp4?attachment"   # Business/meeting
    ],
    "Tenant Rights and Housing Laws": [
        "https://pixabay.com/videos/download/video-39847_source.mp4?attachment",  # Real estate/housing
        "https://pixabay.com/videos/download/video-25698_source.mp4?attachment"   # Home/property
    ],
    "default": [
        "https://pixabay.com/videos/download/video-15197_source.mp4?attachment",  # Justice/scales
        "https://pixabay.com/videos/download/video-28745_source.mp4?attachment"   # Business/law
    ]
}

def download_relevant_background_video(topic):
    """Download contextually relevant background video"""
    try:
        print(f"🎬 Finding relevant background for: {topic}")
        
        # Get topic-specific videos or fallback to default
        video_urls = BACKGROUND_VIDEO_SOURCES.get(topic, BACKGROUND_VIDEO_SOURCES["default"])
        
        for i, url in enumerate(video_urls):
            try:
                print(f"📥 Downloading background video {i+1}...")
                response = requests.get(url, stream=True, timeout=45)
                
                if response.status_code == 200:
                    filename = f"background_{topic.lower().replace(' ', '_')}.mp4"
                    
                    with open(filename, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    # Verify video file
                    if os.path.getsize(filename) > 1000:  # At least 1KB
                        print(f"✅ Downloaded: {filename}")
                        return prepare_background_video(filename, topic)
                    else:
                        os.remove(filename)
                        
            except Exception as e:
                print(f"❌ Failed to download video {i+1}: {e}")
                continue
        
        # Fallback: Create animated legal-themed background
        return create_legal_themed_background(topic)
        
    except Exception as e:
        print(f"Error downloading background: {e}")
        return create_legal_themed_background(topic)

def prepare_background_video(video_path, topic):
    """Prepare and optimize background video for YouTube Shorts"""
    try:
        output_path = f"prepared_bg_{topic.lower().replace(' ', '_')}.mp4"
        
        # Create engaging background with overlays
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-vf', (
                'scale=1080:1920:force_original_aspect_ratio=increase,'
                'crop=1080:1920,'
                'setsar=1,'
                'colorbalance=rs=0.1:gs=0.1:bs=0.1,'  # Slight color grading
                'curves=all=0/0.1 0.5/0.4 1/0.9,'     # Cinematic curve
                'overlay=color=black@0.2'              # Dark overlay for text readability
            ),
            '-t', '60',
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '28',
            '-r', '30',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(output_path):
            print(f"✅ Background video prepared: {output_path}")
            # Clean up original
            if os.path.exists(video_path):
                os.remove(video_path)
            return output_path
        else:
            print(f"❌ Background preparation failed: {result.stderr}")
            return create_legal_themed_background(topic)
            
    except Exception as e:
        print(f"Error preparing background: {e}")
        return create_legal_themed_background(topic)

def create_legal_themed_background(topic):
    """Create animated legal-themed background as fallback"""
    try:
        print("🎨 Creating legal-themed animated background...")
        
        # Topic-specific color schemes
        color_schemes = {
            "Consumer Rights Protection Laws": "#FF6B35,#F7931E,#FFD23F",      # Orange/yellow (shopping)
            "Digital Privacy and Data Protection": "#4ECDC4,#44A08D,#093637",  # Teal/green (tech)
            "Employment Law Basics": "#667eea,#764ba2,#f093fb",               # Purple/blue (corporate)
            "Tenant Rights and Housing Laws": "#ffecd2,#fcb69f,#ff8a80",      # Warm (home)
            "default": "#1e3c72,#2a5298,#6b73ff"                              # Professional blue
        }
        
        colors = color_schemes.get(topic, color_schemes["default"])
        
        output_path = f"legal_bg_{topic.lower().replace(' ', '_')}.mp4"
        
        # Create animated gradient with legal symbols
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', f'color=size=1080x1920:duration=60:rate=30:color={colors.split(",")[0]}',
            '-vf', (
                f'geq=r=\'128+100*sin(2*PI*t/8)\':'
                f'g=\'128+80*cos(2*PI*t/10)\':'
                f'b=\'200+60*sin(2*PI*t/6)\','
                'drawtext=text=⚖️:fontsize=120:fontcolor=white@0.3:'
                'x=w/2-text_w/2:y=h/4:enable=mod(floor(t*2)\\,4)=0,'
                'drawtext=text=📋:fontsize=100:fontcolor=white@0.2:'
                'x=w/4-text_w/2:y=3*h/4:enable=mod(floor(t*2+1)\\,4)=0,'
                'drawtext=text=🏛️:fontsize=110:fontcolor=white@0.25:'
                'x=3*w/4-text_w/2:y=h/2:enable=mod(floor(t*2+2)\\,4)=0'
            ),
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '28',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Legal background created: {output_path}")
            return output_path
        else:
            print(f"❌ Legal background creation failed: {result.stderr}")
            return create_simple_gradient_background()
            
    except Exception as e:
        print(f"Error creating legal background: {e}")
        return create_simple_gradient_background()

def create_simple_gradient_background():
    """Simple gradient fallback"""
    try:
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', 'color=size=1080x1920:duration=60:rate=30:color=#1e3c72',
            '-vf', 'geq=r=128+100*sin(2*PI*t/10):g=128+100*cos(2*PI*t/10):b=200+50*sin(2*PI*t/5)',
            'simple_gradient.mp4'
        ]
        
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode == 0:
            return "simple_gradient.mp4"
        return None
    except:
        return None

def download_background_music(topic):
    """Download topic-relevant background music"""
    try:
        print("🎵 Getting background music...")
        
        # Topic-specific music moods
        music_urls = {
            "Corporate/Professional": [
                "https://www.bensound.com/bensound-music/bensound-corporate.mp3",
                "https://www.bensound.com/bensound-music/bensound-inspire.mp3"
            ],
            "Tech/Digital": [
                "https://www.bensound.com/bensound-music/bensound-tech.mp3",
                "https://www.bensound.com/bensound-music/bensound-futuristic.mp3"
            ],
            "default": [
                "https://www.bensound.com/bensound-music/bensound-straight.mp3"
            ]
        }
        
        # Determine music category based on topic
        if "Digital" in topic or "Privacy" in topic:
            category = "Tech/Digital"
        elif "Employment" in topic or "Consumer" in topic:
            category = "Corporate/Professional"
        else:
            category = "default"
        
        urls = music_urls.get(category, music_urls["default"])
        
        for url in urls:
            try:
                response = requests.get(url, stream=True, timeout=30)
                if response.status_code == 200:
                    with open("bg_music.mp3", "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    if os.path.getsize("bg_music.mp3") > 5000:  # At least 5KB
                        return "bg_music.mp3"
                    else:
                        os.remove("bg_music.mp3")
            except:
                continue
        
        # Fallback: Create simple ambient tone
        return create_ambient_music()
        
    except Exception as e:
        print(f"Error downloading music: {e}")
        return create_ambient_music()

def create_ambient_music():
    """Create subtle ambient background music"""
    try:
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', 'sine=frequency=220:duration=60',
            '-f', 'lavfi',
            '-i', 'sine=frequency=330:duration=60',
            '-filter_complex', '[0:a][1:a]amix=inputs=2,volume=0.05',
            'ambient_music.mp3'
        ]
        
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode == 0:
            return "ambient_music.mp3"
        return None
    except:
        return None

def generate_engaging_content_with_examples(topic):
    """Generate content with recent examples and interesting cases"""
    try:
        # Use OpenAI/HF API with specific prompt for examples
        headers = {
            'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY", os.getenv("HF_API_KEY"))}',
            'Content-Type': 'application/json'
        }
        
        current_year = datetime.now().year
        
        prompt = f"""Create a 50-60 second YouTube Shorts script about {topic}.

Requirements:
- Include a recent real example or case from {current_year-1}-{current_year}
- Start with a strong hook: "Did you know..." or "In 2024..."  
- Mention specific numbers, dates, or statistics
- Include 3-4 key practical tips
- End with "Follow for more legal tips!"
- Write in short, punchy sentences
- Make it conversational and engaging

Format each sentence on a new line for text display."""
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 250,
            "temperature": 0.8
        }
        
        response = requests.post('https://api.openai.com/v1/chat/completions', 
                               headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content'].strip()
            return format_content_for_display(content)
        else:
            print(f"API Error: {response.text}")
            return generate_fallback_content_with_examples(topic)
            
    except Exception as e:
        print(f"Error generating content: {e}")
        return generate_fallback_content_with_examples(topic)

def generate_fallback_content_with_examples(topic):
    """Generate engaging fallback content with examples"""
    
    current_year = datetime.now().year
    
    content_with_examples = {
        "Consumer Rights Protection Laws": f"""Did you know in {current_year-1}, consumers got $12 billion back from companies?
        
Here's what you need to know.

You have 30 days to return most defective products.

Companies cannot use fake reviews to mislead you.

If a warranty exists, they must honor it.

Keep all receipts and emails as proof.

You can report scams to the FTC online.

Know your rights, save your money.

Follow for more legal tips!""",
        
        "Digital Privacy and Data Protection": f"""In {current_year-1}, data breaches exposed 22 billion records.

Here's how to protect yourself.

Companies must tell you what data they collect.

You can request to see all your personal information.

You have the right to delete your data.

Use different passwords for each account.

Enable two-factor authentication everywhere.

Read privacy policies before clicking agree.

Your data is valuable, protect it.

Follow for more legal tips!""",
        
        "Employment Law Basics": f"""Did you know workers won $2.4 billion in wage theft cases in {current_year-1}?

Here are your key rights.

You must be paid at least minimum wage.

Overtime kicks in after 40 hours per week.

Employers cannot discriminate based on age, race, or gender.

You have the right to a safe workplace.

Document any violations in writing.

You can file complaints anonymously.

Know your worth, demand fair treatment.

Follow for more legal tips!"""
    }
    
    return format_content_for_display(
        content_with_examples.get(topic, f"""Legal knowledge is power in {current_year}.

Understanding {topic.lower()} protects you from costly mistakes.

Here are the key things to remember.

Know your rights before problems arise.

Document everything important in writing.

Seek help when you need it.

Prevention is better than legal battles.

Stay informed, stay protected.

Follow for more legal tips!""")
    )

def format_content_for_display(content):
    """Format content for word-by-word display"""
    # Split into sentences and clean up
    sentences = [s.strip() for s in content.split('.') if s.strip()]
    
    formatted_sentences = []
    for sentence in sentences:
        if sentence and not sentence.endswith('!') and not sentence.endswith('?'):
            sentence += '.'
        formatted_sentences.append(sentence)
    
    return formatted_sentences

def create_word_by_word_video(background_path, sentences, output_path, music_path=None):
    """Create video with word-by-word text synchronization"""
    try:
        print("🎬 Creating word-by-word synchronized video...")
        
        # Calculate timing
        total_duration = 55  # seconds
        total_words = sum(len(sentence.split()) for sentence in sentences)
        words_per_second = total_words / total_duration
        
        # Build text overlays for each sentence
        filter_parts = []
        current_time = 0
        
        # Start with background
        filter_parts.append(f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[bg]")
        
        current_layer = "[bg]"
        
        for i, sentence in enumerate(sentences):
            words = sentence.split()
            sentence_duration = len(words) / words_per_second
            
            # Create sentence overlay
            sentence_text = sentence.replace("'", "\\'").replace(":", "\\:")
            
            # Large, bold text with strong outline
            text_filter = (
                f"{current_layer}drawtext="
                f"text='{sentence_text}':"
                f"fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf':"
                f"fontsize=65:"
                f"fontcolor=white:"
                f"bordercolor=black:"
                f"borderw=4:"
                f"x=(w-text_w)/2:"
                f"y=(h-text_h)/2+{(i%3-1)*200}:"  # Stagger text positions
                f"enable='between(t,{current_time},{current_time + sentence_duration})':"
                f"alpha='fade(in,{current_time},{current_time + 0.3})*fade(out,{current_time + sentence_duration - 0.3},{current_time + sentence_duration})'[text{i}]"
            )
            
            filter_parts.append(text_filter)
            current_layer = f"[text{i}]"
            current_time += sentence_duration
        
        # Build FFmpeg command
        cmd = ['ffmpeg', '-y', '-i', background_path]
        
        if music_path and os.path.exists(music_path):
            cmd.extend(['-i', music_path])
        
        # Add filter complex
        cmd.extend(['-filter_complex', ';'.join(filter_parts)])
        
        # Output settings
        if music_path and os.path.exists(music_path):
            cmd.extend([
                '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
                '-c:a', 'aac', '-b:a', '128k',
                '-af', f'[1:a]volume=0.3[bgm];anullsrc=channel_layout=stereo:sample_rate=44100[silence];[silence][bgm]amix=inputs=2:duration=first[a]',
                '-map', current_layer.replace('[', '').replace(']', ''),
                '-map', '[a]',
                '-t', str(total_duration),
                '-r', '30',
                output_path
            ])
        else:
            cmd.extend([
                '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
                '-an',  # No audio for now
                '-map', current_layer.replace('[', '').replace(']', ''),
                '-t', str(total_duration),
                '-r', '30',
                output_path
            ])
        
        print(f"🎥 Running video creation command...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Word-synchronized video created: {output_path}")
            return True
        else:
            print(f"❌ Video creation failed: {result.stderr}")
            return create_simple_text_video_fallback(background_path, sentences, output_path)
            
    except Exception as e:
        print(f"Error creating word-by-word video: {e}")
        return create_simple_text_video_fallback(background_path, sentences, output_path)

def create_simple_text_video_fallback(background_path, sentences, output_path):
    """Simple fallback video creation"""
    try:
        # Join all sentences
        full_text = " ".join(sentences).replace("'", "\\'").replace(":", "\\:")
        
        cmd = [
            'ffmpeg', '-y',
            '-i', background_path if background_path else '-f',
            '-f' if not background_path else '',
            'lavfi' if not background_path else '',
            '-i' if not background_path else '',
            'color=size=1080x1920:duration=55:rate=30:color=#1e3c72' if not background_path else '',
            '-vf', f'drawtext=text=\'{full_text[:200]}...\':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=50:fontcolor=white:bordercolor=black:borderw=3:x=(w-text_w)/2:y=(h-text_h)/2',
            '-c:v', 'libx264',
            '-t', '55',
            output_path
        ]
        
        # Clean up command
        cmd = [x for x in cmd if x]  # Remove empty strings
        
        result = subprocess.run(cmd, capture_output=True)
        return result.returncode == 0
        
    except Exception as e:
        print(f"Fallback creation failed: {e}")
        return False

def send_to_telegram_with_package(video_path, sentences, topic):
    """Send complete video package to Telegram"""
    try:
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            print("Telegram credentials not found")
            return False
        
        content_preview = " ".join(sentences)[:300]
        
        youtube_package = f"""🔥 VIRAL LEGAL SHORTS VIDEO READY!

📚 Topic: {topic}
⏱️ Duration: 55 seconds
📱 Format: 9:16 YouTube Shorts
🎯 Engagement: Word-by-word text sync

💡 TITLE: "{topic} Explained in 60 Seconds | Know Your Rights"

📝 DESCRIPTION:
{content_preview}...

🏷️ TAGS: #LegalTips #KnowYourRights #Shorts #Law #Legal #Rights #Education #Viral #YoutubeShorts #LegalAdvice

🕰️ BEST UPLOAD TIME: 7:30 PM IST
📊 TARGET: 100K+ views (legal niche is underserved!)
🎬 STYLE: Professional with synchronized text

Ready for upload! 🚀"""
        
        with open(video_path, 'rb') as video:
            url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
            files = {'video': video}
            data = {
                'chat_id': chat_id,
                'caption': youtube_package
            }
            
            response = requests.post(url, files=files, data=data, timeout=120)
            return response.status_code == 200
            
    except Exception as e:
        print(f"Error sending to Telegram: {e}")
        return False

def main():
    """Main execution - Professional YouTube Shorts Creator"""
    print("🎬 STARTING PROFESSIONAL YOUTUBE SHORTS CREATION")
    print("=" * 60)
    
    try:
        # Topic selection
        topic = random.choice(LEGAL_TOPICS)
        print(f"📚 SELECTED TOPIC: {topic}")
        
        # Content generation with examples
        print("✍️ Generating content with recent examples...")
        sentences = generate_engaging_content_with_examples(topic)
        print(f"📝 Generated {len(sentences)} sentences")
        
        # Background video (contextually relevant)
        print("🎬 Downloading relevant background video...")
        background_path = download_relevant_background_video(topic)
        
        # Background music
        print("🎵 Setting up background music...")
        music_path = download_background_music(topic)
        
        # Create professional video
        print("🎥 Creating word-synchronized video...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_path = f"viral_legal_shorts_{timestamp}.mp4"
        
        if create_word_by_word_video(background_path, sentences, video_path, music_path):
            print(f"✅ PROFESSIONAL VIDEO CREATED: {video_path}")
            
            # Get file size for verification
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            print(f"📊 Video size: {file_size:.2f} MB")
            
            # Send to Telegram with complete package
            print("📤 Sending YouTube-ready package...")
            if send_to_telegram_with_package(video_path, sentences, topic):
                print("✅ SENT TO TELEGRAM SUCCESSFULLY!")
            
            # Save comprehensive metadata
            metadata = {
                "topic": topic,
                "sentences": sentences,
                "timestamp": timestamp,
                "video_file": video_path,
                "duration_seconds": 55,
                "format": "9:16_youtube_shorts",
                "features": [
                    "word_synchronized_text",
                    "contextual_background_video", 
                    "background_music",
                    "professional_typography",
                    "viral_format"
                ],
                "youtube_metadata": {
                    "title": f"{topic} Explained in 60 Seconds | Know Your Rights",
                    "description": " ".join(sentences),
                    "tags": ["LegalTips", "KnowYourRights", "Shorts", "Law", "Legal", "Rights", "Education"],
                    "upload_time": "7:30 PM IST",
                    "target_audience": "General public seeking legal knowledge"
                },
                "file_size_mb": file_size,
                "status": "ready_for_viral_upload"
            }
            
            with open(f"viral_package_{timestamp}.json", 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print("\n🎉 SUCCESS! VIRAL YOUTUBE SHORTS VIDEO CREATED!")
            print("🔥 Features: Word-sync text + Relevant background + Music")
            print("📱 Perfect for YouTube Shorts algorithm!")
            print("🚀 Upload at 7:30 PM IST for maximum engagement!")
            print("=" * 60)
            
        else:
            print("❌ VIDEO CREATION FAILED")
    
    except Exception as e:
        print(f"❌ MAIN EXECUTION ERROR: {e}")
    
    finally:
        # Cleanup
        cleanup_files = [
            "background_*.mp4", "prepared_bg_*.mp4", "legal_bg_*.mp4", 
            "simple_gradient.mp4", "bg_music.mp3", "ambient_music.mp3"
        ]
        
        for pattern in cleanup_files:
            import glob
            for file in glob.glob(pattern):
                try:
                    os.remove(file)
                except:
                    pass

if __name__ == "__main__":
    main()
