/**
 * KarauCompactPanel — Compact AI KARAU panel for workspace side panel
 * Shows quick meeting actions + recent meetings
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import {
  Video, Plus, Clock, Users, Calendar, Loader2, Copy, ExternalLink
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';

const API = process.env.REACT_APP_BACKEND_URL;

const KarauCompactPanel = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [joinId, setJoinId] = useState('');
  const token = localStorage.getItem('token');

  useEffect(() => {
    const savedUser = localStorage.getItem('karau_user');
    if (savedUser && token) {
      setUser(JSON.parse(savedUser));
    } else {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (!user || !token) return;
    const load = async () => {
      try {
        const res = await fetch(`${API}/api/karau-meet/meetings?limit=10`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setMeetings(data.meetings || (Array.isArray(data) ? data : []));
        }
      } catch (e) { console.error('Failed to load meetings', e); }
      setLoading(false);
    };
    load();
  }, [user, token]);

  const handleCreateMeeting = async () => {
    if (!token) return;
    setCreating(true);
    try {
      const res = await fetch(`${API}/api/karau/meetings`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: 'Quick Meeting',
          type: 'instant',
          settings: { max_participants: 50 }
        })
      });
      if (res.ok) {
        const meeting = await res.json();
        const meetingId = meeting.meeting_id || meeting.id;
        toast.success('Meeting created!');
        navigate(`/karau-meet/lobby/${meetingId}`);
      } else {
        toast.error('Failed to create meeting');
      }
    } catch (e) { toast.error('Connection error'); }
    setCreating(false);
  };

  const handleJoin = () => {
    if (!joinId.trim()) return;
    navigate(`/karau-meet/join/${joinId.trim().toUpperCase()}`);
  };

  const copyMeetingLink = (meetingId) => {
    const link = `${window.location.origin}/karau-meet/join/${meetingId}`;
    navigator.clipboard.writeText(link);
    toast.success('Link copied!');
  };

  if (!user) {
    return (
      <div className="h-full flex items-center justify-center p-4">
        <p className="text-xs text-slate-400 text-center">
          Sign in to AI KARAU for meetings.
          <br />
          <a href="/karau-meet" className="text-purple-400 hover:underline mt-1 inline-block">Open AI KARAU</a>
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <Loader2 className="w-5 h-5 text-purple-400 animate-spin" />
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-[#0c0d1a]" data-testid="karau-compact-panel">
      {/* Quick Actions */}
      <div className="px-3 py-3 border-b border-slate-700/30 space-y-2 flex-shrink-0">
        <Button
          onClick={handleCreateMeeting}
          disabled={creating}
          className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-xs h-9"
          data-testid="karau-compact-create"
        >
          {creating ? <Loader2 className="w-3.5 h-3.5 animate-spin mr-1.5" /> : <Plus className="w-3.5 h-3.5 mr-1.5" />}
          New Meeting
        </Button>

        <div className="flex gap-1.5">
          <input
            type="text"
            value={joinId}
            onChange={(e) => setJoinId(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleJoin()}
            placeholder="Meeting ID..."
            className="flex-1 bg-slate-800/60 border border-slate-700/30 rounded-lg px-2.5 py-1.5 text-xs text-white placeholder:text-slate-500 outline-none focus:border-purple-500/40"
            data-testid="karau-compact-join-input"
          />
          <Button
            size="sm"
            onClick={handleJoin}
            disabled={!joinId.trim()}
            className="bg-slate-700 hover:bg-slate-600 text-white text-xs h-8 px-3"
            data-testid="karau-compact-join-btn"
          >
            Join
          </Button>
        </div>
      </div>

      {/* Recent Meetings */}
      <ScrollArea className="flex-1">
        <div className="px-3 py-2">
          <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 mb-2">Recent Meetings</p>
          {meetings.length === 0 ? (
            <p className="text-xs text-slate-500 text-center py-4">No meetings yet</p>
          ) : (
            <div className="space-y-1.5">
              {meetings.map((m) => {
                const meetingId = m.meeting_id || m.id;
                return (
                  <div
                    key={meetingId}
                    className="p-2.5 rounded-lg bg-white/[0.02] border border-white/[0.04] hover:bg-white/[0.04] transition-colors"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0 flex-1">
                        <p className="text-xs font-medium text-white truncate">{m.title || 'Meeting'}</p>
                        <p className="text-[10px] text-slate-500 mt-0.5">
                          {m.created_at ? new Date(m.created_at).toLocaleDateString() : 'Recently'}
                        </p>
                      </div>
                      <div className="flex gap-1 flex-shrink-0">
                        <button
                          onClick={() => copyMeetingLink(meetingId)}
                          className="p-1 rounded hover:bg-white/10 text-slate-500 hover:text-white transition-colors"
                          title="Copy link"
                        >
                          <Copy className="w-3 h-3" />
                        </button>
                        <button
                          onClick={() => navigate(`/karau-meet/lobby/${meetingId}`)}
                          className="p-1 rounded hover:bg-purple-500/20 text-slate-500 hover:text-purple-400 transition-colors"
                          title="Join meeting"
                        >
                          <ExternalLink className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Footer link */}
      <div className="px-3 py-2 border-t border-slate-700/30 flex-shrink-0">
        <a href="/karau-meet" className="text-xs text-purple-400 hover:text-purple-300 transition-colors">
          Open full AI KARAU &rarr;
        </a>
      </div>
    </div>
  );
};

export default KarauCompactPanel;
