/**
import { useTranslation } from "@/utils/i18n";
 * Global AI Compliance Dashboard
 * Complete 2026 Global Coverage: EU, UK, US, Canada, Singapore, China, South Korea, Japan, Brazil, Africa, ASEAN
 * Implements Global Unified Audit Log (GUAL) for cross-border compliance
 */
import React, { useState, useEffect } from 'react';
import { toast } from 'sonner';
import {
  Globe,
  Shield,
  Scale,
  FileText,
  AlertTriangle,
  CheckCircle,
  Clock,
  Download,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  MapPin,
  Flag,
  Activity,
  Database,
  Lock,
  Eye,
  UserCheck,
  AlertCircle,
  TrendingUp,
  Calendar,
  FileCheck,
  Zap,
  Server
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
    'ALIGNED': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
    'INTEGRATED': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
    'WARNING': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
    'NORMAL': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
  };
  return <Badge className={styles[status] || 'bg-gray-100 text-gray-800'}>{status}</Badge>;
};

const RegionCard = ({ region, flag, status, laws, onClick, expanded }) => (
  <div className="border rounded-lg overflow-hidden hover:shadow-md transition-shadow">
    <button
      onClick={onClick}
      className="w-full p-4 flex items-center justify-between hover:bg-muted/50 transition-colors"
    >
      <div className="flex items-center gap-3">
        <span className="text-2xl">{flag}</span>
        <div className="text-left">
          <p className="font-medium">{region}</p>
          <p className="text-xs text-muted-foreground">{laws}</p>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <StatusBadge status={status} />
        {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
      </div>
    </button>
  </div>
);

export default function GlobalCompliancePage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [globalSummary, setGlobalSummary] = useState(null);
  const [singapore, setSingapore] = useState(null);
  const [china, setChina] = useState(null);
  const [southKorea, setSouthKorea] = useState(null);
  const [japan, setJapan] = useState(null);
  const [canada, setCanada] = useState(null);
  const [colorado, setColorado] = useState(null);
  const [brazil, setBrazil] = useState(null);
  const [africa, setAfrica] = useState(null);
  const [asean, setAsean] = useState(null);
  const [incidents, setIncidents] = useState(null);
  const [biasReport, setBiasReport] = useState(null);
  const [expandedRegions, setExpandedRegions] = useState({});

  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    setLoading(true);
    try {
      const [sumRes, sgRes, cnRes, krRes, jpRes, caRes, coRes, brRes, afRes, asRes, incRes, biasRes] = await Promise.all([
        fetch(`${API_URL}/api/global-compliance/summary`).then(r => r.json()),
        fetch(`${API_URL}/api/global-compliance/asia-pacific/singapore`).then(r => r.json()),
        fetch(`${API_URL}/api/global-compliance/asia-pacific/china`).then(r => r.json()),
        fetch(`${API_URL}/api/global-compliance/asia-pacific/south-korea`).then(r => r.json()),
        fetch(`${API_URL}/api/global-compliance/asia-pacific/japan`).then(r => r.json()),
        fetch(`${API_URL}/api/global-compliance/north-america/canada`).then(r => r.json()),
        fetch(`${API_URL}/api/global-compliance/north-america/colorado`).then(r => r.json()),
        fetch(`${API_URL}/api/global-compliance/south-america/brazil`).then(r => r.json()),
        fetch(`${API_URL}/api/global-compliance/africa`).then(r => r.json()),
        fetch(`${API_URL}/api/global-compliance/asia-pacific/asean`).then(r => r.json()),
        fetch(`${API_URL}/api/global-compliance/incidents/check`).then(r => r.json()),
        fetch(`${API_URL}/api/global-compliance/reports/annual-bias-audit`).then(r => r.json()),
      ]);
      setGlobalSummary(sumRes);
      setSingapore(sgRes);
      setChina(cnRes);
      setSouthKorea(krRes);
      setJapan(jpRes);
      setCanada(caRes);
      setColorado(coRes);
      setBrazil(brRes);
      setAfrica(afRes);
      setAsean(asRes);
      setIncidents(incRes);
      setBiasReport(biasRes);
    } catch (error) {
      console.error('Error:', error);
      toast.error('Failed to load global compliance data');
    } finally {
      setLoading(false);
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
          <p className="text-muted-foreground">Loading Global Compliance Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6" data-testid="global-compliance-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Globe className="h-7 w-7 text-turquoise" />
            Global AI Compliance Dashboard
          </h1>
          <p className="text-muted-foreground mt-1">
            2026 Cross-Border Compliance • {globalSummary?.regions_covered} Regions • {globalSummary?.laws_tracked} Laws Tracked
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={loadAllData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export GUAL
          </Button>
        </div>
      </div>

      {/* Global Status Banner */}
      <Card className={`border-2 ${globalSummary?.global_compliance_status === 'COMPLIANT' ? 'border-green-500 bg-green-50 dark:bg-green-900/20' : 'border-yellow-500 bg-yellow-50'}`}>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <CheckCircle className="h-10 w-10 text-green-600" />
              <div>
                <h2 className="text-xl font-bold text-green-800 dark:text-green-400">
                  Global Compliance Status: {globalSummary?.global_compliance_status}
                </h2>
                <p className="text-sm text-green-700 dark:text-green-500">
                  Cross-border hiring enabled • GUAL active • Highest standard: EU AI Act
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-muted-foreground">Active Incidents</p>
              <p className="text-2xl font-bold text-green-600">{globalSummary?.incident_status?.active_incidents || 0}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6 text-center">
            <Globe className="h-8 w-8 mx-auto mb-2 text-turquoise" />
            <p className="text-2xl font-bold">{globalSummary?.regions_covered}</p>
            <p className="text-sm text-muted-foreground">Regions Covered</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 text-center">
            <FileText className="h-8 w-8 mx-auto mb-2 text-blue-500" />
            <p className="text-2xl font-bold">{globalSummary?.laws_tracked}</p>
            <p className="text-sm text-muted-foreground">Laws Tracked</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 text-center">
            <Shield className="h-8 w-8 mx-auto mb-2 text-green-500" />
            <p className="text-2xl font-bold">GUAL</p>
            <p className="text-sm text-muted-foreground">Unified Audit Log</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 text-center">
            <Clock className="h-8 w-8 mx-auto mb-2 text-yellow-500" />
            <p className="text-2xl font-bold">96h</p>
            <p className="text-sm text-muted-foreground">Incident Reporting</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5 lg:w-auto lg:inline-grid">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="asia-pacific">Asia-Pacific</TabsTrigger>
          <TabsTrigger value="americas">Americas</TabsTrigger>
          <TabsTrigger value="emerging">Africa & ASEAN</TabsTrigger>
          <TabsTrigger value="reports">Reports</TabsTrigger>
        </TabsList>

        {/* OVERVIEW TAB */}
        <TabsContent value="overview" className="space-y-6">
          {/* Upcoming Deadlines */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5 text-turquoise" />
                2026 Compliance Deadlines
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {globalSummary?.next_deadlines?.map((deadline, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className={`w-3 h-3 rounded-full ${
                        deadline.status === 'COMPLIANT' ? 'bg-green-500' : 'bg-blue-500'
                      }`} />
                      <div>
                        <p className="font-medium">{deadline.region} - {deadline.law}</p>
                        <p className="text-sm text-muted-foreground">Deadline: {deadline.date}</p>
                      </div>
                    </div>
                    <StatusBadge status={deadline.status} />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Regional Status Grid */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapPin className="h-5 w-5 text-turquoise" />
                Regional Compliance Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
                {globalSummary?.regional_status && Object.entries(globalSummary.regional_status).map(([key, data]) => (
                  <div key={key} className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <p className="font-medium capitalize">{key.replace('_', ' ')}</p>
                      <p className="text-xs text-muted-foreground">{data.law || data.framework || data.deadline}</p>
                    </div>
                    <StatusBadge status={data.status} />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* GUAL Structure */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5 text-turquoise" />
                Global Unified Audit Log (GUAL)
              </CardTitle>
              <CardDescription>
                Cross-border compliance logging structure for extraterritorial jurisdiction
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="p-4 bg-muted/50 rounded-lg">
                  <h4 className="font-medium mb-2">GUAL Entry Structure</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between"><span>audit_event_id</span><span className="text-muted-foreground">Unique identifier</span></div>
                    <div className="flex justify-between"><span>jurisdiction_context</span><span className="text-muted-foreground">Candidate + Employer locations</span></div>
                    <div className="flex justify-between"><span>applicable_laws</span><span className="text-muted-foreground">Auto-detected regulations</span></div>
                    <div className="flex justify-between"><span>explainability_data</span><span className="text-muted-foreground">Top factors + bias check</span></div>
                    <div className="flex justify-between"><span>human_oversight</span><span className="text-muted-foreground">Review status + reviewer ID</span></div>
                    <div className="flex justify-between"><span>integrity</span><span className="text-muted-foreground">SHA-256 hash + AES-256</span></div>
                  </div>
                </div>
                <div className="p-4 bg-muted/50 rounded-lg">
                  <h4 className="font-medium mb-2">Golden Rules</h4>
                  <div className="space-y-3">
                    <div className="flex items-start gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
                      <div>
                        <p className="font-medium text-sm">Highest Common Denominator</p>
                        <p className="text-xs text-muted-foreground">Log to EU AI Act standard (satisfies 90% of global requirements)</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
                      <div>
                        <p className="font-medium text-sm">Regional Data Residency</p>
                        <p className="text-xs text-muted-foreground">PII stored locally, anonymized metadata centralized</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
                      <div>
                        <p className="font-medium text-sm">96-Hour Rule</p>
                        <p className="text-xs text-muted-foreground">Auto-alert for bias anomalies or system failures</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ASIA-PACIFIC TAB */}
        <TabsContent value="asia-pacific" className="space-y-6">
          {/* Singapore */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="text-2xl">🇸🇬</span>
                Singapore - Workplace Fairness Act & AI Verify
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium mb-3">Regulations</h4>
                  {singapore?.regulations?.map((reg, idx) => (
                    <div key={idx} className="p-3 border rounded-lg mb-2">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-medium">{reg.name}</span>
                        <StatusBadge status={reg.status} />
                      </div>
                      {reg.effective_date && <p className="text-xs text-muted-foreground">Effective: {reg.effective_date}</p>}
                    </div>
                  ))}
                </div>
                <div>
                  <h4 className="font-medium mb-3">Selection Rates (Protected Characteristics)</h4>
                  {singapore?.selection_rates && Object.entries(singapore.selection_rates).map(([char, data]) => (
                    <div key={char} className="p-3 border rounded-lg mb-2">
                      <div className="flex justify-between items-center">
                        <span className="capitalize">{char.replace('_', ' ')}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-sm">Impact: {data.impact_ratio}</span>
                          <StatusBadge status={data.status} />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* China */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="text-2xl">🇨🇳</span>
                China - PIPL, Algorithm Filing & Synthetic Content
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {china?.regulations?.map((reg, idx) => (
                  <div key={idx} className="p-4 border rounded-lg">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium">{reg.name}</span>
                      <StatusBadge status={reg.status} />
                    </div>
                    {reg.filing && (
                      <div className="text-sm text-muted-foreground">
                        Filing #: {reg.filing.filing_number} • Date: {reg.filing.filing_date}
                      </div>
                    )}
                    {reg.requirements?.ai_content_labeling && (
                      <div className="mt-2 p-2 bg-yellow-50 dark:bg-yellow-900/20 rounded">
                        <p className="text-sm">AI Content Label: {reg.requirements.label_format}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* South Korea & Japan */}
          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <span className="text-xl">🇰🇷</span>
                  South Korea - AI Basic Act
                </CardTitle>
              </CardHeader>
              <CardContent>
                {southKorea?.regulations?.map((reg, idx) => (
                  <div key={idx} className="p-3 border rounded-lg mb-2">
                    <div className="flex justify-between items-center">
                      <span className="font-medium text-sm">{reg.name}</span>
                      <StatusBadge status={reg.status} />
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">Effective: {reg.effective_date}</p>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <span className="text-xl">🇯🇵</span>
                  Japan - AI Strategy Guidelines
                </CardTitle>
              </CardHeader>
              <CardContent>
                {japan?.regulations?.map((reg, idx) => (
                  <div key={idx} className="p-3 border rounded-lg mb-2">
                    <div className="flex justify-between items-center">
                      <span className="font-medium text-sm">{reg.name}</span>
                      <StatusBadge status={reg.status} />
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">{reg.enforcement}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* AMERICAS TAB */}
        <TabsContent value="americas" className="space-y-6">
          {/* Canada */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="text-2xl">🇨🇦</span>
                Canada - AIDA & Ontario ESA Amendment
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  {canada?.regulations?.map((reg, idx) => (
                    <div key={idx} className="p-4 border rounded-lg mb-3">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-medium">{reg.name}</span>
                        <StatusBadge status={reg.status} />
                      </div>
                      <p className="text-sm text-muted-foreground">Effective: {reg.effective_date}</p>
                      {reg.requirements?.record_retention && (
                        <div className="mt-2 p-2 bg-blue-50 dark:bg-blue-900/20 rounded">
                          <p className="text-sm">Records retained: {reg.requirements.record_retention.records_retained.toLocaleString()}</p>
                          <p className="text-xs text-muted-foreground">Retention: {reg.requirements.record_retention.current_retention}</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
                <div>
                  <h4 className="font-medium mb-3">Hiring Decision Logs</h4>
                  <div className="p-4 border rounded-lg">
                    <p className="text-2xl font-bold text-turquoise">{canada?.hiring_decision_logs?.total_logged?.toLocaleString()}</p>
                    <p className="text-sm text-muted-foreground">Total logged decisions</p>
                    <p className="text-sm mt-2">Retention: {canada?.hiring_decision_logs?.retention_period}</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Colorado */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="text-2xl">🏔️</span>
                Colorado AI Act (SB 205) - Effective June 30, 2026
              </CardTitle>
            </CardHeader>
            <CardContent>
              {colorado?.regulations?.map((reg, idx) => (
                <div key={idx}>
                  <div className="flex justify-between items-center mb-4">
                    <StatusBadge status={reg.status} />
                    <span className="text-sm text-muted-foreground">Deadline: {reg.effective_date}</span>
                  </div>
                  <div className="grid md:grid-cols-2 gap-4">
                    {reg.requirements && Object.entries(reg.requirements).map(([key, value]) => (
                      <div key={key} className="p-3 border rounded-lg">
                        <div className="flex justify-between items-center mb-2">
                          <span className="font-medium capitalize">{key.replace(/_/g, ' ')}</span>
                          <StatusBadge status={value.status} />
                        </div>
                        <p className="text-xs text-muted-foreground">{value.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        {/* EMERGING MARKETS TAB */}
        <TabsContent value="emerging" className="space-y-6">
          {/* Brazil */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="text-2xl">🇧🇷</span>
                Brazil - Bill 2338/2023 & LGPD
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {brazil?.regulations?.map((reg, idx) => (
                  <div key={idx} className="p-4 border rounded-lg">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium">{reg.name}</span>
                      <StatusBadge status={reg.status} />
                    </div>
                    {reg.requirements?.right_to_contest && (
                      <div className="mt-2 p-2 bg-green-50 dark:bg-green-900/20 rounded text-sm">
                        <p>Right to Contest: {reg.requirements.right_to_contest.contests_received} received, {reg.requirements.right_to_contest.contests_resolved} resolved</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Africa */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="text-2xl">🌍</span>
                Africa - AU AI Strategy Alignment
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-4 mb-4">
                {africa?.countries && Object.entries(africa.countries).map(([key, country]) => (
                  <div key={key} className="p-4 border rounded-lg text-center">
                    <span className="text-3xl">{country.flag}</span>
                    <p className="font-medium mt-2 capitalize">{key.replace('_', ' ')}</p>
                    <StatusBadge status={country.status} />
                    <p className="text-xs text-muted-foreground mt-2">{country.legislation}</p>
                  </div>
                ))}
              </div>
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <h4 className="font-medium mb-2">AU AI Strategy Alignment</h4>
                <div className="flex flex-wrap gap-2">
                  {africa?.au_ai_strategy_alignment && Object.entries(africa.au_ai_strategy_alignment).map(([key, value]) => (
                    value && <Badge key={key} variant="outline" className="capitalize">{key.replace(/_/g, ' ')}</Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* ASEAN */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="text-2xl">🌏</span>
                ASEAN - AI Governance & Ethics Guide
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium mb-3">Core Principles</h4>
                  {asean?.principles && Object.entries(asean.principles).map(([key, value]) => (
                    <div key={key} className="flex justify-between items-center p-2 border-b">
                      <span className="text-sm capitalize">{key.replace(/_/g, ' ')}</span>
                      <StatusBadge status={value.status} />
                    </div>
                  ))}
                </div>
                <div>
                  <h4 className="font-medium mb-3">Fact-Check Metadata</h4>
                  <div className="p-4 border rounded-lg">
                    <p className="text-2xl font-bold text-turquoise">{asean?.fact_check_metadata?.verification_rate}</p>
                    <p className="text-sm text-muted-foreground">Verification Rate</p>
                    <p className="text-sm mt-2">Checks: {asean?.fact_check_metadata?.checks_performed?.toLocaleString()}</p>
                    <p className="text-sm">Anomalies: {asean?.fact_check_metadata?.anomalies_detected}</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* REPORTS TAB */}
        <TabsContent value="reports" className="space-y-6">
          {/* Report Generation */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileCheck className="h-5 w-5 text-turquoise" />
                Auto-Generated Compliance Reports
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="p-4 border rounded-lg">
                  <FileText className="h-8 w-8 text-blue-500 mb-2" />
                  <h4 className="font-medium">Annual Bias Audit</h4>
                  <p className="text-sm text-muted-foreground mb-3">NYC LL 144 & California AEDT</p>
                  <Button size="sm" className="w-full">
                    <Download className="h-4 w-4 mr-2" />
                    Download
                  </Button>
                </div>
                <div className="p-4 border rounded-lg">
                  <FileText className="h-8 w-8 text-purple-500 mb-2" />
                  <h4 className="font-medium">EU Technical File</h4>
                  <p className="text-sm text-muted-foreground mb-3">EU AI Act Article 11</p>
                  <Button size="sm" className="w-full">
                    <Download className="h-4 w-4 mr-2" />
                    Download
                  </Button>
                </div>
                <div className="p-4 border rounded-lg">
                  <FileText className="h-8 w-8 text-green-500 mb-2" />
                  <h4 className="font-medium">Candidate Explanation</h4>
                  <p className="text-sm text-muted-foreground mb-3">GDPR Article 22</p>
                  <Button size="sm" className="w-full">
                    Generate
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Bias Audit Summary */}
          {biasReport && (
            <Card>
              <CardHeader>
                <CardTitle>Latest Bias Audit Report</CardTitle>
                <CardDescription>
                  Report ID: {biasReport.report_id} • Generated: {biasReport.generated_at}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-3 gap-4 mb-4">
                  {biasReport.disparate_impact_analysis && Object.entries(biasReport.disparate_impact_analysis)
                    .filter(([key]) => key !== 'methodology')
                    .map(([category, data]) => (
                    <div key={category} className="p-4 border rounded-lg">
                      <h4 className="font-medium capitalize mb-2">{category}</h4>
                      <div className="flex justify-between items-center">
                        <span>Impact Ratio</span>
                        <span className={`font-bold ${data.impact_ratio >= 0.80 ? 'text-green-600' : 'text-red-600'}`}>
                          {data.impact_ratio}
                        </span>
                      </div>
                      <StatusBadge status={data.status} />
                    </div>
                  ))}
                </div>
                <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                  <p className="text-sm">{biasReport.certification_statement}</p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* 96-Hour Incident Monitoring */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-yellow-500" />
                96-Hour Incident Monitoring
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium mb-3">Alert Thresholds</h4>
                  {incidents?.incident_thresholds && Object.entries(incidents.incident_thresholds).map(([key, data]) => (
                    <div key={key} className="flex justify-between items-center p-2 border-b">
                      <span className="text-sm capitalize">{key.replace(/_/g, ' ')}</span>
                      <StatusBadge status={data.current_status} />
                    </div>
                  ))}
                </div>
                <div>
                  <h4 className="font-medium mb-3">Reporting Windows</h4>
                  {incidents?.reporting_windows && Object.entries(incidents.reporting_windows).map(([region, window]) => (
                    <div key={region} className="flex justify-between items-center p-2 border-b text-sm">
                      <span className="capitalize">{region.replace(/_/g, ' ')}</span>
                      <span className="text-muted-foreground">{window}</span>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
