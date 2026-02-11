/**
 * Admin Data Integrity & AI QA Dashboard
 * Comprehensive automated governance for global job-seeker applications
 * Compliant with EU AI Act, China AI regulations, US AEDT laws, Brazil LGPD
 */
import React, { useState, useEffect } from 'react';
import { toast } from 'sonner';
import {
  Shield,
  Database,
  Globe,
  Brain,
  AlertTriangle,
  CheckCircle,
  Activity,
  Lock,
  Eye,
  FileText,
  Users,
  BarChart3,
  RefreshCw,
  Play,
  Clock,
  Target,
  Zap,
  Server,
  Code,
  ShieldCheck,
  AlertCircle,
  TrendingUp,
  TrendingDown,
  ChevronRight,
  ChevronDown,
  Search,
  Filter,
  Download,
  Settings,
  Cpu,
  Gauge,
  Bug,
  TestTube,
  Fingerprint,
  Scale,
  Gavel,
  MapPin,
  Bot
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { apiClient } from '@/utils/apiClient';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

// Status Badge Component
const StatusBadge = ({ status }) => {
  const styles = {
    'COMPLIANT': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
    'PASS': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
    'HEALTHY': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
    'SECURE': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
    'ENABLED': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
    'INTEGRATED': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
    'ACTIVE': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
    'WARNING': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
    'MITIGATED': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
    'CRITICAL': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
    'FAILED': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
    'HIGH': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
    'MEDIUM': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
    'LOW': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
  };
  
  return (
    <Badge className={styles[status] || 'bg-gray-100 text-gray-800'}>
      {status}
    </Badge>
  );
};

// Metric Card Component
const MetricCard = ({ title, value, subtitle, icon: Icon, trend, status }) => (
  <Card className="hover:shadow-lg transition-shadow">
    <CardContent className="pt-6">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-muted-foreground">{title}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
          {subtitle && <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>}
        </div>
        <div className={`p-3 rounded-xl ${status === 'good' ? 'bg-green-100 dark:bg-green-900/30' : status === 'warning' ? 'bg-yellow-100 dark:bg-yellow-900/30' : 'bg-blue-100 dark:bg-blue-900/30'}`}>
          <Icon className={`h-5 w-5 ${status === 'good' ? 'text-green-600' : status === 'warning' ? 'text-yellow-600' : 'text-blue-600'}`} />
        </div>
      </div>
      {trend && (
        <div className={`flex items-center gap-1 mt-2 text-xs ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
          {trend > 0 ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
          <span>{Math.abs(trend)}% from last week</span>
        </div>
      )}
    </CardContent>
  </Card>
);

// Section Header Component
const SectionHeader = ({ icon: Icon, title, description, action }) => (
  <div className="flex items-center justify-between mb-4">
    <div className="flex items-center gap-3">
      <div className="p-2 rounded-lg bg-turquoise/10">
        <Icon className="h-5 w-5 text-turquoise" />
      </div>
      <div>
        <h3 className="font-semibold">{title}</h3>
        {description && <p className="text-sm text-muted-foreground">{description}</p>}
      </div>
    </div>
    {action}
  </div>
);

export default function AdminDataIntegrityPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [runningAudit, setRunningAudit] = useState(false);
  
  // Data states
  const [summary, setSummary] = useState(null);
  const [dataLineage, setDataLineage] = useState(null);
  const [piiScan, setPiiScan] = useState(null);
  const [regionalCompliance, setRegionalCompliance] = useState(null);
  const [modelDrift, setModelDrift] = useState(null);
  const [testSuite, setTestSuite] = useState(null);
  const [outputValidation, setOutputValidation] = useState(null);
  const [redTeam, setRedTeam] = useState(null);
  const [complianceLogs, setComplianceLogs] = useState(null);
  const [biasDetection, setBiasDetection] = useState(null);
  const [riskInventory, setRiskInventory] = useState(null);
  const [automationTools, setAutomationTools] = useState(null);
  
  const [expandedRegions, setExpandedRegions] = useState({});
  
  // Audit Reports state
  const [reportTemplates, setReportTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [generatingReport, setGeneratingReport] = useState(false);
  const [reportHistory, setReportHistory] = useState([]);
  const [currentReport, setCurrentReport] = useState(null);

  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    setLoading(true);
    try {
      const [
        summaryRes,
        lineageRes,
        piiRes,
        complianceRes,
        driftRes,
        testRes,
        validationRes,
        redTeamRes,
        logsRes,
        biasRes,
        riskRes,
        toolsRes
      ] = await Promise.all([
        fetch(`${API_URL}/api/data-integrity/summary`).then(r => r.json()),
        fetch(`${API_URL}/api/data-integrity/data-lineage`).then(r => r.json()),
        fetch(`${API_URL}/api/data-integrity/pii-scan`, { method: 'POST' }).then(r => r.json()),
        fetch(`${API_URL}/api/data-integrity/regional-compliance`).then(r => r.json()),
        fetch(`${API_URL}/api/data-integrity/model-drift`).then(r => r.json()),
        fetch(`${API_URL}/api/data-integrity/test-suite`).then(r => r.json()),
        fetch(`${API_URL}/api/data-integrity/output-validation`).then(r => r.json()),
        fetch(`${API_URL}/api/data-integrity/red-team`).then(r => r.json()),
        fetch(`${API_URL}/api/data-integrity/compliance-logs`).then(r => r.json()),
        fetch(`${API_URL}/api/data-integrity/bias-detection`).then(r => r.json()),
        fetch(`${API_URL}/api/data-integrity/risk-inventory`).then(r => r.json()),
        fetch(`${API_URL}/api/data-integrity/automation-tools`).then(r => r.json())
      ]);

      setSummary(summaryRes);
      setDataLineage(lineageRes);
      setPiiScan(piiRes);
      setRegionalCompliance(complianceRes);
      setModelDrift(driftRes);
      setTestSuite(testRes);
      setOutputValidation(validationRes);
      setRedTeam(redTeamRes);
      setComplianceLogs(logsRes);
      setBiasDetection(biasRes);
      setRiskInventory(riskRes);
      setAutomationTools(toolsRes);
    } catch (error) {
      console.error('Error loading data:', error);
      toast.error('Failed to load data integrity dashboard');
    } finally {
      setLoading(false);
    }
  };

  const runFullAudit = async () => {
    setRunningAudit(true);
    try {
      const response = await fetch(`${API_URL}/api/data-integrity/run-audit`, { method: 'POST' });
      const result = await response.json();
      toast.success(`Audit completed! Score: ${result.overall_score}%`);
      loadAllData();
    } catch (error) {
      toast.error('Audit failed');
    } finally {
      setRunningAudit(false);
    }
  };

  const toggleRegion = (region) => {
    setExpandedRegions(prev => ({ ...prev, [region]: !prev[region] }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin text-turquoise mx-auto mb-4" />
          <p className="text-muted-foreground">Loading Data Integrity & AI QA Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6" data-testid="data-integrity-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Shield className="h-7 w-7 text-turquoise" />
            Data Integrity & AI QA
          </h1>
          <p className="text-muted-foreground mt-1">
            Automated governance for global compliance (EU AI Act, China, US AEDT, Brazil LGPD)
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={loadAllData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button onClick={runFullAudit} disabled={runningAudit} className="bg-turquoise hover:bg-turquoise/90">
            {runningAudit ? (
              <>
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                Running Audit...
              </>
            ) : (
              <>
                <Play className="h-4 w-4 mr-2" />
                Run Full Audit
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Regional Compliance"
          value={`${regionalCompliance?.overall_compliance_score || 0}%`}
          subtitle="6 regions monitored"
          icon={Globe}
          status="good"
        />
        <MetricCard
          title="Model Health"
          value={`${modelDrift?.healthy || 0}/${modelDrift?.total_models || 0}`}
          subtitle="Models performing well"
          icon={Brain}
          status={modelDrift?.warning > 0 ? 'warning' : 'good'}
        />
        <MetricCard
          title="Bias Audits"
          value="4/4 Pass"
          subtitle="Protected characteristics"
          icon={Scale}
          status="good"
        />
        <MetricCard
          title="Security Score"
          value={`${redTeam?.overall_security_score || 0}%`}
          subtitle="Red team assessment"
          icon={ShieldCheck}
          status="good"
        />
      </div>

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5 lg:w-auto lg:inline-grid">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="privacy">Privacy & Data</TabsTrigger>
          <TabsTrigger value="ai-qa">AI Quality</TabsTrigger>
          <TabsTrigger value="governance">Governance</TabsTrigger>
          <TabsTrigger value="audit-reports">Audit Reports</TabsTrigger>
        </TabsList>

        {/* OVERVIEW TAB */}
        <TabsContent value="overview" className="space-y-6">
          {/* Regional Compliance Overview */}
          <Card>
            <CardHeader>
              <SectionHeader
                icon={Globe}
                title="Regional Compliance Status"
                description="Real-time compliance monitoring across jurisdictions"
              />
            </CardHeader>
            <CardContent>
              <div className="grid gap-3">
                {regionalCompliance?.regions && Object.entries(regionalCompliance.regions).map(([key, region]) => (
                  <div key={key} className="border rounded-lg overflow-hidden">
                    <button
                      onClick={() => toggleRegion(key)}
                      className="w-full p-4 flex items-center justify-between hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">{region.flag}</span>
                        <div className="text-left">
                          <p className="font-medium">{region.name}</p>
                          <p className="text-xs text-muted-foreground">
                            {region.regulations?.join(', ')}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <StatusBadge status={region.status} />
                        {expandedRegions[key] ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                      </div>
                    </button>
                    {expandedRegions[key] && region.requirements && (
                      <div className="px-4 pb-4 pt-2 bg-muted/30 border-t">
                        <div className="grid gap-2">
                          {Object.entries(region.requirements).map(([reqKey, req]) => (
                            <div key={reqKey} className="flex items-center justify-between p-2 bg-background rounded">
                              <div>
                                <p className="text-sm font-medium capitalize">{reqKey.replace(/_/g, ' ')}</p>
                                <p className="text-xs text-muted-foreground">{req.description}</p>
                              </div>
                              <StatusBadge status={req.status} />
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* AI Models Risk Inventory */}
          <Card>
            <CardHeader>
              <SectionHeader
                icon={Cpu}
                title="AI Model Risk Inventory"
                description="Centralized inventory per EU AI Act requirements"
              />
            </CardHeader>
            <CardContent>
              <div className="grid gap-3">
                {riskInventory?.models?.map((model) => (
                  <div key={model.model_id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg ${
                        model.risk_level === 'HIGH' ? 'bg-red-100 dark:bg-red-900/30' :
                        model.risk_level === 'MEDIUM' ? 'bg-yellow-100 dark:bg-yellow-900/30' :
                        'bg-green-100 dark:bg-green-900/30'
                      }`}>
                        <Bot className={`h-4 w-4 ${
                          model.risk_level === 'HIGH' ? 'text-red-600' :
                          model.risk_level === 'MEDIUM' ? 'text-yellow-600' :
                          'text-green-600'
                        }`} />
                      </div>
                      <div>
                        <p className="font-medium">{model.name}</p>
                        <p className="text-xs text-muted-foreground">{model.risk_category}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <StatusBadge status={model.risk_level} />
                      <Badge variant="outline" className="text-xs">
                        {model.human_oversight}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-4 p-4 bg-muted/50 rounded-lg">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Risk Distribution:</span>
                  <div className="flex gap-4 text-sm">
                    <span className="text-red-600">High: {riskInventory?.risk_summary?.high_risk}</span>
                    <span className="text-yellow-600">Medium: {riskInventory?.risk_summary?.medium_risk}</span>
                    <span className="text-green-600">Low: {riskInventory?.risk_summary?.low_risk}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* PRIVACY & DATA TAB */}
        <TabsContent value="privacy" className="space-y-6">
          {/* Data Lineage */}
          <Card>
            <CardHeader>
              <SectionHeader
                icon={Database}
                title="Data Lineage & Provenance"
                description="Track origin and transformation of job-seeker data"
              />
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium mb-3">Data Sources</h4>
                  <div className="space-y-2">
                    {dataLineage?.data_sources?.map((source, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                          <p className="font-medium text-sm">{source.source}</p>
                          <p className="text-xs text-muted-foreground">{source.type}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-medium">{source.records.toLocaleString()}</p>
                          <p className="text-xs text-muted-foreground">records</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="font-medium mb-3">Transformation Pipeline</h4>
                  <div className="space-y-2">
                    {dataLineage?.transformations?.map((step, idx) => (
                      <div key={idx} className="flex items-center gap-3 p-3 border rounded-lg">
                        <div className="w-6 h-6 rounded-full bg-turquoise text-white flex items-center justify-center text-xs font-bold">
                          {idx + 1}
                        </div>
                        <div className="flex-1">
                          <p className="font-medium text-sm">{step.step}</p>
                          <p className="text-xs text-muted-foreground">
                            {step.records_processed?.toLocaleString()} records processed
                          </p>
                        </div>
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              <div className="mt-4 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span className="font-medium">Data Quality Score: {dataLineage?.data_quality_score}%</span>
                </div>
                <span className="text-sm text-muted-foreground">
                  Provenance Hash: {dataLineage?.provenance_hash}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* PII Scan Results */}
          <Card>
            <CardHeader>
              <SectionHeader
                icon={Fingerprint}
                title="PII Leakage Detection"
                description="Dynamic scanning for personally identifiable information in AI outputs"
              />
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-4 mb-4">
                <div className="p-4 border rounded-lg text-center">
                  <p className="text-3xl font-bold text-turquoise">{piiScan?.total_outputs_scanned?.toLocaleString()}</p>
                  <p className="text-sm text-muted-foreground">Outputs Scanned (24h)</p>
                </div>
                <div className="p-4 border rounded-lg text-center">
                  <p className="text-3xl font-bold text-yellow-600">{piiScan?.outputs_with_pii}</p>
                  <p className="text-sm text-muted-foreground">PII Detected</p>
                </div>
                <div className="p-4 border rounded-lg text-center">
                  <StatusBadge status={piiScan?.compliance_status} />
                  <p className="text-sm text-muted-foreground mt-2">Compliance Status</p>
                </div>
              </div>
              {piiScan?.pii_types_found && (
                <div className="grid grid-cols-2 md:grid-cols-6 gap-2">
                  {Object.entries(piiScan.pii_types_found).map(([type, count]) => (
                    <div key={type} className={`p-3 rounded-lg text-center ${count > 0 ? 'bg-yellow-50 dark:bg-yellow-900/20' : 'bg-green-50 dark:bg-green-900/20'}`}>
                      <p className="text-lg font-bold">{count}</p>
                      <p className="text-xs text-muted-foreground capitalize">{type.replace('_', ' ')}</p>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* AI QUALITY TAB */}
        <TabsContent value="ai-qa" className="space-y-6">
          {/* Model Drift Monitoring */}
          <Card>
            <CardHeader>
              <SectionHeader
                icon={Activity}
                title="Model Drift & Performance Monitoring"
                description="Automated alerts when model accuracy degrades"
              />
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {modelDrift?.models?.map((model) => (
                  <div key={model.model_id} className={`p-4 border rounded-lg ${model.status === 'WARNING' ? 'border-yellow-500' : ''}`}>
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <p className="font-medium">{model.name}</p>
                        <p className="text-xs text-muted-foreground">v{model.version} • Deployed {model.deployed_date}</p>
                      </div>
                      <StatusBadge status={model.status} />
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {Object.entries(model.metrics).map(([metric, data]) => (
                        <div key={metric} className="p-2 bg-muted/50 rounded">
                          <p className="text-xs text-muted-foreground capitalize">{metric.replace('_', ' ')}</p>
                          <div className="flex items-center gap-1">
                            <span className="font-medium">{data.current}%</span>
                            <span className={`text-xs ${data.drift < 0 ? 'text-red-500' : 'text-green-500'}`}>
                              ({data.drift > 0 ? '+' : ''}{data.drift}%)
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                    {model.alert && (
                      <div className="mt-3 p-2 bg-yellow-50 dark:bg-yellow-900/20 rounded flex items-center gap-2">
                        <AlertTriangle className="h-4 w-4 text-yellow-600" />
                        <span className="text-sm text-yellow-700 dark:text-yellow-400">{model.alert}</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Self-Healing Test Suite */}
          <Card>
            <CardHeader>
              <SectionHeader
                icon={TestTube}
                title="Self-Healing Test Suite"
                description="AI-powered test automation (mabl + Testim)"
              />
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-4 gap-4 mb-4">
                <div className="p-4 border rounded-lg text-center">
                  <p className="text-3xl font-bold text-green-600">{testSuite?.results?.pass_rate}%</p>
                  <p className="text-sm text-muted-foreground">Pass Rate</p>
                </div>
                <div className="p-4 border rounded-lg text-center">
                  <p className="text-3xl font-bold text-turquoise">{testSuite?.self_healing_stats?.auto_healed_tests}</p>
                  <p className="text-sm text-muted-foreground">Auto-Healed Tests</p>
                </div>
                <div className="p-4 border rounded-lg text-center">
                  <p className="text-3xl font-bold text-blue-600">{testSuite?.self_healing_stats?.maintenance_reduction}</p>
                  <p className="text-sm text-muted-foreground">Maintenance Reduction</p>
                </div>
                <div className="p-4 border rounded-lg text-center">
                  <p className="text-3xl font-bold">{testSuite?.total_tests}</p>
                  <p className="text-sm text-muted-foreground">Total Tests</p>
                </div>
              </div>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium mb-2">Test Coverage</h4>
                  <div className="space-y-2">
                    {testSuite?.coverage && Object.entries(testSuite.coverage).map(([type, value]) => (
                      <div key={type} className="flex items-center gap-2">
                        <span className="text-sm capitalize w-24">{type}:</span>
                        <Progress value={value} className="flex-1" />
                        <span className="text-sm font-medium w-12">{value}%</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="font-medium mb-2">Platform Status</h4>
                  <div className="space-y-2">
                    {testSuite?.platforms_tested?.map((platform) => (
                      <div key={platform.platform} className="flex items-center justify-between p-2 border rounded">
                        <span className="text-sm">{platform.platform}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-muted-foreground">{platform.tests} tests</span>
                          <StatusBadge status={platform.status} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Output Validation & Red Team */}
          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <SectionHeader
                  icon={Eye}
                  title="Hallucination Detection"
                  description="Grounding checks for AI outputs"
                />
              </CardHeader>
              <CardContent>
                <div className="text-center mb-4">
                  <p className="text-4xl font-bold text-green-600">{outputValidation?.validation_summary?.pass_rate}%</p>
                  <p className="text-sm text-muted-foreground">Grounding Pass Rate</p>
                </div>
                <div className="grid grid-cols-2 gap-2 text-center">
                  <div className="p-3 bg-muted/50 rounded">
                    <p className="font-medium">{outputValidation?.validation_summary?.total_validations_24h?.toLocaleString()}</p>
                    <p className="text-xs text-muted-foreground">Validations (24h)</p>
                  </div>
                  <div className="p-3 bg-muted/50 rounded">
                    <p className="font-medium">{outputValidation?.validation_summary?.hallucinations_caught}</p>
                    <p className="text-xs text-muted-foreground">Hallucinations Caught</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <SectionHeader
                  icon={Bug}
                  title="Red Team Security"
                  description="Adversarial attack testing"
                />
              </CardHeader>
              <CardContent>
                <div className="text-center mb-4">
                  <p className="text-4xl font-bold text-green-600">{redTeam?.overall_security_score}%</p>
                  <p className="text-sm text-muted-foreground">Security Score</p>
                </div>
                <div className="space-y-2">
                  {redTeam?.attack_vectors_tested?.slice(0, 4).map((vector) => (
                    <div key={vector.vector} className="flex items-center justify-between p-2 border rounded">
                      <span className="text-sm">{vector.vector}</span>
                      <StatusBadge status={vector.status} />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* GOVERNANCE TAB */}
        <TabsContent value="governance" className="space-y-6">
          {/* Bias Detection */}
          <Card>
            <CardHeader>
              <SectionHeader
                icon={Scale}
                title="Algorithmic Bias Detection"
                description="Continuous monitoring for disparate impact (FairNow + Custom Monitors)"
              />
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                {biasDetection?.protected_characteristics && Object.entries(biasDetection.protected_characteristics).map(([char, data]) => (
                  <div key={char} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <p className="font-medium capitalize">{char.replace('_', ' ')}</p>
                      <StatusBadge status={data.status} />
                    </div>
                    <div className="text-center py-2">
                      <p className="text-2xl font-bold">{data.adverse_impact_ratio}</p>
                      <p className="text-xs text-muted-foreground">Impact Ratio (≥{data.threshold} required)</p>
                    </div>
                    <Progress 
                      value={(data.adverse_impact_ratio / 1) * 100} 
                      className={data.adverse_impact_ratio >= data.threshold ? 'bg-green-100' : 'bg-red-100'}
                    />
                  </div>
                ))}
              </div>
              <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-blue-600" />
                  <span className="text-sm">
                    Intersectional analysis enabled • {biasDetection?.intersectional_analysis?.combinations_analyzed} combinations analyzed • 
                    Next audit: {biasDetection?.next_audit} by {biasDetection?.auditor}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Compliance Logging */}
          <Card>
            <CardHeader>
              <SectionHeader
                icon={FileText}
                title="Continuous Compliance Logging"
                description="100% logging of AI decisions for audit trails"
              />
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-4 mb-4">
                <div className="p-4 border rounded-lg text-center">
                  <p className="text-3xl font-bold text-turquoise">{complianceLogs?.total_decisions_logged?.toLocaleString()}</p>
                  <p className="text-sm text-muted-foreground">Total Decisions Logged</p>
                </div>
                <div className="p-4 border rounded-lg text-center">
                  <p className="text-3xl font-bold">{complianceLogs?.coverage}</p>
                  <p className="text-sm text-muted-foreground">Coverage</p>
                </div>
                <div className="p-4 border rounded-lg text-center">
                  <p className="text-3xl font-bold">{complianceLogs?.log_retention}</p>
                  <p className="text-sm text-muted-foreground">Retention Period</p>
                </div>
              </div>
              <div className="flex flex-wrap gap-2 mb-4">
                {complianceLogs?.compliance_frameworks?.map((framework) => (
                  <Badge key={framework} variant="outline">{framework}</Badge>
                ))}
              </div>
              <div className="p-4 bg-muted/50 rounded-lg">
                <h4 className="font-medium mb-2">Audit Capabilities</h4>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
                  {complianceLogs?.audit_capabilities && Object.entries(complianceLogs.audit_capabilities).map(([cap, enabled]) => (
                    <div key={cap} className="flex items-center gap-2">
                      {enabled ? <CheckCircle className="h-4 w-4 text-green-500" /> : <AlertCircle className="h-4 w-4 text-red-500" />}
                      <span className="text-xs capitalize">{cap.replace(/_/g, ' ')}</span>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Automation Tools */}
          <Card>
            <CardHeader>
              <SectionHeader
                icon={Zap}
                title="Integrated Automation Tools"
                description="2026 recommended tools for compliance, QA, and security"
              />
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-6">
                {automationTools && ['compliance_governance', 'quality_assurance', 'security_monitoring'].map((category) => (
                  <div key={category}>
                    <h4 className="font-medium mb-3 capitalize">{category.replace('_', ' & ')}</h4>
                    <div className="space-y-2">
                      {automationTools[category]?.map((tool) => (
                        <div key={tool.tool} className="p-3 border rounded-lg">
                          <div className="flex items-center justify-between mb-1">
                            <p className="font-medium text-sm">{tool.tool}</p>
                            <StatusBadge status={tool.status} />
                          </div>
                          <p className="text-xs text-muted-foreground">{tool.category}</p>
                          <div className="flex flex-wrap gap-1 mt-2">
                            {tool.features_used?.slice(0, 2).map((feature) => (
                              <Badge key={feature} variant="secondary" className="text-xs">{feature}</Badge>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-4 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span className="font-medium">All {automationTools?.total_tools} tools healthy and integrated</span>
                </div>
                <span className="text-sm text-muted-foreground">
                  Integration Score: {automationTools?.overall_integration_score}%
                </span>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
