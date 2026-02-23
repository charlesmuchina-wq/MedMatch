/**
 * Admin Dashboard - Central hub for admin functions
 * Only accessible to users with admin role
 * Feature: 3 View Options - Admin, Job Seeker, Recruiter
 */
import React, { useState, useEffect } from 'react';
import { useTranslation } from "@/utils/i18n";
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import {
  Shield,
  Bot,
  BarChart3,
  Users,
  Settings,
  Database,
  Activity,
  Bell,
  Calendar,
  Zap,
  RefreshCw,
  ChevronRight,
  Lock,
  Unlock,
  Crown,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Brain,
  Gauge,
  History,
  Target,
  Globe,
  Languages,
  Briefcase,
  UserCircle,
  Eye,
  Volume2,
  Loader2
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { apiClient } from '@/utils/apiClient';

// View Mode Selector Component
const ViewModeSelector = ({ currentView, onViewChange }) => {
  const views = [
    { id: 'admin', label: 'Admin View', icon: Shield, description: 'Full administrative access' },
    { id: 'recruiter', label: 'Recruiter View', icon: Briefcase, description: 'See platform as a recruiter' },
    { id: 'jobseeker', label: 'Job Seeker View', icon: UserCircle, description: 'See platform as a job seeker' }
  ];

  return (
    <Card className="mb-6 border-2 border-dashed border-turquoise/30">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center gap-2">
          <Eye className="h-5 w-5 text-turquoise" />
          Platform View Mode
        </CardTitle>
        <CardDescription>Switch between different user perspectives to test the platform experience</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {views.map((view) => (
            <button
              key={view.id}
              onClick={() => onViewChange(view.id)}
              className={`p-4 rounded-xl border-2 text-left transition-all ${
                currentView === view.id
                  ? 'border-turquoise bg-turquoise/10 shadow-md'
                  : 'border-border hover:border-turquoise/50 hover:bg-muted/50'
              }`}
              data-testid={`view-mode-${view.id}`}
            >
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${currentView === view.id ? 'bg-turquoise text-white' : 'bg-muted'}`}>
                  <view.icon className="h-5 w-5" />
                </div>
                <div>
                  <p className="font-semibold">{view.label}</p>
                  <p className="text-xs text-muted-foreground">{view.description}</p>
                </div>
              </div>
              {currentView === view.id && (
                <Badge className="mt-2 bg-turquoise/20 text-turquoise text-xs">Active</Badge>
              )}
            </button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

// Admin Module Card
const AdminModuleCard = ({ title, description, icon: Icon, path, status, stats, onClick }) => (
  <Card 
    className="hover:shadow-lg transition-all cursor-pointer hover:border-turquoise/50 group"
    onClick={onClick}
  >
    <CardContent className="p-6">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-4">
          <div className="p-3 rounded-xl bg-turquoise/10 text-turquoise group-hover:bg-turquoise group-hover:text-white transition-colors">
            <Icon className="h-6 w-6" />
          </div>
          <div>
            <h3 className="font-semibold text-lg flex items-center gap-2">
              {title}
              {status === "active" && <Badge className="bg-green-500/10 text-green-500 text-xs">Active</Badge>}
              {status === "warning" && <Badge className="bg-yellow-500/10 text-yellow-500 text-xs">Warning</Badge>}
            </h3>
            <p className="text-sm text-muted-foreground">{description}</p>
          </div>
        </div>
        <ChevronRight className="h-5 w-5 text-muted-foreground group-hover:text-turquoise transition-colors" />
      </div>
      {stats && (
        <div className="mt-4 pt-4 border-t border-border/50 grid grid-cols-3 gap-4">
          {Object.entries(stats).map(([key, value]) => (
            <div key={key} className="text-center">
              <p className="text-xl font-bold">{value}</p>
              <p className="text-xs text-muted-foreground capitalize">{key.replace(/_/g, ' ')}</p>
            </div>
          ))}
        </div>
      )}
    </CardContent>
  </Card>
);

// Quick Stat Card
const QuickStatCard = ({ title, value, icon: Icon, trend, color = "turquoise" }) => {
  const colorClasses = {
    turquoise: "bg-turquoise/10 text-turquoise",
    green: "bg-green-500/10 text-green-500",
    yellow: "bg-yellow-500/10 text-yellow-500",
    red: "bg-red-500/10 text-red-500",
    purple: "bg-purple-500/10 text-purple-500"
  };

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div className={`p-2 rounded-lg ${colorClasses[color]}`}>
            <Icon className="h-5 w-5" />
          </div>
          {trend && (
            <Badge variant="outline" className={trend > 0 ? "text-green-500" : "text-red-500"}>
              {trend > 0 ? "+" : ""}{trend}%
            </Badge>
          )}
        </div>
        <p className="text-2xl font-bold mt-3">{value}</p>
        <p className="text-sm text-muted-foreground">{title}</p>
      </CardContent>
    </Card>
  );
};

export default function AdminDashboard() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('admin');
  const [systemHealth, setSystemHealth] = useState(null);
  const [stats, setStats] = useState({
    total_users: 0,
    active_users: 0,
    total_applications: 0,
    pending_issues: 0
  });
  const [schedulerStatus, setSchedulerStatus] = useState(null);
  const [mlPrediction, setMlPrediction] = useState(null);
  const [mlModelInfo, setMlModelInfo] = useState(null);
  const [rollbackStatus, setRollbackStatus] = useState(null);

  // Handle view mode change
  const handleViewChange = (mode) => {
    setViewMode(mode);
    if (mode === 'recruiter') {
      toast.info('Viewing platform as Recruiter', { description: 'Navigate to see recruiter-specific features' });
    } else if (mode === 'jobseeker') {
      toast.info('Viewing platform as Job Seeker', { description: 'Navigate to see job seeker features' });
    } else {
      toast.success('Admin view activated', { description: 'Full administrative access enabled' });
    }
  };

  // Helper to add delay between requests to prevent rate limiting
  const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

  const loadAdminData = async () => {
    setLoading(true);
    let healthData = null;
    
    try {
      // Stagger API calls to prevent rate limiting (thundering herd)
      // Load health first (critical data)
      try {
        const healthRes = await apiClient.get('/api/dragon/automator/health');
        healthData = healthRes.data;
        setSystemHealth(healthData);
      } catch (err) {
        console.error('Health fetch failed:', err);
      }
      
      await delay(150); // Small delay between requests
      
      // Load scheduler status
      try {
        const schedulerRes = await apiClient.get('/api/dragon/automator/scheduler-status');
        setSchedulerStatus(schedulerRes.data);
      } catch (err) {
        console.error('Scheduler status fetch failed:', err);
      }
      
      await delay(150);
      
      // Load ML predictor summary
      try {
        const mlRes = await apiClient.get('/api/ml-predictor/summary');
        setMlPrediction(mlRes.data);
      } catch (err) {
        console.error('ML prediction fetch failed:', err);
      }
      
      await delay(150);
      
      // Load ML model info
      try {
        const modelRes = await apiClient.get('/api/ml-model/info');
        setMlModelInfo(modelRes.data);
      } catch (err) {
        console.error('ML model info fetch failed:', err);
      }
      
      await delay(150);
      
      // Load rollback status
      try {
        const rollbackRes = await apiClient.get('/api/dragon/automator/rollback/check');
        setRollbackStatus(rollbackRes.data);
      } catch (err) {
        console.error('Rollback status fetch failed:', err);
      }

      // Set stats from health data
      setStats({
        total_users: 76,
        active_users: 45,
        total_applications: healthData?.diagnostics?.database?.metrics?.collections || 0,
        pending_issues: healthData?.total_issues || 0
      });
    } catch (error) {
      console.error('Failed to load admin data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAdminData();
  }, []);

  const adminModules = [
    {
      title: "KARAU Dragon Automator",
      description: "System diagnostics, auto-fixes, and maintenance",
      icon: Bot,
      path: "/dragon-automator",
      status: systemHealth?.overall_status === "healthy" ? "active" : "warning",
      stats: {
        health_score: systemHealth?.health_score || 0,
        issues: systemHealth?.total_issues || 0,
        version: systemHealth?.version || "2.4.0"
      }
    },
    {
      title: "Analytics Funnel",
      description: "Track application to offer conversion rates",
      icon: BarChart3,
      path: "/analytics-funnel",
      status: "active"
    },
    {
      title: "Production Metrics",
      description: "User engagement, AI usage, and business KPIs",
      icon: TrendingUp,
      path: "/admin/metrics",
      status: "active",
      stats: {
        sessions: "Live",
        ai_calls: "Active",
        funnel: "Tracking"
      }
    },
    {
      title: "User Management",
      description: "View and manage platform users",
      icon: Users,
      path: "/recruiter/candidates",
      status: "active",
      stats: {
        total: stats.total_users,
        active: stats.active_users,
        new_today: 3
      }
    },
    {
      title: "System Settings",
      description: "Configure platform settings and preferences",
      icon: Settings,
      path: "/settings",
      status: "active"
    },
    {
      title: "Interview Calendar",
      description: "Manage interviews and Google Calendar sync",
      icon: Calendar,
      path: "/interview-calendar",
      status: "active"
    },
    {
      title: "Meeting Notes",
      description: "Transcription and AI summaries",
      icon: Activity,
      path: "/meeting-notes",
      status: "active"
    },
    {
      title: "Translation Analytics",
      description: "Translation usage, memory, and quality metrics",
      icon: Globe,
      path: "/admin/translations",
      status: "active",
      stats: {
        languages: "55+",
        bundled: "25",
        gendered: "24"
      }
    },
    {
      title: "Review Moderation",
      description: "Approve or reject pending employer reviews",
      icon: Shield,
      path: "/admin/reviews",
      status: "active",
      stats: {
        pending: "Queue",
        approved: "History",
        quality: "Control"
      }
    }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <RefreshCw className="h-8 w-8 animate-spin text-turquoise" />
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6" data-testid="admin-dashboard">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Shield className="h-8 w-8 text-turquoise" />
            Admin Dashboard
          </h1>
          <p className="text-muted-foreground mt-1">
            System overview and administrative tools
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <Badge variant="outline" className="text-lg px-3 py-1 bg-turquoise/10 text-turquoise">
            <Crown className="h-4 w-4 mr-2" />
            Admin Access
          </Badge>
          <Button variant="outline" onClick={loadAdminData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* View Mode Selector - Admin, Recruiter, Job Seeker */}
      <ViewModeSelector currentView={viewMode} onViewChange={handleViewChange} />

      {/* Quick Navigation based on View Mode */}
      {viewMode !== 'admin' && (
        <Card className="bg-gradient-to-r from-turquoise/10 to-transparent border-turquoise/30">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Eye className="h-5 w-5 text-turquoise" />
                <span className="font-medium">
                  Currently viewing as: <span className="text-turquoise capitalize">{viewMode}</span>
                </span>
              </div>
              <Button 
                size="sm" 
                onClick={() => navigate(viewMode === 'recruiter' ? '/' : '/jobs')}
                className="bg-turquoise hover:bg-turquoise/90"
              >
                Go to {viewMode === 'recruiter' ? 'Recruiter Dashboard' : 'Job Search'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* System Health Banner */}
      <Card className={`border-2 ${
        systemHealth?.overall_status === 'healthy' ? 'border-green-500/30 bg-green-500/5' :
        systemHealth?.overall_status === 'degraded' ? 'border-yellow-500/30 bg-yellow-500/5' :
        'border-red-500/30 bg-red-500/5'
      }`}>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {systemHealth?.overall_status === 'healthy' ? (
                <CheckCircle className="h-10 w-10 text-green-500" />
              ) : (
                <AlertTriangle className="h-10 w-10 text-yellow-500" />
              )}
              <div>
                <h3 className="text-xl font-semibold">
                  System Status: {systemHealth?.overall_status?.toUpperCase() || 'UNKNOWN'}
                </h3>
                <p className="text-muted-foreground">
                  Health Score: {systemHealth?.health_score || 0}/100 | 
                  {systemHealth?.total_issues || 0} issues detected
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-3xl font-bold text-turquoise">{systemHealth?.health_score || 0}</p>
              <Progress value={systemHealth?.health_score || 0} className="w-32 h-2 mt-2" />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <QuickStatCard
          title="Total Users"
          value={stats.total_users}
          icon={Users}
          color="turquoise"
          trend={12}
        />
        <QuickStatCard
          title="Active Users"
          value={stats.active_users}
          icon={Activity}
          color="green"
          trend={5}
        />
        <QuickStatCard
          title="Scheduled Jobs"
          value={schedulerStatus?.jobs?.length || 0}
          icon={Calendar}
          color="purple"
        />
        <QuickStatCard
          title="Pending Issues"
          value={stats.pending_issues}
          icon={AlertTriangle}
          color={stats.pending_issues > 0 ? "yellow" : "green"}
        />
      </div>

      {/* ML Predictor Dashboard */}
      <Card className="border-2 border-purple-500/20 bg-gradient-to-br from-purple-500/5 to-transparent">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-purple-500" />
            ML Issue Predictor
            {mlModelInfo?.trained && (
              <Badge className="bg-purple-500/10 text-purple-500 text-xs">Model Trained</Badge>
            )}
          </CardTitle>
          <CardDescription>
            AI-powered system health prediction and issue detection
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Prediction Status */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">System Status</span>
                <Badge 
                  className={`text-xs ${
                    mlPrediction?.status === 'healthy' ? 'bg-green-500/10 text-green-500' :
                    mlPrediction?.status === 'critical' ? 'bg-red-500/10 text-red-500' :
                    mlPrediction?.status === 'warning' ? 'bg-yellow-500/10 text-yellow-500' :
                    'bg-gray-500/10 text-gray-500'
                  }`}
                >
                  {mlPrediction?.status?.toUpperCase() || 'ANALYZING'}
                </Badge>
              </div>
              
              <div className="relative">
                <div className="flex items-center justify-center">
                  <div className="relative w-32 h-32">
                    <svg className="w-32 h-32 transform -rotate-90">
                      <circle
                        cx="64"
                        cy="64"
                        r="56"
                        stroke="currentColor"
                        strokeWidth="8"
                        fill="none"
                        className="text-muted/20"
                      />
                      <circle
                        cx="64"
                        cy="64"
                        r="56"
                        stroke="currentColor"
                        strokeWidth="8"
                        fill="none"
                        strokeDasharray={`${(mlPrediction?.health_score || 0) * 3.51} 351`}
                        className={`${
                          (mlPrediction?.health_score || 0) >= 70 ? 'text-green-500' :
                          (mlPrediction?.health_score || 0) >= 40 ? 'text-yellow-500' :
                          'text-red-500'
                        }`}
                      />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className="text-3xl font-bold">{mlPrediction?.health_score || 0}</span>
                      <span className="text-xs text-muted-foreground">Health Score</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <p className="text-sm text-center text-muted-foreground">
                {mlPrediction?.status_message || 'Loading predictions...'}
              </p>
            </div>

            {/* Predictions by Severity */}
            <div className="space-y-4">
              <h4 className="text-sm font-medium flex items-center gap-2">
                <Target className="h-4 w-4" />
                Issues by Severity
              </h4>
              <div className="space-y-2">
                {['critical', 'high', 'medium', 'low'].map((severity) => {
                  const count = mlPrediction?.predictions_by_severity?.[severity] || 0;
                  const colors = {
                    critical: 'bg-red-500',
                    high: 'bg-orange-500',
                    medium: 'bg-yellow-500',
                    low: 'bg-blue-500'
                  };
                  const maxCount = Math.max(
                    ...Object.values(mlPrediction?.predictions_by_severity || { x: 1 })
                  ) || 1;
                  
                  return (
                    <div key={severity} className="flex items-center gap-3">
                      <span className="text-xs w-16 capitalize">{severity}</span>
                      <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                        <div 
                          className={`h-full ${colors[severity]} rounded-full transition-all`}
                          style={{ width: `${(count / maxCount) * 100}%` }}
                        />
                      </div>
                      <span className="text-xs font-medium w-6">{count}</span>
                    </div>
                  );
                })}
              </div>
              
              {mlPrediction?.metrics && (
                <div className="pt-4 border-t border-border/50 space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Error Rate</span>
                    <span className="font-medium">{mlPrediction.metrics.error_rate}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Avg Latency</span>
                    <span className="font-medium">{mlPrediction.metrics.avg_latency}</span>
                  </div>
                </div>
              )}
            </div>

            {/* Top Issues & Actions */}
            <div className="space-y-4">
              <h4 className="text-sm font-medium flex items-center gap-2">
                <AlertTriangle className="h-4 w-4" />
                Top Issues
              </h4>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {mlPrediction?.top_issues?.length > 0 ? (
                  mlPrediction.top_issues.map((issue, idx) => (
                    <div 
                      key={idx}
                      className={`p-3 rounded-lg text-xs ${
                        issue.severity === 'critical' ? 'bg-red-500/10 border border-red-500/20' :
                        issue.severity === 'high' ? 'bg-orange-500/10 border border-orange-500/20' :
                        'bg-yellow-500/10 border border-yellow-500/20'
                      }`}
                    >
                      <p className="font-medium">{issue.title}</p>
                      <p className="text-muted-foreground mt-1 line-clamp-2">{issue.description}</p>
                    </div>
                  ))
                ) : (
                  <div className="p-4 text-center text-muted-foreground text-sm">
                    <CheckCircle className="h-8 w-8 mx-auto mb-2 text-green-500" />
                    No issues detected
                  </div>
                )}
              </div>
              
              <div className="flex gap-2 pt-2">
                <Button 
                  size="sm" 
                  variant="outline" 
                  className="flex-1"
                  onClick={async () => {
                    try {
                      await apiClient.post('/api/ml-model/train?days=30');
                      toast.success('ML model training started');
                      loadAdminData();
                    } catch (err) {
                      toast.error('Training failed');
                    }
                  }}
                >
                  <Brain className="h-3 w-3 mr-1" />
                  Train Model
                </Button>
                <Button 
                  size="sm" 
                  variant="outline"
                  className="flex-1"
                  onClick={loadAdminData}
                >
                  <RefreshCw className="h-3 w-3 mr-1" />
                  Refresh
                </Button>
              </div>
            </div>
          </div>
          
          {/* Model Info */}
          {mlModelInfo?.trained && (
            <div className="mt-4 pt-4 border-t border-border/50">
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>Model v{mlModelInfo.version} | Accuracy: {(mlModelInfo.metrics?.accuracy * 100)?.toFixed(1)}% | F1: {(mlModelInfo.metrics?.f1_score * 100)?.toFixed(1)}%</span>
                <span>Trained: {new Date(mlModelInfo.trained_at).toLocaleDateString()}</span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Rollback Status */}
      {rollbackStatus && (
        <Card className={`border ${rollbackStatus.rollback_needed ? 'border-red-500/50 bg-red-500/5' : 'border-green-500/30 bg-green-500/5'}`}>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <History className={`h-6 w-6 ${rollbackStatus.rollback_needed ? 'text-red-500' : 'text-green-500'}`} />
                <div>
                  <h4 className="font-medium">Auto-Rollback Status</h4>
                  <p className="text-sm text-muted-foreground">
                    {rollbackStatus.rollback_needed 
                      ? `Rollback recommended: ${rollbackStatus.reasons?.join(', ')}`
                      : `System stable | Health: ${rollbackStatus.current_health}%`}
                  </p>
                </div>
              </div>
              {rollbackStatus.rollback_needed && rollbackStatus.recommendation?.target_snapshot && (
                <Button 
                  size="sm" 
                  variant="destructive"
                  onClick={async () => {
                    if (window.confirm('Execute rollback? This will restore system to previous state.')) {
                      try {
                        await apiClient.post('/api/dragon/automator/rollback/execute', {
                          snapshot_id: rollbackStatus.recommendation.target_snapshot
                        });
                        toast.success('Rollback executed successfully');
                        loadAdminData();
                      } catch (err) {
                        toast.error('Rollback failed');
                      }
                    }
                  }}
                >
                  <History className="h-4 w-4 mr-2" />
                  Execute Rollback
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Scheduler Status */}
      {schedulerStatus && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5 text-turquoise" />
              Scheduled Tasks
            </CardTitle>
            <CardDescription>
              Automated tasks managed by KARAU DRAGON
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {schedulerStatus.jobs?.map((job, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${schedulerStatus.running ? 'bg-green-500' : 'bg-red-500'}`} />
                    <div>
                      <p className="font-medium">{job.name}</p>
                      <p className="text-xs text-muted-foreground">{job.trigger}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm">Next Run</p>
                    <p className="text-xs text-muted-foreground">
                      {job.next_run ? new Date(job.next_run).toLocaleString() : 'Not scheduled'}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Admin Modules Grid */}
      <div>
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Lock className="h-5 w-5" />
          Admin Modules
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {adminModules.map((module, idx) => (
            <AdminModuleCard
              key={idx}
              {...module}
              onClick={() => navigate(module.path)}
            />
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          <Button 
            onClick={() => navigate('/dragon-automator')}
            className="bg-turquoise hover:bg-turquoise/90"
          >
            <Bot className="h-4 w-4 mr-2" />
            Run System Analysis
          </Button>
          <Button 
            variant="outline"
            onClick={() => {
              apiClient.post('/api/dragon/automator/auto-fix')
                .then(() => toast.success('Auto-fix completed'))
                .catch(() => toast.error('Auto-fix failed'));
            }}
          >
            <Zap className="h-4 w-4 mr-2" />
            Apply Auto-Fixes
          </Button>
          <Button 
            variant="outline"
            onClick={() => navigate('/analytics-funnel')}
          >
            <BarChart3 className="h-4 w-4 mr-2" />
            View Analytics
          </Button>
          <Button 
            variant="outline"
            onClick={() => {
              apiClient.post('/api/dragon/automator/version/release', {
                version: "2.4.1",
                type: "patch",
                changes: ["Bug fixes and improvements"]
              })
                .then((res) => toast.success(`Version released! ${res.data.notifications_sent} users notified`))
                .catch(() => toast.error('Release failed'));
            }}
          >
            <Bell className="h-4 w-4 mr-2" />
            Push Update
          </Button>
        </CardContent>
      </Card>

      {/* Tutorial Audio Generation */}
      <AudioGenerationCard />
    </div>
  );
}
