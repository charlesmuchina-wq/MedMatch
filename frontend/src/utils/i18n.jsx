/**
 * Internationalization (i18n) System for MedMatch
 * Provides translation hooks and language management
 */
import { useState, useEffect, createContext, useContext, useCallback } from "react";

// Import all locale files
import en from "@/locales/en.json";
import es from "@/locales/es.json";
import fr from "@/locales/fr.json";
import zh from "@/locales/zh.json";
import de from "@/locales/de.json";

// Available translations
const translations = {
  en,
  es,
  fr,
  zh,
  de
};

// Fallback language
const DEFAULT_LANGUAGE = "en";

// Language metadata
export const LANGUAGE_META = {
  en: { name: "English", native: "English", flag: "🇺🇸", rtl: false },
  es: { name: "Spanish", native: "Español", flag: "🇪🇸", rtl: false },
  fr: { name: "French", native: "Français", flag: "🇫🇷", rtl: false },
  zh: { name: "Chinese", native: "中文", flag: "🇨🇳", rtl: false },
  de: { name: "German", native: "Deutsch", flag: "🇩🇪", rtl: false },
  // Languages that will use AI translation (not bundled)
  ja: { name: "Japanese", native: "日本語", flag: "🇯🇵", rtl: false },
  ko: { name: "Korean", native: "한국어", flag: "🇰🇷", rtl: false },
  pt: { name: "Portuguese", native: "Português", flag: "🇵🇹", rtl: false },
  "pt-BR": { name: "Portuguese (Brazil)", native: "Português (Brasil)", flag: "🇧🇷", rtl: false },
  ar: { name: "Arabic", native: "العربية", flag: "🇸🇦", rtl: true },
  hi: { name: "Hindi", native: "हिन्दी", flag: "🇮🇳", rtl: false },
  it: { name: "Italian", native: "Italiano", flag: "🇮🇹", rtl: false },
  ru: { name: "Russian", native: "Русский", flag: "🇷🇺", rtl: false },
  nl: { name: "Dutch", native: "Nederlands", flag: "🇳🇱", rtl: false },
  tr: { name: "Turkish", native: "Türkçe", flag: "🇹🇷", rtl: false },
  vi: { name: "Vietnamese", native: "Tiếng Việt", flag: "🇻🇳", rtl: false },
  th: { name: "Thai", native: "ไทย", flag: "🇹🇭", rtl: false },
  id: { name: "Indonesian", native: "Bahasa Indonesia", flag: "🇮🇩", rtl: false },
  pl: { name: "Polish", native: "Polski", flag: "🇵🇱", rtl: false },
};

// Bundled languages (full translations available)
export const BUNDLED_LANGUAGES = ["en", "es", "fr", "zh", "de"];

// Popular languages order
export const POPULAR_LANGUAGES = ["en", "es", "fr", "de", "zh", "ja", "ko", "pt-BR", "ar", "hi"];

// i18n Context
const I18nContext = createContext(null);

/**
 * Get nested value from object using dot notation
 * @param {Object} obj - The object to traverse
 * @param {string} path - Dot notation path (e.g., "nav.dashboard")
 * @returns {string} The value or the path if not found
 */
const getNestedValue = (obj, path) => {
  if (!obj || !path) return path;
  
  const keys = path.split(".");
  let value = obj;
  
  for (const key of keys) {
    if (value && typeof value === "object" && key in value) {
      value = value[key];
    } else {
      return path; // Return the key if translation not found
    }
  }
  
  return typeof value === "string" ? value : path;
};

/**
 * I18n Provider Component
 * Wraps the app and provides translation context
 */
