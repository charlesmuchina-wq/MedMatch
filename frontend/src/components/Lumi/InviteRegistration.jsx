import { useState, useEffect } from 'react';
import { Loader2, UserPlus, CheckCircle, AlertCircle, ArrowRight } from 'lucide-react';
import { toast } from 'sonner';
import { API } from './constants';

const InviteRegistration = ({ inviteToken, onComplete }) => {
  const [invite, setInvite] = useState(null);
  const [loading, setLoading] = useState(true);
  const [invalid, setInvalid] = useState(null);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPw, setConfirmPw] = useState('');
  const [registering, setRegistering] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API}/api/lumi/invite/validate/${inviteToken}`);
        if (res.ok) {
          const data = await res.json();
          if (data.valid) {
            setInvite(data.invite);
            setEmail(data.invite.invited_email || '');
          } else {
            setInvalid(data.reason === 'already_used' ? 'This invite has already been used.' : 'This invite link has expired.');
          }
        } else {
          setInvalid('Invalid invite link.');
        }
      } catch {
        setInvalid('Could not validate invite.');
      }
      setLoading(false);
    })();
  }, [inviteToken]);

  const handleRegister = async (e) => {
    e.preventDefault();
    if (!name.trim()) { toast.error('Name is required'); return; }
    if (!email.trim() || !email.includes('@')) { toast.error('Valid email is required'); return; }
    if (password.length < 6) { toast.error('Password must be at least 6 characters'); return; }
    if (password !== confirmPw) { toast.error('Passwords do not match'); return; }

    setRegistering(true);
    try {
      const res = await fetch(`${API}/api/lumi/invite/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ invite_token: inviteToken, name: name.trim(), email: email.trim().toLowerCase(), password })
      });
      if (res.ok) {
        const data = await res.json();
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('karau_user', JSON.stringify(data.user));
        toast.success('Welcome to ENZI!');
        onComplete(data.user);
      } else {
        const err = await res.json();
        toast.error(err.detail || 'Registration failed');
      }
    } catch {
      toast.error('Registration failed');
    }
    setRegistering(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0D1117] flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-[#00CEC9] animate-spin" />
      </div>
    );
  }

  if (invalid) {
    return (
      <div className="min-h-screen bg-[#0D1117] flex items-center justify-center px-4">
        <div className="max-w-sm w-full text-center space-y-4">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto" />
          <h2 className="text-lg font-semibold text-white">{invalid}</h2>
          <p className="text-sm text-slate-400">Please ask your contact for a new invitation link.</p>
          <button onClick={() => window.location.href = '/lumi'}
            className="px-6 py-2.5 rounded-xl text-white text-sm font-medium"
            style={{ background: 'linear-gradient(135deg, #00CEC9, #6C5CE7)' }}
            data-testid="invite-go-login">
            Go to Sign In
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0D1117] flex items-center justify-center px-4" data-testid="invite-registration">
      <div className="max-w-md w-full">
        {/* Branding */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 mx-auto mb-4">
            <img src="/enzi-logo-icon.png" alt="ENZI" className="w-full h-full object-contain" />
          </div>
          <h1 className="text-3xl font-black tracking-[0.15em]"
            style={{ background: 'linear-gradient(135deg, #00CEC9, #6C5CE7, #E84393)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            ENZI
          </h1>
        </div>

        {/* Invite card */}
        <div className="bg-[#131920] border border-white/10 rounded-2xl p-6 mb-4" style={{ animation: 'fadeInUp 0.4s ease-out' }}>
          <div className="flex items-center gap-3 mb-5 pb-4 border-b border-white/10">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #00CEC9, #6C5CE7)' }}>
              <CheckCircle className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-sm text-white font-medium"><strong>{invite?.invited_by_name}</strong> invited you</p>
              {invite?.message && <p className="text-xs text-slate-400 mt-0.5 italic">"{invite.message}"</p>}
            </div>
          </div>

          <h2 className="text-sm font-semibold text-white mb-4">Create your ENZI account</h2>

          <form onSubmit={handleRegister} className="space-y-3">
            <input value={name} onChange={e => setName(e.target.value)} placeholder="Full name"
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-slate-600 outline-none focus:border-[#00CEC9]/50 transition-colors"
              data-testid="invite-reg-name" />
            <input value={email} onChange={e => setEmail(e.target.value)} placeholder="Email address" type="email"
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-slate-600 outline-none focus:border-[#00CEC9]/50 transition-colors"
              data-testid="invite-reg-email" />
            <input value={password} onChange={e => setPassword(e.target.value)} placeholder="Password (6+ characters)" type="password"
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-slate-600 outline-none focus:border-[#00CEC9]/50 transition-colors"
              data-testid="invite-reg-password" />
            <input value={confirmPw} onChange={e => setConfirmPw(e.target.value)} placeholder="Confirm password" type="password"
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-slate-600 outline-none focus:border-[#00CEC9]/50 transition-colors"
              data-testid="invite-reg-confirm" />
            <button type="submit" disabled={registering}
              className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-white text-sm font-semibold transition-all hover:opacity-90 disabled:opacity-50"
              style={{ background: 'linear-gradient(135deg, #00CEC9, #6C5CE7)' }}
              data-testid="invite-reg-submit">
              {registering ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowRight className="w-4 h-4" />}
              {registering ? 'Creating account...' : 'Join ENZI'}
            </button>
          </form>
        </div>

        <p className="text-[10px] text-slate-600 text-center">
          Already have an account? <button onClick={() => window.location.href = '/lumi'} className="text-[#00CEC9] hover:underline">Sign in</button>
        </p>
      </div>

      <style>{`
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(16px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
};

export default InviteRegistration;
