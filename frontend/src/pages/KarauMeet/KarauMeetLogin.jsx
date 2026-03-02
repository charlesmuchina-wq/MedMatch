import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { toast } from 'sonner';
import {
  Users, Shield, Sparkles, Loader2, Eye, Mic,
  Globe, Brain, Wand2, Volume2, Zap, Lock,
  ArrowRight, ChevronRight
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useTranslation } from '@/utils/i18n';
import GlobalLanguageSelector from '@/components/GlobalLanguageSelector';

const API = process.env.REACT_APP_BACKEND_URL;

const KarauMeetLogin = ({ onLogin }) => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [meetingId, setMeetingId] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [activeTab, setActiveTab] = useState('signin');
  const [activeFeature, setActiveFeature] = useState(0);

  const AI_FEATURES = [
    { icon: Brain, labelKey: 'karauMeet.aiMeetingCoach', descKey: 'karauMeet.realtimeTips', color: 'from-purple-500 to-violet-600' },
    { icon: Eye, labelKey: 'karauMeet.eyeContactCorrection', descKey: 'karauMeet.aiGazeAlignment', color: 'from-teal-500 to-emerald-600' },
    { icon: Globe, labelKey: 'karauMeet.liveTranscription', descKey: 'karauMeet.fortyLangCaptions', color: 'from-blue-500 to-indigo-600' },
    { icon: Wand2, labelKey: 'karauMeet.cinematicDirector', descKey: 'karauMeet.autoCameraSwitching', color: 'from-amber-500 to-orange-600' },
    { icon: Volume2, labelKey: 'karauMeet.spatialAudio', descKey: 'karauMeet.threeDPositionalSound', color: 'from-rose-500 to-pink-600' },
    { icon: Mic, labelKey: 'karauMeet.noiseCancellation', descKey: 'karauMeet.aiAudioCleanup', color: 'from-cyan-500 to-blue-600' },
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveFeature(prev => (prev + 1) % AI_FEATURES.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const response = await fetch(`${API}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('karau_user', JSON.stringify(data.user));
        onLogin(data.user);
        toast.success(t("karauMeet.welcomeToast"));
      } else {
        const error = await response.json();
        toast.error(error.detail || t("karauMeet.loginFailed"));
      }
    } catch (error) {
      toast.error(t("karauMeet.connectionError"));
    }
    setIsLoading(false);
  };

  const handleJoinMeeting = (e) => {
    e.preventDefault();
    if (!meetingId.trim()) {
      toast.error(t("karauMeet.enterMeetingIdError"));
      return;
    }
    navigate(`/karau-meet/join/${meetingId.toUpperCase()}`);
  };

  const handleGoogleSignIn = async () => {
    window.location.href = `${API}/api/auth/google`;
  };

  return (
    <div className="min-h-screen bg-[#0c0d1a] flex overflow-hidden" style={{ fontFamily: "'IBM Plex Sans', sans-serif" }}>
      {/* Left side - Feature showcase */}
      <div className="hidden lg:flex lg:w-[55%] relative flex-col justify-between p-12 overflow-hidden">
        {/* Ambient background effects */}
        <div className="absolute inset-0">
          <div className="absolute top-0 left-0 w-[500px] h-[500px] bg-purple-600/8 rounded-full blur-[120px]" />
          <div className="absolute bottom-0 right-0 w-[400px] h-[400px] bg-teal-500/8 rounded-full blur-[100px]" />
          <div className="absolute top-1/2 left-1/3 w-[300px] h-[300px] bg-indigo-500/5 rounded-full blur-[80px]" />
        </div>

        {/* Logo + tagline */}
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-2">
            <img
              src="https://customer-assets.emergentagent.com/job_1fba32e3-e5a1-4174-b642-d1cd092309b3/artifacts/a7nojb8x_IMG_8477.jpeg"
              alt="AI KARAU"
              className="w-12 h-12 rounded-2xl object-cover ring-2 ring-white/10"
            />
            <span className="text-xl font-bold text-white tracking-tight">AI KARAU</span>
          </div>
          <p className="text-slate-500 text-sm ml-[60px] -mt-1">{t("karauMeet.distanceZero")}</p>
        </div>

        {/* Hero section */}
        <div className="relative z-10 flex-1 flex flex-col justify-center max-w-xl">
          <h1 className="text-5xl font-bold text-white leading-[1.1] tracking-tight mb-6">
            {t("karauMeet.meetingsFeelLike")}
            <br />
            <span className="bg-gradient-to-r from-teal-400 via-purple-400 to-indigo-400 bg-clip-text text-transparent">
              {t("karauMeet.likeBeingThere")}
            </span>
          </h1>
          <p className="text-lg text-slate-400 leading-relaxed mb-10 max-w-md">
            {t("karauMeet.loginHeroDesc")}
          </p>

          {/* Feature carousel */}
          <div className="space-y-3" data-testid="feature-carousel">
            {AI_FEATURES.map((feature, idx) => (
              <div
                key={idx}
                className={`flex items-center gap-4 p-4 rounded-2xl border transition-all duration-500 cursor-default ${
                  idx === activeFeature
                    ? 'bg-white/[0.06] border-white/15 scale-[1.02]'
                    : 'bg-transparent border-transparent opacity-40 scale-100'
                }`}
                onMouseEnter={() => setActiveFeature(idx)}
                data-testid={`feature-${idx}`}
              >
                <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center flex-shrink-0 shadow-lg ${
                  idx === activeFeature ? 'shadow-purple-500/20' : ''
                }`}>
                  <feature.icon className="w-5 h-5 text-white" />
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-white">{t(feature.labelKey)}</p>
                  <p className="text-xs text-slate-500">{t(feature.descKey)}</p>
                </div>
                {idx === activeFeature && (
                  <Zap className="w-4 h-4 text-teal-400 ml-auto flex-shrink-0 animate-pulse" />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Bottom trust badges */}
        <div className="relative z-10 flex items-center gap-6 text-xs text-slate-600">
          <span className="flex items-center gap-1.5"><Lock className="w-3.5 h-3.5" /> {t("karauMeet.e2eEncrypted")}</span>
          <span className="flex items-center gap-1.5"><Shield className="w-3.5 h-3.5" /> {t("karauMeet.soc2Compliant")}</span>
          <span className="flex items-center gap-1.5"><Globe className="w-3.5 h-3.5" /> {t("karauMeet.fortyPlusLanguages")}</span>
        </div>
      </div>

      {/* Right side - Auth form */}
      <div className="flex-1 flex items-center justify-center p-6 lg:p-12 relative">
        {/* Subtle background glow */}
        <div className="absolute inset-0 bg-gradient-to-bl from-purple-600/5 via-transparent to-teal-500/5" />

        {/* Language selector - top right */}
        <div className="absolute top-4 right-4 z-20" data-testid="login-language-selector">
          <GlobalLanguageSelector compact={false} />
        </div>
        
        <div className="w-full max-w-[420px] relative z-10">
          {/* Mobile logo */}
          <div className="lg:hidden text-center mb-8">
            <img
              src="https://customer-assets.emergentagent.com/job_1fba32e3-e5a1-4174-b642-d1cd092309b3/artifacts/a7nojb8x_IMG_8477.jpeg"
              alt="AI KARAU"
              className="w-20 h-20 rounded-2xl object-cover shadow-lg shadow-purple-500/20 mx-auto mb-4"
            />
            <h2 className="text-2xl font-bold text-white">AI KARAU</h2>
            <p className="text-slate-500 text-sm">{t("karauMeet.distanceZero")}</p>
          </div>

          {/* Tab switcher */}
          <div className="flex gap-1 p-1 bg-white/[0.04] rounded-full mb-8 border border-white/[0.06]">
            <button
              onClick={() => setActiveTab('signin')}
              className={`flex-1 py-2.5 px-4 rounded-full text-sm font-medium transition-all duration-300 ${
                activeTab === 'signin'
                  ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg shadow-purple-500/25'
                  : 'text-slate-500 hover:text-slate-300'
              }`}
              data-testid="tab-signin"
            >
              {t("karauMeet.signIn")}
            </button>
            <button
              onClick={() => setActiveTab('join')}
              className={`flex-1 py-2.5 px-4 rounded-full text-sm font-medium transition-all duration-300 ${
                activeTab === 'join'
                  ? 'bg-gradient-to-r from-teal-600 to-emerald-600 text-white shadow-lg shadow-teal-500/25'
                  : 'text-slate-500 hover:text-slate-300'
              }`}
              data-testid="tab-join"
            >
              {t("karauMeet.joinMeetingTab")}
            </button>
          </div>

          {activeTab === 'signin' && (
            <div className="animate-in fade-in duration-300">
              <h3 className="text-2xl font-bold text-white mb-1">{t("karauMeet.welcomeBackLogin")}</h3>
              <p className="text-slate-500 text-sm mb-8">{t("karauMeet.signInToAccount")}</p>

              <form onSubmit={handleLogin} className="space-y-5">
                <div>
                  <Label className="text-slate-400 text-xs font-medium uppercase tracking-wider">{t("karauMeet.email")}</Label>
                  <Input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder={t("karauMeet.emailPlaceholder")}
                    className="bg-black/30 border-white/10 text-white mt-2 h-12 rounded-xl focus:border-purple-500/50 focus:ring-2 focus:ring-purple-500/20 placeholder-slate-600"
                    required
                    data-testid="input-email"
                  />
                </div>

                <div>
                  <Label className="text-slate-400 text-xs font-medium uppercase tracking-wider">{t("karauMeet.password")}</Label>
                  <div className="relative">
                    <Input
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder={t("karauMeet.enterPassword")}
                      className="bg-black/30 border-white/10 text-white mt-2 h-12 pr-12 rounded-xl focus:border-purple-500/50 focus:ring-2 focus:ring-purple-500/20 placeholder-slate-600"
                      required
                      data-testid="input-password"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-4 top-1/2 translate-y-[1px] text-slate-600 hover:text-slate-400 transition-colors"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                <Button
                  type="submit"
                  className="w-full h-12 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-semibold rounded-full shadow-lg shadow-purple-500/25 transition-all duration-300 hover:scale-[1.02] active:scale-[0.98]"
                  disabled={isLoading}
                  data-testid="btn-signin"
                >
                  {isLoading ? (
                    <><Loader2 className="w-5 h-5 animate-spin mr-2" /> {t("karauMeet.signingIn")}</>
                  ) : (
                    <>{t("karauMeet.signIn")} <ArrowRight className="w-4 h-4 ml-2" /></>
                  )}
                </Button>
              </form>

              {/* Divider */}
              <div className="relative my-8">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-white/[0.06]"></div>
                </div>
                <div className="relative flex justify-center">
                  <span className="px-4 bg-[#0c0d1a] text-slate-600 text-xs uppercase tracking-wider">{t("karauMeet.or")}</span>
                </div>
              </div>

              {/* Social buttons */}
              <div className="grid grid-cols-2 gap-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleGoogleSignIn}
                  className="h-11 bg-white/[0.04] hover:bg-white/[0.08] text-slate-300 border-white/[0.08] rounded-xl transition-all duration-300"
                  data-testid="btn-google"
                >
                  <svg className="w-4 h-4 mr-2" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                  {t("karauMeet.google")}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => toast.info(t("karauMeet.appleComingSoon"))}
                  className="h-11 bg-white/[0.04] hover:bg-white/[0.08] text-slate-300 border-white/[0.08] rounded-xl transition-all duration-300"
                  data-testid="btn-apple"
                >
                  <svg className="w-4 h-4 mr-2" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09l.01-.01zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/>
                  </svg>
                  {t("karauMeet.apple")}
                </Button>
              </div>
            </div>
          )}

          {activeTab === 'join' && (
            <div className="animate-in fade-in duration-300">
              <h3 className="text-2xl font-bold text-white mb-1">{t("karauMeet.joinAMeeting")}</h3>
              <p className="text-slate-500 text-sm mb-8">{t("karauMeet.enterCodeToJoin")}</p>

              <form onSubmit={handleJoinMeeting} className="space-y-5">
                <div>
                  <Label className="text-slate-400 text-xs font-medium uppercase tracking-wider">{t("karauMeet.meetingId")}</Label>
                  <Input
                    type="text"
                    value={meetingId}
                    onChange={(e) => setMeetingId(e.target.value.toUpperCase())}
                    placeholder="ABC-DEFG-HIJ"
                    className="bg-black/30 border-white/10 text-white mt-2 h-14 text-center text-lg uppercase tracking-[0.3em] rounded-xl focus:border-teal-500/50 focus:ring-2 focus:ring-teal-500/20 placeholder-slate-600 font-mono"
                    data-testid="input-meeting-id"
                  />
                </div>

                <Button
                  type="submit"
                  className="w-full h-12 bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-500 hover:to-emerald-500 text-white font-semibold rounded-full shadow-lg shadow-teal-500/25 transition-all duration-300 hover:scale-[1.02] active:scale-[0.98]"
                  data-testid="btn-join-meeting"
                >
                  <Users className="w-5 h-5 mr-2" />
                  {t("karauMeet.joinAsGuest")}
                </Button>

                <p className="text-xs text-slate-600 text-center leading-relaxed">
                  {t("karauMeet.noAccountNeeded")}
                </p>
              </form>

              {/* AI Features grid for mobile */}
              <div className="mt-10 grid grid-cols-3 gap-3 lg:hidden">
                {AI_FEATURES.slice(0, 3).map((f, i) => (
                  <div key={i} className="flex flex-col items-center gap-2 p-3 bg-white/[0.03] rounded-xl border border-white/[0.05]">
                    <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${f.color} flex items-center justify-center`}>
                      <f.icon className="w-4 h-4 text-white" />
                    </div>
                    <span className="text-[10px] text-slate-500 text-center">{t(f.labelKey)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Footer */}
          <div className="mt-8 pt-6 border-t border-white/[0.04] flex items-center justify-between">
            <div className="flex items-center gap-3 text-xs text-slate-600">
              <Shield className="w-3.5 h-3.5 text-teal-500/50" />
              <span>{t("karauMeet.e2eEncrypted")}</span>
              <Sparkles className="w-3.5 h-3.5 text-purple-500/50" />
              <span>{t("karauMeet.aiPowered")}</span>
            </div>
            <Link to="/" className="text-xs text-slate-600 hover:text-purple-400 transition-colors flex items-center gap-1">
              {t("karauMeet.home")} <ChevronRight className="w-3 h-3" />
            </Link>
          </div>
        </div>
      </div>

      {/* CSS Animations */}
      <style>{`
        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        .animate-in { animation: fadeIn 0.3s ease-out; }
      `}</style>
    </div>
  );
};

export default KarauMeetLogin;
