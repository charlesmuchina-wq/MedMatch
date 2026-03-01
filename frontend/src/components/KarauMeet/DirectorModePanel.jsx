import { Camera, Monitor, Users, UserRound, MessageSquare, Clapperboard } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

const VIEW_OPTIONS = [
  { id: 'auto', label: 'Auto Director', icon: Clapperboard, desc: 'AI switches views automatically', color: 'violet' },
  { id: 'panoramic', label: 'Gallery', icon: Users, desc: 'Equal grid of all participants', color: 'blue' },
  { id: 'speaker_closeup', label: 'Speaker Focus', icon: UserRound, desc: 'Zoom on active speaker', color: 'emerald' },
  { id: 'conversation', label: 'Dialogue', icon: MessageSquare, desc: 'Side-by-side for 2-person talk', color: 'amber' },
  { id: 'manual', label: 'Manual', icon: Monitor, desc: 'You control the camera view', color: 'slate' },
];

export default function DirectorModePanel({ directorMode, onClose }) {
  if (!directorMode) return null;

  return (
    <div className="flex-1 flex flex-col overflow-hidden" data-testid="director-mode-panel">
      <div className="p-2.5 border-b border-white/5">
        <h3 className="text-xs font-semibold text-white flex items-center gap-1.5">
          <Clapperboard className="w-3.5 h-3.5 text-violet-400" />
          Cinematic Director
        </h3>
        <p className="text-[8px] text-slate-500 mt-0.5">AI-powered camera switching</p>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-1.5">
        {/* Current Status */}
        <div className="p-2 bg-violet-500/5 border border-violet-500/10 rounded-lg" data-testid="director-status">
          <div className="flex items-center justify-between mb-1">
            <span className="text-[9px] text-violet-400 font-semibold uppercase tracking-wider">Active View</span>
            <Badge className="bg-violet-500/20 text-violet-300 border-violet-500/30 text-[8px]">
              {directorMode.activeView}
            </Badge>
          </div>
          {directorMode.mode === 'auto' && directorMode.recommendedView && (
            <p className="text-[8px] text-slate-400">
              AI recommends: <span className="text-violet-300">{directorMode.recommendedView}</span>
            </p>
          )}
          {directorMode.focusUsers.length > 0 && (
            <p className="text-[8px] text-slate-400 mt-0.5">
              Focus: {directorMode.focusUsers.length} participant{directorMode.focusUsers.length > 1 ? 's' : ''}
            </p>
          )}
        </div>

        {/* View Mode Selector */}
        <div className="space-y-1" data-testid="director-view-options">
          {VIEW_OPTIONS.map(opt => {
            const isActive = directorMode.mode === opt.id;
            const Icon = opt.icon;
            const colorClasses = {
              violet: isActive ? 'bg-violet-500/15 border-violet-500/30 text-violet-300' : '',
              blue: isActive ? 'bg-blue-500/15 border-blue-500/30 text-blue-300' : '',
              emerald: isActive ? 'bg-emerald-500/15 border-emerald-500/30 text-emerald-300' : '',
              amber: isActive ? 'bg-amber-500/15 border-amber-500/30 text-amber-300' : '',
              slate: isActive ? 'bg-slate-500/15 border-slate-500/30 text-slate-300' : '',
            };

            return (
              <button
                key={opt.id}
                onClick={() => directorMode.setDirectorMode(opt.id)}
                className={`w-full flex items-center gap-2 p-2 rounded-lg border transition-all text-left ${
                  isActive
                    ? colorClasses[opt.color]
                    : 'bg-karau-bg/30 border-white/5 hover:bg-white/5 text-slate-400'
                }`}
                data-testid={`director-mode-${opt.id}`}
              >
                <Icon className="w-3.5 h-3.5 shrink-0" />
                <div>
                  <p className="text-[10px] font-medium">{opt.label}</p>
                  <p className="text-[8px] opacity-60">{opt.desc}</p>
                </div>
                {isActive && (
                  <span className={`ml-auto w-1.5 h-1.5 rounded-full ${
                    opt.color === 'violet' ? 'bg-violet-400' :
                    opt.color === 'blue' ? 'bg-blue-400' :
                    opt.color === 'emerald' ? 'bg-emerald-400' :
                    opt.color === 'amber' ? 'bg-amber-400' : 'bg-slate-400'
                  } animate-pulse`} />
                )}
              </button>
            );
          })}
        </div>

        {/* Director Tips */}
        <div className="p-2 bg-karau-bg/40 rounded-lg border border-white/5 mt-2">
          <p className="text-[8px] text-slate-500 uppercase tracking-wider mb-1">Director Tips</p>
          <ul className="text-[8px] text-slate-400 space-y-0.5 list-disc list-inside">
            <li>Auto mode uses AI to detect conversation patterns</li>
            <li>Speaker Focus activates after 3s of continuous speech</li>
            <li>Dialogue mode frames two speakers in active conversation</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
