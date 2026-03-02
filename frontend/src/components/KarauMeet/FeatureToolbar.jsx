import { useState, useRef, useEffect } from 'react';
import {
  Mic, MicOff, Video, VideoOff, AudioLines, Eye, Captions,
  Brain, Sparkles, BrainCircuit, Clapperboard, BarChart3,
  MessageCircleQuestion, SmilePlus, Trophy, PenLine, QrCode,
  Scan, Disc, Glasses, Wand2, Radio, Cpu, Fingerprint,
  Headphones, Users, Settings, Play, Square, Shield, Save,
  ChevronUp, ChevronDown, Search, Command, Hand,
  BarChart as BarChartIcon, Users as UsersIcon
} from 'lucide-react';
import { Button } from '@/components/ui/button';

const TOOL_GROUPS = [
  {
    id: 'media',
    label: 'Media',
    accent: '#8b5cf6',
    tools: [
      { id: 'mic', icon: Mic, offIcon: MicOff, label: 'Microphone', type: 'toggle' },
      { id: 'cam', icon: Video, offIcon: VideoOff, label: 'Camera', type: 'toggle' },
      { id: 'noise', icon: AudioLines, label: 'Noise Cancel', color: 'emerald', type: 'toggle' },
      { id: 'eye', icon: Eye, label: 'Eye Contact', color: 'emerald', type: 'toggle' },
      { id: 'captions', icon: Captions, label: 'Live Captions', color: 'emerald', type: 'toggle' },
      { id: 'spatial', icon: Headphones, label: 'Spatial Audio', color: 'emerald', type: 'toggle' },
    ]
  },
  {
    id: 'ai',
    label: 'AI Suite',
    accent: '#a78bfa',
    tools: [
      { id: 'ai', icon: Brain, label: 'AI Assistant', color: 'violet', type: 'panel' },
      { id: 'coach', icon: Sparkles, label: 'AI Coach', color: 'emerald', type: 'toggle', hostOnly: true },
      { id: 'copilot', icon: BrainCircuit, label: 'Copilot', color: 'fuchsia', type: 'panel' },
      { id: 'director', icon: Clapperboard, label: 'Director', color: 'violet', type: 'panel' },
      { id: 'sentiment', icon: BarChart3, label: 'Sentiment', color: 'cyan', type: 'panel' },
    ]
  },
  {
    id: 'collab',
    label: 'Collaborate',
    accent: '#f59e0b',
    tools: [
      { id: 'qa', icon: MessageCircleQuestion, label: 'Q&A', type: 'panel' },
      { id: 'reactions', icon: SmilePlus, label: 'Reactions', color: 'amber', type: 'toggle' },
      { id: 'polls', icon: BarChartIcon, label: 'Polls', color: 'yellow', type: 'panel', badge: 'new' },
      { id: 'breakout', icon: UsersIcon, label: 'Lounges', color: 'pink', type: 'panel', badge: 'new' },
      { id: 'leaderboard', icon: Trophy, label: 'Leaderboard', type: 'panel' },
      { id: 'whiteboard', icon: PenLine, label: 'Whiteboard', color: 'emerald', type: 'toggle', hostOnly: true },
      { id: 'qr', icon: QrCode, label: 'QR Entry', color: 'teal', type: 'panel', hostOnly: true },
    ]
  },
  {
    id: 'hardware',
    label: 'Spatial & Hardware',
    accent: '#06b6d4',
    tools: [
      { id: 'slam', icon: Scan, label: 'SLAM Tracking', color: 'rose', type: 'panel' },
      { id: 'panoramic', icon: Disc, label: '360° Camera', color: 'orange', type: 'panel' },
      { id: 'webxr', icon: Glasses, label: 'WebXR', color: 'indigo', type: 'panel' },
      { id: 'iot', icon: Wand2, label: 'Room Control', color: 'amber', type: 'panel' },
      { id: 'beamforming', icon: Radio, label: 'Beamforming', color: 'sky', type: 'panel' },
      { id: 'hardware', icon: Cpu, label: 'Hardware', color: 'lime', type: 'panel' },
      { id: 'biometric', icon: Fingerprint, label: 'Biometric', color: 'teal', type: 'panel' },
    ]
  }
];

