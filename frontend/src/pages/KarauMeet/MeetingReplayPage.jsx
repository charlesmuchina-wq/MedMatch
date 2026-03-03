import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import {
  Play, Pause, SkipForward, SkipBack, Film, Clock, Users,
  ChevronLeft, Sparkles, Loader2, Bookmark, Volume2,
  Gauge, ChevronRight, Maximize2, Minimize2, Rewind, FastForward, Share2, Link, Check
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

const VIEW_LABELS = {
  panoramic: { label: 'Gallery', color: 'bg-blue-500/20 text-blue-300', icon: Users },
  speaker_closeup: { label: 'Close-Up', color: 'bg-emerald-500/20 text-emerald-300', icon: Maximize2 },
  conversation: { label: 'Dialogue', color: 'bg-amber-500/20 text-amber-300', icon: Users },
};

const MOMENT_COLORS = {
  intro: '#3b82f6', presentation: '#8b5cf6', discussion: '#f59e0b',
  decision: '#10b981', action_item: '#f43f5e', speaker_change: '#06b6d4', wrap_up: '#64748b',
};

const CHAPTER_ICONS = {
  intro: '01', presentation: '02', discussion: '03', decision: '04', action_item: '05', wrap_up: '06',
};

const SPEEDS = [0.5, 1, 1.5, 2];

const formatTime = (s) => {
  const m = Math.floor(s / 60);
  const sec = Math.floor(s % 60);
  return `${m.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
};

const SPEAKER_COLORS = {
  "Alex Chen": "#f43f5e",
  "Sarah Miller": "#3b82f6",
  "James Park": "#f59e0b",
  "Maria Garcia": "#10b981",
  "David Kim": "#8b5cf6",
  "Emma Wilson": "#ec4899",
};

export default function MeetingReplayPage() {
  const { meetingId } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [replay, setReplay] = useState(null);
  const [loading, setLoading] = useState(true);
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [speed, setSpeed] = useState(1);
  const [showChapters, setShowChapters] = useState(true);
  const [hlLoading, setHlLoading] = useState(false);
  const [highlights, setHighlights] = useState(null);
  const [hlStyle, setHlStyle] = useState('executive_summary');
  const [shareMarker, setShareMarker] = useState(null);
  const [copied, setCopied] = useState(false);
  const timerRef = useRef(null);
  const transcriptRef = useRef(null);
  const timelineRef = useRef(null);
  const initialSeekDone = useRef(false);

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

  // Seek to shared timestamp from URL param ?t=
  useEffect(() => {
    if (replay && !initialSeekDone.current) {
      const t = searchParams.get('t');
      if (t) {
        const ts = parseFloat(t);
        if (!isNaN(ts) && ts >= 0 && ts <= replay.duration_seconds) {
          setCurrentTime(ts);
          setShareMarker(ts);
          toast.success(`Jumped to shared moment at ${formatTime(ts)}`);
        }
      }
      initialSeekDone.current = true;
    }
  }, [replay, searchParams]);

  const shareMoment = () => {
    const ts = Math.floor(currentTime);
    const url = `${window.location.origin}/karau-meet/replay/${meetingId}?t=${ts}`;
    navigator.clipboard.writeText(url).then(() => {
      setCopied(true);
      setShareMarker(ts);
      toast.success(`Link copied! Shared moment at ${formatTime(ts)}`);
      setTimeout(() => setCopied(false), 2000);
    }).catch(() => toast.error('Failed to copy'));
  };

  useEffect(() => {
    if (playing && replay) {
      timerRef.current = setInterval(() => {
        setCurrentTime(prev => {
          const next = prev + 0.1 * speed;
          if (next >= (replay.duration_seconds || 0)) { setPlaying(false); return replay.duration_seconds; }
          return next;
        });
      }, 100);
    }
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [playing, replay, speed]);

  const seekTo = (ts) => setCurrentTime(Math.max(0, Math.min(ts, replay?.duration_seconds || 0)));
  const skipForward = () => seekTo(currentTime + 15);
  const skipBack = () => seekTo(currentTime - 15);
  const cycleSpeed = () => {
    const idx = SPEEDS.indexOf(speed);
    setSpeed(SPEEDS[(idx + 1) % SPEEDS.length]);
  };

  const currentCut = useMemo(() => {
    if (!replay?.director_cuts) return {};
    const cuts = replay.director_cuts;
    for (let i = cuts.length - 1; i >= 0; i--) {
      if (currentTime >= (cuts[i].timestamp_seconds || 0)) return cuts[i];
    }
    return cuts[0] || {};
  }, [currentTime, replay]);

  const currentChapter = useMemo(() => {
    if (!replay?.chapters) return null;
    for (let i = replay.chapters.length - 1; i >= 0; i--) {
      if (currentTime >= replay.chapters[i].start) return { ...replay.chapters[i], index: i };
    }
    return replay.chapters[0] ? { ...replay.chapters[0], index: 0 } : null;
  }, [currentTime, replay]);

  const visibleTranscript = useMemo(() => {
    if (!replay?.transcript_segments) return [];
    return replay.transcript_segments.filter(t => t.ts <= currentTime + 1).slice(-8);
  }, [currentTime, replay]);

  // Auto-scroll transcript
  useEffect(() => {
    if (transcriptRef.current) {
      transcriptRef.current.scrollTop = transcriptRef.current.scrollHeight;
    }
  }, [visibleTranscript]);

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

  if (loading) return (
    <div className="min-h-screen bg-[#08080d] flex items-center justify-center">
      <div className="text-center animate-fade-in">
        <Film className="w-10 h-10 text-violet-400 mx-auto mb-3 animate-pulse" />
        <p className="text-sm text-slate-400">Loading Director's Cut...</p>
      </div>
    </div>
  );

  if (!replay) return (
    <div className="min-h-screen bg-[#08080d] flex items-center justify-center text-white">
      <p>Replay not found</p>
    </div>
  );

  const duration = replay.duration_seconds || 1;
  const progress = (currentTime / duration) * 100;
  const chapters = replay.chapters || [];
  const moments = replay.key_moments || [];
  const waveform = replay.waveform || [];
  const viewInfo = VIEW_LABELS[currentCut.view_mode] || VIEW_LABELS.panoramic;
  const ViewIcon = viewInfo.icon;

  return (
    <div className="h-screen bg-[#08080d] text-white flex flex-col overflow-hidden" data-testid="meeting-replay-page">
      {/* Cinema Top Bar */}
      <div className="h-11 border-b border-white/[0.04] flex items-center justify-between px-4 bg-[#08080d]/95 backdrop-blur-md z-50 shrink-0">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={() => navigate('/karau-meet/dashboard')}
            className="h-7 text-slate-500 hover:text-white rounded-lg" data-testid="back-btn">
            <ChevronLeft className="w-4 h-4" />
          </Button>
          <div className="w-6 h-6 rounded-md bg-violet-500/15 flex items-center justify-center">
            <Film className="w-3 h-3 text-violet-400" />
          </div>
          <div>
            <h1 className="text-xs font-semibold truncate max-w-[280px]">{replay.title}</h1>
            <div className="flex items-center gap-2 text-[9px] text-slate-500">
              <span>{formatTime(duration)}</span>
              <span>&middot;</span>
              <span>{chapters.length} chapters</span>
              <span>&middot;</span>
              <span>{moments.length} key moments</span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" onClick={shareMoment}
            className="h-7 px-2.5 text-slate-400 hover:text-white hover:bg-white/[0.06] rounded-lg gap-1.5" data-testid="share-moment-btn">
            {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Share2 className="w-3 h-3" />}
            <span className="text-[9px]">{copied ? 'Copied!' : 'Share Moment'}</span>
          </Button>
          <Badge className="text-[8px] bg-violet-500/10 text-violet-400 border border-violet-500/20">Director's Cut</Badge>
          <button onClick={() => setShowChapters(!showChapters)}
            className="text-slate-500 hover:text-white transition-colors p-1 rounded" data-testid="toggle-chapters">
            {showChapters ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      <div className="flex-1 flex min-h-0">
        {/* Chapter Sidebar */}
        {showChapters && (
          <div className="w-56 border-r border-white/[0.04] bg-[#0a0a12] flex flex-col shrink-0 animate-fade-in-left" data-testid="chapter-sidebar">
            <div className="p-3 border-b border-white/[0.04]">
              <h3 className="text-[10px] font-semibold text-slate-400 uppercase tracking-widest">Chapters</h3>
            </div>
            <div className="flex-1 overflow-y-auto py-1">
              {chapters.map((ch, i) => {
                const isActive = currentChapter?.index === i;
                const chProgress = currentTime >= ch.end ? 100 : currentTime >= ch.start ? ((currentTime - ch.start) / (ch.end - ch.start)) * 100 : 0;
                return (
                  <button key={i} onClick={() => seekTo(ch.start)}
                    className={`w-full text-left px-3 py-2.5 transition-all group ${
                      isActive ? 'bg-violet-500/8' : 'hover:bg-white/[0.03]'
                    }`} data-testid={`chapter-${i}`}>
                    <div className="flex items-center gap-2.5">
                      <div className={`w-6 h-6 rounded-md flex items-center justify-center text-[9px] font-bold shrink-0 ${
                        isActive ? 'bg-violet-500/20 text-violet-300' : chProgress === 100 ? 'bg-white/[0.06] text-slate-400' : 'bg-white/[0.03] text-slate-600'
                      }`}>
                        {String(i + 1).padStart(2, '0')}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className={`text-[10px] font-medium truncate ${isActive ? 'text-white' : 'text-slate-400 group-hover:text-slate-300'}`}>{ch.title}</p>
                        <p className="text-[8px] text-slate-600">{formatTime(ch.start)} - {formatTime(ch.end)}</p>
                      </div>
                    </div>
                    {isActive && (
                      <div className="mt-1.5 ml-8 h-[2px] bg-white/[0.06] rounded-full overflow-hidden">
                        <div className="h-full bg-violet-500/60 rounded-full transition-all duration-300" style={{ width: `${chProgress}%` }} />
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Main Area */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Viewport */}
          <div className="flex-1 relative flex items-center justify-center bg-[#08080d] overflow-hidden" data-testid="replay-viewport">
            {/* Vignette overlay */}
            <div className="absolute inset-0 pointer-events-none" style={{
              background: 'radial-gradient(ellipse at center, transparent 50%, rgba(0,0,0,0.5) 100%)',
            }} />

            {/* Cinema viewport */}
            <div className={`relative transition-all duration-700 ease-out ${
              currentCut.view_mode === 'panoramic' ? 'w-[88%] aspect-video' :
              currentCut.view_mode === 'speaker_closeup' ? 'w-[45%] aspect-[3/4] max-h-[85%]' :
              'w-[80%] aspect-video'
            }`}>
              <div className="absolute inset-0 rounded-xl border border-white/[0.06] bg-gradient-to-b from-slate-800/40 to-slate-900/60 overflow-hidden shadow-2xl shadow-black/50">
                {/* Panoramic View */}
                {currentCut.view_mode === 'panoramic' && (
                  <div className="grid grid-cols-3 grid-rows-2 gap-[3px] p-2 h-full">
                    {(replay.speakers || [{ name: 'Alex' }, { name: 'Sarah' }, { name: 'James' }, { name: 'Maria' }, { name: 'David' }, { name: 'Emma' }]).map((sp, i) => {
                      const isSpeaking = visibleTranscript.length > 0 && visibleTranscript[visibleTranscript.length - 1].speaker === sp.name;
                      return (
                        <div key={i} className={`rounded-lg border flex items-center justify-center transition-all duration-500 ${
                          isSpeaking ? 'border-emerald-400/30 bg-slate-700/50 scale-[1.02]' : 'border-white/[0.04] bg-slate-800/30'
                        }`}>
                          <div className="text-center">
                            <div className={`w-12 h-12 mx-auto rounded-full flex items-center justify-center text-lg font-bold transition-all ${
                              isSpeaking ? 'ring-2 ring-emerald-400/40 shadow-lg shadow-emerald-500/10' : ''
                            }`} style={{ backgroundColor: (SPEAKER_COLORS[sp.name] || '#666') + '30', color: SPEAKER_COLORS[sp.name] || '#aaa' }}>
                              {sp.name?.[0] || '?'}
                            </div>
                            <p className="text-[9px] text-slate-400 mt-1.5">{sp.name}</p>
                            {sp.role && <p className="text-[7px] text-slate-600">{sp.role}</p>}
                            {isSpeaking && <div className="flex items-center justify-center gap-0.5 mt-1">
                              {[1,2,3,2,1].map((h, j) => (
                                <div key={j} className="w-[2px] bg-emerald-400 rounded-full animate-pulse" style={{ height: h * 4, animationDelay: `${j * 100}ms` }} />
                              ))}
                            </div>}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* Speaker Close-Up */}
                {currentCut.view_mode === 'speaker_closeup' && (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                      <div className="relative">
                        <div className="w-28 h-28 mx-auto rounded-full flex items-center justify-center text-4xl font-bold" style={{
                          backgroundColor: (SPEAKER_COLORS[currentCut.focus_users?.[0]] || '#666') + '25',
                          color: SPEAKER_COLORS[currentCut.focus_users?.[0]] || '#aaa',
                          boxShadow: `0 0 40px ${(SPEAKER_COLORS[currentCut.focus_users?.[0]] || '#666')}20`,
                        }}>
                          {(currentCut.focus_users?.[0] || 'S')[0]}
                        </div>
                        <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 flex items-center gap-0.5">
                          {[2,3,4,3,2,3,4,3,2].map((h, j) => (
                            <div key={j} className="w-[2px] rounded-full animate-pulse" style={{
                              height: h * 3,
                              backgroundColor: SPEAKER_COLORS[currentCut.focus_users?.[0]] || '#666',
                              animationDelay: `${j * 80}ms`,
                            }} />
                          ))}
                        </div>
                      </div>
                      <p className="text-sm text-white mt-4 font-medium">{currentCut.focus_users?.[0] || 'Speaker'}</p>
                      <p className="text-[9px] mt-0.5" style={{ color: SPEAKER_COLORS[currentCut.focus_users?.[0]] || '#888' }}>Speaking</p>
                    </div>
                  </div>
                )}

                {/* Conversation View */}
                {currentCut.view_mode === 'conversation' && (
                  <div className="flex items-center justify-center h-full gap-12 px-12">
                    {(currentCut.focus_users || ['Speaker 1', 'Speaker 2']).map((name, i) => (
                      <div key={i} className="text-center flex-1">
                        <div className="w-20 h-20 mx-auto rounded-full flex items-center justify-center text-2xl font-bold" style={{
                          backgroundColor: (SPEAKER_COLORS[name] || '#666') + '25',
                          color: SPEAKER_COLORS[name] || '#aaa',
                        }}>
                          {(name || 'S')[0]}
                        </div>
                        <p className="text-xs text-white mt-2 font-medium">{name}</p>
                      </div>
                    ))}
                  </div>
                )}

                {/* View mode badge */}
                <div className="absolute top-3 left-3 flex items-center gap-2">
                  <Badge className={`text-[8px] ${viewInfo.color} border-0`}>
                    <ViewIcon className="w-2.5 h-2.5 mr-1" />{viewInfo.label}
                  </Badge>
                  {currentCut.transition === 'cut' && <Badge className="text-[7px] bg-white/5 text-slate-500 border-0">Cut</Badge>}
                  {currentCut.transition === 'dissolve' && <Badge className="text-[7px] bg-white/5 text-slate-500 border-0">Dissolve</Badge>}
                </div>

                {/* Time + Chapter overlay */}
                <div className="absolute top-3 right-3 text-right">
                  <p className="text-[10px] text-white/60 font-mono">{formatTime(currentTime)}</p>
                  {currentChapter && <p className="text-[8px] text-violet-400/60">{currentChapter.title}</p>}
                </div>
              </div>
            </div>

            {/* Subtitle overlay */}
            {visibleTranscript.length > 0 && (
              <div className="absolute bottom-16 left-1/2 -translate-x-1/2 max-w-[55%]" data-testid="replay-transcript">
                <p className="text-center text-sm py-1.5 px-4 rounded-lg bg-black/70 backdrop-blur-sm text-white">
                  <span className="font-medium" style={{ color: SPEAKER_COLORS[visibleTranscript[visibleTranscript.length - 1].speaker] || '#aaa' }}>
                    {visibleTranscript[visibleTranscript.length - 1].speaker}:
                  </span>{' '}
                  {visibleTranscript[visibleTranscript.length - 1].text}
                </p>
              </div>
            )}
          </div>

          {/* Timeline + Controls */}
          <div className="border-t border-white/[0.04] bg-[#0a0a12]/95 backdrop-blur-md px-4 py-2.5 shrink-0" data-testid="playback-controls">
            {/* Waveform Timeline */}
            <div className="relative h-10 mb-1 group" ref={timelineRef} data-testid="timeline">
              {/* Chapter background segments */}
              {chapters.map((ch, i) => (
                <div key={i} className="absolute top-0 bottom-0 border-r border-white/[0.03]" style={{
                  left: `${(ch.start / duration) * 100}%`,
                  width: `${((ch.end - ch.start) / duration) * 100}%`,
                }}>
                  <span className="absolute top-0 left-1 text-[6px] text-slate-600 font-mono">{String(i + 1).padStart(2, '0')}</span>
                </div>
              ))}

              {/* Waveform */}
              <div className="absolute inset-x-0 top-2 bottom-2 flex items-end gap-[1px] cursor-pointer" onClick={e => {
                const rect = e.currentTarget.getBoundingClientRect();
                seekTo((e.clientX - rect.left) / rect.width * duration);
              }}>
                {waveform.length > 0 && waveform.filter((_, i) => i % Math.max(1, Math.floor(waveform.length / 300)) === 0).map((v, i, arr) => {
                  const barProgress = (i / arr.length) * 100;
                  const isPast = barProgress <= progress;
                  return (
                    <div key={i} className="flex-1 rounded-full transition-colors" style={{
                      height: `${Math.max(8, Math.min(100, v * 100))}%`,
                      backgroundColor: isPast ? 'rgba(139, 92, 246, 0.6)' : 'rgba(255,255,255,0.06)',
                      minWidth: '1px',
                    }} />
                  );
                })}
              </div>

              {/* Key moment markers */}
              {moments.map((m, i) => (
                <button key={i} onClick={() => seekTo(m.ts)}
                  className="absolute top-0 bottom-0 w-[3px] group/m z-10 hover:w-1" style={{ left: `${(m.ts / duration) * 100}%` }}
                  data-testid={`moment-marker-${i}`}>
                  <div className="absolute top-0 w-[3px] h-full rounded-full" style={{ backgroundColor: MOMENT_COLORS[m.type] || '#64748b', opacity: 0.7 }} />
                  <div className="hidden group-hover/m:block absolute bottom-full mb-1 left-1/2 -translate-x-1/2 whitespace-nowrap bg-black/95 rounded-md px-2 py-1 text-[8px] text-white z-20 border border-white/10">
                    <span className="font-medium" style={{ color: MOMENT_COLORS[m.type] }}>{m.type?.replace('_', ' ')}</span>: {m.label}
                  </div>
                </button>
              ))}

              {/* Shared moment marker */}
              {shareMarker !== null && (
                <div className="absolute top-0 bottom-0 z-15 pointer-events-none" style={{ left: `${(shareMarker / duration) * 100}%` }} data-testid="share-marker">
                  <div className="absolute top-0 w-1 h-full bg-fuchsia-400/60 rounded-full" />
                  <div className="absolute -top-1 -left-[5px]">
                    <Share2 className="w-3 h-3 text-fuchsia-400" />
                  </div>
                </div>
              )}

              {/* Playhead */}
              <div className="absolute top-0 bottom-0 w-0.5 bg-white shadow-[0_0_6px_rgba(255,255,255,0.4)] rounded-full z-20 pointer-events-none transition-all" style={{ left: `${progress}%` }}>
                <div className="absolute -top-1 -left-[3px] w-2 h-2 rounded-full bg-white shadow-lg" />
              </div>
            </div>

            {/* Controls row */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3 w-44">
                <span className="text-[11px] text-slate-500 font-mono tabular-nums">{formatTime(currentTime)}</span>
                <span className="text-[9px] text-slate-700">/</span>
                <span className="text-[11px] text-slate-600 font-mono tabular-nums">{formatTime(duration)}</span>
              </div>

              <div className="flex items-center gap-1.5">
                <Button variant="ghost" size="sm" onClick={skipBack}
                  className="h-8 w-8 rounded-full text-slate-400 hover:text-white hover:bg-white/[0.06]" data-testid="skip-back-btn">
                  <SkipBack className="w-4 h-4" />
                </Button>
                <Button variant="ghost" size="sm" onClick={() => seekTo(Math.max(0, currentTime - 5))}
                  className="h-7 w-7 rounded-full text-slate-500 hover:text-white hover:bg-white/[0.06]" data-testid="rewind-5-btn">
                  <Rewind className="w-3 h-3" />
                </Button>
                <Button size="sm" onClick={() => setPlaying(!playing)}
                  className="h-11 w-11 rounded-full bg-white hover:bg-slate-200 text-black shadow-lg shadow-white/10" data-testid="play-pause-btn">
                  {playing ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 ml-0.5" />}
                </Button>
                <Button variant="ghost" size="sm" onClick={() => seekTo(currentTime + 5)}
                  className="h-7 w-7 rounded-full text-slate-500 hover:text-white hover:bg-white/[0.06]" data-testid="forward-5-btn">
                  <FastForward className="w-3 h-3" />
                </Button>
                <Button variant="ghost" size="sm" onClick={skipForward}
                  className="h-8 w-8 rounded-full text-slate-400 hover:text-white hover:bg-white/[0.06]" data-testid="skip-forward-btn">
                  <SkipForward className="w-4 h-4" />
                </Button>
              </div>

              <div className="flex items-center gap-2 w-44 justify-end">
                <button onClick={cycleSpeed}
                  className="text-[10px] font-mono text-slate-400 hover:text-white bg-white/[0.04] hover:bg-white/[0.08] px-2 py-1 rounded-md transition-colors" data-testid="speed-btn">
                  {speed}x
                </button>
                {currentChapter && (
                  <Badge className="text-[8px] bg-white/[0.04] text-slate-400 border-0 max-w-[120px] truncate">
                    Ch {currentChapter.index + 1}: {currentChapter.title}
                  </Badge>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Right Panel: Transcript + Highlights */}
        <div className="w-72 border-l border-white/[0.04] flex flex-col bg-[#0a0a12] shrink-0" data-testid="replay-sidebar">
          {/* Transcript */}
          <div className="flex-1 flex flex-col min-h-0">
            <div className="p-3 border-b border-white/[0.04] flex items-center justify-between">
              <h3 className="text-[10px] font-semibold text-slate-400 uppercase tracking-widest flex items-center gap-1.5">
                <Volume2 className="w-3 h-3 text-violet-400" />Transcript
              </h3>
              <span className="text-[8px] text-slate-600">{replay.transcript_segments?.length || 0} segments</span>
            </div>
            <div ref={transcriptRef} className="flex-1 overflow-y-auto p-2 space-y-1" data-testid="transcript-panel">
              {(replay.transcript_segments || []).map((seg, i) => {
                const isPast = seg.ts <= currentTime;
                const isCurrent = isPast && (i === replay.transcript_segments.length - 1 || replay.transcript_segments[i + 1].ts > currentTime);
                return (
                  <button key={i} onClick={() => seekTo(seg.ts)}
                    className={`w-full text-left p-2 rounded-lg transition-all ${
                      isCurrent ? 'bg-violet-500/10 border border-violet-500/15' :
                      isPast ? 'opacity-60 hover:opacity-80' : 'opacity-30 hover:opacity-50'
                    } ${!isCurrent ? 'border border-transparent' : ''}`}
                    data-testid={`transcript-seg-${i}`}>
                    <div className="flex items-center gap-1.5 mb-0.5">
                      <span className="text-[8px] font-mono text-slate-600">{formatTime(seg.ts)}</span>
                      <span className="text-[9px] font-medium" style={{ color: SPEAKER_COLORS[seg.speaker] || '#aaa' }}>{seg.speaker}</span>
                    </div>
                    <p className="text-[10px] text-slate-300 leading-relaxed">{seg.text}</p>
                  </button>
                );
              })}
            </div>
          </div>

          {/* AI Highlights */}
          <div className="border-t border-white/[0.04] p-3 shrink-0" data-testid="highlights-section">
            <h3 className="text-[10px] font-semibold text-slate-400 uppercase tracking-widest flex items-center gap-1.5 mb-2">
              <Sparkles className="w-3 h-3 text-fuchsia-400" />AI Highlights
            </h3>
            <div className="flex gap-1 mb-2">
              {['executive_summary', 'action_items', 'full_replay'].map(s => (
                <button key={s} onClick={() => setHlStyle(s)}
                  className={`flex-1 text-[8px] py-1 rounded-md transition-all ${
                    hlStyle === s ? 'bg-fuchsia-500/10 text-fuchsia-300' : 'text-slate-500 hover:text-slate-300 hover:bg-white/[0.04]'
                  }`} data-testid={`hl-style-${s}`}>
                  {s.replace(/_/g, ' ')}
                </button>
              ))}
            </div>
            <Button size="sm" onClick={generateHighlights} disabled={hlLoading}
              className="w-full h-7 text-[10px] bg-fuchsia-500/15 hover:bg-fuchsia-500/25 text-fuchsia-300 rounded-md border border-fuchsia-500/20" data-testid="generate-highlights-btn">
              {hlLoading ? <><Loader2 className="w-3 h-3 mr-1 animate-spin" />Generating...</> : <><Sparkles className="w-3 h-3 mr-1" />Generate</>}
            </Button>
            {highlights?.highlights && (
              <div className="mt-2 max-h-32 overflow-y-auto p-2 bg-white/[0.02] rounded-md border border-white/[0.04] text-[9px] text-slate-400 whitespace-pre-wrap leading-relaxed" data-testid="highlights-content">
                {highlights.highlights}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
