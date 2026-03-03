import { useState, useEffect, useCallback, useRef } from 'react';
import { Scan, MapPin, Sun, Maximize2, RotateCcw, Wifi, WifiOff, Crosshair, Loader2, Zap, AlertTriangle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

export default function SpatialTrackingPanel({ meetingId }) {
  const [tracking, setTracking] = useState(null);
  const [connected, setConnected] = useState(false);
  const [calibrating, setCalibrating] = useState(false);
  const [connectPhase, setConnectPhase] = useState(null);
  const prevPositions = useRef([]);

  const fetchStream = useCallback(async () => {
    if (!connected) return;
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/simulation/${meetingId}/slam-stream`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        prevPositions.current = tracking?.positions || [];
        setTracking(data);
      }
    } catch {}
  }, [meetingId, connected, tracking?.positions]);

  useEffect(() => {
    if (!connected) return;
    fetchStream();
    const interval = setInterval(fetchStream, 1500);
    return () => clearInterval(interval);
  }, [connected]); // eslint-disable-line

  const handleConnect = () => {
    setConnectPhase('scanning');
    setTimeout(() => setConnectPhase('initializing'), 1200);
    setTimeout(() => { setConnectPhase('done'); setConnected(true); toast.success('SLAM sensor connected'); }, 2800);
  };

  const handleCalibrate = () => {
    setCalibrating(true);
    setTimeout(() => { setCalibrating(false); toast.success('Room calibration complete'); }, 2500);
  };

  const positions = tracking?.positions || [];
  const adjustments = tracking?.frame_adjustments || [];
  const lighting = tracking?.room_lighting || {};
  const pointCloud = tracking?.point_cloud || {};

  return (
    <div className="flex-1 flex flex-col overflow-hidden" data-testid="spatial-tracking-panel">
      <div className="p-3 border-b border-white/[0.06]">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-rose-500/20 to-pink-500/10 flex items-center justify-center">
            <Scan className="w-3.5 h-3.5 text-rose-400" />
          </div>
          <div className="flex-1">
            <h3 className="text-xs font-semibold text-white">SLAM Tracking</h3>
            <p className="text-[9px] text-slate-500">3D room mapping & auto-framing</p>
          </div>
          <Badge className={`text-[7px] ${connected ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-slate-500/10 text-slate-400 border-slate-500/20'}`}>
            {connected ? <><Wifi className="w-2 h-2 mr-0.5" />Live</> : <><WifiOff className="w-2 h-2 mr-0.5" />Off</>}
          </Badge>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-2.5">
        {!connected ? (
          <div className="text-center py-6 animate-fade-in">
            <div className="w-14 h-14 rounded-2xl bg-rose-500/10 flex items-center justify-center mx-auto mb-3 relative">
              <Scan className={`w-7 h-7 text-rose-400/50 ${connectPhase === 'scanning' ? 'animate-scan-rotate' : ''}`} />
              {connectPhase === 'scanning' && <div className="absolute inset-0 rounded-2xl border border-rose-400/30 animate-pulse-ring" />}
            </div>
            {!connectPhase ? (
              <>
                <p className="text-xs text-white font-medium mb-1">Connect SLAM Sensor</p>
                <p className="text-[10px] text-slate-500 mb-4">Enable 3D room tracking for auto-framing</p>
                <Button size="sm" onClick={handleConnect} className="bg-gradient-to-r from-rose-500 to-pink-500 text-white rounded-xl shadow-lg shadow-rose-500/20 hover-scale transition-all" data-testid="connect-slam-btn">
                  <Zap className="w-3 h-3 mr-1.5" />Connect & Initialize
                </Button>
              </>
            ) : connectPhase === 'scanning' ? (
              <div className="animate-fade-in-up">
                <p className="text-xs text-rose-300 font-medium mb-1">Scanning for SLAM sensor...</p>
                <div className="w-32 h-1.5 bg-white/[0.04] rounded-full mx-auto overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-rose-500 to-pink-500 rounded-full animate-bar-grow" style={{width:'40%'}} />
                </div>
              </div>
            ) : connectPhase === 'initializing' ? (
              <div className="animate-fade-in-up">
                <p className="text-xs text-rose-300 font-medium mb-1">Initializing depth sensor...</p>
                <div className="w-32 h-1.5 bg-white/[0.04] rounded-full mx-auto overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-rose-500 to-pink-500 rounded-full transition-all duration-1000" style={{width:'80%'}} />
                </div>
                <p className="text-[9px] text-slate-500 mt-2">Calibrating IR projector</p>
              </div>
            ) : (
              <div className="animate-fade-in-scale">
                <p className="text-xs text-emerald-400 font-medium mb-1">Connected!</p>
                <Loader2 className="w-4 h-4 text-emerald-400 animate-spin mx-auto" />
              </div>
            )}
          </div>
        ) : (
          <>
            {/* Status row */}
            <div className="flex items-center justify-between" data-testid="slam-status">
              <div className="flex items-center gap-1.5">
                <span className="relative flex h-2 w-2"><span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" /><span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-400" /></span>
                <span className="text-[9px] text-emerald-400 font-medium">SLAM Active</span>
                <span className="text-[8px] text-slate-500">{tracking?.tracking_fps || 30} FPS</span>
                <span className="text-[8px] text-slate-500">{tracking?.depth_accuracy_mm || 12}mm</span>
              </div>
              <Button size="sm" variant="ghost" onClick={handleCalibrate} disabled={calibrating}
                className="h-6 px-2 text-[8px] text-rose-400 hover:bg-rose-500/10 rounded-lg" data-testid="calibrate-btn">
                {calibrating ? <Loader2 className="w-3 h-3 animate-spin" /> : <><RotateCcw className="w-2.5 h-2.5 mr-1" />Calibrate</>}
              </Button>
            </div>

            {/* Point Cloud Stats */}
            <div className="flex gap-1.5">
              <div className="flex-1 p-1.5 rounded-lg border border-white/[0.04] bg-white/[0.02]">
                <p className="text-[7px] text-slate-500 uppercase">Point Cloud</p>
                <p className="text-xs font-bold text-white">{pointCloud.density?.toLocaleString() || '2,400'}</p>
              </div>
              <div className="flex-1 p-1.5 rounded-lg border border-white/[0.04] bg-white/[0.02]">
                <p className="text-[7px] text-slate-500 uppercase">Coverage</p>
                <p className="text-xs font-bold text-white">{Math.round((pointCloud.coverage || 0.92) * 100)}%</p>
              </div>
              {tracking?.drift_detected && (
                <div className="flex-1 p-1.5 rounded-lg border border-amber-500/20 bg-amber-500/5">
                  <p className="text-[7px] text-amber-400 uppercase flex items-center gap-0.5"><AlertTriangle className="w-2 h-2" />Drift</p>
                  <p className="text-xs font-bold text-amber-300">{tracking.drift_mm}mm</p>
                </div>
              )}
            </div>

            {/* Room Map */}
            <div className="relative aspect-[4/3] bg-gradient-to-b from-slate-900/90 to-slate-950/95 rounded-xl border border-white/[0.06] overflow-hidden" data-testid="room-map-visual">
              {calibrating && (
                <div className="absolute inset-0 z-20 flex items-center justify-center bg-black/50 backdrop-blur-sm animate-fade-in">
                  <div className="text-center"><Crosshair className="w-8 h-8 text-rose-400 animate-spin mx-auto mb-2" /><p className="text-[10px] text-rose-300 font-medium">Calibrating...</p></div>
                </div>
              )}
              <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: 'radial-gradient(circle, rgba(255,255,255,0.5) 1px, transparent 1px)', backgroundSize: '20px 20px' }} />
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-24 h-14 rounded-full border border-rose-500/15 bg-rose-500/[0.03]" />

              {positions.map((p, i) => {
                const left = 50 + (p.x / 4) * 40;
                const top = 50 + (p.z ? (p.z - 2.5) / 3 : 0) * 40;
                return (
                  <div key={p.user_id || i}
                    className="absolute -ml-3 -mt-3 group"
                    style={{ left: `${Math.max(5, Math.min(95, left))}%`, top: `${Math.max(5, Math.min(95, top))}%`, transition: 'left 1.2s ease-out, top 1.2s ease-out' }}>
                    {p.is_speaking && <div className="absolute -inset-1 rounded-full border border-emerald-400/40 animate-pulse-ring" />}
                    <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[7px] font-bold text-white transition-all duration-500 ${
                      p.is_speaking ? 'bg-emerald-500 ring-2 ring-emerald-400/30 scale-125' :
                      p.is_remote ? 'bg-blue-500/80 ring-1 ring-blue-400/30' : 'bg-rose-500/80 ring-1 ring-rose-400/30'
                    }`}>
                      {(p.user_name || `U${i}`).charAt(0)}
                    </div>
                    <div className="absolute top-1/2 left-1/2 w-3 h-0.5 bg-white/20 origin-left rounded-full" style={{ transform: `rotate(${p.yaw || 0}deg) translateY(-50%)`, transition: 'transform 1s ease-out' }} />
                    <div className="hidden group-hover:block absolute -top-6 left-1/2 -translate-x-1/2 whitespace-nowrap bg-black/90 backdrop-blur-sm rounded-lg px-2 py-1 text-[7px] text-white z-10 border border-white/10">
                      {p.user_name} {p.is_remote ? '(remote)' : '(room)'} &middot; {Math.round(p.face_confidence * 100)}%
                      {p.is_speaking && <span className="text-emerald-400 ml-1">speaking</span>}
                    </div>
                  </div>
                );
              })}
              <div className="absolute bottom-2 left-2 flex items-center gap-2">
                <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-rose-500/80" /><span className="text-[7px] text-slate-500">In-room</span></div>
                <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-blue-500/80" /><span className="text-[7px] text-slate-500">Remote</span></div>
                <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-emerald-500" /><span className="text-[7px] text-slate-500">Speaking</span></div>
              </div>
            </div>

            {/* Lighting */}
            <div className="p-2.5 rounded-xl border border-white/[0.06] bg-gradient-to-r from-white/[0.02] to-transparent" data-testid="lighting-status">
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-[9px] text-slate-400 flex items-center gap-1.5"><Sun className="w-3 h-3 text-amber-400" />Room Lighting</span>
                <div className="flex items-center gap-1.5">
                  <span className="text-[8px] text-slate-500">{lighting.lux || 380} lux</span>
                  <Badge className={`text-[7px] ${
                    lighting.quality > 0.7 ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                    lighting.quality > 0.5 ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' :
                    'bg-red-500/10 text-red-400 border-red-500/20'
                  }`}>{lighting.recommendation === 'optimal' ? 'Optimal' : 'Adjust'}</Badge>
                </div>
              </div>
              <div className="w-full h-2 bg-white/[0.04] rounded-full overflow-hidden">
                <div className="h-full rounded-full transition-all duration-1000 ease-out" style={{
                  width: `${(lighting.quality || 0.78) * 100}%`,
                  background: lighting.quality > 0.7 ? 'linear-gradient(90deg, #34d399, #10b981)' : lighting.quality > 0.5 ? 'linear-gradient(90deg, #fbbf24, #f59e0b)' : 'linear-gradient(90deg, #f87171, #ef4444)'
                }} />
              </div>
            </div>

            {/* Frame Adjustments */}
            <div data-testid="frame-adjustments">
              <p className="text-[9px] font-semibold text-slate-400 uppercase tracking-widest mb-1.5">Auto-Frame Adjustments</p>
              <div className="space-y-1">
                {adjustments.slice(0, 6).map((adj, i) => (
                  <div key={adj.user_id || i} className="flex items-center gap-2 p-1.5 rounded-lg bg-white/[0.02] border border-white/[0.04] hover:bg-white/[0.04] transition-all">
                    <Maximize2 className="w-3 h-3 text-rose-400 shrink-0" />
                    <span className="text-[9px] text-white truncate w-16">{positions[i]?.user_name || adj.user_id}</span>
                    <div className="flex-1 flex gap-2 text-[8px]">
                      <span className="text-slate-500">Crop <span className="text-white font-medium">{Math.round(adj.crop_width * 100)}%</span></span>
                      <span className="text-slate-500">Bright <span className={adj.brightness_adjust > 0 ? 'text-amber-400' : 'text-blue-400'}>{adj.brightness_adjust > 0 ? '+' : ''}{Math.round(adj.brightness_adjust * 100)}%</span></span>
                    </div>
                    {adj.auto_framing_active && <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />}
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
