#!/usr/bin/env python3
"""
High-KPI Translation Script
Translates all remaining keys to reach 99% coverage across all languages
"""

import json
import os
import sys
import asyncio

sys.path.insert(0, '/app/backend')
from utils.config import EMERGENT_LLM_KEY
from emergentintegrations.llm.chat import LlmChat, UserMessage

LOCALES_DIR = "/app/frontend/src/locales"

# Language names for better AI translation
LANG_NAMES = {
    "es": "Spanish", "fr": "French", "de": "German", "ja": "Japanese",
    "zh": "Chinese (Simplified)", "ko": "Korean", "ar": "Arabic", "pt-BR": "Brazilian Portuguese",
    "hi": "Hindi", "it": "Italian", "nl": "Dutch", "ru": "Russian",
    "pl": "Polish", "sv": "Swedish", "tr": "Turkish", "vi": "Vietnamese",
    "sw": "Swahili", "ha": "Hausa", "yo": "Yoruba", "ig": "Igbo",
    "zu": "Zulu", "xh": "Xhosa", "af": "Afrikaans", "am": "Amharic",
    "om": "Oromo", "so": "Somali", "rw": "Kinyarwanda", "sn": "Shona",
    "ny": "Chichewa", "tw": "Twi", "wo": "Wolof", "lg": "Luganda"
}

def flatten_keys(obj, prefix=""):
    """Flatten nested dictionary to dot-notation keys"""
    keys = {}
    for k, v in obj.items():
        full_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            keys.update(flatten_keys(v, full_key))
        else:
            keys[full_key] = v
    return keys

def unflatten_keys(flat_dict):
    """Convert dot-notation keys back to nested dictionary"""
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

async def translate_batch(texts, target_lang, lang_name):
    """Translate a batch of texts using AI"""
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"translate-99-{target_lang}",
            system_message=f"""You are a professional translator. Translate UI strings from English to {lang_name}.

RULES:
1. Keep translations concise (suitable for UI buttons/labels)
2. Preserve ALL placeholders like {{variable}} or {{{{variable}}}} exactly
3. Maintain the same tone and formality
4. Return ONLY a JSON array of translated strings, nothing else
5. Array must have same length as input"""
        ).with_model("openai", "gpt-5.2")
        
        response = await chat.send_message(UserMessage(text=f"Translate to {lang_name}: {json.dumps(texts, ensure_ascii=False)}"))
        
        # Clean response
        clean = response.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        clean = clean.strip()
        
        translated = json.loads(clean)
        
        if isinstance(translated, list) and len(translated) == len(texts):
            return translated
        else:
            print(f"  WARNING: Response length mismatch for {lang_name}")
            return None
            
    except Exception as e:
        print(f"  ERROR translating {lang_name}: {e}")
        return None

async def process_language(lang_code, english_flat, target_coverage=99.0):
    """Process a single language to reach target coverage"""
    lang_name = LANG_NAMES.get(lang_code, lang_code)
    locale_path = f"{LOCALES_DIR}/{lang_code}.json"
    
    if not os.path.exists(locale_path):
        print(f"  SKIP {lang_code}: File not found")
        return 0
    
    # Load locale
    with open(locale_path, 'r', encoding='utf-8') as f:
        locale_data = json.load(f)
    locale_flat = flatten_keys(locale_data)
    
    total_keys = len(english_flat)
    
    # Find untranslated keys (same as English or missing)
    keys_to_translate = []
    for key, en_value in english_flat.items():
        locale_value = locale_flat.get(key)
        if not locale_value or locale_value == en_value:
            keys_to_translate.append((key, en_value))
    
    current_translated = total_keys - len(keys_to_translate)
    current_coverage = (current_translated / total_keys) * 100
    
    if current_coverage >= target_coverage:
        print(f"  {lang_code} ({lang_name}): Already at {current_coverage:.1f}% - SKIP")
        return 0
    
    # Calculate how many keys needed for target
    keys_needed = int((target_coverage / 100 * total_keys) - current_translated) + 5  # +5 buffer
    keys_to_process = keys_to_translate[:min(keys_needed, len(keys_to_translate))]
    
    print(f"  {lang_code} ({lang_name}): {current_coverage:.1f}% -> Translating {len(keys_to_process)} keys...")
    
    translated_count = 0
    batch_size = 15
    
    for i in range(0, len(keys_to_process), batch_size):
        batch = keys_to_process[i:i+batch_size]
        texts = [item[1] for item in batch]
        keys = [item[0] for item in batch]
        
        translated = await translate_batch(texts, lang_code, lang_name)
        
        if translated:
            for j, key in enumerate(keys):
                if translated[j] and translated[j] != texts[j]:
                    locale_flat[key] = translated[j]
                    translated_count += 1
        
        # Rate limiting
        await asyncio.sleep(0.5)
    
    # Save updated locale
    if translated_count > 0:
        updated_data = unflatten_keys(locale_flat)
        with open(locale_path, 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=2)
        
        new_coverage = ((current_translated + translated_count) / total_keys) * 100
        print(f"    -> Translated {translated_count} keys. New coverage: {new_coverage:.1f}%")
    
    return translated_count

async def main():
    """Main entry point"""
    print("=" * 60)
    print("HIGH-KPI TRANSLATION SCRIPT")
    print("Target: 99% coverage across all languages")
    print("=" * 60)
    
    # Load English master
    with open(f"{LOCALES_DIR}/en.json", 'r', encoding='utf-8') as f:
        english = json.load(f)
    english_flat = flatten_keys(english)
    
    print(f"\nTotal UI keys: {len(english_flat)}")
    
    # Get all languages
    locale_files = [f.replace('.json', '') for f in os.listdir(LOCALES_DIR) 
                    if f.endswith('.json') and f not in ['en.json', 'pseudo.json']]
    
    print(f"Languages to process: {len(locale_files)}\n")
    
    total_translated = 0
    
    # Process languages prioritizing lowest coverage first
    for lang_code in sorted(locale_files):
        count = await process_language(lang_code, english_flat, target_coverage=99.0)
        total_translated += count
    
    print("\n" + "=" * 60)
    print(f"COMPLETED: Translated {total_translated} keys total")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
