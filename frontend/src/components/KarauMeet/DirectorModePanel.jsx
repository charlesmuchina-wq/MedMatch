import { useState, useEffect, useCallback } from 'react';
import { Clapperboard, Camera, Users, Sparkles, Tv, Aperture, Play, Pause, RotateCcw, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

const SHOT_ICONS = {
  close_up: Aperture,
  wide: Tv,
  speaker_focus: Users,
  split_screen: Camera,
};

const SHOT_COLORS = {
  close_up: { bg: 'bg-violet-500/10', text: 'text-violet-400', border: 'border-violet-500/20' },
  wide: { bg: 'bg-blue-500/10', text: 'text-blue-400', border: 'border-blue-500/20' },
  speaker_focus: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/20' },
  split_screen: { bg: 'bg-amber-500/10', text: 'text-amber-400', border: 'border-amber-500/20' },
};

export default function DirectorModePanel({ meetingId }) {
  const [mode, setMode] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchMode = useCallback(async () => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/director/${meetingId}/mode`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) setMode(await res.json());
    } catch {}
    setLoading(false);
  }, [meetingId]);

  useEffect(() => { fetchMode(); const i = setInterval(fetchMode, 6000); return () => clearInterval(i); }, [fetchMode]);

  const setDirectorMode = async (modeType) => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/director/${meetingId}/mode`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ mode: modeType })
      });
      if (res.ok) { fetchMode(); toast.success(`Director mode: ${modeType}`); }
    } catch {}
  };

  if (loading) return (
    <div className="flex-1 flex items-center justify-center">
      <div className="text-center">
        <Loader2 className="w-5 h-5 text-violet-400 animate-spin mx-auto mb-2" />
        <p className="text-[10px] text-slate-500">Loading director...</p>
      </div>
    </div>
  );

  const activeShot = mode?.current_shot_type || 'speaker_focus';
  const activeSpeaker = mode?.active_speaker;
  const transitions = mode?.transitions || [];

  return (
    <div className="flex-1 flex flex-col overflow-hidden" data-testid="director-mode-panel">
      {/* Header */}
      <div className="p-3 border-b border-white/[0.06]">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-violet-500/20 to-purple-500/10 flex items-center justify-center">
            <Clapperboard className="w-3.5 h-3.5 text-violet-400" />
          </div>
          <div>
            <h3 className="text-xs font-semibold text-white">Cinematic Director</h3>
            <p className="text-[9px] text-slate-500">AI camera switching</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {/* Director Mode Toggle */}
        <div className="p-3 rounded-xl border border-white/[0.06] bg-gradient-to-b from-violet-500/[0.04] to-transparent">
          <div className="flex items-center justify-between mb-2.5">
            <div className="flex items-center gap-2">
              <Sparkles className="w-3.5 h-3.5 text-violet-400" />
              <span className="text-[10px] font-semibold text-white">AI Director</span>
            </div>
            <Badge className={`text-[7px] ${mode?.enabled ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-slate-500/10 text-slate-400 border-slate-500/20'}`}>
              {mode?.enabled ? 'Active' : 'Off'}
            </Badge>
          </div>

          <div className="flex gap-2">
            <Button size="sm" onClick={() => setDirectorMode('auto')}
              className={`flex-1 h-8 text-[10px] rounded-xl transition-all duration-300 ${
                mode?.mode === 'auto'
                  ? 'bg-gradient-to-r from-violet-500 to-purple-500 text-white shadow-lg shadow-violet-500/20'
                  : 'bg-white/[0.04] text-slate-400 hover:bg-white/[0.08]'
              }`} data-testid="director-auto-btn">
              <Sparkles className="w-3 h-3 mr-1" />Auto
            </Button>
            <Button size="sm" onClick={() => setDirectorMode('manual')}
              className={`flex-1 h-8 text-[10px] rounded-xl transition-all duration-300 ${
                mode?.mode === 'manual'
                  ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-lg shadow-amber-500/20'
                  : 'bg-white/[0.04] text-slate-400 hover:bg-white/[0.08]'
              }`} data-testid="director-manual-btn">
              <Camera className="w-3 h-3 mr-1" />Manual
            </Button>
          </div>
        </div>

        {/* Current Shot Info */}
        {activeSpeaker && (
          <div className="p-3 rounded-xl border border-violet-500/15 bg-gradient-to-r from-violet-500/[0.04] to-transparent animate-slide-up" data-testid="active-shot">
            <p className="text-[9px] font-semibold text-violet-400 uppercase tracking-widest mb-2">Current Frame</p>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500/20 to-purple-500/10 flex items-center justify-center">
                <Camera className="w-5 h-5 text-violet-300" />
              </div>
              <div>
                <p className="text-[11px] text-white font-medium">{activeSpeaker}</p>
                <Badge className={`text-[7px] ${SHOT_COLORS[activeShot]?.bg} ${SHOT_COLORS[activeShot]?.text} ${SHOT_COLORS[activeShot]?.border}`}>
                  {activeShot.replace(/_/g, ' ')}
                </Badge>
              </div>
            </div>
          </div>
        )}

        {/* Shot Type Grid */}
        <div data-testid="shot-types">
          <p className="text-[9px] font-semibold text-slate-400 uppercase tracking-widest mb-2">Shot Types</p>
          <div className="grid grid-cols-2 gap-1.5">
            {Object.entries(SHOT_ICONS).map(([type, Icon]) => {
              const colors = SHOT_COLORS[type] || {};
              const isActive = activeShot === type;
              return (
                <button key={type} className={`p-2.5 rounded-xl border text-left transition-all duration-200 ${
                  isActive
                    ? `${colors.bg} ${colors.border} scale-[1.02] shadow-lg`
                    : 'border-white/[0.06] bg-white/[0.02] hover:bg-white/[0.04]'
                }`} data-testid={`shot-${type}`}>
                  <Icon className={`w-4 h-4 mb-1 ${isActive ? colors.text : 'text-slate-500'}`} />
                  <p className={`text-[10px] font-medium capitalize ${isActive ? 'text-white' : 'text-slate-400'}`}>{type.replace(/_/g, ' ')}</p>
                  {isActive && (
                    <div className="flex items-center gap-1 mt-1">
                      <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                      <span className="text-[7px] text-emerald-400">Live</span>
                    </div>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Transition Log */}
        {transitions.length > 0 && (
          <div data-testid="transition-log">
            <p className="text-[9px] font-semibold text-slate-400 uppercase tracking-widest mb-2">Recent Transitions</p>
            <div className="space-y-1">
              {transitions.slice(-5).reverse().map((t, i) => (
                <div key={i} className="flex items-center gap-2 p-1.5 rounded-lg bg-white/[0.01] animate-slide-up"
                  style={{ animationDelay: `${i * 60}ms` }}>
                  <div className="w-1 h-4 rounded-full bg-violet-500/40" />
                  <div className="flex-1 min-w-0">
                    <p className="text-[9px] text-white truncate">{t.reason || 'AI Switch'}</p>
                    <p className="text-[7px] text-slate-500">{t.shot_type?.replace(/_/g, ' ') || 'auto'}</p>
                  </div>
                  <span className="text-[7px] text-slate-600 tabular-nums">{t.timestamp?.slice(11, 19) || ''}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
