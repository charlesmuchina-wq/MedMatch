/**
 * Internationalization (i18n) System for MedMatch
 * Provides translation hooks, language management, and AI-powered translation
 */
import { useState, useEffect, createContext, useContext, useCallback, useRef } from "react";
import axios from "axios";

// Import all locale files - Bundled languages (instant loading)
import en from "@/locales/en.json";
import es from "@/locales/es.json";
import fr from "@/locales/fr.json";
import zh from "@/locales/zh.json";
import de from "@/locales/de.json";
// PA-1: High-demand bundled languages
import ja from "@/locales/ja.json";
import ar from "@/locales/ar.json";
import hi from "@/locales/hi.json";
import ptBR from "@/locales/pt-BR.json";

const API = process.env.REACT_APP_BACKEND_URL;

// Available translations - Now includes high-demand languages
const translations = {
  en,
  es,
  fr,
  zh,
  de,
  ja,      // Japanese - bundled
  ar,      // Arabic - bundled
  hi,      // Hindi - bundled
  "pt-BR": ptBR  // Portuguese-BR - bundled
};

// Fallback language
const DEFAULT_LANGUAGE = "en";

// Language metadata
export const LANGUAGE_META = {
  // Bundled languages (full translations available)
  en: { name: "English (US)", native: "English (US)", flag: "🇺🇸", rtl: false },
  "en-GB": { name: "English (UK)", native: "English (UK)", flag: "🇬🇧", rtl: false },
  "en-IE": { name: "English (Ireland)", native: "English (Ireland)", flag: "🇮🇪", rtl: false },
  "en-SG": { name: "English (Singapore)", native: "English (Singapore)", flag: "🇸🇬", rtl: false },
  es: { name: "Spanish", native: "Español", flag: "🇪🇸", rtl: false },
  fr: { name: "French", native: "Français", flag: "🇫🇷", rtl: false },
  zh: { name: "Chinese", native: "中文", flag: "🇨🇳", rtl: false },
  de: { name: "German", native: "Deutsch", flag: "🇩🇪", rtl: false },
  
  // Nordic Languages (AI translation)
  no: { name: "Norwegian", native: "Norsk", flag: "🇳🇴", rtl: false },
  sv: { name: "Swedish", native: "Svenska", flag: "🇸🇪", rtl: false },
  da: { name: "Danish", native: "Dansk", flag: "🇩🇰", rtl: false },
  fi: { name: "Finnish", native: "Suomi", flag: "🇫🇮", rtl: false },
  is: { name: "Icelandic", native: "Íslenska", flag: "🇮🇸", rtl: false },
  
  // Asian Languages (AI translation)
  ja: { name: "Japanese", native: "日本語", flag: "🇯🇵", rtl: false },
  ko: { name: "Korean", native: "한국어", flag: "🇰🇷", rtl: false },
  hi: { name: "Hindi", native: "हिन्दी", flag: "🇮🇳", rtl: false },
  vi: { name: "Vietnamese", native: "Tiếng Việt", flag: "🇻🇳", rtl: false },
  th: { name: "Thai", native: "ไทย", flag: "🇹🇭", rtl: false },
  id: { name: "Indonesian", native: "Bahasa Indonesia", flag: "🇮🇩", rtl: false },
  ms: { name: "Malay", native: "Bahasa Melayu", flag: "🇲🇾", rtl: false },
  tl: { name: "Filipino", native: "Tagalog", flag: "🇵🇭", rtl: false },
  bn: { name: "Bengali", native: "বাংলা", flag: "🇧🇩", rtl: false },
  ta: { name: "Tamil", native: "தமிழ்", flag: "🇮🇳", rtl: false },
  ur: { name: "Urdu", native: "اردو", flag: "🇵🇰", rtl: true },
  
  // European Languages (AI translation)
  pt: { name: "Portuguese", native: "Português", flag: "🇵🇹", rtl: false },
  "pt-BR": { name: "Portuguese (Brazil)", native: "Português (Brasil)", flag: "🇧🇷", rtl: false },
  it: { name: "Italian", native: "Italiano", flag: "🇮🇹", rtl: false },
  ru: { name: "Russian", native: "Русский", flag: "🇷🇺", rtl: false },
  nl: { name: "Dutch", native: "Nederlands", flag: "🇳🇱", rtl: false },
  tr: { name: "Turkish", native: "Türkçe", flag: "🇹🇷", rtl: false },
  pl: { name: "Polish", native: "Polski", flag: "🇵🇱", rtl: false },
  uk: { name: "Ukrainian", native: "Українська", flag: "🇺🇦", rtl: false },
  el: { name: "Greek", native: "Ελληνικά", flag: "🇬🇷", rtl: false },
  cs: { name: "Czech", native: "Čeština", flag: "🇨🇿", rtl: false },
  ro: { name: "Romanian", native: "Română", flag: "🇷🇴", rtl: false },
  hu: { name: "Hungarian", native: "Magyar", flag: "🇭🇺", rtl: false },
  
  // Middle Eastern Languages (AI translation)
  ar: { name: "Arabic", native: "العربية", flag: "🇸🇦", rtl: true },
  "ar-AE": { name: "Arabic (UAE)", native: "العربية (الإمارات)", flag: "🇦🇪", rtl: true },
  "ar-EG": { name: "Arabic (Egypt)", native: "العربية (مصر)", flag: "🇪🇬", rtl: true },
  he: { name: "Hebrew", native: "עברית", flag: "🇮🇱", rtl: true },
  fa: { name: "Persian", native: "فارسی", flag: "🇮🇷", rtl: true },
  
  // African Languages (AI translation) - Popular languages across the continent
  sw: { name: "Swahili", native: "Kiswahili", flag: "🇰🇪", rtl: false },      // East Africa - Kenya, Tanzania
  ha: { name: "Hausa", native: "Hausa", flag: "🇳🇬", rtl: false },           // West Africa - Nigeria, Niger
  yo: { name: "Yoruba", native: "Yorùbá", flag: "🇳🇬", rtl: false },         // West Africa - Nigeria
  ig: { name: "Igbo", native: "Igbo", flag: "🇳🇬", rtl: false },             // West Africa - Nigeria
  zu: { name: "Zulu", native: "isiZulu", flag: "🇿🇦", rtl: false },          // South Africa
  xh: { name: "Xhosa", native: "isiXhosa", flag: "🇿🇦", rtl: false },        // South Africa
  af: { name: "Afrikaans", native: "Afrikaans", flag: "🇿🇦", rtl: false },   // South Africa
  am: { name: "Amharic", native: "አማርኛ", flag: "🇪🇹", rtl: false },         // Ethiopia
  om: { name: "Oromo", native: "Oromoo", flag: "🇪🇹", rtl: false },          // Ethiopia
  so: { name: "Somali", native: "Soomaali", flag: "🇸🇴", rtl: false },       // Somalia
  rw: { name: "Kinyarwanda", native: "Kinyarwanda", flag: "🇷🇼", rtl: false }, // Rwanda
  sn: { name: "Shona", native: "chiShona", flag: "🇿🇼", rtl: false },        // Zimbabwe
  ny: { name: "Chichewa", native: "Chichewa", flag: "🇲🇼", rtl: false },     // Malawi
  tw: { name: "Twi", native: "Twi", flag: "🇬🇭", rtl: false },               // Ghana
  wo: { name: "Wolof", native: "Wolof", flag: "🇸🇳", rtl: false },           // Senegal
  lg: { name: "Luganda", native: "Luganda", flag: "🇺🇬", rtl: false },       // Uganda
};

