#!/usr/bin/env python3
import cv2
import numpy as np
from moviepy.editor import *
import os
import json
import random
from datetime import datetime, timedelta
import requests
from PIL import Image, ImageDraw, ImageFont
import math
import tempfile
import sys

# Configure MoviePy to avoid download issues
os.environ['IMAGEIO_FFMPEG_EXE'] = '/usr/bin/ffmpeg'

class ViralLegalShortsSystem:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = os.path.join(self.base_dir, "output")
        self.video_dir = os.path.join(self.output_dir, "videos")
        self.audio_dir = os.path.join(self.output_dir, "audio")
        self.thumbnail_dir = os.path.join(self.output_dir, "thumbnails")
        self.logs_dir = os.path.join(self.base_dir, "logs")
        
        # Create directories
        for directory in [self.output_dir, self.video_dir, self.audio_dir, self.thumbnail_dir, self.logs_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # 8-topic rotation system
        self.topics = [
            "consumer_rights", "labor_employment", "data_privacy", "corporate_law",
            "family_law", "criminal_law", "intellectual_property", "ai_legal_tools"
        ]
        
        # Power words for viral emphasis
        self.power_words = [
            "MILLION", "BILLION", "LAWSUIT", "ILLEGAL", "BANNED", "FIRED", "ARRESTED", 
            "SUED", "VIOLATION", "PENALTY", "SETTLEMENT", "VERDICT", "GUILTY", "YEARS"
        ]
        
        # Video specifications
        self.video_config = {
            'width': 1080,
            'height': 1920,
            'fps': 30,
            'duration': 55,
            'font_size_regular': 70,
            'font_size_power': 85
        }

    def get_current_topic(self):
        """Get current topic based on 8-day rotation"""
        start_date = datetime(2024, 1, 1)
        days_passed = (datetime.now() - start_date).days
        topic_index = days_passed % 8
        variation = (days_passed // 8) % 3
        
        return self.topics[topic_index], variation

    def get_content_data(self, topic, variation):
        """Get content data for specific topic and variation"""
        content_database = {
            "consumer_rights": {
                0: {
                    "title": "Amazon Paid $100 MILLION - Here's Why",
                    "hook": "Amazon just paid $100 MILLION in fines!",
                    "key_points": [
                        "Amazon charged Prime members without consent",
                        "FTC fined them $100 MILLION dollars",
                        "Customers got automatic refunds",
                        "This violates consumer protection laws",
                        "You can report similar violations to FTC"
                    ],
                    "shocking_fact": "Amazon made $469 billion in 2021 but still tried to overcharge customers",
                    "call_to_action": "Check your subscriptions NOW for unauthorized charges!"
                },
                1: {
                    "title": "This Company Owes You Money - Check Now!",
                    "hook": "Millions of people are owed money and don't know it!",
                    "key_points": [
                        "Class action settlements often go unclaimed",
                        "Facebook paid $725 MILLION in privacy settlement",
                        "Google paid $391 MILLION for location tracking",
                        "Check if you qualify for compensation",
                        "Deadlines are usually strict - act fast!"
                    ],
                    "shocking_fact": "Over $3 BILLION in settlements go unclaimed every year",
                    "call_to_action": "Search 'class action settlement' + your state now!"
                },
                2: {
                    "title": "Your Rights When Companies Scam You",
                    "hook": "Companies bank on you NOT knowing your rights!",
                    "key_points": [
                        "You can dispute charges within 60 days",
                        "Companies must honor their advertised prices",
                        "Bait and switch tactics are ILLEGAL",
                        "Document everything for evidence",
                        "Small claims court is your friend"
                    ],
                    "shocking_fact": "98% of people never exercise their consumer rights",
                    "call_to_action": "Know your rights - save this video!"
                }
            },
            "labor_employment": {
                0: {
                    "title": "Tesla Paid $137 MILLION - Workplace Discrimination",
                    "hook": "Tesla just paid $137 MILLION for discrimination!",
                    "key_points": [
                        "Employee faced racial harassment at Tesla",
                        "Company failed to address complaints",
                        "Jury awarded $137 MILLION in damages",
                        "This sets precedent for workplace rights",
                        "Document all discrimination incidents"
                    ],
                    "shocking_fact": "Workplace discrimination costs companies $64 billion annually",
                    "call_to_action": "Know your workplace rights - report discrimination!"
                },
                1: {
                    "title": "Your Boss CAN'T Do This - It's ILLEGAL",
                    "hook": "Your boss is breaking the law if they do this!",
                    "key_points": [
                        "Can't ask about pregnancy in interviews",
                        "Can't retaliate for filing complaints",
                        "Must pay overtime over 40 hours",
                        "Can't discriminate based on religion",
                        "Must provide reasonable accommodations"
                    ],
                    "shocking_fact": "73% of workers don't know basic employment rights",
                    "call_to_action": "Share this to protect workers' rights!"
                },
                2: {
                    "title": "Wage Theft: $50 BILLION Stolen Annually",
                    "hook": "$50 BILLION stolen from workers every year!",
                    "key_points": [
                        "Unpaid overtime is wage theft",
                        "Off-the-clock work is ILLEGAL",
                        "Tip stealing violates federal law",
                        "You can recover stolen wages plus penalties",
                        "File complaints with Department of Labor"
                    ],
                    "shocking_fact": "Wage theft exceeds all other property crimes combined",
                    "call_to_action": "Calculate your stolen wages - you might be owed thousands!"
                }
            },
            "data_privacy": {
                0: {
                    "title": "Meta Paid $5.1 BILLION GDPR Fine",
                    "hook": "Facebook's parent company paid $5.1 BILLION!",
                    "key_points": [
                        "Meta violated GDPR privacy regulations",
                        "Largest privacy fine in history",
                        "Your data is worth more than you think",
                        "EU gives you right to delete your data",
                        "Companies must ask permission first"
                    ],
                    "shocking_fact": "Your personal data is worth $1,000+ annually to tech companies",
                    "call_to_action": "Review your privacy settings on all platforms NOW!"
                },
                1: {
                    "title": "Your Phone is Spying - Here's Proof",
                    "hook": "Your phone listens even when you think it's off!",
                    "key_points": [
                        "Location tracking continues when 'disabled'",
                        "Microphone activates for ad targeting",
                        "Apps share data with 1000+ companies",
                        "Delete data from Google and Apple",
                        "Use privacy-focused alternatives"
                    ],
                    "shocking_fact": "Average smartphone shares data with 1,200 companies",
                    "call_to_action": "Turn off location services and microphone access now!"
                },
                2: {
                    "title": "Data Brokers Sell Your Info for $100s",
                    "hook": "Companies sell your personal data for hundreds!",
                    "key_points": [
                        "Data brokers collect without permission",
                        "They sell to insurance and employers",
                        "Your SSN sells for $1-$15 on dark web",
                        "Credit reports affect your life",
                        "You can opt out of most databases"
                    ],
                    "shocking_fact": "There are 4,000+ data broker companies operating legally",
                    "call_to_action": "Opt out of data brokers - protect your privacy!"
                }
            },
            "corporate_law": {
                0: {
                    "title": "This CEO Got 30 YEARS in Prison",
                    "hook": "CEO sentenced to 30 YEARS for corporate fraud!",
                    "key_points": [
                        "Theranos CEO Elizabeth Holmes convicted",
                        "Defrauded investors of $900 MILLION",
                        "Fake blood testing technology",
                        "Put patients' lives at risk",
                        "Corporate executives aren't above the law"
                    ],
                    "shocking_fact": "Only 3% of corporate criminals serve jail time",
                    "call_to_action": "Corporate accountability matters - stay informed!"
                },
                1: {
                    "title": "Shareholders Can Sue CEOs Personally",
                    "hook": "Shareholders are suing CEOs for BILLIONS!",
                    "key_points": [
                        "Derivative lawsuits hold executives accountable",
                        "CEOs can be personally liable for damages",
                        "Breach of fiduciary duty has consequences",
                        "Shareholders recovered $7.4 BILLION in 2022",
                        "Even board members face personal liability"
                    ],
                    "shocking_fact": "CEO compensation has grown 1,400% since 1978",
                    "call_to_action": "If you own stocks, know your shareholder rights!"
                },
                2: {
                    "title": "Corporate Whistleblowers Get $100M+ Rewards",
                    "hook": "This whistleblower got $114 MILLION reward!",
                    "key_points": [
                        "SEC paid $114 MILLION to one whistleblower",
                        "Protected under federal law",
                        "Can't be fired for reporting violations",
                        "10-30% of penalties go to whistleblowers",
                        "Anonymous reporting is allowed"
                    ],
                    "shocking_fact": "SEC has paid $1.3 BILLION to whistleblowers since 2012",
                    "call_to_action": "See corporate fraud? Report it - you're protected!"
                }
            },
            "family_law": {
                0: {
                    "title": "Hidden Assets in Divorce - $1M Found",
                    "hook": "Spouse hid $1 MILLION in divorce - here's how!",
                    "key_points": [
                        "Cryptocurrency wallets are often hidden",
                        "Offshore accounts require investigation",
                        "Business valuations can be manipulated",
                        "Forensic accountants find hidden money",
                        "Hiding assets is contempt of court"
                    ],
                    "shocking_fact": "30% of spouses hide assets during divorce proceedings",
                    "call_to_action": "Protect yourself - hire a forensic accountant!"
                },
                1: {
                    "title": "Child Support Can Be Modified - Here's How",
                    "hook": "You can change child support amounts legally!",
                    "key_points": [
                        "Income changes justify modifications",
                        "Job loss requires immediate action",
                        "Medical expenses affect calculations",
                        "Custody changes impact support",
                        "Don't wait - file promptly"
                    ],
                    "shocking_fact": "$33 BILLION in child support goes uncollected annually",
                    "call_to_action": "Know your rights - modifications are possible!"
                },
                2: {
                    "title": "Prenups Save MILLIONS in Divorce",
                    "hook": "This prenup saved $50 MILLION in divorce!",
                    "key_points": [
                        "Prenups protect business ownership",
                        "Separate property stays separate",
                        "Alimony can be limited or waived",
                        "Must be fair and properly executed",
                        "Both parties need separate lawyers"
                    ],
                    "shocking_fact": "Divorce costs average $15,000 per person without prenup",
                    "call_to_action": "Protect your assets - consider a prenuptial agreement!"
                }
            },
            "criminal_law": {
                0: {
                    "title": "Know Your Rights - Police Can't Do This",
                    "hook": "Police violated rights - $2.3 MILLION settlement!",
                    "key_points": [
                        "You have the right to remain silent",
                        "Can't search without warrant or consent",
                        "Must read Miranda rights during arrest",
                        "Illegal evidence gets thrown out",
                        "Document all police interactions"
                    ],
                    "shocking_fact": "Police misconduct costs taxpayers $2 BILLION annually",
                    "call_to_action": "Know your rights - they protect you!"
                },
                1: {
                    "title": "Expungement Can Clear Your Record",
                    "hook": "Clear your criminal record - it's possible!",
                    "key_points": [
                        "Many crimes can be expunged",
                        "Waiting periods vary by state",
                        "Background checks won't show expunged records",
                        "Improves employment opportunities",
                        "Lawyer not always required"
                    ],
                    "shocking_fact": "70 million Americans have criminal records affecting employment",
                    "call_to_action": "Check if you qualify for expungement!"
                },
                2: {
                    "title": "Self-Defense Laws Vary by State",
                    "hook": "Self-defense laws could save or destroy you!",
                    "key_points": [
                        "Stand Your Ground vs Duty to Retreat",
                        "Castle Doctrine protects home defense",
                        "Must be proportional to threat",
                        "Document evidence immediately",
                        "Call 911 even if attacker flees"
                    ],
                    "shocking_fact": "Self-defense cases vary 400% in outcome by state",
                    "call_to_action": "Know your state's self-defense laws!"
                }
            },
            "intellectual_property": {
                0: {
                    "title": "This Patent Made $1 BILLION - Here's How",
                    "hook": "One patent generated $1 BILLION in royalties!",
                    "key_points": [
                        "Pharmaceutical patents are extremely valuable",
                        "Patent trolls make millions licensing",
                        "20-year protection from filing date",
                        "International filing multiplies value",
                        "Prior art research is crucial"
                    ],
                    "shocking_fact": "Patent litigation costs exceed $29 BILLION annually",
                    "call_to_action": "Have an invention? File a patent application!"
                },
                1: {
                    "title": "Trademark Your Business Name NOW",
                    "hook": "Lost business name cost $500,000 - here's why!",
                    "key_points": [
                        "Federal trademarks beat state registrations",
                        "Domain names don't equal trademark rights",
                        "Use it or lose it rule applies",
                        "Infringement damages can be triple",
                        "Registration takes 8-12 months"
                    ],
                    "shocking_fact": "85% of small businesses don't trademark their names",
                    "call_to_action": "Protect your brand - file trademark application!"
                },
                2: {
                    "title": "Copyright Infringement: $150K Per Work",
                    "hook": "Copyright violation cost $150,000 PER WORK!",
                    "key_points": [
                        "Automatic copyright on creative works",
                        "Registration required for lawsuit",
                        "Statutory damages up to $150,000",
                        "Fair use has strict limitations",
                        "DMCA takedowns work fast"
                    ],
                    "shocking_fact": "Copyright infringement costs creators $29.2 BILLION yearly",
                    "call_to_action": "Register your copyrights - protect your creations!"
                }
            },
            "ai_legal_tools": {
                0: {
                    "title": "AI Lawyer Won $50,000 Case",
                    "hook": "AI lawyer just won a $50,000 case!",
                    "key_points": [
                        "DoNotPay AI fights parking tickets",
                        "ChatGPT helps draft legal documents",
                        "AI analyzes contracts in minutes",
                        "Legal research became 10x faster",
                        "Still need human lawyer oversight"
                    ],
                    "shocking_fact": "AI legal tools reduce legal costs by 70%",
                    "call_to_action": "Try AI legal tools - but verify with lawyers!"
                },
                1: {
                    "title": "Legal Research Just Got 1000x Faster",
                    "hook": "What took lawyers weeks now takes minutes!",
                    "key_points": [
                        "Westlaw and LexisNexis have AI search",
                        "Case law analysis in seconds",
                        "Contract review identifies risks",
                        "Legal briefs write themselves",
                        "Lawyers who don't adapt will lose"
                    ],
                    "shocking_fact": "AI can review contracts 60% faster than lawyers",
                    "call_to_action": "Law students: Learn AI tools or fall behind!"
                },
                2: {
                    "title": "Will AI Replace Lawyers? The Answer",
                    "hook": "AI replacing lawyers? Here's the TRUTH!",
                    "key_points": [
                        "Routine work gets automated first",
                        "Complex litigation still needs humans",
                        "Client relations remain crucial",
                        "Ethical judgment can't be programmed",
                        "AI augments rather than replaces"
                    ],
                    "shocking_fact": "23% of lawyer tasks can be automated with current AI",
                    "call_to_action": "Lawyers: Embrace AI or become irrelevant!"
                }
            }
        }
        
        return content_database[topic][variation]

    def create_animated_background(self, theme, duration):
        """Create theme-specific animated background"""
        def make_frame(t):
            # Create base canvas
            frame = np.zeros((self.video_config['height'], self.video_config['width'], 3), dtype=np.uint8)
            
            if theme == "corporate":
                # Corporate blue gradient with moving elements
                for y in range(self.video_config['height']):
                    intensity = int(127 + 50 * math.sin(0.01 * y + t))
                    frame[y, :] = [intensity//4, intensity//2, intensity]
                
                # Add moving corporate symbols
                center_x, center_y = self.video_config['width']//2, self.video_config['height']//2
                for i in range(3):
                    angle = t * 0.5 + i * 2.09
                    x = int(center_x + 200 * math.cos(angle))
                    y = int(center_y + 200 * math.sin(angle))
                    if 0 <= x < self.video_config['width'] and 0 <= y < self.video_config['height']:
                        cv2.circle(frame, (x, y), 30, (100, 150, 255), -1)
            
            elif theme == "justice":
                # Justice theme with scales and gavel
                # Golden gradient background
                for y in range(self.video_config['height']):
                    intensity = int(80 + 30 * math.sin(0.005 * y + t * 0.5))
                    frame[y, :] = [intensity//3, intensity//2, intensity]
                
                # Moving scales of justice pattern
                for i in range(5):
                    y_pos = int(200 + 300 * i + 50 * math.sin(t + i))
                    cv2.rectangle(frame, (400, y_pos), (680, y_pos + 40), (200, 180, 100), -1)
            
            elif theme == "cyber":
                # Cybersecurity matrix theme
                frame.fill(5)  # Dark background
                
                # Matrix rain effect
                for x in range(0, self.video_config['width'], 20):
                    drop_pos = int((t * 100 + x * 3) % (self.video_config['height'] + 100))
                    if drop_pos < self.video_config['height']:
                        intensity = max(0, 255 - abs(drop_pos - self.video_config['height']//2))
                        cv2.circle(frame, (x, drop_pos), 3, (0, intensity, 0), -1)
            
            elif theme == "tech":
                # Technology/AI theme
                # Neural network visualization
                frame[:, :] = [10, 10, 30]  # Dark blue base
                
                # Animated neural connections
                nodes = [(200, 300), (500, 200), (800, 400), (600, 600), (300, 700)]
                for i, (x1, y1) in enumerate(nodes):
                    for j, (x2, y2) in enumerate(nodes[i+1:], i+1):
                        intensity = int(100 + 50 * math.sin(t + i + j))
                        cv2.line(frame, (x1, y1), (x2, y2), (0, intensity, intensity//2), 2)
                    
                    # Pulsing nodes
                    pulse = int(20 + 10 * math.sin(t * 2 + i))
                    cv2.circle(frame, (x1, y1), pulse, (0, 200, 255), -1)
            
            else:  # default/legal
                # Professional legal theme
                for y in range(self.video_config['height']):
                    intensity = int(60 + 20 * math.sin(0.003 * y + t * 0.3))
                    frame[y, :] = [intensity, intensity, intensity + 40]
                
                # Moving legal symbols
                for i in range(4):
                    x = int(200 + 700 * (i / 3) + 50 * math.sin(t + i))
                    y = int(400 + 200 * math.sin(t * 0.7 + i))
                    cv2.rectangle(frame, (x-20, y-20), (x+20, y+20), (150, 150, 200), -1)
            
            return frame
        
        # Create video clip using VideoClip instead of VideoFileClip
        return VideoClip(make_frame, duration=duration).set_fps(self.video_config['fps'])

    def create_viral_subtitles(self, script, duration):
        """Create word-by-word viral subtitles with power word emphasis using OpenCV"""
        words = script.split()
        word_duration = duration / len(words)
        subtitle_clips = []
        
        for i, word in enumerate(words):
            start_time = i * word_duration
            
            # Check if word is a power word
            is_power_word = any(power in word.upper() for power in self.power_words)
            
            if is_power_word:
                display_word = f"🔥{word.upper()}🔥"
                font_scale = 2.5
                color = (0, 255, 255)  # Yellow in BGR
                thickness = 4
            else:
                display_word = word.upper()
                font_scale = 2.0
                color = (255, 255, 255)  # White in BGR
                thickness = 3
            
            # Create subtitle clip using OpenCV
            def make_text_frame(t):
                # Create transparent frame
                frame = np.zeros((self.video_config['height'], self.video_config['width'], 3), dtype=np.uint8)
                
                # Get text size
                font = cv2.FONT_HERSHEY_SIMPLEX
                text_size = cv2.getTextSize(display_word, font, font_scale, thickness)[0]
                
                # Calculate position (center horizontally, bottom third vertically)
                x = (self.video_config['width'] - text_size[0]) // 2
                y = int(self.video_config['height'] * 0.75)
                
                # Draw text outline (black)
                cv2.putText(frame, display_word, (x-2, y-2), font, font_scale, (0, 0, 0), thickness+2, cv2.LINE_AA)
                cv2.putText(frame, display_word, (x+2, y+2), font, font_scale, (0, 0, 0), thickness+2, cv2.LINE_AA)
                cv2.putText(frame, display_word, (x-2, y+2), font, font_scale, (0, 0, 0), thickness+2, cv2.LINE_AA)
                cv2.putText(frame, display_word, (x+2, y-2), font, font_scale, (0, 0, 0), thickness+2, cv2.LINE_AA)
                
                # Draw main text
                cv2.putText(frame, display_word, (x, y), font, font_scale, color, thickness, cv2.LINE_AA)
                
                return frame
            
            # Create video clip for this word
            text_clip = VideoClip(make_text_frame, duration=word_duration).set_start(start_time)
            subtitle_clips.append(text_clip)
        
        return subtitle_clips

    def create_background_music(self, theme, duration):
        """Create theme-appropriate background music"""
        # Simple tone generation for background music
        sample_rate = 44100
        samples = int(sample_rate * duration)
        
        # Create basic chord progression based on theme
        if theme == "corporate":
            frequencies = [261.63, 329.63, 392.00, 523.25]  # C major progression
        elif theme == "justice":
            frequencies = [293.66, 369.99, 440.00, 587.33]  # D major progression
        elif theme == "cyber":
            frequencies = [220.00, 277.18, 329.63, 440.00]  # A minor progression
        else:
            frequencies = [261.63, 329.63, 392.00, 523.25]  # Default C major
        
        # Generate simple background tone
        t = np.linspace(0, duration, samples)
        audio = np.zeros(samples)
        
        for i, freq in enumerate(frequencies):
            wave = 0.1 * np.sin(2 * np.pi * freq * t) * np.exp(-t/10)  # Decaying tone
            audio += wave
        
        # Normalize audio
        audio = audio / np.max(np.abs(audio)) * 0.3  # 30% volume for background
        
        # Create temporary audio file
        temp_audio_path = os.path.join(self.audio_dir, f"bg_music_{theme}.wav")
        
        # Save audio using scipy if available, otherwise skip music
        try:
            from scipy.io import wavfile
            wavfile.write(temp_audio_path, sample_rate, (audio * 32767).astype(np.int16))
            return AudioFileClip(temp_audio_path)
        except ImportError:
            print("Scipy not available, skipping background music")
            return None

    def create_marketing_package(self, content_data, topic):
        """Create complete marketing package"""
        titles = [
            content_data['title'],
            content_data['hook'],
            f"🚨 {content_data['shocking_fact'][:50]}...",
            f"Legal Alert: {topic.replace('_', ' ').title()}",
            f"💰 This Will Save You Money - {topic.replace('_', ' ').title()}"
        ]
        
        description = f"""
{content_data['hook']}

Key Points:
{chr(10).join([f'• {point}' for point in content_data['key_points']])}

🔥 SHOCKING FACT: {content_data['shocking_fact']}

{content_data['call_to_action']}

⚖️ LEGAL DISCLAIMER: This content is for educational purposes only and does not constitute legal advice. Consult with a qualified attorney for specific legal matters.

#LegalAdvice #KnowYourRights #LegalEducation #ConsumerRights #{topic.title().replace('_', '')}
        """
        
        hashtags = [
            f"#{topic.replace('_', '').title()}", "#LegalAdvice", "#KnowYourRights", 
            "#LegalEducation", "#LawyerTips", "#LegalShorts", "#ConsumerRights",
            "#EmploymentLaw", "#CorporateLaw", "#FamilyLaw"
        ]
        
        return {
            'titles': titles,
            'description': description.strip(),
            'hashtags': hashtags,
            'upload_time': '19:30',  # 7:30 PM IST
            'engagement_strategy': f"Post at 7:30 PM IST for maximum engagement. Focus on {topic.replace('_', ' ')} audience."
        }

    def generate_video(self, topic=None, variation=None):
        """Generate complete viral legal short"""
        try:
            # Get current topic and variation
            if topic is None or variation is None:
                current_topic, current_variation = self.get_current_topic()
            else:
                current_topic, current_variation = topic, variation
            
            print(f"Generating video for {current_topic} (variation {current_variation})")
            
            # Get content data
            content_data = self.get_content_data(current_topic, current_variation)
            
            # Create script
            script_parts = [
                content_data['hook'],
                ' '.join(content_data['key_points'][:3]),  # First 3 key points
                content_data['shocking_fact'],
                content_data['call_to_action']
            ]
            script = ' '.join(script_parts)
            
            # Determine theme for animations
            theme_mapping = {
                'consumer_rights': 'corporate',
                'labor_employment': 'corporate', 
                'data_privacy': 'cyber',
                'corporate_law': 'corporate',
                'family_law': 'legal',
                'criminal_law': 'justice',
                'intellectual_property': 'legal',
                'ai_legal_tools': 'tech'
            }
            theme = theme_mapping.get(current_topic, 'legal')
            
            print("Creating animated background...")
            # Create animated background
            background = self.create_animated_background(theme, self.video_config['duration'])
            
            print("Creating viral subtitles...")
            # Create viral subtitles
            subtitles = self.create_viral_subtitles(script, self.video_config['duration'])
            
            print("Creating background music...")
            # Create background music
            bg_music = self.create_background_music(theme, self.video_config['duration'])
            
            print("Compositing final video...")
            # Compose final video
            video_clips = [background] + subtitles
            final_video = CompositeVideoClip(video_clips, size=(self.video_config['width'], self.video_config['height']))
            
            # Add background music if available
            if bg_music:
                final_video = final_video.set_audio(bg_music)
            
            # Generate output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"legal_short_{current_topic}_{current_variation}_{timestamp}.mp4"
            output_path = os.path.join(self.video_dir, output_filename)
            
            print(f"Exporting video to {output_path}...")
            # Export video with optimized settings
            final_video.write_videofile(
                output_path,
                fps=self.video_config['fps'],
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Generate marketing package
            marketing = self.create_marketing_package(content_data, current_topic)
            
            # Save marketing package
            marketing_filename = f"marketing_{current_topic}_{current_variation}_{timestamp}.json"
            marketing_path = os.path.join(self.output_dir, marketing_filename)
            
            with open(marketing_path, 'w') as f:
                json.dump(marketing, f, indent=2)
            
            # Create thumbnail
            thumbnail_path = self.create_thumbnail(content_data, current_topic, timestamp)
            
            # Log generation
            log_data = {
                'timestamp': timestamp,
                'topic': current_topic,
                'variation': current_variation,
                'video_path': output_path,
                'marketing_path': marketing_path,
                'thumbnail_path': thumbnail_path,
                'script_length': len(script.split()),
                'duration': self.video_config['duration'],
                'theme': theme
            }
            
            log_filename = f"generation_log_{timestamp}.json"
            log_path = os.path.join(self.logs_dir, log_filename)
            
            with open(log_path, 'w') as f:
                json.dump(log_data, f, indent=2)
            
            print(f"✅ Video generated successfully!")
            print(f"📹 Video: {output_path}")
            print(f"📋 Marketing: {marketing_path}")
            print(f"🖼️ Thumbnail: {thumbnail_path}")
            print(f"📊 Log: {log_path}")
            
            return {
                'success': True,
                'video_path': output_path,
                'marketing_path': marketing_path,
                'thumbnail_path': thumbnail_path,
                'content_data': content_data
            }
            
        except Exception as e:
            error_log = {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'topic': current_topic if 'current_topic' in locals() else 'unknown',
                'variation': current_variation if 'current_variation' in locals() else 'unknown'
            }
            
            error_filename = f"error_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            error_path = os.path.join(self.logs_dir, error_filename)
            
            with open(error_path, 'w') as f:
                json.dump(error_log, f, indent=2)
            
            print(f"❌ Error generating video: {e}")
            print(f"📋 Error logged to: {error_path}")
            
            return {'success': False, 'error': str(e)}

    def create_thumbnail(self, content_data, topic, timestamp):
        """Create eye-catching thumbnail"""
        try:
            # Create thumbnail image
            img = Image.new('RGB', (1280, 720), color=(20, 25, 40))  # Dark background
            draw = ImageDraw.Draw(img)
            
            # Try to use a basic font, fallback to default
            try:
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 60)
                font_medium = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 40)
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
            
            # Add title text
            title_text = content_data['title'][:50] + "..." if len(content_data['title']) > 50 else content_data['title']
            
            # Draw text with outline effect
            x, y = 50, 100
            outline_color = (255, 0, 0)  # Red outline
            text_color = (255, 255, 255)  # White text
            
            # Draw outline
            for dx in [-2, 0, 2]:
                for dy in [-2, 0, 2]:
                    if dx != 0 or dy != 0:
                        draw.text((x+dx, y+dy), title_text, font=font_large, fill=outline_color)
            
            # Draw main text
            draw.text((x, y), title_text, font=font_large, fill=text_color)
            
            # Add topic badge
            topic_display = topic.replace('_', ' ').title()
            draw.rectangle([50, 50, 300, 90], fill=(255, 215, 0))  # Gold background
            draw.text((60, 60), topic_display, font=font_medium, fill=(0, 0, 0))
            
            # Add shocking fact
            if len(content_data['shocking_fact']) > 0:
                fact_text = "💥 " + content_data['shocking_fact'][:80] + "..."
                draw.text((50, 600), fact_text, font=font_medium, fill=(255, 255, 0))
            
            # Save thumbnail
            thumbnail_filename = f"thumbnail_{topic}_{timestamp}.png"
            thumbnail_path = os.path.join(self.thumbnail_dir, thumbnail_filename)
            img.save(thumbnail_path)
            
            return thumbnail_path
            
        except Exception as e:
            print(f"Warning: Could not create thumbnail: {e}")
            return None

    def show_menu(self):
        """Display interactive menu"""
        print("\n🔥 VIRAL LEGAL SHORTS AUTOPILOT SYSTEM 🔥")
        print("=" * 50)
        print("1. 🚀 Generate Today's Video (Auto-topic)")
        print("2. 📊 Show Topic Rotation Schedule") 
        print("3. 🎯 Generate Specific Topic")
        print("4. 📈 View Generation Statistics")
        print("5. 🧹 Clean Output Directory")
        print("6. ❌ Exit")
        print("=" * 50)

    def show_topic_schedule(self):
        """Show 8-day topic rotation schedule"""
        print("\n📅 8-DAY TOPIC ROTATION SCHEDULE")
        print("=" * 40)
        
        start_date = datetime(2024, 1, 1)
        current_date = datetime.now()
        days_passed = (current_date - start_date).days
        current_position = days_passed % 8
        
        for i, topic in enumerate(self.topics):
            status = ">>> CURRENT <<<" if i == current_position else ""
            variation = (days_passed // 8) % 3
            print(f"Day {i+1}: {topic.replace('_', ' ').title()} (Variation {variation + 1}) {status}")
        
        print(f"\nCurrent cycle day: {current_position + 1}")
        print(f"Current variation set: {(days_passed // 8) % 3 + 1}")

    def generate_specific_topic(self):
        """Generate video for specific topic"""
        print("\n🎯 SELECT TOPIC:")
        for i, topic in enumerate(self.topics):
            print(f"{i+1}. {topic.replace('_', ' ').title()}")
        
        try:
            choice = int(input("\nEnter topic number (1-8): ")) - 1
            if 0 <= choice < len(self.topics):
                variation = int(input("Enter variation (1-3): ")) - 1
                if 0 <= variation < 3:
                    topic = self.topics[choice]
                    print(f"\nGenerating {topic} (variation {variation + 1})...")
                    return self.generate_video(topic, variation)
                else:
                    print("Invalid variation number!")
            else:
                print("Invalid topic number!")
        except ValueError:
            print("Invalid input!")
        
        return None

    def view_statistics(self):
        """View generation statistics"""
        print("\n📈 GENERATION STATISTICS")
        print("=" * 30)
        
        # Count files in directories
        videos = len([f for f in os.listdir(self.video_dir) if f.endswith('.mp4')])
        thumbnails = len([f for f in os.listdir(self.thumbnail_dir) if f.endswith('.png')])
        marketing_files = len([f for f in os.listdir(self.output_dir) if f.startswith('marketing_')])
        log_files = len([f for f in os.listdir(self.logs_dir) if f.endswith('.json')])
        
        print(f"📹 Videos generated: {videos}")
        print(f"🖼️ Thumbnails created: {thumbnails}")
        print(f"📋 Marketing packages: {marketing_files}")
        print(f"📊 Log entries: {log_files}")
        
        # Show recent activity
        if log_files > 0:
            print("\n🕒 Recent Activity:")
            log_files_list = sorted([f for f in os.listdir(self.logs_dir) if f.startswith('generation_log_')], reverse=True)[:5]
            
            for log_file in log_files_list:
                try:
                    with open(os.path.join(self.logs_dir, log_file), 'r') as f:
                        log_data = json.load(f)
                        print(f"  • {log_data['topic']} (v{log_data['variation'] + 1}) - {log_data['timestamp']}")
                except:
                    pass

    def clean_output_directory(self):
        """Clean output directory"""
        confirm = input("\n⚠️ This will delete all generated content. Continue? (yes/no): ")
        if confirm.lower() == 'yes':
            import shutil
            
            for directory in [self.video_dir, self.audio_dir, self.thumbnail_dir]:
                shutil.rmtree(directory, ignore_errors=True)
                os.makedirs(directory, exist_ok=True)
            
            # Clean marketing files from output directory
            for file in os.listdir(self.output_dir):
                if file.startswith('marketing_'):
                    os.remove(os.path.join(self.output_dir, file))
            
            print("✅ Output directory cleaned!")
        else:
            print("❌ Cancelled.")

    def run(self):
        """Main application loop"""
        while True:
            self.show_menu()
            
            try:
                choice = input("\nEnter your choice (1-6): ").strip()
                
                if choice == '1':
                    print("\n🚀 Generating today's viral legal short...")
                    result = self.generate_video()
                    if result['success']:
                        print(f"\n🎉 SUCCESS! Video ready for upload!")
                        print(f"Upload at 7:30 PM IST for maximum engagement!")
                    
                elif choice == '2':
                    self.show_topic_schedule()
                    
                elif choice == '3':
                    self.generate_specific_topic()
                    
                elif choice == '4':
                    self.view_statistics()
                    
                elif choice == '5':
                    self.clean_output_directory()
                    
                elif choice == '6':
                    print("\n👋 Thanks for using Viral Legal Shorts System!")
                    break
                    
                else:
                    print("❌ Invalid choice! Please enter 1-6.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
            
            input("\nPress Enter to continue...")

def main():
    """Main entry point"""
    try:
        system = ViralLegalShortsSystem()
        
        # Check if running in automated mode (GitHub Actions)
        if len(sys.argv) > 1 and sys.argv[1] == '--auto':
            print("🤖 Running in automated mode...")
            result = system.generate_video()
            if result['success']:
                print("✅ Automated video generation completed!")
                sys.exit(0)
            else:
                print("❌ Automated video generation failed!")
                sys.exit(1)
        else:
            # Interactive mode
            system.run()
            
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
