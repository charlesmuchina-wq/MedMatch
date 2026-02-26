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
      const t = setTimeout(() => setResendCooldown(c => c - 1), 1000);
      return () => clearTimeout(t);
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

  // Step 1: Register guest & send OTP
  const handleRegister = async () => {
    if (!guestName.trim()) return toast.error('Please enter your name');
    if (!email.trim() || !email.includes('@')) return toast.error('Please enter a valid email');
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/karau-meet/guest/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, name: guestName.trim(), meeting_id: meetingId })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        toast.success('Verification code sent to your email');
        setStep(STEPS.OTP);
        setResendCooldown(60);
      } else {
        toast.error(data.detail || 'Failed to send verification code');
      }
    } catch {
      toast.error('Network error. Please try again.');
    }
    setLoading(false);
  };

  // Step 2: Verify OTP
  const handleVerifyOTP = async () => {
    const code = otp.join('');
    if (code.length !== 6) return toast.error('Please enter the 6-digit code');
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/karau-meet/guest/verify-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, otp: code, meeting_id: meetingId })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        toast.success('Email verified!');
        setStep(STEPS.AGE);
      } else {
        toast.error(data.detail || 'Invalid code');
      }
    } catch {
      toast.error('Network error. Please try again.');
    }
    setLoading(false);
  };

  // Step 3: Age declaration & join
  const handleAgeDeclaration = async () => {
    if (!ageConfirmed) return toast.error('Please confirm your age to continue');
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/karau-meet/guest/age-declaration`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, meeting_id: meetingId, confirmed_age_16_plus: true })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        toast.success('Verification complete!');
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
        toast.error(data.detail || 'Verification failed');
        setLoading(false);
      }
    } catch {
      toast.error('Network error. Please try again.');
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
        toast.success('New code sent!');
        setResendCooldown(60);
        setOtp(['', '', '', '', '', '']);
      }
    } catch {
      toast.error('Failed to resend code');
    }
  };

  // OTP digit input handler
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
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-turquoise animate-spin" />
      </div>
    );
  }

  if (error === 'notFound') {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
        <Card className="bg-slate-800/80 border-slate-700 max-w-md w-full">
          <CardContent className="p-8 text-center">
            <div className="w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center mx-auto mb-4">
              <Video className="w-8 h-8 text-red-400" />
            </div>
            <h2 className="text-xl font-bold text-white mb-2">Meeting Not Found</h2>
            <p className="text-slate-400 text-sm mb-6">This meeting doesn't exist or has ended.</p>
            <Button onClick={() => navigate('/karau-meet')} variant="outline" className="border-slate-600 text-slate-300" data-testid="guest-back-btn">
              Back to Portal
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Step indicators
  const stepLabels = [
    { num: 1, label: 'Details', icon: User },
    { num: 2, label: 'Verify', icon: KeyRound },
    { num: 3, label: 'Confirm', icon: UserCheck },
  ];

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-turquoise/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-violet-500/5 rounded-full blur-3xl" />
      </div>

      <Card className="bg-slate-800/80 backdrop-blur-xl border-slate-700 max-w-md w-full relative z-10" data-testid="guest-join-card">
        <CardContent className="p-8">
          {/* Logo */}
          <div className="flex items-center justify-center gap-3 mb-4">
            <img
              src="https://customer-assets.emergentagent.com/job_1fba32e3-e5a1-4174-b642-d1cd092309b3/artifacts/a7nojb8x_IMG_8477.jpeg"
              alt="AI KARAU"
              className="w-10 h-10 rounded-xl object-cover"
            />
            <span className="text-xl font-bold bg-gradient-to-r from-teal-400 to-amber-400 bg-clip-text text-transparent">
              AI KARAU Meeting
            </span>
          </div>

          {/* Meeting Info */}
          <div className="text-center mb-5">
            <h1 className="text-xl font-bold text-white mb-1" data-testid="guest-meeting-title">
              {meetingInfo?.title || 'AI KARAU Meeting'}
            </h1>
            <p className="text-xs text-slate-400">
              Meeting ID: <span className="font-mono text-turquoise font-semibold">{meetingId}</span>
            </p>
          </div>

          {/* Step Indicator */}
          <div className="flex items-center justify-center gap-1 mb-6" data-testid="guest-step-indicator">
            {stepLabels.map((s, i) => (
              <div key={s.num} className="flex items-center">
                <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                  step === s.num ? 'bg-turquoise/20 text-turquoise border border-turquoise/30' :
                  step > s.num ? 'bg-green-500/15 text-green-400 border border-green-500/20' :
                  'bg-slate-700/40 text-slate-500 border border-slate-600/30'
                }`}>
                  <s.icon className="w-3.5 h-3.5" />
                  {s.label}
                </div>
                {i < 2 && <div className={`w-6 h-px mx-1 ${step > s.num ? 'bg-green-500/40' : 'bg-slate-600/40'}`} />}
              </div>
            ))}
          </div>

          {/* STEP 1: Name + Email */}
          {step === STEPS.INFO && (
            <div className="space-y-4" data-testid="guest-step-info">
              <div>
                <label className="text-sm font-medium text-slate-300 mb-1.5 block">Your Name</label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <Input
                    placeholder="Enter your full name"
                    value={guestName}
                    onChange={(e) => setGuestName(e.target.value)}
                    className="bg-slate-900 border-slate-600 text-white pl-10 h-11"
                    autoFocus
                    data-testid="guest-name-input"
                  />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium text-slate-300 mb-1.5 block">Email Address</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <Input
                    type="email"
                    placeholder="your@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleRegister()}
                    className="bg-slate-900 border-slate-600 text-white pl-10 h-11"
                    data-testid="guest-email-input"
                  />
                </div>
                <p className="text-xs text-slate-500 mt-1">We'll send a verification code to this email</p>
              </div>
              <Button
                onClick={handleRegister}
                disabled={loading || !guestName.trim() || !email.includes('@')}
                className="w-full h-11 bg-gradient-to-r from-turquoise to-cyan-500 hover:from-turquoise/90 hover:to-cyan-500/90 text-white font-semibold"
                data-testid="guest-send-otp-btn"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin mr-2" /> : <ArrowRight className="w-5 h-5 mr-2" />}
                {loading ? 'Sending code...' : 'Send Verification Code'}
              </Button>
            </div>
          )}

          {/* STEP 2: OTP Verification */}
          {step === STEPS.OTP && (
            <div className="space-y-4" data-testid="guest-step-otp">
              <div className="text-center">
                <div className="w-12 h-12 rounded-full bg-turquoise/10 flex items-center justify-center mx-auto mb-3">
                  <Mail className="w-6 h-6 text-turquoise" />
                </div>
                <p className="text-sm text-slate-300">Enter the 6-digit code sent to</p>
                <p className="text-turquoise font-medium text-sm">{email}</p>
              </div>

              {/* OTP Inputs */}
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
                    className="w-11 h-12 text-center text-lg font-bold text-white bg-slate-900 border border-slate-600 rounded-lg focus:border-turquoise focus:ring-1 focus:ring-turquoise/50 outline-none transition-all"
                    data-testid={`guest-otp-digit-${idx}`}
                  />
                ))}
              </div>

              <Button
                onClick={handleVerifyOTP}
                disabled={loading || otp.join('').length !== 6}
                className="w-full h-11 bg-gradient-to-r from-turquoise to-cyan-500 hover:from-turquoise/90 hover:to-cyan-500/90 text-white font-semibold"
                data-testid="guest-verify-otp-btn"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin mr-2" /> : <KeyRound className="w-5 h-5 mr-2" />}
                {loading ? 'Verifying...' : 'Verify Code'}
              </Button>

              <div className="flex items-center justify-between">
                <button
                  onClick={() => { setStep(STEPS.INFO); setOtp(['','','','','','']); }}
                  className="text-xs text-slate-400 hover:text-white flex items-center gap-1 transition-colors"
                  data-testid="guest-back-to-info"
                >
                  <ChevronLeft className="w-3 h-3" /> Change email
                </button>
                <button
                  onClick={handleResendOTP}
                  disabled={resendCooldown > 0}
                  className={`text-xs flex items-center gap-1 transition-colors ${
                    resendCooldown > 0 ? 'text-slate-500 cursor-not-allowed' : 'text-turquoise hover:text-turquoise/80'
                  }`}
                  data-testid="guest-resend-otp"
                >
                  <RefreshCw className="w-3 h-3" />
                  {resendCooldown > 0 ? `Resend in ${resendCooldown}s` : 'Resend code'}
                </button>
              </div>
            </div>
          )}

          {/* STEP 3: Age Declaration */}
          {step === STEPS.AGE && (
            <div className="space-y-4" data-testid="guest-step-age">
              <div className="text-center">
                <div className="w-12 h-12 rounded-full bg-green-500/10 flex items-center justify-center mx-auto mb-3">
                  <UserCheck className="w-6 h-6 text-green-400" />
                </div>
                <p className="text-sm text-slate-300 mb-1">Email verified successfully!</p>
                <p className="text-xs text-slate-400">One last step before joining</p>
              </div>

              <div className="bg-slate-900/60 rounded-lg p-4 border border-slate-700/50">
                <div className="flex items-start gap-3">
                  <Checkbox
                    id="age-confirm"
                    checked={ageConfirmed}
                    onCheckedChange={setAgeConfirmed}
                    className="mt-0.5 border-slate-500 data-[state=checked]:bg-turquoise data-[state=checked]:border-turquoise"
                    data-testid="guest-age-checkbox"
                  />
                  <label htmlFor="age-confirm" className="text-sm text-slate-300 cursor-pointer leading-relaxed">
                    I confirm that I am <span className="text-white font-semibold">16 years of age or older</span> and agree to the meeting terms of service.
                  </label>
                </div>
              </div>

              <Button
                onClick={handleAgeDeclaration}
                disabled={loading || !ageConfirmed}
                className="w-full h-11 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-500/90 hover:to-emerald-500/90 text-white font-semibold"
                data-testid="guest-join-btn"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin mr-2" /> : <ArrowRight className="w-5 h-5 mr-2" />}
                {loading ? 'Joining...' : 'Join Meeting'}
              </Button>

              <button
                onClick={() => setStep(STEPS.OTP)}
                className="w-full text-xs text-slate-400 hover:text-white flex items-center justify-center gap-1 transition-colors"
                data-testid="guest-back-to-otp"
              >
                <ChevronLeft className="w-3 h-3" /> Back
              </button>
            </div>
          )}

          {/* Security badges */}
          <div className="mt-5 grid grid-cols-3 gap-2">
            {[
              { icon: Shield, label: 'Encrypted', color: 'text-green-400' },
              { icon: Sparkles, label: 'AI-Powered', color: 'text-turquoise' },
              { icon: Lock, label: 'Verified', color: 'text-violet-400' },
            ].map((item, i) => (
              <div key={i} className="flex flex-col items-center gap-1 p-2 rounded-lg bg-slate-900/40">
                <item.icon className={`w-4 h-4 ${item.color}`} />
                <span className="text-[10px] text-slate-500">{item.label}</span>
              </div>
            ))}
          </div>

          {/* Sign in link */}
          <div className="mt-3 text-center">
            <button
              onClick={() => navigate('/karau-meet')}
              className="text-xs text-slate-500 hover:text-turquoise transition-colors"
              data-testid="guest-signin-link"
            >
              Have an account? Sign in instead
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default GuestJoinPage;
