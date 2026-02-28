"""
Propagate new i18n keys from en.json to all other locale files.
Uses Emergent LLM Key + OpenAI for translation.
"""
import json
import os
import asyncio
import time

LOCALES_DIR = "/app/frontend/src/locales"
EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY", "sk-emergent-e19D7A22f3f2b9f8a0")

LANG_MAP = {
    "af": "Afrikaans", "am": "Amharic", "ar": "Arabic", "bn": "Bengali",
    "cs": "Czech", "da": "Danish", "de": "German", "el": "Greek",
    "es": "Spanish", "et": "Estonian", "fa": "Persian", "fi": "Finnish",
    "fil": "Filipino", "fr": "French", "ga": "Irish", "gu": "Gujarati",
    "ha": "Hausa", "he": "Hebrew", "hi": "Hindi", "hu": "Hungarian",
    "id": "Indonesian", "ig": "Igbo", "is": "Icelandic", "it": "Italian",
    "ja": "Japanese", "ko": "Korean", "ml": "Malayalam", "mr": "Marathi",
    "ms": "Malay", "ne": "Nepali", "nl": "Dutch", "no": "Norwegian",
    "pa": "Punjabi", "pl": "Polish", "pt": "Portuguese", "ro": "Romanian",
    "ru": "Russian", "si": "Sinhala", "sk": "Slovak", "so": "Somali",
    "sv": "Swedish", "sw": "Swahili", "ta": "Tamil", "te": "Telugu",
    "th": "Thai", "tr": "Turkish", "uk": "Ukrainian", "ur": "Urdu",
    "vi": "Vietnamese", "yo": "Yoruba", "zh": "Chinese", "zu": "Zulu"
}


def get_missing_keys(en_data, locale_data):
    missing = {}
    for section, values in en_data.items():
        if isinstance(values, dict):
            locale_section = locale_data.get(section, {})
            if isinstance(locale_section, dict):
                for key, val in values.items():
                    if key not in locale_section:
                        missing.setdefault(section, {})[key] = val
    return missing


async def translate_batch(missing_keys, lang_name, lang_code):
    from emergentintegrations.llm.chat import LlmChat, UserMessage

    flat = {}
    for section, keys in missing_keys.items():
        for key, val in keys.items():
            flat[f"{section}.{key}"] = val

    if not flat:
        return {}

    prompt = f"""Translate these English UI strings to {lang_name} ({lang_code}).
Return ONLY a JSON object mapping the SAME keys to translated values.
Keep technical terms, brand names (KARAU, AI, Q&A) untranslated.
Keep translations concise for UI display.

{json.dumps(flat, indent=2)}"""

    try:
        chat = LlmChat(
            api_key=EMERGENT_KEY,
            session_id=f'tr-{lang_code}',
            system_message='You are a professional UI translator. Return only valid JSON, no markdown code blocks.'
        ).with_model('openai', 'gpt-4o-mini')

        resp = await chat.send_message(UserMessage(text=prompt))
        text = resp.strip() if isinstance(resp, str) else str(resp)

        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]

        result = json.loads(text)
        translated = {}
        for dotkey, val in result.items():
            parts = dotkey.split(".", 1)
            if len(parts) == 2:
                translated.setdefault(parts[0], {})[parts[1]] = val
        return translated
    except Exception as e:
        print(f"  Translation error for {lang_code}: {e}")
        return {}


async def main():
    en_path = os.path.join(LOCALES_DIR, "en.json")
    en_data = json.load(open(en_path, "r"))

    total_updated = 0
    for fname in sorted(os.listdir(LOCALES_DIR)):
        if fname == "en.json" or not fname.endswith(".json"):
            continue

        code = fname.replace(".json", "")
        lang_name = LANG_MAP.get(code, code)
        fpath = os.path.join(LOCALES_DIR, fname)

        locale_data = json.load(open(fpath, "r"))
        missing = get_missing_keys(en_data, locale_data)
        total_missing = sum(len(v) for v in missing.values())

        if total_missing == 0:
            print(f"  {code}: Up to date")
            continue

        print(f"  {code} ({lang_name}): {total_missing} missing...", end=" ", flush=True)

        translated = await translate_batch(missing, lang_name, code)
        if translated:
            for section, keys in translated.items():
                if section not in locale_data:
                    locale_data[section] = {}
                locale_data[section].update(keys)
            added = sum(len(v) for v in translated.values())
            print(f"OK ({added})")
            total_updated += added
        else:
            for section, keys in missing.items():
                if section not in locale_data:
                    locale_data[section] = {}
                locale_data[section].update(keys)
            print(f"Fallback ({total_missing})")
            total_updated += total_missing

        json.dump(locale_data, open(fpath, "w"), ensure_ascii=False, indent=2)
        await asyncio.sleep(0.3)

    print(f"\nDone! Updated {total_updated} translations.")


if __name__ == "__main__":
    asyncio.run(main())
