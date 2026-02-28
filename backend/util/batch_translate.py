#!/usr/bin/env python3
"""Batch translate i18n keys using Emergent LLM Key - robust version."""
import asyncio, json, os, sys, re

sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
from emergentintegrations.llm.chat import LlmChat, UserMessage

API_KEY = os.environ.get('EMERGENT_LLM_KEY')
LOCALES_DIR = '/app/frontend/src/locales'

LANG_MAP = {
    'af': 'Afrikaans', 'am': 'Amharic', 'ar': 'Arabic', 'bn': 'Bengali',
    'cs': 'Czech', 'da': 'Danish', 'de': 'German', 'el': 'Greek',
    'es': 'Spanish', 'fa': 'Persian', 'fi': 'Finnish', 'fr': 'French',
    'ha': 'Hausa', 'he': 'Hebrew', 'hi': 'Hindi', 'hu': 'Hungarian',
    'id': 'Indonesian', 'ig': 'Igbo', 'is': 'Icelandic', 'it': 'Italian',
    'ja': 'Japanese', 'ko': 'Korean', 'lg': 'Luganda', 'ms': 'Malay',
    'nl': 'Dutch', 'no': 'Norwegian', 'ny': 'Chichewa', 'om': 'Oromo',
    'pl': 'Polish', 'pt-BR': 'Brazilian Portuguese', 'ro': 'Romanian',
    'ru': 'Russian', 'rw': 'Kinyarwanda', 'sn': 'Shona', 'so': 'Somali',
    'sv': 'Swedish', 'sw': 'Swahili', 'ta': 'Tamil', 'th': 'Thai',
    'tl': 'Filipino/Tagalog', 'tr': 'Turkish', 'tw': 'Twi', 'uk': 'Ukrainian',
    'ur': 'Urdu', 'vi': 'Vietnamese', 'wo': 'Wolof', 'xh': 'Xhosa',
    'yo': 'Yoruba', 'zh': 'Chinese (Simplified)', 'zu': 'Zulu'
}

def extract_json(text):
    """Extract JSON from LLM response, handling markdown fences."""
    text = text.strip()
    if text.startswith('```'):
        text = re.sub(r'^```\w*\n?', '', text)
        text = re.sub(r'\n?```$', '', text)
    # Try parsing
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object
        match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
    return None

async def translate_for_lang(lang_code, lang_name, en_data, locale_data, filepath):
    """Translate all needed keys for one language."""
    keys_needing = {}
    for ns in ['karauMeet', 'candidateSearch']:
        en_ns = en_data.get(ns, {})
        locale_ns = locale_data.get(ns, {})
        for k, v in en_ns.items():
            if k in locale_ns and locale_ns[k] == v:
                keys_needing[k] = v

    if not keys_needing:
        return 0

    chat = LlmChat(
        api_key=API_KEY,
        session_id=f"t-{lang_code}-{id(keys_needing)}",
        system_message=f"You are a professional UI translator. Translate English UI strings to {lang_name}. Return ONLY a JSON object. Keep {{{{variables}}}} and HTML tags as-is. Keep technical terms (SSO, SAML, GDPR, HIPAA, AI, E2E) in English."
    ).with_model("openai", "gpt-4o-mini")

    translated_count = 0
    chunk_size = 30
    keys_list = list(keys_needing.items())

    for i in range(0, len(keys_list), chunk_size):
        chunk = dict(keys_list[i:i + chunk_size])
        prompt = json.dumps(chunk, ensure_ascii=False)

        try:
            response = await chat.send_message(UserMessage(text=prompt))
            parsed = extract_json(response)
            if parsed:
                for ns in ['karauMeet', 'candidateSearch']:
                    if ns not in locale_data:
                        locale_data[ns] = {}
                    for k, v in parsed.items():
                        if k in en_data.get(ns, {}):
                            locale_data[ns][k] = v
                            translated_count += 1
        except Exception as e:
            print(f"    {lang_code} chunk {i//chunk_size}: {e}", flush=True)

    with open(filepath, 'w') as f:
        json.dump(locale_data, f, indent=2, ensure_ascii=False)

    return translated_count

async def main():
    with open(os.path.join(LOCALES_DIR, 'en.json'), 'r') as f:
        en_data = json.load(f)

    total = len(en_data.get('karauMeet', {})) + len(en_data.get('candidateSearch', {}))
    print(f"Total English keys: {total}", flush=True)

    lang_codes = sorted(LANG_MAP.keys())

    # Process 3 languages at a time
    for i in range(0, len(lang_codes), 3):
        batch = lang_codes[i:i+3]
        print(f"\nBatch {i//3+1}: {', '.join(batch)}", flush=True)

        tasks = []
        for lc in batch:
            fp = os.path.join(LOCALES_DIR, f'{lc}.json')
            if not os.path.exists(fp):
                continue
            with open(fp, 'r') as f:
                ld = json.load(f)
            tasks.append(translate_for_lang(lc, LANG_MAP[lc], en_data, ld, fp))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        for lc, result in zip(batch, results):
            if isinstance(result, Exception):
                print(f"  {lc}: FAILED - {result}", flush=True)
            else:
                print(f"  {lc}: {result} keys translated", flush=True)

    print("\nDone!", flush=True)

if __name__ == '__main__':
    asyncio.run(main())
