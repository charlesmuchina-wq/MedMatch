/**
 * AIWritingToolbar - AI-powered writing assistant for LUMI chat
 * Features: Tone refinement, smart replies, translation, voice-to-text
 */
import { useState, useRef } from 'react';
import {
  Wand2, Sparkles, MessageSquare, Globe, Mic, MicOff,
  ArrowRight, Loader2, ChevronDown, X, Volume2
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const TONES = [
  { id: 'professional', label: 'Professional', emoji: '💼' },
  { id: 'friendly', label: 'Friendly', emoji: '😊' },
  { id: 'assertive', label: 'Assertive', emoji: '💪' },
  { id: 'concise', label: 'Concise', emoji: '✂️' },
];

const LANGUAGES = [
  { code: 'es', name: 'Spanish' }, { code: 'fr', name: 'French' },
  { code: 'de', name: 'German' }, { code: 'ja', name: 'Japanese' },
  { code: 'zh', name: 'Chinese' }, { code: 'ko', name: 'Korean' },
  { code: 'pt', name: 'Portuguese' }, { code: 'ar', name: 'Arabic' },
  { code: 'hi', name: 'Hindi' }, { code: 'ru', name: 'Russian' },
];

const AIWritingToolbar = ({ messageText, onTextChange, messages = [], channelName = '' }) => {
  const [showTones, setShowTones] = useState(false);
  const [showTranslate, setShowTranslate] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(null); // 'refine', 'suggest', 'translate', 'voice'
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  const refineText = async (instruction) => {
    if (!messageText.trim()) return;
    setLoading('refine');
    setShowTones(false);
    try {
      const res = await fetch(`${API}/api/lumi/ai/refine`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: messageText, instruction })
      });
      if (res.ok) {
        const data = await res.json();
        onTextChange(data.refined_text);
      }
    } catch (e) {
      console.error('Refine failed:', e);
    } finally {
      setLoading(null);
    }
  };

  const getSuggestions = async () => {
    if (messages.length === 0) return;
    setLoading('suggest');
    setShowSuggestions(true);
    try {
      const res = await fetch(`${API}/api/lumi/ai/smart-reply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: messages.slice(-5), channel_name: channelName })
      });
      if (res.ok) {
        const data = await res.json();
        setSuggestions(data.suggestions || []);
      }
    } catch (e) {
      console.error('Suggestions failed:', e);
    } finally {
      setLoading(null);
    }
  };

  const translateText = async (langCode) => {
    if (!messageText.trim()) return;
    setLoading('translate');
    setShowTranslate(false);
    try {
      const res = await fetch(`${API}/api/lumi/ai/translate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: messageText, target_language: langCode })
      });
      if (res.ok) {
        const data = await res.json();
        onTextChange(data.translated_text);
      }
    } catch (e) {
      console.error('Translate failed:', e);
    } finally {
      setLoading(null);
    }
  };

  const toggleRecording = async () => {
    if (recording) {
      mediaRecorderRef.current?.stop();
      setRecording(false);
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      chunksRef.current = [];
      mediaRecorder.ondataavailable = (e) => chunksRef.current.push(e.data);
      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach(t => t.stop());
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        setLoading('voice');
        try {
          const formData = new FormData();
          formData.append('file', blob, 'voice.webm');
          const res = await fetch(`${API}/api/lumi/ai/voice-to-text`, { method: 'POST', body: formData });
          if (res.ok) {
            const data = await res.json();
            onTextChange(data.polished_text || data.raw_text);
          }
        } catch (e) {
          console.error('Voice transcription failed:', e);
        } finally {
          setLoading(null);
        }
      };
      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setRecording(true);
    } catch (e) {
      console.error('Microphone access denied:', e);
    }
  };

  return (
    <div className="relative" data-testid="ai-writing-toolbar">
      {/* Smart Reply Suggestions */}
      {showSuggestions && suggestions.length > 0 && (
        <div className="absolute bottom-full left-0 right-0 mb-1 p-2 bg-[#161B22] border border-white/10 rounded-xl shadow-xl z-10">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider font-outfit">Smart Replies</span>
            <button onClick={() => { setShowSuggestions(false); setSuggestions([]); }} className="p-0.5 hover:bg-white/10 rounded"><X className="w-3 h-3 text-slate-500" /></button>
          </div>
          <div className="space-y-1">
            {suggestions.map((s, i) => (
              <button key={i} onClick={() => { onTextChange(s); setShowSuggestions(false); setSuggestions([]); }}
                className="w-full text-left px-2.5 py-1.5 rounded-lg text-xs text-white/80 hover:bg-white/5 hover:text-white transition-colors truncate"
                data-testid={`smart-reply-${i}`}>
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Tone Picker */}
      {showTones && (
        <div className="absolute bottom-full left-0 mb-1 p-1.5 bg-[#161B22] border border-white/10 rounded-xl shadow-xl z-10 min-w-[160px]">
          {TONES.map(t => (
            <button key={t.id} onClick={() => refineText(t.id)}
              className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs text-white/80 hover:bg-white/5 hover:text-white transition-colors"
              data-testid={`tone-${t.id}`}>
              <span className="text-sm">{t.emoji}</span> {t.label}
            </button>
          ))}
        </div>
      )}

      {/* Language Picker */}
      {showTranslate && (
        <div className="absolute bottom-full right-0 mb-1 p-1.5 bg-[#161B22] border border-white/10 rounded-xl shadow-xl z-10 min-w-[140px] max-h-[200px] overflow-auto">
          {LANGUAGES.map(l => (
            <button key={l.code} onClick={() => translateText(l.code)}
              className="w-full text-left px-2.5 py-1.5 rounded-lg text-xs text-white/80 hover:bg-white/5 hover:text-white transition-colors"
              data-testid={`lang-${l.code}`}>
              {l.name}
            </button>
          ))}
        </div>
      )}

      {/* Toolbar Buttons */}
      <div className="flex items-center gap-1 px-1">
        <button onClick={() => { setShowTones(!showTones); setShowTranslate(false); }}
          disabled={!messageText.trim() || loading}
          className="flex items-center gap-1 px-2 py-1 rounded-lg text-[10px] font-medium text-slate-400 hover:text-white hover:bg-white/5 transition-colors disabled:opacity-30"
          title="Refine tone" data-testid="ai-refine-btn">
          {loading === 'refine' ? <Loader2 className="w-3 h-3 animate-spin" /> : <Wand2 className="w-3 h-3" />}
          <span className="hidden sm:inline">Refine</span>
        </button>

        <button onClick={getSuggestions}
          disabled={messages.length === 0 || loading}
          className="flex items-center gap-1 px-2 py-1 rounded-lg text-[10px] font-medium text-slate-400 hover:text-white hover:bg-white/5 transition-colors disabled:opacity-30"
          title="Smart replies" data-testid="ai-suggest-btn">
          {loading === 'suggest' ? <Loader2 className="w-3 h-3 animate-spin" /> : <Sparkles className="w-3 h-3" />}
          <span className="hidden sm:inline">Suggest</span>
        </button>

        <button onClick={() => { setShowTranslate(!showTranslate); setShowTones(false); }}
          disabled={!messageText.trim() || loading}
          className="flex items-center gap-1 px-2 py-1 rounded-lg text-[10px] font-medium text-slate-400 hover:text-white hover:bg-white/5 transition-colors disabled:opacity-30"
          title="Translate" data-testid="ai-translate-btn">
          {loading === 'translate' ? <Loader2 className="w-3 h-3 animate-spin" /> : <Globe className="w-3 h-3" />}
          <span className="hidden sm:inline">Translate</span>
        </button>

        <button onClick={toggleRecording}
          disabled={loading === 'voice'}
          className={`flex items-center gap-1 px-2 py-1 rounded-lg text-[10px] font-medium transition-colors ${
            recording ? 'text-red-400 bg-red-500/10 animate-pulse' : 'text-slate-400 hover:text-white hover:bg-white/5'
          } ${loading === 'voice' ? 'opacity-30' : ''}`}
          title="Voice to text" data-testid="ai-voice-btn">
          {loading === 'voice' ? <Loader2 className="w-3 h-3 animate-spin" /> : recording ? <MicOff className="w-3 h-3" /> : <Mic className="w-3 h-3" />}
          <span className="hidden sm:inline">{recording ? 'Stop' : 'Voice'}</span>
        </button>
      </div>
    </div>
  );
};

export default AIWritingToolbar;
