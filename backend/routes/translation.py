"""
Translation Routes
Handles: Language detection, text translation, multi-language support
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import logging
import json

from emergentintegrations.llm.chat import LlmChat, UserMessage

from utils.database import db
from utils.config import EMERGENT_LLM_KEY
from routes.auth import get_current_user

router = APIRouter(prefix="/translate", tags=["Translation"])

# ============== Supported Languages ==============

SUPPORTED_LANGUAGES = {
    # EFIGS Foundation (Core Global Reach)
    "en": {"name": "English", "native": "English", "flag": "🇺🇸"},
    "en-GB": {"name": "English (UK)", "native": "English (UK)", "flag": "🇬🇧"},
    "en-IE": {"name": "English (Ireland)", "native": "English (Ireland)", "flag": "🇮🇪"},
    "en-SG": {"name": "English (Singapore)", "native": "English (Singapore)", "flag": "🇸🇬"},
    "es": {"name": "Spanish", "native": "Español", "flag": "🇪🇸"},
    "fr": {"name": "French", "native": "Français", "flag": "🇫🇷"},
    "de": {"name": "German", "native": "Deutsch", "flag": "🇩🇪"},
    "it": {"name": "Italian", "native": "Italiano", "flag": "🇮🇹"},
    
    # CJK Growth Block (High Spend)
    "zh": {"name": "Chinese (Simplified)", "native": "简体中文", "flag": "🇨🇳"},
    "zh-TW": {"name": "Chinese (Traditional)", "native": "繁體中文", "flag": "🇹🇼"},
    "ja": {"name": "Japanese", "native": "日本語", "flag": "🇯🇵"},
    "ko": {"name": "Korean", "native": "한국어", "flag": "🇰🇷"},
    
    # Rapidly Expanding Markets
    "hi": {"name": "Hindi", "native": "हिन्दी", "flag": "🇮🇳"},
    "pt-BR": {"name": "Portuguese (Brazilian)", "native": "Português (Brasil)", "flag": "🇧🇷"},
    "pt": {"name": "Portuguese (European)", "native": "Português (Portugal)", "flag": "🇵🇹"},
    "ar": {"name": "Arabic", "native": "العربية", "flag": "🇸🇦"},
    "ar-AE": {"name": "Arabic (UAE)", "native": "العربية (الإمارات)", "flag": "🇦🇪"},
    "ar-EG": {"name": "Arabic (Egypt)", "native": "العربية (مصر)", "flag": "🇪🇬"},
    
    # Nordic Languages
    "no": {"name": "Norwegian", "native": "Norsk", "flag": "🇳🇴"},
    "sv": {"name": "Swedish", "native": "Svenska", "flag": "🇸🇪"},
    "da": {"name": "Danish", "native": "Dansk", "flag": "🇩🇰"},
    "fi": {"name": "Finnish", "native": "Suomi", "flag": "🇫🇮"},
    "is": {"name": "Icelandic", "native": "Íslenska", "flag": "🇮🇸"},
    
    # Additional High-Value Languages
    "nl": {"name": "Dutch", "native": "Nederlands", "flag": "🇳🇱"},
    "ru": {"name": "Russian", "native": "Русский", "flag": "🇷🇺"},
    "bn": {"name": "Bengali", "native": "বাংলা", "flag": "🇧🇩"},
    "vi": {"name": "Vietnamese", "native": "Tiếng Việt", "flag": "🇻🇳"},
    "th": {"name": "Thai", "native": "ไทย", "flag": "🇹🇭"},
    "id": {"name": "Indonesian", "native": "Bahasa Indonesia", "flag": "🇮🇩"},
    "ms": {"name": "Malay", "native": "Bahasa Melayu", "flag": "🇲🇾"},
    "tl": {"name": "Filipino", "native": "Filipino", "flag": "🇵🇭"},
    "pl": {"name": "Polish", "native": "Polski", "flag": "🇵🇱"},
    "uk": {"name": "Ukrainian", "native": "Українська", "flag": "🇺🇦"},
    "tr": {"name": "Turkish", "native": "Türkçe", "flag": "🇹🇷"},
    "he": {"name": "Hebrew", "native": "עברית", "flag": "🇮🇱"},
    "cs": {"name": "Czech", "native": "Čeština", "flag": "🇨🇿"},
    "ro": {"name": "Romanian", "native": "Română", "flag": "🇷🇴"},
    "hu": {"name": "Hungarian", "native": "Magyar", "flag": "🇭🇺"},
    "el": {"name": "Greek", "native": "Ελληνικά", "flag": "🇬🇷"},
    
    # Additional Emerging Markets
    "ta": {"name": "Tamil", "native": "தமிழ்", "flag": "🇮🇳"},
    "te": {"name": "Telugu", "native": "తెలుగు", "flag": "🇮🇳"},
    "mr": {"name": "Marathi", "native": "मराठी", "flag": "🇮🇳"},
    "ur": {"name": "Urdu", "native": "اردو", "flag": "🇵🇰"},
    "fa": {"name": "Persian (Farsi)", "native": "فارسی", "flag": "🇮🇷"},
    
    # African Languages
    "sw": {"name": "Swahili", "native": "Kiswahili", "flag": "🇰🇪"},
    "ha": {"name": "Hausa", "native": "Hausa", "flag": "🇳🇬"},
    "yo": {"name": "Yoruba", "native": "Yorùbá", "flag": "🇳🇬"},
    "ig": {"name": "Igbo", "native": "Igbo", "flag": "🇳🇬"},
    "zu": {"name": "Zulu", "native": "isiZulu", "flag": "🇿🇦"},
    "xh": {"name": "Xhosa", "native": "isiXhosa", "flag": "🇿🇦"},
    "af": {"name": "Afrikaans", "native": "Afrikaans", "flag": "🇿🇦"},
    "am": {"name": "Amharic", "native": "አማርኛ", "flag": "🇪🇹"},
    "om": {"name": "Oromo", "native": "Oromoo", "flag": "🇪🇹"},
    "so": {"name": "Somali", "native": "Soomaali", "flag": "🇸🇴"},
    "rw": {"name": "Kinyarwanda", "native": "Kinyarwanda", "flag": "🇷🇼"},
    "sn": {"name": "Shona", "native": "chiShona", "flag": "🇿🇼"},
    "ny": {"name": "Chichewa", "native": "Chichewa", "flag": "🇲🇼"},
    "tw": {"name": "Twi", "native": "Twi", "flag": "🇬🇭"},
    "wo": {"name": "Wolof", "native": "Wolof", "flag": "🇸🇳"},
    "lg": {"name": "Luganda", "native": "Luganda", "flag": "🇺🇬"},
}

# ============== Models ==============

class TranslateRequest(BaseModel):
    text: str
    target_language: str
    source_language: Optional[str] = None  # Auto-detect if not provided

class DetectLanguageRequest(BaseModel):
    text: str

class BatchTranslateRequest(BaseModel):
    texts: List[str]
    target_language: str
    source_language: Optional[str] = None

class TranslateJobRequest(BaseModel):
    job_id: str
    target_language: str

class TranslateCoverLetterRequest(BaseModel):
    cover_letter: str
    target_language: str
    job_title: str = ""
    company: str = ""

# ============== Routes ==============

@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    return {
        "languages": [
            {"code": code, **info} 
            for code, info in SUPPORTED_LANGUAGES.items()
        ],
        "total": len(SUPPORTED_LANGUAGES)
    }

@router.post("/detect")
async def detect_language(data: DetectLanguageRequest):
    """Detect the language of given text"""
    if not data.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="Translation service not configured")
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=str(uuid.uuid4()),
            system_message="""You are a language detection expert. Analyze the given text and identify its language.

