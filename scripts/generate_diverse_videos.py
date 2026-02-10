#!/usr/bin/env python3
"""
Generate diverse AI avatar videos using D-ID API
Uses different male/female presenters to match language regions
"""
import os
import httpx
import asyncio
import json
from pathlib import Path

# D-ID Configuration
D_ID_API_KEY = os.environ.get("D_ID_API_KEY", "")
D_ID_BASE_URL = "https://api.d-id.com"

# Video storage
VIDEOS_DIR = Path("/app/backend/static/videos/tutorials")

# Diverse presenter/voice mapping - alternating male/female
# Groups by region with culturally appropriate presenters
DIVERSE_VIDEOS = {
    # Western Europe - Male presenters
    "de": {
        "voice_id": "de-DE-ConradNeural",  # Male German voice
        "gender": "male",
        "region": "Europe",
        "script": "Willkommen bei MedMatch! Lassen Sie mich Ihnen zeigen, wie Sie beginnen. Laden Sie Ihren Lebenslauf hoch und unsere KI findet passende Jobs aus über 15 spezialisierten Jobbörsen. Erhalten Sie Vertrauenswerte für jede Stelle, bereiten Sie sich mit KI-Coaching auf Interviews vor und erhalten Sie Benachrichtigungen für Jobs in Ihrer Nähe. Verfügbar auf Web, iOS, Android und Desktop. MedMatch — Intelligentes Recruiting. Starten Sie noch heute!"
    },
    "fr": {
        "voice_id": "fr-FR-HenriNeural",  # Male French voice
        "gender": "male", 
        "region": "Europe",
        "script": "Bienvenue sur MedMatch! Laissez-moi vous montrer comment commencer. Téléchargez votre CV et notre IA trouvera des emplois correspondants sur plus de 15 sites spécialisés. Obtenez des scores de confiance pour chaque poste, préparez vos entretiens avec un coaching IA et recevez des alertes pour les emplois près de chez vous. Disponible sur Web, iOS, Android et bureau. MedMatch — Recrutement intelligent. Commencez aujourd'hui!"
    },
    # Southern Europe - Female presenters
    "es": {
        "voice_id": "es-ES-ElviraNeural",  # Female Spanish voice
        "gender": "female",
        "region": "Europe",
        "script": "¡Bienvenido a MedMatch! Permíteme mostrarte cómo empezar. Sube tu currículum y nuestra IA encontrará trabajos coincidentes de más de 15 bolsas de trabajo especializadas. Obtén puntuaciones de confianza para cada puesto, prepárate para entrevistas con coaching de IA y recibe alertas de empleos cerca de ti. Disponible en Web, iOS, Android y escritorio. MedMatch — Contratación inteligente. ¡Empieza hoy!"
    },
    "it": {
        "voice_id": "it-IT-DiegoNeural",  # Male Italian voice
        "gender": "male",
        "region": "Europe",
        "script": "Benvenuto su MedMatch! Lascia che ti mostri come iniziare. Carica il tuo curriculum e la nostra IA troverà lavori corrispondenti da oltre 15 bacheche specializzate. Ottieni punteggi di fiducia per ogni posizione, preparati per i colloqui con il coaching IA e ricevi avvisi per lavori vicino a te. Disponibile su Web, iOS, Android e desktop. MedMatch — Assunzioni intelligenti. Inizia oggi!"
    },
    # Eastern Europe - Female presenters
    "pl": {
        "voice_id": "pl-PL-ZofiaNeural",  # Female Polish voice
        "gender": "female",
        "region": "Europe",
        "script": "Witamy w MedMatch! Pozwól, że pokażę ci, jak zacząć. Prześlij swoje CV, a nasza sztuczna inteligencja znajdzie pasujące oferty pracy z ponad 15 specjalistycznych portali. Otrzymuj oceny zaufania dla każdego stanowiska, przygotuj się do rozmów z coachingiem AI i otrzymuj powiadomienia o ofertach w pobliżu. Dostępne na Web, iOS, Android i komputerze. MedMatch — Inteligentna rekrutacja. Zacznij już dziś!"
    },
    "ru": {
        "voice_id": "ru-RU-DmitryNeural",  # Male Russian voice
        "gender": "male",
        "region": "Europe",
        "script": "Добро пожаловать в MedMatch! Позвольте показать вам, как начать. Загрузите резюме, и наш ИИ найдёт подходящие вакансии с более чем 15 специализированных сайтов. Получайте оценки доверия для каждой позиции, готовьтесь к собеседованиям с помощью ИИ-коучинга и получайте уведомления о вакансиях рядом. Доступно на Web, iOS, Android и десктопе. MedMatch — Умный рекрутинг. Начните сегодня!"
    },
    # Nordic - Female presenter
    "sv": {
        "voice_id": "sv-SE-SofieNeural",  # Female Swedish voice
        "gender": "female",
        "region": "Nordic",
        "script": "Välkommen till MedMatch! Låt mig visa dig hur du kommer igång. Ladda upp ditt CV så hittar vår AI matchande jobb från över 15 specialiserade jobbsajter. Få förtroendepoengen för varje position, förbered dig för intervjuer med AI-coachning och få aviseringar om jobb nära dig. Tillgänglig på webb, iOS, Android och dator. MedMatch — Smart rekrytering. Börja idag!"
    },
    "nl": {
        "voice_id": "nl-NL-MaartenNeural",  # Male Dutch voice
        "gender": "male",
        "region": "Europe",
        "script": "Welkom bij MedMatch! Laat me je laten zien hoe je begint. Upload je CV en onze AI vindt overeenkomende banen van meer dan 15 gespecialiseerde vacaturesites. Krijg vertrouwensscores voor elke positie, bereid je voor op sollicitatiegesprekken met AI-coaching en ontvang meldingen voor banen bij jou in de buurt. Beschikbaar op web, iOS, Android en desktop. MedMatch — Slimme werving. Begin vandaag!"
    },
    # Asia - Diverse presenters
    "ja": {
        "voice_id": "ja-JP-KeitaNeural",  # Male Japanese voice
        "gender": "male",
        "region": "Asia",
        "script": "MedMatchへようこそ！始め方をご説明します。履歴書をアップロードすると、AIが15以上の専門求人サイトからマッチする仕事を見つけます。各求人の信頼スコアを取得し、AIコーチングで面接準備をし、近くの求人アラートを受け取れます。Web、iOS、Android、デスクトップで利用可能。MedMatch — スマートな採用。今日から始めましょう！"
    },
    "zh": {
        "voice_id": "zh-CN-YunxiNeural",  # Male Chinese voice
        "gender": "male",
        "region": "Asia",
        "script": "欢迎来到MedMatch！让我向您展示如何开始。上传您的简历，我们的AI将从15多个专业招聘网站为您找到匹配的工作。获取每个职位的信任分数，通过AI辅导准备面试，并接收附近工作的提醒。支持网页、iOS、Android和桌面版。MedMatch — 智能招聘。立即开始！"
    },
    "ko": {
        "voice_id": "ko-KR-InJoonNeural",  # Male Korean voice
        "gender": "male",
        "region": "Asia",
        "script": "MedMatch에 오신 것을 환영합니다! 시작하는 방법을 알려드리겠습니다. 이력서를 업로드하면 AI가 15개 이상의 전문 채용 사이트에서 맞춤 일자리를 찾아드립니다. 각 포지션의 신뢰 점수를 확인하고, AI 코칭으로 면접을 준비하며, 근처 일자리 알림을 받으세요. 웹, iOS, Android, 데스크톱에서 이용 가능. MedMatch — 스마트 채용. 오늘 시작하세요!"
    },
    "vi": {
        "voice_id": "vi-VN-NamMinhNeural",  # Male Vietnamese voice
        "gender": "male",
        "region": "Asia",
        "script": "Chào mừng đến với MedMatch! Hãy để tôi chỉ cho bạn cách bắt đầu. Tải lên CV của bạn và AI của chúng tôi sẽ tìm việc làm phù hợp từ hơn 15 trang tuyển dụng chuyên ngành. Nhận điểm tin cậy cho mỗi vị trí, chuẩn bị phỏng vấn với huấn luyện AI và nhận thông báo về việc làm gần bạn. Có sẵn trên Web, iOS, Android và máy tính. MedMatch — Tuyển dụng thông minh. Bắt đầu ngay hôm nay!"
    },
    "hi": {
        "voice_id": "hi-IN-MadhurNeural",  # Male Hindi voice
        "gender": "male",
        "region": "South Asia",
        "script": "MedMatch में आपका स्वागत है! मुझे आपको बताने दें कि कैसे शुरू करें। अपना रिज्यूमे अपलोड करें और हमारा AI 15+ विशेष जॉब बोर्ड से मेल खाने वाली नौकरियां खोजेगा। हर पद के लिए ट्रस्ट स्कोर पाएं, AI कोचिंग के साथ इंटरव्यू की तैयारी करें और आस-पास की नौकरियों के अलर्ट प्राप्त करें। वेब, iOS, Android और डेस्कटॉप पर उपलब्ध। MedMatch — स्मार्ट भर्ती। आज ही शुरू करें!"
    },
    # Middle East - Female presenter
    "ar": {
        "voice_id": "ar-SA-ZariyahNeural",  # Female Arabic voice
        "gender": "female",
        "region": "Middle East",
        "script": "مرحباً بك في MedMatch! دعني أريك كيف تبدأ. ارفع سيرتك الذاتية وسيجد الذكاء الاصطناعي لدينا وظائف مطابقة من أكثر من 15 موقع توظيف متخصص. احصل على درجات الثقة لكل منصب، وجهز للمقابلات مع التدريب بالذكاء الاصطناعي، واستلم إشعارات للوظائف القريبة منك. متاح على الويب وiOS وأندرويد وسطح المكتب. MedMatch — توظيف ذكي. ابدأ اليوم!"
    },
    # Turkey - Female presenter
    "tr": {
        "voice_id": "tr-TR-EmelNeural",  # Female Turkish voice
        "gender": "female",
        "region": "Middle East",
        "script": "MedMatch'e hoş geldiniz! Size nasıl başlayacağınızı göstereyim. CV'nizi yükleyin ve yapay zekamız 15'ten fazla özel iş ilanı sitesinden eşleşen işleri bulacak. Her pozisyon için güven puanları alın, yapay zeka koçluğu ile mülakata hazırlanın ve yakınınızdaki işler için bildirimler alın. Web, iOS, Android ve masaüstünde mevcuttur. MedMatch — Akıllı İşe Alım. Bugün başlayın!"
    },
    # Portuguese - Female presenter
    "pt": {
        "voice_id": "pt-BR-FranciscaNeural",  # Female Portuguese voice
        "gender": "female",
        "region": "South America",
        "script": "Bem-vindo ao MedMatch! Deixe-me mostrar como começar. Faça upload do seu currículo e nossa IA encontrará vagas compatíveis em mais de 15 sites de emprego especializados. Obtenha pontuações de confiança para cada vaga, prepare-se para entrevistas com coaching de IA e receba alertas de vagas perto de você. Disponível na Web, iOS, Android e desktop. MedMatch — Recrutamento inteligente. Comece hoje!"
    }
}

