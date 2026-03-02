import { useState, useEffect, useRef, useCallback } from 'react';
import {
  Search, X, Mic, Video, AudioLines, Eye, Captions, Brain, Sparkles,
  BrainCircuit, Clapperboard, BarChart3, MessageCircleQuestion,
  SmilePlus, Trophy, PenLine, QrCode, Scan, Disc, Glasses, Wand2,
  Radio, Cpu, Fingerprint, Headphones, Users, Settings, Hand,
  BarChart as BarChartIcon, Users as UsersIcon, Zap, ArrowRight
} from 'lucide-react';

const ALL_FEATURES = [
  { id: 'mic', icon: Mic, label: 'Microphone', desc: 'Toggle your microphone on/off', category: 'Media', color: '#8b5cf6' },
  { id: 'cam', icon: Video, label: 'Camera', desc: 'Toggle your camera on/off', category: 'Media', color: '#8b5cf6' },
  { id: 'noise', icon: AudioLines, label: 'Noise Cancellation', desc: 'AI-powered background noise removal', category: 'Media', color: '#10b981' },
  { id: 'eye', icon: Eye, label: 'Eye Contact Correction', desc: 'AI adjusts gaze to simulate eye contact', category: 'Media', color: '#10b981' },
  { id: 'captions', icon: Captions, label: 'Live Captions', desc: 'Real-time speech-to-text transcription', category: 'Media', color: '#10b981' },
  { id: 'spatial', icon: Headphones, label: 'Spatial Audio', desc: 'Directional 3D audio positioning', category: 'Media', color: '#10b981' },
  { id: 'ai', icon: Brain, label: 'AI Assistant', desc: 'Ask questions, get research, voice commands', category: 'AI Suite', color: '#a78bfa', isNew: false },
  { id: 'coach', icon: Sparkles, label: 'AI Meeting Coach', desc: 'Private real-time presentation tips', category: 'AI Suite', color: '#10b981' },
  { id: 'copilot', icon: BrainCircuit, label: 'Multiplayer Copilot', desc: 'Cross-meeting context AI copilot', category: 'AI Suite', color: '#d946ef', isNew: false },
  { id: 'director', icon: Clapperboard, label: 'Cinematic Director', desc: 'AI-powered camera switching & framing', category: 'AI Suite', color: '#8b5cf6' },
  { id: 'sentiment', icon: BarChart3, label: 'Sentiment Dashboard', desc: 'Real-time engagement & attention heatmap', category: 'AI Suite', color: '#06b6d4' },
  { id: 'qa', icon: MessageCircleQuestion, label: 'Q&A Panel', desc: 'Ask and answer questions with upvotes', category: 'Collaboration', color: '#f59e0b' },
  { id: 'reactions', icon: SmilePlus, label: 'Emoji Reactions', desc: 'Send floating emoji reactions', category: 'Collaboration', color: '#f59e0b' },
  { id: 'polls', icon: BarChartIcon, label: 'Polls & Challenges', desc: 'Create polls, quizzes, word clouds, ratings', category: 'Collaboration', color: '#eab308', isNew: true },
  { id: 'breakout', icon: UsersIcon, label: 'Breakout Lounges', desc: '2D spatial breakout rooms with proximity audio', category: 'Collaboration', color: '#ec4899', isNew: true },
  { id: 'leaderboard', icon: Trophy, label: 'Leaderboard', desc: 'Participation rankings & gamification', category: 'Collaboration', color: '#8b5cf6' },
  { id: 'whiteboard', icon: PenLine, label: 'Whiteboard', desc: 'Collaborative drawing & annotation tool', category: 'Collaboration', color: '#10b981' },
  { id: 'qr', icon: QrCode, label: 'QR Code Entry', desc: 'Touchless meeting entry via QR code', category: 'Collaboration', color: '#14b8a6' },
  { id: 'slam', icon: Scan, label: 'SLAM Tracking', desc: '3D spatial room mapping & auto-framing', category: 'Hardware', color: '#f43f5e' },
  { id: 'panoramic', icon: Disc, label: '360° Multi-Focus', desc: 'Panoramic camera with headshot extraction', category: 'Hardware', color: '#f97316' },
  { id: 'webxr', icon: Glasses, label: 'WebXR / Vision Pro', desc: '3D meeting rooms & spatial personas', category: 'Hardware', color: '#6366f1' },
  { id: 'iot', icon: Wand2, label: 'Room Control', desc: 'Voice-activated IoT environment presets', category: 'Hardware', color: '#f59e0b' },
  { id: 'beamforming', icon: Radio, label: 'Beamforming Audio', desc: 'Adaptive microphone array with polar patterns', category: 'Hardware', color: '#0ea5e9' },
  { id: 'hardware', icon: Cpu, label: 'Hardware Discovery', desc: 'Auto-detect & manage connected devices', category: 'Hardware', color: '#84cc16' },
  { id: 'biometric', icon: Fingerprint, label: 'Biometric Verify', desc: 'Session watermarks & integrity scoring', category: 'Hardware', color: '#14b8a6' },
  { id: 'participants', icon: Users, label: 'Participants', desc: 'Manage roles, promote, hand raises', category: 'Host', color: '#10b981' },
  { id: 'controls', icon: Settings, label: 'Room Controls', desc: 'Mute all, room settings', category: 'Host', color: '#8b5cf6' },
];

const CATEGORIES = ['Media', 'AI Suite', 'Collaboration', 'Hardware', 'Host'];

