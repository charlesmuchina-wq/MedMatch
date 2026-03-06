import { useEffect, useState } from 'react';
import { X, Command, Keyboard } from 'lucide-react';
import { ESY } from './constants';

const SHORTCUTS = [
  { category: 'Navigation', items: [
    { keys: ['Ctrl', 'K'], desc: 'Open command bar', action: 'command_bar' },
    { keys: ['Ctrl', 'E'], desc: 'Toggle emoji picker', action: 'emoji_picker' },
    { keys: ['Ctrl', 'N'], desc: 'New channel', action: 'new_channel' },
    { keys: ['Ctrl', 'Shift', 'D'], desc: 'New direct message', action: 'new_dm' },
    { keys: ['Ctrl', '/'], desc: 'Show keyboard shortcuts', action: 'shortcuts' },
    { keys: ['Escape'], desc: 'Close current panel / modal', action: 'close' },
  ]},
  { category: 'Messaging', items: [
    { keys: ['Enter'], desc: 'Send message', action: null },
    { keys: ['Shift', 'Enter'], desc: 'New line in message', action: null },
    { keys: ['Ctrl', 'Shift', 'F'], desc: 'Search messages', action: 'search' },
  ]},
  { category: 'Panels', items: [
    { keys: ['Ctrl', 'Shift', 'A'], desc: 'Toggle AI insights', action: 'ai_panel' },
    { keys: ['Ctrl', 'Shift', 'N'], desc: 'Toggle notifications', action: 'notifications' },
    { keys: ['Ctrl', 'Shift', 'M'], desc: 'Toggle channel members', action: 'members' },
    { keys: ['Ctrl', 'Shift', 'P'], desc: 'Open profile', action: 'profile' },
  ]},
];

export const useKeyboardShortcuts = (actions) => {
  useEffect(() => {
    const handler = (e) => {
      if (!e.key) return; // Guard for mobile/touch events
      const ctrl = e.ctrlKey || e.metaKey;
      const shift = e.shiftKey;
      const key = e.key.toLowerCase();

      if (ctrl && key === 'k') { e.preventDefault(); actions.command_bar?.(); }
      else if (ctrl && key === 'e') { e.preventDefault(); actions.emoji_picker?.(); }
      else if (ctrl && key === 'n' && !shift) { e.preventDefault(); actions.new_channel?.(); }
      else if (ctrl && shift && key === 'd') { e.preventDefault(); actions.new_dm?.(); }
      else if (ctrl && key === '/') { e.preventDefault(); actions.shortcuts?.(); }
      else if (ctrl && shift && key === 'a') { e.preventDefault(); actions.ai_panel?.(); }
      else if (ctrl && shift && key === 'n') { e.preventDefault(); actions.notifications?.(); }
      else if (ctrl && shift && key === 'm') { e.preventDefault(); actions.members?.(); }
      else if (ctrl && shift && key === 'p') { e.preventDefault(); actions.profile?.(); }
      else if (ctrl && shift && key === 'f') { e.preventDefault(); actions.search?.(); }
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [actions]);
};

export const ShortcutsPanel = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center" onClick={onClose}>
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" />
      <div className="relative bg-white rounded-2xl w-full max-w-md shadow-2xl border border-slate-200 overflow-hidden" onClick={e => e.stopPropagation()} data-testid="shortcuts-panel">

        <div className="px-6 py-5 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` }}>
              <Keyboard className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-black text-gray-900">Keyboard Shortcuts</h2>
              <p className="text-xs text-gray-600 font-medium">Master LUMI with quick keys</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 hover:bg-slate-100 rounded-lg" data-testid="close-shortcuts">
            <X className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        <div className="p-5 space-y-5 max-h-[60vh] overflow-auto">
          {SHORTCUTS.map(group => (
            <div key={group.category}>
              <h3 className="text-xs font-black text-gray-900 uppercase tracking-wider mb-2.5 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: ESY.turquoise }} />
                {group.category}
              </h3>
              <div className="space-y-1">
                {group.items.map((item, i) => (
                  <div key={i} className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-slate-50 transition-colors">
                    <span className="text-sm text-gray-700 font-medium">{item.desc}</span>
                    <div className="flex items-center gap-1">
                      {item.keys.map((k, ki) => (
                        <span key={ki}>
                          {ki > 0 && <span className="text-[10px] text-gray-400 mx-0.5">+</span>}
                          <kbd className="inline-flex items-center px-2 py-1 text-[11px] font-mono font-bold text-gray-700 bg-slate-100 rounded-md border border-slate-200 shadow-sm min-w-[28px] justify-center">
                            {k}
                          </kbd>
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="px-5 py-3 border-t border-slate-100 bg-slate-50 text-center">
          <span className="text-[11px] text-gray-500 font-medium">Press <kbd className="px-1.5 py-0.5 bg-white rounded border border-slate-200 font-mono text-[10px] font-bold">Ctrl</kbd> + <kbd className="px-1.5 py-0.5 bg-white rounded border border-slate-200 font-mono text-[10px] font-bold">/</kbd> to toggle this panel</span>
        </div>
      </div>
    </div>
  );
};
