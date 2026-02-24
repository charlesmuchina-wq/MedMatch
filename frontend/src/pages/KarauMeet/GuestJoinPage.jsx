import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { Video, User, ArrowRight, Loader2, Shield, Sparkles, Lock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { useTranslation } from '@/utils/i18n';

const API = process.env.REACT_APP_BACKEND_URL;

const GuestJoinPage = ({ onJoin, meetingIdProp }) => {
  const params = useParams();
  const meetingId = meetingIdProp || params.meetingId;
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [guestName, setGuestName] = useState('');
  const [joining, setJoining] = useState(false);
  const [meetingInfo, setMeetingInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (meetingId) checkMeeting();
  }, [meetingId]);

  const checkMeeting = async () => {
    try {
      const res = await fetch(`${API}/api/karau-meet/meetings/${meetingId}/info`);
      if (res.ok) {
        const data = await res.json();
        setMeetingInfo(data);
      } else {
        setError('notFound');
      }
    } catch {
      // Meeting may still be joinable even if info endpoint fails
      setMeetingInfo({ title: 'AI KARAU Meeting', meeting_id: meetingId });
    }
    setLoading(false);
  };

  const handleJoin = async () => {
    if (!guestName.trim()) {
      toast.error(t('guest.enterName'));
      return;
    }
    setJoining(true);

    try {
      const res = await fetch(`${API}/api/karau-meet/meetings/${meetingId}/join-guest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ guest_name: guestName.trim() })
      });

      if (res.ok) {
        const data = await res.json();
        // Create guest user object and pass to meeting
        const guestUser = {
          user_id: data.guest_user_id,
          name: data.guest_name || guestName,
          email: `${data.guest_user_id}@guest.karau`,
          is_guest: true
        };
        if (onJoin) {
          onJoin(guestUser, meetingId);
        } else {
          // Store guest info and navigate to room
          localStorage.setItem('karau_guest', JSON.stringify(guestUser));
          navigate(`/karau-meet/room/${meetingId}`);
        }
      } else {
        const err = await res.json().catch(() => ({}));
        toast.error(err.detail || t('guest.joinFailed'));
        setJoining(false);
      }
    } catch {
      toast.error(t('guest.joinFailed'));
      setJoining(false);
    }
  };

  if (loading) {
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
            <h2 className="text-xl font-bold text-white mb-2">{t('guest.meetingNotFound')}</h2>
            <p className="text-slate-400 text-sm mb-6">{t('guest.meetingNotFoundDesc')}</p>
            <Button
              onClick={() => navigate('/karau-meet')}
              variant="outline"
              className="border-slate-600 text-slate-300"
              data-testid="guest-back-btn"
            >
              {t('guest.backToPortal')}
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-turquoise/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-violet-500/5 rounded-full blur-3xl" />
      </div>

      <Card className="bg-slate-800/80 backdrop-blur-xl border-slate-700 max-w-md w-full relative z-10" data-testid="guest-join-card">
        <CardContent className="p-8">
          {/* Logo */}
          <div className="flex items-center justify-center gap-3 mb-6">
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
          <div className="text-center mb-6">
            <h1 className="text-2xl font-bold text-white mb-1" data-testid="guest-meeting-title">
              {meetingInfo?.title || 'AI KARAU Meeting'}
            </h1>
            <p className="text-sm text-slate-400">
              {t('guest.meetingId')}: <span className="font-mono text-turquoise font-semibold">{meetingId}</span>
            </p>
          </div>

          {/* Guest Name Input */}
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-slate-300 mb-2 block">
                {t('guest.yourName')}
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <Input
                  placeholder={t('guest.namePlaceholder')}
                  value={guestName}
                  onChange={(e) => setGuestName(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleJoin()}
                  className="bg-slate-900 border-slate-600 text-white pl-10 h-12"
                  autoFocus
                  data-testid="guest-name-input"
                />
              </div>
            </div>

            <Button
              onClick={handleJoin}
              disabled={joining || !guestName.trim()}
              className="w-full h-12 bg-gradient-to-r from-turquoise to-cyan-500 hover:from-turquoise/90 hover:to-cyan-500/90 text-white font-semibold text-base"
              data-testid="guest-join-btn"
            >
              {joining ? (
                <Loader2 className="w-5 h-5 animate-spin mr-2" />
              ) : (
                <ArrowRight className="w-5 h-5 mr-2" />
              )}
              {joining ? t('guest.joining') : t('guest.joinMeeting')}
            </Button>
          </div>

          {/* Security Features */}
          <div className="mt-6 grid grid-cols-3 gap-2">
            {[
              { icon: Shield, label: t('guest.encrypted'), color: 'text-green-400' },
              { icon: Sparkles, label: t('guest.aiPowered'), color: 'text-turquoise' },
              { icon: Lock, label: t('guest.secure'), color: 'text-violet-400' },
            ].map((item, i) => (
              <div key={i} className="flex flex-col items-center gap-1 p-2 rounded-lg bg-slate-900/40">
                <item.icon className={`w-4 h-4 ${item.color}`} />
                <span className="text-[10px] text-slate-500">{item.label}</span>
              </div>
            ))}
          </div>

          {/* Sign in link */}
          <div className="mt-4 text-center">
            <button
              onClick={() => navigate('/karau-meet')}
              className="text-xs text-slate-500 hover:text-turquoise transition-colors"
              data-testid="guest-signin-link"
            >
              {t('guest.haveAccount')}
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default GuestJoinPage;
