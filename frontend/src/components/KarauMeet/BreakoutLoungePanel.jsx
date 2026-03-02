import { useState, useEffect, useCallback, useRef } from 'react';
import { Users, Plus, X, MessageSquare, Volume2, Move } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

const AVATAR_COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f97316', '#eab308', '#22c55e', '#06b6d4'];
const MAP_W = 600;
const MAP_H = 400;

export default function BreakoutLoungePanel({ meetingId, userName, userId }) {
  const [lounges, setLounges] = useState([]);
  const [avatars, setAvatars] = useState([]);
  const [myPos, setMyPos] = useState({ x: MAP_W / 2, y: MAP_H / 2 });
  const [nearby, setNearby] = useState([]);
  const [newLounge, setNewLounge] = useState('');
  const [creating, setCreating] = useState(false);
  const mapRef = useRef(null);
  const dragRef = useRef(false);

  const fetchData = useCallback(async () => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/breakout/${meetingId}/lounges`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const d = await res.json();
        setLounges(d.lounges || []);
        setAvatars(d.avatars || []);
      }
    } catch {}
  }, [meetingId]);

  useEffect(() => { fetchData(); const i = setInterval(fetchData, 5000); return () => clearInterval(i); }, [fetchData]);

  const moveAvatar = async (x, y) => {
    setMyPos({ x, y });
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/breakout/${meetingId}/move`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({
          user_id: userId || 'local-user',
          user_name: userName || 'You',
          x, y,
          avatar_color: AVATAR_COLORS[0]
        })
      });
      if (res.ok) {
        const d = await res.json();
        setNearby(d.nearby_users || []);
      }
    } catch {}
  };

  const handleMapClick = (e) => {
    if (!mapRef.current) return;
    const rect = mapRef.current.getBoundingClientRect();
    const scaleX = MAP_W / rect.width;
    const scaleY = MAP_H / rect.height;
    const x = Math.round((e.clientX - rect.left) * scaleX);
    const y = Math.round((e.clientY - rect.top) * scaleY);
    moveAvatar(x, y);
  };

  const createLounge = async () => {
    if (!newLounge.trim()) return;
    setCreating(true);
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/breakout/${meetingId}/lounge`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({
          name: newLounge.trim(),
          topic: '',
          capacity: 8,
          position: { x: 100 + Math.random() * 400, y: 80 + Math.random() * 240 },
          radius: 100
        })
      });
      if (res.ok) { toast.success('Lounge created'); setNewLounge(''); fetchData(); }
    } catch {}
    setCreating(false);
  };

  const deleteLounge = async (loungeId) => {
    const token = localStorage.getItem('token');
    try {
      await fetch(`${API}/api/karau/breakout/${meetingId}/lounge/${loungeId}`, {
        method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` }
      });
      toast.success('Lounge closed');
      fetchData();
    } catch {}
  };

  return (
    <div className="flex-1 flex flex-col overflow-hidden" data-testid="breakout-lounge-panel">
      <div className="p-2.5 border-b border-white/5">
        <h3 className="text-xs font-semibold text-white flex items-center gap-1.5">
          <Users className="w-3.5 h-3.5 text-pink-400" />
          Breakout Lounges
        </h3>
        <p className="text-[8px] text-slate-500 mt-0.5">Click to move your avatar</p>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {/* Create Lounge */}
        <div className="flex gap-1">
          <Input value={newLounge} onChange={e => setNewLounge(e.target.value)}
            placeholder="New lounge name..." onKeyDown={e => e.key === 'Enter' && createLounge()}
            className="bg-karau-bg/60 border-white/10 text-white text-[9px] h-6 rounded-lg" data-testid="new-lounge-input" />
          <Button size="sm" onClick={createLounge} disabled={creating}
            className="h-6 px-2 text-[8px] bg-pink-500/80 hover:bg-pink-400 rounded-lg" data-testid="create-lounge-btn">
            <Plus className="w-3 h-3" />
          </Button>
        </div>

        {/* 2D Interactive Map */}
        <div ref={mapRef} onClick={handleMapClick}
          className="relative w-full aspect-[3/2] bg-gradient-to-b from-slate-900/80 to-slate-950/80 rounded-lg border border-white/5 cursor-crosshair overflow-hidden"
          data-testid="breakout-map">
          {/* Grid */}
          <div className="absolute inset-0 opacity-5" style={{
            backgroundImage: 'radial-gradient(circle, rgba(255,255,255,.3) 1px, transparent 1px)',
            backgroundSize: '20px 20px'
          }} />

          {/* Lounge Zones */}
          {lounges.map(l => {
            const left = (l.position.x / MAP_W) * 100;
            const top = (l.position.y / MAP_H) * 100;
            const size = (l.radius / MAP_W) * 200;
            return (
              <div key={l.lounge_id} className="absolute -translate-x-1/2 -translate-y-1/2 group"
                style={{ left: `${left}%`, top: `${top}%` }}>
                <div className="rounded-full border-2 border-dashed border-pink-500/20 bg-pink-500/5 flex items-center justify-center"
                  style={{ width: `${size}%`, height: `${size}%`, minWidth: 60, minHeight: 60, aspectRatio: '1' }}>
                  <div className="text-center">
                    <p className="text-[8px] text-pink-300 font-medium">{l.name}</p>
                    <p className="text-[6px] text-slate-400">{l.participant_count || 0}/{l.capacity}</p>
                  </div>
                </div>
                <button onClick={(e) => { e.stopPropagation(); deleteLounge(l.lounge_id); }}
                  className="hidden group-hover:block absolute -top-1 -right-1 w-3 h-3 rounded-full bg-red-500 text-white text-[6px] flex items-center justify-center"
                  data-testid={`close-lounge-${l.lounge_id}`}>
                  <X className="w-2 h-2" />
                </button>
              </div>
            );
          })}

          {/* Other Avatars */}
          {avatars.filter(a => a.user_id !== (userId || 'local-user')).map(a => (
            <div key={a.user_id} className="absolute -translate-x-1/2 -translate-y-1/2 group"
              style={{ left: `${(a.x / MAP_W) * 100}%`, top: `${(a.y / MAP_H) * 100}%` }}>
              <div className="w-5 h-5 rounded-full flex items-center justify-center text-[7px] font-bold text-white border border-white/20"
                style={{ backgroundColor: a.avatar_color || AVATAR_COLORS[1] }}>
                {(a.user_name || '?')[0]}
              </div>
              <p className="text-[6px] text-center text-slate-400 mt-0.5 whitespace-nowrap">{a.user_name}</p>
            </div>
          ))}

          {/* My Avatar */}
          <div className="absolute -translate-x-1/2 -translate-y-1/2 z-10 transition-all duration-300"
            style={{ left: `${(myPos.x / MAP_W) * 100}%`, top: `${(myPos.y / MAP_H) * 100}%` }}
            data-testid="my-avatar">
            <div className="w-6 h-6 rounded-full bg-indigo-500 flex items-center justify-center text-[8px] font-bold text-white ring-2 ring-indigo-400/50 animate-pulse">
              {(userName || 'Y')[0]}
            </div>
            <p className="text-[6px] text-center text-indigo-300 mt-0.5">You</p>
          </div>
        </div>

        {/* Nearby Users */}
        {nearby.length > 0 && (
          <div className="p-2 bg-pink-500/5 border border-pink-500/10 rounded-lg" data-testid="nearby-users">
            <p className="text-[8px] text-pink-400 uppercase tracking-wider mb-1">
              <Volume2 className="w-2.5 h-2.5 inline mr-0.5" />Nearby ({nearby.length})
            </p>
            <div className="space-y-0.5">
              {nearby.map(n => (
                <div key={n.user_id} className="flex items-center justify-between text-[8px]">
                  <span className="text-white">{n.user_name}</span>
                  <div className="flex items-center gap-1">
                    <div className="w-12 h-1 bg-white/5 rounded-full overflow-hidden">
                      <div className="h-full bg-pink-400 rounded-full" style={{ width: `${n.audio_volume * 100}%` }} />
                    </div>
                    <span className="text-slate-400 w-6 text-right">{Math.round(n.distance)}px</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Lounge List */}
        <div data-testid="lounge-list">
          <p className="text-[8px] text-slate-400 uppercase tracking-wider mb-1">Active Lounges</p>
          {lounges.length === 0 ? (
            <p className="text-[8px] text-slate-500 text-center py-2">No lounges yet</p>
          ) : lounges.map(l => (
            <div key={l.lounge_id} className="flex items-center justify-between p-1.5 rounded bg-karau-bg/30 mb-0.5">
              <div>
                <p className="text-[9px] text-white">{l.name}</p>
                {l.topic && <p className="text-[7px] text-slate-400">{l.topic}</p>}
              </div>
              <Badge className="text-[7px] bg-pink-500/10 text-pink-400">{l.participant_count || 0}/{l.capacity}</Badge>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
