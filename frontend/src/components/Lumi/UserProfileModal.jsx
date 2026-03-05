import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import {
  X, User, Loader2, ChevronDown, ChevronRight,
  Brain, Sparkles, Network, Zap, MessageSquare,
  Globe, Hash, Search, Bell, BellOff, Volume2
} from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { API, ESY, STATUS_LABELS } from './constants';

const STATUS_OPTIONS = [
  { value: 'available', label: 'Available', color: 'bg-emerald-500' },
  { value: 'busy', label: 'Busy', color: 'bg-amber-500' },
  { value: 'in_meeting', label: 'In a meeting', color: 'bg-red-500' },
  { value: 'ooo', label: 'Out of office', color: 'bg-red-500' },
  { value: 'vacation', label: 'On vacation', color: 'bg-red-500' },
];

const CATEGORY_ICONS = {
  'Productivity AI': Brain,
  'Actionable Intelligence': Sparkles,
  'Graph Intelligence': Network,
  'Advanced Collaboration': Zap,
  'Communication': Globe,
  'Navigation': Search,
  'Core': MessageSquare,
};

const CATEGORY_COLORS = {
  'Productivity AI': ESY.turquoise,
  'Actionable Intelligence': ESY.pink,
  'Graph Intelligence': '#6C5CE7',
  'Advanced Collaboration': ESY.deepRed,
  'Communication': '#0984E3',
  'Navigation': '#636E72',
  'Core': '#2D3436',
};

const NOTIF_LEVELS = [
  { value: 'all', label: 'All messages', icon: Bell },
  { value: 'mentions', label: 'Mentions only', icon: Volume2 },
  { value: 'none', label: 'Nothing', icon: BellOff },
];

