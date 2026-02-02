import { useState, useEffect } from "react";
import { toast } from "sonner";
import { 
  TrendingUp, Target, Clock, Users, Sparkles, Loader2, 
  ChevronRight, History, AlertCircle, CheckCircle2, XCircle,
  Zap, Award, BarChart3, Lightbulb, Brain, Cpu
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import { useTranslation } from "@/utils/i18n";
import { apiClient } from "@/utils/apiClient";
import CallbackProbabilityPredictor from "@/components/ai/CallbackProbabilityPredictor";

// Probability Score Ring Component
const ProbabilityRing = ({ score, size = "large", t }) => {
  const radius = size === "large" ? 54 : 24;
  const strokeWidth = size === "large" ? 8 : 4;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const viewBox = size === "large" ? "0 0 120 120" : "0 0 60 60";
  const center = size === "large" ? 60 : 30;
  
  const getColor = (s) => {
    if (s >= 75) return '#10B981';
    if (s >= 60) return '#0EA5E9';
    if (s >= 40) return '#F59E0B';
    if (s >= 25) return '#F97316';
    return '#EF4444';
  };

  return (
    <div className={`relative ${size === "large" ? "w-32 h-32" : "w-16 h-16"}`}>
      <svg viewBox={viewBox} className="transform -rotate-90">
        <circle 
          cx={center} cy={center} r={radius} 
          fill="none" stroke="#E2E8F0" strokeWidth={strokeWidth} 
        />
        <circle
          cx={center} cy={center} r={radius} fill="none"
          stroke={getColor(score)} strokeWidth={strokeWidth}
          strokeDasharray={circumference} strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`font-bold ${size === "large" ? "text-3xl" : "text-lg"}`} style={{ color: getColor(score) }}>
          {score}%
        </span>
        {size === "large" && (
          <span className="text-xs text-slate-500">Callback</span>
        )}
      </div>
    </div>
  );
};

// Match Breakdown Bar
const MatchBar = ({ label, score, icon: Icon }) => {
  const getColor = (s) => {
    if (s >= 75) return 'bg-emerald-500';
    if (s >= 60) return 'bg-sky-500';
    if (s >= 40) return 'bg-amber-500';
    return 'bg-rose-500';
  };

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center gap-2 text-slate-600">
          <Icon className="w-4 h-4" />
          {label}
        </div>
        <span className="font-medium text-slate-900 dark:text-slate-100">{score}%</span>
      </div>
      <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
        <div 
          className={`h-full ${getColor(score)} transition-all duration-700 ease-out rounded-full`}
          style={{ width: `${score}%` }}
        />
      </div>
    </div>
  );
};

