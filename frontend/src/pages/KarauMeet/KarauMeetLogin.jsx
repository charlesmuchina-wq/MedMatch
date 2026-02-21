import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { toast } from 'sonner';
import { Video, Users, Shield, Sparkles, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * Standalone Login for AI KARAU Meeting Portal
 */
const KarauMeetLogin = ({ onLogin }) => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [meetingId, setMeetingId] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [activeTab, setActiveTab] = useState('signin');

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
        toast.success('Welcome to AI KARAU Meeting!');
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Login failed');
      }
    } catch (error) {
      toast.error('Connection error. Please try again.');
    }
    
    setIsLoading(false);
  };

  const handleJoinMeeting = (e) => {
    e.preventDefault();
    if (!meetingId.trim()) {
      toast.error('Please enter a meeting ID');
      return;
    }
    navigate(`/karau-meet/join/${meetingId.toUpperCase()}`);
  };

  const handleGoogleSignIn = async () => {
    window.location.href = `${API}/api/auth/google`;
  };

  const handleAppleSignIn = async () => {
    toast.info('Apple Sign-In coming soon!');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      {/* Background pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0" style={{
          backgroundImage: `radial-gradient(circle at 25% 25%, rgba(20, 184, 166, 0.3) 0%, transparent 50%),
                           radial-gradient(circle at 75% 75%, rgba(212, 175, 55, 0.3) 0%, transparent 50%)`
        }} />
      </div>
      
      <Card className="w-full max-w-md bg-slate-800/80 border-slate-700 backdrop-blur-xl relative z-10">
        <CardHeader className="text-center pb-2">
          <div className="mx-auto mb-4">
            <img 
              src="https://customer-assets.emergentagent.com/job_1fba32e3-e5a1-4174-b642-d1cd092309b3/artifacts/a7nojb8x_IMG_8477.jpeg"
              alt="AI KARAU - The Meeting Place"
              className="w-28 h-28 rounded-2xl object-cover shadow-lg shadow-teal-500/20"
            />
          </div>
          <CardTitle className="text-2xl font-bold bg-gradient-to-r from-teal-400 via-cyan-300 to-amber-400 bg-clip-text text-transparent">
            AI KARAU Meeting
          </CardTitle>
          <CardDescription className="text-slate-400">
            The Meeting Place - Secure & AI-Powered
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-4">
          {/* Tab Switcher */}
          <div className="flex gap-2 p-1 bg-slate-900/50 rounded-lg">
            <button
              onClick={() => setActiveTab('signin')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all ${
                activeTab === 'signin' ? 'bg-turquoise text-white' : 'text-slate-400 hover:text-white'
              }`}
              data-testid="tab-signin"
            >
              Sign In
            </button>
            <button
              onClick={() => setActiveTab('join')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all ${
                activeTab === 'join' ? 'bg-turquoise text-white' : 'text-slate-400 hover:text-white'
              }`}
              data-testid="tab-join"
            >
              Join Meeting
            </button>
          </div>

          {/* Sign In Tab */}
          {activeTab === 'signin' && (
            <>
              <form onSubmit={handleLogin} className="space-y-4">
                <div>
                  <Label className="text-slate-300">Email</Label>
                  <Input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder={t("karauMeet.emailPlaceholder")}
                    className="bg-slate-900/50 border-slate-600 text-white mt-1"
                    required
                    data-testid="input-email"
                  />
                </div>
                
                <div>
                  <Label className="text-slate-300">Password</Label>
                  <div className="relative">
                    <Input
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder={t("auth.passwordPlaceholder")}
                      className="bg-slate-900/50 border-slate-600 text-white mt-1 pr-10"
                      required
                      data-testid="input-password"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
                    >
                      {showPassword ? '👁️' : '👁️‍🗨️'}
                    </button>
                  </div>
                </div>
                
                <Button 
                  type="submit" 
                  onClick={(e) => {
                    if (!isLoading) {
                      handleLogin(e);
                    }
                  }}
                  className="w-full h-12 bg-turquoise hover:bg-turquoise/90 text-white font-semibold text-base"
                  disabled={isLoading}
                  data-testid="btn-signin"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin mr-2" />
                      Signing In...
                    </>
                  ) : (
                    <>
                      <Video className="w-5 h-5 mr-2" />
                      Sign In
                    </>
                  )}
                </Button>
              </form>

              {/* Divider */}
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-slate-700"></div>
                </div>
                <div className="relative flex justify-center text-xs">
                  <span className="px-2 bg-slate-800 text-slate-400">or continue with</span>
                </div>
              </div>

              {/* Social Sign-In Options */}
              <div className="grid grid-cols-2 gap-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleGoogleSignIn}
                  className="h-11 bg-white hover:bg-gray-100 text-gray-800 border-gray-300"
                  data-testid="btn-google"
                >
                  <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                  Google
                </Button>

                <Button
                  type="button"
                  variant="outline"
                  onClick={handleAppleSignIn}
                  className="h-11 bg-black hover:bg-gray-900 text-white border-gray-700"
                  data-testid="btn-apple"
                >
                  <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09l.01-.01zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/>
                  </svg>
                  Apple
                </Button>
              </div>
            </>
          )}

          {/* Join Meeting Tab */}
          {activeTab === 'join' && (
            <form onSubmit={handleJoinMeeting} className="space-y-4">
              <div className="text-center py-4">
                <Users className="w-12 h-12 text-turquoise mx-auto mb-3" />
                <p className="text-slate-300 text-sm">
                  Enter your meeting ID to join as a guest
                </p>
              </div>
              
              <div>
                <Label className="text-slate-300">Meeting ID</Label>
                <Input
                  type="text"
                  value={meetingId}
                  onChange={(e) => setMeetingId(e.target.value.toUpperCase())}
                  placeholder={t("karauMeet.meetingIdPlaceholder")}
                  className="bg-slate-900/50 border-slate-600 text-white mt-1 text-center uppercase tracking-widest"
                  data-testid="input-meeting-id"
                />
              </div>
              
              <Button 
                type="submit"
                className="w-full h-11 bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-500/90 hover:to-purple-600/90 text-white font-semibold"
                data-testid="btn-join-meeting"
              >
                <Users className="w-5 h-5 mr-2" />
                Join Meeting
              </Button>

              <p className="text-xs text-slate-500 text-center">
                You'll join as a guest. Sign in for full features.
              </p>
            </form>
          )}
          
          <div className="pt-4 border-t border-slate-700">
            <div className="flex items-center justify-center gap-4 text-sm text-slate-400">
              <div className="flex items-center gap-1">
                <Shield className="w-4 h-4 text-green-400" />
                E2E Encrypted
              </div>
              <div className="flex items-center gap-1">
                <Sparkles className="w-4 h-4 text-turquoise" />
                AI-Powered
              </div>
            </div>
          </div>
          
          <div className="text-center">
            <Link to="/" className="text-sm text-slate-400 hover:text-turquoise transition-colors">
              ← Back to Portal Selection
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default KarauMeetLogin;
