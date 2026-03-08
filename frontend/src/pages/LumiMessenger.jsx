/**
 * ENZI Prestige — Enterprise Team Messenger
 * Refactored: Main container imports sub-components from /components/Lumi/
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast, Toaster } from 'sonner';
import {
  Plus, Send, LogOut, ArrowLeft, Hash,
  Users, Search, MessageCircle,
  Loader2, X, Paperclip, UserPlus, User, Phone, Video,
  Building2, Sparkles, Brain, AlertTriangle, Shield,
  Command, Network, Zap, TrendingDown, Bell,
  Smile, Keyboard, ClipboardList, Globe, BarChart3,
  Sun, Moon, Share2, Clock, Edit, ChevronDown, ChevronRight, Settings, BellOff
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useTranslation } from '@/utils/i18n';
import { useTheme } from '@/App';

import {
  ChannelIcon, StatusDot, MessageBubble, ThreadPanel, MembersPanel,
  AiProductivityPanel, AiChatPanel, AlertsPanel, CommandBar,
  KnowledgeGraphPanel, BottleneckPanel, SimulationPanel,
  NotificationsPanel, CreateChannelModal, NewDmModal, LumiLogin,
  UserProfileModal, RetentionPanel, EmojiPicker,
  ShortcutsPanel, useKeyboardShortcuts,
  AdminAuditPanel, CompliancePanel, ComplianceWidget,
  VisualizationsPanel, LumiBrand,
  API, WS_URL, ESY, STATUS_COLORS, STATUS_LABELS
} from '@/components/Lumi';
import AIWritingToolbar from '@/components/Lumi/AIWritingToolbar';
import EnziSplash from '@/components/Lumi/EnziSplash';
import InviteModal from '@/components/Lumi/InviteModal';
import InviteRegistration from '@/components/Lumi/InviteRegistration';
import NewMessagePanel from '@/components/Lumi/NewMessagePanel';
import ConversationSummary from '@/components/Lumi/ConversationSummary';
import ScheduleMessageModal from '@/components/Lumi/ScheduleMessageModal';
import NotificationSettings from '@/components/Lumi/NotificationSettings';
import EnziMeetingModal from '@/components/Lumi/EnziMeetingModal';
import MeetingHistoryPanel from '@/components/Lumi/MeetingHistoryPanel';
import BotStoreModal from '@/components/Lumi/BotStoreModal';
import BotActionsBar from '@/components/Lumi/BotActionsBar';
import E2EEIndicator from '@/components/Lumi/E2EEIndicator';

const LumiMessenger = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { isDark, toggleTheme } = useTheme();
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
  const [showVisualizations, setShowVisualizations] = useState(false);
  const [userAccentColor, setUserAccentColor] = useState('');
  const [presenceMap, setPresenceMap] = useState({});
  const [pendingInvites, setPendingInvites] = useState([]);
  const [bucketCounts, setBucketCounts] = useState({ urgent: 0, action_required: 0, meeting_request: 0, fyi: 0, social: 0 });
  const [activeBucket, setActiveBucket] = useState(null);
  const [bucketMessages, setBucketMessages] = useState([]);
  const [bucketLoading, setBucketLoading] = useState(false);
  const [calendarStatus, setCalendarStatus] = useState({ status: 'available', source: 'manual', calendar_event: null, microsoft_linked: false });
  const [predictions, setPredictions] = useState({ channels: [], dms: [] });
  const [showSplash, setShowSplash] = useState(() => !sessionStorage.getItem('enzi_splash_shown'));
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteToken, setInviteToken] = useState(null);
  const [domainColleagues, setDomainColleagues] = useState([]);
  const [showNewMsgPanel, setShowNewMsgPanel] = useState(false);
  const [showAdminTools, setShowAdminTools] = useState(false);
  const [sidebarView, setSidebarView] = useState('channels'); // 'channels' | 'recent'
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [showNotifSettings, setShowNotifSettings] = useState(false);
  const [showSummary, setShowSummary] = useState(false);
  const [showMeetingModal, setShowMeetingModal] = useState(false);
  const [showMeetingHistory, setShowMeetingHistory] = useState(false);
  const [showBotStore, setShowBotStore] = useState(false);

  const messagesEndRef = useRef(null);
  const wsRef = useRef(null);
  const typingTimeoutRef = useRef(null);
  const fileInputRef = useRef(null);
  const token = localStorage.getItem('token');

  // Handle SSO callback (Google or Microsoft) and invite tokens
  useEffect(() => {
    // Check for invite token in URL
    const params = new URLSearchParams(window.location.search);
    const invToken = params.get('invite_token');
    if (invToken) {
      setInviteToken(invToken);
      setIsLoading(false);
      return;
    }

    const hash = window.location.hash;
    if (hash && hash.includes('session_id=')) {
      const sessionId = hash.split('session_id=')[1]?.split('&')[0];
      if (sessionId) {
        (async () => {
          try {
            // Try Google session first (Emergent auth)
            let res = await fetch(`${API}/api/auth/google/session`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ session_id: sessionId })
            });
            // If Google fails, try generic session validation (Microsoft SSO)
            if (!res.ok) {
              res = await fetch(`${API}/api/auth/session/validate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_token: sessionId })
              });
            }
            if (res.ok) {
              const data = await res.json();
              localStorage.setItem('token', data.access_token);
              localStorage.setItem('karau_user', JSON.stringify(data.user));
              setUser(data.user);
              toast.success('Welcome to ENZI!');
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

  const loadInvites = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/api/lumi/invites`, { headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) setPendingInvites((await res.json()).invites || []);
    } catch (e) {}
  }, [token]);

  const loadBucketCounts = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/api/lumi/buckets/counts`, { headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) setBucketCounts((await res.json()).counts || {});
    } catch (e) {}
  }, [token]);

  const scanAndLoadBuckets = useCallback(async () => {
    if (!token) return;
    try {
      await fetch(`${API}/api/lumi/buckets/scan`, { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } });
      loadBucketCounts();
    } catch (e) {}
  }, [token, loadBucketCounts]);

  const loadCalendarStatus = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/api/lumi/calendar/status`, { headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) setCalendarStatus(await res.json());
    } catch (e) {}
  }, [token]);

  const loadPredictions = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/api/lumi/predict/suggestions`, { headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) setPredictions(await res.json());
    } catch (e) {}
  }, [token]);

  const loadDomainColleagues = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/api/lumi/domain/colleagues`, { headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) {
        const data = await res.json();
        if (data.is_company_domain) setDomainColleagues(data.colleagues || []);
      }
    } catch (e) {}
  }, [token]);

  const trackAction = async (action, targetId, targetName) => {
    if (!token) return;
    fetch(`${API}/api/lumi/predict/track`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ action, target_id: targetId, target_name: targetName })
    }).catch(() => {});
  };

  const openBucket = async (category) => {
    setBucketLoading(true);
    setActiveBucket(category);
    try {
      const res = await fetch(`${API}/api/lumi/buckets/${category}`, { headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) setBucketMessages((await res.json()).messages || []);
    } catch (e) {}
    setBucketLoading(false);
  };

  const dismissBucketItem = async (category, itemId) => {
    await fetch(`${API}/api/lumi/buckets/${category}/${itemId}/dismiss`, { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } });
    setBucketMessages(prev => prev.filter(m => m.id !== itemId));
    loadBucketCounts();
  };

  useEffect(() => {
    if (user) { loadChannels(); loadDms(); loadUnreadCounts(); loadPresence(); loadInvites(); scanAndLoadBuckets(); loadCalendarStatus(); loadPredictions(); loadDomainColleagues(); }
  }, [user, loadChannels, loadDms, loadUnreadCounts, loadPresence, loadInvites, scanAndLoadBuckets, loadCalendarStatus, loadPredictions, loadDomainColleagues]);

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
    const res = await fetch(`${API}/api/lumi/channels/${ch.id}/join`, { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } });
    if (res.ok) {
      const data = await res.json();
      if (data.status === 'pending_approval') {
        toast.info('Join request sent — awaiting approval');
        return;
      }
    }
    await loadChannels(); setActiveChannel(ch); setMobileSidebar(false); toast.success(`Joined #${ch.name}`);
  };

  const handleInviteResponse = async (inviteId, action) => {
    try {
      const res = await fetch(`${API}/api/lumi/invites/${inviteId}/respond`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ action })
      });
      if (res.ok) {
        const data = await res.json();
        if (action === 'accept') {
          toast.success('Invite accepted!');
          await loadChannels();
          const ch = channels.find(c => c.id === data.channel_id);
          if (ch) { setActiveChannel(ch); setMobileSidebar(false); }
        } else {
          toast.info('Invite declined');
        }
        loadInvites();
      }
    } catch (e) { toast.error('Failed to respond'); }
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

  // Predictive sorting: boost channels/DMs that appear in predictions
  const predictedChannelIds = new Set((predictions?.channels || []).map(p => p.target_id));
  const predictedDmIds = new Set((predictions?.dms || []).map(p => p.target_id));

  const sortedChannels = [...filteredChannels].sort((a, b) => {
    const aP = predictedChannelIds.has(a.id) ? 1 : 0;
    const bP = predictedChannelIds.has(b.id) ? 1 : 0;
    if (bP !== aP) return bP - aP;
    // Secondary: unread counts
    return (unreadCounts[b.id] || 0) - (unreadCounts[a.id] || 0);
  });

  const sortedDms = [...dms].sort((a, b) => {
    const aP = predictedDmIds.has(a.id) ? 1 : 0;
    const bP = predictedDmIds.has(b.id) ? 1 : 0;
    if (bP !== aP) return bP - aP;
    return (unreadCounts[b.id] || 0) - (unreadCounts[a.id] || 0);
  });

  // Recent conversations: mix channels + DMs sorted by last activity
  const recentConversations = [
    ...channels.map(ch => ({ ...ch, _type: 'channel', _time: ch.last_activity || ch.created_at || '' })),
    ...dms.map(dm => ({ ...dm, _type: 'dm', _time: dm.last_activity || dm.created_at || '' })),
  ].sort((a, b) => (b._time || '').localeCompare(a._time || '')).slice(0, 15);

  const handleNewMsgInvite = async (method, query) => {
    const APP_URL = API;
    // Generate invite link first
    try {
      const res = await fetch(`${API}/api/lumi/invite/link`, { headers: { Authorization: `Bearer ${token}` } });
      if (!res.ok) return;
      const data = await res.json();
      const inviteUrl = data.invite_url;
      const text = `Join me on ENZI Messenger: ${inviteUrl}`;

      if (method === 'email' && query.includes('@')) {
        fetch(`${API}/api/lumi/invite/send`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
          body: JSON.stringify({ emails: [query], message: '' })
        }).then(() => toast.success(`Invite sent to ${query}`)).catch(() => toast.error('Failed'));
      } else if (method === 'sms') {
        window.open(`sms:?body=${encodeURIComponent(text)}`, '_blank');
      } else if (method === 'whatsapp') {
        window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, '_blank');
      } else if (method === 'linkedin') {
        window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(inviteUrl)}`, '_blank');
      } else if (method === 'instagram') {
        navigator.clipboard.writeText(text);
        toast.success('Link copied! Paste it in Instagram DM');
      } else if (method === 'share') {
        navigator.clipboard.writeText(inviteUrl);
        toast.success('Invite link copied!');
      }
      setShowNewMsgPanel(false);
    } catch { toast.error('Failed to generate invite'); }
  };

  const closeAllPanels = () => { setShowAiChat(false); setShowAlerts(false); setShowAiPanel(false); setShowKnowledgeGraph(false); setShowBottlenecks(false); setShowSimulation(false); setShowNotifications(false); };

  if (isLoading) return <div className="min-h-screen bg-[#0D1117] flex items-center justify-center"><Loader2 className="w-8 h-8 text-[#00CEC9] animate-spin" /></div>;
  if (inviteToken) return <InviteRegistration inviteToken={inviteToken} onComplete={(u) => { setUser(u); setInviteToken(null); window.history.replaceState(null, '', '/lumi'); }} />;
  if (!user) return <LumiLogin onLogin={setUser} />;

  return (
    <div className="h-screen flex bg-[#0D1117] overflow-hidden" style={{ fontFamily: "'Inter', -apple-system, sans-serif" }}>
      <Toaster position="top-right" richColors />
      {showSplash && <EnziSplash onComplete={() => { setShowSplash(false); sessionStorage.setItem('enzi_splash_shown', '1'); }} />}

      {/* Sidebar */}
      <div className={`${mobileSidebar ? 'flex' : 'hidden'} md:flex flex-col w-full md:w-[280px] bg-[#0D1117] flex-shrink-0 border-r border-white/5`}>
        {/* Header */}
        <div className="h-14 flex items-center justify-between px-4 border-b border-white/10">
          <div className="flex items-center gap-2.5">
            <LumiBrand variant="inline-dark" size="xs" showTagline />
          </div>
          <button onClick={() => navigate('/')} className="p-2 text-white/80 hover:text-white hover:bg-white/10 rounded-md transition-colors" data-testid="back-to-karau"><ArrowLeft className="w-4 h-4" /></button>
        </div>

        {/* Quick Actions: Recent / New Message */}
        <div className="px-3 pt-3 pb-2 flex gap-2">
          <button onClick={() => setSidebarView('recent')}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-medium transition-all ${sidebarView === 'recent' ? 'bg-[#00CEC9]/10 text-[#00CEC9] border border-[#00CEC9]/20' : 'bg-white/5 text-white/70 hover:bg-white/10 border border-transparent'}`}
            data-testid="sidebar-recent-btn">
            <Clock className="w-3.5 h-3.5" />Recent
          </button>
          <button onClick={() => setShowNewMsgPanel(true)}
            className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-medium bg-white/5 text-white/70 hover:bg-white/10 border border-transparent hover:border-white/10 transition-all"
            data-testid="sidebar-new-msg-btn">
            <Edit className="w-3.5 h-3.5" />New Message
          </button>
        </div>

        {/* Search */}
        <div className="px-3 pb-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-white/50" />
            <input value={globalSearch || searchQuery} onChange={e => { setSearchQuery(e.target.value); handleGlobalSearch(e.target.value); setSidebarView('channels'); }}
              placeholder={t('lumi.searchChannels') || 'Search channels & people...'}
              className="w-full pl-9 h-8 bg-white/10 border-0 rounded-md text-sm text-white placeholder:text-white/40 outline-none focus:bg-white/15 transition-colors" data-testid="search-channels" />
            {globalSearch && <button onClick={() => { setGlobalSearch(''); setSearchQuery(''); setShowSearchResults(false); }} className="absolute right-2 top-1/2 -translate-y-1/2 text-white/60 hover:text-white"><X className="w-3.5 h-3.5" /></button>}
          </div>
          {showSearchResults && searchResults.length > 0 && (
            <div className="mt-1 max-h-48 overflow-y-auto bg-[#0F1923] border border-white/10 rounded-md shadow-lg" data-testid="search-results">
              {searchResults.map((r, i) => (
                <button key={i} onClick={() => { const ch = channels.find(c => c.id === r.channel_id) || dms.find(d => d.id === r.channel_id); if (ch) { setActiveChannel(ch); setMobileSidebar(false); } setShowSearchResults(false); setGlobalSearch(''); setSearchQuery(''); }}
                  className="w-full px-3 py-2 text-left hover:bg-white/10 border-b border-white/5 last:border-0" data-testid={`search-result-${i}`}>
                  <span className="text-[10px] text-[#00CEC9] font-medium">#{r.channel_name}</span>
                  <p className="text-xs text-white/80 truncate">{r.content}</p>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Smart Buckets (collapsible) */}
        {(bucketCounts.urgent > 0 || bucketCounts.action_required > 0 || bucketCounts.meeting_request > 0) && (
          <div className="px-3 pb-2">
            <div className="bg-white/[0.02] rounded-lg border border-white/5 overflow-hidden">
              <div className="flex items-center gap-1.5 px-2.5 py-1.5">
                <Zap className="w-3 h-3 text-amber-400" />
                <span className="text-[10px] font-semibold text-white/60 uppercase tracking-wider flex-1">Priority</span>
              </div>
              <div className="px-1 pb-1 space-y-0.5">
                {[
                  { key: 'urgent', label: 'Urgent', color: 'bg-red-500', textColor: 'text-red-400' },
                  { key: 'action_required', label: 'Action Required', color: 'bg-amber-500', textColor: 'text-amber-400' },
                  { key: 'meeting_request', label: 'Meetings', color: 'bg-blue-500', textColor: 'text-blue-400' },
                ].filter(b => bucketCounts[b.key] > 0).map(b => (
                  <button key={b.key} onClick={() => { openBucket(b.key); setMobileSidebar(false); }}
                    className="w-full flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-white/5 transition-colors"
                    data-testid={`sidebar-bucket-${b.key}`}>
                    <div className={`w-1.5 h-1.5 rounded-full ${b.color}`} />
                    <span className="text-xs text-white/70 flex-1 text-left">{b.label}</span>
                    <span className={`text-[10px] font-bold ${b.textColor}`}>{bucketCounts[b.key]}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        <ScrollArea className="flex-1 py-1">
          <div className="px-3">
            {/* RECENT VIEW */}
            {sidebarView === 'recent' ? (
              <>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[11px] font-bold text-white/90 uppercase tracking-widest">Recent</span>
                  <button onClick={() => setSidebarView('channels')} className="text-[9px] text-[#00CEC9] hover:underline">All Channels</button>
                </div>
                {recentConversations.map(item => (
                  <button key={item.id} onClick={() => { setActiveChannel(item); setMobileSidebar(false); setShowThread(null); setShowMembers(false); setShowAiPanel(false); }}
                    className={`w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md transition-colors mb-0.5 ${activeChannel?.id === item.id ? 'bg-white/15 text-white' : 'text-white/80 hover:bg-white/10 hover:text-white'}`}
                    data-testid={`recent-${item.id}`}>
                    {item._type === 'dm' ? (
                      <div className="relative">
                        <div className="w-6 h-6 rounded-full bg-slate-500 flex items-center justify-center text-[9px] font-semibold text-white">
                          {(item.dm_partner?.name || item.dm_partner?.email || '?')[0].toUpperCase()}
                        </div>
                        <span className={`absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full ring-1 ring-[#0D1117] ${STATUS_COLORS[presenceMap[item.dm_partner?.user_id] || 'offline']}`} />
                      </div>
                    ) : (
                      <ChannelIcon type={item.channel_type} />
                    )}
                    <span className="flex-1 text-sm truncate text-left">
                      {item._type === 'dm' ? (item.dm_partner?.name || item.dm_partner?.email || 'User') : item.name}
                    </span>
                    {unreadCounts[item.id] > 0 && <span className="min-w-[16px] h-[16px] flex items-center justify-center rounded-full text-[8px] font-bold text-white" style={{ backgroundColor: ESY.pink }}>{unreadCounts[item.id]}</span>}
                  </button>
                ))}
                {recentConversations.length === 0 && <p className="text-[11px] text-white/50 px-2.5 py-3 text-center">No conversations yet</p>}
              </>
            ) : (
              <>
                {/* CHANNELS VIEW */}
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[11px] font-bold text-white/90 uppercase tracking-widest">Channels</span>
                  <button onClick={() => setShowCreateModal(true)} className="p-1 text-white/80 hover:text-white hover:bg-white/10 rounded transition-colors" data-testid="add-channel-btn"><Plus className="w-3.5 h-3.5" /></button>
                </div>
                {sortedChannels.map(ch => (
                  <button key={ch.id} onClick={() => { setActiveChannel(ch); setMobileSidebar(false); setShowThread(null); setShowMembers(false); setShowAiPanel(false); trackAction('channel_visit', ch.id, ch.name); }}
                    className={`w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md transition-colors mb-0.5 ${activeChannel?.id === ch.id ? 'bg-white/15 text-white font-semibold' : 'text-white/80 hover:bg-white/10 hover:text-white'}`} data-testid={`channel-${ch.id}`}>
                    <ChannelIcon type={ch.channel_type} /><span className="flex-1 text-sm truncate text-left">{ch.name}</span>
                    {predictedChannelIds.has(ch.id) && <Zap className="w-3 h-3 text-amber-400 flex-shrink-0" title="Predicted for you" />}
                    {unreadCounts[ch.id] > 0 && <span className="min-w-[18px] h-[18px] flex items-center justify-center rounded-full text-[9px] font-bold text-white" style={{ backgroundColor: ESY.pink }} data-testid={`unread-${ch.id}`}>{unreadCounts[ch.id]}</span>}
                  </button>
                ))}

                {discoverChannels.length > 0 && (<>
                  <div className="flex items-center mt-3 mb-1.5"><span className="text-[11px] font-bold text-white/90 uppercase tracking-widest">Discover</span></div>
                  {discoverChannels.map(ch => (
                    <button key={ch.id} onClick={() => handleJoinChannel(ch)} className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md text-white/80 hover:bg-white/10 hover:text-white mb-0.5" data-testid={`discover-${ch.id}`}>
                      <ChannelIcon type={ch.channel_type} /><span className="flex-1 text-sm truncate text-left">{ch.name}</span><Plus className="w-3 h-3 opacity-70" />
                    </button>
                  ))}
                </>)}

                <div className="flex items-center justify-between mt-3 mb-1.5">
                  <span className="text-[11px] font-bold text-white/90 uppercase tracking-widest">Direct Messages</span>
                  <button onClick={() => setShowNewMsgPanel(true)} className="p-1 text-white/80 hover:text-white hover:bg-white/10 rounded transition-colors" data-testid="new-dm-btn"><UserPlus className="w-3.5 h-3.5" /></button>
                </div>
                {sortedDms.map(dm => {
                  const partner = dm.dm_partner || {};
                  const init = (partner.name || partner.email || '?')[0].toUpperCase();
                  const st = presenceMap[partner.user_id] || 'offline';
                  return (
                    <button key={dm.id} onClick={() => { setActiveChannel(dm); setMobileSidebar(false); setShowThread(null); setShowMembers(false); setShowAiPanel(false); trackAction('dm_visit', dm.id, partner.name || partner.email || 'User'); }}
                      className={`w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md transition-colors mb-0.5 ${activeChannel?.id === dm.id ? 'bg-white/15 text-white' : 'text-white/80 hover:bg-white/10 hover:text-white'}`} data-testid={`dm-${dm.id}`}>
                      <div className="relative">
                        <div className="w-6 h-6 rounded-full bg-slate-500 flex items-center justify-center text-[9px] font-semibold text-white">{init}</div>
                        <span className={`absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full ring-1 ring-[#1A2332] ${STATUS_COLORS[st]}`} />
                      </div>
                      <span className="flex-1 text-sm truncate text-left">{partner.name || partner.email || 'User'}</span>
                      {predictedDmIds.has(dm.id) && <Zap className="w-3 h-3 text-amber-400 flex-shrink-0" title="Predicted" />}
                      {unreadCounts[dm.id] > 0 && <span className="min-w-[16px] h-[16px] flex items-center justify-center rounded-full text-[8px] font-bold text-white" style={{ backgroundColor: ESY.pink }} data-testid={`unread-dm-${dm.id}`}>{unreadCounts[dm.id]}</span>}
                    </button>
                  );
                })}
                {sortedDms.length === 0 && <p className="text-[11px] text-white/80 px-2.5 py-1">No conversations yet</p>}

                {/* Domain Colleagues */}
                {domainColleagues.length > 0 && (<>
                  <div className="flex items-center mt-3 mb-1.5">
                    <span className="text-[11px] font-bold text-white/90 uppercase tracking-widest">Company</span>
                  </div>
                  {domainColleagues.slice(0, 5).map(c => (
                    <button key={c.user_id} onClick={() => handleStartDm(c.user_id)}
                      className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md text-white/80 hover:bg-white/10 hover:text-white mb-0.5" data-testid={`colleague-${c.user_id}`}>
                      <div className="w-6 h-6 rounded-full bg-indigo-500/20 flex items-center justify-center text-[9px] font-semibold text-indigo-300">
                        {(c.name || c.email || '?')[0].toUpperCase()}
                      </div>
                      <span className="flex-1 text-sm truncate text-left">{c.name || c.email}</span>
                    </button>
                  ))}
                </>)}

                {/* Invite Button */}
                <button onClick={() => setShowInviteModal(true)}
                  className="w-full flex items-center gap-2 mt-3 px-2.5 py-2 rounded-lg text-white/70 hover:text-white hover:bg-white/10 transition-colors border border-dashed border-white/10 hover:border-white/20"
                  data-testid="invite-to-enzi-btn">
                  <Share2 className="w-3.5 h-3.5" />
                  <span className="text-xs font-medium">Invite to ENZI</span>
                </button>
              </>
            )}
          </div>
        </ScrollArea>

        {/* Compact Footer */}
        <div className="border-t border-white/10">
          {/* User profile row */}
          <div className="px-3 py-2 flex items-center gap-2">
            <button onClick={() => setShowProfile(true)} className="relative group" data-testid="open-profile-btn" title="My Profile">
              <div className="w-8 h-8 rounded-full flex items-center justify-center group-hover:ring-2 group-hover:ring-white/30 transition-all" style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` }}><span className="text-xs font-semibold text-white">{(user?.name || user?.email || '?')[0].toUpperCase()}</span></div>
              <span className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full ring-2 ring-[#1A2332] bg-emerald-500" />
            </button>
            <button onClick={() => setShowProfile(true)} className="flex-1 min-w-0 text-left hover:opacity-80 transition-opacity" data-testid="open-profile-name">
              <p className="text-sm font-medium text-white truncate">{user?.name || 'User'}</p>
            </button>
            <div className="flex items-center gap-0.5">
              <button onClick={toggleTheme} className="p-1.5 text-white/50 hover:text-white hover:bg-white/10 rounded-md transition-colors" data-testid="theme-toggle-btn" title={isDark ? 'Light Mode' : 'Dark Mode'}>
                {isDark ? <Sun className="w-3.5 h-3.5" /> : <Moon className="w-3.5 h-3.5" />}
              </button>
              <button onClick={() => setShowAdminTools(!showAdminTools)} className={`p-1.5 rounded-md transition-colors ${showAdminTools ? 'text-[#00CEC9] bg-white/10' : 'text-white/50 hover:text-white hover:bg-white/10'}`} data-testid="admin-tools-toggle" title="Admin & Tools">
                <Settings className="w-3.5 h-3.5" />
              </button>
              <button onClick={() => { localStorage.removeItem('token'); localStorage.removeItem('karau_user'); setUser(null); navigate('/'); }} className="p-1.5 text-white/50 hover:text-red-400 hover:bg-red-500/10 rounded-md transition-colors" data-testid="lumi-logout" title="Logout">
                <LogOut className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Collapsible Admin Tools */}
          {showAdminTools && (
            <div className="px-3 pb-2 space-y-1 border-t border-white/5 pt-2" data-testid="admin-tools-panel">
              <div className="grid grid-cols-2 gap-1">
                <button onClick={() => setShowVisualizations(true)} className="flex items-center gap-1.5 px-2.5 py-2 bg-white/5 hover:bg-white/10 rounded-md transition-colors" data-testid="open-visualizations-btn">
                  <BarChart3 className="w-3 h-3" style={{ color: ESY.pink }} />
                  <span className="text-[10px] text-white/80">Analytics</span>
                </button>
                <button onClick={() => setShowRetention(true)} className="flex items-center gap-1.5 px-2.5 py-2 bg-white/5 hover:bg-white/10 rounded-md transition-colors" data-testid="open-retention-btn">
                  <Shield className="w-3 h-3" style={{ color: ESY.deepRed }} />
                  <span className="text-[10px] text-white/80">Retention</span>
                </button>
                <button onClick={() => setShowAuditLog(true)} className="flex items-center gap-1.5 px-2.5 py-2 bg-white/5 hover:bg-white/10 rounded-md transition-colors" data-testid="open-audit-btn">
                  <ClipboardList className="w-3 h-3" style={{ color: ESY.turquoise }} />
                  <span className="text-[10px] text-white/80">Audit Log</span>
                </button>
                <button onClick={() => setShowCompliance(true)} className="flex items-center gap-1.5 px-2.5 py-2 bg-white/5 hover:bg-white/10 rounded-md transition-colors" data-testid="open-compliance-btn">
                  <Globe className="w-3 h-3" style={{ color: '#00B894' }} />
                  <span className="text-[10px] text-white/80">Compliance</span>
                </button>
                <button onClick={() => setShowShortcuts(true)} className="flex items-center gap-1.5 px-2.5 py-2 bg-white/5 hover:bg-white/10 rounded-md transition-colors" data-testid="open-shortcuts-btn">
                  <Keyboard className="w-3 h-3 text-white/60" />
                  <span className="text-[10px] text-white/80">Shortcuts</span>
                </button>
                <button onClick={() => navigate('/karau-meet')} className="flex items-center gap-1.5 px-2.5 py-2 bg-white/5 hover:bg-white/10 rounded-md transition-colors" data-testid="switch-to-karau-footer">
                  <Building2 className="w-3 h-3" style={{ color: ESY.turquoise }} />
                  <span className="text-[10px] text-white/80">AI KARAU</span>
                </button>
              </div>
              <button onClick={() => navigate('/')} className="w-full flex items-center justify-center gap-1.5 px-2.5 py-1.5 bg-white/5 hover:bg-white/10 rounded-md transition-colors" data-testid="return-to-portal">
                <ArrowLeft className="w-3 h-3 text-white/60" />
                <span className="text-[10px] text-white/80">Return to Portal</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Content Area */}
      {activeChannel ? (
      <div className={`${!mobileSidebar ? 'flex' : 'hidden'} md:flex flex-col flex-1 min-w-0 bg-white lumi-light-panel`}>
        <>
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
              <button onClick={() => setShowScheduleModal(true)} className="p-2 rounded-md text-slate-500 hover:text-amber-600 hover:bg-amber-50 transition-colors" data-testid="schedule-msg-btn" title="Schedule Message"><Clock className="w-4 h-4" /></button>
              <button onClick={() => setShowMeetingModal(true)} className="p-2 rounded-md text-slate-500 hover:text-[#6C5CE7] hover:bg-[#6C5CE7]/5 transition-colors" data-testid="start-meeting-btn" title="Start AI KARAU Meeting"><Video className="w-4 h-4" /></button>
              <button onClick={() => setShowSummary(!showSummary)} className={`p-2 rounded-md transition-colors ${showSummary ? 'text-violet-600 bg-violet-50' : 'text-slate-500 hover:text-violet-600 hover:bg-violet-50'}`} data-testid="summarize-channel-btn" title="Summarize Conversation"><ClipboardList className="w-4 h-4" /></button>
              <button onClick={() => setShowNotifSettings(true)} className="p-2 rounded-md text-slate-500 hover:text-slate-700 hover:bg-slate-100 transition-colors" data-testid="notif-settings-btn" title="Notification Settings"><BellOff className="w-4 h-4" /></button>
              <button onClick={() => setShowMembers(!showMembers)} className={`p-2 rounded-md transition-colors ${showMembers ? 'text-[#008080] bg-[#008080]/5' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100'}`} data-testid="channel-members-btn"><Users className="w-4 h-4" /></button>
            </div>
          </div>

          {/* Bot Actions Bar - quick triggers for installed bots */}
          {activeChannel?.channel_type !== 'dm' && (
            <BotActionsBar channelId={activeChannel?.id} token={token} />
          )}

          {/* E2EE Status for DMs */}
          <E2EEIndicator channelId={activeChannel?.id} token={token} isDm={activeChannel?.channel_type === 'dm'} />

          <div className="flex flex-1 overflow-hidden">
            <div className="flex-1 flex flex-col min-w-0">
              {/* Conversation Summary Panel */}
              {showSummary && activeChannel && (
                <div className="px-4 pt-3">
                  <ConversationSummary channelId={activeChannel.id} token={token} onClose={() => setShowSummary(false)} />
                </div>
              )}
              <ScrollArea className="flex-1 py-3">
                {messages.length === 0 && (
                  <div className="flex flex-col items-center justify-center h-full text-center px-6">
                    <LumiBrand variant="text-light" size="md" className="mb-4" />
                    <p className="text-slate-600 text-sm">{t('lumi.noMessages') || 'No messages yet. Start the conversation!'}</p>
                  </div>
                )}
                {messages.filter(m => !m.thread_parent_id).map((msg, i, arr) => {
                  const prevSameSender = i > 0 && arr[i - 1].sender_id === msg.sender_id && arr[i - 1].type !== 'system';
                  return <MessageBubble key={msg.id} msg={msg} isOwn={msg.sender_id === user?.user_id} prevSameSender={prevSameSender} onReact={handleReact} onThread={(id) => setShowThread(id)} onEdit={handleEditMessage} onDelete={handleDeleteMessage} token={token} />;
                })}
                <div ref={messagesEndRef} />
              </ScrollArea>

              {activeTyping.length > 0 && <div className="px-5 py-1"><span className="text-xs text-[#006666] font-medium animate-pulse">{activeTyping.join(', ')} typing...</span></div>}

              {/* AI Writing Toolbar */}
              <div className="px-4 py-1.5 border-t border-slate-100">
                <AIWritingToolbar
                  messageText={messageText}
                  onTextChange={setMessageText}
                  messages={messages}
                  channelName={activeChannel?.name || ''}
                  token={token}
                />
              </div>

              <div className="p-4 pt-2 border-t border-slate-100">
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
                    className={`p-2 rounded-md transition-colors ${messageText.trim() ? 'text-white hover:opacity-90' : 'text-slate-400'}`}
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
        </>
      </div>
      ) : (
      <div className={`${!mobileSidebar ? 'flex' : 'hidden'} md:flex flex-col flex-1 min-w-0 bg-[#0D1117] overflow-auto`}>
          <div className="flex-1 flex flex-col">
            {/* Enhanced Dashboard */}
            <div className="max-w-5xl mx-auto w-full p-6 md:p-10 space-y-6">
              {/* Hero */}
              <div className="text-center mb-2">
                <LumiBrand variant="inline-dark" size="md" showTagline className="justify-center" />
                <p className="text-slate-400 text-sm mt-3 font-outfit">Your intelligent command center</p>
              </div>

              {/* Pending Invites */}
              {pendingInvites.length > 0 && (
                <div className="bento-tile col-span-full" data-testid="pending-invites-panel">
                  <div className="flex items-center gap-2 mb-3">
                    <Bell className="w-3.5 h-3.5 text-amber-400" />
                    <p className="text-[10px] font-semibold text-amber-400 uppercase tracking-widest font-outfit">Pending Invites ({pendingInvites.length})</p>
                  </div>
                  <div className="space-y-2">
                    {pendingInvites.map(inv => (
                      <div key={inv.id} className="flex items-center gap-3 px-3 py-2.5 rounded-xl bg-white/[0.03] border border-white/5" data-testid={`invite-${inv.id}`}>
                        <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center flex-shrink-0">
                          <Hash className="w-4 h-4 text-amber-400" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-white font-medium truncate">#{inv.channel_name}</p>
                          <p className="text-[11px] text-slate-500">Invited by {inv.invited_by_name}</p>
                        </div>
                        <button onClick={() => handleInviteResponse(inv.id, 'accept')}
                          className="px-3 py-1.5 rounded-lg bg-[#00CEC9]/10 text-[#00CEC9] text-xs font-medium hover:bg-[#00CEC9]/20 transition-colors" data-testid={`accept-invite-${inv.id}`}>
                          Accept
                        </button>
                        <button onClick={() => handleInviteResponse(inv.id, 'decline')}
                          className="px-3 py-1.5 rounded-lg bg-white/5 text-slate-400 text-xs font-medium hover:bg-white/10 transition-colors" data-testid={`decline-invite-${inv.id}`}>
                          Decline
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Quick Actions Row */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
                <button onClick={() => setShowNewDmModal(true)} className="bento-tile col-span-1 flex flex-col items-start gap-3 cursor-pointer group hover-lift animate-stagger-in-1" data-testid="bento-new-dm">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-teal-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
                    <UserPlus className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <p className="text-white text-sm font-semibold font-outfit">Direct Message</p>
                    <p className="text-slate-500 text-[11px] mt-0.5">Reach someone directly</p>
                  </div>
                </button>

                <button onClick={() => setShowCommandBar(true)} className="bento-tile col-span-1 flex flex-col items-start gap-3 cursor-pointer group hover-lift animate-stagger-in-2" data-testid="bento-command">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-slate-600 to-slate-700 flex items-center justify-center shadow-lg shadow-slate-500/20">
                    <Command className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <p className="text-white text-sm font-semibold font-outfit">Command Bar</p>
                    <p className="text-slate-500 text-[11px] mt-0.5">Ctrl+K to search</p>
                  </div>
                </button>

                <button onClick={() => setShowVisualizations(true)} className="bento-tile col-span-1 flex flex-col items-start gap-3 cursor-pointer group hover-lift animate-stagger-in-3" data-testid="bento-viz">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
                    <BarChart3 className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <p className="text-white text-sm font-semibold font-outfit">Analytics</p>
                    <p className="text-slate-500 text-[11px] mt-0.5">View insights & data</p>
                  </div>
                </button>

                <button onClick={() => setShowCreateModal(true)} className="bento-tile col-span-1 flex flex-col items-start gap-3 cursor-pointer group hover-lift animate-stagger-in-4" data-testid="bento-create-channel">
                  <div className="w-10 h-10 rounded-xl lumi-gradient flex items-center justify-center shadow-lg shadow-violet-500/20">
                    <Plus className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <p className="text-white text-sm font-semibold font-outfit">New Channel</p>
                    <p className="text-slate-500 text-[11px] mt-0.5">Settings & invites</p>
                  </div>
                </button>
              </div>

              {/* KARAU Meeting Quick Action */}
              <button onClick={() => setShowMeetingModal(true)} className="bento-tile w-full flex items-center gap-4 cursor-pointer group hover:border-[#6C5CE7]/20 transition-all" data-testid="bento-start-meeting">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center shadow-lg flex-shrink-0" style={{ background: 'linear-gradient(135deg, #6C5CE7, #00CEC9)' }}>
                  <Video className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-white text-sm font-semibold font-outfit">AI KARAU Meeting</p>
                  <p className="text-slate-500 text-[11px] mt-0.5">Start an instant or scheduled meeting from ENZI</p>
                </div>
                <ArrowLeft className="w-4 h-4 text-slate-600 rotate-180 group-hover:translate-x-1 transition-transform" />
              </button>

              {/* Invite to ENZI - Dashboard CTA */}
              <button onClick={() => setShowInviteModal(true)}
                className="bento-tile w-full flex items-center gap-4 cursor-pointer group hover:border-[#00CEC9]/20 transition-all"
                data-testid="bento-invite">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center shadow-lg flex-shrink-0"
                  style={{ background: 'linear-gradient(135deg, #00CEC9, #6C5CE7)' }}>
                  <Share2 className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-white text-sm font-semibold font-outfit">Invite to ENZI</p>
                  <p className="text-slate-500 text-[11px] mt-0.5">Share via email, SMS, LinkedIn, or link. Invitees must register first.</p>
                </div>
                <ArrowLeft className="w-4 h-4 text-slate-600 rotate-180 group-hover:translate-x-1 transition-transform" />
              </button>

              {/* Bot Store + Meeting History Row */}
              <div className="grid grid-cols-2 gap-3">
                <button onClick={() => setShowBotStore(true)} className="bento-tile flex flex-col items-start gap-3 cursor-pointer group hover:border-[#00CEC9]/20 transition-all" data-testid="bento-bot-store">
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center shadow-lg" style={{ background: 'linear-gradient(135deg, #00CEC9, #0984E3)' }}>
                    <Brain className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <p className="text-white text-sm font-semibold font-outfit">Bot Store</p>
                    <p className="text-slate-500 text-[11px] mt-0.5">Browse & install bots</p>
                  </div>
                </button>
                <button onClick={() => setShowMeetingHistory(true)} className="bento-tile flex flex-col items-start gap-3 cursor-pointer group hover:border-[#6C5CE7]/20 transition-all" data-testid="bento-meeting-history">
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center shadow-lg" style={{ background: 'linear-gradient(135deg, #6C5CE7, #E84393)' }}>
                    <Clock className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <p className="text-white text-sm font-semibold font-outfit">Meeting History</p>
                    <p className="text-slate-500 text-[11px] mt-0.5">Past & scheduled meetings</p>
                  </div>
                </button>
              </div>

              {/* Main Content Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 md:gap-4">
                {/* Recent Conversations — Channels + DMs combined */}
                <div className="bento-tile" data-testid="recent-conversations-panel">
                  <div className="flex items-center gap-2 mb-3">
                    <MessageCircle className="w-3.5 h-3.5 text-cyan-400" />
                    <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest font-outfit">Recent Conversations</p>
                  </div>
                  <div className="space-y-1">
                    {/* Mix channels and DMs, sorted by recent activity */}
                    {[
                      ...channels.slice(0, 4).map(ch => ({ ...ch, _type: 'channel' })),
                      ...dms.slice(0, 3).map(dm => ({ ...dm, _type: 'dm' })),
                    ].slice(0, 6).map(item => (
                      <button key={item.id} onClick={() => { setActiveChannel(item); setMobileSidebar(false); }}
                        className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-xl hover:bg-white/5 transition-all group text-left"
                        data-testid={`recent-conv-${item.id}`}>
                        {item._type === 'dm' ? (
                          <div className="relative w-7 h-7 flex-shrink-0">
                            <div className="w-7 h-7 rounded-full bg-slate-600 flex items-center justify-center text-[10px] font-semibold text-white">
                              {(item.dm_partner?.name || item.dm_partner?.email || '?')[0].toUpperCase()}
                            </div>
                            <span className={`absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full ring-1 ring-[#0D1117] ${
                              presenceMap[item.dm_partner?.user_id] === 'online' ? 'bg-emerald-500' : 'bg-slate-600'
                            }`} />
                          </div>
                        ) : (
                          <div className="w-7 h-7 rounded-lg bg-white/5 flex items-center justify-center flex-shrink-0 group-hover:bg-white/10 transition-colors">
                            <Hash className="w-3.5 h-3.5 text-violet-400" />
                          </div>
                        )}
                        <div className="flex-1 min-w-0">
                          <span className="text-sm text-white/80 group-hover:text-white truncate font-medium block">
                            {item._type === 'dm' ? (item.dm_partner?.name || item.dm_partner?.email || 'User') : item.name}
                          </span>
                          {item.last_message && (
                            <p className="text-[10px] text-slate-600 truncate">{typeof item.last_message === 'string' ? item.last_message : item.last_message?.content || ''}</p>
                          )}
                        </div>
                        {unreadCounts[item.id] > 0 && (
                          <span className="min-w-[18px] h-[18px] flex items-center justify-center rounded-full text-[9px] font-bold text-white" style={{ backgroundColor: ESY.pink }}>
                            {unreadCounts[item.id]}
                          </span>
                        )}
                      </button>
                    ))}
                    {channels.length === 0 && dms.length === 0 && (
                      <p className="text-slate-600 text-xs py-3 text-center">No conversations yet. Start a DM or join a channel!</p>
                    )}
                  </div>
                </div>

                {/* Right Column: AI Status + Smart Buckets */}
                <div className="space-y-3 md:space-y-4">
                  {/* AI Status + Calendar Widget */}
                  <div className="bento-tile">
                    <div className="flex items-center gap-2 mb-3">
                      <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                      <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest font-outfit">Status & Intelligence</p>
                    </div>
                    {/* Calendar Status */}
                    <div className="flex items-center gap-2.5 px-2.5 py-2 rounded-xl bg-white/[0.03] mb-2" data-testid="calendar-status">
                      <div className={`w-2.5 h-2.5 rounded-full ${
                        calendarStatus.status === 'in_meeting' ? 'bg-red-500 animate-pulse' :
                        calendarStatus.status === 'ooo' ? 'bg-amber-500' : 'bg-emerald-500'
                      }`} />
                      <div className="flex-1 min-w-0">
                        <p className="text-xs text-white/80 font-medium capitalize">{calendarStatus.status.replace('_', ' ')}</p>
                        {calendarStatus.calendar_event && (
                          <p className="text-[10px] text-slate-500 truncate">{calendarStatus.calendar_event.subject}</p>
                        )}
                      </div>
                      {calendarStatus.microsoft_linked && (
                        <span className="text-[8px] px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400">MS Synced</span>
                      )}
                    </div>
                    <div className="grid grid-cols-3 gap-2">
                      <div className="text-center p-2 rounded-xl bg-white/[0.03]">
                        <p className="text-lg font-bold lumi-gradient-text font-outfit">92%</p>
                        <p className="text-[9px] text-slate-500 mt-0.5">Compliance</p>
                      </div>
                      <div className="text-center p-2 rounded-xl bg-white/[0.03]">
                        <p className="text-lg font-bold text-cyan-400 font-outfit">{channels.length}</p>
                        <p className="text-[9px] text-slate-500 mt-0.5">Channels</p>
                      </div>
                      <div className="text-center p-2 rounded-xl bg-white/[0.03]">
                        <p className="text-lg font-bold text-emerald-400 font-outfit">{dms.length}</p>
                        <p className="text-[9px] text-slate-500 mt-0.5">DMs</p>
                      </div>
                    </div>
                  </div>

                  {/* Smart Buckets Preview */}
                  <div className="bento-tile">
                    <div className="flex items-center gap-2 mb-3">
                      <ClipboardList className="w-3.5 h-3.5 text-pink-400" />
                      <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest font-outfit">Smart Buckets</p>
                    </div>
                    <div className="space-y-1.5">
                      {[
                        { key: 'urgent', label: 'Urgent', color: 'bg-red-500' },
                        { key: 'action_required', label: 'Action Required', color: 'bg-amber-500' },
                        { key: 'meeting_request', label: 'Meeting Requests', color: 'bg-blue-500' },
                      ].map(b => (
                        <button key={b.key} onClick={() => openBucket(b.key)}
                          className="w-full flex items-center gap-2.5 px-2 py-1.5 rounded-lg hover:bg-white/5 transition-colors text-left"
                          data-testid={`bucket-${b.key}`}>
                          <div className={`w-2 h-2 rounded-full ${b.color}`} />
                          <span className="text-xs text-white/70 flex-1">{b.label}</span>
                          <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${bucketCounts[b.key] > 0 ? 'bg-white/10 text-white font-medium' : 'bg-white/5 text-slate-600'}`}>
                            {bucketCounts[b.key] || 0}
                          </span>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Predicted Suggestions */}
              {(predictions.channels.length > 0 || predictions.dms.length > 0) && (
                <div className="bento-tile" data-testid="predicted-suggestions">
                  <div className="flex items-center gap-2 mb-3">
                    <Zap className="w-3.5 h-3.5 text-amber-400" />
                    <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest font-outfit">Suggested for You</p>
                  </div>
                  <div className="flex gap-2 overflow-x-auto pb-1">
                    {predictions.channels.slice(0, 3).map(s => {
                      const ch = channels.find(c => c.id === s.target_id);
                      return ch ? (
                        <button key={s.target_id} onClick={() => { setActiveChannel(ch); setMobileSidebar(false); trackAction('channel_visit', ch.id, ch.name); }}
                          className="flex-shrink-0 flex items-center gap-2 px-3 py-2 rounded-xl bg-white/[0.03] border border-white/5 hover:bg-white/5 transition-colors"
                          data-testid={`suggest-${s.target_id}`}>
                          <Hash className="w-3.5 h-3.5 text-violet-400" />
                          <span className="text-xs text-white/80">{s.target_name}</span>
                        </button>
                      ) : null;
                    })}
                    {predictions.dms.slice(0, 3).map(s => {
                      const dm = dms.find(d => d.id === s.target_id);
                      return dm ? (
                        <button key={s.target_id} onClick={() => { setActiveChannel(dm); setMobileSidebar(false); trackAction('dm_visit', dm.id, s.target_name); }}
                          className="flex-shrink-0 flex items-center gap-2 px-3 py-2 rounded-xl bg-white/[0.03] border border-white/5 hover:bg-white/5 transition-colors"
                          data-testid={`suggest-${s.target_id}`}>
                          <div className="w-5 h-5 rounded-full bg-slate-600 flex items-center justify-center text-[9px] text-white font-semibold">
                            {(s.target_name || '?')[0].toUpperCase()}
                          </div>
                          <span className="text-xs text-white/80">{s.target_name}</span>
                        </button>
                      ) : null;
                    })}
                  </div>
                </div>
              )}

              {/* Bucket Detail Panel */}
              {activeBucket && (
                <div className="bento-tile" data-testid="bucket-detail-panel">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <div className={`w-2.5 h-2.5 rounded-full ${
                        activeBucket === 'urgent' ? 'bg-red-500' : activeBucket === 'action_required' ? 'bg-amber-500' : 'bg-blue-500'
                      }`} />
                      <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest font-outfit">
                        {activeBucket.replace('_', ' ')} ({bucketMessages.length})
                      </p>
                    </div>
                    <button onClick={() => { setActiveBucket(null); setBucketMessages([]); }}
                      className="p-1 hover:bg-white/10 rounded"><X className="w-3.5 h-3.5 text-slate-500" /></button>
                  </div>
                  {bucketLoading ? (
                    <div className="flex justify-center py-4"><Loader2 className="w-5 h-5 text-slate-500 animate-spin" /></div>
                  ) : bucketMessages.length === 0 ? (
                    <p className="text-xs text-slate-600 text-center py-4">No messages in this bucket</p>
                  ) : (
                    <div className="space-y-2 max-h-[200px] overflow-auto">
                      {bucketMessages.map(msg => (
                        <div key={msg.id} className="flex items-start gap-2.5 px-2.5 py-2 rounded-lg bg-white/[0.03] border border-white/5 group">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-1.5 mb-0.5">
                              <span className="text-[10px] font-semibold text-white/80">{msg.sender_name}</span>
                              <span className="text-[9px] text-slate-600">#{msg.channel_name}</span>
                            </div>
                            <p className="text-xs text-white/60 leading-relaxed">{msg.content}</p>
                          </div>
                          <button onClick={() => dismissBucketItem(activeBucket, msg.id)}
                            className="p-1 opacity-0 group-hover:opacity-100 hover:bg-white/10 rounded transition-opacity flex-shrink-0"
                            data-testid={`dismiss-${msg.id}`}>
                            <X className="w-3 h-3 text-slate-500" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Keyboard hint */}
              <p className="text-center text-[11px] text-slate-600 font-outfit">
                Press <kbd className="px-1.5 py-0.5 bg-white/5 border border-white/10 rounded text-[10px] text-slate-400 font-mono">Ctrl+K</kbd> to search anything
              </p>
            </div>
          </div>
      </div>
      )}

      {showCreateModal && <CreateChannelModal onClose={() => setShowCreateModal(false)} onCreated={(ch) => { setChannels(prev => [ch, ...prev]); setActiveChannel(ch); setShowCreateModal(false); setMobileSidebar(false); }} token={token} />}
      {showNewDmModal && <NewDmModal onClose={() => setShowNewDmModal(false)} onSelect={handleStartDm} token={token} />}
      {showInviteModal && <InviteModal onClose={() => setShowInviteModal(false)} token={token} />}
      {showNewMsgPanel && <NewMessagePanel onClose={() => setShowNewMsgPanel(false)} onSelectUser={handleStartDm} onInvite={handleNewMsgInvite} token={token} />}
      {showScheduleModal && activeChannel && <ScheduleMessageModal channelId={activeChannel.id} channelName={activeChannel.name || ''} token={token} onClose={() => setShowScheduleModal(false)} />}
      {showMeetingModal && <EnziMeetingModal channelId={activeChannel?.id} channelName={activeChannel?.name || ''} token={token} onClose={() => setShowMeetingModal(false)} />}
      {showMeetingHistory && <MeetingHistoryPanel token={token} onClose={() => setShowMeetingHistory(false)} onStartMeeting={() => { setShowMeetingHistory(false); setShowMeetingModal(true); }} />}
      {showBotStore && <BotStoreModal token={token} channels={channels} onClose={() => setShowBotStore(false)} />}
      {showNotifSettings && <NotificationSettings token={token} channels={channels} onClose={() => setShowNotifSettings(false)} />}
      {showProfile && <UserProfileModal onClose={() => setShowProfile(false)} token={token} onStatusChange={(s) => {}} onThemeChange={(c) => setUserAccentColor(c)} />}
      {showRetention && <RetentionPanel onClose={() => setShowRetention(false)} token={token} />}
      {showAuditLog && <AdminAuditPanel isOpen={showAuditLog} onClose={() => setShowAuditLog(false)} token={token} />}
      {showCompliance && <CompliancePanel isOpen={showCompliance} onClose={() => setShowCompliance(false)} token={token} />}
      {showVisualizations && <VisualizationsPanel isOpen={showVisualizations} onClose={() => setShowVisualizations(false)} token={token} />}
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