// Bundled languages (full translations available)
export const BUNDLED_LANGUAGES = ["en", "es", "fr", "zh", "de", "ja", "ar", "hi", "pt-BR"];

// Popular languages order (including African languages and key regional variants)
export const POPULAR_LANGUAGES = [
  "en", "en-GB", "es", "fr", "de", "zh", "ja", "ko", "pt-BR", "ar", "ar-AE", "hi",
  // Nordic
  "no",
  // Regional English
  "en-IE", "en-SG",
  // African languages in popular list
  "sw", "ha", "am", "yo", "zu", "af"
];

// i18n Context
const I18nContext = createContext(null);

// Cache key for localStorage
const AI_TRANSLATION_CACHE_KEY = "medmatch-ai-translations";

/**
 * Get nested value from object using dot notation
 */
const getNestedValue = (obj, path) => {
  if (!obj || !path) return path;
  
  const keys = path.split(".");
  let value = obj;
  
  for (const key of keys) {
    if (value && typeof value === "object" && key in value) {
      value = value[key];
    } else {
      return path;
    }
  }
  
  return typeof value === "string" ? value : path;
};

/**
 * Flatten nested object to dot notation keys
 */
const flattenTranslations = (obj, prefix = "") => {
  const result = {};
  for (const key in obj) {
    const fullKey = prefix ? `${prefix}.${key}` : key;
    if (typeof obj[key] === "object" && obj[key] !== null) {
      Object.assign(result, flattenTranslations(obj[key], fullKey));
    } else {
      result[fullKey] = obj[key];
    }
  }
  return result;
};

/**
 * AI Translation Service
 * Handles translation for non-bundled languages using the backend API
 */
class AITranslationService {
  constructor() {
    this.cache = this.loadCache();
    this.pendingRequests = new Map();
    this.batchQueue = [];
    this.batchTimeout = null;
  }

  loadCache() {
    try {
      const cached = localStorage.getItem(AI_TRANSLATION_CACHE_KEY);
      return cached ? JSON.parse(cached) : {};
    } catch {
      return {};
    }
  }

  saveCache() {
    try {
      localStorage.setItem(AI_TRANSLATION_CACHE_KEY, JSON.stringify(this.cache));
    } catch (e) {
      console.warn("Failed to save translation cache:", e);
    }
  }

  getCacheKey(text, targetLang) {
    return `${targetLang}:${text}`;
  }

  getFromCache(text, targetLang) {
    const key = this.getCacheKey(text, targetLang);
    return this.cache[key];
  }

  setInCache(text, targetLang, translation) {
    const key = this.getCacheKey(text, targetLang);
    this.cache[key] = translation;
    this.saveCache();
  }

  /**
   * Translate a single text
   */
  async translate(text, targetLang) {
    // Check cache first
    const cached = this.getFromCache(text, targetLang);
    if (cached) return cached;

    // Check if request is already pending
    const pendingKey = this.getCacheKey(text, targetLang);
    if (this.pendingRequests.has(pendingKey)) {
      return this.pendingRequests.get(pendingKey);
    }

    // Create new request
    const promise = this.doTranslate(text, targetLang);
    this.pendingRequests.set(pendingKey, promise);

    try {
      const result = await promise;
      this.setInCache(text, targetLang, result);
      return result;
    } finally {
      this.pendingRequests.delete(pendingKey);
    }
  }

