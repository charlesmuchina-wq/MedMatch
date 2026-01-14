import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { 
  Bookmark, ExternalLink, MapPin, Building2, 
  Clock, ChevronRight, Loader2, TrendingUp, Target,
  CheckCircle2, XCircle, AlertCircle, HelpCircle
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Job Status Badge Component
const JobStatusBadge = ({ status, postedAt }) => {
  // Calculate days since posted
  const getDaysSincePosted = () => {
    if (!postedAt) return null;
    try {
      const date = new Date(postedAt);
      const now = new Date();
      return Math.floor((now - date) / (1000 * 60 * 60 * 24));
    } catch {
      return null;
    }
  };

  const daysSincePosted = getDaysSincePosted();

  // Determine status based on explicit status or age
  const getStatusInfo = () => {
    // If explicit status is provided
    if (status) {
      const statusLower = status.toLowerCase();
      if (statusLower === 'active' || statusLower === 'open') {
        return { label: 'Active', icon: CheckCircle2, color: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400', iconColor: 'text-emerald-500' };
      }
      if (statusLower === 'closed' || statusLower === 'filled' || statusLower === 'expired') {
        return { label: 'Closed', icon: XCircle, color: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400', iconColor: 'text-red-500' };
      }
      if (statusLower === 'paused' || statusLower === 'on hold') {
        return { label: 'Paused', icon: AlertCircle, color: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400', iconColor: 'text-amber-500' };
      }
    }

    // Infer status from age if no explicit status
    if (daysSincePosted !== null) {
      if (daysSincePosted <= 7) {
        return { label: 'New', icon: CheckCircle2, color: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400', iconColor: 'text-emerald-500' };
      }
      if (daysSincePosted <= 30) {
        return { label: 'Active', icon: CheckCircle2, color: 'bg-sky-100 text-sky-700 dark:bg-sky-900/30 dark:text-sky-400', iconColor: 'text-sky-500' };
      }
      if (daysSincePosted <= 60) {
        return { label: 'May be closed', icon: AlertCircle, color: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400', iconColor: 'text-amber-500' };
      }
      return { label: 'Likely closed', icon: XCircle, color: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400', iconColor: 'text-red-500' };
    }

    // Unknown status
    return { label: 'Unknown', icon: HelpCircle, color: 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300', iconColor: 'text-slate-400' };
  };

  const statusInfo = getStatusInfo();
  const StatusIcon = statusInfo.icon;

  return (
    <Badge className={`${statusInfo.color} text-xs px-2 py-0.5 flex items-center gap-1`} data-testid="job-status-badge">
      <StatusIcon className={`w-3 h-3 ${statusInfo.iconColor}`} />
      {statusInfo.label}
    </Badge>
  );
};

// Match Score Ring Component
export const MatchScoreRing = ({ score }) => {
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

// Callback Probability Badge Component
const CallbackBadge = ({ job }) => {
  const [probability, setProbability] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchProbability = async () => {
    if (probability !== null || loading) return;
    setLoading(true);
    try {
      const response = await axios.post(`${API}/jobs/quick-probability`, {
        job_title: job.title,
        company: job.company,
        job_description: job.description || "",
        posted_at: job.posted_at || ""
      });
      setProbability(response.data);
    } catch (e) {
      // Silently fail - don't spam errors for quick probability
    }
    setLoading(false);
  };

  useEffect(() => {
    // Auto-fetch probability when component mounts
    const timer = setTimeout(fetchProbability, 500);
    return () => clearTimeout(timer);
  }, [job.id]);

  if (loading) {
    return (
      <div className="flex items-center gap-1 text-xs text-slate-400">
        <Loader2 className="w-3 h-3 animate-spin" />
      </div>
    );
  }

  if (!probability || probability.probability_label === "Upload Resume") {
    return null;
  }

  const getLabelStyle = (label) => {
    const styles = {
      "Very High": "bg-emerald-100 text-emerald-700 border-emerald-200",
      "High": "bg-sky-100 text-sky-700 border-sky-200",
      "Medium": "bg-amber-100 text-amber-700 border-amber-200",
      "Low": "bg-orange-100 text-orange-700 border-orange-200",
      "Very Low": "bg-rose-100 text-rose-700 border-rose-200"
    };
    return styles[label] || "bg-slate-100 text-slate-700";
  };

  return (
    <div className="flex items-center gap-1.5" title={`Callback Probability: ${probability.probability_score}%`}>
      <Target className="w-3.5 h-3.5 text-violet-500" />
      <Badge className={`${getLabelStyle(probability.probability_label)} text-xs px-1.5 py-0`}>
        {probability.probability_score}%
      </Badge>
    </div>
  );
};

// Job Card Component
export const JobCard = ({ job, onSave, onApply, onAnalyze, isSaved, showActions = true, showProbability = true }) => {
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
                <h3 className="font-semibold text-slate-900 dark:text-slate-100 text-lg leading-tight" style={{ fontFamily: 'IBM Plex Sans' }}>
                  {job.title}
                </h3>
                <div className="flex items-center gap-2 mt-1 text-slate-600 dark:text-slate-400">
                  <Building2 className="w-4 h-4" />
                  <span className="text-sm">{job.company}</span>
                </div>
              </div>
              <div className="flex flex-col items-end gap-2">
                {matchData && <MatchScoreRing score={matchData.match_score} />}
                {!matchData && job.relevance_score > 0 && (
                  <div className="flex flex-col items-center">
                    <span className="text-xs text-slate-400 dark:text-slate-500">Relevance</span>
                    <span className={`text-lg font-semibold ${
                      job.relevance_score >= 50 ? 'text-emerald-500' : 
                      job.relevance_score >= 30 ? 'text-sky-500' : 
                      job.relevance_score >= 10 ? 'text-amber-500' : 'text-slate-400'
                    }`}>
                      {Math.min(job.relevance_score, 100)}%
                    </span>
                  </div>
                )}
                {/* Quick Callback Probability Badge */}
                {showProbability && !matchData && <CallbackBadge job={job} />}
              </div>
            </div>
            
            <div className="flex flex-wrap items-center gap-3 text-sm text-slate-500 dark:text-slate-400 mb-3">
              {/* Job Status Badge */}
              <JobStatusBadge status={job.status || job.job_status} postedAt={job.posted_at} />
              
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
                <span className="text-emerald-600 dark:text-emerald-400 font-medium">{job.salary}</span>
              )}
              <Badge variant="secondary" className="text-xs dark:bg-slate-700 dark:text-slate-200">
                {job.source}
              </Badge>
            </div>
            
            {job.tags?.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-3">
                {job.tags.slice(0, 5).map((tag, i) => (
                  <span key={i} className="tag-badge dark:bg-slate-700 dark:text-slate-200">{tag}</span>
                ))}
              </div>
            )}
            
            {matchData?.analysis && (
              <p className="text-sm text-slate-600 dark:text-slate-300 bg-slate-50 dark:bg-slate-800 p-3 rounded-lg mb-3">
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

export default JobCard;
