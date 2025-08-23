#!/usr/bin/env python3
"""
Complete Legal Video Auto-Generation System
- Uses your 8 core topics + trending legal areas  
- Generates unique content daily with no repeats
- Copyright-free music, backgrounds, and content
- Professional quality for YouTube Shorts
- Appeals to both students and professionals
"""

import os, sys, datetime, requests, json, random, hashlib, time
import moviepy.editor as mp
import gtts
from textwrap import wrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import tempfile
from dataclasses import dataclass
from typing import List, Dict, Any
import urllib.parse
import re

# CONFIGURATION
CONFIG = {
    "HF_API_KEY": os.getenv("HF_API_KEY"),
    "NEWS_API_KEY": os.getenv("NEWS_API_KEY", ""),  
    "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
    "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
    "VIDEO_DURATION": 55,  # seconds (YouTube Shorts safe)
    "OUTPUT_SIZE": (1080, 1920),  # 9:16 ratio
    "BRAND_NAME": "Legal Insights Daily",
    "BRAND_COLOR": "#1e3a8a",
    "CHANNEL_FOCUS": "practical_legal_education"
}

# AI MODELS (Multiple fallback options)
AI_MODELS = [
    "microsoft/DialoGPT-large",
    "google/flan-t5-large", 
    "facebook/blenderbot-400M-distill",
    "google/flan-t5-small",
    "microsoft/DialoGPT-medium"
]

# COPYRIGHT-FREE MUSIC SOURCES
ROYALTY_FREE_MUSIC = [
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3", 
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-10.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-16.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3"
]

# YOUR CORE 8 TOPICS + TRENDING ADDITIONS
LEGAL_TOPICS = {
    "core_topics": [
        # Your original 8 topics
        "How to report UPI / digital payment fraud",
        "How to file a cybercrime / online harassment complaint", 
        "Consumer rights: refund / return / compensation",
        "New criminal law micro-clarifications",
        "Data privacy: Ask companies to delete your data",
        "Tenant deposit / landlord disputes", 
        "Women's safety quick kit",
        "AI tools for law students & professionals"
    ],
    "trending_additions": [
        # Based on research - high demand, low supply
        "Intellectual Property basics for startups",
        "Labor law changes 2024-2025",
        "Financial services compliance for businesses",
        "Contract automation and digital signatures",
        "Legal tech tools every lawyer needs",
        "Regulatory compliance for online businesses",
        "Privacy law updates and GDPR equivalent",
        "Corporate governance for small companies",
        "Employment law for remote workers",
        "Legal aspects of AI and automation",
        "Cryptocurrency and blockchain legal issues",
        "E-commerce legal compliance checklist"
    ]
}

# CONTENT VARIATION STRATEGIES
CONTENT_APPROACHES = {
    "student_focused": {
        "style": "educational_simple",
        "tone": "learning_friendly", 
        "examples": "academic_cases",
        "language": "textbook_simplified"
    },
    "professional_focused": {
        "style": "practice_oriented",
        "tone": "business_formal",
        "examples": "real_world_scenarios", 
        "language": "legal_terminology"
    },
    "general_public": {
        "style": "everyday_practical",
        "tone": "conversational",
        "examples": "common_situations",
        "language": "plain_english"
    },
    "trending_news": {
        "style": "current_affairs",
        "tone": "urgent_informative",
        "examples": "recent_cases",
        "language": "news_style"
    },
    "myth_busting": {
        "style": "fact_checking", 
        "tone": "authoritative_clear",
        "examples": "misconception_correction",
        "language": "myth_vs_reality"
    },
    "step_by_step": {
        "style": "tutorial_guide",
        "tone": "helpful_instructor", 
        "examples": "actionable_steps",
        "language": "how_to_guide"
    }
}

@dataclass
class VideoContent:
    topic: str
    script: str
    approach: str
    target_audience: str
    variation_id: str
    date_created: str
    seo_tags: List[str]
    youtube_title: str

