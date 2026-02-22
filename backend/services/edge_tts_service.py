"""
Edge TTS Service - Free Multi-Language Text-to-Speech

Uses Microsoft's neural TTS voices via edge-tts library.
100+ voices across 40+ languages, no API key required.

Created: Feb 21, 2026
"""

import edge_tts
import asyncio
import os
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Audio storage directory
AUDIO_DIR = Path("/app/backend/static/audio/tutorials")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Language to Voice mapping - Female neural voices for consistency
LANGUAGE_VOICES = {
    # English variants
    "en": "en-US-AriaNeural",
    "en-US": "en-US-AriaNeural",
    "en-GB": "en-GB-SoniaNeural",
    
    # European languages
    "es": "es-ES-ElviraNeural",
    "fr": "fr-FR-DeniseNeural",
    "de": "de-DE-KatjaNeural",
    "it": "it-IT-ElsaNeural",
    "pt": "pt-BR-FranciscaNeural",
    "nl": "nl-NL-ColetteNeural",
    "pl": "pl-PL-ZofiaNeural",
    "sv": "sv-SE-SofieNeural",
    "ru": "ru-RU-SvetlanaNeural",
    
    # Asian languages
    "ja": "ja-JP-NanamiNeural",
    "zh": "zh-CN-XiaoxiaoNeural",
    "ko": "ko-KR-SunHiNeural",
    "vi": "vi-VN-HoaiMyNeural",
    "hi": "hi-IN-SwaraNeural",
    "th": "th-TH-PremwadeeNeural",
    "id": "id-ID-GadisNeural",
    
    # Middle Eastern languages
    "ar": "ar-EG-SalmaNeural",
    "tr": "tr-TR-EmelNeural",
    "he": "he-IL-HilaNeural",
    
    # African languages
    "sw": "sw-KE-ZuriNeural",
    "af": "af-ZA-AdriNeural",
    
    # Other languages
    "tl": "fil-PH-BlessicaNeural",  # Filipino/Tagalog
}

