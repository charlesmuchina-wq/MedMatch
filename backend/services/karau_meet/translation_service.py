"""
Real-time translation service for meeting captions using Emergent LLM.
"""
import asyncio
from utils.config import EMERGENT_LLM_KEY

# Cache translations to reduce API calls
_translation_cache = {}

SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "pt": "Portuguese",
    "zh": "Chinese (Simplified)",
    "ja": "Japanese",
    "ko": "Korean",
    "ar": "Arabic",
    "hi": "Hindi",
    "it": "Italian",
    "ru": "Russian",
    "nl": "Dutch",
    "sv": "Swedish",
    "pl": "Polish",
    "tr": "Turkish"
}


def _make_translation_chat(session_id: str):
    from emergentintegrations.llm.chat import LlmChat
    return LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=session_id,
        system_message="You are a professional translator. Return ONLY the translated text, nothing else."
    ).with_model("openai", "gpt-4o-mini")


async def translate_text(text: str, target_lang: str, source_lang: str = "en") -> str:
    """Translate text using Emergent LLM integration."""
    if not text.strip() or target_lang == source_lang:
        return text

    cache_key = f"{source_lang}:{target_lang}:{text[:100]}"
    if cache_key in _translation_cache:
        return _translation_cache[cache_key]

    if not EMERGENT_LLM_KEY:
        return text

    try:
        from emergentintegrations.llm.chat import UserMessage

        chat = _make_translation_chat(f"translate-{source_lang}-{target_lang}")

        prompt = f"Translate the following text from {SUPPORTED_LANGUAGES.get(source_lang, source_lang)} to {SUPPORTED_LANGUAGES.get(target_lang, target_lang)}. Return ONLY the translated text, nothing else:\n\n{text}"

        result = await asyncio.to_thread(
            chat.send_message,
            UserMessage(text=prompt)
        )

        translated = result.strip()
        _translation_cache[cache_key] = translated

        if len(_translation_cache) > 500:
            keys = list(_translation_cache.keys())[:100]
            for k in keys:
                del _translation_cache[k]

        return translated
    except Exception as e:
        print(f"Translation error: {e}")
        return text


async def translate_batch(texts: list, target_lang: str, source_lang: str = "en") -> list:
    """Translate multiple texts at once."""
    if not texts or target_lang == source_lang:
        return texts

    combined = "\n---\n".join(texts)
    try:
        from emergentintegrations.llm.chat import UserMessage

        chat = _make_translation_chat(f"batch-{source_lang}-{target_lang}")

        prompt = f"Translate each of the following texts from {SUPPORTED_LANGUAGES.get(source_lang, source_lang)} to {SUPPORTED_LANGUAGES.get(target_lang, target_lang)}. Keep the texts separated by '---'. Return ONLY the translations:\n\n{combined}"

        result = await asyncio.to_thread(
            chat.send_message,
            UserMessage(text=prompt)
        )

        translations = result.strip().split("---")
        translations = [t.strip() for t in translations]

        if len(translations) == len(texts):
            return translations
        return texts
    except Exception as e:
        print(f"Batch translation error: {e}")
        return texts
