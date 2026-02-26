import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import {
  Video, Plus, Clock, Shield, Sparkles, Copy,
  Loader2, History, MonitorPlay, Users, Archive, Share2
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

/**
 * Main Dashboard for AI KARAU Meeting Portal
 */
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
  const [stats, setStats] = useState({
    total_meetings: 0,
    total_hours: 0,
    recordings: 0,
    participants: 0
  });

  useEffect(() => {
    fetchMeetings();
    setStats({
      total_meetings: 24,
      total_hours: 48,
      recordings: 12,
      participants: 156
    });
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
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
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
    if (!joinMeetingId.trim()) {
      toast.error(t("karauMeet.enterMeetingIdError"));
      return;
    }
    navigate(`/karau-meet/lobby/${joinMeetingId.toUpperCase()}`);
  };

  const copyMeetingLink = (meetingId) => {
    const link = `${window.location.origin}/karau-meet/join/${meetingId}`;
    navigator.clipboard.writeText(link);
    toast.success(t("karauMeet.meetingLinkCopied"));
  };

  return (
    <div className="p-6 space-y-6">
      {/* Welcome Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white" data-testid="dashboard-welcome">
            {t("karauMeet.welcomeBack", { name: user?.name?.split(' ')[0] || 'User' })}
          </h1>
          <p className="text-slate-400">{t("karauMeet.readyForMeeting")}</p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            onClick={() => setShowCreateDialog(true)}
            className="bg-gradient-to-r from-turquoise to-cyan-500 hover:from-turquoise/90 hover:to-cyan-500/90"
            data-testid="btn-new-meeting"
          >
            <Plus className="w-4 h-4 mr-2" />
            {t("karauMeet.newMeeting")}
          </Button>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid md:grid-cols-2 gap-4">
        {/* Start Instant Meeting */}
        <Card 
          className="bg-slate-800/50 border-slate-700 hover:border-turquoise/50 transition-all cursor-pointer group"
          onClick={() => setShowCreateDialog(true)}
          data-testid="card-instant-meeting"
        >
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-turquoise to-cyan-400 flex items-center justify-center group-hover:scale-105 transition-transform">
                <Video className="w-7 h-7 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white mb-1">{t("karauMeet.startInstantMeeting")}</h3>
                <p className="text-slate-400 text-sm">{t("karauMeet.createNewMeetingNow")}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Join Meeting */}
        <Card className="bg-slate-800/50 border-slate-700" data-testid="card-join-meeting">
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <div className="w-14 h-14 rounded-xl bg-violet-500/20 flex items-center justify-center">
                <Users className="w-7 h-7 text-violet-400" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-white mb-2">{t("meeting.joinMeeting")}</h3>
                <div className="flex gap-2">
                  <Input
                    placeholder={t("meeting.enterMeetingId")}
                    value={joinMeetingId}
                    onChange={(e) => setJoinMeetingId(e.target.value.toUpperCase())}
                    className="bg-slate-900 border-slate-600 text-white"
                    onKeyPress={(e) => e.key === 'Enter' && joinMeeting()}
                    data-testid="input-join-id"
                  />
                  <Button onClick={joinMeeting} className="bg-violet-500 hover:bg-violet-600" data-testid="btn-join">
                    {t("meeting.join")}
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: t("karauMeet.totalMeetings"), value: stats.total_meetings, icon: Video, color: 'text-turquoise' },
          { label: t("karauMeet.hoursInMeetings"), value: stats.total_hours, icon: Clock, color: 'text-blue-400' },
          { label: t("karauMeet.recordings"), value: stats.recordings, icon: Archive, color: 'text-violet-400' },
          { label: t("karauMeet.participantsMet"), value: stats.participants, icon: Users, color: 'text-green-400' },
        ].map((stat, idx) => (
          <Card key={idx} className="bg-slate-800/30 border-slate-700" data-testid={`stat-${stat.label.toLowerCase().replace(' ', '-')}`}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-2xl font-bold text-white">{stat.value}</p>
                  <p className="text-xs text-slate-400">{stat.label}</p>
                </div>
                <stat.icon className={`w-8 h-8 ${stat.color} opacity-50`} />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Features */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { icon: Shield, label: t("karauMeet.endToEndEncrypted"), color: 'text-green-400' },
          { icon: Sparkles, label: t("karauMeet.aiNotesTranscription"), color: 'text-turquoise' },
          { icon: MonitorPlay, label: t("karauMeet.screenSharing"), color: 'text-blue-400' },
          { icon: Users, label: t("karauMeet.breakoutRooms"), color: 'text-violet-400' }
        ].map((feature, idx) => (
          <div key={idx} className="flex items-center gap-2 p-3 bg-slate-800/30 rounded-lg border border-slate-700/50">
            <feature.icon className={`w-4 h-4 ${feature.color}`} />
            <span className="text-xs text-slate-300">{feature.label}</span>
          </div>
        ))}
      </div>

      {/* Recent Meetings */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <History className="w-5 h-5 text-slate-400" />
            {t("karauMeet.recentMeetings")}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-6 h-6 text-turquoise animate-spin" />
            </div>
          ) : meetings.length === 0 ? (
            <div className="text-center py-8" data-testid="no-meetings">
              <Video className="w-12 h-12 text-slate-600 mx-auto mb-3" />
              <p className="text-slate-400">{t("karauMeet.noMeetingsYet")}</p>
              <p className="text-slate-500 text-sm">{t("karauMeet.startFirstMeeting")}</p>
            </div>
          ) : (
            <div className="space-y-3">
              {meetings.slice(0, 5).map((meeting) => (
                <div
                  key={meeting.meeting_id}
                  className="flex items-center justify-between p-4 bg-slate-900/50 rounded-lg hover:bg-slate-900 transition-colors"
                  data-testid={`meeting-${meeting.meeting_id}`}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-turquoise/20 flex items-center justify-center">
                      <Video className="w-5 h-5 text-turquoise" />
                    </div>
                    <div>
                      <h4 className="font-medium text-white">{meeting.title}</h4>
                      <div className="flex items-center gap-2 text-sm text-slate-400">
                        <Clock className="w-3 h-3" />
                        {new Date(meeting.created_at).toLocaleDateString()}
                        <Badge variant="outline" className={
                          meeting.status === 'active' ? 'text-green-400 border-green-400/30' :
                          meeting.status === 'ended' ? 'text-slate-400 border-slate-400/30' :
                          'text-yellow-400 border-yellow-400/30'
                        }>
                          {meeting.status}
                        </Badge>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShareMeeting(meeting)}
                      className="text-slate-400 hover:text-turquoise"
                      data-testid={`share-meeting-${meeting.meeting_id}`}
                    >
                      <Share2 className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => copyMeetingLink(meeting.meeting_id)}
                      className="text-slate-400 hover:text-white"
                    >
                      <Copy className="w-4 h-4" />
                    </Button>
                    {meeting.status !== 'ended' && (
                      <Button
                        size="sm"
                        onClick={() => navigate(`/karau-meet/lobby/${meeting.meeting_id}`)}
                        className="bg-turquoise hover:bg-turquoise/80"
                      >
                        {meeting.status === 'active' ? t("meeting.rejoin") : t("meeting.start")}
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Create Meeting Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="bg-slate-800 border-slate-700">
          <DialogHeader>
            <DialogTitle className="text-white">{t("karauMeet.createNewMeeting")}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label className="text-slate-300">{t("karauMeet.meetingTitle")}</Label>
              <Input
                placeholder={t("karauMeet.meetingTitlePlaceholder")}
                value={newMeetingTitle}
                onChange={(e) => setNewMeetingTitle(e.target.value)}
                className="bg-slate-900 border-slate-600 text-white mt-2"
                data-testid="input-meeting-title"
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <Label className="text-slate-300">{t("karauMeet.enableAINotes")}</Label>
                <p className="text-xs text-slate-500">{t("karauMeet.autoTranscription")}</p>
              </div>
              <Switch defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <Label className="text-slate-300">{t("karauMeet.enableRecording")}</Label>
                <p className="text-xs text-slate-500">{t("karauMeet.recordingConsent")}</p>
              </div>
              <Switch defaultChecked />
            </div>
          </div>
          <DialogFooter className="flex-col sm:flex-row gap-2">
            <Button variant="ghost" onClick={() => setShowCreateDialog(false)} className="text-slate-300">
              {t("karauMeet.cancel")}
            </Button>
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={async () => {
                  setCreating(true);
                  try {
                    const token = localStorage.getItem('token');
                    const response = await fetch(`${API}/api/karau-meet/meetings`, {
                      method: 'POST',
                      headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                      },
                      body: JSON.stringify({ title: newMeetingTitle || 'AI KARAU Meeting' })
                    });
                    if (response.ok) {
                      const data = await response.json();
                      setShowCreateDialog(false);
                      setShareMeeting({ meeting_id: data.meeting_id, title: newMeetingTitle || 'AI KARAU Meeting' });
                      fetchMeetings();
                      toast.success(t("karauMeet.meetingCreatedShare"));
                    } else {
                      toast.error(t("karauMeet.failedCreate"));
                    }
                  } catch { toast.error(t("karauMeet.failedCreate")); }
                  setCreating(false);
                }}
                disabled={creating}
                className="border-slate-600 text-slate-300 hover:bg-slate-700"
                data-testid="btn-create-and-share"
              >
                {creating ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Share2 className="w-4 h-4 mr-2" />}
                {t("karauMeet.createAndShare")}
              </Button>
              <Button onClick={createMeeting} disabled={creating} className="bg-turquoise hover:bg-turquoise/80" data-testid="btn-create-meeting">
                {creating ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                {t("karauMeet.startMeeting")}
              </Button>
            </div>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Share Meeting Dialog */}
      {shareMeeting && (
        <ShareMeetingDialog
          isOpen={!!shareMeeting}
          onClose={() => setShareMeeting(null)}
          meetingId={shareMeeting.meeting_id}
          meetingTitle={shareMeeting.title}
        />
      )}
    </div>
  );
};

export default KarauMeetDashboard;
