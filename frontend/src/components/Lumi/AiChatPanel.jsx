import { useState, useEffect, useRef } from 'react';
import { Send, Sparkles, MessageSquare, X, Loader2 } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { API, ESY } from './constants';

export const AiChatPanel = ({ channelId, onClose, token }) => {
  const [question, setQuestion] = useState('');
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  const askAi = async () => {
    if (!question.trim() || loading) return;
    const q = question.trim();
    setQuestion('');
    setConversations(prev => [...prev, { role: 'user', text: q }]);
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/lumi/ai/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ question: q, channel_id: channelId })
      });
      if (res.ok) { const data = await res.json(); setConversations(prev => [...prev, { role: 'ai', text: data.answer }]); }
    } catch (e) { setConversations(prev => [...prev, { role: 'ai', text: 'Sorry, I could not process that.' }]); }
    setLoading(false);
  };

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [conversations]);

  return (
    <div className="w-[380px] border-l border-slate-200 bg-white flex flex-col h-full" data-testid="ai-chat-panel">
      <div className="h-14 flex items-center justify-between px-4 border-b border-slate-200" style={{ background: `linear-gradient(135deg, ${ESY.turquoise}08, ${ESY.pink}08)` }}>
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` }}><Sparkles className="w-3.5 h-3.5 text-white" /></div>
          <div><h3 className="text-sm font-semibold text-slate-900">Ask ENZI AI</h3><p className="text-[9px] text-slate-400">Powered by ESY Intelligence</p></div>
        </div>
        <button onClick={onClose} className="p-1 hover:bg-slate-100 rounded-md" data-testid="close-ai-chat"><X className="w-4 h-4 text-slate-500" /></button>
      </div>
      <ScrollArea className="flex-1">
        <div className="p-4 space-y-3">
          {conversations.length === 0 && (
            <div className="text-center py-8">
              <div className="w-12 h-12 mx-auto rounded-xl flex items-center justify-center mb-3" style={{ background: `linear-gradient(135deg, ${ESY.turquoise}15, ${ESY.pink}15)` }}><MessageSquare className="w-6 h-6" style={{ color: ESY.turquoise }} /></div>
              <p className="text-sm font-medium text-slate-700 mb-1">Ask me anything</p>
              <p className="text-xs text-slate-400 mb-4">I can query your meetings, tasks, and channel data</p>
              <div className="space-y-2">
                {['What tasks are overdue?', 'Summarize recent meetings', 'Who is most active this week?'].map((q, i) => (
                  <button key={i} onClick={() => setQuestion(q)} className="w-full text-left text-xs px-3 py-2 rounded-lg border border-slate-100 text-slate-600 hover:border-slate-200 hover:bg-slate-50 transition-colors" data-testid={`ai-suggestion-${i}`}>{q}</button>
                ))}
              </div>
            </div>
          )}
          {conversations.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] px-3 py-2 rounded-xl text-xs leading-relaxed ${msg.role === 'user' ? 'text-white rounded-br-sm' : 'bg-slate-50 text-slate-700 border border-slate-100 rounded-bl-sm'}`}
                style={msg.role === 'user' ? { background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink}90)` } : {}} data-testid={`ai-msg-${i}`}>
                <span className="whitespace-pre-wrap">{msg.text}</span>
              </div>
            </div>
          ))}
          {loading && (<div className="flex justify-start"><div className="bg-slate-50 border border-slate-100 px-3 py-2 rounded-xl rounded-bl-sm"><Loader2 className="w-4 h-4 animate-spin" style={{ color: ESY.turquoise }} /></div></div>)}
          <div ref={chatEndRef} />
        </div>
      </ScrollArea>
      <div className="p-3 border-t border-slate-200">
        <div className="flex items-center gap-2">
          <input value={question} onChange={e => setQuestion(e.target.value)} onKeyDown={e => e.key === 'Enter' && askAi()}
            placeholder="Ask about projects, tasks, meetings..." className="flex-1 h-9 px-3 text-xs bg-slate-50 border border-slate-200 rounded-lg outline-none focus:border-[#00CEC9] transition-colors" data-testid="ai-chat-input" />
          <button onClick={askAi} disabled={!question.trim() || loading} className="h-9 w-9 flex items-center justify-center rounded-lg text-white transition-all disabled:opacity-40"
            style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` }} data-testid="ai-chat-send"><Send className="w-3.5 h-3.5" /></button>
        </div>
      </div>
    </div>
  );
};
