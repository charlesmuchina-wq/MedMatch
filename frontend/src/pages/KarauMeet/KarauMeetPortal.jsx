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
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

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

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      {/* Background pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0" style={{
          backgroundImage: `radial-gradient(circle at 25% 25%, rgba(20, 184, 166, 0.3) 0%, transparent 50%),
                           radial-gradient(circle at 75% 75%, rgba(139, 92, 246, 0.3) 0%, transparent 50%)`
        }} />
      </div>
      
      <Card className="w-full max-w-md bg-slate-800/80 border-slate-700 backdrop-blur-xl relative z-10">
        <CardHeader className="text-center pb-2">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-turquoise to-cyan-400 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-turquoise/20">
            <Video className="w-10 h-10 text-white" />
          </div>
          <CardTitle className="text-2xl font-bold text-white">
            AI KARAU Meeting
          </CardTitle>
          <CardDescription className="text-slate-400">
            Secure video conferencing with AI-powered features
          </CardDescription>
        </CardHeader>
        
        <CardContent>
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
              className="w-full h-12 bg-gradient-to-r from-turquoise to-cyan-500 hover:from-turquoise/90 hover:to-cyan-500/90 text-white font-semibold"
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
          
          <div className="mt-6 pt-6 border-t border-slate-700">
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
          
          <div className="mt-4 text-center">
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
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-turquoise to-cyan-400 flex items-center justify-center">
              <Video className="w-4 h-4 text-white" />
            </div>
            <span className="font-semibold text-white">AI KARAU</span>
          </div>
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

const RecordingsPage = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold text-white mb-4">Recordings</h1>
    <p className="text-slate-400">Access your meeting recordings</p>
  </div>
);

const NotesPage = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold text-white mb-4">Meeting Notes</h1>
    <p className="text-slate-400">AI-generated notes and transcriptions</p>
  </div>
);

const AnalyticsPage = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold text-white mb-4">Analytics</h1>
    <p className="text-slate-400">Meeting statistics and insights</p>
  </div>
);

const SettingsPage = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold text-white mb-4">Settings</h1>
    <p className="text-slate-400">Customize your AI KARAU experience</p>
  </div>
);

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
