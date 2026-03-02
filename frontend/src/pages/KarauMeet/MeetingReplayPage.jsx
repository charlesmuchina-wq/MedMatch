import { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Play, Pause, SkipForward, SkipBack, Film, Clock, Users,
  ChevronLeft, Clapperboard, Sparkles, BookOpen, Loader2,
  BarChart3, Bookmark, ZoomIn, Maximize2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

const VIEW_MODE_LABELS = {
  panoramic: { label: 'Gallery', color: 'bg-blue-500/15 text-blue-400', icon: Users },
  speaker_closeup: { label: 'Close-Up', color: 'bg-emerald-500/15 text-emerald-400', icon: ZoomIn },
  conversation: { label: 'Dialogue', color: 'bg-amber-500/15 text-amber-400', icon: Users },
};

const MOMENT_COLORS = {
  intro: 'bg-blue-500', presentation: 'bg-violet-500', discussion: 'bg-amber-500',
  decision: 'bg-emerald-500', action_item: 'bg-rose-500', speaker_change: 'bg-cyan-500',
  wrap_up: 'bg-slate-500',
};

const TRANSITION_LABELS = { smooth: 'Smooth Pan', cut: 'Hard Cut', dissolve: 'Dissolve' };

export default function MeetingReplayPage() {
  const { meetingId } = useParams();
  const navigate = useNavigate();
  const [replay, setReplay] = useState(null);
  const [loading, setLoading] = useState(true);
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [currentCutIdx, setCurrentCutIdx] = useState(0);
  const [highlights, setHighlights] = useState(null);
  const [hlLoading, setHlLoading] = useState(false);
  const [hlStyle, setHlStyle] = useState('executive_summary');
  const timerRef = useRef(null);

  const fetchReplay = useCallback(async () => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/replay/${meetingId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) setReplay(await res.json());
      else toast.error('Replay not found');
    } catch { toast.error('Failed to load replay'); }
    setLoading(false);
  }, [meetingId]);

  useEffect(() => { fetchReplay(); }, [fetchReplay]);

  // Playback timer
  useEffect(() => {
    if (playing && replay) {
      timerRef.current = setInterval(() => {
        setCurrentTime(prev => {
          const next = prev + 0.5;
          if (next >= (replay.duration_seconds || 0)) { setPlaying(false); return prev; }
          return next;
        });
      }, 500);
    }
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [playing, replay]);

  // Track current cut based on time
  useEffect(() => {
    if (!replay?.director_cuts) return;
    const cuts = replay.director_cuts;
    let idx = 0;
    for (let i = cuts.length - 1; i >= 0; i--) {
      if (currentTime >= (cuts[i].timestamp_seconds || 0)) { idx = i; break; }
    }
    setCurrentCutIdx(idx);
  }, [currentTime, replay]);

  const seekTo = (ts) => { setCurrentTime(ts); };
  const skipForward = () => seekTo(Math.min(currentTime + 15, replay?.duration_seconds || 0));
  const skipBack = () => seekTo(Math.max(currentTime - 15, 0));

  const generateHighlights = async () => {
    setHlLoading(true);
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/replay/generate-highlights`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ meeting_id: meetingId, style: hlStyle })
      });
      if (res.ok) { setHighlights(await res.json()); toast.success('Highlights generated'); }
    } catch {}
    setHlLoading(false);
  };

  const formatTime = (s) => {
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    return `${m.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
  };

  if (loading) return (
    <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
      <Loader2 className="w-8 h-8 text-violet-400 animate-spin" />
    </div>
  );

  if (!replay) return (
    <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center text-white">
      <p>Replay not found</p>
    </div>
  );

  const cuts = replay.director_cuts || [];
  const moments = replay.key_moments || [];
  const transcript = replay.transcript_segments || [];
  const currentCut = cuts[currentCutIdx] || {};
  const viewInfo = VIEW_MODE_LABELS[currentCut.view_mode] || VIEW_MODE_LABELS.panoramic;
  const ViewIcon = viewInfo.icon;
  const duration = replay.duration_seconds || 1;
  const progress = (currentTime / duration) * 100;

  // Current transcript segment
  const currentTranscript = transcript.filter(t => t.ts <= currentTime).slice(-3);

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white" data-testid="meeting-replay-page">
      {/* Top Bar */}
      <div className="h-12 border-b border-white/5 flex items-center justify-between px-4 bg-[#0a0a0f]/90 backdrop-blur-sm sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={() => navigate('/karau-meet/dashboard')}
            className="h-7 text-slate-400 hover:text-white" data-testid="back-btn">
            <ChevronLeft className="w-4 h-4" />
          </Button>
          <Film className="w-4 h-4 text-violet-400" />
          <h1 className="text-sm font-semibold truncate max-w-[300px]">{replay.title}</h1>
          <Badge className="text-[8px] bg-violet-500/10 text-violet-400 border border-violet-500/20">Director's Cut</Badge>
        </div>
        <div className="flex items-center gap-3 text-[10px] text-slate-400">
          <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{formatTime(duration)}</span>
          <span className="flex items-center gap-1"><Clapperboard className="w-3 h-3" />{cuts.length} cuts</span>
          <span className="flex items-center gap-1"><Bookmark className="w-3 h-3" />{moments.length} moments</span>
        </div>
      </div>

      <div className="flex h-[calc(100vh-3rem)]">
        {/* Main Replay Area */}
        <div className="flex-1 flex flex-col">
          {/* Video Simulation Area */}
          <div className="flex-1 relative bg-gradient-to-b from-slate-900/50 to-[#0a0a0f] flex items-center justify-center" data-testid="replay-viewport">
            {/* Camera View Simulation */}
            <div className={`relative transition-all duration-700 ease-in-out ${
              currentCut.view_mode === 'panoramic' ? 'w-[90%] aspect-video' :
              currentCut.view_mode === 'speaker_closeup' ? 'w-[50%] aspect-[3/4]' :
              'w-[80%] aspect-video'
            }`}>
              <div className="absolute inset-0 rounded-2xl border border-white/5 bg-gradient-to-b from-slate-800/60 to-slate-900/60 overflow-hidden">
                {/* View Mode Visual */}
                {currentCut.view_mode === 'panoramic' && (
                  <div className="grid grid-cols-3 grid-rows-2 gap-1 p-2 h-full">
                    {['Alex', 'Sarah', 'James', 'Maria', 'David', 'Emma'].map((name, i) => (
                      <div key={i} className="rounded-lg bg-slate-700/40 border border-white/5 flex items-center justify-center">
                        <div className="text-center">
                          <div className="w-10 h-10 mx-auto rounded-full bg-gradient-to-br from-slate-600 to-slate-700 flex items-center justify-center text-lg font-bold text-white/60">{name[0]}</div>
                          <p className="text-[9px] text-slate-400 mt-1">{name}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                {currentCut.view_mode === 'speaker_closeup' && (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                      <div className="w-24 h-24 mx-auto rounded-full bg-gradient-to-br from-emerald-500/30 to-emerald-600/20 border-2 border-emerald-400/30 flex items-center justify-center animate-pulse">
                        <span className="text-3xl font-bold text-emerald-300">{(currentCut.focus_users?.[0] || 'S')[0].toUpperCase()}</span>
                      </div>
                      <p className="text-sm text-white mt-3 font-medium">{currentCut.focus_users?.[0] || 'Speaker'}</p>
                      <p className="text-[10px] text-emerald-400 mt-0.5">Speaking</p>
                    </div>
                  </div>
                )}
                {currentCut.view_mode === 'conversation' && (
                  <div className="flex items-center justify-center h-full gap-8 px-8">
                    {(currentCut.focus_users || ['Speaker 1', 'Speaker 2']).map((name, i) => (
                      <div key={i} className="text-center flex-1">
                        <div className="w-20 h-20 mx-auto rounded-full bg-gradient-to-br from-amber-500/30 to-amber-600/20 border-2 border-amber-400/30 flex items-center justify-center">
                          <span className="text-2xl font-bold text-amber-300">{(name || 'S')[0].toUpperCase()}</span>
                        </div>
                        <p className="text-sm text-white mt-2 font-medium">{name}</p>
                      </div>
                    ))}
                  </div>
                )}

                {/* Overlay Info */}
                <div className="absolute top-3 left-3 flex items-center gap-2">
                  <Badge className={`text-[8px] ${viewInfo.color}`}>
                    <ViewIcon className="w-2.5 h-2.5 mr-0.5" />{viewInfo.label}
                  </Badge>
                  {currentCut.transition && currentCut.transition !== 'smooth' && (
                    <Badge className="text-[7px] bg-white/5 text-slate-400">{TRANSITION_LABELS[currentCut.transition]}</Badge>
                  )}
                </div>
                <div className="absolute top-3 right-3 text-[10px] text-slate-400 font-mono">{formatTime(currentTime)}</div>
              </div>
            </div>

            {/* Live Transcript */}
            {currentTranscript.length > 0 && (
              <div className="absolute bottom-4 left-1/2 -translate-x-1/2 max-w-[60%]" data-testid="replay-transcript">
                {currentTranscript.map((t, i) => (
                  <p key={i} className={`text-center text-sm py-0.5 px-3 rounded bg-black/60 backdrop-blur-sm mb-1 ${
                    i === currentTranscript.length - 1 ? 'text-white' : 'text-slate-400'
                  }`}>
                    <span className="text-violet-400 font-medium">{t.speaker}: </span>{t.text}
                  </p>
                ))}
              </div>
            )}
          </div>

          {/* Playback Controls */}
          <div className="border-t border-white/5 bg-[#0a0a0f]/90 backdrop-blur-sm p-3" data-testid="playback-controls">
            {/* Timeline with cuts and moments */}
            <div className="relative h-8 mb-2">
              {/* Progress bar background */}
              <div className="absolute top-3 inset-x-0 h-1.5 bg-white/5 rounded-full cursor-pointer"
                onClick={e => {
                  const rect = e.currentTarget.getBoundingClientRect();
                  seekTo((e.clientX - rect.left) / rect.width * duration);
                }}>
                <div className="h-full bg-gradient-to-r from-violet-500 to-fuchsia-500 rounded-full transition-all" style={{ width: `${progress}%` }} />
              </div>

              {/* Key moment markers */}
              {moments.map((m, i) => (
                <button key={i} onClick={() => seekTo(m.ts)}
                  className="absolute top-1 -ml-1 w-2 h-5 group" style={{ left: `${(m.ts / duration) * 100}%` }}
                  data-testid={`moment-marker-${i}`}>
                  <div className={`w-2 h-2 rounded-full ${MOMENT_COLORS[m.type] || 'bg-slate-500'}`} />
                  <div className="hidden group-hover:block absolute bottom-full mb-1 left-1/2 -translate-x-1/2 whitespace-nowrap bg-black/90 rounded px-2 py-1 text-[8px] text-white z-10">
                    {m.label}
                  </div>
                </button>
              ))}

              {/* Playhead */}
              <div className="absolute top-1.5 w-3 h-3 rounded-full bg-white shadow-lg shadow-violet-500/30 -ml-1.5 transition-all"
                style={{ left: `${progress}%` }} />
            </div>

            {/* Controls */}
            <div className="flex items-center justify-between">
              <span className="text-[11px] text-slate-400 font-mono w-20">{formatTime(currentTime)} / {formatTime(duration)}</span>
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="sm" onClick={skipBack} className="h-8 w-8 rounded-full text-white hover:bg-white/10" data-testid="skip-back-btn">
                  <SkipBack className="w-4 h-4" />
                </Button>
                <Button size="sm" onClick={() => setPlaying(!playing)}
                  className="h-10 w-10 rounded-full bg-violet-500 hover:bg-violet-400 text-white" data-testid="play-pause-btn">
                  {playing ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 ml-0.5" />}
                </Button>
                <Button variant="ghost" size="sm" onClick={skipForward} className="h-8 w-8 rounded-full text-white hover:bg-white/10" data-testid="skip-forward-btn">
                  <SkipForward className="w-4 h-4" />
                </Button>
              </div>
              <div className="flex items-center gap-2 w-20 justify-end">
                <Badge className="text-[8px] bg-white/5 text-slate-300">Cut {currentCutIdx + 1}/{cuts.length}</Badge>
              </div>
            </div>
          </div>
        </div>

        {/* Right Sidebar - Key Moments & Highlights */}
        <div className="w-80 border-l border-white/5 flex flex-col bg-[#0d0d14]" data-testid="replay-sidebar">
          {/* Key Moments */}
          <div className="flex-1 overflow-y-auto">
            <div className="p-3 border-b border-white/5">
              <h3 className="text-xs font-semibold text-white flex items-center gap-1.5">
                <Bookmark className="w-3.5 h-3.5 text-violet-400" />Key Moments
              </h3>
            </div>
            <div className="p-2 space-y-1">
              {moments.map((m, i) => {
                const isActive = currentTime >= m.ts && (i === moments.length - 1 || currentTime < (moments[i + 1]?.ts || Infinity));
                return (
                  <button key={i} onClick={() => seekTo(m.ts)}
                    className={`w-full text-left p-2 rounded-lg border transition-all ${
                      isActive ? 'bg-violet-500/10 border-violet-500/20' : 'bg-karau-bg/20 border-white/3 hover:bg-white/5'
                    }`} data-testid={`moment-${i}`}>
                    <div className="flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full shrink-0 ${MOMENT_COLORS[m.type] || 'bg-slate-500'}`} />
                      <span className="text-[9px] text-slate-400 font-mono">{formatTime(m.ts)}</span>
                      <Badge className="text-[7px] bg-white/5 text-slate-300">{m.type?.replace('_', ' ')}</Badge>
                    </div>
                    <p className="text-[10px] text-white mt-1 ml-4">{m.label}</p>
                  </button>
                );
              })}
            </div>

            {/* View Distribution */}
            {replay.view_distribution && (
              <div className="p-3 border-t border-white/5" data-testid="view-distribution">
                <h3 className="text-xs font-semibold text-white flex items-center gap-1.5 mb-2">
                  <BarChart3 className="w-3.5 h-3.5 text-cyan-400" />View Distribution
                </h3>
                <div className="space-y-1">
                  {Object.entries(replay.view_distribution).map(([mode, pct]) => {
                    const info = VIEW_MODE_LABELS[mode] || { label: mode, color: 'bg-slate-500/15 text-slate-400' };
                    return (
                      <div key={mode} className="flex items-center gap-2">
                        <span className="text-[9px] text-slate-400 w-16">{info.label}</span>
                        <div className="flex-1 h-1.5 bg-white/5 rounded-full overflow-hidden">
                          <div className="h-full rounded-full bg-violet-500/60" style={{ width: `${pct}%` }} />
                        </div>
                        <span className="text-[9px] text-white w-8 text-right">{pct}%</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* AI Highlights Generator */}
          <div className="border-t border-white/5 p-3" data-testid="highlights-section">
            <h3 className="text-xs font-semibold text-white flex items-center gap-1.5 mb-2">
              <Sparkles className="w-3.5 h-3.5 text-fuchsia-400" />AI Highlights
            </h3>
            <div className="flex gap-1 mb-2">
              {['executive_summary', 'action_items', 'full_replay'].map(s => (
                <button key={s} onClick={() => setHlStyle(s)}
                  className={`flex-1 text-[8px] py-1 rounded-lg border transition-all ${
                    hlStyle === s ? 'bg-fuchsia-500/10 border-fuchsia-500/20 text-fuchsia-300' : 'border-white/5 text-slate-400 hover:bg-white/5'
                  }`} data-testid={`hl-style-${s}`}>
                  {s.replace('_', ' ')}
                </button>
              ))}
            </div>
            <Button size="sm" onClick={generateHighlights} disabled={hlLoading}
              className="w-full h-7 text-[10px] bg-fuchsia-500/80 hover:bg-fuchsia-400 rounded-lg" data-testid="generate-highlights-btn">
              {hlLoading ? <><Loader2 className="w-3 h-3 mr-1 animate-spin" />Generating...</> : <><Sparkles className="w-3 h-3 mr-1" />Generate Highlights</>}
            </Button>
            {highlights?.highlights && (
              <div className="mt-2 max-h-40 overflow-y-auto p-2 bg-karau-bg/40 rounded-lg border border-white/5 text-[9px] text-slate-300 whitespace-pre-wrap" data-testid="highlights-content">
                {highlights.highlights}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