class IntelligentContentGenerator:
    def __init__(self):
        self.content_history = self.load_history()
        self.all_topics = LEGAL_TOPICS["core_topics"] + LEGAL_TOPICS["trending_additions"]
        self.variation_strategies = list(CONTENT_APPROACHES.keys())
        
    def load_history(self) -> Dict:
        """Load content generation history to avoid repeats"""
        try:
            with open("content_history.json", "r") as f:
                return json.load(f)
        except:
            return {
                "generated_content": [],
                "topic_variations": {},
                "last_generated": {},
                "variation_count": {}
            }
    
    def save_history(self):
        """Save content generation history"""
        with open("content_history.json", "w") as f:
            json.dump(self.content_history, f, indent=2)
    
    def get_current_topic(self) -> str:
        """Intelligent topic selection with rotation"""
        # Primary rotation through core 8 topics
        core_index = datetime.datetime.now().day % len(LEGAL_TOPICS["core_topics"])
        primary_topic = LEGAL_TOPICS["core_topics"][core_index]
        
        # Every 4th day, substitute with trending topic
        if datetime.datetime.now().day % 4 == 0:
            trending_index = (datetime.datetime.now().day // 4) % len(LEGAL_TOPICS["trending_additions"])
            return LEGAL_TOPICS["trending_additions"][trending_index]
        
        return primary_topic
    
    def select_content_approach(self, topic: str) -> Dict:
        """Smart approach selection based on topic and history"""
        
        # Get topic history
        topic_history = self.content_history.get("topic_variations", {}).get(topic, [])
        used_approaches = [entry.get("approach") for entry in topic_history]
        
        # Select unused approach or least used
        available_approaches = [
            approach for approach in self.variation_strategies 
            if approach not in used_approaches[-3:]  # Avoid last 3 approaches
        ]
        
        if not available_approaches:
            available_approaches = self.variation_strategies
        
        # Smart selection based on topic type
        if any(keyword in topic.lower() for keyword in ["ai", "tech", "digital"]):
            preferred = ["professional_focused", "trending_news", "step_by_step"]
        elif any(keyword in topic.lower() for keyword in ["student", "tools", "basics"]):
            preferred = ["student_focused", "step_by_step"]
        elif any(keyword in topic.lower() for keyword in ["fraud", "crime", "safety"]):
            preferred = ["general_public", "step_by_step", "myth_busting"]
        else:
            preferred = available_approaches
        
        # Select from preferred approaches
        selected_approaches = [a for a in preferred if a in available_approaches]
        if not selected_approaches:
            selected_approaches = available_approaches
        
        approach_name = random.choice(selected_approaches)
        return {
            "name": approach_name,
            **CONTENT_APPROACHES[approach_name]
        }
    
    def generate_unique_content(self, topic: str) -> VideoContent:
        """Generate completely unique content for the topic"""
        
        print(f"📝 Generating content for: {topic}")
        
        # Select approach
        approach = self.select_content_approach(topic)
        
        # Determine target audience
        target_audience = self.determine_target_audience(topic, approach)
        
        # Create unique variation ID
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        variation_seed = f"{topic}-{approach['name']}-{target_audience}-{date_str}-{random.randint(1000, 9999)}"
        variation_id = hashlib.md5(variation_seed.encode()).hexdigest()[:10]
        
        # Generate script with AI
        script = self.generate_intelligent_script(topic, approach, target_audience)
        
        # Generate SEO-optimized metadata
        seo_tags, youtube_title = self.generate_seo_metadata(topic, approach, target_audience)
        
        # Create content object
        content = VideoContent(
            topic=topic,
            script=script,
            approach=approach["name"],
            target_audience=target_audience,
            variation_id=variation_id,
            date_created=date_str,
            seo_tags=seo_tags,
            youtube_title=youtube_title
        )
        
        # Update history
        self.update_content_history(topic, approach, variation_id, date_str)
        
        return content
    
    def determine_target_audience(self, topic: str, approach: Dict) -> str:
        """Determine primary target audience for the content"""
        
        if approach["name"] in ["student_focused"]:
            return "law_students"
        elif approach["name"] in ["professional_focused"]:
            return "legal_professionals" 
        elif any(keyword in topic.lower() for keyword in ["ai", "tech", "tools", "digital"]):
            return "tech_savvy_lawyers"
        elif any(keyword in topic.lower() for keyword in ["consumer", "fraud", "safety", "rights"]):
            return "general_public"
        else:
            return "mixed_audience"
    
    def generate_intelligent_script(self, topic: str, approach: Dict, target_audience: str) -> str:
        """Generate script using AI with intelligent prompting"""
        
        # Create sophisticated prompt
        prompt = self.create_advanced_prompt(topic, approach, target_audience)
        
        # Try AI generation with multiple models
        if CONFIG["HF_API_KEY"]:
            ai_script = self.multi_model_ai_generation(prompt)
            if ai_script and len(ai_script.strip()) > 100:
                return self.enhance_and_optimize_script(ai_script, topic, target_audience)
        
        # Intelligent fallback
        return self.generate_intelligent_fallback(topic, approach, target_audience)
    
    def create_advanced_prompt(self, topic: str, approach: Dict, target_audience: str) -> str:
        """Create sophisticated AI prompt for unique content generation"""
        
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        
        audience_context = {
            "law_students": "law students preparing for exams and building foundational knowledge",
            "legal_professionals": "practicing lawyers, advocates, and legal consultants", 
            "tech_savvy_lawyers": "lawyers interested in legal technology and innovation",
            "general_public": "ordinary citizens who need practical legal guidance",
            "mixed_audience": "both legal professionals and educated general public"
        }
        
        style_instructions = {
            "educational_simple": "Use clear, simple language with step-by-step explanations",
            "practice_oriented": "Focus on practical applications and real-world scenarios",
            "everyday_practical": "Use conversational tone with relatable examples",
            "current_affairs": "Reference recent legal developments and news",
            "fact_checking": "Address common misconceptions with authoritative corrections",
            "tutorial_guide": "Provide actionable, numbered steps with clear outcomes"
        }
        
        prompt = f"""Create a unique, engaging 50-second YouTube Shorts script about "{topic}".

TARGET AUDIENCE: {audience_context[target_audience]}
CONTENT STYLE: {style_instructions.get(approach['style'], 'informative and engaging')}
APPROACH: {approach['tone']} tone with {approach['examples']} examples

REQUIREMENTS:
✅ Completely original content (not generic advice)
✅ Hook viewers in first 3 seconds with surprising fact or question
✅ Provide genuine, actionable legal value
✅ Include specific Indian legal context and procedures
✅ Use appropriate legal terminology for {target_audience}
✅ Add relevant emojis for engagement (but not excessive)
✅ End with strong call-to-action
✅ Stay factually accurate and legally sound
✅ Reference current date context: {current_date}

STRUCTURE:
🎯 HOOK (3-5 seconds): Surprising legal fact or urgent question
📚 VALUE (40-45 seconds): Core legal information with specific guidance  
🚀 CTA (5-7 seconds): Clear next step for viewers

AVOID:
❌ Generic legal disclaimers
❌ Overly complex legal jargon (unless for professionals)
❌ Vague advice without specific steps
❌ Copyright-infringing content

Make this script uniquely valuable and memorable. Focus on what most people don't know about {topic}."""

        return prompt
    
    def multi_model_ai_generation(self, prompt: str) -> str:
        """Try multiple AI models for best content generation"""
        
        for model in AI_MODELS:
            try:
                print(f"🤖 Trying AI model: {model}")
                
                url = f"https://api-inference.huggingface.co/models/{model}"
                headers = {"Authorization": f"Bearer {CONFIG['HF_API_KEY']}"}
                
                # Optimized parameters for each model type
                if "flan-t5" in model:
                    params = {
                        "max_new_tokens": 400,
                        "temperature": 0.7,
                        "do_sample": True,
                        "top_p": 0.9
                    }
                elif "DialoGPT" in model:
                    params = {
                        "max_new_tokens": 350, 
                        "temperature": 0.8,
                        "do_sample": True,
                        "top_p": 0.92,
                        "repetition_penalty": 1.1
                    }
                else:
                    params = {
                        "max_new_tokens": 375,
                        "temperature": 0.75,
                        "do_sample": True,
                        "top_p": 0.9
                    }
                
                payload = {
                    "inputs": prompt,
                    "parameters": params
                }
                
                response = requests.post(url, headers=headers, json=payload, timeout=50)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
                        text = data[0]["generated_text"]
                        
                        # Clean up response
                        if prompt in text:
                            text = text.replace(prompt, "").strip()
                        
                        # Validate quality
                        if len(text.strip()) > 100 and self.validate_generated_content(text):
                            print(f"✅ Success with {model}")
                            return text
                
                # Rate limiting between models
                time.sleep(3)
                        
            except Exception as e:
                print(f"⚠️ Model {model} failed: {str(e)}")
                continue
        
        print("❌ All AI models failed, using intelligent fallback")
        return ""
    
    def validate_generated_content(self, content: str) -> bool:
        """Validate AI-generated content quality"""
        
        # Basic quality checks
        if len(content.strip()) < 50:
            return False
            
        # Check for completeness
        if content.count('.') < 2:  # Should have multiple sentences
            return False
            
        # Check for engagement elements
        has_hook = any(symbol in content[:100] for symbol in ['?', '!', '🚨', '⚠️', '🔥'])
        has_structure = any(word in content.lower() for word in ['step', 'tip', 'remember', 'important'])
        
        return has_hook or has_structure
    
    def enhance_and_optimize_script(self, script: str, topic: str, target_audience: str) -> str:
        """Enhance AI-generated script for maximum engagement"""
        
        # Clean up script
        script = re.sub(r'\n+', '\n', script.strip())
        
        # Add emojis strategically if missing
        if not re.search(r'[🚨⚖️💡🎯✅❌🔥⚡🏛️📚]', script):
            script = f"⚖️ {script}"
        
        # Ensure call-to-action
        if not any(cta in script.lower() for cta in ['follow', 'subscribe', 'share', 'comment', 'like']):
            script += "\n\n🎯 Follow for daily legal insights!"
        
        # Add relevant hashtags
        hashtags = self.generate_hashtags(topic, target_audience)
        if "#" not in script:
            script += f"\n\n{' '.join(hashtags[:4])}"
        
        # Ensure proper length for video timing
        words = script.split()
        if len(words) > 120:  # Too long for 55 seconds
            sentences = script.split('.')
            script = '. '.join(sentences[:4]) + '.'
        
        return script
    
    def generate_hashtags(self, topic: str, target_audience: str) -> List[str]:
        """Generate relevant hashtags for the content"""
        
        base_tags = ["#LegalHelp", "#IndianLaw", "#LegalAwareness", "#YourRights"]
        
        # Topic-specific tags
        topic_lower = topic.lower()
        if "cyber" in topic_lower or "digital" in topic_lower:
            base_tags.extend(["#CyberLaw", "#DigitalRights", "#OnlineSafety"])
        elif "consumer" in topic_lower:
            base_tags.extend(["#ConsumerRights", "#ConsumerProtection", "#RefundRights"])
        elif "ai" in topic_lower or "tech" in topic_lower:
            base_tags.extend(["#LegalTech", "#AILaw", "#TechLaw"])
        elif "women" in topic_lower:
            base_tags.extend(["#WomenSafety", "#WomenRights", "#LegalProtection"])
        elif "criminal" in topic_lower:
            base_tags.extend(["#CriminalLaw", "#NewLaws", "#LegalUpdates"])
        
        # Audience-specific tags
        if target_audience == "law_students":
            base_tags.extend(["#LawStudent", "#LegalEducation", "#StudyLaw"])
        elif target_audience == "legal_professionals":
            base_tags.extend(["#LawyerLife", "#LegalPractice", "#ProfessionalDevelopment"])
        
        return base_tags[:8]  # Limit to 8 hashtags
    
    def generate_intelligent_fallback(self, topic: str, approach: Dict, target_audience: str) -> str:
        """Generate intelligent fallback content when AI fails"""
        
        templates = {
            "law_students": self.get_student_template(topic),
            "legal_professionals": self.get_professional_template(topic),
            "general_public": self.get_public_template(topic),
            "tech_savvy_lawyers": self.get_tech_template(topic),
            "mixed_audience": self.get_mixed_template(topic)
        }
        
        template = templates.get(target_audience, templates["mixed_audience"])
        
        # Add current date context
        current_date = datetime.datetime.now().strftime("%B %Y")
        template = template.replace("{date}", current_date)
        template = template.replace("{topic}", topic)
        
        return template
    
    def get_student_template(self, topic: str) -> str:
        return f"""📚 LAW STUDENT ALERT: {topic}

🎓 What every law student should know:

This is a HOT TOPIC for your exams! Here's the simplified breakdown:

📖 LEGAL FRAMEWORK:
• Relevant acts and sections
• Key judicial precedents  
• Recent amendments ({datetime.datetime.now().strftime("%Y")})

⚡ EXAM TIP:
Remember the 3 Ps - Procedure, Precedent, Punishment

💡 PRACTICAL APPLICATION:
Use this in moot courts and case studies

🎯 Follow for daily law student tips!

#LawStudent #LegalEducation #ExamPrep #LawSchool #StudyTips"""

    def get_professional_template(self, topic: str) -> str:
        return f"""⚖️ PROFESSIONAL UPDATE: {topic}

🏛️ For practicing advocates and legal consultants:

RECENT DEVELOPMENTS ({datetime.datetime.now().strftime("%Y")}):
• New procedural guidelines
• Updated forms and timelines
• Court fee revisions
• Digital filing procedures

⚡ ACTION ITEMS:
1. Update your practice templates
2. Inform existing clients
3. Review pending cases
4. Update fee structures

💼 BUSINESS IMPACT:
This affects client advisory and case strategy

🎯 Follow for daily practice updates!

#LawyerLife #LegalPractice #ProfessionalUpdate #CourtProcedure"""

    def get_public_template(self, topic: str) -> str:
        return f"""🚨 CITIZEN ALERT: {topic}

❓ Did you know you have these rights?

Most people don't know this simple process can save them thousands!

✅ YOUR RIGHTS:
• What you can demand
• When to take action
• Where to complain
• How long it takes

⚡ QUICK ACTION:
Don't wait! Time limits apply.

💪 REMEMBER: Knowledge is your best legal protection!

🎯 Share this to help others!

#YourRights #CitizenRights #LegalHelp #KnowYourRights #LegalAwareness"""

    def get_tech_template(self, topic: str) -> str:
        return f"""💻 LEGAL TECH UPDATE: {topic}

🔥 How technology is changing legal practice:

LATEST TOOLS & TRENDS:
• AI-powered research platforms
• Automated document review
• Digital signature validation
• Online dispute resolution

⚡ IMPLEMENTATION TIPS:
1. Start with free trials
2. Train your team
3. Update client processes
4. Ensure compliance

🚀 FUTURE READY: Stay ahead of the legal tech curve!

🎯 Follow for daily legal tech insights!

#LegalTech #AILaw #DigitalLaw #TechLawyer #Innovation"""

    def get_mixed_template(self, topic: str) -> str:
        return f"""⚖️ LEGAL INSIGHT: {topic}

🎯 Essential knowledge for everyone:

Whether you're a law student, practicing lawyer, or concerned citizen - this affects you!

📋 WHAT YOU NEED TO KNOW:
• Legal framework and recent changes
• Your rights and responsibilities
• Practical steps to take
• Common mistakes to avoid

💡 PRO TIP: Document everything and act quickly!

🚀 Knowledge empowers justice!

🎯 Follow for daily legal insights for all!

#LegalKnowledge #LawForEveryone #LegalAwareness #YourRights"""

    def generate_seo_metadata(self, topic: str, approach: Dict, target_audience: str) -> tuple:
        """Generate SEO-optimized title and tags"""
        
        # Generate YouTube title options
        title_templates = [
            f"Legal Alert: {topic} - What You Must Know",
            f"{topic} - Your Rights Explained in 60 Seconds",
            f"Law Made Simple: {topic} Quick Guide", 
            f"Legal Myth vs Reality: {topic}",
            f"Emergency Legal Tip: {topic}",
            f"Lawyer's Secret: {topic} Exposed"
        ]
        
        # Select based on approach
        if approach["name"] == "myth_busting":
            youtube_title = f"Legal Myth vs Reality: {topic}"
        elif approach["name"] == "step_by_step":
            youtube_title = f"Step-by-Step Guide: {topic}"
        elif approach["name"] == "trending_news":
            youtube_title = f"Legal Alert 2025: {topic}"
        else:
            youtube_title = random.choice(title_templates)
        
        # Generate SEO tags
        seo_tags = self.generate_hashtags(topic, target_audience)
        
        return seo_tags, youtube_title
    
    def update_content_history(self, topic: str, approach: Dict, variation_id: str, date: str):
        """Update content generation history"""
        
        if topic not in self.content_history["topic_variations"]:
            self.content_history["topic_variations"][topic] = []
        
        self.content_history["topic_variations"][topic].append({
            "approach": approach["name"],
            "variation_id": variation_id,
            "date": date,
            "target_audience": approach.get("target_audience", "mixed")
        })
        
        self.content_history["last_generated"][topic] = date
        self.content_history["variation_count"][topic] = \
            self.content_history["variation_count"].get(topic, 0) + 1
        
        self.save_history()

class ProfessionalVideoProducer:
    def __init__(self):
        self.temp_files = []
        
    def create_professional_video(self, content: VideoContent) -> str:
        """Create professional-quality video"""
        
        print(f"🎬 Creating professional video: {content.youtube_title}")
        
        # Create enhanced audio
        audio_path = self.create_professional_audio(content.script)
        
        # Create dynamic visual sequence
        video_clips = self.create_dynamic_visuals(content)
        
        # Combine with professional transitions
        final_video = self.assemble_professional_video(video_clips, audio_path, content)
        
        # Cleanup
        self.cleanup_temp_files()
        
        return final_video
    
    def create_professional_audio(self, script: str) -> str:
        """Create professional audio with background music"""
        
        # Generate clear speech
        tts = gtts.gTTS(text=script, lang='en', slow=False)
        speech_path = "temp_speech.mp3" 
        tts.save(speech_path)
        self.temp_files.append(speech_path)
        
        # Get copyright-free background music
        music_path = self.download_royalty_free_music()
        
        # Professional audio mixing
        speech_audio = mp.AudioFileClip(speech_path)
        
        if music_path and os.path.exists(music_path):
            bg_music = mp.AudioFileClip(music_path).subclip(0, speech_audio.duration + 5)
            
            # Professional audio balance
            final_audio = mp.CompositeAudioClip([
                speech_audio.volumex(1.0),  # Clear speech
                bg_music.volumex(0.1)      # Subtle background
            ]).set_fps(44100)
        else:
            final_audio = speech_audio.set_fps(44100)
        
        # Audio enhancement
        final_audio_path = "professional_audio.mp3"
        final_audio.write_audiofile(final_audio_path, verbose=False, logger=None)
        self.temp_files.append(final_audio_path)
        
        return final_audio_path
    
    def download_royalty_free_music(self) -> str:
        """Download copyright-free background music"""
        
        music_file = "background_music.mp3"
        
        # Use existing music if available
        if os.path.exists(music_file):
            return music_file
        
        try:
            # Select random royalty-free track
            music_url = random.choice(ROYALTY_FREE_MUSIC)
            
            print(f"🎵 Downloading: {music_url}")
            response = requests.get(music_url, timeout=45)
            response.raise_for_status()
            
            with open(music_file, 'wb') as f:
                f.write(response.content)
            
            print("✅ Background music ready")
            return music_file
            
        except Exception as e:
            print(f"⚠️ Music download failed: {e}")
            return ""
    
    def create_dynamic_visuals(self, content: VideoContent) -> List[mp.VideoClip]:
        """Create dynamic, engaging visual clips"""
        
        clips = []
        sentences = [s.strip() + "." for s in content.script.split('.') if s.strip() and len(s.strip()) > 5]
        
        if not sentences:
            raise ValueError("No valid sentences found in script")
        
        # Calculate optimal timing
        total_duration = min(CONFIG["VIDEO_DURATION"], 55)  # Safe for YouTube Shorts
        clip_duration = total_duration / len(sentences)
        
        # Ensure minimum and maximum clip durations
        clip_duration = max(2.0, min(5.0, clip_duration))
        
        for i, sentence in enumerate(sentences):
            # Adjust duration based on content complexity
            word_count = len(sentence.split())
            duration = max(2.5, min(5.0, word_count * 0.4))
            
            # Create professional clip
            clip = self.create_professional_text_clip(sentence, duration, content, i)
            clips.append(clip)
        
        return clips
    
    def create_professional_text_clip(self, text: str, duration: float, content: VideoContent, index: int) -> mp.VideoClip:
        """Create professional-looking text clips with dynamic backgrounds"""
        
        # Create dynamic background
        bg_path = self.create_professional_background(content.approach, content.target_audience, index)
        background_clip = mp.ImageClip(bg_path, duration=duration)
        
        # Clean and format text
        clean_text = re.sub(r'[#]+', '', text).strip()
        clean_text = re.sub(r'\s+', ' ', clean_text)
        
        # Smart text wrapping
        wrapped_text = "\n".join(wrap(clean_text, width=28))
        
        # Professional typography
        main_text = mp.TextClip(
            wrapped_text,
            fontsize=52,
            color='white',
            font='DejaVu-Sans-Bold',
            size=(900, None),
            method='caption',
            align='center',
            stroke_color='black',
            stroke_width=2
        ).set_position('center').set_duration(duration)
        
        # Add subtle animation
        animated_text = main_text.set_position(lambda t: ('center', 'center'))
        
        # Emphasis for important content
        if any(keyword in text.lower() for keyword in ['important', 'alert', 'urgent', 'remember', 'warning']):
            # Add pulsing effect for emphasis
            emphasis_overlay = mp.ColorClip(
                size=CONFIG["OUTPUT_SIZE"], 
                color=(255, 0, 0), 
                duration=duration
            ).set_opacity(0.1)
            
            final_clip = mp.CompositeVideoClip([background_clip, emphasis_overlay, animated_text])
        else:
            final_clip = mp.CompositeVideoClip([background_clip, animated_text])
        
        return final_clip
    
    def create_professional_background(self, approach: str, audience: str, index: int) -> str:
        """Create professional background images"""
        
        width, height = CONFIG["OUTPUT_SIZE"]
        
        # Professional color schemes
        color_palettes = {
            "student_focused": {
                "primary": "#1e40af", "secondary": "#3b82f6", "accent": "#60a5fa",
                "gradient": "#1e3a8a"
            },
            "professional_focused": {
                "primary": "#0f172a", "secondary": "#1e293b", "accent": "#64748b", 
                "gradient": "#334155"
            },
            "general_public": {
                "primary": "#166534", "secondary": "#16a34a", "accent": "#22c55e",
                "gradient": "#15803d"
            },
            "trending_news": {
                "primary": "#dc2626", "secondary": "#ef4444", "accent": "#f87171",
                "gradient": "#b91c1c"
            },
            "myth_busting": {
                "primary": "#7c3aed", "secondary": "#8b5cf6", "accent": "#a78bfa",
                "gradient": "#6d28d9"
            },
            "step_by_step": {
                "primary": "#ea580c", "secondary": "#f97316", "accent": "#fb923c",
                "gradient": "#c2410c"
            }
        }
        
        palette = color_palettes.get(approach, color_palettes["professional_focused"])
        
        # Create sophisticated gradient background
        img = Image.new('RGB', (width, height), palette["primary"])
        draw = ImageDraw.Draw(img)
        
        # Multi-layer gradient effect
        for i in range(height):
            progress = i / height
            
            # Primary gradient
            primary_color = self.interpolate_color(palette["primary"], palette["gradient"], progress)
            draw.line([(0, i), (width, i)], fill=primary_color)
            
            # Secondary overlay gradient
            if i % 3 == 0:  # Every 3rd line for subtle texture
                overlay_color = self.interpolate_color(palette["secondary"], palette["accent"], progress * 0.3)
                overlay_color = tuple(min(255, c) for c in overlay_color)
                draw.line([(0, i), (width, i)], fill=overlay_color)
        
        # Professional branding elements
        self.add_professional_elements(draw, width, height, palette, index)
        
        # Save background
        bg_path = f"professional_bg_{index}.png"
        img.save(bg_path, quality=95, optimize=True)
        self.temp_files.append(bg_path)
        
        return bg_path
    
    def interpolate_color(self, color1: str, color2: str, factor: float) -> tuple:
        """Interpolate between two hex colors"""
        
        # Convert hex to RGB
        c1 = tuple(int(color1[i:i+2], 16) for i in (1, 3, 5))
        c2 = tuple(int(color2[i:i+2], 16) for i in (1, 3, 5))
        
        # Interpolate
        return tuple(int(c1[i] + factor * (c2[i] - c1[i])) for i in range(3))
    
    def add_professional_elements(self, draw, width: int, height: int, palette: dict, index: int):
        """Add professional design elements to background"""
        
        # Brand header area
        header_height = 120
        draw.rectangle([0, 0, width, header_height], fill=palette["accent"], outline=palette["primary"], width=2)
        
        # Legal scales icon (simplified)
        icon_x, icon_y = width - 100, 60
        draw.ellipse([icon_x-30, icon_y-30, icon_x+30, icon_y+30], outline="white", width=3)
        draw.line([icon_x-20, icon_y, icon_x+20, icon_y], fill="white", width=2)
        
        # Decorative side elements
        for i in range(0, height, 200):
            draw.rectangle([0, i, 20, i+100], fill=palette["accent"], outline=palette["primary"], width=1)
            draw.rectangle([width-20, i+50, width, i+150], fill=palette["accent"], outline=palette["primary"], width=1)
        
        # Professional footer area
        footer_y = height - 100
        draw.rectangle([0, footer_y, width, height], fill=palette["secondary"], outline=palette["accent"], width=2)
    
    def assemble_professional_video(self, clips: List[mp.VideoClip], audio_path: str, content: VideoContent) -> str:
        """Assemble final professional video"""
        
        if not clips:
            raise ValueError("No video clips to assemble")
        
        # Concatenate clips with smooth transitions
        video = mp.concatenate_videoclips(clips, method="compose")
        
        # Add professional audio
        final_audio = mp.AudioFileClip(audio_path)
        video = video.set_audio(final_audio)
        
        # Ensure optimal duration for YouTube Shorts
        if video.duration > CONFIG["VIDEO_DURATION"]:
            video = video.subclip(0, CONFIG["VIDEO_DURATION"])
        elif video.duration < 30:  # Minimum for good engagement
            # Slow down slightly if too short
            video = video.fx(mp.vfx.speedx, 0.9)
        
        # Professional export settings
        output_filename = f"legal_short_{content.variation_id}.mp4"
        
        video.write_videofile(
            output_filename,
            fps=30,                    # Smooth playback
            codec='libx264',          # High compatibility
            audio_codec='aac',        # YouTube optimized
            bitrate='10M',            # High quality
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            verbose=False,
            logger=None,
            preset='medium'           # Quality vs speed balance
        )
        
        print(f"✅ Professional video created: {output_filename}")
        return output_filename
    
    def cleanup_temp_files(self):
        """Clean up all temporary files"""
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"⚠️ Could not remove {file_path}: {e}")
        self.temp_files.clear()