Return ONLY valid JSON:
{
    "detected_language": "<ISO 639-1 code>",
    "language_name": "<full language name>",
    "confidence": <0.0-1.0>,
    "script": "<writing script used>",
    "is_mixed": <true if multiple languages detected>
}"""
        ).with_model("openai", "gpt-5.2")
        
        response = await chat.send_message(UserMessage(text=f"Detect the language of this text:\n\n{data.text[:1000]}"))
        
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        result = json.loads(clean_response)
        
        # Add language info if we have it
        lang_code = result.get("detected_language", "").lower()
        if lang_code in SUPPORTED_LANGUAGES:
            result["language_info"] = SUPPORTED_LANGUAGES[lang_code]
        
        return result
        
    except Exception as e:
        logging.error(f"Language detection error: {e}")
        raise HTTPException(status_code=500, detail="Failed to detect language")

@router.post("/text")
async def translate_text(data: TranslateRequest, request: Request):
    """Translate text to target language"""
    if not data.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    
    if data.target_language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {data.target_language}")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="Translation service not configured")
    
    target_lang_name = SUPPORTED_LANGUAGES[data.target_language]["name"]
    source_lang_name = SUPPORTED_LANGUAGES.get(data.source_language, {}).get("name", "auto-detect")
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=str(uuid.uuid4()),
            system_message=f"""You are an expert translator. Translate the given text to {target_lang_name}.

