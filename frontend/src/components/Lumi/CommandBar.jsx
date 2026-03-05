import { useState, useEffect, useRef } from 'react';
import {
  Search, Hash, User, MessageSquare, ListTodo, CheckCircle2,
  Plus, FileBarChart, Activity, AlertTriangle, Sparkles,
  ArrowRight, Loader2, X
} from 'lucide-react';
import { API, ESY } from './constants';

export const CommandBar = ({ isOpen, onClose, onNavigate, token, onAction }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedIdx, setSelectedIdx] = useState(0);
  const [mode, setMode] = useState('search');
  const inputRef = useRef(null);

  useEffect(() => { if (isOpen) { setQuery(''); setResults([]); setSelectedIdx(0); setMode('search'); setTimeout(() => inputRef.current?.focus(), 100); } }, [isOpen]);

  useEffect(() => {
    if (!query.trim()) { setResults([]); return; }
    const isAi = query.startsWith('?');
    setMode(isAi ? 'ai' : 'search');
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const res = await fetch(`${API}/api/lumi/command/search`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }, body: JSON.stringify({ query: isAi ? query.slice(1).trim() : query, mode: isAi ? 'ai' : 'search' }) });
        if (res.ok) { const d = await res.json(); setResults(d.results || []); setSelectedIdx(0); }
      } catch (e) {}
      setLoading(false);
    }, 300);
    return () => clearTimeout(timer);
  }, [query, token]);

  const handleSelect = (item) => {
    if (item.type === 'channel' || item.type === 'dm') { onNavigate(item); onClose(); }
    else if (item.type === 'message') { onNavigate({ type: 'channel', id: item.channel_id }); onClose(); }
    else if (item.type === 'action') { onAction(item.command); onClose(); }
    else { onClose(); }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'ArrowDown') { e.preventDefault(); setSelectedIdx(prev => Math.min(prev + 1, results.length - 1)); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); setSelectedIdx(prev => Math.max(prev - 1, 0)); }
    else if (e.key === 'Enter' && results[selectedIdx]) { handleSelect(results[selectedIdx]); }
    else if (e.key === 'Escape') { onClose(); }
  };

  const iconMap = { hash: Hash, user: User, message: MessageSquare, 'list-todo': ListTodo, 'check-circle': CheckCircle2, plus: Plus, 'file-bar-chart': FileBarChart, activity: Activity, 'alert-triangle': AlertTriangle, sparkles: Sparkles };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-start justify-center pt-[15vh]" onClick={onClose} data-testid="command-bar-overlay">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />
      <div className="relative w-full max-w-[560px] bg-white rounded-xl shadow-2xl border border-slate-200 overflow-hidden" onClick={e => e.stopPropagation()} data-testid="command-bar">
        <div className="flex items-center gap-3 px-4 h-14 border-b border-slate-100">
          {mode === 'ai' ? <Sparkles className="w-4.5 h-4.5 flex-shrink-0" style={{ color: ESY.turquoise }} /> : <Search className="w-4.5 h-4.5 text-slate-400 flex-shrink-0" />}
          <input ref={inputRef} value={query} onChange={e => setQuery(e.target.value)} onKeyDown={handleKeyDown}
            placeholder='Search channels, tasks, people... (prefix ? for AI)'
            className="flex-1 text-sm bg-transparent outline-none text-slate-900 placeholder:text-slate-400" data-testid="command-input" />
          <kbd className="hidden sm:inline-flex items-center px-1.5 py-0.5 text-[10px] font-mono text-slate-400 bg-slate-50 rounded border border-slate-200">ESC</kbd>
          {loading && <Loader2 className="w-4 h-4 animate-spin" style={{ color: ESY.turquoise }} />}
        </div>
        <div className="max-h-[360px] overflow-auto">
          {results.length === 0 && query && !loading && (<div className="px-4 py-6 text-center text-xs text-slate-400">{mode === 'ai' ? 'Type your question after ?' : 'No results found'}</div>)}
          {mode === 'ai' && results.length > 0 && results[0].type === 'ai_answer' ? (
            <div className="p-4"><div className="flex items-center gap-2 mb-2"><Sparkles className="w-3.5 h-3.5" style={{ color: ESY.turquoise }} /><span className="text-xs font-semibold" style={{ color: ESY.turquoise }}>AI Answer</span></div><p className="text-xs text-slate-700 leading-relaxed whitespace-pre-wrap" data-testid="command-ai-answer">{results[0].content}</p></div>
          ) : (results.map((item, idx) => {
            const Icon = iconMap[item.icon] || Hash;
            const typeLabels = { channel: 'Channel', dm: 'Direct Message', message: 'Message', task: 'Task', action_item: 'Action Item', action: 'Quick Action' };
            return (
              <button key={`${item.type}-${item.id}-${idx}`} onClick={() => handleSelect(item)} className={`w-full flex items-center gap-3 px-4 py-2.5 text-left transition-colors ${idx === selectedIdx ? 'bg-slate-50' : 'hover:bg-slate-50'}`} data-testid={`command-result-${idx}`}>
                <div className={`w-7 h-7 rounded-md flex items-center justify-center flex-shrink-0 ${item.type === 'action' ? 'bg-gradient-to-br' : 'bg-slate-100'}`} style={item.type === 'action' ? { background: `linear-gradient(135deg, ${ESY.turquoise}15, ${ESY.pink}15)` } : {}}>
                  <Icon className="w-3.5 h-3.5" style={item.type === 'action' ? { color: ESY.turquoise } : { color: '#64748b' }} />
                </div>
                <div className="flex-1 min-w-0"><p className="text-xs font-medium text-slate-800 truncate">{item.name || item.content || ''}</p>{item.sender && <p className="text-[10px] text-slate-400">by {item.sender}</p>}{item.assignee && <p className="text-[10px] text-slate-400">assigned to {item.assignee}</p>}</div>
                <span className="text-[9px] text-slate-400 uppercase tracking-wider flex-shrink-0">{typeLabels[item.type] || item.type}</span>
                {item.type === 'action' && <ArrowRight className="w-3 h-3 text-slate-500 flex-shrink-0" />}
              </button>
            );
          }))}
        </div>
        <div className="px-4 py-2 border-t border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-3 text-[10px] text-slate-400">
            <span><kbd className="px-1 py-0.5 bg-slate-50 rounded border border-slate-200 font-mono text-[9px]">↑↓</kbd> navigate</span>
            <span><kbd className="px-1 py-0.5 bg-slate-50 rounded border border-slate-200 font-mono text-[9px]">↵</kbd> select</span>
            <span><kbd className="px-1 py-0.5 bg-slate-50 rounded border border-slate-200 font-mono text-[9px]">?</kbd> ask AI</span>
          </div>
          <span className="text-[9px] font-medium" style={{ color: ESY.pink }}>LUMI Command</span>
        </div>
      </div>
    </div>
  );
};
