/**
 * MedMatch - Interview Funnel Analytics Dashboard
 * Tracks: Applications → Callbacks → Interviews → Offers
 */
import React, { useState, useEffect } from 'react';
import { useTranslation } from '@/utils/i18n';
import { toast } from 'sonner';
import {
  TrendingUp,
  TrendingDown,
  Users,
  Briefcase,
  Award,
  Target,
  BarChart3,
  PieChart,
  Calendar,
  Building,
  Lightbulb,
  ChevronDown,
  RefreshCw
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Progress } from '../components/ui/progress';
import api from '@/utils/apiClient';

// Funnel Stage Component
const FunnelStage = ({ stage, index, total }) => {
  const width = 100 - (index * 15); // Decreasing width for funnel effect
  
  return (
    <div className="flex items-center gap-4 my-2">
      <div className="w-24 text-sm font-medium text-right">{stage.stage}</div>
      <div className="flex-1 relative">
        <div 
          className="h-12 rounded-lg flex items-center justify-between px-4 transition-all"
          style={{ 
            width: `${width}%`, 
            backgroundColor: stage.color,
            opacity: 0.9
          }}
        >
          <span className="text-white font-bold">{stage.count}</span>
          <span className="text-white/80 text-sm">
            {stage.conversion_from_previous ? `${stage.conversion_from_previous}%` : '100%'}
          </span>
        </div>
      </div>
    </div>
  );
};

// Stat Card Component
const StatCard = ({ title, value, subtitle, icon: Icon, trend, color = "turquoise" }) => {
  const colorClasses = {
    turquoise: "bg-turquoise/10 text-turquoise",
    pink: "bg-pink-500/10 text-pink-500",
    purple: "bg-purple-500/10 text-purple-500",
    green: "bg-green-500/10 text-green-500",
    blue: "bg-blue-500/10 text-blue-500"
  };
  
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className={`p-3 rounded-xl ${colorClasses[color]}`}>
            <Icon className="h-6 w-6" />
          </div>
          {trend !== undefined && (
            <div className={`flex items-center gap-1 text-sm ${trend >= 0 ? 'text-green-500' : 'text-red-500'}`}>
              {trend >= 0 ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
              {Math.abs(trend)}%
            </div>
          )}
        </div>
        <div className="mt-4">
          <p className="text-3xl font-bold">{value}</p>
          <p className="text-sm text-muted-foreground mt-1">{title}</p>
          {subtitle && <p className="text-xs text-muted-foreground/70 mt-1">{subtitle}</p>}
        </div>
      </CardContent>
    </Card>
  );
};

// Insight Card Component
const InsightCard = ({ insight }) => {
  const typeStyles = {
    success: "border-green-500/30 bg-green-500/5",
    warning: "border-yellow-500/30 bg-yellow-500/5",
    tip: "border-blue-500/30 bg-blue-500/5",
    info: "border-gray-500/30 bg-gray-500/5"
  };
  
  return (
    <div className={`p-4 rounded-lg border ${typeStyles[insight.type] || typeStyles.info}`}>
      <div className="flex items-start gap-3">
        <span className="text-2xl">{insight.icon}</span>
        <div>
          <h4 className="font-semibold">{insight.title}</h4>
          <p className="text-sm text-muted-foreground mt-1">{insight.message}</p>
        </div>
      </div>
    </div>
  );
};

// Company/Role Row Component
const AnalyticsRow = ({ name, total, callbacks, offers, successRate }) => (
  <div className="flex items-center justify-between py-3 border-b border-border/50 last:border-0">
    <div className="flex-1">
      <p className="font-medium truncate">{name}</p>
      <p className="text-xs text-muted-foreground">{total} applications</p>
    </div>
    <div className="flex items-center gap-6 text-sm">
      <div className="text-center">
        <p className="font-semibold">{callbacks}</p>
        <p className="text-xs text-muted-foreground">Callbacks</p>
      </div>
      <div className="text-center">
        <p className="font-semibold text-green-500">{offers}</p>
        <p className="text-xs text-muted-foreground">Offers</p>
      </div>
      <div className="w-20">
        <div className="flex items-center gap-2">
          <Progress value={successRate} className="h-2" />
          <span className="text-xs font-medium">{successRate}%</span>
        </div>
      </div>
    </div>
  </div>
);

