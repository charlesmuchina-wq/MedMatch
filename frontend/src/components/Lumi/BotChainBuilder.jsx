/**
 * BotChainBuilder — Bot-to-Bot Workflow Automation
 * Create chains where output of one bot feeds into the next
 */
import { useState, useEffect } from 'react';
import { Plus, Play, Trash2, Loader2, ArrowRight, Zap, ChevronDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { toast } from 'sonner';
import { API } from './constants';

const CAT_COLORS = {
  'Job Toolkit': '#00B894',
  'AI Meeting': '#6C5CE7',
  'AI Messenger': '#00CEC9',
  'Security & QA': '#E17055',
};

const BotChainBuilder = ({ channelId, token }) => {
  const [chains, setChains] = useState([]);
  const [catalog, setCatalog] = useState([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(null);
  const [creating, setCreating] = useState(false);
  const [newName, setNewName] = useState('');
  const [steps, setSteps] = useState([]);
  const [showBotPicker, setShowBotPicker] = useState(false);

  useEffect(() => { loadData(); }, [channelId]);

  const loadData = async () => {
    setLoading(true);
    const headers = { Authorization: `Bearer ${token}` };
    const [chainsRes, catalogRes] = await Promise.all([
      fetch(`${API}/api/lumi/bots/chains/${channelId}`, { headers }).catch(() => null),
      fetch(`${API}/api/lumi/bots/catalog`, { headers }).catch(() => null),
    ]);
    if (chainsRes?.ok) setChains((await chainsRes.json()).chains || []);
    if (catalogRes?.ok) setCatalog((await catalogRes.json()).bots || []);
    setLoading(false);
  };

  const addStep = (bot) => {
    setSteps(prev => [...prev, { bot_id: bot.id, action: bot.id, order: prev.length + 1, bot_name: bot.name, category: bot.category }]);
    setShowBotPicker(false);
  };

  const removeStep = (idx) => setSteps(prev => prev.filter((_, i) => i !== idx).map((s, i) => ({ ...s, order: i + 1 })));

  const createChain = async () => {
    if (!newName.trim() || steps.length < 2) return;
    try {
      const res = await fetch(`${API}/api/lumi/bots/chains`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ name: newName, channel_id: channelId, steps: steps.map(s => ({ bot_id: s.bot_id, action: s.action, order: s.order })) })
      });
      if (res.ok) {
        toast.success('Workflow created!');
        setCreating(false);
        setNewName('');
        setSteps([]);
        loadData();
      } else { toast.error((await res.json()).detail || 'Failed'); }
    } catch { toast.error('Connection error'); }
  };

  const runChain = async (chainId) => {
    setRunning(chainId);
    try {
      const res = await fetch(`${API}/api/lumi/bots/chains/${chainId}/run`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        toast.success(`Workflow complete! ${data.steps_completed} steps executed`);
        loadData();
      } else { toast.error('Workflow failed'); }
    } catch { toast.error('Connection error'); }
    setRunning(null);
  };

  const deleteChain = async (chainId) => {
    try {
      await fetch(`${API}/api/lumi/bots/chains/${chainId}`, { method: 'DELETE', headers: { Authorization: `Bearer ${token}` } });
      toast.success('Workflow deleted');
      loadData();
    } catch {}
  };

  if (loading) return <div className="flex items-center justify-center py-8"><Loader2 className="w-5 h-5 animate-spin text-slate-400" /></div>;

  return (
    <div data-testid="bot-chain-builder">
      {/* Create new chain */}
      {!creating ? (
        <Button onClick={() => setCreating(true)} variant="outline" className="w-full mb-4 border-dashed border-white/10 text-slate-400 hover:text-white hover:border-white/20" data-testid="create-chain-btn">
          <Plus className="w-4 h-4 mr-2" /> New Workflow
        </Button>
      ) : (
        <div className="mb-4 p-4 rounded-xl bg-white/[0.03] border border-white/[0.08]" data-testid="chain-builder-form">
          <Input value={newName} onChange={e => setNewName(e.target.value)} placeholder="Workflow name..." className="mb-3 bg-white/5 border-white/10 text-white placeholder-slate-500" data-testid="chain-name-input" />

          {/* Steps */}
          <div className="space-y-2 mb-3">
            {steps.map((step, i) => {
              const color = CAT_COLORS[step.category] || '#64748b';
              return (
                <div key={i} className="flex items-center gap-2" data-testid={`chain-step-${i}`}>
                  {i > 0 && <ArrowRight className="w-3 h-3 text-slate-500 flex-shrink-0" />}
                  <div className="flex-1 flex items-center gap-2 px-3 py-2 rounded-lg border border-white/[0.06] bg-white/[0.02]">
                    <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: color }} />
                    <span className="text-xs text-white font-medium">{step.bot_name}</span>
                    <span className="text-[9px] px-1.5 py-0.5 rounded-full ml-auto" style={{ background: `${color}15`, color }}>{step.category}</span>
                  </div>
                  <button onClick={() => removeStep(i)} className="p-1 text-slate-500 hover:text-red-400"><Trash2 className="w-3 h-3" /></button>
                </div>
              );
            })}
          </div>

          {/* Add step button */}
          <div className="relative">
            <Button onClick={() => setShowBotPicker(!showBotPicker)} variant="ghost" size="sm" className="text-xs text-slate-400 hover:text-white" data-testid="add-step-btn">
              <Plus className="w-3 h-3 mr-1" /> Add Bot Step <ChevronDown className="w-3 h-3 ml-1" />
            </Button>
            {showBotPicker && (
              <div className="absolute left-0 bottom-full mb-1 w-64 bg-[#161B22] border border-white/10 rounded-xl shadow-xl z-20 max-h-48 overflow-auto" data-testid="bot-step-picker">
                {catalog.map(bot => (
                  <button key={bot.id} onClick={() => addStep(bot)}
                    className="w-full flex items-center gap-2 px-3 py-2 text-left hover:bg-white/5 transition-colors"
                    data-testid={`pick-bot-${bot.id}`}>
                    <div className="w-2 h-2 rounded-full" style={{ background: CAT_COLORS[bot.category] || '#64748b' }} />
                    <span className="text-xs text-white">{bot.name}</span>
                    <span className="text-[9px] text-slate-500 ml-auto">{bot.category}</span>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex gap-2 mt-3">
            <Button onClick={() => { setCreating(false); setSteps([]); setNewName(''); }} variant="ghost" size="sm" className="text-xs text-slate-400">Cancel</Button>
            <Button onClick={createChain} size="sm" disabled={!newName.trim() || steps.length < 2}
              className="text-xs bg-[#00CEC9]/10 text-[#00CEC9] hover:bg-[#00CEC9]/20 border border-[#00CEC9]/20" data-testid="save-chain-btn">
              <Zap className="w-3 h-3 mr-1" /> Create ({steps.length} steps)
            </Button>
          </div>
        </div>
      )}

      {/* Existing chains */}
      <ScrollArea className="max-h-[300px]">
        {chains.length === 0 && !creating && (
          <div className="text-center py-8 text-slate-500">
            <Zap className="w-8 h-8 mx-auto mb-2 opacity-30" />
            <p className="text-xs">No workflows yet. Create one to chain bots together!</p>
          </div>
        )}
        <div className="space-y-2">
          {chains.map(chain => (
            <div key={chain.id} className="p-3 rounded-xl bg-white/[0.02] border border-white/[0.06] hover:border-white/[0.1] transition-colors" data-testid={`chain-${chain.id}`}>
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-xs font-semibold text-white">{chain.name}</h4>
                <div className="flex items-center gap-1">
                  {chain.run_count > 0 && <span className="text-[9px] text-slate-500">{chain.run_count} runs</span>}
                  <Button onClick={() => runChain(chain.id)} variant="ghost" size="sm" disabled={running === chain.id}
                    className="h-6 px-2 text-[10px] text-emerald-400 hover:text-emerald-300 hover:bg-emerald-500/10" data-testid={`run-chain-${chain.id}`}>
                    {running === chain.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <Play className="w-3 h-3" />}
                    <span className="ml-1">{running === chain.id ? 'Running...' : 'Run'}</span>
                  </Button>
                  <Button onClick={() => deleteChain(chain.id)} variant="ghost" size="sm" className="h-6 px-1.5 text-slate-500 hover:text-red-400" data-testid={`delete-chain-${chain.id}`}>
                    <Trash2 className="w-3 h-3" />
                  </Button>
                </div>
              </div>
              <div className="flex items-center gap-1 flex-wrap">
                {chain.steps.map((step, i) => (
                  <div key={i} className="flex items-center gap-1">
                    {i > 0 && <ArrowRight className="w-2.5 h-2.5 text-slate-600" />}
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-white/[0.04] text-slate-300 border border-white/[0.06]">
                      {step.bot_name || step.bot_id}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
};

export default BotChainBuilder;
