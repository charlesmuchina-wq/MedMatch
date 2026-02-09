/**
 * KARAU DRAGON AI Automator Dashboard
 * System diagnostics, auto-fixes, improvements, and version management
 */
import React, { useState, useEffect } from 'react';
import { toast } from 'sonner';
import {
  Activity,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Cpu,
  Database,
  Zap,
  Settings,
  RefreshCw,
  Wrench,
  Lightbulb,
  Upload,
  Bell,
  Shield,
  TrendingUp,
  Clock,
  ChevronRight,
  Play,
  Bot,
  Languages
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Progress } from '../components/ui/progress';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { apiClient } from '@/utils/apiClient';
import TranslationQADashboard from '../components/TranslationQADashboard';
import CAPADashboard from '../components/CAPADashboard';

// Status Badge Component
const StatusBadge = ({ status }) => {
  if (!status) {
    return (
      <Badge variant="outline" className="bg-gray-500/10 text-gray-500 border-gray-500/30">
        Unknown
      </Badge>
    );
  }
  
  const styles = {
    healthy: "bg-green-500/10 text-green-500 border-green-500/30",
    degraded: "bg-yellow-500/10 text-yellow-500 border-yellow-500/30",
    critical: "bg-red-500/10 text-red-500 border-red-500/30",
    improved: "bg-blue-500/10 text-blue-500 border-blue-500/30"
  };
  
  const icons = {
    healthy: <CheckCircle className="h-3 w-3" />,
    degraded: <AlertTriangle className="h-3 w-3" />,
    critical: <XCircle className="h-3 w-3" />,
    improved: <TrendingUp className="h-3 w-3" />
  };
  
  return (
    <Badge variant="outline" className={`${styles[status] || styles.degraded} flex items-center gap-1`}>
      {icons[status] || icons.degraded}
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </Badge>
  );
};

// Health Score Gauge
const HealthGauge = ({ score }) => {
  const getColor = (score) => {
    if (score >= 80) return "text-green-500";
    if (score >= 50) return "text-yellow-500";
    return "text-red-500";
  };
  
  return (
    <div className="relative w-32 h-32 mx-auto">
      <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
        <path
          d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
          fill="none"
          stroke="currentColor"
          className="text-muted/20"
          strokeWidth="3"
        />
        <path
          d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
          fill="none"
          stroke="currentColor"
          className={getColor(score)}
          strokeWidth="3"
          strokeDasharray={`${score}, 100`}
          strokeLinecap="round"
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center flex-col">
        <span className={`text-3xl font-bold ${getColor(score)}`}>{Math.round(score)}</span>
        <span className="text-xs text-muted-foreground">Health Score</span>
      </div>
    </div>
  );
};

// Diagnostic Card Component
const DiagnosticCard = ({ title, icon: Icon, status, metrics, issues }) => (
  <Card className="hover:shadow-md transition-shadow">
    <CardHeader className="pb-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Icon className="h-5 w-5 text-turquoise" />
          <CardTitle className="text-base">{title}</CardTitle>
        </div>
        <StatusBadge status={status} />
      </div>
    </CardHeader>
    <CardContent>
      {metrics && (
        <div className="grid grid-cols-2 gap-2 text-sm mb-3">
          {Object.entries(metrics).slice(0, 4).map(([key, value]) => (
            <div key={key} className="flex justify-between">
              <span className="text-muted-foreground">{key.replace(/_/g, ' ')}</span>
              <span className="font-medium">{typeof value === 'boolean' ? (value ? '✓' : '✗') : value}</span>
            </div>
          ))}
        </div>
      )}
      {issues && issues.length > 0 && (
        <div className="space-y-1">
          {issues.map((issue, idx) => (
            <div key={idx} className="flex items-center gap-2 text-sm">
              <Badge variant="outline" className={
                issue.severity === 'critical' ? 'bg-red-500/10 text-red-500' :
                issue.severity === 'high' ? 'bg-orange-500/10 text-orange-500' :
                'bg-yellow-500/10 text-yellow-500'
              }>
                {issue.severity}
              </Badge>
              <span className="text-muted-foreground truncate">{issue.description}</span>
              {issue.auto_fixable && <Wrench className="h-3 w-3 text-turquoise" />}
            </div>
          ))}
        </div>
      )}
      {(!issues || issues.length === 0) && (
        <p className="text-sm text-green-500 flex items-center gap-1">
          <CheckCircle className="h-4 w-4" /> No issues detected
        </p>
      )}
    </CardContent>
  </Card>
);