  async doTranslate(text, targetLang) {
    try {
      const response = await axios.post(`${API}/api/translate/text`, {
        text,
        target_language: targetLang
      });
      return response.data.translated_text || text;
    } catch (e) {
      console.error("AI translation failed:", e);
      return text; // Return original on failure
    }
  }

  /**
   * Batch translate multiple texts
   */
  async translateBatch(texts, targetLang) {
    // Filter out already cached
    const uncached = texts.filter(t => !this.getFromCache(t, targetLang));
    
    if (uncached.length === 0) {
      return texts.map(t => this.getFromCache(t, targetLang) || t);
    }

    try {
      const response = await axios.post(`${API}/api/translate/batch`, {
        texts: uncached,
        target_language: targetLang
      });

      const results = response.data.translations || [];
      results.forEach(({ original, translated }) => {
        this.setInCache(original, targetLang, translated);
      });
    } catch (e) {
      console.error("Batch translation failed:", e);
    }

    return texts.map(t => this.getFromCache(t, targetLang) || t);
  }

  /**
   * Queue text for batch translation
   */
  queueForBatch(text, targetLang, callback) {
    this.batchQueue.push({ text, targetLang, callback });
    
    if (this.batchTimeout) {
      clearTimeout(this.batchTimeout);
    }

    // Process batch after 100ms of no new requests
    this.batchTimeout = setTimeout(() => this.processBatchQueue(), 100);
  }

  async processBatchQueue() {
    if (this.batchQueue.length === 0) return;

    const queue = [...this.batchQueue];
    this.batchQueue = [];

    // Group by target language
    const byLang = {};
    queue.forEach(item => {
      if (!byLang[item.targetLang]) byLang[item.targetLang] = [];
      byLang[item.targetLang].push(item);
    });

    // Translate each language group
    for (const [lang, items] of Object.entries(byLang)) {
      const texts = items.map(i => i.text);
      const translated = await this.translateBatch(texts, lang);
      
      items.forEach((item, idx) => {
        item.callback(translated[idx]);
      });
    }
  }

  clearCache() {
    this.cache = {};
    localStorage.removeItem(AI_TRANSLATION_CACHE_KEY);
  }
}

// Singleton instance
const aiTranslator = new AITranslationService();

/**
 * Detect language from browser locale
 * Maps browser locales to our supported language codes
 */
const detectBrowserLanguage = () => {
  const browserLang = navigator.language || navigator.userLanguage || 'en';
  const langCode = browserLang.split('-')[0].toLowerCase();
  const fullCode = browserLang.toLowerCase();
  
  // Check for exact match first (e.g., en-GB, pt-BR, ar-AE)
  if (LANGUAGE_META[fullCode]) {
    return fullCode;
  }
  
  // Check for language code match
  if (LANGUAGE_META[langCode]) {
    return langCode;
  }
  
  // Special mappings for common browser locales
  const localeMapping = {
    'nb': 'no', // Norwegian Bokmål -> Norwegian
    'nn': 'no', // Norwegian Nynorsk -> Norwegian
    'zh-cn': 'zh',
    'zh-tw': 'zh-TW',
    'zh-hk': 'zh-TW',
  };
  
  return localeMapping[fullCode] || localeMapping[langCode] || 'en';
};

/**
 * Detect language from text input using simple heuristics
 * Returns detected language code or null if uncertain
 */
