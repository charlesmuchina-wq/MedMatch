/**
 * AI QA Compliance Dashboard Component
 * 
 * Provides real-time visibility into AI compliance metrics including:
 * - Overall system health
 * - Bias monitoring
 * - Compliance scores
 * - Human oversight status
 * - DSAR tracking
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Progress } from '../components/ui/progress';
import { Alert, AlertDescription, AlertTitle } from '../components/ui/alert';
import {
  Shield,
  Activity,
  Users,
  FileText,
  AlertTriangle,
  CheckCircle,
  Clock,
  RefreshCw,
  Brain,
  Scale,
  Eye,
  Lock,
  UserCheck,
  ClipboardList,
  TrendingUp,
  AlertCircle,
  XCircle,
  ChevronRight
} from 'lucide-react';
import { apiClient } from '../utils/apiClient';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Status color mapping
const statusColors = {
  excellent: 'bg-green-500',
  good: 'bg-blue-500',
  needs_attention: 'bg-yellow-500',
  critical: 'bg-red-500',
  active: 'bg-green-500',
  stopped: 'bg-red-500',
  compliant: 'bg-green-500',
  non_compliant: 'bg-red-500',
  no_audits: 'bg-gray-500',
  no_assessments: 'bg-gray-500',
  ready: 'bg-blue-500'
};

const severityColors = {
  critical: 'destructive',
  high: 'destructive',
  warning: 'warning',
  medium: 'warning',
  low: 'secondary'
};

export default function AIQADashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [healthCard, setHealthCard] = useState(null);
  const [complianceChecklists, setComplianceChecklists] = useState({});
  const [auditSchedules, setAuditSchedules] = useState([]);
  const [overseers, setOverseers] = useState([]);
  const [dsarStats, setDsarStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  const fetchDashboardData = useCallback(async () => {
    try {
      const [dashboardRes, healthRes, checklistsRes, schedulesRes, overseersRes, dsarRes] = await Promise.all([
        fetch(`${API_URL}/api/ai-qa/dashboard`),
        fetch(`${API_URL}/api/ai-qa/dashboard/health-card`),
        fetch(`${API_URL}/api/ai-qa/compliance/checklists`),
        fetch(`${API_URL}/api/ai-qa/audits/schedules`),
        fetch(`${API_URL}/api/ai-qa/oversight/overseers`),
        fetch(`${API_URL}/api/ai-qa/dsar/stats`)
      ]);

      if (dashboardRes.ok) setDashboard(await dashboardRes.json());
      if (healthRes.ok) setHealthCard(await healthRes.json());
      if (checklistsRes.ok) setComplianceChecklists(await checklistsRes.json());
      if (schedulesRes.ok) setAuditSchedules(await schedulesRes.json());
      if (overseersRes.ok) setOverseers(await overseersRes.json());
      if (dsarRes.ok) setDsarStats(await dsarRes.json());
    } catch (error) {
      console.error('Error fetching AI QA data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, [fetchDashboardData]);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchDashboardData();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-primary" />
        <span className="ml-2">Loading AI QA Dashboard...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Shield className="w-6 h-6 text-primary" />
            AI QA Compliance Dashboard
          </h2>
          <p className="text-muted-foreground">
            2026 AI Act • GDPR • Regional Compliance Monitoring
          </p>
        </div>
        <Button onClick={handleRefresh} disabled={refreshing} variant="outline" size="sm">
          <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Alerts Banner */}
      {dashboard?.alerts?.length > 0 && (
        <div className="space-y-2">
          {dashboard.alerts.slice(0, 3).map((alert, idx) => (
            <Alert key={idx} variant={severityColors[alert.severity] || 'default'}>
              {alert.severity === 'critical' ? (
                <AlertCircle className="h-4 w-4" />
              ) : (
                <AlertTriangle className="h-4 w-4" />
              )}
              <AlertTitle className="capitalize">{alert.type} Alert</AlertTitle>
              <AlertDescription>{alert.message}</AlertDescription>
            </Alert>
          ))}
        </div>
      )}

      {/* Health Score Card */}
      {healthCard && (
        <Card className="border-2" style={{ borderColor: healthCard.status_color === 'green' ? '#22c55e' : healthCard.status_color === 'blue' ? '#3b82f6' : healthCard.status_color === 'yellow' ? '#eab308' : '#ef4444' }}>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className={`w-16 h-16 rounded-full flex items-center justify-center ${statusColors[healthCard.status] || 'bg-gray-500'}`}>
                  <span className="text-2xl font-bold text-white">{healthCard.overall_score}%</span>
                </div>
                <div>
                  <h3 className="text-xl font-semibold">Audit Health Score</h3>
                  <p className="text-muted-foreground capitalize">{healthCard.status}</p>
                </div>
              </div>
              <div className="flex gap-6">
                {healthCard.key_metrics?.slice(0, 4).map((metric, idx) => (
                  <div key={idx} className="text-center">
                    <p className="text-2xl font-bold">{metric.value}</p>
                    <p className="text-xs text-muted-foreground">{metric.name}</p>
                  </div>
                ))}
              </div>
              {healthCard.critical_alerts > 0 && (
                <Badge variant="destructive" className="text-lg px-4 py-2">
                  {healthCard.critical_alerts} Critical Alerts
                </Badge>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="overview" className="flex items-center gap-1">
            <Activity className="w-4 h-4" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="decisions" className="flex items-center gap-1">
            <Brain className="w-4 h-4" />
            AI Decisions
          </TabsTrigger>
          <TabsTrigger value="bias" className="flex items-center gap-1">
            <Scale className="w-4 h-4" />
            Bias Monitor
          </TabsTrigger>
          <TabsTrigger value="compliance" className="flex items-center gap-1">
            <ClipboardList className="w-4 h-4" />
            Compliance
          </TabsTrigger>
          <TabsTrigger value="oversight" className="flex items-center gap-1">
            <Eye className="w-4 h-4" />
            Oversight
          </TabsTrigger>
          <TabsTrigger value="dsar" className="flex items-center gap-1">
            <Lock className="w-4 h-4" />
            DSAR
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4 mt-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* AI Decisions Card */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Brain className="w-4 h-4" />
                  AI Decisions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold">{dashboard?.ai_decisions?.total_logged || 0}</p>
                <p className="text-sm text-muted-foreground">
                  {dashboard?.ai_decisions?.last_24h || 0} in last 24h
                </p>
                <div className="mt-2">
                  <div className="flex justify-between text-xs mb-1">
                    <span>Human Review Rate</span>
                    <span>{dashboard?.ai_decisions?.review_rate || 0}%</span>
                  </div>
                  <Progress value={dashboard?.ai_decisions?.review_rate || 0} className="h-2" />
                </div>
              </CardContent>
            </Card>

            {/* Bias Monitoring Card */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Scale className="w-4 h-4" />
                  Fairness Score
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold">
                  {dashboard?.bias_monitoring?.average_fairness_score?.toFixed(0) || 100}%
                </p>
                <Badge className={`mt-1 ${statusColors[dashboard?.bias_monitoring?.status] || 'bg-gray-500'}`}>
                  {dashboard?.bias_monitoring?.status || 'Ready'}
                </Badge>
                <p className="text-sm text-muted-foreground mt-2">
                  {dashboard?.bias_monitoring?.total_audits || 0} audits conducted
                </p>
              </CardContent>
            </Card>

            {/* Compliance Card */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" />
                  Compliance Score
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold">
                  {dashboard?.compliance?.average_score?.toFixed(0) || 0}%
                </p>
                <Badge className={`mt-1 ${statusColors[dashboard?.compliance?.status] || 'bg-gray-500'}`}>
                  {dashboard?.compliance?.status || 'No Assessments'}
                </Badge>
                <p className="text-sm text-muted-foreground mt-2">
                  {dashboard?.compliance?.total_assessments || 0} assessments
                </p>
              </CardContent>
            </Card>

            {/* DSAR Card */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  DSAR Requests
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold">{dsarStats?.pending || 0}</p>
                <p className="text-sm text-muted-foreground">pending requests</p>
                <Badge className={`mt-2 ${statusColors[dsarStats?.compliance_status] || 'bg-green-500'}`}>
                  {dsarStats?.compliance_status || 'Compliant'}
                </Badge>
                {dsarStats?.overdue > 0 && (
                  <p className="text-sm text-red-500 mt-1">{dsarStats.overdue} overdue!</p>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Health Components Breakdown */}
          <Card>
            <CardHeader>
              <CardTitle>Health Score Components</CardTitle>
              <CardDescription>Breakdown of overall AI QA health score</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-5 gap-4">
                {dashboard?.overall_health?.components && Object.entries(dashboard.overall_health.components).map(([key, value]) => (
                  <div key={key} className="text-center">
                    <div className="relative w-16 h-16 mx-auto">
                      <svg className="w-16 h-16 transform -rotate-90">
                        <circle cx="32" cy="32" r="28" fill="none" stroke="#e5e7eb" strokeWidth="4" />
                        <circle
                          cx="32" cy="32" r="28" fill="none"
                          stroke={value >= 80 ? '#22c55e' : value >= 60 ? '#eab308' : '#ef4444'}
                          strokeWidth="4"
                          strokeDasharray={`${value * 1.76} 176`}
                        />
                      </svg>
                      <span className="absolute inset-0 flex items-center justify-center text-sm font-bold">
                        {value.toFixed(0)}%
                      </span>
                    </div>
                    <p className="text-xs mt-2 capitalize">{key.replace(/_/g, ' ')}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* AI Decisions Tab */}
        <TabsContent value="decisions" className="space-y-4 mt-4">
          <div className="grid grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Decision Logging Status</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span>Total Decisions Logged</span>
                    <span className="font-bold">{dashboard?.ai_decisions?.total_logged || 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Human Reviewed</span>
                    <span className="font-bold">{dashboard?.ai_decisions?.human_reviewed || 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Review Rate</span>
                    <span className="font-bold">{dashboard?.ai_decisions?.review_rate || 0}%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Crypto-Shredding</span>
                    <Badge variant="outline" className="bg-green-50">Active</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Logged Data Fields</CardTitle>
                <CardDescription>2026 AI Act Compliant Logging</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  {[
                    { field: 'Model Provenance', icon: CheckCircle, status: 'active' },
                    { field: 'Input Context (Encrypted)', icon: Lock, status: 'active' },
                    { field: 'Decision Rationale', icon: Brain, status: 'active' },
                    { field: 'Feature Weights', icon: Scale, status: 'active' },
                    { field: 'Human Override Logs', icon: UserCheck, status: 'active' },
                    { field: 'Digital Signatures', icon: Shield, status: 'active' }
                  ].map((item, idx) => (
                    <div key={idx} className="flex items-center gap-2">
                      <item.icon className="w-4 h-4 text-green-500" />
                      <span>{item.field}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Bias Monitoring Tab */}
        <TabsContent value="bias" className="space-y-4 mt-4">
          <div className="grid grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Fairness Metrics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-1">
                      <span>Average Fairness Score</span>
                      <span className="font-bold">
                        {dashboard?.bias_monitoring?.average_fairness_score?.toFixed(1) || 100}%
                      </span>
                    </div>
                    <Progress 
                      value={dashboard?.bias_monitoring?.average_fairness_score || 100} 
                      className="h-3"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4 mt-4">
                    <div className="text-center p-3 bg-muted rounded-lg">
                      <p className="text-2xl font-bold">{dashboard?.bias_monitoring?.total_audits || 0}</p>
                      <p className="text-xs text-muted-foreground">Total Audits</p>
                    </div>
                    <div className="text-center p-3 bg-muted rounded-lg">
                      <p className="text-2xl font-bold">{dashboard?.bias_monitoring?.audits_with_issues || 0}</p>
                      <p className="text-xs text-muted-foreground">Issues Found</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Protected Classes Monitored</CardTitle>
                <CardDescription>Four-Fifths Rule Analysis</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {['Gender', 'Race/Ethnicity', 'Age', 'Disability', 'Nationality'].map((cls, idx) => (
                    <div key={idx} className="flex items-center justify-between p-2 bg-muted rounded">
                      <span>{cls}</span>
                      <Badge variant="outline" className="bg-green-50">Monitored</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Bias Alerts */}
          {dashboard?.bias_monitoring?.alerts?.length > 0 && (
            <Card className="border-yellow-500">
              <CardHeader>
                <CardTitle className="text-yellow-600">Bias Alerts</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {dashboard.bias_monitoring.alerts.map((alert, idx) => (
                    <Alert key={idx} variant="warning">
                      <AlertTriangle className="h-4 w-4" />
                      <AlertDescription>{alert.message}</AlertDescription>
                    </Alert>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Compliance Tab */}
        <TabsContent value="compliance" className="space-y-4 mt-4">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(complianceChecklists).map(([key, checklist]) => (
              <Card key={key}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm">{checklist.name}</CardTitle>
                  <CardDescription className="text-xs">v{checklist.version}</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-2xl font-bold">{checklist.items?.length || 0}</p>
                  <p className="text-xs text-muted-foreground">Requirements</p>
                  <Button variant="outline" size="sm" className="mt-2 w-full">
                    View Checklist <ChevronRight className="w-4 h-4 ml-1" />
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Audit Schedules */}
          <Card>
            <CardHeader>
              <CardTitle>Scheduled Audits</CardTitle>
              <CardDescription>Automated compliance audit schedules</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {auditSchedules.map((schedule, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                    <div className="flex items-center gap-3">
                      <Clock className="w-5 h-5 text-primary" />
                      <div>
                        <p className="font-medium">{schedule.name}</p>
                        <p className="text-xs text-muted-foreground capitalize">
                          {schedule.frequency} • {schedule.audit_type}
                        </p>
                      </div>
                    </div>
                    <Badge variant={schedule.enabled ? 'default' : 'secondary'}>
                      {schedule.enabled ? 'Active' : 'Disabled'}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Human Oversight Tab */}
        <TabsContent value="oversight" className="space-y-4 mt-4">
          <div className="grid grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">System Status</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${dashboard?.human_oversight?.system_status === 'active' ? 'bg-green-500' : 'bg-red-500'}`} />
                  <span className="text-xl font-bold capitalize">
                    {dashboard?.human_oversight?.system_status || 'Active'}
                  </span>
                </div>
                {dashboard?.human_oversight?.emergency_stop_active && (
                  <Alert variant="destructive" className="mt-2">
                    <AlertCircle className="h-4 w-4" />
                    <AlertTitle>EMERGENCY STOP ACTIVE</AlertTitle>
                  </Alert>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Designated Overseers</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold">{dashboard?.human_oversight?.active_overseers || 0}</p>
                <p className="text-sm text-muted-foreground">
                  of {dashboard?.human_oversight?.total_overseers || 0} total
                </p>
                <p className="text-xs mt-2">
                  {dashboard?.human_oversight?.training_complete || 0} training complete
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Override Activity</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold">{dashboard?.human_oversight?.total_overrides || 0}</p>
                <p className="text-sm text-muted-foreground">Total overrides</p>
                <p className="text-xs mt-2">
                  {dashboard?.human_oversight?.overrides_last_30_days || 0} in last 30 days
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Override Actions Breakdown */}
          {dashboard?.human_oversight?.override_actions && (
            <Card>
              <CardHeader>
                <CardTitle>Override Actions Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-4 gap-4">
                  {Object.entries(dashboard.human_oversight.override_actions).map(([action, count]) => (
                    <div key={action} className="text-center p-4 bg-muted rounded-lg">
                      <p className="text-2xl font-bold">{count}</p>
                      <p className="text-xs text-muted-foreground capitalize">{action}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Registered Overseers */}
          <Card>
            <CardHeader>
              <CardTitle>Registered Overseers</CardTitle>
            </CardHeader>
            <CardContent>
              {overseers.length === 0 ? (
                <p className="text-muted-foreground">No overseers registered yet</p>
              ) : (
                <div className="space-y-2">
                  {overseers.map((overseer, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                      <div className="flex items-center gap-3">
                        <UserCheck className="w-5 h-5 text-primary" />
                        <div>
                          <p className="font-medium">{overseer.name}</p>
                          <p className="text-xs text-muted-foreground capitalize">
                            {overseer.role?.replace(/_/g, ' ')} • {overseer.department}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {overseer.training_complete ? (
                          <Badge variant="default">Training Complete</Badge>
                        ) : (
                          <Badge variant="secondary">Training Required</Badge>
                        )}
                        <Badge variant={overseer.active ? 'outline' : 'destructive'}>
                          {overseer.active ? 'Active' : 'Inactive'}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* DSAR Tab */}
        <TabsContent value="dsar" className="space-y-4 mt-4">
          <div className="grid grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Total Requests</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold">{dsarStats?.total_requests || 0}</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Pending</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold text-yellow-600">{dsarStats?.pending || 0}</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Overdue</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold text-red-600">{dsarStats?.overdue || 0}</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Completed (30d)</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold text-green-600">{dsarStats?.completed_last_30_days || 0}</p>
              </CardContent>
            </Card>
          </div>

          {/* Request Types */}
          {dsarStats?.by_type && Object.keys(dsarStats.by_type).length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Requests by Type</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-4 gap-4">
                  {Object.entries(dsarStats.by_type).map(([type, count]) => (
                    <div key={type} className="text-center p-4 bg-muted rounded-lg">
                      <p className="text-2xl font-bold">{count}</p>
                      <p className="text-xs text-muted-foreground capitalize">{type}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Compliance Status */}
          <Card>
            <CardHeader>
              <CardTitle>GDPR DSAR Compliance</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-4">
                {dsarStats?.compliance_status === 'compliant' ? (
                  <>
                    <CheckCircle className="w-12 h-12 text-green-500" />
                    <div>
                      <p className="text-xl font-bold text-green-600">Compliant</p>
                      <p className="text-muted-foreground">All DSARs being processed within 30-day deadline</p>
                    </div>
                  </>
                ) : (
                  <>
                    <XCircle className="w-12 h-12 text-red-500" />
                    <div>
                      <p className="text-xl font-bold text-red-600">Non-Compliant</p>
                      <p className="text-muted-foreground">{dsarStats?.overdue || 0} requests past 30-day deadline</p>
                    </div>
                  </>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
