/**
 * KarauAnalyticsRow — Meeting effectiveness, gamification, and quick analytics cards
 * Extracted from KarauMeetDashboard.jsx
 */
import { Video, Clock, Trophy, Flame, BarChart3, Target } from 'lucide-react';
import { useTranslation } from '@/utils/i18n';

const KarauAnalyticsRow = ({ effectiveness, gamification, leaderboard, showLeaderboard, setShowLeaderboard, user }) => {
  const { t } = useTranslation();

  if (!effectiveness && !gamification) return null;

  return (
    <div className="grid grid-cols-12 gap-5">
      {effectiveness && (
        <div className="col-span-12 md:col-span-4" data-testid="effectiveness-card">
          <div className="rounded-2xl bg-white/[0.03] border border-white/[0.06] p-5 h-full">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Target className="w-4 h-4 text-emerald-400" />
                <span className="text-sm font-semibold text-white">{t("karauMeet.effectiveness")}</span>
              </div>
              <span className={`text-[10px] px-2 py-0.5 rounded-full border ${
                effectiveness.engagement_level === 'High' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                effectiveness.engagement_level === 'Medium' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' :
                'bg-slate-500/10 text-slate-400 border-slate-500/20'
              }`}>{effectiveness.engagement_level}</span>
            </div>
            <div className="flex items-end gap-4">
              <div className="relative w-16 h-16">
                <svg viewBox="0 0 36 36" className="w-16 h-16 -rotate-90">
                  <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="3" />
                  <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none"
                    stroke={effectiveness.overall_score >= 75 ? '#10b981' : effectiveness.overall_score >= 50 ? '#f59e0b' : '#6366f1'}
                    strokeWidth="3" strokeDasharray={`${effectiveness.overall_score}, 100`} strokeLinecap="round" />
                </svg>
                <span className="absolute inset-0 flex items-center justify-center text-lg font-bold text-white">{effectiveness.overall_score}</span>
              </div>
              <div className="flex-1 text-xs text-slate-500 space-y-1">
                <p>{t("karauMeet.avgDuration")}: <span className="text-slate-300">{effectiveness.avg_duration_minutes}m</span></p>
                <p>{t("karauMeet.avgParticipants")}: <span className="text-slate-300">{effectiveness.avg_participants}</span></p>
                <p>{t("karauMeet.withNotes")}: <span className="text-slate-300">{effectiveness.meetings_with_notes}/{effectiveness.total_meetings}</span></p>
              </div>
            </div>
          </div>
        </div>
      )}

      {gamification && (
        <div className="col-span-12 md:col-span-4" data-testid="gamification-card">
          <div className="rounded-2xl bg-white/[0.03] border border-white/[0.06] p-5 h-full">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Trophy className="w-4 h-4 text-amber-400" />
                <span className="text-sm font-semibold text-white">{t(`karauMeet.rank${gamification.rank_title}`, { defaultValue: gamification.rank_title })}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-purple-400 font-semibold">{t("karauMeet.level")}{gamification.level}</span>
                {leaderboard && (
                  <button onClick={() => setShowLeaderboard(!showLeaderboard)}
                    className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/15 hover:bg-amber-500/20 transition-colors"
                    data-testid="toggle-leaderboard-btn">#{leaderboard.my_rank}</button>
                )}
              </div>
            </div>
            <div className="flex items-center gap-2 mb-3">
              <div className="flex-1 h-2 bg-white/[0.04] rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-purple-500 to-violet-500 rounded-full transition-all" style={{ width: `${Math.max(5, (gamification.xp / (gamification.xp + gamification.xp_to_next)) * 100)}%` }} />
              </div>
              <span className="text-xs text-slate-500">{gamification.xp} {t("karauMeet.xpLabel")}</span>
            </div>
            <div className="flex items-center gap-4">
              {gamification.streak_days > 0 && <div className="flex items-center gap-1 text-xs"><Flame className="w-3.5 h-3.5 text-orange-400" /><span className="text-orange-300 font-semibold">{gamification.streak_days}d</span></div>}
              <div className="flex items-center gap-1 text-xs"><Video className="w-3.5 h-3.5 text-blue-400" /><span className="text-slate-400">{gamification.total_meetings}</span></div>
              <div className="flex items-center gap-1 text-xs"><Clock className="w-3.5 h-3.5 text-emerald-400" /><span className="text-slate-400">{gamification.total_hours}h</span></div>
            </div>
            {gamification.badges.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-3">
                {gamification.badges.slice(0, 5).map(b => (
                  <span key={b.id} className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/15" title={b.name}>{b.name}</span>
                ))}
              </div>
            )}
            {showLeaderboard && leaderboard && (
              <div className="mt-3 pt-3 border-t border-white/[0.05] space-y-1" data-testid="leaderboard-list">
                {leaderboard.leaderboard.slice(0, 8).map((entry, i) => (
                  <div key={entry.user_id} className={`flex items-center gap-2 px-2 py-1.5 rounded-lg text-xs ${entry.user_id === user?.user_id ? 'bg-purple-500/10 border border-purple-500/20' : ''}`} data-testid={`leaderboard-entry-${i}`}>
                    <span className={`w-4 text-center font-bold ${i === 0 ? 'text-amber-400' : i === 1 ? 'text-slate-300' : i === 2 ? 'text-orange-400' : 'text-slate-500'}`}>{i + 1}</span>
                    <span className="text-slate-300 flex-1 truncate">{entry.name}</span>
                    <span className="text-purple-400 font-semibold">{entry.xp} {t("karauMeet.xpLabel")}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {effectiveness && (
        <div className="col-span-12 md:col-span-4" data-testid="quick-analytics-card">
          <div className="rounded-2xl bg-white/[0.03] border border-white/[0.06] p-5 h-full">
            <div className="flex items-center gap-2 mb-3">
              <BarChart3 className="w-4 h-4 text-blue-400" />
              <span className="text-sm font-semibold text-white">{t("karauMeet.quickAnalytics")}</span>
            </div>
            <div className="space-y-3">
              {[
                { label: t("karauMeet.onTimeRate"), value: effectiveness.on_time_rate, color: 'bg-emerald-500', textColor: 'text-emerald-400' },
                { label: t("karauMeet.aiNotesUsage"), value: effectiveness.total_meetings > 0 ? Math.round(effectiveness.meetings_with_notes / effectiveness.total_meetings * 100) : 0, color: 'bg-violet-500', textColor: 'text-violet-400' },
                { label: t("karauMeet.actionItems"), value: effectiveness.total_meetings > 0 ? Math.round(effectiveness.meetings_with_action_items / effectiveness.total_meetings * 100) : 0, color: 'bg-blue-500', textColor: 'text-blue-400' },
              ].map((item, i) => (
                <div key={i} className="flex items-center justify-between">
                  <span className="text-xs text-slate-500">{item.label}</span>
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-1.5 bg-white/[0.04] rounded-full overflow-hidden">
                      <div className={`h-full ${item.color} rounded-full transition-all`} style={{ width: `${item.value}%` }} />
                    </div>
                    <span className={`text-xs ${item.textColor} font-semibold w-8 text-right`}>{item.value}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default KarauAnalyticsRow;
