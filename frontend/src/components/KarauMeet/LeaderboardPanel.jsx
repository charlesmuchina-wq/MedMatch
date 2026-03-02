import { useState, useEffect, useRef } from 'react';
import { Badge } from '@/components/ui/badge';
import { Trophy, Medal, Star, TrendingUp, MessageCircleQuestion, Flame, Clock, Crown, Zap } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const RANK_STYLES = [
  { gradient: 'from-amber-500/15 to-yellow-500/5', border: 'border-amber-500/25', text: 'text-amber-400', icon: Crown, glow: 'shadow-amber-500/10' },
  { gradient: 'from-slate-400/10 to-slate-500/5', border: 'border-slate-400/15', text: 'text-slate-300', icon: Medal, glow: '' },
  { gradient: 'from-orange-500/10 to-amber-500/5', border: 'border-orange-500/15', text: 'text-orange-400', icon: Medal, glow: '' },
];

export function LeaderboardPanel({ webinarId }) {
  const [leaderboard, setLeaderboard] = useState([]);
  const [summary, setSummary] = useState(null);
  const pollRef = useRef(null);

  useEffect(() => {
    if (!webinarId) return;
    const fetchData = async () => {
      try {
        const [lbRes, sumRes] = await Promise.all([
          fetch(`${API}/api/karau/webinar/${webinarId}/leaderboard`),
          fetch(`${API}/api/karau/webinar/${webinarId}/reactions/summary`)
        ]);
        if (lbRes.ok) setLeaderboard((await lbRes.json()).leaderboard || []);
        if (sumRes.ok) setSummary(await sumRes.json());
      } catch {}
    };
    fetchData();
    pollRef.current = setInterval(fetchData, 5000);
    return () => clearInterval(pollRef.current);
  }, [webinarId]);

  return (
    <div className="flex-1 flex flex-col overflow-hidden" data-testid="leaderboard-panel">
      {/* Header */}
      <div className="p-3 border-b border-white/[0.06]">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-amber-500/20 to-yellow-500/10 flex items-center justify-center">
            <Trophy className="w-3.5 h-3.5 text-amber-400" />
          </div>
          <div>
            <h3 className="text-xs font-semibold text-white">Leaderboard</h3>
            <p className="text-[9px] text-slate-500">{leaderboard.length} participants</p>
          </div>
        </div>
      </div>

      {/* Reaction Summary */}
      {summary && summary.total_reactions > 0 && (
        <div className="px-3 py-2.5 border-b border-white/[0.06]" data-testid="reaction-summary">
          <div className="flex items-center gap-1.5 mb-2">
            <Zap className="w-3 h-3 text-amber-400" />
            <p className="text-[9px] font-semibold text-slate-400 uppercase tracking-widest">Reactions</p>
            <span className="text-[9px] text-slate-600">{summary.total_reactions}</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {Object.entries(summary.summary || {}).map(([key, val]) => (
              <Badge key={key} className="bg-white/[0.04] text-white/80 border-white/[0.06] text-[10px] gap-1 px-2 py-0.5 rounded-lg">
                {val.emoji} <span className="font-semibold">{val.count}</span>
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* Entries */}
      <div className="flex-1 overflow-y-auto p-3 space-y-1.5">
        {leaderboard.length === 0 ? (
          <div className="text-center py-8">
            <div className="w-12 h-12 rounded-2xl bg-amber-500/10 flex items-center justify-center mx-auto mb-3">
              <Star className="w-6 h-6 text-amber-500/30" />
            </div>
            <p className="text-xs text-slate-500">No activity yet</p>
            <p className="text-[10px] text-slate-600 mt-0.5">Participate to climb!</p>
          </div>
        ) : (
          leaderboard.map((entry, idx) => {
            const style = RANK_STYLES[idx] || { gradient: 'from-white/[0.02] to-transparent', border: 'border-white/[0.04]', text: 'text-slate-400', icon: Star, glow: '' };
            const RankIcon = style.icon;
            return (
              <div key={entry.user_id}
                className={`flex items-center gap-2.5 p-2.5 rounded-xl border bg-gradient-to-r ${style.gradient} ${style.border} ${style.glow} transition-all duration-300 animate-slide-up`}
                style={{ animationDelay: `${idx * 60}ms` }}
                data-testid={`leaderboard-entry-${idx}`}>
                {/* Rank badge */}
                <div className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 ${idx < 3 ? 'bg-black/20' : 'bg-white/[0.04]'}`}>
                  {idx < 3 ? (
                    <RankIcon className={`w-3.5 h-3.5 ${style.text}`} />
                  ) : (
                    <span className="text-[10px] text-slate-500 font-bold">#{entry.rank}</span>
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <p className="text-[11px] text-white font-medium truncate">{entry.user_name}</p>
                  <div className="flex items-center gap-2 mt-0.5">
                    {entry.reactions > 0 && (
                      <span className="text-[8px] text-rose-400 flex items-center gap-0.5">
                        <Flame className="w-2.5 h-2.5" />{entry.reactions}
                      </span>
                    )}
                    {entry.questions > 0 && (
                      <span className="text-[8px] text-blue-400 flex items-center gap-0.5">
                        <MessageCircleQuestion className="w-2.5 h-2.5" />{entry.questions}
                      </span>
                    )}
                    {entry.speaking_time > 0 && (
                      <span className="text-[8px] text-emerald-400 flex items-center gap-0.5">
                        <Clock className="w-2.5 h-2.5" />{entry.speaking_time}s
                      </span>
                    )}
                  </div>
                </div>

                <div className="shrink-0 text-right">
                  <div className={`text-sm font-bold tabular-nums ${style.text}`}>{entry.total_score}</div>
                  <div className="text-[7px] text-slate-600 uppercase tracking-wider">pts</div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

export default LeaderboardPanel;
