import { useState, useEffect, createContext, useContext } from "react";
import axios from "axios";
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

const API = process.env.REACT_APP_BACKEND_URL;

// Strategic language priority order based on market research
const POPULAR_CODES = [
  // EFIGS Foundation
  "en", "es", "fr", "de", "it",
  // CJK Growth Block
  "zh", "ja", "ko",
  // Rapidly Expanding Markets
  "hi", "pt-BR", "ar",
  // Additional high-value
  "pt", "zh-TW"
];

// Language Context for global state
const LanguageContext = createContext();

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    return { 
      selectedLanguage: "en", 
      setSelectedLanguage: () => {},
      languages: [],
      getLanguageName: () => "English"
    };
  }
  return context;
};

export const LanguageProvider = ({ children }) => {
  const [selectedLanguage, setSelectedLanguage] = useState(() => {
    return localStorage.getItem("medmatch-language") || "en";
  });
  const [languages, setLanguages] = useState([]);

  useEffect(() => {
    fetchLanguages();
  }, []);

  useEffect(() => {
    localStorage.setItem("medmatch-language", selectedLanguage);
  }, [selectedLanguage]);

  const fetchLanguages = async () => {
    try {
      const response = await axios.get(`${API}/api/translate/languages`);
      setLanguages(response.data.languages || []);
    } catch (e) {
      console.error("Failed to load languages");
      // Default fallback
      setLanguages([
        { code: "en", name: "English", native: "English", flag: "🇺🇸" },
        { code: "es", name: "Spanish", native: "Español", flag: "🇪🇸" },
        { code: "fr", name: "French", native: "Français", flag: "🇫🇷" },
        { code: "de", name: "German", native: "Deutsch", flag: "🇩🇪" },
        { code: "zh", name: "Chinese", native: "中文", flag: "🇨🇳" },
      ]);
    }
  };

  const getLanguageName = (code) => {
    const lang = languages.find(l => l.code === code);
    return lang?.name || "English";
  };

  const getLanguageInfo = (code) => {
    return languages.find(l => l.code === code) || { code: "en", name: "English", flag: "🇺🇸" };
  };

  return (
    <LanguageContext.Provider value={{ 
      selectedLanguage, 
      setSelectedLanguage, 
      languages,
      getLanguageName,
      getLanguageInfo
    }}>
      {children}
    </LanguageContext.Provider>
  );
};

// Global Language Selector Component for Header
const GlobalLanguageSelector = ({ compact = false }) => {
  const { selectedLanguage, setSelectedLanguage, languages, getLanguageInfo } = useLanguage();
  const currentLang = getLanguageInfo(selectedLanguage);

  // Sort languages: popular first
  const sortedLanguages = [...languages].sort((a, b) => {
    const aPopular = POPULAR_CODES.indexOf(a.code);
    const bPopular = POPULAR_CODES.indexOf(b.code);
    if (aPopular !== -1 && bPopular !== -1) return aPopular - bPopular;
    if (aPopular !== -1) return -1;
    if (bPopular !== -1) return 1;
    return a.name.localeCompare(b.name);
  });

  const popularLanguages = sortedLanguages.filter(l => POPULAR_CODES.includes(l.code));
  const otherLanguages = sortedLanguages.filter(l => !POPULAR_CODES.includes(l.code));

  if (compact) {
    return (
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="sm" className="gap-1 px-2" data-testid="language-selector">
            <span className="text-lg">{currentLang.flag}</span>
            <ChevronDown className="w-3 h-3 opacity-50" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-48 max-h-80 overflow-y-auto">
          <DropdownMenuLabel className="text-xs text-slate-500">Select Language</DropdownMenuLabel>
          <DropdownMenuSeparator />
          {sortedLanguages.slice(0, 10).map((lang) => (
            <DropdownMenuItem
              key={lang.code}
              onClick={() => setSelectedLanguage(lang.code)}
              className="flex items-center justify-between cursor-pointer"
            >
              <span className="flex items-center gap-2">
                <span>{lang.flag}</span>
                <span>{lang.name}</span>
              </span>
              {selectedLanguage === lang.code && <Check className="w-4 h-4 text-green-500" />}
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
      <DropdownMenuContent align="end" className="w-56 max-h-96 overflow-y-auto">
        <DropdownMenuLabel className="flex items-center gap-2">
          <Globe className="w-4 h-4" />
          Select Language
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        
        {/* Popular Languages */}
        <DropdownMenuLabel className="text-xs text-slate-400 font-normal">Popular</DropdownMenuLabel>
        {popularLanguages.map((lang) => (
          <DropdownMenuItem
            key={lang.code}
            onClick={() => setSelectedLanguage(lang.code)}
            className="flex items-center justify-between cursor-pointer"
          >
            <span className="flex items-center gap-2">
              <span className="text-lg">{lang.flag}</span>
              <span>{lang.name}</span>
              <span className="text-xs text-slate-400">({lang.native})</span>
            </span>
            {selectedLanguage === lang.code && <Check className="w-4 h-4 text-green-500" />}
          </DropdownMenuItem>
        ))}
        
        {/* Other Languages */}
        {otherLanguages.length > 0 && (
          <>
            <DropdownMenuSeparator />
            <DropdownMenuLabel className="text-xs text-slate-400 font-normal">Other Languages</DropdownMenuLabel>
            {otherLanguages.map((lang) => (
              <DropdownMenuItem
                key={lang.code}
                onClick={() => setSelectedLanguage(lang.code)}
                className="flex items-center justify-between cursor-pointer"
              >
                <span className="flex items-center gap-2">
                  <span className="text-lg">{lang.flag}</span>
                  <span>{lang.name}</span>
                </span>
                {selectedLanguage === lang.code && <Check className="w-4 h-4 text-green-500" />}
              </DropdownMenuItem>
            ))}
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default GlobalLanguageSelector;
