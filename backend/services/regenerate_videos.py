"""
Regenerate Tutorial Videos with Diverse Presenters
- 1st video: Black woman
- 2nd video: Pacific Islander woman  
- 3rd video: Mixed Asian male
- 4th video: Brazilian blonde woman
"""
import os
import asyncio
from pathlib import Path
from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
from PIL import Image, ImageDraw
import numpy as np

os.environ['EMERGENT_LLM_KEY'] = 'sk-emergent-e19D7A22f3f2b9f8a0'

from emergentintegrations.llm.openai import OpenAITextToSpeech

VIDEOS_DIR = Path("/app/videos")
SCREENS_DIR = Path("/app/videos/screens")
SUBTITLES_DIR = Path("/app/videos/subtitles")

# Presenter images for each video
PRESENTER_IMAGES = {
    "01_jobseeker_features": "/app/frontend/public/images/presenter_1_black_woman.jpeg",
    "02_recruiter_features": "/app/frontend/public/images/presenter_2_pacific_islander.jpeg",
    "03_privacy_matters": "/app/frontend/public/images/presenter_3_asian_male.jpeg",
    "04_faq_ai_compliance": "/app/frontend/public/images/presenter_4_brazilian_blonde.jpeg"
}

# Voice selection for each video
VOICES = {
    "01_jobseeker_features": "nova",      # Female voice for black woman
    "02_recruiter_features": "shimmer",   # Female voice for Pacific Islander
    "03_privacy_matters": "onyx",         # Male voice for Asian male
    "04_faq_ai_compliance": "nova"        # Female voice for Brazilian woman
}

# Tutorial content
TUTORIALS = [
    {
        "id": "01_jobseeker_features",
        "title": "Job Seeker Features",
        "screenshots": ["01_dashboard.png", "02_job_search.png", "03_resume.png", "04_applications.png"],
        "script": """Welcome to MedMatch! I'm here to help you find your dream job in life sciences and engineering.

Let me show you around your dashboard. Here you'll see personalized job matches, your Trust Score, and quick actions to get started.

Use our powerful job search to find remote, hybrid, or on-site opportunities. Filter by location, salary, experience level, and job type.

Upload your resume and our AI will automatically extract your skills and experience to match you with the best positions.

Track all your applications in one place. See the status, next steps, and never miss an opportunity.

Get started today and take the next step in your career!"""
    },
    {
        "id": "02_recruiter_features",
        "title": "Recruiter Features", 
        "screenshots": ["06_recruiter_dashboard.png", "07_ats.png", "08_job_postings.png"],
        "script": """Welcome recruiters! Here's your hiring command center.

Your dashboard shows key metrics like total applications, active job postings, and candidate pipeline status.

The Applicant Tracking System lets you create shareable application links and track candidates through every stage of hiring.

Post remote, hybrid, or on-site positions. Manage all your job listings from one centralized location.

Let's build your dream team together!"""
    },
    {
        "id": "03_privacy_matters",
        "title": "Your Privacy Matters",
        "screenshots": ["01_dashboard.png", "03_resume.png", "02_job_search.png"],
        "script": """At MedMatch, your privacy is our top priority.

Your personal data is encrypted and securely stored using industry-leading practices.

We never sell or share your information with third parties without your explicit consent.

You control who sees your profile. Manage your visibility settings anytime in your account.

Our platform is designed with GDPR and data protection regulations in mind.

Delete your data at any time with our simple data management tools.

Trust MedMatch to keep your career journey private and secure."""
    },
    {
        "id": "04_faq_ai_compliance",
        "title": "FAQs: AI Compliance & Data Rights",
        "screenshots": ["01_dashboard.png", "02_job_search.png", "03_resume.png", "05_interview.png"],
        "script": """Let me answer your questions about AI and data rights at MedMatch.

How does MedMatch use AI? We use AI to match your skills with job opportunities, extract resume information, and provide personalized recommendations.

Is my data used to train AI models? No, your personal data is never used to train external AI models.

What are my data rights? You have full rights to access, export, or delete your data at any time.

How do I request data deletion? Simply go to Settings and select Delete My Data. We'll process your request within 30 days.

Is MedMatch GDPR compliant? Yes, we comply with GDPR, CCPA, and other major data protection regulations.

Who can I contact with questions? Reach our privacy team anytime at privacy@medmatch.com.

Thank you for trusting MedMatch with your career journey!"""
    }
]


async def generate_voice(text: str, output_path: str, voice: str = "nova") -> str:
    """Generate voice narration using OpenAI TTS"""
    tts = OpenAITextToSpeech(api_key=os.environ['EMERGENT_LLM_KEY'])
    
    audio_bytes = await tts.generate_speech(
        text=text,
        model="tts-1-hd",
        voice=voice,
        speed=0.95  # Slightly slower for better comprehension
    )
    
    with open(output_path, "wb") as f:
        f.write(audio_bytes)
    
    return output_path


