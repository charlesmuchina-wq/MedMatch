import { useState, useEffect } from 'react';
import { Loader2, Clipboard, Bell, BarChart3, Video, Hand, Brain, Globe, Github, ChevronDown, ChevronUp, Bot } from 'lucide-react';
import { toast } from 'sonner';
import { API, ESY } from './constants';

const ICONS = {
  clipboard: Clipboard, bell: Bell, 'bar-chart': BarChart3,
  video: Video, 'hand-wave': Hand, brain: Brain,
  globe: Globe, github: Github,
};

const BotActionsBar = ({ channelId, token }) => {
  const [bots, setBots] = useState([]);
  const [expanded, setExpanded] = useState(false);
  const [executing, setExecuting] = useState(null);

  useEffect(() => {
    if (!channelId || !token) return;
    loadBots();
  }, [channelId, token]);

  const loadBots = async () => {
    try {
      const res = await fetch(`${API}/api/lumi/bots/channel/${channelId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const d = await res.json();
        setBots(d.bots || []);
      }
    } catch {}
  };

  const executeAction = async (botId, actionId) => {
    setExecuting(`${botId}-${actionId}`);
    try {
      const res = await fetch(`${API}/api/lumi/bots/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ bot_id: botId, channel_id: channelId, action: actionId })
      });
      if (res.ok) {
        const d = await res.json();
        toast.success(`${d.bot_name} executed!`);
      } else {
        const e = await res.json();
        toast.error(e.detail || 'Action failed');
      }
    } catch { toast.error('Connection error'); }
    setExecuting(null);
  };

  if (bots.length === 0) return null;

  return (
    <div className="border-b border-slate-100 bg-slate-50/80" data-testid="bot-actions-bar">
      <button onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-2 px-4 py-1.5 text-[11px] text-slate-500 hover:text-slate-700 transition-colors"
        data-testid="bot-actions-toggle">
        <Bot className="w-3 h-3" />
        <span className="font-medium">{bots.length} bot{bots.length !== 1 ? 's' : ''} active</span>
        {expanded ? <ChevronUp className="w-3 h-3 ml-auto" /> : <ChevronDown className="w-3 h-3 ml-auto" />}
      </button>
      {expanded && (
        <div className="px-4 pb-2 flex flex-wrap gap-1.5" data-testid="bot-actions-list">
          {bots.map(bot => {
            const BotIcon = ICONS[bot.icon] || Brain;
            return bot.actions.map(action => {
              const ActionIcon = ICONS[action.icon] || BotIcon;
              const isLoading = executing === `${bot.bot_id}-${action.id}`;
              return (
                <button key={`${bot.bot_id}-${action.id}`}
                  onClick={() => executeAction(bot.bot_id, action.id)}
                  disabled={isLoading}
                  className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-[11px] font-medium bg-white border border-slate-200 text-slate-700 hover:border-[#00CEC9] hover:text-[#00CEC9] transition-all shadow-sm hover:shadow"
                  data-testid={`bot-action-${bot.bot_id}-${action.id}`}>
                  {isLoading ? <Loader2 className="w-3 h-3 animate-spin" /> : <ActionIcon className="w-3 h-3" />}
                  {action.label}
                </button>
              );
            });
          })}
        </div>
      )}
    </div>
  );
};

export default BotActionsBar;