const SuccessPredictorPage = ({ resume }) => {
  const { t } = useTranslation();
  const [jobTitle, setJobTitle] = useState("");
  const [company, setCompany] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [postedAt, setPostedAt] = useState("");
  const [predicting, setPredicting] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    // Load prediction history
    apiClient.get("/api/jobs/prediction-history").then(res => {
      setHistory(res.data || []);
    }).catch(() => {});
  }, []);

  const predictCallback = async () => {
    if (!jobTitle || !company || !jobDescription) {
      toast.error(t("predictor.fillAllFields"));
      return;
    }
    if (!resume) {
      toast.error(t("predictor.uploadResumeFirst"));
      return;
    }

    setPredicting(true);
    try {
      const response = await apiClient.post("/api/jobs/predict-callback", {
        job_title: jobTitle,
        company: company,
        job_description: jobDescription,
        posted_at: postedAt,
        location: ""
      });
      setPrediction(response.data);
      toast.success(t("predictor.predictionComplete"));
      // Refresh history
      const historyRes = await apiClient.get("/api/jobs/prediction-history");
      setHistory(historyRes.data || []);
    } catch (e) {
      toast.error(e.data?.detail || t("errors.somethingWentWrong"));
    }
    setPredicting(false);
  };

  const loadFromHistory = (item) => {
    setJobTitle(item.job_title);
    setCompany(item.company);
    setPrediction({
      probability_score: item.probability_score,
      probability_label: item.probability_label
    });
  };

  const getLabelColor = (label) => {
    const colors = {
      "Very High": "bg-emerald-100 text-emerald-700 border-emerald-200",
      "High": "bg-sky-100 text-sky-700 border-sky-200",
      "Medium": "bg-amber-100 text-amber-700 border-amber-200",
      "Low": "bg-orange-100 text-orange-700 border-orange-200",
      "Very Low": "bg-rose-100 text-rose-700 border-rose-200"
    };
    return colors[label] || "bg-slate-100 text-slate-700 dark:text-slate-300";
  };

  const getCompetitionIcon = (level) => {
    if (level === "Low") return <Users className="w-4 h-4 text-emerald-500" />;
    if (level === "Moderate") return <Users className="w-4 h-4 text-amber-500" />;
    return <Users className="w-4 h-4 text-rose-500" />;
  };

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-6xl mx-auto animate-fade-in" data-testid="success-predictor-page">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold text-slate-900 dark:text-slate-100 tracking-tight mb-2" style={{ fontFamily: 'IBM Plex Sans' }}>
          {t("predictor.title")}
        </h1>
        <p className="text-slate-500">{t("predictor.subtitle")}</p>
      </div>

      <div className="grid lg:grid-cols-5 gap-6">
        {/* Input Section - 2 columns */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2" style={{ fontFamily: 'IBM Plex Sans' }}>
                <Target className="w-5 h-5 text-sky-500" />
                {t("predictor.jobDetails")}
              </CardTitle>
              <CardDescription>
                {t("predictor.jobDetailsDesc")}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium text-slate-700 dark:text-slate-300">{t("predictor.jobTitleRequired")}</label>
                <Input
                  placeholder="e.g., Supplier Quality Manager"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  className="mt-1"
                  data-testid="predict-job-title"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700 dark:text-slate-300">{t("predictor.companyRequired")}</label>
                <Input
                  placeholder="e.g., Medtronic"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  className="mt-1"
                  data-testid="predict-company"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700 dark:text-slate-300">{t("predictor.postedDate")}</label>
                <Input
                  type="date"
                  value={postedAt}
                  onChange={(e) => setPostedAt(e.target.value)}
                  className="mt-1"
                  data-testid="predict-posted-date"
                />
                <p className="text-xs text-slate-400 mt-1">{t("predictor.postedDateHint")}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700 dark:text-slate-300">{t("predictor.jobDescRequired")}</label>
                <Textarea
                  placeholder={t("predictor.jobDescPlaceholder")}
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  className="mt-1 min-h-[180px]"
                  data-testid="predict-job-description"
                />
              </div>
              <Button 
                onClick={predictCallback} 
                disabled={predicting || !resume}
                className="w-full bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700"
                data-testid="predict-btn"
              >
                {predicting ? (
                  <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> {t("predictor.analyzing")}</>
                ) : (
                  <><Sparkles className="w-4 h-4 mr-2" /> {t("predictor.predictButton")}</>
                )}
              </Button>
              {!resume && (
                <p className="text-sm text-amber-600 text-center flex items-center justify-center gap-1">
                  <AlertCircle className="w-4 h-4" /> {t("predictor.uploadResumeFirst")}
                </p>
              )}
            </CardContent>
          </Card>

          {/* History */}
          {history.length > 0 && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-base" style={{ fontFamily: 'IBM Plex Sans' }}>
                  <History className="w-4 h-4" />
                  {t("predictor.recentPredictions")}
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
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-slate-900 truncate">{item.job_title}</p>
                        <p className="text-xs text-slate-500">{item.company}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className={`${getLabelColor(item.probability_label)} text-xs`}>
                          {item.probability_score}%
                        </Badge>
                        <ChevronRight className="w-4 h-4 text-slate-400" />
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Results Section - 3 columns */}
        <div className="lg:col-span-3">
          <Card className="h-full">
            <CardHeader>
              <CardTitle className="flex items-center gap-2" style={{ fontFamily: 'IBM Plex Sans' }}>
                <BarChart3 className="w-5 h-5 text-violet-500" />
                {t("predictor.predictionResults")}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {prediction ? (
                <div className="space-y-6">
                  {/* Main Score */}
                  <div className="flex items-center justify-between p-6 bg-gradient-to-r from-slate-50 to-violet-50 rounded-xl">
                    <div>
                      <p className="text-sm text-slate-500 mb-1">{t("predictor.callbackProbability")}</p>
                      <div className="flex items-center gap-3">
                        <Badge className={`${getLabelColor(prediction.probability_label)} text-lg px-3 py-1`}>
                          {prediction.probability_label}
                        </Badge>
                      </div>
                      {prediction.interview_likelihood && (
                        <p className="text-sm text-slate-600 mt-2">
                          {t("predictor.interviewLikelihood")}: <span className="font-medium">{prediction.interview_likelihood}</span>
                        </p>
                      )}
                    </div>
                    <ProbabilityRing score={prediction.probability_score} size="large" t={t} />
                  </div>

                  {/* Match Breakdown */}
                  {prediction.match_breakdown && Object.keys(prediction.match_breakdown).length > 0 && (
                    <div className="space-y-3">
                      <h4 className="font-medium text-slate-900 flex items-center gap-2">
                        <BarChart3 className="w-4 h-4 text-slate-400" />
                        {t("predictor.matchBreakdown")}
                      </h4>
                      <div className="grid gap-3">
                        <MatchBar label={t("predictor.skillsMatch")} score={prediction.match_breakdown.skills_match || 0} icon={Zap} />
                        <MatchBar label={t("predictor.experienceMatch")} score={prediction.match_breakdown.experience_match || 0} icon={Award} />
                        <MatchBar label={t("predictor.educationMatch")} score={prediction.match_breakdown.education_match || 0} icon={CheckCircle2} />
                        <MatchBar label={t("predictor.keywordsMatch")} score={prediction.match_breakdown.keywords_match || 0} icon={Target} />
                      </div>
                    </div>
                  )}

                  {/* Competition & Timing */}
                  <div className="grid md:grid-cols-2 gap-4">
                    {prediction.competition_estimate && (
                      <div className="p-4 bg-slate-50 rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          {getCompetitionIcon(prediction.competition_estimate)}
                          <span className="font-medium text-slate-900 dark:text-slate-100">{t("predictor.competitionLevel")}</span>
                        </div>
                        <p className="text-lg font-semibold text-slate-800">{prediction.competition_estimate}</p>
                        {prediction.competition_reasoning && (
                          <p className="text-sm text-slate-500 mt-1">{prediction.competition_reasoning}</p>
                        )}
                      </div>
                    )}
                    {prediction.timing_advice && (
                      <div className="p-4 bg-sky-50 rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          <Clock className="w-4 h-4 text-sky-500" />
                          <span className="font-medium text-slate-900 dark:text-slate-100">{t("predictor.timingAdvice")}</span>
                        </div>
                        <p className="text-sm text-slate-700 dark:text-slate-300">{prediction.timing_advice}</p>
                      </div>
                    )}
                  </div>

                  {/* Strengths */}
                  {prediction.strengths?.length > 0 && (
                    <div>
                      <h4 className="font-medium text-slate-900 flex items-center gap-2 mb-3">
                        <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                        {t("predictor.yourStrengths")}
                      </h4>
                      <div className="space-y-2">
                        {prediction.strengths.map((strength, i) => (
                          <div key={i} className="flex items-start gap-2 text-sm text-slate-700 dark:text-slate-300">
                            <span className="text-emerald-500 mt-0.5">✓</span>
                            {strength}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Gaps */}
                  {prediction.gaps?.length > 0 && (
                    <div>
                      <h4 className="font-medium text-slate-900 flex items-center gap-2 mb-3">
                        <XCircle className="w-4 h-4 text-amber-500" />
                        {t("predictor.areasToAddress")}
                      </h4>
                      <div className="space-y-2">
                        {prediction.gaps.map((gap, i) => (
                          <div key={i} className="flex items-start gap-2 text-sm text-slate-700 dark:text-slate-300">
                            <span className="text-amber-500 mt-0.5">!</span>
                            {gap}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Recommendations */}
                  {prediction.recommendations?.length > 0 && (
                    <div className="p-4 bg-violet-50 rounded-lg">
                      <h4 className="font-medium text-violet-900 flex items-center gap-2 mb-3">
                        <Lightbulb className="w-4 h-4" />
                        {t("predictor.recommendations")}
                      </h4>
                      <ul className="space-y-2">
                        {prediction.recommendations.map((rec, i) => (
                          <li key={i} className="text-sm text-violet-800 flex items-start gap-2">
                            <span className="font-medium text-violet-600">{i + 1}.</span>
                            {rec}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Key Differentiators */}
                  {prediction.key_differentiators?.length > 0 && (
                    <div>
                      <h4 className="font-medium text-slate-900 flex items-center gap-2 mb-3">
                        <Award className="w-4 h-4 text-sky-500" />
                        {t("predictor.whatMakesYouStandOut")}
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {prediction.key_differentiators.map((diff, i) => (
                          <Badge key={i} variant="secondary" className="bg-sky-100 text-sky-700">
                            {diff}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-16 text-slate-400">
                  <Target className="w-16 h-16 mx-auto mb-4 opacity-40" />
                  <p className="text-lg font-medium text-slate-500 mb-2">{t("predictor.noPredictionYet")}</p>
                  <p>{t("predictor.enterJobDetails")}</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default SuccessPredictorPage;
