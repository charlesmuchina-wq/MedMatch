#!/usr/bin/env python3
"""
Batch translate i18n keys to all 51 languages using Emergent LLM Key.
Uses GPT-4o-mini for cost-effective translation of UI strings.
"""
import asyncio
import json
import os
import glob
import sys

sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

from emergentintegrations.llm.chat import LlmChat, UserMessage

API_KEY = os.environ.get('EMERGENT_LLM_KEY')
LOCALES_DIR = '/app/frontend/src/locales'

# Language code to name mapping
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

async def translate_batch(lang_code, lang_name, keys_to_translate):
    """Translate a batch of keys for a single language."""
    chat = LlmChat(
        api_key=API_KEY,
        session_id=f"translate-{lang_code}",
        system_message=f"""You are a professional UI/UX translator. Translate the following JSON key-value pairs from English to {lang_name}.
Rules:
- Keep translations concise (UI labels should be short)
- Preserve any {{{{variables}}}} like {{{{name}}}}, {{{{count}}}}, {{{{seconds}}}} exactly as-is
- Preserve HTML tags like <strong> exactly as-is
- Return ONLY valid JSON object, no markdown, no explanation
- If a term is technical (e.g. SSO, SAML, GDPR, HIPAA), keep it in English"""
    ).with_model("openai", "gpt-4o-mini")

    # Split into chunks of ~40 keys to avoid token limits
    chunk_size = 40
    all_translated = {}
    
    for i in range(0, len(keys_to_translate), chunk_size):
        chunk = dict(list(keys_to_translate.items())[i:i + chunk_size])
        prompt = f"Translate to {lang_name}:\n{json.dumps(chunk, ensure_ascii=False, indent=2)}"
        
        try:
            response = await chat.send_message(UserMessage(text=prompt))
            # Extract JSON from response
            resp_text = response.strip()
            if resp_text.startswith('```'):
                resp_text = resp_text.split('\n', 1)[1].rsplit('```', 1)[0].strip()
            translated = json.loads(resp_text)
            all_translated.update(translated)
        except Exception as e:
            print(f"  ERROR translating chunk for {lang_code}: {e}")
            # Fallback: keep English
            all_translated.update(chunk)
    
    return all_translated

async def main():
    # Load English source
    with open(os.path.join(LOCALES_DIR, 'en.json'), 'r') as f:
        en_data = json.load(f)
    
    en_karau = en_data.get('karauMeet', {})
    en_candidate = en_data.get('candidateSearch', {})
    
    # Combine all keys that need translation
    all_en_keys = {}
    for k, v in en_karau.items():
        all_en_keys[f"karauMeet.{k}"] = v
    for k, v in en_candidate.items():
        all_en_keys[f"candidateSearch.{k}"] = v
    
    print(f"Total keys to translate: {len(all_en_keys)}")
    
    # Process languages in batches of 5 for parallelism
    lang_codes = sorted(LANG_MAP.keys())
    batch_size = 5
    
    for batch_start in range(0, len(lang_codes), batch_size):
        batch = lang_codes[batch_start:batch_start + batch_size]
        print(f"\n--- Batch {batch_start // batch_size + 1}: {', '.join(batch)} ---")
        
        tasks = []
        for lang_code in batch:
            lang_name = LANG_MAP[lang_code]
            # Load current locale file
            filepath = os.path.join(LOCALES_DIR, f'{lang_code}.json')
            if not os.path.exists(filepath):
                continue
            
            with open(filepath, 'r') as f:
                locale_data = json.load(f)
            
            # Find keys that are still English (same as en.json)
            keys_needing_translation = {}
            for ns in ['karauMeet', 'candidateSearch']:
                en_ns = en_data.get(ns, {})
                locale_ns = locale_data.get(ns, {})
                for k, v in en_ns.items():
                    if k in locale_ns and locale_ns[k] == v:
                        keys_needing_translation[f"{ns}.{k}"] = v
            
            if not keys_needing_translation:
                print(f"  {lang_code}: already translated")
                continue
            
            print(f"  {lang_code} ({lang_name}): {len(keys_needing_translation)} keys to translate")
            tasks.append((lang_code, lang_name, keys_needing_translation, filepath, locale_data))
        
        # Run translations in parallel
        async_tasks = [translate_batch(lc, ln, ktl) for lc, ln, ktl, _, _ in tasks]
        results = await asyncio.gather(*async_tasks, return_exceptions=True)
        
        # Write results
        for (lang_code, lang_name, _, filepath, locale_data), result in zip(tasks, results):
            if isinstance(result, Exception):
                print(f"  {lang_code}: FAILED - {result}")
                continue
            
            # Update locale data
            for flat_key, translated_val in result.items():
                parts = flat_key.split('.', 1)
                if len(parts) == 2:
                    ns, key = parts
                    if ns not in locale_data:
                        locale_data[ns] = {}
                    locale_data[ns][key] = translated_val
            
            with open(filepath, 'w') as f:
                json.dump(locale_data, f, indent=2, ensure_ascii=False)
            
            print(f"  {lang_code}: translated {len(result)} keys")
    
    print("\nTranslation complete!")

if __name__ == '__main__':
    asyncio.run(main())
