import { useState, useEffect } from 'react';
import { X, Loader2, Download, Trash2, Check, Search, Clipboard, Bell, BarChart3, Video, Hand, Brain, Globe, Github } from 'lucide-react';
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
      if (res.ok) { toast.success('Bot uninstalled'); loadInstalled(); }
      else toast.error('Uninstall failed');
    } catch { toast.error('Connection error'); }
  };

  const filtered = catalog.filter(b => {
    if (activeCategory !== 'all' && b.category !== activeCategory) return false;
    if (filter && !b.name.toLowerCase().includes(filter.toLowerCase()) && !b.description.toLowerCase().includes(filter.toLowerCase())) return false;
    return true;
  });

  const isInstalled = (botId, channelId) => installed.some(i => i.bot_id === botId && i.channel_id === channelId);

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
              {/* Category filter chips */}
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
                          <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                            style={{ background: cc.bg }}>
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
                const Icon = BOT_ICONS[BOT_ICONS[inst.bot_id] ? inst.bot_id : 'brain'] || Brain;
                return (
                  <div key={inst.id} className="p-3 rounded-xl border border-slate-100 hover:border-slate-200 transition-all group" data-testid={`installed-bot-${inst.id}`}>
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-lg bg-slate-800 flex items-center justify-center flex-shrink-0">
                        <Icon className="w-4 h-4 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-slate-800">{inst.bot_name}</p>
                        <p className="text-[10px] text-slate-500">Channel: {inst.channel_id?.slice(0, 8)}... {inst.is_active ? '(Active)' : '(Paused)'}</p>
                      </div>
                      <Button size="sm" variant="ghost" onClick={() => uninstallBot(inst.id)}
                        className="h-7 text-[10px] text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                        data-testid={`uninstall-bot-${inst.id}`}>
                        <Trash2 className="w-3 h-3 mr-1" />Remove
                      </Button>
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