Rules:
- Maintain the original meaning and tone
- Preserve formatting (paragraphs, bullet points, etc.)
- Keep proper nouns, company names, and technical terms as appropriate
- For professional/job-related content, use formal language

Return ONLY valid JSON:
{{
    "translated_text": "<translated text>",
    "source_language": "<detected source language code>",
    "target_language": "{data.target_language}",
    "notes": "<any translation notes or cultural adaptations made>"
}}"""
        ).with_model("openai", "gpt-5.2")
        
        prompt = f"Translate this text to {target_lang_name}"
        if data.source_language:
            prompt += f" from {source_lang_name}"
        prompt += f":\n\n{data.text}"
        
        response = await chat.send_message(UserMessage(text=prompt))
        
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        result = json.loads(clean_response)
        
        # Log translation for analytics
        user = await get_current_user(request)
        await log_translation(user, data.source_language, data.target_language, len(data.text))
        
        return result
        
    except Exception as e:
        logging.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to translate text")

@router.post("/batch")
async def batch_translate(data: BatchTranslateRequest, request: Request):
    """Translate multiple texts at once"""
    # Handle empty array gracefully - return empty translations
    if not data.texts or len(data.texts) == 0:
        return {
            "translations": [],
            "target_language": data.target_language,
            "count": 0
        }
    
    # Filter out empty strings
    data.texts = [t for t in data.texts if t and t.strip()]
    if not data.texts:
        return {
            "translations": [],
            "target_language": data.target_language,
            "count": 0
        }
    
    if len(data.texts) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 texts per batch")
    
    if data.target_language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {data.target_language}")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="Translation service not configured")
    
    target_lang_name = SUPPORTED_LANGUAGES[data.target_language]["name"]
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=str(uuid.uuid4()),
            system_message=f"""You are an expert translator. Translate all given texts to {target_lang_name}.

Return ONLY valid JSON array:
[
    {{"original": "<original text>", "translated": "<translated text>"}},
    ...
]"""
        ).with_model("openai", "gpt-5.2")
        
        texts_formatted = "\n".join([f"{i+1}. {text}" for i, text in enumerate(data.texts)])
        response = await chat.send_message(UserMessage(text=f"Translate these texts to {target_lang_name}:\n\n{texts_formatted}"))
        
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        results = json.loads(clean_response)
        
        return {
            "translations": results,
            "target_language": data.target_language,
            "count": len(results)
        }
        
    except Exception as e:
        logging.error(f"Batch translation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to translate texts")

@router.post("/cover-letter")
async def translate_cover_letter(data: TranslateCoverLetterRequest, request: Request):
    """Translate a cover letter with professional formatting"""
    if not data.cover_letter.strip():
        raise HTTPException(status_code=400, detail="Cover letter is required")
    
    if data.target_language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {data.target_language}")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="Translation service not configured")
    
    target_lang_name = SUPPORTED_LANGUAGES[data.target_language]["name"]
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=str(uuid.uuid4()),
            system_message=f"""You are an expert translator specializing in professional business correspondence.
