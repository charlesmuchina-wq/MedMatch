import {
  Brain, Users, FileText, Mic, Zap, DollarSign, Edit, Calendar,
  Search, BookOpen, Globe, MessageCircle, Shield, MonitorSmartphone,
  Scale, AlertTriangle, CheckCircle, ArrowLeft, X, Download, Loader2, Check
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { RatingStars, getCat } from './constants';

const ICON_MAP = {
  'user-search': Users, 'file-text': FileText, 'mic': Mic, 'zap': Zap,
  'dollar-sign': DollarSign, 'edit': Edit, 'calendar': Calendar,
  'search': Search, 'users': Users, 'brain': Brain, 'book-open': BookOpen,
  'globe': Globe, 'message-circle': MessageCircle, 'shield': Shield,
  'monitor': MonitorSmartphone, 'scale': Scale, 'alert-triangle': AlertTriangle,
  'check-circle': CheckCircle,
};

export const BotDetailView = ({ bot, channels, selectedChannel, setSelectedChannel, onInstall, installing, onClose, onBack }) => {
  const Icon = ICON_MAP[bot.icon] || Brain;
  const cc = getCat(bot.category);
  const alreadyInstalled = selectedChannel && false; // Caller should check isInstalled

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-slate-900 rounded-2xl shadow-2xl w-full max-w-md mx-4 max-h-[85vh] flex flex-col overflow-hidden border border-slate-700/50" onClick={e => e.stopPropagation()} data-testid="bot-detail-modal">
        <div className="px-5 py-4 border-b border-slate-700/50 flex items-center gap-3">
          <button onClick={onBack} className="p-1.5 hover:bg-slate-800 rounded-lg" data-testid="back-from-detail">
            <ArrowLeft className="w-4 h-4 text-slate-400" />
          </button>
          <div className="flex-1"><h3 className="text-sm font-semibold text-white">Bot Details</h3></div>
          <button onClick={onClose} className="p-1.5 hover:bg-slate-800 rounded-lg"><X className="w-4 h-4 text-slate-400" /></button>
        </div>
        <ScrollArea className="flex-1 p-5">
          <div className="flex items-start gap-4 mb-5">
            <div className="w-14 h-14 rounded-2xl flex items-center justify-center flex-shrink-0" style={{ background: cc.bg }}>
              <Icon className="w-7 h-7 text-white" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">{bot.name}</h3>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-[10px] px-2 py-0.5 rounded-full font-medium text-white/80" style={{ background: `${cc.bg}30` }}>{bot.category}</span>
                {bot.subcategory && <span className="text-[10px] text-slate-500">{bot.subcategory}</span>}
              </div>
              <div className="flex items-center gap-3 mt-2">
                <RatingStars rating={bot.rating || 0} />
                <span className="text-[10px] text-slate-500">{(bot.install_count || 0).toLocaleString()} installs</span>
              </div>
            </div>
          </div>
          <p className="text-sm text-slate-300 leading-relaxed mb-5">{bot.description}</p>
          {bot.commands?.length > 0 && (
            <div className="mb-5">
              <p className="text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">Commands</p>
              <div className="flex flex-wrap gap-1.5">
                {bot.commands.map((cmd, i) => (
                  <code key={i} className="text-[11px] bg-slate-800 text-cyan-400 px-2 py-1 rounded-md font-mono" data-testid={`bot-cmd-${i}`}>{cmd}</code>
                ))}
              </div>
            </div>
          )}
          <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/40">
            <div className="flex gap-2 items-center mb-3">
              <span className="text-xs text-slate-400 font-medium">Install to:</span>
              <select value={selectedChannel} onChange={e => setSelectedChannel(e.target.value)}
                className="flex-1 h-8 border border-slate-700 rounded-lg text-xs px-2 bg-slate-800 text-white focus:ring-2 focus:ring-cyan-500/20"
                data-testid="detail-channel-select">
                <option value="">Select channel...</option>
                {(channels || []).map(ch => <option key={ch.id} value={ch.id}>#{ch.name}</option>)}
              </select>
            </div>
            <Button onClick={() => onInstall(bot.id)} disabled={installing === bot.id || !selectedChannel}
              className="w-full h-9 text-xs font-semibold text-white" style={{ background: cc.bg }}
              data-testid={`detail-install-${bot.id}`}>
              {installing === bot.id ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Download className="w-4 h-4 mr-2" />}
              Install Bot
            </Button>
          </div>
        </ScrollArea>
      </div>
    </div>
  );
};
