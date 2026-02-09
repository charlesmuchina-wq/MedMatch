"""
Translation Sync Script
Copies all missing keys from English master to all other language files.
This ensures no raw translation keys appear in the UI.
"""

import json
import os
from pathlib import Path

LOCALES_DIR = "/app/frontend/src/locales"

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

def merge_deep(base, updates):
    """Deep merge two dictionaries"""
    result = base.copy()
    for key, value in updates.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_deep(result[key], value)
        else:
            # Only add if not exists (don't overwrite existing translations)
            if key not in result:
                result[key] = value
    return result

def sync_translations():
    """Sync all missing keys from English to other languages"""
    
    # Load English master
    with open(f"{LOCALES_DIR}/en.json", 'r', encoding='utf-8') as f:
        english = json.load(f)
    
    english_flat = flatten_keys(english)
    print(f"English master has {len(english_flat)} keys")
    
    # Get all language files
    lang_files = [f for f in os.listdir(LOCALES_DIR) if f.endswith('.json') and f != 'en.json']
    
    stats = {
        "total_added": 0,
        "by_language": {}
    }
    
    for lang_file in sorted(lang_files):
        lang_code = lang_file.replace('.json', '')
        file_path = f"{LOCALES_DIR}/{lang_file}"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lang_data = json.load(f)
        except Exception as e:
            print(f"Error loading {lang_code}: {e}")
            continue
        
        lang_flat = flatten_keys(lang_data)
        
        # Find missing keys
        missing = set(english_flat.keys()) - set(lang_flat.keys())
        
        if missing:
            # Add missing keys with English fallback
            for key in missing:
                lang_flat[key] = english_flat[key]
            
            # Convert back to nested and save
            updated_data = unflatten_keys(lang_flat)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(updated_data, f, ensure_ascii=False, indent=2)
            
            stats["total_added"] += len(missing)
            stats["by_language"][lang_code] = len(missing)
            print(f"✅ {lang_code}: Added {len(missing)} missing keys")
        else:
            print(f"✓ {lang_code}: All keys present")
    
    return stats

if __name__ == "__main__":
    print("=" * 50)
    print("Translation Sync - Adding Missing Keys")
    print("=" * 50)
    print()
    
    stats = sync_translations()
    
    print()
    print("=" * 50)
    print(f"Total keys added: {stats['total_added']}")
    print("=" * 50)