# Tutorial scripts in different languages
TUTORIAL_SCRIPTS = {
    "01_jobseeker_features": {
        "en": """Welcome to MedMatch-AI KARAU! As a job seeker, you have access to powerful AI tools.
Upload your resume and our AI will parse your skills automatically.
Search across 15 job boards at once. Get interview preparation with real-time feedback.
Your success predictor shows your chances before you apply.
Track all your applications in one place. Start your career journey today!""",
        
        "es": """¡Bienvenido a MedMatch-AI KARAU! Como buscador de empleo, tienes acceso a potentes herramientas de IA.
Sube tu currículum y nuestra IA analizará tus habilidades automáticamente.
Busca en 15 bolsas de trabajo a la vez. Prepárate para entrevistas con retroalimentación en tiempo real.
El predictor de éxito te muestra tus posibilidades antes de aplicar.
Rastrea todas tus aplicaciones en un solo lugar. ¡Comienza tu viaje profesional hoy!""",
        
        "fr": """Bienvenue sur MedMatch-AI KARAU! En tant que chercheur d'emploi, vous avez accès à des outils IA puissants.
Téléchargez votre CV et notre IA analysera vos compétences automatiquement.
Recherchez sur 15 sites d'emploi à la fois. Préparez vos entretiens avec des retours en temps réel.
Le prédicteur de succès vous montre vos chances avant de postuler.
Suivez toutes vos candidatures en un seul endroit. Commencez votre parcours professionnel aujourd'hui!""",
        
        "de": """Willkommen bei MedMatch-AI KARAU! Als Jobsuchender haben Sie Zugang zu leistungsstarken KI-Tools.
Laden Sie Ihren Lebenslauf hoch und unsere KI analysiert Ihre Fähigkeiten automatisch.
Suchen Sie auf 15 Jobbörsen gleichzeitig. Bereiten Sie sich auf Interviews mit Echtzeit-Feedback vor.
Der Erfolgsprädiktor zeigt Ihre Chancen vor der Bewerbung.
Verfolgen Sie alle Ihre Bewerbungen an einem Ort. Starten Sie heute Ihre Karrierereise!""",
        
        "ja": """MedMatch-AI KARAUへようこそ！求職者として、強力なAIツールにアクセスできます。
履歴書をアップロードすると、AIが自動的にスキルを分析します。
15の求人サイトを一度に検索。リアルタイムフィードバックで面接準備。
成功予測機能で応募前にチャンスを確認できます。
すべての応募を一か所で管理。今日からキャリアの旅を始めましょう！""",
        
        "zh": """欢迎使用MedMatch-AI KARAU！作为求职者，您可以使用强大的AI工具。
上传您的简历，我们的AI将自动分析您的技能。
同时搜索15个招聘网站。通过实时反馈准备面试。
成功预测器在申请前显示您的机会。
在一个地方跟踪所有申请。今天就开始您的职业之旅！""",
        
        "ko": """MedMatch-AI KARAU에 오신 것을 환영합니다! 구직자로서 강력한 AI 도구를 사용할 수 있습니다.
이력서를 업로드하면 AI가 자동으로 기술을 분석합니다.
15개 구직 사이트를 한 번에 검색하세요. 실시간 피드백으로 면접을 준비하세요.
성공 예측기가 지원 전에 가능성을 보여줍니다.
모든 지원서를 한 곳에서 추적하세요. 오늘 커리어 여정을 시작하세요!""",
        
        "ar": """مرحبًا بك في MedMatch-AI KARAU! كباحث عن عمل، لديك إمكانية الوصول إلى أدوات ذكاء اصطناعي قوية.
قم بتحميل سيرتك الذاتية وسيقوم الذكاء الاصطناعي بتحليل مهاراتك تلقائيًا.
ابحث في 15 موقع توظيف في وقت واحد. استعد للمقابلات مع تعليقات فورية.
يُظهر لك متنبئ النجاح فرصك قبل التقديم.
تتبع جميع طلباتك في مكان واحد. ابدأ رحلتك المهنية اليوم!""",
        
        "hi": """MedMatch-AI KARAU में आपका स्वागत है! नौकरी चाहने वाले के रूप में, आपके पास शक्तिशाली AI उपकरण उपलब्ध हैं।
अपना रिज्यूमे अपलोड करें और हमारा AI स्वचालित रूप से आपके कौशल का विश्लेषण करेगा।
एक साथ 15 जॉब बोर्ड पर खोजें। रीयल-टाइम फीडबैक के साथ इंटरव्यू की तैयारी करें।
सफलता भविष्यवक्ता आवेदन करने से पहले आपकी संभावनाएं दिखाता है।
अपने सभी आवेदनों को एक जगह ट्रैक करें। आज ही अपनी करियर यात्रा शुरू करें!""",
        
        "ru": """Добро пожаловать в MedMatch-AI KARAU! Как соискатель, вы имеете доступ к мощным инструментам ИИ.
Загрузите резюме, и наш ИИ автоматически проанализирует ваши навыки.
Ищите на 15 сайтах вакансий одновременно. Готовьтесь к собеседованиям с обратной связью в реальном времени.
Предиктор успеха показывает ваши шансы перед подачей заявки.
Отслеживайте все заявки в одном месте. Начните свой карьерный путь сегодня!""",
        
        "it": """Benvenuto su MedMatch-AI KARAU! Come cercatore di lavoro, hai accesso a potenti strumenti AI.
Carica il tuo CV e la nostra AI analizzerà automaticamente le tue competenze.
Cerca su 15 siti di lavoro contemporaneamente. Preparati ai colloqui con feedback in tempo reale.
Il predittore di successo mostra le tue possibilità prima di candidarti.
Monitora tutte le tue candidature in un unico posto. Inizia oggi il tuo percorso professionale!""",
        
        "pt": """Bem-vindo ao MedMatch-AI KARAU! Como candidato, você tem acesso a ferramentas poderosas de IA.
Carregue seu currículo e nossa IA analisará suas habilidades automaticamente.
Pesquise em 15 sites de emprego de uma vez. Prepare-se para entrevistas com feedback em tempo real.
O preditor de sucesso mostra suas chances antes de se candidatar.
Acompanhe todas as suas candidaturas em um só lugar. Comece sua jornada profissional hoje!""",
        
        "sw": """Karibu MedMatch-AI KARAU! Kama mtafutaji wa kazi, una ufikiaji wa zana za AI zenye nguvu.
Pakia CV yako na AI yetu itachambua ujuzi wako kiotomatiki.
Tafuta kwenye tovuti 15 za kazi mara moja. Jiandae kwa mahojiano na maoni ya wakati halisi.
Kitabiri cha mafanikio kinakuonyesha nafasi zako kabla ya kuomba.
Fuatilia maombi yako yote mahali pamoja. Anza safari yako ya kazi leo!""",
        
        "vi": """Chào mừng đến với MedMatch-AI KARAU! Là người tìm việc, bạn có quyền truy cập các công cụ AI mạnh mẽ.
Tải CV của bạn lên và AI của chúng tôi sẽ tự động phân tích kỹ năng của bạn.
Tìm kiếm trên 15 trang việc làm cùng lúc. Chuẩn bị phỏng vấn với phản hồi thời gian thực.
Công cụ dự đoán thành công cho thấy cơ hội của bạn trước khi ứng tuyển.
Theo dõi tất cả đơn ứng tuyển tại một nơi. Bắt đầu hành trình nghề nghiệp ngay hôm nay!"""
    },
    "02_recruiter_features": {
        "en": """Recruiters, streamline your hiring with MedMatch-AI KARAU.
Post jobs and reach qualified candidates instantly.
Use our AI-powered applicant tracking system for efficient screening.
Schedule interviews seamlessly. Let AI help you find the perfect match!
Transform your hiring process today.""",
        
        "es": """Reclutadores, optimicen sus contrataciones con MedMatch-AI KARAU.
Publiquen empleos y lleguen a candidatos calificados al instante.
Usen nuestro sistema de seguimiento de candidatos impulsado por IA.
Programen entrevistas sin problemas. ¡Dejen que la IA les ayude a encontrar al candidato perfecto!
Transformen su proceso de contratación hoy.""",
        
        "ja": """採用担当者の皆様、MedMatch-AI KARAUで採用を効率化しましょう。
求人を投稿し、即座に適格な候補者にリーチ。
AI搭載の応募者追跡システムで効率的なスクリーニング。
シームレスな面接スケジュール。AIが最適な人材探しをサポート！
今日から採用プロセスを変革しましょう。"""
    },
    "03_privacy_matters": {
        "en": """Your privacy matters at MedMatch-AI KARAU.
We use bank-level encryption for all your personal data.
Control exactly what recruiters can see about you.
Your job search stays completely confidential. We comply with GDPR and global privacy laws.
You own your data and can delete it anytime. Your trust is our priority."""
    },
    "04_faq_ai_compliance": {
        "en": """Let me answer common questions about AI compliance at MedMatch-AI KARAU.
Our AI is transparent and explainable. We follow EU AI Act guidelines.
Your data trains no external models. All AI decisions can be appealed.
We regularly audit our algorithms for bias. Fair and ethical AI is our commitment.
Questions? Contact our compliance team anytime.
We're committed to responsible AI use."""
    },
    "05_complete_overview": {
        "en": """Welcome to MedMatch-AI KARAU, your AI-powered career companion!
Whether you're a job seeker or recruiter, we've got you covered.
Upload resumes, search jobs, prepare for interviews, and connect with opportunities.
Privacy-first, AI-powered, human-centered. Start your journey today!
Join thousands of life sciences professionals already using MedMatch-AI KARAU.
Your next career move starts here."""
    }
}


