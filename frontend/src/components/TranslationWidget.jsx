import { useState, useEffect } from "react";
import { useTranslation } from "@/utils/i18n";
import axios from "axios";
import { toast } from "sonner";
import { useTheme } from "@/App";
import { 
  Languages, Globe, ArrowRight, Copy, Check, Loader2, 
  Volume2, RefreshCw, ChevronDown, Sparkles
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";

const API = process.env.REACT_APP_BACKEND_URL;

// Popular languages shown first
const POPULAR_LANGUAGES = ["en", "es", "fr", "de", "zh", "ja", "pt", "ar", "hi", "ko"];

const TranslationWidget = ({ 
  text, 
  onTranslate, 
  compact = false,
  showDetect = true,
  context = "general" // general, cover_letter, job_description, resume
}) => {
  const { isDark } = useTheme();
  const [languages, setLanguages] = useState([]);
  const [targetLanguage, setTargetLanguage] = useState("");
  const [detectedLanguage, setDetectedLanguage] = useState(null);
  const [translatedText, setTranslatedText] = useState("");
  const [loading, setLoading] = useState(false);
  const [detecting, setDetecting] = useState(false);
  const [copied, setCopied] = useState(false);
  const [showDialog, setShowDialog] = useState(false);

  useEffect(() => {
    fetchLanguages();
  }, []);

  const fetchLanguages = async () => {
    try {
      const response = await axios.get(`${API}/api/translate/languages`);
      setLanguages(response.data.languages || []);
    } catch (e) {
      console.error("Failed to load languages");
    }
  };

  const detectLanguage = async () => {
    if (!text?.trim()) return;
    
    setDetecting(true);
    try {
      const response = await axios.post(`${API}/api/translate/detect`, { text });
      setDetectedLanguage(response.data);
    } catch (e) {
      toast.error("Failed to detect language");
    }
    setDetecting(false);
  };

  const translate = async () => {
    if (!text?.trim() || !targetLanguage) {
      toast.error("Please select a target language");
      return;
    }

    setLoading(true);
    try {
      let endpoint = `${API}/api/translate/text`;
      let payload = { text, target_language: targetLanguage };

      // Use specialized endpoints for specific contexts
      if (context === "cover_letter") {
        endpoint = `${API}/api/translate/cover-letter`;
        payload = { cover_letter: text, target_language: targetLanguage };
      } else if (context === "job_description") {
        endpoint = `${API}/api/translate/job-description`;
        payload = { job: { description: text }, target_language: targetLanguage };
      }

      const response = await axios.post(endpoint, payload);
      
      const translated = context === "cover_letter" 
        ? response.data.translated_cover_letter
        : context === "job_description"
        ? response.data.description
        : response.data.translated_text;
      
      setTranslatedText(translated);
      
      if (onTranslate) {
        onTranslate(translated, targetLanguage);
      }
      
      toast.success("Translation complete");
    } catch (e) {
      toast.error("Translation failed");
    }
    setLoading(false);
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(translatedText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
    toast.success("Copied to clipboard");
  };

  const speakText = (textToSpeak) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(textToSpeak);
      const langInfo = languages.find(l => l.code === targetLanguage);
      if (langInfo) {
        utterance.lang = targetLanguage;
      }
      window.speechSynthesis.speak(utterance);
    }
  };

  // Sort languages: popular first, then alphabetically
  const sortedLanguages = [...languages].sort((a, b) => {
    const aPopular = POPULAR_LANGUAGES.indexOf(a.code);
    const bPopular = POPULAR_LANGUAGES.indexOf(b.code);
    
    if (aPopular !== -1 && bPopular !== -1) return aPopular - bPopular;
    if (aPopular !== -1) return -1;
    if (bPopular !== -1) return 1;
    return a.name.localeCompare(b.name);
  });

  if (compact) {
    return (
      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setShowDialog(true)}
          className="gap-2"
        >
          <Languages className="w-4 h-4" />
          Translate
        </Button>

        <Dialog open={showDialog} onOpenChange={setShowDialog}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Languages className="w-5 h-5 text-purple-500" />
                Translate Content
              </DialogTitle>
            </DialogHeader>

            <TranslationContent
              text={text}
              languages={sortedLanguages}
              targetLanguage={targetLanguage}
              setTargetLanguage={setTargetLanguage}
              detectedLanguage={detectedLanguage}
              translatedText={translatedText}
              loading={loading}
              detecting={detecting}
              detectLanguage={detectLanguage}
              translate={translate}
              copyToClipboard={copyToClipboard}
              speakText={speakText}
              copied={copied}
              showDetect={showDetect}
              isDark={isDark}
            />

            <DialogFooter>
              <Button variant="outline" onClick={() => setShowDialog(false)}>
                Close
              </Button>
              {translatedText && (
                <Button onClick={() => {
                  if (onTranslate) onTranslate(translatedText, targetLanguage);
                  setShowDialog(false);
                }}>
                  Use Translation
                </Button>
              )}
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    );
  }

  return (
    <Card className={isDark ? 'bg-slate-800/50 border-slate-700' : ''}>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center gap-2">
          <Languages className="w-5 h-5 text-purple-500" />
          Translation
        </CardTitle>
      </CardHeader>
      <CardContent>
        <TranslationContent
          text={text}
          languages={sortedLanguages}
          targetLanguage={targetLanguage}
          setTargetLanguage={setTargetLanguage}
          detectedLanguage={detectedLanguage}
          translatedText={translatedText}
          loading={loading}
          detecting={detecting}
          detectLanguage={detectLanguage}
          translate={translate}
          copyToClipboard={copyToClipboard}
          speakText={speakText}
          copied={copied}
          showDetect={showDetect}
          isDark={isDark}
        />
      </CardContent>
    </Card>
  );
};

