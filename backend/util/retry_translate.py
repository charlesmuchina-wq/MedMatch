#!/usr/bin/env python3
"""Re-translate early-batch languages that had parsing issues."""
import asyncio, json, os, sys, re

sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
from emergentintegrations.llm.chat import LlmChat, UserMessage

API_KEY = os.environ.get('EMERGENT_LLM_KEY')
LOCALES_DIR = '/app/frontend/src/locales'

RETRY_LANGS = {
    'af': 'Afrikaans', 'am': 'Amharic', 'ar': 'Arabic', 'bn': 'Bengali',
    'cs': 'Czech', 'da': 'Danish', 'de': 'German', 'el': 'Greek',
    'es': 'Spanish', 'fa': 'Persian', 'fi': 'Finnish', 'fr': 'French',
    'ha': 'Hausa', 'he': 'Hebrew', 'hi': 'Hindi'
}

def extract_json(text):
    text = text.strip()
    if text.startswith('```'):
        text = re.sub(r'^```\w*\n?', '', text)
        text = re.sub(r'\n?```$', '', text)
    try:
        return json.loads(text)
    except:
        match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
        if match:
            try: return json.loads(match.group())
            except: pass
    return None

async def translate_lang(lang_code, lang_name, en_data, locale_data, filepath):
    keys_needing = {}
    for ns in ['karauMeet', 'candidateSearch']:
        en_ns = en_data.get(ns, {})
        locale_ns = locale_data.get(ns, {})
        for k, v in en_ns.items():
            if k in locale_ns and locale_ns[k] == v:
                keys_needing[k] = v

    if len(keys_needing) < 10:
        return 0

    chat = LlmChat(
        api_key=API_KEY,
        session_id=f"retry-{lang_code}",
        system_message=f"You are a professional UI translator. Translate English UI strings to {lang_name}. Return ONLY a JSON object. Keep {{{{variables}}}} and HTML tags. Keep technical terms (SSO, SAML, GDPR, HIPAA, AI, E2E) in English."
    ).with_model("openai", "gpt-4o-mini")

    translated = 0
    chunk_size = 30
    keys_list = list(keys_needing.items())

    for i in range(0, len(keys_list), chunk_size):
        chunk = dict(keys_list[i:i+chunk_size])
        try:
            response = await chat.send_message(UserMessage(text=json.dumps(chunk, ensure_ascii=False)))
            parsed = extract_json(response)
            if parsed:
                for ns in ['karauMeet', 'candidateSearch']:
                    if ns not in locale_data: locale_data[ns] = {}
                    for k, v in parsed.items():
                        if k in en_data.get(ns, {}):
                            locale_data[ns][k] = v
                            translated += 1
        except Exception as e:
            print(f"  {lang_code} chunk error: {e}", flush=True)

    with open(filepath, 'w') as f:
        json.dump(locale_data, f, indent=2, ensure_ascii=False)
    return translated

async def main():
    with open(os.path.join(LOCALES_DIR, 'en.json')) as f:
        en_data = json.load(f)

    for i in range(0, len(RETRY_LANGS), 3):
        batch = list(RETRY_LANGS.items())[i:i+3]
        print(f"\nRetry batch: {', '.join(lc for lc,_ in batch)}", flush=True)
        tasks = []
        for lc, ln in batch:
            fp = os.path.join(LOCALES_DIR, f'{lc}.json')
            with open(fp) as f: ld = json.load(f)
            tasks.append(translate_lang(lc, ln, en_data, ld, fp))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for (lc, _), r in zip(batch, results):
            if isinstance(r, Exception): print(f"  {lc}: FAILED - {r}", flush=True)
            else: print(f"  {lc}: {r} keys re-translated", flush=True)

    print("\nRetry done!", flush=True)

if __name__ == '__main__':
    asyncio.run(main())
