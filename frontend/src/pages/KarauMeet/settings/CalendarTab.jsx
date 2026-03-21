import { useState } from 'react';
import { Loader2, Calendar, Link2, Unlink } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { toast } from 'sonner';
import { useTranslation } from '@/utils/i18n';

const API = process.env.REACT_APP_BACKEND_URL;

export const CalendarTab = ({ calendarStatus, setCalendarStatus }) => {
  const { t } = useTranslation();
  const [calendarLoading, setCalendarLoading] = useState(false);

  const connectMicrosoftCalendar = async () => {
    setCalendarLoading(true);
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau-meet/calendar/microsoft/connect`, { headers: { 'Authorization': `Bearer ${token}` } });
      const data = await res.json();
      if (data.auth_url) {
        window.open(data.auth_url, '_blank', 'width=600,height=700');
        toast.success(t("karauMeet.openingMicrosoftSignIn"));
      } else { toast.error(data.detail || t("karauMeet.microsoftNotConfigured")); }
    } catch { toast.error(t("karauMeet.failedConnect")); }
    setCalendarLoading(false);
  };

  const disconnectCalendar = async (provider) => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau-meet/calendar/disconnect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ provider })
      });
      if (res.ok) {
        toast.success(t("karauMeet.calendarDisconnected", { provider }));
        setCalendarStatus(prev => { const p = { ...prev.providers }; delete p[provider]; return { ...prev, providers: p }; });
      }
    } catch { toast.error(t("karauMeet.failedDisconnect")); }
  };

  return (
    <div className="space-y-4">
      <Card className="bg-karau-card/50 border-karau-border rounded-2xl">
        <CardHeader>
          <CardTitle className="text-white text-lg flex items-center gap-2">
            <Calendar className="w-5 h-5 text-purple-400" />
            {t("karauMeet.calendarIntegrations")}
          </CardTitle>
          <CardDescription className="text-karau-muted">{t("karauMeet.calendarIntegrationsDesc")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Microsoft */}
          <div className="flex items-center justify-between p-4 bg-karau-bg/50 rounded-xl border border-white/5" data-testid="calendar-microsoft">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-[#0078D4]/20 flex items-center justify-center">
                <svg className="w-5 h-5 text-[#0078D4]" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M21.17 2.06A2.13 2.13 0 0019.05 0H4.95A2.13 2.13 0 002.83 2.06L12 13.12 21.17 2.06zM22 3.95L12.72 14.4a1 1 0 01-1.44 0L2 3.95V19.05A2.13 2.13 0 004.95 22h14.1A2.13 2.13 0 0022 19.05V3.95z"/>
                </svg>
              </div>
              <div>
                <p className="text-white font-medium">{t("karauMeet.microsoftOutlook")}</p>
                {calendarStatus.providers?.microsoft ? (
                  <p className="text-xs text-emerald-400">{t("karauMeet.connected")}: {calendarStatus.providers.microsoft.email}</p>
                ) : calendarStatus.configured?.microsoft ? (
                  <p className="text-xs text-karau-muted">{t("karauMeet.availableClickConnect")}</p>
                ) : (
                  <p className="text-xs text-amber-400">{t("karauMeet.notConfigured")}</p>
                )}
              </div>
            </div>
            {calendarStatus.providers?.microsoft ? (
              <Button variant="outline" size="sm" className="border-red-500/30 text-red-400 hover:bg-red-500/10 rounded-xl"
                onClick={() => disconnectCalendar('microsoft')} data-testid="btn-disconnect-ms">
                <Unlink className="w-4 h-4 mr-1" /> {t("karauMeet.disconnect")}
              </Button>
            ) : (
              <Button size="sm" className="bg-[#0078D4] hover:bg-[#0078D4]/80 rounded-xl"
                onClick={connectMicrosoftCalendar} disabled={calendarLoading || !calendarStatus.configured?.microsoft} data-testid="btn-connect-ms">
                {calendarLoading ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <Link2 className="w-4 h-4 mr-1" />}
                {t("karauMeet.connect")}
              </Button>
            )}
          </div>

          {/* Apple */}
          <div className="flex items-center justify-between p-4 bg-karau-bg/50 rounded-xl border border-white/5" data-testid="calendar-apple">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-slate-600/30 flex items-center justify-center">
                <Calendar className="w-5 h-5 text-slate-300" />
              </div>
              <div>
                <p className="text-white font-medium">{t("karauMeet.appleCalendar")}</p>
                <p className="text-xs text-emerald-400">{t("karauMeet.alwaysAvailableIcs")}</p>
              </div>
            </div>
            <Badge className="bg-emerald-500/20 text-emerald-400">{t("karauMeet.available")}</Badge>
          </div>

          {/* Google */}
          <div className="flex items-center justify-between p-4 bg-karau-bg/50 rounded-xl border border-white/5" data-testid="calendar-google">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-[#4285F4]/20 flex items-center justify-center">
                <Calendar className="w-5 h-5 text-[#4285F4]" />
              </div>
              <div>
                <p className="text-white font-medium">{t("karauMeet.googleCalendar")}</p>
                {calendarStatus.providers?.google ? (
                  <p className="text-xs text-emerald-400">{t("karauMeet.connected")}: {calendarStatus.providers.google.email}</p>
                ) : calendarStatus.configured?.google ? (
                  <p className="text-xs text-karau-muted">{t("karauMeet.availableClickConnect")}</p>
                ) : (
                  <p className="text-xs text-emerald-400">{t("karauMeet.availableDirectLink")}</p>
                )}
              </div>
            </div>
            {calendarStatus.providers?.google ? (
              <Button variant="outline" size="sm" className="border-red-500/30 text-red-400 hover:bg-red-500/10 rounded-xl"
                onClick={() => disconnectCalendar('google')} data-testid="btn-disconnect-google">
                <Unlink className="w-4 h-4 mr-1" /> {t("karauMeet.disconnect")}
              </Button>
            ) : calendarStatus.configured?.google ? (
              <Button size="sm" className="bg-[#4285F4] hover:bg-[#4285F4]/80 rounded-xl"
                onClick={async () => {
                  const token = localStorage.getItem('token');
                  try {
                    const res = await fetch(`${API}/api/karau-meet/calendar/google/connect`, { headers: { 'Authorization': `Bearer ${token}` } });
                    const data = await res.json();
                    if (data.auth_url) window.open(data.auth_url, '_blank', 'width=600,height=700');
                    else toast.error(data.detail || t("karauMeet.googleNotConfigured"));
                  } catch { toast.error(t("karauMeet.failedConnect")); }
                }} data-testid="btn-connect-google">
                <Link2 className="w-4 h-4 mr-1" /> {t("karauMeet.connect")}
              </Button>
            ) : (
              <Badge className="bg-emerald-500/20 text-emerald-400">{t("karauMeet.available")}</Badge>
            )}
          </div>
        </CardContent>
      </Card>

      <Card className="bg-karau-card/50 border-karau-border rounded-2xl">
        <CardHeader><CardTitle className="text-white text-lg">{t("karauMeet.howCalendarSyncWorks")}</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-3 text-sm text-slate-300">
            <p>{t("karauMeet.calendarSyncIntro")}</p>
            <ul className="list-disc list-inside space-y-1 text-karau-muted">
              <li>{t("karauMeet.calendarSyncFeature1")}</li>
              <li>{t("karauMeet.calendarSyncFeature2")}</li>
              <li>{t("karauMeet.calendarSyncFeature3")}</li>
              <li>{t("karauMeet.calendarSyncFeature4")}</li>
            </ul>
            <p className="text-xs text-slate-500 mt-3">{t("karauMeet.calendarSyncNote")}</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
