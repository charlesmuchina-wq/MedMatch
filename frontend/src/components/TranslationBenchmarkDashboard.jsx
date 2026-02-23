/**
 * Translation Benchmarking Dashboard
 * Shows KPI metrics, tier coverage, and auto-translation controls
 */
import React, { useState, useEffect } from 'react';
import { 
  BarChart3, Target, Globe, AlertTriangle, CheckCircle, 
  Play, RefreshCw, TrendingUp, Award, Zap, Bell, BellOff,
  ChevronDown, ChevronUp, Loader2
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Switch } from '@/components/ui/switch';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

// Grade color mapping
const gradeColors = {
  'A+': 'bg-emerald-500',
  'A': 'bg-green-500',
  'B+': 'bg-lime-500',
  'B': 'bg-yellow-500',
  'C': 'bg-orange-500',
  'D': 'bg-red-400',
  'F': 'bg-red-600'
};

// Status colors
const statusColors = {
  excellent: 'text-emerald-500',
  good: 'text-green-500',
  needs_improvement: 'text-yellow-500',
  critical: 'text-red-500'
};

// Tier badge colors
const tierBadgeColors = {
  tier1: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
  tier2: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  tier3: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
};

const TranslationBenchmarkDashboard = () => {
  const [benchmark, setBenchmark] = useState(null);
  const [loading, setLoading] = useState(true);
  const [autoTranslating, setAutoTranslating] = useState(false);
  const [translationJob, setTranslationJob] = useState(null);
  const [alertThreshold, setAlertThreshold] = useState(90);
  const [alertsEnabled, setAlertsEnabled] = useState(true);
  const [expandedTiers, setExpandedTiers] = useState({});
  const [targetKpi, setTargetKpi] = useState(95);

  useEffect(() => {
    fetchBenchmark();
  }, []);

  // Poll for translation job status
  useEffect(() => {
    if (!translationJob || translationJob.status === 'completed') return;
    
    const interval = setInterval(async () => {
      try {
        const res = await axios.get(`${API}/api/translation-qa/auto-translate/${translationJob.job_id}`);
        setTranslationJob(res.data);
        
        if (res.data.status === 'completed') {
          toast.success(`Auto-translation complete! ${res.data.keys_translated} keys translated.`);
          setAutoTranslating(false);
          fetchBenchmark();
        }
      } catch (err) {
        console.error('Status check failed:', err);
      }
    }, 3000);
    
    return () => clearInterval(interval);
  }, [translationJob]);

  const fetchBenchmark = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/api/translation-qa/benchmark`);
      setBenchmark(res.data);
      setAlertThreshold(res.data.alert_config?.threshold || 90);
      setAlertsEnabled(res.data.alert_config?.enabled ?? true);
    } catch (err) {
      console.error('Failed to fetch benchmark:', err);
      toast.error('Failed to load benchmark data');
    }
    setLoading(false);
  };

  const startAutoTranslation = async (dryRun = false) => {
    try {
      setAutoTranslating(true);
      const res = await axios.post(`${API}/api/translation-qa/auto-translate`, {
        target_kpi: targetKpi,
        dry_run: dryRun
      });
      
      if (dryRun) {
        toast.info(`Dry run: Would translate ${res.data.total_keys_to_translate} keys in ${res.data.languages_to_translate} languages`);
        setAutoTranslating(false);
      } else {
        setTranslationJob(res.data);
        toast.info(`Started auto-translation for ${res.data.languages_to_translate} languages...`);
      }
    } catch (err) {
      setAutoTranslating(false);
      toast.error('Failed to start auto-translation');
    }
  };

  const updateAlertConfig = async () => {
    try {
      await axios.post(`${API}/api/translation-qa/benchmark/alerts`, {
        threshold: alertThreshold,
        enabled: alertsEnabled
      });
      toast.success(`Alerts ${alertsEnabled ? 'enabled' : 'disabled'} at ${alertThreshold}%`);
    } catch (err) {
      toast.error('Failed to update alert config');
    }
  };

  const toggleTierExpanded = (tierId) => {
    setExpandedTiers(prev => ({ ...prev, [tierId]: !prev[tierId] }));
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="py-12 flex items-center justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-turquoise" />
        </CardContent>
      </Card>
    );
  }

  if (!benchmark) return null;

  const { summary, tiers, languages, alerts, industry_comparison } = benchmark;

  return (
    <div className="space-y-6">
      {/* Header with KPI Overview */}
      <Card className="border-2 border-turquoise/30 bg-gradient-to-br from-slate-900/50 to-slate-800/50">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-xl flex items-center gap-2">
                <Target className="w-6 h-6 text-turquoise" />
                Translation Benchmark Dashboard
              </CardTitle>
              <CardDescription>
                Industry-standard KPI monitoring • Last updated: {new Date(benchmark.timestamp).toLocaleString()}
              </CardDescription>
            </div>
            <Button variant="outline" size="sm" onClick={fetchBenchmark}>
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {/* KPI Summary Grid */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
            <div className="bg-slate-800/50 rounded-xl p-4 text-center">
              <div className="text-3xl font-bold text-turquoise">{summary.total_ui_keys}</div>
              <div className="text-sm text-slate-400">Total UI Keys</div>
            </div>
            <div className="bg-slate-800/50 rounded-xl p-4 text-center">
              <div className="text-3xl font-bold text-cyan-400">{summary.total_languages}</div>
              <div className="text-sm text-slate-400">Languages</div>
            </div>
            <div className="bg-slate-800/50 rounded-xl p-4 text-center">
              <div className="text-3xl font-bold text-green-400">{summary.overall_average_coverage}%</div>
              <div className="text-sm text-slate-400">Avg Coverage</div>
            </div>
            <div className="bg-slate-800/50 rounded-xl p-4 text-center">
              <div className="text-3xl font-bold text-emerald-400">{summary.languages_at_95_percent}</div>
              <div className="text-sm text-slate-400">At 95%+ KPI</div>
            </div>
            <div className="bg-slate-800/50 rounded-xl p-4 text-center">
              <div className={`text-3xl font-bold ${gradeColors[summary.overall_grade]} bg-clip-text text-transparent bg-gradient-to-r from-white to-white`}>
                <span className={`inline-block px-3 py-1 rounded-lg text-white ${gradeColors[summary.overall_grade]}`}>
                  {summary.overall_grade}
                </span>
              </div>
              <div className="text-sm text-slate-400">Overall Grade</div>
            </div>
          </div>

          {/* Alerts Section */}
          {alerts && alerts.length > 0 && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 mb-6">
              <div className="flex items-center gap-2 text-red-400 font-medium mb-2">
                <AlertTriangle className="w-5 h-5" />
                {alerts.length} Language{alerts.length > 1 ? 's' : ''} Below {alertThreshold}% Threshold
              </div>
              <div className="flex flex-wrap gap-2">
                {alerts.slice(0, 10).map(alert => (
                  <Badge key={alert.language} variant="outline" className="text-red-400 border-red-400/50">
                    {alert.language}: {alert.coverage}%
                  </Badge>
                ))}
                {alerts.length > 10 && (
                  <Badge variant="outline" className="text-red-400 border-red-400/50">
                    +{alerts.length - 10} more
                  </Badge>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Auto-Translation Control Panel */}
      <Card className="border-2 border-purple-500/30">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Zap className="w-5 h-5 text-purple-400" />
            Auto-Translation Engine
          </CardTitle>
          <CardDescription>
            AI-powered translation to meet KPI targets automatically
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <label className="text-sm text-slate-400">Target KPI:</label>
              <Input 
                type="number" 
                value={targetKpi} 
                onChange={(e) => setTargetKpi(Number(e.target.value))}
                className="w-20"
                min={80}
                max={100}
              />
              <span className="text-sm text-slate-400">%</span>
            </div>
            
            <Button 
              variant="outline" 
              onClick={() => startAutoTranslation(true)}
              disabled={autoTranslating}
            >
              Preview Changes
            </Button>
            
            <Button 
              onClick={() => startAutoTranslation(false)}
              disabled={autoTranslating}
              className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
            >
              {autoTranslating ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Translating...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-2" />
                  Run Auto-Translation
                </>
              )}
            </Button>
          </div>

          {/* Translation Job Progress */}
          {translationJob && translationJob.status === 'running' && (
            <div className="mt-4 bg-slate-800/50 rounded-xl p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-slate-400">
                  Progress: {translationJob.languages_completed}/{translationJob.languages_total} languages
                </span>
                <span className="text-sm text-turquoise">
                  {translationJob.keys_translated} keys translated
                </span>
              </div>
              <Progress 
                value={(translationJob.languages_completed / translationJob.languages_total) * 100} 
                className="h-2"
              />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Alert Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            {alertsEnabled ? <Bell className="w-5 h-5 text-amber-400" /> : <BellOff className="w-5 h-5 text-slate-400" />}
            Coverage Alerts
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <Switch 
                checked={alertsEnabled} 
                onCheckedChange={setAlertsEnabled}
              />
              <span className="text-sm">Alerts {alertsEnabled ? 'Enabled' : 'Disabled'}</span>
            </div>
            
            <div className="flex items-center gap-2">
              <label className="text-sm text-slate-400">Threshold:</label>
              <Input 
                type="number" 
                value={alertThreshold} 
                onChange={(e) => setAlertThreshold(Number(e.target.value))}
                className="w-20"
                min={50}
                max={100}
              />
              <span className="text-sm text-slate-400">%</span>
            </div>
            
            <Button variant="outline" size="sm" onClick={updateAlertConfig}>
              Save Alert Config
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Language Tiers */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Award className="w-5 h-5 text-turquoise" />
          Language Tiers
        </h3>
        
        {Object.entries(tiers).map(([tierId, tierData]) => (
          <Card key={tierId} className={`border-l-4 ${
            tierData.status === 'excellent' ? 'border-l-emerald-500' :
            tierData.status === 'good' ? 'border-l-green-500' :
            tierData.status === 'needs_improvement' ? 'border-l-yellow-500' :
            'border-l-red-500'
          }`}>
            <CardHeader 
              className="cursor-pointer" 
              onClick={() => toggleTierExpanded(tierId)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Badge className={tierBadgeColors[tierId]}>
                    {tierId.replace('tier', 'Tier ')}
                  </Badge>
                  <div>
                    <CardTitle className="text-base">{tierData.name}</CardTitle>
                    <CardDescription>{tierData.languages?.length || 0} languages • Target: {tierData.target_kpi}%</CardDescription>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <div className={`text-2xl font-bold ${statusColors[tierData.status]}`}>
                      {tierData.average_coverage || 0}%
                    </div>
                    <div className="text-xs text-slate-400">
                      {tierData.kpi_achievement || 0}% meeting KPI
                    </div>
                  </div>
                  {expandedTiers[tierId] ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                </div>
              </div>
              <Progress 
                value={tierData.average_coverage || 0} 
                className="h-2 mt-2"
              />
            </CardHeader>
            
            {expandedTiers[tierId] && tierData.languages && (
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                  {tierData.languages.map(lang => (
                    <div 
                      key={lang.code}
                      className="bg-slate-800/50 rounded-lg p-3 text-center"
                    >
                      <div className="text-lg font-bold">{lang.code}</div>
                      <div className={`text-sm ${lang.coverage >= tierData.target_kpi ? 'text-green-400' : 'text-amber-400'}`}>
                        {lang.coverage}%
                      </div>
                      <Badge className={`text-xs ${gradeColors[lang.grade]} text-white`}>
                        {lang.grade}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            )}
          </Card>
        ))}
      </div>

      {/* Industry Comparison */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-turquoise" />
            Industry Benchmark Comparison
          </CardTitle>
          <CardDescription>How MedMatch compares to leading multilingual apps</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {/* MedMatch */}
            <div className="flex items-center gap-4">
              <div className="w-28 font-medium text-turquoise">MedMatch</div>
              <div className="flex-1">
                <Progress value={summary.overall_average_coverage} className="h-3" />
              </div>
              <div className="w-20 text-right">
                <span className="font-bold">{summary.total_languages}</span>
                <span className="text-slate-400 text-sm"> langs</span>
              </div>
              <div className="w-16 text-right font-bold text-turquoise">
                {summary.overall_average_coverage}%
              </div>
            </div>
            
            {/* Industry leaders */}
            {Object.entries(industry_comparison).map(([app, data]) => (
              <div key={app} className="flex items-center gap-4 opacity-70">
                <div className="w-28 font-medium capitalize">{app}</div>
                <div className="flex-1">
                  <Progress value={data.avg_coverage} className="h-3 bg-slate-700" />
                </div>
                <div className="w-20 text-right">
                  <span className="font-bold">{data.languages}</span>
                  <span className="text-slate-400 text-sm"> langs</span>
                </div>
                <div className="w-16 text-right font-bold">
                  {data.avg_coverage}%
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default TranslationBenchmarkDashboard;
