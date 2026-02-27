import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Users, Globe, Target, TrendingUp, BarChart3, Loader2, CheckCircle, ArrowUp } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const MetricCard = ({ icon: Icon, label, value, change, color }) => (
  <Card className="bg-slate-800 border-slate-700">
    <CardContent className="p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs text-slate-400 uppercase tracking-wide">{label}</p>
          <p className={`text-2xl font-bold mt-1 ${color}`}>{value}</p>
          {change && (
            <span className="text-xs text-emerald-400 flex items-center gap-0.5 mt-1">
              <ArrowUp className="w-3 h-3" /> {change}
            </span>
          )}
        </div>
        <div className="p-2 rounded-lg bg-slate-700"><Icon className={`w-5 h-5 ${color}`} /></div>
      </div>
    </CardContent>
  </Card>
);

export default function DEIAnalyticsPage() {
  const [metrics, setMetrics] = useState(null);
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/dei-analytics/metrics`).then(r => r.json()),
      fetch(`${API}/api/dei-analytics/goals`).then(r => r.json())
    ]).then(([m, g]) => {
      setMetrics(m);
      setGoals(g.goals || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="min-h-screen bg-slate-900 flex items-center justify-center"><Loader2 className="w-8 h-8 text-turquoise animate-spin" /></div>;

  const gender = metrics?.gender_distribution || {};
  const geo = metrics?.geographic_diversity || {};
  const benchmarks = metrics?.benchmarks || {};
  const trends = metrics?.trends || {};

  return (
    <div className="min-h-screen bg-slate-900 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center gap-3 mb-8">
          <div className="p-2 bg-purple-500/10 rounded-lg"><Users className="w-6 h-6 text-purple-400" /></div>
          <div>
            <h1 className="text-2xl font-bold text-white" data-testid="dei-page-title">DEI Analytics</h1>
            <p className="text-slate-400 text-sm">Diversity, Equity & Inclusion across your hiring pipeline</p>
          </div>
        </div>

        {/* Score & KPIs */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8" data-testid="dei-kpis">
          <MetricCard icon={Target} label="DEI Score" value={metrics?.dei_score || 0} color="text-purple-400" />
          <MetricCard icon={Users} label="Gender Parity" value={`${Math.round((benchmarks.gender_parity_index || 0) * 100)}%`} change={trends.gender_parity_change} color="text-blue-400" />
          <MetricCard icon={Globe} label="Geo Diversity" value={`${Math.round((benchmarks.geographic_diversity_index || 0) * 100)}%`} color="text-emerald-400" />
          <MetricCard icon={TrendingUp} label="Pipeline Equity" value={`${Math.round((benchmarks.pipeline_equity_ratio || 0) * 100)}%`} change={trends.diversity_hires_change} color="text-yellow-400" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Gender Distribution */}
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader><CardTitle className="text-white text-base flex items-center gap-2"><Users className="w-4 h-4 text-purple-400" /> Gender Distribution</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(gender).map(([g, count]) => {
                  const total = Object.values(gender).reduce((a, b) => a + b, 0);
                  const pct = total > 0 ? Math.round((count / total) * 100) : 0;
                  return (
                    <div key={g}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm text-slate-300 capitalize">{g}</span>
                        <span className="text-sm text-slate-400">{count} ({pct}%)</span>
                      </div>
                      <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                        <div className="h-full bg-purple-500 rounded-full transition-all" style={{ width: `${pct}%` }} />
                      </div>
                    </div>
                  );
                })}
                {Object.keys(gender).length === 0 && <p className="text-slate-500 text-sm">No gender data available</p>}
              </div>
            </CardContent>
          </Card>

          {/* Geographic Diversity */}
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader><CardTitle className="text-white text-base flex items-center gap-2"><Globe className="w-4 h-4 text-emerald-400" /> Geographic Diversity</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(geo).map(([loc, count]) => (
                  <div key={loc} className="flex items-center justify-between py-1.5 border-b border-slate-700/50 last:border-0">
                    <span className="text-sm text-slate-300">{loc}</span>
                    <Badge className="bg-slate-700 text-slate-300">{count}</Badge>
                  </div>
                ))}
                {Object.keys(geo).length === 0 && <p className="text-slate-500 text-sm">No location data available</p>}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* DEI Goals */}
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader><CardTitle className="text-white text-base flex items-center gap-2"><Target className="w-4 h-4 text-turquoise" /> DEI Goals & Progress</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-4" data-testid="dei-goals">
              {goals.map((goal, i) => {
                const pct = goal.target > 0 ? Math.round((goal.current / goal.target) * 100) : 0;
                return (
                  <div key={i} className="flex items-center gap-4">
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm text-slate-300">{goal.name}</span>
                        <span className="text-xs text-slate-400">{goal.current}/{goal.target} {goal.unit}</span>
                      </div>
                      <Progress value={pct} className="h-2 bg-slate-700" />
                    </div>
                    {pct >= 100 && <CheckCircle className="w-4 h-4 text-emerald-400 flex-shrink-0" />}
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
