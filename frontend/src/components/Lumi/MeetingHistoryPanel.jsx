import { useState, useEffect } from 'react';
import { X, Video, Calendar, Clock, ExternalLink, Users, Loader2, History } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { API, ESY } from './constants';

const statusStyles = {
  waiting: { bg: 'bg-amber-50', text: 'text-amber-700', label: 'Waiting' },
  active: { bg: 'bg-emerald-50', text: 'text-emerald-700', label: 'Active' },
  scheduled: { bg: 'bg-blue-50', text: 'text-blue-700', label: 'Scheduled' },
  ended: { bg: 'bg-slate-100', text: 'text-slate-600', label: 'Ended' },
  cancelled: { bg: 'bg-red-50', text: 'text-red-600', label: 'Cancelled' },
};

const MeetingHistoryPanel = ({ token, onClose, onStartMeeting }) => {
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);

  useEffect(() => { loadMeetings(); }, []);

  const loadMeetings = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/lumi/meetings/history?limit=20`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setMeetings(data.meetings || []);
        setTotal(data.total || 0);
      }
    } catch {}
    setLoading(false);
  };

  const formatDate = (iso) => {
    if (!iso) return '';
    const d = new Date(iso);
    const now = new Date();
    const diff = now - d;
    if (diff < 86400000) return `Today ${d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
    if (diff < 172800000) return `Yesterday ${d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
    return d.toLocaleDateString([], { month: 'short', day: 'numeric' }) + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 max-h-[80vh] flex flex-col overflow-hidden" onClick={e => e.stopPropagation()} data-testid="meeting-history-panel">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #6C5CE7, #00CEC9)' }}>
              <History className="w-4 h-4 text-white" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-900">Meeting History</h3>
              <p className="text-[11px] text-slate-500">{total} total meeting{total !== 1 ? 's' : ''}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button size="sm" onClick={onStartMeeting}
              className="h-7 text-[11px] text-white rounded-lg"
              style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` }}
              data-testid="new-meeting-from-history">New Meeting</Button>
            <button onClick={onClose} className="p-1.5 hover:bg-slate-100 rounded-lg transition-colors" data-testid="close-meeting-history">
              <X className="w-4 h-4 text-slate-500" />
            </button>
          </div>
        </div>

        <ScrollArea className="flex-1">
          <div className="p-4 space-y-2">
            {loading ? (
              <div className="flex items-center justify-center py-12"><Loader2 className="w-5 h-5 animate-spin text-slate-400" /></div>
            ) : meetings.length === 0 ? (
              <div className="text-center py-12">
                <Video className="w-8 h-8 text-slate-300 mx-auto mb-3" />
                <p className="text-sm text-slate-500 font-medium">No meetings yet</p>
                <p className="text-xs text-slate-400 mt-1">Start one from the dashboard or chat toolbar</p>
              </div>
            ) : meetings.map(m => {
              const st = statusStyles[m.status] || statusStyles.ended;
              return (
                <div key={m.id} className="p-3 rounded-xl border border-slate-100 hover:border-slate-200 hover:bg-slate-50/50 transition-all group" data-testid={`meeting-item-${m.id}`}>
                  <div className="flex items-start gap-3">
                    <div className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5"
                      style={{ background: m.status === 'active' || m.status === 'waiting' ? 'linear-gradient(135deg, #6C5CE7, #00CEC9)' : '#f1f5f9' }}>
                      <Video className={`w-4 h-4 ${m.status === 'active' || m.status === 'waiting' ? 'text-white' : 'text-slate-400'}`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-medium text-slate-800 truncate">{m.title}</p>
                        <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${st.bg} ${st.text}`}>{st.label}</span>
                      </div>
                      <div className="flex items-center gap-3 mt-1 text-[11px] text-slate-500">
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {formatDate(m.scheduled_time || m.created_at)}
                        </span>
                        {m.source === 'enzi' && <span className="px-1.5 py-0.5 rounded bg-[#00CEC9]/10 text-[#00CEC9] font-medium">ENZI</span>}
                        {m.participants?.length > 0 && (
                          <span className="flex items-center gap-1"><Users className="w-3 h-3" />{m.participants.length}</span>
                        )}
                      </div>
                      {m.description && <p className="text-[11px] text-slate-400 mt-1 truncate">{m.description}</p>}
                    </div>
                    {(m.status === 'waiting' || m.status === 'active' || m.status === 'scheduled') && (
                      <Button size="sm" variant="ghost"
                        onClick={() => window.open(`/karau-meet/meeting/${m.id}`, '_blank')}
                        className="h-7 text-[10px] opacity-0 group-hover:opacity-100 transition-opacity text-[#6C5CE7]"
                        data-testid={`join-meeting-${m.id}`}>
                        <ExternalLink className="w-3 h-3 mr-1" />Join
                      </Button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </ScrollArea>
      </div>
    </div>
  );
};

export default MeetingHistoryPanel;
