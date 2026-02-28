#!/usr/bin/env python3
"""Propagate new karauMeet keys from en.json to all locale files."""
import json
import os
import glob

LOCALES_DIR = '/app/frontend/src/locales'

# Load English source
with open(os.path.join(LOCALES_DIR, 'en.json'), 'r') as f:
    en_data = json.load(f)

en_karau = en_data.get('karauMeet', {})

# Get all locale files
locale_files = glob.glob(os.path.join(LOCALES_DIR, '*.json'))

updated = 0
for filepath in sorted(locale_files):
    filename = os.path.basename(filepath)
    if filename == 'en.json' or filename == 'pseudo.json':
        continue
    
    with open(filepath, 'r') as f:
        try:
            locale_data = json.load(f)
        except json.JSONDecodeError:
            print(f"  SKIP {filename} (invalid JSON)")
            continue
    
    if 'karauMeet' not in locale_data:
        locale_data['karauMeet'] = {}
    
    # Add missing keys (keep existing translations)
    added = 0
    for key, value in en_karau.items():
        if key not in locale_data['karauMeet']:
            locale_data['karauMeet'][key] = value  # English fallback
            added += 1
    
    if added > 0:
        with open(filepath, 'w') as f:
            json.dump(locale_data, f, indent=2, ensure_ascii=False)
        print(f"  {filename}: added {added} keys")
        updated += 1
    else:
        print(f"  {filename}: up to date")

print(f"\nDone. Updated {updated} locale files.")
