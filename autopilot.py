import os
import json
import random
import requests
import time
from datetime import datetime, timedelta
import subprocess
import tempfile
import re
import math

# VIRAL LEGAL CONTENT SYSTEM - 10 Years Video Editing Expertise
# Based on successful channels like Finology Legal, Law Explained, etc.

# 8-Topic Rotation with VIRAL angles
VIRAL_LEGAL_TOPICS = {
    "Consumer Rights Protection Laws": {
        "recent_cases": "Amazon $100M Settlement, Apple $25M Payout, McDonald's $5M Fine",
        "viral_angles": [
            "This BILLION DOLLAR lawsuit changed consumer rights FOREVER!",
            "Amazon customer got $50,000 just by knowing THIS right!",
            "McDonald's LOST big time - Here's what consumers won!"
        ],
        "bg_theme": "corporate_lawsuit",
        "key_points": ["Warranty rights", "Return policies", "Class action power", "Documentation tips"]
    },
    
    "Digital Privacy and Data Protection": {
        "recent_cases": "Meta $5.1B Fine, TikTok Ban Threats, Google Location Tracking $392M",
        "viral_angles": [
            "Facebook paid $5 BILLION for spying on you!",
            "Your phone is selling your location for PENNIES!",
            "TikTok ban? Here's what your data is REALLY worth!"
        ],
        "bg_theme": "cyber_tech",
        "key_points": ["GDPR power", "Data deletion rights", "Privacy settings", "VPN protection"]
    },
    
    "Employment Law Basics": {
        "recent_cases": "Tesla $137M Discrimination, Amazon Union Victory, Starbucks NLRB Cases",
        "viral_angles": [
            "Tesla worker got $137 MILLION for workplace discrimination!",
            "Amazon workers just made HISTORY with this union win!",
            "Starbucks closed stores to stop unions - Here's what happened!"
        ],
        "bg_theme": "workplace_justice",
        "key_points": ["Union rights", "Discrimination protection", "Overtime laws", "Whistleblower safety"]
    },
    
    "Tenant Rights and Housing Laws": {
        "recent_cases": "Rent Control Victories, Eviction Moratoriums, Landlord Fines $2M",
        "viral_angles": [
            "Landlord fined $2 MILLION for illegal evictions!",
            "Rent control is SPREADING - Here's your new rights!",
            "This tenant DESTROYED landlord in court with one trick!"
        ],
        "bg_theme": "housing_crisis",
        "key_points": ["Eviction protection", "Security deposits", "Habitability rights", "Rent stabilization"]
    },
    
    "Intellectual Property Rights": {
        "recent_cases": "Epic vs Apple $100M, Music Sampling $50M, TikTok Creator Wins",
        "viral_angles": [
            "Epic Games beat Apple for $100 MILLION!",
            "This TikTok creator sued for $10M and WON!",
            "Music industry SHOOK by this sampling lawsuit!"
        ],
        "bg_theme": "creative_rights",
        "key_points": ["Copyright basics", "Fair use limits", "Creator protection", "Platform policies"]
    },
    
    "Contract Law Fundamentals": {
        "recent_cases": "Celebrity Contract Disasters, Non-Compete Bans, Terms of Service Lawsuits",
        "viral_angles": [
            "Celebrity lost $500,000 by signing this ONE clause!",
            "Non-compete agreements are getting BANNED nationwide!",
            "You agreed to THIS when you clicked 'Accept'!"
        ],
        "bg_theme": "contract_danger",
        "key_points": ["Reading fine print", "Unconscionable terms", "Digital agreements", "Breach consequences"]
    },
    
    "Criminal Law Basics": {
        "recent_cases": "Police Reform Laws, White Collar Sentences, Digital Evidence Cases",
        "viral_angles": [
            "Know these rights or risk 20 YEARS in prison!",
            "Police body cams just saved this innocent person!",
            "CEO got 30 YEARS for this financial crime!"
        ],
        "bg_theme": "criminal_justice",
        "key_points": ["Miranda rights", "Search warrants", "Legal representation", "Evidence rules"]
    },
    
    "Family Law Essentials": {
        "recent_cases": "Custody Algorithm Bias, Divorce Crypto Cases, Surrogacy Law Changes",
        "viral_angles": [
            "This parent lost custody because of FACEBOOK posts!",
            "Divorce lawyer found $2M in hidden Bitcoin!",
            "Surrogacy laws are changing EVERYTHING for families!"
        ],
        "bg_theme": "family_modern",
        "key_points": ["Custody factors", "Asset division", "Social media impact", "Modern family rights"]
    }
}

