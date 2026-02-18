"""
Fresh Video Regeneration with New Avatar Images
Feb 18, 2026 - Complete rebuild with verified professional headshots
"""

import asyncio
import httpx
import os
from pathlib import Path
from datetime import datetime

# Fresh avatar images - Pexels/Unsplash professional headshots (NO hands blocking faces)
FRESH_AVATAR_URLS = {
    "african_female": "https://images.pexels.com/photos/3727462/pexels-photo-3727462.jpeg?auto=compress&cs=tinysrgb&w=1024",
    "asian_female": "https://images.pexels.com/photos/6572210/pexels-photo-6572210.jpeg?auto=compress&cs=tinysrgb&w=1024",
    "south_asian_female": "https://images.pexels.com/photos/4057039/pexels-photo-4057039.jpeg?auto=compress&cs=tinysrgb&w=1024",
    "middle_eastern_female": "https://images.unsplash.com/photo-1600600457585-570c2eb88b89?w=1024&h=1024&fit=crop",
    "latina_female": "https://images.pexels.com/photos/10041243/pexels-photo-10041243.jpeg?auto=compress&cs=tinysrgb&w=1024",
    "european_female": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=1024&h=1024&fit=crop",
    "japanese_female": "https://images.unsplash.com/photo-1624091844772-554661d10173?w=1024&h=1024&fit=crop",
}

OUTPUT_DIR = Path("/app/backend/static/videos/tutorials")

