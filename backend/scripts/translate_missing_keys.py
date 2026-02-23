"""
Translate Missing Keys Script
Uses AI to translate missing/English-fallback keys in all locale files.
"""

import json
import os
import asyncio
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LOCALES_DIR = "/app/frontend/src/locales"

# Import translation dependencies
import sys
sys.path.insert(0, '/app/backend')
from utils.config import EMERGENT_LLM_KEY
from emergentintegrations.llm.chat import LlmChat, UserMessage

def flatten_keys(data, prefix=""):
    """Flatten nested dictionary to dot-notation keys"""
    keys = {}
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            keys.update(flatten_keys(value, full_key))
        else:
            keys[full_key] = value
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
    if not EMERGENT_LLM_KEY:
        logger.error("EMERGENT_LLM_KEY not configured")
        return texts
    
    try:
        import uuid
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=str(uuid.uuid4()),
            system_message=f"""You are a professional UI translator. Translate the following UI strings to {lang_name}.

RULES:
- Keep translations concise and appropriate for UI buttons/labels
- Preserve any placeholders like {{{{name}}}} or {{{{count}}}} exactly as-is
- Maintain the same tone (formal/informal) as the original
- Keep technical terms if commonly used in that language
- Return ONLY a JSON array of translated strings in the same order

Example input: ["Save", "Cancel", "Loading..."]
Example output: ["Guardar", "Cancelar", "Cargando..."]"""
        ).with_model("openai", "gpt-5.2")
        
        prompt = f"Translate these UI strings to {lang_name}:\n{json.dumps(texts, ensure_ascii=False)}"
        response = await chat.send_message(UserMessage(text=prompt))
        
        # Clean response
        clean = response.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        
        translated = json.loads(clean)
        
        if isinstance(translated, list) and len(translated) == len(texts):
            return translated
        else:
            logger.warning(f"Translation count mismatch: got {len(translated)}, expected {len(texts)}")
            return texts
            
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return texts

async def translate_locale(lang_code, lang_name):
    """Translate all English-fallback keys in a locale file"""
    locale_path = f"{LOCALES_DIR}/{lang_code}.json"
    
    if not os.path.exists(locale_path):
        logger.warning(f"Locale file not found: {locale_path}")
        return 0
    
    # Load English master
    with open(f"{LOCALES_DIR}/en.json", 'r', encoding='utf-8') as f:
        english = json.load(f)
    english_flat = flatten_keys(english)
    
    # Load target locale
    with open(locale_path, 'r', encoding='utf-8') as f:
        locale_data = json.load(f)
    locale_flat = flatten_keys(locale_data)
    
    # Find keys that have English fallback (same value as English)
    keys_to_translate = []
    for key, en_value in english_flat.items():
        if key in locale_flat and locale_flat[key] == en_value:
            keys_to_translate.append((key, en_value))
    
    if not keys_to_translate:
        logger.info(f"✓ {lang_code}: No English fallbacks found")
        return 0
    
    logger.info(f"Translating {len(keys_to_translate)} keys for {lang_code} ({lang_name})")
    
    # Translate in batches of 15
    batch_size = 15
    translated_count = 0
    
    for i in range(0, len(keys_to_translate), batch_size):
        batch = keys_to_translate[i:i+batch_size]
        texts = [item[1] for item in batch]
        keys = [item[0] for item in batch]
        
        translated = await translate_batch(texts, lang_code, lang_name)
        
        for j, key in enumerate(keys):
            if translated[j] != texts[j]:  # Only update if actually translated
                locale_flat[key] = translated[j]
                translated_count += 1
        
        # Small delay between batches
        await asyncio.sleep(0.5)
    
    # Save updated locale
    updated_data = unflatten_keys(locale_flat)
    with open(locale_path, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"✅ {lang_code}: Translated {translated_count} keys")
    return translated_count

# Language names mapping
LANGUAGE_NAMES = {
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "zh": "Chinese (Simplified)",
    "ja": "Japanese",
    "ko": "Korean",
    "pt-BR": "Portuguese (Brazilian)",
    "it": "Italian",
    "nl": "Dutch",
    "ru": "Russian",
    "pl": "Polish",
    "sv": "Swedish",
    "tr": "Turkish",
    "ar": "Arabic",
    "hi": "Hindi",
    "vi": "Vietnamese",
    "sw": "Swahili",
    "ha": "Hausa",
    "yo": "Yoruba",
    "ig": "Igbo",
    "zu": "Zulu",
    "xh": "Xhosa",
    "af": "Afrikaans",
    "am": "Amharic",
    "om": "Oromo",
    "so": "Somali",
    "rw": "Kinyarwanda",
    "sn": "Shona",
    "ny": "Chichewa",
    "tw": "Twi",
    "wo": "Wolof",
    "lg": "Luganda",
}

async def main():
    """Main function to translate all locales"""
    print("=" * 60)
    print("AI Translation - Translating Missing Keys")
    print("=" * 60)
    print()
    
    total_translated = 0
    
    # Get all locale files
    locale_files = [f.replace('.json', '') for f in os.listdir(LOCALES_DIR) 
                    if f.endswith('.json') and f not in ['en.json', 'pseudo.json']]
    
    for lang_code in sorted(locale_files):
        lang_name = LANGUAGE_NAMES.get(lang_code, lang_code)
        try:
            count = await translate_locale(lang_code, lang_name)
            total_translated += count
        except Exception as e:
            logger.error(f"Error translating {lang_code}: {e}")
    
    print()
    print("=" * 60)
    print(f"Total keys translated: {total_translated}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
