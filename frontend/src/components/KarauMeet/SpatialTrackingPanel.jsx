import { useState, useEffect, useCallback } from 'react';
import { Scan, MapPin, Eye, Sun, Move3D, Maximize2, RefreshCw } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

const API = process.env.REACT_APP_BACKEND_URL;

export default function SpatialTrackingPanel({ meetingId }) {
  const [tracking, setTracking] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchTracking = useCallback(async () => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/spatial/${meetingId}/tracking`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) setTracking(await res.json());
    } catch {}
    setLoading(false);
  }, [meetingId]);

  useEffect(() => {
    fetchTracking();
    const interval = setInterval(fetchTracking, 5000);
    return () => clearInterval(interval);
  }, [fetchTracking]);

  if (loading) return <div className="p-3 text-[9px] text-slate-500">Initializing SLAM tracking...</div>;

  const positions = tracking?.positions || [];
  const adjustments = tracking?.frame_adjustments || [];
  const lighting = tracking?.room_lighting || {};

  return (
    <div className="flex-1 flex flex-col overflow-hidden" data-testid="spatial-tracking-panel">
      <div className="p-2.5 border-b border-white/5">
        <h3 className="text-xs font-semibold text-white flex items-center gap-1.5">
          <Scan className="w-3.5 h-3.5 text-rose-400" />
          SLAM Spatial Tracking
        </h3>
        <p className="text-[8px] text-slate-500 mt-0.5">3D room mapping & auto-framing</p>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {/* Status Bar */}
        <div className="flex items-center justify-between" data-testid="slam-status">
          <div className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-[9px] text-emerald-400">SLAM Active</span>
          </div>
          <div className="flex items-center gap-2 text-[8px] text-slate-400">
            <span>{tracking?.tracking_fps || 30} FPS</span>
            <span>{tracking?.depth_accuracy_mm || 12}mm depth</span>
          </div>
        </div>

        {/* Room Visualization - Top-Down View */}
        <div className="relative aspect-[4/3] bg-slate-900/80 rounded-lg border border-white/5 overflow-hidden" data-testid="room-map-visual">
          {/* Grid lines */}
          <div className="absolute inset-0 opacity-10" style={{
            backgroundImage: 'linear-gradient(rgba(255,255,255,.15) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.15) 1px, transparent 1px)',
            backgroundSize: '20% 20%'
          }} />
          {/* Table center */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-24 h-14 rounded-full border border-slate-600/50 bg-slate-800/50" />
          {/* Position dots */}
          {positions.map((p, i) => {
            const left = 50 + (p.x / 4) * 40;
            const top = 50 + (p.z ? (p.z - 2.5) / 3 : 0) * 40;
            return (
              <div key={p.user_id || i}
                className="absolute w-6 h-6 -ml-3 -mt-3 flex items-center justify-center group"
                style={{ left: `${Math.max(5, Math.min(95, left))}%`, top: `${Math.max(5, Math.min(95, top))}%` }}>
                <div className={`w-4 h-4 rounded-full flex items-center justify-center text-[6px] font-bold text-white ${p.is_remote ? 'bg-blue-500/80 ring-1 ring-blue-400/30' : 'bg-rose-500/80 ring-1 ring-rose-400/30'}`}>
                  {(p.user_name || `U${i}`).charAt(0)}
                </div>
                <div className="hidden group-hover:block absolute -top-5 left-1/2 -translate-x-1/2 whitespace-nowrap bg-black/90 rounded px-1.5 py-0.5 text-[7px] text-white z-10">
                  {p.user_name || `User ${i+1}`} {p.is_remote ? '(remote)' : '(room)'}
                </div>
              </div>
            );
          })}
        </div>

        {/* Lighting Status */}
        <div className="p-2 bg-karau-bg/40 rounded-lg border border-white/5" data-testid="lighting-status">
          <div className="flex items-center justify-between">
            <span className="text-[8px] text-slate-400 flex items-center gap-1"><Sun className="w-2.5 h-2.5" />Lighting</span>
            <Badge className={`text-[7px] ${
              lighting.quality > 0.7 ? 'bg-emerald-500/10 text-emerald-400' :
              lighting.quality > 0.5 ? 'bg-amber-500/10 text-amber-400' :
              'bg-red-500/10 text-red-400'
            }`}>
              {lighting.recommendation === 'optimal' ? 'Optimal' : 'Needs Adjustment'}
            </Badge>
          </div>
          <div className="w-full h-1.5 bg-white/5 rounded-full mt-1.5 overflow-hidden">
            <div className="h-full rounded-full transition-all" style={{
              width: `${(lighting.quality || 0.78) * 100}%`,
              backgroundColor: lighting.quality > 0.7 ? '#34d399' : lighting.quality > 0.5 ? '#fbbf24' : '#f87171'
            }} />
          </div>
          {lighting.auto_enhance && (
            <p className="text-[7px] text-amber-400 mt-1">Auto-enhancement active</p>
          )}
        </div>

        {/* Frame Adjustments Per User */}
        <div data-testid="frame-adjustments">
          <p className="text-[8px] text-slate-400 uppercase tracking-wider mb-1">Auto-Frame Adjustments</p>
          <div className="space-y-0.5">
            {adjustments.slice(0, 6).map((adj, i) => (
              <div key={adj.user_id || i} className="flex items-center gap-1.5 p-1 rounded bg-karau-bg/30 text-[8px]">
                <Maximize2 className="w-2.5 h-2.5 text-rose-400 shrink-0" />
                <span className="text-white truncate w-14">{positions[i]?.user_name || adj.user_id}</span>
                <div className="flex-1 flex gap-1">
                  <span className="text-slate-500">crop: {Math.round(adj.crop_width * 100)}%</span>
                  <span className="text-slate-500">bright: {adj.brightness_adjust > 0 ? '+' : ''}{Math.round(adj.brightness_adjust * 100)}%</span>
                </div>
                {adj.auto_framing_active && <span className="w-1 h-1 rounded-full bg-emerald-400" />}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