// Improvement Card Component
const ImprovementCard = ({ improvement, index, onImplement }) => (
  <Card className="hover:shadow-md transition-shadow">
    <CardContent className="p-4">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <Badge variant="outline" className={
              improvement.priority === 'high' ? 'bg-red-500/10 text-red-500' :
              improvement.priority === 'medium' ? 'bg-yellow-500/10 text-yellow-500' :
              'bg-blue-500/10 text-blue-500'
            }>
              {improvement.priority}
            </Badge>
            <Badge variant="outline">{improvement.category}</Badge>
          </div>
          <h4 className="font-semibold">{improvement.title}</h4>
          <p className="text-sm text-muted-foreground mt-1">{improvement.description}</p>
        </div>
        {improvement.auto_implementable && (
          <Button size="sm" onClick={() => onImplement(index)}>
            <Play className="h-4 w-4 mr-1" />
            Apply
          </Button>
        )}
      </div>
    </CardContent>
  </Card>
);

// Update Notification Component
const UpdateNotification = ({ update, onMarkRead }) => (
  <Card className={`${update.importance === 'critical' ? 'border-red-500/50' : ''}`}>
    <CardContent className="p-4">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="outline" className="bg-turquoise/10 text-turquoise">
              v{update.version}
            </Badge>
            <Badge variant="outline" className={
              update.importance === 'critical' ? 'bg-red-500/10 text-red-500' :
              update.importance === 'recommended' ? 'bg-yellow-500/10 text-yellow-500' :
              'bg-blue-500/10 text-blue-500'
            }>
              {update.importance}
            </Badge>
          </div>
          <h4 className="font-semibold">{update.title}</h4>
          <ul className="mt-2 space-y-1">
            {update.changes?.slice(0, 3).map((change, idx) => (
              <li key={idx} className="text-sm text-muted-foreground flex items-center gap-2">
                <ChevronRight className="h-3 w-3" />
                {change}
              </li>
            ))}
          </ul>
        </div>
        <Button variant="ghost" size="sm" onClick={onMarkRead}>
          <CheckCircle className="h-4 w-4" />
        </Button>
      </div>
    </CardContent>
  </Card>
);

