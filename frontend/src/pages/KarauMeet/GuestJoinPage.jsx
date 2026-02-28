import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import {
  Video, User, ArrowRight, Loader2, Shield, Sparkles,
  Lock, Mail, KeyRound, UserCheck, ChevronLeft, RefreshCw
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { useTranslation } from '@/utils/i18n';

const API = process.env.REACT_APP_BACKEND_URL;

const STEPS = { INFO: 1, OTP: 2, AGE: 3 };

const GuestJoinPage = ({ onJoin, meetingIdProp }) => {
  const params = useParams();
  const meetingId = meetingIdProp || params.meetingId;
  const navigate = useNavigate();
  const { t } = useTranslation();

  const [step, setStep] = useState(STEPS.INFO);
  const [guestName, setGuestName] = useState('');
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [ageConfirmed, setAgeConfirmed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [pageLoading, setPageLoading] = useState(true);
  const [meetingInfo, setMeetingInfo] = useState(null);
  const [error, setError] = useState(null);
  const [resendCooldown, setResendCooldown] = useState(0);
  const otpRefs = useRef([]);

  useEffect(() => {
    if (meetingId) checkMeeting();
  }, [meetingId]);

  useEffect(() => {
    if (resendCooldown > 0) {
      const timer = setTimeout(() => setResendCooldown(c => c - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [resendCooldown]);

  const checkMeeting = async () => {
    try {
      const res = await fetch(`${API}/api/karau-meet/meetings/${meetingId}/info`);
      if (res.ok) {
        setMeetingInfo(await res.json());
      } else {
        setError('notFound');
      }
    } catch {
      setMeetingInfo({ title: 'AI KARAU Meeting', meeting_id: meetingId });
    }
    setPageLoading(false);
  };

  const handleRegister = async () => {
    if (!guestName.trim()) return toast.error(t("karauMeet.enterName"));
    if (!email.trim() || !email.includes('@')) return toast.error(t("karauMeet.enterValidEmail"));
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/karau-meet/guest/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, name: guestName.trim(), meeting_id: meetingId })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        toast.success(t("karauMeet.verificationCodeSentEmail"));
        setStep(STEPS.OTP);
        setResendCooldown(60);
      } else {
        toast.error(data.detail || t("karauMeet.failedSendVerification"));
      }
    } catch {
      toast.error(t("karauMeet.networkError"));
    }
    setLoading(false);
  };

  const handleVerifyOTP = async () => {
    const code = otp.join('');
    if (code.length !== 6) return toast.error(t("karauMeet.enterFullCode"));
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/karau-meet/guest/verify-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, otp: code, meeting_id: meetingId })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        toast.success(t("karauMeet.emailVerifiedSuccess"));
        setStep(STEPS.AGE);
      } else {
        toast.error(data.detail || t("karauMeet.invalidCode"));
      }
    } catch {
      toast.error(t("karauMeet.networkError"));
    }
    setLoading(false);
  };

  const handleAgeDeclaration = async () => {
    if (!ageConfirmed) return toast.error(t("karauMeet.confirmAge"));
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/karau-meet/guest/age-declaration`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, meeting_id: meetingId, confirmed_age_16_plus: true })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        toast.success(t("karauMeet.verificationComplete"));
        const guestUser = data.user || {
          user_id: data.guest_id,
          name: guestName,
          email,
          is_guest: true,
          is_verified: true,
        };
        if (onJoin) {
          onJoin(guestUser, meetingId);
        } else {
          localStorage.setItem('karau_guest', JSON.stringify(guestUser));
          navigate(`/karau-meet/lobby/${meetingId}`);
        }
      } else {
        toast.error(data.detail || t("karauMeet.verificationFailed2"));
        setLoading(false);
      }
    } catch {
      toast.error(t("karauMeet.networkError"));
      setLoading(false);
    }
  };

  const handleResendOTP = async () => {
    if (resendCooldown > 0) return;
    try {
      const res = await fetch(`${API}/api/karau-meet/guest/resend-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, name: guestName, meeting_id: meetingId })
      });
      if (res.ok) {
        toast.success(t("karauMeet.newCodeSent"));
        setResendCooldown(60);
        setOtp(['', '', '', '', '', '']);
      }
    } catch {
      toast.error(t("karauMeet.failedResend"));
    }
  };

  const handleOtpChange = (idx, val) => {
    if (val.length > 1) val = val.slice(-1);
    if (val && !/^\d$/.test(val)) return;
    const next = [...otp];
    next[idx] = val;
    setOtp(next);
    if (val && idx < 5) otpRefs.current[idx + 1]?.focus();
  };

  const handleOtpKeyDown = (idx, e) => {
    if (e.key === 'Backspace' && !otp[idx] && idx > 0) {
      otpRefs.current[idx - 1]?.focus();
    }
    if (e.key === 'Enter' && otp.join('').length === 6) handleVerifyOTP();
  };

  const handleOtpPaste = (e) => {
    e.preventDefault();
    const text = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
    if (text.length === 6) {
      setOtp(text.split(''));
      otpRefs.current[5]?.focus();
    }
  };

  if (pageLoading) {
    return (
      <div className="min-h-screen bg-karau-bg flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-purple-400 animate-spin" />
      </div>
    );
  }

  if (error === 'notFound') {
    return (
      <div className="min-h-screen bg-karau-bg flex items-center justify-center p-4">
        <Card className="bg-karau-card/80 border-karau-border max-w-md w-full rounded-2xl">
          <CardContent className="p-8 text-center">
            <div className="w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center mx-auto mb-4">
              <Video className="w-8 h-8 text-red-400" />
            </div>
            <h2 className="text-xl font-bold text-white mb-2">{t("karauMeet.meetingNotFound")}</h2>
            <p className="text-karau-muted text-sm mb-6">{t("karauMeet.meetingNotFoundDesc")}</p>
            <Button onClick={() => navigate('/karau-meet')} variant="outline" className="border-white/10 text-slate-300 rounded-xl" data-testid="guest-back-btn">
              {t("karauMeet.backToPortalBtn")}
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const stepLabels = [
    { num: 1, label: t("karauMeet.stepDetails"), icon: User },
    { num: 2, label: t("karauMeet.stepVerify"), icon: KeyRound },
    { num: 3, label: t("karauMeet.stepConfirm"), icon: UserCheck },
  ];

  return (
    <div className="min-h-screen bg-karau-bg flex items-center justify-center p-4" style={{ fontFamily: "'IBM Plex Sans', sans-serif" }}>
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-emerald-500/5 rounded-full blur-3xl" />
      </div>

      <Card className="bg-karau-card/80 backdrop-blur-xl border-karau-border max-w-md w-full relative z-10 rounded-2xl" data-testid="guest-join-card">
        <CardContent className="p-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <img
              src="https://customer-assets.emergentagent.com/job_1fba32e3-e5a1-4174-b642-d1cd092309b3/artifacts/a7nojb8x_IMG_8477.jpeg"
              alt="AI KARAU"
              className="w-10 h-10 rounded-xl object-cover"
            />
            <span className="text-xl font-bold bg-gradient-to-r from-purple-400 via-violet-300 to-emerald-400 bg-clip-text text-transparent">
              AI KARAU Meeting
            </span>
          </div>

          <div className="text-center mb-5">
            <h1 className="text-xl font-bold text-white mb-1" data-testid="guest-meeting-title">
              {meetingInfo?.title || 'AI KARAU Meeting'}
            </h1>
            <p className="text-xs text-karau-muted">
              {t("karauMeet.meetingId")}: <span className="font-mono text-purple-400 font-semibold">{meetingId}</span>
            </p>
          </div>

          <div className="flex items-center justify-center gap-1 mb-6" data-testid="guest-step-indicator">
            {stepLabels.map((s, i) => (
              <div key={s.num} className="flex items-center">
                <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                  step === s.num ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30' :
                  step > s.num ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/20' :
                  'bg-karau-surface/40 text-slate-500 border border-white/5'
                }`}>
                  <s.icon className="w-3.5 h-3.5" />
                  {s.label}
                </div>
                {i < 2 && <div className={`w-6 h-px mx-1 ${step > s.num ? 'bg-emerald-500/40' : 'bg-karau-border'}`} />}
              </div>
            ))}
          </div>

          {step === STEPS.INFO && (
            <div className="space-y-4" data-testid="guest-step-info">
              <div>
                <label className="text-sm font-medium text-slate-300 mb-1.5 block">{t("karauMeet.yourName")}</label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <Input
                    placeholder={t("karauMeet.enterFullName")}
                    value={guestName}
                    onChange={(e) => setGuestName(e.target.value)}
                    className="bg-karau-bg/60 border-white/10 text-white pl-10 h-11 rounded-xl focus:border-purple-500/40"
                    autoFocus
                    data-testid="guest-name-input"
                  />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium text-slate-300 mb-1.5 block">{t("karauMeet.emailAddress")}</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <Input
                    type="email"
                    placeholder={t("karauMeet.emailPlaceholder")}
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleRegister()}
                    className="bg-karau-bg/60 border-white/10 text-white pl-10 h-11 rounded-xl focus:border-purple-500/40"
                    data-testid="guest-email-input"
                  />
                </div>
                <p className="text-xs text-slate-500 mt-1">{t("karauMeet.verificationCodeWillBeSent")}</p>
              </div>
              <Button
                onClick={handleRegister}
                disabled={loading || !guestName.trim() || !email.includes('@')}
                className="w-full h-11 bg-gradient-to-r from-purple-600 to-violet-600 hover:from-purple-500 hover:to-violet-500 text-white font-semibold rounded-xl shadow-lg shadow-purple-500/20"
                data-testid="guest-send-otp-btn"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin mr-2" /> : <ArrowRight className="w-5 h-5 mr-2" />}
                {loading ? t("karauMeet.sendingCode") : t("karauMeet.sendVerificationCode")}
              </Button>
            </div>
          )}

          {step === STEPS.OTP && (
            <div className="space-y-4" data-testid="guest-step-otp">
              <div className="text-center">
                <div className="w-12 h-12 rounded-full bg-purple-500/10 flex items-center justify-center mx-auto mb-3">
                  <Mail className="w-6 h-6 text-purple-400" />
                </div>
                <p className="text-sm text-slate-300">{t("karauMeet.enterDigitCode")}</p>
                <p className="text-purple-400 font-medium text-sm">{email}</p>
              </div>

              <div className="flex justify-center gap-2" data-testid="guest-otp-inputs">
                {otp.map((digit, idx) => (
                  <input
                    key={idx}
                    ref={el => otpRefs.current[idx] = el}
                    type="text"
                    inputMode="numeric"
                    maxLength={1}
                    value={digit}
                    onChange={(e) => handleOtpChange(idx, e.target.value)}
                    onKeyDown={(e) => handleOtpKeyDown(idx, e)}
                    onPaste={idx === 0 ? handleOtpPaste : undefined}
                    className="w-11 h-12 text-center text-lg font-bold text-white bg-karau-bg/60 border border-white/10 rounded-lg focus:border-purple-500 focus:ring-1 focus:ring-purple-500/50 outline-none transition-all"
                    data-testid={`guest-otp-digit-${idx}`}
                  />
                ))}
              </div>

              <Button
                onClick={handleVerifyOTP}
                disabled={loading || otp.join('').length !== 6}
                className="w-full h-11 bg-gradient-to-r from-purple-600 to-violet-600 hover:from-purple-500 hover:to-violet-500 text-white font-semibold rounded-xl shadow-lg shadow-purple-500/20"
                data-testid="guest-verify-otp-btn"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin mr-2" /> : <KeyRound className="w-5 h-5 mr-2" />}
                {loading ? t("karauMeet.verifying") : t("karauMeet.verifyCode")}
              </Button>

              <div className="flex items-center justify-between">
                <button
                  onClick={() => { setStep(STEPS.INFO); setOtp(['','','','','','']); }}
                  className="text-xs text-karau-muted hover:text-white flex items-center gap-1 transition-colors"
                  data-testid="guest-back-to-info"
                >
                  <ChevronLeft className="w-3 h-3" /> {t("karauMeet.changeEmail")}
                </button>
                <button
                  onClick={handleResendOTP}
                  disabled={resendCooldown > 0}
                  className={`text-xs flex items-center gap-1 transition-colors ${
                    resendCooldown > 0 ? 'text-slate-500 cursor-not-allowed' : 'text-purple-400 hover:text-purple-300'
                  }`}
                  data-testid="guest-resend-otp"
                >
                  <RefreshCw className="w-3 h-3" />
                  {resendCooldown > 0 ? t("karauMeet.resendIn", { seconds: resendCooldown }) : t("karauMeet.resendCode")}
                </button>
              </div>
            </div>
          )}

          {step === STEPS.AGE && (
            <div className="space-y-4" data-testid="guest-step-age">
              <div className="text-center">
                <div className="w-12 h-12 rounded-full bg-emerald-500/10 flex items-center justify-center mx-auto mb-3">
                  <UserCheck className="w-6 h-6 text-emerald-400" />
                </div>
                <p className="text-sm text-slate-300 mb-1">{t("karauMeet.emailVerifiedSuccessDesc")}</p>
                <p className="text-xs text-karau-muted">{t("karauMeet.lastStepBefore")}</p>
              </div>

              <div className="bg-karau-bg/60 rounded-xl p-4 border border-white/5">
                <div className="flex items-start gap-3">
                  <Checkbox
                    id="age-confirm"
                    checked={ageConfirmed}
                    onCheckedChange={setAgeConfirmed}
                    className="mt-0.5 border-white/20 data-[state=checked]:bg-emerald-500 data-[state=checked]:border-emerald-500"
                    data-testid="guest-age-checkbox"
                  />
                  <label htmlFor="age-confirm" className="text-sm text-slate-300 cursor-pointer leading-relaxed">
                    {t("karauMeet.ageConfirmTextPlain")}
                  </label>
                </div>
              </div>

              <Button
                onClick={handleAgeDeclaration}
                disabled={loading || !ageConfirmed}
                className="w-full h-11 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-400 hover:to-emerald-500 text-white font-semibold rounded-xl shadow-lg shadow-emerald-500/20"
                data-testid="guest-join-btn"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin mr-2" /> : <ArrowRight className="w-5 h-5 mr-2" />}
                {loading ? t("karauMeet.joining") : t("karauMeet.joinMeetingBtn")}
              </Button>

              <button
                onClick={() => setStep(STEPS.OTP)}
                className="w-full text-xs text-karau-muted hover:text-white flex items-center justify-center gap-1 transition-colors"
                data-testid="guest-back-to-otp"
              >
                <ChevronLeft className="w-3 h-3" /> {t("karauMeet.backToPortalBtn")}
              </button>
            </div>
          )}

          <div className="mt-5 grid grid-cols-3 gap-2">
            {[
              { icon: Shield, label: t("karauMeet.encrypted"), color: 'text-emerald-400' },
              { icon: Sparkles, label: t("karauMeet.aiPowered"), color: 'text-purple-400' },
              { icon: Lock, label: t("karauMeet.verified"), color: 'text-violet-400' },
            ].map((item, i) => (
              <div key={i} className="flex flex-col items-center gap-1 p-2 rounded-lg bg-karau-bg/40">
                <item.icon className={`w-4 h-4 ${item.color}`} />
                <span className="text-[10px] text-slate-500">{item.label}</span>
              </div>
            ))}
          </div>

          <div className="mt-3 text-center">
            <button
              onClick={() => navigate('/karau-meet')}
              className="text-xs text-slate-500 hover:text-purple-400 transition-colors"
              data-testid="guest-signin-link"
            >
              {t("karauMeet.haveAccount")}
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default GuestJoinPage;
