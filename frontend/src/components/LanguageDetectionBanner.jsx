import { useState, useEffect } from "react";
import { Globe, X, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTranslation, LANGUAGE_META } from "@/utils/i18n";

const BANNER_DISMISSED_KEY = "medmatch-lang-banner-dismissed";

/**
 * Language Detection Banner
 * Shows a notification when the user's browser language differs from the app language
 * Offers to switch to the detected language
 */
const LanguageDetectionBanner = () => {
  const { language, setLanguage, t, detectBrowserLanguage, getLanguageInfo } = useTranslation();
  const [showBanner, setShowBanner] = useState(false);
  const [detectedLang, setDetectedLang] = useState(null);

  useEffect(() => {
    // Check if banner was already dismissed for this session
    const dismissed = sessionStorage.getItem(BANNER_DISMISSED_KEY);
    if (dismissed) return;

    // Check if this is first visit (no saved language preference)
    const savedLang = localStorage.getItem("medmatch-language");
    
    // Detect browser language
    const browserLang = detectBrowserLanguage();
    
    // Only show banner if:
    // 1. User has NOT previously set a language preference (first visit)
    // 2. Browser language is different from current language (English)
    // 3. Browser language is supported
    if (!savedLang && browserLang && browserLang !== 'en' && LANGUAGE_META[browserLang]) {
      setDetectedLang(browserLang);
      setShowBanner(true);
    }
  }, [detectBrowserLanguage]);

  const handleSwitchLanguage = () => {
    if (detectedLang) {
      setLanguage(detectedLang);
      setShowBanner(false);
      sessionStorage.setItem(BANNER_DISMISSED_KEY, "switched");
    }
  };

  const handleDismiss = () => {
    setShowBanner(false);
    sessionStorage.setItem(BANNER_DISMISSED_KEY, "dismissed");
  };

  if (!showBanner || !detectedLang) return null;

  const langInfo = getLanguageInfo(detectedLang);

  return (
    <div 
      className="fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:w-96 z-50 animate-in slide-in-from-bottom-4"
      data-testid="language-detection-banner"
    >
      <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 p-4">
        <div className="flex items-start gap-3">
          {/* Icon */}
          <div className="w-10 h-10 bg-teal-100 dark:bg-teal-900/30 rounded-full flex items-center justify-center flex-shrink-0">
            <Globe className="w-5 h-5 text-teal-600 dark:text-teal-400" />
          </div>
          
          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xl">{langInfo.flag}</span>
              <p className="font-medium text-slate-900 dark:text-white text-sm">
                {t("language.detectedBrowserLanguage", { language: langInfo.name })}
              </p>
            </div>
            
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-3">
              Would you like to switch to {langInfo.name}?
            </p>
            
            {/* Action Buttons */}
            <div className="flex gap-2">
              <Button
                size="sm"
                onClick={handleSwitchLanguage}
                className="bg-teal-600 hover:bg-teal-700 text-white"
                data-testid="switch-language-btn"
              >
                <Check className="w-4 h-4 mr-1" />
                {t("language.switchToLanguage", { language: langInfo.name })}
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={handleDismiss}
                data-testid="keep-language-btn"
              >
                {t("language.keepCurrentLanguage")}
              </Button>
            </div>
          </div>
          
          {/* Close Button */}
          <button
            onClick={handleDismiss}
            className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
            aria-label="Dismiss"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default LanguageDetectionBanner;
