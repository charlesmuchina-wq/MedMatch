#!/usr/bin/env python3
"""
Generate missing locale files for MedMatch
Uses the backend translation API to create bundled translation files
"""
import json
import requests
import os
import sys
import time

API_URL = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:8001")
LOCALES_DIR = "/app/frontend/src/locales"

# Languages that need locale files generated
MISSING_LANGUAGES = [
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
    """Load English locale as source"""
    with open(f"{LOCALES_DIR}/en.json", "r", encoding="utf-8") as f:
        return json.load(f)

def flatten_dict(d, parent_key="", sep="."):
    """Flatten nested dict to dot notation"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def unflatten_dict(d, sep="."):
    """Convert flat dict with dots back to nested"""
    result = {}
    for key, value in d.items():
        parts = key.split(sep)
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    return result

def translate_batch(texts, target_lang, batch_size=15):
    """Translate a batch of texts"""
    results = {}
    for i in range(0, len(texts), batch_size):
        batch = list(texts.items())[i:i+batch_size]
        batch_texts = [v for k, v in batch]
        batch_keys = [k for k, v in batch]
        
        try:
            response = requests.post(
                f"{API_URL}/api/translate/batch",
                json={"texts": batch_texts, "target_language": target_lang},
                timeout=60
            )
            if response.status_code == 200:
                data = response.json()
                translations = data.get("translations", [])
                for j, item in enumerate(translations):
                    results[batch_keys[j]] = item.get("translated", batch_texts[j])
            else:
                print(f"  Error: {response.status_code}")
                for k, v in batch:
                    results[k] = v
        except Exception as e:
            print(f"  Exception: {e}")
            for k, v in batch:
                results[k] = v
        
        # Rate limiting
        time.sleep(0.5)
        
        # Progress
        progress = min(100, int((i + batch_size) / len(texts) * 100))
        print(f"  Progress: {progress}%", end="\r")
    
    print()
    return results

def generate_locale(lang_code, lang_name):
    """Generate a locale file for a language"""
    output_file = f"{LOCALES_DIR}/{lang_code}.json"
    
    # Check if file already exists
    if os.path.exists(output_file):
        print(f"  {lang_code}.json already exists, skipping...")
        return
    
    print(f"\n=== Generating {lang_name} ({lang_code}) ===")
    
    # Load and flatten English
    english = load_english()
    flat_en = flatten_dict(english)
    print(f"  Total keys: {len(flat_en)}")
    
    # Translate
    print(f"  Translating to {lang_name}...")
    translated = translate_batch(flat_en, lang_code)
    
    # Unflatten back to nested structure
    nested = unflatten_dict(translated)
    
    # Save
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(nested, f, ensure_ascii=False, indent=2)
    
    print(f"  Saved: {output_file}")

def main():
    print("MedMatch Locale Generator")
    print("=" * 40)
    
    for lang_code, lang_name in MISSING_LANGUAGES:
        generate_locale(lang_code, lang_name)
    
    print("\n✅ Done! All locale files generated.")
    print("\nNext steps:")
    print("1. Add imports to i18n.jsx")
    print("2. Add to translations object")
    print("3. Add to BUNDLED_LANGUAGES array")

if __name__ == "__main__":
    main()
