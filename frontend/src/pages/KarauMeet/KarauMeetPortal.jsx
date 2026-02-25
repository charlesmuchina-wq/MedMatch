/**
 * AI KARAU Meeting Portal - Main Entry Point
 * 
 * This file has been refactored for better maintainability.
 * Components are now split into separate files:
 * - KarauMeetLogin.jsx - Login page
 * - KarauMeetDashboard.jsx - Main dashboard
 * - KarauRecordingsPage.jsx - Recordings management
 * - KarauSettingsPage.jsx - Settings with accessibility/security/compliance
 */

import { useState, useEffect } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { toast, Toaster } from 'sonner';
import {
  Video, LogOut, Settings, FileText, BarChart3,
  Menu, ChevronRight, Home, CalendarDays, Archive
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Loader2 } from 'lucide-react';
import { useTranslation } from '@/utils/i18n';
import GlobalLanguageSelector from '@/components/GlobalLanguageSelector';

// Refactored page components
import KarauMeetLogin from './KarauMeetLogin';
import KarauMeetDashboard from './KarauMeetDashboard';
import KarauRecordingsPage from './KarauRecordingsPage';
import KarauSettingsPage from './KarauSettingsPage';
import GuestJoinPage from './GuestJoinPage';

// Meeting room component
import MeetingRoom from '@/components/KarauMeet/MeetingRoom';

/**
 * Sidebar Navigation for AI KARAU Meeting Portal
 */
const KarauMeetSidebar = ({ user, currentPath, onLogout, isCollapsed, setIsCollapsed }) => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  
  const navItems = [
    { path: '/karau-meet', icon: Home, labelKey: 'karau.dashboard' },
    { path: '/karau-meet/meetings', icon: Video, labelKey: 'karau.myMeetings' },
    { path: '/karau-meet/schedule', icon: CalendarDays, labelKey: 'karau.schedule' },
    { path: '/karau-meet/recordings', icon: Archive, labelKey: 'karau.recordings' },
    { path: '/karau-meet/notes', icon: FileText, labelKey: 'karau.meetingNotes' },
    { path: '/karau-meet/analytics', icon: BarChart3, labelKey: 'karau.analytics' },
    { path: '/karau-meet/settings', icon: Settings, labelKey: 'karau.settings' },
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
          data-testid="sidebar-toggle"
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
              data-testid={`nav-${item.label.toLowerCase().replace(' ', '-')}`}
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
          data-testid="btn-logout"
        >
          <LogOut className="w-4 h-4" />
          {!isCollapsed && <span className="ml-2">Sign Out</span>}
        </Button>
      </div>
    </div>
  );
};

/**
 * Placeholder pages for sections not yet refactored
 */
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

const NotesPage = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold text-white mb-4">Meeting Notes</h1>
    <p className="text-slate-400">AI-generated summaries and transcriptions</p>
  </div>
);

const AnalyticsPage = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold text-white mb-4">Analytics</h1>
    <p className="text-slate-400">Meeting statistics and insights</p>
  </div>
);

/**
 * Main AI KARAU Meeting Portal App
 */
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

  // Check if we're in a meeting room (room routes only - join routes handled separately)
  const isInRoom = location.pathname.includes('/room/');
  const isJoinPage = location.pathname.includes('/join/');
  
  // Extract meeting ID from URL for meeting routes
  const extractMeetingId = () => {
    const pathParts = location.pathname.split('/');
    const joinIndex = pathParts.indexOf('join');
    const roomIndex = pathParts.indexOf('room');
    if (joinIndex !== -1 && pathParts[joinIndex + 1]) {
      return pathParts[joinIndex + 1];
    }
    if (roomIndex !== -1 && pathParts[roomIndex + 1]) {
      return pathParts[roomIndex + 1];
    }
    return null;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-turquoise animate-spin" />
      </div>
    );
  }

  // Guest Join Page - show branded landing page for guests
  if (isJoinPage && !user) {
    const meetingId = extractMeetingId();
    if (!meetingId) {
      return (
        <div className="min-h-screen bg-slate-900 flex items-center justify-center">
          <div className="text-center">
            <p className="text-red-400 text-lg">Invalid meeting URL</p>
            <button onClick={() => navigate('/karau-meet')} className="mt-4 text-turquoise hover:underline">
              Back to Portal
            </button>
          </div>
        </div>
      );
    }
    
    const handleGuestJoin = (guestUser, mId) => {
      // Store guest info and navigate to room
      localStorage.setItem('karau_guest', JSON.stringify(guestUser));
      navigate(`/karau-meet/room/${mId}`);
    };
    
    return <GuestJoinPage onJoin={handleGuestJoin} meetingIdProp={meetingId} />;
  }

  // Logged-in user clicking join link - redirect to room
  if (isJoinPage && user) {
    const meetingId = extractMeetingId();
    if (meetingId) {
      return <MeetingRoom user={user} meetingIdProp={meetingId} />;
    }
  }

  // In meeting room
  if (isInRoom) {
    const meetingId = extractMeetingId();
    
    if (!meetingId) {
      return (
        <div className="min-h-screen bg-slate-900 flex items-center justify-center">
          <div className="text-center">
            <p className="text-red-400 text-lg">Invalid meeting URL</p>
            <button 
              onClick={() => navigate('/karau-meet')}
              className="mt-4 text-turquoise hover:underline"
            >
              Back to Portal
            </button>
          </div>
        </div>
      );
    }
    
    // Check for guest user from localStorage
    const guestData = localStorage.getItem('karau_guest');
    const meetingUser = user || (guestData ? JSON.parse(guestData) : {
      user_id: `guest_${Date.now()}`,
      name: 'Guest',
      email: 'guest@meeting.local',
      is_guest: true
    });
    
    return <MeetingRoom user={meetingUser} meetingIdProp={meetingId} />;
  }

  // For non-meeting routes, require login
  if (!user) {
    return <KarauMeetLogin onLogin={handleLogin} />;
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
          <Route path="recordings" element={<KarauRecordingsPage />} />
          <Route path="notes" element={<NotesPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="settings" element={<KarauSettingsPage />} />
        </Routes>
      </main>
    </div>
  );
};

export default KarauMeetPortal;
