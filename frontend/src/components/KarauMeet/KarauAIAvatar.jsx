import { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { Bot, Send, Loader2, X, Sparkles, ChevronRight, Minimize2 } from 'lucide-react';
import { Button } from '@/components/ui/button';

const API = process.env.REACT_APP_BACKEND_URL;

const QUICK_ACTIONS = [
  { label: 'Summarize last meeting', question: 'Summarize the key points from my last meeting' },
  { label: 'List my action items', question: 'What are my pending action items from recent meetings?' },
  { label: 'Meeting best practices', question: 'What are best practices for running effective meetings?' },
];

const KarauAIAvatar = ({ meetingId }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 300);
    }
  }, [isOpen]);

  const askAssistant = async (question) => {
    if (!question.trim() || isLoading) return;
    const userMsg = { role: 'user', content: question, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const token = localStorage.getItem('token');
      const effectiveMeetingId = meetingId || 'general';
      const res = await fetch(`${API}/api/karau-features/ai-assistant/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ meeting_id: effectiveMeetingId, question })
      });

      if (res.ok) {
        const data = await res.json();
        setMessages(prev => [...prev, {
          role: 'assistant', content: data.answer,
          timestamp: new Date().toISOString(),
          suggestions: data.follow_up_suggestions || []
        }]);
      } else {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: 'I couldn\'t process that request. Try again.',
          timestamp: new Date().toISOString(), isError: true
        }]);
      }
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant', content: 'Connection error.',
        timestamp: new Date().toISOString(), isError: true
      }]);
    }
    setIsLoading(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      askAssistant(input);
    }
  };

  return (
    <>
      {/* Floating Avatar Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-5 right-5 z-50 w-14 h-14 rounded-full bg-gradient-to-br from-blue-600 via-purple-600 to-violet-600 shadow-xl shadow-purple-500/30 hover:shadow-purple-500/50 flex items-center justify-center transition-all duration-300 hover:scale-110 group"
          data-testid="karau-avatar-btn"
          style={{ animation: 'avatarPulse 3s ease-in-out infinite' }}
        >
          <Bot className="w-6 h-6 text-white group-hover:scale-110 transition-transform" />
          <span className="absolute -top-1 -right-1 w-3.5 h-3.5 bg-emerald-400 rounded-full border-2 border-karau-bg" />
        </button>
      )}

      {/* Chat Panel */}
      {isOpen && (
        <div
          className="fixed bottom-5 right-5 z-50 w-[340px] sm:w-[380px] h-[480px] rounded-2xl bg-karau-card/95 backdrop-blur-xl border border-white/10 shadow-2xl shadow-black/40 flex flex-col overflow-hidden"
          style={{ animation: 'avatarSlideUp 0.3s ease-out' }}
          data-testid="karau-avatar-panel"
        >
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-white/5 bg-gradient-to-r from-blue-600/10 via-purple-600/10 to-violet-600/5 flex-shrink-0">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 via-purple-600 to-violet-600 flex items-center justify-center">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div>
                <p className="text-sm font-semibold text-white">KARAU AI</p>
                <p className="text-[10px] text-emerald-400 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full" />Online
                </p>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <button onClick={() => setIsOpen(false)} className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-white/5 transition-colors" data-testid="karau-avatar-close">
                <Minimize2 className="w-4 h-4" />
              </button>
              <button onClick={() => { setIsOpen(false); setMessages([]); }} className="p-1.5 text-slate-400 hover:text-red-400 rounded-lg hover:bg-red-500/10 transition-colors">
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Messages */}
          <div ref={scrollRef} className="flex-1 overflow-y-auto p-3 space-y-3">
            {messages.length === 0 ? (
              <div className="py-4 space-y-4">
                <div className="text-center">
                  <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500/20 via-purple-500/15 to-emerald-500/10 border border-purple-500/20 flex items-center justify-center mx-auto mb-2">
                    <Sparkles className="w-5 h-5 text-purple-400" />
                  </div>
                  <p className="text-xs font-medium text-white">How can I help?</p>
                  <p className="text-[10px] text-slate-500 mt-0.5">Ask about meetings, get summaries, or explore features</p>
                </div>
                <div className="space-y-1.5">
                  {QUICK_ACTIONS.map((a, i) => (
                    <button key={i} onClick={() => askAssistant(a.question)}
                      className="w-full flex items-center gap-2 px-3 py-2 rounded-xl text-left text-xs text-slate-400 hover:text-white bg-karau-bg/40 hover:bg-karau-surface border border-transparent hover:border-white/5 transition-all group"
                      data-testid={`avatar-action-${i}`}>
                      <ChevronRight className="w-3 h-3 text-purple-500/60 group-hover:text-purple-400 flex-shrink-0" />
                      <span>{a.label}</span>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <>
                {messages.map((msg, idx) => (
                  <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`} data-testid={`avatar-msg-${idx}`}>
                    <div className={`max-w-[85%] ${msg.role === 'user'
                      ? 'bg-gradient-to-br from-blue-600/20 to-purple-600/10 border border-blue-500/10 rounded-2xl rounded-br-md px-3 py-2'
                      : msg.isError
                        ? 'bg-red-500/10 border border-red-500/10 rounded-2xl rounded-bl-md px-3 py-2'
                        : 'bg-karau-surface border border-white/5 rounded-2xl rounded-bl-md px-3 py-2'
                    }`}>
                      {msg.role === 'assistant' && (
                        <div className="flex items-center gap-1 mb-1">
                          <Bot className="w-2.5 h-2.5 text-purple-400" />
                          <span className="text-[9px] text-purple-400 font-medium">KARAU</span>
                        </div>
                      )}
                      <p className={`text-xs leading-relaxed whitespace-pre-wrap ${msg.role === 'user' ? 'text-blue-100' : msg.isError ? 'text-red-300' : 'text-slate-300'}`}>
                        {msg.content}
                      </p>
                      {msg.suggestions && msg.suggestions.length > 0 && (
                        <div className="mt-1.5 pt-1.5 border-t border-white/5 space-y-0.5">
                          {msg.suggestions.map((s, si) => (
                            <button key={si} onClick={() => askAssistant(s)}
                              className="text-[10px] text-purple-400/70 hover:text-purple-300 flex items-center gap-1">
                              <ChevronRight className="w-2 h-2" />{s}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-karau-surface border border-white/5 rounded-2xl rounded-bl-md px-3 py-2.5">
                      <div className="flex gap-1">
                        <span className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                        <span className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                        <span className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>

          {/* Input */}
          <div className="p-3 border-t border-white/5 flex-shrink-0">
            <div className="flex gap-2">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask KARAU AI..."
                className="flex-1 bg-karau-bg/60 border border-karau-border text-white rounded-xl px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-purple-500/40 focus:border-purple-500/30 placeholder-slate-600"
                disabled={isLoading}
                data-testid="karau-avatar-input"
              />
              <Button onClick={() => askAssistant(input)} size="sm" disabled={!input.trim() || isLoading}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white rounded-xl px-3 h-9 disabled:opacity-30"
                data-testid="karau-avatar-send">
                {isLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
              </Button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes avatarPulse {
          0%, 100% { box-shadow: 0 10px 40px -10px rgba(124, 58, 237, 0.3); }
          50% { box-shadow: 0 10px 60px -10px rgba(124, 58, 237, 0.5); }
        }
        @keyframes avatarSlideUp {
          from { opacity: 0; transform: translateY(20px) scale(0.95); }
          to { opacity: 1; transform: translateY(0) scale(1); }
        }
      `}</style>
    </>
  );
};

export default KarauAIAvatar;
