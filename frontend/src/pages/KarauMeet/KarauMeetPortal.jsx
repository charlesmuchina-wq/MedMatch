/**
 * AI KARAU Meeting Portal - Main Entry Point
 */
import { useState, useEffect } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { toast, Toaster } from 'sonner';
import {
  Video, LogOut, Settings, FileText, BookOpen,
  Menu, ChevronRight, Home, CalendarDays, Archive, Radio, Zap, MessageCircle, ArrowLeft
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Loader2 } from 'lucide-react';
import { useTranslation } from '@/utils/i18n';
import GlobalLanguageSelector from '@/components/GlobalLanguageSelector';

import KarauAIAvatar from '@/components/KarauMeet/KarauAIAvatar';

import KarauMeetLogin from './KarauMeetLogin';
import KarauMeetDashboard from './KarauMeetDashboard';
import KarauRecordingsPage from './KarauRecordingsPage';
import KarauSettingsPage from './KarauSettingsPage';
import KarauMeetGuidePage from './KarauMeetGuidePage';
import GuestJoinPage from './GuestJoinPage';
import { WebinarRegistrationPage } from './WebinarPage';
import WebinarManagementPage from './WebinarManagementPage';
import WebinarLiveRoom from './WebinarLiveRoom';
import MeetingReplayPage from './MeetingReplayPage';

import MeetingRoom from '@/components/KarauMeet/MeetingRoom';
import MeetingLobby from '@/components/KarauMeet/MeetingLobby';

