/**
 * LUMI Prestige — Enterprise Team Messenger
 * Refactored: Main container imports sub-components from /components/Lumi/
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast, Toaster } from 'sonner';
import {
  Plus, Send, LogOut, ArrowLeft,
  Users, Search, MessageCircle,
  Loader2, X, Paperclip, UserPlus, User, Phone, Video,
  Building2, Sparkles, Brain, AlertTriangle, Shield,
  Command, Network, Zap, TrendingDown, Bell,
  Smile, Keyboard, ClipboardList, Globe
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useTranslation } from '@/utils/i18n';

import {
  ChannelIcon, StatusDot, MessageBubble, ThreadPanel, MembersPanel,
  AiProductivityPanel, AiChatPanel, AlertsPanel, CommandBar,
  KnowledgeGraphPanel, BottleneckPanel, SimulationPanel,
  NotificationsPanel, CreateChannelModal, NewDmModal, LumiLogin,
  UserProfileModal, RetentionPanel, EmojiPicker,
  ShortcutsPanel, useKeyboardShortcuts,
  AdminAuditPanel, CompliancePanel,
  API, WS_URL, ESY, STATUS_COLORS, STATUS_LABELS
} from '@/components/Lumi';

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
  const [showSimulation, setShowSimulation] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [showRetention, setShowRetention] = useState(false);
  const [showAuditLog, setShowAuditLog] = useState(false);
  const [showCompliance, setShowCompliance] = useState(false);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [userAccentColor, setUserAccentColor] = useState('');
  const [presenceMap, setPresenceMap] = useState({});

  const messagesEndRef = useRef(null);
  const wsRef = useRef(null);
  const typingTimeoutRef = useRef(null);
  const fileInputRef = useRef(null);
  const token = localStorage.getItem('token');

  // Handle Google SSO callback
  useEffect(() => {
    const hash = window.location.hash;
    if (hash && hash.includes('session_id=')) {
      const sessionId = hash.split('session_id=')[1]?.split('&')[0];
      if (sessionId) {
        (async () => {
          try {
            const res = await fetch(`${API}/api/auth/google/session`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ session_id: sessionId })
            });
            if (res.ok) {
              const data = await res.json();
              localStorage.setItem('token', data.access_token);
              localStorage.setItem('karau_user', JSON.stringify(data.user));
              setUser(data.user);
              toast.success('Welcome to LUMI!');
              // Clean hash from URL
              window.history.replaceState(null, '', window.location.pathname);
            }
          } catch (e) {
            toast.error('SSO login failed');
          }
          setIsLoading(false);
        })();
        return;
      }
    }
    // Normal auth check
    const savedUser = localStorage.getItem('karau_user');
    if (savedUser && token) setUser(JSON.parse(savedUser));
    setIsLoading(false);
  }, []);

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
    try { const res = await fetch(`${API}/api/lumi/dm`, { headers: { 'Authorization': `Bearer ${token}` } }); if (res.ok) setDms((await res.json()).dms || []); } catch (e) {}
  }, [token]);

  const loadUnreadCounts = useCallback(async () => {
    if (!token) return;
    try { const res = await fetch(`${API}/api/lumi/unread-counts`, { headers: { 'Authorization': `Bearer ${token}` } }); if (res.ok) setUnreadCounts((await res.json()).unread || {}); } catch (e) {}
  }, [token]);

  const loadPresence = useCallback(async () => {
    if (!token) return;
    try { const res = await fetch(`${API}/api/lumi/presence/all`, { headers: { 'Authorization': `Bearer ${token}` } }); if (res.ok) setPresenceMap((await res.json()).presence || {}); } catch (e) {}
  }, [token]);

  useEffect(() => {
    if (user) { loadChannels(); loadDms(); loadUnreadCounts(); loadPresence(); }
  }, [user, loadChannels, loadDms, loadUnreadCounts, loadPresence]);

  // Mark as read
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
        } else if (msg.type === 'message_edited') {
          setMessages(prev => prev.map(m => m.id === msg.data.message_id ? { ...m, content: msg.data.content, edited: true, edited_at: msg.data.edited_at } : m));
        } else if (msg.type === 'message_deleted') {
          setMessages(prev => prev.filter(m => m.id !== msg.data.message_id));
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

  // Keyboard shortcuts
  useKeyboardShortcuts({
    command_bar: () => setShowCommandBar(true),
    emoji_picker: () => setShowEmojiPicker(prev => !prev),
    new_channel: () => setShowCreateModal(true),
    new_dm: () => setShowNewDmModal(true),
    shortcuts: () => setShowShortcuts(prev => !prev),
    ai_panel: () => { closeAllPanels(); setShowAiPanel(prev => !prev); },
    notifications: () => { closeAllPanels(); setShowNotifications(prev => !prev); },
    members: () => setShowMembers(prev => !prev),
    profile: () => setShowProfile(true),
    search: () => document.querySelector('[data-testid="search-channels"]')?.focus(),
  });

  // Google Calendar status sync (every 5 minutes for Google SSO users)
  useEffect(() => {
    if (!user || !token) return;
    const syncCalendar = async () => {
      try {
        await fetch(`${API}/api/lumi/calendar/sync`, { method: 'POST', headers: { Authorization: `Bearer ${token}` } });
      } catch (e) {}
    };
    syncCalendar();
    const interval = setInterval(syncCalendar, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [user, token]);

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

  const handleEditMessage = async (messageId, newContent) => {
    try {
      const res = await fetch(`${API}/api/lumi/messages/${messageId}`, { method: 'PUT', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }, body: JSON.stringify({ content: newContent }) });
      if (res.ok) { setMessages(prev => prev.map(m => m.id === messageId ? { ...m, content: newContent, edited: true } : m)); toast.success('Message edited'); }
      else { const err = await res.json(); toast.error(err.detail || 'Edit failed'); }
    } catch (e) { toast.error('Edit failed'); }
  };

  const handleDeleteMessage = async (messageId) => {
    try {
      const res = await fetch(`${API}/api/lumi/messages/${messageId}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) { setMessages(prev => prev.filter(m => m.id !== messageId)); toast.success('Message deleted'); }
      else { const err = await res.json(); toast.error(err.detail || 'Delete failed'); }
    } catch (e) { toast.error('Delete failed'); }
  };

  const handleStartCall = async (callType = 'voice') => {
    if (!activeChannel) return;
    const recipientId = activeChannel.channel_type === 'dm' ? activeChannel.dm_partner?.user_id : null;
    try {
      const res = await fetch(`${API}/api/lumi/voice/call`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ recipient_id: recipientId || 'channel', type: callType, channel_id: activeChannel.id })
      });
      if (res.ok) {
        const call = await res.json();
        toast.success(`${callType === 'video' ? 'Video' : 'Voice'} call started — ID: ${call.id}`);
        // Open AI KARAU meeting room in new tab
        window.open(`${window.location.origin}/karau-meet?call=${call.id}`, '_blank');
      }
    } catch (e) { toast.error('Call failed to connect'); }
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
  const handleEmojiSelect = (emoji) => { setMessageText(prev => prev + emoji); setShowEmojiPicker(false); };
  const handleTyping = () => {
    if (!activeChannel || !wsRef.current || typingTimeoutRef.current) return;
    try { wsRef.current.send(JSON.stringify({ type: 'typing', channel_id: activeChannel.id })); } catch (e) {}
    typingTimeoutRef.current = setTimeout(() => { typingTimeoutRef.current = null; }, 2000);
  };

  const filteredChannels = channels.filter(ch => ch.name.toLowerCase().includes(searchQuery.toLowerCase()));
  const activeTyping = activeChannel ? Object.values(typingUsers[activeChannel.id] || {}).filter(n => n !== user?.name) : [];

  const closeAllPanels = () => { setShowAiChat(false); setShowAlerts(false); setShowAiPanel(false); setShowKnowledgeGraph(false); setShowBottlenecks(false); setShowSimulation(false); setShowNotifications(false); };

  if (isLoading) return <div className="min-h-screen bg-slate-50 flex items-center justify-center"><Loader2 className="w-8 h-8 text-[#008080] animate-spin" /></div>;
  if (!user) return <LumiLogin onLogin={setUser} />;

  return (
    <div className="h-screen flex bg-slate-50 overflow-hidden" style={{ fontFamily: "'Inter', -apple-system, sans-serif" }}>
      <Toaster position="top-right" richColors />

      {/* Sidebar */}
      <div className={`${mobileSidebar ? 'flex' : 'hidden'} md:flex flex-col w-full md:w-[280px] bg-[#36454F] flex-shrink-0`}>
        <div className="h-14 flex items-center justify-between px-4 border-b border-white/10">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-md flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` }}><MessageCircle className="w-4.5 h-4.5 text-white" /></div>
            <span className="font-bold text-sm text-white tracking-wide">LUMI</span>
          </div>
          <button onClick={() => navigate('/')} className="p-2 text-slate-300 hover:text-white hover:bg-white/10 rounded-md transition-colors" data-testid="back-to-karau"><ArrowLeft className="w-4 h-4" /></button>
        </div>

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

        <ScrollArea className="flex-1 py-2">
          <div className="px-3">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-[11px] font-semibold text-slate-300/70 uppercase tracking-widest">Channels</span>
              <button onClick={() => setShowCreateModal(true)} className="p-1 text-slate-300 hover:text-white hover:bg-white/10 rounded transition-colors" data-testid="add-channel-btn"><Plus className="w-3.5 h-3.5" /></button>
            </div>
            {filteredChannels.map(ch => (
              <button key={ch.id} onClick={() => { setActiveChannel(ch); setMobileSidebar(false); setShowThread(null); setShowMembers(false); setShowAiPanel(false); }}
                className={`w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md transition-colors mb-0.5 ${activeChannel?.id === ch.id ? 'bg-white/15 text-white' : 'text-slate-300 hover:bg-white/10 hover:text-white'}`} data-testid={`channel-${ch.id}`}>
                <ChannelIcon type={ch.channel_type} /><span className="flex-1 text-sm truncate text-left">{ch.name}</span>
                {unreadCounts[ch.id] > 0 && <span className="min-w-[18px] h-[18px] flex items-center justify-center rounded-full text-[9px] font-bold text-white" style={{ backgroundColor: ESY.pink }} data-testid={`unread-${ch.id}`}>{unreadCounts[ch.id]}</span>}
              </button>
            ))}

            {discoverChannels.length > 0 && (<>
              <div className="flex items-center mt-3 mb-1.5"><span className="text-[11px] font-semibold text-slate-300/70 uppercase tracking-widest">Discover</span></div>
              {discoverChannels.map(ch => (
                <button key={ch.id} onClick={() => handleJoinChannel(ch)} className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md text-slate-400 hover:bg-white/10 hover:text-white mb-0.5" data-testid={`discover-${ch.id}`}>
                  <ChannelIcon type={ch.channel_type} /><span className="flex-1 text-sm truncate text-left">{ch.name}</span><Plus className="w-3 h-3 opacity-70" />
                </button>
              ))}
            </>)}

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
                  className={`w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md transition-colors mb-0.5 ${activeChannel?.id === dm.id ? 'bg-white/15 text-white' : 'text-slate-300 hover:bg-white/10 hover:text-white'}`} data-testid={`dm-${dm.id}`}>
                  <div className="relative">
                    <div className="w-6 h-6 rounded-full bg-slate-500 flex items-center justify-center text-[9px] font-semibold text-white">{init}</div>
                    <span className={`absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full ring-1 ring-[#36454F] ${STATUS_COLORS[st]}`} />
                  </div>
                  <span className="flex-1 text-sm truncate text-left">{partner.name || partner.email || 'User'}</span>
                  {unreadCounts[dm.id] > 0 && <span className="min-w-[16px] h-[16px] flex items-center justify-center rounded-full text-[8px] font-bold text-white" style={{ backgroundColor: ESY.pink }} data-testid={`unread-dm-${dm.id}`}>{unreadCounts[dm.id]}</span>}
                </button>
              );
            })}
            {dms.length === 0 && <p className="text-[11px] text-slate-300 px-2.5 py-1">No conversations yet</p>}
          </div>
        </ScrollArea>

        <div className="p-3 border-t border-white/10">
          <div className="flex items-center gap-3">
            <button onClick={() => setShowProfile(true)} className="relative group" data-testid="open-profile-btn" title="My Profile">
              <div className="w-8 h-8 rounded-full flex items-center justify-center group-hover:ring-2 group-hover:ring-white/30 transition-all" style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` }}><span className="text-xs font-semibold text-white">{(user?.name || user?.email || '?')[0].toUpperCase()}</span></div>
              <span className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full ring-2 ring-[#36454F] bg-emerald-500" />
            </button>
            <button onClick={() => setShowProfile(true)} className="flex-1 min-w-0 text-left hover:opacity-80 transition-opacity" data-testid="open-profile-name">
              <p className="text-sm font-medium text-white truncate">{user?.name || 'User'}</p>
              <p className="text-[10px] text-slate-300">View Profile</p>
            </button>
            <button onClick={() => { localStorage.removeItem('token'); localStorage.removeItem('karau_user'); setUser(null); navigate('/'); }} className="p-1.5 text-slate-300 hover:text-red-400 hover:bg-red-500/10 rounded-md" data-testid="lumi-logout"><LogOut className="w-3.5 h-3.5" /></button>
          </div>
        </div>

        <div className="px-3 pb-3 space-y-2">
          <button onClick={() => setShowRetention(true)} className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-md transition-colors group" data-testid="open-retention-btn">
            <Shield className="w-3.5 h-3.5 group-hover:text-white" style={{ color: ESY.deepRed }} />
            <span className="text-xs font-medium text-slate-300 group-hover:text-white">Retention & Holds</span>
          </button>
          <button onClick={() => setShowAuditLog(true)} className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-md transition-colors group" data-testid="open-audit-btn">
            <ClipboardList className="w-3.5 h-3.5 group-hover:text-white" style={{ color: ESY.turquoise }} />
            <span className="text-xs font-medium text-slate-300 group-hover:text-white">Audit Log</span>
          </button>
          <button onClick={() => setShowCompliance(true)} className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-md transition-colors group" data-testid="open-compliance-btn">
            <Globe className="w-3.5 h-3.5 group-hover:text-white" style={{ color: '#00B894' }} />
            <span className="text-xs font-medium text-slate-300 group-hover:text-white">Privacy & Compliance</span>
          </button>
          <button onClick={() => setShowShortcuts(true)} className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-md transition-colors group" data-testid="open-shortcuts-btn">
            <Keyboard className="w-3.5 h-3.5 text-slate-400 group-hover:text-white" />
            <span className="text-xs font-medium text-slate-300 group-hover:text-white">Shortcuts</span>
          </button>
          <button onClick={() => navigate('/karau-meet')} className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-md transition-colors group" data-testid="switch-to-karau-footer">
            <Building2 className="w-3.5 h-3.5 group-hover:text-white" style={{ color: ESY.turquoise }} />
            <span className="text-xs font-medium text-slate-300 group-hover:text-white">Switch to AI KARAU</span>
          </button>
        </div>
      </div>

      {/* Chat Area */}
      <div className={`${!mobileSidebar ? 'flex' : 'hidden'} md:flex flex-col flex-1 min-w-0 bg-white`}>
        {activeChannel ? (<>
          <div className="h-14 flex items-center justify-between px-5 border-b border-slate-200 flex-shrink-0 bg-white">
            <div className="flex items-center gap-3">
              <button className="md:hidden p-2 text-slate-500 hover:text-slate-900" onClick={() => setMobileSidebar(true)}><ArrowLeft className="w-4 h-4" /></button>
              {activeChannel.channel_type === 'dm' ? (<>
                <div className="relative"><div className="w-9 h-9 rounded-full bg-[#36454F] flex items-center justify-center"><User className="w-4 h-4 text-white" /></div><StatusDot status={presenceMap[activeChannel.dm_partner?.user_id] || 'offline'} /></div>
                <div><h2 className="text-sm font-semibold text-slate-900">{activeChannel.dm_partner?.name || activeChannel.name}</h2><p className="text-[11px] text-slate-500">{STATUS_LABELS[presenceMap[activeChannel.dm_partner?.user_id]] || 'Offline'}</p></div>
              </>) : (<>
                <div className="w-9 h-9 rounded-md bg-slate-100 flex items-center justify-center text-slate-600"><ChannelIcon type={activeChannel.channel_type} /></div>
                <div><h2 className="text-sm font-semibold text-slate-900">#{activeChannel.name}</h2><p className="text-[11px] text-slate-500">{activeChannel.members?.length || 0} members</p></div>
              </>)}
            </div>
            <div className="flex items-center gap-1">
              {activeChannel.channel_type === 'dm' && (
                <>
                  <button onClick={() => handleStartCall('voice')} className="p-2 text-slate-500 hover:text-[#008080] hover:bg-[#008080]/5 rounded-md transition-colors" data-testid="voice-call-btn" title="Voice Call"><Phone className="w-4 h-4" /></button>
                  <button onClick={() => handleStartCall('video')} className="p-2 text-slate-500 hover:text-[#008080] hover:bg-[#008080]/5 rounded-md transition-colors" data-testid="video-call-btn" title="Video Call"><Video className="w-4 h-4" /></button>
                </>
              )}
              <button onClick={() => setShowCommandBar(true)} className="p-2 rounded-md text-slate-500 hover:text-slate-700 hover:bg-slate-100 transition-colors" data-testid="command-bar-btn" title="Command Bar (Ctrl+K)"><Command className="w-4 h-4" /></button>
              <button onClick={() => { closeAllPanels(); setShowAiChat(!showAiChat); }} className={`p-2 rounded-md transition-colors ${showAiChat ? 'bg-[#00CEC9]/10' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100'}`} style={showAiChat ? { color: ESY.turquoise } : {}} data-testid="ai-chat-btn" title="Ask AI"><Sparkles className="w-4 h-4" /></button>
              <button onClick={() => { closeAllPanels(); setShowAlerts(!showAlerts); }} className={`p-2 rounded-md transition-colors ${showAlerts ? 'bg-[#D63031]/10' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100'}`} style={showAlerts ? { color: ESY.deepRed } : {}} data-testid="alerts-btn" title="Alerts & Decisions"><AlertTriangle className="w-4 h-4" /></button>
              <button onClick={() => { closeAllPanels(); setShowKnowledgeGraph(!showKnowledgeGraph); }} className={`p-2 rounded-md transition-colors ${showKnowledgeGraph ? 'bg-[#00CEC9]/10' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100'}`} style={showKnowledgeGraph ? { color: ESY.turquoise } : {}} data-testid="knowledge-graph-btn" title="Knowledge Graph"><Network className="w-4 h-4" /></button>
              <button onClick={() => { closeAllPanels(); setShowBottlenecks(!showBottlenecks); }} className={`p-2 rounded-md transition-colors ${showBottlenecks ? 'bg-[#D63031]/10' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100'}`} style={showBottlenecks ? { color: ESY.deepRed } : {}} data-testid="bottleneck-btn" title="Bottlenecks"><TrendingDown className="w-4 h-4" /></button>
              <button onClick={() => { closeAllPanels(); setShowSimulation(!showSimulation); }} className={`p-2 rounded-md transition-colors ${showSimulation ? 'bg-[#E84393]/10' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100'}`} style={showSimulation ? { color: ESY.pink } : {}} data-testid="simulation-btn" title="What-If Simulator"><Zap className="w-4 h-4" /></button>
              <button onClick={() => { closeAllPanels(); setShowNotifications(!showNotifications); }} className={`p-2 rounded-md transition-colors relative ${showNotifications ? 'bg-[#E84393]/10' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100'}`} style={showNotifications ? { color: ESY.pink } : {}} data-testid="notifications-btn" title="Smart Notifications"><Bell className="w-3.5 h-3.5" /><span className="absolute top-1 right-1 w-1.5 h-1.5 rounded-full" style={{ backgroundColor: ESY.deepRed }} /></button>
              <button onClick={() => { closeAllPanels(); setShowAiPanel(!showAiPanel); }} className={`p-2 rounded-md transition-colors ${showAiPanel ? 'text-[#008080] bg-[#008080]/5' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100'}`} data-testid="ai-panel-btn" title="AI Insights"><Brain className="w-4 h-4" /></button>
              <button onClick={() => setShowMembers(!showMembers)} className={`p-2 rounded-md transition-colors ${showMembers ? 'text-[#008080] bg-[#008080]/5' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100'}`} data-testid="channel-members-btn"><Users className="w-4 h-4" /></button>
            </div>
          </div>

          <div className="flex flex-1 overflow-hidden">
            <div className="flex-1 flex flex-col min-w-0">
              <ScrollArea className="flex-1 py-3">
                {messages.length === 0 && (
                  <div className="flex flex-col items-center justify-center h-full text-center px-6">
                    <div className="w-16 h-16 rounded-lg bg-slate-100 flex items-center justify-center mb-4"><MessageCircle className="w-8 h-8 text-slate-300" /></div>
                    <p className="text-slate-500 text-sm">{t('lumi.noMessages') || 'No messages yet'}</p>
                  </div>
                )}
                {messages.filter(m => !m.thread_parent_id).map((msg, i, arr) => {
                  const prevSameSender = i > 0 && arr[i - 1].sender_id === msg.sender_id && arr[i - 1].type !== 'system';
                  return <MessageBubble key={msg.id} msg={msg} isOwn={msg.sender_id === user?.user_id} prevSameSender={prevSameSender} onReact={handleReact} onThread={(id) => setShowThread(id)} onEdit={handleEditMessage} onDelete={handleDeleteMessage} token={token} />;
                })}
                <div ref={messagesEndRef} />
              </ScrollArea>

              {activeTyping.length > 0 && <div className="px-5 py-1"><span className="text-xs text-[#006666] font-medium animate-pulse">{activeTyping.join(', ')} typing...</span></div>}

              <div className="p-4 border-t border-slate-200">
                <input type="file" ref={fileInputRef} className="hidden" onChange={handleFileShare} accept="image/*,.pdf,.doc,.docx,.txt,.csv" data-testid="file-input" />
                <div className="relative flex items-center gap-2 border border-slate-200 rounded-lg px-4 py-2.5 focus-within:ring-2 focus-within:ring-[#008080]/20 focus-within:border-[#008080] transition-all bg-white shadow-sm">
                  <button onClick={() => fileInputRef.current?.click()} disabled={uploading} className="p-1 text-slate-500 hover:text-[#008080] rounded transition-colors" data-testid="attach-file-btn">
                    {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Paperclip className="w-4 h-4" />}
                  </button>
                  <div className="relative">
                    <button onClick={() => setShowEmojiPicker(!showEmojiPicker)} className={`p-1 rounded transition-colors ${showEmojiPicker ? 'text-[#008080] bg-[#008080]/10' : 'text-slate-500 hover:text-[#008080]'}`} data-testid="emoji-picker-btn">
                      <Smile className="w-4 h-4" />
                    </button>
                    <EmojiPicker isOpen={showEmojiPicker} onClose={() => setShowEmojiPicker(false)} onSelect={handleEmojiSelect} position="above" />
                  </div>
                  <input value={messageText} onChange={e => { setMessageText(e.target.value); handleTyping(); }} onKeyDown={handleKeyDown}
                    placeholder={`Message ${activeChannel.channel_type === 'dm' ? activeChannel.dm_partner?.name || '' : '#' + activeChannel.name}`}
                    className="flex-1 text-sm bg-transparent outline-none text-slate-900 placeholder:text-slate-500" data-testid="message-input" />
                  <button onClick={handleSend} disabled={!messageText.trim() || sending}
                    className={`p-2 rounded-md transition-colors ${messageText.trim() ? 'text-white hover:opacity-90' : 'text-slate-300'}`}
                    style={messageText.trim() ? { background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` } : {}}
                    data-testid="send-message-btn"><Send className="w-4 h-4" /></button>
                </div>
              </div>
            </div>

            {showThread && <ThreadPanel messageId={showThread} onClose={() => setShowThread(null)} token={token} />}
            {showAiPanel && activeChannel && <AiProductivityPanel channelId={activeChannel.id} channelName={activeChannel.name} onClose={() => setShowAiPanel(false)} token={token} />}
            {showAiChat && activeChannel && <AiChatPanel channelId={activeChannel.id} onClose={() => setShowAiChat(false)} token={token} />}
            {showAlerts && <AlertsPanel onClose={() => setShowAlerts(false)} token={token} />}
            {showKnowledgeGraph && <KnowledgeGraphPanel onClose={() => setShowKnowledgeGraph(false)} token={token} />}
            {showBottlenecks && <BottleneckPanel onClose={() => setShowBottlenecks(false)} token={token} />}
            {showSimulation && <SimulationPanel onClose={() => setShowSimulation(false)} token={token} />}
            {showNotifications && <NotificationsPanel onClose={() => setShowNotifications(false)} token={token} onNavigate={(item) => { const ch = channels.find(c => c.id === item.id) || dms.find(d => d.id === item.id); if (ch) { setActiveChannel(ch); setMobileSidebar(false); } }} />}
            {showMembers && <MembersPanel channelId={activeChannel.id} onClose={() => setShowMembers(false)} token={token} />}
          </div>
        </>) : (
          <div className="flex-1 flex flex-col items-center justify-center text-center px-6 bg-slate-50">
            <div className="w-20 h-20 rounded-lg bg-slate-100 flex items-center justify-center mb-5"><MessageCircle className="w-10 h-10 text-slate-300" /></div>
            <h2 className="text-xl font-semibold text-slate-900 mb-2">LUMI</h2>
            <p className="text-slate-500 text-sm max-w-xs">{t('lumi.welcomeMessage') || 'Select a channel to start chatting, or create a new one.'}</p>
            <Button onClick={() => setShowCreateModal(true)} className="mt-4 bg-[#008080] hover:bg-[#006666] text-white rounded-md" data-testid="create-first-channel">
              <Plus className="w-4 h-4 mr-2" />{t('lumi.createChannel') || 'Create Channel'}
            </Button>
          </div>
        )}
      </div>

      {showCreateModal && <CreateChannelModal onClose={() => setShowCreateModal(false)} onCreated={(ch) => { setChannels(prev => [ch, ...prev]); setActiveChannel(ch); setShowCreateModal(false); setMobileSidebar(false); }} token={token} />}
      {showNewDmModal && <NewDmModal onClose={() => setShowNewDmModal(false)} onSelect={handleStartDm} token={token} />}
      {showProfile && <UserProfileModal onClose={() => setShowProfile(false)} token={token} onStatusChange={(s) => {}} onThemeChange={(c) => setUserAccentColor(c)} />}
      {showRetention && <RetentionPanel onClose={() => setShowRetention(false)} token={token} />}
      {showAuditLog && <AdminAuditPanel isOpen={showAuditLog} onClose={() => setShowAuditLog(false)} token={token} />}
      {showCompliance && <CompliancePanel isOpen={showCompliance} onClose={() => setShowCompliance(false)} token={token} />}
      <ShortcutsPanel isOpen={showShortcuts} onClose={() => setShowShortcuts(false)} />

      <CommandBar isOpen={showCommandBar} onClose={() => setShowCommandBar(false)} token={token}
        onNavigate={(item) => {
          if (item.type === 'channel') { const ch = channels.find(c => c.id === item.id) || dms.find(d => d.id === item.id); if (ch) { setActiveChannel(ch); setMobileSidebar(false); } }
          else if (item.type === 'dm') { const dm = dms.find(d => d.id === item.id); if (dm) { setActiveChannel(dm); setMobileSidebar(false); } }
        }}
        onAction={(cmd) => {
          if (cmd === 'create_channel') setShowCreateModal(true);
          else if (cmd === 'generate_report' || cmd === 'analyze_sentiment' || cmd === 'extract_tasks') { if (activeChannel) setShowAiPanel(true); }
          else if (cmd === 'check_anomalies') setShowAlerts(true);
        }}
      />
    </div>
  );
};

export default LumiMessenger;
