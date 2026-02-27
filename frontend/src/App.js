import { useState, useEffect, createContext, useContext } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, NavLink, useLocation, Navigate, useSearchParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { Toaster, toast } from "sonner";
import { 
  Search, Briefcase, FileText, Bookmark, CheckSquare, 
  Menu, X, TrendingUp, Bell, PenTool, Target, Mic, Moon, Sun, Volume2, BarChart3, Users, Video, LogOut, Crown, DollarSign, MessageSquare, UserSearch, LayoutDashboard, Award, ShieldCheck, CalendarDays, Bot, Shield, Code, HelpCircle, Home, FileCheck, Languages, Database, Gavel, Scale, Globe
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
import PortalSelector from "@/pages/PortalSelector";
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
import TranslationQADashboard from "@/components/TranslationQADashboard";
import AdminDashboard from "@/pages/AdminDashboard";
import AdminDataIntegrityPage from "@/pages/AdminDataIntegrityPage";
import AdminAICompliancePage from "@/pages/AdminAICompliancePage";
import AdminTranslationCoveragePage from "@/pages/AdminTranslationCoveragePage";
import GlobalCompliancePage from "@/pages/GlobalCompliancePage";
import CandidateTransparencyPage from "@/pages/CandidateTransparencyPage";
import ProductionMetricsPage from "@/pages/ProductionMetricsPage";
import TranslationAnalyticsPage from "@/pages/TranslationAnalyticsPage";
import PrivacySettingsPage from "@/pages/PrivacySettingsPage";
import PrivacyConsentScreen from "@/components/PrivacyConsentScreen";
import MatchExplanation from "@/components/MatchExplanation";
import BlindScreeningDashboard from "@/pages/BlindScreeningDashboard";
import ContactRequestScreen from "@/pages/ContactRequestScreen";
import RecruiterVerificationPage from "@/pages/RecruiterVerificationPage";
import AdminRecruiterVerificationPage from "@/pages/AdminRecruiterVerificationPage";
import AdminReviewModerationPage from "@/pages/AdminReviewModerationPage";
import TaxonomyExplorerPage from "@/pages/TaxonomyExplorerPage";
import CredentialsPage from "@/pages/CredentialsPage";
import LocationSettingsPage from "@/pages/LocationSettingsPage";
import EnterpriseAPIPage from "@/pages/EnterpriseAPIPage";
import PublicApplicationPage from "@/pages/PublicApplicationPage";
import TrackApplicationPage from "@/pages/TrackApplicationPage";
import ATSManagementPage from "@/pages/ATSManagementPage";
import VideoTutorialsPage from "@/pages/VideoTutorialsPage";
import PSVVerificationPage from "@/pages/PSVVerificationPage";
import CandidateScoringPage from "@/pages/CandidateScoringPage";
import JobDescriptionGenerator from "@/pages/JobDescriptionGenerator";
import HiringMetricsPage from "@/pages/HiringMetricsPage";
import DEIAnalyticsPage from "@/pages/DEIAnalyticsPage";
import TalentCRMPage from "@/pages/TalentCRMPage";
import KarauMeetLanding from "@/pages/KarauMeet/KarauMeetLanding";
import KarauMeetPortal from "@/pages/KarauMeet/KarauMeetPortal";
import MeetingRoom from "@/components/KarauMeet/MeetingRoom";
import { UpgradeBanner } from "@/components/PremiumGate";
import PremiumGate from "@/components/PremiumGate";
import OnboardingTour, { useOnboardingTour } from "@/components/OnboardingTour";
import InstallPrompt from "@/components/InstallPrompt";
import PWAInstallPrompt from "@/components/PWAInstallPrompt";
import KarauDragonAI, { DragonButton } from "@/components/KarauDragonAI";
import GlobalLanguageSelector from "@/components/GlobalLanguageSelector";
import NotificationCenter from "@/components/NotificationCenter";
import { I18nProvider, useTranslation } from "@/utils/i18n";
import { OfflineBanner, OfflineIndicator } from "@/components/OfflineIndicator";
import { offlineStorage } from "@/utils/offlineStorage";
import LanguageTour from "@/components/LanguageTour";
import LanguageDetectionBanner from "@/components/LanguageDetectionBanner";

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
  const navigate = useNavigate();
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
  
  // User role state for admin profile switching
  const [viewMode, setViewMode] = useState(() => {
    // Default: recruiters see recruiter view, job seekers see job seeker view
    // Admin users default to admin view but can switch to any view
    if (user?.is_admin || user?.role === "admin") return "admin";
    return user?.role === "recruiter" ? "recruiter" : "job_seeker";
  });
  
  // Admin users can switch between all views
  const isAdmin = user?.is_admin || user?.role === "admin" || user?.email === "admin@medmatch.com";
  
  const jobSeekerLinks = [
    { path: "/", icon: TrendingUp, labelKey: "nav.dashboard" },
    { path: "/tutorials", icon: HelpCircle, labelKey: "nav.helpTutorials" },
    { path: "/resume", icon: FileText, labelKey: "nav.myResume" },
    { path: "/resume-profiles", icon: Users, labelKey: "nav.resumeProfiles" },
    { path: "/skill-assessments", icon: Award, labelKey: "nav.skillTests" },
    { path: "/credentials", icon: Shield, labelKey: "nav.credentials" },
    { path: "/taxonomy", icon: Briefcase, labelKey: "nav.careerExplorer" },
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
    { path: "/location-settings", icon: Target, labelKey: "nav.locationSettings" },
    { path: "/salary-insights", icon: DollarSign, labelKey: "nav.salaryInsights" },
    { path: "/analytics", icon: BarChart3, labelKey: "nav.analytics" },
    { path: "/analytics-funnel", icon: BarChart3, labelKey: "nav.analyticsFunnel" },
    { path: "/dragon-automator", icon: Bot, labelKey: "nav.dragonAutomator" },
    { path: "/admin", icon: Shield, labelKey: "nav.adminDashboard", adminOnly: true },
    { path: "/companies", icon: Briefcase, labelKey: "nav.companies" },
    { path: "/messages", icon: MessageSquare, labelKey: "nav.messages" },
    { path: "/ai-transparency", icon: Scale, labelKey: "nav.aiAndYourRights" },
    { path: "/id-verification", icon: ShieldCheck, labelKey: "nav.idVerification" },
    { path: "/privacy", icon: Shield, labelKey: "nav.privacy" },
    { path: "/membership", icon: Crown, labelKey: "nav.membership" },
  ];
  
  const recruiterLinks = [
    { path: "/recruiter/dashboard", icon: LayoutDashboard, labelKey: "recruiter.dashboard" },
    { path: "/tutorials", icon: HelpCircle, labelKey: "nav.helpTutorials" },
    { path: "/recruiter/jobs", icon: Briefcase, labelKey: "recruiter.myJobPostings" },
    { path: "/recruiter/ats", icon: Users, labelKey: "nav.applicantTracking" },
    { path: "/ai-scoring", icon: Target, labelKey: "AI Candidate Scoring" },
    { path: "/jd-generator", icon: FileText, labelKey: "AI JD Generator" },
    { path: "/hiring-metrics", icon: BarChart3, labelKey: "Hiring Metrics" },
    { path: "/interviews", icon: Video, labelKey: "recruiter.interviews" },
    { path: "/recruiter/candidates", icon: UserSearch, labelKey: "recruiter.searchCandidates" },
    { path: "/psv", icon: FileCheck, labelKey: "nav.psvVerificationHub" },
    { path: "/recruiter/compliance", icon: Gavel, labelKey: "nav.aiCompliance" },
    { path: "/companies", icon: Briefcase, labelKey: "nav.companies" },
    { path: "/messages", icon: MessageSquare, labelKey: "nav.messages" },
    { path: "/notifications", icon: Bell, labelKey: "nav.notifications" },
    { path: "/enterprise/api", icon: Code, labelKey: "nav.enterpriseAPI" },
    { path: "/id-verification", icon: ShieldCheck, labelKey: "nav.idVerification" },
    { path: "/privacy", icon: Shield, labelKey: "nav.privacy" },
    { path: "/membership", icon: Crown, labelKey: "nav.membership" },
  ];
  
  // Admin-specific navigation links
  const adminLinks = [
    { path: "/admin", icon: Shield, labelKey: "nav.adminDashboard" },
    { path: "/admin/data-integrity", icon: Database, labelKey: "nav.dataIntegrityAIQA" },
    { path: "/admin/ai-compliance", icon: Gavel, labelKey: "nav.aiCompliance" },
    { path: "/admin/global-compliance", icon: Globe, labelKey: "nav.globalCompliance" },
    { path: "/admin/recruiters", icon: Users, labelKey: "nav.recruiterVerification" },
    { path: "/admin/reviews", icon: FileText, labelKey: "nav.reviewModeration" },
    { path: "/admin/translation-coverage", icon: Languages, labelKey: "nav.translationCoverage" },
    { path: "/tutorials", icon: HelpCircle, labelKey: "nav.helpTutorials" },
    { path: "/qa-dashboard", icon: Languages, labelKey: "nav.translationQA" },
    { path: "/notifications", icon: Bell, labelKey: "nav.notifications" },
    { path: "/enterprise/api", icon: Code, labelKey: "nav.enterpriseAPI" },
    { path: "/membership", icon: Crown, labelKey: "nav.membership" },
  ];
  
  // Determine which links to show based on view mode
  const isAdminView = viewMode === "admin";
  const isRecruiterView = viewMode === "recruiter";
  
  // Filter links based on user role - admins see adminOnly items
  const baseLinks = isAdminView ? adminLinks : (isRecruiterView ? recruiterLinks : jobSeekerLinks);
  const links = baseLinks.filter(link => {
    if (link.adminOnly) return isAdmin;
    return true;
  });
  
  // Add admin dashboard link for non-admin views when user is admin
  if (isAdmin && !isAdminView && !links.some(l => l.path === '/admin')) {
    links.push({ path: "/admin", icon: Shield, labelKey: "nav.adminDashboard", adminOnly: true });
  }

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
          <button 
            onClick={() => { navigate('/'); setIsOpen(false); }}
            className="flex items-center gap-3 hover:opacity-80 transition-opacity"
            data-testid="home-btn"
          >
            <img 
              src="/logo-small.png" 
              alt="MedMatch-AI KARAU Logo" 
              className="w-10 h-10 object-contain rounded-lg"
              data-testid="sidebar-logo"
            />
            <span className={`font-semibold text-lg ${isDark ? 'text-white' : 'text-slate-900'}`} style={{ fontFamily: 'IBM Plex Sans' }}>
              MedMatch-AI KARAU
            </span>
          </button>
          <button 
            className={`lg:hidden p-2 rounded-md ${isDark ? 'hover:bg-batik-dark-grey text-slate-300' : 'hover:bg-slate-100'}`}
            onClick={() => setIsOpen(false)}
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        {/* Admin Profile Switcher - 3 View Modes */}
        {isAdmin && (
          <div className={`px-4 py-3 border-b ${isDark ? 'border-batik-dark-grey' : 'border-slate-100'}`}>
            <p className={`text-xs mb-2 ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>View as:</p>
            <div className="flex gap-1">
              <button
                onClick={() => setViewMode("admin")}
                className={`flex-1 px-2 py-1.5 text-xs rounded-lg transition-all ${
                  viewMode === "admin"
                    ? 'bg-purple-600 text-white'
                    : isDark ? 'bg-batik-dark-grey text-slate-300 hover:bg-batik-grey' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
                data-testid="view-admin-btn"
              >
                Admin
              </button>
              <button
                onClick={() => setViewMode("job_seeker")}
                className={`flex-1 px-2 py-1.5 text-xs rounded-lg transition-all ${
                  viewMode === "job_seeker"
                    ? 'bg-turquoise text-white'
                    : isDark ? 'bg-batik-dark-grey text-slate-300 hover:bg-batik-grey' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
                data-testid="view-job-seeker-btn"
              >
                Job Seeker
              </button>
              <button
                onClick={() => setViewMode("recruiter")}
                className={`flex-1 px-2 py-1.5 text-xs rounded-lg transition-all ${
                  viewMode === "recruiter"
                    ? 'bg-turquoise text-white'
                    : isDark ? 'bg-batik-dark-grey text-slate-300 hover:bg-batik-grey' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
                data-testid="view-recruiter-btn"
              >
                Recruiter
              </button>
            </div>
          </div>
        )}
        
        <nav className="p-4 space-y-1 flex-1 overflow-y-auto" key={`nav-${language}-${translationVersion}-${viewMode}`}>
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
              <Icon className="w-5 h-5 flex-shrink-0" />
              <span className="truncate text-sm" title={t(labelKey)}>{t(labelKey)}</span>
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
  const navigate = useNavigate();
  
  return (
    <header className={`glass-header sticky top-0 z-30 px-6 py-4 ${isDark ? 'dark' : ''}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button 
            className={`lg:hidden p-2 rounded-md ${isDark ? 'hover:bg-batik-dark-grey text-slate-300' : 'hover:bg-slate-100'}`}
            onClick={onMenuClick}
            data-testid="mobile-menu-btn"
          >
            <Menu className="w-5 h-5" />
          </button>
          
          {/* Home Button - always visible */}
          <button
            onClick={() => navigate('/')}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-all ${
              isDark 
                ? 'bg-slate-700/50 text-slate-300 hover:bg-slate-700' 
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
            data-testid="header-home-btn"
            title="Go to Dashboard"
          >
            <Home className="w-4 h-4" />
            <span className="text-sm font-medium hidden sm:block">Home</span>
          </button>
        </div>
        
        <div className="flex-1" />
        
        <div className="flex items-center gap-4">
          {/* Help Button */}
          <button
            onClick={() => navigate('/tutorials')}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-all ${
              isDark 
                ? 'bg-teal-900/30 text-teal-400 hover:bg-teal-900/50' 
                : 'bg-teal-50 text-teal-600 hover:bg-teal-100'
            }`}
            data-testid="help-btn"
            title="Help & Tutorials"
          >
            <HelpCircle className="w-4 h-4" />
            <span className="text-sm font-medium hidden sm:block">Help</span>
          </button>
          
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

          {/* Notification Center */}
          {user && <NotificationCenter />}

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
function AppContent({ skipPortalSelector = false }) {
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
  
  // Language tour state - show for new users
  const [showLanguageTour, setShowLanguageTour] = useState(false);
  
  // Check if language tour should be shown
  useEffect(() => {
    if (user && !localStorage.getItem('medmatch-tour-completed') && !localStorage.getItem('medmatch_tour_completed') && !localStorage.getItem('medmatch_tour_skipped')) {
      const timer = setTimeout(() => {
        setShowLanguageTour(true);
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [user]);

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
          // Redirect to consent page if not on excluded paths
          const excludedPaths = ['/consent', '/login', '/recruiter/verify', '/recruiter/dashboard'];
          if (!excludedPaths.some(path => location.pathname.startsWith(path))) {
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
        // API returns { saved_jobs: [], count: 0 } - extract the array
        const savedJobsArray = savedRes.data?.saved_jobs || savedRes.data || [];
        setSavedJobs(Array.isArray(savedJobsArray) ? savedJobsArray : []);
        // Cache saved jobs for offline use
        if (savedJobsArray?.length > 0) {
          offlineStorage.cacheJobs(savedJobsArray).catch(console.error);
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

  // Check if current path is a public route (no auth required)
  const isPublicRoute = location.pathname.startsWith('/apply/') || location.pathname.startsWith('/track-application/');
  
  // Check if current path is AI KARAU Meeting standalone portal
  const isKarauMeetPortal = location.pathname.startsWith('/karau-meet');

  // Show loading while checking auth (except for public routes and karau-meet)
  if (isAuthChecking && !isPublicRoute && !isKarauMeetPortal) {
    return (
      <div className={`min-h-screen flex items-center justify-center ${isDark ? 'bg-batik-black' : 'bg-slate-50'}`}>
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-turquoise"></div>
      </div>
    );
  }
  
  // Render AI KARAU Meeting standalone portal (has its own auth)
  if (isKarauMeetPortal) {
    return (
      <>
        <Routes>
          <Route path="/karau-meet/*" element={<KarauMeetPortal />} />
        </Routes>
        <Toaster position="top-right" richColors theme="dark" />
      </>
    );
  }

  // Render public routes without authentication
  if (isPublicRoute) {
    return (
      <>
        <Routes>
          <Route path="/apply/:token" element={<PublicApplicationPage />} />
          <Route path="/track-application/:applicationId" element={<TrackApplicationPage />} />
        </Routes>
        <Toaster position="top-right" richColors theme={isDark ? 'dark' : 'light'} />
      </>
    );
  }

  // Check if we're on the login page specifically
  const isLoginPage = location.pathname === '/login';

  // Show Portal Selector if not authenticated (except for login page, session_id hash, or when skipPortalSelector is true)
  if (!user && !window.location.hash.includes('session_id') && !isLoginPage && !skipPortalSelector) {
    return (
      <>
        <PortalSelector />
        <Toaster position="top-right" richColors theme="dark" />
      </>
    );
  }

  // Show login page if on /login route, processing session_id, or skipPortalSelector is true
  if (!user && (isLoginPage || window.location.hash.includes('session_id') || skipPortalSelector)) {
    return (
      <>
        <LoginPage onAuthSuccess={handleAuthSuccess} />
        <Toaster position="top-right" richColors theme={isDark ? 'dark' : 'light'} />
      </>
    );
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
            <Route path="/recruiter/candidates" element={<BlindScreeningDashboard />} />
            <Route path="/recruiter/ats" element={<ATSManagementPage />} />
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
            <Route path="/qa-dashboard" element={<TranslationQADashboard />} />
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
            <Route path="/ai-transparency" element={<CandidateTransparencyPage />} />
            <Route path="/recruiter/compliance" element={<AdminAICompliancePage />} />
            <Route path="/consent" element={
              <PrivacyConsentScreen 
                onConsentGranted={() => navigate('/')}
                showSkip={true}
                onSkip={() => navigate('/')}
              />
            } />
            {/* Recruiter RBAC Routes */}
            <Route path="/recruiter/verify" element={<RecruiterVerificationPage />} />
            <Route path="/contact-requests" element={<ContactRequestScreen requests={[]} />} />
            <Route path="/admin/recruiters" element={<AdminRecruiterVerificationPage />} />
            <Route path="/admin/reviews" element={<AdminReviewModerationPage />} />
            <Route path="/admin/data-integrity" element={<AdminDataIntegrityPage />} />
            <Route path="/admin/ai-compliance" element={<AdminAICompliancePage />} />
            <Route path="/admin/global-compliance" element={<GlobalCompliancePage />} />
            <Route path="/admin/translation-coverage" element={<AdminTranslationCoveragePage />} />
            <Route path="/taxonomy" element={<TaxonomyExplorerPage />} />
            <Route path="/careers" element={<TaxonomyExplorerPage />} />
            <Route path="/credentials" element={<CredentialsPage />} />
            <Route path="/location-settings" element={<LocationSettingsPage />} />
            <Route path="/enterprise/api" element={<EnterpriseAPIPage />} />
            <Route path="/tutorials" element={<VideoTutorialsPage />} />
            <Route path="/help" element={<VideoTutorialsPage />} />
            <Route path="/psv" element={<PSVVerificationPage />} />
            <Route path="/verification-hub" element={<PSVVerificationPage />} />
            <Route path="/ai-scoring" element={<CandidateScoringPage />} />
            <Route path="/jd-generator" element={<JobDescriptionGenerator />} />
            <Route path="/hiring-metrics" element={<HiringMetricsPage />} />
          </Routes>
        </main>
      </div>

      {/* Onboarding Tour for first-time users */}
      {showTour && user && !showLanguageTour && <OnboardingTour onComplete={completeTour} user={user} />}
      
      {/* Interactive Language Tour */}
      <LanguageTour 
        isOpen={showLanguageTour && !showTour} 
        onClose={() => setShowLanguageTour(false)} 
        language={localStorage.getItem('medmatch_language') || 'en'}
      />

      {/* PWA Install Prompts */}
      <InstallPrompt />
      <PWAInstallPrompt />

      {/* KARAU Dragon AI */}
      <DragonButton onClick={() => setShowDragonAI(true)} />
      <KarauDragonAI user={user} isOpen={showDragonAI} onClose={() => setShowDragonAI(false)} />

      <ApplyDialog job={applyDialogJob} open={!!applyDialogJob} onClose={() => setApplyDialogJob(null)} onConfirm={handleConfirmApply} />
      
      {/* Language Detection Banner - shows when browser language differs */}
      <LanguageDetectionBanner />
      
      <Toaster position="top-right" richColors theme={isDark ? 'dark' : 'light'} />
    </div>
  );
}

// Subdomain Router - Routes to correct portal based on hostname
const SubdomainRouter = () => {
  const hostname = window.location.hostname;
  
  // Extract subdomain from hostname
  const getSubdomain = () => {
    // Check URL param for testing in any environment: ?portal=meet or ?portal=jobs
    const params = new URLSearchParams(window.location.search);
    const portalParam = params.get('portal');
    if (portalParam) {
      return portalParam.toLowerCase();
    }
    
    // Handle localhost development
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return null;
    }
    
    // Handle production domains (e.g., meet.aikarau.com)
    const parts = hostname.split('.');
    
    // For aikarau.com domain structure
    // meet.aikarau.com -> ['meet', 'aikarau', 'com'] -> subdomain = 'meet'
    // aikarau.com -> ['aikarau', 'com'] -> no subdomain
    
    // Check if this is our main domain (aikarau.com)
    if (parts.includes('aikarau')) {
      const aikarauIndex = parts.indexOf('aikarau');
      if (aikarauIndex > 0) {
        return parts[0].toLowerCase(); // Return the subdomain
      }
      return null; // Main domain, no subdomain
    }
    
    // For preview/staging environments (e.g., medkonnect.preview.emergentagent.com)
    // These don't have subdomains in the traditional sense
    return null;
  };
  
  const subdomain = getSubdomain();
  
  // Route based on subdomain
  // meet.aikarau.com -> AI KARAU Meeting Portal
  if (subdomain === 'meet') {
    return <KarauMeetPortal />;
  }
  
  // medmatch.aikarau.com, careers.aikarau.com, jobs.aikarau.com -> MedMatch Jobs (skip portal selector)
  if (subdomain === 'medmatch' || subdomain === 'careers' || subdomain === 'jobs') {
    // For job portal subdomains, we skip the Portal Selector and go directly to login/app
    return <AppContent skipPortalSelector={true} />;
  }
  
  // Main domain (aikarau.com) or unknown subdomain -> Show Portal Selector first
  return <AppContent />;
};

// Main App Component with Theme Provider
function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <I18nProvider>
          <SubdomainRouter />
        </I18nProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
}

export default App;
