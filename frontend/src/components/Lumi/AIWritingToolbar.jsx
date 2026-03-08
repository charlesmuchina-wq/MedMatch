/**
 * AIWritingToolbar - AI-powered writing assistant for ENZI chat
 * Features: Tone refinement, smart replies, translation, voice-to-text, templates
 */
import { useState, useRef, useEffect } from 'react';
import {
  Wand2, Sparkles, Globe, Mic, MicOff,
  Loader2, X, BookMarked, Save, Trash2, Copy
} from 'lucide-react';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

const TONES = [
  { id: 'professional', label: 'Professional', emoji: '\uD83D\uDCBC' },
  { id: 'friendly', label: 'Friendly', emoji: '\uD83D\uDE0A' },
  { id: 'assertive', label: 'Assertive', emoji: '\uD83D\uDCAA' },
  { id: 'concise', label: 'Concise', emoji: '\u2702\uFE0F' },
];

const LANGUAGES = [
  { code: 'es', name: 'Spanish' }, { code: 'fr', name: 'French' },
  { code: 'de', name: 'German' }, { code: 'ja', name: 'Japanese' },
  { code: 'zh', name: 'Chinese' }, { code: 'ko', name: 'Korean' },
  { code: 'pt', name: 'Portuguese' }, { code: 'ar', name: 'Arabic' },
  { code: 'hi', name: 'Hindi' }, { code: 'ru', name: 'Russian' },
];