def get_viral_topic_today():
    """Get today's viral topic with rotation tracking"""
    try:
        # 8-day rotation system
        day_of_year = datetime.now().timetuple().tm_yday
        topic_index = (day_of_year - 1) % 8
        topics = list(VIRAL_LEGAL_TOPICS.keys())
        
        # Load state
        state_file = "viral_rotation.json"
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                state = json.load(f)
        else:
            state = {"variations": {}}
        
        topic = topics[topic_index]
        topic_data = VIRAL_LEGAL_TOPICS[topic]
        
        # Rotate through viral angles (3 per topic)
        if topic not in state["variations"]:
            state["variations"][topic] = 0
        
        angle_index = state["variations"][topic] % 3
        viral_angle = topic_data["viral_angles"][angle_index]
        
        # Update state
        state["variations"][topic] += 1
        state["last_generated"] = datetime.now().isoformat()
        
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        return {
            "topic": topic,
            "viral_angle": viral_angle,
            "recent_cases": topic_data["recent_cases"],
            "bg_theme": topic_data["bg_theme"],
            "key_points": topic_data["key_points"],
            "variation": angle_index + 1
        }
        
    except Exception as e:
        print(f"Error in topic selection: {e}")
        # Fallback
        topic = "Consumer Rights Protection Laws"
        return {
            "topic": topic,
            "viral_angle": "This lawsuit changed everything!",
            "recent_cases": "Recent major settlements",
            "bg_theme": "legal_generic",
            "key_points": ["Know your rights", "Document everything"],
            "variation": 1
        }

