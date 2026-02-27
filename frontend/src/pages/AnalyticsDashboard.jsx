import { useState, useEffect } from "react";
import { toast } from "sonner";
import { useTheme } from "@/App";
import { 
  BarChart3, TrendingUp, TrendingDown, Calendar, Target, 
  CheckCircle2, XCircle, Clock, Building2, Briefcase,
  PieChart, Activity, Award, Zap, ArrowUpRight, ArrowDownRight
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { useTranslation } from "@/utils/i18n";
import { apiClient } from "@/utils/apiClient";

// Stat Card Component
const StatCard = ({ title, value, change, changeType, icon: Icon, color }) => (
  <Card>
    <CardContent className="p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-500 dark:text-slate-400">{title}</p>
          <p className="text-3xl font-bold text-slate-900 dark:text-slate-100 mt-1">{value}</p>
          {change !== undefined && (
            <div className={`flex items-center gap-1 mt-2 text-sm ${
              changeType === 'up' ? 'text-emerald-600' : changeType === 'down' ? 'text-rose-600' : 'text-slate-500'
            }`}>
              {changeType === 'up' ? <ArrowUpRight className="w-4 h-4" /> : 
               changeType === 'down' ? <ArrowDownRight className="w-4 h-4" /> : null}
              <span>{change}</span>
            </div>
          )}
        </div>
        <div className={`p-4 rounded-xl ${color}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </CardContent>
  </Card>
);

// Progress Ring Component
const ProgressRing = ({ value, max, label, color }) => {
  const percentage = max > 0 ? (value / max) * 100 : 0;
  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-28 h-28">
        <svg className="transform -rotate-90" viewBox="0 0 100 100">
          <circle
            cx="50" cy="50" r={radius}
            fill="none" stroke="currentColor"
            className="text-slate-200 dark:text-slate-700 dark:text-slate-300"
            strokeWidth="8"
          />
          <circle
            cx="50" cy="50" r={radius}
            fill="none" stroke={color}
            strokeWidth="8"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-bold text-slate-900 dark:text-slate-100">{value}</span>
          <span className="text-xs text-slate-500 dark:text-slate-400">of {max}</span>
        </div>
      </div>
      <span className="text-sm text-slate-600 dark:text-slate-400 mt-2">{label}</span>
    </div>
  );
};

// Timeline Item Component
const TimelineItem = ({ date, title, company, status, isLast }) => {
  const statusColors = {
    'Applied': 'bg-sky-500',
    'Interview': 'bg-amber-500',
    'Offer': 'bg-emerald-500',
    'Rejected': 'bg-rose-500'
  };

  return (
    <div className="flex gap-4">
      <div className="flex flex-col items-center">
        <div className={`w-3 h-3 rounded-full ${statusColors[status] || 'bg-slate-400'}`} />
        {!isLast && <div className="w-0.5 h-full bg-slate-200 dark:bg-slate-700 mt-1" />}
      </div>
      <div className="pb-4">
        <p className="text-xs text-slate-500 dark:text-slate-400">{date}</p>
        <p className="font-medium text-slate-900 dark:text-slate-100">{title}</p>
        <p className="text-sm text-slate-600 dark:text-slate-400">{company}</p>
        <Badge className={`mt-1 ${
          status === 'Applied' ? 'bg-sky-100 text-sky-700 dark:bg-sky-900/30 dark:text-sky-300' :
          status === 'Interview' ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300' :
          status === 'Offer' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300' :
          'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-300'
        }`}>
          {status}
        </Badge>
      </div>
    </div>
  );
};

const AnalyticsDashboard = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('30'); // days
  const { isDark } = useTheme();
  const { t } = useTranslation();

  useEffect(() => {
    fetchAnalytics();
  }, [timeRange]);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get(`/api/analytics/dashboard?days=${timeRange}`);
      setAnalytics(response.data);
    } catch (e) {
      toast.error(t("analytics.loadFailed") || "Failed to load analytics");
      // Set default data
      setAnalytics({
        total_applications: 0,
        interviews: 0,
        offers: 0,
        rejections: 0,
        pending: 0,
        response_rate: 0,
        interview_rate: 0,
        offer_rate: 0,
        avg_response_days: 0,
        applications_by_source: {},
        applications_by_status: {},
        applications_over_time: [],
        top_companies: [],
        recent_activity: [],
        weekly_comparison: { current: 0, previous: 0 }
      });
    }
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="p-6 md:p-8 lg:p-12 max-w-7xl mx-auto">
        <div className="animate-pulse space-y-6">
          <div className="h-8 w-64 bg-slate-200 dark:bg-slate-700 rounded" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[1,2,3,4].map(i => (
              <div key={i} className="h-32 bg-slate-200 dark:bg-slate-700 rounded-lg" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  const weeklyChange = analytics?.weekly_comparison?.previous > 0 
    ? Math.round(((analytics.weekly_comparison.current - analytics.weekly_comparison.previous) / analytics.weekly_comparison.previous) * 100)
    : 0;

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-7xl mx-auto animate-fade-in" data-testid="analytics-dashboard">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-semibold text-slate-900 dark:text-slate-100 tracking-tight" style={{ fontFamily: 'IBM Plex Sans' }}>
            Application Analytics
          </h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">Track your job search progress and success rates</p>
        </div>
        <div className="flex gap-2">
          {['7', '30', '90'].map(days => (
            <button
              key={days}
              onClick={() => setTimeRange(days)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                timeRange === days 
                  ? 'bg-turquoise text-white' 
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
              }`}
            >
              {days}d
            </button>
          ))}
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard 
          title="Total Applications" 
          value={analytics?.total_applications || 0}
          change={weeklyChange !== 0 ? `${weeklyChange > 0 ? '+' : ''}${weeklyChange}% vs last week` : undefined}
          changeType={weeklyChange > 0 ? 'up' : weeklyChange < 0 ? 'down' : undefined}
          icon={Briefcase}
          color="bg-gradient-to-br from-violet-500 to-purple-600"
        />
        <StatCard 
          title="Interviews" 
          value={analytics?.interviews || 0}
          change={`${analytics?.interview_rate || 0}% rate`}
          changeType="up"
          icon={Calendar}
          color="bg-gradient-to-br from-amber-500 to-orange-600"
        />
        <StatCard 
          title="Offers Received" 
          value={analytics?.offers || 0}
          change={`${analytics?.offer_rate || 0}% success`}
          changeType={analytics?.offers > 0 ? 'up' : undefined}
          icon={Award}
          color="bg-gradient-to-br from-emerald-500 to-green-600"
        />
        <StatCard 
          title="Response Rate" 
          value={`${analytics?.response_rate || 0}%`}
          change={`Avg ${analytics?.avg_response_days || 0} days`}
          icon={Activity}
          color="bg-gradient-to-br from-sky-500 to-cyan-600"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid lg:grid-cols-3 gap-6 mb-8">
        {/* Application Funnel */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2" style={{ fontFamily: 'IBM Plex Sans' }}>
              <BarChart3 className="w-5 h-5 text-violet-500" />
              Application Funnel
            </CardTitle>
            <CardDescription>Your application pipeline breakdown</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { label: 'Applied', count: analytics?.total_applications || 0, color: 'bg-sky-500', percent: 100 },
                { label: 'Reviewed', count: Math.round((analytics?.total_applications || 0) * (analytics?.response_rate || 0) / 100), color: 'bg-violet-500', percent: analytics?.response_rate || 0 },
                { label: 'Interview', count: analytics?.interviews || 0, color: 'bg-amber-500', percent: analytics?.interview_rate || 0 },
                { label: 'Offer', count: analytics?.offers || 0, color: 'bg-emerald-500', percent: analytics?.offer_rate || 0 },
              ].map((stage, i) => (
                <div key={i} className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-600 dark:text-slate-400">{stage.label}</span>
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-slate-900 dark:text-slate-100">{stage.count}</span>
                      <span className="text-slate-400">({stage.percent}%)</span>
                    </div>
                  </div>
                  <div className="h-3 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div 
                      className={`h-full ${stage.color} rounded-full transition-all duration-1000`}
                      style={{ width: `${stage.percent}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Status Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2" style={{ fontFamily: 'IBM Plex Sans' }}>
              <PieChart className="w-5 h-5 text-turquoise" />
              Status Breakdown
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex justify-center mb-6">
              <ProgressRing 
                value={analytics?.interviews || 0} 
                max={analytics?.total_applications || 1} 
                label="Interview Rate"
                color="#20b2aa"
              />
            </div>
            <div className="space-y-3">
              {[
                { label: 'Pending', count: analytics?.pending || 0, color: 'bg-slate-400' },
                { label: 'Interview', count: analytics?.interviews || 0, color: 'bg-amber-500' },
                { label: 'Offer', count: analytics?.offers || 0, color: 'bg-emerald-500' },
                { label: 'Rejected', count: analytics?.rejections || 0, color: 'bg-rose-500' },
              ].map((status, i) => (
                <div key={i} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full ${status.color}`} />
                    <span className="text-sm text-slate-600 dark:text-slate-400">{status.label}</span>
                  </div>
                  <span className="font-medium text-slate-900 dark:text-slate-100">{status.count}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Bottom Row */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Top Companies */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2" style={{ fontFamily: 'IBM Plex Sans' }}>
              <Building2 className="w-5 h-5 text-sky-500" />
              Top Companies Applied
            </CardTitle>
          </CardHeader>
          <CardContent>
            {analytics?.top_companies?.length > 0 ? (
              <div className="space-y-4">
                {analytics.top_companies.slice(0, 5).map((company, i) => (
                  <div key={i} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
                        <span className="text-sm font-medium text-slate-600 dark:text-slate-400">
                          {company.name?.charAt(0) || '?'}
                        </span>
                      </div>
                      <span className="text-slate-900 dark:text-slate-100">{company.name}</span>
                    </div>
                    <Badge variant="secondary">{company.count} apps</Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-slate-500 dark:text-slate-400 text-center py-8">
                No applications yet
              </p>
            )}
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2" style={{ fontFamily: 'IBM Plex Sans' }}>
              <Clock className="w-5 h-5 text-amber-500" />
              Recent Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            {analytics?.recent_activity?.length > 0 ? (
              <div className="space-y-1">
                {analytics.recent_activity.slice(0, 5).map((activity, i) => (
                  <TimelineItem
                    key={i}
                    date={new Date(activity.date).toLocaleDateString()}
                    title={activity.job_title}
                    company={activity.company}
                    status={activity.status}
                    isLast={i === Math.min(analytics.recent_activity.length - 1, 4)}
                  />
                ))}
              </div>
            ) : (
              <p className="text-slate-500 dark:text-slate-400 text-center py-8">
                No recent activity
              </p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Insights Card */}
      <Card className="mt-6 bg-gradient-to-r from-violet-50 to-purple-50 dark:from-violet-900/20 dark:to-purple-900/20 border-violet-200 dark:border-violet-800">
        <CardContent className="p-6">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-violet-100 dark:bg-violet-900/30 rounded-xl">
              <Zap className="w-6 h-6 text-violet-600 dark:text-violet-400" />
            </div>
            <div>
              <h3 className="font-medium text-violet-900 dark:text-violet-100 mb-2">AI Insights</h3>
              <p className="text-sm text-violet-700 dark:text-violet-300">
                {analytics?.total_applications > 0 ? (
                  analytics?.interview_rate >= 20 
                    ? `Great job! Your ${analytics.interview_rate}% interview rate is above average. Keep targeting similar roles.`
                    : analytics?.interview_rate >= 10
                    ? `Your ${analytics.interview_rate}% interview rate is improving. Consider tailoring your resume more to each job.`
                    : `Pro tip: Try to apply to 10+ jobs per week and customize your cover letter for better response rates.`
                ) : (
                  "Start applying to jobs to see your analytics and insights here!"
                )}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AnalyticsDashboard;
