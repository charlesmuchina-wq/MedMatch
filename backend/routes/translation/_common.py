"""
Translation Routes
Handles: Language detection, text translation, multi-language support
"""

# Auto-split shared module. Imports, models, constants, helpers, singletons.

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

from routes.auth import get_current_user, require_auth

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

class TMXImportRequest(BaseModel):
    tmx_content: str
    overwrite_existing: bool = False