const AIWritingToolbar = ({ messageText, onTextChange, messages = [], channelName = '', token = '' }) => {
  const [showTones, setShowTones] = useState(false);
  const [showTranslate, setShowTranslate] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [showTemplates, setShowTemplates] = useState(false);
  const [showSaveTemplate, setShowSaveTemplate] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [templateName, setTemplateName] = useState('');
  const [lastAction, setLastAction] = useState(''); // refine, translate, suggest
  const [loading, setLoading] = useState(null);
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  const authHeaders = { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` };

  // Load templates
  useEffect(() => {
    if (token) loadTemplates();
  }, [token]);

  const loadTemplates = async () => {
    try {
      const res = await fetch(`${API}/api/lumi/templates`, { headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) setTemplates((await res.json()).templates || []);
    } catch (e) {}
  };

  const closeAllDropdowns = () => {
    setShowTones(false); setShowTranslate(false); setShowSuggestions(false);
    setShowTemplates(false); setShowSaveTemplate(false);
  };

  const refineText = async (instruction) => {
    if (!messageText.trim()) return;
    setLoading('refine');
    closeAllDropdowns();
    try {
      const res = await fetch(`${API}/api/lumi/ai/refine`, {
        method: 'POST', headers: authHeaders,
        body: JSON.stringify({ text: messageText, instruction })
      });
      if (res.ok) {
        const data = await res.json();
        onTextChange(data.refined_text);
        setLastAction('refine');
      }
    } catch (e) { console.error('Refine failed:', e); }
    finally { setLoading(null); }
  };

  const getSuggestions = async () => {
    if (messages.length === 0) return;
    setLoading('suggest');
    closeAllDropdowns();
    setShowSuggestions(true);
    try {
      const res = await fetch(`${API}/api/lumi/ai/smart-reply`, {
        method: 'POST', headers: authHeaders,
        body: JSON.stringify({ messages: messages.slice(-5), channel_name: channelName })
      });
      if (res.ok) setSuggestions((await res.json()).suggestions || []);
    } catch (e) { console.error('Suggestions failed:', e); }
    finally { setLoading(null); }
  };

  const translateText = async (langCode) => {
    if (!messageText.trim()) return;
    setLoading('translate');
    closeAllDropdowns();
    try {
      const res = await fetch(`${API}/api/lumi/ai/translate`, {
        method: 'POST', headers: authHeaders,
        body: JSON.stringify({ text: messageText, target_language: langCode })
      });
      if (res.ok) {
        const data = await res.json();
        onTextChange(data.translated_text);
        setLastAction('translate');
      }
    } catch (e) { console.error('Translate failed:', e); }
    finally { setLoading(null); }
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
        } catch (e) { console.error('Voice transcription failed:', e); }
        finally { setLoading(null); }
      };
      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setRecording(true);
    } catch (e) { console.error('Microphone access denied:', e); }
  };

  // Template actions
  const saveAsTemplate = async () => {
    if (!messageText.trim() || !templateName.trim()) return;
    try {
      const res = await fetch(`${API}/api/lumi/templates`, {
        method: 'POST', headers: authHeaders,
        body: JSON.stringify({ name: templateName, text: messageText, category: lastAction || 'general', source_action: lastAction })
      });
      if (res.ok) {
        toast.success('Template saved!');
        setShowSaveTemplate(false);
        setTemplateName('');
        loadTemplates();
      }
    } catch (e) { toast.error('Failed to save'); }
  };

  const applyTemplate = async (tpl) => {
    try {
      const res = await fetch(`${API}/api/lumi/templates/${tpl.id}/apply`, {
        method: 'POST', headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        onTextChange(data.text);
        closeAllDropdowns();
        toast.success(`Applied: ${data.name}`);
      }
    } catch (e) { toast.error('Failed'); }
  };

  const deleteTemplate = async (id) => {
    try {
      await fetch(`${API}/api/lumi/templates/${id}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` } });
      loadTemplates();
      toast.success('Template deleted');
    } catch (e) {}
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
              <button key={i} onClick={() => { onTextChange(s); setShowSuggestions(false); setSuggestions([]); setLastAction('suggest'); }}
                className="w-full text-left px-2.5 py-1.5 rounded-lg text-xs text-white/80 hover:bg-white/5 hover:text-white transition-colors truncate"
                data-testid={`smart-reply-${i}`}>{s}</button>
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
              data-testid={`lang-${l.code}`}>{l.name}</button>
          ))}
        </div>
      )}

      {/* Save Template Popup */}
      {showSaveTemplate && (
        <div className="absolute bottom-full left-0 mb-1 p-3 bg-[#161B22] border border-white/10 rounded-xl shadow-xl z-10 w-64">
          <p className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mb-2 font-outfit">Save as Template</p>
          <input value={templateName} onChange={e => setTemplateName(e.target.value)}
            placeholder="Template name..."
            className="w-full bg-white/5 border border-white/10 rounded-lg px-2.5 py-1.5 text-xs text-white placeholder-slate-500 outline-none focus:border-[#00CEC9]/50 mb-2"
            data-testid="template-name-input" />
          <p className="text-[10px] text-slate-600 mb-2 truncate">{messageText.slice(0, 80)}...</p>
          <div className="flex gap-2">
            <button onClick={() => setShowSaveTemplate(false)} className="flex-1 px-2 py-1 rounded-lg text-[10px] text-slate-400 hover:bg-white/5">Cancel</button>
            <button onClick={saveAsTemplate} disabled={!templateName.trim()}
              className="flex-1 px-2 py-1 rounded-lg text-[10px] bg-[#00CEC9]/10 text-[#00CEC9] hover:bg-[#00CEC9]/20 disabled:opacity-30 font-medium"
              data-testid="save-template-btn">Save</button>
          </div>
        </div>
      )}

      {/* Template Library */}
      {showTemplates && (
        <div className="absolute bottom-full left-0 right-0 mb-1 p-2 bg-[#161B22] border border-white/10 rounded-xl shadow-xl z-10 max-h-[240px] overflow-auto">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider font-outfit">Templates ({templates.length})</span>
            <button onClick={() => setShowTemplates(false)} className="p-0.5 hover:bg-white/10 rounded"><X className="w-3 h-3 text-slate-500" /></button>
          </div>
          {templates.length === 0 ? (
            <p className="text-[10px] text-slate-600 py-2 text-center">No templates yet. Refine text and save it!</p>
          ) : (
            <div className="space-y-1">
              {templates.map(tpl => (
                <div key={tpl.id} className="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-white/5 group" data-testid={`template-${tpl.id}`}>
                  <button onClick={() => applyTemplate(tpl)} className="flex-1 text-left min-w-0">
                    <p className="text-xs text-white/90 font-medium truncate">{tpl.name}</p>
                    <p className="text-[10px] text-slate-600 truncate">{tpl.text}</p>
                  </button>
                  <button onClick={() => deleteTemplate(tpl.id)}
                    className="p-1 opacity-0 group-hover:opacity-100 hover:bg-red-500/10 rounded transition-opacity"
                    data-testid={`delete-template-${tpl.id}`}>
                    <Trash2 className="w-3 h-3 text-red-400" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Toolbar Buttons */}
      <div className="flex items-center gap-1 px-1">
        <button onClick={() => { closeAllDropdowns(); setShowTones(!showTones); }}
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

        <button onClick={() => { closeAllDropdowns(); setShowTranslate(!showTranslate); }}
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

        <div className="w-px h-4 bg-white/10 mx-0.5" />

        {/* Save as Template (shown after AI action + has text) */}
        {messageText.trim() && lastAction && (
          <button onClick={() => { closeAllDropdowns(); setShowSaveTemplate(!showSaveTemplate); }}
            className="flex items-center gap-1 px-2 py-1 rounded-lg text-[10px] font-medium text-[#00CEC9]/70 hover:text-[#00CEC9] hover:bg-[#00CEC9]/5 transition-colors"
            title="Save as template" data-testid="save-as-template-btn">
            <Save className="w-3 h-3" /><span className="hidden sm:inline">Save</span>
          </button>
        )}

        {/* Template Library */}
        <button onClick={() => { closeAllDropdowns(); setShowTemplates(!showTemplates); loadTemplates(); }}
          className="flex items-center gap-1 px-2 py-1 rounded-lg text-[10px] font-medium text-slate-400 hover:text-white hover:bg-white/5 transition-colors"
          title="Templates" data-testid="templates-btn">
          <BookMarked className="w-3 h-3" />
          <span className="hidden sm:inline">Templates</span>
          {templates.length > 0 && <span className="ml-0.5 text-[8px] text-[#00CEC9]">{templates.length}</span>}
        </button>
      </div>
    </div>
  );
};

export default AIWritingToolbar;