# All videos to regenerate with complete scripts
VIDEOS_CONFIG = {
    # African languages
    "sw": {
        "script": "Karibu MedMatch-AI KARAU! Jukwaa letu la AI linakusaidia kupata kazi bora katika sayansi ya uhai. Anza leo bure na uboreshe kazi yako!",
        "voice_id": "sw-KE-ZuriNeural",
        "avatar": "african_female",
        "title": "Swahili"
    },
    "af": {
        "script": "Welkom by MedMatch-AI KARAU! Ons KI-platform help jou om die beste werk in lewenswetenskappe te vind. Begin vandag gratis!",
        "voice_id": "af-ZA-AdriNeural",
        "avatar": "african_female",
        "title": "Afrikaans"
    },
    "ha": {
        "script": "Barka da zuwa MedMatch-AI KARAU! Dandamalinmu na AI yana taimaka muku samun aikin kirki a kimiyyar rayuwa. Fara yau kyauta!",
        "voice_id": "en-NG-EzinneNeural",
        "avatar": "african_female",
        "title": "Hausa"
    },
    "zu": {
        "script": "Siyakwamukela ku-MedMatch-AI KARAU! Inkundla yethu ye-AI ikusiza ukuthola umsebenzi omuhle kwezesayensi yokuphila. Qala namuhla mahhala!",
        "voice_id": "zu-ZA-ThandileNeural",
        "avatar": "african_female",
        "title": "Zulu"
    },
    
    # Asian languages
    "ja": {
        "script": "MedMatch-AI KARAUへようこそ！AIプラットフォームでライフサイエンス分野の最高の仕事を見つけましょう。今すぐ無料で始めましょう！",
        "voice_id": "ja-JP-NanamiNeural",
        "avatar": "japanese_female",
        "title": "Japanese"
    },
    "zh": {
        "script": "欢迎使用MedMatch-AI KARAU！我们的AI平台帮助您在生命科学领域找到最好的工作。立即免费开始！",
        "voice_id": "zh-CN-XiaoxiaoNeural",
        "avatar": "asian_female",
        "title": "Chinese"
    },
    "ko": {
        "script": "MedMatch-AI KARAU에 오신 것을 환영합니다! AI 플랫폼으로 생명과학 분야 최고의 일자리를 찾으세요. 지금 무료로 시작하세요!",
        "voice_id": "ko-KR-SunHiNeural",
        "avatar": "asian_female",
        "title": "Korean"
    },
    "vi": {
        "script": "Chào mừng đến với MedMatch-AI KARAU! Nền tảng AI giúp bạn tìm công việc tốt nhất trong khoa học đời sống. Bắt đầu miễn phí ngay!",
        "voice_id": "vi-VN-HoaiMyNeural",
        "avatar": "asian_female",
        "title": "Vietnamese"
    },
    
    # South Asian
    "hi": {
        "script": "MedMatch-AI KARAU में स्वागत है! हमारा AI प्लेटफॉर्म जीवन विज्ञान में सबसे अच्छी नौकरी खोजने में मदद करता है। आज ही मुफ्त में शुरू करें!",
        "voice_id": "hi-IN-SwaraNeural",
        "avatar": "south_asian_female",
        "title": "Hindi"
    },
    
    # Middle Eastern
    "ar": {
        "script": "مرحباً بكم في MedMatch-AI KARAU! منصتنا الذكية تساعدكم في إيجاد أفضل الوظائف في علوم الحياة. ابدأوا اليوم مجاناً!",
        "voice_id": "ar-EG-SalmaNeural",
        "avatar": "middle_eastern_female",
        "title": "Arabic"
    },
    "tr": {
        "script": "MedMatch-AI KARAU'ya hoş geldiniz! AI platformumuz yaşam bilimlerinde en iyi işi bulmanıza yardımcı olur. Bugün ücretsiz başlayın!",
        "voice_id": "tr-TR-EmelNeural",
        "avatar": "middle_eastern_female",
        "title": "Turkish"
    },
    
    # Latin American
    "pt": {
        "script": "Bem-vindo ao MedMatch-AI KARAU! Nossa plataforma de IA ajuda você a encontrar os melhores empregos em ciências da vida. Comece hoje gratuitamente!",
        "voice_id": "pt-BR-FranciscaNeural",
        "avatar": "latina_female",
        "title": "Portuguese"
    },
    "es": {
        "script": "¡Bienvenido a MedMatch-AI KARAU! Nuestra plataforma de IA te ayuda a encontrar los mejores trabajos en ciencias de la vida. ¡Empieza hoy gratis!",
        "voice_id": "es-ES-ElviraNeural",
        "avatar": "latina_female",
        "title": "Spanish"
    },
    
    # European languages
    "de": {
        "script": "Willkommen bei MedMatch-AI KARAU! Unsere KI-Plattform hilft Ihnen, die besten Jobs in den Lebenswissenschaften zu finden. Starten Sie heute kostenlos!",
        "voice_id": "de-DE-KatjaNeural",
        "avatar": "european_female",
        "title": "German"
    },
    "fr": {
        "script": "Bienvenue sur MedMatch-AI KARAU! Notre plateforme IA vous aide à trouver les meilleurs emplois en sciences de la vie. Commencez gratuitement!",
        "voice_id": "fr-FR-DeniseNeural",
        "avatar": "european_female",
        "title": "French"
    },
    "it": {
        "script": "Benvenuto su MedMatch-AI KARAU! La nostra piattaforma AI ti aiuta a trovare i migliori lavori nelle scienze della vita. Inizia oggi gratuitamente!",
        "voice_id": "it-IT-ElsaNeural",
        "avatar": "european_female",
        "title": "Italian"
    },
}


async def upload_image_to_did(client, image_url, headers):
    """Upload an image to D-ID and get the hosted URL."""
    print(f"  Uploading image to D-ID: {image_url[:60]}...")
    
    try:
        # Download image first
        img_resp = await client.get(image_url, timeout=30)
        if img_resp.status_code != 200:
            print(f"  ❌ Failed to download image: {img_resp.status_code}")
            return None
        
        # Upload to D-ID
        files = {'image': ('avatar.jpg', img_resp.content, 'image/jpeg')}
        upload_resp = await client.post(
            'https://api.d-id.com/images',
            headers={'Authorization': headers['Authorization']},
            files=files,
            timeout=60
        )
        
        if upload_resp.status_code in [200, 201]:
            data = upload_resp.json()
            did_url = data.get('url')
            print(f"  ✅ Uploaded: {did_url}")
            return did_url
        else:
            print(f"  ❌ Upload failed: {upload_resp.status_code} - {upload_resp.text}")
            return None
            
    except Exception as e:
        print(f"  ❌ Upload error: {e}")
        return None


