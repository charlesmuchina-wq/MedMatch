import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Calendar, Mail, Trash2, Send, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const JobAlertsPage = ({ resume }) => {
  const [sending, setSending] = useState(false);
  const [sendingDigest, setSendingDigest] = useState(false);
  const [email, setEmail] = useState("");
  const [digestHistory, setDigestHistory] = useState([]);

  useEffect(() => {
    if (resume?.email) setEmail(resume.email);
    // Load digest history
    if (resume?.email) {
      axios.get(`${API}/digest/history?email=${resume.email}`).then(res => {
        setDigestHistory(res.data.history || []);
      }).catch(() => {});
    }
  }, [resume]);

  const sendAlertNow = async () => {
    if (!email) {
      toast.error("Please enter an email address");
      return;
    }
    setSending(true);
    try {
      const response = await axios.post(`${API}/alerts/send-now`, { email });
      toast.success(response.data.message);
    } catch (e) {
      toast.error("Failed to send alert");
    }
    setSending(false);
  };

  const sendDailyDigest = async () => {
    if (!email) {
      toast.error("Please enter an email address");
      return;
    }
    setSendingDigest(true);
    try {
      const response = await axios.post(`${API}/digest/send-daily`, { email });
      toast.success(`${response.data.message} (${response.data.jobs_count} new jobs)`);
      // Refresh history
      const historyRes = await axios.get(`${API}/digest/history?email=${email}`);
      setDigestHistory(historyRes.data.history || []);
    } catch (e) {
      toast.error("Failed to send daily digest");
    }
    setSendingDigest(false);
  };

  const clearHistory = async () => {
    try {
      await axios.delete(`${API}/digest/history/${email}`);
      setDigestHistory([]);
      toast.success("Digest history cleared - you'll receive all jobs again");
    } catch (e) {
      toast.error("Failed to clear history");
    }
  };

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-4xl mx-auto animate-fade-in" data-testid="alerts-page">
      <h1 className="text-3xl font-semibold text-slate-900 tracking-tight mb-8" style={{ fontFamily: 'IBM Plex Sans' }}>
        Job Alerts & Daily Digest
      </h1>

      {/* Daily Digest Card */}
      <Card className="mb-6 border-2 border-sky-200 bg-gradient-to-r from-sky-50 to-emerald-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2" style={{ fontFamily: 'IBM Plex Sans' }}>
            <Calendar className="w-5 h-5 text-sky-600" />
            Daily Digest (Last 24 Hours)
          </CardTitle>
          <CardDescription>
            Get only NEW jobs posted in the last 24 hours. No duplicate emails for the same jobs!
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-3 mb-4">
            <Input
              type="email"
              placeholder="Enter email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="flex-1 bg-white"
              data-testid="digest-email-input"
            />
            <Button 
              onClick={sendDailyDigest} 
              disabled={sendingDigest}
              className="bg-gradient-to-r from-sky-500 to-emerald-500 hover:from-sky-600 hover:to-emerald-600"
              data-testid="send-digest-btn"
            >
              {sendingDigest ? (
                <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Sending...</>
              ) : (
                <><Mail className="w-4 h-4 mr-2" /> Send Daily Digest</>
              )}
            </Button>
          </div>
          <div className="flex items-center gap-4 text-sm">
            <span className="text-slate-600">
              {digestHistory.length > 0 ? `${digestHistory.length} jobs already sent` : 'No jobs sent yet'}
            </span>
            {digestHistory.length > 0 && (
              <Button variant="ghost" size="sm" onClick={clearHistory} className="text-slate-500 hover:text-rose-500">
                <Trash2 className="w-3 h-3 mr-1" /> Clear History
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Regular Alert Card */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2" style={{ fontFamily: 'IBM Plex Sans' }}>
            <Send className="w-5 h-5" />
            Quick Job Alert
          </CardTitle>
          <CardDescription>
            Send all matching jobs (may include previously sent jobs)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={sendAlertNow} disabled={sending} variant="outline" data-testid="send-alert-btn">
            {sending ? (
              <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Sending...</>
            ) : (
              <><Send className="w-4 h-4 mr-2" /> Send Alert Now</>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* How it works */}
      <Card>
        <CardHeader>
          <CardTitle style={{ fontFamily: 'IBM Plex Sans' }}>How Daily Digest Works</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-sky-100 flex items-center justify-center text-sky-600 font-medium">1</div>
            <div>
              <h4 className="font-medium text-slate-900">Only jobs from last 24 hours</h4>
              <p className="text-sm text-slate-500">Filters out older postings so you only see fresh opportunities</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-sky-100 flex items-center justify-center text-sky-600 font-medium">2</div>
            <div>
              <h4 className="font-medium text-slate-900">No duplicate emails</h4>
              <p className="text-sm text-slate-500">We track which jobs were sent - you'll never get the same job twice</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-sky-100 flex items-center justify-center text-sky-600 font-medium">3</div>
            <div>
              <h4 className="font-medium text-slate-900">AI-powered matching</h4>
              <p className="text-sm text-slate-500">Searches Indeed, LinkedIn, Glassdoor, ZipRecruiter + 5 more sources</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default JobAlertsPage;
