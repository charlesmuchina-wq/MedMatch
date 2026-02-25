/**
 * Translation QA Dashboard Component
 * Part of Karau Automator
 * 
 * Displays translation quality metrics, issues, and recommendations
 */

import { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Languages, RefreshCw, AlertTriangle, CheckCircle, XCircle, 
  ChevronDown, ChevronUp, Clock, TrendingUp, Shield, Zap,
  Globe, FileWarning, Type, ArrowRight, Wrench, Activity, Heart
} from "lucide-react";
import axios from "axios";
import { toast } from "sonner";

const API = process.env.REACT_APP_BACKEND_URL || "";

// Health status colors
const healthColors = {
  excellent: "bg-green-500",
  good: "bg-blue-500",
  needs_attention: "bg-yellow-500",
  critical: "bg-red-500"
};

const healthTextColors = {
  excellent: "text-green-600",
  good: "text-blue-600",
  needs_attention: "text-yellow-600",
  critical: "text-red-600"
};

// Language Score Card
const LanguageScoreCard = ({ langCode, data, onClick }) => {
  const getStatusColor = (score) => {
    if (score >= 90) return "bg-green-100 border-green-300 text-green-800";
    if (score >= 70) return "bg-yellow-100 border-yellow-300 text-yellow-800";
    return "bg-red-100 border-red-300 text-red-800";
  };

  const getStatusIcon = (score) => {
    if (score >= 90) return <CheckCircle className="w-4 h-4 text-green-600" />;
    if (score >= 70) return <AlertTriangle className="w-4 h-4 text-yellow-600" />;
    return <XCircle className="w-4 h-4 text-red-600" />;
  };

  return (
    <div 
      className={`p-3 rounded-lg border cursor-pointer transition-all hover:shadow-md ${getStatusColor(data.score)}`}
      onClick={() => onClick(langCode)}
      data-testid={`lang-score-${langCode}`}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="font-medium uppercase">{langCode}</span>
        {getStatusIcon(data.score)}
      </div>
      <div className="text-2xl font-bold">{data.score}</div>
      <div className="text-xs mt-1 opacity-75">
        {data.missing_keys > 0 && `${data.missing_keys} missing`}
        {data.placeholder_errors > 0 && ` • ${data.placeholder_errors} errors`}
      </div>
    </div>
  );
};

// Issue Item Component
const IssueItem = ({ issue, priority }) => {
  const priorityColors = {
    critical: "bg-red-100 text-red-800 border-red-200",
    high: "bg-orange-100 text-orange-800 border-orange-200",
    medium: "bg-yellow-100 text-yellow-800 border-yellow-200",
    low: "bg-blue-100 text-blue-800 border-blue-200"
  };

  return (
    <div className={`p-3 rounded-lg border ${priorityColors[priority] || priorityColors.medium}`}>
      <div className="flex items-start gap-2">
        <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />
        <div>
          <div className="font-medium text-sm">{issue.type}</div>
          <div className="text-xs mt-1">{issue.message}</div>
          {issue.key && (
            <code className="text-xs bg-black/10 px-1 rounded mt-1 inline-block">{issue.key}</code>
          )}
        </div>
      </div>
    </div>
  );
};