const detectTextLanguage = (text) => {
  if (!text || text.length < 10) return null;
  
  // Language detection patterns (character ranges and common words)
  const patterns = [
    // African languages
    { lang: 'sw', patterns: [/\b(habari|jambo|asante|karibu|sana|kwaheri|ndio|hapana|kazi|nyumba)\b/i], script: /[\u0041-\u007A]/ },
    { lang: 'ha', patterns: [/\b(sannu|nagode|ina|kai|ku|shi|ta|yi|da|kuma)\b/i], script: /[\u0041-\u007A]/ },
    { lang: 'yo', patterns: [/\b(báwo|ẹ|ọ|ṣe|pẹlẹ|ọjọ́|orúkọ|ilé)\b/i], script: /[\u0041-\u007A\u1E00-\u1EFF]/ },
    { lang: 'zu', patterns: [/\b(sawubona|yebo|ngiyabonga|unjani|mina|wena|ukuthi)\b/i], script: /[\u0041-\u007A]/ },
    { lang: 'am', patterns: [/[\u1200-\u137F]/], script: /[\u1200-\u137F]/ }, // Ethiopic script
    
    // RTL languages
    { lang: 'ar', patterns: [/[\u0600-\u06FF]/], script: /[\u0600-\u06FF]/ }, // Arabic script
    { lang: 'he', patterns: [/[\u0590-\u05FF]/], script: /[\u0590-\u05FF]/ }, // Hebrew script
    { lang: 'fa', patterns: [/[\u0600-\u06FF]/, /[\u0750-\u077F]/], script: /[\u0600-\u06FF]/ }, // Persian uses Arabic script
    { lang: 'ur', patterns: [/[\u0600-\u06FF]/], script: /[\u0600-\u06FF]/ }, // Urdu uses Arabic script
    
    // Asian languages
    { lang: 'zh', patterns: [/[\u4E00-\u9FFF]/], script: /[\u4E00-\u9FFF]/ }, // Chinese
    { lang: 'ja', patterns: [/[\u3040-\u309F\u30A0-\u30FF]/], script: /[\u3040-\u309F\u30A0-\u30FF]/ }, // Japanese
    { lang: 'ko', patterns: [/[\uAC00-\uD7AF]/], script: /[\uAC00-\uD7AF]/ }, // Korean
    { lang: 'hi', patterns: [/[\u0900-\u097F]/], script: /[\u0900-\u097F]/ }, // Hindi (Devanagari)
    { lang: 'bn', patterns: [/[\u0980-\u09FF]/], script: /[\u0980-\u09FF]/ }, // Bengali
    { lang: 'ta', patterns: [/[\u0B80-\u0BFF]/], script: /[\u0B80-\u0BFF]/ }, // Tamil
    { lang: 'th', patterns: [/[\u0E00-\u0E7F]/], script: /[\u0E00-\u0E7F]/ }, // Thai
    { lang: 'vi', patterns: [/[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]/i], script: /[a-zA-Z]/ }, // Vietnamese
    
    // European languages with distinctive patterns
    { lang: 'ru', patterns: [/[\u0400-\u04FF]/], script: /[\u0400-\u04FF]/ }, // Cyrillic
    { lang: 'uk', patterns: [/[\u0400-\u04FF]/, /[іїєґ]/i], script: /[\u0400-\u04FF]/ }, // Ukrainian
    { lang: 'el', patterns: [/[\u0370-\u03FF]/], script: /[\u0370-\u03FF]/ }, // Greek
    { lang: 'de', patterns: [/\b(ich|und|der|die|das|ist|ein|für|mit|nicht|auf|sie|es|von|haben|werden|sein|bei|nach|auch|nur|noch|wie|über|so|keine|mehr)\b/i], script: /[a-zA-ZäöüÄÖÜß]/ },
    { lang: 'fr', patterns: [/\b(je|tu|il|nous|vous|ils|est|sont|une|des|les|pour|avec|dans|sur|que|qui|ne|pas|ce|cette|très|bien|aussi|mais|ou|si)\b/i], script: /[a-zA-Zàâäéèêëïîôùûüÿç]/ },
    { lang: 'es', patterns: [/\b(yo|tú|él|ella|nosotros|ustedes|es|son|una|unos|las|los|para|con|en|que|por|más|como|pero|cuando|donde)\b/i], script: /[a-zA-Záéíóúüñ¿¡]/ },
    { lang: 'pt', patterns: [/\b(eu|tu|ele|ela|nós|vocês|é|são|uma|uns|as|os|para|com|em|que|por|mais|como|mas|quando|onde)\b/i], script: /[a-zA-Záàâãéêíóôõúç]/ },
    { lang: 'it', patterns: [/\b(io|tu|lui|lei|noi|voi|loro|è|sono|una|un|le|gli|per|con|che|di|da|in|su|ma|come|dove|quando)\b/i], script: /[a-zA-Zàèéìíîòóùú]/ },
    { lang: 'nl', patterns: [/\b(ik|jij|hij|zij|wij|jullie|is|zijn|een|de|het|voor|met|van|dat|die|ook|maar|als|of|niet|nog|meer|dan)\b/i], script: /[a-zA-Z]/ },
    { lang: 'no', patterns: [/\b(jeg|du|han|hun|vi|de|er|var|en|et|den|det|for|med|til|fra|som|men|eller|når|hvis|også)\b/i], script: /[a-zA-ZæøåÆØÅ]/ },
    { lang: 'sv', patterns: [/\b(jag|du|han|hon|vi|de|är|var|en|ett|den|det|för|med|till|från|som|men|eller|när|också)\b/i], script: /[a-zA-ZåäöÅÄÖ]/ },
  ];
  
  // Check each pattern
  for (const { lang, patterns: langPatterns, script } of patterns) {
    // First check if text contains the script
    if (script && script.test(text)) {
      // Then check specific patterns
      for (const pattern of langPatterns) {
        if (pattern.test(text)) {
          return lang;
        }
      }
      // If script matches but no word patterns, still return for script-based languages
      if (!/[a-zA-Z]/.test(String(script))) {
        return lang;
      }
    }
  }
  
  return null; // Unable to detect
};

/**
 * I18n Provider Component
 */