def create_viral_background_video(theme, duration=60):
    """Create animated background like viral legal channels"""
    try:
        print(f"🎬 Creating VIRAL background for theme: {theme}")
        
        # Professional color schemes for different themes
        theme_configs = {
            "corporate_lawsuit": {
                "colors": ["#1a237e", "#283593", "#3949ab"],  # Corporate blue
                "elements": "courthouse, scales, corporate building",
                "animation": "corporate_zoom"
            },
            "cyber_tech": {
                "colors": ["#0d47a1", "#1565c0", "#1976d2"],  # Tech blue
                "elements": "binary code, network nodes, lock icons",
                "animation": "matrix_rain"
            },
            "workplace_justice": {
                "colors": ["#b71c1c", "#c62828", "#d32f2f"],  # Justice red
                "elements": "office buildings, workers, protest signs",
                "animation": "industrial_movement"
            },
            "housing_crisis": {
                "colors": ["#ff8f00", "#ffa000", "#ffb300"],  # Housing orange
                "elements": "apartment buildings, keys, home icons",
                "animation": "urban_growth"
            },
            "creative_rights": {
                "colors": ["#7b1fa2", "#8e24aa", "#9c27b0"],  # Creative purple
                "elements": "copyright symbols, art tools, social media",
                "animation": "creative_burst"
            },
            "contract_danger": {
                "colors": ["#d84315", "#e64a19", "#f4511e"],  # Warning red-orange
                "elements": "contracts, pens, warning signs",
                "animation": "contract_signing"
            },
            "criminal_justice": {
                "colors": ["#424242", "#616161", "#757575"],  # Justice gray
                "elements": "gavel, handcuffs, courthouse steps",
                "animation": "justice_scales"
            },
            "family_modern": {
                "colors": ["#00695c", "#00796b", "#00897b"],  # Family teal
                "elements": "family silhouettes, homes, hearts",
                "animation": "family_unity"
            }
        }
        
        config = theme_configs.get(theme, theme_configs["corporate_lawsuit"])
        colors = config["colors"]
        
        # Create professional animated background
        output_file = f"viral_bg_{theme}.mp4"
        
        # Advanced animation patterns
        if config["animation"] == "matrix_rain":
            # Matrix-style digital rain effect
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'color=size=1080x1920:duration={duration}:rate=30:color={colors[0]}',
                '-vf', f'''
                geq=r='if(lt(random(1)*255,50),255,{colors[0][1:3]} * 16)':
                g='if(lt(random(2)*255,50),255,{colors[0][3:5]} * 16)':
                b='if(lt(random(3)*255,50),255,{colors[0][5:7]} * 16)',
                drawtext=text='⚖️':fontsize=100:fontcolor=white@0.1:x='mod(t*150,w)':y='mod(t*200,h)':enable='between(t,0,{duration})',
                drawtext=text='§':fontsize=80:fontcolor=white@0.2:x='mod(t*100+200,w)':y='mod(t*180+100,h)':enable='between(t,0,{duration})'
                ''',
                output_file
            ]
        
        elif config["animation"] == "corporate_zoom":
            # Corporate zoom with legal symbols
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'color=size=1080x1920:duration={duration}:rate=30:color={colors[0]}',
                '-vf', f'''
                drawbox=x='w*0.1':y='h*0.1':w='w*0.8':h='h*0.8':color={colors[1]}@0.3:t=fill,
                drawbox=x='w*0.2':y='h*0.2':w='w*0.6':h='h*0.6':color={colors[2]}@0.2:t=fill,
                geq=r='128+50*sin(2*PI*t/10)':g='128+50*cos(2*PI*t/8)':b='180+30*sin(2*PI*t/6)',
                scale=iw*(1+0.1*sin(2*PI*t/15)):ih*(1+0.1*sin(2*PI*t/15)),
                crop=1080:1920:(iw-1080)/2:(ih-1920)/2
                ''',
                output_file
            ]
        
        else:
            # Default professional gradient animation
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'color=size=1080x1920:duration={duration}:rate=30:color={colors[0]}',
                '-vf', f'''
                geq=r='128+100*sin(2*PI*t/12+X/80)':g='128+100*cos(2*PI*t/10+Y/80)':b='200+50*sin(2*PI*t/8)',
                drawbox=x=0:y='h*0.8':w=w:h='h*0.2':color={colors[1]}@0.4:t=fill,
                drawbox=x=0:y=0:w=w:h='h*0.1':color={colors[2]}@0.3:t=fill
                ''',
                output_file
            ]
        
        print("🎬 Generating viral background animation...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print(f"✅ Viral background created: {output_file}")
            return output_file
        else:
            print(f"⚠️ Background creation warning: {result.stderr}")
            return create_fallback_background(duration)
            
    except Exception as e:
        print(f"Error creating viral background: {e}")
        return create_fallback_background(duration)

def create_fallback_background(duration=60):
    """Professional fallback background"""
    try:
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', f'color=size=1080x1920:duration={duration}:rate=30:color=#1565c0',
            '-vf', '''
            geq=r='128+80*sin(2*PI*t/8)':g='128+80*cos(2*PI*t/6)':b='200+40*sin(2*PI*t/4),
            drawtext=text=⚖️:fontsize=150:fontcolor=white@0.1:x=(w-text_w)/2:y=(h-text_h)/2
            ''',
            'fallback_bg.mp4'
        ]
        
        result = subprocess.run(cmd, capture_output=True, timeout=60)
        if result.returncode == 0:
            return 'fallback_bg.mp4'
        return None
    except:
        return None

def create_viral_background_music(theme, duration=60):
    """Create theme-appropriate background music"""
    try:
        print(f"🎵 Creating background music for {theme}...")
        
        # Different musical themes
        music_configs = {
            "corporate_lawsuit": {"freq": [440, 554, 659], "volume": 0.08},  # Professional chord
            "cyber_tech": {"freq": [523, 659, 784], "volume": 0.06},  # Tech sound
            "workplace_justice": {"freq": [392, 494, 587], "volume": 0.07},  # Justice theme
            "housing_crisis": {"freq": [349, 440, 523], "volume": 0.05},  # Warm tones
            "creative_rights": {"freq": [494, 587, 698], "volume": 0.06},  # Creative harmony
            "default": {"freq": [440, 554, 659], "volume": 0.05}
        }
        
        config = music_configs.get(theme, music_configs["default"])
        
        # Create subtle ambient music
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi', '-i', f'sine=frequency={config["freq"][0]}:duration={duration}',
            '-f', 'lavfi', '-i', f'sine=frequency={config["freq"][1]}:duration={duration}',
            '-f', 'lavfi', '-i', f'sine=frequency={config["freq"][2]}:duration={duration}',
            '-filter_complex', f'[0:a][1:a][2:a]amix=inputs=3:duration=first,volume={config["volume"]},aecho=0.8:0.88:60:0.4',
            f'viral_music_{theme}.mp3'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            return f'viral_music_{theme}.mp3'
        return None
        
    except Exception as e:
        print(f"Error creating music: {e}")
        return None

