import { useState, useEffect } from "react";
import { Download, X, Smartphone, Monitor, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useTranslation } from "@/utils/i18n";

/**
 * PWA Install Prompt Component
 * Shows an install banner for users who can install the app
 */
const PWAInstallPrompt = () => {
  const { t } = useTranslation();
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [showPrompt, setShowPrompt] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);
  const [platform, setPlatform] = useState("desktop");
  
  // Check if already installed on mount
  const isAlreadyInstalled = window.matchMedia("(display-mode: standalone)").matches;

  useEffect(() => {
    if (isAlreadyInstalled) {
      return;
    }

    // Detect platform
    const userAgent = navigator.userAgent.toLowerCase();
    if (/android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent)) {
      setPlatform("mobile");
    }

    // Listen for install prompt
    const handleBeforeInstallPrompt = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
      
      // Check if dismissed recently
      const dismissed = localStorage.getItem("pwa-install-dismissed");
      if (dismissed) {
        const dismissedTime = parseInt(dismissed, 10);
        const daysSinceDismissed = (Date.now() - dismissedTime) / (1000 * 60 * 60 * 24);
        if (daysSinceDismissed < 7) return; // Don't show for 7 days after dismiss
      }
      
      setShowPrompt(true);
    };

    // Listen for successful install
    const handleAppInstalled = () => {
      setIsInstalled(true);
      setShowPrompt(false);
      setDeferredPrompt(null);
    };

    window.addEventListener("beforeinstallprompt", handleBeforeInstallPrompt);
    window.addEventListener("appinstalled", handleAppInstalled);

    return () => {
      window.removeEventListener("beforeinstallprompt", handleBeforeInstallPrompt);
      window.removeEventListener("appinstalled", handleAppInstalled);
    };
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) return;

    try {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      
      if (outcome === "accepted") {
        setIsInstalled(true);
      }
      
      setDeferredPrompt(null);
      setShowPrompt(false);
    } catch (error) {
      console.error("Install prompt error:", error);
    }
  };

  const handleDismiss = () => {
    localStorage.setItem("pwa-install-dismissed", Date.now().toString());
    setShowPrompt(false);
  };

  if (isInstalled || !showPrompt) return null;

  return (
    <div className="fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:w-96 z-50 animate-slide-up">
      <Card className="bg-gradient-to-r from-turquoise/10 to-teal-500/10 border-turquoise/30 shadow-xl">
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-turquoise to-teal-600 flex items-center justify-center flex-shrink-0">
              {platform === "mobile" ? (
                <Smartphone className="w-6 h-6 text-white" />
              ) : (
                <Monitor className="w-6 h-6 text-white" />
              )}
            </div>
            
            <div className="flex-1 min-w-0">
              <h4 className="font-semibold text-slate-900 dark:text-slate-100 text-sm">
                {t("pwa.installTitle") || "Install MedMatch"}
              </h4>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                {platform === "mobile" 
                  ? (t("pwa.installMobileDesc") || "Add to home screen for quick access")
                  : (t("pwa.installDesktopDesc") || "Install as a desktop app for quick access")}
              </p>
              
              <div className="flex items-center gap-2 mt-3">
                <Button size="sm" onClick={handleInstall} className="bg-turquoise hover:bg-turquoise/90">
                  <Download className="w-4 h-4 mr-1" />
                  {t("pwa.install") || "Install"}
                </Button>
                <Button size="sm" variant="ghost" onClick={handleDismiss}>
                  {t("common.later") || "Later"}
                </Button>
              </div>
            </div>
            
            <button 
              onClick={handleDismiss}
              className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
          
          {/* Features */}
          <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-700">
            <div className="flex items-center gap-4 text-xs text-slate-500 dark:text-slate-400">
              <span className="flex items-center gap-1">
                <Check className="w-3 h-3 text-green-500" />
                {t("pwa.featureOffline") || "Works offline"}
              </span>
              <span className="flex items-center gap-1">
                <Check className="w-3 h-3 text-green-500" />
                {t("pwa.featureNotifications") || "Push notifications"}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PWAInstallPrompt;