// Inner translation content component
const TranslationContent = ({
  text,
  languages,
  targetLanguage,
  setTargetLanguage,
  detectedLanguage,
  translatedText,
  loading,
  detecting,
  detectLanguage,
  translate,
  copyToClipboard,
  speakText,
  copied,
  showDetect,
  isDark
}) => {
  return (
    <div className="space-y-4">
      {/* Language Detection */}
      {showDetect && (
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={detectLanguage}
            disabled={detecting || !text?.trim()}
            className="gap-2"
          >
            {detecting ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Globe className="w-4 h-4" />
            )}
            Detect Language
          </Button>
          
          {detectedLanguage && (
            <Badge variant="secondary" className="gap-1">
              {detectedLanguage.language_info?.flag} {detectedLanguage.language_name}
              <span className="text-xs opacity-60">
                ({Math.round(detectedLanguage.confidence * 100)}%)
              </span>
            </Badge>
          )}
        </div>
      )}

      {/* Language Selection */}
      <div className="flex items-center gap-3">
        <div className="flex-1">
          <Select value={targetLanguage} onValueChange={setTargetLanguage}>
            <SelectTrigger>
              <SelectValue placeholder={t("translation.selectTargetLanguage")} />
            </SelectTrigger>
            <SelectContent className="max-h-[300px]">
              {languages.map((lang) => (
                <SelectItem key={lang.code} value={lang.code}>
                  <span className="flex items-center gap-2">
                    <span>{lang.flag}</span>
                    <span>{lang.name}</span>
                    <span className="text-xs text-slate-400">({lang.native})</span>
                  </span>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        
        <Button
          onClick={translate}
          disabled={loading || !targetLanguage || !text?.trim()}
          className="gap-2"
        >
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Sparkles className="w-4 h-4" />
          )}
          Translate
        </Button>
      </div>

      {/* Original Text Preview */}
      {text && (
        <div className={`p-3 rounded-lg ${isDark ? 'bg-slate-700/50' : 'bg-slate-100'}`}>
          <p className="text-xs text-slate-500 mb-1">Original text:</p>
          <p className="text-sm line-clamp-3">{text}</p>
        </div>
      )}

      {/* Translated Result */}
      {translatedText && (
        <div className={`p-4 rounded-lg border ${isDark ? 'bg-slate-700/30 border-slate-600' : 'bg-white border-slate-200'}`}>
          <div className="flex items-center justify-between mb-2">
            <p className="text-xs text-purple-500 font-medium">Translated:</p>
            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => speakText(translatedText)}
                className="h-8 w-8 p-0"
                title="Listen"
              >
                <Volume2 className="w-4 h-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={copyToClipboard}
                className="h-8 w-8 p-0"
                title="Copy"
              >
                {copied ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
              </Button>
            </div>
          </div>
          <p className="text-sm whitespace-pre-wrap">{translatedText}</p>
        </div>
      )}
    </div>
  );
};

// Language Selector Component (for settings/preferences)
export const LanguageSelector = ({ value, onChange, label = "Preferred Language" }) => {
  const [languages, setLanguages] = useState([]);
  const { isDark } = useTheme();

  useEffect(() => {
    const fetchLanguages = async () => {
      try {
        const response = await axios.get(`${API}/api/translate/languages`);
        setLanguages(response.data.languages || []);
      } catch (e) {
        console.error("Failed to load languages");
      }
    };
    fetchLanguages();
  }, []);

  // Sort languages
  const sortedLanguages = [...languages].sort((a, b) => {
    const aPopular = POPULAR_LANGUAGES.indexOf(a.code);
    const bPopular = POPULAR_LANGUAGES.indexOf(b.code);
    if (aPopular !== -1 && bPopular !== -1) return aPopular - bPopular;
    if (aPopular !== -1) return -1;
    if (bPopular !== -1) return 1;
    return a.name.localeCompare(b.name);
  });

  return (
    <div className="space-y-2">
      {label && <label className="text-sm font-medium">{label}</label>}
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger>
          <SelectValue placeholder={t("translation.selectLanguage")}>
            {value && languages.find(l => l.code === value) && (
              <span className="flex items-center gap-2">
                <span>{languages.find(l => l.code === value)?.flag}</span>
                <span>{languages.find(l => l.code === value)?.name}</span>
              </span>
            )}
          </SelectValue>
        </SelectTrigger>
        <SelectContent className="max-h-[300px]">
          {sortedLanguages.map((lang) => (
            <SelectItem key={lang.code} value={lang.code}>
              <span className="flex items-center gap-2">
                <span>{lang.flag}</span>
                <span>{lang.name}</span>
              </span>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
};

// Quick Translate Button (for inline use)
export const QuickTranslateButton = ({ text, onTranslate }) => {
  const [showPopover, setShowPopover] = useState(false);
  
  return (
    <TranslationWidget 
      text={text} 
      onTranslate={onTranslate} 
      compact={true}
      showDetect={false}
    />
  );
};

export default TranslationWidget;
