import { useState, useEffect, useRef } from 'react';
import { Brain, Users, FileText, Mic, Zap, DollarSign, Edit, Calendar, Search, BookOpen, Globe, MessageCircle, Shield, MonitorSmartphone, Scale, AlertTriangle, CheckCircle } from 'lucide-react';
import { API } from './constants';

const ICONS = {
  'user-search': Users, 'file-text': FileText, 'mic': Mic, 'zap': Zap,
  'dollar-sign': DollarSign, 'edit': Edit, 'calendar': Calendar,
  'search': Search, 'users': Users, 'brain': Brain, 'book-open': BookOpen,
  'globe': Globe, 'message-circle': MessageCircle, 'shield': Shield,
  'monitor': MonitorSmartphone, 'scale': Scale, 'alert-triangle': AlertTriangle,
  'check-circle': CheckCircle,
};

const CAT_COLORS = {
  'Job Toolkit': '#00B894',
  'AI Meeting': '#6C5CE7',
  'AI Messenger': '#00CEC9',
  'Security & QA': '#E17055',
};

const SlashCommandAutocomplete = ({ channelId, token, messageText, onSelect }) => {
  const [commands, setCommands] = useState([]);
  const [visible, setVisible] = useState(false);
  const [selectedIdx, setSelectedIdx] = useState(0);

  useEffect(() => {
    if (!channelId || !token) return;
    fetch(`${API}/api/lumi/bots/slash-commands/${channelId}`, {
      headers: { Authorization: `Bearer ${token}` }
    }).then(r => r.ok ? r.json() : null)
      .then(d => { if (d) setCommands(d.commands || []); })
      .catch(() => {});
  }, [channelId, token]);

  useEffect(() => {
    if (!messageText.startsWith('/') || commands.length === 0) {
      setVisible(false);
      return;
    }
    const query = messageText.split(' ')[0].toLowerCase();
    const matches = commands.filter(c => c.command.toLowerCase().startsWith(query));
    setVisible(matches.length > 0 && messageText.indexOf(' ') === -1);
    setSelectedIdx(0);
  }, [messageText, commands]);

  if (!visible) return null;

  const query = messageText.split(' ')[0].toLowerCase();
  const matches = commands.filter(c => c.command.toLowerCase().startsWith(query));

  return (
    <div className="absolute bottom-full left-0 right-0 mb-1 bg-white border border-slate-200 rounded-lg shadow-lg overflow-hidden z-20 max-h-48 overflow-y-auto" data-testid="slash-command-menu">
      <div className="px-3 py-1.5 bg-slate-50 border-b border-slate-100">
        <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Bot Commands</span>
      </div>
      {matches.map((cmd, i) => {
        const catColor = CAT_COLORS[cmd.category] || '#64748b';
        return (
          <button key={`${cmd.bot_id}-${cmd.command}`}
            onClick={() => { onSelect(cmd.command.split(' ')[0] + ' '); setVisible(false); }}
            className={`w-full flex items-center gap-2.5 px-3 py-2 text-left hover:bg-slate-50 transition-colors ${i === selectedIdx ? 'bg-slate-50' : ''}`}
            data-testid={`slash-cmd-${cmd.bot_id}`}>
            <div className="w-5 h-5 rounded flex items-center justify-center flex-shrink-0" style={{ background: `${catColor}20` }}>
              <div className="w-2 h-2 rounded-full" style={{ background: catColor }} />
            </div>
            <div className="flex-1 min-w-0">
              <code className="text-xs font-mono text-slate-800">{cmd.command}</code>
              <span className="text-[10px] text-slate-400 ml-2">{cmd.bot_name}</span>
            </div>
            <span className="text-[9px] px-1.5 py-0.5 rounded-full font-medium" style={{ background: `${catColor}15`, color: catColor }}>{cmd.category}</span>
          </button>
        );
      })}
    </div>
  );
};

export default SlashCommandAutocomplete;
