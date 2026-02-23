"""
Priority Key Translation Script
Translates the most critical UI keys for top languages quickly.
"""

import json
import os
import asyncio
import logging
import sys

sys.path.insert(0, '/app/backend')
from utils.config import EMERGENT_LLM_KEY
from emergentintegrations.llm.chat import LlmChat, UserMessage

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

LOCALES_DIR = "/app/frontend/src/locales"

# All supported languages
PRIORITY_LANGUAGES = {
    # Major European
    "es": "Spanish",
    "fr": "French", 
    "de": "German",
    "it": "Italian",
    "nl": "Dutch",
    "pl": "Polish",
    "ru": "Russian",
    "sv": "Swedish",
    "tr": "Turkish",
    # Asian
    "ja": "Japanese",
    "zh": "Chinese",
    "ko": "Korean",
    "hi": "Hindi",
    "vi": "Vietnamese",
    # Middle Eastern
    "ar": "Arabic",
    # Portuguese
    "pt-BR": "Portuguese (Brazilian)",
    # African Languages
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

# Priority translation keys - expanded to cover all major UI elements
PRIORITY_KEYS = [
    # Portal Selector
    "pages.portalSelector.welcomeTo",
    "pages.portalSelector.title", 
    "pages.portalSelector.subtitle",
    "pages.portalSelector.medmatchAI",
    "pages.portalSelector.jobToolkit",
    "pages.portalSelector.jobToolkitDesc",
    "pages.portalSelector.resumeParser",
    "pages.portalSelector.aiJobMatching",
    "pages.portalSelector.recruiterNetwork",
    "pages.portalSelector.enterJobToolkit",
    "pages.portalSelector.aiKarau",
    "pages.portalSelector.meetingPortal",
    "pages.portalSelector.meetingPortalDesc",
    "pages.portalSelector.hdVideoAudio",
    "pages.portalSelector.aiTranscription",
    "pages.portalSelector.e2eEncrypted",
    "pages.portalSelector.enterMeetingPortal",
    "pages.portalSelector.poweredByAI",
    "pages.portalSelector.trustedBy",
    # Common UI
    "common.loading",
    "common.save",
    "common.cancel",
    "common.delete",
    "common.edit",
    "common.search",
    "common.submit",
    "common.close",
    "common.back",
    "common.next",
    "common.confirm",
    "common.yes",
    "common.no",
    "common.error",
    "common.success",
    "common.warning",
    "common.info",
    "common.required",
    "common.optional",
    "common.actions",
    "common.settings",
    "common.profile",
    "common.logout",
    "common.login",
    "common.signup",
    "common.all",
    "common.refresh",
    "common.download",
    "common.filter",
    "common.help",
    "common.upload",
    "common.generating",
    # Navigation
    "nav.dashboard",
    "nav.myResume",
    "nav.resumeProfiles",
    "nav.skillTests",
    "nav.jobSearch",
    "nav.savedJobs",
    "nav.applications",
    "nav.myInterviews",
    "nav.interviewCalendar",
    "nav.successPredictor",
    "nav.interviewPrep",
    "nav.qaPractice",
    "nav.videoPractice",
    "nav.voiceCoach",
    "nav.coverLetter",
    "nav.jobAlerts",
    "nav.analytics",
    "nav.companies",
    "nav.messages",
    "nav.notifications",
    "nav.membership",
    "nav.idVerification",
    "nav.salaryInsights",
    "nav.privacy",
    "nav.locationSettings",
    # Auth
    "auth.email",
    "auth.password",
    "auth.signIn",
    "auth.signUp",
    "auth.forgotPassword",
    "auth.resetPassword",
    "auth.continueWithGoogle",
    "auth.continueWithApple",
    "auth.noAccount",
    "auth.haveAccount",
    "auth.createAccount",
    "auth.welcomeBack",
    "auth.emailPlaceholder",
    "auth.passwordPlaceholder",
    "auth.confirmPassword",
    "auth.firstName",
    "auth.lastName",
    "auth.phoneNumber",
    # Dashboard
    "dashboard.welcomeBack",
    "dashboard.welcomeToMedMatch",
    "dashboard.yourPersonalizedDashboard",
    "dashboard.quickActions",
    "dashboard.uploadResume",
    "dashboard.searchJobs",
    "dashboard.savedJobs",
    "dashboard.applications",
    "dashboard.interviews",
    "dashboard.resumeScore",
    "dashboard.skills",
    "dashboard.aiPowered",
    "dashboard.recentActivity",
    "dashboard.watchTutorials",
    "dashboard.learnWithVideos",
    "dashboard.getStarted",
    "dashboard.trustScore",
    "dashboard.profileCompletion",
    # Jobs
    "jobs.searchJobs",
    "jobs.apply",
    "jobs.save",
    "jobs.saved",
    "jobs.remote",
    "jobs.fullTime",
    "jobs.partTime",
    "jobs.contract",
    "jobs.hybrid",
    "jobs.salary",
    "jobs.location",
    "jobs.postedDate",
    "jobs.applyNow",
    "jobs.viewDetails",
    "jobs.requirements",
    "jobs.benefits",
    "jobs.aboutCompany",
    "jobs.similarJobs",
    "jobs.noJobsFound",
    # Resume
    "resume.myResume",
    "resume.uploadResume",
    "resume.skills",
    "resume.workExperience",
    "resume.education",
    "resume.summary",
    "resume.contact",
    "resume.downloadPdf",
    "resume.aiSuggestions",
    "resume.improveScore",
    # Interview
    "interview.interviewPrep",
    "interview.practiceQuestions",
    "interview.generateQuestion",
    "interview.scheduleInterview",
    "interview.upcomingInterviews",
    "interview.pastInterviews",
    "interview.prepareNow",
    "interview.tips",
    # Settings
    "settings.title",
    "settings.account",
    "settings.privacy",
    "settings.notifications",
    "settings.language",
    "settings.theme",
    "settings.darkMode",
    "settings.lightMode",
    "settings.systemDefault",
    "settings.saveChanges",
    "settings.deleteAccount",
    # Messages
    "messages.title",
    "messages.inbox",
    "messages.sent",
    "messages.compose",
    "messages.noMessages",
    "messages.reply",
    "messages.send",
    # Language
    "language.selectLanguage",
    "language.popular",
    "language.otherLanguages",
    "language.african",
    "language.browserTranslationActive",
    "language.useGoogleTranslate",
    "language.openGoogleTranslate",
    "language.useBrowserTranslate",
]

def get_nested_value(obj, key):
    """Get value from nested dict using dot notation"""
    parts = key.split('.')
    val = obj
    for part in parts:
        if isinstance(val, dict) and part in val:
            val = val[part]
        else:
            return None
    return val

def set_nested_value(obj, key, value):
    """Set value in nested dict using dot notation"""
    parts = key.split('.')
    for part in parts[:-1]:
        if part not in obj:
            obj[part] = {}
        obj = obj[part]
    obj[parts[-1]] = value

async def translate_batch(texts, target_lang, lang_name):
    """Translate a batch of texts"""
    if not EMERGENT_LLM_KEY or not texts:
        return texts
    
    try:
        import uuid
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=str(uuid.uuid4()),
            system_message=f"""Translate these UI strings to {lang_name}. Keep translations concise for UI buttons/labels. Preserve placeholders like {{{{name}}}} exactly. Return ONLY a JSON array of translated strings."""
        ).with_model("openai", "gpt-5.2")
        
        response = await chat.send_message(UserMessage(text=f"Translate to {lang_name}: {json.dumps(texts, ensure_ascii=False)}"))
        
        clean = response.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        
        result = json.loads(clean)
        if isinstance(result, list) and len(result) == len(texts):
            return result
    except Exception as e:
        logger.error(f"Translation error: {e}")
    
    return texts