// Recommendation Card
const RecommendationCard = ({ recommendation }) => {
  const priorityColors = {
    critical: "border-l-red-500",
    high: "border-l-orange-500",
    medium: "border-l-yellow-500",
    low: "border-l-blue-500"
  };

  const priorityIcons = {
    critical: <XCircle className="w-5 h-5 text-red-500" />,
    high: <AlertTriangle className="w-5 h-5 text-orange-500" />,
    medium: <FileWarning className="w-5 h-5 text-yellow-500" />,
    low: <CheckCircle className="w-5 h-5 text-blue-500" />
  };

  return (
    <Card className={`border-l-4 ${priorityColors[recommendation.priority]}`}>
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          {priorityIcons[recommendation.priority]}
          <div className="flex-1">
            <h4 className="font-semibold text-sm">{recommendation.title}</h4>
            <p className="text-xs text-slate-600 mt-1">{recommendation.description}</p>
            <div className="mt-2 flex items-center gap-2">
              <Badge variant="outline" className="text-xs">{recommendation.category}</Badge>
              <ArrowRight className="w-3 h-3 text-slate-400" />
              <span className="text-xs text-slate-500">{recommendation.action}</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// Main Dashboard Component
const TranslationQADashboard = () => {
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [fixing, setFixing] = useState(false);
  const [fixJobId, setFixJobId] = useState(null);
  const [fixProgress, setFixProgress] = useState(null);
  const [summary, setSummary] = useState(null);
  const [details, setDetails] = useState(null);
  const [selectedLang, setSelectedLang] = useState(null);
  const [expandedSection, setExpandedSection] = useState("overview");
  const [healthData, setHealthData] = useState(null);
  const [healthLoading, setHealthLoading] = useState(false);

  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    try {
      const [summaryRes, detailsRes] = await Promise.all([
        axios.get(`${API}/api/translation-qa/dashboard-summary`),
        axios.get(`${API}/api/translation-qa/latest`)
      ]);
      setSummary(summaryRes.data);
      setDetails(detailsRes.data);
    } catch (error) {
      console.error("Failed to fetch QA data:", error);
      toast.error("Failed to load translation QA data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  const runQA = async () => {
    setRunning(true);
    try {
      await axios.post(`${API}/api/translation-qa/run`);
      toast.success("Translation QA completed");
      await fetchDashboardData();
    } catch (error) {
      toast.error("QA run failed");
    } finally {
      setRunning(false);
    }
  };

  const fetchLanguageDetails = async (langCode) => {
    try {
      const res = await axios.get(`${API}/api/translation-qa/language/${langCode}`);
      setSelectedLang({ code: langCode, data: res.data });
    } catch (error) {
      toast.error(`Failed to load details for ${langCode}`);
    }
  };

  const autoFixIssues = async (targetKpi = 98) => {
    setFixing(true);
    setFixProgress(null);
    try {
      const res = await axios.post(`${API}/api/translation-qa/auto-translate`, {
        target_kpi: targetKpi,
        dry_run: false
      });
      const jobId = res.data.job_id;
      setFixJobId(jobId);
      toast.success(`Auto-fix started for ${res.data.languages_to_translate} languages (${res.data.total_keys_to_translate} keys)`);

      // Poll for progress
      const poll = setInterval(async () => {
        try {
          const statusRes = await axios.get(`${API}/api/translation-qa/auto-translate/${jobId}`);
          setFixProgress(statusRes.data);
          if (statusRes.data.status === "completed") {
            clearInterval(poll);
            setFixing(false);
            toast.success(`Auto-fix complete: ${statusRes.data.keys_translated} keys translated across ${statusRes.data.languages_completed} languages`);
            await fetchDashboardData();
          }
        } catch {
          // keep polling
        }
      }, 3000);

      // Safety timeout after 5 min
      setTimeout(() => {
        clearInterval(poll);
        setFixing(false);
      }, 300000);

    } catch (error) {
      toast.error("Auto-fix failed to start");
      setFixing(false);
    }
  };

  const fetchHealthMonitor = async () => {
    setHealthLoading(true);
    try {
      const res = await axios.get(`${API}/api/translation-qa/health-monitor`);
      setHealthData(res.data);
    } catch (error) {
      console.error("Health monitor fetch failed:", error);
    } finally {
      setHealthLoading(false);
    }
  };

  useEffect(() => {
    fetchHealthMonitor();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-turquoise" />
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="translation-qa-dashboard">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Languages className="w-6 h-6 text-turquoise" />
            Translation QA
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            AI-powered localization quality assurance
          </p>
        </div>
        <div className="flex gap-2">
          <Button 
            onClick={() => autoFixIssues(98)} 
            disabled={fixing || running}
            variant="outline"
            className="border-orange-300 text-orange-700 hover:bg-orange-50"
            data-testid="auto-fix-btn"
          >
            {fixing ? (
              <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Wrench className="w-4 h-4 mr-2" />
            )}
            {fixing ? `Fixing${fixProgress ? ` (${fixProgress.languages_completed}/${fixProgress.languages_total})` : '...'}` : "Auto-Fix Issues"}
          </Button>
          <Button 
            onClick={runQA} 
            disabled={running || fixing}
            className="bg-turquoise hover:bg-turquoise/90"
            data-testid="run-qa-btn"
          >
            {running ? (
              <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Zap className="w-4 h-4 mr-2" />
            )}
            {running ? "Running..." : "Run QA"}
          </Button>
        </div>
      </div>

      {/* Auto-Fix Progress Banner */}
      {fixing && fixProgress && (
        <Card className="border-orange-200 bg-orange-50 dark:bg-orange-950/20 dark:border-orange-800">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <RefreshCw className="w-5 h-5 text-orange-600 animate-spin" />
              <div className="flex-1">
                <div className="font-medium text-sm text-orange-800 dark:text-orange-200">
                  Auto-fixing translation issues...
                </div>
                <div className="text-xs text-orange-600 dark:text-orange-400 mt-1">
                  {fixProgress.languages_completed}/{fixProgress.languages_total} languages processed 
                  {fixProgress.keys_translated > 0 && ` | ${fixProgress.keys_translated} keys translated`}
                </div>
                <Progress 
                  value={fixProgress.languages_total > 0 ? (fixProgress.languages_completed / fixProgress.languages_total) * 100 : 0} 
                  className="mt-2 h-2" 
                />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Overall Score Card */}
      {summary && (
        <Card className="bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-800 dark:to-slate-900">
          <CardContent className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              {/* Score Circle */}
              <div className="flex flex-col items-center justify-center">
                <div className={`w-32 h-32 rounded-full flex items-center justify-center ${healthColors[summary.health]}`}>
                  <div className="text-center text-white">
                    <div className="text-4xl font-bold">{summary.overall_score}</div>
                    <div className="text-xs uppercase tracking-wider">{summary.health}</div>
                  </div>
                </div>
                <div className="mt-2 text-xs text-slate-500">
                  Last run: {new Date(summary.last_run).toLocaleString()}
                </div>
              </div>

              {/* Stats */}
              <div className="col-span-3 grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-white dark:bg-slate-700 rounded-lg shadow-sm">
                  <Globe className="w-5 h-5 text-blue-500 mb-2" />
                  <div className="text-2xl font-bold">{summary.total_languages}</div>
                  <div className="text-xs text-slate-500">Languages</div>
                </div>
                
                <div className="p-4 bg-white dark:bg-slate-700 rounded-lg shadow-sm">
                  <Type className="w-5 h-5 text-purple-500 mb-2" />
                  <div className="text-2xl font-bold">{summary.total_keys}</div>
                  <div className="text-xs text-slate-500">Translation Keys</div>
                </div>
                
                <div className="p-4 bg-white dark:bg-slate-700 rounded-lg shadow-sm">
                  <AlertTriangle className="w-5 h-5 text-red-500 mb-2" />
                  <div className="text-2xl font-bold">{summary.issues?.critical || 0}</div>
                  <div className="text-xs text-slate-500">Critical Issues</div>
                </div>
                
                <div className="p-4 bg-white dark:bg-slate-700 rounded-lg shadow-sm">
                  <FileWarning className="w-5 h-5 text-yellow-500 mb-2" />
                  <div className="text-2xl font-bold">{summary.issues?.missing_keys || 0}</div>
                  <div className="text-xs text-slate-500">Missing Keys</div>
                </div>
              </div>
            </div>

            {/* Language Status Bar */}
            <div className="mt-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Language Health Distribution</span>
                <div className="flex gap-4 text-xs">
                  <span className="flex items-center gap-1">
                    <span className="w-3 h-3 rounded-full bg-green-500"></span>
                    Healthy: {summary.language_status?.healthy || 0}
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="w-3 h-3 rounded-full bg-yellow-500"></span>
                    Warning: {summary.language_status?.warning || 0}
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="w-3 h-3 rounded-full bg-red-500"></span>
                    Critical: {summary.language_status?.critical || 0}
                  </span>
                </div>
              </div>
              <div className="h-4 rounded-full overflow-hidden bg-slate-200 flex">
                {summary.language_status && (
                  <>
                    <div 
                      className="bg-green-500 h-full transition-all" 
                      style={{ width: `${(summary.language_status.healthy / summary.total_languages) * 100}%` }}
                    />
                    <div 
                      className="bg-yellow-500 h-full transition-all" 
                      style={{ width: `${(summary.language_status.warning / summary.total_languages) * 100}%` }}
                    />
                    <div 
                      className="bg-red-500 h-full transition-all" 
                      style={{ width: `${(summary.language_status.critical / summary.total_languages) * 100}%` }}
                    />
                  </>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tabs for Details */}
      <Tabs defaultValue="languages" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="languages" data-testid="tab-languages">Languages</TabsTrigger>
          <TabsTrigger value="issues" data-testid="tab-issues">Issues</TabsTrigger>
          <TabsTrigger value="recommendations" data-testid="tab-recommendations">Recommendations</TabsTrigger>
          <TabsTrigger value="details" data-testid="tab-details">Details</TabsTrigger>
        </TabsList>

        {/* Languages Tab */}
        <TabsContent value="languages" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Language Scores</CardTitle>
              <CardDescription>Click on a language to see detailed issues</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-3">
                {details?.languages && Object.entries(details.languages).map(([code, data]) => (
                  <LanguageScoreCard 
                    key={code} 
                    langCode={code} 
                    data={data}
                    onClick={fetchLanguageDetails}
                  />
                ))}
              </div>

              {/* Selected Language Details */}
              {selectedLang && (
                <div className="mt-6 p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-lg uppercase">
                      {selectedLang.code} Details
                    </h3>
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      onClick={() => setSelectedLang(null)}
                    >
                      Close
                    </Button>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div className="text-center p-3 bg-white dark:bg-slate-700 rounded">
                      <div className="text-xl font-bold">{selectedLang.data.results.score}</div>
                      <div className="text-xs text-slate-500">Score</div>
                    </div>
                    <div className="text-center p-3 bg-white dark:bg-slate-700 rounded">
                      <div className="text-xl font-bold">{selectedLang.data.results.missing_keys_count}</div>
                      <div className="text-xs text-slate-500">Missing Keys</div>
                    </div>
                    <div className="text-center p-3 bg-white dark:bg-slate-700 rounded">
                      <div className="text-xl font-bold">{selectedLang.data.results.placeholder_errors?.length || 0}</div>
                      <div className="text-xs text-slate-500">Placeholder Errors</div>
                    </div>
                    <div className="text-center p-3 bg-white dark:bg-slate-700 rounded">
                      <div className="text-xl font-bold">{selectedLang.data.results.expansion_warnings?.length || 0}</div>
                      <div className="text-xs text-slate-500">Expansion Warnings</div>
                    </div>
                  </div>

                  {/* Missing Keys List */}
                  {selectedLang.data.results.missing_keys?.length > 0 && (
                    <div className="mt-4">
                      <h4 className="font-medium text-sm mb-2">Missing Keys ({selectedLang.data.results.missing_keys.length})</h4>
                      <div className="max-h-40 overflow-y-auto bg-white dark:bg-slate-700 rounded p-2">
                        {selectedLang.data.results.missing_keys.slice(0, 20).map((key, i) => (
                          <code key={i} className="block text-xs py-1 border-b border-slate-100 dark:border-slate-600 last:border-0">
                            {key}
                          </code>
                        ))}
                        {selectedLang.data.results.missing_keys.length > 20 && (
                          <div className="text-xs text-slate-500 mt-2">
                            ...and {selectedLang.data.results.missing_keys.length - 20} more
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Issues Tab */}
        <TabsContent value="issues" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Critical Issues</CardTitle>
              <CardDescription>Issues that need immediate attention</CardDescription>
            </CardHeader>
            <CardContent>
              {details?.critical_issues?.length > 0 ? (
                <div className="space-y-3">
                  {details.critical_issues.map((issue, i) => (
                    <IssueItem key={i} issue={issue} priority="critical" />
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-slate-500">
                  <CheckCircle className="w-12 h-12 mx-auto mb-2 text-green-500" />
                  <p>No critical issues found!</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Recommendations Tab */}
        <TabsContent value="recommendations" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Recommendations</CardTitle>
              <CardDescription>Prioritized actions to improve translation quality</CardDescription>
            </CardHeader>
            <CardContent>
              {details?.recommendations?.length > 0 ? (
                <div className="space-y-4">
                  {details.recommendations.map((rec, i) => (
                    <RecommendationCard key={i} recommendation={rec} />
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-slate-500">
                  <TrendingUp className="w-12 h-12 mx-auto mb-2 text-green-500" />
                  <p>All translations are in great shape!</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Details Tab */}
        <TabsContent value="details" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">QA Run Details</CardTitle>
              <CardDescription>Technical details from the last QA run</CardDescription>
            </CardHeader>
            <CardContent>
              {details && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded">
                      <div className="text-xs text-slate-500">Run ID</div>
                      <div className="font-mono text-sm">{details.run_id}</div>
                    </div>
                    <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded">
                      <div className="text-xs text-slate-500">Duration</div>
                      <div className="font-mono text-sm">{details.duration_ms}ms</div>
                    </div>
                    <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded">
                      <div className="text-xs text-slate-500">Status</div>
                      <Badge variant={details.status === "completed" ? "default" : "destructive"}>
                        {details.status}
                      </Badge>
                    </div>
                    <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded">
                      <div className="text-xs text-slate-500">Timestamp</div>
                      <div className="text-sm">{new Date(details.timestamp).toLocaleString()}</div>
                    </div>
                  </div>

                  {/* Summary Stats */}
                  <div className="mt-4">
                    <h4 className="font-medium mb-2">Summary Statistics</h4>
                    <pre className="bg-slate-900 text-green-400 p-4 rounded text-xs overflow-x-auto">
                      {JSON.stringify(details.summary, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default TranslationQADashboard;
