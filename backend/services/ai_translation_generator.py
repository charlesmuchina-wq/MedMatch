"""
AI Translation Generator for MedMatch
Generates translations for all locale files using GPT-5.2

CAPA-002: Translation Coverage Enhancement
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

# Install emergentintegrations if not present
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "emergentintegrations", 
                          "--extra-index-url", "https://d33sy5i8bnduwe.cloudfront.net/simple/"])
    from emergentintegrations.llm.chat import LlmChat, UserMessage

LOCALES_DIR = Path('/app/frontend/src/locales')
API_KEY = os.environ.get('EMERGENT_LLM_KEY')

# Language codes to native names
LANGUAGE_NAMES = {
    'de': 'German',
    'fr': 'French', 
    'es': 'Spanish',
    'it': 'Italian',
    'nl': 'Dutch',
    'pl': 'Polish',
    'sv': 'Swedish',
    'ru': 'Russian',
    'ja': 'Japanese',
    'zh': 'Chinese (Simplified)',
    'ko': 'Korean',
    'vi': 'Vietnamese',
    'hi': 'Hindi',
    'ar': 'Arabic',
    'tr': 'Turkish',
    'pt-BR': 'Portuguese (Brazil)',
    'sw': 'Swahili',
    'af': 'Afrikaans',
    'ha': 'Hausa',
    'zu': 'Zulu',
    'yo': 'Yoruba',
    'ig': 'Igbo',
    'xh': 'Xhosa',
    'am': 'Amharic',
    'om': 'Oromo',
    'so': 'Somali',
    'rw': 'Kinyarwanda',
    'sn': 'Shona',
    'ny': 'Chichewa',
    'tw': 'Twi',
    'wo': 'Wolof',
    'lg': 'Luganda'
}

async def translate_section(chat: LlmChat, section_name: str, english_content: dict, target_lang: str) -> dict:
    """Translate a section of the locale file."""
    lang_name = LANGUAGE_NAMES.get(target_lang, target_lang)
    
    prompt = f"""Translate the following JSON object from English to {lang_name}.
This is UI text for a job search platform called MedMatch-AI KARAU.

IMPORTANT RULES:
1. Keep all JSON keys exactly as they are (don't translate keys)
2. Only translate the string values
3. Maintain the same JSON structure
4. Keep technical terms like "MedMatch", "KARAU", "AI" unchanged
5. Use formal but friendly tone appropriate for {lang_name} speakers
6. Return ONLY valid JSON, no explanations

English content to translate:
{json.dumps(english_content, indent=2, ensure_ascii=False)}

Return the translated JSON:"""

    user_message = UserMessage(text=prompt)
    
    try:
        response = await chat.send_message(user_message)
        # Parse the response as JSON
        # Clean up response - remove markdown code blocks if present
        response = response.strip()
        if response.startswith('```json'):
            response = response[7:]
        if response.startswith('```'):
            response = response[3:]
        if response.endswith('```'):
            response = response[:-3]
        response = response.strip()
        
        translated = json.loads(response)
        return translated
    except json.JSONDecodeError as e:
        print(f"  ⚠️ JSON parse error for {section_name}: {e}")
        return english_content
    except Exception as e:
        print(f"  ⚠️ Translation error for {section_name}: {e}")
        return english_content

async def translate_locale(target_lang: str, sections_to_translate: list):
    """Translate specified sections for a target language."""
    if not API_KEY:
        print("Error: EMERGENT_LLM_KEY not found in environment")
        return
    
    lang_name = LANGUAGE_NAMES.get(target_lang, target_lang)
    print(f"\n{'='*50}")
    print(f"Translating to {lang_name} ({target_lang})")
    print('='*50)
    
    # Load English source
    with open(LOCALES_DIR / 'en.json', 'r') as f:
        en_content = json.load(f)
    
    # Load target locale
    target_file = LOCALES_DIR / f'{target_lang}.json'
    if target_file.exists():
        with open(target_file, 'r') as f:
            target_content = json.load(f)
    else:
        target_content = {}
    
    # Initialize chat
    chat = LlmChat(
        api_key=API_KEY,
        session_id=f"translate-{target_lang}",
        system_message="You are an expert translator specializing in UI/UX localization for software applications."
    ).with_model("openai", "gpt-5.2")
    
    # Translate each section
    for section in sections_to_translate:
        if section in en_content:
            print(f"  Translating section: {section}...")
            translated = await translate_section(chat, section, en_content[section], target_lang)
            target_content[section] = translated
            print(f"  ✅ {section} translated")
    
    # Save translated locale
    with open(target_file, 'w', encoding='utf-8') as f:
        json.dump(target_content, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved {target_lang}.json")

async def main():
    """Main translation workflow."""
    # Sections that need translation
    sections = ['pages', 'components', 'videoTutorials']
    
    # Priority languages to translate
    priority_languages = ['de', 'fr', 'es', 'ja', 'zh', 'ar', 'hi', 'pt-BR', 'sw', 'ko']
    
    print("="*60)
    print("AI Translation Generator - CAPA-002")
    print("="*60)
    print(f"Sections to translate: {sections}")
    print(f"Languages: {priority_languages}")
    
    for lang in priority_languages:
        await translate_locale(lang, sections)
        # Small delay to avoid rate limiting
        await asyncio.sleep(1)
    
    print("\n" + "="*60)
    print("Translation Complete!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
