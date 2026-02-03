import { useState, useEffect, createContext, useContext } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, NavLink, useLocation, Navigate, useSearchParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { Toaster, toast } from "sonner";
import { 
  Search, Briefcase, FileText, Bookmark, CheckSquare, 
  Menu, X, TrendingUp, Bell, PenTool, Target, Mic, Moon, Sun, Volume2, BarChart3, Users, Video, LogOut, Crown, DollarSign, MessageSquare, UserSearch, LayoutDashboard, Award, ShieldCheck, CalendarDays, Bot, Shield
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";

// Import Page Components
import Dashboard from "@/pages/Dashboard";
import ResumePage from "@/pages/ResumePage";
import JobSearchPage from "@/pages/JobSearchPage";
import SavedJobsPage from "@/pages/SavedJobsPage";
import ApplicationsPage from "@/pages/ApplicationsPage";
import JobAlertsPage from "@/pages/JobAlertsPage";
import CoverLetterPage from "@/pages/CoverLetterPage";
import SuccessPredictorPage from "@/pages/SuccessPredictorPage";
import InterviewPrepPage from "@/pages/InterviewPrepPage";
import VoiceCoachPage from "@/pages/VoiceCoachPage";
import AnalyticsDashboard from "@/pages/AnalyticsDashboard";
import ResumeProfilesPage from "@/pages/ResumeProfilesPage";
import VideoInterviewPage from "@/pages/VideoInterviewPage";
import LoginPage from "@/pages/LoginPage";
import MembershipPage from "@/pages/MembershipPage";
import RecruiterJobsPage from "@/pages/RecruiterJobsPage";
import SalaryInsightsPage from "@/pages/SalaryInsightsPage";
import RecruiterDashboard from "@/pages/RecruiterDashboard";
import ApplicantTracker from "@/pages/ApplicantTracker";
import CandidateSearch from "@/pages/CandidateSearch";
import MessagesPage from "@/pages/MessagesPage";
import CompanyProfilePage from "@/pages/CompanyProfilePage";
import SkillAssessmentsPage from "@/pages/SkillAssessmentsPage";
import InterviewSchedulingPage from "@/pages/InterviewSchedulingPage";
import CompaniesPage from "@/pages/CompaniesPage";
import QAPracticePage from "@/pages/QAPracticePage";
import NotificationsPage from "@/pages/NotificationsPage";
import IDVerificationPage from "@/pages/IDVerificationPage";
import RealTimeSTTPage from "@/pages/RealTimeSTTPage";
import MeetingNotesPage from "@/pages/MeetingNotesPage";
import InterviewCalendarPage from "@/pages/InterviewCalendarPage";
import AnalyticsFunnelPage from "@/pages/AnalyticsFunnelPage";
import DragonAutomatorPage from "@/pages/DragonAutomatorPage";
import AdminDashboard from "@/pages/AdminDashboard";
import ProductionMetricsPage from "@/pages/ProductionMetricsPage";
import TranslationAnalyticsPage from "@/pages/TranslationAnalyticsPage";
import PrivacySettingsPage from "@/pages/PrivacySettingsPage";
import PrivacyConsentScreen from "@/components/PrivacyConsentScreen";
import MatchExplanation from "@/components/MatchExplanation";
import BlindScreeningDashboard from "@/pages/BlindScreeningDashboard";
import ContactRequestScreen from "@/pages/ContactRequestScreen";
import RecruiterVerificationPage from "@/pages/RecruiterVerificationPage";
import { UpgradeBanner } from "@/components/PremiumGate";
import PremiumGate from "@/components/PremiumGate";
import OnboardingTour, { useOnboardingTour } from "@/components/OnboardingTour";
import InstallPrompt from "@/components/InstallPrompt";
import PWAInstallPrompt from "@/components/PWAInstallPrompt";
import KarauDragonAI, { DragonButton } from "@/components/KarauDragonAI";
import GlobalLanguageSelector from "@/components/GlobalLanguageSelector";
import { I18nProvider, useTranslation } from "@/utils/i18n";
import { OfflineBanner, OfflineIndicator } from "@/components/OfflineIndicator";
import { offlineStorage } from "@/utils/offlineStorage";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Theme Context
const ThemeContext = createContext();

export const useTheme = () => useContext(ThemeContext);

const ThemeProvider = ({ children }) => {
  const [isDark, setIsDark] = useState(() => {
    const saved = localStorage.getItem('medmatch-theme');
    return saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches);
  });

  useEffect(() => {
    localStorage.setItem('medmatch-theme', isDark ? 'dark' : 'light');
    document.documentElement.classList.toggle('dark', isDark);
  }, [isDark]);

  const toggleTheme = () => setIsDark(!isDark);

  return (
    <ThemeContext.Provider value={{ isDark, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

// Sidebar Component
const Sidebar = ({ isOpen, setIsOpen, user }) => {
  const location = useLocation();
  const { isDark } = useTheme();
  const { t, translationVersion, translationProgress, isLoadingAI, language, isBundled } = useTranslation();
  
  // Lock body scroll when sidebar is open on mobile
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);
  
  // Different navigation for recruiters vs job seekers
  const isRecruiter = user?.role === "recruiter";
  
  const jobSeekerLinks = [
    { path: "/", icon: TrendingUp, labelKey: "nav.dashboard" },
    { path: "/resume", icon: FileText, labelKey: "nav.myResume" },
    { path: "/resume-profiles", icon: Users, labelKey: "nav.resumeProfiles" },
    { path: "/skill-assessments", icon: Award, labelKey: "nav.skillTests" },
    { path: "/search", icon: Search, labelKey: "nav.jobSearch" },
    { path: "/saved", icon: Bookmark, labelKey: "nav.savedJobs" },
    { path: "/applications", icon: CheckSquare, labelKey: "nav.applications" },
    { path: "/interviews", icon: Video, labelKey: "nav.myInterviews" },
    { path: "/interview-calendar", icon: CalendarDays, labelKey: "nav.interviewCalendar" },
    { path: "/predictor", icon: Target, labelKey: "nav.successPredictor" },
    { path: "/interview", icon: Mic, labelKey: "nav.interviewPrep" },
    { path: "/qa-practice", icon: MessageSquare, labelKey: "nav.qaPractice" },
    { path: "/video-practice", icon: Video, labelKey: "nav.videoPractice" },
    { path: "/voice-coach", icon: Volume2, labelKey: "nav.voiceCoach" },
    { path: "/realtime-stt", icon: Mic, labelKey: "nav.realtimeSTT" },
    { path: "/meeting-notes", icon: FileText, labelKey: "nav.meetingNotes" },
    { path: "/cover-letter", icon: PenTool, labelKey: "nav.coverLetter" },
    { path: "/alerts", icon: Bell, labelKey: "nav.jobAlerts" },
    { path: "/notifications", icon: Bell, labelKey: "nav.notifications" },
    { path: "/salary-insights", icon: DollarSign, labelKey: "nav.salaryInsights" },
    { path: "/analytics", icon: BarChart3, labelKey: "nav.analytics" },
    { path: "/analytics-funnel", icon: BarChart3, labelKey: "nav.analyticsFunnel" },
    { path: "/dragon-automator", icon: Bot, labelKey: "nav.dragonAutomator" },
    { path: "/admin", icon: Shield, labelKey: "nav.adminDashboard", adminOnly: true },
    { path: "/companies", icon: Briefcase, labelKey: "nav.companies" },
    { path: "/messages", icon: MessageSquare, labelKey: "nav.messages" },
    { path: "/id-verification", icon: ShieldCheck, labelKey: "nav.idVerification" },
    { path: "/privacy", icon: Shield, labelKey: "nav.privacy" },
    { path: "/membership", icon: Crown, labelKey: "nav.membership" },
  ];
  
  const recruiterLinks = [
    { path: "/recruiter/dashboard", icon: LayoutDashboard, labelKey: "recruiter.dashboard" },
    { path: "/recruiter/jobs", icon: Briefcase, labelKey: "recruiter.myJobPostings" },
    { path: "/interviews", icon: Video, labelKey: "recruiter.interviews" },
    { path: "/recruiter/candidates", icon: UserSearch, labelKey: "recruiter.searchCandidates" },
    { path: "/companies", icon: Briefcase, labelKey: "nav.companies" },
    { path: "/messages", icon: MessageSquare, labelKey: "nav.messages" },
    { path: "/notifications", icon: Bell, labelKey: "nav.notifications" },
    { path: "/id-verification", icon: ShieldCheck, labelKey: "nav.idVerification" },
    { path: "/privacy", icon: Shield, labelKey: "nav.privacy" },
    { path: "/membership", icon: Crown, labelKey: "nav.membership" },
  ];
  
  const links = isRecruiter ? recruiterLinks : jobSeekerLinks;

  return (
    <>
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/40 z-40 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
      
      <aside className={`
        fixed top-0 left-0 z-50 h-full w-64 
        ${isDark ? 'bg-batik-charcoal border-batik-dark-grey' : 'bg-white border-slate-200'}
        border-r transform transition-transform duration-200 ease-out
        lg:translate-x-0 lg:static lg:z-auto
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        flex flex-col
      `}>
        <div className={`flex items-center justify-between p-6 border-b ${isDark ? 'border-batik-dark-grey' : 'border-slate-100'} shrink-0`}>
          <div className="flex items-center gap-3">
            <img 
              src="/logo-small.png" 
              alt="MedMatch Logo" 
              className="w-10 h-10 object-contain rounded-lg"
              data-testid="sidebar-logo"
            />
            <span className={`font-semibold text-lg ${isDark ? 'text-white' : 'text-slate-900'}`} style={{ fontFamily: 'IBM Plex Sans' }}>
              MedMatch
            </span>
          </div>
          <button 
            className={`lg:hidden p-2 rounded-md ${isDark ? 'hover:bg-batik-dark-grey text-slate-300' : 'hover:bg-slate-100'}`}
            onClick={() => setIsOpen(false)}
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <nav className="p-4 space-y-1 flex-1 overflow-y-auto" key={`nav-${language}-${translationVersion}`}>
          {/* Translation loading indicator for AI languages */}
          {!isBundled(language) && isLoadingAI && (
            <div className="px-3 py-2 mb-2 text-xs text-turquoise flex items-center gap-2">
              <span className="animate-spin w-3 h-3 border-2 border-turquoise border-t-transparent rounded-full"></span>
              <span>Loading translations...</span>
            </div>
          )}
          {!isBundled(language) && !isLoadingAI && translationProgress > 0 && translationProgress < 100 && (
            <div className="px-3 py-2 mb-2">
              <div className="h-1 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-turquoise transition-all duration-300"
                  style={{ width: `${translationProgress}%` }}
                ></div>
              </div>
            </div>
          )}
          {links.map(({ path, icon: Icon, labelKey }) => (
            <NavLink
              key={`${path}-${translationVersion}`}
              to={path}
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''} ${isDark ? 'dark' : ''}`}
              onClick={() => setIsOpen(false)}
              data-testid={`nav-${labelKey.split('.').pop().toLowerCase()}`}
            >
              <Icon className="w-5 h-5" />
              <span>{t(labelKey)}</span>
            </NavLink>
          ))}
        </nav>
      </aside>
    </>
  );
};

// Header Component with Dark Mode Toggle
const Header = ({ onMenuClick, resume, user, onLogout }) => {
  const { isDark, toggleTheme } = useTheme();
  
  return (
    <header className={`glass-header sticky top-0 z-30 px-6 py-4 ${isDark ? 'dark' : ''}`}>
      <div className="flex items-center justify-between">
        <button 
          className={`lg:hidden p-2 rounded-md ${isDark ? 'hover:bg-batik-dark-grey text-slate-300' : 'hover:bg-slate-100'}`}
          onClick={onMenuClick}
          data-testid="mobile-menu-btn"
        >
          <Menu className="w-5 h-5" />
        </button>
        
        <div className="flex-1" />
        
        <div className="flex items-center gap-4">
          {/* Offline Status Indicator */}
          <OfflineIndicator compact={true} />
          
          {/* Global Language Selector */}
          <GlobalLanguageSelector compact={true} />
          
          {/* Dark Mode Toggle */}
          <button
            onClick={toggleTheme}
            className={`p-2 rounded-lg transition-all ${
              isDark 
                ? 'bg-turquoise/20 text-turquoise hover:bg-turquoise/30' 
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
            data-testid="theme-toggle"
            title={isDark ? "Switch to Light Mode" : "Switch to Dark Mode"}
          >
            {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>

          {user && (
            <div className="flex items-center gap-3">
              <div className={`w-9 h-9 rounded-full flex items-center justify-center ${
                isDark ? 'bg-batik-dark-grey' : 'bg-slate-100'
              }`}>
                <span className={`text-sm font-medium ${isDark ? 'text-turquoise' : 'text-slate-700'}`}>
                  {user.name?.charAt(0) || user.email?.charAt(0) || 'U'}
                </span>
              </div>
              <span className={`text-sm font-medium hidden sm:block ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                {user.name || user.email?.split('@')[0] || 'User'}
              </span>
              <button
                onClick={onLogout}
                className={`p-2 rounded-lg ${isDark ? 'text-slate-400 hover:text-red-400 hover:bg-red-900/20' : 'text-slate-500 hover:text-red-500 hover:bg-red-50'}`}
                title="Sign Out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

// Apply Dialog Component
const ApplyDialog = ({ job, open, onClose, onConfirm }) => {
  const [notes, setNotes] = useState("");
  const { isDark } = useTheme();

  const handleConfirm = () => {
    onConfirm(job, notes);
    setNotes("");
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className={isDark ? 'bg-batik-charcoal border-batik-dark-grey text-white' : ''}>
        <DialogHeader>
          <DialogTitle style={{ fontFamily: 'IBM Plex Sans' }}>Track Application</DialogTitle>
          <DialogDescription className={isDark ? 'text-slate-400' : ''}>Add this job to your application tracker</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div>
            <p className={`font-medium ${isDark ? 'text-white' : 'text-slate-900'}`}>{job?.title}</p>
            <p className={`text-sm ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>{job?.company}</p>
          </div>
          <div>
            <label className={`text-sm font-medium ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>Notes (optional)</label>
            <Textarea
              placeholder="Add any notes about this application..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className={`mt-1 ${isDark ? 'bg-batik-dark-grey border-batik-grey text-white' : ''}`}
              data-testid="apply-notes"
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onClose} className={isDark ? 'border-batik-grey text-slate-300' : ''}>Cancel</Button>
          <Button onClick={handleConfirm} data-testid="confirm-apply">Add to Applications</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

// Main App Content Component
function AppContent() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [resume, setResume] = useState(null);
  const [savedJobs, setSavedJobs] = useState([]);
  const [applications, setApplications] = useState([]);
  const [applyDialogJob, setApplyDialogJob] = useState(null);
  const [user, setUser] = useState(null);
  const [membership, setMembership] = useState(null);
  const [isAuthChecking, setIsAuthChecking] = useState(true);
  const [showDragonAI, setShowDragonAI] = useState(false);
  const [consentChecked, setConsentChecked] = useState(false);
  const [needsConsent, setNeedsConsent] = useState(false);
  const { isDark } = useTheme();
  const location = useLocation();
  const navigate = useNavigate();
  
  // Onboarding tour state
  const { showTour, completeTour } = useOnboardingTour();

  // Check privacy consent status after login
  useEffect(() => {
    if (!user || consentChecked || isAuthChecking) return;
    
    const checkConsent = async () => {
      // Skip if already granted locally
      if (localStorage.getItem("medmatch-consent-granted") === "true") {
        setConsentChecked(true);
        return;
      }
      
      try {
        const token = localStorage.getItem("medmatch-token");
        if (!token) {
          setConsentChecked(true);
          return;
        }
        
        const response = await axios.get(`${API}/privacy/consent/status`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        if (!response.data.has_consented) {
          setNeedsConsent(true);
          // Redirect to consent page if not on it already
          if (location.pathname !== '/consent' && location.pathname !== '/login') {
            navigate('/consent');
          }
        } else {
          localStorage.setItem("medmatch-consent-granted", "true");
        }
      } catch (e) {
        // If endpoint fails, don't block user - consent not required to use app
        console.error("Consent check failed:", e);
      }
      setConsentChecked(true);
    };
    
    checkConsent();
  }, [user, consentChecked, isAuthChecking, location.pathname, navigate]);

  // Initialize offline storage
  useEffect(() => {
    offlineStorage.init().catch(console.error);
  }, []);

  // Check for OAuth callback (session_id in hash) 
  useEffect(() => {
    const hash = window.location.hash;
    if (hash && hash.includes('session_id=')) {
      // Don't check auth yet, let the login page handle it
      setIsAuthChecking(false);
      return;
    }
    
    // Check authentication
    const checkAuth = async () => {
      try {
        const response = await axios.get(`${API}/auth/me`, { withCredentials: true });
        if (response.data?.user_id) {
          setUser(response.data);
        }
      } catch (e) {
        // Not authenticated
      }
      setIsAuthChecking(false);
    };
    checkAuth();
  }, []);

  useEffect(() => {
    if (!user) return;
    
    const fetchData = async () => {
      try {
        const [resumeRes, savedRes, appsRes, membershipRes] = await Promise.all([
          axios.get(`${API}/resume`),
          axios.get(`${API}/jobs/saved`),
          axios.get(`${API}/applications`),
          axios.get(`${API}/membership/status`, { withCredentials: true })
        ]);
        if (resumeRes.data) {
          setResume(resumeRes.data);
          // Cache resume for offline use
          offlineStorage.cacheResume(resumeRes.data).catch(console.error);
        }
        setSavedJobs(savedRes.data);
        // Cache saved jobs for offline use
        if (savedRes.data?.length > 0) {
          offlineStorage.cacheJobs(savedRes.data).catch(console.error);
        }
        setApplications(appsRes.data);
        setMembership(membershipRes.data);
        // Cache user data
        offlineStorage.cacheUser(user).catch(console.error);
      } catch (e) {
        console.error("Failed to fetch data:", e);
        // Try to load from cache if offline
        if (!navigator.onLine) {
          try {
            const cachedResume = await offlineStorage.getCachedResume();
            const cachedJobs = await offlineStorage.getCachedJobs();
            const cachedUser = await offlineStorage.getCachedUser();
            if (cachedResume) setResume(cachedResume);
            if (cachedJobs?.length > 0) setSavedJobs(cachedJobs);
            if (cachedUser) setUser(cachedUser);
            toast.info("Loaded cached data - you're offline");
          } catch (cacheErr) {
            console.error("Cache load error:", cacheErr);
          }
        }
      }
    };
    fetchData();
  }, [user]);

  const handleAuthSuccess = (userData) => {
    setUser(userData);
    // Sync language preference from server if available
    if (userData?.language) {
      localStorage.setItem("medmatch-language", userData.language);
      window.dispatchEvent(new CustomEvent('languageSync', { detail: userData.language }));
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post(`${API}/auth/logout`, {}, { withCredentials: true });
    } catch (e) {
      // Continue logout anyway
    }
    setUser(null);
    setResume(null);
    setSavedJobs([]);
    setApplications([]);
    toast.success("Signed out successfully");
  };

  const handleSaveJob = async (job) => {
    try {
      const response = await axios.post(`${API}/jobs/save`, job);
      setSavedJobs([response.data, ...savedJobs]);
      // Cache the updated saved jobs
      offlineStorage.cacheJobs([response.data, ...savedJobs]).catch(console.error);
      toast.success("Job saved!");
    } catch (e) {
      if (e.response?.status === 400) {
        toast.info("Job already saved");
      } else if (!navigator.onLine) {
        // Queue the action for later sync
        await offlineStorage.queueAction({
          type: 'save_job',
          data: job,
          endpoint: `${API}/jobs/save`
        });
        setSavedJobs([{ ...job, id: `temp_${Date.now()}`, pendingSync: true }, ...savedJobs]);
        toast.info("Job saved offline - will sync when online");
      } else {
        toast.error("Failed to save job");
      }
    }
  };

  const handleRemoveSavedJob = async (id) => {
    try {
      await axios.delete(`${API}/jobs/saved/${id}`);
      setSavedJobs(savedJobs.filter(s => s.id !== id));
      toast.success("Job removed from saved");
    } catch (e) {
      toast.error("Failed to remove job");
    }
  };

  const handleApply = (job) => setApplyDialogJob(job);

  const handleConfirmApply = async (job, notes) => {
    try {
      const response = await axios.post(`${API}/applications`, { job, notes });
      setApplications([response.data, ...applications]);
      toast.success("Application tracked!");
      if (job.url) window.open(job.url, '_blank');
    } catch (e) {
      toast.error("Failed to track application");
    }
  };

  const handleUpdateStatus = async (appId, status) => {
    try {
      await axios.put(`${API}/applications/${appId}`, { status });
      setApplications(applications.map(a => a.id === appId ? { ...a, status } : a));
      toast.success("Status updated");
    } catch (e) {
      toast.error("Failed to update status");
    }
  };

  const handleDeleteApplication = async (appId) => {
    try {
      await axios.delete(`${API}/applications/${appId}`);
      setApplications(applications.filter(a => a.id !== appId));
      toast.success("Application deleted");
    } catch (e) {
      toast.error("Failed to delete application");
    }
  };

  const handleAnalyzeJob = async (job) => {
    if (!resume) {
      toast.error("Please upload your resume first");
      throw new Error("No resume");
    }
    const response = await axios.post(`${API}/jobs/analyze`, {
      job_title: job.title,
      job_description: job.description,
      company: job.company
    });
    return response.data;
  };

  // Show loading while checking auth
  if (isAuthChecking) {
    return (
      <div className={`min-h-screen flex items-center justify-center ${isDark ? 'bg-batik-black' : 'bg-slate-50'}`}>
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-turquoise"></div>
      </div>
    );
  }

  // Show login page if not authenticated (but allow hash with session_id to pass through)
  if (!user && !window.location.hash.includes('session_id')) {
    return <LoginPage onAuthSuccess={handleAuthSuccess} />;
  }

  // If we have a session_id in hash, show login page to process it
  if (window.location.hash.includes('session_id')) {
    return <LoginPage onAuthSuccess={handleAuthSuccess} />;
  }

  return (
    <div className={`min-h-screen flex ${isDark ? 'bg-batik-black text-white' : 'bg-slate-50'}`}>
      {/* Offline Banner - shows when user goes offline/online */}
      <OfflineBanner />
      
      <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} user={user} />
      
      <div className="flex-1 flex flex-col min-w-0">
        <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} resume={resume} user={user} onLogout={handleLogout} />
        
        {/* Upgrade Banner for trial/expired users */}
        <UpgradeBanner membership={membership} />
        
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<Dashboard resume={resume} savedJobs={savedJobs} applications={applications} onNavigate={navigate} user={user} />} />
            <Route path="/login" element={<LoginPage onAuthSuccess={handleAuthSuccess} />} />
            <Route path="/resume" element={<ResumePage resume={resume} setResume={setResume} />} />
            <Route path="/resume-profiles" element={<ResumeProfilesPage />} />
            <Route path="/search" element={<JobSearchPage savedJobs={savedJobs} onSave={handleSaveJob} onApply={handleApply} onAnalyze={handleAnalyzeJob} />} />
            <Route path="/saved" element={<SavedJobsPage savedJobs={savedJobs} onRemove={handleRemoveSavedJob} onApply={handleApply} onAnalyze={handleAnalyzeJob} />} />
            <Route path="/applications" element={<ApplicationsPage applications={applications} onUpdateStatus={handleUpdateStatus} onDelete={handleDeleteApplication} />} />
            {/* Premium Features - wrapped with PremiumGate */}
            <Route path="/predictor" element={
              <PremiumGate feature="success_predictor">
                <SuccessPredictorPage resume={resume} />
              </PremiumGate>
            } />
            <Route path="/interview" element={
              <PremiumGate feature="interview_prep">
                <InterviewPrepPage resume={resume} />
              </PremiumGate>
            } />
            <Route path="/qa-practice" element={
              <PremiumGate feature="interview_prep">
                <QAPracticePage resume={resume} />
              </PremiumGate>
            } />
            <Route path="/voice-coach" element={
              <PremiumGate feature="voice_coach">
                <VoiceCoachPage resume={resume} />
              </PremiumGate>
            } />
            <Route path="/video-interview" element={
              <PremiumGate feature="video_interview">
                <VideoInterviewPage resume={resume} />
              </PremiumGate>
            } />
            <Route path="/cover-letter" element={
              <PremiumGate feature="ai_cover_letter">
                <CoverLetterPage resume={resume} />
              </PremiumGate>
            } />
            <Route path="/alerts" element={
              <PremiumGate feature="email_alerts">
                <JobAlertsPage resume={resume} />
              </PremiumGate>
            } />
            <Route path="/analytics" element={
              <PremiumGate feature="analytics">
                <AnalyticsDashboard />
              </PremiumGate>
            } />
            <Route path="/salary-insights" element={
              <PremiumGate feature="salary_insights">
                <SalaryInsightsPage resume={resume} />
              </PremiumGate>
            } />
            <Route path="/membership" element={<MembershipPage user={user} />} />
            <Route path="/payment-success" element={<MembershipPage user={user} />} />
            <Route path="/recruiter/jobs" element={<RecruiterJobsPage user={user} />} />
            <Route path="/recruiter/dashboard" element={<RecruiterDashboard user={user} />} />
            <Route path="/recruiter/jobs/:jobId/applicants" element={<ApplicantTracker user={user} />} />
            <Route path="/recruiter/candidates" element={<CandidateSearch user={user} />} />
            <Route path="/messages" element={<MessagesPage user={user} />} />
            <Route path="/messages/new" element={<MessagesPage user={user} />} />
            <Route path="/companies/:companyId" element={<CompanyProfilePage user={user} />} />
            <Route path="/skill-assessments" element={<SkillAssessmentsPage user={user} />} />
            <Route path="/companies" element={<CompaniesPage user={user} />} />
            <Route path="/interviews" element={<InterviewSchedulingPage user={user} />} />
            <Route path="/notifications" element={<NotificationsPage user={user} />} />
            <Route path="/id-verification" element={<IDVerificationPage user={user} />} />
            <Route path="/video-practice" element={<VideoInterviewPage resume={resume} user={user} />} />
            <Route path="/realtime-stt" element={
              <PremiumGate feature="voice_coach">
                <RealTimeSTTPage />
              </PremiumGate>
            } />
            <Route path="/meeting-notes" element={
              <PremiumGate feature="voice_coach">
                <MeetingNotesPage />
              </PremiumGate>
            } />
            <Route path="/interview-calendar" element={
              <PremiumGate feature="voice_coach">
                <InterviewCalendarPage />
              </PremiumGate>
            } />
            <Route path="/analytics-funnel" element={
              <PremiumGate feature="analytics">
                <AnalyticsFunnelPage />
              </PremiumGate>
            } />
            <Route path="/dragon-automator" element={
              <DragonAutomatorPage />
            } />
            <Route path="/admin" element={
              <AdminDashboard />
            } />
            <Route path="/admin/metrics" element={
              <ProductionMetricsPage />
            } />
            <Route path="/admin/translations" element={
              <TranslationAnalyticsPage />
            } />
            <Route path="/privacy" element={<PrivacySettingsPage />} />
            <Route path="/consent" element={
              <PrivacyConsentScreen 
                onConsentGranted={() => navigate('/')}
                showSkip={true}
                onSkip={() => navigate('/')}
              />
            } />
            {/* Recruiter RBAC Routes */}
            <Route path="/recruiter/candidates" element={<BlindScreeningDashboard />} />
            <Route path="/recruiter/verify" element={<RecruiterVerificationPage />} />
            <Route path="/contact-requests" element={<ContactRequestScreen requests={[]} />} />
          </Routes>
        </main>
      </div>

      {/* Onboarding Tour for first-time users */}
      {showTour && user && <OnboardingTour onComplete={completeTour} user={user} />}

      {/* PWA Install Prompts */}
      <InstallPrompt />
      <PWAInstallPrompt />

      {/* KARAU Dragon AI */}
      <DragonButton onClick={() => setShowDragonAI(true)} />
      <KarauDragonAI user={user} isOpen={showDragonAI} onClose={() => setShowDragonAI(false)} />

      <ApplyDialog job={applyDialogJob} open={!!applyDialogJob} onClose={() => setApplyDialogJob(null)} onConfirm={handleConfirmApply} />
      <Toaster position="bottom-right" richColors theme={isDark ? 'dark' : 'light'} />
    </div>
  );
}

// Main App Component with Theme Provider
function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <I18nProvider>
          <AppContent />
        </I18nProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
}

export default App;
