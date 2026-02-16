"""
Regenerate Tutorial Videos with Correct Region-Appropriate Avatars
This script regenerates all D-ID tutorial videos using the LANGUAGE_CONFIG mapping
to ensure proper avatar/region matching.

Run with: python regenerate_regional_tutorials.py
"""

import asyncio
import os
import sys
import httpx
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, '/app/backend')

from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

from services.did_avatar_service import DIDService, LANGUAGE_CONFIG, AVATAR_IMAGES

# Tutorial scripts for each language
TUTORIAL_SCRIPTS = {
    # African Languages - NEED CORRECT AVATARS
    "sw": """Karibu MedMatch-AI KARAU! Jukwaa letu la AI linakusaidia kupata kazi bora katika sayansi ya uhai. Pakia wasifu wako, pata mechi bora, na jiandae kwa mahojiano na AI. Tumia lugha 25 tofauti. Anza leo bila malipo!""",
    
    "ha": """Barka da zuwa MedMatch-AI KARAU! Dandamalinmu na AI yana taimaka muku samun aikin kirki a kimiyyar rayuwa. Saka bayanan ku, sami daidaitawa, kuma ku shirya don tambayoyi tare da AI. Akwai harsuna 25. Fara yau kyauta!""",
    
    "zu": """Siyakwamukela ku-MedMatch-AI KARAU! Inkundla yethu ye-AI ikusiza ukuthola umsebenzi omuhle kwisayensi yempilo. Layisha i-resume yakho, thola ukufaniswa okuhle, futhi ulungele inhlolokhono ne-AI. Izilimi ezingu-25 ziyatholakala. Qala namuhla mahhala!""",
    
    "af": """Welkom by MedMatch-AI KARAU! Ons AI-platform help jou om die beste werk in lewenswetenskappe te vind. Laai jou CV op, kry die beste pasmaats, en berei voor vir onderhoude met AI. 25 tale beskikbaar. Begin vandag gratis!""",
    
    # Asian Languages - NEED CORRECT AVATARS
    "ja": """MedMatch-AI KARAUへようこそ！私たちのAIプラットフォームは、ライフサイエンス分野で最高の仕事を見つけるお手伝いをします。履歴書をアップロードし、最適なマッチングを取得し、AIで面接準備をしましょう。25言語対応。今すぐ無料で始めましょう！""",
    
    "zh": """欢迎使用MedMatch-AI KARAU！我们的AI平台帮助您在生命科学领域找到最好的工作。上传您的简历，获取最佳匹配，并使用AI准备面试。支持25种语言。立即免费开始！""",
    
    "ko": """MedMatch-AI KARAU에 오신 것을 환영합니다! AI 플랫폼이 생명과학 분야에서 최고의 일자리를 찾도록 도와드립니다. 이력서를 업로드하고, 최적의 매칭을 받고, AI로 면접을 준비하세요. 25개 언어 지원. 지금 무료로 시작하세요!""",
    
    "vi": """Chào mừng đến với MedMatch-AI KARAU! Nền tảng AI của chúng tôi giúp bạn tìm công việc tốt nhất trong khoa học đời sống. Tải lên CV, nhận kết quả phù hợp tốt nhất và chuẩn bị phỏng vấn với AI. 25 ngôn ngữ. Bắt đầu miễn phí ngay hôm nay!""",
    
    # South Asian
    "hi": """MedMatch-AI KARAU में आपका स्वागत है! हमारा AI प्लेटफॉर्म आपको जीवन विज्ञान में सबसे अच्छी नौकरी खोजने में मदद करता है। अपना रिज्यूमे अपलोड करें, सर्वश्रेष्ठ मिलान प्राप्त करें और AI के साथ साक्षात्कार की तैयारी करें। 25 भाषाएं उपलब्ध। आज ही मुफ्त में शुरू करें!""",
    
    # Middle Eastern
    "ar": """مرحباً بكم في MedMatch-AI KARAU! منصتنا الذكية تساعدكم في إيجاد أفضل الوظائف في علوم الحياة. ارفع سيرتك الذاتية، احصل على أفضل المطابقات، واستعد للمقابلات مع الذكاء الاصطناعي. 25 لغة متاحة. ابدأ مجاناً اليوم!""",
    
    "tr": """MedMatch-AI KARAU'ya hoş geldiniz! AI platformumuz yaşam bilimlerinde en iyi işi bulmanıza yardımcı olur. CV'nizi yükleyin, en iyi eşleşmeleri alın ve AI ile mülakata hazırlanın. 25 dil mevcut. Bugün ücretsiz başlayın!""",
}

