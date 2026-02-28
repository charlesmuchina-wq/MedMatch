import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import {
  Video, Plus, Clock, Shield, Sparkles, Copy,
  Loader2, Users, Archive, Share2, Building2,
  ArrowRight, Globe, Mic, ChevronDown, ChevronUp, Bot
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
  const [stats, setStats] = useState({
    total_meetings: 0, total_hours: 0, recordings: 0, total_participants: 0, active_meetings: 0, ai_insights: 0
  });
  const [activities, setActivities] = useState([]);
  const [activitiesLoading, setActivitiesLoading] = useState(true);

  useEffect(() => {
    fetchMeetings();
    fetchTemplates();
    fetchStats();
    fetchActivityFeed();
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

  const createMeeting = async () => {
    setCreating(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/karau-meet/meetings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ title: newMeetingTitle || 'AI KARAU Meeting' })
      });
      if (response.ok) {
        const data = await response.json();
        toast.success(t("karauMeet.meetingCreated"));
        navigate(`/karau-meet/lobby/${data.meeting_id}`);
      } else {
        toast.error(t("karauMeet.failedCreate"));
      }
    } catch {
      toast.error(t("karauMeet.failedCreate"));
    }
    setCreating(false);
    setShowCreateDialog(false);
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

  const statItems = [
    { label: 'Meetings', value: stats.total_meetings, icon: Video, gradient: 'from-blue-500/20 to-blue-600/5', iconColor: 'text-blue-400' },
    { label: 'Hours', value: stats.total_hours, icon: Clock, gradient: 'from-purple-500/20 to-purple-600/5', iconColor: 'text-purple-400' },
    { label: 'AI Insights', value: stats.ai_insights, icon: Sparkles, gradient: 'from-violet-500/20 to-violet-600/5', iconColor: 'text-violet-400' },
    { label: 'Participants', value: stats.total_participants, icon: Users, gradient: 'from-emerald-500/20 to-emerald-600/5', iconColor: 'text-emerald-400' }
  ];

  const features = [
    { icon: Shield, label: 'E2E Encrypted', color: 'text-blue-400', bg: 'bg-blue-500/10 border-blue-500/20' },
    { icon: Sparkles, label: 'AI Notes', color: 'text-purple-400', bg: 'bg-purple-500/10 border-purple-500/20' },
    { icon: Globe, label: 'Multi-Language', color: 'text-violet-400', bg: 'bg-violet-500/10 border-violet-500/20' },
    { icon: Mic, label: 'Noise Cancel', color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/20' },
    { icon: Bot, label: 'AI Assistant', color: 'text-teal-400', bg: 'bg-teal-500/10 border-teal-500/20' }
  ];

  const activeMeetings = meetings.filter(m => m.status === 'active');

  return (
    <div className="h-full flex flex-col p-4 md:p-6 overflow-hidden" style={{ fontFamily: "'IBM Plex Sans', sans-serif" }} data-testid="karau-dashboard">
      {/* Row 1: Welcome + Actions */}
      <div className="flex items-center justify-between mb-4 flex-shrink-0">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-white tracking-tight" data-testid="dashboard-welcome">
            {t("karauMeet.welcomeBack", { name: user?.name?.split(' ')[0] || 'User' })}
          </h1>
          <p className="text-karau-muted text-sm mt-0.5">{t("karauMeet.readyForMeeting")}</p>
        </div>
        <div className="flex items-center gap-2">
          {user?.is_admin && (
            <Button variant="outline" className="border-white/10 text-slate-300 hover:text-white hover:border-purple-500/40 rounded-xl text-xs h-9" onClick={() => navigate('/karau-meet/enterprise')} data-testid="btn-enterprise">
              <Building2 className="w-3.5 h-3.5 mr-1.5" />Enterprise
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
            <h3 className="text-sm font-semibold text-white mb-2">{t("meeting.joinMeeting")}</h3>
            <div className="flex gap-2">
              <Input
                placeholder="Enter code"
                value={joinMeetingId}
                onChange={(e) => setJoinMeetingId(e.target.value.toUpperCase())}
                className="bg-karau-bg/60 border-white/10 text-white rounded-xl focus:border-emerald-500/40 focus:ring-emerald-500/20 font-mono tracking-wider text-xs h-9"
                onKeyPress={(e) => e.key === 'Enter' && joinMeeting()}
                data-testid="input-join-id"
              />
              <Button onClick={joinMeeting} className="bg-emerald-500/90 hover:bg-emerald-400 text-white font-medium rounded-xl px-4 h-9 text-xs shadow-lg shadow-emerald-500/15" data-testid="btn-join">
                Join
              </Button>
            </div>
          </div>
        </div>

        {/* Stats - Compact horizontal */}
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

      {/* Row 3: Feature Badges + Active Meetings Indicator */}
      <div className="flex items-center justify-between mb-3 flex-shrink-0">
        <div className="flex flex-wrap gap-2">
          {features.map((f, i) => (
            <div key={i} className={`flex items-center gap-1.5 px-3 py-1.5 ${f.bg} rounded-full border text-[11px]`}>
              <f.icon className={`w-3 h-3 ${f.color}`} />
              <span className="font-medium text-slate-300">{f.label}</span>
            </div>
          ))}
        </div>
        {stats.active_meetings > 0 && (
          <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-xs animate-pulse" data-testid="active-meetings-badge">
            {stats.active_meetings} Active
          </Badge>
        )}
      </div>

      {/* Row 4: Activity Feed + Collapsible Meetings side by side */}
      <div className="flex-1 min-h-0 grid grid-cols-12 gap-3 overflow-hidden">
        {/* Live Activity Feed */}
        <div className="col-span-12 md:col-span-7 flex flex-col min-h-0">
          <div className="flex items-center gap-2 mb-2">
            <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
            <span className="text-sm font-semibold text-white">Meeting Pulse</span>
            <span className="text-[10px] text-slate-500">Live activity</span>
          </div>
          <div className="flex-1 min-h-0 rounded-xl border border-white/5 bg-karau-card/40 backdrop-blur-sm overflow-auto" data-testid="activity-feed">
            {activitiesLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-4 h-4 text-purple-400 animate-spin" />
              </div>
            ) : activities.length === 0 ? (
              <div className="text-center py-8">
                <Clock className="w-6 h-6 text-slate-600 mx-auto mb-2" />
                <p className="text-slate-500 text-xs">No recent activity</p>
              </div>
            ) : (
              <div className="divide-y divide-white/[0.03]">
                {activities.map((a, idx) => (
                  <div key={idx} className="flex items-start gap-3 px-3 py-2.5 hover:bg-white/[0.02] transition-colors" data-testid={`activity-${idx}`}>
                    <div className={`mt-0.5 w-6 h-6 rounded-lg flex items-center justify-center flex-shrink-0 ${
                      a.type === 'meeting_created' ? 'bg-blue-500/10' :
                      a.type === 'meeting_started' ? 'bg-emerald-500/10' :
                      a.type === 'meeting_ended' ? 'bg-slate-500/10' :
                      a.type === 'participant_joined' ? 'bg-purple-500/10' :
                      a.type === 'ai_insight' ? 'bg-violet-500/10' : 'bg-slate-500/10'
                    }`}>
                      {a.icon === 'video' && <Video className="w-3 h-3 text-blue-400" />}
                      {a.icon === 'play' && <Video className="w-3 h-3 text-emerald-400" />}
                      {a.icon === 'check' && <Clock className="w-3 h-3 text-slate-400" />}
                      {a.icon === 'user' && <Users className="w-3 h-3 text-purple-400" />}
                      {a.icon === 'sparkles' && <Sparkles className="w-3 h-3 text-violet-400" />}
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-xs text-slate-300 truncate">{a.text}</p>
                      <p className="text-[10px] text-slate-600 mt-0.5">
                        {a.timestamp ? new Date(a.timestamp).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : ''}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Collapsible Recent Meetings */}
        <div className="col-span-12 md:col-span-5 flex flex-col min-h-0">
        <button
          onClick={() => setShowMeetings(!showMeetings)}
          className="flex items-center gap-2 mb-2 group w-full text-left"
          data-testid="toggle-meetings"
        >
          <span className="text-sm font-semibold text-white">Recent Meetings</span>
          <Badge className="bg-karau-surface text-slate-400 border-white/5 text-[10px]">{meetings.length}</Badge>
          {showMeetings ? (
            <ChevronUp className="w-3.5 h-3.5 text-slate-500 group-hover:text-white transition-colors" />
          ) : (
            <ChevronDown className="w-3.5 h-3.5 text-slate-500 group-hover:text-white transition-colors" />
          )}
        </button>

        {showMeetings && (
          <div className="rounded-xl border border-white/5 bg-karau-card/60 backdrop-blur-sm overflow-auto max-h-[calc(100%-2rem)]" data-testid="meetings-list">
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-5 h-5 text-purple-400 animate-spin" />
              </div>
            ) : meetings.length === 0 ? (
              <div className="text-center py-8" data-testid="no-meetings">
                <Video className="w-8 h-8 text-slate-600 mx-auto mb-2" />
                <p className="text-slate-400 text-sm">{t("karauMeet.noMeetingsYet")}</p>
              </div>
            ) : (
              <div className="divide-y divide-white/5">
                {meetings.slice(0, 8).map((meeting) => (
                  <div key={meeting.meeting_id} className="flex items-center justify-between px-4 py-3 hover:bg-white/[0.02] transition-colors" data-testid={`meeting-${meeting.meeting_id}`}>
                    <div className="flex items-center gap-3 min-w-0">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${meeting.status === 'active' ? 'bg-emerald-500/10 border border-emerald-500/20' : 'bg-karau-surface'}`}>
                        <Video className={`w-4 h-4 ${meeting.status === 'active' ? 'text-emerald-400' : 'text-slate-500'}`} />
                      </div>
                      <div className="min-w-0">
                        <h4 className="font-medium text-white text-xs truncate">{meeting.title}</h4>
                        <div className="flex items-center gap-1.5 mt-0.5">
                          <span className="text-[10px] text-karau-muted">{new Date(meeting.created_at).toLocaleDateString()}</span>
                          <Badge className={`text-[9px] px-1 py-0 rounded ${meeting.status === 'active' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : meeting.status === 'ended' ? 'bg-slate-500/10 text-slate-500 border-slate-500/20' : 'bg-violet-500/10 text-violet-400 border-violet-500/20'}`}>{meeting.status}</Badge>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-1 flex-shrink-0">
                      <Button variant="ghost" size="sm" onClick={() => setShareMeeting(meeting)} className="text-slate-500 hover:text-purple-400 rounded-lg h-7 w-7 p-0">
                        <Share2 className="w-3 h-3" />
                      </Button>
                      <Button variant="ghost" size="sm" onClick={() => copyMeetingLink(meeting.meeting_id)} className="text-slate-500 hover:text-white rounded-lg h-7 w-7 p-0">
                        <Copy className="w-3 h-3" />
                      </Button>
                      {meeting.status !== 'ended' && (
                        <Button size="sm" onClick={() => navigate(`/karau-meet/lobby/${meeting.meeting_id}`)} className={`rounded-lg text-[10px] px-2.5 h-7 ${meeting.status === 'active' ? 'bg-emerald-500 hover:bg-emerald-400 text-white' : 'bg-purple-500/80 hover:bg-purple-400 text-white'}`}>
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

      {/* Create Meeting Dialog */}
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
            <div>
              <Label className="text-slate-300 text-sm mb-2 block">Template (Optional)</Label>
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
            <Button variant="ghost" onClick={() => setShowCreateDialog(false)} className="text-slate-400 rounded-xl">
              {t("karauMeet.cancel")}
            </Button>
            <div className="flex gap-2">
              <Button variant="outline" onClick={async () => {
                setCreating(true);
                try {
                  const token = localStorage.getItem('token');
                  const response = await fetch(`${API}/api/karau-meet/meetings`, {
                    method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                    body: JSON.stringify({ title: newMeetingTitle || 'AI KARAU Meeting' })
                  });
                  if (response.ok) {
                    const data = await response.json();
                    setShowCreateDialog(false);
                    setShareMeeting({ meeting_id: data.meeting_id, title: newMeetingTitle || 'AI KARAU Meeting' });
                    fetchMeetings();
                    toast.success(t("karauMeet.meetingCreatedShare"));
                  } else { toast.error(t("karauMeet.failedCreate")); }
                } catch { toast.error(t("karauMeet.failedCreate")); }
                setCreating(false);
              }} disabled={creating} className="border-white/10 text-slate-300 hover:bg-white/5 rounded-xl" data-testid="btn-create-and-share">
                {creating ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Share2 className="w-4 h-4 mr-2" />}
                {t("karauMeet.createAndShare")}
              </Button>
              <Button onClick={createMeeting} disabled={creating} className="bg-gradient-to-r from-blue-600 via-purple-600 to-violet-600 hover:from-blue-500 hover:via-purple-500 hover:to-violet-500 text-white rounded-xl shadow-lg shadow-purple-500/20" data-testid="btn-create-meeting">
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