async def translate_language(lang_code, lang_name):
    """Translate priority keys for a single language"""
    locale_path = f"{LOCALES_DIR}/{lang_code}.json"
    
    if not os.path.exists(locale_path):
        logger.warning(f"  ⚠️ {lang_code}: File not found")
        return 0
    
    # Load files
    with open(f"{LOCALES_DIR}/en.json", 'r', encoding='utf-8') as f:
        english = json.load(f)
    
    with open(locale_path, 'r', encoding='utf-8') as f:
        locale_data = json.load(f)
    
    # Find keys that need translation (same as English or missing)
    keys_to_translate = []
    for key in PRIORITY_KEYS:
        en_val = get_nested_value(english, key)
        locale_val = get_nested_value(locale_data, key)
        
        if en_val and (locale_val is None or locale_val == en_val):
            keys_to_translate.append((key, en_val))
    
    if not keys_to_translate:
        logger.info(f"  ✓ {lang_code}: All priority keys translated")
        return 0
    
    logger.info(f"  → {lang_code}: Translating {len(keys_to_translate)} priority keys...")
    
    # Translate in one batch (since we limited to ~50 priority keys)
    texts = [item[1] for item in keys_to_translate]
    keys = [item[0] for item in keys_to_translate]
    
    translated = await translate_batch(texts, lang_code, lang_name)
    
    # Update locale data
    count = 0
    for i, key in enumerate(keys):
        if translated[i] != texts[i]:
            set_nested_value(locale_data, key, translated[i])
            count += 1
    
    # Save
    with open(locale_path, 'w', encoding='utf-8') as f:
        json.dump(locale_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"  ✅ {lang_code}: Translated {count} keys")
    return count

async def main():
    print("=" * 50)
    print("Priority UI Translation")
    print("=" * 50)
    print(f"Translating {len(PRIORITY_KEYS)} priority keys")
    print(f"For {len(PRIORITY_LANGUAGES)} languages")
    print()
    
    total = 0
    for lang_code, lang_name in PRIORITY_LANGUAGES.items():
        try:
            count = await translate_language(lang_code, lang_name)
            total += count
        except Exception as e:
            logger.error(f"  ❌ {lang_code}: Error - {e}")
    
    print()
    print("=" * 50)
    print(f"Total translations: {total}")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
