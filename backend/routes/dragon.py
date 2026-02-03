"""
Dragon AI Routes
Handles: KARAU DRAGON AI voice assistant commands, intent processing, web search
Supports: Multi-language voice commands and responses
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import uuid
import logging
import json
import httpx

from emergentintegrations.llm.chat import LlmChat, UserMessage

from utils.database import db
from utils.config import EMERGENT_LLM_KEY, GOOGLE_API_KEY, GOOGLE_CSE_ID
from routes.auth import get_current_user

router = APIRouter(prefix="/dragon", tags=["KARAU Dragon AI"])

# ============== Models ==============

class DragonCommand(BaseModel):
    command: str
    user_context: Dict[str, Any] = {}
    language: Optional[str] = "en"  # User's preferred language

class WebSearchRequest(BaseModel):
    query: str
    num_results: int = 5

# ============== Multi-Language Support ==============

DRAGON_RESPONSES = {
    "en": {
        "greeting": "Hi {name}! I can help you with cover letters, job searches, interview prep, resume management, skill tests, and company research. What would you like to do?",
        "cover_letter": "I'll help you create a cover letter{role}{company}. Taking you to the cover letter generator.",
        "job_search": "Searching for {query}. Let me find the best opportunities for you.",
        "interview_prep": "Let's prepare you for your interview{company}. I'll generate relevant questions.",
        "resume": "Taking you to your resume. You can view, upload, or edit your professional profile.",
        "companies": "Opening the companies directory{company}.",
        "translate": "I'll help you translate that content.",
    },
    "es": {
        "greeting": "¡Hola {name}! Puedo ayudarte con cartas de presentación, búsqueda de empleo, preparación de entrevistas, gestión de currículum, pruebas de habilidades e investigación de empresas. ¿Qué te gustaría hacer?",
        "cover_letter": "Te ayudaré a crear una carta de presentación{role}{company}. Llevándote al generador de cartas.",
        "job_search": "Buscando {query}. Déjame encontrar las mejores oportunidades para ti.",
        "interview_prep": "Preparémonos para tu entrevista{company}. Generaré preguntas relevantes.",
        "resume": "Llevándote a tu currículum. Puedes ver, subir o editar tu perfil profesional.",
        "companies": "Abriendo el directorio de empresas{company}.",
        "translate": "Te ayudaré a traducir ese contenido.",
    },
    "fr": {
        "greeting": "Bonjour {name}! Je peux vous aider avec les lettres de motivation, la recherche d'emploi, la préparation aux entretiens, la gestion du CV, les tests de compétences et la recherche d'entreprises. Que souhaitez-vous faire?",
        "cover_letter": "Je vais vous aider à créer une lettre de motivation{role}{company}. Direction le générateur de lettres.",
        "job_search": "Recherche de {query}. Laissez-moi trouver les meilleures opportunités pour vous.",
        "interview_prep": "Préparons votre entretien{company}. Je vais générer des questions pertinentes.",
        "resume": "Direction votre CV. Vous pouvez consulter, télécharger ou modifier votre profil professionnel.",
        "companies": "Ouverture du répertoire des entreprises{company}.",
        "translate": "Je vais vous aider à traduire ce contenu.",
    },
    "de": {
        "greeting": "Hallo {name}! Ich kann Ihnen bei Anschreiben, Jobsuche, Interviewvorbereitung, Lebenslaufverwaltung, Kompetenztests und Unternehmensrecherche helfen. Was möchten Sie tun?",
        "cover_letter": "Ich helfe Ihnen beim Erstellen eines Anschreibens{role}{company}. Zum Anschreiben-Generator.",
        "job_search": "Suche nach {query}. Lassen Sie mich die besten Möglichkeiten für Sie finden.",
        "interview_prep": "Bereiten wir Sie auf Ihr Interview vor{company}. Ich werde relevante Fragen generieren.",
        "resume": "Zu Ihrem Lebenslauf. Sie können Ihr berufliches Profil ansehen, hochladen oder bearbeiten.",
        "companies": "Öffne das Unternehmensverzeichnis{company}.",
        "translate": "Ich werde Ihnen bei der Übersetzung dieses Inhalts helfen.",
    },
    "zh": {
        "greeting": "你好 {name}！我可以帮助您处理求职信、工作搜索、面试准备、简历管理、技能测试和公司研究。您想做什么？",
        "cover_letter": "我将帮助您创建一封求职信{role}{company}。正在前往求职信生成器。",
        "job_search": "正在搜索 {query}。让我为您找到最佳机会。",
        "interview_prep": "让我们为您的面试做准备{company}。我将生成相关问题。",
        "resume": "正在前往您的简历。您可以查看、上传或编辑您的专业资料。",
        "companies": "正在打开公司目录{company}。",
        "translate": "我将帮助您翻译该内容。",
    },
    "ja": {
        "greeting": "こんにちは {name}さん！カバーレター、求人検索、面接準備、履歴書管理、スキルテスト、企業調査についてお手伝いできます。何をしますか？",
        "cover_letter": "カバーレターの作成をお手伝いします{role}{company}。カバーレタージェネレーターに移動します。",
        "job_search": "{query}を検索しています。最適な機会を見つけます。",
        "interview_prep": "面接の準備をしましょう{company}。関連する質問を生成します。",
        "resume": "履歴書に移動します。プロフィールの閲覧、アップロード、編集ができます。",
        "companies": "企業ディレクトリを開いています{company}。",
        "translate": "そのコンテンツの翻訳をお手伝いします。",
    },
    "pt": {
        "greeting": "Olá {name}! Posso ajudá-lo com cartas de apresentação, busca de emprego, preparação para entrevistas, gestão de currículo, testes de habilidades e pesquisa de empresas. O que você gostaria de fazer?",
        "cover_letter": "Vou ajudá-lo a criar uma carta de apresentação{role}{company}. Levando você ao gerador de cartas.",
        "job_search": "Procurando {query}. Deixe-me encontrar as melhores oportunidades para você.",
        "interview_prep": "Vamos preparar você para sua entrevista{company}. Vou gerar perguntas relevantes.",
        "resume": "Levando você ao seu currículo. Você pode visualizar, enviar ou editar seu perfil profissional.",
        "companies": "Abrindo o diretório de empresas{company}.",
        "translate": "Vou ajudá-lo a traduzir esse conteúdo.",
    },
    "ar": {
        "greeting": "مرحباً {name}! يمكنني مساعدتك في رسائل التغطية، البحث عن وظائف، التحضير للمقابلات، إدارة السيرة الذاتية، اختبارات المهارات، والبحث عن الشركات. ماذا تريد أن تفعل؟",
        "cover_letter": "سأساعدك في إنشاء رسالة تغطية{role}{company}. جاري الانتقال إلى منشئ الرسائل.",
        "job_search": "جاري البحث عن {query}. دعني أجد أفضل الفرص لك.",
        "interview_prep": "دعنا نستعد لمقابلتك{company}. سأقوم بإنشاء أسئلة ذات صلة.",
        "resume": "جاري الانتقال إلى سيرتك الذاتية. يمكنك عرض أو تحميل أو تعديل ملفك المهني.",
        "companies": "جاري فتح دليل الشركات{company}.",
        "translate": "سأساعدك في ترجمة هذا المحتوى.",
    },
    "hi": {
        "greeting": "नमस्ते {name}! मैं कवर लेटर, नौकरी खोज, इंटरव्यू की तैयारी, रिज्यूमे प्रबंधन, स्किल टेस्ट और कंपनी रिसर्च में आपकी मदद कर सकता हूं। आप क्या करना चाहेंगे?",
        "cover_letter": "मैं आपको कवर लेटर बनाने में मदद करूंगा{role}{company}। कवर लेटर जनरेटर पर ले जा रहा हूं।",
        "job_search": "{query} खोज रहा हूं। मुझे आपके लिए सर्वोत्तम अवसर खोजने दें।",
        "interview_prep": "आइए आपके इंटरव्यू की तैयारी करें{company}। मैं प्रासंगिक प्रश्न तैयार करूंगा।",
        "resume": "आपके रिज्यूमे पर ले जा रहा हूं। आप अपना प्रोफेशनल प्रोफाइल देख, अपलोड या एडिट कर सकते हैं।",
        "companies": "कंपनी डायरेक्टरी खोल रहा हूं{company}।",
        "translate": "मैं उस सामग्री का अनुवाद करने में आपकी मदद करूंगा।",
    },
    "ko": {
        "greeting": "안녕하세요 {name}님! 커버레터, 채용 검색, 면접 준비, 이력서 관리, 스킬 테스트, 회사 조사를 도와드릴 수 있습니다. 무엇을 하시겠습니까?",
        "cover_letter": "커버레터 작성을 도와드리겠습니다{role}{company}. 커버레터 생성기로 이동합니다.",
        "job_search": "{query}를 검색하고 있습니다. 최고의 기회를 찾아드리겠습니다.",
        "interview_prep": "면접 준비를 도와드리겠습니다{company}. 관련 질문을 생성하겠습니다.",
        "resume": "이력서로 이동합니다. 프로필을 보거나 업로드하거나 편집할 수 있습니다.",
        "companies": "회사 디렉토리를 열고 있습니다{company}.",
        "translate": "해당 콘텐츠 번역을 도와드리겠습니다.",
    }
}

def get_response_text(intent: str, language: str, **kwargs) -> str:
    """Get localized response text"""
    lang_responses = DRAGON_RESPONSES.get(language, DRAGON_RESPONSES["en"])
    template = lang_responses.get(intent, DRAGON_RESPONSES["en"].get(intent, ""))
    
    # Format template with kwargs
    try:
        return template.format(**kwargs)
    except KeyError:
        return template

# ============== Dragon AI Intent Processing ==============

INTENT_ACTIONS = {
    "cover_letter": {
        "path": "/cover-letter",
        "label": "Cover Letter Generator",
        "color": "#10B981"
    },
    "job_search": {
        "path": "/search",
        "label": "Job Search",
        "color": "#3B82F6"
    },
    "interview_prep": {
        "path": "/interview",
        "label": "Interview Prep",
        "color": "#8B5CF6"
    },
    "resume": {
        "path": "/resume",
        "label": "My Resume",
        "color": "#F59E0B"
    },
    "prediction": {
        "path": "/predictor",
        "label": "Success Predictor",
        "color": "#EF4444"
    },
    "companies": {
        "path": "/companies",
        "label": "Companies",
        "color": "#06B6D4"
    },
    "interviews": {
        "path": "/interviews",
        "label": "Interview Scheduling",
        "color": "#EC4899"
    },
    "skills": {
        "path": "/skill-assessments",
        "label": "Skill Tests",
        "color": "#F97316"
    },
    "analytics": {
        "path": "/analytics",
        "label": "Analytics Dashboard",
        "color": "#14B8A6"
    },
    "salary": {
        "path": "/salary-insights",
        "label": "Salary Insights",
        "color": "#84CC16"
    },
    "messages": {
        "path": "/messages",
        "label": "Messages",
        "color": "#6366F1"
    },
    "translate": {
        "path": None,
        "label": "Translation",
        "color": "#A855F7"
    },
    "web_search": {
        "path": None,
        "label": "Web Search",
        "color": "#6366F1"
    }
}

@router.post("/process")
async def process_dragon_command(data: DragonCommand, request: Request):
    """Process a KARAU Dragon AI voice/text command (multi-language support)"""
    user = await get_current_user(request)
    command = data.command.strip()
    user_context = data.user_context
    language = data.language or "en"

    # Try AI-powered intent detection first (with language awareness)
    if EMERGENT_LLM_KEY:
        try:
            result = await ai_intent_detection(command, user_context, language)
            
            # Log the command
            await log_dragon_command(user, command, result)
            
            return result
        except Exception as e:
            logging.error(f"AI intent detection failed: {e}")
    
    # Fallback to rule-based detection
    result = rule_based_intent_detection(command, user_context)
    
    # Log the command
    await log_dragon_command(user, command, result)
    
    return result

async def ai_intent_detection(command: str, user_context: Dict, language: str = "en") -> Dict:
    """Use AI to detect intent and generate response (multi-language support)"""
    
    # Language-aware system message
    lang_instruction = ""
    if language != "en":
        lang_instruction = "\nIMPORTANT: The user may be speaking in a language other than English. Detect the language and respond in the SAME language as the user's input. If they speak Spanish, respond in Spanish. If Chinese, respond in Chinese, etc."
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message=f"""You are KARAU DRAGON AI, an intelligent multilingual job search assistant. 
Analyze the user's command in ANY language and determine the intent.
{lang_instruction}

