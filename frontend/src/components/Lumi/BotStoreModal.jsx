import { useState, useEffect } from 'react';
import { X, Loader2, Download, Trash2, Check, Search, Clipboard, Bell, BarChart3, Video, Hand, Brain, Globe, Github, Settings, Power, ChevronRight, ArrowLeft, Save } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { toast } from 'sonner';
import { API, ESY } from './constants';

const BOT_ICONS = {
  clipboard: Clipboard, bell: Bell, 'bar-chart': BarChart3,
  video: Video, 'hand-wave': Hand, brain: Brain,
  globe: Globe, github: Github,
};

const CATEGORY_COLORS = {
  Productivity: { bg: '#00CEC9', light: '#00CEC910' },
  Engagement: { bg: '#E84393', light: '#E8439310' },
  Collaboration: { bg: '#6C5CE7', light: '#6C5CE710' },
  Onboarding: { bg: '#00B894', light: '#00B89410' },
  AI: { bg: '#0984E3', light: '#0984E310' },
  Communication: { bg: '#FDCB6E', light: '#FDCB6E10' },
  DevOps: { bg: '#2D3436', light: '#2D343610' },
};

// Config field renderers
const ConfigField = ({ fieldKey, value, onChange }) => {
  if (typeof value === 'boolean') {
    return (
      <div className="flex items-center justify-between py-2">
        <label className="text-xs text-slate-600 capitalize">{fieldKey.replace(/_/g, ' ')}</label>
        <button
          onClick={() => onChange(!value)}
          className={`w-9 h-5 rounded-full transition-colors ${value ? 'bg-cyan-500' : 'bg-slate-300'}`}
          data-testid={`config-toggle-${fieldKey}`}
        >
          <div className={`w-4 h-4 bg-white rounded-full shadow transition-transform ${value ? 'translate-x-4' : 'translate-x-0.5'}`} />
        </button>
      </div>
    );
  }
  if (typeof value === 'number') {
    return (
      <div className="py-2">
        <label className="text-xs text-slate-600 capitalize block mb-1">{fieldKey.replace(/_/g, ' ')}</label>
        <Input type="number" value={value} onChange={e => onChange(Number(e.target.value))} className="h-8 text-xs" data-testid={`config-num-${fieldKey}`} />
      </div>
    );
  }
  if (Array.isArray(value)) {
    return (
      <div className="py-2">
        <label className="text-xs text-slate-600 capitalize block mb-1">{fieldKey.replace(/_/g, ' ')}</label>
        <Input value={value.join(', ')} onChange={e => onChange(e.target.value.split(',').map(s => s.trim()))} className="h-8 text-xs" data-testid={`config-arr-${fieldKey}`} />
      </div>
    );
  }
  return (
    <div className="py-2">
      <label className="text-xs text-slate-600 capitalize block mb-1">{fieldKey.replace(/_/g, ' ')}</label>
      <Input value={value || ''} onChange={e => onChange(e.target.value)} className="h-8 text-xs" data-testid={`config-str-${fieldKey}`} />
    </div>
  );
};

