#!/usr/bin/env python3
"""Quick translation for helpTutorials keys only"""

import json
import os
import sys
import asyncio

sys.path.insert(0, '/app/backend')
from utils.config import EMERGENT_LLM_KEY
from emergentintegrations.llm.chat import LlmChat, UserMessage

LOCALES_DIR = "/app/frontend/src/locales"

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

async def translate_batch(texts, lang_name):
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"help-{lang_name[:3]}",
            system_message=f"""Translate UI text from English to {lang_name}. 
Return ONLY a JSON array with exactly {len(texts)} translated strings.
Keep translations short for UI. Preserve {{placeholders}}."""
        ).with_model("openai", "gpt-5.2")
        
        response = await chat.send_message(UserMessage(text=f"Translate to {lang_name}: {json.dumps(texts, ensure_ascii=False)}"))
        
        clean = response.strip()
        if "```" in clean:
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        
        return json.loads(clean.strip())
    except Exception as e:
        print(f"  ERROR: {e}")
        return None

async def process_language(lang_code, en_help):
    lang_name = LANG_NAMES.get(lang_code, lang_code)
    path = f"{LOCALES_DIR}/{lang_code}.json"
    
    with open(path, 'r') as f:
        locale = json.load(f)
    
    en_flat = flatten(en_help)
    loc_flat = flatten(locale.get('helpTutorials', {}))
    
    # Find untranslated keys
    to_translate = [(k, v) for k, v in en_flat.items() if loc_flat.get(k) == v]
    
    if not to_translate:
        print(f"  {lang_code}: Already translated")
        return 0
    
    print(f"  {lang_code}: Translating {len(to_translate)} keys...")
    
    texts = [v for _, v in to_translate]
    keys = [k for k, _ in to_translate]
    
    result = await translate_batch(texts, lang_name)
    
    if result and len(result) == len(texts):
        for i, key in enumerate(keys):
            if result[i] != texts[i]:
                loc_flat[key] = result[i]
        
        locale['helpTutorials'] = unflatten(loc_flat)
        with open(path, 'w') as f:
            json.dump(locale, f, ensure_ascii=False, indent=2)
        print(f"    -> Saved {len(result)} translations")
        return len(result)
    
    return 0

async def main():
    with open(f"{LOCALES_DIR}/en.json", 'r') as f:
        en = json.load(f)
    
    en_help = en.get('helpTutorials', {})
    print(f"Translating helpTutorials ({len(flatten(en_help))} keys) to all languages...\n")
    
    total = 0
    for lang in LANG_NAMES.keys():
        count = await process_language(lang, en_help)
        total += count
        await asyncio.sleep(0.3)
    
    print(f"\nDone! Translated {total} total keys.")

if __name__ == "__main__":
    asyncio.run(main())