const KarauMeetSidebar = ({ user, currentPath, onLogout, isCollapsed, setIsCollapsed }) => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  
  const navItems = [
    { path: '/', icon: ArrowLeft, label: 'Return to Portal', isExternal: true },
    { path: '/karau-meet', icon: Home, label: t('karauMeet.dashboard') },
    { path: '/karau-meet/meetings', icon: Video, label: t('karauMeet.myMeetings') },
    { path: '/karau-meet/schedule', icon: CalendarDays, label: t('karauMeet.scheduleSidebar') },
    { path: '/karau-meet/recordings', icon: Archive, label: t('karauMeet.recordings') },
    { path: '/karau-meet/webinars', icon: Radio, label: t('karauMeet.webinars') },
    { path: '/karau-meet/notes', icon: FileText, label: t('karauMeet.meetingNotes') },
    { path: '/karau-meet/guide', icon: BookOpen, label: t('karauMeet.howToGuide') },
    { path: '/karau-meet/settings', icon: Settings, label: t('karauMeet.settings') },
    { path: '/lumi', icon: MessageCircle, label: 'LUMI Messenger' },
  ];

  return (
    <div className={`h-screen flex flex-col transition-all duration-300 border-r border-white/[0.04] ${
      isCollapsed ? 'w-[72px]' : 'w-[240px]'
    }`} style={{ fontFamily: "'IBM Plex Sans', sans-serif", background: 'linear-gradient(180deg, #13142a 0%, #0f1020 100%)' }}>
      {/* Header */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-white/[0.04] flex-shrink-0">
        {!isCollapsed && (
          <div className="flex items-center gap-2.5">
            <img 
              src="https://customer-assets.emergentagent.com/job_1fba32e3-e5a1-4174-b642-d1cd092309b3/artifacts/a7nojb8x_IMG_8477.jpeg"
              alt="AI KARAU"
              className="w-9 h-9 rounded-xl object-cover ring-1 ring-white/10"
            />
            <div>
              <span className="font-bold text-sm text-white block leading-tight">AI KARAU</span>
              <span className="text-[10px] text-slate-400 leading-tight">Distance Zero</span>
            </div>
          </div>
        )}
        {isCollapsed && (
          <img 
            src="https://customer-assets.emergentagent.com/job_1fba32e3-e5a1-4174-b642-d1cd092309b3/artifacts/a7nojb8x_IMG_8477.jpeg"
            alt="AI KARAU"
            className="w-9 h-9 rounded-xl object-cover ring-1 ring-white/10 mx-auto"
          />
        )}
        <Button variant="ghost" size="sm" onClick={() => setIsCollapsed(!isCollapsed)}
          className="text-slate-600 hover:text-white hover:bg-white/[0.06] rounded-lg h-8 w-8 p-0" data-testid="sidebar-toggle">
          {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
        </Button>
      </div>
      
      {/* Navigation */}
      <ScrollArea className="flex-1 py-3">
        <nav className="space-y-0.5 px-3">
          {navItems.map((item) => {
            const isActive = currentPath === item.path || 
              (item.path !== '/karau-meet' && currentPath.startsWith(item.path));
            return (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group ${
                  isActive
                    ? 'bg-purple-500/10 text-white'
                    : 'text-slate-500 hover:bg-white/[0.04] hover:text-slate-300'
                }`}
                data-testid={`nav-${item.label}`}
              >
                <div className={`flex items-center justify-center w-8 h-8 rounded-lg transition-all ${
                  isActive ? 'bg-gradient-to-br from-purple-600 to-indigo-600 shadow-lg shadow-purple-500/20' : 'bg-white/[0.04] group-hover:bg-white/[0.06]'
                }`}>
                  <item.icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-500 group-hover:text-slate-300'}`} />
                </div>
                {!isCollapsed && <span className={`text-sm font-medium ${isActive ? 'text-white' : ''}`}>{item.label}</span>}
                {isActive && !isCollapsed && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-purple-400" />}
              </button>
            );
          })}
        </nav>
      </ScrollArea>

      {/* AI Feature indicator */}
      {!isCollapsed && (
        <div className="mx-3 mb-3 px-3 py-2.5 rounded-xl bg-gradient-to-r from-purple-500/[0.06] to-teal-500/[0.06] border border-white/[0.04]">
          <div className="flex items-center gap-2">
            <Zap className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">AI Powered</span>
          </div>
        </div>
      )}
      
      {/* Language Selector */}
      <div className="px-3 py-2 border-t border-white/[0.04]">
        <GlobalLanguageSelector compact={isCollapsed} />
      </div>

      {/* User section */}
      <div className="p-3 border-t border-white/[0.04]">
        {!isCollapsed && (
          <div className="flex items-center gap-3 mb-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-purple-600/30 to-indigo-600/20 border border-purple-500/20 flex items-center justify-center">
              <span className="text-purple-300 font-semibold text-sm">
                {user?.name?.charAt(0) || user?.email?.charAt(0) || '?'}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">{user?.name || 'User'}</p>
              <p className="text-[11px] text-slate-500 truncate">{user?.email}</p>
            </div>
          </div>
        )}
        <Button
          variant="ghost"
          size="sm"
          onClick={onLogout}
          className={`text-slate-500 hover:text-red-400 hover:bg-red-500/10 rounded-xl ${
            isCollapsed ? 'w-full justify-center' : 'w-full justify-start'
          }`}
          data-testid="btn-logout"
        >
          <LogOut className="w-4 h-4" />
          {!isCollapsed && <span className="ml-2">{t("karauMeet.signOut")}</span>}
        </Button>
      </div>
    </div>
  );
};

const MeetingsListPage = () => {
  const { t } = useTranslation();
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-white mb-4">{t("karau.myMeetings")}</h1>
      <p className="text-slate-500">{t("karau.viewAllMeetings")}</p>
    </div>
  );
};

const SchedulePage = () => {
  const { t } = useTranslation();
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-white mb-4">{t("karau.schedule")}</h1>
      <p className="text-slate-500">{t("karau.scheduleDesc")}</p>
    </div>
  );
};

const NotesPage = () => {
  const { t } = useTranslation();
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-white mb-4">{t("karau.meetingNotes")}</h1>
      <p className="text-slate-500">{t("karau.notesDesc")}</p>
    </div>
  );
};

