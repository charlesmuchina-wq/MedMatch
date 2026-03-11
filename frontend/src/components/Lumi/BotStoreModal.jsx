import { useState, useEffect } from 'react';
import {
  X, Loader2, Download, Trash2, Check, Search, Brain, Globe, Star,
  Settings, Power, ChevronRight, ArrowLeft, Save, Zap, Shield, Users,
  FileText, Mic, DollarSign, Edit, Calendar, MonitorSmartphone,
  Scale, AlertTriangle, CheckCircle, BookOpen, MessageCircle, TrendingUp,
  Sparkles, Award, BarChart3
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { toast } from 'sonner';
import { API, ESY } from './constants';

const ICON_MAP = {
  'user-search': Users, 'file-text': FileText, 'mic': Mic, 'zap': Zap,
  'dollar-sign': DollarSign, 'edit': Edit, 'calendar': Calendar,
  'search': Search, 'users': Users, 'brain': Brain, 'book-open': BookOpen,
  'globe': Globe, 'message-circle': MessageCircle, 'shield': Shield,
  'monitor': MonitorSmartphone, 'scale': Scale, 'alert-triangle': AlertTriangle,
  'check-circle': CheckCircle,
};

const CAT_STYLES = {
  'Job Toolkit':    { bg: '#00B894', accent: '#00B894', emoji: 'briefcase' },
  'AI Meeting':     { bg: '#6C5CE7', accent: '#6C5CE7', emoji: 'video' },
  'AI Messenger':   { bg: '#00CEC9', accent: '#00CEC9', emoji: 'message' },
  'Security & QA':  { bg: '#E17055', accent: '#E17055', emoji: 'shield' },
};

const RatingStars = ({ rating, size = 'sm' }) => {
  const s = size === 'sm' ? 'w-3 h-3' : 'w-4 h-4';
  return (
    <div className="flex items-center gap-0.5">
      {[1,2,3,4,5].map(i => (
        <Star key={i} className={`${s} ${i <= Math.round(rating) ? 'text-amber-400 fill-amber-400' : 'text-slate-600'}`} />
      ))}
      <span className={`ml-1 font-medium ${size === 'sm' ? 'text-[10px]' : 'text-xs'} text-slate-400`}>{rating}</span>
    </div>
  );
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
  const [configBot, setConfigBot] = useState(null);
  const [editConfig, setEditConfig] = useState({});
  const [savingConfig, setSavingConfig] = useState(false);
  const [detailBot, setDetailBot] = useState(null);

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
      if (res.ok) { toast.success('Bot installed!'); loadInstalled(); }
      else { const e = await res.json(); toast.error(e.detail || 'Install failed'); }
    } catch { toast.error('Connection error'); }
    setInstalling(null);
  };

  const uninstallBot = async (installId) => {
    try {
      const res = await fetch(`${API}/api/lumi/bots/uninstall/${installId}`, {
        method: 'DELETE', headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) { toast.success('Bot uninstalled'); setConfigBot(null); loadInstalled(); }
    } catch { toast.error('Connection error'); }
  };

  const toggleBotActive = async (inst) => {
    try {
      const res = await fetch(`${API}/api/lumi/bots/toggle/${inst.id}`, {
        method: 'PUT', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ is_active: !inst.is_active })
      });
      if (res.ok) { toast.success(inst.is_active ? 'Bot paused' : 'Bot activated'); loadInstalled(); }
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
      if (res.ok) { toast.success('Config saved'); loadInstalled(); setConfigBot(null); }
    } catch { toast.error('Connection error'); }
    setSavingConfig(false);
  };

  const getIcon = (iconName) => ICON_MAP[iconName] || Brain;
  const getCat = (cat) => CAT_STYLES[cat] || { bg: '#64748b', accent: '#64748b' };
  const isInstalled = (botId, chId) => installed.some(i => i.bot_id === botId && i.channel_id === chId);
  const getChannelName = (chId) => (channels || []).find(c => c.id === chId)?.name || chId?.slice(0, 10);

  const filtered = catalog.filter(b => {
    if (activeCategory !== 'all' && b.category !== activeCategory) return false;
    if (filter && !b.name.toLowerCase().includes(filter.toLowerCase()) && !b.description.toLowerCase().includes(filter.toLowerCase())) return false;
    return true;
  });

  const featured = catalog.filter(b => b.featured);
  const grouped = categories.reduce((acc, cat) => {
    acc[cat] = filtered.filter(b => b.category === cat);
    return acc;
  }, {});

  // ═══ Config View ═══
  if (configBot) {
    const Icon = getIcon(configBot.bot_id);
    const catInfo = catalog.find(b => b.id === configBot.bot_id);
    const cc = getCat(catInfo?.category);
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
        <div className="bg-slate-900 rounded-2xl shadow-2xl w-full max-w-md mx-4 max-h-[85vh] flex flex-col overflow-hidden border border-slate-700/50" onClick={e => e.stopPropagation()} data-testid="bot-config-modal">
          <div className="px-5 py-4 border-b border-slate-700/50 flex items-center gap-3">
            <button onClick={() => setConfigBot(null)} className="p-1.5 hover:bg-slate-800 rounded-lg"><ArrowLeft className="w-4 h-4 text-slate-400" /></button>
            <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: cc.bg }}>
              <Icon className="w-4 h-4 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-white">{configBot.bot_name}</h3>
              <p className="text-[10px] text-slate-500">#{getChannelName(configBot.channel_id)}</p>
            </div>
            <button onClick={() => toggleBotActive(configBot)}
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
            <Button size="sm" variant="outline" onClick={() => uninstallBot(configBot.id)}
              className="text-red-400 border-red-500/30 hover:bg-red-500/10 text-xs h-8" data-testid="config-uninstall">
              <Trash2 className="w-3 h-3 mr-1" />Uninstall
            </Button>
            <div className="flex-1" />
            <Button size="sm" onClick={saveConfig} disabled={savingConfig}
              className="text-white text-xs h-8" style={{ background: cc.bg }} data-testid="config-save">
              {savingConfig ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : <Save className="w-3 h-3 mr-1" />}Save
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // ═══ Detail View ═══
  if (detailBot) {
    const Icon = getIcon(detailBot.icon);
    const cc = getCat(detailBot.category);
    const alreadyInstalled = selectedChannel && isInstalled(detailBot.id, selectedChannel);
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
        <div className="bg-slate-900 rounded-2xl shadow-2xl w-full max-w-md mx-4 max-h-[85vh] flex flex-col overflow-hidden border border-slate-700/50" onClick={e => e.stopPropagation()} data-testid="bot-detail-modal">
          <div className="px-5 py-4 border-b border-slate-700/50 flex items-center gap-3">
            <button onClick={() => setDetailBot(null)} className="p-1.5 hover:bg-slate-800 rounded-lg" data-testid="back-from-detail">
              <ArrowLeft className="w-4 h-4 text-slate-400" />
            </button>
            <div className="flex-1"><h3 className="text-sm font-semibold text-white">Bot Details</h3></div>
            <button onClick={onClose} className="p-1.5 hover:bg-slate-800 rounded-lg"><X className="w-4 h-4 text-slate-400" /></button>
          </div>
          <ScrollArea className="flex-1 p-5">
            {/* Hero */}
            <div className="flex items-start gap-4 mb-5">
              <div className="w-14 h-14 rounded-2xl flex items-center justify-center flex-shrink-0" style={{ background: cc.bg }}>
                <Icon className="w-7 h-7 text-white" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">{detailBot.name}</h3>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-[10px] px-2 py-0.5 rounded-full font-medium text-white/80" style={{ background: `${cc.bg}30` }}>{detailBot.category}</span>
                  {detailBot.subcategory && <span className="text-[10px] text-slate-500">{detailBot.subcategory}</span>}
                </div>
                <div className="flex items-center gap-3 mt-2">
                  <RatingStars rating={detailBot.rating || 0} />
                  <span className="text-[10px] text-slate-500">{(detailBot.install_count || 0).toLocaleString()} installs</span>
                </div>
              </div>
            </div>
            {/* Description */}
            <p className="text-sm text-slate-300 leading-relaxed mb-5">{detailBot.description}</p>
            {/* Commands */}
            {detailBot.commands?.length > 0 && (
              <div className="mb-5">
                <p className="text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">Commands</p>
                <div className="flex flex-wrap gap-1.5">
                  {detailBot.commands.map((cmd, i) => (
                    <code key={i} className="text-[11px] bg-slate-800 text-cyan-400 px-2 py-1 rounded-md font-mono" data-testid={`bot-cmd-${i}`}>{cmd}</code>
                  ))}
                </div>
              </div>
            )}
            {/* Install section */}
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
              {alreadyInstalled ? (
                <div className="flex items-center justify-center gap-2 py-2 text-green-400 text-xs font-medium">
                  <Check className="w-4 h-4" />Installed in this channel
                </div>
              ) : (
                <Button onClick={() => installBot(detailBot.id)} disabled={installing === detailBot.id || !selectedChannel}
                  className="w-full h-9 text-xs font-semibold text-white" style={{ background: cc.bg }}
                  data-testid={`detail-install-${detailBot.id}`}>
                  {installing === detailBot.id ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Download className="w-4 h-4 mr-2" />}
                  Install Bot
                </Button>
              )}
            </div>
          </ScrollArea>
        </div>
      </div>
    );
  }

  // ═══ Main Marketplace View ═══
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-slate-900 rounded-2xl shadow-2xl w-full max-w-2xl mx-4 max-h-[88vh] flex flex-col overflow-hidden border border-slate-700/50" onClick={e => e.stopPropagation()} data-testid="bot-store-modal">
        {/* Header */}
        <div className="px-5 py-4 border-b border-slate-700/50 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, #6C5CE7)` }}>
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white font-outfit" data-testid="bot-store-title">Bot Marketplace</h3>
              <p className="text-[11px] text-slate-500">{catalog.length} bots across {categories.length} categories</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-slate-800 rounded-xl transition-colors" data-testid="close-bot-store">
            <X className="w-4 h-4 text-slate-400" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-slate-700/50 px-4">
          {[
            { id: 'browse', label: 'Marketplace', icon: Sparkles },
            { id: 'installed', label: `Installed (${installed.length})`, icon: Check },
          ].map(t => (
            <button key={t.id} onClick={() => setTab(t.id)}
              className={`flex items-center gap-1.5 px-4 py-2.5 text-xs font-medium transition-colors ${tab === t.id ? 'text-cyan-400 border-b-2 border-cyan-400' : 'text-slate-500 hover:text-slate-300'}`}
              data-testid={`bot-tab-${t.id}`}>
              <t.icon className="w-3.5 h-3.5" />{t.label}
            </button>
          ))}
        </div>

        {tab === 'browse' ? (
          <>
            {/* Search + Channel + Categories */}
            <div className="p-4 space-y-3 border-b border-slate-700/30 flex-shrink-0">
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                  <Input value={filter} onChange={e => setFilter(e.target.value)} placeholder="Search 18 bots..."
                    className="h-9 text-xs pl-9 bg-slate-800 border-slate-700 text-white placeholder:text-slate-600" data-testid="bot-search-input" />
                </div>
                <select value={selectedChannel} onChange={e => setSelectedChannel(e.target.value)}
                  className="h-9 border border-slate-700 rounded-lg text-xs px-2 bg-slate-800 text-white min-w-[140px]"
                  data-testid="bot-channel-select">
                  <option value="">Install to...</option>
                  {(channels || []).map(ch => <option key={ch.id} value={ch.id}>#{ch.name}</option>)}
                </select>
              </div>
              <div className="flex gap-1.5 flex-wrap">
                <button onClick={() => setActiveCategory('all')}
                  className={`px-3 py-1.5 rounded-full text-[11px] font-medium transition-all ${activeCategory === 'all' ? 'bg-white text-slate-900' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}
                  data-testid="bot-cat-all">All ({catalog.length})</button>
                {categories.map(c => {
                  const cc = getCat(c);
                  const count = catalog.filter(b => b.category === c).length;
                  return (
                    <button key={c} onClick={() => setActiveCategory(c)}
                      className={`px-3 py-1.5 rounded-full text-[11px] font-medium transition-all ${activeCategory === c ? 'text-white' : 'text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700'}`}
                      style={activeCategory === c ? { background: cc.bg } : {}}
                      data-testid={`bot-cat-${c.replace(/\s+/g, '-').toLowerCase()}`}>
                      {c} ({count})
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Bot Grid */}
            <ScrollArea className="flex-1">
              <div className="p-4">
                {loading ? (
                  <div className="flex justify-center py-16"><Loader2 className="w-6 h-6 animate-spin text-slate-500" /></div>
                ) : filtered.length === 0 ? (
                  <p className="text-center text-sm text-slate-500 py-12">No bots found</p>
                ) : activeCategory === 'all' && !filter ? (
                  <>
                    {/* Featured Section */}
                    {featured.length > 0 && (
                      <div className="mb-6">
                        <div className="flex items-center gap-2 mb-3">
                          <Award className="w-4 h-4 text-amber-400" />
                          <h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider">Featured</h4>
                        </div>
                        <div className="grid grid-cols-2 gap-2">
                          {featured.slice(0, 4).map(bot => <BotCard key={bot.id} bot={bot} compact
                            onView={() => setDetailBot(bot)} onInstall={() => installBot(bot.id)}
                            installing={installing} selectedChannel={selectedChannel}
                            isInstalled={selectedChannel && isInstalled(bot.id, selectedChannel)} />)}
                        </div>
                      </div>
                    )}
                    {/* By Category */}
                    {categories.map(cat => {
                      const bots = grouped[cat];
                      if (!bots?.length) return null;
                      const cc = getCat(cat);
                      return (
                        <div key={cat} className="mb-5">
                          <div className="flex items-center gap-2 mb-2.5">
                            <div className="w-5 h-5 rounded-md flex items-center justify-center" style={{ background: `${cc.bg}25` }}>
                              <div className="w-2 h-2 rounded-full" style={{ background: cc.bg }} />
                            </div>
                            <h4 className="text-xs font-bold text-white uppercase tracking-wider">{cat}</h4>
                            <span className="text-[10px] text-slate-600">{bots.length} bots</span>
                          </div>
                          <div className="space-y-1.5">
                            {bots.map(bot => <BotCard key={bot.id} bot={bot}
                              onView={() => setDetailBot(bot)} onInstall={() => installBot(bot.id)}
                              installing={installing} selectedChannel={selectedChannel}
                              isInstalled={selectedChannel && isInstalled(bot.id, selectedChannel)} />)}
                          </div>
                        </div>
                      );
                    })}
                  </>
                ) : (
                  <div className="space-y-1.5">
                    {filtered.map(bot => <BotCard key={bot.id} bot={bot}
                      onView={() => setDetailBot(bot)} onInstall={() => installBot(bot.id)}
                      installing={installing} selectedChannel={selectedChannel}
                      isInstalled={selectedChannel && isInstalled(bot.id, selectedChannel)} />)}
                  </div>
                )}
              </div>
            </ScrollArea>
          </>
        ) : (
          /* ═══ Installed Tab ═══ */
          <ScrollArea className="flex-1">
            <div className="p-4 space-y-1.5">
              {installed.length === 0 ? (
                <div className="text-center py-16">
                  <Brain className="w-10 h-10 text-slate-700 mx-auto mb-3" />
                  <p className="text-sm text-slate-400 font-medium">No bots installed</p>
                  <p className="text-xs text-slate-600 mt-1">Browse the marketplace to install bots</p>
                </div>
              ) : installed.map(inst => {
                const catInfo = catalog.find(b => b.id === inst.bot_id);
                const Icon = getIcon(catInfo?.icon);
                const cc = getCat(catInfo?.category);
                return (
                  <div key={inst.id}
                    className="p-3 rounded-xl border border-slate-700/40 hover:border-slate-600/60 bg-slate-800/30 transition-all group cursor-pointer"
                    onClick={() => { setConfigBot(inst); setEditConfig(inst.config || {}); }}
                    data-testid={`installed-bot-${inst.id}`}>
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: cc.bg }}>
                        <Icon className="w-4 h-4 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <p className="text-sm font-medium text-white">{inst.bot_name}</p>
                          <span className={`w-1.5 h-1.5 rounded-full ${inst.is_active !== false ? 'bg-green-500' : 'bg-slate-500'}`} />
                        </div>
                        <p className="text-[10px] text-slate-500">#{getChannelName(inst.channel_id)} {inst.is_active !== false ? '' : '(Paused)'}</p>
                      </div>
                      <ChevronRight className="w-4 h-4 text-slate-600 group-hover:text-slate-400" />
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

// ═══ Bot Card Component ═══
const BotCard = ({ bot, compact, onView, onInstall, installing, selectedChannel, isInstalled }) => {
  const Icon = ICON_MAP[bot.icon] || Brain;
  const cc = CAT_STYLES[bot.category] || { bg: '#64748b' };

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

export default BotStoreModal;
