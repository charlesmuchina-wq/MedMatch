/**
 * LUMI Messenger - Standalone Real-time Channel Messaging
 * Dark-themed, modern chat interface for the KARAU ecosystem
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast, Toaster } from 'sonner';
import {
  Hash, Lock, Megaphone, Plus, Send, LogOut, ArrowLeft,
  Users, Search, Settings, ChevronDown, Circle, MessageCircle,
  Loader2, X, MoreVertical, Smile, Paperclip, Eye, EyeOff, UserPlus, User
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useTranslation } from '@/utils/i18n';
import GlobalLanguageSelector from '@/components/GlobalLanguageSelector';

const API = process.env.REACT_APP_BACKEND_URL;
const WS_URL = API.replace('https://', 'wss://').replace('http://', 'ws://');

// ============== Channel Icon Helper ==============
const ChannelIcon = ({ type, size = 16 }) => {
  const cls = `w-${size === 16 ? 4 : 3.5} h-${size === 16 ? 4 : 3.5}`;
  if (type === 'announcement') return <Megaphone className={cls} />;
  if (type === 'project') return <Hash className={cls} />;
  return <Hash className={cls} />;
};

// ============== Message Component ==============
const MessageBubble = ({ msg, isOwn, prevSameSender, onReact }) => {
  const time = new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const [showReactPicker, setShowReactPicker] = useState(false);
  const quickEmojis = ['👍', '❤️', '😂', '🎉', '🔥', '👀'];

  if (msg.type === 'system') {
    return (
      <div className="flex justify-center my-3" data-testid={`msg-system-${msg.id}`}>
        <span className="text-xs text-slate-600 bg-white/[0.03] px-3 py-1 rounded-full">
          {msg.content}
        </span>
      </div>
    );
  }

  const initials = (msg.sender_name || '?').split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase();
  const colors = ['from-violet-600 to-purple-600', 'from-teal-600 to-cyan-600', 'from-amber-600 to-orange-600', 'from-rose-600 to-pink-600', 'from-blue-600 to-indigo-600'];
  const colorIdx = (msg.sender_id || '').split('').reduce((a, c) => a + c.charCodeAt(0), 0) % colors.length;
  const reactions = msg.reactions || {};

  return (
    <div className={`group flex gap-3 px-5 py-0.5 hover:bg-white/[0.02] ${!prevSameSender ? 'mt-3' : 'mt-0'}`} data-testid={`msg-${msg.id}`}>
      <div className="w-9 flex-shrink-0">
        {!prevSameSender && (
          <div className={`w-9 h-9 rounded-xl bg-gradient-to-br ${colors[colorIdx]} flex items-center justify-center shadow-lg`}>
            <span className="text-[11px] font-bold text-white">{initials}</span>
          </div>
        )}
      </div>
      <div className="flex-1 min-w-0">
        {!prevSameSender && (
          <div className="flex items-baseline gap-2 mb-0.5">
            <span className="text-sm font-semibold text-white">{msg.sender_name}</span>
            <span className="text-[10px] text-slate-600">{time}</span>
          </div>
        )}
        <p className="text-sm text-slate-300 leading-relaxed break-words">{msg.content}</p>

        {/* Reactions display */}
        {Object.keys(reactions).length > 0 && (
          <div className="flex flex-wrap gap-1 mt-1">
            {Object.entries(reactions).map(([emoji, users]) => (
              <button key={emoji} onClick={() => onReact && onReact(msg.id, emoji)}
                className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-xs border transition-all ${
                  users.includes('self') ? 'bg-violet-600/15 border-violet-500/30 text-violet-300' : 'bg-white/[0.03] border-white/[0.06] text-slate-400 hover:bg-white/[0.06]'
                }`} data-testid={`reaction-${emoji}-${msg.id}`}>
                <span>{emoji}</span>
                <span className="text-[10px]">{users.length}</span>
              </button>
            ))}
          </div>
        )}

        {/* Quick react button (visible on hover) */}
        <div className="relative">
          <button onClick={() => setShowReactPicker(!showReactPicker)}
            className="opacity-0 group-hover:opacity-100 absolute -top-5 right-0 p-1 text-slate-700 hover:text-white hover:bg-white/[0.06] rounded-lg transition-all"
            data-testid={`react-btn-${msg.id}`}>
            <Smile className="w-3.5 h-3.5" />
          </button>
          {showReactPicker && (
            <div className="absolute -top-10 right-0 flex items-center gap-0.5 px-2 py-1 bg-[#1a1b2e] border border-white/[0.1] rounded-xl shadow-xl z-10" data-testid={`react-picker-${msg.id}`}>
              {quickEmojis.map(e => (
                <button key={e} onClick={() => { onReact && onReact(msg.id, e); setShowReactPicker(false); }}
                  className="p-1 hover:bg-white/[0.06] rounded-lg text-sm transition-all">{e}</button>
              ))}
            </div>
          )}
        </div>
      </div>
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
      if (res.ok) {
        const ch = await res.json();
        onCreated(ch);
        toast.success(t('lumi.channelCreated') || 'Channel created');
      }
    } catch (e) {
      toast.error('Failed to create channel');
    }
    setLoading(false);
  };

  const types = [
    { val: 'group', label: t('lumi.typeGroup') || 'Group', icon: Hash },
    { val: 'project', label: t('lumi.typeProject') || 'Project', icon: Hash },
    { val: 'announcement', label: t('lumi.typeAnnouncement') || 'Announcement', icon: Megaphone },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-[#1a1b2e] border border-white/[0.06] rounded-2xl w-full max-w-md p-6 shadow-2xl" onClick={e => e.stopPropagation()} data-testid="create-channel-modal">
        <div className="flex items-center justify-between mb-5">
          <h3 className="text-lg font-bold text-white">{t('lumi.createChannel') || 'Create Channel'}</h3>
          <button onClick={onClose} className="text-slate-500 hover:text-white"><X className="w-5 h-5" /></button>
        </div>
        <div className="space-y-4">
          <div>
            <label className="text-xs font-medium text-slate-400 mb-1.5 block">{t('lumi.channelName') || 'Channel Name'}</label>
            <Input value={name} onChange={e => setName(e.target.value)} placeholder="e.g. project-alpha"
              className="bg-white/[0.04] border-white/[0.08] text-white placeholder:text-slate-600 rounded-xl" data-testid="channel-name-input" />
          </div>
          <div>
            <label className="text-xs font-medium text-slate-400 mb-1.5 block">{t('lumi.description') || 'Description'}</label>
            <Input value={desc} onChange={e => setDesc(e.target.value)} placeholder="What's this channel about?"
              className="bg-white/[0.04] border-white/[0.08] text-white placeholder:text-slate-600 rounded-xl" data-testid="channel-desc-input" />
          </div>
          <div>
            <label className="text-xs font-medium text-slate-400 mb-1.5 block">{t('lumi.channelType') || 'Type'}</label>
            <div className="flex gap-2">
              {types.map(tp => (
                <button key={tp.val} onClick={() => setType(tp.val)}
                  className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-xl text-xs font-medium transition-all ${
                    type === tp.val ? 'bg-violet-600/20 text-violet-300 border border-violet-500/30' : 'bg-white/[0.03] text-slate-500 border border-white/[0.04] hover:bg-white/[0.06]'
                  }`} data-testid={`type-${tp.val}`}>
                  <tp.icon className="w-3.5 h-3.5" />{tp.label}
                </button>
              ))}
            </div>
          </div>
          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" checked={isPrivate} onChange={e => setIsPrivate(e.target.checked)}
              className="w-4 h-4 rounded bg-white/[0.04] border-white/[0.1] text-violet-500" />
            <Lock className="w-3.5 h-3.5 text-slate-500" />
            <span className="text-sm text-slate-400">{t('lumi.privateChannel') || 'Private channel'}</span>
          </label>
        </div>
        <div className="flex gap-3 mt-6">
          <Button variant="ghost" onClick={onClose} className="flex-1 text-slate-400 hover:text-white hover:bg-white/[0.04] rounded-xl">
            {t('common.cancel') || 'Cancel'}
          </Button>
          <Button onClick={handleCreate} disabled={!name.trim() || loading}
            className="flex-1 bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-500 hover:to-purple-500 text-white rounded-xl" data-testid="create-channel-btn">
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : t('common.create') || 'Create'}
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
        const res = await fetch(`${API}/api/lumi/users/search?q=${encodeURIComponent(query)}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setUsers(data.users || []);
        }
      } catch (e) {
        console.error('User search failed:', e);
      }
      setLoading(false);
    };
    const timer = setTimeout(search, 300);
    return () => clearTimeout(timer);
  }, [query, token]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-[#1a1b2e] border border-white/[0.06] rounded-2xl w-full max-w-md p-6 shadow-2xl" onClick={e => e.stopPropagation()} data-testid="new-dm-modal">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-white">{t('lumi.newMessage') || 'New Message'}</h3>
          <button onClick={onClose} className="text-slate-500 hover:text-white"><X className="w-5 h-5" /></button>
        </div>
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-600" />
          <Input value={query} onChange={e => setQuery(e.target.value)}
            placeholder={t('lumi.searchUsers') || 'Search by name or email...'}
            className="pl-10 bg-white/[0.04] border-white/[0.08] text-white placeholder:text-slate-600 rounded-xl"
            autoFocus data-testid="dm-search-input" />
        </div>
        <div className="max-h-64 overflow-y-auto space-y-1">
          {loading && (
            <div className="flex justify-center py-4"><Loader2 className="w-5 h-5 text-violet-400 animate-spin" /></div>
          )}
          {!loading && users.length === 0 && (
            <p className="text-sm text-slate-600 text-center py-4">{t('lumi.noUsersFound') || 'No users found'}</p>
          )}
          {!loading && users.map(u => {
            const initials = (u.name || u.email || '?').split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase();
            return (
              <button key={u.user_id} onClick={() => onSelect(u.user_id)}
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-white/[0.04] transition-all" data-testid={`dm-user-${u.user_id}`}>
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-teal-600/20 to-cyan-600/10 border border-teal-500/10 flex items-center justify-center">
                  <span className="text-xs font-bold text-teal-400">{initials}</span>
                </div>
                <div className="flex-1 text-left">
                  <p className="text-sm font-medium text-white">{u.name || 'Unknown'}</p>
                  <p className="text-[11px] text-slate-600">{u.email}</p>
                </div>
              </button>
            );
          })}
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
  const [onlineUsers, setOnlineUsers] = useState([]);
  const [mobileSidebar, setMobileSidebar] = useState(true);
  const [globalSearch, setGlobalSearch] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showSearchResults, setShowSearchResults] = useState(false);

  const messagesEndRef = useRef(null);
  const wsRef = useRef(null);
  const typingTimeoutRef = useRef(null);
  const token = localStorage.getItem('token');

  // Auth check
  useEffect(() => {
    const savedUser = localStorage.getItem('karau_user');
    if (savedUser && token) {
      setUser(JSON.parse(savedUser));
    }
    setIsLoading(false);
  }, [token]);

  // Load channels
  const loadChannels = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/api/lumi/channels`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setChannels(data.my_channels || []);
        setDiscoverChannels(data.discover || []);
        // Auto-seed if no channels exist
        if ((data.my_channels || []).length === 0 && (data.discover || []).length === 0) {
          await fetch(`${API}/api/lumi/seed`, { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } });
          // Reload
          const res2 = await fetch(`${API}/api/lumi/channels`, { headers: { 'Authorization': `Bearer ${token}` } });
          if (res2.ok) {
            const data2 = await res2.json();
            setChannels(data2.my_channels || []);
            setDiscoverChannels(data2.discover || []);
          }
        }
      }
    } catch (e) {
      console.error('Failed to load channels:', e);
    }
  }, [token]);

  useEffect(() => { if (user) loadChannels(); }, [user, loadChannels]);

  // Load DMs
  const loadDms = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/api/lumi/dm`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setDms(data.dms || []);
      }
    } catch (e) {
      console.error('Failed to load DMs:', e);
    }
  }, [token]);

  useEffect(() => { if (user) loadDms(); }, [user, loadDms]);

  // Start DM with a user
  const handleStartDm = async (recipientId) => {
    try {
      const res = await fetch(`${API}/api/lumi/dm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ recipient_id: recipientId })
      });
      if (res.ok) {
        const dm = await res.json();
        await loadDms();
        setActiveChannel(dm);
        setShowNewDmModal(false);
        setMobileSidebar(false);
      }
    } catch (e) {
      toast.error('Failed to start conversation');
    }
  };

  // WebSocket connection
  useEffect(() => {
    if (!user) return;

    const connectWs = () => {
      const ws = new WebSocket(`${WS_URL}/api/lumi/ws/${user.user_id}`);
      wsRef.current = ws;

      ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.type === 'message') {
          setMessages(prev => {
            if (prev.some(m => m.id === msg.data.id)) return prev;
            return [...prev, msg.data];
          });
          // Update channel and DM lists
          loadChannels();
          loadDms();
        } else if (msg.type === 'reaction') {
          setMessages(prev => prev.map(m => m.id === msg.data.message_id ? { ...m, reactions: msg.data.reactions } : m));
        } else if (msg.type === 'dm_created') {
          loadDms();
        } else if (msg.type === 'typing') {
          setTypingUsers(prev => ({
            ...prev,
            [msg.data.channel_id]: { ...prev[msg.data.channel_id], [msg.data.user_id]: msg.data.name || msg.data.user_id }
          }));
          setTimeout(() => {
            setTypingUsers(prev => {
              const ch = { ...(prev[msg.data.channel_id] || {}) };
              delete ch[msg.data.user_id];
              return { ...prev, [msg.data.channel_id]: ch };
            });
          }, 3000);
        }
      };

      ws.onclose = () => {
        setTimeout(connectWs, 3000);
      };
    };

    connectWs();
    return () => { if (wsRef.current) wsRef.current.close(); };
  }, [user, loadChannels]);

  // Load messages for active channel
  useEffect(() => {
    if (!activeChannel || !token) return;
    const loadMessages = async () => {
      try {
        const res = await fetch(`${API}/api/lumi/channels/${activeChannel.id}/messages?limit=100`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setMessages(data.messages || []);
        }
      } catch (e) {
        console.error('Failed to load messages:', e);
      }
    };
    loadMessages();
  }, [activeChannel, token]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Send message
  const handleSend = async () => {
    if (!messageText.trim() || !activeChannel || sending) return;
    const text = messageText.trim();
    setMessageText('');
    setSending(true);
    try {
      await fetch(`${API}/api/lumi/channels/${activeChannel.id}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ content: text })
      });
    } catch (e) {
      toast.error('Failed to send message');
      setMessageText(text);
    }
    setSending(false);
  };

  // Join channel
  const handleJoinChannel = async (ch) => {
    try {
      await fetch(`${API}/api/lumi/channels/${ch.id}/join`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      await loadChannels();
      setActiveChannel(ch);
      setMobileSidebar(false);
      toast.success(`Joined #${ch.name}`);
    } catch (e) {
      toast.error('Failed to join');
    }
  };

  // Typing indicator
  const handleTyping = () => {
    if (!activeChannel || !wsRef.current) return;
    if (typingTimeoutRef.current) return;
    try {
      wsRef.current.send(JSON.stringify({ type: 'typing', channel_id: activeChannel.id }));
    } catch (e) {}
    typingTimeoutRef.current = setTimeout(() => { typingTimeoutRef.current = null; }, 2000);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Logout
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('karau_user');
    setUser(null);
    navigate('/');
  };

  // React to message
  const handleReact = async (messageId, emoji) => {
    try {
      const res = await fetch(`${API}/api/lumi/messages/${messageId}/react`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ emoji })
      });
      if (res.ok) {
        const data = await res.json();
        setMessages(prev => prev.map(m => m.id === messageId ? { ...m, reactions: data.reactions } : m));
      }
    } catch (e) { console.error('React error:', e); }
  };

  // Global search
  const handleGlobalSearch = async (query) => {
    setGlobalSearch(query);
    if (query.length < 2) { setSearchResults([]); setShowSearchResults(false); return; }
    try {
      const res = await fetch(`${API}/api/lumi/search?q=${encodeURIComponent(query)}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setSearchResults(data.results || []);
        setShowSearchResults(true);
      }
    } catch (e) { console.error('Search error:', e); }
  };

  // Filtered channels
  const filteredChannels = channels.filter(ch =>
    ch.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Active channel typing
  const activeTyping = activeChannel ? Object.values(typingUsers[activeChannel.id] || {}).filter(n => n !== user?.name) : [];

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0c0d1a] flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-violet-400 animate-spin" />
      </div>
    );
  }

  // Login redirect if not authenticated
  if (!user) {
    return <LumiLogin onLogin={(u) => setUser(u)} />;
  }

  return (
    <div className="h-screen flex bg-[#0c0d1a] overflow-hidden" style={{ fontFamily: "'IBM Plex Sans', sans-serif" }}>
      <Toaster position="top-right" theme="dark" />

      {/* Sidebar */}
      <div className={`${mobileSidebar ? 'flex' : 'hidden'} md:flex flex-col w-full md:w-[280px] border-r border-white/[0.04] flex-shrink-0`}
        style={{ background: 'linear-gradient(180deg, #13142a 0%, #0f1020 100%)' }}>

        {/* Header */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-white/[0.04] flex-shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-600 to-purple-700 flex items-center justify-center shadow-lg shadow-violet-600/20">
              <MessageCircle className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="font-bold text-sm text-white block leading-tight">LUMI</span>
              <span className="text-[10px] text-slate-600 leading-tight">{t('lumi.messenger') || 'Messenger'}</span>
            </div>
          </div>
          <div className="flex items-center gap-1">
            <button onClick={() => navigate('/')} className="p-2 text-slate-600 hover:text-white hover:bg-white/[0.04] rounded-lg transition-all" title="Back to KARAU" data-testid="back-to-karau">
              <ArrowLeft className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Search */}
        <div className="px-3 pt-3 pb-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-600" />
            <Input value={globalSearch || searchQuery} onChange={e => { setSearchQuery(e.target.value); handleGlobalSearch(e.target.value); }}
              placeholder={t('lumi.searchChannels') || 'Search channels & messages...'}
              className="pl-9 h-9 bg-white/[0.03] border-white/[0.06] text-white placeholder:text-slate-700 rounded-xl text-sm" data-testid="search-channels" />
            {globalSearch && (
              <button onClick={() => { setGlobalSearch(''); setSearchQuery(''); setShowSearchResults(false); setSearchResults([]); }}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-600 hover:text-white">
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
          {/* Search Results Dropdown */}
          {showSearchResults && searchResults.length > 0 && (
            <div className="mt-1 max-h-48 overflow-y-auto bg-[#1a1b2e] border border-white/[0.08] rounded-xl shadow-xl" data-testid="search-results">
              {searchResults.map((r, i) => (
                <button key={i} onClick={() => {
                  const ch = channels.find(c => c.id === r.channel_id) || dms.find(d => d.id === r.channel_id);
                  if (ch) { setActiveChannel(ch); setMobileSidebar(false); }
                  setShowSearchResults(false); setGlobalSearch(''); setSearchQuery('');
                }}
                  className="w-full px-3 py-2 text-left hover:bg-white/[0.04] transition-all border-b border-white/[0.03] last:border-0" data-testid={`search-result-${i}`}>
                  <div className="flex items-center gap-1.5 mb-0.5">
                    <span className="text-[10px] text-violet-400 font-medium">#{r.channel_name}</span>
                    <span className="text-[10px] text-slate-700">{r.sender_name}</span>
                  </div>
                  <p className="text-xs text-slate-400 truncate">{r.content}</p>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Channel List */}
        <ScrollArea className="flex-1 py-2">
          <div className="px-3">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-bold text-slate-600 uppercase tracking-widest">{t('lumi.channels') || 'Channels'}</span>
              <button onClick={() => setShowCreateModal(true)} className="p-1 text-slate-600 hover:text-violet-400 hover:bg-violet-500/10 rounded-lg transition-all" data-testid="add-channel-btn">
                <Plus className="w-3.5 h-3.5" />
              </button>
            </div>
            {filteredChannels.map(ch => (
              <button key={ch.id} onClick={() => { setActiveChannel(ch); setMobileSidebar(false); }}
                className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-xl transition-all mb-0.5 group ${
                  activeChannel?.id === ch.id
                    ? 'bg-violet-600/10 text-white'
                    : 'text-slate-500 hover:bg-white/[0.03] hover:text-slate-300'
                }`} data-testid={`channel-${ch.id}`}>
                <div className={`flex items-center justify-center w-7 h-7 rounded-lg ${
                  activeChannel?.id === ch.id ? 'bg-violet-600/20' : 'bg-white/[0.03]'
                }`}>
                  <ChannelIcon type={ch.channel_type} />
                </div>
                <div className="flex-1 text-left min-w-0">
                  <span className="text-sm font-medium truncate block">{ch.name}</span>
                  {ch.last_message && (
                    <span className="text-[10px] text-slate-700 truncate block">
                      {ch.last_message.sender_name}: {ch.last_message.content}
                    </span>
                  )}
                </div>
                {ch.message_count > 0 && (
                  <span className="text-[10px] text-slate-700">{ch.message_count}</span>
                )}
              </button>
            ))}

            {/* Discover channels */}
            {discoverChannels.length > 0 && (
              <>
                <div className="flex items-center justify-between mt-4 mb-2">
                  <span className="text-[10px] font-bold text-slate-600 uppercase tracking-widest">{t('lumi.discover') || 'Discover'}</span>
                </div>
                {discoverChannels.map(ch => (
                  <button key={ch.id} onClick={() => handleJoinChannel(ch)}
                    className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-slate-600 hover:bg-white/[0.03] hover:text-slate-400 transition-all mb-0.5"
                    data-testid={`discover-${ch.id}`}>
                    <div className="w-7 h-7 rounded-lg bg-white/[0.02] flex items-center justify-center">
                      <ChannelIcon type={ch.channel_type} />
                    </div>
                    <span className="text-sm truncate">{ch.name}</span>
                    <Plus className="w-3.5 h-3.5 ml-auto opacity-60" />
                  </button>
                ))}
              </>
            )}

            {/* Direct Messages */}
            <div className="flex items-center justify-between mt-4 mb-2">
              <span className="text-[10px] font-bold text-slate-600 uppercase tracking-widest">{t('lumi.directMessages') || 'Direct Messages'}</span>
              <button onClick={() => setShowNewDmModal(true)} className="p-1 text-slate-600 hover:text-teal-400 hover:bg-teal-500/10 rounded-lg transition-all" data-testid="new-dm-btn">
                <UserPlus className="w-3.5 h-3.5" />
              </button>
            </div>
            {dms.map(dm => {
              const partner = dm.dm_partner || {};
              const initials = (partner.name || partner.email || '?').split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase();
              return (
                <button key={dm.id} onClick={() => { setActiveChannel(dm); setMobileSidebar(false); }}
                  className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-xl transition-all mb-0.5 ${
                    activeChannel?.id === dm.id
                      ? 'bg-teal-600/10 text-white'
                      : 'text-slate-500 hover:bg-white/[0.03] hover:text-slate-300'
                  }`} data-testid={`dm-${dm.id}`}>
                  <div className={`w-7 h-7 rounded-lg flex items-center justify-center text-[10px] font-bold ${
                    activeChannel?.id === dm.id ? 'bg-teal-600/20 text-teal-300' : 'bg-white/[0.04] text-slate-500'
                  }`}>{initials}</div>
                  <div className="flex-1 text-left min-w-0">
                    <span className="text-sm font-medium truncate block">{partner.name || partner.email || 'User'}</span>
                    {dm.last_message && (
                      <span className="text-[10px] text-slate-700 truncate block">{dm.last_message.content}</span>
                    )}
                  </div>
                </button>
              );
            })}
            {dms.length === 0 && (
              <p className="text-[11px] text-slate-700 px-3 py-1">{t('lumi.noDmsYet') || 'No conversations yet'}</p>
            )}
          </div>
        </ScrollArea>

        {/* Language + User */}
        <div className="px-3 py-2 border-t border-white/[0.04]">
          <GlobalLanguageSelector compact={false} />
        </div>
        <div className="p-3 border-t border-white/[0.04]">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-violet-600/30 to-purple-600/20 border border-violet-500/20 flex items-center justify-center">
              <span className="text-violet-300 font-semibold text-xs">{(user?.name || user?.email || '?')[0].toUpperCase()}</span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">{user?.name || 'User'}</p>
              <div className="flex items-center gap-1">
                <Circle className="w-2 h-2 fill-emerald-400 text-emerald-400" />
                <span className="text-[10px] text-slate-600">{t('lumi.online') || 'Online'}</span>
              </div>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="ghost" size="sm" onClick={() => navigate('/karau-meet')}
              className="flex-1 text-slate-500 hover:text-white hover:bg-white/[0.04] rounded-xl text-xs" data-testid="go-karau-meet">
              AI KARAU
            </Button>
            <Button variant="ghost" size="sm" onClick={handleLogout}
              className="text-slate-500 hover:text-red-400 hover:bg-red-500/10 rounded-xl" data-testid="lumi-logout">
              <LogOut className="w-3.5 h-3.5" />
            </Button>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className={`${!mobileSidebar ? 'flex' : 'hidden'} md:flex flex-col flex-1 min-w-0`}>
        {activeChannel ? (
          <>
            {/* Channel/DM Header */}
            <div className="h-16 flex items-center justify-between px-5 border-b border-white/[0.04] flex-shrink-0 bg-[#0c0d1a]/80 backdrop-blur-xl">
              <div className="flex items-center gap-3">
                <button className="md:hidden p-2 text-slate-500 hover:text-white" onClick={() => setMobileSidebar(true)}>
                  <ArrowLeft className="w-4 h-4" />
                </button>
                {activeChannel.channel_type === 'dm' ? (
                  <>
                    <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-teal-600/20 to-cyan-600/10 border border-teal-500/10 flex items-center justify-center">
                      <User className="w-4.5 h-4.5 text-teal-400" />
                    </div>
                    <div>
                      <h2 className="text-sm font-bold text-white">{activeChannel.dm_partner?.name || activeChannel.name}</h2>
                      <p className="text-[10px] text-teal-500">{t('lumi.directMessage') || 'Direct Message'}</p>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-600/20 to-purple-600/10 border border-violet-500/10 flex items-center justify-center">
                      <ChannelIcon type={activeChannel.channel_type} size={18} />
                    </div>
                    <div>
                      <h2 className="text-sm font-bold text-white">#{activeChannel.name}</h2>
                      <p className="text-[10px] text-slate-600">{activeChannel.members?.length || 0} {t('lumi.members') || 'members'} &middot; {activeChannel.description}</p>
                    </div>
                  </>
                )}
              </div>
              <div className="flex items-center gap-2">
                <button className="p-2 text-slate-600 hover:text-white hover:bg-white/[0.04] rounded-lg" data-testid="channel-members-btn">
                  <Users className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Messages */}
            <ScrollArea className="flex-1 py-3">
              {messages.length === 0 && (
                <div className="flex flex-col items-center justify-center h-full text-center px-6">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-600/10 to-purple-600/5 flex items-center justify-center mb-4">
                    <MessageCircle className="w-8 h-8 text-violet-500/40" />
                  </div>
                  <p className="text-slate-600 text-sm">{t('lumi.noMessages') || 'No messages yet'}</p>
                  <p className="text-slate-700 text-xs mt-1">{t('lumi.startConversation') || 'Start the conversation!'}</p>
                </div>
              )}
              {messages.map((msg, i) => {
                const prevSameSender = i > 0 && messages[i - 1].sender_id === msg.sender_id && messages[i - 1].type !== 'system';
                return <MessageBubble key={msg.id} msg={msg} isOwn={msg.sender_id === user?.user_id} prevSameSender={prevSameSender} onReact={handleReact} />;
              })}
              <div ref={messagesEndRef} />
            </ScrollArea>

            {/* Typing indicator */}
            {activeTyping.length > 0 && (
              <div className="px-5 py-1">
                <span className="text-xs text-violet-400 animate-pulse">
                  {activeTyping.join(', ')} {activeTyping.length === 1 ? 'is' : 'are'} typing...
                </span>
              </div>
            )}

            {/* Message Input */}
            <div className="p-4 border-t border-white/[0.04]">
              <div className="flex items-center gap-2 bg-white/[0.03] border border-white/[0.06] rounded-2xl px-4 py-2 focus-within:border-violet-500/30 transition-all">
                <input
                  value={messageText}
                  onChange={e => { setMessageText(e.target.value); handleTyping(); }}
                  onKeyDown={handleKeyDown}
                  placeholder={`${t('lumi.messagePlaceholder') || 'Message'} #${activeChannel.name}`}
                  className="flex-1 bg-transparent text-sm text-white placeholder:text-slate-700 outline-none"
                  data-testid="message-input"
                />
                <button onClick={handleSend} disabled={!messageText.trim() || sending}
                  className={`p-2 rounded-xl transition-all ${
                    messageText.trim() ? 'bg-violet-600 text-white hover:bg-violet-500' : 'text-slate-700'
                  }`} data-testid="send-message-btn">
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </div>
          </>
        ) : (
          /* No channel selected */
          <div className="flex-1 flex flex-col items-center justify-center text-center px-6">
            <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-violet-600/10 to-purple-600/5 flex items-center justify-center mb-5 shadow-lg shadow-violet-600/5">
              <MessageCircle className="w-10 h-10 text-violet-500/30" />
            </div>
            <h2 className="text-xl font-bold text-white mb-2">LUMI</h2>
            <p className="text-slate-600 text-sm max-w-xs">{t('lumi.welcomeMessage') || 'Select a channel to start chatting, or create a new one.'}</p>
            <Button onClick={() => setShowCreateModal(true)}
              className="mt-4 bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-500 hover:to-purple-500 text-white rounded-xl" data-testid="create-first-channel">
              <Plus className="w-4 h-4 mr-2" />{t('lumi.createChannel') || 'Create Channel'}
            </Button>
          </div>
        )}
      </div>

      {/* Create Channel Modal */}
      {showCreateModal && (
        <CreateChannelModal
          onClose={() => setShowCreateModal(false)}
          onCreated={(ch) => { setChannels(prev => [ch, ...prev]); setActiveChannel(ch); setShowCreateModal(false); setMobileSidebar(false); }}
          token={token}
        />
      )}

      {/* New DM Modal */}
      {showNewDmModal && (
        <NewDmModal
          onClose={() => setShowNewDmModal(false)}
          onSelect={handleStartDm}
          token={token}
        />
      )}
    </div>
  );
};