export const I18nProvider = ({ children }) => {
  const [language, setLanguageState] = useState(() => {
    return localStorage.getItem("medmatch-language") || DEFAULT_LANGUAGE;
  });
  
  const [dynamicTranslations, setDynamicTranslations] = useState({});
  const [isRTL, setIsRTL] = useState(false);

  // Update localStorage and document direction when language changes
  useEffect(() => {
    localStorage.setItem("medmatch-language", language);
    
    // Check if RTL
    const langMeta = LANGUAGE_META[language];
    const rtl = langMeta?.rtl || false;
    setIsRTL(rtl);
    
    // Update document direction
    document.documentElement.dir = rtl ? "rtl" : "ltr";
    document.documentElement.lang = language;
  }, [language]);

  /**
   * Set the current language
   */
  const setLanguage = useCallback((lang) => {
    if (lang && (translations[lang] || LANGUAGE_META[lang])) {
      setLanguageState(lang);
    }
  }, []);

  /**
   * Get translation for a key
   * @param {string} key - Translation key (e.g., "nav.dashboard")
   * @param {Object} params - Optional interpolation parameters
   * @returns {string} Translated string
   */
  const t = useCallback((key, params = {}) => {
    // First check dynamic translations (AI-generated)
    if (dynamicTranslations[language]?.[key]) {
      let text = dynamicTranslations[language][key];
      // Handle interpolation
      Object.entries(params).forEach(([param, value]) => {
        text = text.replace(new RegExp(`{{${param}}}`, "g"), value);
      });
      return text;
    }
    
    // Then check bundled translations
    const currentTranslations = translations[language] || translations[DEFAULT_LANGUAGE];
    let text = getNestedValue(currentTranslations, key);
    
    // Fallback to English if translation not found
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
   * Check if a translation exists for the current language
   */
  const hasTranslation = useCallback((key) => {
    if (dynamicTranslations[language]?.[key]) return true;
    const currentTranslations = translations[language];
    if (!currentTranslations) return false;
    return getNestedValue(currentTranslations, key) !== key;
  }, [language, dynamicTranslations]);

  /**
   * Add dynamic translations (from AI or API)
   */
  const addTranslations = useCallback((lang, newTranslations) => {
    setDynamicTranslations(prev => ({
      ...prev,
      [lang]: {
        ...(prev[lang] || {}),
        ...newTranslations
      }
    }));
  }, []);

  /**
   * Get language info
   */
  const getLanguageInfo = useCallback((code) => {
    return LANGUAGE_META[code] || { name: code, native: code, flag: "🌐" };
  }, []);

  /**
   * Check if language has bundled translations
   */
  const isBundled = useCallback((lang) => {
    return BUNDLED_LANGUAGES.includes(lang);
  }, []);

  const value = {
    language,
    setLanguage,
    t,
    hasTranslation,
    addTranslations,
    getLanguageInfo,
    isBundled,
    isRTL,
    availableLanguages: Object.keys(LANGUAGE_META),
    bundledLanguages: BUNDLED_LANGUAGES,
    popularLanguages: POPULAR_LANGUAGES
  };

  return (
    <I18nContext.Provider value={value}>
      {children}
    </I18nContext.Provider>
  );
};

/**
 * Hook to access translation functions
 * @returns {Object} Translation utilities
 */
export const useTranslation = () => {
  const context = useContext(I18nContext);
  
  if (!context) {
    // Fallback for components outside provider
    return {
      language: DEFAULT_LANGUAGE,
      setLanguage: () => {},
      t: (key) => key,
      hasTranslation: () => false,
      addTranslations: () => {},
      getLanguageInfo: (code) => LANGUAGE_META[code] || { name: code },
      isBundled: () => false,
      isRTL: false,
      availableLanguages: Object.keys(LANGUAGE_META),
      bundledLanguages: BUNDLED_LANGUAGES,
      popularLanguages: POPULAR_LANGUAGES
    };
  }
  
  return context;
};

/**
 * Hook to get current language info
 */
export const useLanguageInfo = () => {
  const { language, getLanguageInfo, isRTL } = useTranslation();
  return {
    code: language,
    ...getLanguageInfo(language),
    isRTL
  };
};

export default I18nProvider;
