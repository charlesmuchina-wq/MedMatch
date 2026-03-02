import { memo } from 'react';
import { Settings, MicOff } from 'lucide-react';

const ControlsPanel = memo(function ControlsPanel({ muteAll, roomInfo }) {
  return (
    <div className="flex-1 overflow-y-auto space-y-3" data-testid="controls-panel">
      <div className="p-3 border-b border-white/[0.06]">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-violet-500/20 to-purple-500/10 flex items-center justify-center">
            <Settings className="w-3.5 h-3.5 text-violet-400" />
          </div>
          <div>
            <h3 className="text-xs font-semibold text-white">Room Controls</h3>
            <p className="text-[9px] text-slate-500">Settings & permissions</p>
          </div>
        </div>
      </div>
      <div className="px-3 space-y-2">
        <button onClick={muteAll} className="w-full flex items-center gap-2.5 p-2.5 rounded-xl bg-red-500/[0.04] border border-red-500/15 hover:bg-red-500/[0.08] transition-all" data-testid="mute-all-control">
          <MicOff className="w-4 h-4 text-red-400" /><span className="text-[11px] text-red-300 font-medium">Mute All</span>
        </button>
        <div className="p-2.5 rounded-xl border border-white/[0.06] bg-white/[0.02] space-y-1.5">
          <p className="text-[9px] text-slate-400 font-semibold uppercase tracking-widest">Room Settings</p>
          <div className="text-[10px] text-slate-400 space-y-1">
            {['chat_enabled', 'q_and_a_enabled', 'attendee_video', 'attendee_audio'].map(key => (
              <div key={key} className="flex items-center justify-between">
                <span>{key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()).replace('Q And A', 'Q&A')}</span>
                <span className={roomInfo.settings?.[key] ? 'text-emerald-400' : 'text-red-400'}>{roomInfo.settings?.[key] ? 'On' : 'Off'}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
});

export default ControlsPanel;
