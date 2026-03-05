import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { TrendingDown, Activity, AlertTriangle, CheckCircle2, Loader2, X } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { API, ESY } from './constants';

export const BottleneckPanel = ({ onClose, token }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadBottlenecks = async () => { setLoading(true); try { const res = await fetch(`${API}/api/lumi/bottlenecks`, { headers: { 'Authorization': `Bearer ${token}` } }); if (res.ok) setData(await res.json()); } catch (e) { toast.error('Failed to load bottlenecks'); } setLoading(false); };

  useEffect(() => { loadBottlenecks(); }, []);

  const severityIcon = { critical: AlertTriangle, warning: TrendingDown, info: Activity };
  const healthColor = (score) => score >= 80 ? ESY.turquoise : score >= 50 ? '#E17055' : ESY.deepRed;

  return (
    <div className="w-[350px] border-l border-slate-200 bg-white flex flex-col h-full" data-testid="bottleneck-panel">
      <div className="h-14 flex items-center justify-between px-4 border-b border-slate-200">
        <div className="flex items-center gap-2"><TrendingDown className="w-4 h-4" style={{ color: ESY.deepRed }} /><h3 className="text-sm font-semibold text-slate-900">Bottlenecks</h3></div>
        <button onClick={onClose} className="p-1 hover:bg-slate-100 rounded-md"><X className="w-4 h-4 text-slate-500" /></button>
      </div>
      <ScrollArea className="flex-1">
        <div className="p-4">
          {loading ? (<div className="flex items-center justify-center py-8"><Loader2 className="w-5 h-5 animate-spin" style={{ color: ESY.turquoise }} /></div>) : !data ? (
            <button onClick={loadBottlenecks} className="w-full py-3 rounded-lg border text-sm" style={{ borderColor: `${ESY.deepRed}30`, color: ESY.deepRed }}>Scan for Bottlenecks</button>
          ) : (<>
            <div className="flex items-center justify-between p-4 rounded-xl bg-slate-50 border border-slate-100 mb-4">
              <div><p className="text-[10px] text-slate-400 uppercase tracking-wider mb-1">Project Health</p><p className="text-3xl font-bold" style={{ color: healthColor(data.health_score) }}>{data.health_score}</p></div>
              <div className="text-right space-y-1">
                <div className="text-[10px] text-slate-500"><span className="font-semibold">{data.workload_summary?.total_open_items || 0}</span> open items</div>
                <div className="text-[10px] text-slate-500"><span className="font-semibold">{data.workload_summary?.people_with_work || 0}</span> people assigned</div>
                <div className="text-[10px] text-slate-500"><span className="font-semibold">{data.workload_summary?.avg_workload || 0}</span> avg workload</div>
              </div>
            </div>
            {data.bottlenecks?.length === 0 ? (<div className="text-center py-6"><CheckCircle2 className="w-10 h-10 mx-auto mb-2" style={{ color: ESY.turquoise }} /><p className="text-sm font-medium text-slate-700">No Bottlenecks</p><p className="text-xs text-slate-400 mt-1">Team workload is balanced</p></div>) : (
              <div className="space-y-3">{data.bottlenecks.map((bn) => { const Icon = severityIcon[bn.severity] || Activity; const color = bn.severity === 'critical' ? ESY.deepRed : bn.severity === 'warning' ? ESY.pink : ESY.turquoise; return (
                <div key={bn.id} className="p-3 rounded-xl border" style={{ borderColor: `${color}20`, background: `${color}05` }} data-testid={`bottleneck-${bn.id}`}>
                  <div className="flex items-start gap-2"><Icon className="w-4 h-4 mt-0.5 flex-shrink-0" style={{ color }} /><div className="flex-1 min-w-0"><p className="text-xs font-semibold text-slate-800">{bn.title}</p><p className="text-[11px] text-slate-600 mt-1 leading-relaxed">{bn.description}</p>
                    {bn.items && (<div className="mt-2 space-y-0.5">{bn.items.slice(0, 3).map((item, i) => (<p key={i} className="text-[10px] text-slate-500 pl-2 border-l-2" style={{ borderColor: `${color}30` }}>{item}</p>))}</div>)}
                    {bn.workload && (<div className="mt-2 flex items-center gap-2"><span className="text-[9px] px-2 py-0.5 rounded-full font-medium text-white" style={{ backgroundColor: color }}>{bn.workload.total} tasks</span>{bn.workload.high > 0 && <span className="text-[9px] px-2 py-0.5 rounded-full font-medium text-white" style={{ backgroundColor: ESY.deepRed }}>{bn.workload.high} critical</span>}</div>)}
                    {bn.suggestion && <p className="text-[10px] mt-2 font-medium" style={{ color: ESY.turquoise }}>Suggestion: {bn.suggestion}</p>}
                  </div></div>
                </div>); })}</div>
            )}
            <button onClick={loadBottlenecks} className="w-full mt-3 text-xs py-1.5 rounded-md hover:bg-slate-50 transition-colors" style={{ color: ESY.turquoise }}>Rescan</button>
          </>)}
        </div>
      </ScrollArea>
    </div>
  );
};
