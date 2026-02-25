#!/usr/bin/env python3
"""Translate karauMeet keys to all languages"""
import json, os, sys, asyncio
sys.path.insert(0, '/app/backend')
from utils.config import EMERGENT_LLM_KEY
from emergentintegrations.llm.chat import LlmChat, UserMessage

LOCALES_DIR = "/app/frontend/src/locales"

with open(f"{LOCALES_DIR}/en.json") as f:
    en_data = json.load(f)
new_keys = en_data["karauMeet"]

LANG_NAMES = {
    "es": "Spanish", "fr": "French", "de": "German", "ja": "Japanese",
    "zh": "Chinese (Simplified)", "ko": "Korean", "ar": "Arabic", "pt-BR": "Brazilian Portuguese",
    "hi": "Hindi", "it": "Italian", "nl": "Dutch", "ru": "Russian",
    "pl": "Polish", "sv": "Swedish", "tr": "Turkish", "vi": "Vietnamese",
    "sw": "Swahili", "ha": "Hausa", "yo": "Yoruba", "ig": "Igbo",
    "zu": "Zulu", "xh": "Xhosa", "af": "Afrikaans", "am": "Amharic",
    "om": "Oromo", "so": "Somali", "rw": "Kinyarwanda", "sn": "Shona",
    "ny": "Chichewa", "tw": "Twi", "wo": "Wolof", "lg": "Luganda",
    "uk": "Ukrainian", "no": "Norwegian", "da": "Danish", "fi": "Finnish",
    "th": "Thai", "id": "Indonesian", "bn": "Bengali", "he": "Hebrew",
    "cs": "Czech", "el": "Greek", "fa": "Persian/Farsi", "hu": "Hungarian",
    "is": "Icelandic", "ms": "Malay", "ro": "Romanian", "ta": "Tamil",
    "tl": "Filipino/Tagalog", "ur": "Urdu",
}

async def translate_lang(lang_code, lang_name, keys_dict):
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"karau-dash-{lang_code}",
            system_message=f"Translate UI strings to {lang_name}. Keep {{{{name}}}} placeholders. Return ONLY valid JSON object with same keys."
        ).with_model("openai", "gpt-4o-mini")
        response = await chat.send_message(UserMessage(text=f"Translate to {lang_name}:\n{json.dumps(keys_dict, ensure_ascii=False)}"))
        clean = response.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"): clean = clean[4:]
        return json.loads(clean.strip())
    except Exception as e:
        print(f"  ERROR {lang_code}: {e}", flush=True)
        return None

async def main():
    locale_files = sorted([
        f.replace('.json', '') for f in os.listdir(LOCALES_DIR)
        if f.endswith('.json') and f not in ['en.json', 'pseudo.json']
    ])
    
    total = 0
    for lang_code in locale_files:
        lang_name = LANG_NAMES.get(lang_code, lang_code)
        fpath = f"{LOCALES_DIR}/{lang_code}.json"
        with open(fpath, 'r') as f:
            lang_data = json.load(f)
        
        existing = lang_data.get("karauMeet", {})
        missing = {k: v for k, v in new_keys.items() if k not in existing or existing[k] == v}
        if not missing:
            print(f"  {lang_code}: SKIP (done)", flush=True)
            continue
        
        print(f"  {lang_code} ({lang_name}): {len(missing)} keys...", flush=True)
        translated = await translate_lang(lang_code, lang_name, missing)
        
        if translated:
            if "karauMeet" not in lang_data:
                lang_data["karauMeet"] = {}
            lang_data["karauMeet"].update(translated)
            with open(fpath, 'w') as f:
                json.dump(lang_data, f, ensure_ascii=False, indent=2)
            total += len(translated)
            print(f"    -> OK ({len(translated)} keys)", flush=True)
        
        await asyncio.sleep(0.3)
    
    print(f"\nCOMPLETE: {total} translations", flush=True)

asyncio.run(main())
