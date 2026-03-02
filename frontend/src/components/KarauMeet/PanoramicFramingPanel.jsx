import { useState, useEffect, useCallback } from 'react';
import { Camera, Grid3X3, User, Aperture, Disc } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

const API = process.env.REACT_APP_BACKEND_URL;

export default function PanoramicFramingPanel({ meetingId }) {
  const [headshots, setHeadshots] = useState([]);
  const [panoramicStatus, setPanoramicStatus] = useState('initializing');

  const fetchHeadshots = useCallback(async () => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/spatial/${meetingId}/panoramic/headshots`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setHeadshots(data.headshots || []);
        setPanoramicStatus(data.panoramic_status || 'active');
      }
    } catch {}
  }, [meetingId]);

  useEffect(() => {
    fetchHeadshots();
    const interval = setInterval(fetchHeadshots, 8000);
    return () => clearInterval(interval);
  }, [fetchHeadshots]);

  return (
    <div className="flex-1 flex flex-col overflow-hidden" data-testid="panoramic-framing-panel">
      <div className="p-2.5 border-b border-white/5">
        <h3 className="text-xs font-semibold text-white flex items-center gap-1.5">
          <Disc className="w-3.5 h-3.5 text-orange-400" />
          360 Multi-Focus Framing
        </h3>
        <p className="text-[8px] text-slate-500 mt-0.5">AI headshot extraction from panoramic feed</p>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {/* Camera Status */}
        <div className="flex items-center justify-between p-2 bg-orange-500/5 border border-orange-500/10 rounded-lg" data-testid="camera-status">
          <div className="flex items-center gap-1.5">
            <Camera className="w-3 h-3 text-orange-400" />
            <span className="text-[9px] text-white">360 Camera</span>
          </div>
          <Badge className={`text-[7px] ${
            panoramicStatus === 'active' ? 'bg-emerald-500/10 text-emerald-400' :
            'bg-amber-500/10 text-amber-400'
          }`}>
            {panoramicStatus === 'active' ? 'Connected' : panoramicStatus === 'simulated' ? 'Simulated' : 'Initializing'}
          </Badge>
        </div>

        {/* Panoramic View Simulation */}
        <div className="relative w-full aspect-[3/1] bg-slate-900/80 rounded-lg border border-white/5 overflow-hidden" data-testid="panoramic-view">
          {/* Panoramic gradient background */}
          <div className="absolute inset-0 bg-gradient-to-r from-slate-800 via-slate-700 to-slate-800" />
          {/* Head indicators */}
          {headshots.map((h, i) => {
            const region = h.crop_region || {};
            const left = region.x ? (region.x / 3840) * 100 : (i + 1) * (100 / (headshots.length + 1));
            return (
              <div key={h.user_id || i}
                className="absolute top-1/2 -translate-y-1/2 flex flex-col items-center group"
                style={{ left: `${left}%` }}>
                <div className={`w-8 h-10 rounded-lg border-2 ${
                  h.is_speaking ? 'border-orange-400 bg-orange-500/20' : 'border-slate-500/50 bg-slate-600/30'
                } flex items-center justify-center`}>
                  <User className={`w-4 h-4 ${h.is_speaking ? 'text-orange-300' : 'text-slate-400'}`} />
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
              className={`relative aspect-[3/4] rounded-lg border overflow-hidden ${
                h.is_speaking ? 'border-orange-400/50 ring-1 ring-orange-400/20' : 'border-white/5'
              } bg-gradient-to-b from-slate-700/50 to-slate-800/50`}
              data-testid={`headshot-${h.user_id}`}>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <div className={`w-8 h-8 mx-auto rounded-full flex items-center justify-center text-xs font-bold ${
                    h.is_speaking ? 'bg-orange-500/30 text-orange-300' : 'bg-slate-600/50 text-slate-300'
                  }`}>
                    {(h.user_name || 'U').charAt(0)}
                  </div>
                  <p className="text-[7px] text-white mt-1 truncate">{h.user_name}</p>
                </div>
              </div>
              <div className="absolute bottom-0 inset-x-0 px-1 py-0.5 bg-black/40 text-[6px] flex justify-between">
                <span className="text-slate-300">Q: {Math.round((h.quality_score || 0.9) * 100)}%</span>
                <span className="text-slate-400">{h.gaze_direction > 0 ? '+' : ''}{Math.round(h.gaze_direction || 0)}deg</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
