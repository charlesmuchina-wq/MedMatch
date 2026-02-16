"""
Regenerate Tutorial Videos with Correct Region-Appropriate Avatars
Uses D-ID hosted images for API compatibility
"""

import asyncio
import httpx
import os
from pathlib import Path
from datetime import datetime

# D-ID hosted avatar images (uploaded to D-ID S3)
AVATAR_URLS = {
    "african_female": "s3://d-id-images-prod/google-oauth2|110650682359864325385/img_2HWpRuSJNvN0UPRWHJ9VR/african_female.jpg",
    "asian_female": "s3://d-id-images-prod/google-oauth2|110650682359864325385/img_5TQIKszNfYDUiLzO5agSm/asian_female.jpg",
    "south_asian_female": "s3://d-id-images-prod/google-oauth2|110650682359864325385/img_zK2i4CKEgIs23tYACFRRg/south_asian_female.jpg",
    "middle_eastern_female": "s3://d-id-images-prod/google-oauth2|110650682359864325385/img_E0mRHqyb_5v8Lwq6zSHXi/middle_eastern_female.jpg",
}

OUTPUT_DIR = Path("/app/backend/static/videos/tutorials")

# Videos to regenerate with their configs (shortened scripts for faster generation)
VIDEOS_TO_REGENERATE = {
    # African languages
    "ha": {
        "script": "Barka da zuwa MedMatch-AI KARAU! Dandamalinmu na AI yana taimaka muku samun aikin kirki a kimiyyar rayuwa. Fara yau kyauta!",
        "voice_id": "en-NG-EzinneNeural",
        "avatar": "african_female"
    },
    "zu": {
        "script": "Siyakwamukela ku-MedMatch-AI KARAU! Inkundla yethu ye-AI ikusiza ukuthola umsebenzi omuhle. Qala namuhla mahhala!",
        "voice_id": "zu-ZA-ThandileNeural", 
        "avatar": "african_female"
    },
    "af": {
        "script": "Welkom by MedMatch-AI KARAU! Ons AI-platform help jou om die beste werk te vind. Begin vandag gratis!",
        "voice_id": "af-ZA-AdriNeural",
        "avatar": "african_female"
    },
    # Asian languages
    "ja": {
        "script": "MedMatch-AI KARAUへようこそ！AIプラットフォームで最高の仕事を見つけましょう。今すぐ始めましょう！",
        "voice_id": "ja-JP-NanamiNeural",
        "avatar": "asian_female"
    },
    "zh": {
        "script": "欢迎使用MedMatch-AI KARAU！AI平台帮助您找到最好的工作。立即开始！",
        "voice_id": "zh-CN-XiaoxiaoNeural",
        "avatar": "asian_female"
    },
    "ko": {
        "script": "MedMatch-AI KARAU에 오신 것을 환영합니다! AI로 최고의 일자리를 찾으세요. 지금 시작하세요!",
        "voice_id": "ko-KR-SunHiNeural",
        "avatar": "asian_female"
    },
    "vi": {
        "script": "Chào mừng đến với MedMatch-AI KARAU! AI giúp bạn tìm công việc tốt nhất. Bắt đầu ngay!",
        "voice_id": "vi-VN-HoaiMyNeural",
        "avatar": "asian_female"
    },
    # South Asian
    "hi": {
        "script": "MedMatch-AI KARAU में स्वागत है! AI से सबसे अच्छी नौकरी खोजें। आज ही शुरू करें!",
        "voice_id": "hi-IN-SwaraNeural",
        "avatar": "south_asian_female"
    },
    # Middle Eastern
    "ar": {
        "script": "مرحباً بكم في MedMatch-AI KARAU! منصتنا تساعدكم في إيجاد أفضل الوظائف. ابدأ اليوم!",
        "voice_id": "ar-EG-SalmaNeural",
        "avatar": "middle_eastern_female"
    },
    "tr": {
        "script": "MedMatch-AI KARAU'ya hoş geldiniz! AI platformumuz en iyi işi bulmanıza yardımcı olur. Başlayın!",
        "voice_id": "tr-TR-EmelNeural",
        "avatar": "middle_eastern_female"
    },
}

async def regenerate_video(client, lang_code, config, headers):
    """Regenerate a single video with correct avatar."""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Regenerating: {lang_code.upper()}")
    print(f"  Avatar: {config['avatar']}")
    
    payload = {
        "source_url": AVATAR_URLS[config['avatar']],
        "script": {
            "type": "text",
            "input": config['script'],
            "provider": {
                "type": "microsoft",
                "voice_id": config['voice_id']
            }
        },
        "config": {
            "fluent": True,
            "pad_audio": 0.5,
            "stitch": True
        }
    }
    
    try:
        # Create talk
        resp = await client.post(
            'https://api.d-id.com/talks',
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if resp.status_code not in [200, 201]:
            print(f"  ❌ Failed: {resp.status_code}")
            return False
        
        talk_id = resp.json().get('id')
        print(f"  Talk: {talk_id}")
        
        # Poll for completion
        for i in range(45):
            await asyncio.sleep(2)
            status_resp = await client.get(
                f'https://api.d-id.com/talks/{talk_id}',
                headers=headers,
                timeout=30
            )
            if status_resp.status_code == 200:
                data = status_resp.json()
                status = data.get('status')
                if status == 'done':
                    video_url = data.get('result_url')
                    # Download video
                    video_resp = await client.get(video_url, timeout=120)
                    if video_resp.status_code == 200:
                        output_path = OUTPUT_DIR / f"tutorial_{lang_code}.mp4"
                        if output_path.exists():
                            backup = OUTPUT_DIR / f"tutorial_{lang_code}_old.mp4"
                            output_path.rename(backup)
                        output_path.write_bytes(video_resp.content)
                        print(f"  ✅ Downloaded: {output_path.name}")
                        return True
                elif status == 'error':
                    print(f"  ❌ Error: {data.get('error')}")
                    return False
        
        print("  ❌ Timeout")
        return False
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return False

async def main():
    api_key = os.environ.get('D_ID_API_KEY')
    if not api_key:
        print("ERROR: D_ID_API_KEY not set")
        return
    
    print("="*50)
    print("D-ID VIDEO REGENERATION")
    print(f"Videos: {len(VIDEOS_TO_REGENERATE)}")
    print("="*50)
    
    headers = {
        "Authorization": f"Basic {api_key}",
        "Content-Type": "application/json"
    }
    
    results = {"success": [], "failed": []}
    
    async with httpx.AsyncClient() as client:
        for lang_code, config in VIDEOS_TO_REGENERATE.items():
            success = await regenerate_video(client, lang_code, config, headers)
            if success:
                results["success"].append(lang_code)
            else:
                results["failed"].append(lang_code)
            await asyncio.sleep(2)
    
    print("\n" + "="*50)
    print("COMPLETE")
    print(f"✅ Success: {', '.join(results['success'])}")
    print(f"❌ Failed: {', '.join(results['failed'])}")
    
    # Save results
    with open('/tmp/regen_results.txt', 'w') as f:
        f.write(f"Success: {results['success']}\n")
        f.write(f"Failed: {results['failed']}\n")

if __name__ == "__main__":
    asyncio.run(main())