# Video output directory
OUTPUT_DIR = Path("/app/backend/static/videos/tutorials")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

async def regenerate_video(service: DIDService, lang_code: str, script: str):
    """Regenerate a single tutorial video with correct avatar."""
    config = service.get_language_config(lang_code)
    
    print(f"\n{'='*60}")
    print(f"Regenerating: {lang_code.upper()}")
    print(f"Region: {config['region']}")
    print(f"Avatar: {config['avatar_type']}")
    print(f"Avatar URL: {config['avatar_url'][:50]}...")
    print(f"Voice: {config['voice_name']} ({config['voice_id']})")
    print(f"{'='*60}")
    
    result = await service.create_tutorial_video(
        language_code=lang_code,
        script=script,
        title=f"MedMatch-AI KARAU Tutorial ({lang_code})"
    )
    
    if result.get("success"):
        talk_id = result.get("talk_id")
        video_url = result.get("video_url")
        
        print(f"✅ SUCCESS: Talk ID = {talk_id}")
        print(f"   Video URL: {video_url}")
        
        # Download the video
        if video_url:
            output_path = OUTPUT_DIR / f"tutorial_{lang_code}.mp4"
            output_path_new = OUTPUT_DIR / f"tutorial_{lang_code}_new.mp4"
            
            # Backup old video
            if output_path.exists():
                import shutil
                backup_path = OUTPUT_DIR / f"tutorial_{lang_code}_old.mp4"
                shutil.move(str(output_path), str(backup_path))
                print(f"   Backed up old video to: {backup_path.name}")
            
            # Download new video
            async with httpx.AsyncClient() as client:
                response = await client.get(video_url, timeout=120.0)
                if response.status_code == 200:
                    output_path_new.write_bytes(response.content)
                    # Rename to final path
                    output_path_new.rename(output_path)
                    print(f"   Downloaded to: {output_path}")
                else:
                    print(f"   ⚠️ Failed to download video: HTTP {response.status_code}")
        
        return {"success": True, "lang": lang_code, "talk_id": talk_id}
    else:
        print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
        if result.get('detail'):
            print(f"   Detail: {result['detail'][:200]}")
        return {"success": False, "lang": lang_code, "error": result.get('error')}

async def main():
    """Main function to regenerate all mismatched videos."""
    print("\n" + "="*70)
    print("D-ID TUTORIAL VIDEO REGENERATION")
    print("Regenerating videos with correct region-appropriate avatars")
    print("="*70)
    
    # Initialize service
    service = DIDService()
    
    # Check credits
    credits = await service.get_credits()
    remaining = credits.get('remaining', 0)
    print(f"\n💳 D-ID Credits Available: {remaining}")
    
    if remaining < len(TUTORIAL_SCRIPTS) * 15:  # Estimate ~15 credits per video
        print(f"⚠️ Warning: May not have enough credits for all {len(TUTORIAL_SCRIPTS)} videos")
        print("   Proceeding anyway...")
    
    # Languages to regenerate
    languages_to_regenerate = list(TUTORIAL_SCRIPTS.keys())
    print(f"\n📝 Videos to regenerate: {', '.join(languages_to_regenerate)}")
    print(f"   Total: {len(languages_to_regenerate)} videos")
    
    # Confirm
    print("\n" + "-"*70)
    print("Starting regeneration in 3 seconds...")
    await asyncio.sleep(3)
    
    # Regenerate each video
    results = []
    for lang_code in languages_to_regenerate:
        script = TUTORIAL_SCRIPTS[lang_code]
        result = await regenerate_video(service, lang_code, script)
        results.append(result)
        
        # Wait between videos to avoid rate limiting
        print("\n⏳ Waiting 5 seconds before next video...")
        await asyncio.sleep(5)
    
    # Summary
    print("\n" + "="*70)
    print("REGENERATION COMPLETE")
    print("="*70)
    
    success_count = sum(1 for r in results if r.get('success'))
    fail_count = len(results) - success_count
    
    print(f"\n✅ Successful: {success_count}")
    print(f"❌ Failed: {fail_count}")
    
    if fail_count > 0:
        print("\nFailed languages:")
        for r in results:
            if not r.get('success'):
                print(f"  - {r['lang']}: {r.get('error', 'Unknown error')}")
    
    # Check remaining credits
    credits = await service.get_credits()
    print(f"\n💳 Credits remaining: {credits.get('remaining', 'unknown')}")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())