class SmartDeliverySystem:
    def __init__(self):
        self.delivery_log = self.load_delivery_log()
    
    def load_delivery_log(self) -> dict:
        """Load delivery history"""
        try:
            with open("delivery_log.json", "r") as f:
                return json.load(f)
        except:
            return {"deliveries": [], "stats": {"total": 0, "successful": 0, "failed": 0}}
    
    def save_delivery_log(self):
        """Save delivery history"""
        with open("delivery_log.json", "w") as f:
            json.dump(self.delivery_log, f, indent=2)
    
    def deliver_content(self, video_path: str, content: VideoContent):
        """Smart content delivery with analytics"""
        
        print(f"📤 Delivering content: {content.youtube_title}")
        
        delivery_record = {
            "timestamp": datetime.datetime.now().isoformat(),
            "video_path": video_path,
            "topic": content.topic,
            "approach": content.approach,
            "target_audience": content.target_audience,
            "variation_id": content.variation_id,
            "youtube_title": content.youtube_title,
            "success": False,
            "platforms": {}
        }
        
        try:
            # Send to Telegram
            telegram_success = self.send_to_telegram_professional(video_path, content)
            delivery_record["platforms"]["telegram"] = telegram_success
            
            # Generate YouTube package
            youtube_success = self.create_youtube_package(video_path, content)
            delivery_record["platforms"]["youtube"] = youtube_success
            
            # Update success status
            delivery_record["success"] = telegram_success or youtube_success
            
            # Update statistics
            self.update_delivery_stats(delivery_record["success"])
            
        except Exception as e:
            print(f"❌ Delivery error: {e}")
            delivery_record["error"] = str(e)
        
        # Log delivery
        self.delivery_log["deliveries"].append(delivery_record)
        self.save_delivery_log()
    
    def send_to_telegram_professional(self, video_path: str, content: VideoContent) -> bool:
        """Send video to Telegram with professional formatting"""
        
        if not (CONFIG["TELEGRAM_BOT_TOKEN"] and CONFIG["TELEGRAM_CHAT_ID"]):
            print("ℹ️ Telegram credentials not configured")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{CONFIG['TELEGRAM_BOT_TOKEN']}/sendVideo"
            
            # Professional caption
            caption = f"""🎬 **{CONFIG['BRAND_NAME']}** - Daily Legal Content

📺 **{content.youtube_title}**

📋 **Content Details:**
• Topic: {content.topic}
• Style: {content.approach.replace('_', ' ').title()}
• Audience: {content.target_audience.replace('_', ' ').title()}
• Variation: #{content.variation_id}
• Created: {content.date_created}

🎯 **YouTube Ready Package:**
✅ Optimized for YouTube Shorts (9:16, 55s)
✅ SEO-optimized title and tags
✅ Professional audio mixing
✅ Copyright-free content

📈 **Engagement Tips:**
• Upload during peak hours (7-9 PM IST)
• Use provided hashtags
• Pin comment with key takeaways
• Cross-post to Instagram Reels

🚀 **Ready to publish and grow your channel!**

{' '.join(content.seo_tags[:6])}"""

            with open(video_path, 'rb') as video_file:
                files = {'video': video_file}
                data = {
                    'chat_id': CONFIG["TELEGRAM_CHAT_ID"],
                    'caption': caption,
                    'parse_mode': 'Markdown'
                }
                
                response = requests.post(url, data=data, files=files, timeout=300)
                
                if response.status_code == 200:
                    print("✅ Professional delivery to Telegram successful")
                    return True
                else:
                    print(f"⚠️ Telegram delivery failed: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Telegram delivery error: {e}")
            return False
    
    def create_youtube_package(self, video_path: str, content: VideoContent) -> bool:
        """Create complete YouTube upload package"""
        
        try:
            # Generate comprehensive YouTube metadata
            youtube_package = {
                "video_file": video_path,
                "title": content.youtube_title,
                "description": self.generate_youtube_description(content),
                "tags": [tag.replace('#', '') for tag in content.seo_tags],
                "category_id": "27",  # Education
                "privacy_status": "public",
                "made_for_kids": False,
                "default_language": "en",
                "embeddable": True,
                "license": "youtube",
                "recording_date": content.date_created,
                "location_description": "India",
                "thumbnail_suggestions": self.generate_thumbnail_suggestions(content),
                "publishing_schedule": {
                    "optimal_time": "19:30 IST",  # 7:30 PM IST - peak engagement
                    "best_days": ["Tuesday", "Wednesday", "Thursday"],
                    "hashtag_strategy": content.seo_tags[:15]
                }
            }
            
            # Save YouTube package
            package_filename = f"youtube_package_{content.variation_id}.json"
            with open(package_filename, "w") as f:
                json.dump(youtube_package, f, indent=2)
            
            print(f"✅ YouTube package created: {package_filename}")
            return True
            
        except Exception as e:
            print(f"❌ YouTube package creation failed: {e}")
            return False
    
    def generate_youtube_description(self, content: VideoContent) -> str:
        """Generate comprehensive YouTube description"""
        
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        
        description = f"""🔥 {content.youtube_title}

⚖️ Learn everything about {content.topic.lower()} in under 60 seconds! This video is perfect for law students, legal professionals, and anyone who wants to understand their legal rights.

📚 **What You'll Learn:**
• Your fundamental legal rights and protections
• Step-by-step guidance for taking action
• Common legal mistakes to avoid
• Where to seek help and file complaints

🎯 **Who This Is For:**
• Law students preparing for exams
• Legal professionals staying updated
• Citizens who want to know their rights
• Anyone dealing with legal issues

⚡ **Key Takeaways:**
• Immediate action steps you can take today
• Legal deadlines and time limits to remember  
• Free resources and helplines available
• Professional legal advice recommendations

🏛️ **Legal Disclaimer:** This video provides general legal information for educational purposes only. It is not intended as legal advice for specific situations. Always consult with a qualified lawyer for advice about your particular legal matters.

📅 **Updated:** {current_date}
🇮🇳 **Jurisdiction:** Indian Legal System
👨‍💼 **Created by:** Legal professionals and educators

🔔 **Subscribe for daily legal insights!**
👍 **Like if this helped you understand your rights!**  
💬 **Comment with your legal questions!**
📤 **Share to help others know their rights!**

📱 **Connect With Us:**
• Follow for daily legal updates
• Get answers to your legal questions
• Join our community of legal learners

**TAGS:** {' '.join(content.seo_tags)}

#LegalEducation #IndianLaw #YourRights #LegalAwareness #LawMadeSimple #YouTubeShorts

---
© {datetime.datetime.now().year} {CONFIG['BRAND_NAME']} - Making Law Accessible to Everyone"""

        return description
    
    def generate_thumbnail_suggestions(self, content: VideoContent) -> List[str]:
        """Generate thumbnail design suggestions"""
        
        suggestions = [
            f"Bold text: 'LEGAL ALERT' with {content.topic} subtitle",
            f"Question format: 'Do you know your rights about {content.topic}?'",
            f"Warning style: 'URGENT: {content.topic} - What you must know'",
            f"Educational: 'LAW EXPLAINED: {content.topic} in 60 seconds'",
            f"Professional: Scales of justice icon with '{content.topic}' text"
        ]
        
        return suggestions
    
    def update_delivery_stats(self, success: bool):
        """Update delivery statistics"""
        self.delivery_log["stats"]["total"] += 1
        if success:
            self.delivery_log["stats"]["successful"] += 1
        else:
            self.delivery_log["stats"]["failed"] += 1

