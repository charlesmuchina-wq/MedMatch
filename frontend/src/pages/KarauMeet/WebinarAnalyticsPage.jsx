import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft, Users, MessageCircleQuestion, TrendingUp,
  Loader2, CheckCircle2, XCircle, Clock, Building2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useTranslation } from '@/utils/i18n';

const API = process.env.REACT_APP_BACKEND_URL;

const WebinarAnalyticsPage = ({ webinarId, onClose }) => {
  const { t } = useTranslation();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (webinarId) fetchAnalytics();
  }, [webinarId]);

  const fetchAnalytics = async () => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/webinar/${webinarId}/analytics`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) setAnalytics(await res.json());
    } catch (e) { console.error('Analytics fetch error:', e); }
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 className="w-6 h-6 text-purple-400 animate-spin" />
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="text-center py-16 text-karau-muted">
        <p>{t("karauMeet.analyticsNotAvailable") || "Analytics not available"}</p>
      </div>
    );
  }

  const { funnel, qa_stats, engagement, org_breakdown, registration_timeline } = analytics;

  return (
    <div className="space-y-4" data-testid="webinar-analytics-panel">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" onClick={onClose}
          className="h-8 w-8 p-0 text-slate-400 hover:text-white" data-testid="analytics-back-btn">
          <ArrowLeft className="w-4 h-4" />
        </Button>
        <div>
          <h2 className="text-base font-bold text-white">{analytics.title}</h2>
          <p className="text-[10px] text-karau-muted">
            {analytics.status === 'live' ? 'Live Now' : analytics.status === 'ended' ? 'Ended' : 'Scheduled'}
            {analytics.started_at && ` · ${new Date(analytics.started_at).toLocaleDateString()}`}
          </p>
        </div>
      </div>

      {/* Engagement Score */}
      <div className="bg-gradient-to-br from-purple-500/10 via-karau-card/40 to-violet-500/10 rounded-xl border border-purple-500/15 p-4" data-testid="engagement-score-card">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium text-karau-muted">{t("karauMeet.engagementScore") || "Engagement Score"}</span>
          <TrendingUp className="w-4 h-4 text-purple-400" />
        </div>
        <div className="flex items-end gap-3">
          <span className="text-4xl font-black text-white">{engagement.score}</span>
          <span className="text-lg text-karau-muted mb-1">/100</span>
        </div>
        <div className="w-full h-2 bg-white/5 rounded-full mt-2 overflow-hidden">
          <div className="h-full rounded-full transition-all duration-700"
            style={{
              width: `${engagement.score}%`,
              background: engagement.score >= 70 ? 'linear-gradient(90deg, #10b981, #34d399)'
                : engagement.score >= 40 ? 'linear-gradient(90deg, #eab308, #facc15)'
                  : 'linear-gradient(90deg, #ef4444, #f87171)'
            }} />
        </div>
        <div className="flex justify-between mt-2 text-[10px] text-karau-muted">
          <span>{t("karauMeet.peakAttendees") || "Peak"}: {engagement.peak_attendees}</span>
          {engagement.avg_watch_time_minutes > 0 && <span>Avg Watch: {engagement.avg_watch_time_minutes}m</span>}
        </div>
      </div>

      {/* Registration & Attendance Funnel */}
      <div className="bg-karau-card/40 rounded-xl border border-white/5 p-4" data-testid="funnel-card">
        <div className="flex items-center gap-2 mb-3">
          <Users className="w-4 h-4 text-emerald-400" />
          <span className="text-xs font-semibold text-white">{t("karauMeet.attendanceFunnel") || "Attendance Funnel"}</span>
        </div>
        
        {/* Funnel visualization */}
        <div className="space-y-2.5">
          <FunnelRow
            label={t("karauMeet.registered") || "Registered"}
            value={funnel.total_registrations}
            max={analytics.max_attendees}
            color="bg-purple-500"
            icon={<Users className="w-3 h-3" />}
          />
          <FunnelRow
            label={t("karauMeet.attended") || "Attended"}
            value={funnel.attended}
            max={funnel.total_registrations || 1}
            color="bg-emerald-500"
            icon={<CheckCircle2 className="w-3 h-3" />}
            percentage={funnel.attendance_rate}
          />
          <FunnelRow
            label={t("karauMeet.missed") || "Missed"}
            value={funnel.missed}
            max={funnel.total_registrations || 1}
            color="bg-red-500"
            icon={<XCircle className="w-3 h-3" />}
            percentage={funnel.drop_off_rate}
          />
        </div>
      </div>

      {/* Q&A Stats */}
      <div className="bg-karau-card/40 rounded-xl border border-white/5 p-4" data-testid="qa-stats-card">
        <div className="flex items-center gap-2 mb-3">
          <MessageCircleQuestion className="w-4 h-4 text-blue-400" />
          <span className="text-xs font-semibold text-white">{t("karauMeet.qaStatistics") || "Q&A Statistics"}</span>
        </div>
        
        <div className="grid grid-cols-2 gap-2 mb-3">
          <div className="bg-karau-bg/40 rounded-lg p-2.5">
            <p className="text-lg font-bold text-white">{qa_stats.total_questions}</p>
            <p className="text-[10px] text-karau-muted">{t("karauMeet.totalQuestions") || "Total Questions"}</p>
          </div>
          <div className="bg-karau-bg/40 rounded-lg p-2.5">
            <p className="text-lg font-bold text-emerald-400">{qa_stats.answer_rate}%</p>
            <p className="text-[10px] text-karau-muted">{t("karauMeet.answerRate") || "Answer Rate"}</p>
          </div>
        </div>

        <div className="flex items-center gap-3 text-[10px]">
          <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/15">
            <CheckCircle2 className="w-2.5 h-2.5 mr-0.5" />{qa_stats.answered} answered
          </Badge>
          <Badge className="bg-amber-500/10 text-amber-400 border-amber-500/15">
            <Clock className="w-2.5 h-2.5 mr-0.5" />{qa_stats.pending} pending
          </Badge>
          {qa_stats.anonymous > 0 && (
            <Badge className="bg-slate-500/10 text-slate-400 border-slate-500/15">
              {qa_stats.anonymous} anonymous
            </Badge>
          )}
        </div>

        {/* Top questions */}
        {qa_stats.top_questions && qa_stats.top_questions.length > 0 && (
          <div className="mt-3 pt-2 border-t border-white/5">
            <p className="text-[10px] text-karau-muted font-medium mb-1.5">{t("karauMeet.topQuestions") || "Top Questions"}</p>
            {qa_stats.top_questions.slice(0, 3).map((q, i) => (
              <div key={i} className="flex items-start gap-2 py-1">
                <span className="text-[9px] text-purple-400 font-bold shrink-0 mt-0.5">{q.upvotes}</span>
                <p className="text-[10px] text-slate-300 leading-tight line-clamp-2">{q.question}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Organization Breakdown */}
      {org_breakdown && org_breakdown.length > 0 && (
        <div className="bg-karau-card/40 rounded-xl border border-white/5 p-4" data-testid="org-breakdown-card">
          <div className="flex items-center gap-2 mb-3">
            <Building2 className="w-4 h-4 text-violet-400" />
            <span className="text-xs font-semibold text-white">{t("karauMeet.orgBreakdown") || "Organization Breakdown"}</span>
          </div>
          <div className="space-y-1.5">
            {org_breakdown.map((o, i) => (
              <div key={i} className="flex items-center justify-between">
                <span className="text-[11px] text-slate-300 truncate flex-1 mr-2">{o.org}</span>
                <div className="flex items-center gap-2">
                  <div className="w-20 h-1.5 bg-white/5 rounded-full overflow-hidden">
                    <div className="h-full bg-violet-500/60 rounded-full"
                      style={{ width: `${Math.min((o.count / (funnel.total_registrations || 1)) * 100, 100)}%` }} />
                  </div>
                  <span className="text-[10px] text-karau-muted w-6 text-right">{o.count}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Registration Timeline */}
      {registration_timeline && registration_timeline.length > 1 && (
        <div className="bg-karau-card/40 rounded-xl border border-white/5 p-4" data-testid="reg-timeline-card">
          <p className="text-xs font-semibold text-white mb-3">{t("karauMeet.registrationTimeline") || "Registration Timeline"}</p>
          <div className="flex items-end gap-1 h-16">
            {registration_timeline.map((d, i) => {
              const maxCount = Math.max(...registration_timeline.map(x => x.count));
              const height = (d.count / maxCount) * 100;
              return (
                <div key={i} className="flex-1 flex flex-col items-center gap-0.5">
                  <span className="text-[8px] text-karau-muted">{d.count}</span>
                  <div className="w-full bg-purple-500/40 rounded-t"
                    style={{ height: `${Math.max(height, 4)}%` }} />
                </div>
              );
            })}
          </div>
          <div className="flex justify-between mt-1">
            <span className="text-[8px] text-karau-muted">{registration_timeline[0]?.date}</span>
            <span className="text-[8px] text-karau-muted">{registration_timeline[registration_timeline.length - 1]?.date}</span>
          </div>
        </div>
      )}
    </div>
  );
};

const FunnelRow = ({ label, value, max, color, icon, percentage }) => {
  const width = max > 0 ? Math.max((value / max) * 100, 2) : 0;
  return (
    <div>
      <div className="flex items-center justify-between mb-0.5">
        <span className="flex items-center gap-1.5 text-[11px] text-slate-300">
          {icon}{label}
        </span>
        <span className="text-[11px] font-semibold text-white">
          {value}{percentage !== undefined && <span className="text-karau-muted font-normal ml-1">({percentage}%)</span>}
        </span>
      </div>
      <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color} transition-all duration-500`}
          style={{ width: `${width}%`, opacity: 0.7 }} />
      </div>
    </div>
  );
};

export default WebinarAnalyticsPage;
