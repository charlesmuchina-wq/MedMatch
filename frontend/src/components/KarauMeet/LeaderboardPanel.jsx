import { useState, useEffect, useRef } from 'react';
import { Badge } from '@/components/ui/badge';
import { Trophy, Medal, Star, TrendingUp, MessageCircleQuestion, Flame, Clock } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const RANK_STYLES = [
  { bg: 'bg-amber-500/15', border: 'border-amber-500/30', text: 'text-amber-400', icon: Trophy },
  { bg: 'bg-slate-400/10', border: 'border-slate-400/20', text: 'text-slate-300', icon: Medal },
  { bg: 'bg-orange-500/10', border: 'border-orange-500/20', text: 'text-orange-400', icon: Medal },
];

/**
 * Real-time participation leaderboard panel.
 */
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
        if (lbRes.ok) {
          const lbData = await lbRes.json();
          setLeaderboard(lbData.leaderboard || []);
        }
        if (sumRes.ok) {
          const sumData = await sumRes.json();
          setSummary(sumData);
        }
      } catch {}
    };
    fetchData();
    pollRef.current = setInterval(fetchData, 5000);
    return () => clearInterval(pollRef.current);
  }, [webinarId]);

  return (
    <div className="flex-1 flex flex-col overflow-hidden" data-testid="leaderboard-panel">
      <div className="p-2.5 border-b border-white/5">
        <h3 className="text-xs font-semibold text-white flex items-center gap-1.5">
          <Trophy className="w-3.5 h-3.5 text-amber-400" />
          Leaderboard
        </h3>
      </div>

      {/* Reaction Summary */}
      {summary && summary.total_reactions > 0 && (
        <div className="px-2.5 py-2 border-b border-white/5" data-testid="reaction-summary">
          <p className="text-[9px] text-slate-400 uppercase tracking-wider mb-1.5">Reactions</p>
          <div className="flex flex-wrap gap-1">
            {Object.entries(summary.summary || {}).map(([key, val]) => (
              <Badge key={key} className="bg-white/5 text-white/80 border-white/10 text-[9px] gap-0.5">
                {val.emoji} {val.count}
              </Badge>
            ))}
          </div>
          <p className="text-[8px] text-slate-500 mt-1">{summary.total_reactions} total reactions</p>
        </div>
      )}

      {/* Leaderboard Entries */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {leaderboard.length === 0 ? (
          <div className="text-center py-8">
            <Star className="w-8 h-8 text-slate-600 mx-auto mb-2" />
            <p className="text-[10px] text-slate-500">No activity yet</p>
            <p className="text-[8px] text-slate-600 mt-0.5">Participate to climb the leaderboard!</p>
          </div>
        ) : (
          leaderboard.map((entry, idx) => {
            const style = RANK_STYLES[idx] || { bg: 'bg-white/5', border: 'border-white/5', text: 'text-slate-400', icon: Star };
            const RankIcon = style.icon;
            return (
              <div
                key={entry.user_id}
                className={`flex items-center gap-2 p-2 rounded-lg border transition-all ${style.bg} ${style.border}`}
                data-testid={`leaderboard-entry-${idx}`}
              >
                {/* Rank */}
                <div className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 ${idx < 3 ? style.bg : 'bg-white/5'}`}>
                  {idx < 3 ? (
                    <RankIcon className={`w-3 h-3 ${style.text}`} />
                  ) : (
                    <span className="text-[9px] text-slate-400 font-bold">#{entry.rank}</span>
                  )}
                </div>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <p className="text-[10px] text-white font-medium truncate">{entry.user_name}</p>
                  <div className="flex items-center gap-2 mt-0.5">
                    {entry.reactions > 0 && (
                      <span className="text-[8px] text-rose-400 flex items-center gap-0.5">
                        <Flame className="w-2 h-2" />{entry.reactions}
                      </span>
                    )}
                    {entry.questions > 0 && (
                      <span className="text-[8px] text-blue-400 flex items-center gap-0.5">
                        <MessageCircleQuestion className="w-2 h-2" />{entry.questions}
                      </span>
                    )}
                    {entry.speaking_time > 0 && (
                      <span className="text-[8px] text-emerald-400 flex items-center gap-0.5">
                        <Clock className="w-2 h-2" />{entry.speaking_time}s
                      </span>
                    )}
                  </div>
                </div>

                {/* Score */}
                <div className="shrink-0 text-right">
                  <div className={`text-xs font-bold ${style.text}`}>{entry.total_score}</div>
                  <div className="text-[7px] text-slate-500">pts</div>
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
