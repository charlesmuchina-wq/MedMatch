import { useState, useEffect } from 'react';
import { X, Clock, Send, Loader2, Trash2 } from 'lucide-react';
import { toast } from 'sonner';
import { API } from './constants';

const ScheduleMessageModal = ({ channelId, channelName, token, onClose }) => {
  const [content, setContent] = useState('');
  const [date, setDate] = useState('');
  const [time, setTime] = useState('');
  const [scheduling, setScheduling] = useState(false);
  const [scheduled, setScheduled] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadScheduled();
    // Set default date/time to tomorrow 9am
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    setDate(tomorrow.toISOString().split('T')[0]);
    setTime('09:00');
  }, []);

  const loadScheduled = async () => {
    try {
      const res = await fetch(`${API}/api/lumi/automation/schedule`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) {
        const data = await res.json();
        setScheduled((data.scheduled || []).filter(m => m.channel_id === channelId));
      }
    } catch {}
    setLoading(false);
  };

  const handleSchedule = async () => {
    if (!content.trim()) { toast.error('Enter a message'); return; }
    if (!date || !time) { toast.error('Select date and time'); return; }

    const scheduledAt = new Date(`${date}T${time}:00`).toISOString();
    setScheduling(true);
    try {
      const res = await fetch(`${API}/api/lumi/automation/schedule`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ channel_id: channelId, content: content.trim(), scheduled_at: scheduledAt })
      });
      if (res.ok) {
        toast.success('Message scheduled!');
        setContent('');
        loadScheduled();
      }
    } catch { toast.error('Failed to schedule'); }
    setScheduling(false);
  };

  const cancelScheduled = async (id) => {
    try {
      await fetch(`${API}/api/lumi/automation/schedule/${id}`, { method: 'DELETE', headers: { Authorization: `Bearer ${token}` } });
      toast.success('Cancelled');
      loadScheduled();
    } catch {}
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" data-testid="schedule-modal">
      <div className="w-full max-w-md mx-4 bg-[#131920] border border-white/10 rounded-2xl shadow-2xl overflow-hidden"
        style={{ animation: 'fadeInUp 0.3s ease-out' }}>
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/10">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-[#00CEC9]" />
            <h2 className="text-sm font-semibold text-white">Schedule Message</h2>
            <span className="text-[10px] text-slate-500">#{channelName}</span>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-white/10 rounded-lg" data-testid="close-schedule">
            <X className="w-4 h-4 text-slate-400" />
          </button>
        </div>

        <div className="p-5 space-y-4">
          <textarea value={content} onChange={e => setContent(e.target.value)}
            placeholder="Write your message..."
            className="w-full h-20 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder:text-slate-600 outline-none focus:border-[#00CEC9]/50 resize-none"
            data-testid="schedule-content" />

          <div className="flex gap-3">
            <div className="flex-1">
              <label className="text-[10px] text-slate-500 mb-1 block">Date</label>
              <input type="date" value={date} onChange={e => setDate(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white outline-none focus:border-[#00CEC9]/50"
                data-testid="schedule-date" />
            </div>
            <div className="flex-1">
              <label className="text-[10px] text-slate-500 mb-1 block">Time</label>
              <input type="time" value={time} onChange={e => setTime(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white outline-none focus:border-[#00CEC9]/50"
                data-testid="schedule-time" />
            </div>
          </div>

          <button onClick={handleSchedule} disabled={scheduling}
            className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-white text-sm font-semibold transition-all hover:opacity-90 disabled:opacity-50"
            style={{ background: 'linear-gradient(135deg, #00CEC9, #6C5CE7)' }}
            data-testid="schedule-submit">
            {scheduling ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            {scheduling ? 'Scheduling...' : 'Schedule Message'}
          </button>

          {scheduled.length > 0 && (
            <div className="pt-3 border-t border-white/10 space-y-2">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider">Pending ({scheduled.length})</span>
              {scheduled.map(m => (
                <div key={m.id} className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/[0.03] border border-white/5">
                  <Clock className="w-3 h-3 text-slate-500 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-white/80 truncate">{m.content}</p>
                    <p className="text-[9px] text-slate-600">{new Date(m.scheduled_at).toLocaleString()}</p>
                  </div>
                  <button onClick={() => cancelScheduled(m.id)} className="p-1 hover:bg-red-500/10 rounded" data-testid={`cancel-schedule-${m.id}`}>
                    <Trash2 className="w-3 h-3 text-red-400/60 hover:text-red-400" />
                  </button>
                </div>
              ))}
            </div>
          )}
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

export default ScheduleMessageModal;
