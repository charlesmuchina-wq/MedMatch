#!/usr/bin/env python3
"""
Fast locale generator - Creates basic locale files with key translations
"""
import json
import requests
import os
import time

API_URL = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:8001")
LOCALES_DIR = "/app/frontend/src/locales"

# Languages to generate
LANGUAGES = [
    ("nl", "Dutch"),
    ("it", "Italian"),
    ("vi", "Vietnamese"),
    ("ko", "Korean"),
    ("ru", "Russian"),
    ("pl", "Polish"),
    ("sv", "Swedish"),
    ("tr", "Turkish"),
]

def load_english():
    with open(f"{LOCALES_DIR}/en.json", "r", encoding="utf-8") as f:
        return json.load(f)

def translate_texts(texts, target_lang):
    """Translate a list of texts"""
    try:
        response = requests.post(
            f"{API_URL}/api/translate/batch",
            json={"texts": texts, "target_language": target_lang},
            timeout=120
        )
        if response.status_code == 200:
            data = response.json()
            return [t.get("translated", texts[i]) for i, t in enumerate(data.get("translations", []))]
    except Exception as e:
        print(f"Error: {e}")
    return texts

def translate_dict(d, target_lang, depth=0):
    """Recursively translate a nested dict"""
    result = {}
    
    # Collect all string values at this level
    strings_to_translate = []
    keys_order = []
    
    for k, v in d.items():
        if isinstance(v, str):
            strings_to_translate.append(v)
            keys_order.append(k)
        elif isinstance(v, dict):
            result[k] = translate_dict(v, target_lang, depth+1)
    
    # Batch translate strings (max 15 at a time)
    if strings_to_translate:
        batch_size = 15
        translated = []
        for i in range(0, len(strings_to_translate), batch_size):
            batch = strings_to_translate[i:i+batch_size]
            batch_translated = translate_texts(batch, target_lang)
            translated.extend(batch_translated)
            time.sleep(0.3)  # Rate limit
        
        for i, k in enumerate(keys_order):
            result[k] = translated[i] if i < len(translated) else strings_to_translate[i]
    
    return result

def generate_locale(lang_code, lang_name):
    output_file = f"{LOCALES_DIR}/{lang_code}.json"
    
    if os.path.exists(output_file):
        print(f"  {lang_code}.json exists, skipping")
        return True
    
    print(f"\n=== {lang_name} ({lang_code}) ===")
    
    english = load_english()
    print(f"  Translating {len(str(english))} chars...")
    
    translated = translate_dict(english, lang_code)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(translated, f, ensure_ascii=False, indent=2)
    
    print(f"  ✅ Saved: {output_file}")
    return True

def main():
    print("Fast Locale Generator")
    print("=" * 40)
    
    for lang_code, lang_name in LANGUAGES:
        try:
            generate_locale(lang_code, lang_name)
        except Exception as e:
            print(f"  ❌ Error for {lang_code}: {e}")
    
    print("\n✅ Generation complete!")

if __name__ == "__main__":
    main()
