import { useState, useEffect, useRef } from 'react';
import {
  Smile, MessageSquare, FileText, Download,
  Globe, Loader2, X, Pencil, Trash2, Check, Sparkles
} from 'lucide-react';
import { API, ESY } from './constants';
import RichMessage from './RichMessage';

const languages = [
  { code: 'en', name: 'English' }, { code: 'es', name: 'Spanish' }, { code: 'fr', name: 'French' },
  { code: 'de', name: 'German' }, { code: 'pt', name: 'Portuguese' }, { code: 'it', name: 'Italian' },
  { code: 'ar', name: 'Arabic' }, { code: 'zh', name: 'Chinese' }, { code: 'ja', name: 'Japanese' },
  { code: 'ko', name: 'Korean' }, { code: 'hi', name: 'Hindi' }, { code: 'ru', name: 'Russian' },
  { code: 'sw', name: 'Swahili' }, { code: 'tr', name: 'Turkish' }, { code: 'nl', name: 'Dutch' },
  { code: 'pl', name: 'Polish' }, { code: 'vi', name: 'Vietnamese' }, { code: 'th', name: 'Thai' },
  { code: 'id', name: 'Indonesian' }, { code: 'he', name: 'Hebrew' },
];

const quickEmojis = ['👍', '❤️', '😂', '🎉', '🔥', '👀'];

