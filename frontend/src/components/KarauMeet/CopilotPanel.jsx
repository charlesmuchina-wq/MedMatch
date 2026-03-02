import { useState, useRef, useEffect } from 'react';
import { BrainCircuit, Send, Loader2, History, ChevronDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';

const API = process.env.REACT_APP_BACKEND_URL;

export default function CopilotPanel({ meetingId }) {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [history, setHistory] = useState([]);
  const scrollRef = useRef(null);

  useEffect(() => {
    fetchHistory();
  }, [meetingId]);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchHistory = async () => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/sentiment-dash/copilot/history/${meetingId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setHistory(data.interactions || []);
      }
    } catch {}
  };

  const sendQuery = async () => {
    if (!query.trim() || loading) return;
    const q = query.trim();
    setQuery('');
    setMessages(prev => [...prev, { role: 'user', text: q }]);
    setLoading(true);

    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/sentiment-dash/copilot/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({
          meeting_id: meetingId,
          question: q,
          include_past_meetings: true,
          context_window: 5
        })
      });
      if (res.ok) {
        const data = await res.json();
        setMessages(prev => [...prev, {
          role: 'copilot',
          text: data.answer,
          sources: data.context_sources,
          pastMeetings: data.past_meetings_referenced
        }]);
      } else {
        setMessages(prev => [...prev, { role: 'error', text: 'Copilot query failed' }]);
      }
    } catch {
      setMessages(prev => [...prev, { role: 'error', text: 'Connection error' }]);
    }
    setLoading(false);
  };

  return (
    <div className="flex-1 flex flex-col overflow-hidden" data-testid="copilot-panel">
      <div className="p-3 border-b border-white/[0.06]">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-fuchsia-500/20 to-purple-500/10 flex items-center justify-center">
            <BrainCircuit className="w-3.5 h-3.5 text-fuchsia-400" />
          </div>
          <div>
            <h3 className="text-xs font-semibold text-white">AI Copilot</h3>
            <p className="text-[9px] text-slate-500">Cross-meeting intelligence</p>
          </div>
        </div>
      </div>

      {/* Past History Toggle */}
      {history.length > 0 && (
        <button
          onClick={() => setShowHistory(!showHistory)}
          className="flex items-center justify-between px-2.5 py-1.5 text-[9px] text-fuchsia-400 hover:bg-white/5 border-b border-white/5"
          data-testid="copilot-history-toggle"
        >
          <span className="flex items-center gap-1"><History className="w-3 h-3" />Previous queries ({history.length})</span>
          <ChevronDown className={`w-3 h-3 transition-transform ${showHistory ? 'rotate-180' : ''}`} />
        </button>
      )}

      {showHistory && (
        <div className="max-h-32 overflow-y-auto border-b border-white/5 bg-karau-bg/30">
          {history.map((h, i) => (
            <div key={i} className="px-2.5 py-1.5 border-b border-white/3 last:border-0">
              <p className="text-[8px] text-fuchsia-300 font-medium truncate">{h.question}</p>
              <p className="text-[7px] text-slate-500 truncate">{h.answer?.substring(0, 80)}...</p>
            </div>
          ))}
        </div>
      )}

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {messages.length === 0 && (
          <div className="text-center py-6">
            <div className="w-12 h-12 rounded-2xl bg-fuchsia-500/10 flex items-center justify-center mx-auto mb-3">
              <BrainCircuit className="w-6 h-6 text-fuchsia-400/40" />
            </div>
            <p className="text-[10px] text-slate-500">Ask about past decisions, action items, or meeting context</p>
            <div className="flex flex-wrap gap-1.5 mt-3 justify-center">
              {['What were the action items from last meeting?',
                'Summarize key decisions this week',
                'Any unresolved topics from previous sessions?'
              ].map(suggestion => (
                <button key={suggestion} onClick={() => { setQuery(suggestion); }}
                  className="text-[8px] px-2 py-1 rounded-lg bg-fuchsia-500/[0.06] text-fuchsia-300 border border-fuchsia-500/15 hover:bg-fuchsia-500/[0.12] transition-all duration-200"
                  data-testid="copilot-suggestion">
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[90%] p-2 rounded-lg text-[9px] leading-relaxed ${
              msg.role === 'user'
                ? 'bg-fuchsia-500/15 text-fuchsia-200 border border-fuchsia-500/20'
                : msg.role === 'error'
                ? 'bg-red-500/10 text-red-300 border border-red-500/20'
                : 'bg-karau-bg/60 text-slate-300 border border-white/5'
            }`} data-testid={`copilot-msg-${i}`}>
              {msg.text}
              {msg.sources > 0 && (
                <div className="mt-1 flex gap-1">
                  <Badge className="text-[6px] bg-fuchsia-500/10 text-fuchsia-300">{msg.sources} sources</Badge>
                  {msg.pastMeetings > 0 && (
                    <Badge className="text-[6px] bg-violet-500/10 text-violet-300">{msg.pastMeetings} past meetings</Badge>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-1.5 text-[9px] text-fuchsia-400">
            <Loader2 className="w-3 h-3 animate-spin" />Thinking across meetings...
          </div>
        )}
        <div ref={scrollRef} />
      </div>

      {/* Input */}
      <div className="p-3 border-t border-white/[0.06]">
        <div className="flex gap-2">
          <Input value={query} onChange={e => setQuery(e.target.value)}
            placeholder="Ask the AI Copilot..."
            onKeyDown={e => e.key === 'Enter' && sendQuery()}
            className="bg-karau-bg/60 border-white/10 text-white text-[10px] h-8 rounded-xl" data-testid="copilot-input" />
          <Button size="sm" onClick={sendQuery} disabled={loading}
            className="h-8 px-3 bg-fuchsia-500/80 hover:bg-fuchsia-400 rounded-xl shadow-lg shadow-fuchsia-500/15" data-testid="copilot-send-btn">
            <Send className="w-3 h-3" />
          </Button>
        </div>
      </div>
    </div>
  );
}