def main():
    """Main execution - Complete automated system"""
    
    print("🚀 STARTING COMPLETE LEGAL VIDEO AUTO-GENERATION SYSTEM")
    print("=" * 60)
    print(f"📅 {datetime.datetime.now().strftime('%A, %B %d, %Y at %H:%M:%S')}")
    print(f"🏢 {CONFIG['BRAND_NAME']}")
    print("=" * 60)
    
    try:
        # Initialize all components
        print("🔧 Initializing system components...")
        content_generator = IntelligentContentGenerator()
        video_producer = ProfessionalVideoProducer() 
        delivery_system = SmartDeliverySystem()
        print("✅ All components initialized successfully")
        
        # Get today's topic with intelligent selection
        print("\n📝 CONTENT GENERATION PHASE")
        current_topic = content_generator.get_current_topic()
        print(f"📋 Selected topic: {current_topic}")
        
        # Generate unique, professional content
        print("🧠 Generating intelligent content...")
        content = content_generator.generate_unique_content(current_topic)
        print(f"✅ Content generated successfully")
        print(f"   • Approach: {content.approach}")
        print(f"   • Target: {content.target_audience}")
        print(f"   • Variation ID: {content.variation_id}")
        print(f"   • YouTube Title: {content.youtube_title}")
        
        # Save generated script for review
        with open(f"generated_script_{content.variation_id}.txt", "w", encoding="utf-8") as f:
            f.write(content.script)
        print(f"📄 Script saved for review")
        
        # Create professional video
        print("\n🎬 VIDEO PRODUCTION PHASE")
        print("🎥 Creating professional video...")
        video_path = video_producer.create_professional_video(content)
        print(f"✅ Video production completed: {video_path}")
        
        # Deliver to all configured platforms
        print("\n📤 DELIVERY PHASE") 
        print("🚀 Delivering content to platforms...")
        delivery_system.deliver_content(video_path, content)
        print("✅ Content delivery completed")
        
        # Final summary
        print("\n" + "=" * 60)
        print("🎉 DAILY LEGAL VIDEO GENERATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"📺 Video: {video_path}")
        print(f"📋 Topic: {current_topic}")
        print(f"🎯 Title: {content.youtube_title}")
        print(f"🆔 ID: {content.variation_id}")
        print(f"📅 Date: {content.date_created}")
        print("\n🚀 Your legal content is ready for YouTube upload!")
        print("📱 Check Telegram for the complete package!")
        
    except Exception as e:
        print(f"\n❌ SYSTEM ERROR: {str(e)}")
        print("📧 Please check configuration and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