export default function AnalyticsFunnelPage() {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState('30');
  const [funnelData, setFunnelData] = useState(null);
  const [trendsData, setTrendsData] = useState(null);
  const [companyData, setCompanyData] = useState([]);
  const [roleData, setRoleData] = useState([]);
  const [insights, setInsights] = useState({ insights: [], score: 0 });

  const loadData = async () => {
    setLoading(true);
    try {
      const [funnelRes, trendsRes, companyRes, roleRes, insightsRes] = await Promise.all([
        api.get(`/api/analytics/funnel?days=${dateRange}`),
        api.get(`/api/analytics/trends?days=${dateRange}`),
        api.get('/api/analytics/by-company?limit=5'),
        api.get('/api/analytics/by-role?limit=5'),
        api.get('/api/analytics/insights')
      ]);
      
      setFunnelData(funnelRes.data);
      setTrendsData(trendsRes.data);
      setCompanyData(companyRes.data.companies || []);
      setRoleData(roleRes.data.roles || []);
      setInsights(insightsRes.data);
    } catch (error) {
      console.error('Failed to load analytics:', error);
      toast.error('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [dateRange]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <RefreshCw className="h-8 w-8 animate-spin text-turquoise" />
      </div>
    );
  }

  const summary = funnelData?.summary || {};

  return (
    <div className="container mx-auto p-6 space-y-6" data-testid="analytics-funnel-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <BarChart3 className="h-8 w-8 text-turquoise" />
            Interview Funnel Analytics
          </h1>
          <p className="text-muted-foreground mt-1">
            Track your job search performance from application to offer
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <Select value={dateRange} onValueChange={setDateRange}>
            <SelectTrigger className="w-[150px]">
              <Calendar className="h-4 w-4 mr-2" />
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7">Last 7 days</SelectItem>
              <SelectItem value="30">Last 30 days</SelectItem>
              <SelectItem value="90">Last 90 days</SelectItem>
              <SelectItem value="365">Last year</SelectItem>
            </SelectContent>
          </Select>
          
          <Button variant="outline" onClick={loadData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Job Search Score */}
      <Card className="bg-gradient-to-r from-turquoise/10 to-pink-500/10 border-turquoise/20">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold">Job Search Score</h3>
              <p className="text-sm text-muted-foreground">Based on your activity and success rate</p>
            </div>
            <div className="text-right">
              <p className="text-5xl font-bold text-turquoise">{insights.score}</p>
              <p className="text-sm text-muted-foreground">/ 100</p>
            </div>
          </div>
          <Progress value={insights.score} className="h-3 mt-4" />
        </CardContent>
      </Card>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <StatCard
          title="Total Applied"
          value={summary.total_applied || 0}
          icon={Briefcase}
          color="blue"
        />
        <StatCard
          title="Callbacks"
          value={summary.total_callbacks || 0}
          subtitle={`${summary.callback_rate || 0}% rate`}
          icon={Users}
          color="purple"
        />
        <StatCard
          title="Interviews"
          value={summary.total_interviews || 0}
          subtitle={`${summary.interview_rate || 0}% conversion`}
          icon={Target}
          color="pink"
        />
        <StatCard
          title="Offers"
          value={summary.total_offers || 0}
          subtitle={`${summary.offer_rate || 0}% success`}
          icon={Award}
          color="green"
        />
        <StatCard
          title="Success Rate"
          value={`${summary.overall_success_rate || 0}%`}
          icon={TrendingUp}
          color="turquoise"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Funnel Visualization */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PieChart className="h-5 w-5 text-turquoise" />
              Conversion Funnel
            </CardTitle>
            <CardDescription>
              Visualize your journey from application to offer
            </CardDescription>
          </CardHeader>
          <CardContent>
            {funnelData?.funnel?.length > 0 ? (
              <div className="space-y-2">
                {funnelData.funnel.map((stage, index) => (
                  <FunnelStage 
                    key={stage.stage} 
                    stage={stage} 
                    index={index}
                    total={funnelData.funnel.length}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-muted-foreground">
                <Briefcase className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No application data yet</p>
                <p className="text-sm">Start applying to jobs to see your funnel</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* AI Insights */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb className="h-5 w-5 text-yellow-500" />
              AI Insights
            </CardTitle>
            <CardDescription>
              Personalized recommendations
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {insights.insights?.length > 0 ? (
              insights.insights.map((insight, index) => (
                <InsightCard key={index} insight={insight} />
              ))
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <Lightbulb className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">Apply to more jobs to get insights</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Company & Role Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* By Company */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building className="h-5 w-5 text-turquoise" />
              Performance by Company
            </CardTitle>
            <CardDescription>
              Top companies you've applied to
            </CardDescription>
          </CardHeader>
          <CardContent>
            {companyData.length > 0 ? (
              <div>
                {companyData.map((company, index) => (
                  <AnalyticsRow
                    key={index}
                    name={company.company}
                    total={company.total_applications}
                    callbacks={company.callbacks}
                    offers={company.offers}
                    successRate={company.success_rate}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <Building className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No company data yet</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* By Role */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Briefcase className="h-5 w-5 text-pink-500" />
              Performance by Role
            </CardTitle>
            <CardDescription>
              Success rate by job title
            </CardDescription>
          </CardHeader>
          <CardContent>
            {roleData.length > 0 ? (
              <div>
                {roleData.map((role, index) => (
                  <AnalyticsRow
                    key={index}
                    name={role.role}
                    total={role.total_applications}
                    callbacks={role.callbacks}
                    offers={role.offers}
                    successRate={role.success_rate}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <Briefcase className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No role data yet</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
