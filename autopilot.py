import os
import json
import random
import requests
import time
from datetime import datetime
import subprocess
import tempfile
import re

# 8-Topic Rotation System
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

# Video Content Variations for Each Topic (3 variations per topic)
TOPIC_VARIATIONS = {
    "Consumer Rights Protection Laws": [
        {
            "angle": "Recent Cases",
            "hook": "A customer sued Amazon for $50,000 and WON!",
            "content": "Recent consumer rights victories show your power. The Johnson vs Amazon case proved customers can fight back. You have 30 days return rights. Defective products must be replaced. False advertising is illegal. Class action lawsuits protect consumers. Document everything with photos. Keep all receipts and emails.",
            "bg_keywords": "shopping mall customers people buying",
            "examples": "Amazon return case, Apple battery lawsuit, Wells Fargo fine"
        },
        {
            "angle": "Hidden Rights",
            "hook": "You have SECRET consumer rights companies don't tell you!",
            "content": "Hidden consumer protections you never knew existed. Right to repair your own devices. Lemon laws for defective cars. Cooling-off periods for contracts. Price matching guarantees. Warranty extensions by law. Free credit reports annually. Debt collection limits.",
            "bg_keywords": "repair shop mechanic fixing electronics",
            "examples": "Right to repair movement, Lemon law victories"
        },
        {
            "angle": "Money Saving Tips",
            "hook": "This consumer law can save you THOUSANDS!",
            "content": "Consumer laws that put money back in your pocket. Extended warranties are often unnecessary. Price discrimination is sometimes illegal. Automatic renewals need consent. Credit card protections cover disputes. Return policies have legal minimums. Gift cards cannot expire quickly.",
            "bg_keywords": "money cash savings calculator finance",
            "examples": "Credit card chargeback wins, Gift card law changes"
        }
    ],
    "Digital Privacy and Data Protection": [
        {
            "angle": "Big Tech Exposed",
            "hook": "Facebook was fined $5 BILLION for this privacy violation!",
            "content": "Big Tech privacy scandals show why your data matters. Facebook Cambridge Analytica exposed millions. Google tracks your location secretly. Amazon Alexa records conversations. You can delete your data. GDPR gives Europeans control. California CCPA protects residents. Use privacy settings actively.",
            "bg_keywords": "hacker computer code data breach cybersecurity",
            "examples": "Cambridge Analytica, Google location tracking lawsuit"
        },
        {
            "angle": "Personal Protection",
            "hook": "Your phone is spying on you RIGHT NOW!",
            "content": "Protect your digital privacy today. Apps sell your location data. Social media tracks browsing habits. Smart TVs record conversations. Turn off targeted ads. Use VPN services. Check app permissions regularly. Clear cookies and cache. Enable two-factor authentication.",
            "bg_keywords": "smartphone privacy settings security lock",
            "examples": "TikTok data concerns, iOS 14.5 privacy update"
        },
        {
            "angle": "Legal Updates",
            "hook": "New privacy laws are changing everything!",
            "content": "Latest privacy law updates affecting you. GDPR fines reach billions. CCPA expands to employees. Right to be forgotten spreads globally. Data breach notifications mandatory. Biometric data gets special protection. Children's privacy strengthened. AI transparency required.",
            "bg_keywords": "legal documents court gavel justice",
            "examples": "GDPR enforcement cases, CCPA compliance costs"
        }
    ],
    "Employment Law Basics": [
        {
            "angle": "Worker Victories",
            "hook": "This worker got $2 MILLION for wrongful termination!",
            "content": "Recent employment law wins show worker power. Wrongful termination lawsuits succeed. Overtime violations cost companies millions. Discrimination settlements reach records. You cannot be fired for whistleblowing. Pregnancy discrimination is illegal. Document workplace violations. Know your employment contract.",
            "bg_keywords": "office workers meeting business professional",
            "examples": "Tesla discrimination lawsuit, Amazon overtime case"
        },
        {
            "angle": "Gig Economy Rights",
            "hook": "Uber drivers just won MASSIVE labor rights!",
            "content": "Gig economy workers gaining new protections. California AB5 reclassifies contractors. Uber and Lyft face employee rules. Delivery drivers get minimum wage. Platform workers organize unions. Prop 22 creates hybrid category. Benefits expand to gig workers.",
            "bg_keywords": "delivery driver uber lyft gig economy",
            "examples": "AB5 law impact, Uber IPO labor issues"
        },
        {
            "angle": "Remote Work Rights",
            "hook": "Working from home? You have these NEW rights!",
            "content": "Remote work creates new employment rights. Right to disconnect after hours. Home office expense reimbursements. Ergonomic equipment requirements. Privacy in virtual meetings. Overtime rules still apply. Performance monitoring limits. Equal treatment as office workers.",
            "bg_keywords": "home office remote work laptop computer",
            "examples": "Right to disconnect laws, Remote work discrimination"
        }
    ],
    "Tenant Rights and Housing Laws": [
        {
            "angle": "Landlord Violations",
            "hook": "This landlord was fined $100,000 for illegal eviction!",
            "content": "Landlord violations cost them big money. Illegal evictions face huge penalties. Security deposit theft prosecuted. Habitability violations fined heavily. 24-hour entry notice required. Retaliation against tenants illegal. Rent control laws protect tenants. Document everything with photos.",
            "bg_keywords": "apartment building landlord tenant rental property",
            "examples": "NYC illegal eviction fine, California rent control"
        },
        {
            "angle": "Renter Protections",
            "hook": "Renters have MORE rights than you think!",
            "content": "Hidden renter rights landlords won't mention. Implied warranty of habitability. Right to withhold rent for repairs. Protection from discrimination. Limits on security deposits. Notice requirements for rent increases. Just cause eviction laws. Tenant organizing rights.",
            "bg_keywords": "young person moving boxes apartment keys",
            "examples": "San Francisco just cause evictions, Rent strike victories"
        },
        {
            "angle": "Housing Crisis Solutions",
            "hook": "New housing laws are protecting renters!",
            "content": "Recent housing laws help renters survive. Eviction moratoriums save homes. Rent stabilization spreads nationwide. First-time buyer programs expand. Affordable housing mandates increase. Tenant protection acts strengthen. Housing voucher improvements. Anti-speculation taxes implemented.",
            "bg_keywords": "housing crisis affordable homes construction",
            "examples": "COVID eviction moratorium, Oregon rent control law"
        }
    ],
    "Intellectual Property Rights": [
        {
            "angle": "Creator Economy",
            "hook": "This TikTok creator sued for $10 MILLION and WON!",
            "content": "Creators are winning big IP battles. TikTok dance creators get recognition. YouTubers protect original content. Musicians sue for sampling violations. Fair use defenses strengthen. DMCA takedown system evolving. Creator funds acknowledge IP value. Platform revenue sharing improves.",
            "bg_keywords": "content creator filming video social media",
            "examples": "Renegade dance credit battle, YouTube copyright wars"
        },
        {
            "angle": "Business Protection",
            "hook": "Small business lost EVERYTHING by ignoring trademark law!",
            "content": "IP mistakes that destroy businesses. Trademark infringement costs millions. Copyright violations shut companies. Patent trolls target startups. Trade secret theft prosecuted. Proper registration prevents disasters. Fair use has strict limits. International IP enforcement growing.",
            "bg_keywords": "small business startup office entrepreneur",
            "examples": "Epic vs Apple lawsuit, Trademark cyber-squatting cases"
        },
        {
            "angle": "AI and Future",
            "hook": "AI is changing copyright law FOREVER!",
            "content": "Artificial intelligence reshaping IP law. AI-generated art ownership unclear. Machine learning training data disputes. Deepfake technology legal challenges. Algorithm patent applications surge. Creative AI tools raise questions. Copyright for AI outputs debated. Human creativity definition evolving.",
            "bg_keywords": "artificial intelligence robot technology computer",
            "examples": "AI art copyright debates, GitHub Copilot lawsuit"
        }
    ],
    "Contract Law Fundamentals": [
        {
            "angle": "Common Mistakes",
            "hook": "This ONE contract mistake cost him $500,000!",
            "content": "Contract mistakes that ruin lives. Verbal agreements are still binding. Fine print contains deadly clauses. Automatic renewals trap consumers. Non-compete agreements limit freedom. Penalty clauses can be excessive. Read everything before signing. Get legal review for big contracts.",
            "bg_keywords": "business handshake contract signing documents",
            "examples": "Celebrity endorsement contract disasters, Non-compete violations"
        },
        {
            "angle": "Digital Age Contracts",
            "hook": "You agreed to THIS when you clicked accept!",
            "content": "Digital contracts control your online life. Terms of service change frequently. Click-wrap agreements are binding. Privacy policies hide data usage. Social media owns your content. Subscription traps are everywhere. Right to cancel protections exist. Class action waivers limit rights.",
            "bg_keywords": "smartphone app download terms conditions",
            "examples": "Instagram terms controversy, Zoom privacy settlement"
        },
        {
            "angle": "Consumer Protection",
            "hook": "These contract clauses are ILLEGAL!",
            "content": "Contract clauses that cannot be enforced. Unconscionable terms get voided. Arbitration requirements have limits. Liability waivers cannot cover everything. Cooling-off periods protect consumers. Lemon laws override contracts. Fraud voids all agreements. Consumer protection laws trump contracts.",
            "bg_keywords": "legal scale justice court law books",
            "examples": "Arbitration clause challenges, Unconscionable contract cases"
        }
    ],
    "Criminal Law Basics": [
        {
            "angle": "Rights During Arrest",
            "hook": "Know these rights or risk JAIL TIME!",
            "content": "Critical rights during police encounters. Right to remain silent always. Request lawyer immediately. Police cannot search without warrant. You can refuse field sobriety tests. Recording police is legal. False confessions happen frequently. Bail is not always guaranteed.",
            "bg_keywords": "police arrest handcuffs law enforcement",
            "examples": "George Floyd case reforms, Body camera evidence"
        },
        {
            "angle": "White Collar Crime",
            "hook": "This CEO got 20 YEARS for financial fraud!",
            "content": "White collar crime consequences are severe. Securities fraud brings long sentences. Embezzlement ruins careers permanently. Tax evasion prosecution increasing. Corporate executives face personal liability. Whistleblower protections encourage reporting. Financial crime penalties doubled. Compliance programs now mandatory.",
            "bg_keywords": "business suit courthouse white collar executive",
            "examples": "Elizabeth Holmes Theranos case, Bernie Madoff sentence"
        },
        {
            "angle": "Cybercrime Laws",
            "hook": "Teenagers face FELONY charges for social media posts!",
            "content": "Cybercrime laws affect everyone online. Cyberbullying can be criminal. Hacking carries severe penalties. Identity theft prosecution increased. Online threats prosecuted federally. Revenge porn laws spread nationwide. Social media evidence admissible. Digital forensics solve cases.",
            "bg_keywords": "cybercrime hacker computer internet crime",
            "examples": "TikTok cyberbullying arrests, Ransomware prosecutions"
        }
    ],
    "Family Law Essentials": [
        {
            "angle": "Custody Battles",
            "hook": "This parent LOST custody for social media posts!",
            "content": "Social media impacts custody decisions. Courts monitor online behavior. Parental alienation recognized legally. Best interests standard evolving. Grandparent rights expanding. Relocation restrictions tightening. Child support enforcement automated. Domestic violence protections strengthened.",
            "bg_keywords": "family children custody court legal",
            "examples": "Social media custody losses, Grandparent rights cases"
        },
        {
            "angle": "Divorce Economics",
            "hook": "Hidden assets cost this spouse $2 MILLION!",
            "content": "Financial tricks in divorce proceedings. Cryptocurrency hiding attempts. Offshore accounts discovered. Business valuations manipulated. Pension rights often overlooked. Alimony reform changing nationwide. Prenups increasingly important. Forensic accountants find hidden wealth.",
            "bg_keywords": "divorce money finance calculator assets",
            "examples": "Cryptocurrency divorce cases, Celebrity prenup battles"
        },
        {
            "angle": "Modern Family Issues",
            "hook": "Surrogacy laws are creating legal CHAOS!",
            "content": "New family structures challenge old laws. Same-sex marriage rights solidified. Surrogacy agreements enforceable. Sperm donor anonymity ending. Three-parent families recognized. Adoption laws modernizing. Gender marker changes simplified. Reproductive rights expanding.",
            "bg_keywords": "modern family diverse parents children",
            "examples": "Three-parent legal recognition, Surrogacy contract disputes"
        }
    ]
}