Translate the cover letter to {target_lang_name} while:
- Maintaining professional tone appropriate for {target_lang_name}-speaking job markets
- Adapting formal salutations and closings to local conventions
- Keeping company names and job titles in their original form unless they have standard translations
- Preserving the structure and formatting

Return ONLY valid JSON:
{{
    "translated_cover_letter": "<translated cover letter>",
    "cultural_notes": ["<note about cultural adaptations made>"],
    "formal_salutation": "<appropriate formal greeting in target language>",
    "formal_closing": "<appropriate formal closing in target language>"
}}"""
        ).with_model("openai", "gpt-5.2")
        
        context = f"Translate this cover letter to {target_lang_name}"
        if data.job_title:
            context += f" for a {data.job_title} position"
        if data.company:
            context += f" at {data.company}"
        context += f":\n\n{data.cover_letter}"
        
        response = await chat.send_message(UserMessage(text=context))
        
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        result = json.loads(clean_response)
        result["target_language"] = data.target_language
        result["language_info"] = SUPPORTED_LANGUAGES[data.target_language]
        
        return result
        
    except Exception as e:
        logging.error(f"Cover letter translation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to translate cover letter")

@router.post("/job-description")
async def translate_job_description(data: Dict[str, Any], request: Request):
    """Translate a job description"""
    job = data.get("job", {})
    target_language = data.get("target_language", "en")
    
    if not job:
        raise HTTPException(status_code=400, detail="Job data is required")
    
    if target_language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {target_language}")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="Translation service not configured")
    
    target_lang_name = SUPPORTED_LANGUAGES[target_language]["name"]
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=str(uuid.uuid4()),
            system_message=f"""You are an expert translator for job postings.
Translate the job details to {target_lang_name} while:
- Keeping company name and location unchanged
- Translating job title to common equivalent in target language
- Translating description and requirements clearly

Return ONLY valid JSON:
{{
    "title": "<translated job title>",
    "description": "<translated description>",
    "requirements": ["<translated requirement>"],
    "benefits": ["<translated benefit if present>"]
}}"""
        ).with_model("openai", "gpt-5.2")
        
        job_text = f"""
Title: {job.get('title', '')}
Description: {job.get('description', '')}
"""
        
        response = await chat.send_message(UserMessage(
            text=f"Translate this job posting to {target_lang_name}:\n{job_text}"
        ))
        
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        result = json.loads(clean_response)
        
        # Preserve original fields
        result["company"] = job.get("company", "")
        result["location"] = job.get("location", "")
        result["url"] = job.get("url", "")
        result["original_title"] = job.get("title", "")
        result["target_language"] = target_language
        
        return result
        
    except Exception as e:
        logging.error(f"Job description translation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to translate job description")

@router.post("/resume-section")
async def translate_resume_section(data: Dict[str, Any], request: Request):
    """Translate a section of a resume"""
    section_type = data.get("section_type", "")  # summary, experience, education, skills
    content = data.get("content", "")
    target_language = data.get("target_language", "en")
    
    if not content:
        raise HTTPException(status_code=400, detail="Content is required")
    
    if target_language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {target_language}")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="Translation service not configured")
    
    target_lang_name = SUPPORTED_LANGUAGES[target_language]["name"]
    
    section_instructions = {
        "summary": "Translate the professional summary, maintaining impact and professional tone.",
        "experience": "Translate work experience, keeping company names unchanged but translating job titles and descriptions.",
        "education": "Translate education details, keeping institution names unchanged.",
        "skills": "Translate skill names where appropriate, keeping technical terms in English if commonly used."
    }
    
    instruction = section_instructions.get(section_type, "Translate professionally.")
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=str(uuid.uuid4()),
            system_message=f"""You are a professional resume translator.
{instruction}

