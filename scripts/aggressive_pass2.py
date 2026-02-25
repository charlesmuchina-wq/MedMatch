#!/usr/bin/env python3
"""
Aggressive second pass for languages still below 99% coverage.
Uses stronger prompts to ensure words like 'Download', 'Upload', etc. get translated.
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
    "da": "Danish", "fr": "French", "no": "Norwegian", "tl": "Filipino/Tagalog",
    "id": "Indonesian", "ro": "Romanian", "de": "German", "nl": "Dutch",
    "ms": "Malay", "fi": "Finnish", "it": "Italian", "cs": "Czech",
}

# Target only these languages that are below 99%
TARGET_LANGS = ["da", "fr", "no", "tl", "id", "ro", "de", "nl", "ms", "fi", "it", "cs"]

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


def is_skippable(k, v):
    if k in SKIP_KEYS:
        return True
    if isinstance(v, str) and v in SKIP_VALUES:
        return True
    val_str = str(v)
    if len(val_str) <= 2:
        return True
    if not any(c.isalpha() for c in val_str):
        return True
    return False


async def translate_batch(texts, target_lang, lang_name):
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"aggressive-{target_lang}",
            system_message=f"""You are translating a web application's UI into {lang_name}. 
IMPORTANT: You MUST translate EVERY string into {lang_name}. Do NOT leave any string in English.
Even common English loanwords like "Download", "Upload", "Start", "Stop", "Info", "Score", "Feedback", "Tips", "Chat", "Send", "Hybrid", "Trends", "Median", "Pause" MUST be translated to their proper {lang_name} equivalent.

Return ONLY a JSON array with exactly {len(texts)} translated strings. No explanations."""
        ).with_model("openai", "gpt-4o-mini")

        prompt = f"Translate ALL of these to {lang_name} (do NOT keep any in English):\n{json.dumps(texts, ensure_ascii=False)}"
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
        return None
    except Exception as e:
        print(f"    ERROR: {e}")
        return None


async def process_language(lang_code, english_flat):
    lang_name = LANG_NAMES.get(lang_code, lang_code)
    locale_path = f"{LOCALES_DIR}/{lang_code}.json"

    with open(locale_path, 'r', encoding='utf-8') as f:
        locale_data = json.load(f)
    locale_flat = flatten_keys(locale_data)

    to_translate = []
    for k, v in english_flat.items():
        if not is_skippable(k, v) and locale_flat.get(k) == v:
            to_translate.append((k, v))

    if not to_translate:
        print(f"  {lang_code}: Already complete!")
        return 0

    print(f"  {lang_code} ({lang_name}): {len(to_translate)} remaining keys")

    translated_count = 0
    batch_size = 25

    for i in range(0, len(to_translate), batch_size):
        batch = to_translate[i:i + batch_size]
        texts = [item[1] for item in batch]
        keys = [item[0] for item in batch]

        translated = await translate_batch(texts, lang_code, lang_name)

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
        print(f"    -> Translated {translated_count}/{len(to_translate)}")

    return translated_count


async def main():
    print("AGGRESSIVE TRANSLATION PASS 2")
    print("Target languages:", TARGET_LANGS)

    with open(f"{LOCALES_DIR}/en.json", 'r', encoding='utf-8') as f:
        english = json.load(f)
    english_flat = flatten_keys(english)

    total = 0
    for lang in TARGET_LANGS:
        count = await process_language(lang, english_flat)
        total += count

    print(f"\nTotal translated: {total}")


if __name__ == "__main__":
    asyncio.run(main())
