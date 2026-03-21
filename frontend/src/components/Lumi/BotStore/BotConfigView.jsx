import {
  Brain, Users, FileText, Mic, Zap, DollarSign, Edit, Calendar,
  Search, BookOpen, Globe, MessageCircle, Shield, MonitorSmartphone,
  Scale, AlertTriangle, CheckCircle, ArrowLeft, Power, Loader2, Save, Trash2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { getCat } from './constants';

const ICON_MAP = {
  'user-search': Users, 'file-text': FileText, 'mic': Mic, 'zap': Zap,
  'dollar-sign': DollarSign, 'edit': Edit, 'calendar': Calendar,
  'search': Search, 'users': Users, 'brain': Brain, 'book-open': BookOpen,
  'globe': Globe, 'message-circle': MessageCircle, 'shield': Shield,
  'monitor': MonitorSmartphone, 'scale': Scale, 'alert-triangle': AlertTriangle,
  'check-circle': CheckCircle,
};

const ConfigField = ({ fieldKey, value, onChange }) => {
  if (typeof value === 'boolean') {
    return (
      <div className="flex items-center justify-between py-2">
        <label className="text-xs text-slate-400 capitalize">{fieldKey.replace(/_/g, ' ')}</label>
        <button onClick={() => onChange(!value)}
          className={`w-9 h-5 rounded-full transition-colors ${value ? 'bg-cyan-500' : 'bg-slate-600'}`}
          data-testid={`config-toggle-${fieldKey}`}>
          <div className={`w-4 h-4 bg-white rounded-full shadow transition-transform ${value ? 'translate-x-4' : 'translate-x-0.5'}`} />
        </button>
      </div>
    );
  }
  if (typeof value === 'number') {
    return (
      <div className="py-2">
        <label className="text-xs text-slate-400 capitalize block mb-1">{fieldKey.replace(/_/g, ' ')}</label>
        <Input type="number" value={value} onChange={e => onChange(Number(e.target.value))}
          className="h-8 text-xs bg-slate-800 border-slate-700 text-white" data-testid={`config-num-${fieldKey}`} />
      </div>
    );
  }
  if (Array.isArray(value)) {
    return (
      <div className="py-2">
        <label className="text-xs text-slate-400 capitalize block mb-1">{fieldKey.replace(/_/g, ' ')}</label>
        <Input value={value.join(', ')} onChange={e => onChange(e.target.value.split(',').map(s => s.trim()))}
          className="h-8 text-xs bg-slate-800 border-slate-700 text-white" data-testid={`config-arr-${fieldKey}`} />
      </div>
    );
  }
  return (
    <div className="py-2">
      <label className="text-xs text-slate-400 capitalize block mb-1">{fieldKey.replace(/_/g, ' ')}</label>
      <Input value={value || ''} onChange={e => onChange(e.target.value)}
        className="h-8 text-xs bg-slate-800 border-slate-700 text-white" data-testid={`config-str-${fieldKey}`} />
    </div>
  );
};

export const BotConfigView = ({ configBot, editConfig, setEditConfig, catalog, channels, onToggle, onUninstall, onSave, savingConfig, onClose }) => {
  const Icon = ICON_MAP[configBot.bot_id] || Brain;
  const catInfo = catalog.find(b => b.id === configBot.bot_id);
  const cc = getCat(catInfo?.category);
  const getChannelName = (chId) => (channels || []).find(c => c.id === chId)?.name || chId?.slice(0, 10);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-slate-900 rounded-2xl shadow-2xl w-full max-w-md mx-4 max-h-[85vh] flex flex-col overflow-hidden border border-slate-700/50" onClick={e => e.stopPropagation()} data-testid="bot-config-modal">
        <div className="px-5 py-4 border-b border-slate-700/50 flex items-center gap-3">
          <button onClick={() => onClose('back')} className="p-1.5 hover:bg-slate-800 rounded-lg"><ArrowLeft className="w-4 h-4 text-slate-400" /></button>
          <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: cc.bg }}>
            <Icon className="w-4 h-4 text-white" />
          </div>
          <div className="flex-1">
            <h3 className="text-sm font-semibold text-white">{configBot.bot_name}</h3>
            <p className="text-[10px] text-slate-500">#{getChannelName(configBot.channel_id)}</p>
          </div>
          <button onClick={() => onToggle(configBot)}
            className={`p-1.5 rounded-lg ${configBot.is_active ? 'bg-green-500/10 text-green-400' : 'bg-slate-800 text-slate-500'}`}
            data-testid="toggle-bot-active"><Power className="w-4 h-4" /></button>
        </div>
        <ScrollArea className="flex-1 px-5 py-4">
          <p className="text-xs font-semibold text-slate-300 mb-3">Configuration</p>
          {Object.entries(editConfig).map(([key, val]) => (
            <ConfigField key={key} fieldKey={key} value={val}
              onChange={(v) => setEditConfig(prev => ({ ...prev, [key]: v }))} />
          ))}
          {Object.keys(editConfig).length === 0 && <p className="text-xs text-slate-500 py-4 text-center">No config options</p>}
        </ScrollArea>
        <div className="px-5 py-3 border-t border-slate-700/50 flex items-center gap-2">
          <Button size="sm" variant="outline" onClick={() => onUninstall(configBot.id)}
            className="text-red-400 border-red-500/30 hover:bg-red-500/10 text-xs h-8" data-testid="config-uninstall">
            <Trash2 className="w-3 h-3 mr-1" />Uninstall
          </Button>
          <div className="flex-1" />
          <Button size="sm" onClick={onSave} disabled={savingConfig}
            className="text-white text-xs h-8" style={{ background: cc.bg }} data-testid="config-save">
            {savingConfig ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : <Save className="w-3 h-3 mr-1" />}Save
          </Button>
        </div>
      </div>
    </div>
  );
};
