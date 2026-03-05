import { useState, useEffect } from 'react';
import {
  Bell, MessageCircle, ListTodo, CheckCircle2,
  AlertTriangle, Activity, Zap, Loader2, X,
  AtSign, MessageSquare, Filter
} from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { API, ESY } from './constants';

const SOURCE_TABS = [
  { key: 'all', label: 'All' },
  { key: 'chat', label: 'Chat' },
  { key: 'ai', label: 'AI' },
];

export const NotificationsPanel = ({ onClose, token, onNavigate }) => {
  const [notifications, setNotifications] = useState([]);
  const [sources, setSources] = useState({});
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [activeSource, setActiveSource] = useState('all');

  const loadNotifications = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/lumi/notifications/hub`, { headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) {
        const d = await res.json();
        setNotifications(d.notifications || []);
        setSources(d.sources || {});
        setTotal(d.total || 0);
      }
    } catch (e) {}
    setLoading(false);
  };

  useEffect(() => { loadNotifications(); }, []);

  const filtered = activeSource === 'all'
    ? notifications
    : notifications.filter(n => n.source === activeSource);

  const priorityStyles = {
    critical: { bg: `${ESY.deepRed}08`, border: `${ESY.deepRed}20`, dot: ESY.deepRed, label: 'URGENT' },
    high: { bg: `${ESY.pink}08`, border: `${ESY.pink}20`, dot: ESY.pink, label: 'HIGH' },
    medium: { bg: '#FFF8E1', border: '#FFD54F30', dot: '#F9A825', label: 'MED' },
    low: { bg: `${ESY.turquoise}05`, border: `${ESY.turquoise}15`, dot: ESY.turquoise, label: 'LOW' },
  };

  const typeIcons = {
    mention: AtSign,
    anomaly: AlertTriangle,
    task: ListTodo,
    dm: MessageSquare,
    sentiment_warning: Activity,
    action_item: CheckCircle2,
  };

  return (
    <div className="w-[340px] border-l border-slate-200 bg-white flex flex-col h-full" data-testid="notifications-panel">
      <div className="h-14 flex items-center justify-between px-4 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <div className="relative">
            <Bell className="w-4 h-4" style={{ color: ESY.pink }} />
            {total > 0 && <span className="absolute -top-1.5 -right-1.5 w-3.5 h-3.5 rounded-full flex items-center justify-center text-[8px] font-bold text-white" style={{ backgroundColor: ESY.deepRed }}>{total > 9 ? '9+' : total}</span>}
          </div>
          <h3 className="text-sm font-bold text-slate-900">Notification Center</h3>
        </div>
        <button onClick={onClose} className="p-1 hover:bg-slate-100 rounded-md" data-testid="close-notifications"><X className="w-4 h-4 text-slate-500" /></button>
      </div>

      {/* Source summary badges */}
      <div className="px-4 py-2 border-b border-slate-100 flex items-center gap-2 overflow-x-auto">
        {SOURCE_TABS.map(tab => {
          const count = tab.key === 'all' ? total : Object.entries(sources).filter(([k]) => {
            if (tab.key === 'chat') return ['mentions', 'dms'].includes(k);
            if (tab.key === 'ai') return ['anomalies', 'tasks'].includes(k);
            return false;
          }).reduce((s, [, v]) => s + v, 0);
          return (
            <button key={tab.key} onClick={() => setActiveSource(tab.key)}
              className={`px-3 py-1.5 rounded-full text-[10px] font-semibold whitespace-nowrap transition-all ${
                activeSource === tab.key ? 'text-white shadow-sm' : 'bg-slate-50 text-slate-500 hover:bg-slate-100'
              }`}
              style={activeSource === tab.key ? { background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` } : {}}
              data-testid={`notif-tab-${tab.key}`}>
              {tab.label} {count > 0 && `(${count})`}
            </button>
          );
        })}
        <div className="flex-1" />
        <div className="flex gap-1.5 text-[9px] text-slate-400">
          {sources.mentions > 0 && <span className="flex items-center gap-0.5"><AtSign className="w-2.5 h-2.5" />{sources.mentions}</span>}
          {sources.anomalies > 0 && <span className="flex items-center gap-0.5"><AlertTriangle className="w-2.5 h-2.5" />{sources.anomalies}</span>}
          {sources.tasks > 0 && <span className="flex items-center gap-0.5"><ListTodo className="w-2.5 h-2.5" />{sources.tasks}</span>}
          {sources.dms > 0 && <span className="flex items-center gap-0.5"><MessageSquare className="w-2.5 h-2.5" />{sources.dms}</span>}
        </div>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-3 space-y-2">
          {loading ? (
            <div className="flex items-center justify-center py-8"><Loader2 className="w-5 h-5 animate-spin" style={{ color: ESY.pink }} /></div>
          ) : filtered.length === 0 ? (
            <div className="text-center py-8" data-testid="no-notifications">
              <CheckCircle2 className="w-10 h-10 mx-auto mb-2" style={{ color: ESY.turquoise }} />
              <p className="text-sm font-medium text-slate-700">All caught up!</p>
              <p className="text-xs text-slate-500 mt-1">No notifications right now</p>
            </div>
          ) : (
            filtered.map((notif) => {
              const ps = priorityStyles[notif.priority] || priorityStyles.low;
              const Icon = typeIcons[notif.type] || Zap;
              return (
                <button key={notif.id}
                  onClick={() => { if (notif.channel_id && onNavigate) onNavigate({ type: 'channel', id: notif.channel_id }); }}
                  className="w-full text-left p-3 rounded-lg border transition-all hover:shadow-sm"
                  style={{ backgroundColor: ps.bg, borderColor: ps.border }}
                  data-testid={`notif-${notif.id}`}>
                  <div className="flex items-start gap-2.5">
                    <div className="w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${ps.dot}15` }}>
                      <Icon className="w-3.5 h-3.5" style={{ color: ps.dot }} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1.5 mb-0.5">
                        <p className="text-xs font-semibold text-slate-800 truncate">{notif.title}</p>
                        <span className="text-[8px] font-bold px-1.5 py-0.5 rounded-full text-white flex-shrink-0" style={{ backgroundColor: ps.dot }}>{ps.label}</span>
                      </div>
                      <p className="text-[11px] text-slate-600 line-clamp-2">{notif.body}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-[9px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-500 capitalize">{notif.source}</span>
                        {notif.deadline && <span className="text-[9px]" style={{ color: ESY.deepRed }}>Due: {notif.deadline}</span>}
                        {notif.timestamp && <span className="text-[9px] text-slate-400">{new Date(notif.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>}
                      </div>
                    </div>
                  </div>
                </button>
              );
            })
          )}
          {filtered.length > 0 && (
            <button onClick={loadNotifications} className="w-full text-xs py-1.5 rounded-md hover:bg-slate-50" style={{ color: ESY.turquoise }} data-testid="refresh-notifications">Refresh</button>
          )}
        </div>
      </ScrollArea>
    </div>
  );
};
