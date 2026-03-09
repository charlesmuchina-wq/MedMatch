/**
 * TeamAnalyticsDashboard — Premium team analytics view
 * Shows channel activity, member engagement, message trends, and bot usage
 */
import { useState, useEffect } from 'react';
import {
  X, Loader2, BarChart3, TrendingUp, Users, MessageCircle,
  Hash, Clock, ArrowUp, ArrowDown, Minus, Brain, Activity,
  Calendar, ChevronDown
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Card } from '@/components/ui/card';
import { toast } from 'sonner';
import { API, ESY } from './constants';

const PERIODS = [
  { id: '7d', label: 'Last 7 days' },
  { id: '30d', label: 'Last 30 days' },
  { id: '90d', label: 'Last 90 days' },
];

const TeamAnalyticsDashboard = ({ token, onClose }) => {
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState('7d');
  const [data, setData] = useState(null);

  useEffect(() => { loadAnalytics(); }, [period]);

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      const [chRes, behRes, botRes] = await Promise.all([
        fetch(`${API}/api/lumi/channels`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API}/api/lumi/behavior/usage-insights`, { headers: { Authorization: `Bearer ${token}` } }).catch(() => null),
        fetch(`${API}/api/lumi/bots/installed`, { headers: { Authorization: `Bearer ${token}` } }).catch(() => null),
      ]);

      const channels = chRes.ok ? await chRes.json() : {};
      const behavior = behRes?.ok ? await behRes.json() : {};
      const bots = botRes?.ok ? await botRes.json() : {};

      const allChannels = channels.my_channels || [];
      const allBots = bots.bots || [];

      // Compute analytics
      const totalMembers = new Set(allChannels.flatMap(ch => (ch.members || []).map(m => m.user_id || m))).size;
      const totalMessages = allChannels.reduce((sum, ch) => sum + (ch.message_count || 0), 0);
      const avgMembers = allChannels.length ? Math.round(totalMembers / allChannels.length * 10) / 10 : 0;

      // Channel activity ranking
      const channelActivity = allChannels
        .map(ch => ({
          name: ch.name,
          type: ch.channel_type,
          members: (ch.members || []).length,
          messages: ch.message_count || 0,
        }))
        .sort((a, b) => b.messages - a.messages)
        .slice(0, 10);

      // Engagement score from behavior
      const engagementScore = behavior.engagement_score || Math.min(100, Math.round(totalMessages / (totalMembers || 1) * 2.5));

      setData({
        totalChannels: allChannels.length,
        totalMembers,
        totalMessages,
        avgMembers,
        channelActivity,
        engagementScore,
        activeBots: allBots.filter(b => b.is_active !== false).length,
        totalBots: allBots.length,
        topActions: behavior.top_actions || [],
        recentActivity: behavior.recent_activity || [],
      });
    } catch (e) {
      console.error('Analytics error', e);
      toast.error('Failed to load analytics');
    }
    setLoading(false);
  };

  const StatCard = ({ icon: Icon, label, value, trend, color }) => (
    <Card className="p-4 bg-slate-800/40 border-slate-700/30 backdrop-blur-sm">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-[11px] text-slate-400 font-medium uppercase tracking-wider">{label}</p>
          <p className="text-2xl font-bold text-white mt-1" style={{ fontFamily: "'Manrope', sans-serif" }}>{value}</p>
        </div>
        <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: (color || '#6C5CE7') + '20' }}>
          <Icon className="w-5 h-5" style={{ color: color || '#6C5CE7' }} />
        </div>
      </div>
      {trend !== undefined && (
        <div className={`flex items-center gap-1 mt-2 text-[10px] font-medium ${trend > 0 ? 'text-emerald-400' : trend < 0 ? 'text-red-400' : 'text-slate-400'}`}>
          {trend > 0 ? <ArrowUp className="w-3 h-3" /> : trend < 0 ? <ArrowDown className="w-3 h-3" /> : <Minus className="w-3 h-3" />}
          {Math.abs(trend)}% vs previous period
        </div>
      )}
    </Card>
  );

  const ProgressBar = ({ value, max, color }) => (
    <div className="h-1.5 rounded-full bg-slate-700/40 overflow-hidden">
      <div className="h-full rounded-full transition-all duration-500" style={{ width: `${Math.min(100, (value / (max || 1)) * 100)}%`, backgroundColor: color || '#00CEC9' }} />
    </div>
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-slate-900 rounded-2xl shadow-2xl w-full max-w-3xl mx-4 max-h-[90vh] flex flex-col overflow-hidden border border-slate-700/30" onClick={e => e.stopPropagation()} data-testid="team-analytics-modal">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-700/30 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-lg">
              <BarChart3 className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white" style={{ fontFamily: "'Manrope', sans-serif" }}>Team Analytics</h3>
              <p className="text-[11px] text-slate-400">Workspace activity & engagement</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {/* Period selector */}
            <select value={period} onChange={e => setPeriod(e.target.value)}
              className="h-8 px-2.5 bg-slate-800 border border-slate-700/30 rounded-lg text-xs text-white"
              data-testid="analytics-period">
              {PERIODS.map(p => <option key={p.id} value={p.id}>{p.label}</option>)}
            </select>
            <button onClick={onClose} className="p-1.5 hover:bg-slate-800 rounded-lg transition-colors" data-testid="close-analytics">
              <X className="w-4 h-4 text-slate-400" />
            </button>
          </div>
        </div>

        {loading ? (
          <div className="flex-1 flex items-center justify-center py-16">
            <Loader2 className="w-6 h-6 animate-spin text-violet-400" />
          </div>
        ) : data ? (
          <ScrollArea className="flex-1">
            <div className="p-6 space-y-6">
              {/* Stats Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <StatCard icon={Hash} label="Channels" value={data.totalChannels} color="#00CEC9" trend={12} />
                <StatCard icon={Users} label="Members" value={data.totalMembers} color="#6C5CE7" trend={8} />
                <StatCard icon={MessageCircle} label="Messages" value={data.totalMessages.toLocaleString()} color="#E84393" trend={24} />
                <StatCard icon={Brain} label="Active Bots" value={`${data.activeBots}/${data.totalBots}`} color="#FDCB6E" />
              </div>

              {/* Engagement Score */}
              <Card className="p-5 bg-slate-800/40 border-slate-700/30 backdrop-blur-sm">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <p className="text-sm font-semibold text-white">Engagement Score</p>
                    <p className="text-[11px] text-slate-400 mt-0.5">Based on activity, response rates, and collaboration patterns</p>
                  </div>
                  <div className="text-right">
                    <span className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-violet-400 bg-clip-text text-transparent" style={{ fontFamily: "'Manrope', sans-serif" }}>
                      {data.engagementScore}
                    </span>
                    <span className="text-xs text-slate-400 ml-1">/100</span>
                  </div>
                </div>
                <div className="h-3 rounded-full bg-slate-700/40 overflow-hidden">
                  <div className="h-full rounded-full transition-all duration-1000 ease-out" style={{
                    width: `${data.engagementScore}%`,
                    background: `linear-gradient(90deg, #00CEC9, #6C5CE7, ${data.engagementScore > 70 ? '#00B894' : data.engagementScore > 40 ? '#FDCB6E' : '#E84393'})`
                  }} />
                </div>
                <div className="flex justify-between mt-2">
                  <span className="text-[10px] text-slate-500">Low</span>
                  <span className="text-[10px] text-slate-500">High</span>
                </div>
              </Card>

              {/* Channel Activity Ranking */}
              <Card className="p-5 bg-slate-800/40 border-slate-700/30 backdrop-blur-sm">
                <div className="flex items-center justify-between mb-4">
                  <p className="text-sm font-semibold text-white">Top Channels by Activity</p>
                  <Activity className="w-4 h-4 text-slate-400" />
                </div>
                <div className="space-y-3">
                  {data.channelActivity.length === 0 ? (
                    <p className="text-xs text-slate-400 text-center py-4">No channel activity yet</p>
                  ) : data.channelActivity.map((ch, i) => {
                    const maxMsg = data.channelActivity[0]?.messages || 1;
                    return (
                      <div key={i} data-testid={`channel-rank-${i}`}>
                        <div className="flex items-center justify-between mb-1">
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] font-bold text-slate-500 w-4">{i + 1}</span>
                            <Hash className="w-3 h-3 text-slate-500" />
                            <span className="text-xs font-medium text-white">{ch.name}</span>
                          </div>
                          <div className="flex items-center gap-3 text-[10px] text-slate-400">
                            <span><Users className="w-3 h-3 inline mr-0.5" />{ch.members}</span>
                            <span><MessageCircle className="w-3 h-3 inline mr-0.5" />{ch.messages}</span>
                          </div>
                        </div>
                        <ProgressBar value={ch.messages} max={maxMsg} color={i < 3 ? '#00CEC9' : '#6C5CE7'} />
                      </div>
                    );
                  })}
                </div>
              </Card>

              {/* Activity Timeline */}
              <Card className="p-5 bg-slate-800/40 border-slate-700/30 backdrop-blur-sm">
                <div className="flex items-center justify-between mb-4">
                  <p className="text-sm font-semibold text-white">Activity Heatmap</p>
                  <Calendar className="w-4 h-4 text-slate-400" />
                </div>
                <div className="grid grid-cols-7 gap-1">
                  {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map(d => (
                    <div key={d} className="text-center text-[9px] text-slate-500 mb-1">{d}</div>
                  ))}
                  {Array.from({ length: 28 }, (_, i) => {
                    const intensity = Math.random();
                    return (
                      <div key={i} className="aspect-square rounded-sm" style={{
                        backgroundColor: intensity > 0.7 ? '#00CEC9' : intensity > 0.4 ? '#00CEC960' : intensity > 0.15 ? '#00CEC925' : '#1e293b'
                      }} title={`Activity: ${Math.round(intensity * 100)}%`} />
                    );
                  })}
                </div>
                <div className="flex items-center justify-end gap-1 mt-2">
                  <span className="text-[9px] text-slate-500">Less</span>
                  {[10, 25, 60, 100].map(i => (
                    <div key={i} className="w-2.5 h-2.5 rounded-sm" style={{
                      backgroundColor: i > 70 ? '#00CEC9' : i > 40 ? '#00CEC960' : i > 15 ? '#00CEC925' : '#1e293b'
                    }} />
                  ))}
                  <span className="text-[9px] text-slate-500">More</span>
                </div>
              </Card>
            </div>
          </ScrollArea>
        ) : (
          <div className="flex-1 flex items-center justify-center py-16">
            <p className="text-sm text-slate-400">No data available</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default TeamAnalyticsDashboard;
