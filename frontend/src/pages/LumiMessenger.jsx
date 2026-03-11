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
  Sun, Moon, Share2, Clock, Edit, ChevronDown, ChevronRight, Settings, BellOff, Crown, TrendingUp, ShieldCheck
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
import ChannelToolsModal from '@/components/Lumi/ChannelToolsModal';
import MeetingChannelBanner from '@/components/Lumi/MeetingChannelBanner';
import AdminApprovalPanel from '@/components/Lumi/AdminApprovalPanel';
import BotActionsBar from '@/components/Lumi/BotActionsBar';
import EnziSidebar from '@/components/Lumi/EnziSidebar';
import EnziDashboard from '@/components/Lumi/EnziDashboard';
import E2EEIndicator from '@/components/Lumi/E2EEIndicator';
import PremiumModal from '@/components/Lumi/PremiumModal';
import InsightsPanel from '@/components/Lumi/InsightsPanel';
import TeamAnalyticsDashboard from '@/components/Lumi/TeamAnalyticsDashboard';

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
  const [showChannelTools, setShowChannelTools] = useState(false);
  const [showTeamAnalytics, setShowTeamAnalytics] = useState(false);
  const [showPremium, setShowPremium] = useState(false);
  const [showInsights, setShowInsights] = useState(false);
  const [showAdminApprovals, setShowAdminApprovals] = useState(false);

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
    // Check for payment redirect
    const urlParams = new URLSearchParams(window.location.search);
    const paymentStatus = urlParams.get('payment');
    const sessionId = urlParams.get('session_id');
    if (paymentStatus === 'success' && sessionId && token) {
      const pollStatus = async (attempts = 0) => {
        if (attempts >= 5) return;
        try {
          const res = await fetch(`${API}/api/lumi/payments/status/${sessionId}`, { headers: { Authorization: `Bearer ${token}` } });
          if (res.ok) {
            const data = await res.json();
            if (data.payment_status === 'paid') { toast.success('Payment successful! Welcome to ENZI Premium!'); window.history.replaceState({}, '', '/lumi'); return; }
          }
        } catch {}
        setTimeout(() => pollStatus(attempts + 1), 2000);
      };
      pollStatus();
    } else if (paymentStatus === 'cancelled') {
      toast.info('Payment cancelled.');
      window.history.replaceState({}, '', '/lumi');
    }
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
      <EnziSidebar
        mobileSidebar={mobileSidebar} sidebarView={sidebarView} setSidebarView={setSidebarView}
        searchQuery={searchQuery} setSearchQuery={setSearchQuery}
        globalSearch={globalSearch} setGlobalSearch={setGlobalSearch}
        showSearchResults={showSearchResults} setShowSearchResults={setShowSearchResults}
        searchResults={searchResults} handleGlobalSearch={handleGlobalSearch}
        recentConversations={recentConversations} sortedChannels={sortedChannels}
        discoverChannels={discoverChannels} dms={dms}
        activeChannel={activeChannel} setActiveChannel={setActiveChannel}
        setMobileSidebar={setMobileSidebar}
        unreadCounts={unreadCounts} presenceMap={presenceMap}
        predictedChannelIds={predictedChannelIds} bucketCounts={bucketCounts}
        openBucket={openBucket}
        setShowNewMsgPanel={setShowNewMsgPanel} setShowCreateModal={setShowCreateModal}
        setShowNewDmModal={setShowNewDmModal}
        setShowThread={setShowThread} setShowMembers={setShowMembers}
        setShowAiPanel={setShowAiPanel}
        showAdminTools={showAdminTools} setShowAdminTools={setShowAdminTools}
        isDark={isDark} toggleTheme={toggleTheme} user={user} navigate={navigate}
        channels={channels}
        setShowVisualizations={setShowVisualizations} setShowRetention={setShowRetention}
        setShowAuditLog={setShowAuditLog} setShowCompliance={setShowCompliance}
        setShowShortcuts={setShowShortcuts} setShowProfile={setShowProfile}
        handleJoinChannel={handleJoinChannel} handleStartDm={handleStartDm}
        trackAction={trackAction}
      />

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

          {/* Meeting Follow-up Channel Banner */}
          {activeChannel.channel_type === 'meeting-followup' && (
            <MeetingChannelBanner
              channel={activeChannel}
              token={token}
              isAdmin={activeChannel?.members?.some(m => m.user_id === user?.user_id && m.role === 'admin')}
            />
          )}

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
        <EnziDashboard
          mobileSidebar={mobileSidebar} user={user}
          channels={channels} dms={dms}
          unreadCounts={unreadCounts} presenceMap={presenceMap}
          bucketCounts={bucketCounts} predictions={predictions}
          calendarStatus={calendarStatus} pendingInvites={pendingInvites}
          activeBucket={activeBucket} bucketMessages={bucketMessages}
          bucketLoading={bucketLoading}
          setActiveChannel={setActiveChannel} setMobileSidebar={setMobileSidebar}
          setShowNewDmModal={setShowNewDmModal} setShowCommandBar={setShowCommandBar}
          setShowVisualizations={setShowVisualizations} setShowCreateModal={setShowCreateModal}
          setShowMeetingModal={setShowMeetingModal} setShowBotStore={setShowBotStore}
          setShowChannelTools={setShowChannelTools} setShowMeetingHistory={setShowMeetingHistory}
          setShowPremium={setShowPremium} setShowInsights={setShowInsights}
          setShowTeamAnalytics={setShowTeamAnalytics} setShowAdminApprovals={setShowAdminApprovals}
          openBucket={openBucket} dismissBucketItem={dismissBucketItem}
          setActiveBucket={setActiveBucket} setBucketMessages={setBucketMessages}
          handleInviteResponse={handleInviteResponse} trackAction={trackAction}
        />
      )}

      {showCreateModal && <CreateChannelModal onClose={() => setShowCreateModal(false)} onCreated={(ch) => { setChannels(prev => [ch, ...prev]); setActiveChannel(ch); setShowCreateModal(false); setMobileSidebar(false); }} token={token} />}
      {showNewDmModal && <NewDmModal onClose={() => setShowNewDmModal(false)} onSelect={handleStartDm} token={token} />}
      {showInviteModal && <InviteModal onClose={() => setShowInviteModal(false)} token={token} />}
      {showNewMsgPanel && <NewMessagePanel onClose={() => setShowNewMsgPanel(false)} onSelectUser={handleStartDm} onInvite={handleNewMsgInvite} token={token} />}
      {showScheduleModal && activeChannel && <ScheduleMessageModal channelId={activeChannel.id} channelName={activeChannel.name || ''} token={token} onClose={() => setShowScheduleModal(false)} />}
      {showMeetingModal && <EnziMeetingModal channelId={activeChannel?.id} channelName={activeChannel?.name || ''} token={token} onClose={() => setShowMeetingModal(false)} />}
      {showMeetingHistory && <MeetingHistoryPanel token={token} onClose={() => setShowMeetingHistory(false)} onStartMeeting={() => { setShowMeetingHistory(false); setShowMeetingModal(true); }} />}
      {showBotStore && <BotStoreModal token={token} channels={channels} onClose={() => setShowBotStore(false)} />}
      {showChannelTools && <ChannelToolsModal token={token} channels={channels} onClose={() => setShowChannelTools(false)} onChannelCreated={(ch) => { setChannels(prev => [...prev, ch]); setShowChannelTools(false); }} />}
      {showTeamAnalytics && <TeamAnalyticsDashboard token={token} onClose={() => setShowTeamAnalytics(false)} />}
      {showPremium && <PremiumModal token={token} onClose={() => setShowPremium(false)} />}
      {showInsights && <InsightsPanel token={token} onClose={() => setShowInsights(false)} onAction={(action) => { setShowInsights(false); if (action === 'create_meeting') setShowMeetingModal(true); }} />}
      {showAdminApprovals && <AdminApprovalPanel token={token} onClose={() => setShowAdminApprovals(false)} />}
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