export default function DragonAutomatorPage() {
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [health, setHealth] = useState(null);
  const [improvements, setImprovements] = useState([]);
  const [updates, setUpdates] = useState([]);
  const [version, setVersion] = useState(null);
  const [lastReport, setLastReport] = useState(null);

  // Helper to add delay between requests to prevent rate limiting
  const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

  const loadData = async () => {
    setLoading(true);
    try {
      // Stagger API calls to prevent rate limiting (thundering herd)
      // Load health first (critical data)
      try {
        const healthRes = await apiClient.get('/api/dragon/automator/health');
        setHealth(healthRes.data);
      } catch (err) {
        console.error('Health fetch failed:', err);
      }
      
      await delay(150); // Small delay between requests
      
      // Load improvements
      try {
        const improvementsRes = await apiClient.get('/api/dragon/automator/improvements');
        setImprovements(improvementsRes.data.suggestions || []);
      } catch (err) {
        console.error('Improvements fetch failed:', err);
      }
      
      await delay(150);
      
      // Load updates
      try {
        const updatesRes = await apiClient.get('/api/dragon/automator/updates');
        setUpdates(updatesRes.data.updates || []);
      } catch (err) {
        console.error('Updates fetch failed:', err);
      }
      
      await delay(150);
      
      // Load version info
      try {
        const versionRes = await apiClient.get('/api/dragon/automator/version');
        setVersion(versionRes.data);
      } catch (err) {
        console.error('Version fetch failed:', err);
      }
    } catch (error) {
      console.error('Failed to load automator data:', error);
      toast.error('Failed to load automator data');
    } finally {
      setLoading(false);
    }
  };

  const runFullAnalysis = async () => {
    setRunning(true);
    try {
      const response = await apiClient.post('/api/dragon/automator/analyze-and-fix');
      setLastReport(response.data.report);
      toast.success(`Analysis complete! ${response.data.report?.phases?.auto_fix?.fixes_applied || 0} fixes applied`);
      await loadData();
    } catch (error) {
      console.error('Analysis failed:', error);
      toast.error(error.response?.data?.detail || 'Analysis failed');
    } finally {
      setRunning(false);
    }
  };

  const applyAutoFixes = async () => {
    try {
      const response = await apiClient.post('/api/dragon/automator/auto-fix');
      toast.success(`Applied ${response.data.fixes_applied} fixes`);
      await loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Auto-fix failed');
    }
  };

  const implementImprovement = async (index) => {
    try {
      const response = await apiClient.post(`/api/dragon/automator/improvements/${index}/implement`);
      if (response.data.success) {
        toast.success('Improvement implemented successfully');
        await loadData();
      } else {
        toast.info(response.data.reason || 'Manual implementation required');
      }
    } catch (error) {
      toast.error('Failed to implement improvement');
    }
  };

  const markUpdatesRead = async () => {
    try {
      await apiClient.post('/api/dragon/automator/updates/mark-read');
      setUpdates([]);
      toast.success('Updates marked as read');
    } catch (error) {
      toast.error('Failed to mark updates');
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Bot className="h-16 w-16 animate-pulse text-turquoise mx-auto mb-4" />
          <p className="text-muted-foreground">KARAU DRAGON Automator initializing...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6" data-testid="dragon-automator-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Bot className="h-8 w-8 text-turquoise" />
            KARAU DRAGON AI Automator
          </h1>
          <p className="text-muted-foreground mt-1">
            Automatic diagnostics, fixes, improvements, and updates
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <Badge variant="outline" className="text-lg px-3 py-1">
            v{health?.version || version?.current_version || '2.3.0'}
          </Badge>
          <Button variant="outline" onClick={loadData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button 
            onClick={runFullAnalysis} 
            disabled={running}
            className="bg-turquoise hover:bg-turquoise/90"
          >
            {running ? (
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Zap className="h-4 w-4 mr-2" />
            )}
            Run Full Analysis
          </Button>
        </div>
      </div>

      {/* Update Notifications */}
      {updates.length > 0 && (
        <Card className="border-turquoise/30 bg-turquoise/5">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5 text-turquoise" />
                Pending Updates ({updates.length})
              </CardTitle>
              <Button variant="ghost" size="sm" onClick={markUpdatesRead}>
                Mark all read
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {updates.slice(0, 2).map((update, idx) => (
              <UpdateNotification key={idx} update={update} onMarkRead={markUpdatesRead} />
            ))}
          </CardContent>
        </Card>
      )}

      {/* Health Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Health Gauge */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-turquoise" />
              System Health
            </CardTitle>
          </CardHeader>
          <CardContent>
            <HealthGauge score={health?.health_score || 0} />
            <div className="mt-4 text-center">
              <StatusBadge status={health?.overall_status} />
              <p className="text-xs text-muted-foreground mt-2">
                Last checked: {new Date(health?.timestamp).toLocaleTimeString()}
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Quick Stats */}
        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 rounded-lg bg-muted/50">
                <AlertTriangle className="h-8 w-8 mx-auto mb-2 text-yellow-500" />
                <p className="text-2xl font-bold">{health?.total_issues || 0}</p>
                <p className="text-sm text-muted-foreground">Total Issues</p>
              </div>
              <div className="text-center p-4 rounded-lg bg-muted/50">
                <Wrench className="h-8 w-8 mx-auto mb-2 text-blue-500" />
                <p className="text-2xl font-bold">
                  {health?.issues?.filter(i => i.auto_fixable).length || 0}
                </p>
                <p className="text-sm text-muted-foreground">Auto-Fixable</p>
              </div>
              <div className="text-center p-4 rounded-lg bg-muted/50">
                <Lightbulb className="h-8 w-8 mx-auto mb-2 text-yellow-500" />
                <p className="text-2xl font-bold">{improvements.length}</p>
                <p className="text-sm text-muted-foreground">Improvements</p>
              </div>
              <div className="text-center p-4 rounded-lg bg-muted/50">
                <Shield className="h-8 w-8 mx-auto mb-2 text-green-500" />
                <p className="text-2xl font-bold">{version?.changelog?.length || 0}</p>
                <p className="text-sm text-muted-foreground">Updates Released</p>
              </div>
            </div>
            
            {health?.total_issues > 0 && (
              <Button className="w-full mt-4" onClick={applyAutoFixes}>
                <Wrench className="h-4 w-4 mr-2" />
                Apply Auto-Fixes ({health?.issues?.filter(i => i.auto_fixable).length || 0} available)
              </Button>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Tabs for Details */}
      <Tabs defaultValue="diagnostics" className="w-full">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="diagnostics">Diagnostics</TabsTrigger>
          <TabsTrigger value="improvements">Improvements</TabsTrigger>
          <TabsTrigger value="translation-qa" className="flex items-center gap-1">
            <Languages className="w-3 h-3" />
            Translation QA
          </TabsTrigger>
          <TabsTrigger value="capa" className="flex items-center gap-1">
            <Shield className="w-3 h-3" />
            CAPA
          </TabsTrigger>
          <TabsTrigger value="changelog">Changelog</TabsTrigger>
          <TabsTrigger value="reports">Reports</TabsTrigger>
        </TabsList>

        <TabsContent value="diagnostics" className="mt-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <DiagnosticCard
              title="Database"
              icon={Database}
              status={health?.diagnostics?.database?.status}
              metrics={health?.diagnostics?.database?.metrics}
              issues={health?.diagnostics?.database?.issues}
            />
            <DiagnosticCard
              title="API Services"
              icon={Zap}
              status={health?.diagnostics?.api?.status}
              metrics={health?.diagnostics?.api?.metrics}
              issues={health?.diagnostics?.api?.issues}
            />
            <DiagnosticCard
              title="AI Services"
              icon={Bot}
              status={health?.diagnostics?.ai_services?.status}
              metrics={health?.diagnostics?.ai_services?.metrics}
              issues={health?.diagnostics?.ai_services?.issues}
            />
            <DiagnosticCard
              title="Performance"
              icon={Cpu}
              status={health?.diagnostics?.performance?.status}
              metrics={health?.diagnostics?.performance?.metrics}
              issues={health?.diagnostics?.performance?.issues}
            />
          </div>
        </TabsContent>

        <TabsContent value="improvements" className="mt-4 space-y-4">
          {improvements.length > 0 ? (
            improvements.map((improvement, idx) => (
              <ImprovementCard
                key={idx}
                improvement={improvement}
                index={idx}
                onImplement={implementImprovement}
              />
            ))
          ) : (
            <Card>
              <CardContent className="py-12 text-center">
                <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-500" />
                <p className="text-lg font-medium">No improvements suggested</p>
                <p className="text-muted-foreground">Your system is running optimally!</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Translation QA Tab */}
        <TabsContent value="translation-qa" className="mt-4">
          <TranslationQADashboard />
        </TabsContent>

        <TabsContent value="changelog" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Version History</CardTitle>
            </CardHeader>
            <CardContent>
              {version?.changelog?.length > 0 ? (
                <div className="space-y-4">
                  {version.changelog.map((entry, idx) => (
                    <div key={idx} className="border-l-2 border-turquoise pl-4 py-2">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="outline" className="bg-turquoise/10 text-turquoise">
                          v{entry.version}
                        </Badge>
                        <Badge variant="outline">{entry.type}</Badge>
                        <span className="text-sm text-muted-foreground">
                          {new Date(entry.release_date).toLocaleDateString()}
                        </span>
                      </div>
                      <ul className="space-y-1">
                        {entry.changes?.map((change, cIdx) => (
                          <li key={cIdx} className="text-sm flex items-center gap-2">
                            <ChevronRight className="h-3 w-3 text-turquoise" />
                            {change}
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-muted-foreground py-8">
                  No version history available
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="reports" className="mt-4">
          {lastReport ? (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  Latest Analysis Report
                </CardTitle>
                <CardDescription>
                  Generated: {new Date(lastReport.timestamp).toLocaleString()}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div className="text-center p-4 bg-muted/50 rounded-lg">
                    <p className="text-3xl font-bold">{lastReport.phases?.diagnostics?.total_issues || 0}</p>
                    <p className="text-sm text-muted-foreground">Issues Found</p>
                  </div>
                  <div className="text-center p-4 bg-muted/50 rounded-lg">
                    <p className="text-3xl font-bold text-green-500">
                      {lastReport.phases?.auto_fix?.fixes_applied || 0}
                    </p>
                    <p className="text-sm text-muted-foreground">Fixes Applied</p>
                  </div>
                  <div className="text-center p-4 bg-muted/50 rounded-lg">
                    <p className="text-3xl font-bold text-yellow-500">
                      {lastReport.phases?.improvements?.suggestions || 0}
                    </p>
                    <p className="text-sm text-muted-foreground">Suggestions</p>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <h4 className="font-semibold">Summary</h4>
                  <div className="flex items-center gap-4">
                    <span className="text-muted-foreground">Health Before:</span>
                    <StatusBadge status={lastReport.summary?.health_before} />
                    <ChevronRight className="h-4 w-4" />
                    <span className="text-muted-foreground">After:</span>
                    <StatusBadge status={lastReport.summary?.health_after} />
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="py-12 text-center">
                <Bot className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-lg font-medium">No reports yet</p>
                <p className="text-muted-foreground mb-4">Run a full analysis to generate a report</p>
                <Button onClick={runFullAnalysis} disabled={running}>
                  <Zap className="h-4 w-4 mr-2" />
                  Run Analysis
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
