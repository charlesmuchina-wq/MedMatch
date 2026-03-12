import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import {
  X, User, Loader2, ChevronDown, ChevronRight,
  Brain, Sparkles, Network, Zap, MessageSquare,
  Globe, Hash, Search, Bell, BellOff, Volume2,
  Activity, ListTodo, FileBarChart, AlertTriangle,
  TrendingDown, MessageCircle, Paperclip, Heart,
  Command, Languages
} from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { API, ESY, STATUS_LABELS } from './constants';

import { PasskeyManager } from './PasskeyManager';

const STATUS_OPTIONS = [
  { value: 'available', label: 'Available', color: 'bg-emerald-500', emoji: '🟢' },
  { value: 'busy', label: 'Busy', color: 'bg-amber-500', emoji: '🟡' },
  { value: 'in_meeting', label: 'In a meeting', color: 'bg-red-500', emoji: '🔴' },
  { value: 'ooo', label: 'Out of office', color: 'bg-red-500', emoji: '🚫' },
  { value: 'vacation', label: 'On vacation', color: 'bg-red-500', emoji: '🏖️' },
];

const FEATURE_ICONS = {
  sentiment: Activity,
  tasks: ListTodo,
  reports: FileBarChart,
  ask_ai: Sparkles,
  decision_cards: Zap,
  anomaly_alerts: AlertTriangle,
  knowledge_graph: Network,
  bottleneck_detection: TrendingDown,
  what_if: Zap,
  smart_notifications: Bell,
  translation: Languages,
  command_bar: Command,
  threading: MessageCircle,
  file_sharing: Paperclip,
  reactions: Heart,
};

const CATEGORY_META = {
  'Productivity AI': { icon: Brain, color: ESY.turquoise, bg: '#00CEC915', border: '#00CEC930' },
  'Actionable Intelligence': { icon: Sparkles, color: ESY.pink, bg: '#E8439315', border: '#E8439330' },
  'Graph Intelligence': { icon: Network, color: '#6C5CE7', bg: '#6C5CE715', border: '#6C5CE730' },
  'Advanced Collaboration': { icon: Zap, color: ESY.deepRed, bg: '#D6303115', border: '#D6303130' },
  'Communication': { icon: Globe, color: '#0984E3', bg: '#0984E315', border: '#0984E330' },
  'Navigation': { icon: Search, color: '#2D3436', bg: '#2D343612', border: '#2D343625' },
  'Core': { icon: MessageSquare, color: '#00B894', bg: '#00B89415', border: '#00B89430' },
};

const NOTIF_LEVELS = [
  { value: 'all', label: 'All messages', icon: Bell },
  { value: 'mentions', label: 'Mentions only', icon: Volume2 },
  { value: 'none', label: 'Nothing', icon: BellOff },
];

