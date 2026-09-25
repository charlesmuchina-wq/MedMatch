import { useState, useEffect, useCallback } from 'react';
import { Radio, Volume2 } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import PreviewBadge from '@/components/KarauMeet/PreviewBadge';

const API = process.env.REACT_APP_BACKEND_URL;

const BEAM_MODES = [
  { id: 'auto', label: 'Auto', desc: 'AI tracks speaker' },
  { id: 'directional', label: 'Directional', desc: 'Focus on target' },
  { id: 'omni', label: 'Omnidirectional', desc: 'Equal pickup' },
  { id: 'interview', label: 'Interview', desc: 'Two-person focus' },
];

const QUALITY_COLORS = {
  excellent: 'text-emerald-400 bg-emerald-500/10',
  good: 'text-blue-400 bg-blue-500/10',
  fair: 'text-amber-400 bg-amber-500/10',
  poor: 'text-red-400 bg-red-500/10',
};

export default function BeamformingPanel({ meetingId }) {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchStream = useCallback(async () => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/simulation/${meetingId}/audio-stream`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) setStatus(await res.json());
    } catch {}
    setLoading(false);
  }, [meetingId]);

  useEffect(() => {
    fetchStream();
    const interval = setInterval(fetchStream, 1500);
    return () => clearInterval(interval);
  }, [fetchStream]);

  const setBeamMode = async (mode) => {
    const token = localStorage.getItem('token');
    try {
      await fetch(`${API}/api/karau/beamforming/${meetingId}/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ mode, beam_width: mode === 'interview' ? 40 : 60 })
      });
    } catch {}
  };

  if (loading) return <div className="p-3 text-[9px] text-slate-500 animate-soft-pulse">Analyzing audio environment...</div>;

  const config = status?.config || {};
  const health = status?.health || {};
  const profiles = status?.audio_profiles || [];
  const beamPattern = status?.beam_pattern || [];
  const spectrum = status?.spectrum || [];
  const activeSpeaker = status?.active_speaker;

  return (
    <div className="flex-1 flex flex-col overflow-hidden" data-testid="beamforming-panel">
      <div className="p-3 border-b border-white/[0.06]">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-sky-500/20 to-blue-500/10 flex items-center justify-center">
            <Radio className="w-3.5 h-3.5 text-sky-400" />
          </div>
          <div className="flex-1">
            <h3 className="text-xs font-semibold text-white">Beamforming Audio</h3>
            <p className="text-[9px] text-slate-500">Directional audio & noise filtering</p>
          </div>
          <PreviewBadge className="ml-auto" />
          {activeSpeaker && (
            <Badge className="text-[7px] bg-emerald-500/10 text-emerald-400 border-emerald-500/20">
              <Volume2 className="w-2 h-2 mr-0.5" />{activeSpeaker.split(' ')[0]}
            </Badge>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        <div className="flex items-center justify-between p-2 bg-sky-500/5 border border-sky-500/10 rounded-lg" data-testid="audio-health">
          <div>
            <p className="text-[8px] text-slate-400">Audio Quality</p>
            <p className="text-sm font-bold text-white">{health.overall_snr_db || 0} dB SNR</p>
          </div>
          <Badge className={`text-[8px] ${QUALITY_COLORS[health.quality_rating] || QUALITY_COLORS.good}`}>
            {health.quality_rating || 'good'}
          </Badge>
        </div>

        <div className="relative aspect-square bg-slate-900/80 rounded-lg border border-white/5 p-1" data-testid="beam-pattern">
          <svg viewBox="0 0 200 200" className="w-full h-full">
            {[0.25, 0.5, 0.75, 1].map(r => (
              <circle key={r} cx="100" cy="100" r={r * 80} fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="0.5" />
            ))}
            <line x1="100" y1="20" x2="100" y2="180" stroke="rgba(255,255,255,0.04)" strokeWidth="0.5" />
            <line x1="20" y1="100" x2="180" y2="100" stroke="rgba(255,255,255,0.04)" strokeWidth="0.5" />
            {beamPattern.length > 0 && (
              <polygon
                points={beamPattern.map(p => {
                  const rad = (p.angle * Math.PI) / 180;
                  const r = p.gain * 75;
                  return `${100 + r * Math.sin(rad)},${100 - r * Math.cos(rad)}`;
                }).join(' ')}
                fill="rgba(56,189,248,0.12)"
                stroke="rgba(56,189,248,0.5)"
                strokeWidth="1.5"
              />
            )}
            {config.target_angle !== undefined && (() => {
              const rad = (config.target_angle * Math.PI) / 180;
              return <line x1="100" y1="100" x2={100 + 70 * Math.sin(rad)} y2={100 - 70 * Math.cos(rad)} stroke="rgba(56,189,248,0.8)" strokeWidth="2" strokeLinecap="round" />;
            })()}
            <circle cx="100" cy="100" r="3" fill="#38bdf8" />
          </svg>
        </div>

        {spectrum.length > 0 && (
          <div className="flex items-end gap-1 h-12 p-1 bg-slate-900/60 rounded-lg border border-white/[0.04]" data-testid="frequency-spectrum">
            {spectrum.map((band, i) => {
              const normalized = Math.max(0, Math.min(1, (band.level_db + 50) / 40));
              return (
                <div key={i} className="flex-1 flex flex-col items-center gap-0.5">
                  <div className="w-full rounded-t-sm transition-all duration-700" style={{
                    height: `${normalized * 100}%`,
                    backgroundColor: `rgba(56, 189, 248, ${0.3 + normalized * 0.5})`,
                    minHeight: '2px',
                  }} />
                  <span className="text-[5px] text-slate-600">{band.frequency >= 1000 ? `${band.frequency/1000}k` : band.frequency}</span>
                </div>
              );
            })}
          </div>
        )}

        <div className="grid grid-cols-2 gap-1" data-testid="beam-modes">
          {BEAM_MODES.map(bm => (
            <button key={bm.id} onClick={() => setBeamMode(bm.id)}
              className={`p-1.5 rounded-lg border text-left transition-all ${
                config.mode === bm.id ? 'bg-sky-500/10 border-sky-500/20 text-sky-300' : 'bg-karau-bg/30 border-white/5 text-slate-400 hover:bg-white/5'
              }`} data-testid={`beam-mode-${bm.id}`}>
              <p className="text-[9px] font-medium">{bm.label}</p>
              <p className="text-[7px] opacity-60">{bm.desc}</p>
            </button>
          ))}
        </div>

        <div className="grid grid-cols-3 gap-1 text-center" data-testid="processing-stats">
          <div className="p-1.5 bg-karau-bg/30 rounded-lg border border-white/5">
            <p className="text-xs font-bold text-white">{health.processing_latency_ms || 3.2}ms</p>
            <p className="text-[7px] text-slate-400">Latency</p>
          </div>
          <div className="p-1.5 bg-karau-bg/30 rounded-lg border border-white/5">
            <p className="text-xs font-bold text-white">{health.sample_rate ? health.sample_rate / 1000 : 48}kHz</p>
            <p className="text-[7px] text-slate-400">Sample Rate</p>
          </div>
          <div className="p-1.5 bg-karau-bg/30 rounded-lg border border-white/5">
            <p className="text-xs font-bold text-white">{health.channels || 2}ch</p>
            <p className="text-[7px] text-slate-400">Channels</p>
          </div>
        </div>

        <div data-testid="audio-profiles">
          <p className="text-[8px] text-slate-400 uppercase tracking-wider mb-1">User Audio Profiles</p>
          <div className="space-y-0.5">
            {profiles.map((p, i) => (
              <div key={p.user_id || i} className="flex items-center gap-1.5 p-1 rounded bg-karau-bg/30">
                <div className="relative">
                  <Volume2 className="w-2.5 h-2.5 text-sky-400 shrink-0" />
                  {p.is_speaking && <div className="absolute -top-0.5 -right-0.5 w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />}
                </div>
                <span className={`text-[8px] truncate w-14 ${p.is_speaking ? 'text-white font-medium' : 'text-slate-400'}`}>{p.user_name || p.user_id}</span>
                <div className="flex-1 h-1.5 bg-white/5 rounded-full overflow-hidden">
                  <div className="h-full rounded-full transition-all duration-1000" style={{
                    width: `${Math.max(5, Math.min(100, (p.snr_db || 30) / 45 * 100))}%`,
                    backgroundColor: p.snr_db > 30 ? '#34d399' : p.snr_db > 20 ? '#fbbf24' : '#f87171'
                  }} />
                </div>
                <Badge className={`text-[6px] ${
                  p.noise_type === 'ambient' ? 'bg-slate-500/10 text-slate-400' :
                  p.noise_type === 'hvac' ? 'bg-amber-500/10 text-amber-400' :
                  p.noise_type === 'keyboard' ? 'bg-blue-500/10 text-blue-400' :
                  'bg-red-500/10 text-red-400'
                }`}>{p.noise_type}</Badge>
              </div>
            ))}
          </div>
        </div>

        <div className="p-1.5 bg-karau-bg/40 rounded-lg border border-white/5" data-testid="active-filters">
          <p className="text-[8px] text-slate-400 uppercase tracking-wider mb-1">Active Processing</p>
          <div className="flex flex-wrap gap-1">
            {['Noise Cancellation', 'Echo Suppression', 'Auto Gain', 'Beamforming', 'Voice Isolation'].map(f => (
              <Badge key={f} className="text-[7px] bg-sky-500/10 text-sky-400 border border-sky-500/20">{f}</Badge>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