Return ONLY valid JSON:
{{
    "translated_content": "<translated content>",
    "section_type": "{section_type}",
    "formatting_notes": "<any notes about formatting or localization>"
}}"""
        ).with_model("openai", "gpt-5.2")
        
        response = await chat.send_message(UserMessage(
            text=f"Translate this resume {section_type} section to {target_lang_name}:\n\n{content}"
        ))
        
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        result = json.loads(clean_response)
        result["target_language"] = target_language
        
        return result
        
    except Exception as e:
        logging.error(f"Resume translation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to translate resume section")

@router.get("/user-preference")
async def get_user_language_preference(request: Request):
    """Get user's preferred language"""
    user = await get_current_user(request)
    if not user:
        return {"preferred_language": "en", "is_default": True}
    
    pref = await db.user_preferences.find_one(
        {"user_id": user["user_id"]},
        {"_id": 0, "preferred_language": 1}
    )
    
    return {
        "preferred_language": pref.get("preferred_language", "en") if pref else "en",
        "is_default": not pref or "preferred_language" not in pref
    }

@router.put("/user-preference")
async def set_user_language_preference(data: Dict[str, str], request: Request):
    """Set user's preferred language"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    language = data.get("language", "en")
    if language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {language}")
    
    await db.user_preferences.update_one(
        {"user_id": user["user_id"]},
        {"$set": {
            "preferred_language": language,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )
    
    return {
        "message": "Language preference updated",
        "preferred_language": language,
        "language_info": SUPPORTED_LANGUAGES[language]
    }

# Priority UI keys that should be pre-rendered server-side
PRIORITY_UI_KEYS = [
    # Navigation
    "Dashboard", "My Resume", "Resume Profiles", "Skill Tests", "Job Search",
    "Saved Jobs", "Applications", "My Interviews", "Interview Calendar",
    "Success Predictor", "Interview Prep", "Q&A Practice", "Video Practice",
    "Voice Coach", "Cover Letter", "Job Alerts", "Analytics", "Messages",
    "Settings", "Profile", "Sign Out", "Sign In",
    # Dashboard
    "Welcome to MedMatch", "Quick Actions", "Upload Resume", "Search Jobs",
    "Interviews", "Skills", "AI Powered", "Recommended next steps",
    # Common
    "Loading...", "Save", "Cancel", "Delete", "Edit", "Search", "Submit",
    "Close", "Back", "Next", "Confirm", "Yes", "No", "Error", "Success"
]

@router.get("/prerender/{language}")
async def get_prerendered_translations(language: str, request: Request):
    """
    PA-3: Server-side pre-rendered translations
    Returns essential UI translations for instant page load
    """
    if language not in SUPPORTED_LANGUAGES and language != "en":
        raise HTTPException(status_code=400, detail=f"Unsupported language: {language}")
    
    # For English or bundled languages, no pre-rendering needed
    bundled_languages = ["en", "es", "fr", "zh", "de"]
    if language in bundled_languages:
        return {
            "language": language,
            "is_bundled": True,
            "translations": {},
            "message": "Language is bundled, no pre-rendering needed"
        }
    
    # Check cache first
    cache_key = f"prerender:{language}"
    cached = await db.translation_cache.find_one(
        {"cache_key": cache_key},
        {"_id": 0, "translations": 1, "cached_at": 1}
    )
    
    # Use cached translations if less than 24 hours old
    if cached:
        cached_at = cached.get("cached_at", "")
        if cached_at:
            try:
                cache_time = datetime.fromisoformat(cached_at.replace("Z", "+00:00"))
                if (datetime.now(timezone.utc) - cache_time).total_seconds() < 86400:  # 24 hours
                    return {
                        "language": language,
                        "is_bundled": False,
                        "translations": cached.get("translations", {}),
                        "from_cache": True,
                        "language_info": SUPPORTED_LANGUAGES.get(language, {})
                    }
            except:
                pass
    
    if not EMERGENT_LLM_KEY:
        return {
            "language": language,
            "is_bundled": False,
            "translations": {},
            "error": "Translation service not configured"
        }
    
    # Generate translations for priority keys
    target_lang_name = SUPPORTED_LANGUAGES[language]["name"]
    translations = {}
    
    try:
        # Translate in batches of 15
        for i in range(0, len(PRIORITY_UI_KEYS), 15):
            batch = PRIORITY_UI_KEYS[i:i+15]
            
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=str(uuid.uuid4()),
                system_message=f"""You are an expert UI translator. Translate all UI strings to {target_lang_name}.
