import { useState, useEffect } from "react";
import { 
  Shield, Download, Trash2, FileText, Mic, Brain, 
  ChevronRight, AlertTriangle, Check, ExternalLink,
  Clock, Eye, Building2, Languages, Globe
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { useTranslation } from "@/utils/i18n";
import { useBrowserTranslationDetection, openGoogleTranslate, triggerBrowserTranslate } from "@/components/GlobalLanguageSelector";
import axios from "axios";
import { toast } from "sonner";

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * Privacy Settings Page
 * GDPR/CCPA compliant data management
 */
const PrivacySettingsPage = () => {
  const { t } = useTranslation();
  const [consentStatus, setConsentStatus] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);
  const [subProcessors, setSubProcessors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [exportingData, setExportingData] = useState(false);
  const [deletingData, setDeletingData] = useState(false);
  const [deleteOptions, setDeleteOptions] = useState({
    delete_resume: false,
    delete_voice_history: false,
    delete_applications: false,
    delete_matches: false,
    delete_account: false
  });

  useEffect(() => {
    fetchPrivacyData();
  }, []);

  const fetchPrivacyData = async () => {
    setLoading(true);
    const token = localStorage.getItem("medmatch-token");
    const headers = { Authorization: `Bearer ${token}` };

    try {
      const [consentRes, logsRes, processorsRes] = await Promise.all([
        axios.get(`${API}/api/privacy/consent/status`, { headers }),
        axios.get(`${API}/api/privacy/audit/logs?limit=10`, { headers }),
        axios.get(`${API}/api/privacy/sub-processors`)
      ]);

      setConsentStatus(consentRes.data);
      setAuditLogs(logsRes.data.logs || []);
      setSubProcessors(processorsRes.data.sub_processors || []);
    } catch (err) {
      console.error("Error fetching privacy data:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleExportData = async () => {
    setExportingData(true);
    try {
      const token = localStorage.getItem("medmatch-token");
      const response = await axios.get(
        `${API}/api/privacy/data/export`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      // Download as JSON
      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `medmatch-data-export-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
      
      toast.success("Data exported successfully!");
    } catch (err) {
      toast.error("Failed to export data");
    } finally {
      setExportingData(false);
    }
  };

  const handleDeleteData = async () => {
    if (!Object.values(deleteOptions).some(v => v)) {
      toast.error("Please select data to delete");
      return;
    }

    setDeletingData(true);
    try {
      const token = localStorage.getItem("medmatch-token");
      const response = await axios.post(
        `${API}/api/privacy/data/delete`,
        deleteOptions,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      toast.success("Data deleted successfully");
      
      if (deleteOptions.delete_account) {
        // Logout if account deleted
        localStorage.clear();
        window.location.href = "/login";
      } else {
        fetchPrivacyData();
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to delete data");
    } finally {
      setDeletingData(false);
    }
  };

  const handleWithdrawConsent = async () => {
    try {
      const token = localStorage.getItem("medmatch-token");
      await axios.post(
        `${API}/api/privacy/consent/withdraw`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      toast.success("Consent withdrawn. AI-processed data will be deleted.");
      localStorage.removeItem("medmatch-consent-granted");
      fetchPrivacyData();
    } catch (err) {
      toast.error("Failed to withdraw consent");
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return "N/A";
    return new Date(dateString).toLocaleString();
  };

  if (loading) {
    return (
      <div className="p-6 md:p-8 max-w-4xl mx-auto">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-slate-200 dark:bg-slate-700 rounded w-1/3" />
          <div className="h-32 bg-slate-200 dark:bg-slate-700 rounded" />
          <div className="h-32 bg-slate-200 dark:bg-slate-700 rounded" />
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 md:p-8 max-w-4xl mx-auto" data-testid="privacy-settings-page">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Shield className="w-8 h-8 text-turquoise" />
          <h1 className="text-2xl md:text-3xl font-semibold text-slate-900 dark:text-slate-100" style={{ fontFamily: 'IBM Plex Sans' }}>
            Privacy & Data
          </h1>
        </div>
        <p className="text-slate-500 dark:text-slate-400">
          Manage your data, consent preferences, and privacy settings
        </p>
      </div>

      {/* Consent Status */}
      <Card className="mb-6">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-lg">Your Consents</CardTitle>
              <CardDescription>Active data processing permissions</CardDescription>
            </div>
            {consentStatus?.has_consented && (
              <Badge className="bg-emerald-500 text-white">Active</Badge>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {consentStatus?.consent ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-slate-400" />
                  <span className="text-sm">Resume Processing</span>
                  {consentStatus.consent.resume_processing ? (
                    <Check className="w-4 h-4 text-emerald-500 ml-auto" />
                  ) : (
                    <span className="text-xs text-slate-400 ml-auto">Off</span>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <Mic className="w-4 h-4 text-slate-400" />
                  <span className="text-sm">Voice Processing</span>
                  {consentStatus.consent.voice_processing ? (
                    <Check className="w-4 h-4 text-emerald-500 ml-auto" />
                  ) : (
                    <span className="text-xs text-slate-400 ml-auto">Off</span>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <Brain className="w-4 h-4 text-slate-400" />
                  <span className="text-sm">AI Matching</span>
                  {consentStatus.consent.ai_matching ? (
                    <Check className="w-4 h-4 text-emerald-500 ml-auto" />
                  ) : (
                    <span className="text-xs text-slate-400 ml-auto">Off</span>
                  )}
                </div>
              </div>
              
              <div className="text-xs text-slate-400">
                Consent granted: {formatDate(consentStatus.consent.granted_at)}
              </div>

              <Button
                variant="outline"
                size="sm"
                className="text-rose-500 border-rose-200 hover:bg-rose-50"
                onClick={handleWithdrawConsent}
              >
                Withdraw All Consents
              </Button>
            </div>
          ) : (
            <div className="text-center py-4">
              <p className="text-slate-500 mb-4">No active consents. Some features may be limited.</p>
              <Button asChild>
                <a href="/consent">Grant Consent</a>
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Data Management */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-lg">Your Data</CardTitle>
          <CardDescription>Export or delete your personal data</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Export Data */}
          <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
            <div className="flex items-center gap-3">
              <Download className="w-5 h-5 text-turquoise" />
              <div>
                <p className="font-medium text-slate-900 dark:text-slate-100">Export All Data</p>
                <p className="text-xs text-slate-500">Download your data in JSON format (GDPR portability)</p>
              </div>
            </div>
            <Button
              variant="outline"
              onClick={handleExportData}
              disabled={exportingData}
              data-testid="export-data-btn"
            >
              {exportingData ? "Exporting..." : "Export"}
            </Button>
          </div>

          {/* Delete Data */}
          <Dialog>
            <DialogTrigger asChild>
              <div className="flex items-center justify-between p-4 bg-rose-50 dark:bg-rose-900/20 rounded-lg cursor-pointer hover:bg-rose-100 dark:hover:bg-rose-900/30 transition-colors">
                <div className="flex items-center gap-3">
                  <Trash2 className="w-5 h-5 text-rose-500" />
                  <div>
                    <p className="font-medium text-slate-900 dark:text-slate-100">Delete Data</p>
                    <p className="text-xs text-slate-500">Permanently remove your data (GDPR erasure)</p>
                  </div>
                </div>
                <ChevronRight className="w-5 h-5 text-slate-400" />
              </div>
            </DialogTrigger>
            
            <DialogContent>
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2 text-rose-600">
                  <AlertTriangle className="w-5 h-5" />
                  Delete Your Data
                </DialogTitle>
              </DialogHeader>
              
              <div className="space-y-4 py-4">
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  Select the data you want to permanently delete. This action cannot be undone.
                </p>
                
                <div className="space-y-3">
                  {[
                    { key: "delete_resume", label: "Resume & Profile", icon: FileText },
                    { key: "delete_voice_history", label: "Voice Transcriptions", icon: Mic },
                    { key: "delete_matches", label: "AI Match History & Saved Jobs", icon: Brain },
                    { key: "delete_applications", label: "Job Applications", icon: Building2 },
                    { key: "delete_account", label: "Entire Account", icon: Trash2, danger: true }
                  ].map(({ key, label, icon: Icon, danger }) => (
                    <label key={key} className={`flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors ${
                      danger 
                        ? "bg-rose-50 dark:bg-rose-900/20 hover:bg-rose-100" 
                        : "bg-slate-50 dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700"
                    }`}>
                      <input
                        type="checkbox"
                        checked={deleteOptions[key]}
                        onChange={(e) => setDeleteOptions(prev => ({
                          ...prev,
                          [key]: e.target.checked
                        }))}
                        className="w-4 h-4"
                      />
                      <Icon className={`w-4 h-4 ${danger ? "text-rose-500" : "text-slate-400"}`} />
                      <span className={`text-sm ${danger ? "text-rose-700 dark:text-rose-400 font-medium" : ""}`}>
                        {label}
                      </span>
                    </label>
                  ))}
                </div>
              </div>
              
              <DialogFooter>
                <Button
                  variant="destructive"
                  onClick={handleDeleteData}
                  disabled={deletingData || !Object.values(deleteOptions).some(v => v)}
                  data-testid="confirm-delete-btn"
                >
                  {deletingData ? "Deleting..." : "Delete Selected Data"}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </CardContent>
      </Card>

      {/* Third-Party Services */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-lg">Third-Party Services</CardTitle>
          <CardDescription>Services that process your data (sub-processors)</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {subProcessors.map((processor, i) => (
              <div key={i} className="flex items-start gap-3 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
                <Building2 className="w-5 h-5 text-slate-400 mt-0.5" />
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-slate-900 dark:text-slate-100">{processor.name}</span>
                    {processor.dpa_signed && (
                      <Badge variant="outline" className="text-xs text-emerald-600 border-emerald-200">
                        DPA Signed
                      </Badge>
                    )}
                  </div>
                  <p className="text-xs text-slate-500 mt-1">{processor.service}</p>
                  <p className="text-xs text-slate-400">Location: {processor.location}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Audit Log */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Eye className="w-5 h-5" />
            Privacy Activity Log
          </CardTitle>
          <CardDescription>Recent privacy-related actions on your account</CardDescription>
        </CardHeader>
        <CardContent>
          {auditLogs.length > 0 ? (
            <div className="space-y-2">
              {auditLogs.map((log, i) => (
                <div key={i} className="flex items-center gap-3 p-2 text-sm border-b last:border-0">
                  <Clock className="w-4 h-4 text-slate-400" />
                  <span className="text-slate-600 dark:text-slate-400">
                    {log.action.replace(/_/g, " ")}
                  </span>
                  <span className="text-xs text-slate-400 ml-auto">
                    {formatDate(log.timestamp)}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-500 text-center py-4">
              No recent privacy activity
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default PrivacySettingsPage;
