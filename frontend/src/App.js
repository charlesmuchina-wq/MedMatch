import { useState, useEffect, createContext, useContext } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, NavLink, useLocation, Navigate, useSearchParams } from "react-router-dom";
import axios from "axios";
import { Toaster, toast } from "sonner";
import { 
  Search, Briefcase, FileText, Bookmark, CheckSquare, 
  Menu, X, TrendingUp, Bell, PenTool, Target, Mic, Moon, Sun, Volume2, BarChart3, Users, Video, LogOut, Crown, DollarSign, MessageSquare, UserSearch, LayoutDashboard, Award
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
import { UpgradeBanner } from "@/components/PremiumGate";
import PremiumGate from "@/components/PremiumGate";
import OnboardingTour, { useOnboardingTour } from "@/components/OnboardingTour";
import InstallPrompt from "@/components/InstallPrompt";
import KarauDragonAI, { DragonButton } from "@/components/KarauDragonAI";
import GlobalLanguageSelector, { LanguageProvider } from "@/components/GlobalLanguageSelector";

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
  
  // Different navigation for recruiters vs job seekers
  const isRecruiter = user?.role === "recruiter";
  
  const jobSeekerLinks = [
    { path: "/", icon: TrendingUp, label: "Dashboard" },
    { path: "/resume", icon: FileText, label: "My Resume" },
    { path: "/resume-profiles", icon: Users, label: "Resume Profiles" },
    { path: "/skill-assessments", icon: Award, label: "Skill Tests" },
    { path: "/search", icon: Search, label: "Job Search" },
    { path: "/saved", icon: Bookmark, label: "Saved Jobs" },
    { path: "/applications", icon: CheckSquare, label: "Applications" },
    { path: "/interviews", icon: Video, label: "My Interviews" },
    { path: "/predictor", icon: Target, label: "Success Predictor" },
    { path: "/interview", icon: Mic, label: "Interview Prep" },
    { path: "/voice-coach", icon: Volume2, label: "Voice Coach" },
    { path: "/cover-letter", icon: PenTool, label: "Cover Letter" },
    { path: "/alerts", icon: Bell, label: "Job Alerts" },
    { path: "/salary-insights", icon: DollarSign, label: "Salary Insights" },
    { path: "/analytics", icon: BarChart3, label: "Analytics" },
    { path: "/companies", icon: Briefcase, label: "Companies" },
    { path: "/messages", icon: MessageSquare, label: "Messages" },
    { path: "/membership", icon: Crown, label: "Membership" },
  ];
  
  const recruiterLinks = [
    { path: "/recruiter/dashboard", icon: LayoutDashboard, label: "Dashboard" },
    { path: "/recruiter/jobs", icon: Briefcase, label: "My Job Postings" },
    { path: "/interviews", icon: Video, label: "Interviews" },
    { path: "/recruiter/candidates", icon: UserSearch, label: "Search Candidates" },
    { path: "/companies", icon: Briefcase, label: "Companies" },
    { path: "/messages", icon: MessageSquare, label: "Messages" },
    { path: "/membership", icon: Crown, label: "Membership" },
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
      `}>
        <div className={`flex items-center justify-between p-6 border-b ${isDark ? 'border-batik-dark-grey' : 'border-slate-100'}`}>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-batik-black to-batik-charcoal rounded-lg flex items-center justify-center border-2 border-turquoise shadow-lg shadow-turquoise/20">
              <Briefcase className="w-5 h-5 text-turquoise" />
            </div>
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
        
        <nav className="p-4 space-y-1">
          {links.map(({ path, icon: Icon, label }) => (
            <NavLink
              key={path}
              to={path}
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''} ${isDark ? 'dark' : ''}`}
              onClick={() => setIsOpen(false)}
              data-testid={`nav-${label.toLowerCase().replace(' ', '-')}`}
            >
              <Icon className="w-5 h-5" />
              <span>{label}</span>
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
  const { isDark } = useTheme();
  const location = useLocation();
  
  // Onboarding tour state
  const { showTour, completeTour } = useOnboardingTour();

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
        if (resumeRes.data) setResume(resumeRes.data);
        setSavedJobs(savedRes.data);
        setApplications(appsRes.data);
        setMembership(membershipRes.data);
      } catch (e) {
        console.error("Failed to fetch data:", e);
      }
    };
    fetchData();
  }, [user]);

  const handleAuthSuccess = (userData) => {
    setUser(userData);
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
      toast.success("Job saved!");
    } catch (e) {
      if (e.response?.status === 400) toast.info("Job already saved");
      else toast.error("Failed to save job");
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

  const navigate = (path) => { window.location.href = path; };

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
          </Routes>
        </main>
      </div>

      {/* Onboarding Tour for first-time users */}
      {showTour && user && <OnboardingTour onComplete={completeTour} user={user} />}

      {/* PWA Install Prompt */}
      <InstallPrompt />

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
        <AppContent />
      </ThemeProvider>
    </BrowserRouter>
  );
}

export default App;
