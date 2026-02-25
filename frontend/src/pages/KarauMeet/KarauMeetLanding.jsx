import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import {
  Video, Plus, Calendar, Users, Clock, Shield,
  Sparkles, Copy, ExternalLink, Loader2, History,
  Settings, Mic, MonitorPlay
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { useTranslation } from '@/utils/i18n';

const API = process.env.REACT_APP_BACKEND_URL;

const KarauMeetLanding = ({ user }) => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [joinMeetingId, setJoinMeetingId] = useState('');
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newMeetingTitle, setNewMeetingTitle] = useState('');
  const [creating, setCreating] = useState(false);

  // Fetch user's meetings
  useEffect(() => {
    const fetchMeetings = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API}/api/karau-meet/meetings`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
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
    
    fetchMeetings();
  }, []);

  // Create new meeting
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
        body: JSON.stringify({
          title: newMeetingTitle || 'AI KARAU Meeting'
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        toast.success('Meeting created!');
        navigate(`/karau-meet/room/${data.meeting_id}`);
      } else {
        toast.error('Failed to create meeting');
      }
    } catch (error) {
      console.error('Error creating meeting:', error);
      toast.error('Failed to create meeting');
    }
    setCreating(false);
    setShowCreateDialog(false);
  };

  // Join existing meeting
  const joinMeeting = () => {
    if (!joinMeetingId.trim()) {
      toast.error('Please enter a meeting ID');
      return;
    }
    navigate(`/karau-meet/room/${joinMeetingId.toUpperCase()}`);
  };

  // Copy meeting link
  const copyMeetingLink = (meetingId) => {
    const link = `${window.location.origin}/karau-meet/join/${meetingId}`;
    navigator.clipboard.writeText(link);
    toast.success('Meeting link copied!');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Hero Section */}
      <div className="max-w-6xl mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-turquoise to-cyan-400 flex items-center justify-center">
              <Video className="w-8 h-8 text-white" />
            </div>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            AI KARAU <span className="text-turquoise">Meeting</span>
          </h1>
          <p className="text-xl text-slate-300 max-w-2xl mx-auto">
            {t("karauMeet.heroTagline")}
          </p>
        </div>

        {/* Action Cards */}
        <div className="grid md:grid-cols-2 gap-6 mb-12">
          {/* Start New Meeting */}
          <Card className="bg-slate-800/50 border-slate-700 hover:border-turquoise/50 transition-all cursor-pointer group"
                onClick={() => setShowCreateDialog(true)}>
            <CardContent className="p-8">
              <div className="flex items-start gap-4">
                <div className="w-14 h-14 rounded-xl bg-turquoise/20 flex items-center justify-center group-hover:bg-turquoise/30 transition-colors">
                  <Plus className="w-7 h-7 text-turquoise" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">{t("karauMeet.newMeeting")}</h3>
                  <p className="text-slate-400">{t("karauMeet.newMeetingDesc")}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Join Meeting */}
          <Card className="bg-slate-800/50 border-slate-700">
            <CardContent className="p-8">
              <div className="flex items-start gap-4">
                <div className="w-14 h-14 rounded-xl bg-violet-500/20 flex items-center justify-center">
                  <Users className="w-7 h-7 text-violet-400" />
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-white mb-2">{t("meeting.joinMeeting")}</h3>
                  <div className="flex gap-2">
                    <Input
                      placeholder={t("meeting.enterMeetingId")}
                      value={joinMeetingId}
                      onChange={(e) => setJoinMeetingId(e.target.value.toUpperCase())}
                      className="bg-slate-900 border-slate-600 text-white"
                      onKeyPress={(e) => e.key === 'Enter' && joinMeeting()}
                    />
                    <Button onClick={joinMeeting} className="bg-violet-500 hover:bg-violet-600">
                      {t("meeting.join")}
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Features */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
          {[
            { icon: Shield, label: t("karauMeet.endToEndEncrypted"), color: 'text-green-400' },
            { icon: Sparkles, label: t("karauMeet.aiNotesTranscription"), color: 'text-turquoise' },
            { icon: MonitorPlay, label: t("karauMeet.screenSharing"), color: 'text-blue-400' },
            { icon: Users, label: t("karauMeet.breakoutRooms"), color: 'text-violet-400' }
          ].map((feature, idx) => (
            <div key={idx} className="flex items-center gap-2 p-4 bg-slate-800/30 rounded-lg">
              <feature.icon className={`w-5 h-5 ${feature.color}`} />
              <span className="text-sm text-slate-300">{feature.label}</span>
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
            <CardDescription className="text-slate-400">
              {t("karauMeet.meetingHistory")}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-6 h-6 text-turquoise animate-spin" />
              </div>
            ) : meetings.length === 0 ? (
              <div className="text-center py-8">
                <Video className="w-12 h-12 text-slate-600 mx-auto mb-3" />
                <p className="text-slate-400">{t("karauMeet.noMeetingsHistory")}</p>
              </div>
            ) : (
              <div className="space-y-3">
                {meetings.slice(0, 5).map((meeting) => (
                  <div
                    key={meeting.meeting_id}
                    className="flex items-center justify-between p-4 bg-slate-900/50 rounded-lg hover:bg-slate-900 transition-colors"
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
                        onClick={(e) => { e.stopPropagation(); copyMeetingLink(meeting.meeting_id); }}
                        className="text-slate-400 hover:text-white"
                      >
                        <Copy className="w-4 h-4" />
                      </Button>
                      {meeting.status !== 'ended' && (
                        <Button
                          size="sm"
                          onClick={() => navigate(`/karau-meet/room/${meeting.meeting_id}`)}
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
      </div>

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
                <p className="text-xs text-slate-500">{t("karauMeet.recordTheConsentShort")}</p>
              </div>
              <Switch defaultChecked />
            </div>
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setShowCreateDialog(false)} className="text-slate-300">
              {t("karauMeet.cancel")}
            </Button>
            <Button onClick={createMeeting} disabled={creating} className="bg-turquoise hover:bg-turquoise/80">
              {creating ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
              {t("karauMeet.startMeeting")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default KarauMeetLanding;