export const UserProfileModal = ({ onClose, token, onStatusChange, onThemeChange }) => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showStatusPicker, setShowStatusPicker] = useState(false);
  const [updatingStatus, setUpdatingStatus] = useState(false);
  const [expandedCategories, setExpandedCategories] = useState({});
  const [notifPrefs, setNotifPrefs] = useState({});
  const [accentColor, setAccentColor] = useState('');

  useEffect(() => { loadProfile(); loadTheme(); }, []);

  const loadProfile = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/lumi/profile/capabilities`, { headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) { const data = await res.json(); setProfile(data); setNotifPrefs(data.notification_preferences || {}); }
    } catch (e) { toast.error('Failed to load profile'); }
    setLoading(false);
  };

  const loadTheme = async () => {
    try {
      const res = await fetch(`${API}/api/lumi/profile/theme`, { headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) { const d = await res.json(); if (d.accent_color) setAccentColor(d.accent_color); }
    } catch (e) {}
  };

  const saveTheme = async (color) => {
    setAccentColor(color);
    onThemeChange?.(color);
    try {
      await fetch(`${API}/api/lumi/profile/theme`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ accent_color: color })
      });
      toast.success('Theme updated!');
    } catch (e) {}
  };

  const updateStatus = async (newStatus) => {
    setUpdatingStatus(true);
    try {
      const res = await fetch(`${API}/api/lumi/presence`, { method: 'PUT', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }, body: JSON.stringify({ status: newStatus }) });
      if (res.ok) { setProfile(prev => ({ ...prev, user: { ...prev.user, status: newStatus } })); onStatusChange?.(newStatus); toast.success(`Status: ${STATUS_LABELS[newStatus]}`); }
    } catch (e) { toast.error('Failed to update status'); }
    setUpdatingStatus(false); setShowStatusPicker(false);
  };

  const updateNotifPref = async (channelId, mute, level) => {
    try {
      await fetch(`${API}/api/lumi/profile/notification-prefs`, { method: 'PUT', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }, body: JSON.stringify({ channel_id: channelId, mute, level }) });
      setNotifPrefs(prev => ({ ...prev, [channelId]: { mute, level } }));
    } catch (e) { toast.error('Failed to update'); }
  };

  const toggleCategory = (cat) => setExpandedCategories(prev => ({ ...prev, [cat]: !prev[cat] }));

  const grouped = {};
  if (profile?.capabilities) {
    for (const cap of profile.capabilities) {
      if (!grouped[cap.category]) grouped[cap.category] = [];
      grouped[cap.category].push(cap);
    }
  }

  const currentStatusOption = STATUS_OPTIONS.find(s => s.value === profile?.user?.status) || STATUS_OPTIONS[0];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-white rounded-2xl w-full max-w-lg max-h-[85vh] shadow-2xl border border-slate-200 flex flex-col overflow-hidden" onClick={e => e.stopPropagation()} data-testid="user-profile-modal">

        {/* Header with Avatar */}
        <div className="px-6 pt-6 pb-5 border-b border-slate-100 flex-shrink-0 relative overflow-hidden">
          {/* Gradient bg */}
          <div className="absolute inset-0 opacity-[0.07]" style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink}, ${ESY.deepRed})` }} />

          <div className="relative">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-lg font-black text-gray-900 tracking-tight">My Profile</h2>
              <button onClick={onClose} className="p-1.5 hover:bg-black/5 rounded-lg transition-colors" data-testid="close-profile-modal">
                <X className="w-5 h-5 text-gray-600" />
              </button>
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-6"><Loader2 className="w-6 h-6 animate-spin" style={{ color: ESY.turquoise }} /></div>
            ) : profile && (
              <div className="flex items-center gap-4">
                {/* Highlighted Avatar with gradient ring */}
                <div className="relative">
                  <div className="w-16 h-16 rounded-2xl p-[2px] shadow-lg" style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink}, ${ESY.deepRed})` }}>
                    {profile.user.profile_picture ? (
                      <img src={profile.user.profile_picture} alt="" className="w-full h-full rounded-[14px] object-cover" />
                    ) : (
                      <div className="w-full h-full rounded-[14px] bg-white flex items-center justify-center">
                        <span className="text-xl font-black text-gray-800">{(profile.user.name || profile.user.email || '?')[0].toUpperCase()}</span>
                      </div>
                    )}
                  </div>
                  <span className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full ring-[3px] ring-white ${currentStatusOption.color}`} />
                </div>

                <div className="flex-1 min-w-0">
                  <h3 className="text-lg font-black text-gray-900 truncate">{profile.user.name || 'User'}</h3>
                  <p className="text-sm font-medium text-gray-700 truncate">{profile.user.email}</p>
                  <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                    <span className="text-[11px] px-2.5 py-1 rounded-full bg-gray-900 text-white font-bold uppercase tracking-wide" data-testid="profile-role-badge">{profile.user.role}</span>
                    {profile.user.auth_method === 'google' ? (
                      <span className="text-[11px] px-2.5 py-1 rounded-full bg-blue-100 text-blue-800 font-bold flex items-center gap-1" data-testid="profile-auth-badge">
                        <svg className="w-3 h-3" viewBox="0 0 24 24"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>
                        Google SSO
                      </span>
                    ) : profile.user.auth_method === 'microsoft' ? (
                      <span className="text-[11px] px-2.5 py-1 rounded-full bg-blue-50 text-blue-700 font-bold flex items-center gap-1" data-testid="profile-auth-badge">
                        <svg className="w-3 h-3" viewBox="0 0 24 24"><rect x="1" y="1" width="10" height="10" fill="#F25022"/><rect x="13" y="1" width="10" height="10" fill="#7FBA00"/><rect x="1" y="13" width="10" height="10" fill="#00A4EF"/><rect x="13" y="13" width="10" height="10" fill="#FFB900"/></svg>
                        Microsoft SSO
                      </span>
                    ) : profile.user.auth_method === 'github' ? (
                      <span className="text-[11px] px-2.5 py-1 rounded-full bg-gray-100 text-gray-800 font-bold flex items-center gap-1" data-testid="profile-auth-badge">
                        <svg className="w-3 h-3" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
                        GitHub SSO
                      </span>
                    ) : profile.user.auth_method === 'passkey' ? (
                      <span className="text-[11px] px-2.5 py-1 rounded-full bg-violet-50 text-violet-700 font-bold" data-testid="profile-auth-badge">Passkey Auth</span>
                    ) : (
                      <span className="text-[11px] px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 font-bold" data-testid="profile-auth-badge">Password Auth</span>
                    )}
                    <span className="text-[11px] px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-800 font-bold">{profile.user.messages_sent} msgs</span>
                  </div>
                </div>
              </div>
            )}

            {/* Status Picker */}
            {profile && (
              <div className="mt-4 relative">
                <button onClick={() => setShowStatusPicker(!showStatusPicker)}
                  className="w-full flex items-center justify-between px-4 py-3 bg-white border-2 border-slate-200 rounded-xl hover:border-slate-300 transition-colors shadow-sm"
                  data-testid="status-picker-trigger">
                  <div className="flex items-center gap-3">
                    <span className="text-base">{currentStatusOption.emoji}</span>
                    <span className="text-sm font-bold text-gray-900">{currentStatusOption.label}</span>
                  </div>
                  <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${showStatusPicker ? 'rotate-180' : ''}`} />
                </button>

                {showStatusPicker && (
                  <div className="absolute top-full left-0 right-0 mt-1 bg-white border-2 border-slate-200 rounded-xl shadow-xl z-10 py-1 overflow-hidden" data-testid="status-dropdown">
                    {STATUS_OPTIONS.map(opt => (
                      <button key={opt.value} onClick={() => updateStatus(opt.value)} disabled={updatingStatus}
                        className={`w-full flex items-center gap-3 px-4 py-2.5 text-left hover:bg-slate-50 transition-colors ${
                          profile.user.status === opt.value ? 'bg-slate-50' : ''
                        }`} data-testid={`status-${opt.value}`}>
                        <span className="text-base">{opt.emoji}</span>
                        <span className="text-sm font-semibold text-gray-800">{opt.label}</span>
                        {profile.user.status === opt.value && (
                          <span className="ml-auto text-[10px] font-black uppercase tracking-wider" style={{ color: ESY.turquoise }}>Current</span>
                        )}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Content */}
        <ScrollArea className="flex-1">
          {!loading && profile && (
            <div className="p-5 space-y-6">

              {/* Profile Theme Accent */}
              <div>
                <h3 className="text-sm font-black text-gray-900 mb-3 flex items-center gap-2">
                  <div className="w-6 h-6 rounded-lg flex items-center justify-center bg-gradient-to-br from-pink-400 to-violet-500">
                    <span className="text-white text-xs">🎨</span>
                  </div>
                  Profile Theme
                </h3>
                <div className="flex flex-wrap gap-2" data-testid="theme-color-picker">
                  {[
                    { color: '#00CEC9', name: 'Turquoise' },
                    { color: '#E84393', name: 'Pink' },
                    { color: '#D63031', name: 'Deep Red' },
                    { color: '#6C5CE7', name: 'Violet' },
                    { color: '#0984E3', name: 'Blue' },
                    { color: '#00B894', name: 'Emerald' },
                    { color: '#FDCB6E', name: 'Gold' },
                    { color: '#E17055', name: 'Coral' },
                    { color: '#2D3436', name: 'Charcoal' },
                    { color: '#636E72', name: 'Slate' },
                  ].map(t => (
                    <button key={t.color} onClick={() => saveTheme(t.color)} title={t.name}
                      className={`w-8 h-8 rounded-xl transition-all hover:scale-110 ${accentColor === t.color ? 'ring-[3px] ring-offset-2 ring-gray-900 scale-110' : 'ring-1 ring-black/10'}`}
                      style={{ backgroundColor: t.color }}
                      data-testid={`theme-${t.name.toLowerCase()}`} />
                  ))}
                </div>
                {accentColor && (
                  <div className="mt-2 flex items-center gap-2">
                    <span className="text-[11px] text-gray-600 font-medium">Preview:</span>
                    <div className="w-7 h-7 rounded-lg p-[2px]" style={{ background: `linear-gradient(135deg, ${accentColor}, ${ESY.pink})` }}>
                      <div className="w-full h-full rounded-[6px] bg-white flex items-center justify-center">
                        <span className="text-[10px] font-black" style={{ color: accentColor }}>A</span>
                      </div>
                    </div>
                    <span className="text-[10px] font-bold text-gray-500">{accentColor}</span>
                  </div>
                )}
              </div>

              {/* Security & Passkeys */}
              <PasskeyManager user={profile?.user} />

              {/* AI Capabilities */}
              <div>
                <h3 className="text-sm font-black text-gray-900 mb-3 flex items-center gap-2">
                  <div className="w-6 h-6 rounded-lg flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` }}>
                    <Brain className="w-3.5 h-3.5 text-white" />
                  </div>
                  ENZI Capabilities
                  <span className="text-[10px] px-2.5 py-0.5 rounded-full font-black text-white shadow-sm" style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` }}>
                    {profile.capabilities.length} features
                  </span>
                </h3>
                <div className="space-y-2">
                  {Object.entries(grouped).map(([category, caps]) => {
                    const meta = CATEGORY_META[category] || { icon: Brain, color: '#64748b', bg: '#64748b15', border: '#64748b30' };
                    const CatIcon = meta.icon;
                    const isExpanded = expandedCategories[category] !== false;
                    return (
                      <div key={category} className="rounded-xl overflow-hidden border-2 transition-colors" style={{ borderColor: isExpanded ? meta.border : '#e2e8f0' }} data-testid={`cap-category-${category.replace(/\s+/g, '-').toLowerCase()}`}>
                        <button onClick={() => toggleCategory(category)}
                          className="w-full flex items-center gap-3 px-3 py-3 hover:bg-slate-50 transition-colors text-left"
                          style={isExpanded ? { backgroundColor: meta.bg } : {}}>
                          <div className="w-8 h-8 rounded-lg flex items-center justify-center shadow-sm" style={{ backgroundColor: meta.color }}>
                            <CatIcon className="w-4 h-4 text-white" />
                          </div>
                          <div className="flex-1">
                            <span className="text-sm font-bold text-gray-900">{category}</span>
                            <span className="text-[10px] font-bold ml-2 px-2 py-0.5 rounded-full text-white" style={{ backgroundColor: meta.color }}>
                              {caps.length}
                            </span>
                          </div>
                          {isExpanded ? <ChevronDown className="w-4 h-4 text-gray-600" /> : <ChevronRight className="w-4 h-4 text-gray-600" />}
                        </button>
                        {isExpanded && (
                          <div className="px-3 pb-3 space-y-2 bg-white">
                            {caps.map(cap => {
                              const FeatureIcon = FEATURE_ICONS[cap.id] || Sparkles;
                              return (
                                <div key={cap.id} className="flex items-start gap-3 ml-2 p-2 rounded-lg hover:bg-slate-50 transition-colors" data-testid={`cap-${cap.id}`}>
                                  <div className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5" style={{ backgroundColor: `${meta.color}15`, border: `1px solid ${meta.color}30` }}>
                                    <FeatureIcon className="w-3.5 h-3.5" style={{ color: meta.color }} />
                                  </div>
                                  <div className="flex-1 min-w-0">
                                    <p className="text-xs font-bold text-gray-900">{cap.name}</p>
                                    <p className="text-[11px] text-gray-600 leading-relaxed mt-0.5">{cap.description}</p>
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Channel Subscriptions */}
              <div>
                <h3 className="text-sm font-black text-gray-900 mb-3 flex items-center gap-2">
                  <div className="w-6 h-6 rounded-lg flex items-center justify-center" style={{ backgroundColor: ESY.pink }}>
                    <Hash className="w-3.5 h-3.5 text-white" />
                  </div>
                  Channel Subscriptions
                  <span className="text-[10px] px-2.5 py-0.5 rounded-full font-black text-white shadow-sm" style={{ backgroundColor: ESY.pink }}>
                    {profile.channels.length} channels
                  </span>
                </h3>
                <div className="space-y-1.5">
                  {profile.channels.map(ch => {
                    const pref = notifPrefs[ch.id] || { mute: false, level: 'all' };
                    return (
                      <div key={ch.id} className="flex items-center gap-3 px-3 py-2.5 rounded-xl border-2 border-slate-100 hover:border-slate-200 transition-colors" data-testid={`ch-sub-${ch.id}`}>
                        <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center flex-shrink-0">
                          <Hash className="w-3.5 h-3.5 text-white" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-bold text-gray-900 truncate">{ch.name}</p>
                          <p className="text-[10px] text-gray-600 font-medium capitalize">{ch.channel_type}{ch.is_private ? ' · Private' : ''}</p>
                        </div>
                        <div className="flex items-center gap-1">
                          {NOTIF_LEVELS.map(level => {
                            const Icon = level.icon;
                            const isActive = pref.level === level.value;
                            return (
                              <button key={level.value}
                                onClick={() => updateNotifPref(ch.id, level.value === 'none', level.value)}
                                title={level.label}
                                className={`p-1.5 rounded-lg transition-all ${
                                  isActive
                                    ? 'text-white shadow-sm'
                                    : 'text-gray-400 hover:bg-slate-100 hover:text-gray-700'
                                }`}
                                style={isActive ? { backgroundColor: '#1e293b' } : {}}
                                data-testid={`notif-${ch.id}-${level.value}`}>
                                <Icon className="w-3.5 h-3.5" />
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    );
                  })}
                  {profile.channels.length === 0 && (
                    <p className="text-sm text-gray-600 text-center py-4 font-medium">No channel subscriptions yet</p>
                  )}
                </div>

                {profile.dm_count > 0 && (
                  <div className="mt-3 flex items-center gap-2.5 px-3 py-2.5 rounded-xl bg-slate-50 border-2 border-slate-100">
                    <div className="w-7 h-7 rounded-lg bg-slate-700 flex items-center justify-center">
                      <User className="w-3.5 h-3.5 text-white" />
                    </div>
                    <span className="text-xs text-gray-800 font-bold">{profile.dm_count} direct message conversation{profile.dm_count !== 1 ? 's' : ''}</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </ScrollArea>
      </div>
    </div>
  );
};