IMPORTANT RULES:
1. If the user mentions ANY job title (e.g., "Supplier Quality Manager", "Software Engineer", "Data Scientist"), 
   treat it as a JOB SEARCH intent and help them find those jobs.
2. Be action-oriented - guide users to take specific actions in the app.
3. When detecting job_search intent, include the job title in params.role and params.query.

Available intents:
- job_search: Find jobs, search positions (DEFAULT for job titles)
- cover_letter: Generate or help with cover letters
- interview_prep: Prepare for interviews, practice questions
- resume: View, edit, or manage resume
- prediction: Predict job application success
- companies: Research companies, browse company profiles
- interviews: View or schedule interviews
- skills: Take skill assessments
- analytics: View job search analytics
- salary: Get salary insights for a role
- messages: Check messages
- translate: Translate content between languages
- web_search: Search the internet for information

Return ONLY valid JSON:
{{
    "intent": "<intent_name>",
    "speech": "<friendly, ACTION-ORIENTED response. For job_search: tell them you're searching for those jobs. Be specific and helpful.>",
    "detected_language": "<ISO 639-1 code of user's language>",
    "params": {{
        "company": "<company name if mentioned>",
        "role": "<job role/title - REQUIRED for job_search>",
        "query": "<search query - use the job title for job_search>",
        "target_language": "<target language if translation requested>"
    }},
    "requires_web": <true if web search needed, false otherwise>,
    "confidence": <0.0-1.0>
}}"""
    ).with_model("openai", "gpt-5.2")

    user_name = user_context.get("user_name", "there")
    
    response = await chat.send_message(UserMessage(
        text=f"User '{user_name}' says: {command}"
    ))
    
    # Parse AI response
    clean_response = response.strip()
    if clean_response.startswith("```"):
        clean_response = clean_response.split("```")[1]
        if clean_response.startswith("json"):
            clean_response = clean_response[4:]
    
    result = json.loads(clean_response)
    
    # Add action details
    intent = result.get("intent", "unknown")
    if intent in INTENT_ACTIONS:
        result["action"] = INTENT_ACTIONS[intent]
    
    return result

def rule_based_intent_detection(command: str, user_context: Dict) -> Dict:
    """Fallback rule-based intent detection"""
    cmd = command.lower()
    user_name = user_context.get("user_name", "there")
    
    # Cover letter intents
    if any(phrase in cmd for phrase in ["cover letter", "write letter", "application letter"]):
        company = extract_company(cmd)
        role = extract_role(cmd)
        
        speech = "I'll help you create a cover letter"
        if role:
            speech += f" for a {role} position"
        if company:
            speech += f" at {company}"
        speech += ". Taking you to the cover letter generator."
        
        return {
            "intent": "cover_letter",
            "speech": speech,
            "action": INTENT_ACTIONS["cover_letter"],
            "params": {"company": company, "role": role},
            "requires_web": False,
            "confidence": 0.9
        }
    
    # Job search intents
    if any(phrase in cmd for phrase in ["find job", "search job", "look for job", "job search", "find position"]):
        role = extract_role(cmd)
        location = extract_location(cmd)
        
        speech = f"Searching for {role or 'jobs'}"
        if location:
            speech += f" in {location}"
        speech += ". Let me find the best opportunities for you."
        
        return {
            "intent": "job_search",
            "speech": speech,
            "action": INTENT_ACTIONS["job_search"],
            "params": {"query": role or "", "location": location or ""},
            "requires_web": False,
            "confidence": 0.9
        }
    
    # Interview prep
    if any(phrase in cmd for phrase in ["interview prep", "prepare interview", "practice interview", "interview question"]):
        company = extract_company(cmd)
        role = extract_role(cmd)
        
        speech = "Let's prepare you for your interview"
        if company:
            speech += f" at {company}"
        speech += ". I'll generate relevant questions."
        
        return {
            "intent": "interview_prep",
            "speech": speech,
            "action": INTENT_ACTIONS["interview_prep"],
            "params": {"company": company, "role": role},
            "requires_web": False,
            "confidence": 0.9
        }
    
    # Success prediction
    if any(phrase in cmd for phrase in ["predict", "chance", "probability", "likelihood", "success rate"]):
        return {
            "intent": "prediction",
            "speech": "I'll analyze your profile and predict your success rate for job applications.",
            "action": INTENT_ACTIONS["prediction"],
            "params": {},
            "requires_web": False,
            "confidence": 0.85
        }
    
    # Resume
    if any(phrase in cmd for phrase in ["resume", "cv", "my profile"]):
        return {
            "intent": "resume",
            "speech": "Taking you to your resume. You can view, upload, or edit your professional profile.",
            "action": INTENT_ACTIONS["resume"],
            "params": {},
            "requires_web": False,
            "confidence": 0.9
        }
    
    # Companies
    if any(phrase in cmd for phrase in ["company", "companies", "research company", "about company"]):
        company = extract_company(cmd)
        
        speech = "Opening the companies directory"
        if company:
            speech = f"Let me find information about {company}"
        
        return {
            "intent": "companies",
            "speech": speech,
            "action": INTENT_ACTIONS["companies"],
            "params": {"company": company},
            "requires_web": bool(company),
            "confidence": 0.85
        }
    
    # Interviews/Schedule
    if any(phrase in cmd for phrase in ["my interview", "scheduled interview", "interview schedule", "upcoming interview"]):
        return {
            "intent": "interviews",
            "speech": "Opening your interview schedule.",
            "action": INTENT_ACTIONS["interviews"],
            "params": {},
            "requires_web": False,
            "confidence": 0.9
        }
    
    # Skills
    if any(phrase in cmd for phrase in ["skill", "assessment", "test", "certification"]):
        return {
            "intent": "skills",
            "speech": "Taking you to the skill assessments. You can test your knowledge and earn badges.",
            "action": INTENT_ACTIONS["skills"],
            "params": {},
            "requires_web": False,
            "confidence": 0.85
        }
    
    # Analytics
    if any(phrase in cmd for phrase in ["analytics", "statistics", "dashboard", "progress"]):
        return {
            "intent": "analytics",
            "speech": "Opening your analytics dashboard to show your job search progress.",
            "action": INTENT_ACTIONS["analytics"],
            "params": {},
            "requires_web": False,
            "confidence": 0.85
        }
    
    # Salary
    if any(phrase in cmd for phrase in ["salary", "pay", "compensation", "how much"]):
        role = extract_role(cmd)
        
        return {
            "intent": "salary",
            "speech": f"Let me get salary insights{' for ' + role if role else ''}.",
            "action": INTENT_ACTIONS["salary"],
            "params": {"role": role},
            "requires_web": False,
            "confidence": 0.85
        }
    
    # Messages
    if any(phrase in cmd for phrase in ["message", "inbox", "chat"]):
        return {
            "intent": "messages",
            "speech": "Opening your messages.",
            "action": INTENT_ACTIONS["messages"],
            "params": {},
            "requires_web": False,
            "confidence": 0.9
        }
    
    # Web search (fallback for queries)
    if any(phrase in cmd for phrase in ["search", "find", "what is", "who is", "tell me about", "look up"]):
        return {
            "intent": "web_search",
            "speech": "Let me search the web for that information.",
            "action": INTENT_ACTIONS["web_search"],
            "params": {"query": command},
            "requires_web": True,
            "confidence": 0.7
        }
    
    # Unknown intent
    return {
        "intent": "unknown",
        "speech": f"Hi {user_name}! I can help you with cover letters, job searches, interview prep, resume management, skill tests, and company research. What would you like to do?",
        "suggestions": [
            "Generate a cover letter for Medtronic",
            "Find quality engineer jobs",
            "Prepare for my interview",
            "Show my resume",
            "Take a skill assessment"
        ],
        "confidence": 0.3
    }

def extract_company(text: str) -> Optional[str]:
    """Extract company name from text"""
    import re
    
    # Common patterns
    patterns = [
        r'(?:for|at|with)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)',
        r'(?:company|organization)\s+([A-Z][a-zA-Z]+)',
    ]
    
    # Known companies (extend this list)
    known_companies = [
        "medtronic", "johnson", "abbott", "stryker", "boston scientific",
        "google", "amazon", "microsoft", "apple", "meta", "netflix",
        "tesla", "spacex", "boeing", "lockheed", "raytheon",
        "pfizer", "merck", "novartis", "roche", "astrazeneca"
    ]
    
    text_lower = text.lower()
    for company in known_companies:
        if company in text_lower:
            return company.title()
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def extract_role(text: str) -> Optional[str]:
    """Extract job role from text"""
    roles = [
        "supplier quality engineer", "supplier quality manager", "supplier quality",
        "quality engineer", "quality manager", "quality director",
        "manufacturing engineer", "process engineer", "production manager",
        "software engineer", "developer", "data scientist", "machine learning",
        "project manager", "program manager", "product manager",
        "sales manager", "marketing manager", "account manager",
        "analyst", "consultant", "designer", "architect"
    ]
    
    text_lower = text.lower()
    for role in roles:
        if role in text_lower:
            return role.title()
    
    return None

def extract_location(text: str) -> Optional[str]:
    """Extract location from text"""
    import re
    
    # Pattern for "in [Location]"
    match = re.search(r'in\s+([A-Za-z\s,]+?)(?:\s+at|\s+for|$)', text, re.IGNORECASE)
    if match:
        location = match.group(1).strip()
        if location.lower() not in ["a", "the", "my"]:
            return location
    
    # Check for common locations
    locations = ["remote", "new york", "san francisco", "chicago", "los angeles", "austin", "seattle", "boston"]
    text_lower = text.lower()
    for loc in locations:
        if loc in text_lower:
            return loc.title()
    
    return None

async def log_dragon_command(user: Optional[Dict], command: str, result: Dict):
    """Log Dragon AI commands for analytics"""
    try:
        log_doc = {
            "id": str(uuid.uuid4()),
            "user_id": user["user_id"] if user else None,
            "command": command,
            "intent": result.get("intent"),
            "confidence": result.get("confidence"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await db.dragon_logs.insert_one(log_doc)
    except Exception as e:
        logging.error(f"Failed to log dragon command: {e}")

# ============== Web Search ==============

@router.post("/web-search")
async def dragon_web_search(data: WebSearchRequest, request: Request):
    """Perform web search for Dragon AI"""
    user = await get_current_user(request)
    
    results = []
    
    # Try Google Custom Search if configured
    if GOOGLE_API_KEY and GOOGLE_CSE_ID:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.googleapis.com/customsearch/v1",
                    params={
                        "key": GOOGLE_API_KEY,
                        "cx": GOOGLE_CSE_ID,
                        "q": data.query,
                        "num": data.num_results
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    search_data = response.json()
                    for item in search_data.get("items", []):
                        results.append({
                            "title": item.get("title", ""),
                            "url": item.get("link", ""),
                            "snippet": item.get("snippet", "")
                        })
        except Exception as e:
            logging.error(f"Google search error: {e}")
    
    # Fallback: Use AI to generate relevant information
    if not results and EMERGENT_LLM_KEY:
        try:
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=str(uuid.uuid4()),
                system_message="You are a helpful assistant. Provide brief, factual information."
            ).with_model("openai", "gpt-5.2")
            
            response = await chat.send_message(UserMessage(
                text=f"Provide a brief, helpful response about: {data.query}"
            ))
            
            results.append({
                "title": "AI Generated Response",
                "url": "",
                "snippet": response[:500]
            })
        except Exception as e:
            logging.error(f"AI fallback error: {e}")
    
    return {"results": results, "query": data.query}

# ============== Dragon Analytics ==============

@router.get("/analytics")
async def get_dragon_analytics(request: Request):
    """Get Dragon AI usage analytics (admin only)"""
    user = await get_current_user(request)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get intent distribution
    pipeline = [
        {"$group": {"_id": "$intent", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    intent_stats = await db.dragon_logs.aggregate(pipeline).to_list(20)
    
    # Get total commands
    total_commands = await db.dragon_logs.count_documents({})
    
    # Get unique users
    unique_users = len(await db.dragon_logs.distinct("user_id"))
    
    return {
        "total_commands": total_commands,
        "unique_users": unique_users,
        "intent_distribution": {item["_id"]: item["count"] for item in intent_stats if item["_id"]}
    }
