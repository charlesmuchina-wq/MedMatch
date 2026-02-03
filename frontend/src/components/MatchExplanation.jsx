import { useState } from "react";
import { Info, Brain, Target, MapPin, Briefcase, GraduationCap, AlertCircle, Users, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { useTranslation } from "@/utils/i18n";
import axios from "axios";

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * Match Explanation Component
 * GDPR Article 22 - Right to Explanation
 * Shows users why AI recommended a specific job
 */
const MatchExplanation = ({ jobId, jobTitle, matchScore, trigger }) => {
  const { t } = useTranslation();
  const [explanation, setExplanation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [requestingReview, setRequestingReview] = useState(false);
  const [reviewRequested, setReviewRequested] = useState(false);

  const fetchExplanation = async () => {
    if (explanation) return; // Already fetched
    
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem("medmatch-token");
      const response = await axios.get(
        `${API}/api/privacy/explain/match/${jobId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setExplanation(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load explanation");
    } finally {
      setLoading(false);
    }
  };

  const requestHumanReview = async () => {
    setRequestingReview(true);
    
    try {
      const token = localStorage.getItem("medmatch-token");
      await axios.post(
        `${API}/api/privacy/review/request`,
        {
          job_id: jobId,
          reason: "User requested human review of AI matching decision",
          additional_context: `Job: ${jobTitle}, Match Score: ${matchScore}`
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setReviewRequested(true);
    } catch (err) {
      setError("Failed to submit review request");
    } finally {
      setRequestingReview(false);
    }
  };

  const getWeightIcon = (weight) => {
    switch (weight) {
      case "High": return <Target className="w-4 h-4 text-emerald-500" />;
      case "Medium": return <Briefcase className="w-4 h-4 text-amber-500" />;
      case "Low": return <Info className="w-4 h-4 text-slate-400" />;
      default: return <Info className="w-4 h-4" />;
    }
  };

  const getFactorIcon = (factor) => {
    if (factor.includes("Skills")) return <Brain className="w-4 h-4" />;
    if (factor.includes("Experience")) return <Briefcase className="w-4 h-4" />;
    if (factor.includes("Location") || factor.includes("Work Type")) return <MapPin className="w-4 h-4" />;
    if (factor.includes("Education")) return <GraduationCap className="w-4 h-4" />;
    return <Target className="w-4 h-4" />;
  };

  return (
    <Dialog onOpenChange={(open) => open && fetchExplanation()}>
      <DialogTrigger asChild>
        {trigger || (
          <Button
            variant="ghost"
            size="sm"
            className="text-turquoise hover:text-turquoise/80"
            data-testid={`match-info-btn-${jobId}`}
          >
            <Info className="w-4 h-4 mr-1" />
            Match Info
          </Button>
        )}
      </DialogTrigger>
      
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Brain className="w-5 h-5 text-turquoise" />
            Why was I matched?
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {loading && (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin w-6 h-6 border-2 border-turquoise border-t-transparent rounded-full" />
            </div>
          )}

          {error && (
            <div className="p-3 bg-rose-50 dark:bg-rose-900/20 rounded-lg text-rose-600 dark:text-rose-400 text-sm flex items-center gap-2">
              <AlertCircle className="w-4 h-4" />
              {error}
            </div>
          )}

          {explanation && !loading && (
            <>
              {/* Main Explanation */}
              <div className="p-4 bg-turquoise/5 rounded-lg border border-turquoise/20">
                <p className="text-slate-700 dark:text-slate-300 text-sm">
                  {explanation.explanation}
                </p>
              </div>

              {/* Match Score */}
              {matchScore && (
                <div className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
                  <span className="text-sm text-slate-600 dark:text-slate-400">Match Score</span>
                  <Badge 
                    className={`${
                      matchScore >= 80 ? 'bg-emerald-500' : 
                      matchScore >= 60 ? 'bg-amber-500' : 'bg-slate-500'
                    } text-white`}
                  >
                    {matchScore}%
                  </Badge>
                </div>
              )}

              {/* Match Factors */}
              {explanation.match_factors && explanation.match_factors.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-slate-700 dark:text-slate-300">
                    Matching Factors
                  </h4>
                  
                  {explanation.match_factors.map((factor, i) => (
                    <div 
                      key={i}
                      className="flex items-start gap-3 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg"
                    >
                      <div className="p-1.5 rounded bg-white dark:bg-slate-700">
                        {getFactorIcon(factor.factor)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                            {factor.factor}
                          </span>
                          <Badge variant="outline" className="text-xs">
                            {factor.weight}
                          </Badge>
                        </div>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                          {factor.details}
                        </p>
                      </div>
                      {getWeightIcon(factor.weight)}
                    </div>
                  ))}
                </div>
              )}

              {/* Transparency Note */}
              {explanation.transparency_note && (
                <div className="text-xs text-slate-500 dark:text-slate-400 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
                  <strong>Transparency:</strong> {explanation.transparency_note}
                </div>
              )}

              {/* Human Review Option */}
              {explanation.request_review_available && (
                <div className="border-t pt-4">
                  {reviewRequested ? (
                    <div className="p-3 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg text-emerald-700 dark:text-emerald-400 text-sm flex items-center gap-2">
                      <Users className="w-4 h-4" />
                      Human review requested! We'll respond within 2-3 business days.
                    </div>
                  ) : (
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full"
                      onClick={requestHumanReview}
                      disabled={requestingReview}
                      data-testid="request-human-review-btn"
                    >
                      <Users className="w-4 h-4 mr-2" />
                      {requestingReview ? "Submitting..." : "Request Human Review"}
                      <ChevronRight className="w-4 h-4 ml-auto" />
                    </Button>
                  )}
                  <p className="text-xs text-slate-400 mt-2 text-center">
                    GDPR Article 22 - You have the right to human oversight
                  </p>
                </div>
              )}
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default MatchExplanation;
