import { useState, useCallback } from "react";
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

// Cloud provider configurations
const CLOUD_PROVIDERS = {
  google_drive: {
    name: "Google Drive",
    icon: "/icons/google-drive.svg",
    color: "from-blue-500 to-blue-600",
    bgColor: "bg-blue-50 dark:bg-blue-900/20",
    accepts: ".pdf,.doc,.docx"
  },
  dropbox: {
    name: "Dropbox",
    icon: "/icons/dropbox.svg", 
    color: "from-blue-600 to-blue-700",
    bgColor: "bg-blue-50 dark:bg-blue-900/20",
    accepts: ".pdf,.doc,.docx"
  },
  onedrive: {
    name: "OneDrive",
    icon: "/icons/onedrive.svg",
    color: "from-sky-500 to-sky-600", 
    bgColor: "bg-sky-50 dark:bg-sky-900/20",
    accepts: ".pdf,.doc,.docx"
  }
};

/**
 * Cloud Storage Resume Upload Component
 * Allows users to upload resumes from Google Drive, Dropbox, or OneDrive
 */
const CloudStorageUpload = ({ onFileSelected, isLoading }) => {
  const [showPicker, setShowPicker] = useState(false);
  const [activeProvider, setActiveProvider] = useState(null);
  const [pickerLoading, setPickerLoading] = useState(false);

  // Google Drive Picker
  const openGoogleDrivePicker = useCallback(async () => {
    setPickerLoading(true);
    try {
      // Check if Google Picker API is loaded
      if (!window.google?.picker) {
        // Load Google Picker API
        await loadGooglePickerScript();
      }

      // Note: This requires Google API credentials
      // For now, we'll show a message that credentials are needed
      toast.info("Google Drive integration requires API setup. Use direct upload for now.");
      setPickerLoading(false);
      return;

    } catch (error) {
      console.error("Google Drive error:", error);
      toast.error("Failed to open Google Drive picker");
      setPickerLoading(false);
    }
  }, []);

  // Dropbox Chooser
  const openDropboxChooser = useCallback(() => {
    setPickerLoading(true);
    
    // Check if Dropbox SDK is loaded
    if (!window.Dropbox) {
      // Load Dropbox SDK
      const script = document.createElement('script');
      script.src = 'https://www.dropbox.com/static/api/2/dropins.js';
      script.id = 'dropboxjs';
      script.setAttribute('data-app-key', 'YOUR_DROPBOX_APP_KEY');
      script.onload = () => initDropboxChooser();
      document.body.appendChild(script);
    } else {
      initDropboxChooser();
    }
  }, []);

  const initDropboxChooser = () => {
    if (!window.Dropbox?.choose) {
      toast.info("Dropbox integration requires API setup. Use direct upload for now.");
      setPickerLoading(false);
      return;
    }

    window.Dropbox.choose({
      success: async (files) => {
        const file = files[0];
        if (file) {
          // Download file from Dropbox URL
          try {
            const response = await fetch(file.link);
            const blob = await response.blob();
            const fileObj = new File([blob], file.name, { type: blob.type });
            onFileSelected(fileObj);
            toast.success(`Imported ${file.name} from Dropbox`);
          } catch (error) {
            toast.error("Failed to download file from Dropbox");
          }
        }
        setPickerLoading(false);
        setShowPicker(false);
      },
      cancel: () => {
        setPickerLoading(false);
      },
      linkType: "direct",
      multiselect: false,
      extensions: ['.pdf', '.doc', '.docx'],
      folderselect: false
    });
  };

  // OneDrive Picker
  const openOneDrivePicker = useCallback(() => {
    setPickerLoading(true);
    
    // Check if OneDrive SDK is loaded
    if (!window.OneDrive) {
      // Load OneDrive SDK
      const script = document.createElement('script');
      script.src = 'https://js.live.net/v7.2/OneDrive.js';
      script.onload = () => initOneDrivePicker();
      document.body.appendChild(script);
    } else {
      initOneDrivePicker();
    }
  }, []);

  const initOneDrivePicker = () => {
    if (!window.OneDrive?.open) {
      toast.info("OneDrive integration requires API setup. Use direct upload for now.");
      setPickerLoading(false);
      return;
    }

    window.OneDrive.open({
      clientId: 'YOUR_ONEDRIVE_CLIENT_ID',
      action: 'download',
      multiSelect: false,
      advanced: {
        filter: '.pdf,.doc,.docx'
      },
      success: async (response) => {
        const file = response.value[0];
        if (file) {
          try {
            const downloadResponse = await fetch(file['@microsoft.graph.downloadUrl']);
            const blob = await downloadResponse.blob();
            const fileObj = new File([blob], file.name, { type: blob.type });
            onFileSelected(fileObj);
            toast.success(`Imported ${file.name} from OneDrive`);
          } catch (error) {
            toast.error("Failed to download file from OneDrive");
          }
        }
        setPickerLoading(false);
        setShowPicker(false);
      },
      cancel: () => {
        setPickerLoading(false);
      },
      error: (error) => {
        console.error("OneDrive error:", error);
        toast.error("OneDrive picker failed");
        setPickerLoading(false);
      }
    });
  };

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
        Import from Cloud
      </Button>

      <Dialog open={showPicker} onOpenChange={setShowPicker}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Cloud className="w-5 h-5 text-turquoise" />
              Import Resume from Cloud
            </DialogTitle>
            <DialogDescription>
              Select a cloud storage service to import your resume
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-3 py-4">
            {Object.entries(CLOUD_PROVIDERS).map(([key, provider]) => (
              <button
                key={key}
                onClick={() => handleProviderClick(key)}
                disabled={pickerLoading}
                className={`w-full p-4 rounded-lg border border-slate-200 dark:border-slate-700 hover:border-turquoise/50 transition-all flex items-center gap-4 ${provider.bgColor} ${pickerLoading && activeProvider === key ? 'opacity-50' : ''}`}
                data-testid={`cloud-${key}-btn`}
              >
                <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${provider.color} flex items-center justify-center`}>
                  {key === 'google_drive' && <HardDrive className="w-5 h-5 text-white" />}
                  {key === 'dropbox' && <Folder className="w-5 h-5 text-white" />}
                  {key === 'onedrive' && <Cloud className="w-5 h-5 text-white" />}
                </div>
                <div className="flex-1 text-left">
                  <h4 className="font-medium text-slate-900 dark:text-slate-100">
                    {provider.name}
                  </h4>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    PDF, DOC, DOCX files
                  </p>
                </div>
                {pickerLoading && activeProvider === key ? (
                  <Loader2 className="w-5 h-5 text-turquoise animate-spin" />
                ) : (
                  <Upload className="w-5 h-5 text-slate-400" />
                )}
              </button>
            ))}
          </div>

          <div className="text-center text-xs text-slate-500 dark:text-slate-400 pt-2 border-t border-slate-200 dark:border-slate-700">
            <AlertCircle className="w-3 h-3 inline mr-1" />
            Cloud integrations require API setup. Contact admin for configuration.
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
};

// Helper to load Google Picker script
async function loadGooglePickerScript() {
  return new Promise((resolve, reject) => {
    if (window.google?.picker) {
      resolve();
      return;
    }
    const script = document.createElement('script');
    script.src = 'https://apis.google.com/js/api.js';
    script.onload = () => {
      window.gapi.load('picker', resolve);
    };
    script.onerror = reject;
    document.body.appendChild(script);
  });
}

export default CloudStorageUpload;
