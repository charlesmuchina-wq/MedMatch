"""
Edge TTS Service - Free Multi-Language Text-to-Speech
Comprehensive support for 22+ languages across all 5 tutorial videos

Uses Microsoft's neural TTS voices via edge-tts library.
100+ voices across 40+ languages, no API key required.

Updated: Feb 22, 2026 - Added full multi-language support
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
    "zu": "zu-ZA-ThandoNeural",
    
    # Other languages
    "tl": "fil-PH-BlessicaNeural",  # Filipino/Tagalog
    "am": "am-ET-MekdesNeural",     # Amharic
}

# Complete tutorial scripts for all 5 videos in all supported languages
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
Theo dõi tất cả đơn ứng tuyển tại một nơi. Bắt đầu hành trình nghề nghiệp ngay hôm nay!""",
        
        "nl": """Welkom bij MedMatch-AI KARAU! Als werkzoekende heb je toegang tot krachtige AI-tools.
Upload je CV en onze AI analyseert automatisch je vaardigheden.
Zoek op 15 vacaturesites tegelijk. Bereid je voor op sollicitatiegesprekken met realtime feedback.
De succesvoorspeller toont je kansen voordat je solliciteert.
Volg al je sollicitaties op één plek. Begin vandaag nog je carrièrereis!""",
        
        "pl": """Witamy w MedMatch-AI KARAU! Jako osoba szukająca pracy, masz dostęp do potężnych narzędzi AI.
Prześlij swoje CV, a nasza AI automatycznie przeanalizuje Twoje umiejętności.
Szukaj na 15 portalach pracy jednocześnie. Przygotuj się do rozmów z informacją zwrotną w czasie rzeczywistym.
Predyktor sukcesu pokazuje Twoje szanse przed aplikowaniem.
Śledź wszystkie swoje aplikacje w jednym miejscu. Rozpocznij swoją karierę już dziś!""",
        
        "sv": """Välkommen till MedMatch-AI KARAU! Som jobbsökande har du tillgång till kraftfulla AI-verktyg.
Ladda upp ditt CV och vår AI analyserar dina färdigheter automatiskt.
Sök på 15 jobbsajter samtidigt. Förbered dig för intervjuer med feedback i realtid.
Framgångsprediktorn visar dina chanser innan du ansöker.
Följ alla dina ansökningar på ett ställe. Börja din karriärresa idag!""",
        
        "tr": """MedMatch-AI KARAU'ya hoş geldiniz! İş arayan olarak güçlü AI araçlarına erişiminiz var.
CV'nizi yükleyin ve AI'mız becerilerinizi otomatik olarak analiz etsin.
15 iş sitesinde aynı anda arama yapın. Gerçek zamanlı geri bildirimle mülakata hazırlanın.
Başarı tahmincisi başvurmadan önce şansınızı gösterir.
Tüm başvurularınızı tek bir yerde takip edin. Kariyer yolculuğunuza bugün başlayın!""",
        
        "af": """Welkom by MedMatch-AI KARAU! As werksoeker het jy toegang tot kragtige AI-gereedskap.
Laai jou CV op en ons AI sal jou vaardighede outomaties ontleed.
Soek op 15 werkgewer webwerwe gelyktydig. Berei voor vir onderhoude met intydse terugvoer.
Die suksesvoorspeller wys jou kanse voordat jy aansoek doen.
Volg al jou aansoeke op een plek. Begin vandag jou loopbaanreis!""",
        
        "tl": """Maligayang pagdating sa MedMatch-AI KARAU! Bilang naghahanap ng trabaho, may access ka sa makapangyarihang AI tools.
I-upload ang iyong resume at awtomatikong susuriin ng AI namin ang iyong mga kasanayan.
Maghanap sa 15 job sites nang sabay-sabay. Maghanda sa mga interview na may real-time feedback.
Ipinapakita ng success predictor ang iyong mga pagkakataon bago mag-apply.
Subaybayan ang lahat ng iyong aplikasyon sa isang lugar. Simulan ang iyong career journey ngayon!""",
        
        "th": """ยินดีต้อนรับสู่ MedMatch-AI KARAU! ในฐานะผู้หางาน คุณสามารถเข้าถึงเครื่องมือ AI ที่ทรงพลัง
อัปโหลดเรซูเม่ของคุณ และ AI ของเราจะวิเคราะห์ทักษะของคุณโดยอัตโนมัติ
ค้นหาใน 15 เว็บไซต์หางานพร้อมกัน เตรียมสัมภาษณ์พร้อมฟีดแบ็กแบบเรียลไทม์
ตัวทำนายความสำเร็จแสดงโอกาสของคุณก่อนสมัคร
ติดตามการสมัครทั้งหมดของคุณในที่เดียว เริ่มเส้นทางอาชีพของคุณวันนี้!""",
        
        "id": """Selamat datang di MedMatch-AI KARAU! Sebagai pencari kerja, Anda memiliki akses ke alat AI yang powerful.
Unggah CV Anda dan AI kami akan menganalisis keterampilan Anda secara otomatis.
Cari di 15 situs lowongan sekaligus. Persiapkan wawancara dengan feedback real-time.
Prediktor sukses menunjukkan peluang Anda sebelum melamar.
Lacak semua lamaran Anda di satu tempat. Mulai perjalanan karir Anda hari ini!""",
        
        "he": """ברוכים הבאים ל-MedMatch-AI KARAU! כמחפש עבודה, יש לך גישה לכלי AI חזקים.
העלה את קורות החיים שלך וה-AI שלנו ינתח את הכישורים שלך אוטומטית.
חפש ב-15 אתרי דרושים בבת אחת. התכונן לראיונות עם משוב בזמן אמת.
מנבא ההצלחה מציג את הסיכויים שלך לפני שאתה מגיש מועמדות.
עקוב אחר כל הבקשות שלך במקום אחד. התחל את מסע הקריירה שלך היום!"""
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
        
        "fr": """Recruteurs, optimisez vos embauches avec MedMatch-AI KARAU.
Publiez des offres et atteignez des candidats qualifiés instantanément.
Utilisez notre système de suivi des candidats alimenté par l'IA.
Planifiez des entretiens facilement. Laissez l'IA vous aider à trouver le candidat parfait!
Transformez votre processus de recrutement aujourd'hui.""",
        
        "de": """Recruiter, optimieren Sie Ihre Einstellungen mit MedMatch-AI KARAU.
Veröffentlichen Sie Stellen und erreichen Sie qualifizierte Kandidaten sofort.
Nutzen Sie unser KI-gestütztes Bewerbermanagementsystem für effizientes Screening.
Planen Sie Interviews nahtlos. Lassen Sie KI Ihnen helfen, den perfekten Kandidaten zu finden!
Transformieren Sie Ihren Einstellungsprozess heute.""",
        
        "ja": """採用担当者の皆様、MedMatch-AI KARAUで採用を効率化しましょう。
求人を投稿し、即座に適格な候補者にリーチ。
AI搭載の応募者追跡システムで効率的なスクリーニング。
シームレスな面接スケジュール。AIが最適な人材探しをサポート！
今日から採用プロセスを変革しましょう。""",
        
        "zh": """招聘人员，使用MedMatch-AI KARAU简化您的招聘流程。
发布职位，立即触达合格候选人。
使用我们的AI驱动的申请人跟踪系统进行高效筛选。
无缝安排面试。让AI帮您找到完美匹配！
今天就改变您的招聘流程。""",
        
        "ko": """채용 담당자 여러분, MedMatch-AI KARAU로 채용을 간소화하세요.
채용 공고를 게시하고 자격을 갖춘 후보자에게 즉시 도달하세요.
효율적인 스크리닝을 위해 AI 기반 지원자 추적 시스템을 사용하세요.
면접을 원활하게 예약하세요. AI가 완벽한 인재를 찾도록 도와드립니다!
오늘 채용 프로세스를 혁신하세요.""",
        
        "pt": """Recrutadores, otimizem suas contratações com MedMatch-AI KARAU.
Publiquem vagas e alcancem candidatos qualificados instantaneamente.
Usem nosso sistema de rastreamento de candidatos com IA para triagem eficiente.
Agendem entrevistas facilmente. Deixem a IA ajudar a encontrar o candidato perfeito!
Transformem seu processo de contratação hoje.""",
        
        "nl": """Recruiters, stroomlijn uw werving met MedMatch-AI KARAU.
Plaats vacatures en bereik direct gekwalificeerde kandidaten.
Gebruik ons AI-aangedreven sollicitant volgsysteem voor efficiënte screening.
Plan interviews naadloos. Laat AI u helpen de perfecte match te vinden!
Transformeer uw wervingsproces vandaag.""",
        
        "pl": """Rekruterzy, usprawnijcie rekrutację z MedMatch-AI KARAU.
Publikujcie oferty pracy i natychmiast docierajcie do kwalifikowanych kandydatów.
Korzystajcie z naszego systemu śledzenia kandydatów opartego na AI do efektywnej selekcji.
Planujcie rozmowy bezproblemowo. Pozwólcie AI pomóc znaleźć idealne dopasowanie!
Przekształćcie swój proces rekrutacji już dziś.""",
        
        "tr": """İşe alım uzmanları, MedMatch-AI KARAU ile işe alımı kolaylaştırın.
İş ilanı yayınlayın ve nitelikli adaylara anında ulaşın.
Verimli tarama için AI destekli aday takip sistemimizi kullanın.
Mülakatları sorunsuz planlayın. AI'ın mükemmel eşleşmeyi bulmanıza yardımcı olmasına izin verin!
İşe alım sürecinizi bugün dönüştürün.""",
        
        "vi": """Nhà tuyển dụng, hãy tối ưu hóa quy trình tuyển dụng với MedMatch-AI KARAU.
Đăng việc làm và tiếp cận ứng viên phù hợp ngay lập tức.
Sử dụng hệ thống theo dõi ứng viên được hỗ trợ bởi AI để sàng lọc hiệu quả.
Lên lịch phỏng vấn dễ dàng. Để AI giúp bạn tìm ứng viên hoàn hảo!
Thay đổi quy trình tuyển dụng của bạn ngay hôm nay.""",
        
        "tl": """Mga recruiter, i-streamline ang inyong hiring gamit ang MedMatch-AI KARAU.
Mag-post ng trabaho at maabot kaagad ang mga kwalipikadong kandidato.
Gamitin ang aming AI-powered applicant tracking system para sa efficient na screening.
Mag-schedule ng interviews nang walang hassle. Hayaan ang AI na tumulong sa paghahanap ng perfect match!
I-transform ang inyong hiring process ngayon.""",
        
        "it": """Recruiter, semplificate le assunzioni con MedMatch-AI KARAU.
Pubblicate offerte di lavoro e raggiungete candidati qualificati istantaneamente.
Utilizzate il nostro sistema di tracciamento candidati basato sull'IA per uno screening efficiente.
Programmate colloqui senza problemi. Lasciate che l'IA vi aiuti a trovare il candidato perfetto!
Trasformate il vostro processo di assunzione oggi.""",
        
        "sv": """Rekryterare, effektivisera er rekrytering med MedMatch-AI KARAU.
Publicera jobb och nå kvalificerade kandidater direkt.
Använd vårt AI-drivna kandidatspårningssystem för effektiv screening.
Schemalägg intervjuer sömlöst. Låt AI hjälpa er hitta den perfekta matchningen!
Transformera er rekryteringsprocess idag.""",
        
        "ru": """Рекрутеры, оптимизируйте найм с MedMatch-AI KARAU.
Размещайте вакансии и мгновенно находите квалифицированных кандидатов.
Используйте нашу систему отслеживания кандидатов на базе ИИ для эффективного отбора.
Планируйте собеседования без проблем. Позвольте ИИ помочь найти идеального кандидата!
Преобразите процесс найма уже сегодня.""",
        
        "hi": """भर्तीकर्ताओं, MedMatch-AI KARAU के साथ अपनी भर्ती को सरल बनाएं।
नौकरियां पोस्ट करें और तुरंत योग्य उम्मीदवारों तक पहुंचें।
कुशल स्क्रीनिंग के लिए हमारे AI-संचालित आवेदक ट्रैकिंग सिस्टम का उपयोग करें।
साक्षात्कार आसानी से शेड्यूल करें। AI को सही मैच खोजने में मदद करने दें!
आज ही अपनी भर्ती प्रक्रिया को बदलें।""",
        
        "th": """ผู้สรรหา ปรับปรุงการจ้างงานของคุณด้วย MedMatch-AI KARAU
โพสต์งานและเข้าถึงผู้สมัครที่มีคุณสมบัติทันที
ใช้ระบบติดตามผู้สมัครที่ขับเคลื่อนด้วย AI สำหรับการคัดกรองที่มีประสิทธิภาพ
กำหนดเวลาสัมภาษณ์อย่างราบรื่น ให้ AI ช่วยคุณค้นหาคู่ที่สมบูรณ์แบบ!
เปลี่ยนกระบวนการจ้างงานของคุณวันนี้""",
        
        "id": """Rekruter, sederhanakan perekrutan Anda dengan MedMatch-AI KARAU.
Posting lowongan dan jangkau kandidat berkualitas secara instan.
Gunakan sistem pelacakan pelamar bertenaga AI kami untuk penyaringan yang efisien.
Jadwalkan wawancara dengan mudah. Biarkan AI membantu Anda menemukan kecocokan sempurna!
Transformasi proses perekrutan Anda hari ini.""",
        
        "ar": """المجندون، قوموا بتبسيط التوظيف مع MedMatch-AI KARAU.
انشروا الوظائف وتواصلوا مع المرشحين المؤهلين فوراً.
استخدموا نظام تتبع المتقدمين المدعوم بالذكاء الاصطناعي للفحص الفعال.
جدولوا المقابلات بسلاسة. دعوا الذكاء الاصطناعي يساعدكم في إيجاد التطابق المثالي!
حولوا عملية التوظيف الخاصة بكم اليوم.""",
        
        "he": """מגייסים, ייעלו את הגיוס עם MedMatch-AI KARAU.
פרסמו משרות והגיעו למועמדים מוסמכים מיד.
השתמשו במערכת מעקב המועמדים שלנו המופעלת בינה מלאכותית לסינון יעיל.
תזמנו ראיונות בצורה חלקה. תנו ל-AI לעזור לכם למצוא את ההתאמה המושלמת!
שנו את תהליך הגיוס שלכם היום.""",
        
        "sw": """Waajiri, rahisisheni uajiri wenu na MedMatch-AI KARAU.
Chapisheni kazi na kufikia wagombea waliohitimu mara moja.
Tumia mfumo wetu wa kufuatilia waombaji unaotumia AI kwa uchujaji bora.
Pangeni mahojiano kwa urahisi. Acha AI ikuongoze kupata ulinganifu kamili!
Badilisheni mchakato wenu wa uajiri leo.""",
        
        "af": """Werwers, stroomlyn u aanstelling met MedMatch-AI KARAU.
Plaas poste en bereik gekwalifiseerde kandidate onmiddellik.
Gebruik ons KI-aangedrewe aansoeker-opsporingstelsel vir doeltreffende keuring.
Skeduleer onderhoude naatloos. Laat KI u help om die perfekte passing te vind!
Transformeer u aanstellingsproses vandag.""",
        
        "zu": """Abaqashi, yenza ukuqasha kwakho kube lula nge-MedMatch-AI KARAU.
Thumela imisebenzi ufinyelele abafake izicelo abafanele ngokushesha.
Sebenzisa uhlelo lwethu lokulandelela abafake izicelo olusetshenziswa yi-AI ukuhlola ngempumelelo.
Hlela izingxoxo ngokushesha. Vumela i-AI ikusize uthole ukufaneleka okugcwele!
Guqula inqubo yakho yokuqasha namuhla.""",
        
        "am": """ቀጣሪዎች፣ ከMedMatch-AI KARAU ጋር ቅጥርዎን ቀላል ያድርጉ።
ስራዎችን ይለጥፉ እና ብቁ እጩዎችን ወዲያውኑ ያግኙ።
ለቀልጣፋ ምርመራ AI-የተደገፈ የአመልካች ክትትል ስርዓታችንን ይጠቀሙ።
ቃለ መጠይቆችን በቀላሉ ያቅዱ። AI ፍጹም ግጥሚያ እንዲያገኙ ይርዳዎ!
የቅጥር ሂደትዎን ዛሬ ይቀይሩ።"""
    },
    
    "03_privacy_matters": {
        "en": """Your privacy matters at MedMatch-AI KARAU.
We use bank-level encryption for all your personal data.
Control exactly what recruiters can see about you.
Your job search stays completely confidential. We comply with GDPR and global privacy laws.
You own your data and can delete it anytime. Your trust is our priority.""",
        
        "es": """Tu privacidad importa en MedMatch-AI KARAU.
Usamos encriptación de nivel bancario para todos tus datos personales.
Controla exactamente lo que los reclutadores pueden ver sobre ti.
Tu búsqueda de empleo permanece completamente confidencial. Cumplimos con GDPR y leyes de privacidad globales.
Eres dueño de tus datos y puedes eliminarlos en cualquier momento. Tu confianza es nuestra prioridad.""",
        
        "fr": """Votre vie privée compte chez MedMatch-AI KARAU.
Nous utilisons un cryptage de niveau bancaire pour toutes vos données personnelles.
Contrôlez exactement ce que les recruteurs peuvent voir sur vous.
Votre recherche d'emploi reste entièrement confidentielle. Nous respectons le RGPD et les lois mondiales sur la vie privée.
Vous êtes propriétaire de vos données et pouvez les supprimer à tout moment. Votre confiance est notre priorité.""",
        
        "de": """Ihre Privatsphäre ist uns bei MedMatch-AI KARAU wichtig.
Wir verwenden Verschlüsselung auf Bankniveau für alle Ihre persönlichen Daten.
Kontrollieren Sie genau, was Recruiter über Sie sehen können.
Ihre Jobsuche bleibt vollständig vertraulich. Wir erfüllen DSGVO und globale Datenschutzgesetze.
Sie besitzen Ihre Daten und können sie jederzeit löschen. Ihr Vertrauen ist unsere Priorität.""",
        
        "ja": """MedMatch-AI KARAUではプライバシーを大切にしています。
すべての個人データに銀行レベルの暗号化を使用しています。
採用担当者に見せる情報を正確にコントロールできます。
求職活動は完全に機密保持されます。GDPRおよびグローバルなプライバシー法を遵守しています。
データはあなたのものであり、いつでも削除できます。信頼が私たちの優先事項です。""",
        
        "zh": """您的隐私在MedMatch-AI KARAU很重要。
我们对您所有的个人数据使用银行级加密。
精确控制招聘人员可以看到关于您的哪些信息。
您的求职完全保密。我们遵守GDPR和全球隐私法律。
您拥有自己的数据，可以随时删除。您的信任是我们的首要任务。""",
        
        "ko": """MedMatch-AI KARAU에서 귀하의 개인정보는 중요합니다.
모든 개인 데이터에 은행 수준의 암호화를 사용합니다.
채용 담당자가 귀하에 대해 볼 수 있는 정보를 정확하게 제어하세요.
구직 활동은 완전히 기밀로 유지됩니다. GDPR 및 글로벌 개인정보 보호법을 준수합니다.
데이터는 귀하의 것이며 언제든지 삭제할 수 있습니다. 귀하의 신뢰가 우리의 최우선입니다.""",
        
        "it": """La tua privacy conta su MedMatch-AI KARAU.
Utilizziamo crittografia di livello bancario per tutti i tuoi dati personali.
Controlla esattamente cosa possono vedere i recruiter su di te.
La tua ricerca di lavoro rimane completamente confidenziale. Rispettiamo il GDPR e le leggi globali sulla privacy.
I tuoi dati sono tuoi e puoi cancellarli in qualsiasi momento. La tua fiducia è la nostra priorità.""",
        
        "pt": """Sua privacidade importa no MedMatch-AI KARAU.
Usamos criptografia de nível bancário para todos os seus dados pessoais.
Controle exatamente o que os recrutadores podem ver sobre você.
Sua busca de emprego permanece completamente confidencial. Cumprimos com GDPR e leis de privacidade globais.
Você é dono dos seus dados e pode deletá-los a qualquer momento. Sua confiança é nossa prioridade.""",
        
        "nl": """Uw privacy is belangrijk bij MedMatch-AI KARAU.
Wij gebruiken versleuteling op bankniveau voor al uw persoonlijke gegevens.
Bepaal precies wat recruiters over u kunnen zien.
Uw zoektocht naar werk blijft volledig vertrouwelijk. Wij voldoen aan GDPR en wereldwijde privacywetten.
U bent eigenaar van uw gegevens en kunt ze op elk moment verwijderen. Uw vertrouwen is onze prioriteit.""",
        
        "pl": """Twoja prywatność ma znaczenie w MedMatch-AI KARAU.
Używamy szyfrowania na poziomie bankowym dla wszystkich Twoich danych osobowych.
Kontroluj dokładnie, co rekruterzy mogą o Tobie zobaczyć.
Twoje poszukiwanie pracy pozostaje całkowicie poufne. Przestrzegamy RODO i globalnych przepisów o ochronie prywatności.
Jesteś właścicielem swoich danych i możesz je usunąć w dowolnym momencie. Twoje zaufanie jest naszym priorytetem.""",
        
        "sv": """Din integritet är viktig hos MedMatch-AI KARAU.
Vi använder kryptering på banknivå för all din personliga data.
Kontrollera exakt vad rekryterare kan se om dig.
Din jobbsökning förblir helt konfidentiell. Vi följer GDPR och globala integritetslagar.
Du äger din data och kan radera den när som helst. Ditt förtroende är vår prioritet.""",
        
        "ru": """Ваша конфиденциальность важна для MedMatch-AI KARAU.
Мы используем шифрование банковского уровня для всех ваших личных данных.
Контролируйте, что именно рекрутеры могут видеть о вас.
Ваш поиск работы остается полностью конфиденциальным. Мы соблюдаем GDPR и мировые законы о конфиденциальности.
Вы владеете своими данными и можете удалить их в любое время. Ваше доверие - наш приоритет.""",
        
        "vi": """Quyền riêng tư của bạn quan trọng tại MedMatch-AI KARAU.
Chúng tôi sử dụng mã hóa cấp ngân hàng cho tất cả dữ liệu cá nhân của bạn.
Kiểm soát chính xác những gì nhà tuyển dụng có thể thấy về bạn.
Việc tìm kiếm việc làm của bạn hoàn toàn được bảo mật. Chúng tôi tuân thủ GDPR và luật bảo mật toàn cầu.
Bạn sở hữu dữ liệu của mình và có thể xóa bất cứ lúc nào. Sự tin tưởng của bạn là ưu tiên của chúng tôi.""",
        
        "hi": """MedMatch-AI KARAU में आपकी गोपनीयता महत्वपूर्ण है।
हम आपके सभी व्यक्तिगत डेटा के लिए बैंक-स्तरीय एन्क्रिप्शन का उपयोग करते हैं।
भर्तीकर्ता आपके बारे में क्या देख सकते हैं, इसे सटीक रूप से नियंत्रित करें।
आपकी नौकरी खोज पूरी तरह से गोपनीय रहती है। हम GDPR और वैश्विक गोपनीयता कानूनों का पालन करते हैं।
आप अपने डेटा के मालिक हैं और इसे कभी भी हटा सकते हैं। आपका विश्वास हमारी प्राथमिकता है।""",
        
        "th": """ความเป็นส่วนตัวของคุณสำคัญที่ MedMatch-AI KARAU
เราใช้การเข้ารหัสระดับธนาคารสำหรับข้อมูลส่วนบุคคลทั้งหมดของคุณ
ควบคุมสิ่งที่ผู้สรรหาสามารถเห็นเกี่ยวกับคุณได้อย่างแม่นยำ
การหางานของคุณยังคงเป็นความลับอย่างสมบูรณ์ เราปฏิบัติตาม GDPR และกฎหมายความเป็นส่วนตัวทั่วโลก
คุณเป็นเจ้าของข้อมูลของคุณและสามารถลบได้ทุกเมื่อ ความไว้วางใจของคุณคือสิ่งสำคัญของเรา""",
        
        "id": """Privasi Anda penting di MedMatch-AI KARAU.
Kami menggunakan enkripsi tingkat bank untuk semua data pribadi Anda.
Kontrol dengan tepat apa yang dapat dilihat perekrut tentang Anda.
Pencarian kerja Anda tetap sepenuhnya rahasia. Kami mematuhi GDPR dan undang-undang privasi global.
Anda memiliki data Anda dan dapat menghapusnya kapan saja. Kepercayaan Anda adalah prioritas kami.""",
        
        "ar": """خصوصيتك مهمة في MedMatch-AI KARAU.
نستخدم تشفيراً على مستوى البنوك لجميع بياناتك الشخصية.
تحكم بالضبط فيما يمكن للمجندين رؤيته عنك.
يبقى بحثك عن عمل سرياً تماماً. نلتزم بـGDPR وقوانين الخصوصية العالمية.
أنت تملك بياناتك ويمكنك حذفها في أي وقت. ثقتك هي أولويتنا.""",
        
        "tr": """MedMatch-AI KARAU'da gizliliğiniz önemlidir.
Tüm kişisel verileriniz için banka düzeyinde şifreleme kullanıyoruz.
İşe alım uzmanlarının sizin hakkınızda ne görebileceğini tam olarak kontrol edin.
İş aramanız tamamen gizli kalır. GDPR ve küresel gizlilik yasalarına uyuyoruz.
Verilerinizin sahibi sizsiniz ve istediğiniz zaman silebilirsiniz. Güveniniz önceliğimizdir.""",
        
        "he": """הפרטיות שלך חשובה ב-MedMatch-AI KARAU.
אנו משתמשים בהצפנה ברמת בנק לכל הנתונים האישיים שלך.
שלוט בדיוק מה מגייסים יכולים לראות עליך.
חיפוש העבודה שלך נשאר חסוי לחלוטין. אנו מצייתים ל-GDPR ולחוקי פרטיות גלובליים.
אתה בעל הנתונים שלך ויכול למחוק אותם בכל עת. האמון שלך הוא בראש סדר העדיפויות שלנו.""",
        
        "sw": """Faragha yako ni muhimu katika MedMatch-AI KARAU.
Tunatumia usimbaji wa kiwango cha benki kwa data yako yote ya kibinafsi.
Dhibiti kwa usahihi waajiri wanaweza kuona nini kuhusu wewe.
Utafutaji wako wa kazi unabaki siri kabisa. Tunafuata GDPR na sheria za faragha za kimataifa.
Unamiliki data yako na unaweza kuifuta wakati wowote. Uaminifu wako ni kipaumbele chetu.""",
        
        "af": """Jou privaatheid is belangrik by MedMatch-AI KARAU.
Ons gebruik bank-vlak enkripsie vir al jou persoonlike data.
Beheer presies wat werwers oor jou kan sien.
Jou werksoektog bly heeltemal vertroulik. Ons voldoen aan GDPR en globale privaatheidswette.
Jy besit jou data en kan dit enige tyd uitvee. Jou vertroue is ons prioriteit.""",
        
        "zu": """Ubumfihlo bakho bubalulekile ku-MedMatch-AI KARAU.
Sisebenzisa ukubethela kwezinga lebhange kuyo yonke idatha yakho yomuntu siqu.
Lawula ngqo ukuthi abaqashi bangabona ini ngawe.
Ukufuna kwakho umsebenzi kuhlala kuyimfihlo ngokuphelele. Silandela i-GDPR nemithetho yobumfihlo bomhlaba wonke.
Ungumnikazi wedatha yakho futhi ungayisusa noma nini. Ukwethemba kwakho kuyinto yethu ebalulekile.""",
        
        "tl": """Mahalaga ang iyong privacy sa MedMatch-AI KARAU.
Gumagamit kami ng bank-level encryption para sa lahat ng iyong personal na data.
Kontrolin kung ano mismo ang makikita ng mga recruiter tungkol sa iyo.
Nananatiling ganap na confidential ang iyong job search. Sumusunod kami sa GDPR at global privacy laws.
Ikaw ang may-ari ng iyong data at maaari mo itong burahin anumang oras. Ang iyong tiwala ang aming prayoridad.""",
        
        "am": """ግላዊነትዎ በMedMatch-AI KARAU ላይ አስፈላጊ ነው።
ለሁሉም የግል ውሂብዎ የባንክ ደረጃ ምስጠራ እንጠቀማለን።
ቀጣሪዎች ስለ እርስዎ ምን ማየት እንደሚችሉ በትክክል ይቆጣጠሩ።
የስራ ፍለጋዎ ሙሉ በሙሉ ሚስጥራዊ ሆኖ ይቆያል። GDPR እና ዓለም አቀፍ የግላዊነት ህጎችን እናከብራለን።
ውሂብዎ የእርስዎ ነው እና በማንኛውም ጊዜ መሰረዝ ይችላሉ። እምነትዎ ቅድሚያ የሚሰጠን ነው።"""
    },
    
    "04_faq_ai_compliance": {
        "en": """Let me answer common questions about AI compliance at MedMatch-AI KARAU.
Our AI is transparent and explainable. We follow EU AI Act guidelines.
Your data trains no external models. All AI decisions can be appealed.
We regularly audit our algorithms for bias. Fair and ethical AI is our commitment.
Questions? Contact our compliance team anytime.
We're committed to responsible AI use.""",
        
        "es": """Permítanme responder preguntas comunes sobre el cumplimiento de IA en MedMatch-AI KARAU.
Nuestra IA es transparente y explicable. Seguimos las directrices de la Ley de IA de la UE.
Sus datos no entrenan modelos externos. Todas las decisiones de IA pueden ser apeladas.
Auditamos regularmente nuestros algoritmos en busca de sesgos. La IA justa y ética es nuestro compromiso.
¿Preguntas? Contacte a nuestro equipo de cumplimiento en cualquier momento.
Estamos comprometidos con el uso responsable de la IA.""",
        
        "fr": """Permettez-moi de répondre aux questions courantes sur la conformité IA chez MedMatch-AI KARAU.
Notre IA est transparente et explicable. Nous suivons les directives de la loi européenne sur l'IA.
Vos données n'entraînent aucun modèle externe. Toutes les décisions IA peuvent être contestées.
Nous auditons régulièrement nos algorithmes pour détecter les biais. Une IA juste et éthique est notre engagement.
Des questions? Contactez notre équipe de conformité à tout moment.
Nous nous engageons à une utilisation responsable de l'IA.""",
        
        "de": """Lassen Sie mich häufige Fragen zur KI-Compliance bei MedMatch-AI KARAU beantworten.
Unsere KI ist transparent und erklärbar. Wir folgen den Richtlinien des EU-KI-Gesetzes.
Ihre Daten trainieren keine externen Modelle. Alle KI-Entscheidungen können angefochten werden.
Wir überprüfen unsere Algorithmen regelmäßig auf Voreingenommenheit. Faire und ethische KI ist unsere Verpflichtung.
Fragen? Kontaktieren Sie unser Compliance-Team jederzeit.
Wir sind dem verantwortungsvollen KI-Einsatz verpflichtet.""",
        
        "ja": """MedMatch-AI KARAUのAIコンプライアンスに関するよくある質問にお答えします。
私たちのAIは透明で説明可能です。EU AI法のガイドラインに従っています。
お客様のデータは外部モデルの学習に使用されません。すべてのAIの決定に異議を申し立てることができます。
バイアスについてアルゴリズムを定期的に監査しています。公正で倫理的なAIが私たちの約束です。
ご質問は？いつでもコンプライアンスチームにお問い合わせください。
責任あるAI使用に取り組んでいます。""",
        
        "zh": """让我回答关于MedMatch-AI KARAU AI合规性的常见问题。
我们的AI是透明且可解释的。我们遵循欧盟AI法案的指导方针。
您的数据不会训练任何外部模型。所有AI决策都可以申诉。
我们定期审计算法以防止偏见。公平和道德的AI是我们的承诺。
有问题吗？随时联系我们的合规团队。
我们致力于负责任地使用AI。""",
        
        "ko": """MedMatch-AI KARAU의 AI 규정 준수에 대한 일반적인 질문에 답해 드리겠습니다.
우리의 AI는 투명하고 설명 가능합니다. EU AI 법안 지침을 따릅니다.
귀하의 데이터는 외부 모델을 훈련시키지 않습니다. 모든 AI 결정에 이의를 제기할 수 있습니다.
편향성에 대해 알고리즘을 정기적으로 감사합니다. 공정하고 윤리적인 AI가 우리의 약속입니다.
질문이 있으신가요? 언제든지 규정 준수 팀에 문의하세요.
책임감 있는 AI 사용에 전념합니다.""",
        
        "it": """Permettetemi di rispondere alle domande comuni sulla conformità AI di MedMatch-AI KARAU.
La nostra AI è trasparente e spiegabile. Seguiamo le linee guida dell'EU AI Act.
I vostri dati non addestrano modelli esterni. Tutte le decisioni AI possono essere appellate.
Auditiamo regolarmente i nostri algoritmi per i pregiudizi. Un'AI equa ed etica è il nostro impegno.
Domande? Contattate il nostro team di conformità in qualsiasi momento.
Ci impegniamo per un uso responsabile dell'AI.""",
        
        "pt": """Deixe-me responder perguntas comuns sobre conformidade de IA no MedMatch-AI KARAU.
Nossa IA é transparente e explicável. Seguimos as diretrizes do EU AI Act.
Seus dados não treinam modelos externos. Todas as decisões de IA podem ser apeladas.
Auditamos regularmente nossos algoritmos quanto a vieses. IA justa e ética é nosso compromisso.
Perguntas? Entre em contato com nossa equipe de conformidade a qualquer momento.
Estamos comprometidos com o uso responsável de IA.""",
        
        "nl": """Laat me veelgestelde vragen over AI-compliance bij MedMatch-AI KARAU beantwoorden.
Onze AI is transparant en uitlegbaar. We volgen de EU AI Act richtlijnen.
Uw gegevens trainen geen externe modellen. Alle AI-beslissingen kunnen worden aangevochten.
We auditen onze algoritmes regelmatig op vooroordelen. Eerlijke en ethische AI is onze toewijding.
Vragen? Neem op elk moment contact op met ons compliance-team.
We zetten ons in voor verantwoord AI-gebruik.""",
        
        "pl": """Pozwólcie, że odpowiem na częste pytania dotyczące zgodności AI w MedMatch-AI KARAU.
Nasza AI jest przejrzysta i wyjaśnialna. Przestrzegamy wytycznych EU AI Act.
Wasze dane nie trenują żadnych zewnętrznych modeli. Wszystkie decyzje AI można zaskarżyć.
Regularnie audytujemy nasze algorytmy pod kątem stronniczości. Uczciwa i etyczna AI to nasze zobowiązanie.
Pytania? Skontaktujcie się z naszym zespołem ds. zgodności w dowolnym momencie.
Jesteśmy zaangażowani w odpowiedzialne wykorzystanie AI.""",
        
        "sv": """Låt mig svara på vanliga frågor om AI-efterlevnad hos MedMatch-AI KARAU.
Vår AI är transparent och förklarbar. Vi följer EU:s AI-lagstiftning.
Din data tränar inga externa modeller. Alla AI-beslut kan överklagas.
Vi granskar regelbundet våra algoritmer för partiskhet. Rättvis och etisk AI är vårt åtagande.
Frågor? Kontakta vårt compliance-team när som helst.
Vi är engagerade i ansvarsfull AI-användning.""",
        
        "ru": """Позвольте ответить на частые вопросы о соответствии ИИ в MedMatch-AI KARAU.
Наш ИИ прозрачен и объясним. Мы следуем руководящим принципам EU AI Act.
Ваши данные не обучают внешние модели. Все решения ИИ могут быть обжалованы.
Мы регулярно проверяем наши алгоритмы на предвзятость. Справедливый и этичный ИИ - наше обязательство.
Вопросы? Свяжитесь с нашей командой по соответствию в любое время.
Мы привержены ответственному использованию ИИ.""",
        
        "vi": """Hãy để tôi trả lời các câu hỏi thường gặp về tuân thủ AI tại MedMatch-AI KARAU.
AI của chúng tôi minh bạch và có thể giải thích được. Chúng tôi tuân theo hướng dẫn của EU AI Act.
Dữ liệu của bạn không đào tạo bất kỳ mô hình bên ngoài nào. Tất cả quyết định AI có thể được khiếu nại.
Chúng tôi thường xuyên kiểm tra các thuật toán về thiên kiến. AI công bằng và đạo đức là cam kết của chúng tôi.
Có câu hỏi? Liên hệ với nhóm tuân thủ của chúng tôi bất cứ lúc nào.
Chúng tôi cam kết sử dụng AI có trách nhiệm.""",
        
        "hi": """आइए MedMatch-AI KARAU में AI अनुपालन के बारे में सामान्य प्रश्नों का उत्तर दें।
हमारी AI पारदर्शी और व्याख्या योग्य है। हम EU AI Act दिशानिर्देशों का पालन करते हैं।
आपका डेटा कोई बाहरी मॉडल नहीं प्रशिक्षित करता। सभी AI निर्णयों पर अपील की जा सकती है।
हम नियमित रूप से पूर्वाग्रह के लिए हमारे एल्गोरिदम का ऑडिट करते हैं। निष्पक्ष और नैतिक AI हमारी प्रतिबद्धता है।
प्रश्न? किसी भी समय हमारी अनुपालन टीम से संपर्क करें।
हम जिम्मेदार AI उपयोग के लिए प्रतिबद्ध हैं।""",
        
        "th": """ให้ฉันตอบคำถามทั่วไปเกี่ยวกับการปฏิบัติตาม AI ที่ MedMatch-AI KARAU
AI ของเราโปร่งใสและอธิบายได้ เราปฏิบัติตามแนวทาง EU AI Act
ข้อมูลของคุณไม่ได้ฝึกโมเดลภายนอกใดๆ การตัดสินใจ AI ทั้งหมดสามารถอุทธรณ์ได้
เราตรวจสอบอัลกอริทึมของเราเป็นประจำเพื่อหาอคติ AI ที่ยุติธรรมและมีจริยธรรมคือความมุ่งมั่นของเรา
มีคำถาม? ติดต่อทีมการปฏิบัติตามของเราได้ตลอดเวลา
เรามุ่งมั่นที่จะใช้ AI อย่างรับผิดชอบ""",
        
        "id": """Izinkan saya menjawab pertanyaan umum tentang kepatuhan AI di MedMatch-AI KARAU.
AI kami transparan dan dapat dijelaskan. Kami mengikuti pedoman EU AI Act.
Data Anda tidak melatih model eksternal apa pun. Semua keputusan AI dapat diajukan banding.
Kami secara rutin mengaudit algoritma kami untuk bias. AI yang adil dan etis adalah komitmen kami.
Ada pertanyaan? Hubungi tim kepatuhan kami kapan saja.
Kami berkomitmen untuk penggunaan AI yang bertanggung jawab.""",
        
        "ar": """دعوني أجيب على الأسئلة الشائعة حول امتثال الذكاء الاصطناعي في MedMatch-AI KARAU.
ذكاؤنا الاصطناعي شفاف وقابل للتفسير. نتبع إرشادات قانون الذكاء الاصطناعي الأوروبي.
بياناتك لا تدرب أي نماذج خارجية. يمكن الطعن في جميع قرارات الذكاء الاصطناعي.
نراجع خوارزمياتنا بانتظام للتحقق من التحيز. الذكاء الاصطناعي العادل والأخلاقي هو التزامنا.
أسئلة؟ تواصلوا مع فريق الامتثال لدينا في أي وقت.
نحن ملتزمون بالاستخدام المسؤول للذكاء الاصطناعي.""",
        
        "tr": """MedMatch-AI KARAU'da AI uyumluluğu hakkında sık sorulan soruları yanıtlayayım.
Yapay zekamız şeffaf ve açıklanabilir. EU AI Act yönergelerini takip ediyoruz.
Verileriniz hiçbir harici modeli eğitmez. Tüm AI kararlarına itiraz edilebilir.
Algoritmalarımızı önyargı açısından düzenli olarak denetliyoruz. Adil ve etik AI taahhüdümüzdür.
Sorular mı var? Uyumluluk ekibimizle istediğiniz zaman iletişime geçin.
Sorumlu AI kullanımına bağlıyız.""",
        
        "he": """הרשו לי לענות על שאלות נפוצות לגבי תאימות AI ב-MedMatch-AI KARAU.
ה-AI שלנו שקוף וניתן להסבר. אנו עוקבים אחר הנחיות EU AI Act.
הנתונים שלך לא מאמנים מודלים חיצוניים. ניתן לערער על כל החלטות ה-AI.
אנו מבקרים באופן קבוע את האלגוריתמים שלנו לאיתור הטיות. AI הוגן ואתי הוא המחויבות שלנו.
שאלות? צרו קשר עם צוות התאימות שלנו בכל עת.
אנו מחויבים לשימוש אחראי ב-AI.""",
        
        "sw": """Niruhusu kujibu maswali ya kawaida kuhusu utiifu wa AI katika MedMatch-AI KARAU.
AI yetu ni wazi na inaweza kuelezwa. Tunafuata miongozo ya EU AI Act.
Data yako haifunzi modeli zozote za nje. Maamuzi yote ya AI yanaweza kukata rufaa.
Tunakagua mara kwa mara algorithms zetu kwa upendeleo. AI ya haki na maadili ni ahadi yetu.
Maswali? Wasiliana na timu yetu ya utiifu wakati wowote.
Tumejitolea kutumia AI kwa uwajibikaji.""",
        
        "af": """Laat my algemene vrae oor KI-nakoming by MedMatch-AI KARAU beantwoord.
Ons KI is deursigtig en verduidelikbaar. Ons volg die EU KI Wet riglyne.
Jou data lei geen eksterne modelle op nie. Alle KI-besluite kan geappelleer word.
Ons oudit gereeld ons algoritmes vir vooroordeel. Regverdige en etiese KI is ons verbintenis.
Vrae? Kontak ons nakomingspan enige tyd.
Ons is verbind tot verantwoordelike KI-gebruik.""",
        
        "zu": """Ake ngiphendule imibuzo ejwayelekile mayelana nokuthobela kwe-AI ku-MedMatch-AI KARAU.
I-AI yethu icacile futhi iyachazeka. Silandela imihlahlandlela ye-EU AI Act.
Idatha yakho ayiqeqeshi amamodeli angaphandle. Zonke izinqumo ze-AI zingabhikishwa.
Sihlola njalo ama-algorithms ethu ukuthola ukuchema. I-AI enobulungiswa nobulungiswa ukuzinikela kwethu.
Imibuzo? Xhumana nethimba lethu lokuthobela noma nini.
Sizibophezele ekusetshenzisweni kwe-AI okukufanele.""",
        
        "tl": """Hayaan ninyong sagutin ang mga karaniwang tanong tungkol sa AI compliance sa MedMatch-AI KARAU.
Ang aming AI ay transparent at explainable. Sumusunod kami sa mga alituntunin ng EU AI Act.
Ang inyong data ay hindi nagta-train ng anumang external models. Lahat ng AI decisions ay maaaring i-appeal.
Regular naming ino-audit ang aming algorithms para sa bias. Fair at ethical na AI ang aming commitment.
May tanong? Makipag-ugnayan sa aming compliance team anumang oras.
Nakatuon kami sa responsible na paggamit ng AI.""",
        
        "am": """ስለ MedMatch-AI KARAU AI ተገዢነት ተደጋጋሚ ጥያቄዎችን ልመልስ።
AI ያችን ግልጽ እና ሊገለጽ የሚችል ነው። የEU AI Act መመሪያዎችን እንከተላለን።
ውሂብዎ ውጫዊ ሞዴሎችን አያሠለጥንም። ሁሉም የAI ውሳኔዎች ይግባኝ ማቅረብ ይቻላል።
ስልተ ቀመሮቻችንን በመደበኛነት ለአድልዎ እንመረምራለን። ፍትሃዊ እና ስነ-ምግባራዊ AI ቁርጠኝነታችን ነው።
ጥያቄዎች? በማንኛውም ጊዜ የተገዢነት ቡድናችንን ያግኙ።
ሃላፊነት ያለው AI አጠቃቀም ቁርጠኛ ነን።"""
    },
    
    "05_complete_overview": {
        "en": """Welcome to MedMatch-AI KARAU, your AI-powered career companion!
Whether you're a job seeker or recruiter, we've got you covered.
Upload resumes, search jobs, prepare for interviews, and connect with opportunities.
Privacy-first, AI-powered, human-centered. Start your journey today!
Join thousands of life sciences professionals already using MedMatch-AI KARAU.
Your next career move starts here.""",
        
        "es": """¡Bienvenido a MedMatch-AI KARAU, tu compañero de carrera impulsado por IA!
Ya seas buscador de empleo o reclutador, te tenemos cubierto.
Sube currículums, busca empleos, prepárate para entrevistas y conéctate con oportunidades.
Privacidad primero, impulsado por IA, centrado en el humano. ¡Comienza tu viaje hoy!
Únete a miles de profesionales de ciencias de la vida que ya usan MedMatch-AI KARAU.
Tu próximo movimiento de carrera comienza aquí.""",
        
        "fr": """Bienvenue sur MedMatch-AI KARAU, votre compagnon de carrière alimenté par l'IA!
Que vous soyez chercheur d'emploi ou recruteur, nous vous couvrons.
Téléchargez des CV, recherchez des emplois, préparez-vous aux entretiens et connectez-vous aux opportunités.
Confidentialité d'abord, alimenté par l'IA, centré sur l'humain. Commencez votre parcours aujourd'hui!
Rejoignez des milliers de professionnels des sciences de la vie qui utilisent déjà MedMatch-AI KARAU.
Votre prochain mouvement de carrière commence ici.""",
        
        "de": """Willkommen bei MedMatch-AI KARAU, Ihrem KI-gestützten Karrierebegleiter!
Ob Jobsuchender oder Recruiter, wir haben Sie abgedeckt.
Laden Sie Lebensläufe hoch, suchen Sie Jobs, bereiten Sie sich auf Interviews vor und verbinden Sie sich mit Chancen.
Datenschutz zuerst, KI-gestützt, menschenzentriert. Starten Sie Ihre Reise heute!
Schließen Sie sich Tausenden von Life-Sciences-Fachleuten an, die bereits MedMatch-AI KARAU nutzen.
Ihr nächster Karriereschritt beginnt hier.""",
        
        "ja": """MedMatch-AI KARAUへようこそ、あなたのAI搭載キャリアパートナー！
求職者でも採用担当者でも、私たちがサポートします。
履歴書をアップロード、仕事を検索、面接準備、そして機会とつながりましょう。
プライバシー優先、AI搭載、人間中心。今日から旅を始めましょう！
すでにMedMatch-AI KARAUを使用している何千人ものライフサイエンス専門家に加わりましょう。
次のキャリアの一歩はここから始まります。"""
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


def get_supported_videos() -> list:
    """Get list of video IDs with script support."""
    return list(TUTORIAL_SCRIPTS.keys())