def create_circular_presenter(presenter_path: str, size=200):
    """Create circular presenter image with border"""
    img = Image.open(presenter_path)
    
    # Crop to square from center
    width, height = img.size
    min_dim = min(width, height)
    left = (width - min_dim) // 2
    top = (height - min_dim) // 2
    img = img.crop((left, top, left + min_dim, top + min_dim))
    
    # Resize to target size
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
        screenshot = screenshot.resize((1000, 620), Image.LANCZOS)
        canvas.paste(screenshot, (20, 50))
    
    # Convert presenter to RGB for pasting
    presenter_rgb = Image.new('RGB', presenter_img.size, (30, 30, 40))
    presenter_rgb.paste(presenter_img, mask=presenter_img.split()[3])
    
    # Position presenter in bottom right
    presenter_pos = (1050, 480)
    canvas.paste(presenter_img, presenter_pos, presenter_img)
    
    return np.array(canvas)


def create_pip_video(audio_path: str, output_path: str, screenshot_paths: list, presenter_img: Image.Image):
    """Create picture-in-picture video with presenter visible throughout"""
    
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration
    
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


def generate_subtitles(script: str, audio_duration: float, video_id: str):
    """Generate VTT subtitles with proper timing synced to audio duration"""
    lines = [line.strip() for line in script.strip().split('\n') if line.strip()]
    
    # Calculate time per line based on actual audio duration
    time_per_line = audio_duration / len(lines)
    
    vtt_content = "WEBVTT\n\n"
    
    for i, line in enumerate(lines):
        start_time = i * time_per_line
        end_time = (i + 1) * time_per_line
        
        # Format timestamps
        start_str = f"{int(start_time // 3600):02d}:{int((start_time % 3600) // 60):02d}:{start_time % 60:06.3f}"
        end_str = f"{int(end_time // 3600):02d}:{int((end_time % 3600) // 60):02d}:{end_time % 60:06.3f}"
        
        vtt_content += f"{start_str} --> {end_str}\n{line}\n\n"
    
    # Save subtitle file
    subtitle_path = SUBTITLES_DIR / f"{video_id}_en.vtt"
    with open(subtitle_path, 'w') as f:
        f.write(vtt_content)
    
    print(f"  Subtitles saved: {subtitle_path}")
    return subtitle_path


async def regenerate_all_videos():
    """Regenerate all tutorial videos with diverse presenters"""
    
    SUBTITLES_DIR.mkdir(parents=True, exist_ok=True)
    
    for tutorial in TUTORIALS:
        video_id = tutorial['id']
        print(f"\n{'='*60}")
        print(f"Regenerating: {tutorial['title']}")
        print(f"{'='*60}")
        
        presenter_path = PRESENTER_IMAGES.get(video_id)
        voice = VOICES.get(video_id, "nova")
        
        if not presenter_path or not os.path.exists(presenter_path):
            print(f"  ⚠ Presenter image not found: {presenter_path}")
            continue
        
        print(f"  Presenter: {os.path.basename(presenter_path)}")
        print(f"  Voice: {voice}")
        
        audio_path = VIDEOS_DIR / f"{video_id}_audio.mp3"
        video_path = VIDEOS_DIR / f"{video_id}.mp4"
        
        # Build screenshot paths
        screenshot_paths = [str(SCREENS_DIR / s) for s in tutorial['screenshots']]
        
        # Verify screenshots exist
        for sp in screenshot_paths:
            if os.path.exists(sp):
                print(f"  ✓ Screenshot: {os.path.basename(sp)}")
            else:
                print(f"  ✗ Missing: {sp}")
        
        # Generate voice
        print("  Generating voice narration...")
        await generate_voice(tutorial['script'], str(audio_path), voice)
        print(f"  Audio saved: {audio_path}")
        
        # Get audio duration for subtitle sync
        audio = AudioFileClip(str(audio_path))
        audio_duration = audio.duration
        audio.close()
        print(f"  Audio duration: {audio_duration:.1f} seconds")
        
        # Generate subtitles synced to audio
        print("  Generating synchronized subtitles...")
        generate_subtitles(tutorial['script'], audio_duration, video_id)
        
        # Create presenter image
        presenter_img = create_circular_presenter(presenter_path, size=200)
        
        # Create video with picture-in-picture
        print("  Creating picture-in-picture video...")
        create_pip_video(
            audio_path=str(audio_path),
            output_path=str(video_path),
            screenshot_paths=screenshot_paths,
            presenter_img=presenter_img
        )
        print(f"  Video saved: {video_path}")
        
        # Cleanup audio file
        if audio_path.exists():
            audio_path.unlink()
        
        print(f"✓ {tutorial['title']} complete!")
    
    print(f"\n{'='*60}")
    print("All videos regenerated successfully!")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(regenerate_all_videos())
