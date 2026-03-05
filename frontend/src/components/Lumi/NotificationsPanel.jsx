import { useState, useEffect } from 'react';
import {
  Bell, MessageCircle, ListTodo, CheckCircle2,
  AlertTriangle, Activity, Zap, Loader2, X
} from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { API, ESY } from './constants';

export const NotificationsPanel = ({ onClose, token, onNavigate }) => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadNotifications = async () => { setLoading(true); try { const res = await fetch(`${API}/api/lumi/ai/notifications`, { headers: { 'Authorization': `Bearer ${token}` } }); if (res.ok) { const d = await res.json(); setNotifications(d.notifications || []); } } catch (e) {} setLoading(false); };

  useEffect(() => { loadNotifications(); }, []);

  const priorityStyles = {
    critical: { bg: `${ESY.deepRed}08`, border: `${ESY.deepRed}20`, dot: ESY.deepRed, label: 'URGENT' },
    high: { bg: `${ESY.pink}08`, border: `${ESY.pink}20`, dot: ESY.pink, label: 'HIGH' },
    medium: { bg: '#FFF8E1', border: '#FFD54F30', dot: '#F9A825', label: 'MEDIUM' },
    low: { bg: `${ESY.turquoise}05`, border: `${ESY.turquoise}15`, dot: ESY.turquoise, label: 'LOW' },
  };
  const typeIcons = { mention: MessageCircle, task_assigned: ListTodo, action_item: CheckCircle2, anomaly: AlertTriangle, sentiment_warning: Activity };

  return (
    <div className="w-[320px] border-l border-slate-200 bg-white flex flex-col h-full" data-testid="notifications-panel">
      <div className="h-14 flex items-center justify-between px-4 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <div className="relative"><Bell className="w-4 h-4" style={{ color: ESY.pink }} />{notifications.length > 0 && <span className="absolute -top-1 -right-1 w-2 h-2 rounded-full" style={{ backgroundColor: ESY.deepRed }} />}</div>
          <h3 className="text-sm font-semibold text-slate-900">Notifications</h3>
          <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-slate-100 text-slate-500">{notifications.length}</span>
        </div>
        <button onClick={onClose} className="p-1 hover:bg-slate-100 rounded-md"><X className="w-4 h-4 text-slate-500" /></button>
      </div>
      <ScrollArea className="flex-1">
        <div className="p-3 space-y-2">
          {loading ? (<div className="flex items-center justify-center py-8"><Loader2 className="w-5 h-5 animate-spin" style={{ color: ESY.pink }} /></div>) : notifications.length === 0 ? (
            <div className="text-center py-8"><CheckCircle2 className="w-10 h-10 mx-auto mb-2" style={{ color: ESY.turquoise }} /><p className="text-sm font-medium text-slate-700">All caught up!</p><p className="text-xs text-slate-400 mt-1">No notifications right now</p></div>
          ) : (notifications.map((notif) => { const ps = priorityStyles[notif.priority] || priorityStyles.low; const Icon = typeIcons[notif.type] || Zap; return (
            <button key={notif.id} onClick={() => { if (notif.channel_id && onNavigate) onNavigate({ type: 'channel', id: notif.channel_id }); onClose(); }}
              className="w-full text-left p-3 rounded-lg border transition-all hover:shadow-sm" style={{ backgroundColor: ps.bg, borderColor: ps.border }} data-testid={`notif-${notif.id}`}>
              <div className="flex items-start gap-2.5">
                <div className="w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${ps.dot}15` }}><Icon className="w-3.5 h-3.5" style={{ color: ps.dot }} /></div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5 mb-0.5"><p className="text-xs font-semibold text-slate-800 truncate">{notif.title}</p><span className="text-[8px] font-bold px-1.5 py-0.5 rounded-full text-white flex-shrink-0" style={{ backgroundColor: ps.dot }}>{ps.label}</span></div>
                  <p className="text-[11px] text-slate-600 line-clamp-2">{notif.body}</p>
                  {notif.deadline && notif.deadline !== 'TBD' && <p className="text-[9px] mt-1" style={{ color: ESY.deepRed }}>Due: {notif.deadline}</p>}
                </div>
              </div>
            </button>); }))}
          {notifications.length > 0 && (<button onClick={loadNotifications} className="w-full text-xs py-1.5 rounded-md hover:bg-slate-50" style={{ color: ESY.turquoise }}>Refresh</button>)}
        </div>
      </ScrollArea>
    </div>
  );
};
