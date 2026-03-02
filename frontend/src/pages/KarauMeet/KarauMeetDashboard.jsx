import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import {
  Video, Plus, Clock, Sparkles, Copy,
  Loader2, Users, ArrowRight, Globe, Mic, Bot,
  CalendarClock, TrendingUp, Trophy, Flame, Target, BarChart3,
  Brain, Eye, Wand2, Volume2, Radio, Zap,
  ChevronDown, ChevronUp, Play, ExternalLink
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { useTranslation } from '@/utils/i18n';
import ShareMeetingDialog from '@/components/KarauMeet/ShareMeetingDialog';

const API = process.env.REACT_APP_BACKEND_URL;

const getCountdown = (scheduledTime) => {
  if (!scheduledTime) return null;
  const diff = new Date(scheduledTime) - new Date();
  if (diff <= 0) return 'Now';
  const h = Math.floor(diff / 3600000);
  const m = Math.floor((diff % 3600000) / 60000);
  if (h > 24) return `${Math.floor(h / 24)}d ${h % 24}h`;
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m`;
};

const AI_CAPABILITIES = [
  { icon: Brain, labelKey: 'karauMeet.aiCoach', color: 'text-purple-400', bg: 'bg-purple-500/10' },
  { icon: Eye, labelKey: 'karauMeet.eyeContact', color: 'text-teal-400', bg: 'bg-teal-500/10' },
  { icon: Globe, labelKey: 'karauMeet.liveCaptions', color: 'text-blue-400', bg: 'bg-blue-500/10' },
  { icon: Wand2, labelKey: 'karauMeet.directorMode', color: 'text-amber-400', bg: 'bg-amber-500/10' },
  { icon: Volume2, labelKey: 'karauMeet.spatialAudio', color: 'text-rose-400', bg: 'bg-rose-500/10' },
  { icon: Mic, labelKey: 'karauMeet.noiseCancel', color: 'text-cyan-400', bg: 'bg-cyan-500/10' },
  { icon: Sparkles, labelKey: 'karauMeet.aiNotesShort', color: 'text-violet-400', bg: 'bg-violet-500/10' },
  { icon: Bot, labelKey: 'karauMeet.assistant', color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
];

const KarauMeetDashboard = ({ user }) => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [joinMeetingId, setJoinMeetingId] = useState('');
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newMeetingTitle, setNewMeetingTitle] = useState('');
  const [creating, setCreating] = useState(false);
  const [shareMeeting, setShareMeeting] = useState(null);
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [scheduledTime, setScheduledTime] = useState('');
  const [stats, setStats] = useState({ total_meetings: 0, total_hours: 0, recordings: 0, total_participants: 0, active_meetings: 0, ai_insights: 0 });
  const [activities, setActivities] = useState([]);
  const [upcoming, setUpcoming] = useState([]);
  const [trendingTopics, setTrendingTopics] = useState([]);
  const [, setTick] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [effectiveness, setEffectiveness] = useState(null);
  const [gamification, setGamification] = useState(null);
  const [leaderboard, setLeaderboard] = useState(null);
  const [showLeaderboard, setShowLeaderboard] = useState(false);
  const [expandedSection, setExpandedSection] = useState('');
  const [insights, setInsights] = useState([]);
  const [showAllUpcoming, setShowAllUpcoming] = useState(false);
  const [showAllInsights, setShowAllInsights] = useState(false);

  useEffect(() => {
    fetchMeetings();
    fetchTemplates();
    fetchStats();
    fetchActivityFeed();
    fetchUpcoming();
    fetchTrendingTopics();
    fetchAnalytics();
    fetchInsights();
  }, []);

  useEffect(() => {
    const interval = setInterval(() => setTick(t => t + 1), 60000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const refreshInterval = setInterval(async () => {
      setIsRefreshing(true);
      await Promise.all([fetchStats(), fetchActivityFeed(), fetchUpcoming()]);
      setTimeout(() => setIsRefreshing(false), 800);
    }, 30000);
    return () => clearInterval(refreshInterval);
  }, []);

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API}/api/karau-meet/stats`, { headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) setStats(await res.json());
    } catch (e) { console.error('Stats error:', e); }
  };
  const fetchActivityFeed = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API}/api/karau-meet/activity-feed?limit=12`, { headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) { const data = await res.json(); setActivities(data.activities || []); }
    } catch (e) { console.error('Activity error:', e); }
  };
  const fetchUpcoming = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API}/api/karau-meet/upcoming`, { headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) { const data = await res.json(); setUpcoming(data.upcoming || []); }
    } catch (e) { console.error('Upcoming error:', e); }
  };
  const fetchTrendingTopics = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API}/api/karau-meet/trending-topics`, { headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) { const data = await res.json(); setTrendingTopics(data.topics || []); }
    } catch (e) { console.error('Trending error:', e); }
  };
  const fetchAnalytics = async () => {
    const token = localStorage.getItem('token');
    try {
      const [effRes, gamRes, lbRes] = await Promise.all([
        fetch(`${API}/api/karau/analytics/effectiveness`, { headers: { 'Authorization': `Bearer ${token}` } }),
        fetch(`${API}/api/karau/analytics/gamification`, { headers: { 'Authorization': `Bearer ${token}` } }),
        fetch(`${API}/api/karau/analytics/leaderboard`, { headers: { 'Authorization': `Bearer ${token}` } })
      ]);
      if (effRes.ok) setEffectiveness(await effRes.json());
      if (gamRes.ok) setGamification(await gamRes.json());
      if (lbRes.ok) setLeaderboard(await lbRes.json());
    } catch (e) { console.error('Analytics error:', e); }
  };
  const fetchInsights = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API}/api/karau-meet/meeting-insights`, { headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) { const data = await res.json(); setInsights(data.insights || []); }
    } catch (e) { console.error('Insights error:', e); }
  };
  const fetchTemplates = async () => {
    try {
      const res = await fetch(`${API}/api/karau-features/templates`);
      if (res.ok) { const data = await res.json(); setTemplates(data.templates || []); }
    } catch (e) { console.error(e); }
  };
  const fetchMeetings = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/karau-meet/meetings`, { headers: { 'Authorization': `Bearer ${token}` } });
      if (response.ok) { const data = await response.json(); setMeetings(data.meetings || []); }
    } catch (error) { console.error('Error fetching meetings:', error); }
    setLoading(false);
  };

  const createMeeting = async (isScheduled = false) => {
    setCreating(true);
    try {
      const token = localStorage.getItem('token');
      const body = { title: newMeetingTitle || 'AI KARAU Meeting' };
      if (isScheduled && scheduledTime) body.scheduled_time = new Date(scheduledTime).toISOString();
      const response = await fetch(`${API}/api/karau-meet/meetings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify(body)
      });
      if (response.ok) {
        const data = await response.json();
        if (isScheduled) { toast.success(t("karauMeet.meetingScheduled")); fetchUpcoming(); fetchMeetings(); }
        else { toast.success(t("karauMeet.meetingCreated")); navigate(`/karau-meet/lobby/${data.meeting_id}`); }
      } else { toast.error(t("karauMeet.failedCreate")); }
    } catch { toast.error(t("karauMeet.failedCreate")); }
    setCreating(false);
    setShowCreateDialog(false);
    setScheduledTime('');
  };

  const joinMeeting = () => {
    if (!joinMeetingId.trim()) { toast.error(t("karauMeet.enterMeetingIdError")); return; }
    navigate(`/karau-meet/lobby/${joinMeetingId.toUpperCase()}`);
  };

  const copyMeetingLink = (meetingId) => {
    navigator.clipboard.writeText(`${window.location.origin}/karau-meet/join/${meetingId}`);
    toast.success(t("karauMeet.meetingLinkCopied"));
  };

  const importantActivities = activities.filter(a => a.type === 'ai_insight' || a.type === 'meeting_started');
  const activeMeetings = meetings.filter(m => m.status === 'active');
  const pastMeetings = meetings.filter(m => m.status === 'ended').slice(0, 5);

  const statItems = [
    { label: t('karauMeet.meetings'), value: stats.total_meetings, icon: Video, accent: 'text-blue-400', glow: 'group-hover:shadow-blue-500/20' },
    { label: t('karauMeet.hours'), value: stats.total_hours, icon: Clock, accent: 'text-purple-400', glow: 'group-hover:shadow-purple-500/20' },
    { label: t('karauMeet.aiInsights'), value: stats.ai_insights, icon: Sparkles, accent: 'text-violet-400', glow: 'group-hover:shadow-violet-500/20' },
    { label: t('karauMeet.participants'), value: stats.total_participants, icon: Users, accent: 'text-emerald-400', glow: 'group-hover:shadow-emerald-500/20' }
  ];

  return (
    <div className="h-full flex flex-col overflow-hidden" style={{ fontFamily: "'IBM Plex Sans', sans-serif" }} data-testid="karau-dashboard">
      {/* Header */}
      <header className="flex items-center justify-between px-8 py-5 flex-shrink-0 border-b border-white/[0.04]">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-3" data-testid="dashboard-welcome">
            {t("karauMeet.welcomeBack", { name: user?.name?.split(' ')[0] || 'User' })}
            {isRefreshing && <Loader2 className="w-4 h-4 text-purple-400/50 animate-spin" />}
          </h1>
          <p className="text-slate-500 text-sm mt-0.5">{t("karauMeet.readyForMeeting")}</p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            onClick={() => setShowCreateDialog(true)}
            className="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white rounded-full px-6 h-10 shadow-lg shadow-purple-500/20 transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] font-medium"
            data-testid="btn-new-meeting"
          >
            <Plus className="w-4 h-4 mr-2" /> {t("karauMeet.newMeetingBtn")}
          </Button>
        </div>
      </header>

      {/* Main content */}
      <div className="flex-1 overflow-auto p-8 space-y-6">
        {/* Row 1: Actions + Stats */}
        <div className="grid grid-cols-12 gap-5">
          {/* Start Meeting */}
          <div
            className="col-span-12 md:col-span-5 group cursor-pointer rounded-2xl bg-white/[0.03] border border-white/[0.06] p-6 hover:bg-white/[0.06] hover:border-purple-500/20 transition-all duration-300 hover:shadow-lg hover:shadow-purple-500/5"
            onClick={() => setShowCreateDialog(true)}
            data-testid="card-instant-meeting"
          >
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-purple-500/25 group-hover:scale-110 transition-transform duration-300">
                <Video className="w-7 h-7 text-white" />
              </div>
              <div className="flex-1">
                <h2 className="text-lg font-semibold text-white">{t("karauMeet.startInstantMeeting")}</h2>
                <p className="text-slate-500 text-sm">{t("karauMeet.createNewMeetingNow")}</p>
              </div>
              <ArrowRight className="w-5 h-5 text-slate-700 group-hover:text-purple-400 group-hover:translate-x-1 transition-all" />
            </div>
          </div>

          {/* Join Meeting */}
          <div className="col-span-12 md:col-span-3 rounded-2xl bg-white/[0.03] border border-white/[0.06] p-6 hover:border-teal-500/20 transition-all duration-300" data-testid="card-join-meeting">
            <h3 className="text-sm font-semibold text-white mb-3">{t("karauMeet.joinMeeting")}</h3>
            <div className="flex gap-2">
              <Input
                placeholder="Enter code"
                value={joinMeetingId}
                onChange={(e) => setJoinMeetingId(e.target.value.toUpperCase())}
                className="bg-black/30 border-white/[0.08] text-white rounded-xl font-mono tracking-wider text-xs h-10 focus:border-teal-500/40 focus:ring-teal-500/20 placeholder-slate-600"
                onKeyPress={(e) => e.key === 'Enter' && joinMeeting()}
                data-testid="input-join-id"
              />
              <Button onClick={joinMeeting} className="bg-teal-600 hover:bg-teal-500 text-white rounded-xl px-4 h-10 shadow-lg shadow-teal-500/15" data-testid="btn-join">
                Join
              </Button>
            </div>
          </div>

          {/* Stats grid */}
          <div className="col-span-12 md:col-span-4 grid grid-cols-2 gap-3">
            {statItems.map((stat, idx) => (
              <div key={idx} className={`group rounded-2xl bg-white/[0.03] border border-white/[0.06] p-4 hover:bg-white/[0.06] hover:border-white/[0.1] transition-all duration-300 ${stat.glow}`} data-testid={`stat-${idx}`}>
                <stat.icon className={`w-4 h-4 ${stat.accent} mb-2 opacity-70`} />
                <p className="text-2xl font-bold text-white tabular-nums">{stat.value}</p>
                <p className="text-[11px] text-slate-500">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Row 2: AI Capabilities Banner */}
        <div className="rounded-2xl bg-gradient-to-r from-purple-900/20 via-indigo-900/10 to-teal-900/20 border border-white/[0.06] p-5" data-testid="ai-capabilities-banner">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-400" />
              <span className="text-xs font-semibold text-white uppercase tracking-wider">{t("karauMeet.aiPoweredFeatures")}</span>
            </div>
            <span className="text-[10px] text-slate-500">{t("karauMeet.availableEveryMeeting")}</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {AI_CAPABILITIES.map((cap, i) => (
              <div key={i} className={`flex items-center gap-2 px-3 py-2 ${cap.bg} rounded-xl border border-white/[0.06] hover:border-white/[0.12] transition-all duration-200 cursor-default`}>
                <cap.icon className={`w-3.5 h-3.5 ${cap.color}`} />
                <span className="text-xs text-slate-300 font-medium">{t(cap.labelKey)}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Row 3: Next Meeting + Meeting Insights */}
        <div className="grid grid-cols-12 gap-5">
          {/* Next Upcoming Meeting (featured) + hidden rest */}
          <div className="col-span-12 md:col-span-7" data-testid="upcoming-meetings">
            {upcoming.length === 0 ? (
              <div className="rounded-2xl bg-white/[0.03] border border-white/[0.06] p-5">
                <div className="flex items-center gap-2 mb-2">
                  <CalendarClock className="w-4 h-4 text-blue-400" />
                  <span className="text-sm font-semibold text-white">Upcoming</span>
                </div>
                <p className="text-xs text-slate-600">{t("karauMeet.noUpcoming")}</p>
              </div>
            ) : (
              <div className="space-y-3">
                {/* Featured next meeting */}
                {(() => {
                  const next = upcoming[0];
                  const countdown = getCountdown(next.scheduled_time);
                  const scheduledDate = new Date(next.scheduled_time);
                  return (
                    <div className="rounded-2xl bg-gradient-to-r from-blue-900/20 via-indigo-900/10 to-purple-900/15 border border-blue-500/15 p-5 hover:border-blue-500/25 transition-all" data-testid="next-meeting-card">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <div className="w-2.5 h-2.5 rounded-full bg-blue-400 animate-pulse" />
                          <span className="text-xs font-semibold text-blue-300 uppercase tracking-wider">{t("karauMeet.nextMeeting")}</span>
                        </div>
                        {upcoming.length > 1 && (
                          <Badge className="bg-white/[0.06] text-slate-400 border-white/[0.06] text-[10px]">
                            +{upcoming.length - 1} more
                          </Badge>
                        )}
                      </div>
                      <h3 className="text-lg font-semibold text-white mb-2">{next.title}</h3>
                      <div className="flex items-center gap-4 mb-4">
                        <div className="flex items-center gap-1.5 text-xs text-slate-400">
                          <CalendarClock className="w-3.5 h-3.5" />
                          <span>{scheduledDate.toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' })} at {scheduledDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                        </div>
                        {countdown && (
                          <Badge className="bg-blue-500/15 text-blue-300 border-blue-500/25 text-xs font-semibold px-3">{countdown}</Badge>
                        )}
                      </div>
                      <Button onClick={() => navigate(`/karau-meet/lobby/${next.meeting_id}`)}
                        className="bg-blue-600 hover:bg-blue-500 text-white rounded-full px-6 h-9 text-sm shadow-lg shadow-blue-500/20 transition-all hover:scale-[1.02] active:scale-[0.98]"
                        data-testid="btn-start-next-meeting">
                        <Play className="w-3.5 h-3.5 mr-2" /> {t("karauMeet.startMeeting")}
                      </Button>
                    </div>
                  );
                })()}

                {/* Collapsible remaining meetings */}
                {upcoming.length > 1 && (
                  <div className="rounded-2xl bg-white/[0.03] border border-white/[0.06] overflow-hidden">
                    <button
                      onClick={() => setShowAllUpcoming(!showAllUpcoming)}
                      className="w-full flex items-center justify-between px-5 py-3 hover:bg-white/[0.02] transition-colors"
                      data-testid="toggle-all-upcoming"
                    >
                      <span className="text-xs font-medium text-slate-400">{upcoming.length - 1} more upcoming meeting{upcoming.length > 2 ? 's' : ''}</span>
                      {showAllUpcoming ? <ChevronUp className="w-4 h-4 text-slate-600" /> : <ChevronDown className="w-4 h-4 text-slate-600" />}
                    </button>
                    {showAllUpcoming && (
                      <div className="px-5 pb-3 space-y-1.5">
                        {upcoming.slice(1).map((m) => {
                          const cd = getCountdown(m.scheduled_time);
                          return (
                            <div key={m.meeting_id} className="flex items-center justify-between gap-3 px-3 py-2.5 rounded-xl bg-white/[0.02] hover:bg-white/[0.04] border border-white/[0.04] transition-all" data-testid={`upcoming-${m.meeting_id}`}>
                              <div className="flex items-center gap-2.5 min-w-0 flex-1">
                                <div className="w-1.5 h-1.5 rounded-full bg-blue-400/60 flex-shrink-0" />
                                <span className="text-xs text-slate-400 truncate">{m.title}</span>
                                {cd && <Badge className="bg-blue-500/10 text-blue-300/70 border-blue-500/15 text-[9px] flex-shrink-0">{cd}</Badge>}
                              </div>
                              <Button size="sm" onClick={() => navigate(`/karau-meet/lobby/${m.meeting_id}`)}
                                className="bg-blue-600/60 hover:bg-blue-500 text-white rounded-lg text-[10px] px-2.5 h-6">
                                Start
                              </Button>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Meeting Insights */}
          <div className="col-span-12 md:col-span-5" data-testid="meeting-insights-card">
            <div className="rounded-2xl bg-white/[0.03] border border-white/[0.06] p-5 h-full">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-violet-400" />
                  <span className="text-sm font-semibold text-white">{t("karauMeet.meetingInsights")}</span>
                </div>
                {insights.length > 1 && (
                  <Badge className="bg-violet-500/10 text-violet-400 border-violet-500/20 text-[10px]">{insights.filter(i => i.summary).length} summaries</Badge>
                )}
              </div>
              {insights.filter(i => i.summary).length === 0 ? (
                <p className="text-xs text-slate-600">{t("karauMeet.insightsAppearAfter")}</p>
              ) : (
                <div className="space-y-3">
                  {/* Featured insight (latest) */}
                  {(() => {
                    const featured = insights.find(i => i.summary) || insights[0];
                    if (!featured) return null;
                    return (
                      <div className="rounded-xl bg-white/[0.03] border border-white/[0.05] p-4" data-testid="featured-insight">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs font-semibold text-white truncate flex-1">{featured.title}</span>
                          <span className="text-[10px] text-slate-600 flex-shrink-0 ml-2">
                            {featured.ended_at ? new Date(featured.ended_at).toLocaleDateString([], { month: 'short', day: 'numeric' }) : ''}
                          </span>
                        </div>
                        <p className="text-xs text-slate-400 leading-relaxed mb-3">{featured.summary}</p>
                        {featured.key_decisions.length > 0 && (
                          <div className="mb-2">
                            <span className="text-[10px] text-emerald-400 font-semibold uppercase tracking-wider">{t("karauMeet.decisions")}</span>
                            {featured.key_decisions.map((d, i) => (
                              <p key={i} className="text-[11px] text-slate-400 mt-1 pl-2 border-l-2 border-emerald-500/30">{d}</p>
                            ))}
                          </div>
                        )}
                        {featured.action_items.length > 0 && (
                          <div>
                            <span className="text-[10px] text-amber-400 font-semibold uppercase tracking-wider">{t("karauMeet.actionItems")}</span>
                            {featured.action_items.slice(0, 2).map((a, i) => (
                              <p key={i} className="text-[11px] text-slate-400 mt-1 pl-2 border-l-2 border-amber-500/30">{a}</p>
                            ))}
                            {featured.unresolved_count > 0 && (
                              <Badge className="bg-amber-500/10 text-amber-300 border-amber-500/15 text-[9px] mt-2">{featured.unresolved_count} unresolved</Badge>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })()}

                  {/* Collapsible rest */}
                  {insights.filter(i => i.summary).length > 1 && (
                    <div>
                      <button onClick={() => setShowAllInsights(!showAllInsights)}
                        className="flex items-center gap-1.5 text-[11px] text-purple-400 hover:text-purple-300 transition-colors"
                        data-testid="toggle-all-insights">
                        {showAllInsights ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                        {showAllInsights ? 'Hide' : `View ${insights.filter(i => i.summary).length - 1} more`}
                      </button>
                      {showAllInsights && (
                        <div className="mt-2 space-y-2 max-h-48 overflow-auto">
                          {insights.filter(i => i.summary).slice(1).map((ins, idx) => (
                            <div key={idx} className="px-3 py-2.5 rounded-xl bg-white/[0.02] border border-white/[0.04] hover:bg-white/[0.04] transition-colors" data-testid={`insight-${idx}`}>
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-[11px] font-semibold text-slate-300 truncate">{ins.title}</span>
                                <span className="text-[9px] text-slate-600 ml-2">{ins.ended_at ? new Date(ins.ended_at).toLocaleDateString([], { month: 'short', day: 'numeric' }) : ''}</span>
                              </div>
                              <p className="text-[10px] text-slate-500 line-clamp-2">{ins.summary}</p>
                              <div className="flex gap-2 mt-1.5">
                                {ins.key_decisions.length > 0 && <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/15 text-[8px]">{ins.key_decisions.length} decisions</Badge>}
                                {ins.action_items.length > 0 && <Badge className="bg-amber-500/10 text-amber-300 border-amber-500/15 text-[8px]">{ins.action_items.length} actions</Badge>}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Row 3b: Trending Topics */}
        <div className="rounded-2xl bg-white/[0.03] border border-white/[0.06] p-5" data-testid="trending-topics">
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp className="w-4 h-4 text-violet-400" />
            <span className="text-sm font-semibold text-white">{t("karauMeet.trendingTopics")}</span>
          </div>
          {trendingTopics.length === 0 ? (
            <p className="text-xs text-slate-600">{t("karauMeet.topicsAppearAfter")}</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {trendingTopics.map((tp, i) => (
                <div key={i} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-xs ${
                  tp.sentiment === 'positive' ? 'bg-emerald-500/5 border-emerald-500/15 text-emerald-300' :
                  tp.sentiment === 'concern' ? 'bg-amber-500/5 border-amber-500/15 text-amber-300' :
                  'bg-purple-500/5 border-purple-500/15 text-purple-300'
                }`} data-testid={`topic-${i}`}>
                  <span className="font-medium">{tp.topic}</span>
                  {tp.count > 1 && <span className="text-[10px] opacity-60">x{tp.count}</span>}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Row 4: Analytics row */}
        {(effectiveness || gamification) && (
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
                      <p>Avg: <span className="text-slate-300">{effectiveness.avg_duration_minutes}m</span></p>
                      <p>Participants: <span className="text-slate-300">{effectiveness.avg_participants}</span></p>
                      <p>With notes: <span className="text-slate-300">{effectiveness.meetings_with_notes}/{effectiveness.total_meetings}</span></p>
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
                      <span className="text-sm font-semibold text-white">{gamification.rank_title}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-purple-400 font-semibold">Lv.{gamification.level}</span>
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
                    <span className="text-xs text-slate-500">{gamification.xp} XP</span>
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
                          <span className="text-purple-400 font-semibold">{entry.xp} XP</span>
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
                    <span className="text-sm font-semibold text-white">Quick Analytics</span>
                  </div>
                  <div className="space-y-3">
                    {[
                      { label: 'On-time rate', value: effectiveness.on_time_rate, color: 'bg-emerald-500', textColor: 'text-emerald-400' },
                      { label: 'AI Notes usage', value: effectiveness.total_meetings > 0 ? Math.round(effectiveness.meetings_with_notes / effectiveness.total_meetings * 100) : 0, color: 'bg-violet-500', textColor: 'text-violet-400' },
                      { label: 'Action items', value: effectiveness.total_meetings > 0 ? Math.round(effectiveness.meetings_with_action_items / effectiveness.total_meetings * 100) : 0, color: 'bg-blue-500', textColor: 'text-blue-400' },
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
        )}

        {/* Row 5: Recent Meetings + Highlights */}
        <div className="grid grid-cols-12 gap-5">
          {/* Recent Meetings */}
          <div className="col-span-12 md:col-span-7">
            <div className="rounded-2xl bg-white/[0.03] border border-white/[0.06] overflow-hidden" data-testid="meetings-list">
              <button
                onClick={() => setExpandedSection(expandedSection === 'meetings' ? '' : 'meetings')}
                className="w-full flex items-center justify-between px-5 py-4 hover:bg-white/[0.02] transition-colors"
              >
                <div className="flex items-center gap-2">
                  <Video className="w-4 h-4 text-slate-400" />
                  <span className="text-sm font-semibold text-white">{t("karauMeet.recentMeetings")}</span>
                  <Badge className="bg-white/[0.06] text-slate-400 border-white/[0.06] text-[10px]">{meetings.length}</Badge>
                  {activeMeetings.length > 0 && <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-[10px] animate-pulse">{activeMeetings.length} active</Badge>}
                </div>
                {expandedSection === 'meetings' ? <ChevronUp className="w-4 h-4 text-slate-600" /> : <ChevronDown className="w-4 h-4 text-slate-600" />}
              </button>
              {expandedSection === 'meetings' && (
                <div className="px-5 pb-4">
                  {loading ? (
                    <div className="flex items-center justify-center py-6"><Loader2 className="w-5 h-5 text-purple-400 animate-spin" /></div>
                  ) : meetings.length === 0 ? (
                    <p className="text-xs text-slate-600 py-4" data-testid="no-meetings">{t("karauMeet.noMeetingsYet")}</p>
                  ) : (
                    <div className="space-y-2">
                      {meetings.slice(0, 8).map((meeting) => (
                        <div key={meeting.meeting_id} className="flex items-center justify-between px-4 py-3 rounded-xl bg-white/[0.02] hover:bg-white/[0.04] border border-white/[0.04] transition-all" data-testid={`meeting-${meeting.meeting_id}`}>
                          <div className="flex items-center gap-3 min-w-0 flex-1">
                            <div className={`w-2 h-2 rounded-full flex-shrink-0 ${meeting.status === 'active' ? 'bg-emerald-400 animate-pulse' : meeting.status === 'ended' ? 'bg-slate-600' : 'bg-blue-400'}`} />
                            <span className="text-sm text-slate-300 truncate">{meeting.title}</span>
                            <span className="text-[10px] text-slate-600">{new Date(meeting.created_at).toLocaleDateString([], { month: 'short', day: 'numeric' })}</span>
                          </div>
                          <div className="flex items-center gap-2 flex-shrink-0">
                            <button onClick={() => copyMeetingLink(meeting.meeting_id)} className="text-slate-600 hover:text-white p-1 rounded-lg hover:bg-white/[0.06] transition-colors">
                              <Copy className="w-3.5 h-3.5" />
                            </button>
                            {meeting.status !== 'ended' && (
                              <Button size="sm" onClick={() => navigate(`/karau-meet/lobby/${meeting.meeting_id}`)} className={`rounded-lg text-xs px-3 h-7 ${meeting.status === 'active' ? 'bg-emerald-600 hover:bg-emerald-500' : 'bg-purple-600/80 hover:bg-purple-500'} text-white`}>
                                {meeting.status === 'active' ? 'Rejoin' : 'Start'}
                              </Button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Activity Highlights */}
          <div className="col-span-12 md:col-span-5">
            <div className="rounded-2xl bg-white/[0.03] border border-white/[0.06] p-5 h-full" data-testid="activity-feed">
              <div className="flex items-center gap-2 mb-3">
                <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
                <span className="text-sm font-semibold text-white">{t("karauMeet.highlights")}</span>
                {importantActivities.length > 0 && <Badge className="bg-violet-500/10 text-violet-400 border-violet-500/20 text-[10px]">{importantActivities.length}</Badge>}
              </div>
              {importantActivities.length === 0 ? (
                <p className="text-xs text-slate-600">{t("karauMeet.highlightsAppearAfter")}</p>
              ) : (
                <div className="space-y-2 max-h-48 overflow-auto">
                  {importantActivities.map((a, idx) => (
                    <div key={idx} className="flex items-center gap-3 px-3 py-2.5 rounded-xl bg-white/[0.02] border border-white/[0.03] hover:bg-white/[0.04] transition-colors" data-testid={`activity-${idx}`}>
                      <div className={`w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 ${a.type === 'ai_insight' ? 'bg-violet-500/10' : 'bg-emerald-500/10'}`}>
                        {a.icon === 'sparkles' ? <Sparkles className="w-3.5 h-3.5 text-violet-400" /> : <Video className="w-3.5 h-3.5 text-emerald-400" />}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs text-slate-300 truncate">{a.text}</p>
                        <span className="text-[10px] text-slate-600">{a.timestamp ? new Date(a.timestamp).toLocaleDateString([], { month: 'short', day: 'numeric' }) : ''}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Create Meeting Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="bg-[#1a1b2e] border-white/[0.08] rounded-2xl shadow-2xl shadow-black/60 max-w-lg">
          <DialogHeader>
            <DialogTitle className="text-white text-lg font-semibold" style={{ fontFamily: "'IBM Plex Sans', sans-serif" }}>{t("karauMeet.createNewMeeting")}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div>
              <Label className="text-slate-400 text-xs uppercase tracking-wider">{t("karauMeet.meetingTitle")}</Label>
              <Input placeholder="e.g. Weekly Team Sync" value={newMeetingTitle} onChange={(e) => setNewMeetingTitle(e.target.value)}
                className="bg-black/30 border-white/[0.08] text-white mt-2 rounded-xl h-11 focus:border-purple-500/40 placeholder-slate-600" data-testid="input-meeting-title" />
            </div>
            <div>
              <Label className="text-slate-400 text-xs uppercase tracking-wider">{t("karauMeet.scheduleOptional")}</Label>
              <Input type="datetime-local" value={scheduledTime} onChange={(e) => setScheduledTime(e.target.value)}
                className="bg-black/30 border-white/[0.08] text-white mt-2 rounded-xl h-11 focus:border-blue-500/40 [color-scheme:dark]" data-testid="input-scheduled-time" />
            </div>
            {templates.length > 0 && (
              <div>
                <Label className="text-slate-400 text-xs uppercase tracking-wider mb-2 block">{t("karauMeet.templateOptional")}</Label>
                <div className="grid grid-cols-2 gap-2 max-h-28 overflow-y-auto">
                  {templates.map(tmpl => (
                    <button key={tmpl.template_id} onClick={() => setSelectedTemplate(selectedTemplate?.template_id === tmpl.template_id ? null : tmpl)}
                      className={`text-left p-3 rounded-xl border transition-all text-xs ${selectedTemplate?.template_id === tmpl.template_id ? 'border-purple-500/40 bg-purple-500/10 text-purple-300' : 'border-white/[0.06] bg-white/[0.02] text-slate-400 hover:border-white/[0.1]'}`}
                      data-testid={`template-${tmpl.template_id}`}>
                      <span className="font-medium block text-slate-200">{tmpl.name}</span>
                      <span className="text-[10px] text-slate-500">{tmpl.industry}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}
            <div className="flex items-center justify-between p-4 bg-white/[0.03] rounded-xl border border-white/[0.05]">
              <div><Label className="text-slate-300 text-sm">{t("karauMeet.aiNotesShort")}</Label><p className="text-[11px] text-slate-500">{t("karauMeet.autoTranscribeAndSummarize")}</p></div>
              <Switch defaultChecked />
            </div>
            <div className="flex items-center justify-between p-4 bg-white/[0.03] rounded-xl border border-white/[0.05]">
              <div><Label className="text-slate-300 text-sm">{t("karauMeet.recording")}</Label><p className="text-[11px] text-slate-500">{t("karauMeet.cloudRecordingConsent")}</p></div>
              <Switch defaultChecked />
            </div>
          </div>
          <DialogFooter className="flex-col sm:flex-row gap-2">
            <Button variant="ghost" onClick={() => { setShowCreateDialog(false); setScheduledTime(''); }} className="text-slate-400 rounded-full">{t("karauMeet.cancel")}</Button>
            <div className="flex gap-2">
              {scheduledTime && (
                <Button variant="outline" onClick={() => createMeeting(true)} disabled={creating}
                  className="border-blue-500/30 text-blue-300 hover:bg-blue-500/10 rounded-full" data-testid="btn-schedule">
                  {creating ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <CalendarClock className="w-4 h-4 mr-2" />}
                  {t("karauMeet.schedule")}
                </Button>
              )}
              <Button onClick={() => createMeeting(false)} disabled={creating}
                className="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white rounded-full shadow-lg shadow-purple-500/20" data-testid="btn-create-meeting">
                {creating ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                {t("karauMeet.startNow")}
              </Button>
            </div>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {shareMeeting && <ShareMeetingDialog isOpen={!!shareMeeting} onClose={() => setShareMeeting(null)} meetingId={shareMeeting.meeting_id} meetingTitle={shareMeeting.title} />}
    </div>
  );
};

export default KarauMeetDashboard;
