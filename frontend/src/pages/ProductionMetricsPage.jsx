/**
 * Production Metrics Dashboard
 * Visualizes user engagement, AI usage, business metrics, and conversion funnels
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import {
  BarChart3,
  Users,
  TrendingUp,
  Activity,
  Zap,
  Brain,
  Target,
  Clock,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw,
  Calendar,
  Filter,
  Download,
  ChevronLeft,
  Eye,
  MousePointer,
  Smartphone,
  Monitor,
  Globe,
  DollarSign,
  FileText,
  Briefcase,
  MessageSquare,
  Sparkles,
  PieChart
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { apiClient } from '@/utils/apiClient';

// ============== Chart Components ==============

// Simple Bar Chart
const SimpleBarChart = ({ data, label, color = "#14b8a6" }) => {
  if (!data || data.length === 0) return <div className="text-center text-muted-foreground py-8">No data available</div>;
  
  const maxValue = Math.max(...data.map(d => d.value));
  
  return (
    <div className="space-y-2">
      {data.map((item, idx) => (
        <div key={idx} className="flex items-center gap-3">
          <span className="text-xs text-muted-foreground w-24 truncate">{item.name}</span>
          <div className="flex-1 h-6 bg-muted/30 rounded-full overflow-hidden">
            <div 
              className="h-full rounded-full transition-all duration-500"
              style={{ 
                width: `${(item.value / maxValue) * 100}%`,
                backgroundColor: color
              }}
            />
          </div>
          <span className="text-sm font-medium w-16 text-right">{item.value.toLocaleString()}</span>
        </div>
      ))}
    </div>
  );
};

// Funnel Chart
const FunnelChart = ({ stages }) => {
  if (!stages || stages.length === 0) return <div className="text-center text-muted-foreground py-8">No funnel data</div>;
  
  const maxCount = stages[0]?.count || 1;
  const colors = ["#14b8a6", "#0ea5e9", "#8b5cf6", "#f59e0b", "#22c55e"];
  
  return (
    <div className="space-y-3">
      {stages.map((stage, idx) => {
        const widthPercent = (stage.count / maxCount) * 100;
        const conversionRate = idx > 0 ? ((stage.count / stages[idx-1].count) * 100).toFixed(1) : 100;
        
        return (
          <div key={stage.name} className="relative">
            <div className="flex items-center gap-3">
              <div className="w-28 text-sm font-medium truncate">{stage.name}</div>
              <div className="flex-1 relative">
                <div 
                  className="h-10 rounded-lg transition-all duration-500 flex items-center justify-end pr-3"
                  style={{ 
                    width: `${Math.max(widthPercent, 10)}%`,
                    backgroundColor: colors[idx % colors.length]
                  }}
                >
                  <span className="text-white text-sm font-bold">{stage.count.toLocaleString()}</span>
                </div>
              </div>
              {idx > 0 && (
                <Badge variant="outline" className="w-16 justify-center">
                  {conversionRate}%
                </Badge>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};

// Metric Card
const MetricCard = ({ title, value, subtitle, icon: Icon, trend, trendValue, color = "turquoise" }) => {
  const colorClasses = {
    turquoise: "bg-turquoise/10 text-turquoise",
    blue: "bg-blue-500/10 text-blue-500",
    green: "bg-green-500/10 text-green-500",
    purple: "bg-purple-500/10 text-purple-500",
    orange: "bg-orange-500/10 text-orange-500",
    pink: "bg-pink-500/10 text-pink-500"
  };

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div className={`p-2.5 rounded-xl ${colorClasses[color]}`}>
            <Icon className="h-5 w-5" />
          </div>
          {trend && (
            <div className={`flex items-center gap-1 text-xs font-medium ${
              trend === 'up' ? 'text-green-500' : trend === 'down' ? 'text-red-500' : 'text-muted-foreground'
            }`}>
              {trend === 'up' ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
              {trendValue}
            </div>
          )}
        </div>
        <div className="mt-3">
          <p className="text-2xl font-bold">{value}</p>
          <p className="text-sm text-muted-foreground">{title}</p>
          {subtitle && <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>}
        </div>
      </CardContent>
    </Card>
  );
};

// ============== Main Component ==============

const ProductionMetricsPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [timeRange, setTimeRange] = useState("7");
  const [dashboardData, setDashboardData] = useState(null);
  const [error, setError] = useState(null);

  // Fetch dashboard data
  const fetchDashboardData = useCallback(async (showToast = false) => {
    try {
      setRefreshing(true);
      const response = await apiClient.get(`/api/metrics/analytics/dashboard?days=${timeRange}`);
      setDashboardData(response.data);
      setError(null);
      if (showToast) toast.success("Metrics refreshed");
    } catch (err) {
      console.error("Failed to fetch metrics:", err);
      setError(err.response?.data?.detail || "Failed to load metrics");
      if (err.response?.status === 403) {
        toast.error("Admin access required");
        navigate('/');
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [timeRange, navigate]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  // Handle time range change
  const handleTimeRangeChange = (value) => {
    setTimeRange(value);
  };

  // Export data
  const handleExport = () => {
    if (!dashboardData) return;
    
    const dataStr = JSON.stringify(dashboardData, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `medmatch-metrics-${timeRange}days-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success("Metrics exported");
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-3 text-turquoise" />
          <p className="text-muted-foreground">Loading production metrics...</p>
        </div>
      </div>
    );
  }

  if (error && !dashboardData) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Card className="max-w-md">
          <CardContent className="p-6 text-center">
            <Activity className="h-12 w-12 mx-auto mb-4 text-red-500" />
            <h3 className="font-semibold text-lg mb-2">Unable to Load Metrics</h3>
            <p className="text-muted-foreground mb-4">{error}</p>
            <Button onClick={() => fetchDashboardData()}>Try Again</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const { engagement, business, ai_usage, funnel } = dashboardData || {};

  return (
    <div className="space-y-6 pb-8" data-testid="production-metrics-page">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={() => navigate('/admin')}
            className="shrink-0"
          >
            <ChevronLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <BarChart3 className="h-6 w-6 text-turquoise" />
              Production Metrics
            </h1>
            <p className="text-muted-foreground text-sm">
              Real-time analytics and performance insights
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <Select value={timeRange} onValueChange={handleTimeRangeChange}>
            <SelectTrigger className="w-[140px]" data-testid="time-range-select">
              <Calendar className="h-4 w-4 mr-2" />
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7">Last 7 days</SelectItem>
              <SelectItem value="14">Last 14 days</SelectItem>
              <SelectItem value="30">Last 30 days</SelectItem>
              <SelectItem value="60">Last 60 days</SelectItem>
              <SelectItem value="90">Last 90 days</SelectItem>
            </SelectContent>
          </Select>
          
          <Button 
            variant="outline" 
            size="icon"
            onClick={() => fetchDashboardData(true)}
            disabled={refreshing}
            data-testid="refresh-btn"
          >
            <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
          </Button>
          
          <Button 
            variant="outline" 
            onClick={handleExport}
            data-testid="export-btn"
          >
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Engagement Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <MetricCard
          title="Total Sessions"
          value={engagement?.total_sessions?.toLocaleString() || '0'}
          icon={Users}
          color="turquoise"
          trend={engagement?.sessions_trend}
          trendValue={engagement?.sessions_change}
        />
        <MetricCard
          title="Unique Users"
          value={engagement?.unique_users?.toLocaleString() || '0'}
          icon={Globe}
          color="blue"
        />
        <MetricCard
          title="Page Views"
          value={engagement?.total_page_views?.toLocaleString() || '0'}
          icon={Eye}
          color="purple"
        />
        <MetricCard
          title="Avg. Session"
          value={engagement?.avg_session_duration || '0m'}
          icon={Clock}
          color="orange"
        />
        <MetricCard
          title="Bounce Rate"
          value={`${engagement?.bounce_rate || 0}%`}
          icon={MousePointer}
          color="pink"
        />
        <MetricCard
          title="Return Rate"
          value={`${engagement?.return_rate || 0}%`}
          icon={TrendingUp}
          color="green"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Conversion Funnel */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5 text-turquoise" />
              Conversion Funnel
            </CardTitle>
            <CardDescription>User journey from signup to subscription</CardDescription>
          </CardHeader>
          <CardContent>
            <FunnelChart stages={funnel?.stages || [
              { name: "Visitors", count: engagement?.total_sessions || 0 },
              { name: "Sign Ups", count: business?.total_signups || 0 },
              { name: "Resumed", count: business?.resumes_uploaded || 0 },
              { name: "Job Applied", count: business?.applications || 0 },
              { name: "Subscribed", count: business?.subscriptions || 0 }
            ]} />
          </CardContent>
        </Card>

        {/* AI Tool Usage */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-purple-500" />
              AI Tool Usage
            </CardTitle>
            <CardDescription>Usage breakdown by feature</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-4 bg-muted/30 rounded-lg">
                  <p className="text-3xl font-bold text-purple-500">{ai_usage?.total_requests?.toLocaleString() || '0'}</p>
                  <p className="text-sm text-muted-foreground">Total AI Requests</p>
                </div>
                <div className="text-center p-4 bg-muted/30 rounded-lg">
                  <p className="text-3xl font-bold text-turquoise">{ai_usage?.avg_response_time || '0'}ms</p>
                  <p className="text-sm text-muted-foreground">Avg Response Time</p>
                </div>
              </div>
              
              <SimpleBarChart 
                data={ai_usage?.by_tool?.map(t => ({ name: t.tool, value: t.count })) || [
                  { name: "Cover Letter", value: 0 },
                  { name: "Interview Prep", value: 0 },
                  { name: "Resume Parse", value: 0 },
                  { name: "KARAU Dragon", value: 0 }
                ]}
                color="#8b5cf6"
              />
            </div>
          </CardContent>
        </Card>

        {/* Business Metrics */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="h-5 w-5 text-green-500" />
              Business Metrics
            </CardTitle>
            <CardDescription>Revenue and conversion tracking</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-3">
                <div className="text-center p-3 bg-green-500/10 rounded-lg">
                  <p className="text-2xl font-bold text-green-500">${business?.total_revenue?.toLocaleString() || '0'}</p>
                  <p className="text-xs text-muted-foreground">Revenue</p>
                </div>
                <div className="text-center p-3 bg-blue-500/10 rounded-lg">
                  <p className="text-2xl font-bold text-blue-500">{business?.new_subscribers || 0}</p>
                  <p className="text-xs text-muted-foreground">New Subs</p>
                </div>
                <div className="text-center p-3 bg-purple-500/10 rounded-lg">
                  <p className="text-2xl font-bold text-purple-500">{business?.trial_conversions || 0}%</p>
                  <p className="text-xs text-muted-foreground">Trial Conv.</p>
                </div>
              </div>
              
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Resumes Uploaded</span>
                    <span className="font-medium">{business?.resumes_uploaded || 0}</span>
                  </div>
                  <Progress value={Math.min((business?.resumes_uploaded || 0) / 100 * 100, 100)} className="h-2" />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Job Applications</span>
                    <span className="font-medium">{business?.applications || 0}</span>
                  </div>
                  <Progress value={Math.min((business?.applications || 0) / 500 * 100, 100)} className="h-2" />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Cover Letters Generated</span>
                    <span className="font-medium">{business?.cover_letters || 0}</span>
                  </div>
                  <Progress value={Math.min((business?.cover_letters || 0) / 200 * 100, 100)} className="h-2" />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Device & Platform Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PieChart className="h-5 w-5 text-orange-500" />
              Platform Distribution
            </CardTitle>
            <CardDescription>User sessions by device type</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {(engagement?.by_device || [
                { device: "Desktop", sessions: 0, percent: 0 },
                { device: "Mobile", sessions: 0, percent: 0 },
                { device: "Tablet", sessions: 0, percent: 0 },
                { device: "Desktop App", sessions: 0, percent: 0 }
              ]).map((device, idx) => {
                const icons = { Desktop: Monitor, Mobile: Smartphone, Tablet: Smartphone, "Desktop App": Monitor };
                const colors = ["#14b8a6", "#0ea5e9", "#8b5cf6", "#f59e0b"];
                const Icon = icons[device.device] || Globe;
                
                return (
                  <div key={device.device} className="flex items-center gap-3">
                    <div className="p-2 rounded-lg" style={{ backgroundColor: `${colors[idx]}20` }}>
                      <Icon className="h-4 w-4" style={{ color: colors[idx] }} />
                    </div>
                    <div className="flex-1">
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium">{device.device}</span>
                        <span className="text-sm text-muted-foreground">{device.sessions?.toLocaleString() || 0} ({device.percent || 0}%)</span>
                      </div>
                      <div className="h-2 bg-muted/30 rounded-full overflow-hidden">
                        <div 
                          className="h-full rounded-full transition-all duration-500"
                          style={{ width: `${device.percent || 0}%`, backgroundColor: colors[idx] }}
                        />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Top Pages & Features */}
      <div className="grid lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-blue-500" />
              Top Pages
            </CardTitle>
            <CardDescription>Most visited pages in the period</CardDescription>
          </CardHeader>
          <CardContent>
            <SimpleBarChart 
              data={engagement?.top_pages?.map(p => ({ name: p.path, value: p.views })) || [
                { name: "/dashboard", value: 0 },
                { name: "/search", value: 0 },
                { name: "/resume", value: 0 },
                { name: "/applications", value: 0 }
              ]}
              color="#0ea5e9"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-turquoise" />
              Feature Engagement
            </CardTitle>
            <CardDescription>Most used features by users</CardDescription>
          </CardHeader>
          <CardContent>
            <SimpleBarChart 
              data={engagement?.top_features?.map(f => ({ name: f.feature, value: f.usage })) || [
                { name: "Job Search", value: 0 },
                { name: "Resume Upload", value: 0 },
                { name: "Cover Letter", value: 0 },
                { name: "Interview Prep", value: 0 }
              ]}
              color="#14b8a6"
            />
          </CardContent>
        </Card>
      </div>

      {/* Footer Info */}
      <div className="text-center text-sm text-muted-foreground">
        <p>
          Data period: Last {timeRange} days • 
          Generated: {dashboardData?.generated_at ? new Date(dashboardData.generated_at).toLocaleString() : 'N/A'}
        </p>
      </div>
    </div>
  );
};

export default ProductionMetricsPage;
