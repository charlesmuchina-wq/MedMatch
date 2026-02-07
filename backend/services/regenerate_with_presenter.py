"""
Regenerate Tutorial Videos with the Main Presenter Image
Uses the professional MedMatch presenter image with app screenshots
"""
import os
import asyncio
from pathlib import Path
from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

os.environ['EMERGENT_LLM_KEY'] = 'sk-emergent-e19D7A22f3f2b9f8a0'

from emergentintegrations.llm.openai import OpenAITextToSpeech

VIDEOS_DIR = Path("/app/videos")
SCREENS_DIR = Path("/app/videos/screens")
SUBTITLES_DIR = Path("/app/videos/subtitles")

# Main presenter image for all videos
MAIN_PRESENTER = "/app/frontend/public/images/presenter_main.jpeg"

# Voice selection for each video
VOICES = {
    "01_jobseeker_features": "nova",      # Female voice
    "02_recruiter_features": "nova",      # Female voice
    "03_privacy_matters": "nova",         # Female voice
    "04_faq_ai_compliance": "nova"        # Female voice
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


def create_presenter_frame(presenter_path: str, screenshot_path: str = None) -> np.ndarray:
    """Create a frame with the presenter image and optional screenshot overlay"""
    # Load presenter image
    presenter = Image.open(presenter_path)
    
    # Resize to 1280x720 maintaining aspect ratio
    presenter_ratio = presenter.width / presenter.height
    target_ratio = 1280 / 720
    
    if presenter_ratio > target_ratio:
        # Image is wider, fit by height
        new_height = 720
        new_width = int(720 * presenter_ratio)
    else:
        # Image is taller, fit by width
        new_width = 1280
        new_height = int(1280 / presenter_ratio)
    
    presenter = presenter.resize((new_width, new_height), Image.LANCZOS)
    
    # Create canvas and paste presenter centered
    canvas = Image.new('RGB', (1280, 720), (240, 235, 230))  # Beige background
    
    # Center the image
    x_offset = (1280 - new_width) // 2
    y_offset = (720 - new_height) // 2
    canvas.paste(presenter, (x_offset, y_offset))
    
    # If we have a screenshot, create a phone mockup overlay
    if screenshot_path and os.path.exists(screenshot_path):
        screenshot = Image.open(screenshot_path)
        
        # Resize screenshot to fit in phone mockup area (approximately where phone is in the image)
        # The phone in the original image is roughly 180x350 pixels in the lower left area
        phone_width = 200
        phone_height = 380
        screenshot = screenshot.resize((phone_width, phone_height), Image.LANCZOS)
        
        # Create a phone frame effect
        phone_frame = Image.new('RGBA', (phone_width + 10, phone_height + 20), (30, 30, 30, 255))
        # Paste screenshot with small border
        phone_frame.paste(screenshot, (5, 10))
        
        # Position the phone mockup (adjust based on presenter image)
        # Place it where the phone would naturally be held
        phone_x = 280  # Approximate position
        phone_y = 250
        
        # Paste with alpha
        canvas.paste(phone_frame, (phone_x, phone_y), phone_frame)
    
    return np.array(canvas)


def create_split_frame(presenter_path: str, screenshot_path: str) -> np.ndarray:
    """Create a split-screen frame with presenter on right and screenshot on left"""
    # Create canvas
    canvas = Image.new('RGB', (1280, 720), (240, 235, 230))  # Beige background
    
    # Load and resize screenshot for left side (60% of width)
    if screenshot_path and os.path.exists(screenshot_path):
        screenshot = Image.open(screenshot_path)
        # Screenshot takes 60% width, full height with padding
        screenshot = screenshot.resize((700, 500), Image.LANCZOS)
        
        # Add slight shadow effect
        shadow = Image.new('RGBA', (710, 510), (0, 0, 0, 50))
        canvas.paste(shadow, (30, 115))
        canvas.paste(screenshot, (25, 110))
    
    # Load presenter for right side
    presenter = Image.open(presenter_path)
    
    # Crop presenter to focus on face/upper body (right 40% of canvas)
    p_width, p_height = presenter.size
    
    # Crop to upper right portion of the image
    crop_left = int(p_width * 0.3)
    crop_top = 0
    crop_right = p_width
    crop_bottom = int(p_height * 0.85)
    
    presenter_crop = presenter.crop((crop_left, crop_top, crop_right, crop_bottom))
    
    # Resize to fit right side
    target_height = 720
    aspect = presenter_crop.width / presenter_crop.height
    target_width = int(target_height * aspect)
    
    if target_width > 500:
        target_width = 500
        target_height = int(500 / aspect)
    
    presenter_crop = presenter_crop.resize((target_width, target_height), Image.LANCZOS)
    
    # Position presenter on right side
    p_x = 1280 - target_width - 20
    p_y = (720 - target_height) // 2
    canvas.paste(presenter_crop, (p_x, p_y))
    
    return np.array(canvas)


def create_pip_video(audio_path: str, output_path: str, screenshot_paths: list, presenter_path: str):
    """Create video with presenter and rotating screenshots"""
    
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration
    
    duration_per_screenshot = total_duration / len(screenshot_paths) if screenshot_paths else total_duration
    
    clips = []
    
    for i, spath in enumerate(screenshot_paths):
        # Alternate between full presenter and split view
        if i % 2 == 0:
            # Split view with screenshot
            frame = create_split_frame(presenter_path, spath)
        else:
            # Full presenter with phone mockup
            frame = create_presenter_frame(presenter_path, spath)
        
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
    """Regenerate all tutorial videos with the main presenter"""
    
    SUBTITLES_DIR.mkdir(parents=True, exist_ok=True)
    
    for tutorial in TUTORIALS:
        video_id = tutorial['id']
        print(f"\n{'='*60}")
        print(f"Regenerating: {tutorial['title']}")
        print(f"{'='*60}")
        
        voice = VOICES.get(video_id, "nova")
        
        print(f"  Using main presenter image")
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
        
        # Create video with presenter and screenshots
        print("  Creating video with presenter and screenshots...")
        create_pip_video(
            audio_path=str(audio_path),
            output_path=str(video_path),
            screenshot_paths=screenshot_paths,
            presenter_path=MAIN_PRESENTER
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
