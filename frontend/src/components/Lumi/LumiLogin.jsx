import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast, Toaster } from 'sonner';
import { Eye, EyeOff, Loader2, Fingerprint, Smartphone } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useTranslation } from '@/utils/i18n';
import { API, ESY } from './constants';
import { LumiBrand } from './LumiBrand';

export const LumiLogin = ({ onLogin }) => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPw, setShowPw] = useState(false);
  const [showMore, setShowMore] = useState(false);
  const [passkeyMode, setPasskeyMode] = useState(null);
  const [passkeyEmail, setPasskeyEmail] = useState('');
  const [passkeyLoading, setPasskeyLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const res = await fetch(`${API}/api/auth/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, credentials: 'include', body: JSON.stringify({ email, password }) });
      if (res.ok) {
        const data = await res.json();
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('karau_user', JSON.stringify(data.user));
        // Sync session for cross-portal auth
        try {
          const syncRes = await fetch(`${API}/api/portal/sync-session`, { method: 'POST', credentials: 'include', headers: { 'Authorization': `Bearer ${data.access_token}` } });
          if (syncRes.ok) {
            const syncData = await syncRes.json();
            localStorage.setItem('session_token', syncData.token);
          }
          // Handle package intent from landing page
          const pkgIntent = localStorage.getItem('selected_package_intent');
          if (pkgIntent) {
            localStorage.removeItem('selected_package_intent');
            const pkgRes = await fetch(`${API}/api/portal/set-package`, { method: 'POST', credentials: 'include', headers: { 'Authorization': `Bearer ${data.access_token}`, 'Content-Type': 'application/json' }, body: JSON.stringify({ package_id: pkgIntent }) });
            if (pkgRes.ok) {
              const pkgData = await pkgRes.json();
              localStorage.setItem('portal_package', pkgIntent);
              localStorage.setItem('portal_access', JSON.stringify(pkgData.portals));
            }
          } else {
            // Load existing portal access
            const accRes = await fetch(`${API}/api/portal/access`, { headers: { 'Authorization': `Bearer ${data.access_token}` } });
            if (accRes.ok) {
              const accData = await accRes.json();
              if (accData.portals) {
                localStorage.setItem('portal_package', accData.package_id);
                localStorage.setItem('portal_access', JSON.stringify(accData.portals));
              }
            }
          }
        } catch(e) { /* not critical */ }
        onLogin(data.user);
        toast.success('Welcome to ENZI!');
      } else { const err = await res.json(); toast.error(err.detail || 'Login failed'); }
    } catch (e) { toast.error('Connection error'); }
    setIsLoading(false);
  };

  const handleGoogleLogin = () => {
    const redirectUrl = window.location.origin + '/lumi';
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  const handleMicrosoftLogin = async () => {
    try {
      const res = await fetch(`${API}/api/auth/microsoft/login`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        if (data.auth_url) window.location.href = data.auth_url;
      } else { toast.info('Microsoft SSO not configured yet.'); }
    } catch { toast.info('Microsoft SSO not configured yet.'); }
  };

  const handleAppleLogin = async () => {
    try {
      const res = await fetch(`${API}/api/auth/apple/config`);
      if (res.ok) {
        const config = await res.json();
        if (config.client_id) {
          const redirectUri = `${API}/api/auth/apple/callback`;
          const state = btoa(JSON.stringify({ redirect: '/lumi' }));
          window.location.href = `https://appleid.apple.com/auth/authorize?client_id=${config.client_id}&redirect_uri=${encodeURIComponent(redirectUri)}&response_type=code%20id_token&response_mode=form_post&scope=name%20email&state=${state}`;
        } else toast.info('Apple Sign-In not configured yet.');
      }
    } catch { toast.info('Apple Sign-In not available.'); }
  };

  const handleGitHubLogin = async () => {
    try {
      const res = await fetch(`${API}/api/auth/github/login`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        if (data.auth_url) {
          if (data.mode === 'demo') toast.info('GitHub SSO in demo mode. Redirecting...');
          window.location.href = data.auth_url;
        }
      } else { toast.info('GitHub SSO not available.'); }
    } catch { toast.info('GitHub SSO not available.'); }
  };

  const b64ToArray = (b64) => Uint8Array.from(atob(b64.replace(/-/g, '+').replace(/_/g, '/')), c => c.charCodeAt(0));
  const arrayToB64 = (buf) => btoa(String.fromCharCode(...new Uint8Array(buf))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');

  const handlePasskeyLogin = async () => {
    if (!passkeyEmail) { setPasskeyMode('login'); return; }
    setPasskeyLoading(true);
    try {
      const startRes = await fetch(`${API}/api/auth/passkey/login/start`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: passkeyEmail })
      });
      if (!startRes.ok) {
        const err = await startRes.json();
        if (err.detail?.includes('No passkeys')) { toast.error('No passkeys for this email. Register first.'); setPasskeyMode('register'); }
        else toast.error(err.detail || 'Passkey login failed');
        setPasskeyLoading(false); return;
      }
      const opts = await startRes.json();
      if (!window.PublicKeyCredential) { toast.error('Passkeys not supported.'); setPasskeyLoading(false); return; }
      const assertion = await navigator.credentials.get({
        publicKey: {
          challenge: b64ToArray(opts.challenge),
          rpId: opts.rpId || window.location.hostname,
          allowCredentials: (opts.allowCredentials || []).map(c => ({ type: c.type, id: b64ToArray(c.id) })),
          timeout: 60000, userVerification: 'preferred'
        }
      });
      const finishRes = await fetch(`${API}/api/auth/passkey/login/finish`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: passkeyEmail, credential_id: arrayToB64(assertion.rawId),
          authenticator_data: arrayToB64(assertion.response.authenticatorData),
          signature: arrayToB64(assertion.response.signature) })
      });
      if (finishRes.ok) {
        const data = await finishRes.json();
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('karau_user', JSON.stringify(data.user));
        onLogin(data.user);
        toast.success('Signed in with passkey!');
      } else { const err = await finishRes.json(); toast.error(err.detail || 'Passkey login failed'); }
    } catch (e) {
      if (e.name === 'NotAllowedError') toast.info('Passkey cancelled.');
      else toast.error('Passkey failed. Try another method.');
    }
    setPasskeyLoading(false);
  };

  const handlePasskeyRegister = async () => {
    if (!passkeyEmail) { toast.error('Enter email first'); return; }
    setPasskeyLoading(true);
    try {
      const startRes = await fetch(`${API}/api/auth/passkey/register/start`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: passkeyEmail })
      });
      if (!startRes.ok) { const err = await startRes.json(); toast.error(err.detail || 'Cannot register'); setPasskeyLoading(false); return; }
      const opts = await startRes.json();
      if (!window.PublicKeyCredential) { toast.error('Passkeys not supported.'); setPasskeyLoading(false); return; }
      const cred = await navigator.credentials.create({
        publicKey: {
          challenge: b64ToArray(opts.challenge),
          rp: { name: opts.rp.name, id: opts.rp.id || window.location.hostname },
          user: { id: Uint8Array.from(opts.user.id, c => c.charCodeAt(0)), name: opts.user.name, displayName: opts.user.displayName },
          pubKeyCredParams: opts.pubKeyCredParams, timeout: 60000, attestation: 'none'
        }
      });
      const pk = cred.response.getPublicKey ? arrayToB64(cred.response.getPublicKey()) : '';
      const finishRes = await fetch(`${API}/api/auth/passkey/register/finish`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: passkeyEmail, credential_id: arrayToB64(cred.rawId), public_key: pk,
          attestation: arrayToB64(cred.response.attestationObject) })
      });
      if (finishRes.ok) { toast.success('Passkey registered! Sign in with it now.'); setPasskeyMode('login'); }
      else { const err = await finishRes.json(); toast.error(err.detail || 'Registration failed'); }
    } catch (e) {
      if (e.name === 'NotAllowedError') toast.info('Passkey creation cancelled.');
      else toast.error('Passkey registration failed.');
    }
    setPasskeyLoading(false);
  };

  const handlePhoneLogin = () => { toast.info('Phone OTP login coming soon.'); };

  if (passkeyMode) {
    return (
      <div className="min-h-screen flex items-center justify-center p-8 bg-slate-50" style={{ fontFamily: "'Inter', -apple-system, sans-serif" }}>
        <Toaster position="top-right" richColors />
        <div className="w-full max-w-sm">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` }}>
              <Fingerprint className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-800">{passkeyMode === 'register' ? 'Register Passkey' : 'Sign in with Passkey'}</h2>
              <p className="text-xs text-slate-500">Use biometrics or security key</p>
            </div>
          </div>
          <div className="space-y-3">
            <Input value={passkeyEmail} onChange={e => setPasskeyEmail(e.target.value)} type="email" placeholder="Enter your email"
              className="h-11 border-slate-200 rounded-lg" data-testid="passkey-email-input" />
            {passkeyMode === 'login' ? (
              <Button onClick={handlePasskeyLogin} disabled={passkeyLoading || !passkeyEmail}
                className="w-full h-11 text-white rounded-lg font-medium"
                style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` }} data-testid="passkey-login-submit">
                {passkeyLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Authenticate with Passkey'}
              </Button>
            ) : (
              <Button onClick={handlePasskeyRegister} disabled={passkeyLoading || !passkeyEmail}
                className="w-full h-11 text-white rounded-lg font-medium"
                style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` }} data-testid="passkey-register-submit">
                {passkeyLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Create Passkey'}
              </Button>
            )}
            <div className="flex gap-2">
              {passkeyMode === 'login' && <button onClick={() => setPasskeyMode('register')} className="flex-1 text-xs text-[#00CEC9] hover:underline py-2" data-testid="switch-to-register-passkey">Register new passkey</button>}
              {passkeyMode === 'register' && <button onClick={() => setPasskeyMode('login')} className="flex-1 text-xs text-[#00CEC9] hover:underline py-2" data-testid="switch-to-login-passkey">Sign in with passkey</button>}
              <button onClick={() => { setPasskeyMode(null); setPasskeyEmail(''); }} className="flex-1 text-xs text-slate-500 hover:text-slate-700 py-2" data-testid="back-from-passkey">Back to login</button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex" style={{ fontFamily: "'Inter', -apple-system, sans-serif" }}>
      <Toaster position="top-right" richColors />
      <div className="hidden lg:flex lg:w-1/2 bg-[#36454F] items-center justify-center relative overflow-hidden">
        <img src="https://images.unsplash.com/photo-1719667052333-1cba4797fd85?w=1200&q=80" alt="" className="absolute inset-0 w-full h-full object-cover opacity-20" />
        <div className="relative z-10 text-center px-12">
          <LumiBrand variant="full-dark" size="xl" />
          <p className="text-sm text-white/90 mt-6 max-w-sm text-center">Secure, domain-protected team communication for the modern workplace.</p>
          <div className="mt-8 flex flex-wrap justify-center gap-2">
            {['E2E Encrypted', 'AI-Powered', 'Multi-Platform SSO', 'Bot Marketplace'].map(f => (
              <span key={f} className="px-3 py-1 rounded-full text-[10px] font-medium text-white/70 bg-white/10 border border-white/10">{f}</span>
            ))}
          </div>
        </div>
      </div>
      <div className="flex-1 flex items-center justify-center p-8 bg-slate-50 lumi-light-panel">
        <div className="w-full max-w-sm">
          <div className="lg:hidden flex items-center gap-3 mb-8"><LumiBrand variant="inline-light" size="sm" /></div>
          <h2 className="text-2xl font-bold text-slate-800 mb-1">{t('lumi.signIn') || 'Sign in to ENZI'}</h2>
          <p className="text-sm text-slate-600 mb-6">{t('lumi.tagline') || 'Team messaging for the KARAU ecosystem'}</p>
          <div className="space-y-2.5 mb-4">
            <button onClick={handleGoogleLogin} className="w-full h-11 flex items-center justify-center gap-3 bg-white border border-slate-200 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50 hover:border-slate-300 transition-all shadow-sm" data-testid="lumi-google-sso-btn">
              <svg className="w-5 h-5" viewBox="0 0 24 24"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>
              Continue with Google
            </button>
            <button onClick={handleMicrosoftLogin} className="w-full h-11 flex items-center justify-center gap-3 bg-white border border-slate-200 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50 hover:border-slate-300 transition-all shadow-sm" data-testid="lumi-microsoft-sso-btn">
              <svg className="w-5 h-5" viewBox="0 0 24 24"><rect x="1" y="1" width="10" height="10" fill="#F25022"/><rect x="13" y="1" width="10" height="10" fill="#7FBA00"/><rect x="1" y="13" width="10" height="10" fill="#00A4EF"/><rect x="13" y="13" width="10" height="10" fill="#FFB900"/></svg>
              Continue with Microsoft
            </button>
          </div>
          {!showMore ? (
            <button onClick={() => setShowMore(true)} className="w-full text-center text-xs text-slate-500 hover:text-slate-700 mb-4 py-1 transition-colors" data-testid="show-more-auth">More sign-in options</button>
          ) : (
            <div className="space-y-2 mb-4 animate-stagger-in">
              <button onClick={handleAppleLogin} className="w-full h-10 flex items-center justify-center gap-3 bg-black text-white rounded-lg text-sm font-medium hover:bg-gray-900 transition-all shadow-sm" data-testid="lumi-apple-sso-btn">
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><path d="M17.05 20.28c-.98.95-2.05.88-3.08.4-1.09-.5-2.08-.48-3.24 0-1.44.62-2.2.44-3.06-.4C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/></svg>
                Continue with Apple
              </button>
              <div className="grid grid-cols-2 gap-2">
                <button onClick={handleGitHubLogin} className="h-10 flex items-center justify-center gap-2 bg-white border border-slate-200 rounded-lg text-xs font-medium text-slate-700 hover:bg-slate-50 transition-all" data-testid="lumi-github-sso-btn">
                  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
                  GitHub
                </button>
                <button onClick={handlePhoneLogin} className="h-10 flex items-center justify-center gap-2 bg-white border border-slate-200 rounded-lg text-xs font-medium text-slate-700 hover:bg-slate-50 transition-all" data-testid="lumi-phone-sso-btn">
                  <Smartphone className="w-4 h-4" />Phone OTP
                </button>
              </div>
              <button onClick={handlePasskeyLogin} className="w-full h-10 flex items-center justify-center gap-2 bg-white border border-slate-200 rounded-lg text-xs font-medium text-slate-700 hover:bg-slate-50 transition-all" data-testid="lumi-passkey-btn">
                <Fingerprint className="w-4 h-4" />Sign in with Passkey
              </button>
            </div>
          )}
          <div className="relative mb-5">
            <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-slate-200" /></div>
            <div className="relative flex justify-center text-xs"><span className="bg-slate-50 px-3 text-slate-500">or continue with email</span></div>
          </div>
          <form onSubmit={handleLogin} className="space-y-3">
            <Input value={email} onChange={e => setEmail(e.target.value)} type="email" placeholder="Email" className="h-11 border-slate-200 rounded-lg focus:ring-[#008080]/20 focus:border-[#008080]" data-testid="lumi-email" />
            <div className="relative">
              <Input value={password} onChange={e => setPassword(e.target.value)} type={showPw ? 'text' : 'password'} placeholder="Password" className="h-11 border-slate-200 rounded-lg pr-10 focus:ring-[#008080]/20 focus:border-[#008080]" data-testid="lumi-password" />
              <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            <Button type="submit" disabled={isLoading || !email || !password} className="w-full h-11 text-white rounded-lg font-medium hover:opacity-90 transition-opacity" style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` }} data-testid="lumi-login-btn">
              {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Sign in'}
            </Button>
          </form>
          <div className="mt-5 text-center">
            <button onClick={() => navigate('/')} className="text-sm text-slate-600 hover:text-[#008080] transition-colors" data-testid="back-to-portal">{t('lumi.backToPortal') || 'Back to Portal'}</button>
          </div>
        </div>
      </div>
    </div>
  );
};
