import { useState } from 'react';
import { Loader2, Key, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { toast } from 'sonner';
import { useTranslation } from '@/utils/i18n';

const API = process.env.REACT_APP_BACKEND_URL;

export const SSOTab = () => {
  const { t } = useTranslation();
  const [ssoForm, setSsoForm] = useState({
    idp_entity_id: '', idp_sso_url: '', idp_slo_url: '', idp_certificate: '',
    enforce_sso: false, auto_provision: true,
  });
  const [ssoSaving, setSsoSaving] = useState(false);

  const saveSso = async () => {
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
  };

  return (
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
              data-testid="btn-save-sso" onClick={saveSso}>
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
  );
};