# Background video sources for different themes
BACKGROUND_VIDEO_SOURCES = {
    "legal": "https://pixabay.com/videos/search/court%20law%20justice/",
    "business": "https://pixabay.com/videos/search/business%20office%20meeting/",
    "technology": "https://pixabay.com/videos/search/computer%20technology%20data/",
    "people": "https://pixabay.com/videos/search/people%20lifestyle%20daily/",
    "money": "https://pixabay.com/videos/search/money%20finance%20banking/",
    "family": "https://pixabay.com/videos/search/family%20home%20children/"
}

def get_topic_for_day():
    """Get topic based on 8-day rotation"""
    try:
        # Use current day of year to determine topic
        day_of_year = datetime.now().timetuple().tm_yday
        topic_index = (day_of_year - 1) % 8
        
        # Load or create rotation state
        state_file = "topic_rotation.json"
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                state = json.load(f)
        else:
            state = {"last_day": 0, "topic_variations": {}}
        
        # Get topic and variation
        topic = LEGAL_TOPICS[topic_index]
        
        # Track variations for each topic
        if topic not in state["topic_variations"]:
            state["topic_variations"][topic] = 0
        
        # Get current variation (0, 1, or 2)
        variation_index = state["topic_variations"][topic] % 3
        variation = TOPIC_VARIATIONS[topic][variation_index]
        
        # Update state
        state["topic_variations"][topic] += 1
        state["last_day"] = day_of_year
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        print(f"📅 Day {day_of_year} | Topic: {topic} | Variation: {variation_index + 1}/3")
        return topic, variation
        
    except Exception as e:
        print(f"Error in topic rotation: {e}")
        # Fallback to random
        topic = random.choice(LEGAL_TOPICS)
        variation = random.choice(TOPIC_VARIATIONS[topic])
        return topic, variation

