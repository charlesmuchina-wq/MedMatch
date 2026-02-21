import { Globe, Check, ChevronDown, Loader2, Sparkles, User, ExternalLink, Languages } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel,
  DropdownMenuSub,
  DropdownMenuSubTrigger,
  DropdownMenuSubContent,
} from "@/components/ui/dropdown-menu";
import { useTranslation, POPULAR_LANGUAGES, LANGUAGE_META, BUNDLED_LANGUAGES, useLanguageInfo, useGenderRules, LANGUAGE_GENDER_RULES } from "@/utils/i18n";
import { useState, useEffect } from "react";
import axios from "axios";

const API = process.env.REACT_APP_BACKEND_URL;

// African language codes for separate section
const AFRICAN_LANGUAGES = ["sw", "ha", "yo", "ig", "zu", "xh", "af", "am", "om", "so", "rw", "sn", "ny", "tw", "wo", "lg"];

/**
 * Detect if browser translation is active
 * Checks for Google Translate, Microsoft Translator, and other common translation extensions
 */
const useBrowserTranslationDetection = () => {
  const [isBrowserTranslating, setIsBrowserTranslating] = useState(false);

  useEffect(() => {
    const checkBrowserTranslation = () => {
      // Check for Google Translate
      const googleTranslate = document.querySelector('.goog-te-banner-frame') ||
                             document.querySelector('#goog-gt-tt') ||
                             document.querySelector('.skiptranslate') ||
                             document.body.classList.contains('translated-ltr') ||
                             document.body.classList.contains('translated-rtl') ||
                             document.documentElement.classList.contains('translated-ltr') ||
                             document.documentElement.classList.contains('translated-rtl');
      
      // Check for html lang attribute change (common translation indicator)
      const htmlLang = document.documentElement.lang;
      const storedLang = localStorage.getItem("medmatch-language") || "en";
      const langMismatch = htmlLang && htmlLang !== storedLang && htmlLang !== storedLang.split('-')[0];
      
      // Check for Microsoft Translator
      const msTranslate = document.querySelector('#MicrosoftTranslatorWidget');
      
      // Check for common translation meta tags
      const translateMeta = document.querySelector('meta[name="google-translate-customization"]');
      
      setIsBrowserTranslating(!!(googleTranslate || msTranslate || translateMeta || langMismatch));
    };

    // Initial check
    checkBrowserTranslation();

    // Set up mutation observer to detect translation changes
    const observer = new MutationObserver(checkBrowserTranslation);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class', 'lang'],
      subtree: false
    });
    observer.observe(document.body, {
      attributes: true,
      attributeFilter: ['class'],
      childList: true,
      subtree: false
    });

    // Check periodically as some translators load async
    const interval = setInterval(checkBrowserTranslation, 2000);

    return () => {
      observer.disconnect();
      clearInterval(interval);
    };
  }, []);

  return isBrowserTranslating;
};

/**
 * Open Google Translate with current page
 */
const openGoogleTranslate = () => {
  const currentUrl = window.location.href;
  const googleTranslateUrl = `https://translate.google.com/translate?sl=auto&tl=auto&u=${encodeURIComponent(currentUrl)}`;
  window.open(googleTranslateUrl, '_blank');
};

/**
 * Trigger browser's native translate feature
 * This works differently across browsers - we'll show instructions
 */
const triggerBrowserTranslate = () => {
  // Most browsers don't have a programmatic way to trigger translation
  // We'll show a helpful tooltip/alert with instructions
  const isChrome = navigator.userAgent.includes('Chrome');
  const isFirefox = navigator.userAgent.includes('Firefox');
  const isSafari = navigator.userAgent.includes('Safari') && !navigator.userAgent.includes('Chrome');
  const isEdge = navigator.userAgent.includes('Edg');

  let instructions = '';
  if (isChrome || isEdge) {
    instructions = 'Right-click anywhere on the page and select "Translate to [Your Language]", or click the translate icon in the address bar.';
  } else if (isFirefox) {
    instructions = 'Install the "To Google Translate" extension, or right-click and select a translation option.';
  } else if (isSafari) {
    instructions = 'Click the "aA" button in the address bar and select "Translate to [Your Language]".';
  } else {
    instructions = 'Right-click on the page and look for a translation option, or check your browser settings.';
  }

  alert(instructions);
};

// Gender preference labels
const GENDER_LABELS = {
  masculine: { label: "Masculine", icon: "♂️", description: "Use masculine grammatical forms" },
  feminine: { label: "Feminine", icon: "♀️", description: "Use feminine grammatical forms" },
  neutral: { label: "Neutral", icon: "⚧️", description: "Use neutral/inclusive forms where available" },
  auto: { label: "Auto", icon: "🔄", description: "Use language default" }
};

