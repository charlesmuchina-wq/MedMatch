"""
Video Translation Service
Provides subtitles and on-demand video translation
"""
import os
import asyncio
from pathlib import Path
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, Response
from typing import Optional
import json

router = APIRouter(prefix="/tutorials", tags=["Tutorials Translation"])

VIDEOS_DIR = Path("/app/videos")
SUBTITLES_DIR = Path("/app/videos/subtitles")

# Supported languages for translation
SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "zh": "Chinese",
    "ja": "Japanese",
    "pt": "Portuguese",
    "ar": "Arabic",
    "hi": "Hindi",
    "ko": "Korean",
    "it": "Italian",
    "ru": "Russian",
    "sw": "Swahili",
    "tl": "Tagalog",
    "vi": "Vietnamese"
}

# Video transcripts for translation
VIDEO_TRANSCRIPTS = {
    "01_jobseeker_features": {
        "en": """Welcome to MedMatch! I'm excited to show you our powerful features for job seekers.
Start with your personalized dashboard showing AI-matched jobs and your Trust Score.
Our job search lets you find remote, hybrid, or on-site positions with smart filters.
Upload your resume and our AI automatically extracts your skills and experience.
Track all your applications in one place and see your progress.
Prepare for interviews with our coaching tools, practice questions, and expert tips.
MedMatch is your complete career platform for life sciences success!"""
    },
    "02_recruiter_features": {
        "en": """Welcome recruiters! Let me show you our powerful hiring tools.
Your dashboard gives you real-time metrics on applications and hiring progress.
Our Applicant Tracking System lets you create shareable links for any job posting.
Track candidates through every stage from application to offer.
Post remote, hybrid, or on-site positions and manage everything in one place.
Send automatic email notifications to keep candidates engaged.
MedMatch helps you find and hire top life sciences talent faster!"""
    },
    "03_privacy_matters": {
        "en": """At MedMatch, your privacy is our top priority.
Your personal data is encrypted and securely stored using industry best practices.
We never sell or share your information with third parties without your consent.
You control who sees your profile and can manage your visibility settings anytime.
Our platform is designed with GDPR and data protection regulations in mind.
Delete your data at any time with our simple data management tools.
Trust MedMatch to keep your career journey private and secure."""
    },
    "04_faq_ai_compliance": {
        "en": """Aloha! Let me answer some frequently asked questions about AI and your data rights at MedMatch.
How does MedMatch use AI? Our AI analyzes your resume and job preferences to provide personalized matches. It does not make hiring decisions. Employers always make the final choice.
What about AI compliance? MedMatch follows responsible AI principles. Our algorithms are designed to be fair and unbiased. We regularly audit our systems to prevent discrimination based on age, gender, ethnicity, or other protected characteristics.
Do you own your data? Absolutely yes. You retain full ownership of all information you provide. Your resume, profile, and application history belong to you.
Can you delete your data? Yes, at any time. Visit your account settings to download a copy of your data or request complete deletion. We comply with GDPR and other data protection regulations.
Is your information shared? Never without your consent. We do not sell your personal data to third parties. Recruiters only see what you choose to make visible.
How is AI used in matching? Our AI looks at your skills, experience, and preferences to suggest relevant jobs. You control the matching by setting your own filters and criteria.
Thank you for trusting MedMatch with your career journey. Your privacy and rights are always our priority. Mahalo!"""
    }
}

# Track translation jobs in progress
translation_jobs = {}


