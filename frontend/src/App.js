import { useState, useEffect, useCallback } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, NavLink, useLocation } from "react-router-dom";
import axios from "axios";
import { Toaster, toast } from "sonner";
import { 
  Search, Briefcase, FileText, Bookmark, CheckSquare, 
  Menu, X, Upload, ExternalLink, MapPin, Building2,
  TrendingUp, Clock, ChevronRight, Trash2, Filter,
  Bell, Mail, Globe, Calendar, ShieldCheck, Award,
  CheckCircle, Code, HeartPulse, Sparkles, Send, Loader2,
  Settings, FileSearch, PenTool, Copy, Download, History
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useDropzone } from "react-dropzone";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Icon mapping for presets
const PresetIcons = {
  "shield-check": ShieldCheck,
  "award": Award,
  "check-circle": CheckCircle,
  "file-text": FileText,
  "code": Code,
  "heart-pulse": HeartPulse,
  "settings": Settings,
  "search": FileSearch
};

// Sidebar Component
const Sidebar = ({ isOpen, setIsOpen }) => {
  const location = useLocation();
  
  const links = [
    { path: "/", icon: TrendingUp, label: "Dashboard" },
    { path: "/resume", icon: FileText, label: "My Resume" },
    { path: "/search", icon: Search, label: "Job Search" },
    { path: "/saved", icon: Bookmark, label: "Saved Jobs" },
    { path: "/applications", icon: CheckSquare, label: "Applications" },
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

// Match Score Ring Component
const MatchScoreRing = ({ score }) => {
  const radius = 24;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  
  const getColor = (s) => {
    if (s >= 80) return '#10B981';
    if (s >= 60) return '#0EA5E9';
    if (s >= 40) return '#F59E0B';
    return '#F43F5E';
  };

  return (
    <div className="match-ring">
      <svg width="60" height="60">
        <circle cx="30" cy="30" r={radius} fill="none" stroke="#E2E8F0" strokeWidth="4" />
        <circle
          cx="30" cy="30" r={radius} fill="none"
          stroke={getColor(score)} strokeWidth="4"
          strokeDasharray={circumference} strokeDashoffset={offset}
          strokeLinecap="round"
        />
      </svg>
      <span className="match-ring-text" style={{ color: getColor(score) }}>
        {score}%
      </span>
    </div>
  );
};

// Job Card Component
const JobCard = ({ job, onSave, onApply, onAnalyze, isSaved, showActions = true }) => {
  const [analyzing, setAnalyzing] = useState(false);
  const [matchData, setMatchData] = useState(job.match_score ? { 
    match_score: job.match_score, 
    analysis: job.match_analysis 
  } : null);

  const handleAnalyze = async () => {
    setAnalyzing(true);
    try {
      const result = await onAnalyze(job);
      setMatchData(result);
    } catch (e) {
      toast.error("Failed to analyze job match");
    }
    setAnalyzing(false);
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    try {
      const date = new Date(dateStr);
      const now = new Date();
      const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));
      if (diffDays === 0) return 'Today';
      if (diffDays === 1) return 'Yesterday';
      if (diffDays < 7) return `${diffDays} days ago`;
      if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
      return date.toLocaleDateString();
    } catch {
      return '';
    }
  };

  return (
    <Card className="job-card" data-testid={`job-card-${job.id}`}>
      <CardContent className="p-6">
        <div className="flex gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-4 mb-3">
              <div>
                <h3 className="font-semibold text-slate-900 text-lg leading-tight" style={{ fontFamily: 'IBM Plex Sans' }}>
                  {job.title}
                </h3>
                <div className="flex items-center gap-2 mt-1 text-slate-600">
                  <Building2 className="w-4 h-4" />
                  <span className="text-sm">{job.company}</span>
                </div>
              </div>
              {matchData && <MatchScoreRing score={matchData.match_score} />}
              {!matchData && job.relevance_score > 0 && (
                <div className="flex flex-col items-center">
                  <span className="text-xs text-slate-400">Relevance</span>
                  <span className={`text-lg font-semibold ${
                    job.relevance_score >= 50 ? 'text-emerald-500' : 
                    job.relevance_score >= 30 ? 'text-sky-500' : 
                    job.relevance_score >= 10 ? 'text-amber-500' : 'text-slate-400'
                  }`}>
                    {Math.min(job.relevance_score, 100)}%
                  </span>
                </div>
              )}
            </div>
            
            <div className="flex flex-wrap items-center gap-3 text-sm text-slate-500 mb-3">
              <span className="flex items-center gap-1">
                <MapPin className="w-4 h-4" />
                {job.location}
              </span>
              {job.posted_at && (
                <span className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  {formatDate(job.posted_at)}
                </span>
              )}
              {job.salary && (
                <span className="text-emerald-600 font-medium">{job.salary}</span>
              )}
              <Badge variant="secondary" className="text-xs">
                {job.source}
              </Badge>
            </div>
            
            {job.tags?.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-3">
                {job.tags.slice(0, 5).map((tag, i) => (
                  <span key={i} className="tag-badge">{tag}</span>
                ))}
              </div>
            )}
            
            {matchData?.analysis && (
              <p className="text-sm text-slate-600 bg-slate-50 p-3 rounded-lg mb-3">
                {matchData.analysis}
              </p>
            )}
            
            {showActions && (
              <div className="flex flex-wrap items-center gap-2 pt-2">
                {!matchData && (
                  <Button 
                    variant="outline" size="sm"
                    onClick={handleAnalyze}
                    disabled={analyzing}
                    data-testid={`analyze-btn-${job.id}`}
                  >
                    {analyzing ? <><Loader2 className="w-4 h-4 mr-1 animate-spin" /> Analyzing...</> : "Analyze Match"}
                  </Button>
                )}
                <Button 
                  variant={isSaved ? "secondary" : "outline"}
                  size="sm"
                  onClick={() => onSave(job)}
                  data-testid={`save-btn-${job.id}`}
                >
                  <Bookmark className={`w-4 h-4 mr-1 ${isSaved ? 'fill-current' : ''}`} />
                  {isSaved ? "Saved" : "Save"}
                </Button>
                <Button size="sm" onClick={() => onApply(job)} data-testid={`apply-btn-${job.id}`}>
                  Apply <ChevronRight className="w-4 h-4 ml-1" />
                </Button>
                {job.url && (
                  <a href={job.url} target="_blank" rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-sm text-sky-600 hover:text-sky-700">
                    View Original <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// Dashboard Page
const Dashboard = ({ resume, savedJobs, applications, onNavigate }) => {
  const stats = [
    { label: "Saved Jobs", value: savedJobs.length, icon: Bookmark, color: "text-sky-500" },
    { label: "Applications", value: applications.length, icon: CheckSquare, color: "text-emerald-500" },
    { label: "Interviews", value: applications.filter(a => a.status === "Interview").length, icon: Clock, color: "text-amber-500" },
    { label: "Skills", value: resume?.skills?.length || 0, icon: TrendingUp, color: "text-violet-500" },
  ];

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-7xl mx-auto animate-fade-in" data-testid="dashboard">
      <div className="mb-8">
        <h1 className="text-3xl md:text-4xl font-semibold text-slate-900 tracking-tight" style={{ fontFamily: 'IBM Plex Sans' }}>
          {resume?.full_name ? `Welcome, ${resume.full_name.split(' ')[0]}` : 'Welcome to MedMatch'}
        </h1>
        <p className="text-slate-500 mt-2">
          {resume ? 'Your personalized remote job dashboard' : 'Upload your resume to get started'}
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {stats.map(({ label, value, icon: Icon, color }) => (
          <Card key={label} className="border-slate-200">
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-500">{label}</p>
                  <p className="text-2xl font-semibold text-slate-900 mt-1">{value}</p>
                </div>
                <div className={`p-3 rounded-lg bg-slate-50 ${color}`}>
                  <Icon className="w-5 h-5" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {!resume ? (
        <Card className="border-dashed border-2 border-slate-300">
          <CardContent className="p-12 text-center">
            <Upload className="w-12 h-12 text-slate-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-slate-900 mb-2">Upload Your Resume</h3>
            <p className="text-slate-500 mb-4">Get AI-powered job matches based on your skills and experience</p>
            <Button onClick={() => onNavigate('/resume')} data-testid="upload-resume-cta">
              Upload Resume
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg" style={{ fontFamily: 'IBM Plex Sans' }}>Your Skills</CardTitle>
              <CardDescription>Extracted from your resume</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {resume.skills?.slice(0, 12).map((skill, i) => (
                  <Badge key={i} variant="secondary" className="bg-slate-100">{skill}</Badge>
                ))}
                {resume.skills?.length > 12 && (
                  <Badge variant="outline">+{resume.skills.length - 12} more</Badge>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg" style={{ fontFamily: 'IBM Plex Sans' }}>Recent Applications</CardTitle>
              <CardDescription>Track your job applications</CardDescription>
            </CardHeader>
            <CardContent>
              {applications.length === 0 ? (
                <p className="text-slate-500 text-sm">No applications yet</p>
              ) : (
                <div className="space-y-3">
                  {applications.slice(0, 3).map((app) => (
                    <div key={app.id} className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-slate-900 text-sm">{app.job.title}</p>
                        <p className="text-xs text-slate-500">{app.job.company}</p>
                      </div>
                      <Badge className={`status-${app.status.toLowerCase()}`}>{app.status}</Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

// Resume Page
const ResumePage = ({ resume, setResume }) => {
  const [uploading, setUploading] = useState(false);

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;
    
    if (!file.name.endsWith('.pdf')) {
      toast.error("Please upload a PDF file");
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API}/resume/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResume(response.data);
      toast.success("Resume uploaded and parsed successfully!");
    } catch (e) {
      toast.error(e.response?.data?.detail || "Failed to upload resume");
    }
    setUploading(false);
  }, [setResume]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1
  });

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-4xl mx-auto animate-fade-in" data-testid="resume-page">
      <h1 className="text-3xl font-semibold text-slate-900 tracking-tight mb-8" style={{ fontFamily: 'IBM Plex Sans' }}>
        My Resume
      </h1>

      <Card className="mb-8">
        <CardContent className="p-6">
          <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`} data-testid="resume-dropzone">
            <input {...getInputProps()} data-testid="resume-input" />
            <Upload className="w-10 h-10 text-slate-400 mx-auto mb-3" />
            {uploading ? (
              <p className="text-slate-600">Processing your resume...</p>
            ) : (
              <>
                <p className="text-slate-700 font-medium">
                  {isDragActive ? "Drop your resume here" : "Drag & drop your resume"}
                </p>
                <p className="text-slate-500 text-sm mt-1">or click to browse (PDF only)</p>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {resume && (
        <div className="space-y-6">
          <Card>
            <CardHeader><CardTitle style={{ fontFamily: 'IBM Plex Sans' }}>Profile</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm text-slate-500">Full Name</label>
                  <p className="font-medium text-slate-900">{resume.full_name || '-'}</p>
                </div>
                <div>
                  <label className="text-sm text-slate-500">Email</label>
                  <p className="font-medium text-slate-900">{resume.email || '-'}</p>
                </div>
              </div>
              {resume.summary && (
                <div>
                  <label className="text-sm text-slate-500">Summary</label>
                  <p className="text-slate-700 mt-1">{resume.summary}</p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle style={{ fontFamily: 'IBM Plex Sans' }}>Skills</CardTitle>
              <CardDescription>These skills will be used for job matching</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {resume.skills?.map((skill, i) => (
                  <Badge key={i} variant="secondary" className="bg-slate-100">{skill}</Badge>
                ))}
              </div>
            </CardContent>
          </Card>

          {resume.experience?.length > 0 && (
            <Card>
              <CardHeader><CardTitle style={{ fontFamily: 'IBM Plex Sans' }}>Experience</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                {resume.experience.map((exp, i) => (
                  <div key={i} className="border-l-2 border-slate-200 pl-4">
                    <h4 className="font-medium text-slate-900">{exp.title}</h4>
                    <p className="text-sm text-slate-600">{exp.company} • {exp.duration}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
};

// Job Search Page with filters
const JobSearchPage = ({ savedJobs, onSave, onApply, onAnalyze }) => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState("");
  const [source, setSource] = useState("all");
  const [location, setLocation] = useState("any");
  const [days, setDays] = useState("0");
  const [presets, setPresets] = useState({ presets: [], locations: [], quality_terms: [] });
  const [aiSearching, setAiSearching] = useState(false);
  const [deepSearching, setDeepSearching] = useState(false);
  const [searchStats, setSearchStats] = useState(null);

  useEffect(() => {
    // Fetch presets
    axios.get(`${API}/jobs/presets`).then(res => setPresets(res.data)).catch(() => {});
    searchJobs();
    // eslint-disable-next-line
  }, []);

  const searchJobs = async (searchQuery = query) => {
    setLoading(true);
    setSearchStats(null);
    try {
      const response = await axios.get(`${API}/jobs/search`, {
        params: { query: searchQuery, source, location: location === "any" ? "" : location, days: parseInt(days) }
      });
      setJobs(response.data);
    } catch (e) {
      toast.error("Failed to fetch jobs");
    }
    setLoading(false);
  };

  const deepSearch = async () => {
    setDeepSearching(true);
    setSearchStats(null);
    try {
      const response = await axios.post(`${API}/jobs/deep-search`, { use_ai: true });
      setJobs(response.data.jobs || []);
      setSearchStats({
        total: response.data.total_found,
        queries: response.data.queries_used,
        strategy: response.data.search_strategy
      });
      toast.success(`AI Deep Search found ${response.data.total_found} relevant jobs!`);
    } catch (e) {
      toast.error("Deep search failed");
    }
    setDeepSearching(false);
  };

  const handlePresetClick = (presetQuery) => {
    setQuery(presetQuery);
    searchJobs(presetQuery);
  };

  const savedJobIds = savedJobs.map(s => s.job.id);

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-6xl mx-auto animate-fade-in" data-testid="job-search-page">
      <h1 className="text-3xl font-semibold text-slate-900 tracking-tight mb-6" style={{ fontFamily: 'IBM Plex Sans' }}>
        Find Remote Jobs
      </h1>

      {/* Quick Search Presets */}
      <div className="mb-6">
        <p className="text-sm text-slate-500 mb-3">Quick Search:</p>
        <div className="flex flex-wrap gap-2">
          {presets.presets?.map(preset => {
            const Icon = PresetIcons[preset.icon] || Search;
            return (
              <Button
                key={preset.id}
                variant="outline"
                size="sm"
                onClick={() => handlePresetClick(preset.query)}
                className="gap-2"
                data-testid={`preset-${preset.id}`}
              >
                <Icon className="w-4 h-4" />
                {preset.name}
              </Button>
            );
          })}
        </div>
      </div>

      {/* Search Bar & Filters */}
      <Card className="mb-6">
        <CardContent className="p-4">
          <div className="flex flex-col gap-4">
            {/* Search input row */}
            <div className="flex flex-col md:flex-row gap-3">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <Input
                  placeholder="Search jobs by title, company, or skills..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && searchJobs()}
                  className="pl-10"
                  data-testid="job-search-input"
                />
              </div>
              <Button onClick={() => searchJobs()} disabled={loading} data-testid="search-btn">
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Search"}
              </Button>
              <Button 
                variant="default" 
                onClick={deepSearch} 
                disabled={deepSearching}
                className="bg-gradient-to-r from-sky-500 to-emerald-500 hover:from-sky-600 hover:to-emerald-600"
                data-testid="deep-search-btn"
              >
                <Sparkles className="w-4 h-4 mr-2" />
                {deepSearching ? "Deep Searching..." : "AI Deep Search"}
              </Button>
            </div>

            {/* Filters row */}
            <div className="flex flex-wrap gap-3">
              <Select value={source} onValueChange={setSource}>
                <SelectTrigger className="w-36" data-testid="source-select">
                  <Globe className="w-4 h-4 mr-2" />
                  <SelectValue placeholder="Source" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Sources</SelectItem>
                  <SelectItem value="google">Google CSE</SelectItem>
                  <SelectItem value="remoteok">RemoteOK</SelectItem>
                  <SelectItem value="remotive">Remotive</SelectItem>
                  <SelectItem value="jobicy">Jobicy</SelectItem>
                  <SelectItem value="arbeitnow">Arbeitnow</SelectItem>
                  <SelectItem value="himalayas">Himalayas</SelectItem>
                </SelectContent>
              </Select>

              <Select value={location} onValueChange={setLocation}>
                <SelectTrigger className="w-36" data-testid="location-select">
                  <MapPin className="w-4 h-4 mr-2" />
                  <SelectValue placeholder="Location" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="any">Any Location</SelectItem>
                  {presets.locations?.map(loc => (
                    <SelectItem key={loc} value={loc.toLowerCase()}>{loc}</SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Select value={days} onValueChange={setDays}>
                <SelectTrigger className="w-36" data-testid="date-select">
                  <Calendar className="w-4 h-4 mr-2" />
                  <SelectValue placeholder="Posted" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="0">Any Time</SelectItem>
                  <SelectItem value="1">Last 24 hours</SelectItem>
                  <SelectItem value="3">Last 3 days</SelectItem>
                  <SelectItem value="7">Last 7 days</SelectItem>
                  <SelectItem value="14">Last 2 weeks</SelectItem>
                  <SelectItem value="30">Last 30 days</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Advanced Filters - TheirStack inspired */}
            <div className="pt-3 border-t border-slate-100">
              <p className="text-xs text-slate-400 mb-2 flex items-center gap-1">
                <Filter className="w-3 h-3" /> Advanced Filters (Industries & Technologies)
              </p>
              <div className="flex flex-wrap gap-2">
                {presets.industries?.slice(0, 5).map(industry => (
                  <Badge 
                    key={industry} 
                    variant="outline" 
                    className="cursor-pointer hover:bg-slate-100 text-xs"
                    onClick={() => { setQuery(industry); searchJobs(industry); }}
                  >
                    {industry}
                  </Badge>
                ))}
                {presets.technologies?.slice(0, 4).map(tech => (
                  <Badge 
                    key={tech} 
                    variant="secondary" 
                    className="cursor-pointer hover:bg-slate-200 text-xs"
                    onClick={() => { setQuery(tech); searchJobs(tech); }}
                  >
                    {tech}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      <div className="space-y-4">
        {/* Search Stats from Deep Search */}
        {searchStats && (
          <Card className="bg-gradient-to-r from-sky-50 to-emerald-50 border-sky-200">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="w-5 h-5 text-sky-500" />
                <span className="font-medium text-slate-900">AI Deep Search Results</span>
                {searchStats.jobspy_enabled && (
                  <Badge variant="outline" className="text-xs bg-emerald-50 text-emerald-700 border-emerald-200">
                    JobSpy
                  </Badge>
                )}
                {searchStats.google_cse_enabled && (
                  <Badge variant="outline" className="text-xs bg-sky-50 text-sky-700 border-sky-200">
                    Google CSE
                  </Badge>
                )}
              </div>
              <p className="text-sm text-slate-600 mb-2">
                Found <strong>{searchStats.total}</strong> relevant jobs across <strong>{searchStats.sources_searched?.length || 9}</strong> sources
              </p>
              <div className="flex flex-wrap gap-1 mb-2">
                {searchStats.sources_searched?.map((source, i) => (
                  <Badge key={i} variant="outline" className="text-xs">{source}</Badge>
                ))}
              </div>
              <p className="text-xs text-slate-400">Searched: {searchStats.queries?.slice(0, 4).join(', ')}</p>
            </CardContent>
          </Card>
        )}
        
        {loading || deepSearching ? (
          <div className="space-y-4">
            <div className="flex items-center gap-3 p-4 bg-slate-50 rounded-lg">
              <Loader2 className="w-5 h-5 animate-spin text-sky-500" />
              <span className="text-slate-600">
                {deepSearching ? "AI is searching LinkedIn, Indeed, Glassdoor, Google, ZipRecruiter, and 5 more job boards..." : "Searching..."}
              </span>
            </div>
            {[1, 2, 3].map(i => (
              <Card key={i}>
                <CardContent className="p-6">
                  <div className="skeleton h-6 w-48 rounded mb-3" />
                  <div className="skeleton h-4 w-32 rounded mb-4" />
                  <div className="skeleton h-4 w-full rounded" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : jobs.length === 0 ? (
          <div className="empty-state">
            <Search className="w-12 h-12 text-slate-300 mb-4" />
            <h3 className="text-lg font-medium text-slate-700">No jobs found</h3>
            <p className="text-slate-500 mb-4">Try AI Deep Search to find Quality & Medical Device jobs</p>
            <Button onClick={deepSearch} className="bg-gradient-to-r from-sky-500 to-emerald-500">
              <Sparkles className="w-4 h-4 mr-2" /> Run AI Deep Search
            </Button>
          </div>
        ) : (
          <>
            <p className="text-sm text-slate-500 mb-4">{jobs.length} jobs found</p>
            {jobs.map(job => (
              <JobCard
                key={job.id}
                job={job}
                onSave={onSave}
                onApply={onApply}
                onAnalyze={onAnalyze}
                isSaved={savedJobIds.includes(job.id)}
              />
            ))}
          </>
        )}
      </div>
    </div>
  );
};

// Saved Jobs Page
const SavedJobsPage = ({ savedJobs, onRemove, onApply, onAnalyze }) => {
  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-6xl mx-auto animate-fade-in" data-testid="saved-jobs-page">
      <h1 className="text-3xl font-semibold text-slate-900 tracking-tight mb-8" style={{ fontFamily: 'IBM Plex Sans' }}>
        Saved Jobs
      </h1>

      {savedJobs.length === 0 ? (
        <div className="empty-state">
          <Bookmark className="w-12 h-12 text-slate-300 mb-4" />
          <h3 className="text-lg font-medium text-slate-700">No saved jobs</h3>
          <p className="text-slate-500">Save jobs while searching to review them later</p>
        </div>
      ) : (
        <div className="space-y-4">
          {savedJobs.map(saved => (
            <div key={saved.id} className="relative">
              <JobCard job={saved.job} onSave={() => {}} onApply={onApply} onAnalyze={onAnalyze} isSaved={true} />
              <Button
                variant="ghost" size="sm"
                className="absolute top-4 right-4 text-slate-400 hover:text-rose-500"
                onClick={() => onRemove(saved.id)}
                data-testid={`remove-saved-${saved.id}`}
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Applications Page
const ApplicationsPage = ({ applications, onUpdateStatus, onDelete }) => {
  const [filter, setFilter] = useState("all");
  const filteredApps = filter === "all" ? applications : applications.filter(a => a.status === filter);
  const statusOptions = ["Applied", "Interview", "Offer", "Rejected"];

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-6xl mx-auto animate-fade-in" data-testid="applications-page">
      <h1 className="text-3xl font-semibold text-slate-900 tracking-tight mb-8" style={{ fontFamily: 'IBM Plex Sans' }}>
        Applications
      </h1>

      <Tabs value={filter} onValueChange={setFilter} className="mb-6">
        <TabsList>
          <TabsTrigger value="all" data-testid="filter-all">All ({applications.length})</TabsTrigger>
          {statusOptions.map(status => (
            <TabsTrigger key={status} value={status} data-testid={`filter-${status.toLowerCase()}`}>
              {status} ({applications.filter(a => a.status === status).length})
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>

      {filteredApps.length === 0 ? (
        <div className="empty-state">
          <CheckSquare className="w-12 h-12 text-slate-300 mb-4" />
          <h3 className="text-lg font-medium text-slate-700">No applications</h3>
          <p className="text-slate-500">Start applying to jobs to track them here</p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredApps.map(app => (
            <Card key={app.id} data-testid={`application-${app.id}`}>
              <CardContent className="p-6">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="flex-1">
                    <h3 className="font-semibold text-slate-900" style={{ fontFamily: 'IBM Plex Sans' }}>
                      {app.job.title}
                    </h3>
                    <p className="text-slate-600 text-sm">{app.job.company}</p>
                    <p className="text-slate-500 text-xs mt-1">
                      Applied {new Date(app.applied_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <Select value={app.status} onValueChange={(value) => onUpdateStatus(app.id, value)}>
                      <SelectTrigger className="w-32" data-testid={`status-select-${app.id}`}>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {statusOptions.map(status => (
                          <SelectItem key={status} value={status}>{status}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Button 
                      variant="ghost" size="sm"
                      onClick={() => onDelete(app.id)}
                      className="text-slate-400 hover:text-rose-500"
                      data-testid={`delete-app-${app.id}`}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

// Job Alerts Page with Daily Digest
const JobAlertsPage = ({ resume }) => {
  const [sending, setSending] = useState(false);
  const [sendingDigest, setSendingDigest] = useState(false);
  const [email, setEmail] = useState("");
  const [digestHistory, setDigestHistory] = useState([]);

  useEffect(() => {
    if (resume?.email) setEmail(resume.email);
    // Load digest history
    if (resume?.email) {
      axios.get(`${API}/digest/history?email=${resume.email}`).then(res => {
        setDigestHistory(res.data.history || []);
      }).catch(() => {});
    }
  }, [resume]);

  const sendAlertNow = async () => {
    if (!email) {
      toast.error("Please enter an email address");
      return;
    }
    setSending(true);
    try {
      const response = await axios.post(`${API}/alerts/send-now`, { email });
      toast.success(response.data.message);
    } catch (e) {
      toast.error("Failed to send alert");
    }
    setSending(false);
  };

  const sendDailyDigest = async () => {
    if (!email) {
      toast.error("Please enter an email address");
      return;
    }
    setSendingDigest(true);
    try {
      const response = await axios.post(`${API}/digest/send-daily`, { email });
      toast.success(`${response.data.message} (${response.data.jobs_count} new jobs)`);
      // Refresh history
      const historyRes = await axios.get(`${API}/digest/history?email=${email}`);
      setDigestHistory(historyRes.data.history || []);
    } catch (e) {
      toast.error("Failed to send daily digest");
    }
    setSendingDigest(false);
  };

  const clearHistory = async () => {
    try {
      await axios.delete(`${API}/digest/history/${email}`);
      setDigestHistory([]);
      toast.success("Digest history cleared - you'll receive all jobs again");
    } catch (e) {
      toast.error("Failed to clear history");
    }
  };

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-4xl mx-auto animate-fade-in" data-testid="alerts-page">
      <h1 className="text-3xl font-semibold text-slate-900 tracking-tight mb-8" style={{ fontFamily: 'IBM Plex Sans' }}>
        Job Alerts & Daily Digest
      </h1>

      {/* Daily Digest Card */}
      <Card className="mb-6 border-2 border-sky-200 bg-gradient-to-r from-sky-50 to-emerald-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2" style={{ fontFamily: 'IBM Plex Sans' }}>
            <Calendar className="w-5 h-5 text-sky-600" />
            Daily Digest (Last 24 Hours)
          </CardTitle>
          <CardDescription>
            Get only NEW jobs posted in the last 24 hours. No duplicate emails for the same jobs!
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-3 mb-4">
            <Input
              type="email"
              placeholder="Enter email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="flex-1 bg-white"
              data-testid="digest-email-input"
            />
            <Button 
              onClick={sendDailyDigest} 
              disabled={sendingDigest}
              className="bg-gradient-to-r from-sky-500 to-emerald-500 hover:from-sky-600 hover:to-emerald-600"
              data-testid="send-digest-btn"
            >
              {sendingDigest ? (
                <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Sending...</>
              ) : (
                <><Mail className="w-4 h-4 mr-2" /> Send Daily Digest</>
              )}
            </Button>
          </div>
          <div className="flex items-center gap-4 text-sm">
            <span className="text-slate-600">
              {digestHistory.length > 0 ? `${digestHistory.length} jobs already sent` : 'No jobs sent yet'}
            </span>
            {digestHistory.length > 0 && (
              <Button variant="ghost" size="sm" onClick={clearHistory} className="text-slate-500 hover:text-rose-500">
                <Trash2 className="w-3 h-3 mr-1" /> Clear History
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Regular Alert Card */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2" style={{ fontFamily: 'IBM Plex Sans' }}>
            <Send className="w-5 h-5" />
            Quick Job Alert
          </CardTitle>
          <CardDescription>
            Send all matching jobs (may include previously sent jobs)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={sendAlertNow} disabled={sending} variant="outline" data-testid="send-alert-btn">
            {sending ? (
              <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Sending...</>
            ) : (
              <><Send className="w-4 h-4 mr-2" /> Send Alert Now</>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* How it works */}
      <Card>
        <CardHeader>
          <CardTitle style={{ fontFamily: 'IBM Plex Sans' }}>How Daily Digest Works</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-sky-100 flex items-center justify-center text-sky-600 font-medium">1</div>
            <div>
              <h4 className="font-medium text-slate-900">Only jobs from last 24 hours</h4>
              <p className="text-sm text-slate-500">Filters out older postings so you only see fresh opportunities</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-sky-100 flex items-center justify-center text-sky-600 font-medium">2</div>
            <div>
              <h4 className="font-medium text-slate-900">No duplicate emails</h4>
              <p className="text-sm text-slate-500">We track which jobs were sent - you'll never get the same job twice</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-sky-100 flex items-center justify-center text-sky-600 font-medium">3</div>
            <div>
              <h4 className="font-medium text-slate-900">AI-powered matching</h4>
              <p className="text-sm text-slate-500">Searches Indeed, LinkedIn, Glassdoor, ZipRecruiter + 5 more sources</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Cover Letter Generator Page
const CoverLetterPage = ({ resume }) => {
  const [jobTitle, setJobTitle] = useState("");
  const [company, setCompany] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [generating, setGenerating] = useState(false);
  const [coverLetter, setCoverLetter] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    // Load cover letter history
    axios.get(`${API}/cover-letter/history`).then(res => {
      setHistory(res.data || []);
    }).catch(() => {});
  }, []);

  const generateCoverLetter = async () => {
    if (!jobTitle || !company || !jobDescription) {
      toast.error("Please fill in all fields");
      return;
    }
    if (!resume) {
      toast.error("Please upload your resume first");
      return;
    }

    setGenerating(true);
    try {
      const response = await axios.post(`${API}/cover-letter/generate`, {
        job_title: jobTitle,
        company: company,
        job_description: jobDescription
      });
      setCoverLetter(response.data);
      toast.success("Cover letter generated!");
      // Refresh history
      const historyRes = await axios.get(`${API}/cover-letter/history`);
      setHistory(historyRes.data || []);
    } catch (e) {
      toast.error(e.response?.data?.detail || "Failed to generate cover letter");
    }
    setGenerating(false);
  };

  const copyToClipboard = () => {
    if (coverLetter?.cover_letter) {
      navigator.clipboard.writeText(coverLetter.cover_letter);
      toast.success("Cover letter copied to clipboard!");
    }
  };

  const downloadAsTxt = () => {
    if (coverLetter?.cover_letter) {
      const blob = new Blob([coverLetter.cover_letter], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Cover_Letter_${company.replace(/\s+/g, '_')}.txt`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  const loadFromHistory = (item) => {
    setCoverLetter({
      cover_letter: item.cover_letter,
      key_matches: item.key_matches || [],
      transferable_skills: item.transferable_skills || []
    });
    setJobTitle(item.job_title);
    setCompany(item.company);
  };

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-5xl mx-auto animate-fade-in" data-testid="cover-letter-page">
      <h1 className="text-3xl font-semibold text-slate-900 tracking-tight mb-2" style={{ fontFamily: 'IBM Plex Sans' }}>
        AI Cover Letter Generator
      </h1>
      <p className="text-slate-500 mb-8">Generate personalized cover letters based on your resume and job requirements</p>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Input Section */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2" style={{ fontFamily: 'IBM Plex Sans' }}>
                <PenTool className="w-5 h-5" />
                Job Details
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium text-slate-700">Job Title *</label>
                <Input
                  placeholder="e.g., Supplier Quality Manager"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  className="mt-1"
                  data-testid="job-title-input"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Company *</label>
                <Input
                  placeholder="e.g., Medtronic"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  className="mt-1"
                  data-testid="company-input"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Job Description *</label>
                <Textarea
                  placeholder="Paste the job description here..."
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  className="mt-1 min-h-[200px]"
                  data-testid="job-description-input"
                />
              </div>
              <Button 
                onClick={generateCoverLetter} 
                disabled={generating || !resume}
                className="w-full bg-gradient-to-r from-sky-500 to-emerald-500 hover:from-sky-600 hover:to-emerald-600"
                data-testid="generate-btn"
              >
                {generating ? (
                  <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Generating...</>
                ) : (
                  <><Sparkles className="w-4 h-4 mr-2" /> Generate Cover Letter</>
                )}
              </Button>
              {!resume && (
                <p className="text-sm text-amber-600 text-center">Please upload your resume first</p>
              )}
            </CardContent>
          </Card>

          {/* History */}
          {history.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base" style={{ fontFamily: 'IBM Plex Sans' }}>
                  <History className="w-4 h-4" />
                  Recent Cover Letters
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {history.slice(0, 5).map((item, i) => (
                    <div 
                      key={i}
                      className="flex items-center justify-between p-2 rounded-lg hover:bg-slate-50 cursor-pointer"
                      onClick={() => loadFromHistory(item)}
                    >
                      <div>
                        <p className="text-sm font-medium text-slate-900">{item.job_title}</p>
                        <p className="text-xs text-slate-500">{item.company}</p>
                      </div>
                      <ChevronRight className="w-4 h-4 text-slate-400" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Output Section */}
        <div>
          <Card className="h-full">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle style={{ fontFamily: 'IBM Plex Sans' }}>Generated Cover Letter</CardTitle>
                {coverLetter && (
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={copyToClipboard}>
                      <Copy className="w-4 h-4 mr-1" /> Copy
                    </Button>
                    <Button variant="outline" size="sm" onClick={downloadAsTxt}>
                      <Download className="w-4 h-4 mr-1" /> Download
                    </Button>
                  </div>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {coverLetter ? (
                <div className="space-y-4">
                  {/* Cover Letter Text */}
                  <div className="bg-slate-50 rounded-lg p-4 max-h-[400px] overflow-y-auto">
                    <pre className="whitespace-pre-wrap text-sm text-slate-700 font-sans">
                      {coverLetter.cover_letter}
                    </pre>
                  </div>

                  {/* Key Matches */}
                  {coverLetter.key_matches?.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-slate-700 mb-2">Key Matches</h4>
                      <div className="flex flex-wrap gap-2">
                        {coverLetter.key_matches.map((match, i) => (
                          <Badge key={i} variant="secondary" className="bg-emerald-100 text-emerald-700">
                            {match}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Transferable Skills */}
                  {coverLetter.transferable_skills?.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-slate-700 mb-2">Transferable Skills</h4>
                      <div className="flex flex-wrap gap-2">
                        {coverLetter.transferable_skills.map((skill, i) => (
                          <Badge key={i} variant="secondary" className="bg-sky-100 text-sky-700">
                            {skill}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Suggestions */}
                  {coverLetter.suggestions?.length > 0 && (
                    <div className="bg-amber-50 rounded-lg p-3">
                      <h4 className="text-sm font-medium text-amber-800 mb-2">Tips to Strengthen Your Application</h4>
                      <ul className="text-sm text-amber-700 space-y-1">
                        {coverLetter.suggestions.map((tip, i) => (
                          <li key={i}>• {tip}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-12 text-slate-400">
                  <PenTool className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>Fill in the job details and click Generate to create your personalized cover letter</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

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