const AnalyticsPage = () => {
  const { t } = useTranslation();
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-white mb-4">{t("karau.analytics")}</h1>
      <p className="text-slate-500">{t("karau.analyticsDesc")}</p>
    </div>
  );
};

const KarauMeetPortal = () => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => window.innerWidth < 768);
  const location = useLocation();
  const navigate = useNavigate();
  const { t } = useTranslation();

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) setSidebarCollapsed(true);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    const savedUser = localStorage.getItem('karau_user');
    const token = localStorage.getItem('token');
    if (savedUser && token) setUser(JSON.parse(savedUser));
    setIsLoading(false);
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
    if (location.pathname.includes('/login')) {
      navigate('/karau-meet', { replace: true });
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('karau_user');
    setUser(null);
    navigate('/karau-meet');
    toast.success(t("karauMeet.signedOut"));
  };

  const isInRoom = location.pathname.includes('/room/');
  const isJoinPage = location.pathname.includes('/join/');
  const isLobbyPage = location.pathname.includes('/lobby/');
  const isEnterprisePage = location.pathname.includes('/enterprise');
  const isWebinarRegisterPage = location.pathname.includes('/webinar/') && location.pathname.includes('/register');
  const isWebinarLiveRoom = location.pathname.includes('/webinar/') && location.pathname.includes('/live');
  const isReplayPage = location.pathname.includes('/replay/');
  
  const extractMeetingId = () => {
    const pathParts = location.pathname.split('/');
    const lobbyIndex = pathParts.indexOf('lobby');
    const joinIndex = pathParts.indexOf('join');
    const roomIndex = pathParts.indexOf('room');
    if (lobbyIndex !== -1 && pathParts[lobbyIndex + 1]) return pathParts[lobbyIndex + 1];
    if (joinIndex !== -1 && pathParts[joinIndex + 1]) return pathParts[joinIndex + 1];
    if (roomIndex !== -1 && pathParts[roomIndex + 1]) return pathParts[roomIndex + 1];
    return null;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0c0d1a] flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-purple-400 animate-spin" />
      </div>
    );
  }

  if (isEnterprisePage && user) {
    const OrganizationAdmin = require('@/components/KarauMeet/OrganizationAdmin').default;
    return (
      <div className="min-h-screen bg-[#0c0d1a]">
        <div className="max-w-7xl mx-auto py-6 px-4">
          <OrganizationAdmin user={user} />
        </div>
      </div>
    );
  }

  if (isJoinPage && !user) {
    const meetingId = extractMeetingId();
    if (!meetingId) {
      return (
        <div className="min-h-screen bg-[#0c0d1a] flex items-center justify-center">
          <div className="text-center">
            <p className="text-red-400 text-lg">{t("karauMeet.invalidMeetingUrl")}</p>
            <button onClick={() => navigate('/karau-meet')} className="mt-4 text-purple-400 hover:underline">{t("karauMeet.backToPortalBtn")}</button>
          </div>
        </div>
      );
    }
    const handleGuestJoin = (guestUser, mId) => {
      localStorage.setItem('karau_guest', JSON.stringify(guestUser));
      navigate(`/karau-meet/lobby/${mId}`);
    };
    return <GuestJoinPage onJoin={handleGuestJoin} meetingIdProp={meetingId} />;
  }

  if (isJoinPage && user) {
    const meetingId = extractMeetingId();
    if (meetingId) {
      navigate(`/karau-meet/lobby/${meetingId}`, { replace: true });
      return null;
    }
  }

  if (isLobbyPage) {
    const meetingId = extractMeetingId();
    if (!meetingId) {
      return (
        <div className="min-h-screen bg-[#0c0d1a] flex items-center justify-center">
          <div className="text-center">
            <p className="text-red-400 text-lg">{t("karauMeet.invalidMeetingUrl")}</p>
            <button onClick={() => navigate('/karau-meet')} className="mt-4 text-purple-400 hover:underline">{t("karauMeet.backToPortalBtn")}</button>
          </div>
        </div>
      );
    }
    const guestData = localStorage.getItem('karau_guest');
    const lobbyUser = user || (guestData ? JSON.parse(guestData) : { user_id: `guest_${Date.now()}`, name: 'Guest', email: 'guest@meeting.local', is_guest: true });
    const isGuest = !user;
    const handleJoinFromLobby = (config) => {
      localStorage.setItem('karau_lobby_config', JSON.stringify(config));
      if (isGuest) {
        localStorage.setItem('karau_guest', JSON.stringify({ ...lobbyUser, user_id: config.userId, name: config.userName }));
      }
      navigate(`/karau-meet/webinar/${meetingId}/live`);
    };
    return <MeetingLobby meetingId={meetingId} user={lobbyUser} isGuest={isGuest} onJoinMeeting={handleJoinFromLobby} />;
  }

  if (isInRoom) {
    const meetingId = extractMeetingId();
    if (!meetingId) {
      return (
        <div className="min-h-screen bg-[#0c0d1a] flex items-center justify-center">
          <div className="text-center">
            <p className="text-red-400 text-lg">{t("karauMeet.invalidMeetingUrl")}</p>
            <button onClick={() => navigate('/karau-meet')} className="mt-4 text-purple-400 hover:underline">{t("karauMeet.backToPortalBtn")}</button>
          </div>
        </div>
      );
    }
    const guestData = localStorage.getItem('karau_guest');
    const meetingUser = user || (guestData ? JSON.parse(guestData) : { user_id: `guest_${Date.now()}`, name: 'Guest', email: 'guest@meeting.local', is_guest: true });
    return <MeetingRoom user={meetingUser} meetingIdProp={meetingId} />;
  }

  if (!user && !isWebinarRegisterPage) {
    return <KarauMeetLogin onLogin={handleLogin} />;
  }
  
  if (isWebinarRegisterPage) {
    return (
      <div className="min-h-screen bg-[#0c0d1a]">
        <Routes>
          <Route path="webinar/:webinarId/register" element={<WebinarRegistrationPage />} />
        </Routes>
      </div>
    );
  }

  if (isReplayPage && user) {
    return (
      <div className="h-screen bg-[#08080d]">
        <Toaster position="top-right" theme="dark" />
        <Routes>
          <Route path="replay/:meetingId" element={<MeetingReplayPage />} />
        </Routes>
      </div>
    );
  }

  if (isWebinarLiveRoom) {
    return (
      <div className="min-h-screen bg-[#0c0d1a]">
        <Toaster position="top-right" theme="dark" />
        <Routes>
          <Route path="webinar/:webinarId/live" element={<WebinarLiveRoom />} />
        </Routes>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0c0d1a] flex">
      <Toaster position="top-right" theme="dark" />
      <KarauMeetSidebar
        user={user}
        currentPath={location.pathname}
        onLogout={handleLogout}
        isCollapsed={sidebarCollapsed}
        setIsCollapsed={setSidebarCollapsed}
      />
      <main className="flex-1 overflow-auto">
        <Routes>
          <Route index element={<KarauMeetDashboard user={user} />} />
          <Route path="dashboard" element={<KarauMeetDashboard user={user} />} />
          <Route path="meetings" element={<MeetingsListPage />} />
          <Route path="schedule" element={<SchedulePage />} />
          <Route path="recordings" element={<KarauRecordingsPage />} />
          <Route path="replay/:meetingId" element={<MeetingReplayPage />} />
          <Route path="webinars" element={<WebinarManagementPage />} />
          <Route path="notes" element={<NotesPage />} />
          <Route path="guide" element={<KarauMeetGuidePage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="settings" element={<KarauSettingsPage />} />
          <Route path="webinar/:webinarId/register" element={<WebinarRegistrationPage />} />
        </Routes>
      </main>
      <KarauAIAvatar />
    </div>
  );
};

export default KarauMeetPortal;
