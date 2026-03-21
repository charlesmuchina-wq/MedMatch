import { useState, useEffect } from 'react';
import {
  X, Loader2, Check, Search, Brain, Sparkles, Award, ChevronRight
} from 'lucide-react';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { toast } from 'sonner';
import { API, ESY } from './constants';
import { BotCard } from './BotStore/BotCard';
import { BotDetailView } from './BotStore/BotDetailView';
import { BotConfigView } from './BotStore/BotConfigView';
import { getCat } from './BotStore/constants';

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

  const isInstalled = (botId, chId) => installed.some(i => i.bot_id === botId && i.channel_id === chId);
  const getChannelName = (chId) => (channels || []).find(c => c.id === chId)?.name || chId?.slice(0, 10);

  const filtered = catalog.filter(b => {
    if (activeCategory !== 'all' && b.category !== activeCategory) return false;
    if (filter && !b.name.toLowerCase().includes(filter.toLowerCase()) && !b.description.toLowerCase().includes(filter.toLowerCase())) return false;
    return true;
  });

  const featured = catalog.filter(b => b.featured);
  const grouped = categories.reduce((acc, cat) => { acc[cat] = filtered.filter(b => b.category === cat); return acc; }, {});

  if (configBot) {
    return <BotConfigView configBot={configBot} editConfig={editConfig} setEditConfig={setEditConfig}
      catalog={catalog} channels={channels} onToggle={toggleBotActive} onUninstall={uninstallBot}
      onSave={saveConfig} savingConfig={savingConfig}
      onClose={(action) => action === 'back' ? setConfigBot(null) : onClose()} />;
  }

  if (detailBot) {
    return <BotDetailView bot={detailBot} channels={channels} selectedChannel={selectedChannel}
      setSelectedChannel={setSelectedChannel} onInstall={installBot} installing={installing}
      onClose={onClose} onBack={() => setDetailBot(null)} />;
  }

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
            <div className="p-4 space-y-3 border-b border-slate-700/30 flex-shrink-0">
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                  <Input value={filter} onChange={e => setFilter(e.target.value)} placeholder={`Search ${catalog.length} bots...`}
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

            <ScrollArea className="flex-1">
              <div className="p-4">
                {loading ? (
                  <div className="flex justify-center py-16"><Loader2 className="w-6 h-6 animate-spin text-slate-500" /></div>
                ) : filtered.length === 0 ? (
                  <p className="text-center text-sm text-slate-500 py-12">No bots found</p>
                ) : activeCategory === 'all' && !filter ? (
                  <>
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
                const cc = getCat(catInfo?.category);
                return (
                  <div key={inst.id}
                    className="p-3 rounded-xl border border-slate-700/40 hover:border-slate-600/60 bg-slate-800/30 transition-all group cursor-pointer"
                    onClick={() => { setConfigBot(inst); setEditConfig(inst.config || {}); }}
                    data-testid={`installed-bot-${inst.id}`}>
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: cc.bg }}>
                        <Brain className="w-4 h-4 text-white" />
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

export default BotStoreModal;
