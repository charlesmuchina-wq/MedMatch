import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Users, Clock, DollarSign, BarChart3, Target, Briefcase, CheckCircle, TrendingUp, Loader2 } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const StatCard = ({ icon: Icon, label, value, color = 'text-turquoise' }) => (
  <Card className="bg-slate-800 border-slate-700">
    <CardContent className="p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs text-slate-400 uppercase tracking-wide">{label}</p>
          <p className={`text-2xl font-bold mt-1 ${color}`}>{value}</p>
        </div>
        <div className="p-2 rounded-lg bg-slate-700"><Icon className={`w-5 h-5 ${color}`} /></div>
      </div>
    </CardContent>
  </Card>
);

export default function HiringMetricsPage() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/api/ai-talent/hiring-metrics`).then(r => r.ok ? r.json() : null).then(d => { if (d) setMetrics(d); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="min-h-screen bg-slate-900 flex items-center justify-center"><Loader2 className="w-8 h-8 text-turquoise animate-spin" /></div>;

  const pipeline = metrics?.pipeline || {};
  const sources = metrics?.source_effectiveness || {};

  return (
    <div className="min-h-screen bg-slate-900 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center gap-3 mb-8">
          <div className="p-2 bg-turquoise/10 rounded-lg"><BarChart3 className="w-6 h-6 text-turquoise" /></div>
          <div>
            <h1 className="text-2xl font-bold text-white" data-testid="hiring-metrics-title">Hiring Metrics</h1>
            <p className="text-slate-400 text-sm">Time-to-hire, cost-per-hire, and pipeline analytics</p>
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8" data-testid="metrics-cards">
          <StatCard icon={Users} label="Total Applications" value={metrics?.total_applications || 0} />
          <StatCard icon={CheckCircle} label="Hired" value={metrics?.hired || 0} color="text-emerald-400" />
          <StatCard icon={Clock} label="Avg Time to Hire" value={`${metrics?.avg_time_to_hire_days || 0}d`} color="text-yellow-400" />
          <StatCard icon={DollarSign} label="Cost per Hire" value={`$${(metrics?.avg_cost_per_hire || 0).toLocaleString()}`} color="text-blue-400" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader><CardTitle className="text-white text-base flex items-center gap-2"><Target className="w-4 h-4 text-turquoise" /> Hire Rate</CardTitle></CardHeader>
            <CardContent>
              <div className="flex items-center gap-4">
                <div className="relative w-24 h-24">
                  <svg className="w-24 h-24 -rotate-90" viewBox="0 0 36 36">
                    <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#334155" strokeWidth="3" />
                    <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#10b981" strokeWidth="3" strokeDasharray={`${metrics?.hire_rate || 0}, 100`} />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center"><span className="text-xl font-bold text-white">{metrics?.hire_rate || 0}%</span></div>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-emerald-500" /><span className="text-slate-300">Hired: {metrics?.hired || 0}</span></div>
                  <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-red-500" /><span className="text-slate-300">Rejected: {metrics?.rejected || 0}</span></div>
                  <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-yellow-500" /><span className="text-slate-300">In Progress: {metrics?.in_progress || 0}</span></div>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader><CardTitle className="text-white text-base flex items-center gap-2"><TrendingUp className="w-4 h-4 text-turquoise" /> Source Effectiveness</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(sources).map(([source, pct]) => (
                  <div key={source}>
                    <div className="flex items-center justify-between mb-1"><span className="text-sm text-slate-300 capitalize">{source}</span><span className="text-sm text-slate-400">{pct}%</span></div>
                    <div className="h-2 bg-slate-700 rounded-full overflow-hidden"><div className="h-full bg-turquoise rounded-full" style={{ width: `${pct}%` }} /></div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader><CardTitle className="text-white text-base flex items-center gap-2"><Briefcase className="w-4 h-4 text-turquoise" /> Pipeline</CardTitle></CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-4" data-testid="pipeline-breakdown">
              {Object.entries(pipeline).length > 0 ? Object.entries(pipeline).map(([status, count]) => (
                <div key={status} className="bg-slate-700 rounded-lg p-4 min-w-[120px] text-center">
                  <p className="text-2xl font-bold text-white">{count}</p><p className="text-xs text-slate-400 capitalize mt-1">{status}</p>
                </div>
              )) : <p className="text-slate-500 text-sm">No pipeline data yet</p>}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
