"""
CAPA Video Regeneration Script
Regenerates all tutorial videos with proper database tracking

Run with: python3 /app/backend/services/capa_video_regen.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
env_path = Path('/app/backend/.env')
load_dotenv(env_path)

sys.path.insert(0, '/app/backend')

from services.video_asset_manager import video_asset_manager, LANGUAGE_AVATAR_CONFIG

async def regenerate_all():
    """Regenerate all videos with proper tracking."""
    print("=" * 60)
    print("CAPA VIDEO REGENERATION - Starting Full Rebuild")
    print("=" * 60)
    
    await video_asset_manager.initialize()
    
    # Get all languages
    languages = list(LANGUAGE_AVATAR_CONFIG.keys())
    print(f"\nTotal languages to regenerate: {len(languages)}")
    print(f"Languages: {', '.join(languages)}")
    print()
    
    results = {
        "success": [],
        "failed": []
    }
    
    for i, lang in enumerate(languages, 1):
        config = video_asset_manager.get_language_config(lang)
        print(f"[{i}/{len(languages)}] Generating {lang} ({config['region']})...")
        print(f"    Avatar: {config['avatar_type']}")
        print(f"    Voice: {config['voice_name']}")
        
        result = await video_asset_manager.generate_video(lang)
        
        if result.get("success"):
            print(f"    ✅ SUCCESS - {result.get('file_size', 0) / 1024 / 1024:.2f} MB")
            results["success"].append(lang)
        else:
            print(f"    ❌ FAILED - {result.get('error', 'Unknown error')}")
            results["failed"].append({"lang": lang, "error": result.get("error")})
        
        print()
        # Small delay to avoid rate limiting
        await asyncio.sleep(2)
    
    # Summary
    print("=" * 60)
    print("REGENERATION COMPLETE")
    print("=" * 60)
    print(f"✅ Successful: {len(results['success'])} / {len(languages)}")
    print(f"❌ Failed: {len(results['failed'])} / {len(languages)}")
    
    if results["failed"]:
        print("\nFailed languages:")
        for f in results["failed"]:
            print(f"  - {f['lang']}: {f['error']}")
    
    return results

if __name__ == "__main__":
    asyncio.run(regenerate_all())
