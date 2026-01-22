import { useState, useCallback, useEffect } from "react";
import { 
  Cloud, Upload, X, Loader2, FileText, Check, AlertCircle,
  HardDrive, Folder
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { toast } from "sonner";
import { useTranslation } from "@/utils/i18n";
import { apiClient } from "@/utils/apiClient";
import axios from "axios";

const API = process.env.REACT_APP_BACKEND_URL;
const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID;
const GOOGLE_API_KEY = process.env.REACT_APP_GOOGLE_API_KEY;

// Default cloud provider configurations
const DEFAULT_PROVIDERS = {
  google_drive: {
    name: "Google Drive",
    icon: "/icons/google-drive.svg",
    color: "from-blue-500 to-blue-600",
    bgColor: "bg-blue-50 dark:bg-blue-900/20",
    accepts: ".pdf,.doc,.docx",
    configured: false
  },
  dropbox: {
    name: "Dropbox",
    icon: "/icons/dropbox.svg", 
    color: "from-blue-600 to-blue-700",
    bgColor: "bg-blue-50 dark:bg-blue-900/20",
    accepts: ".pdf,.doc,.docx",
    configured: false
  },
  onedrive: {
    name: "OneDrive",
    icon: "/icons/onedrive.svg",
    color: "from-sky-500 to-sky-600", 
    bgColor: "bg-sky-50 dark:bg-sky-900/20",
    accepts: ".pdf,.doc,.docx",
    configured: false
  }
};

/**
 * Cloud Storage Resume Upload Component
 * Allows users to upload resumes from Google Drive, Dropbox, or OneDrive
 */
const CloudStorageUpload = ({ onFileSelected, isLoading }) => {
  const { t } = useTranslation();
  const [showPicker, setShowPicker] = useState(false);
  const [activeProvider, setActiveProvider] = useState(null);
  const [pickerLoading, setPickerLoading] = useState(false);
  const [googleApiLoaded, setGoogleApiLoaded] = useState(false);
  const [tokenClient, setTokenClient] = useState(null);
  const [accessToken, setAccessToken] = useState(null);
  const [cloudProviders, setCloudProviders] = useState(DEFAULT_PROVIDERS);
  const [statusLoading, setStatusLoading] = useState(true);

  // Fetch cloud storage status from backend
  useEffect(() => {
    const fetchCloudStatus = async () => {
      try {
        const response = await fetch(`${API}/api/cloud/status`);
        if (response.ok) {
          const data = await response.json();
          setCloudProviders(prev => ({
            google_drive: {
              ...prev.google_drive,
              configured: data.google_drive?.configured || (!!GOOGLE_CLIENT_ID && !!GOOGLE_API_KEY)
            },
            dropbox: {
              ...prev.dropbox,
              configured: data.dropbox?.configured || false
            },
            onedrive: {
              ...prev.onedrive,
              configured: data.onedrive?.configured || false
            }
          }));
        }
      } catch (error) {
        console.error("Failed to fetch cloud status:", error);
        // Fallback to checking Google credentials locally
        setCloudProviders(prev => ({
          ...prev,
          google_drive: {
            ...prev.google_drive,
            configured: !!GOOGLE_CLIENT_ID && !!GOOGLE_API_KEY
          }
        }));
      } finally {
        setStatusLoading(false);
      }
    };

    fetchCloudStatus();
  }, []);

  // Load Google APIs on mount
  useEffect(() => {
    if (GOOGLE_CLIENT_ID && GOOGLE_API_KEY) {
      loadGoogleApis();
    }
  }, []);

  // Load Google Identity Services and Picker API
  const loadGoogleApis = useCallback(async () => {
    try {
      // Load Google Identity Services (GIS) for OAuth
      await loadScript('https://accounts.google.com/gsi/client');
      
      // Load Google API for Picker
      await loadScript('https://apis.google.com/js/api.js');
      
      // Initialize gapi
      await new Promise((resolve) => {
        window.gapi.load('picker', resolve);
      });

      // Initialize token client for OAuth
      const client = window.google.accounts.oauth2.initTokenClient({
        client_id: GOOGLE_CLIENT_ID,
        scope: 'https://www.googleapis.com/auth/drive.readonly',
        callback: (response) => {
          if (response.access_token) {
            setAccessToken(response.access_token);
            // Open picker after getting token
            createAndOpenPicker(response.access_token);
          }
        },
      });
      
      setTokenClient(client);
      setGoogleApiLoaded(true);
      console.log('Google APIs loaded successfully');
    } catch (error) {
      console.error('Failed to load Google APIs:', error);
    }
  }, []);

  // Create and open Google Drive Picker
  const createAndOpenPicker = useCallback((token) => {
    if (!window.google?.picker) {
      toast.error('Google Picker API not loaded');
      setPickerLoading(false);
      return;
    }

    try {
      const docsView = new window.google.picker.DocsView()
        .setIncludeFolders(true)
        .setMimeTypes('application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        .setMode(window.google.picker.DocsViewMode.LIST);

      const picker = new window.google.picker.PickerBuilder()
        .addView(docsView)
        .setOAuthToken(token)
        .setDeveloperKey(GOOGLE_API_KEY)
        .setCallback(handleGooglePickerCallback)
        .setTitle('Select your resume')
        .build();
      
      picker.setVisible(true);
      setPickerLoading(false);
    } catch (error) {
      console.error('Error creating picker:', error);
      toast.error('Failed to open Google Drive picker');
      setPickerLoading(false);
    }
  }, []);

  // Handle file selection from Google Drive
  const handleGooglePickerCallback = useCallback(async (data) => {
    if (data[window.google.picker.Response.ACTION] === window.google.picker.Action.PICKED) {
      const doc = data[window.google.picker.Response.DOCUMENTS][0];
      const fileId = doc[window.google.picker.Document.ID];
      const fileName = doc[window.google.picker.Document.NAME];
      const mimeType = doc[window.google.picker.Document.MIME_TYPE];

      toast.loading(`Downloading ${fileName}...`, { id: 'download-toast' });

      try {
        // Download file content via backend proxy (to avoid CORS issues)
        const response = await axios.post(`${API}/api/cloud/google-drive/download`, {
          file_id: fileId,
          access_token: accessToken
        }, {
          responseType: 'blob'
        });

        const blob = response.data;
        const file = new File([blob], fileName, { type: mimeType });
        
        toast.dismiss('download-toast');
        toast.success(`Imported ${fileName} from Google Drive`);
        
        if (onFileSelected) {
          onFileSelected(file);
        }
        
        setShowPicker(false);
      } catch (error) {
        toast.dismiss('download-toast');
        console.error('Error downloading file:', error);
        
        // Fallback: Try direct download via Google Drive API
        try {
          const downloadUrl = `https://www.googleapis.com/drive/v3/files/${fileId}?alt=media`;
          const directResponse = await fetch(downloadUrl, {
            headers: {
              'Authorization': `Bearer ${accessToken}`
            }
          });
          
          if (directResponse.ok) {
            const blob = await directResponse.blob();
            const file = new File([blob], fileName, { type: mimeType });
            
            toast.success(`Imported ${fileName} from Google Drive`);
            
            if (onFileSelected) {
              onFileSelected(file);
            }
            
            setShowPicker(false);
          } else {
            throw new Error('Direct download failed');
          }
        } catch (fallbackError) {
          toast.error('Failed to download file from Google Drive');
        }
      }
    } else if (data[window.google.picker.Response.ACTION] === window.google.picker.Action.CANCEL) {
      setPickerLoading(false);
    }
  }, [accessToken, onFileSelected]);

  // Google Drive Picker
  const openGoogleDrivePicker = useCallback(async () => {
    setPickerLoading(true);
    
    if (!GOOGLE_CLIENT_ID || !GOOGLE_API_KEY) {
      toast.error('Google Drive not configured. Contact administrator.');
      setPickerLoading(false);
      return;
    }

    if (!googleApiLoaded) {
      toast.loading('Loading Google Drive...', { id: 'loading-toast' });
      await loadGoogleApis();
      toast.dismiss('loading-toast');
    }

    // Request access token
    if (tokenClient) {
      if (accessToken) {
        // Already have token, open picker directly
        createAndOpenPicker(accessToken);
      } else {
        // Request new token (will trigger callback which opens picker)
        tokenClient.requestAccessToken({ prompt: 'consent' });
      }
    } else {
      toast.error('Google authentication not ready. Please try again.');
      setPickerLoading(false);
    }
  }, [googleApiLoaded, tokenClient, accessToken, loadGoogleApis, createAndOpenPicker]);

  // Dropbox Chooser
  const openDropboxChooser = useCallback(() => {
    setPickerLoading(true);
    toast.info("Dropbox integration requires API setup. Use direct upload or Google Drive.");
    setPickerLoading(false);
  }, []);

  // OneDrive Picker
  const openOneDrivePicker = useCallback(() => {
    setPickerLoading(true);
    toast.info("OneDrive integration requires API setup. Use direct upload or Google Drive.");
    setPickerLoading(false);
  }, []);

  const handleProviderClick = (provider) => {
    setActiveProvider(provider);
    switch (provider) {
      case 'google_drive':
        openGoogleDrivePicker();
        break;
      case 'dropbox':
        openDropboxChooser();
        break;
      case 'onedrive':
        openOneDrivePicker();
        break;
      default:
        break;
    }
  };

  const getProviderStatus = (key) => {
    const provider = cloudProviders[key];
    if (provider?.configured) {
      return <Check className="w-4 h-4 text-green-500" />;
    }
    return <AlertCircle className="w-4 h-4 text-amber-500" />;
  };

  return (
    <>
      <Button
        variant="outline"
        onClick={() => setShowPicker(true)}
        disabled={isLoading}
        className="flex items-center gap-2"
        data-testid="cloud-storage-btn"
      >
        <Cloud className="w-4 h-4" />
        {t("cloudStorage.importFrom") || "Import from Cloud Storage"}
      </Button>

      <Dialog open={showPicker} onOpenChange={setShowPicker}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Cloud className="w-5 h-5 text-turquoise" />
              {t("cloudStorage.importFrom") || "Import Resume from Cloud"}
            </DialogTitle>
            <DialogDescription>
              {t("cloudStorage.selectFile") || "Select a cloud storage service to import your resume"}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-3 py-4">
            {statusLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-6 h-6 animate-spin text-turquoise" />
              </div>
            ) : (
              Object.entries(cloudProviders).map(([key, provider]) => (
              <button
                key={key}
                onClick={() => handleProviderClick(key)}
                disabled={pickerLoading || !provider.configured}
                className={`w-full p-4 rounded-lg border border-slate-200 dark:border-slate-700 
                  ${provider.configured ? 'hover:border-turquoise/50 cursor-pointer' : 'opacity-60 cursor-not-allowed'} 
                  transition-all flex items-center gap-4 ${provider.bgColor} 
                  ${pickerLoading && activeProvider === key ? 'opacity-50' : ''}`}
                data-testid={`cloud-${key}-btn`}
              >
                <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${provider.color} flex items-center justify-center`}>
                  {key === 'google_drive' && <HardDrive className="w-5 h-5 text-white" />}
                  {key === 'dropbox' && <Folder className="w-5 h-5 text-white" />}
                  {key === 'onedrive' && <Cloud className="w-5 h-5 text-white" />}
                </div>
                <div className="flex-1 text-left">
                  <h4 className="font-medium text-slate-900 dark:text-slate-100 flex items-center gap-2">
                    {provider.name}
                    {getProviderStatus(key)}
                  </h4>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    {provider.configured ? (t("cloudStorage.supportedTypes") || 'PDF, DOC, DOCX files') : (t("cloudStorage.comingSoon") || 'Not configured')}
                  </p>
                </div>
                {pickerLoading && activeProvider === key ? (
                  <Loader2 className="w-5 h-5 text-turquoise animate-spin" />
                ) : (
                  <Upload className="w-5 h-5 text-slate-400" />
                )}
              </button>
            ))
            )}
          </div>

          {/* Show status based on configured providers */}
          <div className="text-center text-xs text-slate-500 dark:text-slate-400 pt-2 border-t border-slate-200 dark:border-slate-700">
            {Object.values(cloudProviders).some(p => p.configured) ? (
              <>
                <Check className="w-3 h-3 inline mr-1 text-green-500" />
                {t("cloudStorage.connected") || "Cloud storage is ready to use"}
              </>
            ) : (
              <>
                <AlertCircle className="w-3 h-3 inline mr-1 text-amber-500" />
                {t("cloudStorage.notConfigured") || "No cloud storage configured"}
              </>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
};

// Helper to load external scripts
function loadScript(src) {
  return new Promise((resolve, reject) => {
    // Check if already loaded
    if (document.querySelector(`script[src="${src}"]`)) {
      resolve();
      return;
    }
    
    const script = document.createElement('script');
    script.src = src;
    script.async = true;
    script.onload = resolve;
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

export default CloudStorageUpload;
