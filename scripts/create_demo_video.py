#!/usr/bin/env python3
"""
MedMatch Demo Video Creator
Creates an animated GIF/video demonstrating the full job seeker and recruiter flows.
"""

import asyncio
import os
from datetime import datetime
from playwright.async_api import async_playwright

# Configuration
BASE_URL = "https://hirelifesci.preview.emergentagent.com"
OUTPUT_DIR = "/tmp/medmatch_demo"
FRAME_DELAY = 800  # ms between frames

# Test credentials
JOB_SEEKER = {"email": "demo_jobseeker@test.com", "password": "demo123"}
RECRUITER = {"email": "demo_recruiter@test.com", "password": "demo123"}


async def capture_frame(page, name, frame_num):
    """Capture a frame for the demo"""
    path = f"{OUTPUT_DIR}/{frame_num:03d}_{name}.png"
    await page.screenshot(path=path, full_page=False)
    print(f"  📸 Captured: {name}")
    return path


async def demo_job_seeker_flow(page):
    """Demonstrate the job seeker experience"""
    frames = []
    
    print("\n🔵 JOB SEEKER FLOW")
    print("=" * 50)
    
    # 1. Landing page
    await page.goto(BASE_URL)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(1000)
    frames.append(await capture_frame(page, "01_login_page", 1))
    
    # 2. Enter credentials
    await page.fill('input[type="email"]', JOB_SEEKER["email"])
    await page.fill('input[type="password"]', JOB_SEEKER["password"])
    await page.wait_for_timeout(500)
    frames.append(await capture_frame(page, "02_credentials_entered", 2))
    
    # 3. Click sign in
    await page.click('button:has-text("Sign In")', force=True)
    await page.wait_for_timeout(3000)
    frames.append(await capture_frame(page, "03_dashboard", 3))
    
    # 4. Navigate to Job Search
    await page.click('text=Job Search', force=True)
    await page.wait_for_timeout(2000)
    frames.append(await capture_frame(page, "04_job_search", 4))
    
    # 5. Search for a job
    search_input = page.locator('input[placeholder*="Job title"]').first
    if await search_input.is_visible():
        await search_input.fill("Software Engineer")
        await page.wait_for_timeout(500)
        frames.append(await capture_frame(page, "05_search_query", 5))
    
    # 6. Show "Why matched?" feature
    why_matched = page.locator('text=Why matched?').first
    if await why_matched.is_visible():
        await why_matched.click(force=True)
        await page.wait_for_timeout(1500)
        frames.append(await capture_frame(page, "06_why_matched", 6))
        # Close modal
        close_btn = page.locator('[data-testid="close-button"], button:has-text("Close"), .dialog-close').first
        if await close_btn.is_visible():
            await close_btn.click(force=True)
            await page.wait_for_timeout(500)
    
    # 7. Navigate to Membership page
    await page.goto(f"{BASE_URL}/membership")
    await page.wait_for_timeout(2000)
    frames.append(await capture_frame(page, "07_membership", 7))
    
    # 8. Scroll to show pricing
    await page.evaluate("window.scrollBy(0, 300)")
    await page.wait_for_timeout(1000)
    frames.append(await capture_frame(page, "08_pricing", 8))
    
    return frames


async def demo_recruiter_flow(page):
    """Demonstrate the recruiter experience"""
    frames = []
    
    print("\n🟢 RECRUITER FLOW")
    print("=" * 50)
    
    # 1. Go to login
    await page.goto(BASE_URL)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(1000)
    
    # 2. Login as recruiter
    await page.fill('input[type="email"]', RECRUITER["email"])
    await page.fill('input[type="password"]', RECRUITER["password"])
    await page.wait_for_timeout(500)
    await page.click('button:has-text("Sign In")', force=True)
    await page.wait_for_timeout(3000)
    frames.append(await capture_frame(page, "09_recruiter_dashboard", 9))
    
    # 3. Show candidate search (with verification notice)
    search_candidates = page.locator('text=Search Candidates').first
    if await search_candidates.is_visible():
        await search_candidates.click(force=True)
        await page.wait_for_timeout(2000)
        frames.append(await capture_frame(page, "10_candidate_search", 10))
    
    # 4. Show job postings
    await page.click('text=My Job Postings', force=True)
    await page.wait_for_timeout(2000)
    frames.append(await capture_frame(page, "11_job_postings", 11))
    
    # 5. Show privacy settings
    privacy_link = page.locator('text=Privacy').first
    if await privacy_link.is_visible():
        await privacy_link.click(force=True)
        await page.wait_for_timeout(2000)
        frames.append(await capture_frame(page, "12_privacy", 12))
    
    return frames


async def create_gif(frames, output_path):
    """Create animated GIF from frames"""
    import imageio.v2 as imageio
    
    print("\n🎬 Creating GIF...")
    images = []
    for frame_path in frames:
        if os.path.exists(frame_path):
            images.append(imageio.imread(frame_path))
    
    if images:
        # Duration in seconds per frame
        imageio.mimsave(output_path, images, duration=1.5, loop=0)
        print(f"✅ GIF created: {output_path}")
        return output_path
    return None


async def main():
    """Main demo creation function"""
    print("🚀 MedMatch Demo Video Creator")
    print("=" * 50)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    all_frames = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1
        )
        page = await context.new_page()
        
        try:
            # Capture job seeker flow
            job_seeker_frames = await demo_job_seeker_flow(page)
            all_frames.extend(job_seeker_frames)
            
            # Clear session for recruiter
            await context.clear_cookies()
            
            # Capture recruiter flow
            recruiter_frames = await demo_recruiter_flow(page)
            all_frames.extend(recruiter_frames)
            
        finally:
            await browser.close()
    
    # Create GIF
    gif_path = f"{OUTPUT_DIR}/medmatch_demo.gif"
    await create_gif(all_frames, gif_path)
    
    # Create summary
    print("\n" + "=" * 50)
    print("📊 DEMO SUMMARY")
    print("=" * 50)
    print(f"Total frames captured: {len(all_frames)}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"GIF location: {gif_path}")
    print(f"Individual frames: {OUTPUT_DIR}/*.png")
    
    return gif_path


if __name__ == "__main__":
    asyncio.run(main())
