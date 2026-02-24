#!/usr/bin/env python3
"""
Aggressive Translation Script to reach 99%+
Specifically targets keys that are still in English
"""

import json
import os
import sys
import asyncio

sys.path.insert(0, '/app/backend')
from utils.config import EMERGENT_LLM_KEY
from emergentintegrations.llm.chat import LlmChat, UserMessage

LOCALES_DIR = "/app/frontend/src/locales"

# Words that should remain the same (brand names, tech terms)
KEEP_AS_IS = {
    'Google', 'Apple', 'LinkedIn', 'ORCID', 'Facebook', 'Twitter', 'GitHub', 'Premium',
    'PDF', 'URL', 'API', 'AI', 'Email', 'OK', 'Video', 'Audio', 'Online', 'Offline',
    'Dashboard', 'Admin', 'ID', 'PIN', 'QR', 'USB', 'GPS', 'WiFi', 'Bluetooth',
    'GxP', 'FDA', 'ISO', 'EMA', 'HIPAA', 'CSV', 'JSON', 'HTML', 'CSS', 'JavaScript',
    'min', 'max', 'x', 'N/A', 'vs', 'am', 'pm', 'KB', 'MB', 'GB', 'TB'
}

LANG_NAMES = {
    "es": "Spanish", "fr": "French", "de": "German", "ja": "Japanese",
    "zh": "Simplified Chinese", "ko": "Korean", "ar": "Arabic", "pt-BR": "Brazilian Portuguese",
    "hi": "Hindi", "it": "Italian", "nl": "Dutch", "ru": "Russian",
    "pl": "Polish", "sv": "Swedish", "tr": "Turkish", "vi": "Vietnamese",
    "sw": "Swahili", "ha": "Hausa", "yo": "Yoruba", "ig": "Igbo",
    "zu": "Zulu", "xh": "Xhosa", "af": "Afrikaans", "am": "Amharic",
    "om": "Oromo", "so": "Somali", "rw": "Kinyarwanda", "sn": "Shona",
    "ny": "Chichewa", "tw": "Twi", "wo": "Wolof", "lg": "Luganda"
}

def flatten(obj, prefix=""):
    keys = {}
    for k, v in obj.items():
        full = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            keys.update(flatten(v, full))
        else:
            keys[full] = v
    return keys

def unflatten(flat_dict):
    result = {}
    for key, value in flat_dict.items():
        parts = key.split('.')
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    return result

def should_translate(text):
    """Check if text needs translation (not a tech term/brand)"""
    clean = str(text).strip()
    if clean in KEEP_AS_IS:
        return False
    if len(clean) <= 2:
        return False
    return True

async def translate_texts(texts, lang_code, lang_name):
    """Translate a list of texts"""
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"aggressive-{lang_code}",
            system_message=f"""You are a professional UI translator. Translate English UI strings to {lang_name}.

CRITICAL RULES:
1. ALWAYS translate - never return the English text unchanged
2. Keep translations short and concise for UI buttons/labels
3. Preserve placeholders like {{{{name}}}} or {{variable}} exactly
4. Return ONLY a JSON array of translated strings
5. The array MUST have exactly {len(texts)} elements
6. Even simple words must be translated to {lang_name}"""
        ).with_model("openai", "gpt-5.2")
        
        prompt = f"Translate these {len(texts)} UI strings to {lang_name}. Return JSON array only:\n{json.dumps(texts, ensure_ascii=False)}"
        response = await chat.send_message(UserMessage(text=prompt))
        
        clean = response.strip()
        if "```" in clean:
            clean = clean.split("```")[1] if "```" in clean else clean
            if clean.startswith("json"):
                clean = clean[4:]
        clean = clean.strip()
        
        result = json.loads(clean)
        if isinstance(result, list) and len(result) == len(texts):
            return result
        return None
    except Exception as e:
        print(f"    ERROR: {e}")
        return None

async def process_language(lang_code, en_flat):
    """Process one language to maximize coverage"""
    lang_name = LANG_NAMES.get(lang_code, lang_code)
    path = f"{LOCALES_DIR}/{lang_code}.json"
    
    if not os.path.exists(path):
        return 0
    
    with open(path, 'r') as f:
        locale = json.load(f)
    locale_flat = flatten(locale)
    
    # Find keys needing translation
    to_translate = []
    for key, en_val in en_flat.items():
        loc_val = locale_flat.get(key, "")
        if loc_val == en_val and should_translate(en_val):
            to_translate.append((key, en_val))
    
    if not to_translate:
        print(f"  {lang_code}: No keys need translation")
        return 0
    
    print(f"  {lang_code} ({lang_name}): Translating {len(to_translate)} keys...")
    
    translated_count = 0
    batch_size = 20
    
    for i in range(0, len(to_translate), batch_size):
        batch = to_translate[i:i+batch_size]
        texts = [t[1] for t in batch]
        keys = [t[0] for t in batch]
        
        result = await translate_texts(texts, lang_code, lang_name)
        
        if result:
            for j, key in enumerate(keys):
                if result[j] and result[j] != texts[j]:
                    locale_flat[key] = result[j]
                    translated_count += 1
        
        await asyncio.sleep(0.3)
    
    # Save
    if translated_count > 0:
        with open(path, 'w') as f:
            json.dump(unflatten(locale_flat), f, ensure_ascii=False, indent=2)
        print(f"    -> Saved {translated_count} new translations")
    
    return translated_count

async def main():
    print("=" * 60)
    print("AGGRESSIVE TRANSLATION TO 99%")
    print("=" * 60)
    
    # Load English
    with open(f"{LOCALES_DIR}/en.json", 'r') as f:
        en = json.load(f)
    en_flat = flatten(en)
    
    print(f"Total keys: {len(en_flat)}")
    
    # Get languages sorted by priority (lowest coverage first)
    langs = ['fr', 'de', 'nl', 'sv', 'it', 'sn', 'wo', 'ny', 'ig', 'yo', 'ha', 
             'af', 'rw', 'sw', 'tw', 'so', 'om', 'lg', 'tr', 'zu', 'pt-BR',
             'ko', 'zh', 'vi', 'ja', 'ru', 'xh', 'am', 'es', 'ar', 'hi', 'pl']
    
    total = 0
    for lang in langs:
        count = await process_language(lang, en_flat)
        total += count
    
    print(f"\n{'=' * 60}")
    print(f"DONE: Translated {total} keys across all languages")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
