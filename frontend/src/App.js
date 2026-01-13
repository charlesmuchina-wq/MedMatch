import { useState, useEffect } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, NavLink, useLocation } from "react-router-dom";
import axios from "axios";
import { Toaster, toast } from "sonner";
import { 
  Search, Briefcase, FileText, Bookmark, CheckSquare, 
  Menu, X, TrendingUp, Bell, PenTool, Target
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

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Sidebar Component
const Sidebar = ({ isOpen, setIsOpen }) => {
  const location = useLocation();
  
  const links = [
    { path: "/", icon: TrendingUp, label: "Dashboard" },
    { path: "/resume", icon: FileText, label: "My Resume" },
    { path: "/search", icon: Search, label: "Job Search" },
    { path: "/saved", icon: Bookmark, label: "Saved Jobs" },
    { path: "/applications", icon: CheckSquare, label: "Applications" },
    { path: "/predictor", icon: Target, label: "Success Predictor" },
    { path: "/cover-letter", icon: PenTool, label: "Cover Letter" },
    { path: "/alerts", icon: Bell, label: "Job Alerts" },
  ];

  return (
    <>
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/20 z-40 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
      
      <aside className={`
        fixed top-0 left-0 z-50 h-full w-64 bg-white border-r border-slate-200
        transform transition-transform duration-200 ease-out
        lg:translate-x-0 lg:static lg:z-auto
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex items-center justify-between p-6 border-b border-slate-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-slate-900 rounded-lg flex items-center justify-center">
              <Briefcase className="w-5 h-5 text-white" />
            </div>
            <span className="font-semibold text-lg text-slate-900" style={{ fontFamily: 'IBM Plex Sans' }}>
              MedMatch
            </span>
          </div>
          <button 
            className="lg:hidden p-2 hover:bg-slate-100 rounded-md"
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
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
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

// Header Component
const Header = ({ setIsOpen, resume }) => (
  <header className="glass-header sticky top-0 z-30 border-b border-slate-200/50 px-6 py-4">
    <div className="flex items-center justify-between">
      <button 
        className="lg:hidden p-2 hover:bg-slate-100 rounded-md"
        onClick={() => setIsOpen(true)}
        data-testid="mobile-menu-btn"
      >
        <Menu className="w-5 h-5" />
      </button>
      
      <div className="flex-1" />
      
      <div className="flex items-center gap-4">
        {resume && (
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-slate-100 rounded-full flex items-center justify-center">
              <span className="text-sm font-medium text-slate-700">
                {resume.full_name?.charAt(0) || 'U'}
              </span>
            </div>
            <span className="text-sm font-medium text-slate-700 hidden sm:block">
              {resume.full_name || 'Upload Resume'}
            </span>
          </div>
        )}
      </div>
    </div>
  </header>
);

// Apply Dialog Component
const ApplyDialog = ({ job, open, onClose, onConfirm }) => {
  const [notes, setNotes] = useState("");

  const handleConfirm = () => {
    onConfirm(job, notes);
    setNotes("");
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle style={{ fontFamily: 'IBM Plex Sans' }}>Track Application</DialogTitle>
          <DialogDescription>Add this job to your application tracker</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div>
            <p className="font-medium text-slate-900">{job?.title}</p>
            <p className="text-sm text-slate-600">{job?.company}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700">Notes (optional)</label>
            <Textarea
              placeholder="Add any notes about this application..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="mt-1"
              data-testid="apply-notes"
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button onClick={handleConfirm} data-testid="confirm-apply">Add to Applications</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

// Main App Component
function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [resume, setResume] = useState(null);
  const [savedJobs, setSavedJobs] = useState([]);
  const [applications, setApplications] = useState([]);
  const [applyDialogJob, setApplyDialogJob] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [resumeRes, savedRes, appsRes] = await Promise.all([
          axios.get(`${API}/resume`),
          axios.get(`${API}/jobs/saved`),
          axios.get(`${API}/applications`)
        ]);
        if (resumeRes.data) setResume(resumeRes.data);
        setSavedJobs(savedRes.data);
        setApplications(appsRes.data);
      } catch (e) {
        console.error("Failed to fetch data:", e);
      }
    };
    fetchData();
  }, []);

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

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-50 flex">
        <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />
        
        <div className="flex-1 flex flex-col min-w-0">
          <Header setIsOpen={setSidebarOpen} resume={resume} />
          
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<Dashboard resume={resume} savedJobs={savedJobs} applications={applications} onNavigate={navigate} />} />
              <Route path="/resume" element={<ResumePage resume={resume} setResume={setResume} />} />
              <Route path="/search" element={<JobSearchPage savedJobs={savedJobs} onSave={handleSaveJob} onApply={handleApply} onAnalyze={handleAnalyzeJob} />} />
              <Route path="/saved" element={<SavedJobsPage savedJobs={savedJobs} onRemove={handleRemoveSavedJob} onApply={handleApply} onAnalyze={handleAnalyzeJob} />} />
              <Route path="/applications" element={<ApplicationsPage applications={applications} onUpdateStatus={handleUpdateStatus} onDelete={handleDeleteApplication} />} />
              <Route path="/predictor" element={<SuccessPredictorPage resume={resume} />} />
              <Route path="/cover-letter" element={<CoverLetterPage resume={resume} />} />
              <Route path="/alerts" element={<JobAlertsPage resume={resume} />} />
            </Routes>
          </main>
        </div>

        <ApplyDialog job={applyDialogJob} open={!!applyDialogJob} onClose={() => setApplyDialogJob(null)} onConfirm={handleConfirmApply} />
        <Toaster position="bottom-right" richColors />
      </div>
    </BrowserRouter>
  );
}

export default App;
