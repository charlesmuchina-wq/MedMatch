"""
Video Generator with Screenshots and Voice
Creates tutorial videos with presenter image, app screenshots, and AI voice
"""
import os
import asyncio
from pathlib import Path
from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, ColorClip
from PIL import Image
import numpy as np

os.environ['EMERGENT_LLM_KEY'] = 'sk-emergent-e19D7A22f3f2b9f8a0'

from emergentintegrations.llm.openai import OpenAITextToSpeech

VIDEOS_DIR = Path("/app/videos")
SCREENS_DIR = Path("/app/videos/screens")
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


def create_presenter_intro(duration: float) -> ImageClip:
    """Create presenter intro clip"""
    presenter = ImageClip(PRESENTER_IMAGE)
    
    # Resize to fit left side of frame
    presenter = presenter.resized(height=720)
    
    # Create teal background
    bg = ColorClip(size=(1280, 720), color=(20, 120, 120))
    
    # Position presenter on left
    presenter = presenter.with_position(("center", "center"))
    
    clip = CompositeVideoClip([bg, presenter]).with_duration(duration)
    return clip


def create_screenshot_clip(screenshot_path: str, duration: float) -> ImageClip:
    """Create clip from screenshot"""
    if not os.path.exists(screenshot_path):
        # Fallback to teal background
        return ColorClip(size=(1280, 720), color=(20, 120, 120)).with_duration(duration)
    
    img = ImageClip(screenshot_path)
    img = img.resized((1280, 720))
    return img.with_duration(duration)


def create_video_with_screenshots(
    audio_path: str,
    output_path: str,
    screenshot_paths: list,
    intro_duration: float = 3.0
):
    """Create video combining presenter intro with screenshots"""
    
    # Load audio
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration
    
    # Calculate durations
    remaining_duration = total_duration - intro_duration
    screenshot_duration = remaining_duration / len(screenshot_paths) if screenshot_paths else remaining_duration
    
    clips = []
    
    # Add presenter intro
    intro = create_presenter_intro(intro_duration)
    clips.append(intro)
    
    # Add screenshots
    for spath in screenshot_paths:
        sclip = create_screenshot_clip(spath, screenshot_duration)
        clips.append(sclip)
    
    # Concatenate all clips
    video = concatenate_videoclips(clips, method="compose")
    
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


# CORRECTED Tutorial scripts - NO mention of SSN or national IDs
TUTORIALS = [
    {
        "id": "01_jobseeker_intro",
        "title": "Getting Started",
        "screenshots": ["01_dashboard.png", "02_job_search.png", "03_resume.png"],
        "script": """Welcome to MedMatch, your AI-powered job search platform designed for life sciences professionals. 
I'm here to guide you through getting started. 
First, create your free account using your email address. 
Then you'll see your personalized dashboard with quick actions and your Trust Score.
Upload your resume and our AI will extract your work experience, education, and skills automatically.
From there, browse personalized job matches tailored to your background.
Let's begin your journey to your dream career in life sciences!"""
    },
    {
        "id": "02_recruiter_dashboard", 
        "title": "Recruiter Dashboard",
        "screenshots": ["06_recruiter_dashboard.png", "07_ats.png", "08_job_postings.png"],
        "script": """Welcome recruiters! Let me show you your powerful hiring dashboard. 
Here you can manage all your job postings and track applicants through every stage of hiring.
The dashboard shows your key metrics including total applications and active job links.
Use the Applicant Tracking System to create shareable application links for candidates.
Search our database of qualified life sciences professionals to find your perfect hire.
Send automated email notifications to keep candidates informed throughout the process.
Let's find your next great team member together!"""
    },
    {
        "id": "03_job_search",
        "title": "Finding Jobs",
        "screenshots": ["02_job_search.png", "04_applications.png"],
        "script": """Let me show you how to find your perfect job on MedMatch.
Use the search bar to enter job titles, keywords, or company names.
Apply filters for location, salary range, remote work, and job type.
We have specialized filters just for life sciences and engineering roles.
Our AI matching technology shows you a compatibility score for each position.
Click the AI Deep Search button for even more personalized results.
Save jobs you're interested in and apply with just one click.
Track all your applications in the Applications section.
Your next opportunity in life sciences is waiting for you!"""
    },
    {
        "id": "04_ats_system",
        "title": "Applicant Tracking",
        "screenshots": ["07_ats.png", "06_recruiter_dashboard.png"],
        "script": """The Applicant Tracking System makes hiring simple and organized.
Create shareable application links for your job postings with one click.
Share these links directly with candidates through email or social media.
Track every application through stages like reviewing, interviewing, and offer extended.
See real-time metrics on total applications and active links.
Enable email notifications to automatically keep candidates informed of their status.
Use the status breakdown to see where all your candidates are in the pipeline.
With MedMatch ATS, you'll never lose track of a promising candidate!"""
    },
    {
        "id": "05_resume_upload",
        "title": "Upload Your Resume",
        "screenshots": ["03_resume.png", "01_dashboard.png"],
        "script": """Uploading your resume to MedMatch is quick and easy.
Go to My Resume in the sidebar and you'll see the upload area.
Simply drag and drop your file, or click Browse Files to select it.
We accept PDF, Word documents, and other common formats.
Our AI technology automatically extracts your work history, education, and skills.
You can also import directly from cloud storage like Google Drive or Dropbox.
Review the extracted information and make any edits you need.
A complete profile helps you get matched with the best job opportunities.
Start building your professional profile today!"""
    },
    {
        "id": "06_interview_prep",
        "title": "Interview Preparation",
        "screenshots": ["05_interview.png", "01_dashboard.png"],
        "script": """Prepare for your interviews with MedMatch's preparation tools.
Go to Interview Prep in the sidebar to access all our coaching features.
Practice common behavioral and technical questions specific to life sciences roles.
Use Mock Interview mode to simulate real interview conditions.
Research companies with our Company Research tool before your interview.
Check out Tips and Tricks for expert advice on interview success.
Record your practice answers and review them to improve your delivery.
Walk into every interview feeling confident and prepared to succeed!
Your dream job is within reach!"""
    }
]


async def generate_all_tutorials():
    """Generate all tutorial videos with screenshots"""
    for tutorial in TUTORIALS:
        print(f"\n{'='*50}")
        print(f"Generating: {tutorial['title']}")
        print(f"{'='*50}")
        
        audio_path = VIDEOS_DIR / f"{tutorial['id']}_audio.mp3"
        video_path = VIDEOS_DIR / f"{tutorial['id']}.mp4"
        
        # Build screenshot paths
        screenshot_paths = [str(SCREENS_DIR / s) for s in tutorial['screenshots']]
        
        # Generate voice
        print("Generating voice narration...")
        await generate_voice(tutorial['script'], str(audio_path))
        print(f"Audio saved: {audio_path}")
        
        # Create video with screenshots
        print("Creating video with screenshots...")
        create_video_with_screenshots(
            audio_path=str(audio_path),
            output_path=str(video_path),
            screenshot_paths=screenshot_paths,
            intro_duration=4.0
        )
        print(f"Video saved: {video_path}")
        
        # Cleanup audio file
        if audio_path.exists():
            audio_path.unlink()
        
        print(f"✓ {tutorial['title']} complete!")


if __name__ == "__main__":
    asyncio.run(generate_all_tutorials())
