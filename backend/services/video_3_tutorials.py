"""
Create 3 Tutorial Videos:
1. Job Seeker Features - Female presenter
2. Recruiter Features - Female presenter
3. Your Privacy Matters - Male presenter
"""
import os
import asyncio
from pathlib import Path
from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, ColorClip
from PIL import Image, ImageDraw
import numpy as np

os.environ['EMERGENT_LLM_KEY'] = 'sk-emergent-e19D7A22f3f2b9f8a0'

from emergentintegrations.llm.openai import OpenAITextToSpeech

VIDEOS_DIR = Path("/app/videos")
SCREENS_DIR = Path("/app/videos/screens")
PRESENTER_FEMALE = "/app/frontend/public/images/presenter.jpeg"
PRESENTER_MALE = "/app/frontend/public/images/presenter_male.jpeg"


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


def create_circular_presenter(image_path: str, size=200):
    """Create circular presenter image with border"""
    img = Image.open(image_path)
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
    
    border_bg = Image.new('RGBA', (border_size, border_size), (255, 255, 255, 255))
    border_bg.putalpha(border_mask)
    
    bordered.paste(border_bg, (0, 0))
    bordered.paste(output, (4, 4), output)
    
    return bordered


def create_pip_frame(screenshot_path: str, presenter_img: Image.Image) -> np.ndarray:
    """Create a frame with screenshot and presenter picture-in-picture"""
    canvas = Image.new('RGB', (1280, 720), (30, 30, 40))
    
    if os.path.exists(screenshot_path):
        screenshot = Image.open(screenshot_path)
        screenshot = screenshot.resize((1000, 620), Image.LANCZOS)
        canvas.paste(screenshot, (20, 50))
    
    presenter_pos = (1050, 480)
    canvas.paste(presenter_img, presenter_pos, presenter_img)
    
    return np.array(canvas)


def create_pip_video(
    audio_path: str,
    output_path: str,
    screenshot_paths: list,
    presenter_image_path: str
):
    """Create picture-in-picture video"""
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration
    
    presenter_img = create_circular_presenter(presenter_image_path, size=200)
    duration_per_screenshot = total_duration / len(screenshot_paths) if screenshot_paths else total_duration
    
    clips = []
    for spath in screenshot_paths:
        frame = create_pip_frame(spath, presenter_img)
        clip = ImageClip(frame).with_duration(duration_per_screenshot)
        clips.append(clip)
    
    video = concatenate_videoclips(clips, method="compose")
    video = video.with_audio(audio)
    
    video.write_videofile(
        output_path,
        fps=24,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile='temp-audio.m4a',
        remove_temp=True,
        logger=None
    )
    
    audio.close()
    video.close()
    return output_path


# The 3 videos as specified
TUTORIALS = [
    {
        "id": "01_jobseeker_features",
        "title": "Job Seeker Features",
        "presenter": PRESENTER_FEMALE,
        "voice": "nova",  # Female voice
        "screenshots": ["01_dashboard.png", "02_job_search.png", "03_resume.png", "04_applications.png", "05_interview.png"],
        "script": """Welcome to MedMatch! I'm excited to show you our powerful features for job seekers.
Start with your personalized dashboard showing AI-matched jobs and your Trust Score.
Our job search lets you find remote, hybrid, or on-site positions with smart filters.
Upload your resume and our AI automatically extracts your skills and experience.
Track all your applications in one place and see your progress.
Prepare for interviews with our coaching tools, practice questions, and expert tips.
MedMatch is your complete career platform for life sciences success!"""
    },
    {
        "id": "02_recruiter_features",
        "title": "Recruiter Features",
        "presenter": PRESENTER_FEMALE,
        "voice": "nova",  # Female voice
        "screenshots": ["06_recruiter_dashboard.png", "07_ats.png", "08_job_postings.png"],
        "script": """Welcome recruiters! Let me show you our powerful hiring tools.
Your dashboard gives you real-time metrics on applications and hiring progress.
Our Applicant Tracking System lets you create shareable links for any job posting.
Track candidates through every stage from application to offer.
Post remote, hybrid, or on-site positions and manage everything in one place.
Send automatic email notifications to keep candidates engaged.
MedMatch helps you find and hire top life sciences talent faster!"""
    },
    {
        "id": "03_privacy_matters",
        "title": "Your Privacy Matters",
        "presenter": PRESENTER_MALE,
        "voice": "onyx",  # Male voice
        "screenshots": ["01_dashboard.png", "03_resume.png"],
        "script": """At MedMatch, your privacy is our top priority.
Your personal data is encrypted and securely stored using industry best practices.
We never sell or share your information with third parties without your consent.
You control who sees your profile and can manage your visibility settings anytime.
Our platform is designed with GDPR and data protection regulations in mind.
Delete your data at any time with our simple data management tools.
Trust MedMatch to keep your career journey private and secure."""
    }
]


async def generate_all_videos():
    """Generate all 3 tutorial videos"""
    for tutorial in TUTORIALS:
        print(f"\n{'='*50}")
        print(f"Generating: {tutorial['title']}")
        print(f"Presenter: {'Female' if 'presenter.jpeg' in tutorial['presenter'] else 'Male'}")
        print(f"{'='*50}")
        
        audio_path = VIDEOS_DIR / f"{tutorial['id']}_audio.mp3"
        video_path = VIDEOS_DIR / f"{tutorial['id']}.mp4"
        
        screenshot_paths = [str(SCREENS_DIR / s) for s in tutorial['screenshots']]
        
        for sp in screenshot_paths:
            if os.path.exists(sp):
                print(f"  ✓ Found: {os.path.basename(sp)}")
        
        # Generate voice with appropriate voice
        print(f"Generating voice narration ({tutorial['voice']})...")
        await generate_voice(tutorial['script'], str(audio_path), voice=tutorial['voice'])
        print(f"Audio saved: {audio_path}")
        
        # Create video
        print("Creating picture-in-picture video...")
        create_pip_video(
            audio_path=str(audio_path),
            output_path=str(video_path),
            screenshot_paths=screenshot_paths,
            presenter_image_path=tutorial['presenter']
        )
        print(f"Video saved: {video_path}")
        
        if audio_path.exists():
            audio_path.unlink()
        
        print(f"✓ {tutorial['title']} complete!")


if __name__ == "__main__":
    asyncio.run(generate_all_videos())
