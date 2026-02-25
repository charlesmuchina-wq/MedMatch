import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { FileText, Loader2, Shield, Settings } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { useTranslation } from '@/utils/i18n';

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * Full Settings Page with Security & Accessibility
 */
const KarauSettingsPage = () => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('accessibility');
  const [accessibilitySettings, setAccessibilitySettings] = useState({
    high_contrast: false,
    large_text: false,
    font_size: 'medium',
    reduce_motion: false,
    live_captions_enabled: true,
    caption_font_size: 'medium',
    keyboard_shortcuts_enabled: true,
    color_blind_mode: 'none'
  });
  const [securityStatus, setSecurityStatus] = useState({
    mfa_enabled: false,
    email_verified: false
  });
  const [complianceStatus, setComplianceStatus] = useState(null);
  const [verificationCode, setVerificationCode] = useState('');
  const [sendingCode, setSendingCode] = useState(false);
  const [mockCode, setMockCode] = useState('');

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    const token = localStorage.getItem('token');
    try {
      const [accessRes, secRes, compRes] = await Promise.all([
        fetch(`${API}/api/karau-meet/accessibility/settings`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${API}/api/karau-meet/security/email/status`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${API}/api/karau-meet/security/compliance`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);
      
      if (accessRes.ok) {
        const data = await accessRes.json();
        setAccessibilitySettings(prev => ({ ...prev, ...data }));
      }
      if (secRes.ok) {
        const data = await secRes.json();
        setSecurityStatus(prev => ({ ...prev, email_verified: data.verified }));
      }
      if (compRes.ok) {
        setComplianceStatus(await compRes.json());
      }
    } catch (error) {
      console.error('Error fetching settings:', error);
    }
    setLoading(false);
  };

  const updateAccessibility = async (key, value) => {
    setAccessibilitySettings(prev => ({ ...prev, [key]: value }));
    
    const token = localStorage.getItem('token');
    try {
      await fetch(`${API}/api/karau-meet/accessibility/settings`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ [key]: value })
      });
      toast.success('Setting updated');
    } catch (error) {
      toast.error('Failed to update setting');
    }
  };

  const sendVerificationCode = async () => {
    setSendingCode(true);
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau-meet/security/email/send-code`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      if (data.success) {
        toast.success('Verification code sent!');
        if (data.mock_mode) {
          setMockCode(data.code);
        }
      }
    } catch (error) {
      toast.error('Failed to send code');
    }
    setSendingCode(false);
  };

  const verifyCode = async () => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau-meet/security/email/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ code: verificationCode })
      });
      if (res.ok) {
        toast.success('Email verified!');
        setSecurityStatus(prev => ({ ...prev, email_verified: true }));
        setMockCode('');
        setVerificationCode('');
      } else {
        const error = await res.json();
        toast.error(error.detail || 'Verification failed');
      }
    } catch (error) {
      toast.error('Verification failed');
    }
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <Loader2 className="w-6 h-6 text-turquoise animate-spin" />
      </div>
    );
  }

  const tabs = [
    { id: 'accessibility', label: 'Accessibility', icon: Settings },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'compliance', label: 'Compliance', icon: FileText }
  ];

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white" data-testid="settings-title">Settings</h1>
        <p className="text-slate-400">Customize your AI KARAU experience</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-slate-700 pb-2">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 rounded-t-lg flex items-center gap-2 transition-colors ${
              activeTab === tab.id
                ? 'bg-slate-800 text-turquoise border-b-2 border-turquoise'
                : 'text-slate-400 hover:text-white'
            }`}
            data-testid={`tab-${tab.id}`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Accessibility Tab */}
      {activeTab === 'accessibility' && (
        <div className="space-y-4">
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white text-lg">Display Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white">High Contrast Mode</Label>
                  <p className="text-xs text-slate-400">Increase contrast for better visibility</p>
                </div>
                <Switch
                  checked={accessibilitySettings.high_contrast}
                  onCheckedChange={(v) => updateAccessibility('high_contrast', v)}
                  data-testid="switch-high-contrast"
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white">Large Text</Label>
                  <p className="text-xs text-slate-400">Increase text size throughout the app</p>
                </div>
                <Switch
                  checked={accessibilitySettings.large_text}
                  onCheckedChange={(v) => updateAccessibility('large_text', v)}
                  data-testid="switch-large-text"
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white">Reduce Motion</Label>
                  <p className="text-xs text-slate-400">Minimize animations</p>
                </div>
                <Switch
                  checked={accessibilitySettings.reduce_motion}
                  onCheckedChange={(v) => updateAccessibility('reduce_motion', v)}
                />
              </div>

              <div>
                <Label className="text-white mb-2 block">Color Blind Mode</Label>
                <select
                  value={accessibilitySettings.color_blind_mode}
                  onChange={(e) => updateAccessibility('color_blind_mode', e.target.value)}
                  className="bg-slate-900 border border-slate-600 text-white rounded-lg px-3 py-2 w-full"
                  data-testid="select-color-blind"
                >
                  <option value="none">None</option>
                  <option value="protanopia">Protanopia (Red-Green)</option>
                  <option value="deuteranopia">Deuteranopia (Green-Red)</option>
                  <option value="tritanopia">Tritanopia (Blue-Yellow)</option>
                </select>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white text-lg">Live Captions</CardTitle>
              <CardDescription className="text-slate-400">Real-time transcription during meetings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white">Enable Live Captions</Label>
                  <p className="text-xs text-slate-400">Show real-time transcription</p>
                </div>
                <Switch
                  checked={accessibilitySettings.live_captions_enabled}
                  onCheckedChange={(v) => updateAccessibility('live_captions_enabled', v)}
                />
              </div>

              <div>
                <Label className="text-white mb-2 block">Caption Font Size</Label>
                <select
                  value={accessibilitySettings.caption_font_size}
                  onChange={(e) => updateAccessibility('caption_font_size', e.target.value)}
                  className="bg-slate-900 border border-slate-600 text-white rounded-lg px-3 py-2 w-full"
                >
                  <option value="small">Small</option>
                  <option value="medium">Medium</option>
                  <option value="large">Large</option>
                  <option value="x-large">Extra Large</option>
                </select>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white text-lg">Keyboard Shortcuts</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white">Enable Keyboard Shortcuts</Label>
                  <p className="text-xs text-slate-400">Use keyboard to control meetings</p>
                </div>
                <Switch
                  checked={accessibilitySettings.keyboard_shortcuts_enabled}
                  onCheckedChange={(v) => updateAccessibility('keyboard_shortcuts_enabled', v)}
                />
              </div>

              <div className="grid grid-cols-2 gap-2 mt-4">
                {[
                  { keys: 'Ctrl+M', action: 'Toggle Mute' },
                  { keys: 'Ctrl+V', action: 'Toggle Video' },
                  { keys: 'Ctrl+L', action: 'Toggle Captions' },
                  { keys: 'Ctrl+C', action: 'Toggle Chat' },
                  { keys: 'Ctrl+H', action: 'Raise Hand' },
                  { keys: 'Ctrl+Shift+Q', action: 'Leave Meeting' }
                ].map((shortcut, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 bg-slate-900/50 rounded">
                    <span className="text-xs text-slate-400">{shortcut.action}</span>
                    <Badge variant="outline" className="text-turquoise border-turquoise/30 text-xs">
                      {shortcut.keys}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Security Tab */}
      {activeTab === 'security' && (
        <div className="space-y-4">
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white text-lg flex items-center gap-2">
                <Shield className="w-5 h-5 text-turquoise" />
                Email Verification
              </CardTitle>
              <CardDescription className="text-slate-400">
                Verify your email for enhanced security
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {securityStatus.email_verified ? (
                <div className="flex items-center gap-2 p-4 bg-green-500/10 border border-green-500/30 rounded-lg" data-testid="email-verified">
                  <div className="w-8 h-8 rounded-full bg-green-500/20 flex items-center justify-center">
                    <Shield className="w-4 h-4 text-green-400" />
                  </div>
                  <div>
                    <p className="text-green-400 font-medium">Email Verified</p>
                    <p className="text-xs text-slate-400">Your email is verified for this session</p>
                  </div>
                </div>
              ) : (
                <>
                  <p className="text-slate-300 text-sm">
                    Verify your email to enable additional security features for meetings.
                  </p>
                  
                  <Button
                    onClick={sendVerificationCode}
                    disabled={sendingCode}
                    className="bg-turquoise hover:bg-turquoise/80"
                    data-testid="btn-send-code"
                  >
                    {sendingCode ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                    Send Verification Code
                  </Button>

                  {mockCode && (
                    <div className="p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
                      <p className="text-yellow-400 text-sm">
                        Demo Mode: Your verification code is <strong>{mockCode}</strong>
                      </p>
                    </div>
                  )}

                  <div className="flex gap-2">
                    <Input
                      placeholder={t("karauMeet.verificationCodePlaceholder")}
                      value={verificationCode}
                      onChange={(e) => setVerificationCode(e.target.value)}
                      className="bg-slate-900 border-slate-600 text-white"
                      maxLength={6}
                      data-testid="input-verification-code"
                    />
                    <Button onClick={verifyCode} disabled={verificationCode.length !== 6} data-testid="btn-verify">
                      Verify
                    </Button>
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white text-lg">Security Features</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-3">
                {[
                  { label: 'End-to-End Encryption', enabled: true, description: 'All meetings are encrypted' },
                  { label: 'Waiting Room', enabled: true, description: 'Control who joins your meetings' },
                  { label: 'Meeting Lock', enabled: true, description: 'Lock meetings to prevent new joins' },
                  { label: 'Recording Consent', enabled: true, description: 'Participants notified of recording' }
                ].map((feature, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg">
                    <div>
                      <p className="text-white text-sm">{feature.label}</p>
                      <p className="text-xs text-slate-400">{feature.description}</p>
                    </div>
                    <Badge className={feature.enabled ? 'bg-green-500/20 text-green-400' : 'bg-slate-500/20 text-slate-400'}>
                      {feature.enabled ? 'Enabled' : 'Disabled'}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Compliance Tab */}
      {activeTab === 'compliance' && complianceStatus && (
        <div className="space-y-4">
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white text-lg flex items-center gap-2">
                <FileText className="w-5 h-5 text-blue-400" />
                GDPR Compliance
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2 mb-4">
                <Badge className={complianceStatus.gdpr?.compliant ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'} data-testid="gdpr-status">
                  {complianceStatus.gdpr?.compliant ? 'Compliant' : 'Non-Compliant'}
                </Badge>
              </div>
              <div className="grid gap-2">
                {complianceStatus.gdpr?.features?.map((feature, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 bg-slate-900/50 rounded">
                    <span className="text-sm text-slate-300">{feature.name}</span>
                    <Badge variant="outline" className="text-green-400 border-green-400/30 text-xs">
                      {feature.status}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white text-lg flex items-center gap-2">
                <Shield className="w-5 h-5 text-violet-400" />
                HIPAA Compliance
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2 mb-4">
                <Badge className={complianceStatus.hipaa?.compliant ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'} data-testid="hipaa-status">
                  {complianceStatus.hipaa?.compliant ? 'Compliant' : 'Non-Compliant'}
                </Badge>
              </div>
              <div className="grid gap-2">
                {complianceStatus.hipaa?.features?.map((feature, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 bg-slate-900/50 rounded">
                    <span className="text-sm text-slate-300">{feature.name}</span>
                    <Badge variant="outline" className="text-green-400 border-green-400/30 text-xs">
                      {feature.status}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default KarauSettingsPage;
