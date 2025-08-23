#!/usr/bin/env python3
import cv2
import numpy as np
from moviepy.editor import *
import os
import json
import random
from datetime import datetime, timedelta
import math
import sys

# Configure MoviePy
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
            'duration': 15,  # Shorter for testing
            'font_scale': 1.5
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
                    "script": "Amazon just paid one hundred MILLION dollars in fines! They charged Prime members without consent. The FTC fined them one hundred MILLION dollars. Customers got automatic refunds. This violates consumer protection laws. Check your subscriptions NOW for unauthorized charges!",
                    "key_facts": ["$100M fine", "Prime members", "FTC action", "Consumer protection"]
                }
            },
            "labor_employment": {
                0: {
                    "title": "Tesla Paid $137 MILLION - Workplace Discrimination", 
                    "script": "Tesla just paid one hundred thirty seven MILLION dollars for discrimination! Employee faced racial harassment at Tesla. Company failed to address complaints. Jury awarded one hundred thirty seven MILLION in damages. Document all discrimination incidents. Know your workplace rights!",
                    "key_facts": ["$137M settlement", "Racial harassment", "Tesla lawsuit", "Workplace rights"]
                }
            },
            "data_privacy": {
                0: {
                    "title": "Meta Paid $5.1 BILLION GDPR Fine",
                    "script": "Facebook parent company paid five point one BILLION dollars! Meta violated GDPR privacy regulations. Largest privacy fine in history. Your data is worth more than you think. EU gives you right to delete data. Review your privacy settings NOW!",
                    "key_facts": ["$5.1B fine", "GDPR violation", "Privacy rights", "Data deletion"]
                }
            },
            "corporate_law": {
                0: {
                    "title": "This CEO Got 30 YEARS in Prison",
                    "script": "CEO sentenced to thirty YEARS for corporate fraud! Theranos CEO Elizabeth Holmes convicted. Defrauded investors of nine hundred MILLION dollars. Fake blood testing technology. Put patients lives at risk. Corporate executives aren't above the law!",
                    "key_facts": ["30 years prison", "Elizabeth Holmes", "$900M fraud", "Theranos scandal"]
                }
            },
            "family_law": {
                0: {
                    "title": "Hidden Assets in Divorce - $1M Found",
                    "script": "Spouse hid one MILLION dollars in divorce! Cryptocurrency wallets are often hidden. Offshore accounts require investigation. Forensic accountants find hidden money. Hiding assets is contempt of court. Protect yourself - hire a forensic accountant!",
                    "key_facts": ["$1M hidden", "Crypto wallets", "Forensic accounting", "Asset protection"]
                }
            },
            "criminal_law": {
                0: {
                    "title": "Know Your Rights - Police Can't Do This", 
                    "script": "Police violated rights - two point three MILLION settlement! You have the right to remain silent. Cannot search without warrant or consent. Must read Miranda rights during arrest. ILLEGAL evidence gets thrown out. Know your rights!",
                    "key_facts": ["$2.3M settlement", "Miranda rights", "Search warrants", "Police misconduct"]
                }
            },
            "intellectual_property": {
                0: {
                    "title": "This Patent Made $1 BILLION - Here's How",
                    "script": "One patent generated one BILLION dollars in royalties! Pharmaceutical patents are extremely valuable. Patent trolls make MILLIONS licensing. Twenty year protection from filing date. Have an invention? File a patent application NOW!",
                    "key_facts": ["$1B royalties", "Patent protection", "20-year term", "Patent filing"]
                }
            },
            "ai_legal_tools": {
                0: {
                    "title": "AI Lawyer Won $50,000 Case",
                    "script": "AI lawyer just won a fifty thousand dollar case! DoNotPay AI fights parking tickets. ChatGPT helps draft legal documents. AI analyzes contracts in minutes. Legal research became ten times faster. Try AI legal tools but verify with lawyers!",
                    "key_facts": ["$50K case won", "DoNotPay AI", "Contract analysis", "Legal research"]
                }
            }
        }
        
        # Default to first variation if not found
        topic_data = content_database.get(topic, content_database["consumer_rights"])
        return topic_data.get(variation, topic_data[0])

    def create_animated_background(self, theme, duration):
        """Create simple but effective animated background"""
        def make_frame(t):
            frame = np.zeros((self.video_config['height'], self.video_config['width'], 3), dtype=np.uint8)
            
            if theme in ["corporate", "legal"]:
                # Professional blue gradient with moving elements
                for y in range(self.video_config['height']):
                    intensity = int(50 + 30 * math.sin(0.01 * y + t * 0.5))
                    frame[y, :] = [intensity//3, intensity//2, intensity]
                
                # Add moving elements
                for i in range(3):
                    x = int(200 + 600 * (i/2) + 100 * math.sin(t + i))
                    y = int(400 + 400 * math.sin(t * 0.3 + i))
                    if 0 <= x < self.video_config['width'] and 0 <= y < self.video_config['height']:
                        cv2.circle(frame, (x, y), 50, (100, 150, 255), -1)
                        cv2.circle(frame, (x, y), 30, (150, 200, 255), -1)
            
            elif theme == "justice":
                # Golden justice theme
                for y in range(self.video_config['height']):
                    intensity = int(60 + 20 * math.sin(0.005 * y + t * 0.3))
                    frame[y, :] = [intensity//3, intensity//2, intensity]
                
                # Scales of justice animation
                center_x = self.video_config['width'] // 2
                scale_y = int(500 + 50 * math.sin(t))
                cv2.rectangle(frame, (center_x-100, scale_y), (center_x+100, scale_y+20), (200, 180, 100), -1)
                cv2.circle(frame, (center_x-60, scale_y), 40, (255, 215, 0), 3)
                cv2.circle(frame, (center_x+60, scale_y), 40, (255, 215, 0), 3)
            
            elif theme == "cyber":
                # Matrix-style background
                frame[:, :] = [0, 20, 0]  # Dark green base
                
                # Digital rain effect
                for x in range(0, self.video_config['width'], 30):
                    drop_pos = int((t * 200 + x * 5) % (self.video_config['height'] + 200))
                    if 0 <= drop_pos < self.video_config['height']:
                        intensity = max(50, 255 - abs(drop_pos - self.video_config['height']//2) * 2)
                        cv2.rectangle(frame, (x, drop_pos-20), (x+10, drop_pos+20), (0, intensity, 0), -1)
            
            elif theme == "tech":
                # Tech/AI theme with neural network
                frame[:, :] = [20, 20, 50]  # Dark blue
                
                # Animated connections
                nodes = [(300, 400), (600, 300), (900, 500), (500, 800), (700, 1200)]
                for i, (x1, y1) in enumerate(nodes[:4]):  # Limit to screen
                    if y1 < self.video_config['height']:
                        pulse_size = int(30 + 20 * math.sin(t * 2 + i))
                        cv2.circle(frame, (x1, y1), pulse_size, (0, 200, 255), -1)
                        cv2.circle(frame, (x1, y1), pulse_size//2, (100, 255, 255), -1)
                        
                        # Connections
                        for j, (x2, y2) in enumerate(nodes[i+1:i+3], i+1):
                            if j < len(nodes) and y2 < self.video_config['height']:
                                cv2.line(frame, (x1, y1), (x2, y2), (0, 100, 200), 2)
            
            else:  # Default professional theme
                # Simple gradient
                for y in range(self.video_config['height']):
                    intensity = int(40 + 20 * math.sin(0.002 * y))
                    frame[y, :] = [intensity, intensity, intensity + 30]
            
            return frame
        
        return VideoClip(make_frame, duration=duration).set_fps(self.video_config['fps'])

    def create_text_overlay(self, script, duration):
        """Create text overlay with viral styling"""
        sentences = script.split('.')[:4]  # Limit to 4 sentences
        sentence_duration = duration / len(sentences)
        text_clips = []
        
        for i, sentence in enumerate(sentences):
            if not sentence.strip():
                continue
                
            start_time = i * sentence_duration
            
            # Check for power words
            has_power_word = any(power in sentence.upper() for power in self.power_words)
            
            def make_text_frame(t):
                frame = np.zeros((self.video_config['height'], self.video_config['width'], 3), dtype=np.uint8)
                
                # Prepare text
                text = sentence.strip().upper()
                if len(text) > 50:
                    text = text[:47] + "..."
                
                # Text styling
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 1.8 if has_power_word else 1.5
                color = (0, 255, 255) if has_power_word else (255, 255, 255)  # Yellow for power words
                thickness = 4 if has_power_word else 3
                
                # Multi-line text handling
                words = text.split()
                lines = []
                current_line = ""
                
                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    text_size = cv2.getTextSize(test_line, font, font_scale, thickness)[0]
                    
                    if text_size[0] < self.video_config['width'] - 100:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                
                if current_line:
                    lines.append(current_line)
                
                # Draw text lines
                line_height = 80
                start_y = self.video_config['height'] // 2 - (len(lines) * line_height // 2)
                
                for j, line in enumerate(lines[:3]):  # Max 3 lines
                    text_size = cv2.getTextSize(line, font, font_scale, thickness)[0]
                    x = (self.video_config['width'] - text_size[0]) // 2
                    y = start_y + j * line_height
                    
                    # Text outline
                    cv2.putText(frame, line, (x-3, y-3), font, font_scale, (0, 0, 0), thickness+2, cv2.LINE_AA)
                    cv2.putText(frame, line, (x+3, y+3), font, font_scale, (0, 0, 0), thickness+2, cv2.LINE_AA)
                    cv2.putText(frame, line, (x-3, y+3), font, font_scale, (0, 0, 0), thickness+2, cv2.LINE_AA)
                    cv2.putText(frame, line, (x+3, y-3), font, font_scale, (0, 0, 0), thickness+2, cv2.LINE_AA)
                    
                    # Main text
                    cv2.putText(frame, line, (x, y), font, font_scale, color, thickness, cv2.LINE_AA)
                
                return frame
            
            text_clip = VideoClip(make_text_frame, duration=sentence_duration).set_start(start_time)
            text_clips.append(text_clip)
        
        return text_clips

    def create_title_card(self, title, duration=3):
        """Create engaging title card"""
        def make_title_frame(t):
            frame = np.zeros((self.video_config['height'], self.video_config['width'], 3), dtype=np.uint8)
            
            # Animated background
            for y in range(0, self.video_config['height'], 20):
                intensity = int(30 + 20 * math.sin(0.1 * y + t * 3))
                cv2.rectangle(frame, (0, y), (self.video_config['width'], y+10), (intensity, intensity//2, intensity*2), -1)
            
            # Title text
            font = cv2.FONT_HERSHEY_SIMPLEX
            title_text = title.upper()
            
            # Handle long titles
            if len(title_text) > 30:
                words = title_text.split()
                mid = len(words) // 2
                line1 = " ".join(words[:mid])
                line2 = " ".join(words[mid:])
                lines = [line1, line2]
            else:
                lines = [title_text]
            
            # Draw title
            font_scale = 2.0
            thickness = 5
            line_height = 120
            start_y = self.video_config['height'] // 2 - (len(lines) * line_height // 2)
            
            for i, line in enumerate(lines):
                text_size = cv2.getTextSize(line, font, font_scale, thickness)[0]
                x = (self.video_config['width'] - text_size[0]) // 2
                y = start_y + i * line_height
                
                # Glowing effect
                for offset in range(8, 0, -1):
                    alpha = 1.0 - (offset / 10.0)
                    glow_color = (int(255 * alpha), int(255 * alpha), 0)
                    cv2.putText(frame, line, (x, y), font, font_scale, glow_color, thickness + offset, cv2.LINE_AA)
                
                # Main text
                cv2.putText(frame, line, (x, y), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)
            
            return frame
        
        return VideoClip(make_title_frame, duration=duration).set_fps(self.video_config['fps'])

    def create_narration_audio(self, script, duration):
        """Create simple narration using beeps (placeholder for TTS)"""
        # Create simple audio track
        sample_rate = 44100
        samples = int(sample_rate * duration)
        
        # Generate varied tones to simulate speech rhythm
        t = np.linspace(0, duration, samples)
        
        # Base frequency modulated by script length and content
        words = script.split()
        base_freq = 200 + len(words) % 100  # Vary by word count
        
        # Create speech-like rhythm
        audio = np.zeros(samples)
        word_duration = duration / len(words)
        
        for i, word in enumerate(words):
            start_sample = int(i * word_duration * sample_rate)
            end_sample = int((i + 1) * word_duration * sample_rate)
            
            # Vary frequency based on word characteristics
            if any(power in word.upper() for power in self.power_words):
                freq = base_freq * 1.5  # Higher pitch for power words
                amplitude = 0.3
            else:
                freq = base_freq + (i % 3 - 1) * 50  # Vary pitch
                amplitude = 0.2
            
            # Generate tone for this word
            word_t = t[start_sample:end_sample]
            if len(word_t) > 0:
                word_audio = amplitude * np.sin(2 * np.pi * freq * word_t) * np.exp(-word_t/duration * 2)
                audio[start_sample:end_sample] = word_audio
        
        # Add some variety with brief pauses
        for i in range(0, len(audio), sample_rate // 2):
            if i + sample_rate // 10 < len(audio):
                audio[i:i + sample_rate // 10] *= 0.1  # Brief pause
        
        # Normalize
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio)) * 0.8
        
        # Save audio
        temp_audio_path = os.path.join(self.audio_dir, f"narration_{int(datetime.now().timestamp())}.wav")
        
        try:
            from scipy.io import wavfile
            wavfile.write(temp_audio_path, sample_rate, (audio * 32767).astype(np.int16))
            return AudioFileClip(temp_audio_path)
        except ImportError:
            print("Scipy not available, creating silent audio")
            return AudioFileClip("dummy").set_duration(duration).volumex(0)

    def generate_video(self, topic=None, variation=None):
        """Generate complete viral legal short"""
        try:
            # Get topic and content
            if topic is None or variation is None:
                current_topic, current_variation = self.get_current_topic()
            else:
                current_topic, current_variation = topic, variation
            
            print(f"Generating video for {current_topic} (variation {current_variation})")
            
            content_data = self.get_content_data(current_topic, current_variation)
            
            # Determine theme
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
            
            print("Creating components...")
            
            # Create video components
            title_card = self.create_title_card(content_data['title'], 3)
            background = self.create_animated_background(theme, self.video_config['duration'] - 3)
            text_overlays = self.create_text_overlay(content_data['script'], self.video_config['duration'] - 3)
            
            # Create narration audio
            narration = self.create_narration_audio(content_data['script'], self.video_config['duration'])
            
            print("Compositing video...")
            
            # Combine video elements
            main_video_clips = [background] + text_overlays
            main_video = CompositeVideoClip(main_video_clips, size=(self.video_config['width'], self.video_config['height']))
            
            # Combine title card and main video
            final_video = concatenate_videoclips([title_card, main_video])
            
            # Add audio
            if narration:
                final_video = final_video.set_audio(narration)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"legal_short_{current_topic}_{current_variation}_{timestamp}.mp4"
            output_path = os.path.join(self.video_dir, output_filename)
            
            print(f"Exporting to {output_path}...")
            
            # Export with proper settings
            final_video.write_videofile(
                output_path,
                fps=self.video_config['fps'],
                codec='libx264',
                audio_codec='aac' if narration else None,
                verbose=False,
                logger=None,
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            # Create marketing package
            marketing = self.create_marketing_package(content_data, current_topic)
            marketing_filename = f"marketing_{current_topic}_{current_variation}_{timestamp}.json"
            marketing_path = os.path.join(self.output_dir, marketing_filename)
            
            with open(marketing_path, 'w') as f:
                json.dump(marketing, f, indent=2)
            
            # Log success
            log_data = {
                'timestamp': timestamp,
                'topic': current_topic,
                'variation': current_variation,
                'video_path': output_path,
                'marketing_path': marketing_path,
                'script_length': len(content_data['script'].split()),
                'duration': self.video_config['duration'],
                'theme': theme,
                'key_facts': content_data['key_facts']
            }
            
            log_path = os.path.join(self.logs_dir, f"success_log_{timestamp}.json")
            with open(log_path, 'w') as f:
                json.dump(log_data, f, indent=2)
            
            print(f"✅ SUCCESS! Video generated: {output_path}")
            print(f"📋 Marketing package: {marketing_path}")
            print(f"📊 Log: {log_path}")
            
            return {
                'success': True,
                'video_path': output_path,
                'marketing_path': marketing_path,
                'content_data': content_data
            }
            
        except Exception as e:
            print(f"❌ Error generating video: {e}")
            
            # Log error
            error_log = {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'topic': current_topic if 'current_topic' in locals() else 'unknown',
                'variation': current_variation if 'current_variation' in locals() else 'unknown'
            }
            
            error_path = os.path.join(self.logs_dir, f"error_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(error_path, 'w') as f:
                json.dump(error_log, f, indent=2)
            
            return {'success': False, 'error': str(e)}

    def create_marketing_package(self, content_data, topic):
        """Create marketing materials"""
        titles = [
            content_data['title'],
            f"🚨 {content_data['title']}",
            f"Legal Alert: {topic.replace('_', ' ').title()}",
            f"💰 This Will Save You Money",
            f"🔥 Viral Legal News: {topic.replace('_', ' ').title()}"
        ]
        
        description = f"""
{content_data['title']}

Key Facts:
{chr(10).join([f'• {fact}' for fact in content_data['key_facts']])}

⚖️ LEGAL DISCLAIMER: Educational content only. Consult qualified attorney for legal advice.

#LegalAdvice #KnowYourRights #LegalEducation #{topic.replace('_', '').title()}
        """
        
        return {
            'titles': titles,
            'description': description.strip(),
            'hashtags': [f"#{topic.replace('_', '').title()}", "#LegalAdvice", "#KnowYourRights"],
            'upload_time': '19:30 IST',
            'topic': topic,
            'key_facts': content_data['key_facts']
        }

def main():
    """Main entry point"""
    try:
        system = ViralLegalShortsSystem()
        
        if len(sys.argv) > 1 and sys.argv[1] == '--auto':
            print("🤖 Running in automated mode...")
            result = system.generate_video()
            if result['success']:
                print("✅ Automated generation completed!")
                sys.exit(0)
            else:
                print("❌ Automated generation failed!")
                sys.exit(1)
        else:
            # Manual generation for testing
            result = system.generate_video()
            if result['success']:
                print("✅ Manual generation completed!")
            else:
                print("❌ Manual generation failed!")
                
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
