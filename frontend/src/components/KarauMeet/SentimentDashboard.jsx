import { useState, useEffect, useCallback } from 'react';
import { Activity, AlertCircle, TrendingUp, TrendingDown, Zap, Coffee, HelpCircle, BarChart3 } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

const API = process.env.REACT_APP_BACKEND_URL;

const ENERGY_ICONS = {
  high: Zap,
  neutral: Activity,
  low: Coffee,
};

const ENERGY_COLORS = {
  high: 'text-emerald-400',
  neutral: 'text-blue-400',
  low: 'text-amber-400',
};

export default function SentimentDashboard({ meetingId }) {
  const [heatmap, setHeatmap] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchHeatmap = useCallback(async () => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/sentiment-dash/heatmap/${meetingId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) setHeatmap(await res.json());
    } catch {}
    setLoading(false);
  }, [meetingId]);

  useEffect(() => {
    fetchHeatmap();
    const interval = setInterval(fetchHeatmap, 15000);
    return () => clearInterval(interval);
  }, [fetchHeatmap]);

  if (loading) return <div className="p-3 text-[9px] text-slate-500">Loading sentiment data...</div>;

  const agg = heatmap?.aggregate;
  const recs = heatmap?.recommendations || [];
  const participants = heatmap?.participants || [];

  return (
    <div className="flex-1 flex flex-col overflow-hidden" data-testid="sentiment-dashboard">
      <div className="p-2.5 border-b border-white/5">
        <h3 className="text-xs font-semibold text-white flex items-center gap-1.5">
          <BarChart3 className="w-3.5 h-3.5 text-cyan-400" />
          Sentiment Dashboard
        </h3>
        <p className="text-[8px] text-slate-500 mt-0.5">Real-time engagement heatmap</p>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {/* Aggregate Metrics */}
        {agg && (
          <div className="grid grid-cols-3 gap-1" data-testid="sentiment-metrics">
            <MetricCard
              label="Attention"
              value={agg.avg_attention}
              max={10}
              color={agg.avg_attention >= 6 ? 'emerald' : agg.avg_attention >= 4 ? 'amber' : 'red'}
              icon={agg.avg_attention >= 6 ? TrendingUp : TrendingDown}
            />
            <MetricCard
              label="Engagement"
              value={agg.avg_engagement}
              max={10}
              color={agg.avg_engagement >= 6 ? 'emerald' : agg.avg_engagement >= 4 ? 'amber' : 'red'}
              icon={agg.avg_engagement >= 6 ? TrendingUp : TrendingDown}
            />
            <MetricCard
              label="Confusion"
              value={Math.round(agg.avg_confusion * 100)}
              max={100}
              suffix="%"
              color={agg.avg_confusion < 0.3 ? 'emerald' : agg.avg_confusion < 0.6 ? 'amber' : 'red'}
              icon={HelpCircle}
            />
          </div>
        )}

        {/* Energy Breakdown */}
        {agg?.energy_breakdown && (
          <div className="p-2 bg-karau-bg/40 rounded-lg border border-white/5" data-testid="energy-breakdown">
            <p className="text-[8px] text-slate-400 uppercase tracking-wider mb-1.5">Room Energy</p>
            <div className="flex items-center gap-2">
              {Object.entries(agg.energy_breakdown).map(([energy, count]) => {
                const Icon = ENERGY_ICONS[energy] || Activity;
                return (
                  <div key={energy} className="flex items-center gap-1">
                    <Icon className={`w-3 h-3 ${ENERGY_COLORS[energy] || 'text-slate-400'}`} />
                    <span className="text-[8px] text-white">{energy}</span>
                    <Badge className="text-[7px] bg-white/5 text-slate-300">{count}</Badge>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* AI Recommendations */}
        {recs.length > 0 && (
          <div className="space-y-1" data-testid="sentiment-recommendations">
            <p className="text-[8px] text-cyan-400 uppercase tracking-wider">AI Recommendations</p>
            {recs.map((rec, i) => (
              <div key={i} className={`p-1.5 rounded-lg border text-[9px] ${
                rec.priority === 'high'
                  ? 'bg-red-500/5 border-red-500/15 text-red-300'
                  : 'bg-amber-500/5 border-amber-500/15 text-amber-300'
              }`} data-testid={`recommendation-${i}`}>
                <div className="flex items-start gap-1.5">
                  <AlertCircle className="w-3 h-3 shrink-0 mt-0.5" />
                  <span>{rec.message}</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Per-Participant Heatmap */}
        {participants.length > 0 && (
          <div data-testid="participant-heatmap">
            <p className="text-[8px] text-slate-400 uppercase tracking-wider mb-1">Participant Heatmap</p>
            <div className="space-y-0.5">
              {participants.map(p => {
                const EnergyIcon = ENERGY_ICONS[p.energy] || Activity;
                return (
                  <div key={p.user_id} className="flex items-center gap-1.5 p-1 rounded bg-karau-bg/30" data-testid={`participant-${p.user_id}`}>
                    <span className="text-[8px] text-white truncate w-16">{p.user_name}</span>
                    {/* Attention bar */}
                    <div className="flex-1 h-1.5 bg-white/5 rounded-full overflow-hidden" title={`Attention: ${p.attention_score}/10`}>
                      <div className="h-full rounded-full transition-all duration-500" style={{
                        width: `${(p.attention_score / 10) * 100}%`,
                        backgroundColor: p.attention_score >= 6 ? '#34d399' : p.attention_score >= 4 ? '#fbbf24' : '#f87171'
                      }} />
                    </div>
                    <EnergyIcon className={`w-2.5 h-2.5 ${ENERGY_COLORS[p.energy] || 'text-slate-400'}`} />
                    {p.confusion_level > 0.5 && <HelpCircle className="w-2.5 h-2.5 text-red-400" title="Confused" />}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function MetricCard({ label, value, max, suffix = '', color, icon: Icon }) {
  const colorMap = {
    emerald: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/15',
    amber: 'text-amber-400 bg-amber-500/10 border-amber-500/15',
    red: 'text-red-400 bg-red-500/10 border-red-500/15',
  };

  return (
    <div className={`p-1.5 rounded-lg border text-center ${colorMap[color] || colorMap.emerald}`}>
      <Icon className="w-3 h-3 mx-auto mb-0.5" />
      <p className="text-sm font-bold">{value}{suffix}</p>
      <p className="text-[7px] opacity-60">{label}</p>
    </div>
  );
}
