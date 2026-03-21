import { useState } from 'react';
import { Loader2, Shield } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { toast } from 'sonner';
import { useTranslation } from '@/utils/i18n';

const API = process.env.REACT_APP_BACKEND_URL;

export const SecurityTab = ({ securityStatus, setSecurityStatus }) => {
  const { t } = useTranslation();
  const [verificationCode, setVerificationCode] = useState('');
  const [sendingCode, setSendingCode] = useState(false);
  const [mockCode, setMockCode] = useState('');

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

  return (
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
  );
};
