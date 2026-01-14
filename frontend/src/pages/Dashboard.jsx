import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { 
  Bookmark, CheckSquare, Clock, TrendingUp, Upload, Search, 
  PenTool, Target, Mic, BarChart3, Sparkles, ArrowRight,
  Zap, FileText, Bell, Video
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import axios from "axios";

const API = process.env.REACT_APP_BACKEND_URL;

// Quick Actions based on user activity and state
const QuickActionsWidget = ({ resume, savedJobs, applications, user }) => {
  const navigate = useNavigate();
  const [recentActivity, setRecentActivity] = useState([]);

  // Determine most relevant quick actions based on user state
  const getQuickActions = () => {
    const actions = [];

    // If no resume, prioritize upload
    if (!resume) {
      actions.push({
        id: "upload_resume",
        label: "Upload Resume",
        description: "Get AI-powered job matches",
        icon: Upload,
        color: "from-violet-500 to-purple-600",
        path: "/resume",
        priority: 1
      });
    }

    // Always show job search
    actions.push({
      id: "search_jobs",
      label: "Search Jobs",
      description: "Find matching opportunities",
      icon: Search,
      color: "from-sky-500 to-blue-600",
      path: "/search",
      priority: 2
    });

    // If has saved jobs, show apply action
    if (savedJobs.length > 0) {
      actions.push({
        id: "review_saved",
        label: "Review Saved",
        description: `${savedJobs.length} jobs waiting`,
        icon: Bookmark,
        color: "from-amber-500 to-orange-600",
        path: "/saved",
        priority: 3
      });
    }

    // If has resume, show AI features
    if (resume) {
      actions.push({
        id: "cover_letter",
        label: "Write Cover Letter",
        description: "AI-powered generation",
        icon: PenTool,
        color: "from-emerald-500 to-teal-600",
        path: "/cover-letter",
        priority: 4
      });

      actions.push({
        id: "interview_prep",
        label: "Prepare Interview",
        description: "Practice with AI coach",
        icon: Mic,
        color: "from-pink-500 to-rose-600",
        path: "/interview",
        priority: 5
      });

      actions.push({
        id: "success_predictor",
        label: "Check Match Score",
        description: "AI callback predictor",
        icon: Target,
        color: "from-indigo-500 to-purple-600",
        path: "/predictor",
        priority: 6
      });
    }

    // If has applications, show analytics
    if (applications.length > 0) {
      actions.push({
        id: "view_analytics",
        label: "View Analytics",
        description: `${applications.length} applications tracked`,
        icon: BarChart3,
        color: "from-cyan-500 to-blue-600",
        path: "/analytics",
        priority: 7
      });
    }

    // Sort by priority and return top 4
    return actions.sort((a, b) => a.priority - b.priority).slice(0, 4);
  };

  const quickActions = getQuickActions();

  return (
    <Card className="mb-6">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-amber-500" />
            <CardTitle className="text-lg" style={{ fontFamily: 'IBM Plex Sans' }}>Quick Actions</CardTitle>
          </div>
          <Badge variant="outline" className="text-xs">
            <Sparkles className="w-3 h-3 mr-1" /> AI Powered
          </Badge>
        </div>
        <CardDescription>Recommended next steps based on your activity</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {quickActions.map((action) => (
            <button
              key={action.id}
              onClick={() => navigate(action.path)}
              className="group relative p-4 rounded-xl border border-slate-200 dark:border-slate-700 hover:border-transparent hover:shadow-lg transition-all duration-200 text-left overflow-hidden"
              data-testid={`quick-action-${action.id}`}
            >
              {/* Gradient background on hover */}
              <div className={`absolute inset-0 bg-gradient-to-br ${action.color} opacity-0 group-hover:opacity-10 transition-opacity`} />
              
              <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${action.color} flex items-center justify-center mb-3`}>
                <action.icon className="w-5 h-5 text-white" />
              </div>
              
              <h4 className="font-medium text-slate-900 dark:text-slate-100 text-sm mb-1">
                {action.label}
              </h4>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {action.description}
              </p>
              
              <ArrowRight className="absolute bottom-4 right-4 w-4 h-4 text-slate-300 dark:text-slate-600 group-hover:text-slate-500 dark:group-hover:text-slate-400 transition-colors" />
            </button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

// Contextual Tooltip Component
const ContextualTip = ({ id, children, position = "bottom" }) => {
  const [dismissed, setDismissed] = useState(false);
  const storageKey = `medmatch-tip-${id}`;

  useEffect(() => {
    const seen = localStorage.getItem(storageKey);
    if (seen) setDismissed(true);
  }, [storageKey]);

  const handleDismiss = () => {
    localStorage.setItem(storageKey, "true");
    setDismissed(true);
  };

  if (dismissed) return null;

  return (
    <div className="relative inline-flex items-center">
      <div className={`absolute ${position === 'bottom' ? 'top-full mt-2' : 'bottom-full mb-2'} left-0 z-50`}>
        <div className="bg-slate-900 text-white px-3 py-2 rounded-lg shadow-lg text-xs max-w-xs animate-fade-in">
          <div className="flex items-start gap-2">
            <Sparkles className="w-3 h-3 text-amber-400 flex-shrink-0 mt-0.5" />
            <span>{children}</span>
            <button 
              onClick={handleDismiss}
              className="text-slate-400 hover:text-white ml-2"
            >
              ×
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const Dashboard = ({ resume, savedJobs, applications, onNavigate, user }) => {
  const navigate = useNavigate();
  
  const stats = [
    { label: "Saved Jobs", value: savedJobs.length, icon: Bookmark, color: "text-sky-500", path: "/saved" },
    { label: "Applications", value: applications.length, icon: CheckSquare, color: "text-emerald-500", path: "/applications" },
    { label: "Interviews", value: applications.filter(a => a.status === "Interview").length, icon: Clock, color: "text-amber-500", path: "/applications" },
    { label: "Skills", value: resume?.skills?.length || 0, icon: TrendingUp, color: "text-violet-500", path: "/resume" },
  ];

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-7xl mx-auto animate-fade-in" data-testid="dashboard">
      {/* Welcome Header */}
      <div className="mb-8">
        <h1 className="text-3xl md:text-4xl font-semibold text-slate-900 dark:text-slate-100 tracking-tight" style={{ fontFamily: 'IBM Plex Sans' }}>
          {resume?.full_name ? `Welcome, ${resume.full_name.split(' ')[0]}` : 'Welcome to MedMatch'}
        </h1>
        <p className="text-slate-500 dark:text-slate-400 mt-2">
          {resume ? 'Your personalized remote job dashboard' : 'Upload your resume to get started'}
        </p>
      </div>

      {/* Quick Actions Widget */}
      <QuickActionsWidget 
        resume={resume} 
        savedJobs={savedJobs} 
        applications={applications}
        user={user}
      />

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {stats.map(({ label, value, icon: Icon, color, path }) => (
          <Card 
            key={label} 
            className="border-slate-200 dark:border-slate-700 cursor-pointer hover:shadow-md transition-shadow"
            onClick={() => navigate(path)}
          >
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-500 dark:text-slate-400">{label}</p>
                  <p className="text-2xl font-semibold text-slate-900 dark:text-slate-100 mt-1">{value}</p>
                </div>
                <div className={`p-3 rounded-lg bg-slate-50 dark:bg-slate-800 ${color}`}>
                  <Icon className="w-5 h-5" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {!resume ? (
        <Card className="border-dashed border-2 border-slate-300 dark:border-slate-600">
          <CardContent className="p-12 text-center">
            <Upload className="w-12 h-12 text-slate-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-2">Upload Your Resume</h3>
            <p className="text-slate-500 dark:text-slate-400 mb-4">Get AI-powered job matches based on your skills and experience</p>
            <Button onClick={() => onNavigate('/resume')} data-testid="upload-resume-cta">
              Upload Resume
            </Button>
            <ContextualTip id="first-upload" position="bottom">
              Pro tip: Upload a PDF for best results. Our AI extracts skills, experience, and education automatically!
            </ContextualTip>
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
                  <Badge key={i} variant="secondary" className="bg-slate-100 dark:bg-slate-700 dark:text-slate-200">{skill}</Badge>
                ))}
                {resume.skills?.length > 12 && (
                  <Badge variant="outline" className="dark:border-slate-600 dark:text-slate-300">+{resume.skills.length - 12} more</Badge>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg" style={{ fontFamily: 'IBM Plex Sans' }}>Recent Applications</CardTitle>
                  <CardDescription>Track your job applications</CardDescription>
                </div>
                {applications.length > 0 && (
                  <Button variant="ghost" size="sm" onClick={() => navigate('/applications')}>
                    View All <ArrowRight className="w-4 h-4 ml-1" />
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {applications.length === 0 ? (
                <div className="text-center py-4">
                  <p className="text-slate-500 dark:text-slate-400 text-sm mb-3">No applications yet</p>
                  <Button variant="outline" size="sm" onClick={() => navigate('/search')}>
                    <Search className="w-4 h-4 mr-2" /> Find Jobs
                  </Button>
                </div>
              ) : (
                <div className="space-y-3">
                  {applications.slice(0, 3).map((app) => (
                    <div key={app.id} className="flex items-center justify-between p-2 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
                      <div className="min-w-0 flex-1">
                        <p className="font-medium text-slate-900 dark:text-slate-100 text-sm truncate">{app.job.title}</p>
                        <p className="text-xs text-slate-500 dark:text-slate-400 truncate">{app.job.company}</p>
                      </div>
                      <Badge className={`ml-2 status-${app.status.toLowerCase()}`}>{app.status}</Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Feature Highlights for users with resume */}
      {resume && (
        <div className="mt-8">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4" style={{ fontFamily: 'IBM Plex Sans' }}>
            AI-Powered Tools
          </h2>
          <div className="grid md:grid-cols-3 gap-4">
            {[
              { 
                icon: Target, 
                title: "Success Predictor", 
                desc: "Get AI-powered callback probability scores",
                path: "/predictor",
                color: "from-violet-500 to-purple-600"
              },
              { 
                icon: Video, 
                title: "Video Interview", 
                desc: "Practice with AI body language analysis",
                path: "/video-interview",
                color: "from-pink-500 to-rose-600"
              },
              { 
                icon: Bell, 
                title: "Smart Alerts", 
                desc: "Get notified when matching jobs appear",
                path: "/alerts",
                color: "from-amber-500 to-orange-600"
              }
            ].map((feature) => (
              <Card 
                key={feature.title}
                className="cursor-pointer hover:shadow-md transition-all group"
                onClick={() => navigate(feature.path)}
              >
                <CardContent className="p-5">
                  <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${feature.color} flex items-center justify-center mb-3 group-hover:scale-110 transition-transform`}>
                    <feature.icon className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="font-medium text-slate-900 dark:text-slate-100 mb-1">{feature.title}</h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400">{feature.desc}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
