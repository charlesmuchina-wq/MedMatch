import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Film, Clock, Clapperboard, Bookmark, Play, Trash2, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

export default function ReplayListPanel() {
  const navigate = useNavigate();
  const [replays, setReplays] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchReplays(); }, []);

  const fetchReplays = async () => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/replay/list`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setReplays(data.replays || []);
      }
    } catch {}
    setLoading(false);
  };

  const deleteReplay = async (meetingId) => {
    const token = localStorage.getItem('token');
    try {
      await fetch(`${API}/api/karau/replay/${meetingId}`, {
        method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` }
      });
      toast.success('Replay deleted');
      fetchReplays();
    } catch {}
  };

  const formatDuration = (s) => {
    const m = Math.floor((s || 0) / 60);
    return m < 60 ? `${m}m` : `${Math.floor(m / 60)}h ${m % 60}m`;
  };

  if (loading) return (
    <div className="flex items-center justify-center py-12">
      <Loader2 className="w-6 h-6 text-violet-400 animate-spin" />
    </div>
  );

  return (
    <div data-testid="replay-list">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <Film className="w-5 h-5 text-violet-400" />Director's Cut Replays
        </h2>
      </div>

      {replays.length === 0 ? (
        <div className="text-center py-12 bg-karau-card/30 rounded-xl border border-white/5">
          <Film className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <p className="text-sm text-slate-400">No replays yet</p>
          <p className="text-xs text-slate-500 mt-1">Meeting replays with director cuts will appear here</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {replays.map(r => (
            <div key={r.meeting_id}
              className="bg-karau-card/40 border border-white/5 rounded-xl overflow-hidden hover:border-violet-500/20 transition-all group cursor-pointer"
              onClick={() => navigate(`/karau-meet/replay/${r.meeting_id}`)}
              data-testid={`replay-card-${r.meeting_id}`}>
              {/* Thumbnail */}
              <div className="aspect-video bg-gradient-to-br from-violet-500/10 to-fuchsia-500/10 relative flex items-center justify-center">
                <Clapperboard className="w-10 h-10 text-violet-400/30" />
                <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black/30">
                  <div className="w-12 h-12 rounded-full bg-violet-500/80 flex items-center justify-center">
                    <Play className="w-6 h-6 text-white ml-0.5" />
                  </div>
                </div>
                {r.status && (
                  <Badge className="absolute top-2 right-2 text-[7px] bg-violet-500/10 text-violet-400 border border-violet-500/20">
                    {r.status}
                  </Badge>
                )}
              </div>

              <div className="p-3">
                <h3 className="text-sm font-medium text-white truncate">{r.title}</h3>
                <div className="flex items-center gap-3 mt-1.5 text-[10px] text-slate-400">
                  <span className="flex items-center gap-0.5"><Clock className="w-2.5 h-2.5" />{formatDuration(r.duration_seconds)}</span>
                  <span className="flex items-center gap-0.5"><Clapperboard className="w-2.5 h-2.5" />{r.cut_count || 0} cuts</span>
                  <span className="flex items-center gap-0.5"><Bookmark className="w-2.5 h-2.5" />{(r.key_moments || []).length} moments</span>
                </div>
                {r.saved_at && (
                  <p className="text-[9px] text-slate-500 mt-1">{new Date(r.saved_at).toLocaleDateString()}</p>
                )}

                <div className="flex gap-1 mt-2">
                  <Button size="sm" className="flex-1 h-6 text-[9px] bg-violet-500/80 hover:bg-violet-400 rounded-lg" data-testid={`watch-replay-${r.meeting_id}`}>
                    <Play className="w-2.5 h-2.5 mr-0.5" />Watch
                  </Button>
                  <Button size="sm" variant="ghost" onClick={(e) => { e.stopPropagation(); deleteReplay(r.meeting_id); }}
                    className="h-6 px-1.5 text-red-400 hover:bg-red-500/10" data-testid={`delete-replay-${r.meeting_id}`}>
                    <Trash2 className="w-2.5 h-2.5" />
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