Return ONLY valid JSON array:
[{{"original": "<original text>", "translated": "<translated text>"}}]"""
            ).with_model("openai", "gpt-5.2")
            
            texts_formatted = "\n".join([f"{j+1}. {text}" for j, text in enumerate(batch)])
            response = await chat.send_message(UserMessage(text=f"Translate:\n{texts_formatted}"))
            
            clean_response = response.strip()
            if clean_response.startswith("```"):
                clean_response = clean_response.split("```")[1]
                if clean_response.startswith("json"):
                    clean_response = clean_response[4:]
            
            results = json.loads(clean_response)
            for item in results:
                translations[item["original"]] = item["translated"]
        
        # Cache the translations
        await db.translation_cache.update_one(
            {"cache_key": cache_key},
            {"$set": {
                "cache_key": cache_key,
                "language": language,
                "translations": translations,
                "cached_at": datetime.now(timezone.utc).isoformat()
            }},
            upsert=True
        )
        
        return {
            "language": language,
            "is_bundled": False,
            "translations": translations,
            "from_cache": False,
            "language_info": SUPPORTED_LANGUAGES.get(language, {})
        }
        
    except Exception as e:
        logging.error(f"Pre-render translation error: {e}")
        return {
            "language": language,
            "is_bundled": False,
            "translations": {},
            "error": str(e)
        }

# ============== Helper Functions ==============

async def log_translation(user: Optional[Dict], source_lang: str, target_lang: str, char_count: int):
    """Log translation for analytics"""
    try:
        log_doc = {
            "id": str(uuid.uuid4()),
            "user_id": user["user_id"] if user else None,
            "source_language": source_lang,
            "target_language": target_lang,
            "character_count": char_count,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await db.translation_logs.insert_one(log_doc)
    except Exception as e:
        logging.error(f"Failed to log translation: {e}")

@router.get("/analytics")
async def get_translation_analytics(request: Request):
    """Get translation usage analytics (admin only)"""
    user = await get_current_user(request)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Most used target languages
    pipeline = [
        {"$group": {"_id": "$target_language", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    lang_stats = await db.translation_logs.aggregate(pipeline).to_list(10)
    
    # Total translations
    total = await db.translation_logs.count_documents({})
    
    # Total characters
    char_pipeline = [
        {"$group": {"_id": None, "total_chars": {"$sum": "$character_count"}}}
    ]
    char_result = await db.translation_logs.aggregate(char_pipeline).to_list(1)
    total_chars = char_result[0]["total_chars"] if char_result else 0
    
    return {
        "total_translations": total,
        "total_characters": total_chars,
        "top_languages": [
            {"language": item["_id"], "count": item["count"], "info": SUPPORTED_LANGUAGES.get(item["_id"], {})}
            for item in lang_stats if item["_id"]
        ]
    }
