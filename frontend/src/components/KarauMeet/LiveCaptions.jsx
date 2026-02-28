import { useState, useEffect, useRef, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Captions, CaptionsOff, Circle, Globe } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const LANG_NAMES = {
  en: 'EN', es: 'ES', fr: 'FR', de: 'DE', pt: 'PT', zh: 'ZH',
  ja: 'JA', ko: 'KO', ar: 'AR', hi: 'HI', it: 'IT', ru: 'RU',
  nl: 'NL', tr: 'TR', sv: 'SV', pl: 'PL'
};

const LiveCaptions = ({ isEnabled, onTranscriptUpdate, onToggle, targetLang = 'en' }) => {
  const [caption, setCaption] = useState('');
  const [translatedCaption, setTranslatedCaption] = useState('');
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);
  const transcriptRef = useRef([]);
  const restartTimeoutRef = useRef(null);
  const translationTimeoutRef = useRef(null);

  const translateCaption = useCallback(async (text) => {
    if (!text || targetLang === 'en') {
      setTranslatedCaption('');
      return;
    }
    clearTimeout(translationTimeoutRef.current);
    translationTimeoutRef.current = setTimeout(async () => {
      try {
        const token = localStorage.getItem('token');
        const res = await fetch(`${API}/api/karau-features/translate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify({ text, target_lang: targetLang, source_lang: 'en' })
        });
        if (res.ok) {
          const data = await res.json();
          setTranslatedCaption(data.translated_text);
        }
      } catch (e) {
        console.warn('Translation failed:', e);
      }
    }, 500);
  }, [targetLang]);

  const startRecognition = useCallback(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    if (recognitionRef.current) {
      try { recognitionRef.current.stop(); } catch {}
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    recognition.maxAlternatives = 1;

    recognition.onstart = () => setIsListening(true);

    recognition.onresult = (event) => {
      let interim = '';
      let final = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          final += transcript;
        } else {
          interim += transcript;
        }
      }

      if (final) {
        const segment = {
          speaker: 'You',
          text: final.trim(),
          timestamp: new Date().toISOString()
        };
        transcriptRef.current.push(segment);
        onTranscriptUpdate?.(segment);
        setCaption(final.trim());
        if (targetLang !== 'en') translateCaption(final.trim());
      } else if (interim) {
        setCaption(interim);
      }
    };

    recognition.onerror = (event) => {
      if (event.error === 'no-speech' || event.error === 'aborted') {
        if (isEnabled) {
          restartTimeoutRef.current = setTimeout(startRecognition, 300);
        }
        return;
      }
      console.warn('Speech recognition error:', event.error);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
      if (isEnabled) {
        restartTimeoutRef.current = setTimeout(startRecognition, 300);
      }
    };

    recognitionRef.current = recognition;
    try { recognition.start(); } catch {}
  }, [isEnabled, onTranscriptUpdate, targetLang, translateCaption]);

  useEffect(() => {
    if (isEnabled) {
      startRecognition();
    } else {
      if (recognitionRef.current) {
        try { recognitionRef.current.stop(); } catch {}
      }
      clearTimeout(restartTimeoutRef.current);
      clearTimeout(translationTimeoutRef.current);
      setIsListening(false);
      setCaption('');
      setTranslatedCaption('');
    }
    return () => {
      if (recognitionRef.current) {
        try { recognitionRef.current.stop(); } catch {}
      }
      clearTimeout(restartTimeoutRef.current);
      clearTimeout(translationTimeoutRef.current);
    };
  }, [isEnabled, startRecognition]);

  const getFullTranscript = useCallback(() => transcriptRef.current, []);

  useEffect(() => {
    if (window) window.__karauGetTranscript = getFullTranscript;
    return () => { if (window) delete window.__karauGetTranscript; };
  }, [getFullTranscript]);

  if (!isEnabled) return null;

  const displayCaption = targetLang !== 'en' && translatedCaption ? translatedCaption : caption;

  return (
    <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-30 max-w-[80%] pointer-events-none" data-testid="live-captions">
      {caption && (
        <div className="bg-black/85 backdrop-blur-md rounded-xl px-5 py-3 text-center">
          <div className="flex items-center justify-center gap-2 mb-1.5">
            {isListening && (
              <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30 text-[10px] px-1.5 py-0">
                <Circle className="w-1.5 h-1.5 mr-1 fill-current animate-pulse" />
                LIVE
              </Badge>
            )}
            {targetLang !== 'en' && (
              <Badge className="bg-amber-500/20 text-amber-400 border-amber-500/30 text-[10px] px-1.5 py-0">
                <Globe className="w-2.5 h-2.5 mr-1" />
                {LANG_NAMES[targetLang] || targetLang.toUpperCase()}
              </Badge>
            )}
          </div>
          <p className="text-white text-sm md:text-base font-medium leading-relaxed">
            {displayCaption}
          </p>
          {targetLang !== 'en' && translatedCaption && (
            <p className="text-slate-400 text-xs mt-1 italic">{caption}</p>
          )}
        </div>
      )}
    </div>
  );
};

export const CaptionsButton = ({ isEnabled, onToggle }) => (
  <Button
    variant={isEnabled ? 'default' : 'secondary'}
    size="lg"
    className={`rounded-full w-12 h-12 ${isEnabled ? 'bg-purple-500' : ''}`}
    onClick={onToggle}
    title={isEnabled ? 'Disable Captions' : 'Enable Captions'}
    data-testid="control-captions"
  >
    {isEnabled ? <Captions className="w-5 h-5" /> : <CaptionsOff className="w-5 h-5" />}
  </Button>
);

export default LiveCaptions;
