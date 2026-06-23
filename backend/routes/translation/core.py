# Auto-split route group: core

from fastapi import APIRouter

from ._common import *  # noqa: F401,F403



router = APIRouter()



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
    """Translate text to target language with optional gender-awareness"""
    if not data.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    
    if data.target_language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {data.target_language}")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="Translation service not configured")
    
    target_lang_name = SUPPORTED_LANGUAGES[data.target_language]["name"]
    source_lang_name = SUPPORTED_LANGUAGES.get(data.source_language, {}).get("name", "auto-detect")
    
    # Get gender rules for target language
    gender_rules = LANGUAGE_GENDER_RULES.get(data.target_language, {"has_gender": False})
    gender_instruction = ""
    
    if gender_rules.get("has_gender") and data.grammatical_gender:
        gender_instruction = f"""
- IMPORTANT: This text addresses a {data.grammatical_gender} person. Use {data.grammatical_gender} grammatical forms for:
  * Adjectives that agree with the addressee
  * Past participles that agree with the addressee
  * Pronouns referring to the addressee
  * Any other grammatical elements that require gender agreement"""
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=str(uuid.uuid4()),
            system_message=f"""You are an expert translator specializing in grammatically correct, gender-aware translations. Translate the given text to {target_lang_name}.

Rules:
- Maintain the original meaning and tone
- Preserve formatting (paragraphs, bullet points, etc.)
- Keep proper nouns, company names, and technical terms as appropriate
- For professional/job-related content, use formal language{gender_instruction}

Return ONLY valid JSON:
{{
    "translated_text": "<translated text>",
    "source_language": "<detected source language code>",
    "target_language": "{data.target_language}",
    "gender_applied": "{data.grammatical_gender or 'none'}",
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
        user = await require_auth(request)
        await log_translation(user, data.source_language, data.target_language, len(data.text))
        
        return result
        
    except Exception as e:
        logging.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to translate text")

@router.post("/gender-aware")
async def translate_gender_aware(data: GenderAwareTranslateRequest, request: Request):
    """
    Translate text with explicit gender-awareness following ICU MessageFormat principles.
    
    This endpoint is specifically designed for UI strings that address the user directly,
    ensuring grammatically correct gender agreement in gendered languages.
    
    Examples of affected text:
    - "You are connected" -> Spanish: "Estás conectado" (m) / "Estás conectada" (f)
    - "Welcome back" -> French: "Bienvenu" (m) / "Bienvenue" (f)
    """
    if not data.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    
    if data.target_language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {data.target_language}")
    
    if data.grammatical_gender not in ['masculine', 'feminine', 'neutral']:
        raise HTTPException(status_code=400, detail="grammatical_gender must be 'masculine', 'feminine', or 'neutral'")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="Translation service not configured")
    
    gender_rules = LANGUAGE_GENDER_RULES.get(data.target_language, {"has_gender": False})
    target_lang_name = SUPPORTED_LANGUAGES[data.target_language]["name"]
    
    # If language doesn't have grammatical gender, do normal translation
    if not gender_rules.get("has_gender"):
        try:
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=str(uuid.uuid4()),
                system_message=f"Translate to {target_lang_name}. Return only the translated text, nothing else."
            ).with_model("openai", "gpt-5.2")
            
            response = await chat.send_message(UserMessage(text=data.text))
            
            return {
                "original": data.text,
                "translated": response.strip(),
                "target_language": data.target_language,
                "grammatical_gender": data.grammatical_gender,
                "gender_applied": False,
                "reason": "Target language does not use grammatical gender"
            }
        except Exception as e:
            logging.error(f"Translation error: {e}")
            raise HTTPException(status_code=500, detail="Failed to translate text")
    
    # Gender-aware translation for gendered languages
    try:
        context_note = f"\nContext: {data.context}" if data.context else ""
        
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=str(uuid.uuid4()),
            system_message=f"""You are an expert linguist specializing in grammatically correct, gender-aware translations.

TASK: Translate the text to {target_lang_name} using {data.grammatical_gender} grammatical forms.

