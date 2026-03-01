import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import {
  Bot, Send, Loader2, Lightbulb, ListChecks, FileText,
  Clock, Sparkles, ChevronRight, Brain, Search, UserCheck,
  Activity, Mic, MicOff, Zap, AlertTriangle
} from 'lucide-react';
import { useTranslation } from '@/utils/i18n';

const API = process.env.REACT_APP_BACKEND_URL;

const AIAssistantPanel = ({ meetingId, aiNotes = [], webinarId, engagementData }) => {
  const { t } = useTranslation();

  const SMART_SUGGESTIONS = [
    { label: t("karauMeet.summarizeDiscussion"), icon: FileText, question: 'Summarize the key points discussed so far' },
    { label: t("karauMeet.listActionItems"), icon: ListChecks, question: 'What action items have been identified?' },
    { label: t("karauMeet.keyDecisions"), icon: Lightbulb, question: 'What decisions have been made in this meeting?' },
    { label: t("karauMeet.whatDidIMiss"), icon: Clock, question: 'Give me a brief catch-up of what was discussed' },
  ];

  const AGENT_ACTIONS = [
    { label: 'Research Topic', icon: Search, type: 'research' },
    { label: 'Auto-Assign Actions', icon: UserCheck, type: 'actions' },
    { label: 'Engagement Check', icon: Activity, type: 'sentiment' },
  ];
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [insightsCount, setInsightsCount] = useState(0);
  const [activeTab, setActiveTab] = useState('chat'); // chat, agent, sentiment
  const [actionItems, setActionItems] = useState([]);
  const [voiceListening, setVoiceListening] = useState(false);
  const scrollRef = useRef(null);
  const inputRef = useRef(null);
  const recognitionRef = useRef(null);

  // Auto-count insights from aiNotes
  useEffect(() => {
    const actionItems = aiNotes.filter(n => n.type === 'action_item').length;
    const highlights = aiNotes.filter(n => n.type === 'highlight').length;
    setInsightsCount(actionItems + highlights);
  }, [aiNotes]);

  // Auto-scroll on new messages
  useEffect(() => {
    if (scrollRef.current) {
      const el = scrollRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (el) el.scrollTop = el.scrollHeight;
    }
  }, [messages]);

  const askAssistant = async (question) => {
    if (!question.trim() || isLoading) return;

    const userMsg = { role: 'user', content: question, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API}/api/karau-features/ai-assistant/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ meeting_id: meetingId, question })
      });

      if (res.ok) {
        const data = await res.json();
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.answer,
          timestamp: new Date().toISOString(),
          suggestions: data.follow_up_suggestions || []
        }]);
      } else {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: 'I couldn\'t process that request. Please try again.',
          timestamp: new Date().toISOString(),
          isError: true
        }]);
      }
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Connection error. Please check your network.',
        timestamp: new Date().toISOString(),
        isError: true
      }]);
    }
    setIsLoading(false);
    inputRef.current?.focus();
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      askAssistant(input);
    }
  };

  // --- Agentic AI: Research ---
  const researchTopic = async (topic) => {
    if (!topic.trim()) return;
    setIsLoading(true);
    setMessages(prev => [...prev, { role: 'user', content: `Research: ${topic}`, timestamp: new Date().toISOString() }]);
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau-features/ai-agent/research`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ meeting_id: meetingId, topic, context: '' })
      });
      if (res.ok) {
        const data = await res.json();
        setMessages(prev => [...prev, {
          role: 'assistant', content: data.research, timestamp: new Date().toISOString(),
          isResearch: true, suggestions: data.follow_up_suggestions || []
        }]);
      }
    } catch { setMessages(prev => [...prev, { role: 'assistant', content: 'Research failed.', timestamp: new Date().toISOString(), isError: true }]); }
    setIsLoading(false);
  };

  // --- Agentic AI: Voice Commands ---
  const toggleVoiceCommand = () => {
    if (voiceListening) {
      recognitionRef.current?.stop();
      setVoiceListening(false);
      return;
    }
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.onresult = async (event) => {
      const text = event.results[0][0].transcript;
      setVoiceListening(false);
      await executeVoiceCommand(text);
    };
    recognition.onerror = () => setVoiceListening(false);
    recognition.onend = () => setVoiceListening(false);
    recognitionRef.current = recognition;
    recognition.start();
    setVoiceListening(true);
  };

  const executeVoiceCommand = async (text) => {
    setMessages(prev => [...prev, { role: 'user', content: `Voice: "${text}"`, timestamp: new Date().toISOString(), isVoice: true }]);
    setIsLoading(true);
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau-features/voice-command/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ meeting_id: meetingId, command_text: text, webinar_id: webinarId })
      });
      if (res.ok) {
        const data = await res.json();
        const cmd = data.command;
        let responseText = data.executed
          ? `Executed: ${cmd.action}${cmd.params ? ' - ' + JSON.stringify(cmd.params) : ''}`
          : `Could not understand: "${text}". Try: "mute all", "start recording", "summarize last 5 minutes"`;
        setMessages(prev => [...prev, { role: 'assistant', content: responseText, timestamp: new Date().toISOString(), isCommand: true }]);
      }
    } catch { setMessages(prev => [...prev, { role: 'assistant', content: 'Voice command failed.', timestamp: new Date().toISOString(), isError: true }]); }
    setIsLoading(false);
  };

  // --- Agentic AI: Assign Action Items ---
  const assignAction = async (actionItem, assignee) => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau-features/ai-agent/assign-action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ meeting_id: meetingId, action_item: actionItem, assignee })
      });
      if (res.ok) {
        const data = await res.json();
        setActionItems(prev => [...prev, data.action]);
      }
    } catch {}
  };

  // --- Fetch action items ---
  const fetchActionItems = async () => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau-features/ai-agent/actions/${meetingId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) { const data = await res.json(); setActionItems(data.action_items || []); }
    } catch {}
  };

  const generateSummary = async () => {
    if (isLoading) return;
    setIsLoading(true);
    setMessages(prev => [...prev, { role: 'user', content: 'Generate a full meeting summary', timestamp: new Date().toISOString() }]);

    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API}/api/karau-features/ai-assistant/generate-summary/${meetingId}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.summary,
          timestamp: new Date().toISOString(),
          isSummary: true
        }]);
      }
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Could not generate summary at this time.',
        timestamp: new Date().toISOString(),
        isError: true
      }]);
    }
    setIsLoading(false);
  };

  return (
    <div className="flex flex-col h-full" data-testid="ai-assistant-panel">
      {/* Tab Bar */}
      <div className="flex border-b border-karau-border">
        {[
          { id: 'chat', label: 'AI Chat', icon: Bot },
          { id: 'agent', label: 'Agent', icon: Zap },
          { id: 'sentiment', label: 'Pulse', icon: Activity },
        ].map(tab => (
          <button key={tab.id} onClick={() => setActiveTab(tab.id)}
            data-testid={`ai-tab-${tab.id}`}
            className={`flex-1 flex items-center justify-center gap-1 py-2 text-[10px] font-medium transition-colors ${activeTab === tab.id
              ? 'text-teal-400 border-b-2 border-teal-400 bg-teal-500/5'
              : 'text-slate-500 hover:text-slate-300'}`}>
            <tab.icon className="w-3 h-3" />{tab.label}
          </button>
        ))}
      </div>

      {/* Insights Bar */}
      {insightsCount > 0 && (
        <div className="px-3 py-2 border-b border-karau-border bg-gradient-to-r from-emerald-500/5 to-teal-500/5">
          <div className="flex items-center gap-2">
            <Brain className="w-3.5 h-3.5 text-emerald-400" />
            <span className="text-xs text-emerald-300 font-medium">
              {insightsCount} insight{insightsCount !== 1 ? 's' : ''} detected
            </span>
            <Badge className="ml-auto bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-[10px] px-1.5 py-0">
              Live
            </Badge>
          </div>
        </div>
      )}

      {/* Messages Area */}
      {activeTab === 'chat' && (
      <>
      <ScrollArea ref={scrollRef} className="flex-1">
        <div className="p-3 space-y-4">
          {messages.length === 0 ? (
            <div className="py-6 space-y-5">
              {/* Welcome */}
              <div className="text-center">
                <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-teal-500/20 to-emerald-500/10 border border-teal-500/20 flex items-center justify-center mx-auto mb-3">
                  <Bot className="w-6 h-6 text-teal-400" />
                </div>
                <p className="text-sm font-medium text-white">{t("karauMeet.karauAI")}</p>
                <p className="text-xs text-slate-500 mt-1 max-w-[200px] mx-auto">
                  {t("karauMeet.askAboutMeetings")}
                </p>
              </div>

              {/* Smart Suggestions */}
              <div className="space-y-1.5">
                <span className="text-[10px] uppercase tracking-wider text-slate-600 font-medium px-1">{t("karauMeet.quickActions")}</span>
                {SMART_SUGGESTIONS.map((s, i) => (
                  <button
                    key={i}
                    onClick={() => askAssistant(s.question)}
                    className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-left text-sm text-slate-400 hover:text-white bg-karau-bg/40 hover:bg-karau-surface border border-transparent hover:border-white/5 transition-all duration-200 group"
                    data-testid={`suggestion-${i}`}
                  >
                    <s.icon className="w-3.5 h-3.5 text-teal-500/60 group-hover:text-teal-400 flex-shrink-0" />
                    <span className="flex-1 text-xs">{s.label}</span>
                    <ChevronRight className="w-3 h-3 text-slate-700 group-hover:text-slate-400 group-hover:translate-x-0.5 transition-transform" />
                  </button>
                ))}
              </div>

              {/* Generate Summary Button */}
              <button
                onClick={generateSummary}
                className="w-full flex items-center justify-center gap-2 px-3 py-3 rounded-xl text-sm font-medium text-teal-300 bg-gradient-to-r from-teal-500/10 to-emerald-500/5 border border-teal-500/20 hover:border-teal-500/40 hover:from-teal-500/15 hover:to-emerald-500/10 transition-all duration-200"
                data-testid="generate-full-summary"
              >
                <Sparkles className="w-4 h-4" />
                {t("karauMeet.generateFullSummary")}
              </button>
            </div>
          ) : (
            <>
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  data-testid={`assistant-msg-${idx}`}
                >
                  <div className={`max-w-[85%] ${msg.role === 'user'
                    ? 'bg-teal-500/20 border border-teal-500/10 rounded-2xl rounded-br-md px-3.5 py-2.5'
                    : msg.isError
                      ? 'bg-red-500/10 border border-red-500/10 rounded-2xl rounded-bl-md px-3.5 py-2.5'
                      : msg.isSummary
                        ? 'bg-gradient-to-br from-karau-surface to-karau-bg border border-teal-500/10 rounded-2xl px-3.5 py-2.5'
                        : 'bg-karau-surface border border-white/5 rounded-2xl rounded-bl-md px-3.5 py-2.5'
                  }`}>
                    {msg.role === 'assistant' && (
                      <div className="flex items-center gap-1.5 mb-1.5">
                        <Bot className="w-3 h-3 text-teal-400" />
                        <span className="text-[10px] text-teal-400 font-medium">KARAU AI</span>
                        {msg.isSummary && <Badge className="text-[9px] bg-teal-500/10 text-teal-300 border-teal-500/20 px-1 py-0">Summary</Badge>}
                      </div>
                    )}
                    <p className={`text-xs leading-relaxed whitespace-pre-wrap ${
                      msg.role === 'user' ? 'text-teal-100' : msg.isError ? 'text-red-300' : 'text-slate-300'
                    }`}>
                      {msg.content}
                    </p>
                    <span className="text-[9px] text-slate-600 mt-1.5 block">
                      {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>

                    {/* Follow-up suggestions */}
                    {msg.suggestions && msg.suggestions.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-white/5 space-y-1">
                        {msg.suggestions.map((s, si) => (
                          <button
                            key={si}
                            onClick={() => askAssistant(s)}
                            className="text-[10px] text-teal-400/70 hover:text-teal-300 flex items-center gap-1 transition-colors"
                          >
                            <ChevronRight className="w-2.5 h-2.5" />{s}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-karau-surface border border-white/5 rounded-2xl rounded-bl-md px-3.5 py-3">
                    <div className="flex items-center gap-2">
                      <div className="flex gap-1">
                        <span className="w-1.5 h-1.5 bg-teal-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                        <span className="w-1.5 h-1.5 bg-teal-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                        <span className="w-1.5 h-1.5 bg-teal-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                      </div>
                      <span className="text-[10px] text-slate-500">{t("karauMeet.thinking")}</span>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </ScrollArea>

      {/* Input Area */}
      <div className="p-3 border-t border-karau-border">
        {messages.length > 0 && (
          <div className="flex gap-1.5 mb-2 overflow-x-auto pb-1 scrollbar-hide">
            {SMART_SUGGESTIONS.slice(0, 3).map((s, i) => (
              <button
                key={i}
                onClick={() => askAssistant(s.question)}
                className="flex-shrink-0 text-[10px] px-2.5 py-1 rounded-full border border-white/5 text-slate-500 hover:text-teal-300 hover:border-teal-500/20 bg-karau-bg/40 transition-all"
              >
                {s.label}
              </button>
            ))}
          </div>
        )}
        <div className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={t("karauMeet.askKarauPlaceholder")}
            className="flex-1 bg-karau-bg/60 border border-karau-border text-white rounded-xl px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-teal-500/40 focus:border-teal-500/30 placeholder-slate-600"
            disabled={isLoading}
            data-testid="ai-assistant-input"
          />
          <Button
            onClick={() => askAssistant(input)}
            size="sm"
            disabled={!input.trim() || isLoading}
            className="bg-teal-500 hover:bg-teal-400 text-white rounded-xl px-3 h-9 disabled:opacity-30"
            data-testid="ai-assistant-send"
          >
            {isLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
          </Button>
          <Button
            onClick={toggleVoiceCommand}
            size="sm"
            className={`rounded-xl px-2 h-9 ${voiceListening ? 'bg-red-500 hover:bg-red-400 animate-pulse' : 'bg-karau-surface hover:bg-karau-bg border border-white/10'}`}
            data-testid="voice-command-btn"
          >
            {voiceListening ? <MicOff className="w-3.5 h-3.5 text-white" /> : <Mic className="w-3.5 h-3.5 text-slate-400" />}
          </Button>
        </div>
      </div>
      </>
      )}

      {/* Agent Tab */}
      {activeTab === 'agent' && (
        <div className="flex-1 overflow-y-auto p-3 space-y-3">
          <div className="space-y-1.5">
            <p className="text-[9px] uppercase tracking-wider text-teal-400 font-semibold flex items-center gap-1"><Zap className="w-2.5 h-2.5" />AI Agent Actions</p>
            {AGENT_ACTIONS.map((a, i) => (
              <button key={i} onClick={() => {
                if (a.type === 'research') { const topic = prompt('Research topic:'); if (topic) researchTopic(topic); }
                else if (a.type === 'actions') { fetchActionItems(); }
                else if (a.type === 'sentiment') { setActiveTab('sentiment'); }
              }}
                className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-left text-sm text-slate-400 hover:text-white bg-karau-bg/40 hover:bg-karau-surface border border-transparent hover:border-white/5 transition-all group"
                data-testid={`agent-action-${a.type}`}>
                <a.icon className="w-3.5 h-3.5 text-teal-500/60 group-hover:text-teal-400" />
                <span className="flex-1 text-xs">{a.label}</span>
                <ChevronRight className="w-3 h-3 text-slate-700 group-hover:text-slate-400" />
              </button>
            ))}
          </div>

          {/* Action Items List */}
          {actionItems.length > 0 && (
            <div className="space-y-1.5">
              <p className="text-[9px] uppercase tracking-wider text-amber-400 font-semibold flex items-center gap-1">
                <ListChecks className="w-2.5 h-2.5" />Action Items ({actionItems.length})
              </p>
              {actionItems.map((a, i) => (
                <div key={a.action_id || i} className="p-2 bg-amber-500/5 rounded-lg border border-amber-500/10" data-testid={`action-item-${i}`}>
                  <p className="text-[10px] text-white">{a.action_item}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge className="text-[7px] bg-amber-500/10 text-amber-400 border-amber-500/20">
                      <UserCheck className="w-2 h-2 mr-0.5" />{a.assignee}
                    </Badge>
                    <Badge className="text-[7px] bg-white/5 text-slate-500 border-white/10">{a.status}</Badge>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Quick Research Input */}
          <div className="pt-2 border-t border-karau-border">
            <p className="text-[9px] text-slate-500 mb-1.5">Quick Research</p>
            <div className="flex gap-1.5">
              <input type="text" placeholder="Enter topic to research..."
                className="flex-1 bg-karau-bg/60 border border-karau-border text-white rounded-xl px-3 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-teal-500/40"
                onKeyDown={e => { if (e.key === 'Enter') { researchTopic(e.target.value); e.target.value = ''; } }}
                data-testid="quick-research-input" />
              <Button size="sm" className="bg-teal-500 hover:bg-teal-400 text-white rounded-xl h-7 px-2" data-testid="quick-research-btn">
                <Search className="w-3 h-3" />
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Sentiment/Pulse Tab */}
      {activeTab === 'sentiment' && (
        <div className="flex-1 overflow-y-auto p-3 space-y-3">
          <p className="text-[9px] uppercase tracking-wider text-teal-400 font-semibold flex items-center gap-1">
            <Activity className="w-2.5 h-2.5" />Meeting Pulse
          </p>

          {engagementData ? (
            <>
              {/* Engagement Score */}
              <div className="p-3 bg-karau-bg/40 rounded-xl border border-white/5 text-center" data-testid="engagement-score">
                <p className="text-3xl font-bold" style={{ color: engagementData.engagement_score > 7 ? '#34d399' : engagementData.engagement_score > 4 ? '#fbbf24' : '#f87171' }}>
                  {engagementData.engagement_score}/10
                </p>
                <p className="text-[9px] text-slate-500 mt-0.5">Engagement Score</p>
                <Badge className={`mt-1 text-[8px] ${engagementData.dominant_energy === 'high' ? 'bg-emerald-500/10 text-emerald-400' : engagementData.dominant_energy === 'low' ? 'bg-red-500/10 text-red-400' : 'bg-amber-500/10 text-amber-400'}`}>
                  {engagementData.dominant_energy} energy
                </Badge>
              </div>

              {/* Alerts */}
              {engagementData.alerts?.map((a, i) => (
                <div key={i} className={`p-2 rounded-lg border flex items-center gap-2 ${a.type === 'warning' ? 'bg-red-500/5 border-red-500/10' : 'bg-emerald-500/5 border-emerald-500/10'}`}
                  data-testid={`sentiment-alert-${i}`}>
                  <AlertTriangle className={`w-3 h-3 ${a.type === 'warning' ? 'text-red-400' : 'text-emerald-400'}`} />
                  <span className="text-[9px] text-slate-300">{a.message}</span>
                </div>
              ))}

              {/* Sentiment Breakdown */}
              {engagementData.sentiment_breakdown && (
                <div className="space-y-1">
                  <p className="text-[8px] text-slate-500 uppercase tracking-wider">Sentiment Breakdown</p>
                  {Object.entries(engagementData.sentiment_breakdown).map(([k, v]) => (
                    <div key={k} className="flex items-center gap-2">
                      <span className="text-[9px] text-slate-400 w-16 capitalize">{k}</span>
                      <div className="flex-1 h-1.5 bg-white/5 rounded-full overflow-hidden">
                        <div className="h-full rounded-full bg-teal-400/60" style={{ width: `${(v / Math.max(...Object.values(engagementData.sentiment_breakdown), 1)) * 100}%` }} />
                      </div>
                      <span className="text-[8px] text-slate-500 w-4">{v}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Stats */}
              <div className="grid grid-cols-2 gap-1.5">
                <div className="p-2 bg-karau-bg/40 rounded-lg text-center">
                  <p className="text-sm font-bold text-teal-400">{engagementData.action_items_count || 0}</p>
                  <p className="text-[8px] text-slate-500">Actions</p>
                </div>
                <div className="p-2 bg-karau-bg/40 rounded-lg text-center">
                  <p className="text-sm font-bold text-violet-400">{engagementData.research_count || 0}</p>
                  <p className="text-[8px] text-slate-500">Research</p>
                </div>
              </div>
            </>
          ) : (
            <div className="text-center py-6 text-slate-500">
              <Activity className="w-8 h-8 mx-auto mb-2 opacity-30" />
              <p className="text-xs">Sentiment analysis will appear here as the meeting progresses</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AIAssistantPanel;