export const MessageBubble = ({ msg, isOwn, prevSameSender, onReact, onThread, onEdit, onDelete, token }) => {
  const time = new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const [showReact, setShowReact] = useState(false);
  const [translation, setTranslation] = useState(null);
  const [translating, setTranslating] = useState(false);
  const [showLangPicker, setShowLangPicker] = useState(false);
  const [editing, setEditing] = useState(false);
  const [editText, setEditText] = useState(msg.content);
  const [showMenu, setShowMenu] = useState(false);
  const editRef = useRef(null);

  const translateMsg = async (langName) => {
    if (translating) return;
    setShowLangPicker(false);
    if (translation && translation.target_language === langName) { setTranslation(null); return; }
    setTranslating(true);
    try {
      const res = await fetch(`${API}/api/lumi/ai/translate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ text: msg.content, target_language: langName })
      });
      if (res.ok) { const d = await res.json(); setTranslation(d); }
    } catch (e) {}
    setTranslating(false);
  };

  const handleEditSave = () => {
    if (editText.trim() && editText.trim() !== msg.content) {
      onEdit?.(msg.id, editText.trim());
    }
    setEditing(false);
  };

  const handleEditCancel = () => { setEditText(msg.content); setEditing(false); };

  useEffect(() => { if (editing && editRef.current) editRef.current.focus(); }, [editing]);

  if (msg.type === 'system') {
    return (
      <div className="flex justify-center my-4" data-testid={`msg-system-${msg.id}`}>
        <span className="text-xs text-slate-600 bg-slate-100 px-3 py-1 rounded-full">{msg.content}</span>
      </div>
    );
  }

  const initials = (msg.sender_name || '?').split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase();
  const colors = ['bg-[#36454F]', 'bg-[#008080]', 'bg-slate-600', 'bg-[#6B7280]', 'bg-[#4B5563]'];
  const ci = (msg.sender_id || '').split('').reduce((a, c) => a + c.charCodeAt(0), 0) % colors.length;
  const reactions = msg.reactions || {};
  const profilePic = msg.sender_profile_picture;

  return (
    <div className={`group relative flex gap-3 px-5 py-1 hover:bg-slate-50/50 ${!prevSameSender ? 'mt-4' : 'mt-0.5'}`} data-testid={`msg-${msg.id}`}>
      <div className="w-9 flex-shrink-0">
        {!prevSameSender && (
          msg.type === 'ai_assistant' ? (
            <div className="w-9 h-9 rounded-full flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #00CEC9, #E84393)' }} data-testid="ai-assistant-avatar">
              <Sparkles className="w-4 h-4 text-white" aria-hidden="true" />
            </div>
          ) : profilePic ? (
            <img src={profilePic} alt="" className="w-9 h-9 rounded-full object-cover" />
          ) : (
            <div className={`w-9 h-9 rounded-full ${colors[ci]} flex items-center justify-center`}>
              <span className="text-[11px] font-semibold text-white">{initials}</span>
            </div>
          )
        )}
      </div>
      <div className="flex-1 min-w-0">
        {!prevSameSender && (
          <div className="flex items-baseline gap-2 mb-0.5">
            <span className="text-sm font-bold text-slate-900">{msg.sender_name}</span>
            {msg.type === 'ai_assistant' && (
              <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-teal-50 text-teal-700 border border-teal-200" data-testid="ai-assistant-badge">AI</span>
            )}
            <span className="text-[11px] text-slate-500">{time}</span>
            {msg.edited && <span className="text-[10px] text-slate-400 italic">(edited)</span>}
          </div>
        )}

        {editing ? (
          <div className="flex items-center gap-2 mt-1" data-testid={`edit-input-${msg.id}`}>
            <input ref={editRef} value={editText} onChange={e => setEditText(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') handleEditSave(); if (e.key === 'Escape') handleEditCancel(); }}
              className="flex-1 text-sm px-3 py-1.5 border border-slate-300 rounded-md outline-none focus:border-[#008080] bg-white text-slate-900" />
            <button onClick={handleEditSave} className="p-1.5 rounded-md bg-[#008080] text-white hover:bg-[#006666]" data-testid={`edit-save-${msg.id}`}><Check className="w-3.5 h-3.5" /></button>
            <button onClick={handleEditCancel} className="p-1.5 rounded-md bg-slate-200 text-slate-600 hover:bg-slate-300" data-testid={`edit-cancel-${msg.id}`}><X className="w-3.5 h-3.5" /></button>
          </div>
        ) : (
          <div className="text-sm text-slate-900 leading-relaxed break-words">
            <RichMessage content={msg.content} />
            {msg.edited && prevSameSender && <span className="text-[10px] text-slate-400 italic ml-1">(edited)</span>}
          </div>
        )}

        {msg.file && (
          <div className="mt-2" data-testid={`file-${msg.id}`}>
            {msg.file.is_image ? (
              <div className="max-w-xs rounded-lg overflow-hidden border border-slate-200">
                <img src={`${API}/api/lumi/files/${msg.file.id}?auth=${token}`}
                  alt={msg.file.original_filename} className="max-w-full max-h-48 object-cover" loading="lazy" />
              </div>
            ) : (
              <a href={`${API}/api/lumi/files/${msg.file.id}?auth=${token}`} target="_blank" rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-50 border border-slate-200 hover:bg-slate-100 transition-colors max-w-xs">
                <FileText className="w-4 h-4 text-[#008080]" />
                <span className="text-xs text-slate-700 truncate">{msg.file.original_filename}</span>
                <Download className="w-3.5 h-3.5 text-slate-400" />
              </a>
            )}
          </div>
        )}

        {Object.keys(reactions).length > 0 && (
          <div className="flex flex-wrap gap-1 mt-1.5">
            {Object.entries(reactions).map(([emoji, users]) => (
              <button key={emoji} onClick={() => onReact?.(msg.id, emoji)}
                className="flex items-center gap-1 px-2 py-0.5 rounded-full text-xs border border-slate-200 bg-white hover:bg-slate-50 transition-colors text-slate-700"
                data-testid={`reaction-${emoji}-${msg.id}`}>
                <span>{emoji}</span><span className="text-[10px]">{users.length}</span>
              </button>
            ))}
          </div>
        )}

        {msg.thread_count > 0 && (
          <button onClick={() => onThread?.(msg.id)} className="flex items-center gap-1.5 mt-1.5 text-xs hover:underline" style={{ color: ESY.turquoise }} data-testid={`thread-${msg.id}`}>
            <MessageSquare className="w-3.5 h-3.5" />
            {msg.thread_count} {msg.thread_count === 1 ? 'reply' : 'replies'}
          </button>
        )}

        {translation && (
          <div className="mt-1.5 p-2 rounded-md border text-xs leading-relaxed" style={{ borderColor: `${ESY.turquoise}20`, background: `${ESY.turquoise}05` }} data-testid={`translation-${msg.id}`}>
            <div className="flex items-center gap-1 mb-1">
              <Globe className="w-3 h-3" style={{ color: ESY.turquoise }} />
              <span className="text-[9px] font-medium" style={{ color: ESY.turquoise }}>{translation.target_language}</span>
            </div>
            <p className="text-slate-800">{translation.translated}</p>
          </div>
        )}

        <div className="opacity-0 group-hover:opacity-100 absolute -top-3 right-5 flex items-center gap-0.5 bg-white border border-slate-200 rounded-md shadow-sm p-0.5 z-10">
            <button onClick={() => setShowReact(!showReact)} className="p-1 hover:bg-slate-100 rounded" data-testid={`react-btn-${msg.id}`}>
              <Smile className="w-3.5 h-3.5 text-slate-500" />
            </button>
            <button onClick={() => onThread?.(msg.id)} className="p-1 hover:bg-slate-100 rounded" data-testid={`thread-btn-${msg.id}`}>
              <MessageSquare className="w-3.5 h-3.5 text-slate-500" />
            </button>
            <button onClick={() => setShowLangPicker(!showLangPicker)} className="p-1 hover:bg-slate-100 rounded" data-testid={`translate-btn-${msg.id}`}>
              {translating ? <Loader2 className="w-3.5 h-3.5 animate-spin" style={{ color: ESY.turquoise }} /> : <Globe className="w-3.5 h-3.5" style={{ color: translation ? ESY.turquoise : '#64748b' }} />}
            </button>
            {isOwn && (
              <>
                <button onClick={() => { setEditing(true); setShowMenu(false); }} className="p-1 hover:bg-slate-100 rounded" data-testid={`edit-btn-${msg.id}`}>
                  <Pencil className="w-3.5 h-3.5 text-slate-500" />
                </button>
                <button onClick={() => onDelete?.(msg.id)} className="p-1 hover:bg-red-50 rounded" data-testid={`delete-btn-${msg.id}`}>
                  <Trash2 className="w-3.5 h-3.5 text-red-400" />
                </button>
              </>
            )}
          </div>
        {showReact && (
          <div className="absolute -top-10 right-5 flex items-center gap-0.5 px-1.5 py-1 bg-white border border-slate-200 rounded-lg shadow-lg z-20" data-testid={`react-picker-${msg.id}`}>
            {quickEmojis.map(e => (
              <button key={e} onClick={() => { onReact?.(msg.id, e); setShowReact(false); }} className="p-1 hover:bg-slate-100 rounded text-sm">{e}</button>
            ))}
          </div>
        )}

        {showLangPicker && (
          <div className="mt-1 inline-block w-48 max-h-56 overflow-auto bg-white border border-slate-200 rounded-lg shadow-xl z-20 py-1" data-testid={`lang-picker-${msg.id}`}>
            <div className="flex items-center justify-between px-3 py-1.5 border-b border-slate-100 sticky top-0 bg-white">
              <span className="text-[9px] font-semibold text-slate-400 uppercase tracking-wider">Translate to</span>
              <button onClick={() => setShowLangPicker(false)} className="p-0.5 hover:bg-slate-100 rounded"><X className="w-3 h-3 text-slate-400" /></button>
            </div>
            {languages.map(lang => (
              <button key={lang.code} onClick={() => translateMsg(lang.name)}
                className={`w-full text-left px-3 py-1.5 text-xs hover:bg-slate-50 transition-colors flex items-center gap-2 ${translation?.target_language === lang.name ? 'font-semibold' : 'text-slate-700'}`}
                style={translation?.target_language === lang.name ? { color: ESY.turquoise } : {}}
                data-testid={`lang-${lang.code}`}>
                <span className="w-5 text-center text-[10px] text-slate-400">{lang.code.toUpperCase()}</span>
                {lang.name}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
