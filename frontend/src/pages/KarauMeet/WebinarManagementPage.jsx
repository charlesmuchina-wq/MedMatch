import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import {
  Radio, Plus, Users, Calendar, Clock, BarChart3,
  Loader2, ExternalLink, Copy, Check, Trash2, Play, Square, Video
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { useTranslation } from '@/utils/i18n';
import { CreateWebinarForm } from './WebinarPage';
import WebinarAnalyticsPage from './WebinarAnalyticsPage';

const API = process.env.REACT_APP_BACKEND_URL;

const WebinarManagementPage = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [webinars, setWebinars] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [copiedId, setCopiedId] = useState(null);
  const [analyticsWebinarId, setAnalyticsWebinarId] = useState(null);

  useEffect(() => { fetchWebinars(); }, []);

  const fetchWebinars = async () => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/webinar/list`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setWebinars(data.webinars || []);
      }
    } catch (e) { console.error('Webinar fetch error:', e); }
    setLoading(false);
  };

  const handleCreated = (webinar) => {
    setShowCreate(false);
    fetchWebinars();
  };

  const startWebinar = async (webinarId) => {
    const token = localStorage.getItem('token');
    const res = await fetch(`${API}/api/karau/webinar/${webinarId}/start`, {
      method: 'POST', headers: { 'Authorization': `Bearer ${token}` }
    });
    if (res.ok) { toast.success('Webinar started!'); fetchWebinars(); }
  };

  const endWebinar = async (webinarId) => {
    const token = localStorage.getItem('token');
    const res = await fetch(`${API}/api/karau/webinar/${webinarId}/end`, {
      method: 'POST', headers: { 'Authorization': `Bearer ${token}` }
    });
    if (res.ok) { toast.success('Webinar ended'); fetchWebinars(); }
  };

  const copyRegLink = (webinarId) => {
    const url = `${window.location.origin}/karau-meet/webinar/${webinarId}/register`;
    navigator.clipboard.writeText(url);
    setCopiedId(webinarId);
    setTimeout(() => setCopiedId(null), 2000);
    toast.success('Registration link copied');
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'live':
        return <Badge className="bg-red-500/20 text-red-400 border-red-500/20 animate-pulse" data-testid="badge-live"><Radio className="w-2.5 h-2.5 mr-1" />LIVE</Badge>;
      case 'practice':
        return <Badge className="bg-amber-500/20 text-amber-400 border-amber-500/20" data-testid="badge-practice">Practice</Badge>;
      case 'ended':
        return <Badge className="bg-slate-500/20 text-slate-400 border-slate-500/20" data-testid="badge-ended">Ended</Badge>;
      default:
        return <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/20" data-testid="badge-scheduled">Scheduled</Badge>;
    }
  };

  return (
    <div className="p-4 md:p-6 max-w-5xl" style={{ fontFamily: "'IBM Plex Sans', sans-serif" }}>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2" data-testid="webinar-page-title">
            <Radio className="w-5 h-5 text-purple-400" />
            {t("karauMeet.webinars") || "Webinars"}
          </h1>
          <p className="text-xs text-karau-muted mt-1">
            {t("karauMeet.webinarDesc") || "Host large-scale events with 1000+ attendees, Q&A, and audience controls"}
          </p>
        </div>
        <Button
          onClick={() => setShowCreate(true)}
          className="bg-gradient-to-r from-purple-600 to-violet-600 hover:from-purple-500 hover:to-violet-500 rounded-xl text-sm h-9"
          data-testid="new-webinar-btn"
        >
          <Plus className="w-4 h-4 mr-1.5" />{t("karauMeet.newWebinar") || "New Webinar"}
        </Button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="w-6 h-6 text-purple-400 animate-spin" />
        </div>
      ) : webinars.length === 0 ? (
        <div className="text-center py-16" data-testid="no-webinars">
          <div className="w-16 h-16 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center mx-auto mb-4">
            <Radio className="w-8 h-8 text-purple-400/50" />
          </div>
          <h3 className="text-base font-medium text-white mb-1">{t("karauMeet.noWebinars") || "No webinars yet"}</h3>
          <p className="text-xs text-karau-muted mb-4">{t("karauMeet.createFirstWebinar") || "Create your first webinar to host large-scale events"}</p>
          <Button onClick={() => setShowCreate(true)} className="bg-gradient-to-r from-purple-600 to-violet-600 rounded-xl text-sm" data-testid="create-first-webinar-btn">
            <Plus className="w-4 h-4 mr-1.5" />{t("karauMeet.createWebinar") || "Create Webinar"}
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3" data-testid="webinar-list">
          {webinars.map(w => (
            <Card key={w.webinar_id} className="bg-karau-card/40 border-white/5 hover:border-purple-500/20 transition-all rounded-xl overflow-hidden" data-testid={`webinar-card-${w.webinar_id}`}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-semibold text-white truncate">{w.title}</h3>
                    <div className="flex items-center gap-3 mt-1.5 text-[10px] text-slate-400">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {w.scheduled_time ? new Date(w.scheduled_time).toLocaleDateString() : 'TBD'}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {w.scheduled_time ? new Date(w.scheduled_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '--:--'}
                      </span>
                    </div>
                  </div>
                  {getStatusBadge(w.status)}
                </div>

                <div className="flex items-center gap-4 mb-3 text-[10px]">
                  <span className="flex items-center gap-1 text-slate-400">
                    <Users className="w-3 h-3 text-purple-400" />
                    <span className="text-slate-300 font-medium">{w.registered_count || 0}</span>
                    <span>/ {w.max_attendees}</span>
                  </span>
                  {w.analytics?.questions_asked > 0 && (
                    <span className="flex items-center gap-1 text-slate-400">
                      <BarChart3 className="w-3 h-3 text-emerald-400" />
                      {w.analytics.questions_asked} Q&A
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-1.5">
                  {w.status === 'scheduled' && (
                    <>
                      <Button size="sm" onClick={() => navigate(`/karau-meet/webinar/${w.webinar_id}/live`)}
                        className="h-7 px-2.5 text-[11px] bg-purple-500/80 hover:bg-purple-400 rounded-lg" data-testid={`join-${w.webinar_id}`}>
                        <Video className="w-3 h-3 mr-1" />Join Room
                      </Button>
                      <Button size="sm" onClick={() => startWebinar(w.webinar_id)}
                        className="h-7 px-2.5 text-[11px] bg-emerald-500/80 hover:bg-emerald-400 rounded-lg" data-testid={`start-${w.webinar_id}`}>
                        <Play className="w-3 h-3 mr-1" />{t("karauMeet.start") || "Start"}
                      </Button>
                    </>
                  )}
                  {(w.status === 'live' || w.status === 'practice') && (
                    <>
                      <Button size="sm" onClick={() => navigate(`/karau-meet/webinar/${w.webinar_id}/live`)}
                        className="h-7 px-2.5 text-[11px] bg-purple-500/80 hover:bg-purple-400 rounded-lg animate-pulse" data-testid={`join-live-${w.webinar_id}`}>
                        <Video className="w-3 h-3 mr-1" />Join Live
                      </Button>
                      <Button size="sm" variant="destructive" onClick={() => endWebinar(w.webinar_id)}
                        className="h-7 px-2.5 text-[11px] rounded-lg" data-testid={`end-${w.webinar_id}`}>
                        <Square className="w-3 h-3 mr-1" />{t("karauMeet.end") || "End"}
                      </Button>
                    </>
                  )}
                  <Button size="sm" variant="outline" onClick={() => copyRegLink(w.webinar_id)}
                    className="h-7 px-2.5 text-[11px] border-white/10 text-slate-300 hover:bg-white/5 rounded-lg" data-testid={`copy-link-${w.webinar_id}`}>
                    {copiedId === w.webinar_id ? <Check className="w-3 h-3 mr-1 text-emerald-400" /> : <Copy className="w-3 h-3 mr-1" />}
                    {copiedId === w.webinar_id ? 'Copied' : 'Copy Link'}
                  </Button>
                  <Button size="sm" variant="ghost" onClick={() => navigate(`/karau-meet/webinar/${w.webinar_id}/register`)}
                    className="h-7 px-2 text-[11px] text-slate-400 hover:text-white" data-testid={`view-${w.webinar_id}`}>
                    <ExternalLink className="w-3 h-3" />
                  </Button>
                  <Button size="sm" variant="ghost" onClick={() => setAnalyticsWebinarId(w.webinar_id)}
                    className="h-7 px-2 text-[11px] text-purple-400 hover:text-purple-300 hover:bg-purple-500/10" data-testid={`analytics-${w.webinar_id}`}>
                    <BarChart3 className="w-3 h-3" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Create Webinar Dialog */}
      <Dialog open={showCreate} onOpenChange={setShowCreate}>
        <DialogContent className="bg-karau-card border-white/10 rounded-2xl max-w-lg" aria-describedby="create-webinar-desc" data-testid="create-webinar-dialog">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <Radio className="w-5 h-5 text-purple-400" />
              {t("karauMeet.createWebinar") || "Create Webinar"}
            </DialogTitle>
            <p id="create-webinar-desc" className="text-xs text-karau-muted">Configure your webinar settings</p>
          </DialogHeader>
          <CreateWebinarForm onCreated={handleCreated} onCancel={() => setShowCreate(false)} />
        </DialogContent>
      </Dialog>

      {/* Webinar Analytics Slide-over */}
      <Dialog open={!!analyticsWebinarId} onOpenChange={(open) => { if (!open) setAnalyticsWebinarId(null); }}>
        <DialogContent className="bg-karau-card border-white/10 rounded-2xl max-w-lg max-h-[85vh] overflow-y-auto" data-testid="analytics-dialog">
          <WebinarAnalyticsPage webinarId={analyticsWebinarId} onClose={() => setAnalyticsWebinarId(null)} />
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default WebinarManagementPage;
