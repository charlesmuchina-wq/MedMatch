import { useState, useEffect, useCallback } from 'react';
import { Activity, AlertCircle, TrendingUp, TrendingDown, Zap, Coffee, HelpCircle, BarChart3, Users, Eye } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

const API = process.env.REACT_APP_BACKEND_URL;

const ENERGY_ICONS = { high: Zap, neutral: Activity, low: Coffee };
const ENERGY_COLORS = { high: '#10b981', neutral: '#3b82f6', low: '#f59e0b' };
const ENERGY_LABELS = { high: 'High Energy', neutral: 'Neutral', low: 'Low Energy' };

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

  if (loading) return (
    <div className="flex-1 flex items-center justify-center">
      <div className="text-center">
        <div className="w-8 h-8 rounded-xl bg-cyan-500/10 flex items-center justify-center mx-auto mb-2 animate-pulse">
          <BarChart3 className="w-4 h-4 text-cyan-400" />
        </div>
        <p className="text-[10px] text-slate-500">Analyzing sentiment...</p>
      </div>
    </div>
  );

  const agg = heatmap?.aggregate;
  const recs = heatmap?.recommendations || [];
  const participants = heatmap?.participants || [];

  return (
    <div className="flex-1 flex flex-col overflow-hidden" data-testid="sentiment-dashboard">
      {/* Header */}
      <div className="p-3 border-b border-white/[0.06]">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-cyan-500/20 to-blue-500/10 flex items-center justify-center">
            <BarChart3 className="w-3.5 h-3.5 text-cyan-400" />
          </div>
          <div>
            <h3 className="text-xs font-semibold text-white">Sentiment Dashboard</h3>
            <p className="text-[9px] text-slate-500">Real-time engagement heatmap</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {/* Animated Gauge Cards */}
        {agg && (
          <div className="grid grid-cols-3 gap-2" data-testid="sentiment-metrics">
            <GaugeCard label="Attention" value={agg.avg_attention} max={10} color={agg.avg_attention >= 6 ? '#10b981' : agg.avg_attention >= 4 ? '#f59e0b' : '#ef4444'} icon={Eye} />
            <GaugeCard label="Engagement" value={agg.avg_engagement} max={10} color={agg.avg_engagement >= 6 ? '#10b981' : agg.avg_engagement >= 4 ? '#f59e0b' : '#ef4444'} icon={TrendingUp} />
            <GaugeCard label="Confusion" value={Math.round(agg.avg_confusion * 100)} max={100} suffix="%" color={agg.avg_confusion < 0.3 ? '#10b981' : agg.avg_confusion < 0.6 ? '#f59e0b' : '#ef4444'} icon={HelpCircle} inverted />
          </div>
        )}

        {/* Energy Breakdown - Visual Bar */}
        {agg?.energy_breakdown && (
          <div className="p-3 rounded-xl border border-white/[0.06] bg-gradient-to-b from-white/[0.02] to-transparent" data-testid="energy-breakdown">
            <p className="text-[9px] font-semibold text-slate-400 uppercase tracking-widest mb-2.5">Room Energy</p>
            <div className="flex items-end gap-1 h-12 mb-2">
              {Object.entries(agg.energy_breakdown).map(([energy, count]) => {
                const maxCount = Math.max(...Object.values(agg.energy_breakdown), 1);
                const height = Math.max(12, (count / maxCount) * 100);
                return (
                  <div key={energy} className="flex-1 flex flex-col items-center gap-1">
                    <div className="w-full rounded-t-lg transition-all duration-700 ease-out animate-bar-grow"
                      style={{ height: `${height}%`, backgroundColor: `${ENERGY_COLORS[energy]}20`, borderBottom: `2px solid ${ENERGY_COLORS[energy]}` }} />
                  </div>
                );
              })}
            </div>
            <div className="flex justify-around">
              {Object.entries(agg.energy_breakdown).map(([energy, count]) => {
                const Icon = ENERGY_ICONS[energy] || Activity;
                return (
                  <div key={energy} className="flex items-center gap-1.5">
                    <Icon className="w-3 h-3" style={{ color: ENERGY_COLORS[energy] }} />
                    <span className="text-[9px] text-slate-400">{ENERGY_LABELS[energy]}</span>
                    <span className="text-[9px] font-bold text-white">{count}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* AI Recommendations */}
        {recs.length > 0 && (
          <div className="space-y-1.5" data-testid="sentiment-recommendations">
            <p className="text-[9px] font-semibold text-cyan-400 uppercase tracking-widest">AI Recommendations</p>
            {recs.map((rec, i) => (
              <div key={i} style={{ animationDelay: `${i * 100}ms` }}
                className={`p-2.5 rounded-xl border text-[10px] leading-relaxed animate-slide-up ${
                  rec.priority === 'high'
                    ? 'bg-red-500/[0.04] border-red-500/15 text-red-300'
                    : 'bg-amber-500/[0.04] border-amber-500/15 text-amber-300'
                }`} data-testid={`recommendation-${i}`}>
                <div className="flex items-start gap-2">
                  <div className={`w-5 h-5 rounded-lg flex items-center justify-center shrink-0 mt-0.5 ${
                    rec.priority === 'high' ? 'bg-red-500/10' : 'bg-amber-500/10'
                  }`}>
                    <AlertCircle className="w-3 h-3" />
                  </div>
                  <span>{rec.message}</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Per-Participant Heatmap */}
        {participants.length > 0 && (
          <div data-testid="participant-heatmap">
            <div className="flex items-center gap-2 mb-2">
              <Users className="w-3 h-3 text-slate-500" />
              <p className="text-[9px] font-semibold text-slate-400 uppercase tracking-widest">Participant Heatmap</p>
              <span className="text-[9px] text-slate-600">{participants.length}</span>
            </div>
            <div className="space-y-1">
              {participants.map((p, i) => {
                const EnergyIcon = ENERGY_ICONS[p.energy] || Activity;
                const attColor = p.attention_score >= 6 ? '#10b981' : p.attention_score >= 4 ? '#fbbf24' : '#f87171';
                return (
                  <div key={p.user_id} className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-white/[0.02] transition-colors"
                    style={{ animationDelay: `${i * 50}ms` }}
                    data-testid={`participant-${p.user_id}`}>
                    {/* Avatar */}
                    <div className="w-6 h-6 rounded-lg flex items-center justify-center text-[8px] font-bold text-white shrink-0"
                      style={{ backgroundColor: `${attColor}20`, color: attColor }}>
                      {(p.user_name || '?')[0]}
                    </div>
                    <span className="text-[9px] text-white truncate w-14">{p.user_name}</span>
                    {/* Attention bar with animated fill */}
                    <div className="flex-1 h-2 bg-white/[0.04] rounded-full overflow-hidden">
                      <div className="h-full rounded-full transition-all duration-700 ease-out"
                        style={{ width: `${(p.attention_score / 10) * 100}%`, backgroundColor: attColor }} />
                    </div>
                    <EnergyIcon className="w-3 h-3 shrink-0" style={{ color: ENERGY_COLORS[p.energy] || '#94a3b8' }} />
                    {p.confusion_level > 0.5 && (
                      <div className="relative">
                        <HelpCircle className="w-3 h-3 text-red-400" />
                        <span className="absolute inset-0 rounded-full animate-pulse-ring" style={{ borderColor: '#f87171', border: '1px solid' }} />
                      </div>
                    )}
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

function GaugeCard({ label, value, max, suffix = '', color, icon: Icon, inverted }) {
  const pct = Math.min((value / max) * 100, 100);
  const circumference = 2 * Math.PI * 18;
  const dashArray = `${(pct / 100) * circumference * 0.75}, ${circumference}`;

  return (
    <div className="p-2 rounded-xl border border-white/[0.06] bg-gradient-to-b from-white/[0.02] to-transparent text-center">
      <div className="relative w-12 h-12 mx-auto mb-1">
        <svg viewBox="0 0 40 40" className="w-12 h-12 -rotate-[135deg]">
          <circle cx="20" cy="20" r="18" fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="3" strokeDasharray={`${circumference * 0.75}, ${circumference}`} strokeLinecap="round" />
          <circle cx="20" cy="20" r="18" fill="none" stroke={color} strokeWidth="3" strokeDasharray={dashArray} strokeLinecap="round" className="animate-gauge-fill" style={{ transition: 'stroke-dasharray 0.8s ease-out' }} />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-sm font-bold text-white">{value}{suffix}</span>
        </div>
      </div>
      <div className="flex items-center justify-center gap-1">
        <Icon className="w-2.5 h-2.5" style={{ color }} />
        <p className="text-[8px] text-slate-500">{label}</p>
      </div>
    </div>
  );
}