// Global Language Selector Component for Header
const GlobalLanguageSelector = ({ compact = false }) => {
  const { language, setLanguage, t, getLanguageInfo, isBundled, isLoadingAI } = useTranslation();
  const langInfo = useLanguageInfo();
  const genderRules = useGenderRules();
  const currentLang = getLanguageInfo(language);
  const [grammaticalGender, setGrammaticalGender] = useState(null);
  const isBrowserTranslating = useBrowserTranslationDetection();

  // Load user's gender preference
  useEffect(() => {
    const loadPreference = async () => {
      try {
        const token = localStorage.getItem("medmatch-token") || localStorage.getItem("access_token");
        if (!token) return;
        
        const response = await axios.get(`${API}/api/auth/preferences`, {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        });
        setGrammaticalGender(response.data.grammatical_gender || 'auto');
      } catch (e) {
        // User might not be logged in - silently fail
        setGrammaticalGender('auto');
      }
    };
    loadPreference();
  }, []);

  // Save gender preference
  const updateGenderPreference = async (gender) => {
    setGrammaticalGender(gender);
    try {
      const token = localStorage.getItem("medmatch-token") || localStorage.getItem("access_token");
      if (!token) return;
      
      await axios.put(`${API}/api/auth/preferences`, 
        { grammatical_gender: gender === 'auto' ? '' : gender },
        { headers: { Authorization: `Bearer ${token}` }, withCredentials: true }
      );
    } catch (e) {
      console.warn("Failed to save gender preference:", e);
    }
  };

  // Get all available languages
  const allLanguages = Object.entries(LANGUAGE_META).map(([code, info]) => ({
    code,
    ...info,
    isBundled: BUNDLED_LANGUAGES.includes(code),
    isAfrican: AFRICAN_LANGUAGES.includes(code)
  }));

  // Sort languages: popular first, then by name
  const sortedLanguages = [...allLanguages].sort((a, b) => {
    const aPopular = POPULAR_LANGUAGES.indexOf(a.code);
    const bPopular = POPULAR_LANGUAGES.indexOf(b.code);
    if (aPopular !== -1 && bPopular !== -1) return aPopular - bPopular;
    if (aPopular !== -1) return -1;
    if (bPopular !== -1) return 1;
    return a.name.localeCompare(b.name);
  });

  const popularLanguages = sortedLanguages.filter(l => POPULAR_LANGUAGES.includes(l.code) && !AFRICAN_LANGUAGES.includes(l.code));
  const africanLanguages = sortedLanguages.filter(l => AFRICAN_LANGUAGES.includes(l.code));
  const otherLanguages = sortedLanguages.filter(l => !POPULAR_LANGUAGES.includes(l.code) && !AFRICAN_LANGUAGES.includes(l.code));

  // Check if current language has grammatical gender
  const currentLangHasGender = LANGUAGE_GENDER_RULES[language]?.hasGender || false;

  // If browser translation is active, show indicator instead of selector
  if (isBrowserTranslating) {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 bg-blue-50 dark:bg-blue-900/30 rounded-lg border border-blue-200 dark:border-blue-800" data-testid="browser-translation-indicator">
        <Languages className="w-4 h-4 text-blue-600 dark:text-blue-400" />
        <span className="text-xs text-blue-700 dark:text-blue-300 hidden sm:inline">
          {t("language.browserTranslationActive")}
        </span>
      </div>
    );
  }

  if (compact) {
    return (
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="sm" className="gap-1 px-2" data-testid="language-selector">
            {isLoadingAI ? (
              <Loader2 className="w-4 h-4 animate-spin text-purple-500" />
            ) : langInfo.isAIPowered ? (
              <span className="relative">
                <span className="text-lg">{currentLang.flag}</span>
                <Sparkles className="w-2.5 h-2.5 absolute -top-0.5 -right-1 text-purple-500" />
              </span>
            ) : (
              <span className="text-lg">{currentLang.flag}</span>
            )}
            <ChevronDown className="w-3 h-3 opacity-50" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-56 max-h-[70vh] overflow-y-auto">
          <DropdownMenuLabel className="text-xs text-slate-500">
            {t("language.selectLanguage")}
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          
          {/* Google Translate Options */}
          <DropdownMenuLabel className="text-xs text-slate-400 font-normal px-2 py-1 flex items-center gap-1">
            <Languages className="w-3 h-3" /> {t("language.useGoogleTranslate")}
          </DropdownMenuLabel>
          <DropdownMenuItem
            onClick={openGoogleTranslate}
            className="flex items-center gap-2 cursor-pointer text-blue-600 hover:text-blue-700"
            data-testid="google-translate-btn"
          >
            <ExternalLink className="w-4 h-4" />
            <span className="text-sm">{t("language.openGoogleTranslate")}</span>
          </DropdownMenuItem>
          <DropdownMenuItem
            onClick={triggerBrowserTranslate}
            className="flex items-center gap-2 cursor-pointer text-blue-600 hover:text-blue-700"
            data-testid="browser-translate-btn"
          >
            <Globe className="w-4 h-4" />
            <span className="text-sm">{t("language.useBrowserTranslate")}</span>
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          
          {/* Popular Languages */}
          <DropdownMenuLabel className="text-xs text-slate-400 font-normal px-2 py-1">
            {t("language.popular")}
          </DropdownMenuLabel>
          {popularLanguages.slice(0, 15).map((lang) => (
            <DropdownMenuItem
              key={lang.code}
              onClick={() => setLanguage(lang.code)}
              className="flex items-center justify-between cursor-pointer"
            >
              <span className="flex items-center gap-2">
                <span>{lang.flag}</span>
                <span className="text-sm">{lang.name}</span>
                {!lang.isBundled && (
                  <span className="text-[9px] px-1 bg-gradient-to-r from-purple-100 to-pink-100 text-purple-700 rounded font-medium">AI</span>
                )}
              </span>
              {language === lang.code && <Check className="w-4 h-4 text-green-500" />}
            </DropdownMenuItem>
          ))}
          
          {/* African Languages */}
          {africanLanguages.length > 0 && (
            <>
              <DropdownMenuSeparator />
              <DropdownMenuLabel className="text-xs text-slate-400 font-normal px-2 py-1 flex items-center gap-1">
                🌍 {t("language.african") || "African Languages"}
              </DropdownMenuLabel>
              {africanLanguages.map((lang) => (
                <DropdownMenuItem
                  key={lang.code}
                  onClick={() => setLanguage(lang.code)}
                  className="flex items-center justify-between cursor-pointer"
                >
                  <span className="flex items-center gap-2">
                    <span>{lang.flag}</span>
                    <span className="text-sm">{lang.name}</span>
                    {!lang.isBundled && (
                      <span className="text-[9px] px-1 bg-gradient-to-r from-purple-100 to-pink-100 text-purple-700 rounded font-medium">AI</span>
                    )}
                  </span>
                  {language === lang.code && <Check className="w-4 h-4 text-green-500" />}
                </DropdownMenuItem>
              ))}
            </>
          )}
          
          {/* Other Languages */}
          {otherLanguages.length > 0 && (
            <>
              <DropdownMenuSeparator />
              <DropdownMenuLabel className="text-xs text-slate-400 font-normal px-2 py-1">
                {t("language.otherLanguages")}
              </DropdownMenuLabel>
              {otherLanguages.map((lang) => (
                <DropdownMenuItem
                  key={lang.code}
                  onClick={() => setLanguage(lang.code)}
                  className="flex items-center justify-between cursor-pointer"
                >
                  <span className="flex items-center gap-2">
                    <span>{lang.flag}</span>
                    <span className="text-sm">{lang.name}</span>
                    {!lang.isBundled && (
                      <span className="text-[9px] px-1 bg-gradient-to-r from-purple-100 to-pink-100 text-purple-700 rounded font-medium">AI</span>
                    )}
                  </span>
                  {language === lang.code && <Check className="w-4 h-4 text-green-500" />}
                </DropdownMenuItem>
              ))}
            </>
          )}
        </DropdownMenuContent>
      </DropdownMenu>
    );
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm" className="gap-2" data-testid="language-selector">
          {isLoadingAI ? (
            <Loader2 className="w-4 h-4 animate-spin text-purple-500" />
          ) : langInfo.isAIPowered ? (
            <span className="relative flex items-center gap-1">
              <Sparkles className="w-4 h-4 text-purple-500" />
            </span>
          ) : (
            <Globe className="w-4 h-4" />
          )}
          <span className="hidden sm:inline">{currentLang.flag} {currentLang.name}</span>
          <span className="sm:hidden">{currentLang.flag}</span>
          {langInfo.isAIPowered && !isLoadingAI && (
            <span className="text-[9px] px-1.5 py-0.5 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-full font-medium hidden sm:inline">
              AI
            </span>
          )}
          <ChevronDown className="w-3 h-3 opacity-50" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-64 max-h-[28rem] overflow-y-auto">
        <DropdownMenuLabel className="flex items-center gap-2">
          <Globe className="w-4 h-4" />
          {t("language.selectLanguage")}
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        
        {/* Gender Preference (for gendered languages) */}
        {currentLangHasGender && (
          <>
            <DropdownMenuSub>
              <DropdownMenuSubTrigger className="flex items-center gap-2">
                <User className="w-4 h-4" />
                <span>{t("language.grammaticalGender") || "Grammatical Gender"}</span>
                <span className="text-xs text-slate-400 ml-auto">
                  {GENDER_LABELS[grammaticalGender || 'auto']?.icon}
                </span>
              </DropdownMenuSubTrigger>
              <DropdownMenuSubContent className="w-56">
                <DropdownMenuLabel className="text-xs text-slate-500">
                  {t("language.genderDescription") || "How should UI address you?"}
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                {Object.entries(GENDER_LABELS).map(([key, { label, icon, description }]) => (
                  <DropdownMenuItem
                    key={key}
                    onClick={() => updateGenderPreference(key)}
                    className="flex items-center justify-between cursor-pointer"
                  >
                    <span className="flex items-center gap-2">
                      <span>{icon}</span>
                      <span>{label}</span>
                    </span>
                    {(grammaticalGender || 'auto') === key && <Check className="w-4 h-4 text-green-500" />}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuSubContent>
            </DropdownMenuSub>
            <DropdownMenuSeparator />
          </>
        )}
        
        {/* Popular Languages */}
        <DropdownMenuLabel className="text-xs text-slate-400 font-normal">
          {t("language.popular")}
        </DropdownMenuLabel>
        {popularLanguages.map((lang) => (
          <DropdownMenuItem
            key={lang.code}
            onClick={() => setLanguage(lang.code)}
            className="flex items-center justify-between cursor-pointer"
          >
            <span className="flex items-center gap-2">
              <span className="text-lg">{lang.flag}</span>
              <span>{lang.name}</span>
              <span className="text-xs text-slate-400">({lang.native})</span>
              {!lang.isBundled && (
                <span className="text-[10px] px-1 bg-gradient-to-r from-purple-100 to-pink-100 text-purple-700 rounded font-medium" title="AI-powered translation">AI</span>
              )}
            </span>
            {language === lang.code && <Check className="w-4 h-4 text-green-500" />}
          </DropdownMenuItem>
        ))}
        
        {/* African Languages */}
        {africanLanguages.length > 0 && (
          <>
            <DropdownMenuSeparator />
            <DropdownMenuLabel className="text-xs text-slate-400 font-normal flex items-center gap-1">
              🌍 {t("language.african") || "African Languages"}
            </DropdownMenuLabel>
            {africanLanguages.map((lang) => (
              <DropdownMenuItem
                key={lang.code}
                onClick={() => setLanguage(lang.code)}
                className="flex items-center justify-between cursor-pointer"
              >
                <span className="flex items-center gap-2">
                  <span className="text-lg">{lang.flag}</span>
                  <span>{lang.name}</span>
                  <span className="text-xs text-slate-400">({lang.native})</span>
                  {!lang.isBundled && (
                    <span className="text-[10px] px-1 bg-gradient-to-r from-purple-100 to-pink-100 text-purple-700 rounded font-medium" title="AI-powered translation">AI</span>
                  )}
                </span>
                {language === lang.code && <Check className="w-4 h-4 text-green-500" />}
              </DropdownMenuItem>
            ))}
          </>
        )}
        
        {/* Other Languages */}
        {otherLanguages.length > 0 && (
          <>
            <DropdownMenuSeparator />
            <DropdownMenuLabel className="text-xs text-slate-400 font-normal">
              {t("language.otherLanguages")}
            </DropdownMenuLabel>
            {otherLanguages.map((lang) => (
              <DropdownMenuItem
                key={lang.code}
                onClick={() => setLanguage(lang.code)}
                className="flex items-center justify-between cursor-pointer"
              >
                <span className="flex items-center gap-2">
                  <span className="text-lg">{lang.flag}</span>
                  <span>{lang.name}</span>
                  {!lang.isBundled && (
                    <span className="text-[10px] px-1 bg-gradient-to-r from-purple-100 to-pink-100 text-purple-700 rounded font-medium" title="AI-powered translation">AI</span>
                  )}
                </span>
                {language === lang.code && <Check className="w-4 h-4 text-green-500" />}
              </DropdownMenuItem>
            ))}
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default GlobalLanguageSelector;