// ============== LUMI Login Screen ==============
const LumiLogin = ({ onLogin }) => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const res = await fetch(`${API}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      if (res.ok) {
        const data = await res.json();
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('karau_user', JSON.stringify(data.user));
        onLogin(data.user);
        toast.success(t('lumi.welcomeToLumi') || 'Welcome to LUMI!');
      } else {
        const err = await res.json();
        toast.error(err.detail || 'Login failed');
      }
    } catch (e) {
      toast.error('Connection error');
    }
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-[#0c0d1a] flex items-center justify-center p-4" style={{ fontFamily: "'IBM Plex Sans', sans-serif" }}>
      <Toaster position="top-right" theme="dark" />
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-violet-600 to-purple-700 flex items-center justify-center shadow-2xl shadow-violet-600/30 mb-4">
            <MessageCircle className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white mb-1">LUMI</h1>
          <p className="text-sm text-slate-600">{t('lumi.tagline') || 'Team messaging for the KARAU ecosystem'}</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <Input value={email} onChange={e => setEmail(e.target.value)} type="email" placeholder={t('common.login') || 'Email'}
              className="bg-white/[0.04] border-white/[0.08] text-white placeholder:text-slate-600 rounded-xl h-12" data-testid="lumi-email" />
          </div>
          <div className="relative">
            <Input value={password} onChange={e => setPassword(e.target.value)} type={showPassword ? 'text' : 'password'} placeholder={t('auth.password') || 'Password'}
              className="bg-white/[0.04] border-white/[0.08] text-white placeholder:text-slate-600 rounded-xl h-12 pr-10" data-testid="lumi-password" />
            <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-600 hover:text-white">
              {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
          <Button type="submit" disabled={isLoading || !email || !password}
            className="w-full h-12 bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-500 hover:to-purple-500 text-white rounded-xl text-base font-semibold" data-testid="lumi-login-btn">
            {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : t('lumi.signIn') || 'Sign in to LUMI'}
          </Button>
        </form>

        <div className="mt-6 text-center">
          <button onClick={() => navigate('/')} className="text-sm text-slate-600 hover:text-violet-400 transition-colors" data-testid="back-to-portal">
            {t('lumi.backToPortal') || 'Back to Portal'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default LumiMessenger;