const COLOR_MAP = {
  emerald: { active: 'bg-emerald-500/20 text-emerald-400 shadow-emerald-500/20', dot: 'bg-emerald-400' },
  violet: { active: 'bg-violet-500/20 text-violet-400 shadow-violet-500/20', dot: 'bg-violet-400' },
  cyan: { active: 'bg-cyan-500/20 text-cyan-400 shadow-cyan-500/20', dot: 'bg-cyan-400' },
  fuchsia: { active: 'bg-fuchsia-500/20 text-fuchsia-400 shadow-fuchsia-500/20', dot: 'bg-fuchsia-400' },
  amber: { active: 'bg-amber-500/20 text-amber-400 shadow-amber-500/20', dot: 'bg-amber-400' },
  rose: { active: 'bg-rose-500/20 text-rose-400 shadow-rose-500/20', dot: 'bg-rose-400' },
  orange: { active: 'bg-orange-500/20 text-orange-400 shadow-orange-500/20', dot: 'bg-orange-400' },
  indigo: { active: 'bg-indigo-500/20 text-indigo-400 shadow-indigo-500/20', dot: 'bg-indigo-400' },
  sky: { active: 'bg-sky-500/20 text-sky-400 shadow-sky-500/20', dot: 'bg-sky-400' },
  lime: { active: 'bg-lime-500/20 text-lime-400 shadow-lime-500/20', dot: 'bg-lime-400' },
  pink: { active: 'bg-pink-500/20 text-pink-400 shadow-pink-500/20', dot: 'bg-pink-400' },
  yellow: { active: 'bg-yellow-500/20 text-yellow-400 shadow-yellow-500/20', dot: 'bg-yellow-400' },
  teal: { active: 'bg-teal-500/20 text-teal-400 shadow-teal-500/20', dot: 'bg-teal-400' },
  purple: { active: 'bg-purple-500/20 text-purple-400 shadow-purple-500/20', dot: 'bg-purple-400' },
};

function ToolButton({ tool, isActive, onClick, badgeCount }) {
  const [showTooltip, setShowTooltip] = useState(false);
  const Icon = isActive && tool.offIcon ? tool.icon : (isActive ? tool.icon : (tool.offIcon || tool.icon));
  const colorStyle = tool.color && COLOR_MAP[tool.color];
  const isOn = isActive;

  return (
    <div className="relative group"
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}>
      <button
        onClick={onClick}
        data-testid={`tb-${tool.id}`}
        className={`relative flex items-center justify-center w-9 h-9 rounded-xl transition-all duration-200 ${
          isOn
            ? `${colorStyle?.active || 'bg-purple-500/20 text-purple-400 shadow-purple-500/20'} shadow-lg`
            : 'bg-white/[0.06] text-slate-400 hover:bg-white/[0.1] hover:text-white'
        }`}
      >
        <Icon className="w-4 h-4" />
        {isOn && (
          <span className={`absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full ${colorStyle?.dot || 'bg-purple-400'} animate-pulse`} />
        )}
        {badgeCount && (
          <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-red-500 text-[7px] text-white flex items-center justify-center font-bold">
            {badgeCount}
          </span>
        )}
        {tool.badge === 'new' && !isOn && (
          <span className="absolute -top-1 -right-1 px-1 py-0 rounded text-[6px] font-bold bg-gradient-to-r from-amber-500 to-orange-500 text-white">
            NEW
          </span>
        )}
      </button>
      {/* Tooltip */}
      {showTooltip && (
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2.5 py-1 bg-slate-900 border border-white/10 rounded-lg whitespace-nowrap z-50 pointer-events-none animate-tooltip-in">
          <p className="text-[10px] text-white font-medium">{tool.label}</p>
          {tool.badge === 'new' && <p className="text-[8px] text-amber-400">New Feature</p>}
        </div>
      )}
    </div>
  );
}

