"""
Priority Key Translation Script
Translates the most critical UI keys for top languages quickly.
"""

import json
import os
import asyncio
import logging
import sys

sys.path.insert(0, '/app/backend')
from utils.config import EMERGENT_LLM_KEY
from emergentintegrations.llm.chat import LlmChat, UserMessage

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

LOCALES_DIR = "/app/frontend/src/locales"

# Priority languages to translate first
PRIORITY_LANGUAGES = {
    "es": "Spanish",
    "fr": "French", 
    "de": "German",
    "ja": "Japanese",
    "zh": "Chinese",
    "ko": "Korean",
    "ar": "Arabic",
    "pt-BR": "Portuguese (Brazilian)",
    "hi": "Hindi",
    "sw": "Swahili",
    "ru": "Russian",
    "it": "Italian",
}

# Priority translation keys (most visible UI elements)
PRIORITY_KEYS = [
    # Portal Selector
    "pages.portalSelector.welcomeTo",
    "pages.portalSelector.title", 
    "pages.portalSelector.subtitle",
    "pages.portalSelector.medmatchAI",
    "pages.portalSelector.jobToolkit",
    "pages.portalSelector.jobToolkitDesc",
    "pages.portalSelector.resumeParser",
    "pages.portalSelector.aiJobMatching",
    "pages.portalSelector.recruiterNetwork",
    "pages.portalSelector.enterJobToolkit",
    "pages.portalSelector.aiKarau",
    "pages.portalSelector.meetingPortal",
    "pages.portalSelector.meetingPortalDesc",
    "pages.portalSelector.hdVideoAudio",
    "pages.portalSelector.aiTranscription",
    "pages.portalSelector.e2eEncrypted",
    "pages.portalSelector.enterMeetingPortal",
    "pages.portalSelector.poweredByAI",
    "pages.portalSelector.trustedBy",
    # Common UI
    "common.loading",
    "common.save",
    "common.cancel",
    "common.delete",
    "common.edit",
    "common.search",
    "common.submit",
    "common.close",
    "common.back",
    "common.next",
    "common.settings",
    "common.profile",
    "common.logout",
    "common.login",
    "common.signup",
    # Navigation
    "nav.dashboard",
    "nav.myResume",
    "nav.jobSearch",
    "nav.savedJobs",
    "nav.applications",
    "nav.messages",
    "nav.notifications",
    # Auth
    "auth.email",
    "auth.password",
    "auth.signIn",
    "auth.signUp",
    "auth.forgotPassword",
    "auth.continueWithGoogle",
    "auth.noAccount",
    "auth.haveAccount",
]

def get_nested_value(obj, key):
    """Get value from nested dict using dot notation"""
    parts = key.split('.')
    val = obj
    for part in parts:
        if isinstance(val, dict) and part in val:
            val = val[part]
        else:
            return None
    return val

def set_nested_value(obj, key, value):
    """Set value in nested dict using dot notation"""
    parts = key.split('.')
    for part in parts[:-1]:
        if part not in obj:
            obj[part] = {}
        obj = obj[part]
    obj[parts[-1]] = value

async def translate_batch(texts, target_lang, lang_name):
    """Translate a batch of texts"""
    if not EMERGENT_LLM_KEY or not texts:
        return texts
    
    try:
        import uuid
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=str(uuid.uuid4()),
            system_message=f"""Translate these UI strings to {lang_name}. Keep translations concise for UI buttons/labels. Preserve placeholders like {{{{name}}}} exactly. Return ONLY a JSON array of translated strings."""
        ).with_model("openai", "gpt-5.2")
        
        response = await chat.send_message(UserMessage(text=f"Translate to {lang_name}: {json.dumps(texts, ensure_ascii=False)}"))
        
        clean = response.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        
        result = json.loads(clean)
        if isinstance(result, list) and len(result) == len(texts):
            return result
    except Exception as e:
        logger.error(f"Translation error: {e}")
    
    return texts

async def translate_language(lang_code, lang_name):
    """Translate priority keys for a single language"""
    locale_path = f"{LOCALES_DIR}/{lang_code}.json"
    
    if not os.path.exists(locale_path):
        logger.warning(f"  ⚠️ {lang_code}: File not found")
        return 0
    
    # Load files
    with open(f"{LOCALES_DIR}/en.json", 'r', encoding='utf-8') as f:
        english = json.load(f)
    
    with open(locale_path, 'r', encoding='utf-8') as f:
        locale_data = json.load(f)
    
    # Find keys that need translation (same as English or missing)
    keys_to_translate = []
    for key in PRIORITY_KEYS:
        en_val = get_nested_value(english, key)
        locale_val = get_nested_value(locale_data, key)
        
        if en_val and (locale_val is None or locale_val == en_val):
            keys_to_translate.append((key, en_val))
    
    if not keys_to_translate:
        logger.info(f"  ✓ {lang_code}: All priority keys translated")
        return 0
    
    logger.info(f"  → {lang_code}: Translating {len(keys_to_translate)} priority keys...")
    
    # Translate in one batch (since we limited to ~50 priority keys)
    texts = [item[1] for item in keys_to_translate]
    keys = [item[0] for item in keys_to_translate]
    
    translated = await translate_batch(texts, lang_code, lang_name)
    
    # Update locale data
    count = 0
    for i, key in enumerate(keys):
        if translated[i] != texts[i]:
            set_nested_value(locale_data, key, translated[i])
            count += 1
    
    # Save
    with open(locale_path, 'w', encoding='utf-8') as f:
        json.dump(locale_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"  ✅ {lang_code}: Translated {count} keys")
    return count

async def main():
    print("=" * 50)
    print("Priority UI Translation")
    print("=" * 50)
    print(f"Translating {len(PRIORITY_KEYS)} priority keys")
    print(f"For {len(PRIORITY_LANGUAGES)} languages")
    print()
    
    total = 0
    for lang_code, lang_name in PRIORITY_LANGUAGES.items():
        try:
            count = await translate_language(lang_code, lang_name)
            total += count
        except Exception as e:
            logger.error(f"  ❌ {lang_code}: Error - {e}")
    
    print()
    print("=" * 50)
    print(f"Total translations: {total}")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
