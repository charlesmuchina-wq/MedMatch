import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { FileText, Loader2, Shield, Settings, Calendar, Key, Link2, Unlink, ExternalLink, Webhook, Plus, Trash2, TestTube2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { useTranslation } from '@/utils/i18n';

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
  const [verificationCode, setVerificationCode] = useState('');
  const [sendingCode, setSendingCode] = useState(false);
  const [mockCode, setMockCode] = useState('');
  const [calendarStatus, setCalendarStatus] = useState({ providers: {}, configured: {} });
  const [calendarLoading, setCalendarLoading] = useState(false);
  const [ssoForm, setSsoForm] = useState({
    idp_entity_id: '', idp_sso_url: '', idp_slo_url: '', idp_certificate: '',
    enforce_sso: false, auto_provision: true,
  });
  const [ssoSaving, setSsoSaving] = useState(false);

  useEffect(() => { fetchSettings(); }, []);

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

  const sendVerificationCode = async () => {
    setSendingCode(true);
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau-meet/security/email/send-code`, { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } });
      const data = await res.json();
      if (data.success) {
        toast.success(t("karauMeet.verificationCodeSent"));
        if (data.mock_mode) setMockCode(data.code);
      }
    } catch { toast.error(t("karauMeet.failedSendCode")); }
    setSendingCode(false);
  };

  const verifyCode = async () => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau-meet/security/email/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ code: verificationCode })
      });
      if (res.ok) {
        toast.success(t("karauMeet.emailVerified"));
        setSecurityStatus(prev => ({ ...prev, email_verified: true }));
        setMockCode(''); setVerificationCode('');
      } else {
        const error = await res.json();
        toast.error(error.detail || t("karauMeet.verificationFailed"));
      }
    } catch { toast.error(t("karauMeet.verificationFailed")); }
  };

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
    { id: 'webhooks', label: t("karauMeet.tabWebhooks"), icon: Webhook }
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

      {activeTab === 'accessibility' && (
        <div className="space-y-4">
          <Card className="bg-karau-card/50 border-karau-border rounded-2xl">
            <CardHeader><CardTitle className="text-white text-lg">{t("karauMeet.displaySettings")}</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div><Label className="text-white">{t("karauMeet.highContrastMode")}</Label><p className="text-xs text-karau-muted">{t("karauMeet.highContrastDesc")}</p></div>
                <Switch checked={accessibilitySettings.high_contrast} onCheckedChange={(v) => updateAccessibility('high_contrast', v)} data-testid="switch-high-contrast" />
              </div>
              <div className="flex items-center justify-between">
                <div><Label className="text-white">{t("karauMeet.largeText")}</Label><p className="text-xs text-karau-muted">{t("karauMeet.largeTextDesc")}</p></div>
                <Switch checked={accessibilitySettings.large_text} onCheckedChange={(v) => updateAccessibility('large_text', v)} data-testid="switch-large-text" />
              </div>
              <div className="flex items-center justify-between">
                <div><Label className="text-white">{t("karauMeet.reduceMotion")}</Label><p className="text-xs text-karau-muted">{t("karauMeet.reduceMotionDesc")}</p></div>
                <Switch checked={accessibilitySettings.reduce_motion} onCheckedChange={(v) => updateAccessibility('reduce_motion', v)} />
              </div>
              <div>
                <Label className="text-white mb-2 block">{t("karauMeet.colorBlindMode")}</Label>
                <select value={accessibilitySettings.color_blind_mode} onChange={(e) => updateAccessibility('color_blind_mode', e.target.value)}
                  className="bg-karau-bg border border-white/10 text-white rounded-xl px-3 py-2 w-full" data-testid="select-color-blind">
                  <option value="none">{t("karauMeet.colorBlindNone")}</option>
                  <option value="protanopia">{t("karauMeet.colorBlindProtanopia")}</option>
                  <option value="deuteranopia">{t("karauMeet.colorBlindDeuteranopia")}</option>
                  <option value="tritanopia">{t("karauMeet.colorBlindTritanopia")}</option>
                </select>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-karau-card/50 border-karau-border rounded-2xl">
            <CardHeader>
              <CardTitle className="text-white text-lg">{t("karauMeet.liveCaptions")}</CardTitle>
              <CardDescription className="text-karau-muted">{t("karauMeet.liveCaptionsDesc")}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div><Label className="text-white">{t("karauMeet.enableLiveCaptions")}</Label><p className="text-xs text-karau-muted">{t("karauMeet.enableLiveCaptionsDesc")}</p></div>
                <Switch checked={accessibilitySettings.live_captions_enabled} onCheckedChange={(v) => updateAccessibility('live_captions_enabled', v)} />
              </div>
              <div>
                <Label className="text-white mb-2 block">{t("karauMeet.captionFontSize")}</Label>
                <select value={accessibilitySettings.caption_font_size} onChange={(e) => updateAccessibility('caption_font_size', e.target.value)}
                  className="bg-karau-bg border border-white/10 text-white rounded-xl px-3 py-2 w-full">
                  <option value="small">{t("karauMeet.fontSizeSmall")}</option>
                  <option value="medium">{t("karauMeet.fontSizeMedium")}</option>
                  <option value="large">{t("karauMeet.fontSizeLarge")}</option>
                  <option value="x-large">{t("karauMeet.fontSizeXLarge")}</option>
                </select>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-karau-card/50 border-karau-border rounded-2xl">
            <CardHeader><CardTitle className="text-white text-lg">{t("karauMeet.keyboardShortcuts")}</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div><Label className="text-white">{t("karauMeet.enableKeyboardShortcuts")}</Label><p className="text-xs text-karau-muted">{t("karauMeet.enableKeyboardShortcutsDesc")}</p></div>
                <Switch checked={accessibilitySettings.keyboard_shortcuts_enabled} onCheckedChange={(v) => updateAccessibility('keyboard_shortcuts_enabled', v)} />
              </div>
              <div className="grid grid-cols-2 gap-2 mt-4">
                {[
                  { keys: 'Ctrl+M', action: t("karauMeet.toggleMute") },
                  { keys: 'Ctrl+V', action: t("karauMeet.toggleVideo") },
                  { keys: 'Ctrl+L', action: t("karauMeet.toggleCaptions") },
                  { keys: 'Ctrl+C', action: t("karauMeet.toggleChat") },
                  { keys: 'Ctrl+H', action: t("karauMeet.raiseHandShortcut") },
                  { keys: 'Ctrl+Shift+Q', action: t("karauMeet.leaveShortcut") }
                ].map((shortcut, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 bg-karau-bg/50 rounded-lg">
                    <span className="text-xs text-karau-muted">{shortcut.action}</span>
                    <Badge variant="outline" className="text-purple-400 border-purple-500/30 text-xs">{shortcut.keys}</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'calendar' && (
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
      )}

      {activeTab === 'sso' && (
        <div className="space-y-4">
          <Card className="bg-karau-card/50 border-karau-border rounded-2xl">
            <CardHeader>
              <CardTitle className="text-white text-lg flex items-center gap-2">
                <Key className="w-5 h-5 text-amber-400" />
                {t("karauMeet.enterpriseSSO")}
              </CardTitle>
              <CardDescription className="text-karau-muted">{t("karauMeet.enterpriseSSODesc")}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-4 bg-karau-bg/50 rounded-xl border border-white/5">
                <h4 className="text-white font-medium mb-2">{t("karauMeet.spDetails")}</h4>
                <p className="text-xs text-karau-muted mb-3">{t("karauMeet.spDetailsDesc")}</p>
                <div className="space-y-2">
                  <div className="flex items-center justify-between p-2 bg-karau-card rounded-lg">
                    <span className="text-xs text-karau-muted">{t("karauMeet.entityId")}</span>
                    <code className="text-xs text-purple-400">https://aikarau.com/saml/metadata</code>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-karau-card rounded-lg">
                    <span className="text-xs text-karau-muted">{t("karauMeet.acsUrl")}</span>
                    <code className="text-xs text-purple-400">https://aikarau.com/api/karau-meet/sso/acs</code>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-karau-card rounded-lg">
                    <span className="text-xs text-karau-muted">{t("karauMeet.metadataUrl")}</span>
                    <a href={`${API}/api/karau-meet/sso/metadata`} target="_blank" rel="noopener noreferrer"
                      className="text-xs text-purple-400 hover:underline flex items-center gap-1">
                      {t("karauMeet.viewXml")} <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <h4 className="text-white font-medium">{t("karauMeet.idpConfig")}</h4>
                <div>
                  <Label className="text-slate-300 text-sm">{t("karauMeet.idpEntityId")}</Label>
                  <Input placeholder="https://idp.example.com/saml/metadata" value={ssoForm.idp_entity_id}
                    onChange={e => setSsoForm(f => ({ ...f, idp_entity_id: e.target.value }))}
                    className="bg-karau-bg border-white/10 text-white mt-1 rounded-xl" data-testid="sso-idp-entity-id" />
                </div>
                <div>
                  <Label className="text-slate-300 text-sm">{t("karauMeet.ssoLoginUrl")}</Label>
                  <Input placeholder="https://idp.example.com/saml/sso" value={ssoForm.idp_sso_url}
                    onChange={e => setSsoForm(f => ({ ...f, idp_sso_url: e.target.value }))}
                    className="bg-karau-bg border-white/10 text-white mt-1 rounded-xl" data-testid="sso-sso-url" />
                </div>
                <div>
                  <Label className="text-slate-300 text-sm">{t("karauMeet.sloUrlOptional")}</Label>
                  <Input placeholder="https://idp.example.com/saml/slo" value={ssoForm.idp_slo_url}
                    onChange={e => setSsoForm(f => ({ ...f, idp_slo_url: e.target.value }))}
                    className="bg-karau-bg border-white/10 text-white mt-1 rounded-xl" data-testid="sso-slo-url" />
                </div>
                <div>
                  <Label className="text-slate-300 text-sm">{t("karauMeet.idpCertificate")}</Label>
                  <textarea placeholder={"-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----"} value={ssoForm.idp_certificate}
                    onChange={e => setSsoForm(f => ({ ...f, idp_certificate: e.target.value }))}
                    className="w-full bg-karau-bg border border-white/10 text-white rounded-xl px-3 py-2 mt-1 h-24 text-xs font-mono" data-testid="sso-certificate" />
                </div>
                <div className="flex items-center justify-between">
                  <div><Label className="text-white">{t("karauMeet.enforceSso")}</Label><p className="text-xs text-karau-muted">{t("karauMeet.enforceSsoDesc")}</p></div>
                  <Switch checked={ssoForm.enforce_sso} onCheckedChange={v => setSsoForm(f => ({ ...f, enforce_sso: v }))} data-testid="sso-enforce-toggle" />
                </div>
                <div className="flex items-center justify-between">
                  <div><Label className="text-white">{t("karauMeet.autoProvision")}</Label><p className="text-xs text-karau-muted">{t("karauMeet.autoProvisionDesc")}</p></div>
                  <Switch checked={ssoForm.auto_provision} onCheckedChange={v => setSsoForm(f => ({ ...f, auto_provision: v }))} data-testid="sso-auto-provision-toggle" />
                </div>
                <Button className="bg-karau-accent hover:bg-karau-accent-bright w-full rounded-xl" disabled={ssoSaving || !ssoForm.idp_entity_id || !ssoForm.idp_sso_url}
                  data-testid="btn-save-sso"
                  onClick={async () => {
                    setSsoSaving(true);
                    const token = localStorage.getItem('token');
                    try {
                      const userRes = await fetch(`${API}/api/auth/me`, { headers: { 'Authorization': `Bearer ${token}` } });
                      const userData = await userRes.json();
                      const orgId = userData.organization_id || 'default';
                      const res = await fetch(`${API}/api/karau-meet/sso/configure`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                        body: JSON.stringify({ org_id: orgId, ...ssoForm })
                      });
                      if (res.ok) { toast.success(t("karauMeet.ssoSaved")); }
                      else { const err = await res.json(); toast.error(err.detail || t("karauMeet.ssoSaveFailed")); }
                    } catch { toast.error(t("karauMeet.ssoSaveError")); }
                    setSsoSaving(false);
                  }}>
                  {ssoSaving ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Key className="w-4 h-4 mr-2" />}
                  {t("karauMeet.saveSsoConfig")}
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-karau-card/50 border-karau-border rounded-2xl">
            <CardHeader><CardTitle className="text-white text-lg">{t("karauMeet.supportedIdps")}</CardTitle></CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {['Okta', 'Azure AD', 'OneLogin', 'Google Workspace', 'PingIdentity', 'Auth0', 'Duo', 'JumpCloud'].map(idp => (
                  <div key={idp} className="p-3 bg-karau-bg/50 rounded-xl text-center border border-white/5">
                    <p className="text-sm text-slate-300">{idp}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'security' && (
        <div className="space-y-4">
          <Card className="bg-karau-card/50 border-karau-border rounded-2xl">
            <CardHeader>
              <CardTitle className="text-white text-lg flex items-center gap-2">
                <Shield className="w-5 h-5 text-emerald-400" />
                {t("karauMeet.emailVerification")}
              </CardTitle>
              <CardDescription className="text-karau-muted">{t("karauMeet.emailVerificationDesc")}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {securityStatus.email_verified ? (
                <div className="flex items-center gap-2 p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl" data-testid="email-verified">
                  <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center">
                    <Shield className="w-4 h-4 text-emerald-400" />
                  </div>
                  <div>
                    <p className="text-emerald-400 font-medium">{t("karauMeet.emailVerifiedLabel")}</p>
                    <p className="text-xs text-karau-muted">{t("karauMeet.emailVerifiedDesc")}</p>
                  </div>
                </div>
              ) : (
                <>
                  <p className="text-slate-300 text-sm">{t("karauMeet.emailVerifyPrompt")}</p>
                  <Button onClick={sendVerificationCode} disabled={sendingCode}
                    className="bg-karau-accent hover:bg-karau-accent-bright rounded-xl" data-testid="btn-send-code">
                    {sendingCode ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                    {t("karauMeet.sendVerificationCode")}
                  </Button>
                  {mockCode && (
                    <div className="p-3 bg-amber-500/10 border border-amber-500/30 rounded-xl">
                      <p className="text-amber-400 text-sm">{t("karauMeet.demoModeCode")} <strong>{mockCode}</strong></p>
                    </div>
                  )}
                  <div className="flex gap-2">
                    <Input placeholder={t("karauMeet.verificationCodePlaceholder")} value={verificationCode}
                      onChange={(e) => setVerificationCode(e.target.value)}
                      className="bg-karau-bg border-white/10 text-white rounded-xl" maxLength={6} data-testid="input-verification-code" />
                    <Button onClick={verifyCode} disabled={verificationCode.length !== 6}
                      className="rounded-xl" data-testid="btn-verify">{t("karauMeet.verify")}</Button>
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          <Card className="bg-karau-card/50 border-karau-border rounded-2xl">
            <CardHeader><CardTitle className="text-white text-lg">{t("karauMeet.securityFeatures")}</CardTitle></CardHeader>
            <CardContent>
              <div className="grid gap-3">
                {[
                  { label: t("karauMeet.endToEndEncryptionLabel"), enabled: true, description: t("karauMeet.encryptionDesc") },
                  { label: t("karauMeet.waitingRoom"), enabled: true, description: t("karauMeet.waitingRoomDesc") },
                  { label: t("karauMeet.meetingLock"), enabled: true, description: t("karauMeet.meetingLockDesc") },
                  { label: t("karauMeet.recordingConsentLabel"), enabled: true, description: t("karauMeet.recordingConsentDesc") }
                ].map((feature, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-karau-bg/50 rounded-xl">
                    <div>
                      <p className="text-white text-sm">{feature.label}</p>
                      <p className="text-xs text-karau-muted">{feature.description}</p>
                    </div>
                    <Badge className={feature.enabled ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-500/20 text-karau-muted'}>
                      {feature.enabled ? t("karauMeet.enabled") : t("karauMeet.disabled")}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'compliance' && complianceStatus && (
        <div className="space-y-4">
          <Card className="bg-karau-card/50 border-karau-border rounded-2xl">
            <CardHeader>
              <CardTitle className="text-white text-lg flex items-center gap-2">
                <FileText className="w-5 h-5 text-purple-400" />
                {t("karauMeet.gdprCompliance")}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2 mb-4">
                <Badge className={complianceStatus.gdpr?.compliant ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'} data-testid="gdpr-status">
                  {complianceStatus.gdpr?.compliant ? t("karauMeet.compliant") : t("karauMeet.nonCompliant")}
                </Badge>
              </div>
              <div className="grid gap-2">
                {complianceStatus.gdpr?.features?.map((feature, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 bg-karau-bg/50 rounded-lg">
                    <span className="text-sm text-slate-300">{feature.name}</span>
                    <Badge variant="outline" className="text-emerald-400 border-emerald-400/30 text-xs">{feature.status}</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-karau-card/50 border-karau-border rounded-2xl">
            <CardHeader>
              <CardTitle className="text-white text-lg flex items-center gap-2">
                <Shield className="w-5 h-5 text-violet-400" />
                {t("karauMeet.hipaaCompliance")}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2 mb-4">
                <Badge className={complianceStatus.hipaa?.compliant ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'} data-testid="hipaa-status">
                  {complianceStatus.hipaa?.compliant ? t("karauMeet.compliant") : t("karauMeet.nonCompliant")}
                </Badge>
              </div>
              <div className="grid gap-2">
                {complianceStatus.hipaa?.features?.map((feature, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 bg-karau-bg/50 rounded-lg">
                    <span className="text-sm text-slate-300">{feature.name}</span>
                    <Badge variant="outline" className="text-emerald-400 border-emerald-400/30 text-xs">{feature.status}</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'webhooks' && <WebhookSettings />}
    </div>
  );
};

const WebhookSettings = () => {
  const { t } = useTranslation();
  const [webhooks, setWebhooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newUrl, setNewUrl] = useState('');
  const [newName, setNewName] = useState('');
  const [showAdd, setShowAdd] = useState(false);

  const fetchWebhooks = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API}/api/karau-features/webhooks`, { headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) { const data = await res.json(); setWebhooks(data.webhooks || []); }
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  useEffect(() => { fetchWebhooks(); }, []);

  const addWebhook = async () => {
    if (!newUrl.trim()) return;
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API}/api/karau-features/webhooks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ webhook_url: newUrl, name: newName || 'Custom CRM', events: ['meeting_ended', 'meeting_created'] })
      });
      if (res.ok) { toast.success(t("karauMeet.webhookAdded")); setNewUrl(''); setNewName(''); setShowAdd(false); fetchWebhooks(); }
    } catch { toast.error(t("karauMeet.failedAddWebhook")); }
  };

  const deleteWebhook = async (id) => {
    try {
      const token = localStorage.getItem('token');
      await fetch(`${API}/api/karau-features/webhooks/${id}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` } });
      toast.success(t("karauMeet.webhookDeleted")); fetchWebhooks();
    } catch { toast.error(t("karauMeet.failedDeleteWebhook")); }
  };

  const testWebhook = async (id) => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API}/api/karau-features/webhooks/test/${id}`, { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } });
      const data = await res.json();
      if (data.success) toast.success(t("karauMeet.testSuccessful", { code: data.status_code }));
      else toast.error(`${t("karauMeet.testFailed")}: ${data.error || data.status_code}`);
    } catch { toast.error(t("karauMeet.testFailed")); }
  };

  return (
    <div className="space-y-4">
      <Card className="bg-karau-card/50 border-karau-border rounded-2xl">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-white">{t("karauMeet.crmWebhookIntegration")}</CardTitle>
              <CardDescription className="text-karau-muted">{t("karauMeet.crmWebhookDesc")}</CardDescription>
            </div>
            <Button onClick={() => setShowAdd(!showAdd)} className="bg-emerald-500/80 hover:bg-emerald-400 text-white rounded-xl" data-testid="add-webhook-btn">
              <Plus className="w-4 h-4 mr-1" />{t("karauMeet.addWebhook")}
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {showAdd && (
            <div className="p-4 bg-karau-bg/50 rounded-xl border border-white/5 space-y-3">
              <Input placeholder={t("karauMeet.webhookNamePlaceholder")} value={newName} onChange={e => setNewName(e.target.value)}
                className="bg-karau-card border-white/10 text-white rounded-xl" data-testid="webhook-name-input" />
              <Input placeholder={t("karauMeet.webhookUrlPlaceholder")} value={newUrl} onChange={e => setNewUrl(e.target.value)}
                className="bg-karau-card border-white/10 text-white rounded-xl" data-testid="webhook-url-input" />
              <div className="flex gap-2">
                <Button onClick={addWebhook} className="bg-emerald-500 text-white rounded-xl" data-testid="save-webhook-btn">{t("karauMeet.save")}</Button>
                <Button variant="ghost" onClick={() => setShowAdd(false)} className="text-karau-muted rounded-xl">{t("karauMeet.cancel")}</Button>
              </div>
            </div>
          )}
          {loading ? (
            <div className="flex justify-center py-8"><Loader2 className="w-5 h-5 animate-spin text-purple-400" /></div>
          ) : webhooks.length === 0 ? (
            <div className="text-center py-8 text-karau-muted">
              <Webhook className="w-10 h-10 mx-auto mb-2 opacity-30" />
              <p>{t("karauMeet.noWebhooks")}</p>
              <p className="text-xs mt-1">{t("karauMeet.noWebhooksDesc")}</p>
            </div>
          ) : (
            webhooks.map(wh => (
              <div key={wh.webhook_id} className="flex items-center justify-between p-3 bg-karau-bg/30 rounded-xl border border-white/5" data-testid={`webhook-${wh.webhook_id}`}>
                <div className="flex-1 min-w-0">
                  <p className="text-white text-sm font-medium">{wh.name}</p>
                  <p className="text-slate-500 text-xs truncate">{wh.webhook_url}</p>
                  <div className="flex gap-1 mt-1">
                    {wh.events?.map(ev => (
                      <Badge key={ev} className="bg-karau-surface text-karau-muted text-[10px]">{ev}</Badge>
                    ))}
                  </div>
                </div>
                <div className="flex gap-1 ml-3">
                  <Button variant="ghost" size="sm" onClick={() => testWebhook(wh.webhook_id)} className="text-amber-400 hover:bg-amber-500/10 h-8 w-8 p-0" title="Test">
                    <TestTube2 className="w-3.5 h-3.5" />
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => deleteWebhook(wh.webhook_id)} className="text-red-400 hover:bg-red-500/10 h-8 w-8 p-0" title="Delete">
                    <Trash2 className="w-3.5 h-3.5" />
                  </Button>
                </div>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default KarauSettingsPage;