def get_headers():
    return {
        "Authorization": f"Basic {D_ID_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

async def create_diverse_video(lang_code, config):
    """Create a video with the D-ID API using diverse presenters."""
    print(f"\n=== Creating {lang_code.upper()} video ({config['gender']}) ===")
    
    # Use Josh (male) or Amy (female) based on gender
    presenter_mapping = {
        "male": "josh-jp4VsYVnXa",
        "female": "amy-jcwCkr1grs"
    }
    
    payload = {
        "presenter_id": presenter_mapping[config["gender"]],
        "script": {
            "type": "text",
            "input": config["script"],
            "provider": {
                "type": "microsoft",
                "voice_id": config["voice_id"]
            }
        },
        "config": {
            "fluent": True,
            "pad_audio": 0.5,
            "stitch": True
        }
    }
    
    async with httpx.AsyncClient() as client:
        # Create the talk
        response = await client.post(
            f"{D_ID_BASE_URL}/talks",
            headers=get_headers(),
            json=payload,
            timeout=60.0
        )
        
        if response.status_code == 201:
            data = response.json()
            talk_id = data.get("id")
            print(f"  Created talk: {talk_id}")
            return {"lang": lang_code, "talk_id": talk_id, "status": "created", "gender": config["gender"]}
        else:
            print(f"  Error: {response.status_code} - {response.text[:200]}")
            return {"lang": lang_code, "error": response.text[:200], "status": "failed"}

async def check_video_status(talk_id):
    """Check if video is ready."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{D_ID_BASE_URL}/talks/{talk_id}",
            headers=get_headers(),
            timeout=30.0
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("status"), data.get("result_url")
    return None, None

async def download_video(url, lang_code):
    """Download the video to local storage."""
    output_path = VIDEOS_DIR / f"tutorial_{lang_code}_diverse.mp4"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=120.0)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"  Downloaded: {output_path}")
            return str(output_path)
    return None

async def generate_all_diverse_videos():
    """Generate diverse videos for all languages."""
    print("=" * 50)
    print("Diverse AI Avatar Video Generation")
    print("=" * 50)
    
    results = []
    
    # Create videos in batches to respect rate limits
    for lang_code, config in DIVERSE_VIDEOS.items():
        try:
            result = await create_diverse_video(lang_code, config)
            results.append(result)
            await asyncio.sleep(2)  # Rate limit
        except Exception as e:
            print(f"  Error: {e}")
            results.append({"lang": lang_code, "error": str(e), "status": "failed"})
    
    # Summary
    print("\n" + "=" * 50)
    print("Generation Summary")
    print("=" * 50)
    
    created = [r for r in results if r.get("status") == "created"]
    failed = [r for r in results if r.get("status") == "failed"]
    
    print(f"Created: {len(created)}")
    print(f"Failed: {len(failed)}")
    
    if created:
        print("\nCreated videos:")
        for r in created:
            print(f"  - {r['lang']}: {r['talk_id']} ({r['gender']})")
    
    if failed:
        print("\nFailed videos:")
        for r in failed:
            print(f"  - {r['lang']}: {r.get('error', 'Unknown error')[:50]}")
    
    # Save results
    with open("/tmp/diverse_videos_result.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nResults saved to /tmp/diverse_videos_result.json")
    return results

if __name__ == "__main__":
    asyncio.run(generate_all_diverse_videos())
