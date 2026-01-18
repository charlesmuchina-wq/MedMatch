import { Globe, Check, ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from "@/components/ui/dropdown-menu";
import { useTranslation, POPULAR_LANGUAGES, LANGUAGE_META, BUNDLED_LANGUAGES } from "@/utils/i18n";

// Global Language Selector Component for Header
const GlobalLanguageSelector = ({ compact = false }) => {
  const { language, setLanguage, t, getLanguageInfo, isBundled } = useTranslation();
  const currentLang = getLanguageInfo(language);

  // Get all available languages
  const allLanguages = Object.entries(LANGUAGE_META).map(([code, info]) => ({
    code,
    ...info,
    isBundled: BUNDLED_LANGUAGES.includes(code)
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

  const popularLanguages = sortedLanguages.filter(l => POPULAR_LANGUAGES.includes(l.code));
  const otherLanguages = sortedLanguages.filter(l => !POPULAR_LANGUAGES.includes(l.code));

  if (compact) {
    return (
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="sm" className="gap-1 px-2" data-testid="language-selector">
            <span className="text-lg">{currentLang.flag}</span>
            <ChevronDown className="w-3 h-3 opacity-50" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-52 max-h-80 overflow-y-auto">
          <DropdownMenuLabel className="text-xs text-slate-500">
            {t("language.selectLanguage")}
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          {sortedLanguages.slice(0, 12).map((lang) => (
            <DropdownMenuItem
              key={lang.code}
              onClick={() => setLanguage(lang.code)}
              className="flex items-center justify-between cursor-pointer"
            >
              <span className="flex items-center gap-2">
                <span>{lang.flag}</span>
                <span>{lang.name}</span>
                {!lang.isBundled && (
                  <span className="text-[10px] px-1 bg-amber-100 text-amber-700 rounded">AI</span>
                )}
              </span>
              {language === lang.code && <Check className="w-4 h-4 text-green-500" />}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>
    );
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm" className="gap-2" data-testid="language-selector">
          <Globe className="w-4 h-4" />
          <span className="hidden sm:inline">{currentLang.flag} {currentLang.name}</span>
          <span className="sm:hidden">{currentLang.flag}</span>
          <ChevronDown className="w-3 h-3 opacity-50" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-60 max-h-96 overflow-y-auto">
        <DropdownMenuLabel className="flex items-center gap-2">
          <Globe className="w-4 h-4" />
          {t("language.selectLanguage")}
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        
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
                <span className="text-[10px] px-1 bg-amber-100 text-amber-700 rounded" title="AI Translated">AI</span>
              )}
            </span>
            {language === lang.code && <Check className="w-4 h-4 text-green-500" />}
          </DropdownMenuItem>
        ))}
        
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
                    <span className="text-[10px] px-1 bg-amber-100 text-amber-700 rounded" title="AI Translated">AI</span>
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
