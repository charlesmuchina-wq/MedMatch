import { useState, useEffect, useCallback, useRef } from 'react';
import { Users, Plus, X, Volume2, Move, MapPin, Sparkles } from 'lucide-react';
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
        body: JSON.stringify({ user_id: userId || 'local-user', user_name: userName || 'You', x, y, avatar_color: AVATAR_COLORS[0] })
      });
      if (res.ok) setNearby((await res.json()).nearby_users || []);
    } catch {}
  };

  const handleMapClick = (e) => {
    if (!mapRef.current) return;
    const rect = mapRef.current.getBoundingClientRect();
    const x = Math.round(((e.clientX - rect.left) / rect.width) * MAP_W);
    const y = Math.round(((e.clientY - rect.top) / rect.height) * MAP_H);
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
        body: JSON.stringify({ name: newLounge.trim(), topic: '', capacity: 8, position: { x: 100 + Math.random() * 400, y: 80 + Math.random() * 240 }, radius: 100 })
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
      {/* Header */}
      <div className="p-3 border-b border-white/[0.06]">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-pink-500/20 to-rose-500/10 flex items-center justify-center">
            <Users className="w-3.5 h-3.5 text-pink-400" />
          </div>
          <div>
            <h3 className="text-xs font-semibold text-white">Breakout Lounges</h3>
            <p className="text-[9px] text-slate-500">Click map to move</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {/* Create Lounge */}
        <div className="flex gap-2">
          <Input value={newLounge} onChange={e => setNewLounge(e.target.value)}
            placeholder="New lounge name..." onKeyDown={e => e.key === 'Enter' && createLounge()}
            className="bg-karau-bg/60 border-white/10 text-white text-[10px] h-8 rounded-xl" data-testid="new-lounge-input" />
          <Button size="sm" onClick={createLounge} disabled={creating}
            className="h-8 px-3 text-[10px] bg-pink-500/80 hover:bg-pink-400 rounded-xl shadow-lg shadow-pink-500/15" data-testid="create-lounge-btn">
            <Plus className="w-3 h-3" />
          </Button>
        </div>

        {/* Interactive 2D Map */}
        <div ref={mapRef} onClick={handleMapClick}
          className="relative w-full aspect-[3/2] rounded-xl overflow-hidden cursor-crosshair border border-white/[0.06]"
          style={{ background: 'radial-gradient(ellipse at center, rgba(15,22,41,0.95), rgba(10,14,26,0.99))' }}
          data-testid="breakout-map">
          {/* Subtle grid pattern */}
          <div className="absolute inset-0 opacity-[0.04]" style={{
            backgroundImage: `radial-gradient(circle, rgba(255,255,255,0.5) 1px, transparent 1px)`,
            backgroundSize: '24px 24px'
          }} />

          {/* Lounge Zones with glow */}
          {lounges.map(l => {
            const left = (l.position.x / MAP_W) * 100;
            const top = (l.position.y / MAP_H) * 100;
            return (
              <div key={l.lounge_id} className="absolute -translate-x-1/2 -translate-y-1/2 group"
                style={{ left: `${left}%`, top: `${top}%` }}>
                {/* Glow ring */}
                <div className="absolute inset-0 -m-4 rounded-full opacity-30"
                  style={{ background: `radial-gradient(circle, rgba(236,72,153,0.2), transparent 70%)`, width: '80px', height: '80px', transform: 'translate(-50%, -50%)', left: '50%', top: '50%' }} />
                {/* Zone circle */}
                <div className="relative rounded-full border-2 border-dashed border-pink-500/25 bg-pink-500/[0.04] flex items-center justify-center backdrop-blur-sm"
                  style={{ width: 70, height: 70 }}>
                  <div className="text-center">
                    <p className="text-[9px] text-pink-300 font-semibold">{l.name}</p>
                    <p className="text-[7px] text-slate-400">{l.participant_count || 0}/{l.capacity}</p>
                  </div>
                </div>
                <button onClick={(e) => { e.stopPropagation(); deleteLounge(l.lounge_id); }}
                  className="hidden group-hover:flex absolute -top-1 -right-1 w-4 h-4 rounded-full bg-red-500/80 text-white items-center justify-center hover:bg-red-400 transition-colors"
                  data-testid={`close-lounge-${l.lounge_id}`}>
                  <X className="w-2.5 h-2.5" />
                </button>
              </div>
            );
          })}

          {/* Other Avatars */}
          {avatars.filter(a => a.user_id !== (userId || 'local-user')).map(a => (
            <div key={a.user_id} className="absolute -translate-x-1/2 -translate-y-1/2 transition-all duration-500"
              style={{ left: `${(a.x / MAP_W) * 100}%`, top: `${(a.y / MAP_H) * 100}%` }}>
              <div className="w-6 h-6 rounded-full flex items-center justify-center text-[8px] font-bold text-white border border-white/20 shadow-lg"
                style={{ backgroundColor: a.avatar_color || AVATAR_COLORS[1] }}>
                {(a.user_name || '?')[0]}
              </div>
              <p className="text-[7px] text-center text-slate-400 mt-0.5 whitespace-nowrap">{a.user_name}</p>
            </div>
          ))}

          {/* My Avatar with glow */}
          <div className="absolute -translate-x-1/2 -translate-y-1/2 z-10 transition-all duration-300 ease-out"
            style={{ left: `${(myPos.x / MAP_W) * 100}%`, top: `${(myPos.y / MAP_H) * 100}%` }}
            data-testid="my-avatar">
            {/* Pulse ring */}
            <div className="absolute inset-0 -m-2 rounded-full bg-indigo-500/20 animate-pulse-ring" />
            <div className="relative w-7 h-7 rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center text-[9px] font-bold text-white ring-2 ring-indigo-400/40 shadow-xl shadow-indigo-500/30">
              {(userName || 'Y')[0]}
            </div>
            <p className="text-[7px] text-center text-indigo-300 mt-0.5 font-medium">You</p>
          </div>

          {/* Map label */}
          <div className="absolute bottom-2 right-2 flex items-center gap-1 bg-black/40 backdrop-blur-sm rounded-lg px-2 py-1">
            <MapPin className="w-2.5 h-2.5 text-slate-500" />
            <span className="text-[7px] text-slate-500">Click to move</span>
          </div>
        </div>

        {/* Nearby Users */}
        {nearby.length > 0 && (
          <div className="p-3 rounded-xl border border-pink-500/15 bg-gradient-to-b from-pink-500/[0.04] to-transparent animate-slide-up" data-testid="nearby-users">
            <div className="flex items-center gap-2 mb-2">
              <Volume2 className="w-3 h-3 text-pink-400" />
              <span className="text-[9px] font-semibold text-pink-400 uppercase tracking-widest">Nearby</span>
              <Badge className="text-[7px] bg-pink-500/10 text-pink-400 border-pink-500/20">{nearby.length}</Badge>
            </div>
            <div className="space-y-1.5">
              {nearby.map(n => (
                <div key={n.user_id} className="flex items-center gap-2">
                  <div className="w-5 h-5 rounded-full bg-pink-500/20 flex items-center justify-center text-[7px] text-pink-300 font-bold">
                    {(n.user_name || '?')[0]}
                  </div>
                  <span className="text-[10px] text-white flex-1">{n.user_name}</span>
                  <div className="flex items-center gap-1.5">
                    {/* Volume indicator */}
                    <div className="flex gap-0.5">
                      {[0.2, 0.4, 0.6, 0.8].map((threshold, i) => (
                        <div key={i} className={`w-1 rounded-full transition-all duration-300 ${
                          n.audio_volume >= threshold ? 'bg-pink-400' : 'bg-white/[0.06]'
                        }`} style={{ height: `${6 + i * 3}px` }} />
                      ))}
                    </div>
                    <span className="text-[8px] text-slate-500 tabular-nums w-8 text-right">{Math.round(n.distance)}px</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Lounge List */}
        <div data-testid="lounge-list">
          <p className="text-[9px] font-semibold text-slate-400 uppercase tracking-widest mb-2">Active Lounges</p>
          {lounges.length === 0 ? (
            <div className="text-center py-4">
              <Sparkles className="w-5 h-5 text-pink-500/30 mx-auto mb-1" />
              <p className="text-[10px] text-slate-500">No lounges yet. Create one above.</p>
            </div>
          ) : lounges.map((l, i) => (
            <div key={l.lounge_id} className="flex items-center justify-between p-2.5 rounded-xl bg-white/[0.02] border border-white/[0.04] mb-1.5 hover:bg-white/[0.04] transition-colors"
              style={{ animationDelay: `${i * 60}ms` }}>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-pink-400" />
                <div>
                  <p className="text-[10px] text-white font-medium">{l.name}</p>
                  {l.topic && <p className="text-[8px] text-slate-500">{l.topic}</p>}
                </div>
              </div>
              <Badge className="text-[8px] bg-pink-500/10 text-pink-400 border-pink-500/20">{l.participant_count || 0}/{l.capacity}</Badge>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
