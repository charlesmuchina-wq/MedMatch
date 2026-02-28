import { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { toast } from 'sonner';
import {
  Video, Users, Calendar, Clock, Shield, Loader2, Play, Square,
  Mic, MicOff, MessageSquare, HelpCircle, ChevronUp, ChevronDown,
  Send, ThumbsUp, X, Settings, BarChart3, Radio, UserCheck
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { useTranslation } from '@/utils/i18n';

const API = process.env.REACT_APP_BACKEND_URL;

// ===================== Registration Page =====================
export const WebinarRegistrationPage = () => {
  const { webinarId } = useParams();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [webinar, setWebinar] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({ name: '', email: '', organization: '', role: '' });
  const [registered, setRegistered] = useState(false);
  const [joinUrl, setJoinUrl] = useState('');

  useEffect(() => { fetchWebinar(); }, [webinarId]);

  const fetchWebinar = async () => {
    try {
      const res = await fetch(`${API}/api/karau/webinar/${webinarId}`);
      if (res.ok) setWebinar(await res.json());
    } catch {}
    setLoading(false);
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    if (!form.name.trim() || !form.email.trim()) return toast.error('Name and email required');
    setSubmitting(true);
    try {
      const res = await fetch(`${API}/api/karau/webinar/${webinarId}/register`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setRegistered(true);
        setJoinUrl(data.join_url);
        toast.success(t("karauMeet.registrationSuccess") || "Successfully registered!");
      } else {
        toast.error(data.detail || 'Registration failed');
      }
    } catch { toast.error('Network error'); }
    setSubmitting(false);
  };

  if (loading) return <div className="min-h-screen bg-karau-bg flex items-center justify-center"><Loader2 className="w-8 h-8 text-purple-400 animate-spin" /></div>;
  if (!webinar) return <div className="min-h-screen bg-karau-bg flex items-center justify-center"><p className="text-red-400">Webinar not found</p></div>;

  return (
    <div className="min-h-screen bg-karau-bg flex items-center justify-center p-4" style={{ fontFamily: "'IBM Plex Sans', sans-serif" }}>
      <Card className="w-full max-w-lg bg-karau-card/80 backdrop-blur-xl border-karau-border rounded-2xl" data-testid="webinar-register-card">
        <CardHeader className="text-center pb-3">
          <div className="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center mx-auto mb-3">
            <Radio className="w-6 h-6 text-purple-400" />
          </div>
          <CardTitle className="text-xl text-white">{webinar.title}</CardTitle>
          <CardDescription className="text-karau-muted">{webinar.description}</CardDescription>
          <div className="flex items-center justify-center gap-4 mt-3 text-xs text-slate-400">
            <span className="flex items-center gap-1"><Calendar className="w-3 h-3" />{new Date(webinar.scheduled_time).toLocaleDateString()}</span>
            <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{new Date(webinar.scheduled_time).toLocaleTimeString()}</span>
            <span className="flex items-center gap-1"><Users className="w-3 h-3" />{webinar.registered_count}/{webinar.max_attendees}</span>
          </div>
          <p className="text-xs text-slate-500 mt-1">{t("karauMeet.hostedBy") || "Hosted by"} {webinar.host_name}</p>
        </CardHeader>

        <CardContent>
          {registered ? (
            <div className="text-center py-4" data-testid="registration-success">
              <div className="w-14 h-14 rounded-full bg-emerald-500/10 flex items-center justify-center mx-auto mb-3">
                <UserCheck className="w-7 h-7 text-emerald-400" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-1">{t("karauMeet.youreRegistered") || "You're Registered!"}</h3>
              <p className="text-sm text-karau-muted mb-4">{t("karauMeet.joinWhenLive") || "You'll be able to join when the webinar goes live."}</p>
              <Button onClick={() => navigate(`/karau-meet/webinar/${webinarId}/live`)} className="bg-gradient-to-r from-purple-600 to-violet-600 rounded-xl" data-testid="join-webinar-btn">
                <Video className="w-4 h-4 mr-2" />{t("karauMeet.joinWebinar") || "Join Webinar"}
              </Button>
            </div>
          ) : (
            <form onSubmit={handleRegister} className="space-y-3" data-testid="webinar-register-form">
              <div>
                <label className="text-xs text-slate-300 mb-1 block">{t("karauMeet.yourName")}</label>
                <Input value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                  className="bg-karau-bg/60 border-white/10 text-white rounded-xl" required data-testid="webinar-name" />
              </div>
              <div>
                <label className="text-xs text-slate-300 mb-1 block">{t("karauMeet.emailAddress")}</label>
                <Input type="email" value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
                  className="bg-karau-bg/60 border-white/10 text-white rounded-xl" required data-testid="webinar-email" />
              </div>
              <div>
                <label className="text-xs text-slate-300 mb-1 block">{t("karauMeet.organization") || "Organization"}</label>
                <Input value={form.organization} onChange={e => setForm(f => ({ ...f, organization: e.target.value }))}
                  className="bg-karau-bg/60 border-white/10 text-white rounded-xl" data-testid="webinar-org" />
              </div>
              <Button type="submit" disabled={submitting}
                className="w-full bg-gradient-to-r from-purple-600 to-violet-600 hover:from-purple-500 hover:to-violet-500 h-11 rounded-xl" data-testid="webinar-register-btn">
                {submitting ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <UserCheck className="w-4 h-4 mr-2" />}
                {t("karauMeet.registerNow") || "Register Now"}
              </Button>
              <div className="flex items-center justify-center gap-4 text-[10px] text-slate-500 mt-2">
                <span className="flex items-center gap-1"><Shield className="w-3 h-3 text-emerald-400" />{t("karauMeet.encrypted")}</span>
                <span className="flex items-center gap-1"><Video className="w-3 h-3 text-purple-400" />{t("karauMeet.aiPowered")}</span>
              </div>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  );
};


// ===================== Webinar Host Console =====================
export const WebinarHostConsole = ({ webinarId, user }) => {
  const { t } = useTranslation();
  const [webinar, setWebinar] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [controlsOpen, setControlsOpen] = useState(true);
  const [answerText, setAnswerText] = useState({});

  useEffect(() => { fetchData(); }, [webinarId]);

  const fetchData = async () => {
    const token = localStorage.getItem('token');
    try {
      const [wRes, qRes] = await Promise.all([
        fetch(`${API}/api/karau/webinar/${webinarId}`, { headers: { 'Authorization': `Bearer ${token}` } }),
        fetch(`${API}/api/karau/webinar/${webinarId}/qa`, { headers: { 'Authorization': `Bearer ${token}` } })
      ]);
      if (wRes.ok) setWebinar(await wRes.json());
      if (qRes.ok) { const d = await qRes.json(); setQuestions(d.questions || []); }
    } catch {}
    setLoading(false);
  };

  const startWebinar = async () => {
    const token = localStorage.getItem('token');
    const res = await fetch(`${API}/api/karau/webinar/${webinarId}/start`, { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } });
    if (res.ok) { toast.success('Webinar started!'); fetchData(); }
  };

  const endWebinar = async () => {
    const token = localStorage.getItem('token');
    const res = await fetch(`${API}/api/karau/webinar/${webinarId}/end`, { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } });
    if (res.ok) { toast.success('Webinar ended'); fetchData(); }
  };

  const muteAll = async () => {
    const token = localStorage.getItem('token');
    await fetch(`${API}/api/karau/webinar/${webinarId}/controls/mute-all`, { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } });
    toast.success('All attendees muted');
  };

  const toggleChat = async (enabled) => {
    const token = localStorage.getItem('token');
    await fetch(`${API}/api/karau/webinar/${webinarId}/controls/disable-chat?enabled=${enabled}`, {
      method: 'POST', headers: { 'Authorization': `Bearer ${token}` }
    });
    toast.success(enabled ? 'Chat enabled' : 'Chat disabled');
  };

  const answerQuestion = async (qId) => {
    if (!answerText[qId]?.trim()) return;
    const token = localStorage.getItem('token');
    const res = await fetch(`${API}/api/karau/webinar/${webinarId}/qa/${qId}/answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ answer: answerText[qId] })
    });
    if (res.ok) { setAnswerText(prev => ({ ...prev, [qId]: '' })); fetchData(); toast.success('Answer posted'); }
  };

  const dismissQuestion = async (qId) => {
    const token = localStorage.getItem('token');
    await fetch(`${API}/api/karau/webinar/${webinarId}/qa/${qId}/dismiss`, { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } });
    fetchData();
  };

  if (loading) return <div className="p-4"><Loader2 className="w-5 h-5 text-purple-400 animate-spin" /></div>;
  if (!webinar) return null;

  const pendingQs = questions.filter(q => q.status === 'pending');
  const answeredQs = questions.filter(q => q.status === 'answered');

  return (
    <div className="space-y-3 p-3" data-testid="webinar-host-console">
      {/* Status Bar */}
      <div className="flex items-center justify-between p-3 bg-karau-card/60 rounded-xl border border-white/5">
        <div className="flex items-center gap-2">
          {webinar.status === 'live' ? (
            <Badge className="bg-red-500/20 text-red-400 animate-pulse"><Radio className="w-3 h-3 mr-1" />LIVE</Badge>
          ) : (
            <Badge className="bg-slate-500/20 text-slate-400">{webinar.status}</Badge>
          )}
          <span className="text-sm text-white font-medium">{webinar.title}</span>
        </div>
        <div className="flex gap-2">
          {webinar.status === 'scheduled' && (
            <Button size="sm" onClick={startWebinar} className="bg-emerald-500 hover:bg-emerald-400 rounded-lg h-8" data-testid="start-webinar-btn">
              <Play className="w-3.5 h-3.5 mr-1" />{t("karauMeet.startWebinar") || "Start"}
            </Button>
          )}
          {webinar.status === 'live' && (
            <Button size="sm" onClick={endWebinar} variant="destructive" className="rounded-lg h-8" data-testid="end-webinar-btn">
              <Square className="w-3.5 h-3.5 mr-1" />{t("karauMeet.endWebinar") || "End"}
            </Button>
          )}
        </div>
      </div>

      {/* Host Controls */}
      <div className="bg-karau-card/40 rounded-xl border border-white/5">
        <button onClick={() => setControlsOpen(!controlsOpen)}
          className="w-full flex items-center justify-between p-3 text-sm text-white font-medium" data-testid="toggle-controls">
          <span className="flex items-center gap-2"><Settings className="w-4 h-4 text-purple-400" />{t("karauMeet.hostControls") || "Host Controls"}</span>
          {controlsOpen ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
        </button>
        {controlsOpen && (
          <div className="px-3 pb-3 space-y-2">
            <div className="flex items-center justify-between p-2 bg-karau-bg/40 rounded-lg">
              <span className="text-xs text-slate-300 flex items-center gap-1.5"><MicOff className="w-3 h-3" />{t("karauMeet.muteAllAttendees") || "Mute All"}</span>
              <Button size="sm" variant="outline" onClick={muteAll} className="h-7 text-xs border-white/10 rounded-lg" data-testid="mute-all-btn">
                <MicOff className="w-3 h-3 mr-1" />{t("karauMeet.muteAll") || "Mute All"}
              </Button>
            </div>
            <div className="flex items-center justify-between p-2 bg-karau-bg/40 rounded-lg">
              <span className="text-xs text-slate-300 flex items-center gap-1.5"><MessageSquare className="w-3 h-3" />{t("karauMeet.attendeeChat") || "Attendee Chat"}</span>
              <Switch defaultChecked={webinar.settings?.chat_enabled} onCheckedChange={toggleChat} data-testid="chat-toggle" />
            </div>
            <div className="flex items-center gap-4 p-2 bg-karau-bg/40 rounded-lg text-xs text-slate-400">
              <span className="flex items-center gap-1"><Users className="w-3 h-3" />{webinar.registered_count} {t("karauMeet.registered") || "registered"}</span>
              <span className="flex items-center gap-1"><HelpCircle className="w-3 h-3" />{questions.length} {t("karauMeet.questions") || "questions"}</span>
            </div>
          </div>
        )}
      </div>

      {/* Q&A Panel */}
      <div className="bg-karau-card/40 rounded-xl border border-white/5 p-3" data-testid="qa-panel">
        <h4 className="text-sm font-medium text-white flex items-center gap-2 mb-3">
          <HelpCircle className="w-4 h-4 text-amber-400" />
          Q&A ({pendingQs.length} {t("karauMeet.pending") || "pending"})
        </h4>
        {pendingQs.length === 0 ? (
          <p className="text-xs text-slate-500 text-center py-4">{t("karauMeet.noQuestions") || "No questions yet"}</p>
        ) : (
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {pendingQs.map(q => (
              <div key={q.question_id} className="p-2 bg-karau-bg/40 rounded-lg" data-testid={`qa-${q.question_id}`}>
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1">
                    <p className="text-xs text-white">{q.question}</p>
                    <div className="flex items-center gap-2 mt-1 text-[10px] text-slate-500">
                      <span>{q.asked_by}</span>
                      <span className="flex items-center gap-0.5"><ThumbsUp className="w-2.5 h-2.5" />{q.upvotes}</span>
                    </div>
                  </div>
                  <button onClick={() => dismissQuestion(q.question_id)} className="p-1 hover:bg-red-500/10 rounded">
                    <X className="w-3 h-3 text-red-400" />
                  </button>
                </div>
                <div className="flex gap-1 mt-2">
                  <Input value={answerText[q.question_id] || ''} onChange={e => setAnswerText(prev => ({ ...prev, [q.question_id]: e.target.value }))}
                    placeholder={t("karauMeet.typeAnswer") || "Type answer..."} className="bg-karau-card border-white/10 text-white text-xs h-7 rounded-lg" />
                  <Button size="sm" onClick={() => answerQuestion(q.question_id)} className="h-7 px-2 bg-emerald-500/80 rounded-lg">
                    <Send className="w-3 h-3" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};


// ===================== Create Webinar Dialog Content =====================
export const CreateWebinarForm = ({ onCreated, onCancel }) => {
  const { t } = useTranslation();
  const [form, setForm] = useState({
    title: '', description: '', scheduled_time: '',
    max_attendees: 1000, registration_required: true,
    q_and_a_enabled: true, chat_enabled: true,
    attendee_video: false, attendee_audio: false,
    panelist_emails: '', coordinator_emails: ''
  });
  const [creating, setCreating] = useState(false);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!form.title.trim() || !form.scheduled_time) return toast.error('Title and time required');
    setCreating(true);
    const token = localStorage.getItem('token');
    try {
      const payload = {
        ...form,
        panelist_emails: form.panelist_emails.split(',').map(e => e.trim()).filter(Boolean)
      };
      const res = await fetch(`${API}/api/karau/webinar/create`, {
        method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const data = await res.json();
        toast.success(t("karauMeet.webinarCreated") || "Webinar created!");
        if (onCreated) onCreated(data);
      } else { const e = await res.json(); toast.error(e.detail || 'Failed'); }
    } catch { toast.error('Network error'); }
    setCreating(false);
  };

  return (
    <form onSubmit={handleCreate} className="space-y-3" data-testid="create-webinar-form">
      <div>
        <label className="text-xs text-slate-300 mb-1 block">{t("karauMeet.webinarTitle") || "Webinar Title"}</label>
        <Input value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
          className="bg-karau-bg/60 border-white/10 text-white rounded-xl" required data-testid="webinar-title-input" />
      </div>
      <div>
        <label className="text-xs text-slate-300 mb-1 block">{t("karauMeet.description") || "Description"}</label>
        <textarea value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
          className="w-full bg-karau-bg/60 border border-white/10 text-white rounded-xl px-3 py-2 text-sm h-16" />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="text-xs text-slate-300 mb-1 block">{t("karauMeet.dateTime") || "Date & Time"}</label>
          <Input type="datetime-local" value={form.scheduled_time} onChange={e => setForm(f => ({ ...f, scheduled_time: e.target.value }))}
            className="bg-karau-bg/60 border-white/10 text-white rounded-xl" required data-testid="webinar-time-input" />
        </div>
        <div>
          <label className="text-xs text-slate-300 mb-1 block">{t("karauMeet.maxAttendees") || "Max Attendees"}</label>
          <Input type="number" value={form.max_attendees} onChange={e => setForm(f => ({ ...f, max_attendees: parseInt(e.target.value) || 1000 }))}
            className="bg-karau-bg/60 border-white/10 text-white rounded-xl" min={10} max={10000} data-testid="webinar-max-input" />
        </div>
      </div>
      <div>
        <label className="text-xs text-slate-300 mb-1 block">{t("karauMeet.panelistEmails") || "Panelist Emails (comma-separated)"}</label>
        <Input value={form.panelist_emails} onChange={e => setForm(f => ({ ...f, panelist_emails: e.target.value }))}
          placeholder="panelist1@org.com, panelist2@org.com"
          className="bg-karau-bg/60 border-white/10 text-white rounded-xl" />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div className="flex items-center justify-between p-2 bg-karau-bg/40 rounded-lg">
          <span className="text-xs text-slate-300">Q&A</span>
          <Switch checked={form.q_and_a_enabled} onCheckedChange={v => setForm(f => ({ ...f, q_and_a_enabled: v }))} />
        </div>
        <div className="flex items-center justify-between p-2 bg-karau-bg/40 rounded-lg">
          <span className="text-xs text-slate-300">{t("karauMeet.attendeeChat") || "Chat"}</span>
          <Switch checked={form.chat_enabled} onCheckedChange={v => setForm(f => ({ ...f, chat_enabled: v }))} />
        </div>
        <div className="flex items-center justify-between p-2 bg-karau-bg/40 rounded-lg">
          <span className="text-xs text-slate-300">{t("karauMeet.attendeeVideo") || "Attendee Video"}</span>
          <Switch checked={form.attendee_video} onCheckedChange={v => setForm(f => ({ ...f, attendee_video: v }))} />
        </div>
        <div className="flex items-center justify-between p-2 bg-karau-bg/40 rounded-lg">
          <span className="text-xs text-slate-300">{t("karauMeet.requireRegistration") || "Registration"}</span>
          <Switch checked={form.registration_required} onCheckedChange={v => setForm(f => ({ ...f, registration_required: v }))} />
        </div>
      </div>
      <div className="flex gap-2 pt-1">
        <Button type="submit" disabled={creating}
          className="flex-1 bg-gradient-to-r from-purple-600 to-violet-600 hover:from-purple-500 hover:to-violet-500 rounded-xl" data-testid="create-webinar-submit">
          {creating ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Radio className="w-4 h-4 mr-2" />}
          {t("karauMeet.createWebinar") || "Create Webinar"}
        </Button>
        {onCancel && <Button type="button" variant="outline" onClick={onCancel} className="border-white/10 text-slate-300 rounded-xl">{t("karauMeet.cancel")}</Button>}
      </div>
    </form>
  );
};

export default WebinarRegistrationPage;
