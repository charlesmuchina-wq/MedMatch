import { useState, useEffect, useCallback } from "react";
import { Linkedin, Link2, Unlink, RefreshCw, Check, AlertCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { useTranslation } from "@/utils/i18n";
import { apiClient } from "@/utils/apiClient";

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * LinkedIn Profile Sync Component
 * Allows users to connect and sync their LinkedIn profile
 */
const LinkedInSync = ({ onSync }) => {
  const { t } = useTranslation();
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [connecting, setConnecting] = useState(false);

  const fetchStatus = useCallback(async () => {
    try {
      const response = await apiClient.get("/linkedin/status");
      setStatus(response);
    } catch (error) {
      console.error("Failed to fetch LinkedIn status:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleOAuthCallback = useCallback(async (code) => {
    setConnecting(true);
    try {
      const redirectUri = `${window.location.origin}/settings?linkedin_callback=true`;
      await apiClient.post("/linkedin/token", {
        code,
        redirect_uri: redirectUri
      });
      
      toast.success(t("linkedin.connected") || "LinkedIn connected successfully!");
      
      // Clear URL params
      window.history.replaceState({}, document.title, window.location.pathname);
      
      await fetchStatus();
    } catch (error) {
      toast.error(t("linkedin.connectFailed") || "Failed to connect LinkedIn");
    } finally {
      setConnecting(false);
    }
  }, [t, fetchStatus]);

  useEffect(() => {
    fetchStatus();
    
    // Handle OAuth callback
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get("code");
    const state = urlParams.get("state");
    
    if (code && state && window.location.pathname.includes("linkedin")) {
      handleOAuthCallback(code);
    }
  }, [handleOAuthCallback, fetchStatus]);

  const handleConnect = async () => {
    setConnecting(true);
    try {
      const redirectUri = `${window.location.origin}/settings?linkedin_callback=true`;
      const response = await apiClient.get(`/linkedin/auth-url?redirect_uri=${encodeURIComponent(redirectUri)}`);
      
      if (response.auth_url) {
        window.location.href = response.auth_url;
      }
    } catch (error) {
      toast.error(t("linkedin.connectFailed") || "Failed to connect LinkedIn");
      setConnecting(false);
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    try {
      const response = await apiClient.post("/linkedin/sync");
      toast.success(t("linkedin.synced") || "Profile synced successfully!");
      await fetchStatus();
      if (onSync) onSync(response.synced_data);
    } catch (error) {
      if (error.response?.status === 401) {
        toast.error(t("linkedin.tokenExpired") || "LinkedIn token expired. Please reconnect.");
        setStatus(prev => ({ ...prev, user_connected: false }));
      } else {
        toast.error(t("linkedin.syncFailed") || "Failed to sync profile");
      }
    } finally {
      setSyncing(false);
    }
  };

  const handleDisconnect = async () => {
    try {
      await apiClient.delete("/linkedin/disconnect");
      toast.success(t("linkedin.disconnected") || "LinkedIn disconnected");
      setStatus(prev => ({ ...prev, user_connected: false, connection_details: null }));
    } catch (error) {
      toast.error(t("linkedin.disconnectFailed") || "Failed to disconnect");
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6 flex items-center justify-center">
          <Loader2 className="w-6 h-6 animate-spin text-turquoise" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-[#0A66C2] flex items-center justify-center">
              <Linkedin className="w-5 h-5 text-white" />
            </div>
            <div>
              <CardTitle className="text-lg">{t("linkedin.title") || "LinkedIn Profile"}</CardTitle>
              <CardDescription>
                {t("linkedin.description") || "Import your profile data from LinkedIn"}
              </CardDescription>
            </div>
          </div>
          {status?.user_connected && (
            <Badge variant="outline" className="text-green-600 border-green-300 bg-green-50">
              <Check className="w-3 h-3 mr-1" />
              {t("linkedin.connected") || "Connected"}
            </Badge>
          )}
        </div>
      </CardHeader>
      
      <CardContent>
        {!status?.integration_configured ? (
          <div className="flex items-center gap-3 p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg">
            <AlertCircle className="w-5 h-5 text-amber-500" />
            <div>
              <p className="text-sm font-medium text-amber-800 dark:text-amber-200">
                {t("linkedin.notConfigured") || "LinkedIn integration not configured"}
              </p>
              <p className="text-xs text-amber-600 dark:text-amber-400 mt-1">
                {t("linkedin.contactAdmin") || "Contact administrator to enable LinkedIn sync"}
              </p>
            </div>
          </div>
        ) : status?.user_connected ? (
          <div className="space-y-4">
            {/* Connection Details */}
            <div className="flex items-center gap-4 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
              {status.connection_details?.linkedin_picture ? (
                <img 
                  src={status.connection_details.linkedin_picture} 
                  alt="LinkedIn profile"
                  className="w-12 h-12 rounded-full"
                />
              ) : (
                <div className="w-12 h-12 rounded-full bg-[#0A66C2] flex items-center justify-center text-white font-medium">
                  {status.connection_details?.linkedin_name?.[0] || "?"}
                </div>
              )}
              <div className="flex-1">
                <p className="font-medium text-slate-900 dark:text-slate-100">
                  {status.connection_details?.linkedin_name || "LinkedIn User"}
                </p>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {status.connection_details?.linkedin_email}
                </p>
                <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">
                  {t("linkedin.lastSynced") || "Last synced"}: {status.connection_details?.last_synced 
                    ? new Date(status.connection_details.last_synced).toLocaleDateString()
                    : "Never"}
                </p>
              </div>
            </div>
            
            {/* Actions */}
            <div className="flex items-center gap-2">
              <Button 
                onClick={handleSync} 
                disabled={syncing}
                className="bg-[#0A66C2] hover:bg-[#004182]"
              >
                {syncing ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <RefreshCw className="w-4 h-4 mr-2" />
                )}
                {t("linkedin.syncNow") || "Sync Now"}
              </Button>
              <Button variant="outline" onClick={handleDisconnect}>
                <Unlink className="w-4 h-4 mr-2" />
                {t("linkedin.disconnect") || "Disconnect"}
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <p className="text-sm text-slate-600 dark:text-slate-400">
              {t("linkedin.importInfo") || "Connect your LinkedIn account to import:"}
            </p>
            <ul className="text-sm text-slate-500 dark:text-slate-400 space-y-1">
              <li className="flex items-center gap-2">
                <Check className="w-4 h-4 text-green-500" />
                {t("linkedin.importName") || "Name and headline"}
              </li>
              <li className="flex items-center gap-2">
                <Check className="w-4 h-4 text-green-500" />
                {t("linkedin.importEmail") || "Email address"}
              </li>
              <li className="flex items-center gap-2">
                <Check className="w-4 h-4 text-green-500" />
                {t("linkedin.importPhoto") || "Profile photo"}
              </li>
            </ul>
            
            <Button 
              onClick={handleConnect} 
              disabled={connecting}
              className="w-full bg-[#0A66C2] hover:bg-[#004182]"
            >
              {connecting ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Link2 className="w-4 h-4 mr-2" />
              )}
              {t("linkedin.connect") || "Connect LinkedIn"}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default LinkedInSync;
