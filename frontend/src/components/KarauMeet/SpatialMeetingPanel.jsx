import { useState, useEffect, useCallback } from 'react';
import { Glasses, Box, Users, RotateCcw, Maximize } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import PreviewBadge from '@/components/KarauMeet/PreviewBadge';

const API = process.env.REACT_APP_BACKEND_URL;

const ROOM_TYPES = [
  { id: 'boardroom', label: 'Boardroom', icon: Box },
  { id: 'amphitheater', label: 'Theater', icon: Maximize },
  { id: 'lounge', label: 'Lounge', icon: Users },
];

const HEADSET_LABELS = {
  vision_pro: { label: 'Vision Pro', color: 'bg-violet-500/10 text-violet-400' },
  quest_3: { label: 'Quest 3', color: 'bg-blue-500/10 text-blue-400' },
  web_browser: { label: 'Browser', color: 'bg-slate-500/10 text-slate-400' },
};

export default function SpatialMeetingPanel({ meetingId }) {
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchSession = useCallback(async () => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/webxr/${meetingId}/session`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) setSession(await res.json());
    } catch {}
    setLoading(false);
  }, [meetingId]);

  useEffect(() => { fetchSession(); }, [fetchSession]);

  const createSession = async (roomType) => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/webxr/${meetingId}/session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({
          meeting_id: meetingId,
          room_environment: { room_type: roomType, capacity: 12 }
        })
      });
      if (res.ok) fetchSession();
    } catch {}
  };

  if (loading) return <div className="p-3 text-[9px] text-slate-500">Loading spatial session...</div>;

  const personas = session?.personas || [];
  const room = session?.room_environment || {};
  const features = session?.features || {};
  const seats = session?.seats || [];

  return (
    <div className="flex-1 flex flex-col overflow-hidden" data-testid="spatial-meeting-panel">
      <div className="p-3 border-b border-white/[0.06]">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500/20 to-violet-500/10 flex items-center justify-center">
            <Glasses className="w-3.5 h-3.5 text-indigo-400" />
          </div>
          <div>
            <h3 className="text-xs font-semibold text-white">WebXR Spatial</h3>
            <p className="text-[9px] text-slate-500">Vision Pro / Quest 3 ready</p>
          </div>
          <PreviewBadge className="ml-auto" />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {/* Room Type Selector */}
        <div className="flex gap-1" data-testid="room-type-selector">
          {ROOM_TYPES.map(rt => (
            <button key={rt.id} onClick={() => createSession(rt.id)}
              className={`flex-1 p-1.5 rounded-lg border text-center transition-all ${
                room.type === rt.id ? 'bg-indigo-500/15 border-indigo-500/30 text-indigo-300' : 'bg-karau-bg/30 border-white/5 text-slate-400 hover:bg-white/5'
              }`} data-testid={`room-type-${rt.id}`}>
              <rt.icon className="w-3 h-3 mx-auto mb-0.5" />
              <span className="text-[8px]">{rt.label}</span>
            </button>
          ))}
        </div>

        {/* 3D Room Visualization */}
        <div className="relative aspect-[16/10] bg-gradient-to-b from-slate-900 to-slate-950 rounded-lg border border-white/5 overflow-hidden" data-testid="spatial-room-view" style={{ perspective: '600px' }}>
          {/* Floor grid with perspective */}
          <div className="absolute bottom-0 inset-x-0 h-2/3" style={{
            background: 'linear-gradient(transparent 0%, rgba(99,102,241,0.03) 100%)',
            transform: 'rotateX(60deg)',
            transformOrigin: 'bottom center'
          }}>
            <div className="w-full h-full opacity-20" style={{
              backgroundImage: 'linear-gradient(rgba(99,102,241,.3) 1px, transparent 1px), linear-gradient(90deg, rgba(99,102,241,.3) 1px, transparent 1px)',
              backgroundSize: '12% 12%'
            }} />
          </div>

          {/* Persona avatars */}
          {personas.map((p, i) => {
            const leftPct = 50 + (p.position?.x || 0) * 12;
            const bottomPct = 20 + (p.position?.z || 0) * 10;
            const headset = HEADSET_LABELS[p.headset_type] || HEADSET_LABELS.web_browser;
            return (
              <div key={p.user_id} className="absolute group"
                style={{ left: `${Math.max(5, Math.min(95, leftPct))}%`, bottom: `${Math.max(5, Math.min(90, bottomPct))}%`, transform: 'translateX(-50%)' }}>
                <div className={`w-7 h-7 rounded-full flex items-center justify-center text-[8px] font-bold text-white ring-2 ${
                  p.avatar_type === 'spatial_persona' ? 'bg-violet-500/50 ring-violet-400/40' :
                  p.avatar_type === 'video_feed' ? 'bg-blue-500/50 ring-blue-400/40' : 'bg-slate-500/50 ring-slate-400/40'
                } ${p.is_speaking ? 'ring-emerald-400 animate-pulse' : ''}`}>
                  {p.user_name?.charAt(0) || '?'}
                </div>
                <div className="hidden group-hover:block absolute -top-10 left-1/2 -translate-x-1/2 bg-black/90 rounded px-1.5 py-1 text-center whitespace-nowrap z-10">
                  <p className="text-[7px] text-white font-medium">{p.user_name}</p>
                  <Badge className={`text-[6px] mt-0.5 ${headset.color}`}>{headset.label}</Badge>
                </div>
              </div>
            );
          })}

          {/* Table outline */}
          <div className="absolute bottom-[25%] left-1/2 -translate-x-1/2 w-28 h-8 rounded-full border border-indigo-500/20 bg-indigo-500/5" />
        </div>

        {/* XR Features */}
        <div className="p-2 bg-indigo-500/5 border border-indigo-500/10 rounded-lg" data-testid="xr-features">
          <p className="text-[8px] text-indigo-400 uppercase tracking-wider mb-1">XR Capabilities</p>
          <div className="grid grid-cols-2 gap-1">
            {Object.entries(features).map(([key, val]) => (
              <div key={key} className="flex items-center gap-1 text-[8px]">
                <span className={`w-1.5 h-1.5 rounded-full ${val ? 'bg-emerald-400' : 'bg-slate-600'}`} />
                <span className={val ? 'text-white' : 'text-slate-500'}>{key.replace(/_/g, ' ')}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Connected Personas */}
        <div data-testid="persona-list">
          <p className="text-[8px] text-slate-400 uppercase tracking-wider mb-1">Spatial Personas ({personas.length})</p>
          <div className="space-y-0.5">
            {personas.map(p => {
              const headset = HEADSET_LABELS[p.headset_type] || HEADSET_LABELS.web_browser;
              return (
                <div key={p.user_id} className="flex items-center gap-1.5 p-1 rounded bg-karau-bg/30">
                  <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[7px] font-bold ${
                    p.avatar_type === 'spatial_persona' ? 'bg-violet-500/30 text-violet-300' : 'bg-blue-500/30 text-blue-300'
                  }`}>{p.user_name?.charAt(0)}</span>
                  <span className="text-[8px] text-white flex-1 truncate">{p.user_name}</span>
                  <Badge className={`text-[6px] ${headset.color}`}>{headset.label}</Badge>
                  {p.is_speaking && <span className="w-1 h-1 rounded-full bg-emerald-400 animate-pulse" />}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
