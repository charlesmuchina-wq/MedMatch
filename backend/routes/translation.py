"""
Translation Routes
Handles: Language detection, text translation, multi-language support
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
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

# ============== Linguistic Gender Rules (CLDR-based) ==============
# Languages that require grammatical gender agreement
# 'has_gender': whether the language uses grammatical gender for adjectives/verbs
# 'genders': available grammatical genders in the language
# 'default': default gender to use when user preference is not set

LANGUAGE_GENDER_RULES = {
    # Romance Languages (masculine/feminine)
    "es": {"has_gender": True, "genders": ["masculine", "feminine"], "default": "masculine"},
    "fr": {"has_gender": True, "genders": ["masculine", "feminine"], "default": "masculine"},
    "it": {"has_gender": True, "genders": ["masculine", "feminine"], "default": "masculine"},
    "pt": {"has_gender": True, "genders": ["masculine", "feminine"], "default": "masculine"},
    "pt-BR": {"has_gender": True, "genders": ["masculine", "feminine"], "default": "masculine"},
    "ro": {"has_gender": True, "genders": ["masculine", "feminine", "neuter"], "default": "masculine"},
    
    # Germanic Languages
    "de": {"has_gender": True, "genders": ["masculine", "feminine", "neuter"], "default": "masculine"},
    "nl": {"has_gender": True, "genders": ["common", "neuter"], "default": "common"},
    
    # Slavic Languages
    "ru": {"has_gender": True, "genders": ["masculine", "feminine", "neuter"], "default": "masculine"},
    "pl": {"has_gender": True, "genders": ["masculine", "feminine", "neuter"], "default": "masculine"},
    "uk": {"has_gender": True, "genders": ["masculine", "feminine", "neuter"], "default": "masculine"},
    "cs": {"has_gender": True, "genders": ["masculine", "feminine", "neuter"], "default": "masculine"},
    
    # Semitic Languages
    "ar": {"has_gender": True, "genders": ["masculine", "feminine"], "default": "masculine"},
    "ar-AE": {"has_gender": True, "genders": ["masculine", "feminine"], "default": "masculine"},
    "ar-EG": {"has_gender": True, "genders": ["masculine", "feminine"], "default": "masculine"},
    "he": {"has_gender": True, "genders": ["masculine", "feminine"], "default": "masculine"},
    
    # Other Gendered Languages
    "el": {"has_gender": True, "genders": ["masculine", "feminine", "neuter"], "default": "masculine"},
    "hi": {"has_gender": True, "genders": ["masculine", "feminine"], "default": "masculine"},
    "ur": {"has_gender": True, "genders": ["masculine", "feminine"], "default": "masculine"},
    
    # African Languages with Gender
    "sw": {"has_gender": True, "genders": ["noun_class"], "default": None},  # Bantu noun classes
    "zu": {"has_gender": True, "genders": ["noun_class"], "default": None},
    "xh": {"has_gender": True, "genders": ["noun_class"], "default": None},
    "af": {"has_gender": False, "genders": [], "default": None},  # No grammatical gender
    "am": {"has_gender": True, "genders": ["masculine", "feminine"], "default": "masculine"},
    "ha": {"has_gender": True, "genders": ["masculine", "feminine"], "default": "masculine"},
    "yo": {"has_gender": False, "genders": [], "default": None},  # No grammatical gender
    "ig": {"has_gender": False, "genders": [], "default": None},
    
    # Non-gendered Languages (explicit for reference)
    "en": {"has_gender": False, "genders": [], "default": None},
    "en-GB": {"has_gender": False, "genders": [], "default": None},
    "zh": {"has_gender": False, "genders": [], "default": None},
    "ja": {"has_gender": False, "genders": [], "default": None},
    "ko": {"has_gender": False, "genders": [], "default": None},
    "vi": {"has_gender": False, "genders": [], "default": None},
    "th": {"has_gender": False, "genders": [], "default": None},
    "id": {"has_gender": False, "genders": [], "default": None},
    "ms": {"has_gender": False, "genders": [], "default": None},
    "tr": {"has_gender": False, "genders": [], "default": None},
    "fi": {"has_gender": False, "genders": [], "default": None},
    "hu": {"has_gender": False, "genders": [], "default": None},
}

# ============== Models ==============

class TranslateRequest(BaseModel):
    text: str
    target_language: str
    source_language: Optional[str] = None  # Auto-detect if not provided
    grammatical_gender: Optional[str] = None  # For gender-aware translation

class DetectLanguageRequest(BaseModel):
    text: str

class BatchTranslateRequest(BaseModel):
    texts: List[str]
    target_language: str
    source_language: Optional[str] = None
    grammatical_gender: Optional[str] = None  # For gender-aware translation

class TranslateJobRequest(BaseModel):
    job_id: str
    target_language: str

class TranslateCoverLetterRequest(BaseModel):
    cover_letter: str
    target_language: str
    job_title: str = ""
    company: str = ""

class GenderAwareTranslateRequest(BaseModel):
    """Request for gender-aware translation following ICU MessageFormat"""
    text: str
    target_language: str
    grammatical_gender: str  # 'masculine', 'feminine', 'neutral'
    context: Optional[str] = None  # Additional context for accurate translation

class GenderVariantsRequest(BaseModel):
    """Request to get all gender variants of a translation"""
    text: str
    target_language: str

# ============== Routes ==============

@router.get("/gender-rules")
async def get_gender_rules():
    """Get linguistic gender rules for all supported languages (CLDR-based)"""
    return {
        "rules": LANGUAGE_GENDER_RULES,
        "description": {
            "has_gender": "Whether the language uses grammatical gender",
            "genders": "Available grammatical genders in the language",
            "default": "Default gender when user preference is not set"
        },
        "gendered_languages": [
            code for code, rules in LANGUAGE_GENDER_RULES.items() 
            if rules.get("has_gender")
        ],
        "total_gendered": sum(1 for rules in LANGUAGE_GENDER_RULES.values() if rules.get("has_gender"))
    }

@router.get("/gender-rules/{language}")
async def get_language_gender_rule(language: str):
    """Get gender rules for a specific language"""
    if language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=404, detail=f"Language {language} not supported")
    
    rules = LANGUAGE_GENDER_RULES.get(language, {"has_gender": False, "genders": [], "default": None})
    return {
        "language": language,
        "language_info": SUPPORTED_LANGUAGES[language],
        **rules,
        "requires_gender_selection": rules.get("has_gender", False) and len(rules.get("genders", [])) > 1
    }

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

# ============== CLDR Translation Memory (TMX Standard) ==============

@router.post("/memory/store")
async def store_translation_memory(data: Dict[str, Any], request: Request):
    """
    CLDR TMX-compliant Translation Memory storage
    Stores verified translations for consistency and reuse
    """
    source_text = data.get("source_text", "").strip()
    target_text = data.get("target_text", "").strip()
    source_lang = data.get("source_language", "en")
    target_lang = data.get("target_language", "")
    context = data.get("context", "")  # UI context: nav, dashboard, common, etc.
    
    if not source_text or not target_text or not target_lang:
        raise HTTPException(status_code=400, detail="source_text, target_text, and target_language are required")
    
    if target_lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {target_lang}")
    
    # Create TMX-compliant translation unit (TU)
    tu_id = f"{source_lang}:{target_lang}:{hash(source_text) % 10**8}"
    
    tm_entry = {
        "tu_id": tu_id,
        "source_language": source_lang,
        "target_language": target_lang,
        "source_text": source_text,
        "target_text": target_text,
        "context": context,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "usage_count": 1,
        "verified": False,
        "cldr_locale": target_lang
    }
    
    # Upsert to avoid duplicates
    existing = await db.translation_memory.find_one({"tu_id": tu_id})
    if existing:
        await db.translation_memory.update_one(
            {"tu_id": tu_id},
            {"$set": {"target_text": target_text, "updated_at": datetime.now(timezone.utc).isoformat()}, 
             "$inc": {"usage_count": 1}}
        )
    else:
        await db.translation_memory.insert_one(tm_entry)
    
    return {"message": "Translation stored in memory", "tu_id": tu_id}

@router.get("/memory/lookup")
async def lookup_translation_memory(
    source_text: str,
    target_language: str,
    source_language: str = "en",
    request: Request = None
):
    """
    CLDR TMX-compliant Translation Memory lookup
    Returns exact and fuzzy matches from translation memory
    """
    if not source_text or not target_language:
        raise HTTPException(status_code=400, detail="source_text and target_language are required")
    
    # Exact match
    exact_match = await db.translation_memory.find_one(
        {
            "source_language": source_language,
            "target_language": target_language,
            "source_text": source_text
        },
        {"_id": 0}
    )
    
    if exact_match:
        # Increment usage count
        await db.translation_memory.update_one(
            {"tu_id": exact_match["tu_id"]},
            {"$inc": {"usage_count": 1}}
        )
        return {
            "match_type": "exact",
            "confidence": 100,
            "translation": exact_match["target_text"],
            "tu_id": exact_match["tu_id"],
            "usage_count": exact_match.get("usage_count", 1)
        }
    
    # Fuzzy match (simplified - words overlap)
    words = set(source_text.lower().split())
    if len(words) >= 2:
        # Find similar entries
        similar = await db.translation_memory.find(
            {
                "source_language": source_language,
                "target_language": target_language,
            },
            {"_id": 0}
        ).to_list(100)
        
        best_match = None
        best_score = 0
        
        for entry in similar:
            entry_words = set(entry["source_text"].lower().split())
            overlap = len(words & entry_words)
            total = len(words | entry_words)
            score = (overlap / total * 100) if total > 0 else 0
            
            if score > best_score and score >= 50:  # 50% minimum threshold
                best_score = score
                best_match = entry
        
        if best_match:
            return {
                "match_type": "fuzzy",
                "confidence": round(best_score),
                "translation": best_match["target_text"],
                "tu_id": best_match["tu_id"],
                "source_matched": best_match["source_text"]
            }
    
    return {
        "match_type": "none",
        "confidence": 0,
        "translation": None
    }

@router.get("/memory/stats")
async def get_translation_memory_stats(request: Request):
    """Get Translation Memory statistics"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Total entries
    total_entries = await db.translation_memory.count_documents({})
    
    # By language
    lang_pipeline = [
        {"$group": {"_id": "$target_language", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 20}
    ]
    by_language = await db.translation_memory.aggregate(lang_pipeline).to_list(20)
    
    # By context
    context_pipeline = [
        {"$group": {"_id": "$context", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    by_context = await db.translation_memory.aggregate(context_pipeline).to_list(10)
    
    # Most used translations
    most_used_pipeline = [
        {"$sort": {"usage_count": -1}},
        {"$limit": 10},
        {"$project": {"_id": 0, "source_text": 1, "target_language": 1, "usage_count": 1}}
    ]
    most_used = await db.translation_memory.aggregate(most_used_pipeline).to_list(10)
    
    return {
        "total_entries": total_entries,
        "by_language": [
            {"language": item["_id"], "count": item["count"], "info": SUPPORTED_LANGUAGES.get(item["_id"], {})}
            for item in by_language if item["_id"]
        ],
        "by_context": [
            {"context": item["_id"] or "general", "count": item["count"]}
            for item in by_context
        ],
        "most_used": most_used
    }

@router.post("/memory/bulk-store")
async def bulk_store_translation_memory(data: Dict[str, Any], request: Request):
    """
    Bulk store translations in memory (for pre-population)
    """
    user = await get_current_user(request)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    translations = data.get("translations", [])
    target_language = data.get("target_language", "")
    source_language = data.get("source_language", "en")
    context = data.get("context", "ui")
    
    if not translations or not target_language:
        raise HTTPException(status_code=400, detail="translations array and target_language are required")
    
    stored_count = 0
    for item in translations:
        source = item.get("source", "")
        target = item.get("target", "")
        
        if source and target:
            tu_id = f"{source_language}:{target_language}:{hash(source) % 10**8}"
            
            await db.translation_memory.update_one(
                {"tu_id": tu_id},
                {"$set": {
                    "tu_id": tu_id,
                    "source_language": source_language,
                    "target_language": target_language,
                    "source_text": source,
                    "target_text": target,
                    "context": context,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "verified": True,
                    "cldr_locale": target_language
                }},
                upsert=True
            )
            stored_count += 1
    
    return {
        "message": f"Stored {stored_count} translations in memory",
        "target_language": target_language
    }

# ============== Enhanced Analytics Dashboard ==============

@router.get("/analytics/dashboard")
async def get_analytics_dashboard(request: Request):
    """
    Comprehensive translation analytics dashboard
    """
    user = await get_current_user(request)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Translation logs stats
    total_translations = await db.translation_logs.count_documents({})
    
    # Character count
    char_pipeline = [
        {"$group": {"_id": None, "total": {"$sum": "$character_count"}}}
    ]
    char_result = await db.translation_logs.aggregate(char_pipeline).to_list(1)
    total_characters = char_result[0]["total"] if char_result else 0
    
    # Top languages
    lang_pipeline = [
        {"$group": {"_id": "$target_language", "count": {"$sum": 1}, "chars": {"$sum": "$character_count"}}},
        {"$sort": {"count": -1}},
        {"$limit": 15}
    ]
    top_languages = await db.translation_logs.aggregate(lang_pipeline).to_list(15)
    
    # Pre-render cache stats
    cache_count = await db.translation_cache.count_documents({})
    
    # Translation Memory stats
    tm_count = await db.translation_memory.count_documents({})
    
    # Daily usage (last 7 days)
    from datetime import timedelta
    seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    daily_pipeline = [
        {"$match": {"timestamp": {"$gte": seven_days_ago}}},
        {"$group": {
            "_id": {"$substr": ["$timestamp", 0, 10]},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    daily_usage = await db.translation_logs.aggregate(daily_pipeline).to_list(7)
    
    return {
        "summary": {
            "total_translations": total_translations,
            "total_characters": total_characters,
            "cache_entries": cache_count,
            "memory_entries": tm_count
        },
        "top_languages": [
            {
                "language": item["_id"],
                "translations": item["count"],
                "characters": item.get("chars", 0),
                "info": SUPPORTED_LANGUAGES.get(item["_id"], {})
            }
            for item in top_languages if item["_id"]
        ],
        "daily_usage": [
            {"date": item["_id"], "count": item["count"]}
            for item in daily_usage
        ],
        "cldr_compliance": {
            "tmx_enabled": True,
            "locale_support": len(SUPPORTED_LANGUAGES),
            "rtl_languages": ["ar", "he", "fa", "ur"],
            "bundled_languages": ["en", "es", "fr", "de", "zh", "ja", "ar", "hi", "pt-BR"]
        }
    }

# ============== Translation Quality Scoring ==============

class TranslationQualityScorer:
    """
    CLDR-compliant Translation Quality Scoring System
    Evaluates translations based on:
    1. Completeness - All content translated
    2. Consistency - Similar phrases translated similarly
    3. Formatting - Proper punctuation and structure
    4. Length ratio - Target length appropriate for source
    """
    
    # Expected length ratios by language (target/source)
    LENGTH_RATIOS = {
        "ja": (0.5, 1.5),   # Japanese can be shorter
        "zh": (0.4, 1.2),   # Chinese is compact
        "ar": (0.8, 1.5),   # Arabic similar to English
        "hi": (0.9, 1.6),   # Hindi can be longer
        "de": (1.0, 1.5),   # German often longer
        "es": (1.0, 1.3),   # Spanish slightly longer
        "fr": (1.0, 1.4),   # French slightly longer
        "pt-BR": (1.0, 1.4), # Portuguese similar to Spanish
        "default": (0.5, 2.0)
    }
    
    @staticmethod
    def score_completeness(source: str, target: str) -> float:
        """Check if translation is complete (not empty, not same as source)"""
        if not target or not target.strip():
            return 0.0
        if target.strip() == source.strip():
            return 0.3  # Might be intentional (brand names)
        return 1.0
    
    @staticmethod
    def score_length_ratio(source: str, target: str, target_lang: str) -> float:
        """Check if target length is appropriate for the language"""
        if not source or not target:
            return 0.0
        
        ratio = len(target) / len(source) if len(source) > 0 else 0
        min_ratio, max_ratio = TranslationQualityScorer.LENGTH_RATIOS.get(
            target_lang, 
            TranslationQualityScorer.LENGTH_RATIOS["default"]
        )
        
        if min_ratio <= ratio <= max_ratio:
            return 1.0
        elif ratio < min_ratio:
            return max(0.3, ratio / min_ratio)
        else:
            return max(0.3, max_ratio / ratio)
    
    @staticmethod
    def score_formatting(source: str, target: str) -> float:
        """Check formatting consistency (punctuation, capitalization)"""
        score = 1.0
        
        # Check ending punctuation
        source_ends = source.strip()[-1] if source.strip() else ""
        target_ends = target.strip()[-1] if target.strip() else ""
        
        if source_ends in ".!?" and target_ends not in ".!?。！？":
            score -= 0.2
        
        # Check for placeholder preservation {{}}
        import re
        source_placeholders = set(re.findall(r'\{\{.*?\}\}', source))
        target_placeholders = set(re.findall(r'\{\{.*?\}\}', target))
        
        if source_placeholders and source_placeholders != target_placeholders:
            score -= 0.3
        
        return max(0.0, score)
    
    @classmethod
    def calculate_score(cls, source: str, target: str, target_lang: str) -> dict:
        """Calculate overall quality score"""
        completeness = cls.score_completeness(source, target)
        length = cls.score_length_ratio(source, target, target_lang)
        formatting = cls.score_formatting(source, target)
        
        # Weighted average
        overall = (completeness * 0.4) + (length * 0.3) + (formatting * 0.3)
        
        return {
            "overall_score": round(overall * 100),
            "completeness": round(completeness * 100),
            "length_ratio": round(length * 100),
            "formatting": round(formatting * 100),
            "quality_level": "excellent" if overall >= 0.9 else "good" if overall >= 0.7 else "fair" if overall >= 0.5 else "poor"
        }

@router.post("/quality/score")
async def score_translation_quality(data: Dict[str, Any], request: Request):
    """
    Score the quality of a translation
    """
    source_text = data.get("source_text", "")
    target_text = data.get("target_text", "")
    target_language = data.get("target_language", "")
    
    if not source_text or not target_text or not target_language:
        raise HTTPException(status_code=400, detail="source_text, target_text, and target_language are required")
    
    score = TranslationQualityScorer.calculate_score(source_text, target_text, target_language)
    
    # Store quality score in DB for analytics
    await db.translation_quality.insert_one({
        "source_text": source_text[:100],
        "target_text": target_text[:100],
        "target_language": target_language,
        "scores": score,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return {
        "source_text": source_text,
        "target_text": target_text,
        "target_language": target_language,
        "quality": score
    }

@router.post("/quality/batch-score")
async def batch_score_translations(data: Dict[str, Any], request: Request):
    """
    Score quality of multiple translations at once
    """
    translations = data.get("translations", [])
    target_language = data.get("target_language", "")
    
    if not translations or not target_language:
        raise HTTPException(status_code=400, detail="translations array and target_language are required")
    
    results = []
    total_score = 0
    
    for item in translations:
        source = item.get("source", "")
        target = item.get("target", "")
        
        if source and target:
            score = TranslationQualityScorer.calculate_score(source, target, target_language)
            total_score += score["overall_score"]
            results.append({
                "source": source[:50],
                "target": target[:50],
                "quality": score
            })
    
    avg_score = total_score / len(results) if results else 0
    
    return {
        "target_language": target_language,
        "translations_scored": len(results),
        "average_score": round(avg_score),
        "quality_level": "excellent" if avg_score >= 90 else "good" if avg_score >= 70 else "fair" if avg_score >= 50 else "poor",
        "results": results[:20]  # Limit response size
    }

@router.get("/quality/stats")
async def get_quality_stats(request: Request):
    """
    Get translation quality statistics
    """
    user = await get_current_user(request)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Overall quality by language
    quality_pipeline = [
        {"$group": {
            "_id": "$target_language",
            "avg_score": {"$avg": "$scores.overall_score"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 20}
    ]
    by_language = await db.translation_quality.aggregate(quality_pipeline).to_list(20)
    
    # Quality distribution
    distribution_pipeline = [
        {"$bucket": {
            "groupBy": "$scores.overall_score",
            "boundaries": [0, 50, 70, 90, 101],
            "default": "unknown",
            "output": {"count": {"$sum": 1}}
        }}
    ]
    distribution = await db.translation_quality.aggregate(distribution_pipeline).to_list(10)
    
    # Total scored
    total_scored = await db.translation_quality.count_documents({})
    
    return {
        "total_scored": total_scored,
        "by_language": [
            {
                "language": item["_id"],
                "average_score": round(item["avg_score"]) if item["avg_score"] else 0,
                "count": item["count"],
                "quality_level": "excellent" if item["avg_score"] and item["avg_score"] >= 90 else "good" if item["avg_score"] and item["avg_score"] >= 70 else "fair"
            }
            for item in by_language if item["_id"]
        ],
        "quality_distribution": [
            {
                "range": f"{dist['_id']}-{dist['_id']+20 if dist['_id'] < 90 else 100}" if isinstance(dist['_id'], int) else "unknown",
                "count": dist["count"],
                "level": "poor" if dist['_id'] == 0 else "fair" if dist['_id'] == 50 else "good" if dist['_id'] == 70 else "excellent"
            }
            for dist in distribution if isinstance(dist.get('_id'), int)
        ]
    }

# ============== Enhanced Translation Memory Analytics ==============

@router.get("/memory/analytics")
async def get_memory_analytics(request: Request):
    """
    Comprehensive Translation Memory analytics with CLDR metrics
    """
    user = await get_current_user(request)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Total entries
    total_entries = await db.translation_memory.count_documents({})
    verified_entries = await db.translation_memory.count_documents({"verified": True})
    
    # Usage statistics
    usage_pipeline = [
        {"$group": {
            "_id": None,
            "total_usage": {"$sum": "$usage_count"},
            "avg_usage": {"$avg": "$usage_count"},
            "max_usage": {"$max": "$usage_count"}
        }}
    ]
    usage_stats = await db.translation_memory.aggregate(usage_pipeline).to_list(1)
    
    # Top used translations
    top_used_pipeline = [
        {"$sort": {"usage_count": -1}},
        {"$limit": 15},
        {"$project": {
            "_id": 0,
            "source_text": 1,
            "target_text": 1,
            "target_language": 1,
            "usage_count": 1,
            "context": 1
        }}
    ]
    top_used = await db.translation_memory.aggregate(top_used_pipeline).to_list(15)
    
    # Coverage by language
    coverage_pipeline = [
        {"$group": {
            "_id": "$target_language",
            "entries": {"$sum": 1},
            "verified": {"$sum": {"$cond": ["$verified", 1, 0]}},
            "total_usage": {"$sum": "$usage_count"}
        }},
        {"$sort": {"entries": -1}},
        {"$limit": 20}
    ]
    by_language = await db.translation_memory.aggregate(coverage_pipeline).to_list(20)
    
    # Context distribution
    context_pipeline = [
        {"$group": {
            "_id": "$context",
            "count": {"$sum": 1},
            "usage": {"$sum": "$usage_count"}
        }},
        {"$sort": {"count": -1}}
    ]
    by_context = await db.translation_memory.aggregate(context_pipeline).to_list(10)
    
    # Recent additions (last 7 days)
    seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    recent_count = await db.translation_memory.count_documents({
        "created_at": {"$gte": seven_days_ago}
    })
    
    return {
        "summary": {
            "total_entries": total_entries,
            "verified_entries": verified_entries,
            "verification_rate": round((verified_entries / total_entries * 100) if total_entries > 0 else 0),
            "recent_additions": recent_count
        },
        "usage": {
            "total_lookups": usage_stats[0]["total_usage"] if usage_stats else 0,
            "average_per_entry": round(usage_stats[0]["avg_usage"], 1) if usage_stats else 0,
            "most_used_count": usage_stats[0]["max_usage"] if usage_stats else 0
        },
        "top_translations": top_used,
        "by_language": [
            {
                "language": item["_id"],
                "entries": item["entries"],
                "verified": item["verified"],
                "total_usage": item["total_usage"],
                "info": SUPPORTED_LANGUAGES.get(item["_id"], {})
            }
            for item in by_language if item["_id"]
        ],
        "by_context": [
            {
                "context": item["_id"] or "general",
                "entries": item["count"],
                "usage": item["usage"]
            }
            for item in by_context
        ],
        "cldr_metrics": {
            "tmx_version": "1.4",
            "supported_locales": len(SUPPORTED_LANGUAGES),
            "bundled_locales": 9,  # Updated count
            "rtl_support": True,
            "pluralization": False,  # Future enhancement
            "gender_forms": False   # Future enhancement
        }
    }