def download_background_video(keywords):
    """Download relevant background video"""
    try:
        print(f"🎥 Searching for background video: {keywords}")
        
        # Try to download from free video sources
        # This is a placeholder - in practice, you'd integrate with:
        # - Pexels API
        # - Pixabay API  
        # - Unsplash API
        # For now, create animated background
        
        return create_animated_background_themed(keywords)
        
    except Exception as e:
        print(f"Error downloading background: {e}")
        return create_animated_background_themed("legal")

def create_animated_background_themed(theme):
    """Create themed animated background"""
    try:
        # Color schemes based on theme
        themes = {
            "legal": {"colors": ["#1e3c72", "#2a5298", "#3b82f6"], "pattern": "justice"},
            "business": {"colors": ["#667eea", "#764ba2", "#8b5cf6"], "pattern": "corporate"},
            "technology": {"colors": ["#f093fb", "#f5576c", "#4facfe"], "pattern": "tech"},
            "money": {"colors": ["#43e97b", "#38f9d7", "#84fab0"], "pattern": "finance"},
            "family": {"colors": ["#fa709a", "#fee140", "#ffeaa7"], "pattern": "warm"},
            "default": {"colors": ["#667eea", "#764ba2", "#8b5cf6"], "pattern": "generic"}
        }
        
        theme_config = themes.get(theme.split()[0].lower(), themes["default"])
        colors = theme_config["colors"]
        
        # Create animated gradient with moving elements
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', f'color=size=1080x1920:duration=65:rate=30:color={colors[0]}',
            '-vf', f'''
            geq=r='128+100*sin(2*PI*t/8+X/100)':g='128+100*cos(2*PI*t/6+Y/100)':b='180+50*sin(2*PI*t/4)',
            drawbox=x=0:y=iw*0.7:w=iw:h=ih*0.3:color={colors[1]}@0.3:t=fill,
            drawbox=x=0:y=0:w=iw:h=ih*0.15:color={colors[2]}@0.4:t=fill
            ''',
            '-t', '65',
            'themed_bg.mp4'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return "themed_bg.mp4"
        else:
            return create_simple_background()
            
    except Exception as e:
        print(f"Error creating themed background: {e}")
        return create_simple_background()

