#!/usr/bin/env python3
"""
Download D-ID generated diverse videos and update tutorial files
"""
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

async def check_and_download(talk_id, lang_code, gender):
    """Check video status and download if ready."""
    print(f"Checking {lang_code} ({talk_id})...", end=" ")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{D_ID_BASE_URL}/talks/{talk_id}",
            headers=get_headers(),
            timeout=30.0
        )
        
        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            result_url = data.get("result_url")
            
            if status == "done" and result_url:
                print(f"READY - Downloading...")
                # Download the video
                video_response = await client.get(result_url, timeout=120.0)
                if video_response.status_code == 200:
                    # Save as the new diverse video
                    output_path = VIDEOS_DIR / f"tutorial_{lang_code}.mp4"
                    
                    # Backup original if exists
                    backup_path = VIDEOS_DIR / f"tutorial_{lang_code}_old.mp4"
                    if output_path.exists() and not backup_path.exists():
                        output_path.rename(backup_path)
                    
                    with open(output_path, "wb") as f:
                        f.write(video_response.content)
                    
                    print(f"  ✅ Downloaded: {output_path.name} ({gender})")
                    return {"lang": lang_code, "status": "downloaded", "gender": gender}
            elif status == "started" or status == "created":
                print(f"PENDING ({status})")
                return {"lang": lang_code, "status": "pending"}
            else:
                print(f"ERROR: {status}")
                return {"lang": lang_code, "status": "error", "error": status}
        else:
            print(f"API Error: {response.status_code}")
            return {"lang": lang_code, "status": "error"}

async def main():
    print("=" * 50)
    print("Downloading Diverse D-ID Videos")
    print("=" * 50)
    
    # Load created videos
    with open("/tmp/diverse_videos_result.json", "r") as f:
        videos = json.load(f)
    
    results = []
    for v in videos:
        if v.get("status") == "created":
            result = await check_and_download(v["talk_id"], v["lang"], v["gender"])
            results.append(result)
            await asyncio.sleep(1)
    
    # Summary
    downloaded = [r for r in results if r.get("status") == "downloaded"]
    pending = [r for r in results if r.get("status") == "pending"]
    errors = [r for r in results if r.get("status") == "error"]
    
    print("\n" + "=" * 50)
    print("Download Summary")
    print("=" * 50)
    print(f"Downloaded: {len(downloaded)}")
    print(f"Pending: {len(pending)}")
    print(f"Errors: {len(errors)}")
    
    if downloaded:
        print("\nDownloaded videos:")
        males = [d for d in downloaded if d.get("gender") == "male"]
        females = [d for d in downloaded if d.get("gender") == "female"]
        print(f"  Male presenters: {', '.join([d['lang'] for d in males])}")
        print(f"  Female presenters: {', '.join([d['lang'] for d in females])}")
    
    if pending:
        print(f"\nStill processing: {', '.join([p['lang'] for p in pending])}")
        print("Run this script again in 1-2 minutes.")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())