const BotStoreModal = ({ token, channels, onClose }) => {
  const [catalog, setCatalog] = useState([]);
  const [categories, setCategories] = useState([]);
  const [installed, setInstalled] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');
  const [activeCategory, setActiveCategory] = useState('all');
  const [tab, setTab] = useState('browse');
  const [installing, setInstalling] = useState(null);
  const [selectedChannel, setSelectedChannel] = useState('');
  const [configBot, setConfigBot] = useState(null); // bot being configured
  const [editConfig, setEditConfig] = useState({});
  const [savingConfig, setSavingConfig] = useState(false);

  useEffect(() => { loadCatalog(); loadInstalled(); }, []);

  const loadCatalog = async () => {
    try {
      const res = await fetch(`${API}/api/lumi/bots/catalog`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) { const d = await res.json(); setCatalog(d.bots || []); setCategories(d.categories || []); }
    } catch {}
    setLoading(false);
  };

  const loadInstalled = async () => {
    try {
      const res = await fetch(`${API}/api/lumi/bots/installed`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) { const d = await res.json(); setInstalled(d.bots || []); }
    } catch {}
  };

  const installBot = async (botId) => {
    if (!selectedChannel) { toast.error('Select a channel first'); return; }
    setInstalling(botId);
    try {
      const res = await fetch(`${API}/api/lumi/bots/install`, {
        method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ bot_id: botId, channel_id: selectedChannel })
      });
      if (res.ok) {
        const d = await res.json();
        toast.success(`${d.bot_name} installed!`);
        loadInstalled();
      } else { const e = await res.json(); toast.error(e.detail || 'Install failed'); }
    } catch { toast.error('Connection error'); }
    setInstalling(null);
  };

  const uninstallBot = async (installId) => {
    try {
      const res = await fetch(`${API}/api/lumi/bots/uninstall/${installId}`, {
        method: 'DELETE', headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) { toast.success('Bot uninstalled'); setConfigBot(null); loadInstalled(); }
      else toast.error('Uninstall failed');
    } catch { toast.error('Connection error'); }
  };

  const toggleBotActive = async (inst) => {
    try {
      const res = await fetch(`${API}/api/lumi/bots/toggle/${inst.id}`, {
        method: 'PUT', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ is_active: !inst.is_active })
      });
      if (res.ok) { toast.success(inst.is_active ? 'Bot paused' : 'Bot activated'); loadInstalled(); }
      else { toast.error('Toggle failed'); }
    } catch { toast.error('Connection error'); }
  };

  const saveConfig = async () => {
    if (!configBot) return;
    setSavingConfig(true);
    try {
      const res = await fetch(`${API}/api/lumi/bots/configure/${configBot.id}`, {
        method: 'PUT', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ config: editConfig })
      });
      if (res.ok) { toast.success('Configuration saved'); loadInstalled(); setConfigBot(null); }
      else toast.error('Save failed');
    } catch { toast.error('Connection error'); }
    setSavingConfig(false);
  };

  const openConfig = (inst) => {
    setConfigBot(inst);
    setEditConfig(inst.config || {});
  };

  const filtered = catalog.filter(b => {
    if (activeCategory !== 'all' && b.category !== activeCategory) return false;
    if (filter && !b.name.toLowerCase().includes(filter.toLowerCase()) && !b.description.toLowerCase().includes(filter.toLowerCase())) return false;
    return true;
  });

  const isInstalled = (botId, channelId) => installed.some(i => i.bot_id === botId && i.channel_id === channelId);
  const getChannelName = (chId) => (channels || []).find(c => c.id === chId)?.name || chId?.slice(0, 10);

  // Bot Config View
  if (configBot) {
    const Icon = BOT_ICONS[configBot.bot_id] || Brain;
    const catInfo = catalog.find(b => b.id === configBot.bot_id);
    const cc = CATEGORY_COLORS[catInfo?.category] || { bg: '#64748b', light: '#64748b10' };

    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 max-h-[85vh] flex flex-col overflow-hidden" onClick={e => e.stopPropagation()} data-testid="bot-config-modal">
          {/* Header */}
          <div className="px-5 py-4 border-b border-slate-100 flex items-center gap-3 flex-shrink-0">
            <button onClick={() => setConfigBot(null)} className="p-1.5 hover:bg-slate-100 rounded-lg" data-testid="back-to-installed">
              <ArrowLeft className="w-4 h-4 text-slate-500" />
            </button>
            <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: cc.bg }}>
              <Icon className="w-4 h-4 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-slate-900">{configBot.bot_name}</h3>
              <p className="text-[10px] text-slate-500">#{getChannelName(configBot.channel_id)}</p>
            </div>
            <div className="flex items-center gap-1">
              <button onClick={() => toggleBotActive(configBot)}
                className={`p-1.5 rounded-lg transition-colors ${configBot.is_active ? 'bg-green-50 text-green-600 hover:bg-green-100' : 'bg-slate-50 text-slate-400 hover:bg-slate-100'}`}
                data-testid="toggle-bot-active" title={configBot.is_active ? 'Pause bot' : 'Activate bot'}>
                <Power className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Config Fields */}
          <ScrollArea className="flex-1 px-5 py-4">
            <div className="space-y-1">
              <p className="text-xs font-semibold text-slate-700 mb-3">Configuration</p>
              {Object.entries(editConfig).map(([key, val]) => (
                <ConfigField
                  key={key}
                  fieldKey={key}
                  value={val}
                  onChange={(newVal) => setEditConfig(prev => ({ ...prev, [key]: newVal }))}
                />
              ))}
              {Object.keys(editConfig).length === 0 && (
                <p className="text-xs text-slate-400 py-4 text-center">No configuration options for this bot</p>
              )}
            </div>
          </ScrollArea>

          {/* Actions */}
          <div className="px-5 py-3 border-t border-slate-100 flex items-center gap-2 flex-shrink-0">
            <Button size="sm" variant="outline" onClick={() => uninstallBot(configBot.id)}
              className="text-red-500 hover:text-red-600 hover:bg-red-50 text-xs h-8" data-testid="config-uninstall">
              <Trash2 className="w-3 h-3 mr-1" />Uninstall
            </Button>
            <div className="flex-1" />
            <Button size="sm" onClick={saveConfig} disabled={savingConfig}
              className="bg-[#00CEC9] hover:bg-[#00CEC9]/90 text-white text-xs h-8" data-testid="config-save">
              {savingConfig ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : <Save className="w-3 h-3 mr-1" />}
              Save Config
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 max-h-[85vh] flex flex-col overflow-hidden" onClick={e => e.stopPropagation()} data-testid="bot-store-modal">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, #6C5CE7)` }}>
              <Brain className="w-4 h-4 text-white" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-900">ENZI Bot Store</h3>
              <p className="text-[11px] text-slate-500">{catalog.length} bots available</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 hover:bg-slate-100 rounded-lg transition-colors" data-testid="close-bot-store">
            <X className="w-4 h-4 text-slate-500" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-slate-100 px-4">
          {[{ id: 'browse', label: 'Browse' }, { id: 'installed', label: `Installed (${installed.length})` }].map(t => (
            <button key={t.id} onClick={() => setTab(t.id)}
              className={`px-4 py-2.5 text-xs font-medium transition-colors ${tab === t.id ? 'text-[#00CEC9] border-b-2 border-[#00CEC9]' : 'text-slate-500 hover:text-slate-700'}`}
              data-testid={`bot-tab-${t.id}`}>{t.label}</button>
          ))}
        </div>

        {tab === 'browse' ? (
          <>
            {/* Search + Channel Selector */}
            <div className="p-4 space-y-3 border-b border-slate-50 flex-shrink-0">
              <div className="relative">
                <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <Input value={filter} onChange={e => setFilter(e.target.value)} placeholder="Search bots..."
                  className="h-9 text-xs pl-9" data-testid="bot-search-input" />
              </div>
              <div className="flex gap-2 items-center">
                <span className="text-[11px] text-slate-500 font-medium whitespace-nowrap">Install to:</span>
                <select value={selectedChannel} onChange={e => setSelectedChannel(e.target.value)}
                  className="flex-1 h-8 border border-slate-200 rounded-lg text-xs px-2 bg-white focus:ring-2 focus:ring-[#00CEC9]/20"
                  data-testid="bot-channel-select">
                  <option value="">Select channel...</option>
                  {(channels || []).map(ch => <option key={ch.id} value={ch.id}>#{ch.name}</option>)}
                </select>
              </div>
              <div className="flex gap-1.5 flex-wrap">
                <button onClick={() => setActiveCategory('all')}
                  className={`px-2.5 py-1 rounded-full text-[10px] font-medium transition-all ${activeCategory === 'all' ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
                  data-testid="bot-cat-all">All</button>
                {categories.map(c => {
                  const cc = CATEGORY_COLORS[c] || { bg: '#64748b' };
                  return (
                    <button key={c} onClick={() => setActiveCategory(c)}
                      className={`px-2.5 py-1 rounded-full text-[10px] font-medium transition-all ${activeCategory === c ? 'text-white' : 'text-slate-600 hover:bg-slate-100'}`}
                      style={activeCategory === c ? { background: cc.bg } : {}}
                      data-testid={`bot-cat-${c.toLowerCase()}`}>{c}</button>
                  );
                })}
              </div>
            </div>

            {/* Bot List */}
            <ScrollArea className="flex-1">
              <div className="p-4 space-y-2">
                {loading ? <div className="flex justify-center py-12"><Loader2 className="w-5 h-5 animate-spin text-slate-400" /></div> :
                  filtered.length === 0 ? <p className="text-center text-sm text-slate-400 py-8">No bots found</p> :
                  filtered.map(bot => {
                    const Icon = BOT_ICONS[bot.icon] || Brain;
                    const cc = CATEGORY_COLORS[bot.category] || { bg: '#64748b', light: '#64748b10' };
                    const alreadyInstalled = selectedChannel && isInstalled(bot.id, selectedChannel);
                    return (
                      <div key={bot.id} className="p-3 rounded-xl border border-slate-100 hover:border-slate-200 transition-all group" data-testid={`bot-card-${bot.id}`}>
                        <div className="flex items-start gap-3">
                          <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: cc.bg }}>
                            <Icon className="w-5 h-5 text-white" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <p className="text-sm font-semibold text-slate-800">{bot.name}</p>
                              <span className="text-[9px] px-1.5 py-0.5 rounded-full font-medium" style={{ background: cc.light, color: cc.bg }}>{bot.category}</span>
                            </div>
                            <p className="text-[11px] text-slate-500 mt-0.5 leading-relaxed">{bot.description}</p>
                          </div>
                          {alreadyInstalled ? (
                            <div className="flex items-center gap-1 text-emerald-600 text-[10px] font-medium mt-1" data-testid={`bot-installed-${bot.id}`}>
                              <Check className="w-3.5 h-3.5" />Installed
                            </div>
                          ) : (
                            <Button size="sm" onClick={() => installBot(bot.id)}
                              disabled={installing === bot.id || !selectedChannel}
                              className="h-7 text-[10px] text-white rounded-lg mt-1 opacity-70 group-hover:opacity-100 transition-opacity"
                              style={{ background: cc.bg }}
                              data-testid={`install-bot-${bot.id}`}>
                              {installing === bot.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <><Download className="w-3 h-3 mr-1" />Install</>}
                            </Button>
                          )}
                        </div>
                      </div>
                    );
                  })}
              </div>
            </ScrollArea>
          </>
        ) : (
          /* Installed Tab */
          <ScrollArea className="flex-1">
            <div className="p-4 space-y-2">
              {installed.length === 0 ? (
                <div className="text-center py-12">
                  <Brain className="w-8 h-8 text-slate-300 mx-auto mb-3" />
                  <p className="text-sm text-slate-500 font-medium">No bots installed</p>
                  <p className="text-xs text-slate-400 mt-1">Browse and install bots from the catalog</p>
                </div>
              ) : installed.map(inst => {
                const catInfo = catalog.find(b => b.id === inst.bot_id);
                const Icon = BOT_ICONS[catInfo?.icon] || BOT_ICONS[inst.bot_id] || Brain;
                const cc = CATEGORY_COLORS[catInfo?.category] || { bg: '#64748b', light: '#64748b10' };
                return (
                  <div key={inst.id}
                    className="p-3 rounded-xl border border-slate-100 hover:border-slate-200 transition-all group cursor-pointer"
                    onClick={() => openConfig(inst)}
                    data-testid={`installed-bot-${inst.id}`}>
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: cc.bg }}>
                        <Icon className="w-4 h-4 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <p className="text-sm font-medium text-slate-800">{inst.bot_name}</p>
                          <span className={`w-1.5 h-1.5 rounded-full ${inst.is_active !== false ? 'bg-green-500' : 'bg-slate-300'}`} />
                        </div>
                        <p className="text-[10px] text-slate-500">#{getChannelName(inst.channel_id)} {inst.is_active !== false ? '' : '(Paused)'}</p>
                      </div>
                      <div className="flex items-center gap-1">
                        <ChevronRight className="w-4 h-4 text-slate-300 group-hover:text-slate-500 transition-colors" />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </ScrollArea>
        )}
      </div>
    </div>
  );
};

export default BotStoreModal;
