import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { Network, Globe, Zap, Loader2, X } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { API, ESY } from './constants';

export const KnowledgeGraphPanel = ({ onClose, token }) => {
  const [graph, setGraph] = useState(null);
  const [loading, setLoading] = useState(false);
  const [impactResult, setImpactResult] = useState(null);
  const [impactLoading, setImpactLoading] = useState(false);
  const [selectedNode, setSelectedNode] = useState(null);
  const [filterType, setFilterType] = useState('all');

  const loadGraph = async () => { setLoading(true); try { const res = await fetch(`${API}/api/lumi/knowledge-graph`, { headers: { 'Authorization': `Bearer ${token}` } }); if (res.ok) setGraph(await res.json()); } catch (e) { toast.error('Failed to load graph'); } setLoading(false); };
  const runImpactAnalysis = async (node) => { setSelectedNode(node); setImpactLoading(true); try { const res = await fetch(`${API}/api/lumi/knowledge-graph/impact`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }, body: JSON.stringify({ entity_type: node.type, entity_id: node.id.split('_').slice(1).join('_'), entity_name: node.label }) }); if (res.ok) setImpactResult(await res.json()); } catch (e) {} setImpactLoading(false); };

  useEffect(() => { loadGraph(); }, []);

  const nodeColors = { person: { bg: ESY.turquoise, text: 'white' }, channel: { bg: '#36454F', text: 'white' }, task: { bg: ESY.pink, text: 'white' }, action_item: { bg: ESY.deepRed, text: 'white' }, meeting: { bg: '#6C5CE7', text: 'white' } };
  const riskColors = { critical: ESY.deepRed, high: ESY.pink, medium: '#E17055', low: ESY.turquoise };
  const filteredNodes = graph?.nodes?.filter(n => filterType === 'all' || n.type === filterType) || [];

  return (
    <div className="w-[380px] border-l border-slate-200 bg-white flex flex-col h-full" data-testid="knowledge-graph-panel">
      <div className="h-14 flex items-center justify-between px-4 border-b border-slate-200">
        <div className="flex items-center gap-2"><Network className="w-4 h-4" style={{ color: ESY.turquoise }} /><h3 className="text-sm font-semibold text-slate-900">Knowledge Graph</h3>{graph && <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-slate-100 text-slate-500">{graph.stats?.total_nodes} nodes</span>}</div>
        <button onClick={onClose} className="p-1 hover:bg-slate-100 rounded-md"><X className="w-4 h-4 text-slate-500" /></button>
      </div>
      <div className="flex gap-1 px-3 py-2 border-b border-slate-100 overflow-x-auto">
        {['all', 'person', 'channel', 'task', 'meeting', 'action_item'].map(t => (
          <button key={t} onClick={() => setFilterType(t)} className={`px-2.5 py-1 rounded-full text-[10px] font-medium whitespace-nowrap transition-colors ${filterType === t ? 'text-white' : 'bg-slate-50 text-slate-500 hover:bg-slate-100'}`} style={filterType === t ? { backgroundColor: nodeColors[t]?.bg || ESY.turquoise } : {}} data-testid={`graph-filter-${t}`}>{t === 'all' ? 'All' : t === 'action_item' ? 'Actions' : t.charAt(0).toUpperCase() + t.slice(1)}s</button>
        ))}
      </div>
      <ScrollArea className="flex-1">
        <div className="p-3">
          {loading ? (<div className="flex items-center justify-center py-8"><Loader2 className="w-5 h-5 animate-spin" style={{ color: ESY.turquoise }} /></div>) : !graph ? (
            <button onClick={loadGraph} className="w-full py-3 rounded-lg border text-sm" style={{ borderColor: `${ESY.turquoise}30`, color: ESY.turquoise }}>Load Knowledge Graph</button>
          ) : (<>
            <div className="grid grid-cols-3 gap-2 mb-3">
              {Object.entries(graph.stats?.by_type || {}).map(([type, count]) => (<div key={type} className="p-2 rounded-lg border border-slate-100 text-center"><p className="text-lg font-bold" style={{ color: nodeColors[type]?.bg || '#64748b' }}>{count}</p><p className="text-[9px] text-slate-400 capitalize">{type === 'action_item' ? 'Actions' : type}s</p></div>))}
            </div>
            <div className="mb-3 p-2 rounded-lg border border-slate-100 flex items-center justify-between"><span className="text-xs text-slate-500">Relationships</span><span className="text-sm font-bold" style={{ color: ESY.pink }}>{graph.stats?.total_edges}</span></div>
            <div className="space-y-1">
              {filteredNodes.slice(0, 30).map((node) => { const nc = nodeColors[node.type] || { bg: '#64748b', text: 'white' }; const connections = graph.edges?.filter(e => e.source === node.id || e.target === node.id).length || 0; return (
                <button key={node.id} onClick={() => runImpactAnalysis(node)} className={`w-full flex items-center gap-2.5 p-2 rounded-lg border transition-all hover:shadow-sm ${selectedNode?.id === node.id ? 'border-slate-300 bg-slate-50' : 'border-slate-100 hover:border-slate-200'}`} data-testid={`graph-node-${node.id}`}>
                  <div className="w-6 h-6 rounded-full flex items-center justify-center text-[8px] font-bold flex-shrink-0" style={{ backgroundColor: nc.bg, color: nc.text }}>{node.label?.[0]?.toUpperCase() || '?'}</div>
                  <div className="flex-1 min-w-0 text-left"><p className="text-xs font-medium text-slate-800 truncate">{node.label}</p><p className="text-[9px] text-slate-400">{node.type} · {connections} connections</p></div>
                  {node.status && <span className={`text-[8px] px-1.5 py-0.5 rounded ${node.status === 'done' ? 'bg-emerald-50 text-emerald-600' : node.status === 'open' ? 'bg-amber-50 text-amber-600' : 'bg-slate-50 text-slate-500'}`}>{node.status}</span>}
                </button>); })}
            </div>
          </>)}
          {impactLoading && (<div className="mt-3 p-3 rounded-lg border border-slate-200 bg-slate-50 text-center"><Loader2 className="w-4 h-4 animate-spin mx-auto" style={{ color: ESY.turquoise }} /><p className="text-[10px] text-slate-400 mt-1">Analyzing impact...</p></div>)}
          {impactResult && !impactLoading && (
            <div className="mt-3 p-3 rounded-xl border" style={{ borderColor: `${riskColors[impactResult.risk_level]}30`, background: `${riskColors[impactResult.risk_level]}05` }} data-testid="impact-result">
              <div className="flex items-center justify-between mb-2"><span className="text-xs font-bold text-slate-800">Impact Analysis</span><span className="text-[9px] font-bold px-2 py-0.5 rounded-full text-white" style={{ backgroundColor: riskColors[impactResult.risk_level] }}>{impactResult.risk_level?.toUpperCase()}</span></div>
              {impactResult.direct?.map((d, i) => (<div key={i} className="flex items-start gap-2 text-xs text-slate-600 mb-1"><Zap className="w-3 h-3 mt-0.5 flex-shrink-0" style={{ color: ESY.deepRed }} /><span>{d.description}</span></div>))}
              {impactResult.indirect?.map((d, i) => (<div key={i} className="flex items-start gap-2 text-xs text-slate-500 mb-1"><Globe className="w-3 h-3 mt-0.5 flex-shrink-0" style={{ color: ESY.pink }} /><span>{d.description}</span></div>))}
              {impactResult.ai_analysis && (<div className="mt-2 pt-2 border-t border-slate-100"><p className="text-[10px] text-slate-600 leading-relaxed whitespace-pre-wrap">{impactResult.ai_analysis}</p></div>)}
            </div>
          )}
        </div>
      </ScrollArea>
    </div>
  );
};
