import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast, Toaster } from 'sonner';
import { MessageCircle, Eye, EyeOff, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useTranslation } from '@/utils/i18n';
import { API, ESY } from './constants';

export const LumiLogin = ({ onLogin }) => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPw, setShowPw] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const res = await fetch(`${API}/api/auth/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password }) });
      if (res.ok) {
        const data = await res.json();
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('karau_user', JSON.stringify(data.user));
        onLogin(data.user);
        toast.success('Welcome to LUMI!');
      } else { const err = await res.json(); toast.error(err.detail || 'Login failed'); }
    } catch (e) { toast.error('Connection error'); }
    setIsLoading(false);
  };

  // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
  const handleGoogleLogin = () => {
    const redirectUrl = window.location.origin + '/lumi';
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  const handleMicrosoftLogin = () => {
    toast.info('Microsoft SSO is coming soon. Please use Google or email login.');
  };

  return (
    <div className="min-h-screen flex" style={{ fontFamily: "'Inter', -apple-system, sans-serif" }}>
      <Toaster position="top-right" richColors />
      <div className="hidden lg:flex lg:w-1/2 bg-[#36454F] items-center justify-center relative overflow-hidden">
        <img src="https://images.unsplash.com/photo-1719667052333-1cba4797fd85?w=1200&q=80" alt="" className="absolute inset-0 w-full h-full object-cover opacity-20" />
        <div className="relative z-10 text-center px-12">
          <div className="w-16 h-16 mx-auto rounded-lg flex items-center justify-center mb-6 shadow-lg" style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` }}>
            <MessageCircle className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-3">LUMI</h1>
          <p className="text-lg text-slate-200">Enterprise Team Messenger</p>
          <p className="text-sm text-slate-300 mt-2 max-w-sm">Secure, domain-protected team communication for the modern workplace.</p>
        </div>
      </div>
      <div className="flex-1 flex items-center justify-center p-8 bg-slate-50">
        <div className="w-full max-w-sm">
          <div className="lg:hidden flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` }}><MessageCircle className="w-5 h-5 text-white" /></div>
            <span className="text-xl font-bold text-slate-900">LUMI</span>
          </div>
          <h2 className="text-2xl font-semibold text-slate-900 mb-1">{t('lumi.signIn') || 'Sign in to LUMI'}</h2>
          <p className="text-sm text-slate-500 mb-6">{t('lumi.tagline') || 'Team messaging for the KARAU ecosystem'}</p>

          {/* SSO Buttons */}
          <div className="space-y-3 mb-6">
            <button onClick={handleGoogleLogin}
              className="w-full h-11 flex items-center justify-center gap-3 bg-white border border-slate-200 rounded-md text-sm font-medium text-slate-700 hover:bg-slate-50 hover:border-slate-300 transition-all shadow-sm"
              data-testid="lumi-google-sso-btn">
              <svg className="w-5 h-5" viewBox="0 0 24 24"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>
              Sign in with Google
            </button>
            <button onClick={handleMicrosoftLogin}
              className="w-full h-11 flex items-center justify-center gap-3 bg-white border border-slate-200 rounded-md text-sm font-medium text-slate-700 hover:bg-slate-50 hover:border-slate-300 transition-all shadow-sm"
              data-testid="lumi-microsoft-sso-btn">
              <svg className="w-5 h-5" viewBox="0 0 24 24"><rect x="1" y="1" width="10" height="10" fill="#F25022"/><rect x="13" y="1" width="10" height="10" fill="#7FBA00"/><rect x="1" y="13" width="10" height="10" fill="#00A4EF"/><rect x="13" y="13" width="10" height="10" fill="#FFB900"/></svg>
              Sign in with Microsoft
            </button>
          </div>

          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-slate-200" /></div>
            <div className="relative flex justify-center text-xs"><span className="bg-slate-50 px-3 text-slate-400">or continue with email</span></div>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            <Input value={email} onChange={e => setEmail(e.target.value)} type="email" placeholder="Email"
              className="h-11 border-slate-200 rounded-md focus:ring-[#008080]/20 focus:border-[#008080]" data-testid="lumi-email" />
            <div className="relative">
              <Input value={password} onChange={e => setPassword(e.target.value)} type={showPw ? 'text' : 'password'} placeholder="Password"
                className="h-11 border-slate-200 rounded-md pr-10 focus:ring-[#008080]/20 focus:border-[#008080]" data-testid="lumi-password" />
              <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            <Button type="submit" disabled={isLoading || !email || !password}
              className="w-full h-11 text-white rounded-md font-medium hover:opacity-90 transition-opacity"
              style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` }}
              data-testid="lumi-login-btn">
              {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Sign in'}
            </Button>
          </form>
          <div className="mt-6 text-center">
            <button onClick={() => navigate('/')} className="text-sm text-slate-400 hover:text-[#008080] transition-colors" data-testid="back-to-portal">
              {t('lumi.backToPortal') || 'Back to Portal'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
