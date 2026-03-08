import { useState, useEffect } from 'react';
import { X, Bell, BellOff, Moon, Plus, Trash2, Volume2, VolumeX, Hash } from 'lucide-react';
import { toast } from 'sonner';
import { API } from './constants';

const NotificationSettings = ({ token, channels, onClose }) => {
  const [prefs, setPrefs] = useState(null);
  const [loading, setLoading] = useState(true);
  const [newKeyword, setNewKeyword] = useState('');

  useEffect(() => { loadPrefs(); }, []);

  const loadPrefs = async () => {
    try {
      const res = await fetch(`${API}/api/lumi/notifications/preferences`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) setPrefs(await res.json());
    } catch {}
    setLoading(false);
  };

  const setChannelLevel = async (channelId, level) => {
    await fetch(`${API}/api/lumi/notifications/channel`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ channel_id: channelId, level })
    });
    setPrefs(p => ({ ...p, channel_prefs: { ...p.channel_prefs, [channelId]: level } }));
  };

  const toggleDND = async () => {
    const newDnd = { ...prefs.dnd, enabled: !prefs.dnd.enabled };
    await fetch(`${API}/api/lumi/notifications/dnd`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify(newDnd)
    });
    setPrefs(p => ({ ...p, dnd: newDnd }));
    toast.success(newDnd.enabled ? 'DND enabled' : 'DND disabled');
  };

  const addKeyword = async () => {
    if (!newKeyword.trim()) return;
    await fetch(`${API}/api/lumi/notifications/keywords`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ keyword: newKeyword.trim() })
    });
    setPrefs(p => ({ ...p, keyword_alerts: [...(p.keyword_alerts || []), newKeyword.trim().toLowerCase()] }));
    setNewKeyword('');
    toast.success('Keyword alert added');
  };

  const removeKeyword = async (kw) => {
    await fetch(`${API}/api/lumi/notifications/keywords/${kw}`, { method: 'DELETE', headers: { Authorization: `Bearer ${token}` } });
    setPrefs(p => ({ ...p, keyword_alerts: (p.keyword_alerts || []).filter(k => k !== kw) }));
  };

  if (loading) return null;

  const levels = [
    { id: 'all', label: 'All', icon: Bell, color: 'text-emerald-400' },
    { id: 'mentions', label: '@Mentions', icon: Volume2, color: 'text-amber-400' },
    { id: 'none', label: 'Muted', icon: VolumeX, color: 'text-red-400' },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" data-testid="notification-settings">
      <div className="w-full max-w-lg mx-4 bg-[#131920] border border-white/10 rounded-2xl shadow-2xl overflow-hidden max-h-[80vh] flex flex-col"
        style={{ animation: 'fadeInUp 0.3s ease-out' }}>
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/10 flex-shrink-0">
          <div className="flex items-center gap-2">
            <Bell className="w-4 h-4 text-[#00CEC9]" />
            <h2 className="text-sm font-semibold text-white">Notification Settings</h2>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-white/10 rounded-lg" data-testid="close-notif-settings">
            <X className="w-4 h-4 text-slate-400" />
          </button>
        </div>

        <div className="p-5 space-y-5 overflow-auto flex-1">
          {/* DND */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Moon className="w-4 h-4 text-indigo-400" />
                <span className="text-xs font-semibold text-white">Do Not Disturb</span>
              </div>
              <button onClick={toggleDND}
                className={`w-10 h-5 rounded-full transition-colors relative ${prefs?.dnd?.enabled ? 'bg-[#00CEC9]' : 'bg-white/10'}`}
                data-testid="dnd-toggle">
                <div className={`absolute top-0.5 w-4 h-4 bg-white rounded-full transition-transform ${prefs?.dnd?.enabled ? 'translate-x-5' : 'translate-x-0.5'}`} />
              </button>
            </div>
            {prefs?.dnd?.enabled && (
              <p className="text-[10px] text-slate-500">Quiet hours: {prefs.dnd.start_time} - {prefs.dnd.end_time} ({prefs.dnd.timezone})</p>
            )}
          </div>

          {/* Keyword Alerts */}
          <div>
            <span className="text-xs font-semibold text-white mb-2 block">Keyword Alerts</span>
            <p className="text-[10px] text-slate-500 mb-2">Get notified when these words appear in any message</p>
            <div className="flex gap-2 mb-2">
              <input value={newKeyword} onChange={e => setNewKeyword(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && addKeyword()}
                placeholder="Add keyword..."
                className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-white placeholder:text-slate-600 outline-none focus:border-[#00CEC9]/50"
                data-testid="keyword-input" />
              <button onClick={addKeyword}
                className="px-3 py-1.5 rounded-lg bg-[#00CEC9]/10 text-[#00CEC9] text-xs font-medium hover:bg-[#00CEC9]/20"
                data-testid="add-keyword-btn">
                <Plus className="w-3 h-3" />
              </button>
            </div>
            <div className="flex flex-wrap gap-1">
              {(prefs?.keyword_alerts || []).map(kw => (
                <span key={kw} className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-white/5 border border-white/10 text-[10px] text-white/70">
                  {kw}
                  <button onClick={() => removeKeyword(kw)} className="hover:text-red-400"><Trash2 className="w-2.5 h-2.5" /></button>
                </span>
              ))}
            </div>
          </div>

          {/* Per-Channel */}
          <div>
            <span className="text-xs font-semibold text-white mb-2 block">Per-Channel Notifications</span>
            <div className="space-y-1.5 max-h-48 overflow-auto">
              {(channels || []).slice(0, 20).map(ch => {
                const current = prefs?.channel_prefs?.[ch.id] || 'all';
                return (
                  <div key={ch.id} className="flex items-center gap-2 px-2 py-1.5 rounded-lg bg-white/[0.02]">
                    <Hash className="w-3 h-3 text-slate-500 flex-shrink-0" />
                    <span className="text-xs text-white/70 flex-1 truncate">{ch.name}</span>
                    <div className="flex gap-0.5">
                      {levels.map(l => (
                        <button key={l.id} onClick={() => setChannelLevel(ch.id, l.id)}
                          className={`p-1 rounded ${current === l.id ? 'bg-white/10' : 'hover:bg-white/5'}`}
                          title={l.label} data-testid={`notif-${ch.id}-${l.id}`}>
                          <l.icon className={`w-3 h-3 ${current === l.id ? l.color : 'text-slate-600'}`} />
                        </button>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
      <style>{`
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(16px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
};

export default NotificationSettings;
