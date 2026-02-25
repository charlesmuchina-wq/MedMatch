#!/usr/bin/env python3
"""
Final Translation Sweep
Translates remaining same-as-English keys across all languages.
Skips brand names, placeholders, and technical terms that should stay in English.
"""

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

# Keys that should NOT be translated (brand names, placeholders, technical terms)
SKIP_KEYS = {
    "nav.dragonAutomator", "nav.enterpriseAPI",
    "auth.google", "auth.apple",
    "auth.emailPlaceholder", "auth.passwordPlaceholder", "auth.phonePlaceholder",
    "membership.premium", "membership.enterprise", "membership.recruiterPro",
    "scheduling.meetingLinkPlaceholder",
    "helpTutorials.neuralVoice",
    "pages.portalSelector.title", "pages.portalSelector.medmatchAI", "pages.portalSelector.aiKarau",
    "pages.dragonAutomator.title",
    "pages.globalCompliance.gdpr", "pages.globalCompliance.ccpa",
    "pages.globalCompliance.hipaa", "pages.globalCompliance.soc2",
    "language.genderNeutral",
}

# Values that should stay as-is (email patterns, phone patterns, tech terms)
SKIP_VALUES = {
    "you@example.com", "••••••••", "+1 (555) 123-4567",
    "https://zoom.us/j/...", "GDPR", "CCPA", "HIPAA", "SOC 2",
    "MedMatch-AI KARAU", "MedMatch AI", "AI KARAU", "KARAU Automator",
    "Microsoft Neural Voice", "Google", "Apple",
}


def flatten_keys(obj, prefix=""):
    keys = {}
    for k, v in obj.items():
        full_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            keys.update(flatten_keys(v, full_key))
        else:
            keys[full_key] = v
    return keys


def unflatten_keys(flat_dict):
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


def should_translate(key, value):
    """Check if a key/value pair should be translated"""
    if key in SKIP_KEYS:
        return False
    if value in SKIP_VALUES:
        return False
    # Skip very short values (1-2 chars) that are likely abbreviations
    if len(str(value)) <= 2:
        return False
    # Skip values that are just numbers or special characters
    if not any(c.isalpha() for c in str(value)):
        return False
    return True


async def translate_batch(texts, keys, target_lang, lang_name):
    """Translate a batch of texts using AI"""
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"final-sweep-{target_lang}",
            system_message=f"""You are a professional UI translator. Translate these English UI strings to {lang_name}.

RULES:
1. Keep translations concise (suitable for UI buttons/labels)
2. Preserve ALL placeholders like {{{{name}}}}, {{{{count}}}}, etc.
3. Keep brand names like MedMatch, KARAU as-is
4. For technical terms commonly used in the target language, use the local equivalent
5. If a word is commonly used in English in {lang_name} (like 'Download', 'Upload'), still translate it to the proper {lang_name} term
6. Return ONLY a valid JSON array of translated strings with the same length as input. No explanations."""
        ).with_model("openai", "gpt-4o-mini")

        prompt = f"Translate these {len(texts)} UI strings to {lang_name}:\n{json.dumps(texts, ensure_ascii=False)}"
        response = await chat.send_message(UserMessage(text=prompt))

        clean = response.strip()
        if clean.startswith("```"):
            lines = clean.split("```")
            clean = lines[1] if len(lines) > 1 else clean
            if clean.startswith("json"):
                clean = clean[4:]
        clean = clean.strip()

        translated = json.loads(clean)

        if isinstance(translated, list) and len(translated) == len(texts):
            return translated
        else:
            print(f"    WARNING: Length mismatch for {lang_name}: got {len(translated)}, expected {len(texts)}")
            return None

    except Exception as e:
        print(f"    ERROR: {lang_name}: {e}")
        return None


async def process_language(lang_code, english_flat):
    """Process a single language"""
    lang_name = LANG_NAMES.get(lang_code, lang_code)
    locale_path = f"{LOCALES_DIR}/{lang_code}.json"

    if not os.path.exists(locale_path):
        return 0

    with open(locale_path, 'r', encoding='utf-8') as f:
        locale_data = json.load(f)
    locale_flat = flatten_keys(locale_data)

    # Find translatable keys that are same as English
    to_translate = []
    for key, en_value in english_flat.items():
        locale_value = locale_flat.get(key)
        if locale_value == en_value and should_translate(key, en_value):
            to_translate.append((key, en_value))

    if not to_translate:
        return 0

    print(f"  {lang_code} ({lang_name}): {len(to_translate)} keys to translate")

    translated_count = 0
    batch_size = 20

    for i in range(0, len(to_translate), batch_size):
        batch = to_translate[i:i + batch_size]
        texts = [item[1] for item in batch]
        keys = [item[0] for item in batch]

        translated = await translate_batch(texts, keys, lang_code, lang_name)

        if translated:
            for j, key in enumerate(keys):
                if translated[j] and translated[j] != texts[j]:
                    locale_flat[key] = translated[j]
                    translated_count += 1

        await asyncio.sleep(0.3)

    if translated_count > 0:
        updated_data = unflatten_keys(locale_flat)
        with open(locale_path, 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=2)
        print(f"    -> Translated {translated_count}/{len(to_translate)} keys")

    return translated_count


async def main():
    print("=" * 60)
    print("FINAL TRANSLATION SWEEP")
    print("=" * 60)

    with open(f"{LOCALES_DIR}/en.json", 'r', encoding='utf-8') as f:
        english = json.load(f)
    english_flat = flatten_keys(english)
    print(f"Total UI keys: {len(english_flat)}")

    locale_files = sorted([
        f.replace('.json', '') for f in os.listdir(LOCALES_DIR)
        if f.endswith('.json') and f not in ['en.json', 'pseudo.json']
    ])
    print(f"Languages: {len(locale_files)}\n")

    total = 0
    for lang_code in locale_files:
        count = await process_language(lang_code, english_flat)
        total += count

    print(f"\nCOMPLETED: Translated {total} keys total")


if __name__ == "__main__":
    asyncio.run(main())