async def generate_tutorial_audio(video_id: str, language: str) -> Dict[str, Any]:
    """
    Generate audio for a tutorial video in the specified language using edge-tts.
    
    Args:
        video_id: Tutorial video ID (e.g., "01_jobseeker_features")
        language: Language code (e.g., "es", "ja", "zh")
    
    Returns:
        Dict with success status and audio file path/URL
    """
    try:
        # Get voice for language
        voice = LANGUAGE_VOICES.get(language)
        if not voice:
            # Try base language code
            base_lang = language.split("-")[0]
            voice = LANGUAGE_VOICES.get(base_lang, "en-US-AriaNeural")
        
        # Get script for video and language
        video_scripts = TUTORIAL_SCRIPTS.get(video_id, {})
        script = video_scripts.get(language)
        
        if not script:
            # Fall back to English if no translation
            script = video_scripts.get("en", "Welcome to MedMatch-AI KARAU!")
            logger.warning(f"No script for {video_id} in {language}, using English")
        
        # Generate unique filename
        hash_input = f"{video_id}_{language}_{script[:50]}"
        file_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        filename = f"{video_id}_{language}_{file_hash}.mp3"
        filepath = AUDIO_DIR / filename
        
        # Check if already generated
        if filepath.exists():
            logger.info(f"Audio already exists: {filepath}")
            return {
                "success": True,
                "audio_url": f"/api/tutorials/audio/{filename}",
                "filepath": str(filepath),
                "cached": True
            }
        
        # Generate audio using edge-tts
        logger.info(f"Generating audio: {video_id} in {language} with voice {voice}")
        
        communicate = edge_tts.Communicate(script, voice)
        await communicate.save(str(filepath))
        
        logger.info(f"Audio generated successfully: {filepath}")
        
        return {
            "success": True,
            "audio_url": f"/api/tutorials/audio/{filename}",
            "filepath": str(filepath),
            "cached": False
        }
        
    except Exception as e:
        logger.error(f"Error generating audio: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def get_available_voices() -> list:
    """Get list of all available edge-tts voices."""
    voices = await edge_tts.list_voices()
    return [
        {
            "name": v["Name"],
            "locale": v["Locale"],
            "gender": v["Gender"],
            "language": v["Locale"].split("-")[0]
        }
        for v in voices
    ]


def get_supported_languages() -> list:
    """Get list of languages with audio support."""
    return list(LANGUAGE_VOICES.keys())