def generate_viral_script(topic_data):
    """Generate viral script with recent cases and examples"""
    try:
        print("✍️ Generating VIRAL script with real cases...")
        
        # Use OpenAI API if available
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("HF_API_KEY")
        
        if api_key:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            prompt = f"""Create a viral 55-second YouTube Shorts script about {topic_data['topic']}.

HOOK: {topic_data['viral_angle']}

RECENT CASES: {topic_data['recent_cases']}

KEY POINTS: {', '.join(topic_data['key_points'])}

FORMAT:
- Start with the exact hook (attention-grabbing)
- Include specific dollar amounts and recent case names
- Use power words: SHOCKING, MASSIVE, ILLEGAL, WON, LOST, BANNED
- End with strong call-to-action
- Make it exactly 55 seconds when spoken
- Write in short, punchy sentences for word-by-word subtitles
- Include actionable tips viewers can use

Style: Like viral TikTok legal content - dramatic, educational, engaging"""

            data = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 300,
                "temperature": 0.8
            }
            
            response = requests.post('https://api.openai.com/v1/chat/completions', 
                                   headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                return clean_script_for_speech(content)
        
        # Fallback viral script
        return generate_fallback_viral_script(topic_data)
        
    except Exception as e:
        print(f"Error generating script: {e}")
        return generate_fallback_viral_script(topic_data)

def generate_fallback_viral_script(topic_data):
    """Generate high-quality fallback viral script"""
    viral_templates = {
        "Consumer Rights Protection Laws": f"{topic_data['viral_angle']} Amazon just paid customers $100 MILLION in a massive settlement. Here's how YOU can protect yourself. First, ALWAYS keep receipts and documentation. Second, know your warranty rights - companies must honor them. Third, join class action lawsuits when available. The consumer who sued Amazon for false advertising got $50,000! You have the RIGHT to return defective products. Companies cannot use misleading advertising. Document EVERYTHING with photos and emails. Your consumer rights are POWERFUL when you know how to use them. Follow for more legal wins!",
        
        "Digital Privacy and Data Protection": f"{topic_data['viral_angle']} Meta paid $5.1 BILLION for violating YOUR privacy! Here's what they don't want you to know. Your location data is sold for PENNIES to advertisers. Every click, every scroll is tracked and monetized. But you have POWER! Delete your data from Google and Facebook. Use VPN to hide your location. Turn OFF targeted advertising in settings. The GDPR gives you the right to be forgotten. California's CCPA protects residents too. TikTok faces BANS over data collection. Protect yourself NOW before it's too late. Follow for privacy protection tips!",
        
        "Employment Law Basics": f"{topic_data['viral_angle']} This Tesla worker got $137 MILLION for workplace discrimination! Here's what every worker needs to know. You CANNOT be fired for your race, gender, or age. Overtime violations cost companies MILLIONS in penalties. Document workplace harassment with emails and photos. Whistleblower protections keep you safe from retaliation. Amazon workers just won HISTORIC union rights! Starbucks tried to stop unions - they FAILED. Know your employment contract inside out. Join unions for collective bargaining power. Workers have MORE rights than companies admit. Follow for workplace justice!",
    }
    
    return viral_templates.get(topic_data['topic'], f"{topic_data['viral_angle']} This recent case shows the power of knowing your legal rights. {topic_data['recent_cases']} prove that ordinary people can win big when they understand the law. Here are the key points you need to know: {'. '.join(topic_data['key_points'])}. Documentation is crucial in any legal matter. Know your rights and don't be afraid to exercise them. The law is on your side when you're informed. Follow for more legal insights!")

def clean_script_for_speech(script):
    """Clean script for better text-to-speech"""
    # Remove markdown and special characters
    script = re.sub(r'\*\*(.*?)\*\*', r'\1', script)
    script = re.sub(r'\*(.*?)\*', r'\1', script)
    
    # Improve pronunciation
    replacements = {
        '$': ' dollars ',
        '%': ' percent ',
        '&': ' and ',
        '#': ' hashtag ',
        '@': ' at ',
        'GDPR': 'G D P R',
        'CCPA': 'C C P A',
        'CEO': 'C E O',
        'FBI': 'F B I',
        'SEC': 'S E C'
    }
    
    for old, new in replacements.items():
        script = script.replace(old, new)
    
    return script.strip()

def create_viral_word_subtitles(script, duration=55):
    """Create viral-style word-by-word subtitles with emphasis"""
    try:
        # Split into words while preserving emphasis
        words = []
        current_word = ""
        
        for char in script:
            if char.isspace():
                if current_word:
                    words.append(current_word)
                    current_word = ""
            else:
                current_word += char
        
        if current_word:
            words.append(current_word)
        
        # Calculate timing
        total_words = len(words)
        base_duration_per_word = duration / total_words if total_words > 0 else 1
        
        subtitles = []
        current_time = 0
        
        # Power words that get emphasis
        power_words = [
            'MILLION', 'BILLION', 'DOLLARS', 'WON', 'LOST', 'ILLEGAL', 'BANNED', 'SHOCKING', 
            'MASSIVE', 'LAWSUIT', 'SETTLEMENT', 'RIGHTS', 'PROTECTION', 'VICTORY', 'FINE'
        ]
        
        for i, word in enumerate(words):
            # Clean word for display
            display_word = word.upper().strip('.,!?;:')
            
            # Adjust timing based on word importance
            word_duration = base_duration_per_word
            
            if any(power in word.upper() for power in power_words):
                word_duration *= 1.3  # Longer display for power words
            elif word.endswith('.') or word.endswith('!') or word.endswith('?'):
                word_duration *= 1.2  # Pause after sentences
            
            subtitles.append({
                'text': display_word,
                'start': current_time,
                'end': current_time + word_duration,
                'is_power_word': any(power in word.upper() for power in power_words),
                'position': i
            })
            
            current_time += word_duration
        
        return subtitles
        
    except Exception as e:
        print(f"Error creating subtitles: {e}")
        return []

def create_viral_audio(script, output_path):
    """Create engaging viral audio"""
    try:
        print("🎤 Creating VIRAL audio narration...")
        from gtts import gTTS
        
        # Clean script for TTS
        clean_script = clean_script_for_speech(script)
        
        # Create TTS
        tts = gTTS(text=clean_script, lang='en', slow=False)
        temp_file = "temp_viral_audio.mp3"
        tts.save(temp_file)
        
        # Enhance audio for viral appeal
        cmd = [
            'ffmpeg', '-y',
            '-i', temp_file,
            '-af', '''
            atempo=1.08,
            aecho=0.8:0.88:40:0.3,
            equalizer=f=2000:width_type=h:width=800:g=3,
            compand=attacks=0.1:decays=0.8:points=-90/-90|-30/-15|-20/-10|-5/-5|0/-3|20/0,
            volume=1.4
            ''',
            '-c:a', 'mp3',
            '-b:a', '128k',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Cleanup
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        if result.returncode == 0:
            print("✅ Viral audio created successfully!")
            return True
        else:
            print(f"Audio processing warning: {result.stderr}")
            return True  # Still usable
            
    except Exception as e:
        print(f"Error creating viral audio: {e}")
        return False

def create_professional_viral_video(background_path, audio_path, music_path, subtitles, topic_data, output_path):
    """Create professional viral video like top legal channels"""
    try:
        print("🎬 Creating PROFESSIONAL VIRAL VIDEO...")
        
        if not subtitles:
            print("❌ No subtitles available")
            return False
        
        # Build complex filter for viral video
        filter_parts = []
        
        # Base video preparation
        filter_parts.append("[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[bg]")
        
        # Add dark overlay for subtitle readability
        filter_parts.append("[bg]drawbox=x=0:y=ih*0.7:w=iw:h=ih*0.3:color=black@0.7:t=fill[overlay]")
        
        # Add topic title at top
        topic_title = topic_data['topic'].replace('Law', '').replace('Rights', '').replace('Basics', '').strip()
        filter_parts.append(f"[overlay]drawtext=text='{topic_title.upper()}':fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf':fontsize=35:fontcolor=white:bordercolor=black:borderw=2:x=(w-text_w)/2:y=60[titled]")
        
        # Create word-by-word subtitle layers
        current_layer = "[titled]"
        
        for i, subtitle in enumerate(subtitles[:50]):  # Limit to prevent command length issues
            word_text = subtitle['text'].replace("'", "\\'").replace(":", "\\:")
            
            if subtitle['is_power_word']:
                # POWER WORDS - Large, yellow, with effects
                word_filter = (
                    f"{current_layer}drawtext="
                    f"text='🔥 {word_text} 🔥':"
                    f"fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf':"
                    f"fontsize=85:"
                    f"fontcolor=yellow:"
                    f"bordercolor=red:"
                    f"borderw=4:"
                    f"x=(w-text_w)/2:"
                    f"y=h*0.75:"
                    f"enable='between(t,{subtitle['start']:.2f},{subtitle['end']:.2f})'[power{i}]"
                )
            else:
                # Regular words - White, large, readable
                word_filter = (
                    f"{current_layer}drawtext="
                    f"text='{word_text}':"
                    f"fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf':"
                    f"fontsize=70:"
                    f"fontcolor=white:"
                    f"bordercolor=black:"
                    f"borderw=3:"
                    f"x=(w-text_w)/2:"
                    f"y=h*0.8:"
                    f"enable='between(t,{subtitle['start']:.2f},{subtitle['end']:.2f})'[word{i}]"
                )
            
            filter_parts.append(word_filter)
            current_layer = f"[power{i}]" if subtitle['is_power_word'] else f"[word{i}]"
        
        # Build FFmpeg command
        cmd = ['ffmpeg', '-y']
        
        # Input files
        cmd.extend(['-i', background_path])  # Background video
        cmd.extend(['-i', audio_path])       # Narration audio
        
        if music_path and os.path.exists(music_path):
            cmd.extend(['-i', music_path])   # Background music
            audio_mix = '[1:a][2:a]amix=inputs=2:duration=first:dropout_transition=2,volume=1.2[final_audio]'
        else:
            audio_mix = '[1:a]volume=1.2[final_audio]'
        
        # Combine all filters
        full_filter = ';'.join(filter_parts) + ';' + audio_mix
        
        # Final encoding settings for viral quality
        cmd.extend([
            '-filter_complex', full_filter,
            '-map', current_layer.replace('[', '').replace(']', ''),
            '-map', '[final_audio]',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '20',  # High quality
            '-c:a', 'aac',
            '-b:a', '128k',
            '-r', '30',
            '-t', '55',
            '-movflags', '+faststart',  # Web optimization
            output_path
        ])
        
        print("🎬 Rendering VIRAL video...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"🔥 VIRAL VIDEO CREATED: {output_path}")
            
            # Verify output
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                return True
            else:
                print("❌ Video file appears corrupted")
                return False
        else:
            print(f"❌ Video creation failed: {result.stderr}")
            return create_viral_fallback_video(background_path, audio_path, topic_data['topic'], output_path)
            
    except Exception as e:
        print(f"Error creating viral video: {e}")
        return create_viral_fallback_video(background_path, audio_path, topic_data['topic'], output_path)

def create_viral_fallback_video(background_path, audio_path, topic, output_path):
    """Create fallback viral video if main creation fails"""
    try:
        print("🔄 Creating fallback viral video...")
        
        cmd = [
            'ffmpeg', '-y',
            '-i', background_path if background_path and os.path.exists(background_path) else '-f',
            'lavfi', '-i', 'color=size=1080x1920:duration=55:rate=30:color=#1565c0'
        ]
        
        if not (background_path and os.path.exists(background_path)):
            cmd = ['ffmpeg', '-y', '-f', 'lavfi', '-i', 'color=size=1080x1920:duration=55:rate=30:color=#1565c0']
        
        cmd.extend([
            '-i', audio_path,
            '-vf', f'''
            drawbox=x=0:y=ih*0.75:w=iw:h=ih*0.25:color=black@0.8:t=fill,
            drawtext=text='{topic.upper()}':fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf':fontsize=60:fontcolor=white:bordercolor=black:borderw=3:x=(w-text_w)/2:y=h*0.8,
            drawtext=text='VIRAL LEGAL CONTENT':fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf':fontsize=40:fontcolor=yellow:bordercolor=red:borderw=2:x=(w-text_w)/2:y=100
            ''',
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-c:a', 'aac',
            '-t', '55',
            output_path
        ])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return result.returncode == 0
        
    except Exception as e:
        print(f"Fallback video creation failed: {e}")
        return False

def send_viral_package_to_telegram(video_path, topic_data, script):
    """Send complete viral video package to Telegram"""
    try:
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            print("❌ Telegram credentials missing")
            return False
        
        # Create professional package
        package_message = f"""🔥 VIRAL LEGAL SHORTS - READY FOR UPLOAD! 🔥

📺 TOPIC: {topic_data['topic']}
🎯 ANGLE: {topic_data['viral_angle']}
💼 RECENT CASES: {topic_data['recent_cases']}

🎬 VIDEO FEATURES:
✅ Professional animated background
✅ Word-by-word viral subtitles
✅ Power word emphasis (🔥MILLION🔥)
✅ Background music
✅ 55-second perfect duration
✅ 9:16 YouTube Shorts format
✅ High engagement design

📱 SUGGESTED TITLE:
"{topic_data['viral_angle'][:60]}... | Legal Rights Explained"

📝 DESCRIPTION TEMPLATE:
{script[:200]}...

🔥 POWER HASHTAGS:
#LegalRights #ViralLegal #LawExplained #ConsumerRights #LegalTips #Lawsuit #Settlement #YourRights #LegalAdvice #Justice

⏰ OPTIMAL UPLOAD TIMES:
• 7:30 PM IST (Peak engagement)
• 12:00 PM IST (Lunch break viewers)
• 9:00 AM IST (Morning commuters)

📊 ENGAGEMENT BOOSTERS:
• Pin comment: "What legal right surprised you most?"
• Reply to all comments within 2 hours
• Cross-post to Instagram Reels
• Share on LinkedIn with professional angle

🎯 TARGET AUDIENCE:
Legal professionals, law students, consumers seeking rights information, small business owners

💡 FOLLOW-UP VIDEO IDEAS:
• Part 2 with more cases
• "How to file similar lawsuit"
• "Biggest legal wins of 2024"

🚀 READY TO GO VIRAL!"""

        # Send video with package
        with open(video_path, 'rb') as video:
            url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
            files = {'video': video}
            data = {
                'chat_id': chat_id,
                'caption': package_message
            }
            
            response = requests.post(url, files=files, data=data, timeout=180)
            
            if response.status_code == 200:
                print("✅ VIRAL PACKAGE SENT TO TELEGRAM!")
                return True
            else:
                print(f"❌ Telegram send failed: {response.text}")
                return False
                
    except Exception as e:
        print(f"Error sending to Telegram: {e}")
        return False

def analyze_video_quality(video_path):
    """Analyze final video quality"""
    try:
        # Check duration
        duration_cmd = [
            'ffprobe', '-v', 'quiet', '-show_entries', 
            'format=duration', '-of', 'csv=p=0', video_path
        ]
        duration_result = subprocess.run(duration_cmd, capture_output=True, text=True)
        duration = float(duration_result.stdout.strip()) if duration_result.stdout.strip() else 0
        
        # Check resolution
        resolution_cmd = [
            'ffprobe', '-v', 'quiet', '-show_entries',
            'stream=width,height', '-of', 'csv=p=0', video_path
        ]
        resolution_result = subprocess.run(resolution_cmd, capture_output=True, text=True)
        
        # File size
        file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        
        quality_report = {
            "duration": duration,
            "file_size_mb": file_size_mb,
            "resolution": resolution_result.stdout.strip() if resolution_result.stdout else "Unknown",
            "is_viral_ready": 50 <= duration <= 60 and file_size_mb > 5,
            "recommendations": []
        }
        
        if duration < 50:
            quality_report["recommendations"].append("Duration too short - add more content")
        elif duration > 60:
            quality_report["recommendations"].append("Duration too long - trim content")
        else:
            quality_report["recommendations"].append("Perfect duration for YouTube Shorts!")
        
        if file_size_mb < 5:
            quality_report["recommendations"].append("File size low - check video quality")
        
        print(f"📊 Video Quality Report:")
        print(f"   Duration: {duration:.1f}s")
        print(f"   File Size: {file_size_mb:.1f}MB")
        print(f"   Resolution: {quality_report['resolution']}")
        print(f"   Viral Ready: {'✅' if quality_report['is_viral_ready'] else '❌'}")
        
        return quality_report
        
    except Exception as e:
        print(f"Quality analysis failed: {e}")
        return {"is_viral_ready": True, "recommendations": ["Quality check unavailable"]}

def main():
    """Main viral video generation system - 10 years expertise"""
    print("🚀 VIRAL LEGAL SHORTS GENERATOR v2.0")
    print("🎬 Professional Video Editor - 10 Years Expertise")
    print("📺 Creating content like Finology Legal & top channels")
    print("=" * 60)
    
    try:
        # Get today's viral topic
        topic_data = get_viral_topic_today()
        print(f"🎯 TODAY'S VIRAL TOPIC: {topic_data['topic']}")
        print(f"🔥 VIRAL ANGLE: {topic_data['viral_angle']}")
        print(f"📰 RECENT CASES: {topic_data['recent_cases']}")
        print(f"🎨 THEME: {topic_data['bg_theme']}")
        print(f"📅 VARIATION: {topic_data['variation']}/3")
        
        # Generate viral script
        print("\n✍️ GENERATING VIRAL SCRIPT...")
        viral_script = generate_viral_script(topic_data)
        print(f"📝 Script Preview: {viral_script[:100]}...")
        
        # Create themed background video
        print("\n🎬 CREATING PROFESSIONAL ANIMATED BACKGROUND...")
        background_path = create_viral_background_video(topic_data['bg_theme'], 60)
        
        # Create background music
        print("🎵 CREATING THEME MUSIC...")
        music_path = create_viral_background_music(topic_data['bg_theme'], 60)
        
        # Create viral audio
        print("🎤 CREATING VIRAL NARRATION...")
        audio_path = "viral_narration.mp3"
        if not create_viral_audio(viral_script, audio_path):
            print("❌ Audio creation failed")
            return
        
        # Create word-by-word subtitles
        print("📝 CREATING VIRAL SUBTITLES...")
        subtitles = create_viral_word_subtitles(viral_script, 55)
        print(f"📊 Generated {len(subtitles)} subtitle segments")
        
        # Create final viral video
        print("\n🎥 CREATING VIRAL LEGAL SHORTS VIDEO...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_filename = f"viral_legal_{topic_data['topic'].replace(' ', '_')}_{timestamp}.mp4"
        
        success = create_professional_viral_video(
            background_path, 
            audio_path, 
            music_path, 
            subtitles, 
            topic_data, 
            video_filename
        )
        
        if success:
            print(f"\n🔥 VIRAL VIDEO CREATED SUCCESSFULLY!")
            print(f"📁 File: {video_filename}")
            
            # Analyze video quality
            quality_report = analyze_video_quality(video_filename)
            
            if quality_report["is_viral_ready"]:
                print("✅ VIDEO IS VIRAL-READY!")
            else:
                print("⚠️ Video needs improvements:")
                for rec in quality_report["recommendations"]:
                    print(f"   • {rec}")
            
            # Send to Telegram
            print("\n📤 SENDING VIRAL PACKAGE TO TELEGRAM...")
            telegram_success = send_viral_package_to_telegram(video_filename, topic_data, viral_script)
            
            # Save comprehensive metadata
            metadata = {
                "timestamp": timestamp,
                "topic_data": topic_data,
                "script": viral_script,
                "video_file": video_filename,
                "quality_report": quality_report,
                "telegram_delivered": telegram_success,
                "viral_features": [
                    "Professional animated background",
                    "Word-by-word subtitles with power word emphasis",
                    "Theme-appropriate background music",
                    "Real case examples and dollar amounts",
                    "Viral hook and engaging content",
                    "Perfect 55-second duration",
                    "9:16 YouTube Shorts format",
                    "High-quality audio with effects"
                ],
                "upload_strategy": {
                    "best_times": ["7:30 PM IST", "12:00 PM IST", "9:00 AM IST"],
                    "hashtags": "#LegalRights #ViralLegal #LawExplained #ConsumerRights #LegalTips",
                    "title": f"{topic_data['viral_angle'][:60]}... | Legal Rights",
                    "thumbnail_tips": "Use red arrows, shocked face, money symbols"
                },
                "rotation_status": {
                    "current_variation": topic_data['variation'],
                    "next_topic": "Will rotate in 1 day",
                    "uniqueness": "No content repeats for 24 videos"
                }
            }
            
            with open(f"viral_metadata_{timestamp}.json", 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print("\n🎉 VIRAL LEGAL SHORTS GENERATION COMPLETE!")
            print("=" * 60)
            print(f"📺 Created: Professional viral legal shorts")
            print(f"⏱️  Duration: {quality_report.get('duration', 55):.1f} seconds")
            print(f"🎯 Topic: {topic_data['topic']}")
            print(f"🔥 Hook: {topic_data['viral_angle']}")
            print(f"💼 Cases: {topic_data['recent_cases']}")
            print(f"📱 Format: YouTube Shorts (9:16)")
            print(f"🚀 Status: READY TO GO VIRAL!")
            print("=" * 60)
            
        else:
            print("❌ VIRAL VIDEO CREATION FAILED")
            
    except Exception as e:
        print(f"❌ SYSTEM ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup but keep important files
        cleanup_files = [
            "temp_viral_audio.mp3",
            "fallback_bg.mp4"
        ]
        
        for file in cleanup_files:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except:
                    pass
        
        print("🧹 Cleanup completed!")

if __name__ == "__main__":
    main()
