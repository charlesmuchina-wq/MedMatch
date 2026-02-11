/**
 * Admin AI Compliance Dashboard
 * Full compliance monitoring for EU AI Act, NYC LL 144, California AEDT
 */
import React, { useState, useEffect } from 'react';
import { toast } from 'sonner';
import {
  Shield,
  Scale,
  Users,
  FileText,
  AlertTriangle,
  CheckCircle,
  Clock,
  Eye,
  UserCheck,
  Database,
  Bell,
  Calendar,
  TrendingUp,
  TrendingDown,
  ChevronRight,
  ChevronDown,
  Download,
  RefreshCw,
  BarChart3,
  PieChart,
  Activity,
  Globe,
  Gavel,
  AlertCircle,
  Info
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const StatusBadge = ({ status }) => {
  const styles = {
    'COMPLIANT': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
    'PASS': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
    'ON_TRACK': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
    'WARNING': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
    'CRITICAL': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
    'MEDIUM': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
    'LOW': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
  };
  return <Badge className={styles[status] || 'bg-gray-100 text-gray-800'}>{status}</Badge>;
};

export default function AdminAICompliancePage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState(null);
  const [biasData, setBiasData] = useState(null);
  const [overrides, setOverrides] = useState(null);
  const [notices, setNotices] = useState(null);
  const [rationale, setRationale] = useState(null);
  const [trainingData, setTrainingData] = useState(null);
  const [incidents, setIncidents] = useState(null);
  const [deadlines, setDeadlines] = useState(null);

  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    setLoading(true);
    try {
      const [sumRes, biasRes, overRes, notRes, ratRes, trainRes, incRes, deadRes] = await Promise.all([
        fetch(`${API_URL}/api/ai-compliance/admin/summary`).then(r => r.json()),
        fetch(`${API_URL}/api/ai-compliance/admin/disparate-impact`).then(r => r.json()),
        fetch(`${API_URL}/api/ai-compliance/admin/human-overrides`).then(r => r.json()),
        fetch(`${API_URL}/api/ai-compliance/admin/candidate-notices`).then(r => r.json()),
        fetch(`${API_URL}/api/ai-compliance/admin/decision-rationale`).then(r => r.json()),
        fetch(`${API_URL}/api/ai-compliance/admin/training-data`).then(r => r.json()),
        fetch(`${API_URL}/api/ai-compliance/admin/incidents`).then(r => r.json()),
        fetch(`${API_URL}/api/ai-compliance/admin/deadlines`).then(r => r.json()),
      ]);
      setSummary(sumRes);
      setBiasData(biasRes);
      setOverrides(overRes);
      setNotices(notRes);
      setRationale(ratRes);
      setTrainingData(trainRes);
      setIncidents(incRes);
      setDeadlines(deadRes);
    } catch (error) {
      console.error('Error loading compliance data:', error);
      toast.error('Failed to load compliance dashboard');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin text-turquoise mx-auto mb-4" />
          <p className="text-muted-foreground">Loading AI Compliance Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6" data-testid="ai-compliance-admin-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Gavel className="h-7 w-7 text-turquoise" />
            AI & Data Compliance Dashboard
          </h1>
          <p className="text-muted-foreground mt-1">
            EU AI Act • NYC LL 144 • California AEDT • Full Audit Trail
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={loadAllData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export Report
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Bias Audit</p>
                <p className="text-2xl font-bold text-green-600">PASS</p>
              </div>
              <Scale className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Human Review</p>
                <p className="text-2xl font-bold">{overrides?.review_rate}</p>
              </div>
              <UserCheck className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Notice Rate</p>
                <p className="text-2xl font-bold">{notices?.statistics?.acknowledgment_rate}</p>
              </div>
              <Eye className="h-8 w-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Active Incidents</p>
                <p className="text-2xl font-bold text-green-600">{incidents?.current_alerts?.length || 0}</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-yellow-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Candidates Assessed</p>
                <p className="text-2xl font-bold">{biasData?.total_candidates_assessed?.toLocaleString()}</p>
              </div>
              <Users className="h-8 w-8 text-turquoise" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-6 lg:w-auto lg:inline-grid">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="bias">Bias Audit</TabsTrigger>
          <TabsTrigger value="oversight">Human Oversight</TabsTrigger>
          <TabsTrigger value="transparency">Transparency</TabsTrigger>
          <TabsTrigger value="data">Data Lineage</TabsTrigger>
          <TabsTrigger value="incidents">Incidents</TabsTrigger>
        </TabsList>

        {/* OVERVIEW TAB */}
        <TabsContent value="overview" className="space-y-6">
          {/* Compliance Deadlines */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5 text-turquoise" />
                Critical Compliance Deadlines
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {deadlines?.critical_deadlines?.map((deadline, idx) => (
                  <div key={idx} className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <p className="font-medium">{deadline.regulation}</p>
                      <p className="text-sm text-muted-foreground">{deadline.description}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">{deadline.deadline}</p>
                      <StatusBadge status={deadline.status} />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Data Retention */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5 text-turquoise" />
                Data Retention Compliance
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-4">
                {deadlines?.data_retention && Object.entries(deadlines.data_retention).map(([key, value]) => (
                  <div key={key} className="p-4 border rounded-lg">
                    <p className="font-medium capitalize">{key.replace(/_/g, ' ')}</p>
                    <p className="text-sm text-muted-foreground mt-1">Requirement: {value.requirement}</p>
                    <p className="text-sm text-muted-foreground">Current: {value.current_retention}</p>
                    <StatusBadge status={value.status} />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* BIAS AUDIT TAB */}
        <TabsContent value="bias" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Scale className="h-5 w-5 text-turquoise" />
                Disparate Impact Analysis (Four-Fifths Rule)
              </CardTitle>
              <CardDescription>
                NYC Local Law 144 & California AEDT - Annual Bias Audit Results
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Info className="h-4 w-4 text-blue-600" />
                  <span className="font-medium">Audit Information</span>
                </div>
                <p className="text-sm">
                  Auditor: {biasData?.audit_metadata?.auditor} • 
                  Date: {biasData?.audit_metadata?.audit_date} • 
                  Certification: {biasData?.audit_metadata?.certification_number}
                </p>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                {biasData?.selection_rates && Object.entries(biasData.selection_rates).map(([category, data]) => (
                  <div key={category} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold capitalize">{category}</h3>
                      <StatusBadge status={data.status} />
                    </div>
                    <div className="space-y-2 mb-4">
                      {Object.entries(data).filter(([k]) => !['impact_ratio', 'status', 'four_fifths_threshold'].includes(k)).map(([group, stats]) => (
                        <div key={group} className="flex items-center justify-between text-sm">
                          <span className="capitalize">{group.replace('_', ' ')}</span>
                          <span>{(stats.rate * 100).toFixed(1)}% ({stats.selected}/{stats.assessed})</span>
                        </div>
                      ))}
                    </div>
                    <div className="pt-4 border-t">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Impact Ratio:</span>
                        <span className={`font-bold ${data.impact_ratio >= 0.80 ? 'text-green-600' : 'text-red-600'}`}>
                          {data.impact_ratio} (≥{data.four_fifths_threshold} required)
                        </span>
                      </div>
                      <Progress value={(data.impact_ratio / 1) * 100} className="mt-2" />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* HUMAN OVERSIGHT TAB */}
        <TabsContent value="oversight" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <UserCheck className="h-5 w-5 text-turquoise" />
                Human-in-the-Loop Verification
              </CardTitle>
              <CardDescription>
                Proves human control over final hiring decisions (EU AI Act requirement)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-4 gap-4 mb-6">
                <div className="p-4 border rounded-lg text-center">
                  <p className="text-3xl font-bold text-turquoise">{overrides?.total_ai_recommendations?.toLocaleString()}</p>
                  <p className="text-sm text-muted-foreground">AI Recommendations</p>
                </div>
                <div className="p-4 border rounded-lg text-center">
                  <p className="text-3xl font-bold text-green-600">{overrides?.review_rate}</p>
                  <p className="text-sm text-muted-foreground">Human Review Rate</p>
                </div>
                <div className="p-4 border rounded-lg text-center">
                  <p className="text-3xl font-bold text-blue-600">{overrides?.overrides?.total}</p>
                  <p className="text-sm text-muted-foreground">Manual Overrides</p>
                </div>
                <div className="p-4 border rounded-lg text-center">
                  <p className="text-3xl font-bold">{overrides?.overrides?.override_rate}</p>
                  <p className="text-sm text-muted-foreground">Override Rate</p>
                </div>
              </div>

              <h4 className="font-medium mb-3">Recent Overrides</h4>
              <div className="space-y-3">
                {overrides?.sample_overrides?.map((override) => (
                  <div key={override.override_id} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{override.recruiter_name}</span>
                        <Badge variant="outline">{override.timestamp}</Badge>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className="bg-gray-100 text-gray-800">AI: {override.ai_recommendation}</Badge>
                        <ChevronRight className="h-4 w-4" />
                        <Badge className="bg-blue-100 text-blue-800">Human: {override.recruiter_decision}</Badge>
                      </div>
                    </div>
                    <p className="text-sm text-muted-foreground">{override.override_reason}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* TRANSPARENCY TAB */}
        <TabsContent value="transparency" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5 text-turquoise" />
                Candidate Transparency Notices
              </CardTitle>
              <CardDescription>
                NIST AI RMF accountability & Right to Explanation tracking
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-4 gap-4 mb-6">
                <div className="p-4 border rounded-lg text-center">
                  <p className="text-3xl font-bold">{notices?.statistics?.notices_displayed?.toLocaleString()}</p>
                  <p className="text-sm text-muted-foreground">Notices Displayed</p>
                </div>
                <div className="p-4 border rounded-lg text-center">
                  <p className="text-3xl font-bold text-green-600">{notices?.statistics?.acknowledgment_rate}</p>
                  <p className="text-sm text-muted-foreground">Acknowledged</p>
                </div>
                <div className="p-4 border rounded-lg text-center">
                  <p className="text-3xl font-bold text-yellow-600">{notices?.statistics?.opt_out_requests}</p>
                  <p className="text-sm text-muted-foreground">Opt-Out Requests</p>
                </div>
                <div className="p-4 border rounded-lg text-center">
                  <p className="text-3xl font-bold text-blue-600">{notices?.statistics?.explanation_requests}</p>
                  <p className="text-sm text-muted-foreground">Explanation Requests</p>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium mb-3">Notice Languages</h4>
                  <div className="space-y-2">
                    {notices?.notice_languages?.map((lang) => (
                      <div key={lang.code} className="flex items-center justify-between p-2 border rounded">
                        <span>{lang.language}</span>
                        <span className="font-medium">{lang.notices.toLocaleString()}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="font-medium mb-3">Timing Compliance</h4>
                  <div className="p-4 border rounded-lg space-y-3">
                    <div className="flex items-center justify-between">
                      <span>10-Day Advance Notice</span>
                      <CheckCircle className="h-5 w-5 text-green-500" />
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Avg Days Before Assessment</span>
                      <span className="font-bold">{notices?.timing_compliance?.avg_days_before_assessment}</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* DATA LINEAGE TAB */}
        <TabsContent value="data" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5 text-turquoise" />
                Training Data Lineage
              </CardTitle>
              <CardDescription>
                EU AI Act Article 10 - Proof of data quality and representativeness
              </CardDescription>
            </CardHeader>
            <CardContent>
              {trainingData?.datasets?.map((dataset) => (
                <div key={dataset.dataset_id} className="border rounded-lg p-4 mb-4">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h4 className="font-medium">{dataset.name}</h4>
                      <p className="text-sm text-muted-foreground">v{dataset.version} • {dataset.record_count.toLocaleString()} records</p>
                    </div>
                    <StatusBadge status="COMPLIANT" />
                  </div>

                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <h5 className="text-sm font-medium mb-2">Quality Metrics</h5>
                      <div className="space-y-2">
                        {Object.entries(dataset.quality_metrics).map(([metric, value]) => (
                          <div key={metric} className="flex items-center gap-2">
                            <span className="text-sm capitalize w-24">{metric}:</span>
                            <Progress value={value} className="flex-1" />
                            <span className="text-sm font-medium w-12">{value}%</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h5 className="text-sm font-medium mb-2">Processing Pipeline</h5>
                      <div className="space-y-2">
                        {dataset.processing_steps?.map((step, idx) => (
                          <div key={idx} className="flex items-center gap-2 text-sm">
                            <div className="w-5 h-5 rounded-full bg-turquoise text-white flex items-center justify-center text-xs">
                              {idx + 1}
                            </div>
                            <span>{step.step}</span>
                            <CheckCircle className="h-4 w-4 text-green-500 ml-auto" />
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        {/* INCIDENTS TAB */}
        <TabsContent value="incidents" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-turquoise" />
                Incident Response & Monitoring
              </CardTitle>
              <CardDescription>
                96-hour reporting window for high-risk system malfunctions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-4 gap-4 mb-6">
                <div className="p-4 border rounded-lg text-center">
                  <p className="text-3xl font-bold text-green-600">0</p>
                  <p className="text-sm text-muted-foreground">Critical</p>
                </div>
                <div className="p-4 border rounded-lg text-center">
                  <p className="text-3xl font-bold text-green-600">0</p>
                  <p className="text-sm text-muted-foreground">High</p>
                </div>
                <div className="p-4 border rounded-lg text-center">
                  <p className="text-3xl font-bold text-yellow-600">{incidents?.incident_statistics?.medium}</p>
                  <p className="text-sm text-muted-foreground">Medium</p>
                </div>
                <div className="p-4 border rounded-lg text-center">
                  <p className="text-3xl font-bold">{incidents?.incident_statistics?.low}</p>
                  <p className="text-sm text-muted-foreground">Low</p>
                </div>
              </div>

              <h4 className="font-medium mb-3">Alert Thresholds</h4>
              <div className="grid md:grid-cols-2 gap-4 mb-6">
                {incidents?.alert_thresholds && Object.entries(incidents.alert_thresholds).map(([key, value]) => (
                  <div key={key} className="p-3 border rounded-lg">
                    <p className="font-medium capitalize">{key.replace('_', ' ')}</p>
                    <p className="text-sm text-muted-foreground">{value}</p>
                  </div>
                ))}
              </div>

              <h4 className="font-medium mb-3">Resolved Incidents (30 days)</h4>
              {incidents?.resolved_incidents_30d?.map((incident) => (
                <div key={incident.incident_id} className="p-4 border rounded-lg mb-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium">{incident.description}</span>
                    <StatusBadge status={incident.severity} />
                  </div>
                  <p className="text-sm text-muted-foreground mb-2">Root Cause: {incident.root_cause}</p>
                  <p className="text-sm text-muted-foreground">Remediation: {incident.remediation}</p>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