async def regenerate_video(client, lang_code, config, headers, avatar_cache):
    """Regenerate a single video with fresh avatar."""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Regenerating: {lang_code.upper()} ({config['title']})")
    
    avatar_type = config['avatar']
    
    # Get or upload avatar
    if avatar_type not in avatar_cache:
        source_url = FRESH_AVATAR_URLS.get(avatar_type)
        if not source_url:
            print(f"  ❌ No source URL for avatar: {avatar_type}")
            return False
        
        did_url = await upload_image_to_did(client, source_url, headers)
        if not did_url:
            print(f"  ❌ Failed to upload avatar")
            return False
        avatar_cache[avatar_type] = did_url
    
    source_url = avatar_cache[avatar_type]
    print(f"  Avatar URL: {source_url[:60]}...")
    
    payload = {
        "source_url": source_url,
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
            print(f"  ❌ Create talk failed: {resp.status_code}")
            print(f"     Response: {resp.text[:200]}")
            return False
        
        talk_id = resp.json().get('id')
        print(f"  Talk ID: {talk_id}")
        
        # Poll for completion (max 90 seconds)
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
                    print(f"  Downloading video...")
                    
                    # Download video
                    video_resp = await client.get(video_url, timeout=120)
                    if video_resp.status_code == 200:
                        output_path = OUTPUT_DIR / f"tutorial_{lang_code}.mp4"
                        
                        # Backup existing
                        if output_path.exists():
                            backup = OUTPUT_DIR / f"tutorial_{lang_code}_backup.mp4"
                            output_path.rename(backup)
                        
                        output_path.write_bytes(video_resp.content)
                        size_mb = len(video_resp.content) / (1024 * 1024)
                        print(f"  ✅ Saved: {output_path.name} ({size_mb:.2f} MB)")
                        return True
                    else:
                        print(f"  ❌ Download failed: {video_resp.status_code}")
                        return False
                        
                elif status == 'error':
                    error_msg = data.get('error', {})
                    print(f"  ❌ D-ID Error: {error_msg}")
                    return False
                    
                elif i % 5 == 0:
                    print(f"  ... Status: {status} (waiting)")
        
        print(f"  ❌ Timeout waiting for video")
        return False
        
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return False


async def main():
    """Main regeneration function."""
    api_key = os.environ.get('D_ID_API_KEY')
    if not api_key:
        print("ERROR: D_ID_API_KEY not set in environment")
        return
    
    print("=" * 60)
    print("Fresh Video Regeneration - Feb 18, 2026")
    print("=" * 60)
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Videos to regenerate: {len(VIDEOS_CONFIG)}")
    print()
    
    headers = {
        'Authorization': f'Basic {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Cache for uploaded avatars (to avoid re-uploading same image)
    avatar_cache = {}
    
    results = {"success": [], "failed": []}
    
    async with httpx.AsyncClient() as client:
        for lang_code, config in VIDEOS_CONFIG.items():
            success = await regenerate_video(client, lang_code, config, headers, avatar_cache)
            if success:
                results["success"].append(lang_code)
            else:
                results["failed"].append(lang_code)
            
            # Small delay between videos
            await asyncio.sleep(1)
    
    # Summary
    print("\n" + "=" * 60)
    print("REGENERATION COMPLETE")
    print("=" * 60)
    print(f"✅ Success: {len(results['success'])} - {', '.join(results['success'])}")
    print(f"❌ Failed: {len(results['failed'])} - {', '.join(results['failed'])}")
    
    # Cleanup backup files if successful
    if not results['failed']:
        print("\nCleaning up backup files...")
        for backup in OUTPUT_DIR.glob("*_backup.mp4"):
            backup.unlink()
            print(f"  Removed: {backup.name}")


if __name__ == "__main__":
    asyncio.run(main())