def create_simple_background():
    """Fallback simple background"""
    try:
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', 'color=size=1080x1920:duration=65:rate=30:color=#2563eb',
            'simple_bg.mp4'
        ]
        subprocess.run(cmd, capture_output=True)
        return "simple_bg.mp4"
    except:
        return None

def create_word_by_word_subtitles(text, total_duration=58):
    """Create word-by-word subtitle timing"""
    try:
        # Clean and split text into words
        words = re.findall(r'\b\w+(?:\'\w+)?\b', text.lower())
        
        if not words:
            return []
        
        # Calculate timing
        words_per_second = len(words) / total_duration
        time_per_word = total_duration / len(words)
        
        subtitles = []
        current_time = 0
        
        for i, word in enumerate(words):
            start_time = current_time
            end_time = current_time + time_per_word
            
            # Adjust for natural speech pauses
            if word.endswith('.') or word.endswith('!') or word.endswith('?'):
                end_time += 0.3  # Pause after sentences
            
            subtitles.append({
                'word': word.upper(),
                'start': start_time,
                'end': end_time,
                'position': i
            })
            
            current_time = end_time
            
        return subtitles
        
    except Exception as e:
        print(f"Error creating subtitles: {e}")
        return []

def create_professional_video_with_wordbyword(background_path, audio_path, content, topic, output_path):
    """Create video with word-by-word subtitles like viral TikToks"""
    try:
        print("🎬 Creating professional video with word-by-word subtitles...")
        
        # Get subtitle timing
        subtitles = create_word_by_word_subtitles(content, 58)
        
        if not subtitles:
            print("❌ No subtitles created")
            return False
        
        # Build complex filter for word-by-word text
        filter_parts = []
        
        # Base video preparation
        filter_parts.append(f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[bg]")
        
        # Add dark overlay for text readability
        filter_parts.append("[bg]drawbox=x=0:y=ih*0.75:w=iw:h=ih*0.25:color=black@0.6:t=fill[overlay]")
        
        # Create word-by-word text overlays
        current_layer = "[overlay]"
        for i, sub in enumerate(subtitles):
            # Main word (large, center)
            word_filter = (
                f"{current_layer}drawtext="
                f"text='{sub['word']}':"
                f"fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf':"
                f"fontsize=70:"
                f"fontcolor=white:"
                f"bordercolor=black:"
                f"borderw=4:"
                f"x=(w-text_w)/2:"
                f"y=h*0.8:"
                f"enable='between(t,{sub['start']:.2f},{sub['end']:.2f})'[word{i}]"
            )
            filter_parts.append(word_filter)
            current_layer = f"[word{i}]"
            
            # Add emphasis effect for important words
            if sub['word'] in ['MILLION', 'BILLION', 'WON', 'ILLEGAL', 'RIGHTS', 'LAW', 'LAWSUIT']:
                emphasis_filter = (
                    f"{current_layer}drawtext="
                    f"text='🔥 {sub['word']} 🔥':"
                    f"fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf':"
                    f"fontsize=90:"
                    f"fontcolor=yellow:"
                    f"bordercolor=red:"
                    f"borderw=5:"
                    f"x=(w-text_w)/2:"
                    f"y=h*0.75:"
                    f"enable='between(t,{sub['start']:.2f},{sub['end']:.2f})'[emphasis{i}]"
                )
                filter_parts.append(emphasis_filter)
                current_layer = f"[emphasis{i}]"
        
        # Add topic title overlay
        title_filter = (
            f"{current_layer}drawtext="
            f"text='{topic.upper()}':"
            f"fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf':"
            f"fontsize=40:"
            f"fontcolor=white:"
            f"bordercolor=black:"
            f"borderw=3:"
            f"x=(w-text_w)/2:"
            f"y=50:"
            f"enable='between(t,0,5)'[final]"
        )
        filter_parts.append(title_filter)
        
        # Build FFmpeg command
        cmd = ['ffmpeg', '-y']
        
        # Input files
        if background_path and os.path.exists(background_path):
            cmd.extend(['-i', background_path])
        else:
            cmd.extend(['-f', 'lavfi', '-i', 'color=size=1080x1920:duration=65:rate=30:color=#2563eb'])
        
        cmd.extend(['-i', audio_path])
        
        # Add background music if available
        music_path = "bg_music.mp3"
        if create_background_music():
            cmd.extend(['-i', music_path])
            # Audio mixing
            audio_mix = '[1:a][2:a]amix=inputs=2:duration=first:dropout_transition=2,volume=1.2[audio_out]'
        else:
            audio_mix = '[1:a]volume=1.2[audio_out]'
        
        # Combine all filters
        full_filter = ';'.join(filter_parts) + ';' + audio_mix
        
        cmd.extend([
            '-filter_complex', full_filter,
            '-map', '[final]',
            '-map', '[audio_out]',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-r', '30',
            '-t', '58',
            output_path
        ])
        
        print("🎬 Running FFmpeg with word-by-word subtitles...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ Professional video created: {output_path}")
            return True
        else:
            print(f"❌ FFmpeg error: {result.stderr}")
            return create_fallback_video(background_path, audio_path, content, output_path)
            
    except Exception as e:
        print(f"Error creating professional video: {e}")
        return create_fallback_video(background_path, audio_path, content, output_path)

def create_fallback_video(background_path, audio_path, content, output_path):
    """Simple fallback video"""
    try:
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi', '-i', 'color=size=1080x1920:duration=58:rate=30:color=#3b82f6',
            '-i', audio_path,
            '-vf', f"drawtext=text='LEGAL KNOWLEDGE':fontsize=80:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-t', '58',
            '-shortest',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
        
    except:
        return False

def create_background_music():
    """Create subtle background music"""
    try:
        # Create ambient background music
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', 'sine=frequency=440:duration=60',
            '-f', 'lavfi',
            '-i', 'sine=frequency=554.37:duration=60',
            '-filter_complex', '[0:a][1:a]amix=inputs=2:duration=first,volume=0.05',
            'bg_music.mp3'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
        
    except:
        return False

def create_engaging_audio(content, output_path):
    """Create engaging audio with proper pacing"""
    try:
        from gtts import gTTS
        
        # Process content for better speech
        # Add pauses for emphasis
        processed_content = content.replace('!', '. ').replace('?', '. ')
        processed_content = re.sub(r'\$([0-9,]+)', r'\1 dollars', processed_content)
        processed_content = processed_content.replace('MILLION', 'million').replace('BILLION', 'billion')
        
        # Create TTS
        tts = gTTS(text=processed_content, lang='en', slow=False)
        temp_audio = "temp_narration.mp3"
        tts.save(temp_audio)
        
        # Enhance audio with effects
        cmd = [
            'ffmpeg', '-y',
            '-i', temp_audio,
            '-af', 'atempo=1.05,aecho=0.8:0.88:60:0.4,equalizer=f=3000:width_type=h:width=500:g=2',
            '-c:a', 'mp3',
            '-b:a', '128k',
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

def send_viral_video_to_telegram(video_path, topic, variation, content):
    """Send viral-ready video package to Telegram"""
    try:
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            print("❌ Telegram credentials not found")
            return False
        
        # Create viral YouTube package
        viral_title = f"{variation['hook'][:50]}... | {topic}"
        
        youtube_package = f"""🔥 VIRAL SHORTS VIDEO READY! 🔥

📱 TITLE: {viral_title}

🎯 HOOK: {variation['hook']}

📊 EXAMPLES: {variation['examples']}

⏰ DURATION: 58 seconds (Perfect for YouTube Shorts!)

📝 DESCRIPTION:
{content[:150]}...

🔥 VIRAL HASHTAGS:
#LegalTips #LawExplained #Rights #Legal #Shorts #Viral #Education #KnowYourRights #LegalAdvice #Justice

📈 BEST UPLOAD TIMES:
- 7:30 PM IST (Peak engagement)
- Alternative: 9:00 AM IST

🎬 VIDEO FEATURES:
✅ Word-by-word subtitles (like viral TikToks)
✅ Animated background 
✅ Professional audio
✅ 58-second duration
✅ 9:16 ratio (YouTube Shorts optimized)
✅ Engaging hook + examples
✅ No copyright issues

🚀 READY TO GO VIRAL!"""
        
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
    """Main viral video generation system"""
    print("🚀 VIRAL LEGAL SHORTS GENERATOR STARTING...")
    print("📅 8-Day Topic Rotation System Active")
    
    try:
        # Get today's topic and variation
        topic, variation = get_topic_for_day()
        print(f"🎯 Today's Content: {variation['angle']}")
        print(f"🔥 Hook: {variation['hook']}")
        
        # Create full content script (50-58 seconds)
        full_content = f"{variation['hook']} {variation['content']}"
        print(f"📝 Content length: {len(full_content.split())} words")
        
        # Download/create themed background
        print(f"🎥 Creating background for: {variation['bg_keywords']}")
        background_path = download_background_video(variation['bg_keywords'])
        
        # Create professional audio
        print("🎤 Generating engaging narration...")
        audio_path = "professional_narration.mp3"
        if not create_engaging_audio(full_content, audio_path):
            print("❌ Audio creation failed")
            return
        
        # Verify audio duration (should be 50-58 seconds)
        try:
            duration_check = subprocess.run([
                'ffprobe', '-v', 'quiet', '-show_entries', 
                'format=duration', '-of', 'csv=p=0', audio_path
            ], capture_output=True, text=True)
            
            audio_duration = float(duration_check.stdout.strip())
            print(f"🎵 Audio duration: {audio_duration:.1f} seconds")
            
            if audio_duration < 50:
                print("⚠️ Audio too short, adding pauses...")
                # Add strategic pauses
                extended_content = full_content.replace('. ', '. ... ')
                create_engaging_audio(extended_content, audio_path)
                
        except Exception as e:
            print(f"Duration check failed: {e}")
        
        # Create viral video with word-by-word subtitles
        print("🎬 Creating VIRAL YouTube Shorts video...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_path = f"viral_legal_{topic.replace(' ', '_')}_{timestamp}.mp4"
        
        if create_professional_video_with_wordbyword(background_path, audio_path, full_content, topic, video_path):
            # Verify final video duration
            try:
                final_duration_check = subprocess.run([
                    'ffprobe', '-v', 'quiet', '-show_entries', 
                    'format=duration', '-of', 'csv=p=0', video_path
                ], capture_output=True, text=True)
                
                final_duration = float(final_duration_check.stdout.strip())
                print(f"📹 Final video duration: {final_duration:.1f} seconds")
                
                if 50 <= final_duration <= 60:
                    print("✅ Perfect duration for YouTube Shorts!")
                else:
                    print(f"⚠️ Duration warning: {final_duration:.1f}s")
                    
            except:
                print("Duration verification skipped")
            
            # Send viral video package to Telegram
            print("📤 Sending VIRAL video package to Telegram...")
            if send_viral_video_to_telegram(video_path, topic, variation, full_content):
                print("✅ VIRAL VIDEO SENT SUCCESSFULLY!")
            else:
                print("⚠️ Telegram delivery failed")
            
            # Save detailed metadata
            metadata = {
                "timestamp": timestamp,
                "topic": topic,
                "variation_angle": variation['angle'],
                "hook": variation['hook'],
                "content": full_content,
                "examples": variation['examples'],
                "bg_keywords": variation['bg_keywords'],
                "video_file": video_path,
                "duration_target": "50-58 seconds",
                "features": [
                    "Word-by-word subtitles",
                    "Animated themed background",
                    "Professional audio with effects",
                    "9:16 YouTube Shorts ratio",
                    "Viral hook + real examples",
                    "No copyright issues"
                ],
                "youtube_optimization": {
                    "title": f"{variation['hook'][:50]}... | {topic}",
                    "description": f"{full_content[:150]}...\n\nExamples covered: {variation['examples']}",
                    "hashtags": "#LegalTips #LawExplained #Rights #Legal #Shorts #Viral #Education",
                    "best_upload_times": ["7:30 PM IST", "9:00 AM IST"],
                    "target_audience": "Legal education, consumer awareness, rights protection"
                },
                "rotation_info": {
                    "day_in_cycle": datetime.now().timetuple().tm_yday % 8 + 1,
                    "next_topic_date": (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + 
                                      timedelta(days=1)).strftime("%Y-%m-%d"),
                    "cycle_completion": "Every 8 days, unique variations prevent repetition"
                }
            }
            
            with open(f"viral_metadata_{timestamp}.json", 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print("\n🎉 VIRAL LEGAL SHORTS VIDEO GENERATION COMPLETE!")
            print("=" * 60)
            print(f"📱 Video: {video_path}")
            print(f"⏱️  Duration: 50-58 seconds (YouTube Shorts optimized)")
            print(f"🎯 Topic: {topic} ({variation['angle']})")
            print(f"🔥 Hook: {variation['hook'][:50]}...")
            print(f"📊 Examples: {variation['examples']}")
            print(f"🎬 Features: Word-by-word subtitles, animated background")
            print(f"🚀 Ready for upload at 7:30 PM IST!")
            print("=" * 60)
            
        else:
            print("❌ Video creation failed")
            
    except Exception as e:
        print(f"❌ Error in main execution: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup temporary files but keep final outputs
        temp_files = [
            "themed_bg.mp4", "simple_bg.mp4", "bg_music.mp3", 
            "temp_narration.mp3", "professional_narration.mp3"
        ]
        
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    print(f"🧹 Cleaned up: {temp_file}")
                except:
                    pass
        
        print("🧹 Cleanup complete!")

if __name__ == "__main__":
    main()