export const I18nProvider = ({ children }) => {
  const [language, setLanguageState] = useState(() => {
    const savedLang = localStorage.getItem("medmatch-language");
    if (savedLang && LANGUAGE_META[savedLang]) {
      return savedLang;
    }
    // Auto-detect from browser on first visit
    const detected = detectBrowserLanguage();
    console.log('[i18n] Auto-detected language from browser:', detected);
    return detected;
  });
  
  const [dynamicTranslations, setDynamicTranslations] = useState({});
  const [isRTL, setIsRTL] = useState(false);
  const [isLoadingAI, setIsLoadingAI] = useState(false);
  const [isSynced, setIsSynced] = useState(false);
  const [isInitialized, setIsInitialized] = useState(true); // Start as true to avoid flash
  const [translationVersion, setTranslationVersion] = useState(0); // Force re-render when translations load
  const [translationProgress, setTranslationProgress] = useState(0); // Track loading progress (0-100)
  const aiTranslationCache = useRef({});
  const lastSyncRef = useRef(Date.now());

  // Sync language preference with server when user is logged in
  const syncLanguageWithServer = useCallback(async (lang) => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) return;
      
      await axios.put(`${API}/api/auth/preferences`, 
        { language: lang },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setIsSynced(true);
    } catch (e) {
      console.warn("Failed to sync language preference:", e);
    }
  }, []);

  // Fetch user's language preference from server on mount
  // Only fetches if not recently synced from login event
  const fetchLanguagePreference = useCallback(async () => {
    // Skip if we just got a sync event (within last 5 seconds)
    if (Date.now() - lastSyncRef.current < 5000) {
      return;
    }
    
    try {
      const token = localStorage.getItem("access_token");
      if (!token) return;
      
      const response = await axios.get(`${API}/api/auth/preferences`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const serverLang = response.data?.language;
      if (serverLang && serverLang !== language) {
        setLanguageState(serverLang);
        localStorage.setItem("medmatch-language", serverLang);
      }
      setIsSynced(true);
    } catch (e) {
      // User might not be logged in, that's okay
    }
  }, [language]);

  // Fetch language preference on mount
  useEffect(() => {
    fetchLanguagePreference();
  }, [fetchLanguagePreference]);

  // Listen for language sync events from auth
  useEffect(() => {
    const handleLanguageSync = (event) => {
      const newLang = event.detail;
      if (newLang && LANGUAGE_META[newLang] && newLang !== language) {
        lastSyncRef.current = Date.now(); // Mark as recently synced
        setLanguageState(newLang);
      }
    };
    
    window.addEventListener('languageSync', handleLanguageSync);
    return () => window.removeEventListener('languageSync', handleLanguageSync);
  }, [language]);

  // Priority keys that should be translated first (visible immediately)
  const PRIORITY_KEYS = [
    // Common actions
    "common.loading", "common.error", "common.success", "common.save", "common.cancel",
    "common.delete", "common.edit", "common.search", "common.submit", "common.close",
    "common.back", "common.next", "common.confirm", "common.yes", "common.no",
    "common.settings", "common.profile", "common.logout", "common.login", "common.signup",
    // Navigation
    "nav.dashboard", "nav.myResume", "nav.jobSearch", "nav.savedJobs", "nav.applications",
    "nav.myInterviews", "nav.interviewPrep", "nav.successPredictor", "nav.coverLetter",
    "nav.voiceCoach", "nav.analytics", "nav.companies", "nav.messages", "nav.notifications",
    "nav.membership", "nav.idVerification", "nav.salaryInsights", "nav.qaPractice",
    // Dashboard stats
    "dashboard.savedJobs", "dashboard.applications", "dashboard.interviews", "dashboard.resumeScore",
    "dashboard.quickActions", "dashboard.uploadResume", "dashboard.searchJobs",
    "dashboard.welcomeBack", "dashboard.welcomeToMedMatch",
    // Resume/Skills
    "resume.skills", "resume.myResume", "resume.uploadResume", "resume.workExperience",
    "resume.education", "resume.summary", "resume.contact",
    // Jobs
    "jobs.searchJobs", "jobs.apply", "jobs.save", "jobs.saved", "jobs.remote",
    "jobs.fullTime", "jobs.partTime", "jobs.contract", "jobs.hybrid", "jobs.salary",
    // Language selector
    "language.selectLanguage", "language.popular", "language.otherLanguages", "language.african",
    // Interview
    "interview.interviewPrep", "interview.practiceQuestions", "interview.generateQuestion",
    // Dragon AI
    "dragon.webSearch", "dragon.askAnything", "dragon.suggestions"
  ];

  /**
   * Load AI translations for a non-bundled language
   * Uses progressive loading: priority keys first, then background loading
   */
  const loadAITranslations = useCallback(async (lang) => {
    console.log(`[i18n] Loading AI translations for: ${lang}`);
    
    // Check if we already have translations for this language
    if (aiTranslationCache.current[lang] && Object.keys(aiTranslationCache.current[lang]).length > 50) {
      console.log(`[i18n] Using cached translations for ${lang}: ${Object.keys(aiTranslationCache.current[lang]).length} keys`);
      setDynamicTranslations(prev => ({
        ...prev,
        [lang]: aiTranslationCache.current[lang]
      }));
      setTranslationVersion(v => v + 1); // Force re-render
      return;
    }

    setIsLoadingAI(true);
    setTranslationProgress(0);

    try {
      // Get all English strings
      const englishStrings = flattenTranslations(translations.en);
      const allKeys = Object.keys(englishStrings);
      const totalKeys = allKeys.length;
      console.log(`[i18n] Total keys to translate: ${totalKeys}`);
      
      // Separate priority keys from the rest
      const priorityTexts = PRIORITY_KEYS
        .filter(k => englishStrings[k])
        .map(k => ({ key: k, text: englishStrings[k] }));
      
      console.log(`[i18n] Priority keys to translate: ${priorityTexts.length}`);
      
      const remainingKeys = allKeys.filter(k => !PRIORITY_KEYS.includes(k));
      
      const translatedMap = {};

      // First: Translate priority keys in smaller batches (backend limit is 20)
      if (priorityTexts.length > 0) {
        const priorityBatchSize = 15;
        for (let i = 0; i < priorityTexts.length; i += priorityBatchSize) {
          const batchPriority = priorityTexts.slice(i, i + priorityBatchSize);
          const priorityBatch = batchPriority.map(p => p.text);
          console.log(`[i18n] Translating priority batch ${i / priorityBatchSize + 1}:`, priorityBatch.slice(0, 5));
          const translated = await aiTranslator.translateBatch(priorityBatch, lang);
          console.log(`[i18n] Priority batch translated:`, translated.slice(0, 5));
          
          batchPriority.forEach((p, idx) => {
            translatedMap[p.key] = translated[idx];
          });
          
          // Update UI after each priority batch - MERGE with existing translations
          aiTranslationCache.current[lang] = { 
            ...(aiTranslationCache.current[lang] || {}),
            ...translatedMap 
          };
          setDynamicTranslations(prev => {
            const existing = prev[lang] || {};
            const updated = {
              ...prev,
              [lang]: { ...existing, ...translatedMap }
            };
            console.log(`[i18n] Dynamic translations updated for ${lang}:`, Object.keys(updated[lang]).length);
            return updated;
          });
          setTranslationVersion(v => v + 1); // Force re-render after priority translations
          setTranslationProgress(Math.round((Object.keys(translatedMap).length / totalKeys) * 100));
        }
      }

      // Show quick loading indicator done
      setIsLoadingAI(false);

      // Second: Background load remaining translations (don't block UI)
      const loadRemaining = async () => {
        const batchSize = 15; // Keep under backend limit of 20
        let processedCount = priorityTexts.length;
        
        for (let i = 0; i < remainingKeys.length; i += batchSize) {
          const batchKeys = remainingKeys.slice(i, i + batchSize);
          const batchTexts = batchKeys.map(k => englishStrings[k]);
          
          try {
            const translated = await aiTranslator.translateBatch(batchTexts, lang);
            
            batchKeys.forEach((key, idx) => {
              translatedMap[key] = translated[idx];
            });
            
            processedCount += batchKeys.length;
            
            // Update cache and state periodically - MERGE with existing translations
            if (i % 100 === 0 || i + batchSize >= remainingKeys.length) {
              aiTranslationCache.current[lang] = { 
                ...(aiTranslationCache.current[lang] || {}),
                ...translatedMap 
              };
              setDynamicTranslations(prev => {
                const existing = prev[lang] || {};
                return {
                  ...prev,
                  [lang]: { ...existing, ...translatedMap }
                };
              });
              setTranslationVersion(v => v + 1); // Force re-render on each batch
              setTranslationProgress(Math.round((processedCount / totalKeys) * 100));
            }
          } catch (batchErr) {
            console.warn(`AI translation batch ${i} failed:`, batchErr);
          }
          
          // Small delay between batches to avoid rate limiting
          await new Promise(r => setTimeout(r, 100));
        }
        
        // Final update to ensure 100% progress
        setTranslationProgress(100);
        setTranslationVersion(v => v + 1);
        console.log(`[i18n] All translations loaded for ${lang}:`, Object.keys(aiTranslationCache.current[lang] || {}).length);
      };
      
      // Run remaining translations in background
      loadRemaining().catch(e => console.error("Background translation error:", e));
      
    } catch (e) {
      console.error("Failed to load AI translations:", e);
      setIsLoadingAI(false);
      setTranslationProgress(0);
    }
  }, []);

  /**
   * ATOMIC LANGUAGE SWITCHING - Industry Standard Pattern
   * 
   * Based on i18next best practices and CLDR standards:
   * 1. Sequential loading with await (prevents race conditions)
   * 2. Fallback chain: Cached → Pre-rendered → AI
   * 3. Atomic state update (all translations applied at once)
   * 4. Loading gate prevents partial renders
   */
  const loadTranslationsAtomically = useCallback(async (lang) => {
    console.log(`[i18n] Atomic language switch to: ${lang}`);
    setIsLoadingAI(true);
    setTranslationProgress(0);
    
    let allTranslations = {};
    
    // Step 1: Check localStorage cache (instant)
    const cached = aiTranslationCache.current[lang];
    if (cached && Object.keys(cached).length > 50) {
      console.log(`[i18n] Step 1: Found ${Object.keys(cached).length} cached translations`);
      allTranslations = { ...cached };
    }
    
    // Step 2: Fetch pre-rendered translations (fast, ~100ms)
    try {
      const response = await axios.get(`${API}/api/translate/prerender/${lang}`);
      if (response.data.translations && Object.keys(response.data.translations).length > 0) {
        console.log(`[i18n] Step 2: Got ${Object.keys(response.data.translations).length} pre-rendered translations`);
        
        // Map pre-rendered to translation keys
        const keyMapping = {
          "Dashboard": "nav.dashboard",
          "My Resume": "nav.myResume",
          "Resume Profiles": "nav.resumeProfiles",
          "Skill Tests": "nav.skillTests",
          "Job Search": "nav.jobSearch",
          "Saved Jobs": "nav.savedJobs",
          "Applications": "nav.applications",
          "My Interviews": "nav.myInterviews",
          "Interview Calendar": "nav.interviewCalendar",
          "Success Predictor": "nav.successPredictor",
          "Interview Prep": "nav.interviewPrep",
          "Q&A Practice": "nav.qaPractice",
          "Video Practice": "nav.videoPractice",
          "Voice Coach": "nav.voiceCoach",
          "Cover Letter": "nav.coverLetter",
          "Job Alerts": "nav.jobAlerts",
          "Analytics": "nav.analytics",
          "Messages": "nav.messages",
          "Settings": "common.settings",
          "Profile": "common.profile",
          "Sign Out": "common.logout",
          "Sign In": "common.login",
          "Welcome to MedMatch": "dashboard.welcomeToMedMatch",
          "Quick Actions": "dashboard.quickActions",
          "Upload Resume": "dashboard.uploadResume",
          "Search Jobs": "dashboard.searchJobs",
          "Interviews": "dashboard.interviews",
          "Skills": "dashboard.skills",
          "AI Powered": "dashboard.aiPowered",
          "Loading...": "common.loading",
          "Save": "common.save",
          "Cancel": "common.cancel",
          "Delete": "common.delete",
          "Edit": "common.edit",
          "Search": "common.search",
          "Submit": "common.submit",
          "Close": "common.close",
          "Back": "common.back",
          "Next": "common.next",
          "Confirm": "common.confirm",
          "Yes": "common.yes",
          "No": "common.no",
          "Error": "common.error",
          "Success": "common.success"
        };
        
        Object.entries(response.data.translations).forEach(([original, translated]) => {
          const key = keyMapping[original];
          if (key) {
            allTranslations[key] = translated;
          }
        });
      }
    } catch (e) {
      console.log(`[i18n] Step 2: Pre-rendered not available: ${e.message}`);
    }
    
    // Step 3: ATOMIC UPDATE - Apply all collected translations at once
    if (Object.keys(allTranslations).length > 0) {
      console.log(`[i18n] Step 3: Atomic update with ${Object.keys(allTranslations).length} translations`);
      aiTranslationCache.current[lang] = { ...allTranslations };
      setDynamicTranslations(prev => ({
        ...prev,
        [lang]: { ...allTranslations }
      }));
      setTranslationVersion(v => v + 1);
      setTranslationProgress(Math.min(20, Math.round((Object.keys(allTranslations).length / 659) * 100)));
    }
    
    // Step 4: Load remaining AI translations in background (don't await - non-blocking)
    setIsLoadingAI(false);
    loadAITranslations(lang);
    
  }, [loadAITranslations]);

  // Update localStorage and document direction when language changes
  useEffect(() => {
    localStorage.setItem("medmatch-language", language);
    
    const langMeta = LANGUAGE_META[language];
    const rtl = langMeta?.rtl || false;
    setIsRTL(rtl);
    
    document.documentElement.dir = rtl ? "rtl" : "ltr";
    document.documentElement.lang = language;

    // If non-bundled language, use atomic loading pattern
    if (!BUNDLED_LANGUAGES.includes(language)) {
      loadTranslationsAtomically(language);
    }
  }, [language, loadTranslationsAtomically]);

  const setLanguage = useCallback((lang) => {
    if (lang && LANGUAGE_META[lang]) {
      setLanguageState(lang);
      // Sync with server if user is logged in
      syncLanguageWithServer(lang);
    }
  }, [syncLanguageWithServer]);

  /**
   * Get translation for a key
   */
  const t = useCallback((key, params = {}) => {
    // For non-bundled languages, check AI translations
    if (!BUNDLED_LANGUAGES.includes(language)) {
      const aiTranslation = dynamicTranslations[language]?.[key];
      if (aiTranslation) {
        let text = aiTranslation;
        Object.entries(params).forEach(([param, value]) => {
          text = text.replace(new RegExp(`{{${param}}}`, "g"), value);
        });
        return text;
      }
    }
    
    // Check bundled translations
    const currentTranslations = translations[language] || translations[DEFAULT_LANGUAGE];
    let text = getNestedValue(currentTranslations, key);
    
    // Fallback to English
    if (text === key && language !== DEFAULT_LANGUAGE) {
      text = getNestedValue(translations[DEFAULT_LANGUAGE], key);
    }
    
    // Handle interpolation
    if (text && typeof text === "string") {
      Object.entries(params).forEach(([param, value]) => {
        text = text.replace(new RegExp(`{{${param}}}`, "g"), value);
      });
    }
    
    return text;
  }, [language, dynamicTranslations]);

  /**
   * Translate arbitrary text (for dynamic content)
   */
  const translateText = useCallback(async (text) => {
    if (language === DEFAULT_LANGUAGE || BUNDLED_LANGUAGES.includes(language)) {
      return text;
    }
    return aiTranslator.translate(text, language);
  }, [language]);

  const hasTranslation = useCallback((key) => {
    if (!BUNDLED_LANGUAGES.includes(language)) {
      return !!dynamicTranslations[language]?.[key];
    }
    const currentTranslations = translations[language];
    if (!currentTranslations) return false;
    return getNestedValue(currentTranslations, key) !== key;
  }, [language, dynamicTranslations]);

  const addTranslations = useCallback((lang, newTranslations) => {
    setDynamicTranslations(prev => ({
      ...prev,
      [lang]: {
        ...(prev[lang] || {}),
        ...newTranslations
      }
    }));
  }, []);

  const getLanguageInfo = useCallback((code) => {
    return LANGUAGE_META[code] || { name: code, native: code, flag: "🌐" };
  }, []);

  const isBundled = useCallback((lang) => {
    return BUNDLED_LANGUAGES.includes(lang);
  }, []);

  /**
   * Detect language from user input text and optionally switch
   * @param {string} text - User input text
   * @param {boolean} autoSwitch - Whether to automatically switch language
   * @returns {string|null} Detected language code or null
   */
  const detectAndSwitchLanguage = useCallback((text, autoSwitch = false) => {
    const detected = detectTextLanguage(text);
    if (detected && detected !== language) {
      console.log('[i18n] Detected language from text:', detected);
      if (autoSwitch) {
        setLanguage(detected);
      }
      return detected;
    }
    return null;
  }, [language, setLanguage]);

  const value = {
    language,
    setLanguage,
    t,
    translateText,
    hasTranslation,
    addTranslations,
    getLanguageInfo,
    isBundled,
    isRTL,
    isLoadingAI,
    translationVersion, // Used to force re-renders when translations load
    translationProgress, // 0-100 progress of translation loading
    availableLanguages: Object.keys(LANGUAGE_META),
    bundledLanguages: BUNDLED_LANGUAGES,
    popularLanguages: POPULAR_LANGUAGES,
    aiTranslator,
    detectAndSwitchLanguage, // New: detect language from user text
    detectBrowserLanguage: () => detectBrowserLanguage(), // Expose browser detection
  };

  return (
    <I18nContext.Provider value={value}>
      {children}
    </I18nContext.Provider>
  );
};

