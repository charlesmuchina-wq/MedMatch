"""
Create FAQ Video: AI Compliance & Data Ownership Rights
Pacific Islander/Hawaiian woman presenter
At least 40 seconds
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
PRESENTER_HAWAIIAN = "/app/frontend/public/images/presenter_hawaiian.jpeg"


async def generate_voice(text: str, output_path: str, voice: str = "nova") -> str:
    """Generate voice narration using OpenAI TTS"""
    tts = OpenAITextToSpeech(api_key=os.environ['EMERGENT_LLM_KEY'])
    
    audio_bytes = await tts.generate_speech(
        text=text,
        model="tts-1-hd",
        voice=voice,
        speed=0.95  # Slightly slower for clarity on complex topics
    )
    
    with open(output_path, "wb") as f:
        f.write(audio_bytes)
    
    return output_path


def create_circular_presenter(image_path: str, size=200):
    """Create circular presenter image with border"""
    img = Image.open(image_path)
    img = img.resize((size, size), Image.LANCZOS)
    
    mask = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    
    output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    output.paste(img, (0, 0))
    output.putalpha(mask)
    
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


# FAQ Script - AI Compliance & Data Ownership (40+ seconds)
FAQ_VIDEO = {
    "id": "04_faq_ai_compliance",
    "title": "FAQs: AI Compliance & Your Data Rights",
    "presenter": PRESENTER_HAWAIIAN,
    "voice": "nova",  # Female voice
    "screenshots": ["01_dashboard.png", "03_resume.png", "01_dashboard.png", "03_resume.png"],
    "script": """Aloha! Let me answer some frequently asked questions about AI and your data rights at MedMatch.

First, how does MedMatch use AI? Our AI analyzes your resume and job preferences to provide personalized matches. It does not make hiring decisions. Employers always make the final choice.

What about AI compliance? MedMatch follows responsible AI principles. Our algorithms are designed to be fair and unbiased. We regularly audit our systems to prevent discrimination based on age, gender, ethnicity, or other protected characteristics.

Do you own your data? Absolutely yes. You retain full ownership of all information you provide. Your resume, profile, and application history belong to you.

Can you delete your data? Yes, at any time. Visit your account settings to download a copy of your data or request complete deletion. We comply with GDPR and other data protection regulations.

Is your information shared? Never without your consent. We do not sell your personal data to third parties. Recruiters only see what you choose to make visible.

How is AI used in matching? Our AI looks at your skills, experience, and preferences to suggest relevant jobs. You control the matching by setting your own filters and criteria.

Thank you for trusting MedMatch with your career journey. Your privacy and rights are always our priority. Mahalo!"""
}


async def generate_faq_video():
    """Generate the FAQ video"""
    tutorial = FAQ_VIDEO
    
    print(f"\n{'='*50}")
    print(f"Generating: {tutorial['title']}")
    print(f"Presenter: Pacific Islander/Hawaiian woman")
    print(f"Target: 40+ seconds")
    print(f"{'='*50}")
    
    audio_path = VIDEOS_DIR / f"{tutorial['id']}_audio.mp3"
    video_path = VIDEOS_DIR / f"{tutorial['id']}.mp4"
    
    screenshot_paths = [str(SCREENS_DIR / s) for s in tutorial['screenshots']]
    
    for sp in screenshot_paths:
        if os.path.exists(sp):
            print(f"  ✓ Found: {os.path.basename(sp)}")
    
    # Generate voice
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
    
    # Check duration
    from moviepy import VideoFileClip
    clip = VideoFileClip(str(video_path))
    duration = clip.duration
    clip.close()
    
    print(f"\n✓ {tutorial['title']} complete!")
    print(f"  Duration: {duration:.1f} seconds")
    
    return duration


if __name__ == "__main__":
    asyncio.run(generate_faq_video())
