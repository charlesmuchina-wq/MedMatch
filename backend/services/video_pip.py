"""
Picture-in-Picture Video Generator
Creates tutorial videos with presenter visible alongside app screenshots
"""
import os
import asyncio
from pathlib import Path
from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, ColorClip
from PIL import Image, ImageDraw, ImageFilter
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
        speed=1.0
    )
    
    with open(output_path, "wb") as f:
        f.write(audio_bytes)
    
    return output_path


def create_circular_presenter(size=200):
    """Create circular presenter image with border"""
    # Open presenter image
    img = Image.open(PRESENTER_IMAGE)
    
    # Resize to square
    img = img.resize((size, size), Image.LANCZOS)
    
    # Create circular mask
    mask = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    
    # Apply mask
    output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    output.paste(img, (0, 0))
    output.putalpha(mask)
    
    # Add border
    border_size = size + 8
    bordered = Image.new('RGBA', (border_size, border_size), (0, 0, 0, 0))
    border_mask = Image.new('L', (border_size, border_size), 0)
    border_draw = ImageDraw.Draw(border_mask)
    border_draw.ellipse((0, 0, border_size, border_size), fill=255)
    
    # White border background
    border_bg = Image.new('RGBA', (border_size, border_size), (255, 255, 255, 255))
    border_bg.putalpha(border_mask)
    
    # Paste presenter on border
    bordered.paste(border_bg, (0, 0))
    bordered.paste(output, (4, 4), output)
    
    return bordered


def create_pip_frame(screenshot_path: str, presenter_img: Image.Image) -> np.ndarray:
    """Create a single frame with screenshot and presenter picture-in-picture"""
    # Create base canvas (1280x720)
    canvas = Image.new('RGB', (1280, 720), (30, 30, 40))
    
    # Load and resize screenshot
    if os.path.exists(screenshot_path):
        screenshot = Image.open(screenshot_path)
        # Resize screenshot to fit main area (leaving space for presenter)
        screenshot = screenshot.resize((1000, 620), Image.LANCZOS)
        # Position screenshot on left side with padding
        canvas.paste(screenshot, (20, 50))
    
    # Convert presenter to RGB for pasting
    presenter_rgb = Image.new('RGB', presenter_img.size, (30, 30, 40))
    presenter_rgb.paste(presenter_img, mask=presenter_img.split()[3])
    
    # Position presenter in bottom right
    presenter_pos = (1050, 480)
    canvas.paste(presenter_img, presenter_pos, presenter_img)
    
    return np.array(canvas)


def create_pip_video(
    audio_path: str,
    output_path: str,
    screenshot_paths: list
):
    """Create picture-in-picture video with presenter visible throughout"""
    
    # Load audio
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration
    
    # Create circular presenter image
    presenter_img = create_circular_presenter(size=200)
    
    # Calculate duration per screenshot
    duration_per_screenshot = total_duration / len(screenshot_paths) if screenshot_paths else total_duration
    
    clips = []
    
    for i, spath in enumerate(screenshot_paths):
        # Create frame with this screenshot
        frame = create_pip_frame(spath, presenter_img)
        
        # Create clip from frame
        clip = ImageClip(frame).with_duration(duration_per_screenshot)
        clips.append(clip)
    
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


# Tutorial scripts - accurate information, ~20-25 seconds each
TUTORIALS = [
    {
        "id": "01_jobseeker_intro",
        "title": "Getting Started",
        "screenshots": ["01_dashboard.png", "02_job_search.png", "03_resume.png"],
        "script": """Welcome to MedMatch! I'm here to help you find your dream job in life sciences. 
Let me show you around. This is your dashboard where you'll see personalized job matches and your Trust Score.
Use Job Search to find opportunities filtered by location, salary, and job type.
Upload your resume and our AI will automatically extract your skills and experience.
Get started today and take the next step in your career!"""
    },
    {
        "id": "02_recruiter_dashboard", 
        "title": "Recruiter Dashboard",
        "screenshots": ["06_recruiter_dashboard.png", "07_ats.png", "08_job_postings.png"],
        "script": """Welcome recruiters! Here's your hiring command center.
Your dashboard shows key metrics like total applications and active job postings.
The Applicant Tracking System lets you create shareable links and track candidates through every stage.
Manage all your job postings, review applicants, and find your next great hire.
Let's build your dream team together!"""
    },
    {
        "id": "03_job_search",
        "title": "Finding Jobs",
        "screenshots": ["02_job_search.png", "04_applications.png", "01_dashboard.png"],
        "script": """Let me show you how to find your perfect job.
Use the search bar and filters to narrow down opportunities by location, salary, and job type.
Our AI matching shows you a compatibility score for each position.
Save jobs you like and apply with one click.
Track all your applications in the Applications section.
Your next opportunity is just a search away!"""
    },
    {
        "id": "04_ats_system",
        "title": "Applicant Tracking",
        "screenshots": ["07_ats.png", "08_job_postings.png", "06_recruiter_dashboard.png"],
        "script": """The Applicant Tracking System makes hiring simple.
Create shareable application links for your job postings with one click.
Track candidates through stages like reviewing, interviewing, and offer extended.
Enable automatic email notifications to keep candidates informed.
See your pipeline at a glance and never lose track of great talent!"""
    },
    {
        "id": "05_resume_upload",
        "title": "Upload Your Resume",
        "screenshots": ["03_resume.png", "01_dashboard.png", "02_job_search.png"],
        "script": """Uploading your resume is quick and easy.
Simply drag and drop your file or click to browse. We accept PDF and Word formats.
Our AI extracts your work history, education, and skills automatically.
A complete profile helps you get matched with the best opportunities.
Start building your professional profile today!"""
    },
    {
        "id": "06_interview_prep",
        "title": "Interview Preparation",
        "screenshots": ["05_interview.png", "01_dashboard.png", "02_job_search.png"],
        "script": """Prepare for interviews with our coaching tools.
Practice behavioral and technical questions specific to life sciences.
Use Mock Interview mode to simulate real conditions.
Research companies before your interview and review expert tips.
Walk into every interview feeling confident and ready to succeed!"""
    }
]


async def generate_all_tutorials():
    """Generate all tutorial videos with picture-in-picture"""
    for tutorial in TUTORIALS:
        print(f"\n{'='*50}")
        print(f"Generating: {tutorial['title']}")
        print(f"{'='*50}")
        
        audio_path = VIDEOS_DIR / f"{tutorial['id']}_audio.mp3"
        video_path = VIDEOS_DIR / f"{tutorial['id']}.mp4"
        
        # Build screenshot paths
        screenshot_paths = [str(SCREENS_DIR / s) for s in tutorial['screenshots']]
        
        # Verify screenshots exist
        for sp in screenshot_paths:
            if os.path.exists(sp):
                print(f"  ✓ Found: {os.path.basename(sp)}")
            else:
                print(f"  ✗ Missing: {sp}")
        
        # Generate voice
        print("Generating voice narration...")
        await generate_voice(tutorial['script'], str(audio_path))
        print(f"Audio saved: {audio_path}")
        
        # Create video with picture-in-picture
        print("Creating picture-in-picture video...")
        create_pip_video(
            audio_path=str(audio_path),
            output_path=str(video_path),
            screenshot_paths=screenshot_paths
        )
        print(f"Video saved: {video_path}")
        
        # Cleanup audio file
        if audio_path.exists():
            audio_path.unlink()
        
        print(f"✓ {tutorial['title']} complete!")


if __name__ == "__main__":
    asyncio.run(generate_all_tutorials())
