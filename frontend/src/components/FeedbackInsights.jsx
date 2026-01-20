import { useState, useEffect } from "react";
import { 
  MessageSquare, TrendingUp, AlertTriangle, Target, 
  Lightbulb, BarChart3, Loader2, ChevronRight, Info
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";
import { useTranslation } from "@/utils/i18n";
import { apiClient } from "@/utils/apiClient";

/**
 * Feedback Insights Component for Job Seekers
 * Shows aggregated, anonymous feedback from recruiters to help improve
 */
const FeedbackInsights = () => {
  const { t } = useTranslation();
  const [insights, setInsights] = useState(null);
  const [benchmarks, setBenchmarks] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showBenchmarks, setShowBenchmarks] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [insightsRes, benchmarksRes] = await Promise.all([
        apiClient.get("/feedback/insights"),
        apiClient.get("/feedback/benchmarks")
      ]);
      setInsights(insightsRes);
      setBenchmarks(benchmarksRes);
    } catch (error) {
      console.error("Failed to fetch feedback:", error);
    } finally {
      setLoading(false);
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      "Skills Gap": "bg-red-500",
      "Experience Mismatch": "bg-orange-500",
      "Culture Fit": "bg-yellow-500",
      "Salary Mismatch": "bg-purple-500",
      "Overqualified": "bg-blue-500",
      "Underqualified": "bg-pink-500",
      "Location": "bg-cyan-500",
      "Communication": "bg-emerald-500",
      "Portfolio": "bg-indigo-500",
      "Other": "bg-slate-500"
    };
    return colors[category] || "bg-slate-500";
  };

  const getCategoryIcon = (category) => {
    const lower = category.toLowerCase();
    if (lower.includes("skill")) return Target;
    if (lower.includes("experience")) return TrendingUp;
    if (lower.includes("culture")) return MessageSquare;
    return AlertTriangle;
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="p-8 flex items-center justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-turquoise" />
        </CardContent>
      </Card>
    );
  }

  if (!insights?.has_feedback) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-turquoise" />
            {t("feedback.title") || "Application Insights"}
          </CardTitle>
          <CardDescription>
            {t("feedback.description") || "Anonymous feedback to help improve your applications"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Info className="w-12 h-12 text-slate-300 mx-auto mb-4" />
            <h3 className="font-medium text-slate-900 dark:text-slate-100 mb-2">
              {t("feedback.noFeedbackYet") || "No Feedback Yet"}
            </h3>
            <p className="text-sm text-slate-500 dark:text-slate-400 max-w-md mx-auto">
              {t("feedback.keepApplying") || "Keep applying! As recruiters provide feedback on your applications, you'll see insights here to help improve."}
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Main Insights Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="w-5 h-5 text-turquoise" />
                {t("feedback.title") || "Application Insights"}
              </CardTitle>
              <CardDescription>
                {t("feedback.basedOn", { count: insights.total_applications_with_feedback }) || 
                  `Based on ${insights.total_applications_with_feedback} application(s) with feedback`}
              </CardDescription>
            </div>
            <Badge variant="outline" className="text-turquoise border-turquoise/30">
              {t("feedback.anonymous") || "Anonymous"}
            </Badge>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Top Area for Improvement */}
          {insights.top_area_for_improvement && (
            <div className="p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-lg bg-amber-500 flex items-center justify-center flex-shrink-0">
                  <Target className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h4 className="font-medium text-amber-800 dark:text-amber-200">
                    {t("feedback.topArea") || "Top Area for Improvement"}
                  </h4>
                  <p className="text-sm text-amber-700 dark:text-amber-300 mt-1">
                    {insights.top_area_for_improvement}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Feedback Breakdown */}
          <div>
            <h4 className="font-medium text-slate-900 dark:text-slate-100 mb-4">
              {t("feedback.breakdown") || "Feedback Breakdown"}
            </h4>
            <div className="space-y-3">
              {insights.insights?.map((item, idx) => {
                const Icon = getCategoryIcon(item.category);
                return (
                  <div key={idx} className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-lg ${getCategoryColor(item.category)} flex items-center justify-center flex-shrink-0`}>
                      <Icon className="w-4 h-4 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                          {item.category}
                        </span>
                        <span className="text-sm text-slate-500 dark:text-slate-400">
                          {item.percentage}%
                        </span>
                      </div>
                      <Progress value={item.percentage} className="h-2" />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* AI Improvement Suggestions */}
          {insights.improvement_suggestions?.length > 0 && (
            <div className="pt-4 border-t border-slate-200 dark:border-slate-700">
              <h4 className="font-medium text-slate-900 dark:text-slate-100 mb-3 flex items-center gap-2">
                <Lightbulb className="w-4 h-4 text-amber-500" />
                {t("feedback.suggestions") || "AI-Powered Suggestions"}
              </h4>
              <ul className="space-y-2">
                {insights.improvement_suggestions.map((suggestion, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                    <ChevronRight className="w-4 h-4 text-turquoise flex-shrink-0 mt-0.5" />
                    <span>{suggestion}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Industry Benchmarks */}
      <Card>
        <CardHeader>
          <button 
            onClick={() => setShowBenchmarks(!showBenchmarks)}
            className="w-full flex items-center justify-between"
          >
            <div>
              <CardTitle className="flex items-center gap-2 text-base">
                <BarChart3 className="w-5 h-5 text-turquoise" />
                {t("feedback.benchmarks") || "Industry Benchmarks"}
              </CardTitle>
              <CardDescription>
                {t("feedback.benchmarksDesc") || "See how your feedback compares to all candidates"}
              </CardDescription>
            </div>
            <ChevronRight className={`w-5 h-5 text-slate-400 transition-transform ${showBenchmarks ? "rotate-90" : ""}`} />
          </button>
        </CardHeader>
        
        {showBenchmarks && benchmarks?.has_data && (
          <CardContent>
            <div className="space-y-3">
              {benchmarks.benchmarks?.slice(0, 5).map((item, idx) => (
                <div key={idx} className="flex items-center gap-3">
                  <div className={`w-2 h-2 rounded-full ${getCategoryColor(item.category)}`} />
                  <span className="text-sm text-slate-600 dark:text-slate-400 flex-1">
                    {item.category}
                  </span>
                  <span className="text-sm font-medium text-slate-900 dark:text-slate-100">
                    {item.percentage}%
                  </span>
                </div>
              ))}
            </div>
            {benchmarks.insight && (
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-4 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
                {benchmarks.insight}
              </p>
            )}
          </CardContent>
        )}
      </Card>
    </div>
  );
};

export default FeedbackInsights;
