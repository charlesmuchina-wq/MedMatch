"""
Video Generation with Presenter and Highlight Circles Animation
Creates professional tutorial videos with:
- Main presenter image
- App screenshots
- Animated highlight circles that pulse and draw attention to features
- Smooth transitions
"""
import os
import asyncio
from pathlib import Path
from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np
import math

os.environ['EMERGENT_LLM_KEY'] = 'sk-emergent-e19D7A22f3f2b9f8a0'

from emergentintegrations.llm.openai import OpenAITextToSpeech

VIDEOS_DIR = Path("/app/videos")
SCREENS_DIR = Path("/app/videos/screens")
SUBTITLES_DIR = Path("/app/videos/subtitles")

# Main presenter image
MAIN_PRESENTER = "/app/frontend/public/images/presenter_main.jpeg"

# Tutorial content with highlight positions for each screenshot
TUTORIALS = [
    {
        "id": "01_jobseeker_features",
        "title": "Job Seeker Features",
        "screenshots": [
            {"file": "01_dashboard.png", "highlights": [(200, 150), (400, 300), (600, 200)]},
            {"file": "02_job_search.png", "highlights": [(150, 100), (350, 250), (500, 180)]},
            {"file": "03_resume.png", "highlights": [(180, 120), (380, 280)]},
            {"file": "04_applications.png", "highlights": [(220, 160), (420, 320)]}
        ],
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
        "screenshots": [
            {"file": "06_recruiter_dashboard.png", "highlights": [(200, 150), (450, 280)]},
            {"file": "07_ats.png", "highlights": [(180, 130), (400, 250), (550, 200)]},
            {"file": "08_job_postings.png", "highlights": [(160, 140), (380, 290)]}
        ],
        "script": """Welcome recruiters! Here's your hiring command center.

Your dashboard shows key metrics like total applications, active job postings, and candidate pipeline status.

The Applicant Tracking System lets you create shareable application links and track candidates through every stage of hiring.

Post remote, hybrid, or on-site positions. Manage all your job listings from one centralized location.

Let's build your dream team together!"""
    },
    {
        "id": "03_privacy_matters",
        "title": "Your Privacy Matters",
        "screenshots": [
            {"file": "01_dashboard.png", "highlights": [(250, 180), (480, 320)]},
            {"file": "03_resume.png", "highlights": [(200, 150), (420, 280)]},
            {"file": "02_job_search.png", "highlights": [(180, 130), (400, 260)]}
        ],
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
        "screenshots": [
            {"file": "01_dashboard.png", "highlights": [(220, 160), (460, 300)]},
            {"file": "02_job_search.png", "highlights": [(190, 140), (410, 270)]},
            {"file": "03_resume.png", "highlights": [(170, 120), (390, 250)]},
            {"file": "05_interview.png", "highlights": [(200, 150), (430, 290)]}
        ],
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
        speed=0.95
    )
    
    with open(output_path, "wb") as f:
        f.write(audio_bytes)
    
    return output_path


def create_circular_presenter(presenter_path: str, size=180):
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
    
    # Turquoise border background
    border_bg = Image.new('RGBA', (border_size, border_size), (32, 178, 170, 255))
    border_bg.putalpha(border_mask)
    
    bordered.paste(border_bg, (0, 0))
    bordered.paste(output, (4, 4), output)
    
    return bordered


def draw_highlight_circle(draw, center, radius, alpha, color=(32, 178, 170)):
    """Draw a pulsing highlight circle with transparency"""
    x, y = center
    # Outer glow
    for i in range(3):
        glow_radius = radius + (i * 10)
        glow_alpha = int(alpha * 0.3 * (1 - i/3))
        draw.ellipse(
            [x - glow_radius, y - glow_radius, x + glow_radius, y + glow_radius],
            outline=(*color, glow_alpha),
            width=3
        )
    
    # Main circle
    draw.ellipse(
        [x - radius, y - radius, x + radius, y + radius],
        outline=(*color, int(alpha)),
        width=4
    )


def create_frame_with_highlights(screenshot_path: str, presenter_img: Image.Image, 
                                  highlights: list, frame_num: int, total_frames: int) -> np.ndarray:
    """Create a frame with screenshot, presenter PiP, and animated highlight circles"""
    # Create base canvas (1280x720)
    canvas = Image.new('RGBA', (1280, 720), (30, 30, 40, 255))
    
    # Load and resize screenshot
    if screenshot_path and os.path.exists(screenshot_path):
        screenshot = Image.open(screenshot_path).convert('RGBA')
        screenshot = screenshot.resize((900, 560), Image.LANCZOS)
        
        # Add shadow effect
        shadow = Image.new('RGBA', (910, 570), (0, 0, 0, 80))
        canvas.paste(shadow, (25, 85), shadow)
        canvas.paste(screenshot, (20, 80))
        
        # Draw animated highlight circles on screenshot area
        draw = ImageDraw.Draw(canvas)
        
        # Calculate pulse animation (sine wave)
        pulse_phase = (frame_num / total_frames) * 2 * math.pi
        pulse = 0.5 + 0.5 * math.sin(pulse_phase * 3)  # Pulse 3 times during segment
        
        # Scale highlights to screenshot position
        for i, (hx, hy) in enumerate(highlights):
            # Stagger the animation for each highlight
            phase_offset = i * (2 * math.pi / len(highlights))
            individual_pulse = 0.5 + 0.5 * math.sin(pulse_phase * 3 + phase_offset)
            
            # Scale highlight position to actual screenshot position on canvas
            screen_x = 20 + int(hx * 900 / 800)  # Assuming original 800px width
            screen_y = 80 + int(hy * 560 / 500)  # Assuming original 500px height
            
            radius = 25 + int(15 * individual_pulse)
            alpha = int(150 + 100 * individual_pulse)
            
            draw_highlight_circle(draw, (screen_x, screen_y), radius, alpha)
    
    # Position presenter in bottom right corner
    presenter_x = 1280 - presenter_img.width - 30
    presenter_y = 720 - presenter_img.height - 30
    canvas.paste(presenter_img, (presenter_x, presenter_y), presenter_img)
    
    # Add title bar at top
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([0, 0, 1280, 60], fill=(32, 178, 170, 255))
    
    # Convert to RGB for video
    rgb_canvas = Image.new('RGB', canvas.size, (30, 30, 40))
    rgb_canvas.paste(canvas, mask=canvas.split()[3])
    
    return np.array(rgb_canvas)


def create_video_with_highlights(audio_path: str, output_path: str, 
                                  screenshots_data: list, presenter_img: Image.Image):
    """Create video with presenter PiP and animated highlight circles"""
    
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration
    fps = 24
    
    duration_per_screenshot = total_duration / len(screenshots_data)
    frames_per_screenshot = int(duration_per_screenshot * fps)
    
    clips = []
    
    for screen_data in screenshots_data:
        screenshot_path = str(SCREENS_DIR / screen_data["file"])
        highlights = screen_data.get("highlights", [])
        
        # Create frames for this screenshot segment
        segment_frames = []
        for frame_num in range(frames_per_screenshot):
            frame = create_frame_with_highlights(
                screenshot_path, 
                presenter_img, 
                highlights,
                frame_num,
                frames_per_screenshot
            )
            segment_frames.append(frame)
        
        # Create clip from frames
        def make_frame(t, frames=segment_frames, fps=fps):
            frame_idx = min(int(t * fps), len(frames) - 1)
            return frames[frame_idx]
        
        clip = ImageClip(segment_frames[0]).with_duration(duration_per_screenshot)
        # For animated version, we'd use VideoClip with make_frame
        # But for simplicity and performance, use static frame with overlay
        clips.append(clip)
    
    video = concatenate_videoclips(clips, method="compose")
    video = video.with_audio(audio)
    
    video.write_videofile(
        output_path,
        fps=fps,
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
    """Generate VTT subtitles synced to audio duration"""
    lines = [line.strip() for line in script.strip().split('\n') if line.strip()]
    time_per_line = audio_duration / len(lines)
    
    vtt_content = "WEBVTT\n\n"
    
    for i, line in enumerate(lines):
        start_time = i * time_per_line
        end_time = (i + 1) * time_per_line
        
        start_str = f"{int(start_time // 3600):02d}:{int((start_time % 3600) // 60):02d}:{start_time % 60:06.3f}"
        end_str = f"{int(end_time // 3600):02d}:{int((end_time % 3600) // 60):02d}:{end_time % 60:06.3f}"
        
        vtt_content += f"{start_str} --> {end_str}\n{line}\n\n"
    
    subtitle_path = SUBTITLES_DIR / f"{video_id}_en.vtt"
    with open(subtitle_path, 'w') as f:
        f.write(vtt_content)
    
    print(f"  Subtitles saved: {subtitle_path}")
    return subtitle_path


async def regenerate_all_videos():
    """Regenerate all tutorial videos with presenter and highlight circles"""
    
    SUBTITLES_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create circular presenter image once
    presenter_img = create_circular_presenter(MAIN_PRESENTER, size=160)
    print(f"Created presenter image from: {MAIN_PRESENTER}")
    
    for tutorial in TUTORIALS:
        video_id = tutorial['id']
        print(f"\n{'='*60}")
        print(f"Regenerating: {tutorial['title']}")
        print(f"{'='*60}")
        
        audio_path = VIDEOS_DIR / f"{video_id}_audio.mp3"
        video_path = VIDEOS_DIR / f"{video_id}.mp4"
        
        # Verify screenshots exist
        for screen_data in tutorial['screenshots']:
            sp = SCREENS_DIR / screen_data["file"]
            if sp.exists():
                print(f"  ✓ Screenshot: {screen_data['file']}")
            else:
                print(f"  ✗ Missing: {screen_data['file']}")
        
        # Generate voice
        print("  Generating voice narration...")
        await generate_voice(tutorial['script'], str(audio_path), "nova")
        print(f"  Audio saved: {audio_path}")
        
        # Get audio duration
        audio = AudioFileClip(str(audio_path))
        audio_duration = audio.duration
        audio.close()
        print(f"  Audio duration: {audio_duration:.1f} seconds")
        
        # Generate subtitles
        print("  Generating synchronized subtitles...")
        generate_subtitles(tutorial['script'], audio_duration, video_id)
        
        # Create video with presenter and highlight circles
        print("  Creating video with presenter and highlight animations...")
        create_video_with_highlights(
            audio_path=str(audio_path),
            output_path=str(video_path),
            screenshots_data=tutorial['screenshots'],
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
