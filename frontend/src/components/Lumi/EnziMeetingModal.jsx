import { useState } from 'react';
import { X, Video, Calendar, Loader2, Copy, ExternalLink, Users } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';
import { API, ESY } from './constants';

const EnziMeetingModal = ({ channelId, channelName, token, onClose }) => {
  const [tab, setTab] = useState('instant'); // 'instant' | 'schedule'
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [scheduledAt, setScheduledAt] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const createInstantMeeting = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/lumi/meetings/quick`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          title: title || `${channelName || 'ENZI'} Quick Meeting`,
          channel_id: channelId,
          participants: []
        })
      });
      if (res.ok) {
        const data = await res.json();
        setResult(data);
        toast.success('Meeting created! A notification was posted to the channel.');
      } else {
        const err = await res.json();
        toast.error(err.detail || 'Failed to create meeting');
      }
    } catch { toast.error('Connection error'); }
    setLoading(false);
  };

  const scheduleMeeting = async () => {
    if (!scheduledAt) { toast.error('Please select a date and time'); return; }
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/lumi/meetings/schedule`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          title: title || `${channelName || 'ENZI'} Scheduled Meeting`,
          scheduled_at: new Date(scheduledAt).toISOString(),
          channel_id: channelId,
          participants: [],
          description
        })
      });
      if (res.ok) {
        const data = await res.json();
        setResult(data);
        toast.success('Meeting scheduled! A notification was posted to the channel.');
      } else {
        const err = await res.json();
        toast.error(err.detail || 'Failed to schedule meeting');
      }
    } catch { toast.error('Connection error'); }
    setLoading(false);
  };

  const copyLink = () => {
    if (result?.join_url) {
      navigator.clipboard.writeText(`${window.location.origin}${result.join_url}`);
      toast.success('Meeting link copied!');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 overflow-hidden" onClick={e => e.stopPropagation()} data-testid="enzi-meeting-modal">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, #6C5CE7)` }}>
              <Video className="w-4 h-4 text-white" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-900">AI KARAU Meeting</h3>
              <p className="text-[11px] text-slate-500">Create from ENZI{channelName ? ` - #${channelName}` : ''}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 hover:bg-slate-100 rounded-lg transition-colors" data-testid="close-meeting-modal">
            <X className="w-4 h-4 text-slate-500" />
          </button>
        </div>

        {!result ? (
          <>
            {/* Tabs */}
            <div className="flex border-b border-slate-100">
              <button onClick={() => setTab('instant')}
                className={`flex-1 py-2.5 text-xs font-medium transition-colors ${tab === 'instant' ? 'text-[#00CEC9] border-b-2 border-[#00CEC9]' : 'text-slate-500 hover:text-slate-700'}`}
                data-testid="meeting-tab-instant">
                <Video className="w-3.5 h-3.5 inline mr-1.5" />Instant Meeting
              </button>
              <button onClick={() => setTab('schedule')}
                className={`flex-1 py-2.5 text-xs font-medium transition-colors ${tab === 'schedule' ? 'text-[#00CEC9] border-b-2 border-[#00CEC9]' : 'text-slate-500 hover:text-slate-700'}`}
                data-testid="meeting-tab-schedule">
                <Calendar className="w-3.5 h-3.5 inline mr-1.5" />Schedule
              </button>
            </div>

            {/* Form */}
            <div className="p-6 space-y-4">
              <div>
                <label className="text-xs font-medium text-slate-600 mb-1 block">Meeting Title</label>
                <Input value={title} onChange={e => setTitle(e.target.value)}
                  placeholder={`${channelName || 'ENZI'} Meeting`}
                  className="h-10 text-sm" data-testid="meeting-title-input" />
              </div>

              {tab === 'schedule' && (
                <>
                  <div>
                    <label className="text-xs font-medium text-slate-600 mb-1 block">Date & Time</label>
                    <Input type="datetime-local" value={scheduledAt} onChange={e => setScheduledAt(e.target.value)}
                      className="h-10 text-sm" data-testid="meeting-datetime-input" />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-slate-600 mb-1 block">Description (optional)</label>
                    <textarea value={description} onChange={e => setDescription(e.target.value)}
                      placeholder="Meeting agenda or notes..."
                      className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm resize-none h-20 focus:ring-2 focus:ring-[#00CEC9]/20 focus:border-[#00CEC9] outline-none"
                      data-testid="meeting-desc-input" />
                  </div>
                </>
              )}

              <Button onClick={tab === 'instant' ? createInstantMeeting : scheduleMeeting}
                disabled={loading}
                className="w-full h-10 text-white font-medium rounded-lg"
                style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` }}
                data-testid="create-meeting-btn">
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : tab === 'instant' ? 'Start Meeting Now' : 'Schedule Meeting'}
              </Button>
            </div>
          </>
        ) : (
          /* Success State */
          <div className="p-6 text-center space-y-4">
            <div className="w-14 h-14 rounded-full mx-auto flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${ESY.turquoise}20, #6C5CE720)` }}>
              <Video className="w-6 h-6" style={{ color: ESY.turquoise }} />
            </div>
            <div>
              <h4 className="text-base font-semibold text-slate-900">{result.status === 'scheduled' ? 'Meeting Scheduled!' : 'Meeting Created!'}</h4>
              <p className="text-sm text-slate-500 mt-1">{result.title}</p>
              {result.scheduled_at && (
                <p className="text-xs text-slate-400 mt-1">{new Date(result.scheduled_at).toLocaleString()}</p>
              )}
            </div>
            <div className="flex items-center gap-2 bg-slate-50 rounded-lg p-3">
              <code className="flex-1 text-xs text-slate-600 truncate" data-testid="meeting-link">{window.location.origin}{result.join_url}</code>
              <button onClick={copyLink} className="p-1.5 hover:bg-slate-200 rounded-md transition-colors" data-testid="copy-meeting-link">
                <Copy className="w-3.5 h-3.5 text-slate-500" />
              </button>
            </div>
            <div className="flex gap-2">
              <Button onClick={() => window.open(result.join_url, '_blank')}
                className="flex-1 h-9 text-white text-xs font-medium rounded-lg"
                style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` }}
                data-testid="join-meeting-btn">
                <ExternalLink className="w-3.5 h-3.5 mr-1.5" />Join Meeting
              </Button>
              <Button variant="outline" onClick={onClose} className="flex-1 h-9 text-xs" data-testid="done-meeting-btn">
                Done
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EnziMeetingModal;
