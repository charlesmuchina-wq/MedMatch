/**
 * ENZI Prestige — Enterprise Team Messenger
 * Refactored: Main container imports sub-components from /components/Lumi/
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast, Toaster } from 'sonner';
import {
  Loader2, X
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useTranslation } from '@/utils/i18n';
import { useTheme } from '@/App';

import {
  ChannelIcon, StatusDot,
  CommandBar, CreateChannelModal, NewDmModal, LumiLogin,
  UserProfileModal, RetentionPanel,
  ShortcutsPanel, useKeyboardShortcuts,
  AdminAuditPanel, CompliancePanel,
  VisualizationsPanel,
  API, WS_URL
} from '@/components/Lumi';
import EnziSplash from '@/components/Lumi/EnziSplash';
import InviteModal from '@/components/Lumi/InviteModal';
import InviteRegistration from '@/components/Lumi/InviteRegistration';
import NewMessagePanel from '@/components/Lumi/NewMessagePanel';
import ScheduleMessageModal from '@/components/Lumi/ScheduleMessageModal';
import NotificationSettings from '@/components/Lumi/NotificationSettings';
import EnziMeetingModal from '@/components/Lumi/EnziMeetingModal';
import MeetingHistoryPanel from '@/components/Lumi/MeetingHistoryPanel';
import BotStoreModal from '@/components/Lumi/BotStoreModal';
import ChannelToolsModal from '@/components/Lumi/ChannelToolsModal';
import AdminApprovalPanel from '@/components/Lumi/AdminApprovalPanel';
import EnziSidebar from '@/components/Lumi/EnziSidebar';
import EnziDashboard from '@/components/Lumi/EnziDashboard';
import EnziChatView from '@/components/Lumi/EnziChatView';
import PremiumModal from '@/components/Lumi/PremiumModal';
import InsightsPanel from '@/components/Lumi/InsightsPanel';
import TeamAnalyticsDashboard from '@/components/Lumi/TeamAnalyticsDashboard';
import MobileBottomNav from '@/components/Lumi/MobileBottomNav';

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
  const [mobileNavTab, setMobileNavTab] = useState('channels');
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
      const res = await fetch(`${API}/api/lumi/behavior/predict-channels`, { headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) {
        const data = await res.json();
        // Map predict-channels response to the format the sidebar expects
        const channelPreds = (data.predictions || []).map(p => ({ target_id: p.channel_id, score: p.prediction_score }));
        setPredictions({ channels: channelPreds, dms: [], suggestion: data.suggestion });
      }
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

  // Sync browser timezone for the daily digest schedule
  useEffect(() => {
    if (!user) return;
    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
    if (tz) {
      fetch(`${API}/api/agents/digest/preferences`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ timezone: tz }),
      }).catch(() => {});
    }
  }, [user]);

  // WebSocket (stable: loaders via refs so the socket never churns on state updates)
  const activeChannelRef = useRef(null);
  useEffect(() => { activeChannelRef.current = activeChannel; }, [activeChannel]);
  const wsLoadersRef = useRef({});
  useEffect(() => { wsLoadersRef.current = { loadChannels, loadDms, loadUnreadCounts }; });
  useEffect(() => {
    if (!user) return;
    let disposed = false;
    const connectWs = () => {
      if (disposed) return;
      const ws = new WebSocket(`${WS_URL}/api/lumi/ws/${user.user_id}`);
      wsRef.current = ws;
      ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.type === 'message') {
          if (msg.data.channel_id === activeChannelRef.current?.id) {
            setMessages(prev => prev.some(m => m.id === msg.data.id) ? prev : [...prev, msg.data]);
          }
          const { loadChannels: lc, loadDms: ld, loadUnreadCounts: lu } = wsLoadersRef.current;
          lc?.(); ld?.(); lu?.();
        } else if (msg.type === 'reaction') {
          setMessages(prev => prev.map(m => m.id === msg.data.message_id ? { ...m, reactions: msg.data.reactions } : m));
        } else if (msg.type === 'thread_reply') {
          setMessages(prev => prev.map(m => m.id === msg.data.parent_id ? { ...m, thread_count: (m.thread_count || 0) + 1 } : m));
        } else if (msg.type === 'message_edited') {
          setMessages(prev => prev.map(m => m.id === msg.data.message_id ? { ...m, content: msg.data.content, edited: true, edited_at: msg.data.edited_at } : m));
        } else if (msg.type === 'message_deleted') {
          setMessages(prev => prev.filter(m => m.id !== msg.data.message_id));
        } else if (msg.type === 'dm_created') {
          wsLoadersRef.current.loadDms?.();
        } else if (msg.type === 'presence_change') {
          setPresenceMap(prev => ({ ...prev, [msg.data.user_id]: msg.data.status }));
        } else if (msg.type === 'typing') {
          setTypingUsers(prev => ({ ...prev, [msg.data.channel_id]: { ...(prev[msg.data.channel_id] || {}), [msg.data.user_id]: msg.data.name || msg.data.user_id } }));
          setTimeout(() => setTypingUsers(prev => { const ch = { ...(prev[msg.data.channel_id] || {}) }; delete ch[msg.data.user_id]; return { ...prev, [msg.data.channel_id]: ch }; }), 3000);
        }
      };
      ws.onclose = () => { if (!disposed) setTimeout(connectWs, 3000); };
    };
    connectWs();
    return () => { disposed = true; const ws = wsRef.current; if (ws) { ws.onclose = null; ws.close(); } };
  }, [user]);

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
    try {
      await fetch(`${API}/api/lumi/channels/${activeChannel.id}/messages`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }, body: JSON.stringify({ content: text }) });
      const aiMatch = text.match(/^@ai\s+(.+)/is);
      if (aiMatch) {
        toast('✨ ENZI AI is thinking…');
        fetch(`${API}/api/lumi/channels/${activeChannel.id}/ai`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }, body: JSON.stringify({ query: aiMatch[1].trim() }) })
          .then(async r => { if (!r.ok) { const err = await r.json().catch(() => ({})); toast.error(err.detail || 'ENZI AI could not respond'); } })
          .catch(() => toast.error('ENZI AI could not respond'));
      }
    } catch (e) { toast.error('Failed'); setMessageText(text); }
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
      <EnziChatView
        activeChannel={activeChannel} user={user} token={token}
        messages={messages} messageText={messageText} setMessageText={setMessageText}
        sending={sending} uploading={uploading} presenceMap={presenceMap} activeTyping={activeTyping}
        showAiPanel={showAiPanel} setShowAiPanel={setShowAiPanel}
        showAiChat={showAiChat} setShowAiChat={setShowAiChat}
        showAlerts={showAlerts} setShowAlerts={setShowAlerts}
        showKnowledgeGraph={showKnowledgeGraph} setShowKnowledgeGraph={setShowKnowledgeGraph}
        showBottlenecks={showBottlenecks} setShowBottlenecks={setShowBottlenecks}
        showSimulation={showSimulation} setShowSimulation={setShowSimulation}
        showNotifications={showNotifications} setShowNotifications={setShowNotifications}
        showMembers={showMembers} setShowMembers={setShowMembers}
        showThread={showThread} setShowThread={setShowThread}
        showEmojiPicker={showEmojiPicker} setShowEmojiPicker={setShowEmojiPicker}
        showSummary={showSummary} setShowSummary={setShowSummary}
        showCommandBar={showCommandBar} setShowCommandBar={setShowCommandBar}
        setShowScheduleModal={setShowScheduleModal} setShowMeetingModal={setShowMeetingModal}
        setShowNotifSettings={setShowNotifSettings}
        handleSend={handleSend} handleReact={handleReact}
        handleEditMessage={handleEditMessage} handleDeleteMessage={handleDeleteMessage}
        handleStartCall={handleStartCall} handleFileShare={handleFileShare}
        handleKeyDown={handleKeyDown} handleTyping={handleTyping}
        handleEmojiSelect={handleEmojiSelect} closeAllPanels={closeAllPanels}
        messagesEndRef={messagesEndRef} fileInputRef={fileInputRef}
        setMobileSidebar={setMobileSidebar} mobileSidebar={mobileSidebar}
        channels={channels} dms={dms} setActiveChannel={setActiveChannel}
      />
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

      {/* Mobile Bottom Navigation */}
      <MobileBottomNav
        activeTab={mobileNavTab}
        onTabChange={(tab) => {
          setMobileNavTab(tab);
          if (tab === 'channels') { setMobileSidebar(true); setActiveChannel(null); }
          else if (tab === 'dms') { setMobileSidebar(true); }
          else if (tab === 'search') { setShowCommandBar(true); }
          else if (tab === 'ai') { if (activeChannel) setShowAiChat(true); else setShowBotStore(true); }
          else if (tab === 'profile') { setShowProfile(true); }
        }}
        unreadCount={Object.values(unreadCounts).reduce((a, b) => a + b, 0)}
        user={user}
      />
    </div>
  );
};

export default LumiMessenger;