GENDER AGREEMENT RULES:
- Use {data.grammatical_gender} forms for ALL grammatical elements that agree with the person being addressed:
  * Adjectives (e.g., Spanish: conectado/conectada, French: bienvenu/bienvenue)
  * Past participles
  * Pronouns
  * Articles where applicable
  * Verb endings in languages where verbs agree with gender

IMPORTANT:
- This text addresses or refers to a {data.grammatical_gender} person
- Ensure ALL gender-agreeing elements are consistently {data.grammatical_gender}
- Maintain formal/professional tone for job-related content{context_note}

Return ONLY valid JSON:
{{
    "translated": "<translated text with {data.grammatical_gender} gender agreement>",
    "gender_markers": ["<list of words where gender was applied>"],
    "confidence": <0.0-1.0 confidence in correct gender application>
}}"""
        ).with_model("openai", "gpt-5.2")
        
        response = await chat.send_message(UserMessage(text=f"Translate: {data.text}"))
        
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        result = json.loads(clean_response)
        
        return {
            "original": data.text,
            "translated": result.get("translated", ""),
            "target_language": data.target_language,
            "grammatical_gender": data.grammatical_gender,
            "gender_applied": True,
            "gender_markers": result.get("gender_markers", []),
            "confidence": result.get("confidence", 0.9)
        }
        
    except Exception as e:
        logging.error(f"Gender-aware translation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to translate text")

@router.post("/gender-variants")
async def get_gender_variants(data: GenderVariantsRequest, request: Request):
    """
    Get all gender variants of a translation for gendered languages.
    
    Useful for:
    - Pre-generating all variants for static UI strings
    - Building translation memory with gender variants
    - Quality assurance of gender-aware translations
    
    Returns masculine, feminine, and neutral (where applicable) variants.
    """
    if not data.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    
    if data.target_language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {data.target_language}")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="Translation service not configured")
    
    gender_rules = LANGUAGE_GENDER_RULES.get(data.target_language, {"has_gender": False})
    target_lang_name = SUPPORTED_LANGUAGES[data.target_language]["name"]
    
    # If language doesn't have grammatical gender
    if not gender_rules.get("has_gender"):
        try:
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=str(uuid.uuid4()),
                system_message=f"Translate to {target_lang_name}. Return only the translated text."
            ).with_model("openai", "gpt-5.2")
            
            response = await chat.send_message(UserMessage(text=data.text))
            translated = response.strip()
            
            return {
                "original": data.text,
                "target_language": data.target_language,
                "has_gender": False,
                "variants": {
                    "default": translated
                }
            }
        except Exception as e:
            logging.error(f"Translation error: {e}")
            raise HTTPException(status_code=500, detail="Failed to translate text")
    
    # Get all gender variants for gendered languages
    available_genders = gender_rules.get("genders", ["masculine", "feminine"])
    
    try:
        gender_list = ", ".join(available_genders)
        
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=str(uuid.uuid4()),
            system_message=f"""You are an expert linguist. Translate the text to {target_lang_name} providing ALL gender variants.

TASK: Provide translations for each grammatical gender: {gender_list}

For each variant:
- Apply correct gender agreement to adjectives, participles, pronouns
- Maintain identical meaning across variants
- Only the gender-agreeing elements should differ

Return ONLY valid JSON:
{{
    "variants": {{
        "<gender>": "<translated text with that gender agreement>",
        ...for each gender in [{gender_list}]
    }},
    "differences": ["<list of words/phrases that differ between genders>"],
    "neutral_possible": <true if a gender-neutral version exists>
}}"""
        ).with_model("openai", "gpt-5.2")
        
        response = await chat.send_message(UserMessage(text=f"Translate with all gender variants: {data.text}"))
        
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        result = json.loads(clean_response)
        
        return {
            "original": data.text,
            "target_language": data.target_language,
            "has_gender": True,
            "available_genders": available_genders,
            "variants": result.get("variants", {}),
            "differences": result.get("differences", []),
            "neutral_possible": result.get("neutral_possible", False)
        }
        
    except Exception as e:
        logging.error(f"Gender variants error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get gender variants")

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
    user = await require_auth(request)
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
    user = await require_auth(request)
    
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
            except Exception:
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