/**
 * Hook to access translation functions
 */
export const useTranslation = () => {
  const context = useContext(I18nContext);
  
  if (!context) {
    return {
      language: DEFAULT_LANGUAGE,
      setLanguage: () => {},
      t: (key) => key,
      translateText: async (text) => text,
      hasTranslation: () => false,
      addTranslations: () => {},
      getLanguageInfo: (code) => LANGUAGE_META[code] || { name: code },
      isBundled: () => false,
      isRTL: false,
      isLoadingAI: false,
      translationVersion: 0,
      translationProgress: 100,
      availableLanguages: Object.keys(LANGUAGE_META),
      bundledLanguages: BUNDLED_LANGUAGES,
      popularLanguages: POPULAR_LANGUAGES,
      aiTranslator: null
    };
  }
  
  return context;
};

/**
 * Hook for translating dynamic text with AI
 * Provides loading state and translated text
 */
export const useAITranslation = (text, options = {}) => {
  const { language, translateText, isBundled } = useTranslation();
  const [translated, setTranslated] = useState(text);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const { enabled = true } = options;

  useEffect(() => {
    if (!text || !enabled || language === DEFAULT_LANGUAGE || isBundled(language)) {
      setTranslated(text);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);
    
    translateText(text)
      .then(result => {
        setTranslated(result);
        setIsLoading(false);
      })
      .catch(err => {
        console.error("AI translation error:", err);
        setError(err);
        setTranslated(text); // Fallback to original
        setIsLoading(false);
      });
  }, [text, language, translateText, isBundled, enabled]);

  return { translated, isLoading, error, originalText: text };
};

