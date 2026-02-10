#!/usr/bin/env python3
"""Download D-ID generated videos"""
import os
import httpx
import asyncio
import json
from pathlib import Path

D_ID_API_KEY = os.environ.get("D_ID_API_KEY", "")
D_ID_BASE_URL = "https://api.d-id.com"
VIDEOS_DIR = Path("/app/backend/static/videos/tutorials")

def get_headers():
    return {
        "Authorization": f"Basic {D_ID_API_KEY}",
        "Content-Type": "application/json"
    }

async def check_and_download(clip_id, output_name):
    """Check clip status and download if ready."""
    print(f"Checking {output_name}...", end=" ")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{D_ID_BASE_URL}/clips/{clip_id}",
            headers=get_headers(),
            timeout=30.0
        )
        
        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            result_url = data.get("result_url")
            
            if status == "done" and result_url:
                print(f"READY - Downloading...")
                video_response = await client.get(result_url, timeout=120.0)
                if video_response.status_code == 200:
                    output_path = VIDEOS_DIR / f"{output_name}.mp4"
                    with open(output_path, "wb") as f:
                        f.write(video_response.content)
                    print(f"  ✅ Downloaded: {output_path.name}")
                    return True
            elif status in ["started", "created"]:
                print(f"PENDING ({status})")
            else:
                print(f"Status: {status}")
        else:
            print(f"Error: {response.status_code}")
    return False

async def main():
    print("=" * 50)
    print("Downloading D-ID Videos")
    print("=" * 50)
    
    videos = [
        ("clp_9mRIXF_1MDdbop8Z47tJs", "tutorial_sw"),
        ("clp_RhxaLxQCdpGvfxOk-W1ar", "tutorial_af"),
        ("clp_408OyvpPr53pZoqdIk5tJ", "tutorial_ha"),
        ("clp_tl_bu9AVhD4p7Hv1K9SJR", "tutorial_zu"),
        ("clp_64uphXb3CwGsDzKhknz91", "tutorial_xh"),
        ("clp_iwKjW6Vs8B5NAfX49f_sn", "role_recruiter"),
    ]
    
    downloaded = 0
    for clip_id, output_name in videos:
        if await check_and_download(clip_id, output_name):
            downloaded += 1
        await asyncio.sleep(1)
    
    print(f"\nDownloaded: {downloaded}/{len(videos)}")

if __name__ == "__main__":
    asyncio.run(main())