export const UserProfileModal = ({ onClose, token, onStatusChange }) => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showStatusPicker, setShowStatusPicker] = useState(false);
  const [updatingStatus, setUpdatingStatus] = useState(false);
  const [expandedCategories, setExpandedCategories] = useState({});
  const [notifPrefs, setNotifPrefs] = useState({});

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/lumi/profile/capabilities`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setProfile(data);
        setNotifPrefs(data.notification_preferences || {});
      }
    } catch (e) {
      toast.error('Failed to load profile');
    }
    setLoading(false);
  };

  const updateStatus = async (newStatus) => {
    setUpdatingStatus(true);
    try {
      const res = await fetch(`${API}/api/lumi/presence`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ status: newStatus })
      });
      if (res.ok) {
        setProfile(prev => ({ ...prev, user: { ...prev.user, status: newStatus } }));
        onStatusChange?.(newStatus);
        toast.success(`Status: ${STATUS_LABELS[newStatus]}`);
      }
    } catch (e) {
      toast.error('Failed to update status');
    }
    setUpdatingStatus(false);
    setShowStatusPicker(false);
  };

  const updateNotifPref = async (channelId, mute, level) => {
    try {
      await fetch(`${API}/api/lumi/profile/notification-prefs`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ channel_id: channelId, mute, level })
      });
      setNotifPrefs(prev => ({ ...prev, [channelId]: { mute, level } }));
    } catch (e) {
      toast.error('Failed to update');
    }
  };

  const toggleCategory = (cat) => {
    setExpandedCategories(prev => ({ ...prev, [cat]: !prev[cat] }));
  };

  // Group capabilities by category
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
      <div className="bg-white rounded-xl w-full max-w-lg max-h-[85vh] shadow-2xl border border-slate-200 flex flex-col overflow-hidden" onClick={e => e.stopPropagation()} data-testid="user-profile-modal">

        {/* Header */}
        <div className="px-6 py-5 border-b border-slate-100 flex-shrink-0" style={{ background: `linear-gradient(135deg, ${ESY.turquoise}08, ${ESY.pink}08)` }}>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-slate-900">My Profile</h2>
            <button onClick={onClose} className="p-1.5 hover:bg-slate-100 rounded-lg transition-colors" data-testid="close-profile-modal">
              <X className="w-5 h-5 text-slate-500" />
            </button>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-4">
              <Loader2 className="w-6 h-6 animate-spin" style={{ color: ESY.turquoise }} />
            </div>
          ) : profile && (
            <div className="flex items-center gap-4">
              {profile.user.profile_picture ? (
                <img src={profile.user.profile_picture} alt="" className="w-14 h-14 rounded-xl object-cover shadow-md" />
              ) : (
                <div className="w-14 h-14 rounded-xl flex items-center justify-center text-white text-lg font-bold shadow-md"
                  style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` }}>
                  {(profile.user.name || profile.user.email || '?')[0].toUpperCase()}
                </div>
              )}
              <div className="flex-1 min-w-0">
                <h3 className="text-base font-bold text-slate-900 truncate">{profile.user.name || 'User'}</h3>
                <p className="text-sm text-slate-600 truncate">{profile.user.email}</p>
                <div className="flex items-center gap-3 mt-1">
                  <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-medium capitalize">{profile.user.role}</span>
                  {profile.user.auth_method === 'google' && <span className="text-[11px] px-2 py-0.5 rounded-full bg-blue-50 text-blue-600 font-medium">Google SSO</span>}
                  <span className="text-[11px] text-slate-500">{profile.user.messages_sent} messages sent</span>
                </div>
              </div>
            </div>
          )}

          {/* Status Picker */}
          {profile && (
            <div className="mt-4 relative">
              <button onClick={() => setShowStatusPicker(!showStatusPicker)}
                className="w-full flex items-center justify-between px-3 py-2.5 bg-white border border-slate-200 rounded-lg hover:border-slate-300 transition-colors"
                data-testid="status-picker-trigger">
                <div className="flex items-center gap-2.5">
                  <span className={`w-3 h-3 rounded-full ${currentStatusOption.color}`} />
                  <span className="text-sm font-medium text-slate-800">{currentStatusOption.label}</span>
                </div>
                <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform ${showStatusPicker ? 'rotate-180' : ''}`} />
              </button>

              {showStatusPicker && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-slate-200 rounded-lg shadow-xl z-10 py-1" data-testid="status-dropdown">
                  {STATUS_OPTIONS.map(opt => (
                    <button key={opt.value} onClick={() => updateStatus(opt.value)} disabled={updatingStatus}
                      className={`w-full flex items-center gap-2.5 px-3 py-2 text-left hover:bg-slate-50 transition-colors ${
                        profile.user.status === opt.value ? 'bg-slate-50' : ''
                      }`} data-testid={`status-${opt.value}`}>
                      <span className={`w-2.5 h-2.5 rounded-full ${opt.color}`} />
                      <span className="text-sm text-slate-700">{opt.label}</span>
                      {profile.user.status === opt.value && (
                        <span className="ml-auto text-[10px] font-semibold" style={{ color: ESY.turquoise }}>Current</span>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Content */}
        <ScrollArea className="flex-1">
          {!loading && profile && (
            <div className="p-5 space-y-6">

              {/* AI Capabilities */}
              <div>
                <h3 className="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
                  <Brain className="w-4 h-4" style={{ color: ESY.turquoise }} />
                  LUMI Capabilities
                  <span className="text-[10px] px-2 py-0.5 rounded-full font-semibold text-white" style={{ backgroundColor: ESY.turquoise }}>
                    {profile.capabilities.length} features
                  </span>
                </h3>
                <div className="space-y-2">
                  {Object.entries(grouped).map(([category, caps]) => {
                    const CatIcon = CATEGORY_ICONS[category] || Brain;
                    const catColor = CATEGORY_COLORS[category] || '#64748b';
                    const isExpanded = expandedCategories[category] !== false;
                    return (
                      <div key={category} className="border border-slate-100 rounded-lg overflow-hidden" data-testid={`cap-category-${category.replace(/\s+/g, '-').toLowerCase()}`}>
                        <button onClick={() => toggleCategory(category)}
                          className="w-full flex items-center gap-2.5 px-3 py-2.5 hover:bg-slate-50 transition-colors text-left">
                          <div className="w-7 h-7 rounded-md flex items-center justify-center" style={{ backgroundColor: `${catColor}12` }}>
                            <CatIcon className="w-3.5 h-3.5" style={{ color: catColor }} />
                          </div>
                          <div className="flex-1">
                            <span className="text-xs font-semibold text-slate-800">{category}</span>
                            <span className="text-[10px] text-slate-400 ml-2">{caps.length} features</span>
                          </div>
                          {isExpanded ? <ChevronDown className="w-3.5 h-3.5 text-slate-400" /> : <ChevronRight className="w-3.5 h-3.5 text-slate-400" />}
                        </button>
                        {isExpanded && (
                          <div className="px-3 pb-2 space-y-1.5">
                            {caps.map(cap => (
                              <div key={cap.id} className="flex items-start gap-2 pl-9" data-testid={`cap-${cap.id}`}>
                                <div className="w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0" style={{ backgroundColor: catColor }} />
                                <div>
                                  <p className="text-xs font-medium text-slate-700">{cap.name}</p>
                                  <p className="text-[10px] text-slate-500 leading-relaxed">{cap.description}</p>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Channel Subscriptions */}
              <div>
                <h3 className="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
                  <Hash className="w-4 h-4" style={{ color: ESY.pink }} />
                  Channel Subscriptions
                  <span className="text-[10px] px-2 py-0.5 rounded-full font-semibold text-white" style={{ backgroundColor: ESY.pink }}>
                    {profile.channels.length} channels
                  </span>
                </h3>
                <div className="space-y-1.5">
                  {profile.channels.map(ch => {
                    const pref = notifPrefs[ch.id] || { mute: false, level: 'all' };
                    const currentLevel = NOTIF_LEVELS.find(l => l.value === pref.level) || NOTIF_LEVELS[0];
                    const LevelIcon = currentLevel.icon;
                    return (
                      <div key={ch.id} className="flex items-center gap-3 px-3 py-2.5 rounded-lg border border-slate-100 hover:border-slate-200 transition-colors" data-testid={`ch-sub-${ch.id}`}>
                        <div className="w-8 h-8 rounded-md bg-slate-100 flex items-center justify-center flex-shrink-0">
                          <Hash className="w-3.5 h-3.5 text-slate-500" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-slate-800 truncate">{ch.name}</p>
                          <p className="text-[10px] text-slate-500 capitalize">{ch.channel_type}{ch.is_private ? ' (Private)' : ''}</p>
                        </div>

                        {/* Notification Level Selector */}
                        <div className="flex items-center gap-1">
                          {NOTIF_LEVELS.map(level => {
                            const Icon = level.icon;
                            const isActive = pref.level === level.value;
                            return (
                              <button key={level.value}
                                onClick={() => updateNotifPref(ch.id, level.value === 'none', level.value)}
                                title={level.label}
                                className={`p-1.5 rounded-md transition-all ${
                                  isActive
                                    ? 'bg-slate-800 text-white shadow-sm'
                                    : 'text-slate-400 hover:bg-slate-100 hover:text-slate-600'
                                }`}
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
                    <p className="text-sm text-slate-500 text-center py-4">No channel subscriptions yet</p>
                  )}
                </div>

                {profile.dm_count > 0 && (
                  <div className="mt-3 flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-50 border border-slate-100">
                    <User className="w-3.5 h-3.5 text-slate-500" />
                    <span className="text-xs text-slate-600">{profile.dm_count} direct message conversation{profile.dm_count !== 1 ? 's' : ''}</span>
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
