import { useState, useEffect } from 'react';
import { Routes, Route, useNavigate, useLocation, Link } from 'react-router-dom';
import { toast, Toaster } from 'sonner';
import {
  Video, Plus, Calendar, Users, Clock, Shield, LogOut,
  Sparkles, Copy, ExternalLink, Loader2, History, Moon, Sun,
  Settings, Mic, MonitorPlay, FileText, BarChart3, Bell,
  Menu, X, ChevronRight, Home, CalendarDays, Archive
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { ScrollArea } from '@/components/ui/scroll-area';
import MeetingRoom from '@/components/KarauMeet/MeetingRoom';

const API = process.env.REACT_APP_BACKEND_URL;

// Standalone Login for AI KARAU Meeting
const KarauMeetLogin = ({ onLogin }) => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [meetingId, setMeetingId] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [activeTab, setActiveTab] = useState('signin'); // 'signin' or 'join'

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
    // Navigate to the meeting room (guest access)
    navigate(`/karau-meet/join/${meetingId.toUpperCase()}`);
  };

  const handleGoogleSignIn = async () => {
    // Redirect to Google OAuth
    window.location.href = `${API}/api/auth/google`;
  };

  const handleAppleSignIn = async () => {
    toast.info('Apple Sign-In coming soon!');
    // Apple Sign-In would require Apple Developer account setup
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
          {/* AI KARAU Logo */}
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
                activeTab === 'signin'
                  ? 'bg-turquoise text-white'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => setActiveTab('join')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all ${
                activeTab === 'join'
                  ? 'bg-turquoise text-white'
                  : 'text-slate-400 hover:text-white'
              }`}
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
                    placeholder="your@email.com"
                    className="bg-slate-900/50 border-slate-600 text-white mt-1"
                    required
                  />
                </div>
                
                <div>
                  <Label className="text-slate-300">Password</Label>
                  <div className="relative">
                    <Input
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••"
                      className="bg-slate-900/50 border-slate-600 text-white mt-1 pr-10"
                      required
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
                  className="w-full h-11 bg-gradient-to-r from-turquoise to-cyan-500 hover:from-turquoise/90 hover:to-cyan-500/90 text-white font-semibold"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <>
                      <Video className="w-5 h-5 mr-2" />
                      Sign In to AI KARAU
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
                {/* Google Sign-In */}
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleGoogleSignIn}
                  className="h-11 bg-white hover:bg-gray-100 text-gray-800 border-gray-300"
                >
                  <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                  Google
                </Button>

                {/* Apple Sign-In */}
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleAppleSignIn}
                  className="h-11 bg-black hover:bg-gray-900 text-white border-gray-700"
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
                  placeholder="Enter meeting ID (e.g., ABC-123-XYZ)"
                  className="bg-slate-900/50 border-slate-600 text-white mt-1 text-center uppercase tracking-widest"
                />
              </div>
              
              <Button 
                type="submit"
                className="w-full h-11 bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-500/90 hover:to-purple-600/90 text-white font-semibold"
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
              ← Back to MedMatch-AI KARAU
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Sidebar Navigation for AI KARAU Meeting Portal
const KarauMeetSidebar = ({ user, currentPath, onLogout, isCollapsed, setIsCollapsed }) => {
  const navigate = useNavigate();
  
  const navItems = [
    { path: '/karau-meet', icon: Home, label: 'Dashboard' },
    { path: '/karau-meet/meetings', icon: Video, label: 'My Meetings' },
    { path: '/karau-meet/schedule', icon: CalendarDays, label: 'Schedule' },
    { path: '/karau-meet/recordings', icon: Archive, label: 'Recordings' },
    { path: '/karau-meet/notes', icon: FileText, label: 'Meeting Notes' },
    { path: '/karau-meet/analytics', icon: BarChart3, label: 'Analytics' },
    { path: '/karau-meet/settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <div className={`h-screen bg-slate-900 border-r border-slate-700 flex flex-col transition-all duration-300 ${
      isCollapsed ? 'w-16' : 'w-64'
    }`}>
      {/* Header */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-slate-700">
        {!isCollapsed && (
          <div className="flex items-center gap-2">
            <img 
              src="https://customer-assets.emergentagent.com/job_1fba32e3-e5a1-4174-b642-d1cd092309b3/artifacts/a7nojb8x_IMG_8477.jpeg"
              alt="AI KARAU"
              className="w-8 h-8 rounded-lg object-cover"
            />
            <span className="font-semibold bg-gradient-to-r from-teal-400 to-amber-400 bg-clip-text text-transparent">AI KARAU</span>
          </div>
        )}
        {isCollapsed && (
          <img 
            src="https://customer-assets.emergentagent.com/job_1fba32e3-e5a1-4174-b642-d1cd092309b3/artifacts/a7nojb8x_IMG_8477.jpeg"
            alt="AI KARAU"
            className="w-8 h-8 rounded-lg object-cover mx-auto"
          />
        )}
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="text-slate-400 hover:text-white"
        >
          {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
        </Button>
      </div>
      
      {/* Navigation */}
      <ScrollArea className="flex-1 py-4">
        <nav className="space-y-1 px-2">
          {navItems.map((item) => (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${
                currentPath === item.path
                  ? 'bg-turquoise/20 text-turquoise'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              {!isCollapsed && <span className="text-sm">{item.label}</span>}
            </button>
          ))}
        </nav>
      </ScrollArea>
      
      {/* User section */}
      <div className="p-4 border-t border-slate-700">
        {!isCollapsed && (
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-full bg-turquoise/20 flex items-center justify-center">
              <span className="text-turquoise font-medium">
                {user?.name?.charAt(0) || user?.email?.charAt(0) || '?'}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">{user?.name || 'User'}</p>
              <p className="text-xs text-slate-400 truncate">{user?.email}</p>
            </div>
          </div>
        )}
        <Button
          variant="ghost"
          size="sm"
          onClick={onLogout}
          className={`text-slate-400 hover:text-red-400 hover:bg-red-500/10 ${
            isCollapsed ? 'w-full justify-center' : 'w-full justify-start'
          }`}
        >
          <LogOut className="w-4 h-4" />
          {!isCollapsed && <span className="ml-2">Sign Out</span>}
        </Button>
      </div>
    </div>
  );
};

// Main Dashboard for AI KARAU Meeting
const KarauMeetDashboard = ({ user }) => {
  const navigate = useNavigate();
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [joinMeetingId, setJoinMeetingId] = useState('');
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newMeetingTitle, setNewMeetingTitle] = useState('');
  const [creating, setCreating] = useState(false);
  const [stats, setStats] = useState({
    total_meetings: 0,
    total_hours: 0,
    recordings: 0,
    participants: 0
  });

  useEffect(() => {
    fetchMeetings();
    // Mock stats - in production, fetch from API
    setStats({
      total_meetings: 24,
      total_hours: 48,
      recordings: 12,
      participants: 156
    });
  }, []);

  const fetchMeetings = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/karau-meet/meetings`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setMeetings(data.meetings || []);
      }
    } catch (error) {
      console.error('Error fetching meetings:', error);
    }
    setLoading(false);
  };

  const createMeeting = async () => {
    setCreating(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/karau-meet/meetings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ title: newMeetingTitle || 'AI KARAU Meeting' })
      });
      
      if (response.ok) {
        const data = await response.json();
        toast.success('Meeting created!');
        navigate(`/karau-meet/room/${data.meeting_id}`);
      } else {
        toast.error('Failed to create meeting');
      }
    } catch (error) {
      toast.error('Failed to create meeting');
    }
    setCreating(false);
    setShowCreateDialog(false);
  };

  const joinMeeting = () => {
    if (!joinMeetingId.trim()) {
      toast.error('Please enter a meeting ID');
      return;
    }
    navigate(`/karau-meet/room/${joinMeetingId.toUpperCase()}`);
  };

  const copyMeetingLink = (meetingId) => {
    const link = `${window.location.origin}/karau-meet/join/${meetingId}`;
    navigator.clipboard.writeText(link);
    toast.success('Meeting link copied!');
  };

  return (
    <div className="p-6 space-y-6">
      {/* Welcome Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">
            Welcome back, {user?.name?.split(' ')[0] || 'User'}!
          </h1>
          <p className="text-slate-400">Ready for your next meeting?</p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            onClick={() => setShowCreateDialog(true)}
            className="bg-gradient-to-r from-turquoise to-cyan-500 hover:from-turquoise/90 hover:to-cyan-500/90"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Meeting
          </Button>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid md:grid-cols-2 gap-4">
        {/* Start Instant Meeting */}
        <Card className="bg-slate-800/50 border-slate-700 hover:border-turquoise/50 transition-all cursor-pointer group"
              onClick={() => setShowCreateDialog(true)}>
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-turquoise to-cyan-400 flex items-center justify-center group-hover:scale-105 transition-transform">
                <Video className="w-7 h-7 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white mb-1">Start Instant Meeting</h3>
                <p className="text-slate-400 text-sm">Create a new meeting right now</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Join Meeting */}
        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <div className="w-14 h-14 rounded-xl bg-violet-500/20 flex items-center justify-center">
                <Users className="w-7 h-7 text-violet-400" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-white mb-2">Join Meeting</h3>
                <div className="flex gap-2">
                  <Input
                    placeholder="Enter meeting ID"
                    value={joinMeetingId}
                    onChange={(e) => setJoinMeetingId(e.target.value.toUpperCase())}
                    className="bg-slate-900 border-slate-600 text-white"
                    onKeyPress={(e) => e.key === 'Enter' && joinMeeting()}
                  />
                  <Button onClick={joinMeeting} className="bg-violet-500 hover:bg-violet-600">
                    Join
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Meetings', value: stats.total_meetings, icon: Video, color: 'text-turquoise' },
          { label: 'Hours in Meetings', value: stats.total_hours, icon: Clock, color: 'text-blue-400' },
          { label: 'Recordings', value: stats.recordings, icon: Archive, color: 'text-violet-400' },
          { label: 'Participants Met', value: stats.participants, icon: Users, color: 'text-green-400' },
        ].map((stat, idx) => (
          <Card key={idx} className="bg-slate-800/30 border-slate-700">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-2xl font-bold text-white">{stat.value}</p>
                  <p className="text-xs text-slate-400">{stat.label}</p>
                </div>
                <stat.icon className={`w-8 h-8 ${stat.color} opacity-50`} />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Features */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { icon: Shield, label: 'End-to-End Encrypted', color: 'text-green-400' },
          { icon: Sparkles, label: 'AI Notes & Transcription', color: 'text-turquoise' },
          { icon: MonitorPlay, label: 'Screen Sharing', color: 'text-blue-400' },
          { icon: Users, label: 'Breakout Rooms', color: 'text-violet-400' }
        ].map((feature, idx) => (
          <div key={idx} className="flex items-center gap-2 p-3 bg-slate-800/30 rounded-lg border border-slate-700/50">
            <feature.icon className={`w-4 h-4 ${feature.color}`} />
            <span className="text-xs text-slate-300">{feature.label}</span>
          </div>
        ))}
      </div>

      {/* Recent Meetings */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <History className="w-5 h-5 text-slate-400" />
            Recent Meetings
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-6 h-6 text-turquoise animate-spin" />
            </div>
          ) : meetings.length === 0 ? (
            <div className="text-center py-8">
              <Video className="w-12 h-12 text-slate-600 mx-auto mb-3" />
              <p className="text-slate-400">No meetings yet</p>
              <p className="text-slate-500 text-sm">Start your first meeting!</p>
            </div>
          ) : (
            <div className="space-y-3">
              {meetings.slice(0, 5).map((meeting) => (
                <div
                  key={meeting.meeting_id}
                  className="flex items-center justify-between p-4 bg-slate-900/50 rounded-lg hover:bg-slate-900 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-turquoise/20 flex items-center justify-center">
                      <Video className="w-5 h-5 text-turquoise" />
                    </div>
                    <div>
                      <h4 className="font-medium text-white">{meeting.title}</h4>
                      <div className="flex items-center gap-2 text-sm text-slate-400">
                        <Clock className="w-3 h-3" />
                        {new Date(meeting.created_at).toLocaleDateString()}
                        <Badge variant="outline" className={
                          meeting.status === 'active' ? 'text-green-400 border-green-400/30' :
                          meeting.status === 'ended' ? 'text-slate-400 border-slate-400/30' :
                          'text-yellow-400 border-yellow-400/30'
                        }>
                          {meeting.status}
                        </Badge>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => copyMeetingLink(meeting.meeting_id)}
                      className="text-slate-400 hover:text-white"
                    >
                      <Copy className="w-4 h-4" />
                    </Button>
                    {meeting.status !== 'ended' && (
                      <Button
                        size="sm"
                        onClick={() => navigate(`/karau-meet/room/${meeting.meeting_id}`)}
                        className="bg-turquoise hover:bg-turquoise/80"
                      >
                        {meeting.status === 'active' ? 'Rejoin' : 'Start'}
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Create Meeting Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="bg-slate-800 border-slate-700">
          <DialogHeader>
            <DialogTitle className="text-white">Create New Meeting</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label className="text-slate-300">Meeting Title</Label>
              <Input
                placeholder="AI KARAU Meeting"
                value={newMeetingTitle}
                onChange={(e) => setNewMeetingTitle(e.target.value)}
                className="bg-slate-900 border-slate-600 text-white mt-2"
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <Label className="text-slate-300">Enable AI Notes</Label>
                <p className="text-xs text-slate-500">Auto-transcription and summaries</p>
              </div>
              <Switch defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <Label className="text-slate-300">Enable Recording</Label>
                <p className="text-xs text-slate-500">Record the meeting (requires consent)</p>
              </div>
              <Switch defaultChecked />
            </div>
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setShowCreateDialog(false)} className="text-slate-300">
              Cancel
            </Button>
            <Button onClick={createMeeting} disabled={creating} className="bg-turquoise hover:bg-turquoise/80">
              {creating ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
              Start Meeting
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// Placeholder pages for other sections
const MeetingsListPage = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold text-white mb-4">My Meetings</h1>
    <p className="text-slate-400">View all your past and upcoming meetings</p>
  </div>
);

const SchedulePage = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold text-white mb-4">Schedule</h1>
    <p className="text-slate-400">Schedule and manage your meetings</p>
  </div>
);

// Recordings Page with actual recording history
const RecordingsPage = () => {
  const [recordings, setRecordings] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRecordings();
  }, []);

  const fetchRecordings = async () => {
    const token = localStorage.getItem('token');
    try {
      const [recordingsRes, statsRes] = await Promise.all([
        fetch(`${API}/api/karau-meet/recordings/`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${API}/api/karau-meet/recordings/stats`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);

      if (recordingsRes.ok) {
        const data = await recordingsRes.json();
        setRecordings(data.recordings || []);
      }
      if (statsRes.ok) {
        setStats(await statsRes.json());
      }
    } catch (error) {
      console.error('Error fetching recordings:', error);
    }
    setLoading(false);
  };

  const formatDuration = (seconds) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    if (hrs > 0) return `${hrs}h ${mins}m`;
    if (mins > 0) return `${mins}m ${secs}s`;
    return `${secs}s`;
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
  };

  const deleteRecording = async (recordingId) => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau-meet/recordings/${recordingId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        setRecordings(prev => prev.filter(r => r.recording_id !== recordingId));
        toast.success('Recording deleted');
      }
    } catch (error) {
      toast.error('Failed to delete recording');
    }
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <Loader2 className="w-6 h-6 text-turquoise animate-spin" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Recordings</h1>
        <p className="text-slate-400">Access your meeting recordings</p>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-3 gap-4">
          <Card className="bg-slate-800/50 border-slate-700 p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-violet-500/20 flex items-center justify-center">
                <Video className="w-5 h-5 text-violet-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{stats.total_recordings}</p>
                <p className="text-xs text-slate-400">Total Recordings</p>
              </div>
            </div>
          </Card>
          <Card className="bg-slate-800/50 border-slate-700 p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-turquoise/20 flex items-center justify-center">
                <Clock className="w-5 h-5 text-turquoise" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{formatDuration(stats.total_duration_seconds)}</p>
                <p className="text-xs text-slate-400">Total Duration</p>
              </div>
            </div>
          </Card>
          <Card className="bg-slate-800/50 border-slate-700 p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center">
                <Archive className="w-5 h-5 text-amber-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{formatFileSize(stats.total_size_bytes)}</p>
                <p className="text-xs text-slate-400">Storage Used</p>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Recordings List */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">Your Recordings</CardTitle>
          <CardDescription className="text-slate-400">
            Recordings are saved to your local device
          </CardDescription>
        </CardHeader>
        <CardContent>
          {recordings.length === 0 ? (
            <div className="text-center py-8">
              <Video className="w-12 h-12 text-slate-600 mx-auto mb-3" />
              <p className="text-slate-400">No recordings yet</p>
              <p className="text-sm text-slate-500">Start recording in a meeting to see them here</p>
            </div>
          ) : (
            <div className="space-y-3">
              {recordings.map((rec) => (
                <div key={rec.recording_id} className="flex items-center justify-between p-4 bg-slate-900/50 rounded-lg">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-lg bg-violet-500/20 flex items-center justify-center">
                      <Video className="w-6 h-6 text-violet-400" />
                    </div>
                    <div>
                      <p className="font-medium text-white">{rec.meeting_title}</p>
                      <div className="flex items-center gap-3 text-xs text-slate-400">
                        <span>{new Date(rec.recorded_at).toLocaleDateString()}</span>
                        <span>•</span>
                        <span>{formatDuration(rec.duration_seconds)}</span>
                        <span>•</span>
                        <span>{formatFileSize(rec.file_size_bytes)}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-slate-400 border-slate-600">
                      Local
                    </Badge>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => deleteRecording(rec.recording_id)}
                      className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// Notes Page with AI summaries and transcripts
const NotesPage = () => {
  const [summaries, setSummaries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSummary, setSelectedSummary] = useState(null);

  useEffect(() => {
    fetchNotes();
  }, []);

  const fetchNotes = async () => {
    const token = localStorage.getItem('token');
    try {
      // Get user's meetings first, then fetch summaries
      const meetingsRes = await fetch(`${API}/api/karau-meet/meetings`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (meetingsRes.ok) {
        const meetingsData = await meetingsRes.json();
        const meetings = meetingsData.meetings || [];
        
        // Fetch summaries for each meeting
        const summaryPromises = meetings.slice(0, 20).map(async (meeting) => {
          try {
            const res = await fetch(`${API}/api/karau-meet/ai/summary/${meeting.meeting_id}`, {
              headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
              const summary = await res.json();
              return { ...summary, meeting };
            }
          } catch (e) {}
          return null;
        });
        
        const results = await Promise.all(summaryPromises);
        setSummaries(results.filter(s => s !== null));
      }
    } catch (error) {
      console.error('Error fetching notes:', error);
    }
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <Loader2 className="w-6 h-6 text-turquoise animate-spin" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Meeting Notes</h1>
        <p className="text-slate-400">AI-generated summaries and transcriptions</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Notes List */}
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white">Recent Summaries</CardTitle>
          </CardHeader>
          <CardContent>
            {summaries.length === 0 ? (
              <div className="text-center py-8">
                <FileText className="w-12 h-12 text-slate-600 mx-auto mb-3" />
                <p className="text-slate-400">No summaries yet</p>
                <p className="text-sm text-slate-500">AI summaries will appear after meetings end</p>
              </div>
            ) : (
              <div className="space-y-2">
                {summaries.map((item, idx) => (
                  <button
                    key={idx}
                    onClick={() => setSelectedSummary(item)}
                    className={`w-full text-left p-3 rounded-lg transition-colors ${
                      selectedSummary === item
                        ? 'bg-turquoise/20 border border-turquoise/50'
                        : 'bg-slate-900/50 hover:bg-slate-900'
                    }`}
                  >
                    <p className="font-medium text-white">{item.meeting_title || 'Meeting'}</p>
                    <p className="text-xs text-slate-400">
                      {item.generated_at ? new Date(item.generated_at).toLocaleDateString() : 'Unknown date'}
                    </p>
                  </button>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Summary Detail */}
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white">
              {selectedSummary ? selectedSummary.meeting_title : 'Select a Summary'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {selectedSummary ? (
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium text-turquoise mb-2">Summary</h4>
                  <p className="text-slate-300 text-sm">{selectedSummary.summary}</p>
                </div>
                
                {selectedSummary.key_points?.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-turquoise mb-2">Key Points</h4>
                    <ul className="list-disc list-inside text-slate-300 text-sm space-y-1">
                      {selectedSummary.key_points.map((point, i) => (
                        <li key={i}>{point}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {selectedSummary.action_items?.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-amber-400 mb-2">Action Items</h4>
                    <div className="space-y-2">
                      {selectedSummary.action_items.map((item, i) => (
                        <div key={i} className="p-2 bg-slate-900/50 rounded text-sm">
                          <p className="text-white">{item.task}</p>
                          <p className="text-xs text-slate-400">
                            Assignee: {item.assignee} • Due: {item.deadline || 'TBD'}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-slate-500">
                Select a summary to view details
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

const AnalyticsPage = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold text-white mb-4">Analytics</h1>
    <p className="text-slate-400">Meeting statistics and insights</p>
  </div>
);

// Full Settings Page with Security & Accessibility
const SettingsPage = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
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
        <h1 className="text-2xl font-bold text-white">Settings</h1>
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
                <div className="flex items-center gap-2 p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
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
                  >
                    {sendingCode ? (
                      <Loader2 className="w-4 h-4 animate-spin mr-2" />
                    ) : null}
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
                      placeholder="Enter 6-digit code"
                      value={verificationCode}
                      onChange={(e) => setVerificationCode(e.target.value)}
                      className="bg-slate-900 border-slate-600 text-white"
                      maxLength={6}
                    />
                    <Button onClick={verifyCode} disabled={verificationCode.length !== 6}>
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
                <Badge className={complianceStatus.gdpr?.compliant ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}>
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
                <Badge className={complianceStatus.hipaa?.compliant ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}>
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

// Main AI KARAU Meeting Portal App
const KarauMeetPortal = () => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    // Check for existing session
    const savedUser = localStorage.getItem('karau_user');
    const token = localStorage.getItem('token');
    
    if (savedUser && token) {
      setUser(JSON.parse(savedUser));
    }
    setIsLoading(false);
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('karau_user');
    setUser(null);
    navigate('/karau-meet');
    toast.success('Signed out successfully');
  };

  // Check if we're in a meeting room
  const isInMeeting = location.pathname.includes('/room/') || location.pathname.includes('/join/');

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-turquoise animate-spin" />
      </div>
    );
  }

  if (!user) {
    return <KarauMeetLogin onLogin={handleLogin} />;
  }

  // Meeting room - full screen without sidebar
  if (isInMeeting) {
    return <MeetingRoom user={user} />;
  }

  return (
    <div className="min-h-screen bg-slate-900 flex">
      <Toaster position="top-right" theme="dark" />
      
      {/* Sidebar */}
      <KarauMeetSidebar
        user={user}
        currentPath={location.pathname}
        onLogout={handleLogout}
        isCollapsed={sidebarCollapsed}
        setIsCollapsed={setSidebarCollapsed}
      />
      
      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <Routes>
          <Route index element={<KarauMeetDashboard user={user} />} />
          <Route path="meetings" element={<MeetingsListPage />} />
          <Route path="schedule" element={<SchedulePage />} />
          <Route path="recordings" element={<RecordingsPage />} />
          <Route path="notes" element={<NotesPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Routes>
      </main>
    </div>
  );
};

export default KarauMeetPortal;
