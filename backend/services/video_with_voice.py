"""
Video Generator with Voice Narration
Creates tutorial videos with presenter image and AI voice
"""
import os
import asyncio
from pathlib import Path
from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, TextClip, ColorClip
from PIL import Image
import numpy as np

# Set environment
os.environ['EMERGENT_LLM_KEY'] = 'sk-emergent-e19D7A22f3f2b9f8a0'

from emergentintegrations.llm.openai import OpenAITextToSpeech

VIDEOS_DIR = Path("/app/videos")
PRESENTER_IMAGE = "/app/frontend/public/images/presenter.jpeg"


async def generate_voice(text: str, output_path: str, voice: str = "nova") -> str:
    """Generate voice narration using OpenAI TTS"""
    tts = OpenAITextToSpeech(api_key=os.environ['EMERGENT_LLM_KEY'])
    
    audio_bytes = await tts.generate_speech(
        text=text,
        model="tts-1-hd",
        voice=voice,
        speed=0.95
    )
    
    with open(output_path, "wb") as f:
        f.write(audio_bytes)
    
    return output_path


def create_video_with_voice(
    presenter_image: str,
    audio_path: str,
    output_path: str,
    title: str,
    subtitle: str
):
    """Create video with presenter image and voice narration"""
    
    # Load audio to get duration
    audio = AudioFileClip(audio_path)
    duration = audio.duration
    
    # Create presenter image clip
    presenter = ImageClip(presenter_image).with_duration(duration)
    
    # Resize to fit video frame (1280x720)
    presenter = presenter.resized(height=720)
    
    # Center the image
    presenter = presenter.with_position("center")
    
    # Create background
    bg = ColorClip(size=(1280, 720), color=(20, 100, 100)).with_duration(duration)
    
    # Create title overlay
    try:
        title_clip = TextClip(
            text=title,
            font_size=36,
            color='white',
            font='Arial-Bold'
        ).with_duration(duration).with_position(("center", 30))
    except:
        title_clip = None
    
    # Composite video
    if title_clip:
        video = CompositeVideoClip([bg, presenter, title_clip])
    else:
        video = CompositeVideoClip([bg, presenter])
    
    # Add audio
    video = video.with_audio(audio)
    
    # Write output
    video.write_videofile(
        output_path,
        fps=24,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile='temp-audio.m4a',
        remove_temp=True,
        logger=None
    )
    
    # Cleanup
    audio.close()
    video.close()
    
    return output_path


# Tutorial scripts with complete sentences
TUTORIALS = [
    {
        "id": "01_jobseeker_intro",
        "title": "Getting Started",
        "script": """Welcome to MedMatch, your AI-powered job search platform designed specifically for life sciences professionals. 
I'm excited to guide you through getting started. First, create your profile by signing up with your email or social account. 
Then upload your resume, and our AI will automatically extract your skills and experience. 
From there, you'll receive personalized job matches tailored to your background. Let's begin your journey to your dream career!"""
    },
    {
        "id": "02_recruiter_dashboard", 
        "title": "Recruiter Dashboard",
        "script": """Welcome recruiters! Let me show you your powerful dashboard. 
Here you can manage all your job postings, track applicants through every stage, and search our database of qualified candidates.
The dashboard gives you real-time metrics on applications, interviews, and hiring progress.
Use the applicant tracking system to move candidates through your pipeline and send automated notifications.
Let's find your next great hire together!"""
    },
    {
        "id": "03_job_search",
        "title": "Finding Jobs",
        "script": """Let me show you how to find your perfect job on MedMatch.
Use the search bar to enter keywords, job titles, or company names. Then apply filters for location, salary range, and job type.
Our AI matching shows you a compatibility score for each position based on your profile.
Save jobs you're interested in to review later, and apply with just one click when you're ready.
Your next opportunity is waiting!"""
    },
    {
        "id": "04_ats_system",
        "title": "Applicant Tracking",
        "script": """The Applicant Tracking System makes hiring simple.
Create shareable application links for your job postings and send them to candidates directly.
Track every application through stages like reviewing, interviewing, and offer extended.
Enable email notifications to keep candidates informed automatically.
With MedMatch ATS, you'll never lose track of a great candidate again!"""
    },
    {
        "id": "05_resume_upload",
        "title": "Upload Your Resume",
        "script": """Uploading your resume to MedMatch is quick and easy.
Simply drag and drop your file, or click to browse. We accept PDF, Word, and text formats.
Our AI technology automatically extracts your work experience, education, skills, and certifications.
Review the extracted information and make any edits needed.
A complete profile helps you get matched with the best opportunities!"""
    },
    {
        "id": "06_interview_prep",
        "title": "Interview Preparation",
        "script": """Prepare for your interviews with MedMatch's preparation tools.
Practice common behavioral and technical questions specific to life sciences roles.
Record your answers and review them to improve your delivery.
Get AI-powered feedback on your responses and body language tips.
Walk into every interview feeling confident and prepared to succeed!"""
    }
]


async def generate_all_tutorials():
    """Generate all tutorial videos"""
    for tutorial in TUTORIALS:
        print(f"\n{'='*50}")
        print(f"Generating: {tutorial['title']}")
        print(f"{'='*50}")
        
        audio_path = VIDEOS_DIR / f"{tutorial['id']}_audio.mp3"
        video_path = VIDEOS_DIR / f"{tutorial['id']}.mp4"
        
        # Generate voice
        print("Generating voice narration...")
        await generate_voice(tutorial['script'], str(audio_path))
        print(f"Audio saved: {audio_path}")
        
        # Create video
        print("Creating video...")
        create_video_with_voice(
            presenter_image=PRESENTER_IMAGE,
            audio_path=str(audio_path),
            output_path=str(video_path),
            title=tutorial['title'],
            subtitle=""
        )
        print(f"Video saved: {video_path}")
        
        # Cleanup audio file
        if audio_path.exists():
            audio_path.unlink()


if __name__ == "__main__":
    asyncio.run(generate_all_tutorials())