/**
 * Component for AI-translated text with loading indicator
 * Usage: <AIText text="Hello World" />
 */
export const AIText = ({ text, className = "", showLoading = true, fallback = null }) => {
  const { translated, isLoading } = useAITranslation(text);
  
  if (isLoading && showLoading) {
    return (
      <span className={`inline-flex items-center gap-1 ${className}`}>
        <span className="animate-pulse bg-slate-200 dark:bg-slate-700 rounded h-4 w-20"></span>
      </span>
    );
  }
  
  if (isLoading && fallback) {
    return <span className={className}>{fallback}</span>;
  }
  
  return <span className={className}>{translated}</span>;
};

/**
 * Hook for batch translating multiple texts at once
 * More efficient than individual translations
 */
export const useBatchTranslation = (texts = []) => {
  const { language, isBundled, aiTranslator } = useTranslation();
  const [translations, setTranslations] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!texts.length || language === DEFAULT_LANGUAGE || isBundled(language)) {
      // Return original texts
      const map = {};
      texts.forEach(t => { map[t] = t; });
      setTranslations(map);
      return;
    }

    setIsLoading(true);
    
    // Check cache first
    const uncached = [];
    const cached = {};
    texts.forEach(t => {
      const cachedTranslation = aiTranslator?.getFromCache(t, language);
      if (cachedTranslation) {
        cached[t] = cachedTranslation;
      } else {
        uncached.push(t);
      }
    });

    if (uncached.length === 0) {
      setTranslations(cached);
      setIsLoading(false);
      return;
    }

    // Batch translate uncached texts
    aiTranslator?.translateBatch(uncached, language)
      .then(results => {
        const newTranslations = { ...cached };
        uncached.forEach((text, idx) => {
          newTranslations[text] = results[idx] || text;
        });
        setTranslations(newTranslations);
        setIsLoading(false);
      })
      .catch(() => {
        // Fallback to original texts
        const fallback = { ...cached };
        uncached.forEach(t => { fallback[t] = t; });
        setTranslations(fallback);
        setIsLoading(false);
      });
  }, [texts.join(','), language, isBundled, aiTranslator]);

  return { translations, isLoading, get: (text) => translations[text] || text };
};

/**
 * Hook to get current language info
 */
export const useLanguageInfo = () => {
  const { language, getLanguageInfo, isRTL, isBundled, translationVersion, translationProgress, isLoadingAI } = useTranslation();
  return {
    code: language,
    ...getLanguageInfo(language),
    isRTL,
    isAIPowered: !isBundled(language),
    isBundled: isBundled(language),
    translationVersion, // Use this in key prop to force re-renders
    translationProgress,
    isLoadingAI
  };
};

export default I18nProvider;