export default function FeatureToolbar({
  // Media toggles
  isMicOn, onToggleMic, isCamOn, onToggleCam,
  noiseEnabled, onToggleNoise, noiseSupported,
  eyeContactOn, onToggleEye,
  captionsActive, onToggleCaptions,
  spatialEnabled, onToggleSpatial,
  // Panel toggle
  activePanel, onTogglePanel,
  // Other toggles
  showReactions, onToggleReactions,
  showCoach, onToggleCoach, coachTipsCount,
  showWhiteboard, onToggleWhiteboard,
  // Hand raise
  isHandRaised, onToggleHand, isAttendee,
  // Badges
  pendingQCount,
  // Permissions
  canStream, canControl,
  // Command bar
  onOpenCommandBar,
  // Host controls
  isHost, roomStatus, practiceMode,
  onStartPractice, onEndPractice, onStartWebinar, onEndWebinar,
  onSaveTranscript, hasTranscript,
  // Language picker
  onToggleLang, showLangPicker, sourceLanguage, displayLanguage,
}) {
  const [expanded, setExpanded] = useState(false);
  const [showMore, setShowMore] = useState(false);

  const getToolState = (toolId) => {
    switch (toolId) {
      case 'mic': return isMicOn;
      case 'cam': return isCamOn;
      case 'noise': return noiseEnabled;
      case 'eye': return eyeContactOn;
      case 'captions': return captionsActive;
      case 'spatial': return spatialEnabled;
      case 'reactions': return showReactions;
      case 'coach': return showCoach;
      case 'whiteboard': return showWhiteboard;
      default: return activePanel === toolId;
    }
  };

  const handleToolClick = (toolId) => {
    switch (toolId) {
      case 'mic': onToggleMic?.(); break;
      case 'cam': onToggleCam?.(); break;
      case 'noise': onToggleNoise?.(); break;
      case 'eye': onToggleEye?.(); break;
      case 'captions': onToggleCaptions?.(); break;
      case 'spatial': onToggleSpatial?.(); break;
      case 'reactions': onToggleReactions?.(); break;
      case 'coach': onToggleCoach?.(); break;
      case 'whiteboard': onToggleWhiteboard?.(); break;
      default: onTogglePanel?.(toolId); break;
    }
  };

  const getBadgeCount = (toolId) => {
    if (toolId === 'qa') return pendingQCount || null;
    if (toolId === 'coach') return coachTipsCount || null;
    return null;
  };

  const isToolVisible = (tool) => {
    if (tool.id === 'noise' && !noiseSupported) return false;
    if (tool.id === 'mic' || tool.id === 'cam' || tool.id === 'eye' || tool.id === 'noise') return canStream;
    if (tool.id === 'coach') return canStream;
    if (tool.id === 'whiteboard' || tool.id === 'qr') return canControl;
    return true;
  };

  // Primary groups (always visible): media + ai
  // Secondary groups (in "more"): collab + hardware
  const primaryGroups = TOOL_GROUPS.filter(g => g.id === 'media' || g.id === 'ai');
  const secondaryGroups = TOOL_GROUPS.filter(g => g.id === 'collab' || g.id === 'hardware');

  return (
    <div className="relative" data-testid="feature-toolbar">
      {/* Expanded tray for secondary features */}
      {showMore && (
        <div className="absolute bottom-full left-0 right-0 bg-karau-card/95 backdrop-blur-xl border-t border-white/[0.06] rounded-t-2xl animate-slide-up z-20" data-testid="toolbar-expanded">
          <div className="px-4 py-3 flex gap-6 overflow-x-auto">
            {secondaryGroups.map(group => (
              <div key={group.id} className="flex-shrink-0">
                <p className="text-[9px] font-semibold uppercase tracking-widest mb-2" style={{ color: group.accent }}>
                  {group.label}
                </p>
                <div className="flex items-center gap-1.5">
                  {group.tools.filter(isToolVisible).map(tool => (
                    <ToolButton
                      key={tool.id}
                      tool={tool}
                      isActive={getToolState(tool.id)}
                      onClick={() => handleToolClick(tool.id)}
                      badgeCount={getBadgeCount(tool.id)}
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main toolbar */}
      <div className="h-16 bg-karau-card/80 backdrop-blur-xl border-t border-white/[0.06] flex items-center justify-center px-4 gap-2" data-testid="toolbar-main">
        {/* Hand raise for attendee */}
        {isAttendee && (
          <ToolButton
            tool={{ id: 'hand', icon: Hand, label: 'Raise Hand', color: 'amber' }}
            isActive={isHandRaised}
            onClick={onToggleHand}
          />
        )}

        {/* Primary tool groups */}
        {primaryGroups.map((group, gi) => (
          <div key={group.id} className="flex items-center gap-1">
            {gi > 0 && <div className="w-px h-7 bg-white/[0.06] mx-1.5" />}
            <div className="flex items-center gap-1">
              <span className="text-[8px] font-semibold uppercase tracking-widest mr-1 hidden lg:block" style={{ color: group.accent, opacity: 0.6 }}>
                {group.label}
              </span>
              {group.tools.filter(isToolVisible).map(tool => (
                <ToolButton
                  key={tool.id}
                  tool={tool}
                  isActive={getToolState(tool.id)}
                  onClick={() => handleToolClick(tool.id)}
                  badgeCount={getBadgeCount(tool.id)}
                />
              ))}
            </div>
          </div>
        ))}

        {/* Divider */}
        <div className="w-px h-7 bg-white/[0.06] mx-1" />

        {/* Quick collaboration tools (most used) */}
        <ToolButton tool={{ id: 'qa', icon: MessageCircleQuestion, label: 'Q&A' }} isActive={activePanel === 'qa'} onClick={() => onTogglePanel?.('qa')} badgeCount={pendingQCount || null} />
        <ToolButton tool={{ id: 'polls', icon: BarChartIcon, label: 'Polls', color: 'yellow', badge: 'new' }} isActive={activePanel === 'polls'} onClick={() => onTogglePanel?.('polls')} />
        <ToolButton tool={{ id: 'reactions', icon: SmilePlus, label: 'Reactions', color: 'amber' }} isActive={showReactions} onClick={onToggleReactions} />

        {/* More tools button */}
        <button
          onClick={() => setShowMore(!showMore)}
          data-testid="tb-more"
          className={`flex items-center gap-1 px-3 h-9 rounded-xl transition-all duration-200 text-[10px] font-medium ${
            showMore
              ? 'bg-purple-500/20 text-purple-400'
              : 'bg-white/[0.06] text-slate-400 hover:bg-white/[0.1] hover:text-white'
          }`}
        >
          {showMore ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
          <span className="hidden sm:inline">More Tools</span>
        </button>

        {/* Language picker */}
        <button onClick={onToggleLang} data-testid="tb-lang"
          className={`flex items-center gap-1 px-2.5 h-9 rounded-xl text-[10px] font-mono transition-all duration-200 ${
            showLangPicker ? 'bg-violet-500/20 text-violet-400' : 'bg-white/[0.06] text-slate-400 hover:bg-white/[0.1] hover:text-white'
          }`}>
          <Captions className="w-3 h-3" />
          {sourceLanguage?.toUpperCase()}
          {sourceLanguage !== displayLanguage && <span className="text-emerald-400">{displayLanguage?.toUpperCase()}</span>}
        </button>

        {/* Command bar shortcut */}
        <button
          onClick={onOpenCommandBar}
          data-testid="tb-command"
          className="flex items-center gap-1.5 px-2.5 h-9 rounded-xl bg-white/[0.04] border border-white/[0.06] text-slate-500 hover:text-white hover:bg-white/[0.08] hover:border-white/[0.12] transition-all duration-200"
        >
          <Search className="w-3 h-3" />
          <span className="text-[10px] hidden sm:inline">Features</span>
          <kbd className="text-[8px] px-1 py-0.5 rounded bg-white/[0.06] border border-white/[0.08] font-mono hidden sm:inline">⌘K</kbd>
        </button>

        {/* Divider */}
        <div className="w-px h-7 bg-white/[0.06] mx-1" />

        {/* Host controls */}
        {canControl && (
          <>
            <ToolButton tool={{ id: 'participants', icon: Users, label: 'Participants' }} isActive={activePanel === 'participants'} onClick={() => onTogglePanel?.('participants')} />
            <ToolButton tool={{ id: 'controls', icon: Settings, label: 'Settings' }} isActive={activePanel === 'controls'} onClick={() => onTogglePanel?.('controls')} />
          </>
        )}

        {/* Session controls */}
        {isHost && roomStatus === 'scheduled' && !practiceMode && (
          <>
            <Button size="sm" onClick={onStartPractice} className="h-8 px-3 text-[11px] bg-amber-500/20 text-amber-400 hover:bg-amber-500/30 rounded-xl border border-amber-500/20" data-testid="start-practice-btn">
              <Shield className="w-3 h-3 mr-1" />Practice
            </Button>
            <Button size="sm" onClick={onStartWebinar} className="h-8 px-3 text-[11px] bg-emerald-500/80 hover:bg-emerald-400 rounded-xl shadow-lg shadow-emerald-500/20" data-testid="go-live-btn">
              <Play className="w-3 h-3 mr-1" />Go Live
            </Button>
          </>
        )}
        {isHost && practiceMode && (
          <>
            <Button size="sm" onClick={onEndPractice} className="h-8 px-3 text-[11px] bg-slate-500/20 text-slate-400 hover:bg-slate-500/30 rounded-xl border border-white/10" data-testid="end-practice-btn">End Practice</Button>
            <Button size="sm" onClick={onStartWebinar} className="h-8 px-3 text-[11px] bg-emerald-500/80 hover:bg-emerald-400 rounded-xl shadow-lg shadow-emerald-500/20" data-testid="go-live-from-practice-btn">
              <Play className="w-3 h-3 mr-1" />Go Live
            </Button>
          </>
        )}
        {isHost && roomStatus === 'live' && (
          <>
            {hasTranscript && (
              <Button size="sm" onClick={onSaveTranscript} className="h-8 px-3 text-[11px] bg-violet-500/20 text-violet-400 hover:bg-violet-500/30 rounded-xl border border-violet-500/20" data-testid="save-transcript-btn">
                <Save className="w-3 h-3 mr-1" />Save
              </Button>
            )}
            <Button size="sm" variant="destructive" onClick={onEndWebinar} className="h-8 px-3 text-[11px] rounded-xl" data-testid="end-webinar-btn">
              <Square className="w-3 h-3 mr-1" />End
            </Button>
          </>
        )}
      </div>
    </div>
  );
}
