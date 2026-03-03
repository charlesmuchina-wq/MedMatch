import { useState, useEffect, useCallback } from 'react';
import { Camera, User, Disc, Target, ZoomIn } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

const API = process.env.REACT_APP_BACKEND_URL;

export default function PanoramicFramingPanel({ meetingId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchStream = useCallback(async () => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/simulation/${meetingId}/camera-stream`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) setData(await res.json());
    } catch {}
    setLoading(false);
  }, [meetingId]);

  useEffect(() => {
    fetchStream();
    const interval = setInterval(fetchStream, 1500);
    return () => clearInterval(interval);
  }, [fetchStream]);

  if (loading) return <div className="p-3 text-[9px] text-slate-500 animate-soft-pulse">Connecting to 360 camera...</div>;

  const headshots = data?.headshots || [];
  const tracking = data?.auto_tracking || {};

  return (
    <div className="flex-1 flex flex-col overflow-hidden" data-testid="panoramic-framing-panel">
      <div className="p-3 border-b border-white/[0.06]">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-orange-500/20 to-amber-500/10 flex items-center justify-center">
            <Disc className="w-3.5 h-3.5 text-orange-400" />
          </div>
          <div className="flex-1">
            <h3 className="text-xs font-semibold text-white">360 Multi-Focus</h3>
            <p className="text-[9px] text-slate-500">AI headshot extraction from panoramic</p>
          </div>
          {tracking.target && (
            <Badge className="text-[7px] bg-emerald-500/10 text-emerald-400 border-emerald-500/20">
              <Target className="w-2 h-2 mr-0.5" />{tracking.target.split(' ')[0]}
            </Badge>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {/* Camera Status */}
        <div className="flex items-center justify-between p-2 bg-orange-500/5 border border-orange-500/10 rounded-lg" data-testid="camera-status">
          <div className="flex items-center gap-1.5">
            <Camera className="w-3 h-3 text-orange-400" />
            <span className="text-[9px] text-white">360 Camera</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-[7px] text-slate-500">{data?.resolution || '3840x1080'}</span>
            <span className="text-[7px] text-slate-500">{data?.frame_rate || 30}fps</span>
            <Badge className="text-[7px] bg-emerald-500/10 text-emerald-400">Connected</Badge>
          </div>
        </div>

        {/* FOV indicator */}
        <div className="flex items-center gap-2 p-1.5 bg-white/[0.02] rounded-lg border border-white/[0.04]">
          <span className="text-[8px] text-slate-400">FOV</span>
          <div className="flex-1 h-1.5 bg-white/[0.04] rounded-full overflow-hidden">
            <div className="h-full bg-orange-500/50 rounded-full transition-all duration-1000" style={{ width: `${((data?.fov_degrees || 180) / 360) * 100}%` }} />
          </div>
          <span className="text-[8px] text-white font-mono">{Math.round(data?.fov_degrees || 180)}&deg;</span>
        </div>

        {/* Panoramic View */}
        <div className="relative w-full aspect-[3/1] bg-slate-900/80 rounded-lg border border-white/5 overflow-hidden" data-testid="panoramic-view">
          <div className="absolute inset-0 bg-gradient-to-r from-slate-800 via-slate-700 to-slate-800" />
          {headshots.map((h, i) => {
            const region = h.crop_region || {};
            const left = region.x ? (region.x / 3840) * 100 : (i + 1) * (100 / (headshots.length + 1));
            return (
              <div key={h.user_id || i}
                className="absolute top-1/2 -translate-y-1/2 flex flex-col items-center group"
                style={{ left: `${left}%`, transition: 'left 1s ease-out' }}>
                <div className={`w-8 h-10 rounded-lg border-2 transition-all duration-500 ${
                  h.is_speaking ? 'border-orange-400 bg-orange-500/20 scale-110' :
                  h.was_recently_speaking ? 'border-orange-400/30 bg-orange-500/10' :
                  'border-slate-500/50 bg-slate-600/30'
                } flex items-center justify-center relative`}>
                  <User className={`w-4 h-4 ${h.is_speaking ? 'text-orange-300' : 'text-slate-400'}`} />
                  {h.tracking_lock && (
                    <div className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-emerald-500 border border-black flex items-center justify-center">
                      <Target className="w-1.5 h-1.5 text-white" />
                    </div>
                  )}
                  {h.zoom_level > 1.1 && (
                    <div className="absolute -bottom-1 -right-1 w-2.5 h-2.5 rounded-full bg-orange-500 border border-black flex items-center justify-center">
                      <ZoomIn className="w-1.5 h-1.5 text-white" />
                    </div>
                  )}
                </div>
                <span className="text-[6px] text-white mt-0.5 truncate max-w-[40px]">{h.user_name || `S${h.seat_position}`}</span>
                {h.is_speaking && <span className="w-1 h-1 rounded-full bg-orange-400 mt-0.5 animate-pulse" />}
              </div>
            );
          })}
        </div>

        {/* Extracted Headshots Grid */}
        <p className="text-[8px] text-slate-400 uppercase tracking-wider">Extracted Headshots</p>
        <div className="grid grid-cols-3 gap-1" data-testid="headshot-grid">
          {headshots.map((h, i) => (
            <div key={h.user_id || i}
              className={`relative aspect-[3/4] rounded-lg border overflow-hidden transition-all duration-500 ${
                h.is_speaking ? 'border-orange-400/50 ring-1 ring-orange-400/20 scale-[1.03]' :
                h.was_recently_speaking ? 'border-orange-400/20' : 'border-white/5'
              } bg-gradient-to-b from-slate-700/50 to-slate-800/50`}
              data-testid={`headshot-${h.user_id}`}>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <div className={`w-8 h-8 mx-auto rounded-full flex items-center justify-center text-xs font-bold transition-all ${
                    h.is_speaking ? 'bg-orange-500/30 text-orange-300 ring-2 ring-orange-400/20' : 'bg-slate-600/50 text-slate-300'
                  }`}>
                    {(h.user_name || 'U').charAt(0)}
                  </div>
                  <p className="text-[7px] text-white mt-1 truncate">{h.user_name}</p>
                  {h.is_speaking && (
                    <div className="flex items-center justify-center gap-0.5 mt-0.5">
                      {[1,2,3,2,1].map((height, j) => (
                        <div key={j} className="w-[1px] bg-orange-400 rounded-full animate-pulse" style={{ height: height * 2, animationDelay: `${j * 80}ms` }} />
                      ))}
                    </div>
                  )}
                </div>
              </div>
              <div className="absolute bottom-0 inset-x-0 px-1 py-0.5 bg-black/40 text-[6px] flex justify-between">
                <span className="text-slate-300">Q: {Math.round((h.quality_score || 0.9) * 100)}%</span>
                <span className="text-slate-400">{h.gaze_direction > 0 ? '+' : ''}{Math.round(h.gaze_direction || 0)}deg</span>
              </div>
            </div>
          ))}
        </div>

        {/* Auto-tracking info */}
        {tracking.target && (
          <div className="p-1.5 bg-orange-500/5 border border-orange-500/10 rounded-lg text-[8px]" data-testid="auto-tracking">
            <div className="flex items-center justify-between">
              <span className="text-orange-300">Auto-tracking: {tracking.target}</span>
              <span className="text-slate-400">Confidence: {Math.round((tracking.confidence || 0) * 100)}%</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
