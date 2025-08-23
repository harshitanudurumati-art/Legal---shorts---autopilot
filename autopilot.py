import os
import json
import random
import requests
import time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import subprocess
import tempfile

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

def create_simple_video_with_ffmpeg(image_path, audio_path, output_path, duration=55):
    """Create video using FFmpeg directly instead of MoviePy"""
    try:
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', image_path,
            '-i', audio_path,
            '-c:v', 'libx264',
            '-t', str(duration),
            '-pix_fmt', 'yuv420p',
            '-vf', 'scale=1080:1920',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-shortest',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Video created successfully: {output_path}")
            return True
        else:
            print(f"FFmpeg error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error creating video: {e}")
        return False

def generate_content_with_openai(topic):
    """Generate content using OpenAI API"""
    try:
        # Using basic requests instead of openai library
        headers = {
            'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": f"Create a 45-second YouTube Shorts script about {topic}. Make it educational and engaging for general audience."}
            ],
            "max_tokens": 200
        }
        
        response = requests.post('https://api.openai.com/v1/chat/completions', 
                               headers=headers, json=data)
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            print(f"OpenAI API error: {response.text}")
            return generate_fallback_content(topic)
            
    except Exception as e:
        print(f"Error with OpenAI: {e}")
        return generate_fallback_content(topic)

def generate_fallback_content(topic):
    """Generate fallback content without API"""
    content_templates = {
        "Consumer Rights Protection Laws": "Know your consumer rights! You have the right to return defective products, get refunds, and protection from false advertising. Always keep receipts and know your local consumer protection laws.",
        "Digital Privacy and Data Protection": "Your digital privacy matters! Companies must protect your personal data. You have rights to know what data is collected, request deletion, and control how it's used. Stay informed about privacy policies.",
        "Employment Law Basics": "Workers have fundamental rights! This includes fair wages, safe working conditions, protection from discrimination, and the right to organize. Know your employment contract and local labor laws.",
        "Tenant Rights and Housing Laws": "Tenants have important rights! Landlords must provide habitable conditions, proper notice before entry, and follow legal eviction processes. Document everything and know your local housing laws.",
        "Intellectual Property Rights": "Protect your creative work! Copyright, trademarks, and patents safeguard intellectual property. Understand fair use, licensing, and how to protect your original creations legally.",
        "Contract Law Fundamentals": "Contracts are legally binding agreements! Essential elements include offer, acceptance, and consideration. Always read before signing and understand your rights and obligations.",
        "Criminal Law Basics": "Everyone should know basic criminal law! You have rights including presumption of innocence, right to remain silent, and legal representation. Understand the difference between felonies and misdemeanors.",
        "Family Law Essentials": "Family law covers marriage, divorce, and child custody. Key areas include property division, spousal support, and child welfare. Always prioritize children's best interests in family matters."
    }
    
    return content_templates.get(topic, f"Learn about {topic} - an important legal topic everyone should understand for better protection of their rights and interests.")

def create_background_image():
    """Create a simple gradient background image"""
    try:
        # Create image (9:16 aspect ratio for YouTube Shorts)
        width, height = 1080, 1920
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)
        
        # Create gradient background
        colors = [
            (25, 25, 112),   # Navy blue
            (72, 61, 139),   # Dark slate blue
            (123, 104, 238)  # Medium slate blue
        ]
        
        for i in range(height):
            r = int(colors[0][0] + (colors[2][0] - colors[0][0]) * i / height)
            g = int(colors[0][1] + (colors[2][1] - colors[0][1]) * i / height)
            b = int(colors[0][2] + (colors[2][2] - colors[0][2]) * i / height)
            draw.line([(0, i), (width, i)], fill=(r, g, b))
        
        # Add text overlay
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Add title
        title = "LEGAL FACTS"
        draw.text((width//2, 400), title, font=font_large, fill='white', anchor='mm')
        
        # Add subtitle
        subtitle = "Know Your Rights"
        draw.text((width//2, 500), subtitle, font=font_small, fill='white', anchor='mm')
        
        # Save image
        image_path = "background.png"
        image.save(image_path)
        return image_path
        
    except Exception as e:
        print(f"Error creating background: {e}")
        return None

def create_audio_with_gtts(text, output_path):
    """Create audio using gTTS"""
    try:
        from gtts import gTTS
        
        # Create audio
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(output_path)
        return True
        
    except Exception as e:
        print(f"Error creating audio: {e}")
        return False

def send_to_telegram(video_path, content_text):
    """Send video to Telegram"""
    try:
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            print("Telegram credentials not found")
            return False
        
        # Send video
        with open(video_path, 'rb') as video:
            url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
            files = {'video': video}
            data = {
                'chat_id': chat_id,
                'caption': f"📚 Legal Knowledge Video\n\n{content_text[:500]}..."
            }
            
            response = requests.post(url, files=files, data=data)
            return response.status_code == 200
            
    except Exception as e:
        print(f"Error sending to Telegram: {e}")
        return False

def main():
    """Main execution function"""
    print("🚀 Starting Legal Video Generation...")
    
    try:
        # Select random topic
        topic = random.choice(LEGAL_TOPICS)
        print(f"📚 Selected topic: {topic}")
        
        # Generate content
        print("✍️ Generating content...")
        content = generate_content_with_openai(topic)
        
        # Create background image
        print("🎨 Creating background image...")
        image_path = create_background_image()
        if not image_path:
            print("❌ Failed to create background image")
            return
        
        # Create audio
        print("🎵 Creating audio...")
        audio_path = "audio.mp3"
        if not create_audio_with_gtts(content, audio_path):
            print("❌ Failed to create audio")
            return
        
        # Create video
        print("🎬 Creating video...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_path = f"legal_video_{timestamp}.mp4"
        
        if create_simple_video_with_ffmpeg(image_path, audio_path, video_path):
            print(f"✅ Video created: {video_path}")
            
            # Send to Telegram
            print("📤 Sending to Telegram...")
            if send_to_telegram(video_path, content):
                print("✅ Successfully sent to Telegram")
            else:
                print("⚠️ Failed to send to Telegram")
            
            # Save metadata
            metadata = {
                "topic": topic,
                "content": content,
                "timestamp": timestamp,
                "video_file": video_path
            }
            
            with open(f"metadata_{timestamp}.json", 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print("🎉 Process completed successfully!")
            
        else:
            print("❌ Failed to create video")
    
    except Exception as e:
        print(f"❌ Error in main execution: {e}")

if __name__ == "__main__":
    main()
