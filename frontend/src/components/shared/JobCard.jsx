import { useState } from "react";
import { toast } from "sonner";
import { 
  Bookmark, ExternalLink, MapPin, Building2, 
  Clock, ChevronRight, Loader2 
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";

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

// Job Card Component
export const JobCard = ({ job, onSave, onApply, onAnalyze, isSaved, showActions = true }) => {
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

export default JobCard;