@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages for video translation"""
    return {
        "languages": [
            {"code": code, "name": name}
            for code, name in SUPPORTED_LANGUAGES.items()
        ],
        "default": "en"
    }


@router.get("/subtitles/{video_id}")
async def get_subtitles(video_id: str, lang: str = "en"):
    """Get subtitles for a video in specified language"""
    subtitle_file = SUBTITLES_DIR / f"{video_id}_{lang}.vtt"
    
    if subtitle_file.exists():
        return FileResponse(
            path=str(subtitle_file),
            media_type="text/vtt",
            filename=f"{video_id}_{lang}.vtt"
        )
    
    # If not English and doesn't exist, try to generate on-demand
    if lang != "en":
        # Check if English exists to translate from
        en_subtitle = SUBTITLES_DIR / f"{video_id}_en.vtt"
        if en_subtitle.exists():
            # Translate subtitles on-demand
            translated = await translate_subtitles(video_id, lang)
            if translated:
                return FileResponse(
                    path=str(subtitle_file),
                    media_type="text/vtt",
                    filename=f"{video_id}_{lang}.vtt"
                )
    
    raise HTTPException(status_code=404, detail=f"Subtitles not available for {video_id} in {lang}")


@router.get("/subtitles/{video_id}/available")
async def get_available_subtitles(video_id: str):
    """Get list of available subtitle languages for a video"""
    available = []
    for lang_code in SUPPORTED_LANGUAGES.keys():
        subtitle_file = SUBTITLES_DIR / f"{video_id}_{lang_code}.vtt"
        if subtitle_file.exists():
            available.append({
                "code": lang_code,
                "name": SUPPORTED_LANGUAGES[lang_code],
                "url": f"/api/tutorials/subtitles/{video_id}?lang={lang_code}"
            })
    
    return {
        "video_id": video_id,
        "available_subtitles": available,
        "can_generate": list(SUPPORTED_LANGUAGES.keys())
    }


@router.post("/translate/{video_id}")
async def request_video_translation(
    video_id: str,
    lang: str,
    background_tasks: BackgroundTasks
):
    """Request on-demand video translation"""
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Language {lang} not supported")
    
    if video_id not in VIDEO_TRANSCRIPTS:
        raise HTTPException(status_code=404, detail=f"Video {video_id} not found")
    
    # Check if already exists
    video_file = VIDEOS_DIR / f"{video_id}_{lang}.mp4"
    if video_file.exists():
        return {
            "status": "ready",
            "video_url": f"/api/tutorials/videos/{video_id}?lang={lang}",
            "language": SUPPORTED_LANGUAGES[lang]
        }
    
    # Check if already generating
    job_key = f"{video_id}_{lang}"
    if job_key in translation_jobs and translation_jobs[job_key] == "generating":
        return {
            "status": "generating",
            "message": f"Translation to {SUPPORTED_LANGUAGES[lang]} is in progress"
        }
    
    # Queue translation job
    translation_jobs[job_key] = "generating"
    background_tasks.add_task(generate_translated_video, video_id, lang)
    
    return {
        "status": "queued",
        "message": f"Translation to {SUPPORTED_LANGUAGES[lang]} has been queued",
        "check_url": f"/api/tutorials/translate/{video_id}/status?lang={lang}"
    }


@router.get("/translate/{video_id}/status")
async def check_translation_status(video_id: str, lang: str):
    """Check status of video translation"""
    job_key = f"{video_id}_{lang}"
    
    # Check if video exists
    video_file = VIDEOS_DIR / f"{video_id}_{lang}.mp4"
    if video_file.exists():
        return {
            "status": "ready",
            "video_url": f"/api/tutorials/videos/{video_id}?lang={lang}"
        }
    
    if job_key in translation_jobs:
        return {"status": translation_jobs[job_key]}
    
    return {"status": "not_started"}


async def translate_subtitles(video_id: str, target_lang: str) -> bool:
    """Translate subtitles to target language using AI"""
    try:
        from emergentintegrations.llm.openai import OpenAITextGeneration
        
        # Read English subtitles
        en_file = SUBTITLES_DIR / f"{video_id}_en.vtt"
        if not en_file.exists():
            return False
        
        en_content = en_file.read_text()
        
        # Use AI to translate
        llm = OpenAITextGeneration(api_key=os.environ.get('EMERGENT_LLM_KEY'))
        
        prompt = f"""Translate the following WebVTT subtitle file to {SUPPORTED_LANGUAGES[target_lang]}.
Keep the exact same timestamp format (WEBVTT format).
Only translate the text content, not the timestamps or WEBVTT header.

{en_content}"""
        
        translated = await llm.generate(prompt, model="gpt-4o-mini")
        
        # Save translated subtitles
        target_file = SUBTITLES_DIR / f"{video_id}_{target_lang}.vtt"
        target_file.write_text(translated)
        
        return True
    except Exception as e:
        print(f"Subtitle translation error: {e}")
        return False


async def generate_translated_video(video_id: str, target_lang: str):
    """Generate video with translated audio (background task)"""
    job_key = f"{video_id}_{lang}"
    
    try:
        from emergentintegrations.llm.openai import OpenAITextGeneration, OpenAITextToSpeech
        from moviepy import VideoFileClip, AudioFileClip
        
        # Get original transcript
        if video_id not in VIDEO_TRANSCRIPTS:
            translation_jobs[job_key] = "failed"
            return
        
        en_transcript = VIDEO_TRANSCRIPTS[video_id]["en"]
        
        # Translate transcript
        llm = OpenAITextGeneration(api_key=os.environ.get('EMERGENT_LLM_KEY'))
        prompt = f"Translate the following to {SUPPORTED_LANGUAGES[target_lang]}. Keep the same tone and style:\n\n{en_transcript}"
        translated_text = await llm.generate(prompt, model="gpt-4o-mini")
        
        # Generate audio in target language
        tts = OpenAITextToSpeech(api_key=os.environ.get('EMERGENT_LLM_KEY'))
        audio_bytes = await tts.generate_speech(
            text=translated_text,
            model="tts-1-hd",
            voice="nova"
        )
        
        # Save audio
        audio_path = VIDEOS_DIR / f"{video_id}_{target_lang}_audio.mp3"
        with open(audio_path, "wb") as f:
            f.write(audio_bytes)
        
        # Load original video (for visuals only)
        original_video = VideoFileClip(str(VIDEOS_DIR / f"{video_id}.mp4"))
        new_audio = AudioFileClip(str(audio_path))
        
        # Combine original visuals with new audio
        final_video = original_video.with_audio(new_audio)
        
        # Save translated video
        output_path = VIDEOS_DIR / f"{video_id}_{target_lang}.mp4"
        final_video.write_videofile(
            str(output_path),
            fps=24,
            codec='libx264',
            audio_codec='aac'
        )
        
        # Cleanup
        original_video.close()
        new_audio.close()
        audio_path.unlink()
        
        translation_jobs[job_key] = "ready"
        
    except Exception as e:
        print(f"Video translation error: {e}")
        translation_jobs[job_key] = "failed"
