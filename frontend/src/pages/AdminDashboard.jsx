/**
 * Admin Dashboard - Central hub for admin functions
 * Only accessible to users with admin role
 */
import React, { useState, useEffect } from 'react';
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
  CheckCircle
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import api from '@/utils/apiClient';

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
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [systemHealth, setSystemHealth] = useState(null);
  const [stats, setStats] = useState({
    total_users: 0,
    active_users: 0,
    total_applications: 0,
    pending_issues: 0
  });
  const [schedulerStatus, setSchedulerStatus] = useState(null);

  // Helper to add delay between requests to prevent rate limiting
  const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

  const loadAdminData = async () => {
    setLoading(true);
    let healthData = null;
    
    try {
      // Stagger API calls to prevent rate limiting (thundering herd)
      // Load health first (critical data)
      try {
        const healthRes = await api.get('/api/dragon/automator/health');
        healthData = healthRes.data;
        setSystemHealth(healthData);
      } catch (err) {
        console.error('Health fetch failed:', err);
      }
      
      await delay(150); // Small delay between requests
      
      // Load scheduler status
      try {
        const schedulerRes = await api.get('/api/dragon/automator/scheduler-status');
        setSchedulerStatus(schedulerRes.data);
      } catch (err) {
        console.error('Scheduler status fetch failed:', err);
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
              api.post('/api/dragon/automator/auto-fix')
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
              api.post('/api/dragon/automator/version/release', {
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
    </div>
  );
}
