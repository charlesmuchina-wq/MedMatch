import { useState, useEffect } from 'react';
import { Loader2, Settings, Calendar, Shield, Key, FileText, Webhook, TestTube2, Mail } from 'lucide-react';
import { toast } from 'sonner';
import { useTranslation } from '@/utils/i18n';
import { AccessibilityTab } from './settings/AccessibilityTab';
import { CalendarTab } from './settings/CalendarTab';
import { SecurityTab } from './settings/SecurityTab';
import { SSOTab } from './settings/SSOTab';
import { ComplianceTab } from './settings/ComplianceTab';
import { WebhookTab } from './settings/WebhookTab';
import { TSRTab } from './settings/TSRTab';
import { EmailSettingsTab } from './settings/EmailSettingsTab';

const API = process.env.REACT_APP_BACKEND_URL;

const KarauSettingsPage = () => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('accessibility');
  const [accessibilitySettings, setAccessibilitySettings] = useState({
    high_contrast: false, large_text: false, font_size: 'medium',
    reduce_motion: false, live_captions_enabled: true, caption_font_size: 'medium',
    keyboard_shortcuts_enabled: true, color_blind_mode: 'none'
  });
  const [securityStatus, setSecurityStatus] = useState({ mfa_enabled: false, email_verified: false });
  const [complianceStatus, setComplianceStatus] = useState(null);
  const [calendarStatus, setCalendarStatus] = useState({ providers: {}, configured: {} });
  const [tsrReports, setTsrReports] = useState([]);

  useEffect(() => { fetchSettings(); fetchTsrReports(); }, []);

  const fetchTsrReports = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API}/api/karau-meet/tsr/reports`, { headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) { const d = await res.json(); setTsrReports(d.reports || []); }
    } catch (e) { console.error('TSR fetch error:', e); }
  };

  const fetchSettings = async () => {
    const token = localStorage.getItem('token');
    try {
      const [accessRes, secRes, compRes] = await Promise.all([
        fetch(`${API}/api/karau-meet/accessibility/settings`, { headers: { 'Authorization': `Bearer ${token}` } }),
        fetch(`${API}/api/karau-meet/security/email/status`, { headers: { 'Authorization': `Bearer ${token}` } }),
        fetch(`${API}/api/karau-meet/security/compliance`, { headers: { 'Authorization': `Bearer ${token}` } })
      ]);
      if (accessRes.ok) { const data = await accessRes.json(); setAccessibilitySettings(prev => ({ ...prev, ...data })); }
      if (secRes.ok) { const data = await secRes.json(); setSecurityStatus(prev => ({ ...prev, email_verified: data.verified })); }
      if (compRes.ok) { setComplianceStatus(await compRes.json()); }
    } catch (error) { console.error('Error fetching settings:', error); }
    try {
      const calRes = await fetch(`${API}/api/karau-meet/calendar/status`, { headers: { 'Authorization': `Bearer ${token}` } });
      if (calRes.ok) setCalendarStatus(await calRes.json());
    } catch {}
    setLoading(false);
  };

  const updateAccessibility = async (key, value) => {
    setAccessibilitySettings(prev => ({ ...prev, [key]: value }));
    const token = localStorage.getItem('token');
    try {
      await fetch(`${API}/api/karau-meet/accessibility/settings`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ [key]: value })
      });
      toast.success(t("karauMeet.settingUpdated"));
    } catch { toast.error(t("karauMeet.failedUpdateSetting")); }
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <Loader2 className="w-6 h-6 text-purple-400 animate-spin" />
      </div>
    );
  }

  const tabs = [
    { id: 'accessibility', label: t("karauMeet.tabAccessibility"), icon: Settings },
    { id: 'calendar', label: t("karauMeet.tabCalendar"), icon: Calendar },
    { id: 'security', label: t("karauMeet.tabSecurity"), icon: Shield },
    { id: 'sso', label: t("karauMeet.tabSSO"), icon: Key },
    { id: 'compliance', label: t("karauMeet.tabCompliance"), icon: FileText },
    { id: 'webhooks', label: t("karauMeet.tabWebhooks"), icon: Webhook },
    { id: 'email', label: 'Email', icon: Mail },
    { id: 'tsr', label: t("karauMeet.tabTSR") || 'TSR Reports', icon: TestTube2 }
  ];

  return (
    <div className="p-6 space-y-6" style={{ fontFamily: "'IBM Plex Sans', sans-serif" }}>
      <div>
        <h1 className="text-2xl font-bold text-white" data-testid="settings-title">{t("karauMeet.settingsTitle")}</h1>
        <p className="text-karau-muted">{t("karauMeet.settingsSubtitle")}</p>
      </div>

      <div className="flex gap-2 border-b border-karau-border pb-2 overflow-x-auto">
        {tabs.map(tab => (
          <button key={tab.id} onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 rounded-t-lg flex items-center gap-2 transition-colors whitespace-nowrap ${
              activeTab === tab.id ? 'bg-karau-card text-purple-400 border-b-2 border-purple-400' : 'text-karau-muted hover:text-white'
            }`} data-testid={`tab-${tab.id}`}>
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'accessibility' && <AccessibilityTab settings={accessibilitySettings} onUpdate={updateAccessibility} />}
      {activeTab === 'calendar' && <CalendarTab calendarStatus={calendarStatus} setCalendarStatus={setCalendarStatus} />}
      {activeTab === 'security' && <SecurityTab securityStatus={securityStatus} setSecurityStatus={setSecurityStatus} />}
      {activeTab === 'sso' && <SSOTab />}
      {activeTab === 'compliance' && <ComplianceTab complianceStatus={complianceStatus} />}
      {activeTab === 'webhooks' && <WebhookTab />}
      {activeTab === 'email' && <EmailSettingsTab />}
      {activeTab === 'tsr' && <TSRTab tsrReports={tsrReports} setTsrReports={setTsrReports} />}
    </div>
  );
};

export default KarauSettingsPage;
