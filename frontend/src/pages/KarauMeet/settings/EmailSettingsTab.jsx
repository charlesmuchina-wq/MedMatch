import { useState } from 'react';
import { Loader2, Mail, Send, Shield, Check, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

export const EmailSettingsTab = () => {
  const [loading, setLoading] = useState(true);
  const [settings, setSettings] = useState({ resend_api_key_masked: '', sender_email: '', is_configured: false, source: '' });
  const [apiKey, setApiKey] = useState('');
  const [senderEmail, setSenderEmail] = useState('');
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testEmail, setTestEmail] = useState('');
  const [editing, setEditing] = useState(false);

  useState(() => {
    const load = async () => {
      const token = localStorage.getItem('token');
      try {
        const res = await fetch(`${API}/api/admin/email-settings`, { headers: { Authorization: `Bearer ${token}` } });
        if (res.ok) {
          const data = await res.json();
          setSettings(data);
          setSenderEmail(data.sender_email || '');
        }
      } catch { /* ignore */ }
      setLoading(false);
    };
    load();
  });

  const handleSave = async () => {
    setSaving(true);
    const token = localStorage.getItem('token');
    try {
      const body = {};
      if (apiKey) body.resend_api_key = apiKey;
      if (senderEmail) body.sender_email = senderEmail;

      const res = await fetch(`${API}/api/admin/email-settings`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(body)
      });
      if (res.ok) {
        toast.success('Email settings updated');
        setEditing(false);
        setApiKey('');
        // Reload settings
        const r2 = await fetch(`${API}/api/admin/email-settings`, { headers: { Authorization: `Bearer ${token}` } });
        if (r2.ok) setSettings(await r2.json());
      } else {
        const err = await res.json();
        toast.error(err.detail || 'Failed to update');
      }
    } catch { toast.error('Connection error'); }
    setSaving(false);
  };

  const handleTest = async () => {
    if (!testEmail) { toast.error('Enter a test email address'); return; }
    setTesting(true);
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/admin/email-settings/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ to_email: testEmail })
      });
      const data = await res.json();
      if (data.success) toast.success(data.message);
      else toast.error(data.message || 'Test failed');
    } catch { toast.error('Connection error'); }
    setTesting(false);
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="w-5 h-5 animate-spin text-purple-400" />
      </div>
    );
  }

  return (
    <div className="space-y-4" data-testid="email-settings-tab">
      <Card className="bg-karau-card/50 border-karau-border rounded-2xl">
        <CardHeader>
          <CardTitle className="text-white text-lg flex items-center gap-2">
            <Mail className="w-5 h-5 text-cyan-400" />
            Resend Email Configuration
          </CardTitle>
          <CardDescription className="text-karau-muted">
            Configure your Resend API key to enable email features (invitations, notifications, verifications)
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Status */}
          <div className="flex items-center gap-3 p-4 rounded-xl border border-white/5 bg-karau-bg/50" data-testid="email-config-status">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${settings.is_configured ? 'bg-emerald-500/20' : 'bg-amber-500/20'}`}>
              {settings.is_configured ? <Check className="w-5 h-5 text-emerald-400" /> : <AlertCircle className="w-5 h-5 text-amber-400" />}
            </div>
            <div className="flex-1">
              <p className="text-white font-medium">
                {settings.is_configured ? 'Resend API Connected' : 'Resend API Not Configured'}
              </p>
              <p className="text-xs text-karau-muted">
                {settings.is_configured
                  ? `Key: ${settings.resend_api_key_masked} | Source: ${settings.source}`
                  : 'Add your Resend API key to enable email delivery'}
              </p>
            </div>
            <Badge className={settings.is_configured ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'}>
              {settings.is_configured ? 'Active' : 'Inactive'}
            </Badge>
          </div>

          {/* Config Form */}
          {editing ? (
            <div className="space-y-3 p-4 rounded-xl border border-white/10 bg-white/[0.02]" data-testid="email-config-form">
              <div>
                <Label className="text-slate-300 text-sm">Resend API Key</Label>
                <Input
                  type="password"
                  placeholder="re_xxxxxxxxxx..."
                  value={apiKey}
                  onChange={e => setApiKey(e.target.value)}
                  className="bg-karau-bg border-white/10 text-white mt-1 rounded-xl"
                  data-testid="resend-api-key-input"
                />
                <p className="text-[10px] text-slate-600 mt-1">
                  Get your key at <a href="https://resend.com/api-keys" target="_blank" rel="noopener noreferrer" className="text-cyan-400 hover:underline">resend.com/api-keys</a>
                </p>
              </div>
              <div>
                <Label className="text-slate-300 text-sm">Sender Email</Label>
                <Input
                  placeholder="noreply@yourdomain.com"
                  value={senderEmail}
                  onChange={e => setSenderEmail(e.target.value)}
                  className="bg-karau-bg border-white/10 text-white mt-1 rounded-xl"
                  data-testid="sender-email-input"
                />
                <p className="text-[10px] text-slate-600 mt-1">Must be a verified domain in Resend, or use onboarding@resend.dev for testing</p>
              </div>
              <div className="flex gap-2 pt-2">
                <Button onClick={handleSave} disabled={saving} className="bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl" data-testid="save-email-settings">
                  {saving ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Shield className="w-4 h-4 mr-2" />}
                  Save Settings
                </Button>
                <Button variant="ghost" onClick={() => { setEditing(false); setApiKey(''); }} className="text-karau-muted rounded-xl">Cancel</Button>
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <div className="flex-1 space-y-1.5">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-400">Sender:</span>
                  <code className="text-xs text-cyan-400 bg-white/[0.03] px-2 py-0.5 rounded">{settings.sender_email || 'Not set'}</code>
                </div>
                {settings.updated_at && (
                  <p className="text-[10px] text-slate-600">Last updated: {new Date(settings.updated_at).toLocaleString()}</p>
                )}
              </div>
              <Button onClick={() => setEditing(true)} variant="outline" className="border-white/10 text-slate-300 hover:text-white rounded-xl" data-testid="edit-email-settings">
                Configure
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Test Email */}
      {settings.is_configured && (
        <Card className="bg-karau-card/50 border-karau-border rounded-2xl">
          <CardHeader>
            <CardTitle className="text-white text-lg flex items-center gap-2">
              <Send className="w-5 h-5 text-violet-400" />
              Test Email Delivery
            </CardTitle>
            <CardDescription className="text-karau-muted">Send a test email to verify your configuration</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-2">
              <Input
                placeholder="recipient@example.com"
                value={testEmail}
                onChange={e => setTestEmail(e.target.value)}
                className="bg-karau-bg border-white/10 text-white rounded-xl"
                data-testid="test-email-input"
              />
              <Button onClick={handleTest} disabled={testing} className="bg-violet-600 hover:bg-violet-500 text-white rounded-xl" data-testid="send-test-email">
                {testing ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Send className="w-4 h-4 mr-2" />}
                Send Test
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Info */}
      <Card className="bg-karau-card/50 border-karau-border rounded-2xl">
        <CardHeader><CardTitle className="text-white text-lg">Email Features Powered by Resend</CardTitle></CardHeader>
        <CardContent>
          <div className="grid gap-2">
            {[
              { label: 'Team Invitations (ENZI)', description: 'Send invite links to join your workspace' },
              { label: 'Meeting Notifications (AI KARAU)', description: 'Notify participants of upcoming meetings' },
              { label: 'Guest Verification', description: 'OTP codes for guest meeting access' },
              { label: 'Job Digest Emails (MedMatch)', description: 'Automated job alert digests for seekers' },
            ].map((f, i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-karau-bg/50 rounded-xl">
                <div>
                  <p className="text-white text-sm">{f.label}</p>
                  <p className="text-xs text-karau-muted">{f.description}</p>
                </div>
                <Badge className={settings.is_configured ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-500/20 text-karau-muted'}>
                  {settings.is_configured ? 'Ready' : 'Needs Key'}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
