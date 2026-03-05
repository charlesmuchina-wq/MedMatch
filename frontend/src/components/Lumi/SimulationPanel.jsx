import { useState } from 'react';
import { toast } from 'sonner';
import { Zap, ArrowRight, Loader2, X } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { API, ESY } from './constants';

export const SimulationPanel = ({ onClose, token }) => {
  const [scenario, setScenario] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const runSimulation = async () => {
    if (!scenario.trim() || loading) return;
    setLoading(true);
    try { const res = await fetch(`${API}/api/lumi/ai/simulate`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }, body: JSON.stringify({ scenario: scenario.trim() }) }); if (res.ok) setResult(await res.json()); } catch (e) { toast.error('Simulation failed'); }
    setLoading(false);
  };

  const riskColor = (score) => score >= 70 ? ESY.deepRed : score >= 40 ? ESY.pink : ESY.turquoise;
  const severityColor = { high: ESY.deepRed, medium: ESY.pink, low: ESY.turquoise };
  const suggestions = ['What if we delay the project by 2 weeks?', 'What if we remove a team member?', 'What if we add 5 more high-priority tasks?', 'What if we reassign all tasks from Engineering?'];

  return (
    <div className="w-[380px] border-l border-slate-200 bg-white flex flex-col h-full" data-testid="simulation-panel">
      <div className="h-14 flex items-center justify-between px-4 border-b border-slate-200" style={{ background: `linear-gradient(135deg, ${ESY.pink}05, ${ESY.turquoise}05)` }}>
        <div className="flex items-center gap-2"><Zap className="w-4 h-4" style={{ color: ESY.pink }} /><h3 className="text-sm font-semibold text-slate-900">What-If Simulator</h3></div>
        <button onClick={onClose} className="p-1 hover:bg-slate-100 rounded-md"><X className="w-4 h-4 text-slate-500" /></button>
      </div>
      <div className="p-3 border-b border-slate-100">
        <textarea value={scenario} onChange={e => setScenario(e.target.value)} placeholder="Describe a scenario to simulate..." rows={2}
          className="w-full text-xs bg-slate-50 border border-slate-200 rounded-lg p-3 outline-none resize-none focus:border-[#E84393] transition-colors" data-testid="simulation-input" />
        <button onClick={runSimulation} disabled={!scenario.trim() || loading}
          className="w-full mt-2 py-2 rounded-lg text-xs font-medium text-white transition-all disabled:opacity-40 hover:opacity-90"
          style={{ background: `linear-gradient(135deg, ${ESY.pink}, ${ESY.turquoise})` }} data-testid="run-simulation-btn">
          {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin inline mr-1" /> : <Zap className="w-3.5 h-3.5 inline mr-1" />}{loading ? 'Simulating...' : 'Run Simulation'}
        </button>
        {!result && !loading && (<div className="mt-2 space-y-1">{suggestions.map((s, i) => (<button key={i} onClick={() => setScenario(s)} className="w-full text-left text-[10px] px-2 py-1.5 rounded border border-slate-100 text-slate-500 hover:bg-slate-50 transition-colors" data-testid={`sim-suggestion-${i}`}>{s}</button>))}</div>)}
      </div>
      <ScrollArea className="flex-1">
        <div className="p-3">
          {result && (<div className="space-y-3">
            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100">
              <div><p className="text-[10px] text-slate-400 uppercase tracking-wider mb-1">Risk Score</p><p className="text-3xl font-bold" style={{ color: riskColor(result.risk_score || 0) }}>{result.risk_score || 0}</p></div>
              <div className="text-right"><p className="text-xs font-medium text-slate-700">{result.scenario_summary}</p></div>
            </div>
            {result.before_after && (<div className="grid grid-cols-2 gap-2">
              <div className="p-2.5 rounded-lg border border-slate-200"><p className="text-[9px] font-semibold text-slate-400 uppercase mb-1">Before</p><p className="text-xs text-slate-600">{result.before_after.before?.team_capacity}</p><p className="text-[10px] text-slate-400">Risk: {result.before_after.before?.risk_level}</p></div>
              <div className="p-2.5 rounded-lg border" style={{ borderColor: `${ESY.pink}30`, background: `${ESY.pink}05` }}><p className="text-[9px] font-semibold uppercase mb-1" style={{ color: ESY.pink }}>After</p><p className="text-xs text-slate-600">{result.before_after.after?.team_capacity}</p><p className="text-[10px] text-slate-400">Risk: {result.before_after.after?.risk_level}</p></div>
            </div>)}
            {result.impact_timeline?.length > 0 && (<div><p className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-2">Impact Timeline</p><div className="space-y-2">{result.impact_timeline.map((item, i) => (<div key={i} className="flex gap-2 items-start"><div className="w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0" style={{ backgroundColor: severityColor[item.severity] || ESY.turquoise }} /><div><p className="text-[10px] font-medium" style={{ color: severityColor[item.severity] || ESY.turquoise }}>{item.timeframe}</p><p className="text-[11px] text-slate-600">{item.impact}</p></div></div>))}</div></div>)}
            {result.recommendation && (<div className="p-3 rounded-lg border" style={{ borderColor: `${ESY.turquoise}20`, background: `${ESY.turquoise}05` }}><p className="text-[10px] font-semibold uppercase tracking-wider mb-1" style={{ color: ESY.turquoise }}>Recommendation</p><p className="text-xs text-slate-700 leading-relaxed">{result.recommendation}</p></div>)}
            {result.alternative_approaches?.length > 0 && (<div><p className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1">Alternatives</p>{result.alternative_approaches.map((alt, i) => (<p key={i} className="text-[11px] text-slate-600 flex items-start gap-1.5 mb-1"><ArrowRight className="w-3 h-3 mt-0.5 flex-shrink-0" style={{ color: ESY.pink }} />{alt}</p>))}</div>)}
            <button onClick={() => { setResult(null); setScenario(''); }} className="w-full text-xs py-1.5 rounded-md hover:bg-slate-50 transition-colors" style={{ color: ESY.turquoise }}>New Simulation</button>
          </div>)}
        </div>
      </ScrollArea>
    </div>
  );
};
