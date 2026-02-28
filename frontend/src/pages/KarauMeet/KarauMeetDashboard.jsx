import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import {
  Video, Plus, Clock, Shield, Sparkles, Copy,
  Loader2, History, MonitorPlay, Users, Archive, Share2, Building2,
  ArrowRight, Zap, Globe, Mic
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
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
  const [stats, setStats] = useState({
    total_meetings: 0,
    total_hours: 0,
    recordings: 0,
    participants: 0
  });

  useEffect(() => {
    fetchMeetings();
    setStats({ total_meetings: 24, total_hours: 48, recordings: 12, participants: 156 });
  }, []);

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
    } catch (error) {
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
    { label: t("karauMeet.totalMeetings"), value: stats.total_meetings, icon: Video, color: 'from-teal-500/20 to-teal-500/5', iconColor: 'text-teal-400', border: 'hover:border-teal-500/30' },
    { label: t("karauMeet.hoursInMeetings"), value: stats.total_hours, icon: Clock, color: 'from-emerald-500/20 to-emerald-500/5', iconColor: 'text-emerald-400', border: 'hover:border-emerald-500/30' },
    { label: t("karauMeet.recordings"), value: stats.recordings, icon: Archive, color: 'from-amber-500/20 to-amber-500/5', iconColor: 'text-amber-400', border: 'hover:border-amber-500/30' },
    { label: t("karauMeet.participantsMet"), value: stats.participants, icon: Users, color: 'from-green-500/20 to-green-500/5', iconColor: 'text-green-400', border: 'hover:border-green-500/30' }
  ];

  const features = [
    { icon: Shield, label: t("karauMeet.endToEndEncrypted"), color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
    { icon: Sparkles, label: t("karauMeet.aiNotesTranscription"), color: 'text-teal-400', bg: 'bg-teal-500/10' },
    { icon: Globe, label: 'Multi-Language', color: 'text-amber-400', bg: 'bg-amber-500/10' },
    { icon: Mic, label: 'Noise Cancellation', color: 'text-green-400', bg: 'bg-green-500/10' }
  ];

  return (
    <div className="p-6 md:p-8 space-y-8" style={{ fontFamily: "'IBM Plex Sans', sans-serif" }}>
      {/* Welcome Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight" data-testid="dashboard-welcome">
            {t("karauMeet.welcomeBack", { name: user?.name?.split(' ')[0] || 'User' })}
          </h1>
          <p className="text-karau-muted mt-1">{t("karauMeet.readyForMeeting")}</p>
        </div>
        <div className="flex items-center gap-3">
          {user?.is_admin && (
            <Button variant="outline" className="border-white/10 text-slate-300 hover:text-white hover:border-amber-500/40 rounded-xl" onClick={() => navigate('/karau-meet/enterprise')} data-testid="btn-enterprise">
              <Building2 className="w-4 h-4 mr-2" />Enterprise
            </Button>
          )}
          <Button onClick={() => setShowCreateDialog(true)} className="bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-400 hover:to-emerald-400 text-white rounded-xl shadow-lg shadow-teal-500/20 hover:shadow-teal-500/30 transition-all duration-300 hover:scale-[1.02]" data-testid="btn-new-meeting">
            <Plus className="w-4 h-4 mr-2" />{t("karauMeet.newMeeting")}
          </Button>
        </div>
      </div>

      {/* Bento Grid: Actions + Stats */}
      <div className="grid grid-cols-12 gap-4 md:gap-5">
        {/* Start Instant Meeting - Large Card */}
        <div className="col-span-12 md:col-span-7">
          <div
            className="relative group cursor-pointer overflow-hidden rounded-2xl border border-white/5 bg-gradient-to-br from-karau-card to-karau-panel p-6 md:p-8 hover:border-teal-500/30 transition-all duration-500"
            onClick={() => setShowCreateDialog(true)}
            data-testid="card-instant-meeting"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-teal-500/5 via-transparent to-emerald-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="relative z-10 flex items-start gap-5">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-teal-500 to-emerald-500 flex items-center justify-center shadow-lg shadow-teal-500/25 group-hover:scale-110 transition-transform duration-300">
                <Video className="w-8 h-8 text-white" />
              </div>
              <div className="flex-1">
                <h2 className="text-xl font-semibold text-white mb-1.5">{t("karauMeet.startInstantMeeting")}</h2>
                <p className="text-karau-muted text-sm leading-relaxed">{t("karauMeet.createNewMeetingNow")}</p>
                <div className="flex items-center gap-4 mt-4">
                  {features.slice(0, 3).map((f, i) => (
                    <span key={i} className="flex items-center gap-1.5 text-xs text-slate-500">
                      <f.icon className={`w-3 h-3 ${f.color}`} />{f.label}
                    </span>
                  ))}
                </div>
              </div>
              <ArrowRight className="w-5 h-5 text-slate-600 group-hover:text-teal-400 group-hover:translate-x-1 transition-all" />
            </div>
          </div>
        </div>

        {/* Join Meeting */}
        <div className="col-span-12 md:col-span-5">
          <div className="h-full rounded-2xl border border-white/5 bg-gradient-to-br from-karau-card to-karau-panel p-6 md:p-8 hover:border-amber-500/30 transition-all duration-300" data-testid="card-join-meeting">
            <div className="flex items-start gap-4 mb-5">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-amber-500/20 to-amber-600/10 flex items-center justify-center border border-amber-500/10">
                <Users className="w-7 h-7 text-amber-400" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-white">{t("meeting.joinMeeting")}</h2>
                <p className="text-karau-muted text-xs mt-0.5">Enter a meeting code to join</p>
              </div>
            </div>
            <div className="flex gap-2">
              <Input
                placeholder={t("meeting.enterMeetingId")}
                value={joinMeetingId}
                onChange={(e) => setJoinMeetingId(e.target.value.toUpperCase())}
                className="bg-karau-bg/60 border-white/10 text-white rounded-xl focus:border-amber-500/40 focus:ring-amber-500/20 font-mono tracking-wider"
                onKeyPress={(e) => e.key === 'Enter' && joinMeeting()}
                data-testid="input-join-id"
              />
              <Button onClick={joinMeeting} className="bg-amber-500/90 hover:bg-amber-400 text-black font-medium rounded-xl px-5 shadow-lg shadow-amber-500/15 hover:shadow-amber-500/25 transition-all" data-testid="btn-join">
                {t("meeting.join")}
              </Button>
            </div>
          </div>
        </div>

        {/* Stats Row */}
        {statItems.map((stat, idx) => (
          <div key={idx} className="col-span-6 md:col-span-3">
            <div className={`rounded-2xl border border-white/5 bg-gradient-to-br ${stat.color} backdrop-blur-sm p-4 md:p-5 ${stat.border} transition-all duration-300`} data-testid={`stat-${idx}`}>
              <div className="flex items-center justify-between mb-3">
                <stat.icon className={`w-5 h-5 ${stat.iconColor}`} />
                <Zap className="w-3 h-3 text-slate-700" />
              </div>
              <p className="text-2xl md:text-3xl font-bold text-white tracking-tight">{stat.value}</p>
              <p className="text-xs text-karau-muted mt-1">{stat.label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Feature Badges */}
      <div className="flex flex-wrap gap-3">
        {features.map((f, i) => (
          <div key={i} className={`flex items-center gap-2 px-4 py-2.5 ${f.bg} rounded-full border border-white/5`}>
            <f.icon className={`w-4 h-4 ${f.color}`} />
            <span className="text-xs font-medium text-slate-300">{f.label}</span>
          </div>
        ))}
      </div>

      {/* Recent Meetings */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <History className="w-4 h-4 text-karau-muted" />
          <h3 className="text-base font-semibold text-white">{t("karauMeet.recentMeetings")}</h3>
        </div>
        <div className="rounded-2xl border border-white/5 bg-karau-card/60 backdrop-blur-sm overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-6 h-6 text-teal-400 animate-spin" />
            </div>
          ) : meetings.length === 0 ? (
            <div className="text-center py-12" data-testid="no-meetings">
              <div className="w-16 h-16 rounded-2xl bg-karau-surface mx-auto mb-4 flex items-center justify-center">
                <Video className="w-8 h-8 text-slate-600" />
              </div>
              <p className="text-slate-400 font-medium">{t("karauMeet.noMeetingsYet")}</p>
              <p className="text-slate-500 text-sm mt-1">{t("karauMeet.startFirstMeeting")}</p>
            </div>
          ) : (
            <div className="divide-y divide-white/5">
              {meetings.slice(0, 6).map((meeting) => (
                <div key={meeting.meeting_id} className="flex items-center justify-between px-5 py-4 hover:bg-white/[0.02] transition-colors" data-testid={`meeting-${meeting.meeting_id}`}>
                  <div className="flex items-center gap-4">
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${meeting.status === 'active' ? 'bg-emerald-500/10 border border-emerald-500/20' : 'bg-karau-surface'}`}>
                      <Video className={`w-5 h-5 ${meeting.status === 'active' ? 'text-emerald-400' : 'text-slate-500'}`} />
                    </div>
                    <div>
                      <h4 className="font-medium text-white text-sm">{meeting.title}</h4>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-xs text-karau-muted">{new Date(meeting.created_at).toLocaleDateString()}</span>
                        <Badge className={`text-[10px] px-1.5 py-0 rounded-md ${
                          meeting.status === 'active' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                          meeting.status === 'ended' ? 'bg-slate-500/10 text-slate-500 border-slate-500/20' :
                          'bg-amber-500/10 text-amber-400 border-amber-500/20'
                        }`}>{meeting.status}</Badge>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Button variant="ghost" size="sm" onClick={() => setShareMeeting(meeting)} className="text-slate-500 hover:text-teal-400 rounded-lg h-8 w-8 p-0" data-testid={`share-meeting-${meeting.meeting_id}`}>
                      <Share2 className="w-3.5 h-3.5" />
                    </Button>
                    <Button variant="ghost" size="sm" onClick={() => copyMeetingLink(meeting.meeting_id)} className="text-slate-500 hover:text-white rounded-lg h-8 w-8 p-0">
                      <Copy className="w-3.5 h-3.5" />
                    </Button>
                    {meeting.status !== 'ended' && (
                      <Button size="sm" onClick={() => navigate(`/karau-meet/lobby/${meeting.meeting_id}`)} className={`rounded-lg text-xs px-3 h-8 ${meeting.status === 'active' ? 'bg-emerald-500 hover:bg-emerald-400 text-white' : 'bg-teal-500/80 hover:bg-teal-400 text-white'}`}>
                        {meeting.status === 'active' ? t("meeting.rejoin") : t("meeting.start")}
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Create Meeting Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="bg-karau-card border-white/10 rounded-2xl shadow-2xl shadow-black/50">
          <DialogHeader>
            <DialogTitle className="text-white font-semibold" style={{ fontFamily: "'IBM Plex Sans', sans-serif" }}>{t("karauMeet.createNewMeeting")}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label className="text-slate-300 text-sm">{t("karauMeet.meetingTitle")}</Label>
              <Input placeholder={t("karauMeet.meetingTitlePlaceholder")} value={newMeetingTitle} onChange={(e) => setNewMeetingTitle(e.target.value)} className="bg-karau-bg/60 border-white/10 text-white mt-2 rounded-xl focus:border-teal-500/40" data-testid="input-meeting-title" />
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
              <Button onClick={createMeeting} disabled={creating} className="bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-400 hover:to-emerald-400 text-white rounded-xl shadow-lg shadow-teal-500/20" data-testid="btn-create-meeting">
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
