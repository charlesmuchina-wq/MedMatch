import {
  Brain, Users, FileText, Mic, Zap, DollarSign, Edit, Calendar,
  Search, BookOpen, Globe, MessageCircle, Shield, MonitorSmartphone,
  Scale, AlertTriangle, CheckCircle, Download, Loader2, Check
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { RatingStars, getCat } from './constants';

const ICON_MAP = {
  'user-search': Users, 'file-text': FileText, 'mic': Mic, 'zap': Zap,
  'dollar-sign': DollarSign, 'edit': Edit, 'calendar': Calendar,
  'search': Search, 'users': Users, 'brain': Brain, 'book-open': BookOpen,
  'globe': Globe, 'message-circle': MessageCircle, 'shield': Shield,
  'monitor': MonitorSmartphone, 'scale': Scale, 'alert-triangle': AlertTriangle,
  'check-circle': CheckCircle,
};

export const BotCard = ({ bot, compact, onView, onInstall, installing, selectedChannel, isInstalled }) => {
  const Icon = ICON_MAP[bot.icon] || Brain;
  const cc = getCat(bot.category);

  if (compact) {
    return (
      <div className="p-3 rounded-xl border border-slate-700/40 bg-slate-800/30 hover:border-slate-600/60 transition-all cursor-pointer group"
        onClick={onView} data-testid={`bot-card-${bot.id}`}>
        <div className="flex items-center gap-2.5 mb-2">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: cc.bg }}>
            <Icon className="w-4 h-4 text-white" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-semibold text-white truncate">{bot.name}</p>
            <p className="text-[9px] text-slate-500">{bot.category}</p>
          </div>
        </div>
        <div className="flex items-center justify-between">
          <RatingStars rating={bot.rating || 0} />
          <span className="text-[9px] text-slate-600">{(bot.install_count || 0).toLocaleString()}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="p-3 rounded-xl border border-slate-700/40 bg-slate-800/20 hover:border-slate-600/50 transition-all group"
      data-testid={`bot-card-${bot.id}`}>
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 cursor-pointer" style={{ background: cc.bg }}
          onClick={onView}>
          <Icon className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1 min-w-0 cursor-pointer" onClick={onView}>
          <div className="flex items-center gap-2">
            <p className="text-sm font-semibold text-white">{bot.name}</p>
            {bot.featured && <Zap className="w-3 h-3 text-amber-400" />}
          </div>
          <p className="text-[11px] text-slate-500 mt-0.5 line-clamp-1">{bot.description}</p>
          <div className="flex items-center gap-3 mt-1.5">
            <RatingStars rating={bot.rating || 0} />
            <span className="text-[10px] text-slate-600">{(bot.install_count || 0).toLocaleString()} installs</span>
          </div>
        </div>
        {isInstalled ? (
          <div className="flex items-center gap-1 text-green-400 text-[10px] font-medium mt-2 flex-shrink-0">
            <Check className="w-3.5 h-3.5" />
          </div>
        ) : (
          <Button size="sm" onClick={(e) => { e.stopPropagation(); onInstall(); }}
            disabled={installing === bot.id || !selectedChannel}
            className="h-7 text-[10px] text-white rounded-lg mt-1 opacity-60 group-hover:opacity-100 transition-opacity flex-shrink-0"
            style={{ background: cc.bg }}
            data-testid={`install-bot-${bot.id}`}>
            {installing === bot.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <><Download className="w-3 h-3 mr-1" />Install</>}
          </Button>
        )}
      </div>
    </div>
  );
};
