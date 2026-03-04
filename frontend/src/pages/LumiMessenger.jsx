/**
 * LUMI Prestige — Enterprise Team Messenger
 * Design: Charcoal (#36454F), Cool Grey, ESY accents (Pink, Turquoise, Deep Red)
 * ESY Color Theme: Honoring ESY — Pink (#E84393), Turquoise (#00CEC9), Deep Red (#D63031)
 * 60-30-10 Rule: Slate base / Charcoal brand / ESY accents
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast, Toaster } from 'sonner';
import {
  Hash, Lock, Megaphone, Plus, Send, LogOut, ArrowLeft,
  Users, Search, ChevronDown, Circle, MessageCircle,
  Loader2, X, Smile, Paperclip, Eye, EyeOff, UserPlus, User,
  FileText, Image, Download, CheckCheck, Phone, PhoneOff,
  Settings, MessageSquare, Shield, Building2, MoreHorizontal,
  Sparkles, BarChart3, ListTodo, FileBarChart, Brain,
  CheckCircle2, AlertTriangle, Activity, Command, Network,
  Zap, ArrowRight, Globe, TrendingDown
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useTranslation } from '@/utils/i18n';

const API = process.env.REACT_APP_BACKEND_URL;
const WS_URL = API.replace('https://', 'wss://').replace('http://', 'ws://');

// ESY Color Palette — Honoring ESY
const ESY = {
  pink: '#E84393',
  pinkLight: '#FD79A8',
  turquoise: '#00CEC9',
  turquoiseLight: '#55EFC4',
  deepRed: '#D63031',
  deepRedLight: '#FF7675',
};
// ============== Presence Colors ==============
const STATUS_COLORS = {
  available: 'bg-emerald-500',
  busy: 'bg-amber-500',
  in_meeting: 'bg-red-500',
  ooo: 'bg-red-500',
  vacation: 'bg-red-500',
  offline: 'bg-slate-400',
};
const STATUS_LABELS = {
  available: 'Available',
  busy: 'Busy',
  in_meeting: 'In a meeting',
  ooo: 'Out of office',
  vacation: 'On vacation',
  offline: 'Offline',
};

// ============== Channel Icon ==============
const ChannelIcon = ({ type }) => {
  if (type === 'announcement') return <Megaphone className="w-4 h-4" />;
  if (type === 'domain') return <Shield className="w-4 h-4" />;
  if (type === 'project') return <Hash className="w-4 h-4" />;
  return <Hash className="w-4 h-4" />;
};

// ============== Status Dot ==============
const StatusDot = ({ status, size = 'sm', ringColor = 'ring-white' }) => {
  const s = size === 'sm' ? 'w-2.5 h-2.5' : 'w-3 h-3';
  return <span className={`inline-block ${s} rounded-full ${STATUS_COLORS[status] || STATUS_COLORS.offline} ring-2 ${ringColor}`} />;
};

// ============== Message Bubble ==============
const MessageBubble = ({ msg, isOwn, prevSameSender, onReact, onThread, token }) => {
  const time = new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const [showReact, setShowReact] = useState(false);
  const quickEmojis = ['👍', '❤️', '😂', '🎉', '🔥', '👀'];

  if (msg.type === 'system') {
    return (
      <div className="flex justify-center my-4" data-testid={`msg-system-${msg.id}`}>
        <span className="text-xs text-slate-500 bg-slate-100 px-3 py-1 rounded-full">{msg.content}</span>
      </div>
    );
  }

  const initials = (msg.sender_name || '?').split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase();
  const colors = ['bg-[#36454F]', 'bg-[#008080]', 'bg-slate-600', 'bg-[#6B7280]', 'bg-[#4B5563]'];
  const ci = (msg.sender_id || '').split('').reduce((a, c) => a + c.charCodeAt(0), 0) % colors.length;
  const reactions = msg.reactions || {};

  return (
    <div className={`group flex gap-3 px-5 py-1 hover:bg-slate-50/50 ${!prevSameSender ? 'mt-4' : 'mt-0.5'}`} data-testid={`msg-${msg.id}`}>
      <div className="w-9 flex-shrink-0">
        {!prevSameSender && (
          <div className={`w-9 h-9 rounded-full ${colors[ci]} flex items-center justify-center`}>
            <span className="text-[11px] font-semibold text-white">{initials}</span>
          </div>
        )}
      </div>
      <div className="flex-1 min-w-0">
        {!prevSameSender && (
          <div className="flex items-baseline gap-2 mb-0.5">
            <span className="text-sm font-semibold text-slate-900">{msg.sender_name}</span>
            <span className="text-[11px] text-slate-400">{time}</span>
          </div>
        )}
        <p className="text-sm text-slate-700 leading-relaxed break-words">{msg.content}</p>

        {/* File */}
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

        {/* Reactions */}
        {Object.keys(reactions).length > 0 && (
          <div className="flex flex-wrap gap-1 mt-1.5">
            {Object.entries(reactions).map(([emoji, users]) => (
              <button key={emoji} onClick={() => onReact?.(msg.id, emoji)}
                className="flex items-center gap-1 px-2 py-0.5 rounded-full text-xs border border-slate-200 bg-white hover:bg-slate-50 transition-colors text-slate-600"
                data-testid={`reaction-${emoji}-${msg.id}`}>
                <span>{emoji}</span><span className="text-[10px]">{users.length}</span>
              </button>
            ))}
          </div>
        )}

        {/* Thread indicator */}
        {msg.thread_count > 0 && (
          <button onClick={() => onThread?.(msg.id)} className="flex items-center gap-1.5 mt-1.5 text-[#008080] text-xs hover:underline" data-testid={`thread-${msg.id}`}>
            <MessageSquare className="w-3.5 h-3.5" />
            {msg.thread_count} {msg.thread_count === 1 ? 'reply' : 'replies'}
          </button>
        )}

        {/* Hover actions */}
        <div className="relative inline-flex">
          <div className="opacity-0 group-hover:opacity-100 absolute -top-7 right-0 flex items-center gap-0.5 bg-white border border-slate-200 rounded-md shadow-sm p-0.5 z-10">
            <button onClick={() => setShowReact(!showReact)} className="p-1 hover:bg-slate-100 rounded" data-testid={`react-btn-${msg.id}`}>
              <Smile className="w-3.5 h-3.5 text-slate-500" />
            </button>
            <button onClick={() => onThread?.(msg.id)} className="p-1 hover:bg-slate-100 rounded" data-testid={`thread-btn-${msg.id}`}>
              <MessageSquare className="w-3.5 h-3.5 text-slate-500" />
            </button>
          </div>
          {showReact && (
            <div className="absolute -top-12 right-0 flex items-center gap-0.5 px-1.5 py-1 bg-white border border-slate-200 rounded-lg shadow-lg z-20" data-testid={`react-picker-${msg.id}`}>
              {quickEmojis.map(e => (
                <button key={e} onClick={() => { onReact?.(msg.id, e); setShowReact(false); }} className="p-1 hover:bg-slate-100 rounded text-sm">{e}</button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// ============== Thread Panel ==============
const ThreadPanel = ({ messageId, onClose, token }) => {
  const { t } = useTranslation();
  const [thread, setThread] = useState(null);
  const [replyText, setReplyText] = useState('');
  const [sending, setSending] = useState(false);

  useEffect(() => {
    if (!messageId) return;
    fetch(`${API}/api/lumi/messages/${messageId}/thread`, { headers: { 'Authorization': `Bearer ${token}` } })
      .then(r => r.json()).then(setThread);
  }, [messageId, token]);

  const sendReply = async () => {
    if (!replyText.trim()) return;
    setSending(true);
    try {
      await fetch(`${API}/api/lumi/messages/${messageId}/thread`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ content: replyText.trim() })
      });
      setReplyText('');
      // Refresh
      const res = await fetch(`${API}/api/lumi/messages/${messageId}/thread`, { headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) setThread(await res.json());
    } catch (e) { toast.error('Failed to send reply'); }
    setSending(false);
  };

  if (!thread) return null;

  return (
    <div className="w-[350px] border-l border-slate-200 bg-white flex flex-col h-full" data-testid="thread-panel">
      <div className="h-14 flex items-center justify-between px-4 border-b border-slate-200">
        <h3 className="text-sm font-semibold text-slate-900">{t('lumi.thread') || 'Thread'}</h3>
        <button onClick={onClose} className="p-1 hover:bg-slate-100 rounded-md"><X className="w-4 h-4 text-slate-500" /></button>
      </div>
      <ScrollArea className="flex-1 py-3">
        {/* Parent */}
        <div className="px-4 pb-3 border-b border-slate-100">
          <p className="text-xs font-semibold text-slate-500 mb-1">{thread.parent?.sender_name}</p>
          <p className="text-sm text-slate-800">{thread.parent?.content}</p>
        </div>
        {/* Replies */}
        <div className="px-4 pt-3 space-y-3">
          {(thread.replies || []).map(r => (
            <div key={r.id} className="flex gap-2" data-testid={`thread-reply-${r.id}`}>
              <div className="w-7 h-7 rounded-full bg-[#36454F] flex items-center justify-center flex-shrink-0">
                <span className="text-[9px] font-semibold text-white">{(r.sender_name || '?')[0]}</span>
              </div>
              <div>
                <div className="flex items-baseline gap-1.5">
                  <span className="text-xs font-semibold text-slate-900">{r.sender_name}</span>
                  <span className="text-[10px] text-slate-400">{new Date(r.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                </div>
                <p className="text-xs text-slate-700">{r.content}</p>
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>
      <div className="p-3 border-t border-slate-200">
        <div className="flex items-center gap-2 border border-slate-200 rounded-lg px-3 py-2 focus-within:ring-2 focus-within:ring-[#008080]/20 focus-within:border-[#008080]">
          <input value={replyText} onChange={e => setReplyText(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') sendReply(); }}
            placeholder={t('lumi.replyPlaceholder') || 'Reply...'}
            className="flex-1 text-sm bg-transparent outline-none text-slate-800 placeholder:text-slate-400" data-testid="thread-reply-input" />
          <button onClick={sendReply} disabled={!replyText.trim() || sending}
            className={`p-1.5 rounded-md transition-colors ${replyText.trim() ? 'bg-[#008080] text-white' : 'text-slate-400'}`} data-testid="thread-send-btn">
            <Send className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};

// ============== Members Panel ==============
const MembersPanel = ({ channelId, onClose, token }) => {
  const { t } = useTranslation();
  const [members, setMembers] = useState([]);

  useEffect(() => {
    fetch(`${API}/api/lumi/channels/${channelId}/members`, { headers: { 'Authorization': `Bearer ${token}` } })
      .then(r => r.json()).then(d => setMembers(d.members || []));
  }, [channelId, token]);

  return (
    <div className="w-[280px] border-l border-slate-200 bg-white flex flex-col h-full" data-testid="members-panel">
      <div className="h-14 flex items-center justify-between px-4 border-b border-slate-200">
        <h3 className="text-sm font-semibold text-slate-900">{t('lumi.members') || 'Members'} ({members.length})</h3>
        <button onClick={onClose} className="p-1 hover:bg-slate-100 rounded-md"><X className="w-4 h-4 text-slate-500" /></button>
      </div>
      <ScrollArea className="flex-1 py-2">
        {members.map(m => (
          <div key={m.user_id} className="flex items-center gap-3 px-4 py-2 hover:bg-slate-50" data-testid={`member-${m.user_id}`}>
            <div className="relative">
              <div className="w-8 h-8 rounded-full bg-[#36454F] flex items-center justify-center">
                <span className="text-[10px] font-semibold text-white">{(m.name || '?')[0].toUpperCase()}</span>
              </div>
              <span className={`absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full ring-2 ring-white ${STATUS_COLORS[m.status] || STATUS_COLORS.offline}`} />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm text-slate-900 truncate">{m.name || 'User'}</p>
              <p className="text-[10px] text-slate-400">{m.role === 'admin' ? 'Admin' : STATUS_LABELS[m.status] || 'Offline'}</p>
            </div>
          </div>
        ))}
      </ScrollArea>
    </div>
  );
};

// ============== AI Productivity Panel ==============
const AiProductivityPanel = ({ channelId, channelName, onClose, token }) => {
  const [activeTab, setActiveTab] = useState('sentiment');
  const [sentiment, setSentiment] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyzeSentiment = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/lumi/ai/sentiment/${channelId}`, {
        method: 'POST', headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) setSentiment(await res.json());
    } catch (e) { toast.error('Analysis failed'); }
    setLoading(false);
  };

  const extractTasks = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/lumi/ai/extract-tasks/${channelId}`, {
        method: 'POST', headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) { const d = await res.json(); setTasks(d.tasks || []); }
    } catch (e) { toast.error('Extraction failed'); }
    setLoading(false);
  };

  const generateReport = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/lumi/ai/report/${channelId}`, {
        method: 'POST', headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) setReport(await res.json());
    } catch (e) { toast.error('Report failed'); }
    setLoading(false);
  };

  const toggleTask = async (taskId, current) => {
    const newStatus = current === 'done' ? 'open' : 'done';
    try {
      await fetch(`${API}/api/lumi/ai/tasks/${taskId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ status: newStatus })
      });
      setTasks(prev => prev.map(t => t.id === taskId ? { ...t, status: newStatus } : t));
    } catch (e) {}
  };

  const scoreColor = (score) => {
    if (score >= 70) return 'text-emerald-500';
    if (score >= 40) return 'text-amber-500';
    return 'text-red-500';
  };

  const priorityBadge = {
    high: 'bg-red-50 text-red-600 border-red-200',
    medium: 'bg-amber-50 text-amber-600 border-amber-200',
    low: 'bg-slate-50 text-slate-500 border-slate-200',
  };

  const tabs = [
    { key: 'sentiment', label: 'Sentiment', icon: Activity },
    { key: 'tasks', label: 'Tasks', icon: ListTodo },
    { key: 'report', label: 'Report', icon: FileBarChart },
  ];

  return (
    <div className="w-[350px] border-l border-slate-200 bg-white flex flex-col h-full" data-testid="ai-panel">
      <div className="h-14 flex items-center justify-between px-4 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <Brain className="w-4 h-4 text-[#008080]" />
          <h3 className="text-sm font-semibold text-slate-900">AI Insights</h3>
        </div>
        <button onClick={onClose} className="p-1 hover:bg-slate-100 rounded-md"><X className="w-4 h-4 text-slate-500" /></button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200">
        {tabs.map(tab => (
          <button key={tab.key} onClick={() => setActiveTab(tab.key)}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 text-xs font-medium transition-colors ${
              activeTab === tab.key ? 'text-[#008080] border-b-2 border-[#008080]' : 'text-slate-400 hover:text-slate-600'
            }`} data-testid={`ai-tab-${tab.key}`}>
            <tab.icon className="w-3.5 h-3.5" />{tab.label}
          </button>
        ))}
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4">
          {/* Sentiment Tab */}
          {activeTab === 'sentiment' && (
            <div className="space-y-4">
              {!sentiment ? (
                <button onClick={analyzeSentiment} disabled={loading}
                  className="w-full flex items-center justify-center gap-2 py-3 rounded-lg bg-[#008080]/5 border border-[#008080]/20 text-[#008080] text-sm font-medium hover:bg-[#008080]/10 transition-colors"
                  data-testid="analyze-sentiment-btn">
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Activity className="w-4 h-4" />}
                  {loading ? 'Analyzing...' : 'Analyze Channel Mood'}
                </button>
              ) : (
                <>
                  <div className="flex items-center justify-between p-4 rounded-lg bg-slate-50 border border-slate-100">
                    <div>
                      <p className="text-xs text-slate-500 mb-1">Team Morale Score</p>
                      <p className={`text-3xl font-bold ${scoreColor(sentiment.score)}`}>{sentiment.score}</p>
                    </div>
                    <div className="text-right">
                      <span className={`text-sm font-semibold ${scoreColor(sentiment.score)}`}>{sentiment.label}</span>
                      <p className="text-[10px] text-slate-400 mt-0.5">{sentiment.engagement_level} engagement</p>
                    </div>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed">{sentiment.summary}</p>
                  {sentiment.highlights?.length > 0 && (
                    <div className="space-y-1">
                      <span className="text-[10px] font-semibold text-emerald-600 uppercase tracking-wider">Highlights</span>
                      {sentiment.highlights.map((h, i) => (
                        <div key={i} className="flex items-start gap-2 text-xs text-slate-600">
                          <CheckCircle2 className="w-3 h-3 text-emerald-500 mt-0.5 flex-shrink-0" /><span>{h}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  {sentiment.alerts?.length > 0 && (
                    <div className="space-y-1">
                      <span className="text-[10px] font-semibold text-amber-600 uppercase tracking-wider">Attention Needed</span>
                      {sentiment.alerts.map((a, i) => (
                        <div key={i} className="flex items-start gap-2 text-xs text-amber-700">
                          <AlertTriangle className="w-3 h-3 text-amber-500 mt-0.5 flex-shrink-0" /><span>{a}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  <button onClick={() => { setSentiment(null); analyzeSentiment(); }}
                    className="w-full text-xs text-slate-400 hover:text-[#008080] py-1 transition-colors">Refresh Analysis</button>
                </>
              )}
            </div>
          )}

          {/* Tasks Tab */}
          {activeTab === 'tasks' && (
            <div className="space-y-3">
              <button onClick={extractTasks} disabled={loading}
                className="w-full flex items-center justify-center gap-2 py-2.5 rounded-lg bg-[#008080]/5 border border-[#008080]/20 text-[#008080] text-sm font-medium hover:bg-[#008080]/10 transition-colors"
                data-testid="extract-tasks-btn">
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                {loading ? 'Extracting...' : 'Extract Tasks from Chat'}
              </button>
              {tasks.length > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-700">{tasks.length} tasks found</span>
                    <span className="text-[10px] text-slate-400">{tasks.filter(t => t.status === 'done').length} done</span>
                  </div>
                  {tasks.map(task => (
                    <div key={task.id} className={`p-3 rounded-lg border transition-all ${task.status === 'done' ? 'bg-slate-50 border-slate-100 opacity-70' : 'bg-white border-slate-200'}`}
                      data-testid={`task-${task.id}`}>
                      <div className="flex items-start gap-2">
                        <button onClick={() => toggleTask(task.id, task.status)}
                          className={`w-4 h-4 mt-0.5 rounded border flex-shrink-0 flex items-center justify-center ${task.status === 'done' ? 'bg-[#008080]/20 border-[#008080]/40 text-[#008080]' : 'border-slate-300 hover:border-[#008080]'}`}
                          data-testid={`toggle-task-${task.id}`}>
                          {task.status === 'done' && <CheckCircle2 className="w-3 h-3" />}
                        </button>
                        <div className="flex-1 min-w-0">
                          <p className={`text-xs leading-relaxed ${task.status === 'done' ? 'text-slate-400 line-through' : 'text-slate-800'}`}>{task.task}</p>
                          <div className="flex flex-wrap items-center gap-1.5 mt-1.5">
                            {task.assignee && task.assignee !== 'Unassigned' && (
                              <span className="text-[9px] bg-[#008080]/10 text-[#008080] px-1.5 py-0.5 rounded font-medium">{task.assignee}</span>
                            )}
                            {task.deadline && task.deadline !== 'TBD' && (
                              <span className="text-[9px] text-slate-400 bg-slate-50 px-1.5 py-0.5 rounded">{task.deadline}</span>
                            )}
                            {task.priority && (
                              <span className={`text-[9px] px-1.5 py-0.5 rounded border ${priorityBadge[task.priority] || priorityBadge.low}`}>{task.priority}</span>
                            )}
                          </div>
                          {task.context && <p className="text-[10px] text-slate-400 mt-1 italic">"{task.context}"</p>}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Report Tab */}
          {activeTab === 'report' && (
            <div className="space-y-3">
              {!report ? (
                <button onClick={generateReport} disabled={loading}
                  className="w-full flex items-center justify-center gap-2 py-3 rounded-lg bg-[#008080]/5 border border-[#008080]/20 text-[#008080] text-sm font-medium hover:bg-[#008080]/10 transition-colors"
                  data-testid="generate-report-btn">
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileBarChart className="w-4 h-4" />}
                  {loading ? 'Generating...' : 'Generate Weekly Report'}
                </button>
              ) : (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-700">#{report.channel_name} Report</span>
                    <span className="text-[10px] text-slate-400">{report.stats?.messages || 0} msgs / {report.stats?.participants || 0} people</span>
                  </div>
                  <div className="prose prose-sm max-w-none">
                    <div className="text-xs text-slate-700 leading-relaxed whitespace-pre-wrap bg-slate-50 p-4 rounded-lg border border-slate-100 max-h-[400px] overflow-auto" data-testid="report-content">
                      {report.report}
                    </div>
                  </div>
                  <button onClick={() => { setReport(null); }}
                    className="w-full text-xs text-slate-400 hover:text-[#008080] py-1 transition-colors">Generate New Report</button>
                </div>
              )}
            </div>
          )}
        </div>
      </ScrollArea>
    </div>
  );
};

// ============== Conversational AI Chat ==============
const AiChatPanel = ({ channelId, onClose, token }) => {
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
      if (res.ok) {
        const data = await res.json();
        setConversations(prev => [...prev, { role: 'ai', text: data.answer }]);
      }
    } catch (e) { setConversations(prev => [...prev, { role: 'ai', text: 'Sorry, I could not process that.' }]); }
    setLoading(false);
  };

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [conversations]);

  return (
    <div className="w-[380px] border-l border-slate-200 bg-white flex flex-col h-full" data-testid="ai-chat-panel">
      <div className="h-14 flex items-center justify-between px-4 border-b border-slate-200" style={{ background: `linear-gradient(135deg, ${ESY.turquoise}08, ${ESY.pink}08)` }}>
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` }}>
            <Sparkles className="w-3.5 h-3.5 text-white" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-900">Ask LUMI AI</h3>
            <p className="text-[9px] text-slate-400">Powered by ESY Intelligence</p>
          </div>
        </div>
        <button onClick={onClose} className="p-1 hover:bg-slate-100 rounded-md" data-testid="close-ai-chat"><X className="w-4 h-4 text-slate-500" /></button>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 space-y-3">
          {conversations.length === 0 && (
            <div className="text-center py-8">
              <div className="w-12 h-12 mx-auto rounded-xl flex items-center justify-center mb-3" style={{ background: `linear-gradient(135deg, ${ESY.turquoise}15, ${ESY.pink}15)` }}>
                <MessageSquare className="w-6 h-6" style={{ color: ESY.turquoise }} />
              </div>
              <p className="text-sm font-medium text-slate-700 mb-1">Ask me anything</p>
              <p className="text-xs text-slate-400 mb-4">I can query your meetings, tasks, and channel data</p>
              <div className="space-y-2">
                {['What tasks are overdue?', 'Summarize recent meetings', 'Who is most active this week?'].map((q, i) => (
                  <button key={i} onClick={() => { setQuestion(q); }}
                    className="w-full text-left text-xs px-3 py-2 rounded-lg border border-slate-100 text-slate-600 hover:border-slate-200 hover:bg-slate-50 transition-colors"
                    data-testid={`ai-suggestion-${i}`}>{q}</button>
                ))}
              </div>
            </div>
          )}
          {conversations.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] px-3 py-2 rounded-xl text-xs leading-relaxed ${
                msg.role === 'user'
                  ? 'text-white rounded-br-sm'
                  : 'bg-slate-50 text-slate-700 border border-slate-100 rounded-bl-sm'
              }`} style={msg.role === 'user' ? { background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink}90)` } : {}}
                data-testid={`ai-msg-${i}`}>
                <span className="whitespace-pre-wrap">{msg.text}</span>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-slate-50 border border-slate-100 px-3 py-2 rounded-xl rounded-bl-sm">
                <Loader2 className="w-4 h-4 animate-spin" style={{ color: ESY.turquoise }} />
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>
      </ScrollArea>

      <div className="p-3 border-t border-slate-200">
        <div className="flex items-center gap-2">
          <input value={question} onChange={e => setQuestion(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && askAi()}
            placeholder="Ask about projects, tasks, meetings..."
            className="flex-1 h-9 px-3 text-xs bg-slate-50 border border-slate-200 rounded-lg outline-none focus:border-[#00CEC9] transition-colors"
            data-testid="ai-chat-input" />
          <button onClick={askAi} disabled={!question.trim() || loading}
            className="h-9 w-9 flex items-center justify-center rounded-lg text-white transition-all disabled:opacity-40"
            style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` }}
            data-testid="ai-chat-send"><Send className="w-3.5 h-3.5" /></button>
        </div>
      </div>
    </div>
  );
};

// ============== Decision Cards & Anomaly Alerts ==============
const AlertsPanel = ({ onClose, token }) => {
  const [alerts, setAlerts] = useState([]);
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('alerts');

  const loadAlerts = async () => {
    try {
      const res = await fetch(`${API}/api/lumi/ai/anomalies`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) { const d = await res.json(); setAlerts(d.alerts || []); }
    } catch (e) {}
  };

  const loadDecisionCards = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/lumi/ai/decision-card`, {
        method: 'POST', headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) { const d = await res.json(); setCards(d.cards || []); }
    } catch (e) {}
    setLoading(false);
  };

  const executeCardAction = async (cardId, actionType, payload) => {
    try {
      const res = await fetch(`${API}/api/lumi/ai/decision-card/${cardId}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ action_type: actionType, payload })
      });
      if (res.ok) {
        const d = await res.json();
        toast.success(d.message || 'Action executed');
        setCards(prev => prev.map(c => c.id === cardId ? { ...c, status: 'resolved' } : c));
      }
    } catch (e) { toast.error('Action failed'); }
  };

  useEffect(() => { loadAlerts(); }, []);

  const severityStyles = {
    critical: { bg: `${ESY.deepRed}10`, border: `${ESY.deepRed}25`, text: ESY.deepRed, icon: AlertTriangle },
    warning: { bg: '#FFF3E0', border: '#FFB74D40', text: '#E65100', icon: AlertTriangle },
    info: { bg: `${ESY.turquoise}10`, border: `${ESY.turquoise}25`, text: ESY.turquoise, icon: Activity },
  };

  const cardSeverityStyles = {
    critical: { gradient: `linear-gradient(135deg, ${ESY.deepRed}10, ${ESY.deepRedLight}05)`, border: `${ESY.deepRed}30` },
    warning: { gradient: `linear-gradient(135deg, ${ESY.pink}08, #FFF3E005)`, border: `${ESY.pink}30` },
    info: { gradient: `linear-gradient(135deg, ${ESY.turquoise}08, ${ESY.turquoiseLight}05)`, border: `${ESY.turquoise}30` },
  };

  return (
    <div className="w-[350px] border-l border-slate-200 bg-white flex flex-col h-full" data-testid="alerts-panel">
      <div className="h-14 flex items-center justify-between px-4 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-4 h-4" style={{ color: ESY.deepRed }} />
          <h3 className="text-sm font-semibold text-slate-900">Alerts & Decisions</h3>
          {alerts.length > 0 && (
            <span className="min-w-[18px] h-[18px] flex items-center justify-center rounded-full text-[9px] font-bold text-white" style={{ backgroundColor: ESY.deepRed }}>{alerts.length}</span>
          )}
        </div>
        <button onClick={onClose} className="p-1 hover:bg-slate-100 rounded-md"><X className="w-4 h-4 text-slate-500" /></button>
      </div>

      <div className="flex border-b border-slate-200">
        <button onClick={() => setActiveTab('alerts')}
          className={`flex-1 py-2.5 text-xs font-medium transition-colors ${activeTab === 'alerts' ? 'border-b-2 text-slate-900' : 'text-slate-400'}`}
          style={activeTab === 'alerts' ? { borderColor: ESY.deepRed, color: ESY.deepRed } : {}}
          data-testid="tab-alerts">Anomaly Alerts</button>
        <button onClick={() => { setActiveTab('cards'); if (cards.length === 0) loadDecisionCards(); }}
          className={`flex-1 py-2.5 text-xs font-medium transition-colors ${activeTab === 'cards' ? 'border-b-2 text-slate-900' : 'text-slate-400'}`}
          style={activeTab === 'cards' ? { borderColor: ESY.pink, color: ESY.pink } : {}}
          data-testid="tab-decisions">Decision Cards</button>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 space-y-3">
          {activeTab === 'alerts' && (
            <>
              {alerts.length === 0 ? (
                <div className="text-center py-8">
                  <CheckCircle2 className="w-10 h-10 mx-auto mb-2" style={{ color: ESY.turquoise }} />
                  <p className="text-sm font-medium text-slate-700">All Clear</p>
                  <p className="text-xs text-slate-400 mt-1">No anomalies detected at this time</p>
                </div>
              ) : (
                alerts.map((alert) => {
                  const s = severityStyles[alert.severity] || severityStyles.info;
                  const Icon = s.icon;
                  return (
                    <div key={alert.id} className="p-3 rounded-lg border" style={{ backgroundColor: s.bg, borderColor: s.border }}
                      data-testid={`alert-${alert.id}`}>
                      <div className="flex items-start gap-2">
                        <Icon className="w-4 h-4 mt-0.5 flex-shrink-0" style={{ color: s.text }} />
                        <div className="flex-1 min-w-0">
                          <p className="text-xs font-semibold" style={{ color: s.text }}>{alert.title}</p>
                          <p className="text-[11px] text-slate-600 mt-1 leading-relaxed">{alert.description}</p>
                          {alert.suggested_action && (
                            <p className="text-[10px] mt-2 font-medium" style={{ color: ESY.turquoise }}>Suggested: {alert.suggested_action}</p>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
              <button onClick={loadAlerts} className="w-full text-xs py-1.5 rounded-md hover:bg-slate-50 transition-colors" style={{ color: ESY.turquoise }}>
                Refresh Alerts
              </button>
            </>
          )}

          {activeTab === 'cards' && (
            <>
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-5 h-5 animate-spin" style={{ color: ESY.pink }} />
                </div>
              ) : cards.length === 0 ? (
                <div className="text-center py-8">
                  <button onClick={loadDecisionCards}
                    className="w-full py-3 rounded-lg border text-sm font-medium transition-colors hover:opacity-90"
                    style={{ borderColor: `${ESY.pink}30`, color: ESY.pink, backgroundColor: `${ESY.pink}05` }}
                    data-testid="generate-cards-btn">
                    <Sparkles className="w-4 h-4 inline mr-2" />Generate Decision Cards
                  </button>
                </div>
              ) : (
                cards.map((card) => {
                  const cs = cardSeverityStyles[card.severity] || cardSeverityStyles.info;
                  return (
                    <div key={card.id} className={`rounded-xl border overflow-hidden ${card.status === 'resolved' ? 'opacity-50' : ''}`}
                      style={{ background: cs.gradient, borderColor: cs.border }}
                      data-testid={`card-${card.id}`}>
                      <div className="p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="text-xs font-bold text-slate-800">{card.title}</h4>
                          {card.metric && (
                            <span className="text-lg font-bold" style={{ color: ESY.deepRed }}>{card.metric.value}</span>
                          )}
                        </div>
                        <p className="text-[11px] text-slate-600 leading-relaxed">{card.description}</p>
                        {card.metric?.label && <p className="text-[9px] text-slate-400 mt-1">{card.metric.label}</p>}
                      </div>
                      {card.actions?.length > 0 && card.status !== 'resolved' && (
                        <div className="px-4 pb-3 flex flex-wrap gap-2">
                          {card.actions.map((action, j) => (
                            <button key={j} onClick={() => executeCardAction(card.id, action.action_type, action.payload)}
                              className="px-3 py-1.5 rounded-md text-[10px] font-semibold text-white transition-all hover:opacity-90"
                              style={{ background: action.action_type === 'escalate' ? ESY.deepRed : action.action_type === 'resolve' ? ESY.turquoise : ESY.pink }}
                              data-testid={`card-action-${card.id}-${j}`}>
                              {action.label}
                            </button>
                          ))}
                        </div>
                      )}
                      {card.status === 'resolved' && (
                        <div className="px-4 pb-3">
                          <span className="text-[10px] font-medium" style={{ color: ESY.turquoise }}>Resolved</span>
                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </>
          )}
        </div>
      </ScrollArea>
    </div>
  );
};

// ============== Command Bar (Ctrl+K) ==============
const CommandBar = ({ isOpen, onClose, onNavigate, token, onAction }) => {
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
        const res = await fetch(`${API}/api/lumi/command/search`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify({ query: isAi ? query.slice(1).trim() : query, mode: isAi ? 'ai' : 'search' })
        });
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
        {/* Search Input */}
        <div className="flex items-center gap-3 px-4 h-14 border-b border-slate-100">
          {mode === 'ai' ? (
            <Sparkles className="w-4.5 h-4.5 flex-shrink-0" style={{ color: ESY.turquoise }} />
          ) : (
            <Search className="w-4.5 h-4.5 text-slate-400 flex-shrink-0" />
          )}
          <input ref={inputRef} value={query} onChange={e => setQuery(e.target.value)} onKeyDown={handleKeyDown}
            placeholder='Search channels, tasks, people... (prefix ? for AI)'
            className="flex-1 text-sm bg-transparent outline-none text-slate-900 placeholder:text-slate-400"
            data-testid="command-input" />
          <kbd className="hidden sm:inline-flex items-center px-1.5 py-0.5 text-[10px] font-mono text-slate-400 bg-slate-50 rounded border border-slate-200">ESC</kbd>
          {loading && <Loader2 className="w-4 h-4 animate-spin" style={{ color: ESY.turquoise }} />}
        </div>

        {/* Results */}
        <div className="max-h-[360px] overflow-auto">
          {results.length === 0 && query && !loading && (
            <div className="px-4 py-6 text-center text-xs text-slate-400">
              {mode === 'ai' ? 'Type your question after ?' : 'No results found'}
            </div>
          )}

          {mode === 'ai' && results.length > 0 && results[0].type === 'ai_answer' ? (
            <div className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="w-3.5 h-3.5" style={{ color: ESY.turquoise }} />
                <span className="text-xs font-semibold" style={{ color: ESY.turquoise }}>AI Answer</span>
              </div>
              <p className="text-xs text-slate-700 leading-relaxed whitespace-pre-wrap" data-testid="command-ai-answer">{results[0].content}</p>
            </div>
          ) : (
            results.map((item, idx) => {
              const Icon = iconMap[item.icon] || Hash;
              const typeLabels = { channel: 'Channel', dm: 'Direct Message', message: 'Message', task: 'Task', action_item: 'Action Item', action: 'Quick Action' };
              return (
                <button key={`${item.type}-${item.id}-${idx}`} onClick={() => handleSelect(item)}
                  className={`w-full flex items-center gap-3 px-4 py-2.5 text-left transition-colors ${idx === selectedIdx ? 'bg-slate-50' : 'hover:bg-slate-50'}`}
                  data-testid={`command-result-${idx}`}>
                  <div className={`w-7 h-7 rounded-md flex items-center justify-center flex-shrink-0 ${item.type === 'action' ? 'bg-gradient-to-br' : 'bg-slate-100'}`}
                    style={item.type === 'action' ? { background: `linear-gradient(135deg, ${ESY.turquoise}15, ${ESY.pink}15)` } : {}}>
                    <Icon className="w-3.5 h-3.5" style={item.type === 'action' ? { color: ESY.turquoise } : { color: '#64748b' }} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-slate-800 truncate">{item.name || item.content || ''}</p>
                    {item.sender && <p className="text-[10px] text-slate-400">by {item.sender}</p>}
                    {item.assignee && <p className="text-[10px] text-slate-400">assigned to {item.assignee}</p>}
                  </div>
                  <span className="text-[9px] text-slate-400 uppercase tracking-wider flex-shrink-0">{typeLabels[item.type] || item.type}</span>
                  {item.type === 'action' && <ArrowRight className="w-3 h-3 text-slate-300 flex-shrink-0" />}
                </button>
              );
            })
          )}
        </div>

        {/* Footer */}
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

// ============== Knowledge Graph Panel ==============
const KnowledgeGraphPanel = ({ onClose, token }) => {
  const [graph, setGraph] = useState(null);
  const [loading, setLoading] = useState(false);
  const [impactResult, setImpactResult] = useState(null);
  const [impactLoading, setImpactLoading] = useState(false);
  const [selectedNode, setSelectedNode] = useState(null);
  const [filterType, setFilterType] = useState('all');

  const loadGraph = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/lumi/knowledge-graph`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) setGraph(await res.json());
    } catch (e) { toast.error('Failed to load graph'); }
    setLoading(false);
  };

  const runImpactAnalysis = async (node) => {
    setSelectedNode(node);
    setImpactLoading(true);
    try {
      const res = await fetch(`${API}/api/lumi/knowledge-graph/impact`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ entity_type: node.type, entity_id: node.id.split('_').slice(1).join('_'), entity_name: node.label })
      });
      if (res.ok) setImpactResult(await res.json());
    } catch (e) {}
    setImpactLoading(false);
  };

  useEffect(() => { loadGraph(); }, []);

  const nodeColors = {
    person: { bg: ESY.turquoise, text: 'white' },
    channel: { bg: '#36454F', text: 'white' },
    task: { bg: ESY.pink, text: 'white' },
    action_item: { bg: ESY.deepRed, text: 'white' },
    meeting: { bg: '#6C5CE7', text: 'white' },
  };

  const riskColors = { critical: ESY.deepRed, high: ESY.pink, medium: '#E17055', low: ESY.turquoise };

  const filteredNodes = graph?.nodes?.filter(n => filterType === 'all' || n.type === filterType) || [];

  return (
    <div className="w-[380px] border-l border-slate-200 bg-white flex flex-col h-full" data-testid="knowledge-graph-panel">
      <div className="h-14 flex items-center justify-between px-4 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <Network className="w-4 h-4" style={{ color: ESY.turquoise }} />
          <h3 className="text-sm font-semibold text-slate-900">Knowledge Graph</h3>
          {graph && <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-slate-100 text-slate-500">{graph.stats?.total_nodes} nodes</span>}
        </div>
        <button onClick={onClose} className="p-1 hover:bg-slate-100 rounded-md"><X className="w-4 h-4 text-slate-500" /></button>
      </div>

      {/* Filter */}
      <div className="flex gap-1 px-3 py-2 border-b border-slate-100 overflow-x-auto">
        {['all', 'person', 'channel', 'task', 'meeting', 'action_item'].map(t => (
          <button key={t} onClick={() => setFilterType(t)}
            className={`px-2.5 py-1 rounded-full text-[10px] font-medium whitespace-nowrap transition-colors ${filterType === t ? 'text-white' : 'bg-slate-50 text-slate-500 hover:bg-slate-100'}`}
            style={filterType === t ? { backgroundColor: nodeColors[t]?.bg || ESY.turquoise } : {}}
            data-testid={`graph-filter-${t}`}>
            {t === 'all' ? 'All' : t === 'action_item' ? 'Actions' : t.charAt(0).toUpperCase() + t.slice(1)}s
          </button>
        ))}
      </div>

      <ScrollArea className="flex-1">
        <div className="p-3">
          {loading ? (
            <div className="flex items-center justify-center py-8"><Loader2 className="w-5 h-5 animate-spin" style={{ color: ESY.turquoise }} /></div>
          ) : !graph ? (
            <button onClick={loadGraph} className="w-full py-3 rounded-lg border text-sm" style={{ borderColor: `${ESY.turquoise}30`, color: ESY.turquoise }}>Load Knowledge Graph</button>
          ) : (
            <>
              {/* Stats Cards */}
              <div className="grid grid-cols-3 gap-2 mb-3">
                {Object.entries(graph.stats?.by_type || {}).map(([type, count]) => (
                  <div key={type} className="p-2 rounded-lg border border-slate-100 text-center">
                    <p className="text-lg font-bold" style={{ color: nodeColors[type]?.bg || '#64748b' }}>{count}</p>
                    <p className="text-[9px] text-slate-400 capitalize">{type === 'action_item' ? 'Actions' : type}s</p>
                  </div>
                ))}
              </div>

              {/* Edge count */}
              <div className="mb-3 p-2 rounded-lg border border-slate-100 flex items-center justify-between">
                <span className="text-xs text-slate-500">Relationships</span>
                <span className="text-sm font-bold" style={{ color: ESY.pink }}>{graph.stats?.total_edges}</span>
              </div>

              {/* Node List */}
              <div className="space-y-1">
                {filteredNodes.slice(0, 30).map((node) => {
                  const nc = nodeColors[node.type] || { bg: '#64748b', text: 'white' };
                  const connections = graph.edges?.filter(e => e.source === node.id || e.target === node.id).length || 0;
                  return (
                    <button key={node.id} onClick={() => runImpactAnalysis(node)}
                      className={`w-full flex items-center gap-2.5 p-2 rounded-lg border transition-all hover:shadow-sm ${selectedNode?.id === node.id ? 'border-slate-300 bg-slate-50' : 'border-slate-100 hover:border-slate-200'}`}
                      data-testid={`graph-node-${node.id}`}>
                      <div className="w-6 h-6 rounded-full flex items-center justify-center text-[8px] font-bold flex-shrink-0" style={{ backgroundColor: nc.bg, color: nc.text }}>
                        {node.label?.[0]?.toUpperCase() || '?'}
                      </div>
                      <div className="flex-1 min-w-0 text-left">
                        <p className="text-xs font-medium text-slate-800 truncate">{node.label}</p>
                        <p className="text-[9px] text-slate-400">{node.type} · {connections} connections</p>
                      </div>
                      {node.status && (
                        <span className={`text-[8px] px-1.5 py-0.5 rounded ${node.status === 'done' ? 'bg-emerald-50 text-emerald-600' : node.status === 'open' ? 'bg-amber-50 text-amber-600' : 'bg-slate-50 text-slate-500'}`}>{node.status}</span>
                      )}
                    </button>
                  );
                })}
              </div>
            </>
          )}

          {/* Impact Analysis Result */}
          {impactLoading && (
            <div className="mt-3 p-3 rounded-lg border border-slate-200 bg-slate-50 text-center">
              <Loader2 className="w-4 h-4 animate-spin mx-auto" style={{ color: ESY.turquoise }} />
              <p className="text-[10px] text-slate-400 mt-1">Analyzing impact...</p>
            </div>
          )}
          {impactResult && !impactLoading && (
            <div className="mt-3 p-3 rounded-xl border" style={{ borderColor: `${riskColors[impactResult.risk_level]}30`, background: `${riskColors[impactResult.risk_level]}05` }}
              data-testid="impact-result">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-slate-800">Impact Analysis</span>
                <span className="text-[9px] font-bold px-2 py-0.5 rounded-full text-white" style={{ backgroundColor: riskColors[impactResult.risk_level] }}>{impactResult.risk_level?.toUpperCase()}</span>
              </div>
              {impactResult.direct?.map((d, i) => (
                <div key={i} className="flex items-start gap-2 text-xs text-slate-600 mb-1">
                  <Zap className="w-3 h-3 mt-0.5 flex-shrink-0" style={{ color: ESY.deepRed }} />
                  <span>{d.description}</span>
                </div>
              ))}
              {impactResult.indirect?.map((d, i) => (
                <div key={i} className="flex items-start gap-2 text-xs text-slate-500 mb-1">
                  <Globe className="w-3 h-3 mt-0.5 flex-shrink-0" style={{ color: ESY.pink }} />
                  <span>{d.description}</span>
                </div>
              ))}
              {impactResult.ai_analysis && (
                <div className="mt-2 pt-2 border-t border-slate-100">
                  <p className="text-[10px] text-slate-600 leading-relaxed whitespace-pre-wrap">{impactResult.ai_analysis}</p>
                </div>
              )}
            </div>
          )}
        </div>
      </ScrollArea>
    </div>
  );
};

// ============== Bottleneck Panel ==============
const BottleneckPanel = ({ onClose, token }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadBottlenecks = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/lumi/bottlenecks`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) setData(await res.json());
    } catch (e) { toast.error('Failed to load bottlenecks'); }
    setLoading(false);
  };

  useEffect(() => { loadBottlenecks(); }, []);

  const severityIcon = { critical: AlertTriangle, warning: TrendingDown, info: Activity };
  const healthColor = (score) => score >= 80 ? ESY.turquoise : score >= 50 ? '#E17055' : ESY.deepRed;

  return (
    <div className="w-[350px] border-l border-slate-200 bg-white flex flex-col h-full" data-testid="bottleneck-panel">
      <div className="h-14 flex items-center justify-between px-4 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <TrendingDown className="w-4 h-4" style={{ color: ESY.deepRed }} />
          <h3 className="text-sm font-semibold text-slate-900">Bottlenecks</h3>
        </div>
        <button onClick={onClose} className="p-1 hover:bg-slate-100 rounded-md"><X className="w-4 h-4 text-slate-500" /></button>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4">
          {loading ? (
            <div className="flex items-center justify-center py-8"><Loader2 className="w-5 h-5 animate-spin" style={{ color: ESY.turquoise }} /></div>
          ) : !data ? (
            <button onClick={loadBottlenecks} className="w-full py-3 rounded-lg border text-sm" style={{ borderColor: `${ESY.deepRed}30`, color: ESY.deepRed }}>Scan for Bottlenecks</button>
          ) : (
            <>
              {/* Health Score */}
              <div className="flex items-center justify-between p-4 rounded-xl bg-slate-50 border border-slate-100 mb-4">
                <div>
                  <p className="text-[10px] text-slate-400 uppercase tracking-wider mb-1">Project Health</p>
                  <p className="text-3xl font-bold" style={{ color: healthColor(data.health_score) }}>{data.health_score}</p>
                </div>
                <div className="text-right space-y-1">
                  <div className="text-[10px] text-slate-500"><span className="font-semibold">{data.workload_summary?.total_open_items || 0}</span> open items</div>
                  <div className="text-[10px] text-slate-500"><span className="font-semibold">{data.workload_summary?.people_with_work || 0}</span> people assigned</div>
                  <div className="text-[10px] text-slate-500"><span className="font-semibold">{data.workload_summary?.avg_workload || 0}</span> avg workload</div>
                </div>
              </div>

              {/* Bottleneck Items */}
              {data.bottlenecks?.length === 0 ? (
                <div className="text-center py-6">
                  <CheckCircle2 className="w-10 h-10 mx-auto mb-2" style={{ color: ESY.turquoise }} />
                  <p className="text-sm font-medium text-slate-700">No Bottlenecks</p>
                  <p className="text-xs text-slate-400 mt-1">Team workload is balanced</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {data.bottlenecks.map((bn) => {
                    const Icon = severityIcon[bn.severity] || Activity;
                    const color = bn.severity === 'critical' ? ESY.deepRed : bn.severity === 'warning' ? ESY.pink : ESY.turquoise;
                    return (
                      <div key={bn.id} className="p-3 rounded-xl border" style={{ borderColor: `${color}20`, background: `${color}05` }}
                        data-testid={`bottleneck-${bn.id}`}>
                        <div className="flex items-start gap-2">
                          <Icon className="w-4 h-4 mt-0.5 flex-shrink-0" style={{ color }} />
                          <div className="flex-1 min-w-0">
                            <p className="text-xs font-semibold text-slate-800">{bn.title}</p>
                            <p className="text-[11px] text-slate-600 mt-1 leading-relaxed">{bn.description}</p>
                            {bn.items && (
                              <div className="mt-2 space-y-0.5">
                                {bn.items.slice(0, 3).map((item, i) => (
                                  <p key={i} className="text-[10px] text-slate-500 pl-2 border-l-2" style={{ borderColor: `${color}30` }}>{item}</p>
                                ))}
                              </div>
                            )}
                            {bn.workload && (
                              <div className="mt-2 flex items-center gap-2">
                                <span className="text-[9px] px-2 py-0.5 rounded-full font-medium text-white" style={{ backgroundColor: color }}>{bn.workload.total} tasks</span>
                                {bn.workload.high > 0 && <span className="text-[9px] px-2 py-0.5 rounded-full font-medium text-white" style={{ backgroundColor: ESY.deepRed }}>{bn.workload.high} critical</span>}
                              </div>
                            )}
                            {bn.suggestion && (
                              <p className="text-[10px] mt-2 font-medium" style={{ color: ESY.turquoise }}>Suggestion: {bn.suggestion}</p>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

              <button onClick={loadBottlenecks} className="w-full mt-3 text-xs py-1.5 rounded-md hover:bg-slate-50 transition-colors" style={{ color: ESY.turquoise }}>
                Rescan
              </button>
            </>
          )}
        </div>
      </ScrollArea>
    </div>
  );
};

// ============== Create Channel Modal ==============
const CreateChannelModal = ({ onClose, onCreated, token }) => {
  const { t } = useTranslation();
  const [name, setName] = useState('');
  const [desc, setDesc] = useState('');
  const [type, setType] = useState('group');
  const [isPrivate, setIsPrivate] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleCreate = async () => {
    if (!name.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/lumi/channels`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ name: name.trim(), description: desc, channel_type: type, is_private: isPrivate })
      });
      if (res.ok) { onCreated(await res.json()); toast.success('Channel created'); }
    } catch (e) { toast.error('Failed'); }
    setLoading(false);
  };

  const types = [
    { val: 'group', label: t('lumi.typeGroup') || 'Group', icon: Hash },
    { val: 'project', label: t('lumi.typeProject') || 'Project', icon: Hash },
    { val: 'announcement', label: t('lumi.typeAnnouncement') || 'Announcement', icon: Megaphone },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-white border border-slate-200 rounded-lg w-full max-w-md p-6 shadow-lg" onClick={e => e.stopPropagation()} data-testid="create-channel-modal">
        <div className="flex items-center justify-between mb-5">
          <h3 className="text-lg font-semibold text-slate-900">{t('lumi.createChannel') || 'Create Channel'}</h3>
          <button onClick={onClose} className="p-1 hover:bg-slate-100 rounded-md"><X className="w-5 h-5 text-slate-400" /></button>
        </div>
        <div className="space-y-4">
          <div>
            <label className="text-xs font-medium text-slate-500 mb-1.5 block">{t('lumi.channelName') || 'Channel Name'}</label>
            <Input value={name} onChange={e => setName(e.target.value)} placeholder="e.g. project-alpha"
              className="border-slate-200 rounded-md focus:ring-[#008080]/20 focus:border-[#008080]" data-testid="channel-name-input" />
          </div>
          <div>
            <label className="text-xs font-medium text-slate-500 mb-1.5 block">{t('lumi.description') || 'Description'}</label>
            <Input value={desc} onChange={e => setDesc(e.target.value)} placeholder="What's this channel about?"
              className="border-slate-200 rounded-md focus:ring-[#008080]/20 focus:border-[#008080]" data-testid="channel-desc-input" />
          </div>
          <div className="flex gap-2">
            {types.map(tp => (
              <button key={tp.val} onClick={() => setType(tp.val)}
                className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-md text-xs font-medium transition-colors ${
                  type === tp.val ? 'bg-[#008080]/10 text-[#008080] border border-[#008080]/30' : 'bg-slate-50 text-slate-500 border border-slate-200 hover:bg-slate-100'
                }`} data-testid={`type-${tp.val}`}>
                <tp.icon className="w-3.5 h-3.5" />{tp.label}
              </button>
            ))}
          </div>
          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" checked={isPrivate} onChange={e => setIsPrivate(e.target.checked)} className="rounded border-slate-300 text-[#008080]" />
            <Lock className="w-3.5 h-3.5 text-slate-400" /><span className="text-sm text-slate-600">{t('lumi.privateChannel') || 'Private'}</span>
          </label>
        </div>
        <div className="flex gap-3 mt-6">
          <Button variant="ghost" onClick={onClose} className="flex-1 text-slate-500 hover:bg-slate-100 rounded-md">Cancel</Button>
          <Button onClick={handleCreate} disabled={!name.trim() || loading}
            className="flex-1 bg-[#008080] hover:bg-[#006666] text-white rounded-md" data-testid="create-channel-btn">
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Create'}
          </Button>
        </div>
      </div>
    </div>
  );
};

// ============== New DM Modal ==============
const NewDmModal = ({ onClose, onSelect, token }) => {
  const { t } = useTranslation();
  const [query, setQuery] = useState('');
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const search = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${API}/api/lumi/users/search?q=${encodeURIComponent(query)}`, { headers: { 'Authorization': `Bearer ${token}` } });
        if (res.ok) { setUsers((await res.json()).users || []); }
      } catch (e) {}
      setLoading(false);
    };
    const timer = setTimeout(search, 300);
    return () => clearTimeout(timer);
  }, [query, token]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-white border border-slate-200 rounded-lg w-full max-w-md p-6 shadow-lg" onClick={e => e.stopPropagation()} data-testid="new-dm-modal">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-slate-900">{t('lumi.newMessage') || 'New Message'}</h3>
          <button onClick={onClose} className="p-1 hover:bg-slate-100 rounded-md"><X className="w-5 h-5 text-slate-400" /></button>
        </div>
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input value={query} onChange={e => setQuery(e.target.value)} placeholder={t('lumi.searchUsers') || 'Search by name or email...'}
            className="pl-10 border-slate-200 rounded-md" autoFocus data-testid="dm-search-input" />
        </div>
        <div className="max-h-64 overflow-y-auto space-y-1">
          {loading && <div className="flex justify-center py-4"><Loader2 className="w-5 h-5 text-[#008080] animate-spin" /></div>}
          {!loading && users.length === 0 && <p className="text-sm text-slate-400 text-center py-4">{t('lumi.noUsersFound') || 'No users found'}</p>}
          {!loading && users.map(u => (
            <button key={u.user_id} onClick={() => onSelect(u.user_id)}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-md hover:bg-slate-50 transition-colors" data-testid={`dm-user-${u.user_id}`}>
              <div className="relative">
                <div className="w-9 h-9 rounded-full bg-[#36454F] flex items-center justify-center">
                  <span className="text-xs font-semibold text-white">{(u.name || u.email || '?')[0].toUpperCase()}</span>
                </div>
                <span className={`absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full ring-2 ring-white ${STATUS_COLORS[u.status] || STATUS_COLORS.offline}`} />
              </div>
              <div className="text-left"><p className="text-sm font-medium text-slate-900">{u.name || 'Unknown'}</p><p className="text-[11px] text-slate-400">{u.email}</p></div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

// ============== Main LUMI Messenger ==============
const LumiMessenger = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [channels, setChannels] = useState([]);
  const [discoverChannels, setDiscoverChannels] = useState([]);
  const [activeChannel, setActiveChannel] = useState(null);
  const [messages, setMessages] = useState([]);
  const [messageText, setMessageText] = useState('');
  const [sending, setSending] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showNewDmModal, setShowNewDmModal] = useState(false);
  const [dms, setDms] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [typingUsers, setTypingUsers] = useState({});
  const [mobileSidebar, setMobileSidebar] = useState(true);
  const [globalSearch, setGlobalSearch] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [unreadCounts, setUnreadCounts] = useState({});
  const [uploading, setUploading] = useState(false);
  const [showThread, setShowThread] = useState(null);
  const [showMembers, setShowMembers] = useState(false);
  const [showAiPanel, setShowAiPanel] = useState(false);
  const [showAiChat, setShowAiChat] = useState(false);
  const [showAlerts, setShowAlerts] = useState(false);
  const [showCommandBar, setShowCommandBar] = useState(false);
  const [showKnowledgeGraph, setShowKnowledgeGraph] = useState(false);
  const [showBottlenecks, setShowBottlenecks] = useState(false);
  const [presenceMap, setPresenceMap] = useState({});

  const messagesEndRef = useRef(null);
  const wsRef = useRef(null);
  const typingTimeoutRef = useRef(null);
  const fileInputRef = useRef(null);
  const token = localStorage.getItem('token');

  // Auth
  useEffect(() => {
    const savedUser = localStorage.getItem('karau_user');
    if (savedUser && token) setUser(JSON.parse(savedUser));
    setIsLoading(false);
  }, [token]);

  // Load channels
  const loadChannels = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/api/lumi/channels`, { headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) {
        const data = await res.json();
        setChannels(data.my_channels || []);
        setDiscoverChannels(data.discover || []);
        if ((data.my_channels || []).length === 0 && (data.discover || []).length === 0) {
          await fetch(`${API}/api/lumi/seed`, { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } });
          await fetch(`${API}/api/lumi/domain/auto-channel`, { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } });
          const r2 = await fetch(`${API}/api/lumi/channels`, { headers: { 'Authorization': `Bearer ${token}` } });
          if (r2.ok) { const d2 = await r2.json(); setChannels(d2.my_channels || []); setDiscoverChannels(d2.discover || []); }
        }
      }
    } catch (e) {}
  }, [token]);

  const loadDms = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/api/lumi/dm`, { headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) setDms((await res.json()).dms || []);
    } catch (e) {}
  }, [token]);

  const loadUnreadCounts = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/api/lumi/unread-counts`, { headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) setUnreadCounts((await res.json()).unread || {});
    } catch (e) {}
  }, [token]);

  const loadPresence = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/api/lumi/presence/all`, { headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) setPresenceMap((await res.json()).presence || {});
    } catch (e) {}
  }, [token]);

  useEffect(() => {
    if (user) { loadChannels(); loadDms(); loadUnreadCounts(); loadPresence(); }
  }, [user, loadChannels, loadDms, loadUnreadCounts, loadPresence]);

  // Mark as read when switching channels
  useEffect(() => {
    if (!activeChannel || !token) return;
    fetch(`${API}/api/lumi/channels/${activeChannel.id}/read`, { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } })
      .then(() => setUnreadCounts(prev => { const n = { ...prev }; delete n[activeChannel.id]; return n; }));
  }, [activeChannel, token]);

  // WebSocket
  useEffect(() => {
    if (!user) return;
    const connectWs = () => {
      const ws = new WebSocket(`${WS_URL}/api/lumi/ws/${user.user_id}`);
      wsRef.current = ws;
      ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.type === 'message') {
          setMessages(prev => prev.some(m => m.id === msg.data.id) ? prev : [...prev, msg.data]);
          loadChannels(); loadDms(); loadUnreadCounts();
        } else if (msg.type === 'reaction') {
          setMessages(prev => prev.map(m => m.id === msg.data.message_id ? { ...m, reactions: msg.data.reactions } : m));
        } else if (msg.type === 'thread_reply') {
          setMessages(prev => prev.map(m => m.id === msg.data.parent_id ? { ...m, thread_count: (m.thread_count || 0) + 1 } : m));
        } else if (msg.type === 'dm_created') {
          loadDms();
        } else if (msg.type === 'presence_change') {
          setPresenceMap(prev => ({ ...prev, [msg.data.user_id]: msg.data.status }));
        } else if (msg.type === 'typing') {
          setTypingUsers(prev => ({ ...prev, [msg.data.channel_id]: { ...(prev[msg.data.channel_id] || {}), [msg.data.user_id]: msg.data.name || msg.data.user_id } }));
          setTimeout(() => setTypingUsers(prev => { const ch = { ...(prev[msg.data.channel_id] || {}) }; delete ch[msg.data.user_id]; return { ...prev, [msg.data.channel_id]: ch }; }), 3000);
        }
      };
      ws.onclose = () => setTimeout(connectWs, 3000);
    };
    connectWs();
    return () => { if (wsRef.current) wsRef.current.close(); };
  }, [user, loadChannels, loadDms, loadUnreadCounts]);

  // Load messages
  useEffect(() => {
    if (!activeChannel || !token) return;
    fetch(`${API}/api/lumi/channels/${activeChannel.id}/messages?limit=100`, { headers: { 'Authorization': `Bearer ${token}` } })
      .then(r => r.json()).then(d => setMessages(d.messages || []));
  }, [activeChannel, token]);

  // Ctrl+K Command Bar
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') { e.preventDefault(); setShowCommandBar(true); }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  // Actions
  const handleSend = async () => {
    if (!messageText.trim() || !activeChannel || sending) return;
    const text = messageText.trim(); setMessageText(''); setSending(true);
    try { await fetch(`${API}/api/lumi/channels/${activeChannel.id}/messages`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }, body: JSON.stringify({ content: text }) }); } catch (e) { toast.error('Failed'); setMessageText(text); }
    setSending(false);
  };

  const handleStartDm = async (recipientId) => {
    try {
      const res = await fetch(`${API}/api/lumi/dm`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }, body: JSON.stringify({ recipient_id: recipientId }) });
      if (res.ok) { const dm = await res.json(); await loadDms(); setActiveChannel(dm); setShowNewDmModal(false); setMobileSidebar(false); }
    } catch (e) { toast.error('Failed'); }
  };

  const handleReact = async (messageId, emoji) => {
    try {
      const res = await fetch(`${API}/api/lumi/messages/${messageId}/react`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }, body: JSON.stringify({ emoji }) });
      if (res.ok) { const d = await res.json(); setMessages(prev => prev.map(m => m.id === messageId ? { ...m, reactions: d.reactions } : m)); }
    } catch (e) {}
  };

  const handleFileShare = async (e) => {
    const file = e.target.files?.[0];
    if (!file || !activeChannel) return;
    if (file.size > 10 * 1024 * 1024) { toast.error('Max 10MB'); return; }
    setUploading(true);
    try {
      const fd = new FormData(); fd.append('file', file);
      const r = await fetch(`${API}/api/lumi/upload?channel_id=${activeChannel.id}`, { method: 'POST', headers: { 'Authorization': `Bearer ${token}` }, body: fd });
      if (r.ok) {
        const fileData = await r.json();
        const mr = await fetch(`${API}/api/lumi/channels/${activeChannel.id}/messages`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }, body: JSON.stringify({ content: `Shared: ${file.name}` }) });
        if (mr.ok) { const msg = await mr.json(); setMessages(prev => prev.map(m => m.id === msg.id ? { ...m, file: fileData } : m)); }
        toast.success('File shared');
      }
    } catch (e) { toast.error('Upload failed'); }
    setUploading(false); e.target.value = '';
  };

  const handleGlobalSearch = async (query) => {
    setGlobalSearch(query);
    if (query.length < 2) { setSearchResults([]); setShowSearchResults(false); return; }
    try {
      const res = await fetch(`${API}/api/lumi/search?q=${encodeURIComponent(query)}`, { headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) { setSearchResults((await res.json()).results || []); setShowSearchResults(true); }
    } catch (e) {}
  };

  const handleJoinChannel = async (ch) => {
    await fetch(`${API}/api/lumi/channels/${ch.id}/join`, { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } });
    await loadChannels(); setActiveChannel(ch); setMobileSidebar(false); toast.success(`Joined #${ch.name}`);
  };

  const handleKeyDown = (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } };
  const handleTyping = () => {
    if (!activeChannel || !wsRef.current || typingTimeoutRef.current) return;
    try { wsRef.current.send(JSON.stringify({ type: 'typing', channel_id: activeChannel.id })); } catch (e) {}
    typingTimeoutRef.current = setTimeout(() => { typingTimeoutRef.current = null; }, 2000);
  };

  const filteredChannels = channels.filter(ch => ch.name.toLowerCase().includes(searchQuery.toLowerCase()));
  const activeTyping = activeChannel ? Object.values(typingUsers[activeChannel.id] || {}).filter(n => n !== user?.name) : [];

  if (isLoading) return <div className="min-h-screen bg-slate-50 flex items-center justify-center"><Loader2 className="w-8 h-8 text-[#008080] animate-spin" /></div>;
  if (!user) return <LumiLogin onLogin={setUser} />;

  return (
    <div className="h-screen flex bg-slate-50 overflow-hidden" style={{ fontFamily: "'Inter', -apple-system, sans-serif" }}>
      <Toaster position="top-right" richColors />

      {/* ===== Sidebar ===== */}
      <div className={`${mobileSidebar ? 'flex' : 'hidden'} md:flex flex-col w-full md:w-[280px] bg-[#36454F] flex-shrink-0`}>
        {/* Header */}
        <div className="h-14 flex items-center justify-between px-4 border-b border-white/10">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-md flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` }}>
              <MessageCircle className="w-4.5 h-4.5 text-white" />
            </div>
            <span className="font-bold text-sm text-white tracking-wide">LUMI</span>
          </div>
          <button onClick={() => navigate('/')} className="p-2 text-slate-300 hover:text-white hover:bg-white/10 rounded-md transition-colors" data-testid="back-to-karau">
            <ArrowLeft className="w-4 h-4" />
          </button>
        </div>

        {/* Search */}
        <div className="px-3 pt-3 pb-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
            <input value={globalSearch || searchQuery} onChange={e => { setSearchQuery(e.target.value); handleGlobalSearch(e.target.value); }}
              placeholder={t('lumi.searchChannels') || 'Search...'}
              className="w-full pl-9 h-8 bg-white/10 border-0 rounded-md text-sm text-white placeholder:text-slate-400 outline-none focus:bg-white/15 transition-colors" data-testid="search-channels" />
            {globalSearch && <button onClick={() => { setGlobalSearch(''); setSearchQuery(''); setShowSearchResults(false); }} className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-300 hover:text-white"><X className="w-3.5 h-3.5" /></button>}
          </div>
          {showSearchResults && searchResults.length > 0 && (
            <div className="mt-1 max-h-48 overflow-y-auto bg-[#2d3a42] border border-white/10 rounded-md shadow-lg" data-testid="search-results">
              {searchResults.map((r, i) => (
                <button key={i} onClick={() => { const ch = channels.find(c => c.id === r.channel_id) || dms.find(d => d.id === r.channel_id); if (ch) { setActiveChannel(ch); setMobileSidebar(false); } setShowSearchResults(false); setGlobalSearch(''); setSearchQuery(''); }}
                  className="w-full px-3 py-2 text-left hover:bg-white/10 border-b border-white/5 last:border-0" data-testid={`search-result-${i}`}>
                  <span className="text-[10px] text-[#5bbfbf] font-medium">#{r.channel_name}</span>
                  <p className="text-xs text-slate-200 truncate">{r.content}</p>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Channel List */}
        <ScrollArea className="flex-1 py-2">
          <div className="px-3">
            {/* Channels */}
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-[11px] font-semibold text-slate-300/70 uppercase tracking-widest">Channels</span>
              <button onClick={() => setShowCreateModal(true)} className="p-1 text-slate-300 hover:text-white hover:bg-white/10 rounded transition-colors" data-testid="add-channel-btn"><Plus className="w-3.5 h-3.5" /></button>
            </div>
            {filteredChannels.map(ch => (
              <button key={ch.id} onClick={() => { setActiveChannel(ch); setMobileSidebar(false); setShowThread(null); setShowMembers(false); setShowAiPanel(false); }}
                className={`w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md transition-colors mb-0.5 ${
                  activeChannel?.id === ch.id ? 'bg-white/15 text-white' : 'text-slate-300 hover:bg-white/10 hover:text-white'
                }`} data-testid={`channel-${ch.id}`}>
                <ChannelIcon type={ch.channel_type} />
                <span className="flex-1 text-sm truncate text-left">{ch.name}</span>
                {unreadCounts[ch.id] > 0 && <span className="min-w-[18px] h-[18px] flex items-center justify-center rounded-full text-[9px] font-bold text-white" style={{ backgroundColor: ESY.pink }} data-testid={`unread-${ch.id}`}>{unreadCounts[ch.id]}</span>}
              </button>
            ))}

            {/* Discover */}
            {discoverChannels.length > 0 && (
              <>
                <div className="flex items-center mt-3 mb-1.5"><span className="text-[11px] font-semibold text-slate-300/70 uppercase tracking-widest">Discover</span></div>
                {discoverChannels.map(ch => (
                  <button key={ch.id} onClick={() => handleJoinChannel(ch)} className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md text-slate-400 hover:bg-white/10 hover:text-white mb-0.5" data-testid={`discover-${ch.id}`}>
                    <ChannelIcon type={ch.channel_type} /><span className="flex-1 text-sm truncate text-left">{ch.name}</span><Plus className="w-3 h-3 opacity-70" />
                  </button>
                ))}
              </>
            )}

            {/* DMs */}
            <div className="flex items-center justify-between mt-3 mb-1.5">
              <span className="text-[11px] font-semibold text-slate-300/70 uppercase tracking-widest">Direct Messages</span>
              <button onClick={() => setShowNewDmModal(true)} className="p-1 text-slate-300 hover:text-white hover:bg-white/10 rounded transition-colors" data-testid="new-dm-btn"><UserPlus className="w-3.5 h-3.5" /></button>
            </div>
            {dms.map(dm => {
              const partner = dm.dm_partner || {};
              const init = (partner.name || partner.email || '?')[0].toUpperCase();
              const st = presenceMap[partner.user_id] || 'offline';
              return (
                <button key={dm.id} onClick={() => { setActiveChannel(dm); setMobileSidebar(false); setShowThread(null); setShowMembers(false); setShowAiPanel(false); }}
                  className={`w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md transition-colors mb-0.5 ${
                    activeChannel?.id === dm.id ? 'bg-white/15 text-white' : 'text-slate-300 hover:bg-white/10 hover:text-white'
                  }`} data-testid={`dm-${dm.id}`}>
                  <div className="relative">
                    <div className="w-6 h-6 rounded-full bg-slate-500 flex items-center justify-center text-[9px] font-semibold text-white">{init}</div>
                    <span className={`absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full ring-1 ring-[#36454F] ${STATUS_COLORS[st]}`} />
                  </div>
                  <span className="flex-1 text-sm truncate text-left">{partner.name || partner.email || 'User'}</span>
                  {unreadCounts[dm.id] > 0 && <span className="min-w-[16px] h-[16px] flex items-center justify-center rounded-full text-[8px] font-bold text-white" style={{ backgroundColor: ESY.pink }} data-testid={`unread-dm-${dm.id}`}>{unreadCounts[dm.id]}</span>}
                </button>
              );
            })}
            {dms.length === 0 && <p className="text-[11px] text-slate-400 px-2.5 py-1">No conversations yet</p>}
          </div>
        </ScrollArea>

        {/* User */}
        <div className="p-3 border-t border-white/10">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` }}><span className="text-xs font-semibold text-white">{(user?.name || user?.email || '?')[0].toUpperCase()}</span></div>
              <span className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full ring-2 ring-[#36454F] bg-emerald-500" />
            </div>
            <div className="flex-1 min-w-0"><p className="text-sm font-medium text-white truncate">{user?.name || 'User'}</p><p className="text-[10px] text-slate-300">Available</p></div>
            <button onClick={() => { localStorage.removeItem('token'); localStorage.removeItem('karau_user'); setUser(null); navigate('/'); }} className="p-1.5 text-slate-300 hover:text-red-400 hover:bg-red-500/10 rounded-md" data-testid="lumi-logout"><LogOut className="w-3.5 h-3.5" /></button>
          </div>
        </div>

        {/* Footer Nav - Switch to AI KARAU */}
        <div className="px-3 pb-3">
          <button onClick={() => navigate('/karau-meet')} className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-md transition-colors group" data-testid="switch-to-karau-footer">
            <Building2 className="w-3.5 h-3.5 group-hover:text-white" style={{ color: ESY.turquoise }} />
            <span className="text-xs font-medium text-slate-300 group-hover:text-white">Switch to AI KARAU</span>
          </button>
        </div>
      </div>

      {/* ===== Chat Area ===== */}
      <div className={`${!mobileSidebar ? 'flex' : 'hidden'} md:flex flex-col flex-1 min-w-0 bg-white`}>
        {activeChannel ? (
          <>
            {/* Header */}
            <div className="h-14 flex items-center justify-between px-5 border-b border-slate-200 flex-shrink-0 bg-white">
              <div className="flex items-center gap-3">
                <button className="md:hidden p-2 text-slate-500 hover:text-slate-900" onClick={() => setMobileSidebar(true)}><ArrowLeft className="w-4 h-4" /></button>
                {activeChannel.channel_type === 'dm' ? (
                  <><div className="relative"><div className="w-9 h-9 rounded-full bg-[#36454F] flex items-center justify-center"><User className="w-4 h-4 text-white" /></div><StatusDot status={presenceMap[activeChannel.dm_partner?.user_id] || 'offline'} /></div>
                  <div><h2 className="text-sm font-semibold text-slate-900">{activeChannel.dm_partner?.name || activeChannel.name}</h2><p className="text-[11px] text-slate-400">{STATUS_LABELS[presenceMap[activeChannel.dm_partner?.user_id]] || 'Offline'}</p></div></>
                ) : (
                  <><div className="w-9 h-9 rounded-md bg-slate-100 flex items-center justify-center text-slate-600"><ChannelIcon type={activeChannel.channel_type} /></div>
                  <div><h2 className="text-sm font-semibold text-slate-900">#{activeChannel.name}</h2><p className="text-[11px] text-slate-400">{activeChannel.members?.length || 0} members</p></div></>
                )}
              </div>
              <div className="flex items-center gap-1">
                {activeChannel.channel_type === 'dm' && (
                  <button onClick={() => toast.info('Calling...')} className="p-2 text-slate-400 hover:text-[#008080] hover:bg-[#008080]/5 rounded-md" data-testid="voice-call-btn"><Phone className="w-4 h-4" /></button>
                )}
                <button onClick={() => setShowCommandBar(true)}
                  className="p-2 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
                  data-testid="command-bar-btn" title="Command Bar (Ctrl+K)"><Command className="w-4 h-4" /></button>
                <button onClick={() => { setShowAiChat(!showAiChat); setShowAlerts(false); setShowAiPanel(false); setShowKnowledgeGraph(false); setShowBottlenecks(false); }}
                  className={`p-2 rounded-md transition-colors ${showAiChat ? 'bg-[#00CEC9]/10' : 'text-slate-400 hover:text-slate-600 hover:bg-slate-100'}`}
                  style={showAiChat ? { color: ESY.turquoise } : {}}
                  data-testid="ai-chat-btn" title="Ask AI"><Sparkles className="w-4 h-4" /></button>
                <button onClick={() => { setShowAlerts(!showAlerts); setShowAiChat(false); setShowAiPanel(false); setShowKnowledgeGraph(false); setShowBottlenecks(false); }}
                  className={`p-2 rounded-md transition-colors ${showAlerts ? 'bg-[#D63031]/10' : 'text-slate-400 hover:text-slate-600 hover:bg-slate-100'}`}
                  style={showAlerts ? { color: ESY.deepRed } : {}}
                  data-testid="alerts-btn" title="Alerts & Decisions"><AlertTriangle className="w-4 h-4" /></button>
                <button onClick={() => { setShowKnowledgeGraph(!showKnowledgeGraph); setShowAiChat(false); setShowAlerts(false); setShowAiPanel(false); setShowBottlenecks(false); }}
                  className={`p-2 rounded-md transition-colors ${showKnowledgeGraph ? 'bg-[#00CEC9]/10' : 'text-slate-400 hover:text-slate-600 hover:bg-slate-100'}`}
                  style={showKnowledgeGraph ? { color: ESY.turquoise } : {}}
                  data-testid="knowledge-graph-btn" title="Knowledge Graph"><Network className="w-4 h-4" /></button>
                <button onClick={() => { setShowBottlenecks(!showBottlenecks); setShowAiChat(false); setShowAlerts(false); setShowAiPanel(false); setShowKnowledgeGraph(false); }}
                  className={`p-2 rounded-md transition-colors ${showBottlenecks ? 'bg-[#D63031]/10' : 'text-slate-400 hover:text-slate-600 hover:bg-slate-100'}`}
                  style={showBottlenecks ? { color: ESY.deepRed } : {}}
                  data-testid="bottleneck-btn" title="Bottlenecks"><TrendingDown className="w-4 h-4" /></button>
                <button onClick={() => { setShowAiPanel(!showAiPanel); setShowAiChat(false); setShowAlerts(false); setShowKnowledgeGraph(false); setShowBottlenecks(false); }}
                  className={`p-2 rounded-md transition-colors ${showAiPanel ? 'text-[#008080] bg-[#008080]/5' : 'text-slate-400 hover:text-slate-600 hover:bg-slate-100'}`}
                  data-testid="ai-panel-btn" title="AI Insights"><Brain className="w-4 h-4" /></button>
                <button onClick={() => setShowMembers(!showMembers)} className={`p-2 rounded-md transition-colors ${showMembers ? 'text-[#008080] bg-[#008080]/5' : 'text-slate-400 hover:text-slate-600 hover:bg-slate-100'}`} data-testid="channel-members-btn"><Users className="w-4 h-4" /></button>
              </div>
            </div>

            <div className="flex flex-1 overflow-hidden">
              {/* Messages */}
              <div className="flex-1 flex flex-col min-w-0">
                <ScrollArea className="flex-1 py-3">
                  {messages.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-full text-center px-6">
                      <div className="w-16 h-16 rounded-lg bg-slate-100 flex items-center justify-center mb-4"><MessageCircle className="w-8 h-8 text-slate-300" /></div>
                      <p className="text-slate-400 text-sm">{t('lumi.noMessages') || 'No messages yet'}</p>
                    </div>
                  )}
                  {messages.filter(m => !m.thread_parent_id).map((msg, i, arr) => {
                    const prevSameSender = i > 0 && arr[i - 1].sender_id === msg.sender_id && arr[i - 1].type !== 'system';
                    return <MessageBubble key={msg.id} msg={msg} isOwn={msg.sender_id === user?.user_id} prevSameSender={prevSameSender}
                      onReact={handleReact} onThread={(id) => setShowThread(id)} token={token} />;
                  })}
                  <div ref={messagesEndRef} />
                </ScrollArea>

                {/* Typing */}
                {activeTyping.length > 0 && <div className="px-5 py-1"><span className="text-xs text-[#008080] animate-pulse">{activeTyping.join(', ')} typing...</span></div>}

                {/* Input */}
                <div className="p-4 border-t border-slate-200">
                  <input type="file" ref={fileInputRef} className="hidden" onChange={handleFileShare} accept="image/*,.pdf,.doc,.docx,.txt,.csv" data-testid="file-input" />
                  <div className="flex items-center gap-2 border border-slate-200 rounded-lg px-4 py-2.5 focus-within:ring-2 focus-within:ring-[#008080]/20 focus-within:border-[#008080] transition-all bg-white shadow-sm">
                    <button onClick={() => fileInputRef.current?.click()} disabled={uploading} className="p-1 text-slate-400 hover:text-[#008080] rounded transition-colors" data-testid="attach-file-btn">
                      {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Paperclip className="w-4 h-4" />}
                    </button>
                    <input value={messageText} onChange={e => { setMessageText(e.target.value); handleTyping(); }} onKeyDown={handleKeyDown}
                      placeholder={`Message ${activeChannel.channel_type === 'dm' ? activeChannel.dm_partner?.name || '' : '#' + activeChannel.name}`}
                      className="flex-1 text-sm bg-transparent outline-none text-slate-800 placeholder:text-slate-400" data-testid="message-input" />
                    <button onClick={handleSend} disabled={!messageText.trim() || sending}
                      className={`p-2 rounded-md transition-colors ${messageText.trim() ? 'text-white hover:opacity-90' : 'text-slate-300'}`}
                      style={messageText.trim() ? { background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` } : {}}
                      data-testid="send-message-btn">
                      <Send className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Thread Panel */}
              {showThread && <ThreadPanel messageId={showThread} onClose={() => setShowThread(null)} token={token} />}

              {/* AI Productivity Panel */}
              {showAiPanel && activeChannel && <AiProductivityPanel channelId={activeChannel.id} channelName={activeChannel.name} onClose={() => setShowAiPanel(false)} token={token} />}

              {/* AI Chat Panel */}
              {showAiChat && activeChannel && <AiChatPanel channelId={activeChannel.id} onClose={() => setShowAiChat(false)} token={token} />}

              {/* Alerts & Decision Cards Panel */}
              {showAlerts && <AlertsPanel onClose={() => setShowAlerts(false)} token={token} />}

              {/* Knowledge Graph Panel */}
              {showKnowledgeGraph && <KnowledgeGraphPanel onClose={() => setShowKnowledgeGraph(false)} token={token} />}

              {/* Bottleneck Panel */}
              {showBottlenecks && <BottleneckPanel onClose={() => setShowBottlenecks(false)} token={token} />}

              {/* Members Panel */}
              {showMembers && <MembersPanel channelId={activeChannel.id} onClose={() => setShowMembers(false)} token={token} />}
            </div>
          </>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-center px-6 bg-slate-50">
            <div className="w-20 h-20 rounded-lg bg-slate-100 flex items-center justify-center mb-5"><MessageCircle className="w-10 h-10 text-slate-300" /></div>
            <h2 className="text-xl font-semibold text-slate-900 mb-2">LUMI</h2>
            <p className="text-slate-400 text-sm max-w-xs">{t('lumi.welcomeMessage') || 'Select a channel to start chatting, or create a new one.'}</p>
            <Button onClick={() => setShowCreateModal(true)} className="mt-4 bg-[#008080] hover:bg-[#006666] text-white rounded-md" data-testid="create-first-channel">
              <Plus className="w-4 h-4 mr-2" />{t('lumi.createChannel') || 'Create Channel'}
            </Button>
          </div>
        )}
      </div>

      {showCreateModal && <CreateChannelModal onClose={() => setShowCreateModal(false)} onCreated={(ch) => { setChannels(prev => [ch, ...prev]); setActiveChannel(ch); setShowCreateModal(false); setMobileSidebar(false); }} token={token} />}
      {showNewDmModal && <NewDmModal onClose={() => setShowNewDmModal(false)} onSelect={handleStartDm} token={token} />}

      {/* Command Bar (Ctrl+K) */}
      <CommandBar isOpen={showCommandBar} onClose={() => setShowCommandBar(false)} token={token}
        onNavigate={(item) => {
          if (item.type === 'channel') {
            const ch = channels.find(c => c.id === item.id) || dms.find(d => d.id === item.id);
            if (ch) { setActiveChannel(ch); setMobileSidebar(false); }
          } else if (item.type === 'dm') {
            const dm = dms.find(d => d.id === item.id);
            if (dm) { setActiveChannel(dm); setMobileSidebar(false); }
          }
        }}
        onAction={(cmd) => {
          if (cmd === 'create_channel') setShowCreateModal(true);
          else if (cmd === 'generate_report') { if (activeChannel) { setShowAiPanel(true); } }
          else if (cmd === 'analyze_sentiment') { if (activeChannel) { setShowAiPanel(true); } }
          else if (cmd === 'extract_tasks') { if (activeChannel) { setShowAiPanel(true); } }
          else if (cmd === 'check_anomalies') { setShowAlerts(true); }
        }}
      />
    </div>
  );
};

// ============== LUMI Login ==============
const LumiLogin = ({ onLogin }) => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPw, setShowPw] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const res = await fetch(`${API}/api/auth/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password }) });
      if (res.ok) {
        const data = await res.json();
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('karau_user', JSON.stringify(data.user));
        onLogin(data.user);
        toast.success('Welcome to LUMI!');
      } else { const err = await res.json(); toast.error(err.detail || 'Login failed'); }
    } catch (e) { toast.error('Connection error'); }
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen flex" style={{ fontFamily: "'Inter', -apple-system, sans-serif" }}>
      <Toaster position="top-right" richColors />
      {/* Left - Image */}
      <div className="hidden lg:flex lg:w-1/2 bg-[#36454F] items-center justify-center relative overflow-hidden">
        <img src="https://images.unsplash.com/photo-1719667052333-1cba4797fd85?w=1200&q=80" alt="" className="absolute inset-0 w-full h-full object-cover opacity-20" />
        <div className="relative z-10 text-center px-12">
          <div className="w-16 h-16 mx-auto rounded-lg flex items-center justify-center mb-6 shadow-lg" style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` }}>
            <MessageCircle className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-3">LUMI</h1>
          <p className="text-lg text-slate-200">Enterprise Team Messenger</p>
          <p className="text-sm text-slate-300 mt-2 max-w-sm">Secure, domain-protected team communication for the modern workplace.</p>
        </div>
      </div>
      {/* Right - Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-slate-50">
        <div className="w-full max-w-sm">
          <div className="lg:hidden flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` }}><MessageCircle className="w-5 h-5 text-white" /></div>
            <span className="text-xl font-bold text-slate-900">LUMI</span>
          </div>
          <h2 className="text-2xl font-semibold text-slate-900 mb-1">{t('lumi.signIn') || 'Sign in to LUMI'}</h2>
          <p className="text-sm text-slate-500 mb-6">{t('lumi.tagline') || 'Team messaging for the KARAU ecosystem'}</p>
          <form onSubmit={handleLogin} className="space-y-4">
            <Input value={email} onChange={e => setEmail(e.target.value)} type="email" placeholder="Email"
              className="h-11 border-slate-200 rounded-md focus:ring-[#008080]/20 focus:border-[#008080]" data-testid="lumi-email" />
            <div className="relative">
              <Input value={password} onChange={e => setPassword(e.target.value)} type={showPw ? 'text' : 'password'} placeholder="Password"
                className="h-11 border-slate-200 rounded-md pr-10 focus:ring-[#008080]/20 focus:border-[#008080]" data-testid="lumi-password" />
              <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            <Button type="submit" disabled={isLoading || !email || !password}
              className="w-full h-11 text-white rounded-md font-medium hover:opacity-90 transition-opacity"
              style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` }}
              data-testid="lumi-login-btn">
              {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Sign in'}
            </Button>
          </form>
          <div className="mt-6 text-center">
            <button onClick={() => navigate('/')} className="text-sm text-slate-400 hover:text-[#008080] transition-colors" data-testid="back-to-portal">
              {t('lumi.backToPortal') || 'Back to Portal'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LumiMessenger;
