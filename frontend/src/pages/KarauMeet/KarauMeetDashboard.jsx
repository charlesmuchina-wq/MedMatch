import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import {
  Video, Plus, Clock, Shield, Sparkles, Copy,
  Loader2, Users, Share2, Building2,
  ArrowRight, Globe, Mic, ChevronDown, ChevronUp, Bot,
  CalendarClock, TrendingUp, Trophy, Flame, Target, BarChart3
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

// Countdown helper
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
  const [showMeetings, setShowMeetings] = useState(false);
  const [showPulse, setShowPulse] = useState(false);
  const [scheduledTime, setScheduledTime] = useState('');
  const [stats, setStats] = useState({
    total_meetings: 0, total_hours: 0, recordings: 0, total_participants: 0, active_meetings: 0, ai_insights: 0
  });
  const [activities, setActivities] = useState([]);
  const [activitiesLoading, setActivitiesLoading] = useState(true);
  const [upcoming, setUpcoming] = useState([]);
  const [trendingTopics, setTrendingTopics] = useState([]);
  const [, setTick] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [effectiveness, setEffectiveness] = useState(null);
  const [gamification, setGamification] = useState(null);

  useEffect(() => {
    fetchMeetings();
    fetchTemplates();
    fetchStats();
    fetchActivityFeed();
    fetchUpcoming();
    fetchTrendingTopics();
  }, []);

  // Countdown timer - update every minute
  useEffect(() => {
    const interval = setInterval(() => setTick(t => t + 1), 60000);
    return () => clearInterval(interval);
  }, []);

  // Auto-refresh polling every 30 seconds
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
      if (res.ok) { const data = await res.json(); setStats(data); }
    } catch (e) { console.error('Stats error:', e); }
  };

  const fetchActivityFeed = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API}/api/karau-meet/activity-feed?limit=12`, { headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) { const data = await res.json(); setActivities(data.activities || []); }
    } catch (e) { console.error('Activity error:', e); }
    setActivitiesLoading(false);
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

  const fetchTemplates = async () => {
    try {
      const res = await fetch(`${API}/api/karau-features/templates`);
      if (res.ok) { const data = await res.json(); setTemplates(data.templates || []); }
    } catch (e) { console.error(e); }
  };

  const fetchMeetings = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/karau-meet/meetings`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setMeetings(data.meetings || []);
      }
    } catch (error) {
      console.error('Error fetching meetings:', error);
    }
    setLoading(false);
  };

  const createMeeting = async (isScheduled = false) => {
    setCreating(true);
    try {
      const token = localStorage.getItem('token');
      const body = { title: newMeetingTitle || 'AI KARAU Meeting' };
      if (isScheduled && scheduledTime) {
        body.scheduled_time = new Date(scheduledTime).toISOString();
      }
      const response = await fetch(`${API}/api/karau-meet/meetings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify(body)
      });
      if (response.ok) {
        const data = await response.json();
        if (isScheduled) {
          toast.success(t("karauMeet.meetingScheduled"));
          fetchUpcoming();
          fetchMeetings();
        } else {
          toast.success(t("karauMeet.meetingCreated"));
          navigate(`/karau-meet/lobby/${data.meeting_id}`);
        }
      } else {
        toast.error(t("karauMeet.failedCreate"));
      }
    } catch {
      toast.error(t("karauMeet.failedCreate"));
    }
    setCreating(false);
    setShowCreateDialog(false);
    setScheduledTime('');
  };

  const joinMeeting = () => {
    if (!joinMeetingId.trim()) { toast.error(t("karauMeet.enterMeetingIdError")); return; }
    navigate(`/karau-meet/lobby/${joinMeetingId.toUpperCase()}`);
  };

  const copyMeetingLink = (meetingId) => {
    const link = `${window.location.origin}/karau-meet/join/${meetingId}`;
    navigator.clipboard.writeText(link);
    toast.success(t("karauMeet.meetingLinkCopied"));
  };

  // Filter to only highlights and action items
  const importantActivities = activities.filter(a =>
    a.type === 'ai_insight' || a.type === 'meeting_started'
  );

  const statItems = [
    { label: t("karauMeet.meetings"), value: stats.total_meetings, icon: Video, gradient: 'from-blue-500/20 to-blue-600/5', iconColor: 'text-blue-400' },
    { label: t("karauMeet.hours"), value: stats.total_hours, icon: Clock, gradient: 'from-purple-500/20 to-purple-600/5', iconColor: 'text-purple-400' },
    { label: t("karauMeet.aiInsights"), value: stats.ai_insights, icon: Sparkles, gradient: 'from-violet-500/20 to-violet-600/5', iconColor: 'text-violet-400' },
    { label: t("karauMeet.participants"), value: stats.total_participants, icon: Users, gradient: 'from-emerald-500/20 to-emerald-600/5', iconColor: 'text-emerald-400' }
  ];

  const features = [
    { icon: Shield, label: t("karauMeet.e2eEncrypted"), color: 'text-blue-400', bg: 'bg-blue-500/10 border-blue-500/20' },
    { icon: Sparkles, label: t("karauMeet.aiNotes"), color: 'text-purple-400', bg: 'bg-purple-500/10 border-purple-500/20' },
    { icon: Globe, label: t("karauMeet.multiLanguage"), color: 'text-violet-400', bg: 'bg-violet-500/10 border-violet-500/20' },
    { icon: Mic, label: t("karauMeet.noiseCancel"), color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/20' },
    { icon: Bot, label: t("karauMeet.aiAssistant"), color: 'text-teal-400', bg: 'bg-teal-500/10 border-teal-500/20' }
  ];

  return (
    <div className="h-full flex flex-col p-4 md:p-6 overflow-hidden" style={{ fontFamily: "'IBM Plex Sans', sans-serif" }} data-testid="karau-dashboard">
      {/* Row 1: Welcome + Actions */}
      <div className="flex items-center justify-between mb-4 flex-shrink-0">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-white tracking-tight" data-testid="dashboard-welcome">
            {t("karauMeet.welcomeBack", { name: user?.name?.split(' ')[0] || 'User' })}
          </h1>
          <p className="text-karau-muted text-sm mt-0.5 flex items-center gap-2">
            {t("karauMeet.readyForMeeting")}
            {isRefreshing && (
              <span className="flex items-center gap-1 text-[10px] text-purple-400/60">
                <Loader2 className="w-3 h-3 animate-spin" />
              </span>
            )}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {user?.is_admin && (
            <Button variant="outline" className="border-white/10 text-slate-300 hover:text-white hover:border-purple-500/40 rounded-xl text-xs h-9" onClick={() => navigate('/karau-meet/enterprise')} data-testid="btn-enterprise">
              <Building2 className="w-3.5 h-3.5 mr-1.5" />{t("karauMeet.enterprise")}
            </Button>
          )}
          <Button onClick={() => setShowCreateDialog(true)} className="bg-gradient-to-r from-blue-600 via-purple-600 to-violet-600 hover:from-blue-500 hover:via-purple-500 hover:to-violet-500 text-white rounded-xl shadow-lg shadow-purple-500/20 hover:shadow-purple-500/30 transition-all duration-300 hover:scale-[1.02] h-9 text-xs" data-testid="btn-new-meeting">
            <Plus className="w-3.5 h-3.5 mr-1.5" />{t("karauMeet.newMeeting")}
          </Button>
        </div>
      </div>

      {/* Row 2: Horizontal Bento Grid - Actions + Stats */}
      <div className="grid grid-cols-12 gap-3 mb-3 flex-shrink-0">
        {/* Start Meeting Card */}
        <div className="col-span-12 md:col-span-5">
          <div
            className="relative group cursor-pointer overflow-hidden rounded-2xl border border-white/5 bg-gradient-to-br from-karau-card via-karau-panel to-karau-card p-5 hover:border-purple-500/30 transition-all duration-500 h-full"
            onClick={() => setShowCreateDialog(true)}
            data-testid="card-instant-meeting"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 via-purple-500/5 to-emerald-500/3 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="relative z-10 flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-600 via-purple-600 to-violet-600 flex items-center justify-center shadow-lg shadow-purple-500/25 group-hover:scale-110 transition-transform duration-300 flex-shrink-0">
                <Video className="w-6 h-6 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <h2 className="text-base font-semibold text-white">{t("karauMeet.startInstantMeeting")}</h2>
                <p className="text-karau-muted text-xs mt-0.5">{t("karauMeet.createNewMeetingNow")}</p>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-600 group-hover:text-purple-400 group-hover:translate-x-1 transition-all flex-shrink-0" />
            </div>
          </div>
        </div>

        {/* Join Meeting Card */}
        <div className="col-span-12 md:col-span-3">
          <div className="h-full rounded-2xl border border-white/5 bg-gradient-to-br from-karau-card to-karau-panel p-5 hover:border-emerald-500/30 transition-all duration-300" data-testid="card-join-meeting">
            <h3 className="text-sm font-semibold text-white mb-2">{t("karauMeet.joinMeeting")}</h3>
            <div className="flex gap-2">
              <Input
                placeholder={t("karauMeet.enterCode")}
                value={joinMeetingId}
                onChange={(e) => setJoinMeetingId(e.target.value.toUpperCase())}
                className="bg-karau-bg/60 border-white/10 text-white rounded-xl focus:border-emerald-500/40 focus:ring-emerald-500/20 font-mono tracking-wider text-xs h-9"
                onKeyPress={(e) => e.key === 'Enter' && joinMeeting()}
                data-testid="input-join-id"
              />
              <Button onClick={joinMeeting} className="bg-emerald-500/90 hover:bg-emerald-400 text-white font-medium rounded-xl px-4 h-9 text-xs shadow-lg shadow-emerald-500/15" data-testid="btn-join">
                {t("karauMeet.join")}
              </Button>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="col-span-12 md:col-span-4 grid grid-cols-4 gap-2">
          {statItems.map((stat, idx) => (
            <div key={idx} className={`rounded-xl border border-white/5 bg-gradient-to-br ${stat.gradient} p-3 transition-all duration-300 hover:border-white/10`} data-testid={`stat-${idx}`}>
              <stat.icon className={`w-4 h-4 ${stat.iconColor} mb-1`} />
              <p className="text-xl font-bold text-white">{stat.value}</p>
              <p className="text-[10px] text-karau-muted">{stat.label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Row 3: Upcoming Meetings + Trending Topics */}
      <div className="grid grid-cols-12 gap-3 mb-3 flex-shrink-0">
        {/* Upcoming Meetings with countdown */}
        <div className="col-span-12 md:col-span-7">
          <div className="rounded-xl border border-white/5 bg-karau-card/40 p-3" data-testid="upcoming-meetings">
            <div className="flex items-center gap-2 mb-2">
              <CalendarClock className="w-3.5 h-3.5 text-blue-400" />
              <span className="text-xs font-semibold text-white">{t("karauMeet.upcoming")}</span>
              {upcoming.length > 0 && <Badge className="bg-blue-500/10 text-blue-400 border-blue-500/20 text-[10px]">{upcoming.length}</Badge>}
            </div>
            {upcoming.length === 0 ? (
              <p className="text-[11px] text-slate-600">{t("karauMeet.noScheduledMeetings")}</p>
            ) : (
              <div className="space-y-1.5">
                {upcoming.slice(0, 3).map((m) => {
                  const countdown = getCountdown(m.scheduled_time);
                  return (
                    <div key={m.meeting_id} className="flex items-center justify-between gap-2 px-2 py-1.5 rounded-lg bg-karau-bg/40 hover:bg-karau-surface transition-colors" data-testid={`upcoming-${m.meeting_id}`}>
                      <div className="flex items-center gap-2 min-w-0 flex-1">
                        <div className="w-1.5 h-1.5 rounded-full bg-blue-400 flex-shrink-0" />
                        <span className="text-[11px] text-slate-300 truncate">{m.title}</span>
                        {countdown && (
                          <Badge className="bg-blue-500/10 text-blue-300 border-blue-500/20 text-[9px] px-1.5 py-0 flex-shrink-0">
                            {t("karauMeet.startsIn")} {countdown}
                          </Badge>
                        )}
                        {m.scheduled_time && !countdown && (
                          <span className="text-[9px] text-slate-500 flex-shrink-0">
                            {new Date(m.scheduled_time).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                          </span>
                        )}
                      </div>
                      <Button size="sm" onClick={() => navigate(`/karau-meet/lobby/${m.meeting_id}`)}
                        className="bg-blue-500/80 hover:bg-blue-400 text-white rounded text-[9px] px-2 h-6">
                        {t("karauMeet.start")}
                      </Button>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Trending Topics */}
        <div className="col-span-12 md:col-span-5">
          <div className="rounded-xl border border-white/5 bg-karau-card/40 p-3 h-full" data-testid="trending-topics">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-3.5 h-3.5 text-violet-400" />
              <span className="text-xs font-semibold text-white">{t("karauMeet.trendingTopics")}</span>
            </div>
            {trendingTopics.length === 0 ? (
              <p className="text-[11px] text-slate-600">{t("karauMeet.topicsAppearHint")}</p>
            ) : (
              <div className="flex flex-wrap gap-1.5">
                {trendingTopics.map((tp, i) => (
                  <div key={i} className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-[10px] ${
                    tp.sentiment === 'positive' ? 'bg-emerald-500/5 border-emerald-500/15 text-emerald-300' :
                    tp.sentiment === 'concern' ? 'bg-amber-500/5 border-amber-500/15 text-amber-300' :
                    'bg-purple-500/5 border-purple-500/15 text-purple-300'
                  }`} data-testid={`topic-${i}`}>
                    <span className="font-medium">{tp.topic}</span>
                    {tp.count > 1 && <span className="text-[9px] opacity-60">x{tp.count}</span>}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Row 4: Feature Badges + Active Badge */}
      <div className="flex items-center justify-between mb-2 flex-shrink-0">
        <div className="flex flex-wrap gap-1.5">
          {features.map((f, i) => (
            <div key={i} className={`flex items-center gap-1 px-2 py-1 ${f.bg} rounded-full border text-[10px]`}>
              <f.icon className={`w-2.5 h-2.5 ${f.color}`} />
              <span className="font-medium text-slate-400">{f.label}</span>
            </div>
          ))}
        </div>
        {stats.active_meetings > 0 && (
          <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-[10px] animate-pulse" data-testid="active-meetings-badge">
            {stats.active_meetings} {t("karauMeet.active")}
          </Badge>
        )}
      </div>

      {/* Row 5: Collapsible Sections */}
      <div className="flex-1 min-h-0 space-y-2 overflow-auto">
        {/* Highlights - Collapsible */}
        <div>
          <button onClick={() => setShowPulse(!showPulse)} className="flex items-center gap-2 group w-full text-left py-1" data-testid="toggle-pulse">
            <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse" />
            <span className="text-sm font-semibold text-white">{t("karauMeet.highlights")}</span>
            {importantActivities.length > 0 && (
              <Badge className="bg-violet-500/10 text-violet-400 border-violet-500/20 text-[10px]">{importantActivities.length}</Badge>
            )}
            {showPulse ? <ChevronUp className="w-3 h-3 text-slate-500" /> : <ChevronDown className="w-3 h-3 text-slate-500" />}
          </button>
          {showPulse && (
            <div className="rounded-xl border border-white/5 bg-karau-card/40 overflow-auto max-h-48 mt-1" data-testid="activity-feed">
              {activitiesLoading ? (
                <div className="flex items-center justify-center py-4"><Loader2 className="w-4 h-4 text-purple-400 animate-spin" /></div>
              ) : importantActivities.length === 0 ? (
                <div className="text-center py-4"><p className="text-slate-600 text-xs">{t("karauMeet.noHighlights")}</p></div>
              ) : (
                <div className="divide-y divide-white/[0.03]">
                  {importantActivities.map((a, idx) => (
                    <div key={idx} className="flex items-center gap-2.5 px-3 py-2 hover:bg-white/[0.02] transition-colors" data-testid={`activity-${idx}`}>
                      <div className={`w-5 h-5 rounded-md flex items-center justify-center flex-shrink-0 ${a.type === 'ai_insight' ? 'bg-violet-500/10' : 'bg-emerald-500/10'}`}>
                        {a.icon === 'sparkles' ? <Sparkles className="w-2.5 h-2.5 text-violet-400" /> : <Video className="w-2.5 h-2.5 text-emerald-400" />}
                      </div>
                      <p className="text-[11px] text-slate-300 truncate flex-1">{a.text}</p>
                      <span className="text-[9px] text-slate-600 flex-shrink-0">
                        {a.timestamp ? new Date(a.timestamp).toLocaleString([], { month: 'short', day: 'numeric' }) : ''}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Recent Meetings - Collapsible */}
        <div>
          <button onClick={() => setShowMeetings(!showMeetings)} className="flex items-center gap-2 group w-full text-left py-1" data-testid="toggle-meetings">
            <span className="text-sm font-semibold text-white">{t("karauMeet.recentMeetings")}</span>
            <Badge className="bg-karau-surface text-slate-400 border-white/5 text-[10px]">{meetings.length}</Badge>
            {showMeetings ? <ChevronUp className="w-3 h-3 text-slate-500" /> : <ChevronDown className="w-3 h-3 text-slate-500" />}
          </button>
          {showMeetings && (
            <div className="rounded-xl border border-white/5 bg-karau-card/40 overflow-auto max-h-48 mt-1" data-testid="meetings-list">
              {loading ? (
                <div className="flex items-center justify-center py-4"><Loader2 className="w-4 h-4 text-purple-400 animate-spin" /></div>
              ) : meetings.length === 0 ? (
                <div className="text-center py-4" data-testid="no-meetings"><p className="text-slate-500 text-xs">{t("karauMeet.noMeetingsYet")}</p></div>
              ) : (
                <div className="divide-y divide-white/[0.03]">
                  {meetings.slice(0, 6).map((meeting) => (
                    <div key={meeting.meeting_id} className="flex items-center justify-between px-3 py-2 hover:bg-white/[0.02] transition-colors" data-testid={`meeting-${meeting.meeting_id}`}>
                      <div className="flex items-center gap-2 min-w-0 flex-1">
                        <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${meeting.status === 'active' ? 'bg-emerald-400' : 'bg-slate-600'}`} />
                        <span className="text-[11px] text-slate-300 truncate">{meeting.title}</span>
                        <Badge className={`text-[8px] px-1 py-0 rounded flex-shrink-0 ${meeting.status === 'active' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-slate-500/10 text-slate-500 border-slate-500/20'}`}>{meeting.status}</Badge>
                      </div>
                      <div className="flex items-center gap-1 flex-shrink-0">
                        <Button variant="ghost" size="sm" onClick={() => copyMeetingLink(meeting.meeting_id)} className="text-slate-600 hover:text-white rounded h-6 w-6 p-0">
                          <Copy className="w-2.5 h-2.5" />
                        </Button>
                        {meeting.status !== 'ended' && (
                          <Button size="sm" onClick={() => navigate(`/karau-meet/lobby/${meeting.meeting_id}`)} className={`rounded text-[9px] px-2 h-6 ${meeting.status === 'active' ? 'bg-emerald-500 hover:bg-emerald-400 text-white' : 'bg-purple-500/80 hover:bg-purple-400 text-white'}`}>
                            {meeting.status === 'active' ? t("karauMeet.rejoin") : t("karauMeet.start")}
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

      {/* Create Meeting Dialog with Scheduling */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="bg-karau-card border-white/10 rounded-2xl shadow-2xl shadow-black/50 max-w-lg">
          <DialogHeader>
            <DialogTitle className="text-white font-semibold" style={{ fontFamily: "'IBM Plex Sans', sans-serif" }}>{t("karauMeet.createNewMeeting")}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div>
              <Label className="text-slate-300 text-sm">{t("karauMeet.meetingTitle")}</Label>
              <Input placeholder={t("karauMeet.meetingTitlePlaceholder")} value={newMeetingTitle} onChange={(e) => setNewMeetingTitle(e.target.value)} className="bg-karau-bg/60 border-white/10 text-white mt-1.5 rounded-xl focus:border-purple-500/40" data-testid="input-meeting-title" />
            </div>
            {/* Schedule Date/Time */}
            <div>
              <Label className="text-slate-300 text-sm">{t("karauMeet.selectDateTime")}</Label>
              <Input
                type="datetime-local"
                value={scheduledTime}
                onChange={(e) => setScheduledTime(e.target.value)}
                className="bg-karau-bg/60 border-white/10 text-white mt-1.5 rounded-xl focus:border-blue-500/40 [color-scheme:dark]"
                data-testid="input-scheduled-time"
              />
              {scheduledTime && (
                <p className="text-[10px] text-blue-400 mt-1">
                  {t("karauMeet.scheduledFor")} {new Date(scheduledTime).toLocaleString()}
                </p>
              )}
            </div>
            <div>
              <Label className="text-slate-300 text-sm mb-2 block">{t("karauMeet.templateOptional")}</Label>
              <div className="grid grid-cols-2 gap-2 max-h-32 overflow-y-auto">
                {templates.map(tmpl => (
                  <button key={tmpl.template_id} onClick={() => setSelectedTemplate(selectedTemplate?.template_id === tmpl.template_id ? null : tmpl)}
                    className={`text-left p-2 rounded-xl border transition-all text-xs ${selectedTemplate?.template_id === tmpl.template_id ? 'border-purple-500/50 bg-purple-500/10 text-purple-300' : 'border-white/5 bg-karau-bg/40 text-slate-400 hover:border-white/10'}`} data-testid={`template-${tmpl.template_id}`}>
                    <span className="font-medium block text-slate-200 text-xs">{tmpl.name}</span>
                    <span className="text-[10px] text-slate-500">{tmpl.industry}</span>
                  </button>
                ))}
              </div>
            </div>
            <div className="flex items-center justify-between p-3 bg-karau-bg/40 rounded-xl">
              <div>
                <Label className="text-slate-300 text-sm">{t("karauMeet.enableAINotes")}</Label>
                <p className="text-xs text-karau-muted">{t("karauMeet.autoTranscription")}</p>
              </div>
              <Switch defaultChecked />
            </div>
            <div className="flex items-center justify-between p-3 bg-karau-bg/40 rounded-xl">
              <div>
                <Label className="text-slate-300 text-sm">{t("karauMeet.enableRecording")}</Label>
                <p className="text-xs text-karau-muted">{t("karauMeet.recordingConsent")}</p>
              </div>
              <Switch defaultChecked />
            </div>
          </div>
          <DialogFooter className="flex-col sm:flex-row gap-2">
            <Button variant="ghost" onClick={() => { setShowCreateDialog(false); setScheduledTime(''); }} className="text-slate-400 rounded-xl">
              {t("karauMeet.cancel")}
            </Button>
            <div className="flex gap-2">
              {scheduledTime && (
                <Button variant="outline" onClick={() => createMeeting(true)} disabled={creating} className="border-blue-500/30 text-blue-300 hover:bg-blue-500/10 rounded-xl" data-testid="btn-schedule">
                  {creating ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <CalendarClock className="w-4 h-4 mr-2" />}
                  {t("karauMeet.scheduleMeeting")}
                </Button>
              )}
              <Button onClick={() => createMeeting(false)} disabled={creating} className="bg-gradient-to-r from-blue-600 via-purple-600 to-violet-600 hover:from-blue-500 hover:via-purple-500 hover:to-violet-500 text-white rounded-xl shadow-lg shadow-purple-500/20" data-testid="btn-create-meeting">
                {creating ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                {t("karauMeet.startMeeting")}
              </Button>
            </div>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {shareMeeting && (
        <ShareMeetingDialog isOpen={!!shareMeeting} onClose={() => setShareMeeting(null)} meetingId={shareMeeting.meeting_id} meetingTitle={shareMeeting.title} />
      )}
    </div>
  );
};

export default KarauMeetDashboard;
