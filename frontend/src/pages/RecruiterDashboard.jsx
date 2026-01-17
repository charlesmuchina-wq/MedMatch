import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import { useTheme } from "@/App";
import { 
  Users, Briefcase, MessageSquare, Search, TrendingUp, Clock,
  ChevronRight, UserCheck, UserX, Loader2, Brain, Eye, Filter
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const API = process.env.REACT_APP_BACKEND_URL;

const RecruiterDashboard = ({ user }) => {
  const navigate = useNavigate();
  const { isDark } = useTheme();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.role !== "recruiter") {
      navigate("/");
      return;
    }
    fetchStats();
  }, [user, navigate]);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/api/recruiter/dashboard/stats`);
      setStats(response.data);
    } catch (e) {
      console.error("Failed to fetch stats:", e);
    }
    setLoading(false);
  };

  const getStatusColor = (status) => {
    const colors = {
      new: "bg-blue-500",
      reviewing: "bg-amber-500",
      shortlisted: "bg-emerald-500",
      interviewing: "bg-violet-500",
      offered: "bg-cyan-500",
      hired: "bg-green-600",
      rejected: "bg-slate-400"
    };
    return colors[status] || "bg-slate-500";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 animate-spin text-turquoise" />
      </div>
    );
  }

  const quickActions = [
    { icon: Briefcase, label: "Post a Job", path: "/recruiter/jobs", color: "text-turquoise" },
    { icon: Search, label: "Search Candidates", path: "/recruiter/candidates", color: "text-violet-500" },
    { icon: MessageSquare, label: "Messages", path: "/messages", color: "text-emerald-500" },
    { icon: Brain, label: "AI Prescreening", path: "/recruiter/prescreen", color: "text-amber-500" }
  ];

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-7xl mx-auto animate-fade-in" data-testid="recruiter-dashboard">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl md:text-4xl font-semibold text-slate-900 dark:text-slate-100">
          Recruiter Dashboard
        </h1>
        <p className="text-slate-500 dark:text-slate-400 mt-2">
          Manage your job postings and track applicants
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <Card className="bg-gradient-to-br from-turquoise/10 to-turquoise/5 border-turquoise/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-500 dark:text-slate-400">Active Jobs</p>
                <p className="text-2xl font-bold text-turquoise">{stats?.jobs?.active || 0}</p>
              </div>
              <Briefcase className="w-8 h-8 text-turquoise/50" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-violet-500/10 to-violet-500/5 border-violet-500/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-500 dark:text-slate-400">Total Applicants</p>
                <p className="text-2xl font-bold text-violet-500">{stats?.applicants?.total || 0}</p>
              </div>
              <Users className="w-8 h-8 text-violet-500/50" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-emerald-500/10 to-emerald-500/5 border-emerald-500/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-500 dark:text-slate-400">Shortlisted</p>
                <p className="text-2xl font-bold text-emerald-500">
                  {stats?.applicants?.by_status?.shortlisted || 0}
                </p>
              </div>
              <UserCheck className="w-8 h-8 text-emerald-500/50" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-amber-500/10 to-amber-500/5 border-amber-500/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-500 dark:text-slate-400">Interviewing</p>
                <p className="text-2xl font-bold text-amber-500">
                  {stats?.applicants?.by_status?.interviewing || 0}
                </p>
              </div>
              <Clock className="w-8 h-8 text-amber-500/50" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {quickActions.map((action, idx) => (
          <button
            key={idx}
            onClick={() => navigate(action.path)}
            className="p-4 rounded-xl border border-slate-200 dark:border-slate-700 
              hover:border-turquoise/50 transition-all bg-white dark:bg-slate-800/50
              flex flex-col items-center gap-2 group"
            data-testid={`quick-action-${action.label.toLowerCase().replace(/\s/g, '-')}`}
          >
            <action.icon className={`w-6 h-6 ${action.color} group-hover:scale-110 transition-transform`} />
            <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
              {action.label}
            </span>
          </button>
        ))}
      </div>

      {/* Recent Applicants */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Users className="w-5 h-5 text-turquoise" />
                Recent Applicants
              </CardTitle>
              <CardDescription>Latest candidates who applied to your jobs</CardDescription>
            </div>
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => navigate('/recruiter/jobs')}
            >
              View All Jobs
              <ChevronRight className="w-4 h-4 ml-1" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {stats?.applicants?.recent?.length > 0 ? (
            <div className="space-y-3">
              {stats.applicants.recent.map((applicant, idx) => (
                <div
                  key={applicant.id || idx}
                  className="flex items-center justify-between p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50 
                    hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
                  onClick={() => navigate(`/recruiter/jobs/${applicant.job_id}/applicants`)}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-turquoise to-emerald-500 
                      flex items-center justify-center text-white font-semibold">
                      {(applicant.applicant_name || applicant.applicant_email || "?")[0].toUpperCase()}
                    </div>
                    <div>
                      <p className="font-medium text-slate-900 dark:text-slate-100">
                        {applicant.applicant_name || applicant.applicant_email}
                      </p>
                      <p className="text-sm text-slate-500">
                        Applied for: {applicant.job_title}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className={`${getStatusColor(applicant.status)} text-white`}>
                      {applicant.status}
                    </Badge>
                    <span className="text-xs text-slate-400">
                      {new Date(applicant.applied_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-slate-500">
              <Users className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p>No applicants yet</p>
              <p className="text-sm">Post a job to start receiving applications</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pipeline Overview */}
      {stats?.applicants?.total > 0 && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-turquoise" />
              Applicant Pipeline
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-4">
              {Object.entries(stats.applicants.by_status || {}).map(([status, count]) => (
                <div key={status} className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${getStatusColor(status)}`} />
                  <span className="text-sm text-slate-600 dark:text-slate-400 capitalize">
                    {status}: <strong>{count}</strong>
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default RecruiterDashboard;
