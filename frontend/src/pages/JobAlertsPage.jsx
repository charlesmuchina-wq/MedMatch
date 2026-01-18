import { useState, useEffect, useCallback } from "react";
import { toast } from "sonner";
import { 
  Calendar, Mail, Trash2, Send, Loader2, Clock, 
  CheckCircle2, Settings
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { useTranslation } from "@/utils/i18n";
import { apiClient } from "@/utils/apiClient";

const JobAlertsPage = ({ resume }) => {
  const { t } = useTranslation();
  const [sending, setSending] = useState(false);
  const [sendingDigest, setSendingDigest] = useState(false);
  const [email, setEmail] = useState("");
  const [digestHistory, setDigestHistory] = useState([]);
  const [schedulerStatus, setSchedulerStatus] = useState(null);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [subscribing, setSubscribing] = useState(false);

  const loadData = useCallback(async () => {
    if (resume?.email) {
      setEmail(resume.email);
      
      try {
        const historyRes = await apiClient.get(`/api/digest/history?email=${resume.email}`);
        setDigestHistory(historyRes.data.history || []);
      } catch (e) {
        console.error("Failed to load digest history");
      }
      
      try {
        const settingsRes = await apiClient.get("/api/digest/settings");
        const settings = settingsRes.data || [];
        const userSettings = settings.find(s => s.email === resume?.email);
        setIsSubscribed(userSettings?.is_active || false);
      } catch (e) {
        console.error("Failed to load settings");
      }
    }
    
    try {
      const schedulerRes = await apiClient.get("/api/digest/scheduler-status");
      setSchedulerStatus(schedulerRes.data);
    } catch (e) {
      console.error("Failed to load scheduler status");
    }
  }, [resume?.email]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const toggleSubscription = async () => {
    if (!email) {
      toast.error(t("jobAlerts.enterEmail") || "Please enter an email address");
      return;
    }
    
    setSubscribing(true);
    try {
      if (isSubscribed) {
        await apiClient.delete(`/api/digest/settings/${email}`);
        setIsSubscribed(false);
        toast.success(t("jobAlerts.unsubscribed") || "Unsubscribed from daily digest");
      } else {
        await apiClient.post("/api/digest/settings", {
          email: email,
          frequency: "daily",
          search_queries: [],
          locations: ["Remote"]
        });
        setIsSubscribed(true);
        toast.success(t("jobAlerts.subscribed") || "Subscribed to daily digest! You'll receive emails at 8 AM UTC.");
      }
    } catch (e) {
      toast.error(t("errors.somethingWentWrong"));
    }
    setSubscribing(false);
  };

  const sendAlertNow = async () => {
    if (!email) {
      toast.error(t("jobAlerts.enterEmail") || "Please enter an email address");
      return;
    }
    setSending(true);
    try {
      const response = await apiClient.post("/api/alerts/send-now", { email });
      toast.success(response.data.message);
    } catch (e) {
      toast.error(t("errors.somethingWentWrong"));
    }
    setSending(false);
  };

  const sendDailyDigest = async () => {
    if (!email) {
      toast.error(t("jobAlerts.enterEmail") || "Please enter an email address");
      return;
    }
    setSendingDigest(true);
    try {
      const response = await apiClient.post("/api/digest/send-daily", { email });
      toast.success(`${response.data.message} (${response.data.jobs_count} ${t("jobAlerts.newJobs") || "new jobs"})`);
      const historyRes = await apiClient.get(`/api/digest/history?email=${email}`);
      setDigestHistory(historyRes.data.history || []);
    } catch (e) {
      toast.error(t("errors.somethingWentWrong"));
    }
    setSendingDigest(false);
  };

  const clearHistory = async () => {
    try {
      await apiClient.delete(`/api/digest/history/${email}`);
      setDigestHistory([]);
      toast.success(t("jobAlerts.historyCleared") || "Digest history cleared - you'll receive all jobs again");
    } catch (e) {
      toast.error(t("errors.somethingWentWrong"));
    }
  };

  const formatNextRun = (isoString) => {
    if (!isoString) return t("jobAlerts.notScheduled") || "Not scheduled";
    const date = new Date(isoString);
    return date.toLocaleString();
  };

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-4xl mx-auto animate-fade-in" data-testid="alerts-page">
      <h1 className="text-3xl font-semibold text-slate-900 dark:text-slate-100 tracking-tight mb-2" style={{ fontFamily: 'IBM Plex Sans' }}>
        {t("jobAlerts.title") || "Job Alerts & Daily Digest"}
      </h1>
      <p className="text-slate-500 dark:text-slate-400 mb-8">
        {t("jobAlerts.subtitle") || "Automated job alerts delivered to your inbox"}
      </p>

      {/* Scheduler Status Card */}
      <Card className="mb-6 border-2 border-violet-200 bg-gradient-to-r from-violet-50 to-purple-50 dark:from-violet-900/20 dark:to-purple-900/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2" style={{ fontFamily: 'IBM Plex Sans' }}>
            <Clock className="w-5 h-5 text-violet-600" />
            {t("jobAlerts.automatedDigest") || "Automated Daily Digest"}
            {schedulerStatus?.scheduler_running && (
              <Badge className="bg-emerald-100 text-emerald-700 border-emerald-200 ml-2">
                <CheckCircle2 className="w-3 h-3 mr-1" /> {t("common.active") || "Active"}
              </Badge>
            )}
          </CardTitle>
          <CardDescription>
            {t("jobAlerts.automatedDesc") || "Automatically receive new job postings every day at 8:00 AM UTC"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4 mb-4">
            <Input
              type="email"
              placeholder={t("jobAlerts.enterEmailPlaceholder") || "Enter email address"}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="flex-1 bg-white dark:bg-slate-800"
              data-testid="digest-email-input"
            />
            <div className="flex items-center gap-3 bg-white dark:bg-slate-800 px-4 py-2 rounded-lg border">
              <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                {isSubscribed ? t("jobAlerts.subscribed") || "Subscribed" : t("jobAlerts.subscribe") || "Subscribe"}
              </span>
              <Switch
                checked={isSubscribed}
                onCheckedChange={toggleSubscription}
                disabled={subscribing || !email}
                data-testid="subscribe-toggle"
              />
            </div>
          </div>
          
          {schedulerStatus && (
            <div className="bg-white/70 dark:bg-slate-800/70 rounded-lg p-4 mb-4">
              <div className="grid sm:grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">{t("jobAlerts.schedule") || "Schedule"}</p>
                  <p className="text-sm font-medium text-slate-900 dark:text-slate-100">
                    {schedulerStatus.digest_time}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">{t("jobAlerts.nextRun") || "Next Run"}</p>
                  <p className="text-sm font-medium text-slate-900 dark:text-slate-100">
                    {schedulerStatus.scheduled_jobs?.[0]?.next_run 
                      ? formatNextRun(schedulerStatus.scheduled_jobs[0].next_run)
                      : t("jobAlerts.checkScheduler") || "Check scheduler status"}
                  </p>
                </div>
              </div>
            </div>
          )}

          <div className="flex flex-wrap items-center gap-4 text-sm">
            <span className="text-slate-600 dark:text-slate-400 flex items-center gap-1">
              <Mail className="w-4 h-4" />
              {digestHistory.length > 0 
                ? `${digestHistory.length} ${t("jobAlerts.jobsSent") || "jobs already sent"}` 
                : t("jobAlerts.noJobsSent") || 'No jobs sent yet'}
            </span>
            {digestHistory.length > 0 && (
              <Button variant="ghost" size="sm" onClick={clearHistory} className="text-slate-500 hover:text-rose-500">
                <Trash2 className="w-3 h-3 mr-1" /> {t("jobAlerts.clearHistory") || "Clear History"}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Manual Digest Card */}
      <Card className="mb-6 border-2 border-sky-200 bg-gradient-to-r from-sky-50 to-emerald-50 dark:from-sky-900/20 dark:to-emerald-900/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2" style={{ fontFamily: 'IBM Plex Sans' }}>
            <Calendar className="w-5 h-5 text-sky-600" />
            {t("jobAlerts.sendNow") || "Send Digest Now"}
          </CardTitle>
          <CardDescription>
            {t("jobAlerts.sendNowDesc") || "Don't want to wait? Send a digest immediately with jobs from the last 24 hours."}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button 
            onClick={sendDailyDigest} 
            disabled={sendingDigest || !email}
            className="bg-gradient-to-r from-sky-500 to-emerald-500 hover:from-sky-600 hover:to-emerald-600"
            data-testid="send-digest-btn"
          >
            {sendingDigest ? (
              <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> {t("common.sending") || "Sending..."}</>
            ) : (
              <><Mail className="w-4 h-4 mr-2" /> {t("jobAlerts.sendDigestNow") || "Send Daily Digest Now"}</>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Quick Alert Card */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2" style={{ fontFamily: 'IBM Plex Sans' }}>
            <Send className="w-5 h-5" />
            {t("jobAlerts.quickAlert") || "Quick Job Alert"}
          </CardTitle>
          <CardDescription>
            {t("jobAlerts.quickAlertDesc") || "Send all matching jobs (may include previously sent jobs)"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={sendAlertNow} disabled={sending || !email} variant="outline" data-testid="send-alert-btn">
            {sending ? (
              <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> {t("common.sending") || "Sending..."}</>
            ) : (
              <><Send className="w-4 h-4 mr-2" /> {t("jobAlerts.sendAlertNow") || "Send Alert Now"}</>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* How it works */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2" style={{ fontFamily: 'IBM Plex Sans' }}>
            <Settings className="w-5 h-5" />
            {t("jobAlerts.howItWorks") || "How Automated Digest Works"}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-violet-100 flex items-center justify-center text-violet-600 font-medium">1</div>
            <div>
              <h4 className="font-medium text-slate-900 dark:text-slate-100">{t("jobAlerts.step1Title") || "Subscribe with your email"}</h4>
              <p className="text-sm text-slate-500 dark:text-slate-400">{t("jobAlerts.step1Desc") || "Toggle the subscription switch above to enable automatic emails"}</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-violet-100 flex items-center justify-center text-violet-600 font-medium">2</div>
            <div>
              <h4 className="font-medium text-slate-900 dark:text-slate-100">{t("jobAlerts.step2Title") || "Daily at 8:00 AM UTC"}</h4>
              <p className="text-sm text-slate-500 dark:text-slate-400">{t("jobAlerts.step2Desc") || "Our scheduler automatically searches for new jobs every morning"}</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-violet-100 flex items-center justify-center text-violet-600 font-medium">3</div>
            <div>
              <h4 className="font-medium text-slate-900 dark:text-slate-100">{t("jobAlerts.step3Title") || "Only fresh jobs, no duplicates"}</h4>
              <p className="text-sm text-slate-500 dark:text-slate-400">{t("jobAlerts.step3Desc") || "Jobs from the last 24 hours only - you'll never receive the same job twice"}</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-violet-100 flex items-center justify-center text-violet-600 font-medium">4</div>
            <div>
              <h4 className="font-medium text-slate-900 dark:text-slate-100">{t("jobAlerts.step4Title") || "AI-powered matching"}</h4>
              <p className="text-sm text-slate-500 dark:text-slate-400">{t("jobAlerts.step4Desc") || "Searches Indeed, LinkedIn, Glassdoor, ZipRecruiter + 5 more sources"}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default JobAlertsPage;