export default function FeatureCommandBar({ isOpen, onClose, onSelectFeature }) {
  const [query, setQuery] = useState('');
  const [selectedIdx, setSelectedIdx] = useState(0);
  const inputRef = useRef(null);
  const listRef = useRef(null);

  const filtered = query.trim()
    ? ALL_FEATURES.filter(f =>
        f.label.toLowerCase().includes(query.toLowerCase()) ||
        f.desc.toLowerCase().includes(query.toLowerCase()) ||
        f.category.toLowerCase().includes(query.toLowerCase())
      )
    : ALL_FEATURES;

  useEffect(() => {
    if (isOpen) {
      setQuery('');
      setSelectedIdx(0);
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen]);

  useEffect(() => {
    setSelectedIdx(0);
  }, [query]);

  // Scroll selected item into view
  useEffect(() => {
    const el = listRef.current?.querySelector(`[data-idx="${selectedIdx}"]`);
    el?.scrollIntoView({ block: 'nearest' });
  }, [selectedIdx]);

  const handleKeyDown = useCallback((e) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIdx(prev => Math.min(prev + 1, filtered.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIdx(prev => Math.max(prev - 1, 0));
    } else if (e.key === 'Enter' && filtered[selectedIdx]) {
      e.preventDefault();
      onSelectFeature(filtered[selectedIdx].id);
      onClose();
    } else if (e.key === 'Escape') {
      onClose();
    }
  }, [filtered, selectedIdx, onSelectFeature, onClose]);

  // Global keyboard shortcut
  useEffect(() => {
    const handler = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        if (isOpen) onClose();
        else onSelectFeature('__open_command__');
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [isOpen, onClose, onSelectFeature]);

  if (!isOpen) return null;

  // Group by category when no search
  const grouped = !query.trim()
    ? CATEGORIES.map(cat => ({
        category: cat,
        items: filtered.filter(f => f.category === cat)
      })).filter(g => g.items.length > 0)
    : null;

  let flatIdx = 0;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]" data-testid="feature-command-bar">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm animate-fade-in" onClick={onClose} />

      {/* Command bar */}
      <div className="relative w-full max-w-lg bg-karau-card/95 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-2xl shadow-black/50 overflow-hidden animate-command-in">
        {/* Search input */}
        <div className="flex items-center gap-3 px-4 py-3 border-b border-white/[0.06]">
          <Search className="w-4 h-4 text-slate-500 shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search features, tools, AI capabilities..."
            className="flex-1 bg-transparent text-sm text-white placeholder:text-slate-500 outline-none"
            data-testid="command-search-input"
          />
          <button onClick={onClose} className="text-slate-500 hover:text-white transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Results */}
        <div ref={listRef} className="max-h-[50vh] overflow-y-auto py-2">
          {grouped ? (
            grouped.map(group => (
              <div key={group.category}>
                <p className="px-4 py-1.5 text-[9px] font-semibold uppercase tracking-widest text-slate-500">
                  {group.category}
                </p>
                {group.items.map(feature => {
                  const idx = flatIdx++;
                  return (
                    <CommandItem
                      key={feature.id}
                      feature={feature}
                      isSelected={idx === selectedIdx}
                      dataIdx={idx}
                      onClick={() => { onSelectFeature(feature.id); onClose(); }}
                    />
                  );
                })}
              </div>
            ))
          ) : (
            filtered.map((feature, idx) => (
              <CommandItem
                key={feature.id}
                feature={feature}
                isSelected={idx === selectedIdx}
                dataIdx={idx}
                onClick={() => { onSelectFeature(feature.id); onClose(); }}
              />
            ))
          )}
          {filtered.length === 0 && (
            <div className="px-4 py-8 text-center">
              <Zap className="w-6 h-6 text-slate-600 mx-auto mb-2" />
              <p className="text-sm text-slate-500">No features found for "{query}"</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-4 py-2 border-t border-white/[0.06] flex items-center gap-4 text-[9px] text-slate-600">
          <span className="flex items-center gap-1"><kbd className="px-1 py-0.5 rounded bg-white/[0.06] border border-white/[0.08] font-mono">↑↓</kbd> Navigate</span>
          <span className="flex items-center gap-1"><kbd className="px-1 py-0.5 rounded bg-white/[0.06] border border-white/[0.08] font-mono">↵</kbd> Activate</span>
          <span className="flex items-center gap-1"><kbd className="px-1 py-0.5 rounded bg-white/[0.06] border border-white/[0.08] font-mono">esc</kbd> Close</span>
        </div>
      </div>
    </div>
  );
}

function CommandItem({ feature, isSelected, dataIdx, onClick }) {
  const Icon = feature.icon;
  return (
    <button
      data-idx={dataIdx}
      onClick={onClick}
      data-testid={`cmd-${feature.id}`}
      className={`w-full flex items-center gap-3 px-4 py-2 text-left transition-all duration-100 ${
        isSelected
          ? 'bg-white/[0.06]'
          : 'hover:bg-white/[0.03]'
      }`}
    >
      <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0" style={{ backgroundColor: `${feature.color}15` }}>
        <Icon className="w-4 h-4" style={{ color: feature.color }} />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <p className="text-[12px] font-medium text-white truncate">{feature.label}</p>
          {feature.isNew && (
            <span className="px-1.5 py-0 rounded text-[7px] font-bold bg-gradient-to-r from-amber-500 to-orange-500 text-white shrink-0">NEW</span>
          )}
        </div>
        <p className="text-[10px] text-slate-500 truncate">{feature.desc}</p>
      </div>
      {isSelected && <ArrowRight className="w-3.5 h-3.5 text-slate-500 shrink-0" />}
    </button>
  );
}
