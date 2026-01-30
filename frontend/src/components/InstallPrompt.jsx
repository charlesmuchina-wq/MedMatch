import { useState, useEffect } from "react";
import { X, Download, Smartphone, Monitor, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

/**
 * PWA Install Prompt Component
 * Shows a prompt to install the app when the browser supports it
 */
const InstallPrompt = () => {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [showPrompt, setShowPrompt] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);

  useEffect(() => {
    // Check if already installed
    if (window.matchMedia('(display-mode: standalone)').matches) {
      setIsInstalled(true);
      return;
    }

    // Check if dismissed recently
    const dismissed = localStorage.getItem('medmatch-pwa-dismissed');
    if (dismissed) {
      const dismissedTime = parseInt(dismissed, 10);
      const daysSinceDismissed = (Date.now() - dismissedTime) / (1000 * 60 * 60 * 24);
      if (daysSinceDismissed < 7) {
        return; // Don't show for 7 days after dismissal
      }
    }

    // Listen for the beforeinstallprompt event
    const handleBeforeInstall = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
      // Show prompt after a short delay
      setTimeout(() => setShowPrompt(true), 3000);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstall);

    // Listen for successful installation
    window.addEventListener('appinstalled', () => {
      setIsInstalled(true);
      setShowPrompt(false);
      setDeferredPrompt(null);
    });

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstall);
    };
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) return;

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    
    if (outcome === 'accepted') {
      console.log('PWA installed');
    }
    
    setDeferredPrompt(null);
    setShowPrompt(false);
  };

  const handleDismiss = () => {
    localStorage.setItem('medmatch-pwa-dismissed', Date.now().toString());
    setShowPrompt(false);
  };

  if (!showPrompt || isInstalled) return null;

  return (
    <div className="fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:w-96 z-50 animate-slide-up" data-testid="pwa-install-prompt">
      <Card className="shadow-2xl border-2 border-turquoise/30 bg-white dark:bg-slate-900">
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            {/* Logo */}
            <img 
              src="/logo-small.png" 
              alt="MedMatch" 
              className="w-12 h-12 rounded-xl flex-shrink-0 object-contain"
              data-testid="install-prompt-logo"
            />

            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-1">
                <h3 className="font-semibold text-slate-900 dark:text-slate-100 text-sm">
                  Install MedMatch
                </h3>
                <button 
                  onClick={handleDismiss}
                  className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              
              <p className="text-xs text-slate-500 dark:text-slate-400 mb-3">
                Add to your home screen for quick access, offline support, and a native app experience.
              </p>

              {/* Features */}
              <div className="flex items-center gap-4 mb-3 text-xs text-slate-500 dark:text-slate-400">
                <span className="flex items-center gap-1">
                  <Smartphone className="w-3 h-3" /> Mobile
                </span>
                <span className="flex items-center gap-1">
                  <Monitor className="w-3 h-3" /> Desktop
                </span>
                <span className="flex items-center gap-1">
                  <Sparkles className="w-3 h-3" /> Offline
                </span>
              </div>

              {/* Buttons */}
              <div className="flex gap-2">
                <Button 
                  size="sm" 
                  onClick={handleInstall}
                  className="flex-1 bg-gradient-to-r from-turquoise to-teal-600"
                >
                  <Download className="w-4 h-4 mr-1" />
                  Install
                </Button>
                <Button 
                  size="sm" 
                  variant="outline" 
                  onClick={handleDismiss}
                  className="dark:border-slate-700"
                >
                  Later
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

/**
 * Hook to detect if app is installed as PWA
 */
export const useIsPWA = () => {
  const [isPWA, setIsPWA] = useState(false);

  useEffect(() => {
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches;
    const isIOSStandalone = window.navigator.standalone === true;
    setIsPWA(isStandalone || isIOSStandalone);
  }, []);

  return isPWA;
};

export default InstallPrompt;
