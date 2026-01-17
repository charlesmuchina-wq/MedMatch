import { useState, useEffect } from "react";
import { Wifi, WifiOff, Cloud, CloudOff, RefreshCw, Check, AlertCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { offlineStorage } from "@/utils/offlineStorage";

// Offline Status Indicator Component
export const OfflineIndicator = ({ compact = false }) => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [pendingCount, setPendingCount] = useState(0);
  const [syncing, setSyncing] = useState(false);
  const [lastSync, setLastSync] = useState(null);

  useEffect(() => {
    const updateStatus = async () => {
      try {
        const info = await offlineStorage.getStorageInfo();
        setPendingCount(info.pendingActions.count);
        setLastSync(info.jobs.lastSync);
      } catch (e) {
        console.error("Failed to get storage info:", e);
      }
    };

    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    const unsubscribe = offlineStorage.addListener((event) => {
      if (event.type === 'syncStart') setSyncing(true);
      if (event.type === 'syncComplete') {
        setSyncing(false);
        updateStatus();
      }
      if (event.type === 'online' || event.type === 'offline') {
        setIsOnline(event.type === 'online');
      }
    });

    updateStatus();

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      unsubscribe();
    };
  }, []);

  const handleSync = async () => {
    setSyncing(true);
    try {
      await offlineStorage.syncPendingActions();
    } finally {
      setSyncing(false);
    }
  };

  if (compact) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs ${
              isOnline 
                ? "bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400" 
                : "bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400"
            }`}>
              {isOnline ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
              {pendingCount > 0 && (
                <span className="bg-amber-500 text-white rounded-full px-1 text-[10px]">
                  {pendingCount}
                </span>
              )}
            </div>
          </TooltipTrigger>
          <TooltipContent>
            <p>{isOnline ? "Online" : "Offline Mode"}</p>
            {pendingCount > 0 && <p className="text-xs">{pendingCount} pending actions</p>}
            {lastSync && <p className="text-xs text-slate-400">Last sync: {new Date(lastSync).toLocaleString()}</p>}
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  return (
    <div className={`flex items-center gap-3 p-3 rounded-lg ${
      isOnline 
        ? "bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800" 
        : "bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800"
    }`}>
      <div className={`p-2 rounded-full ${
        isOnline ? "bg-emerald-100 dark:bg-emerald-800" : "bg-amber-100 dark:bg-amber-800"
      }`}>
        {isOnline ? (
          <Cloud className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
        ) : (
          <CloudOff className="w-5 h-5 text-amber-600 dark:text-amber-400" />
        )}
      </div>

      <div className="flex-1">
        <p className={`font-medium text-sm ${
          isOnline ? "text-emerald-700 dark:text-emerald-300" : "text-amber-700 dark:text-amber-300"
        }`}>
          {isOnline ? "Connected" : "Offline Mode"}
        </p>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          {isOnline 
            ? "All changes sync automatically" 
            : "Changes will sync when back online"}
        </p>
      </div>

      {pendingCount > 0 && (
        <Badge variant="secondary" className="bg-amber-100 text-amber-700">
          {pendingCount} pending
        </Badge>
      )}

      {isOnline && pendingCount > 0 && (
        <Button 
          size="sm" 
          variant="ghost" 
          onClick={handleSync}
          disabled={syncing}
        >
          <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
        </Button>
      )}
    </div>
  );
};

// Offline Banner Component (for top of page)
export const OfflineBanner = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [show, setShow] = useState(!navigator.onLine);

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      // Show "back online" message briefly
      setTimeout(() => setShow(false), 3000);
    };
    
    const handleOffline = () => {
      setIsOnline(false);
      setShow(true);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (!show) return null;

  return (
    <div className={`fixed top-0 left-0 right-0 z-50 px-4 py-2 text-center text-sm font-medium transition-all ${
      isOnline 
        ? "bg-emerald-500 text-white" 
        : "bg-amber-500 text-white"
    }`}>
      <div className="flex items-center justify-center gap-2">
        {isOnline ? (
          <>
            <Check className="w-4 h-4" />
            Back online! Syncing your changes...
          </>
        ) : (
          <>
            <WifiOff className="w-4 h-4" />
            You're offline. Don't worry - your work is saved locally.
          </>
        )}
      </div>
    </div>
  );
};

// Cached Data Indicator
export const CachedDataBadge = ({ dataType, lastSync }) => {
  if (!lastSync) return null;

  const syncDate = new Date(lastSync);
  const isStale = (Date.now() - syncDate.getTime()) > 24 * 60 * 60 * 1000; // 24 hours

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Badge 
            variant="outline" 
            className={`text-xs ${isStale ? "border-amber-300 text-amber-600" : "border-slate-300 text-slate-500"}`}
          >
            {isStale ? <AlertCircle className="w-3 h-3 mr-1" /> : null}
            Cached
          </Badge>
        </TooltipTrigger>
        <TooltipContent>
          <p>Last updated: {syncDate.toLocaleString()}</p>
          {isStale && <p className="text-amber-400 text-xs">Data may be outdated</p>}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};

// Storage Usage Component
export const StorageUsage = () => {
  const [storageInfo, setStorageInfo] = useState(null);

  useEffect(() => {
    const fetchInfo = async () => {
      const info = await offlineStorage.getStorageInfo();
      setStorageInfo(info);
    };
    fetchInfo();
  }, []);

  if (!storageInfo) return null;

  return (
    <div className="space-y-2 p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
      <h4 className="font-medium text-sm">Offline Storage</h4>
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="flex justify-between">
          <span className="text-slate-500">Cached Jobs:</span>
          <span>{storageInfo.jobs.count}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-500">Messages:</span>
          <span>{storageInfo.messages.count}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-500">Pending Actions:</span>
          <span className={storageInfo.pendingActions.count > 0 ? "text-amber-500" : ""}>
            {storageInfo.pendingActions.count}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-500">Status:</span>
          <span className={storageInfo.isOnline ? "text-emerald-500" : "text-amber-500"}>
            {storageInfo.isOnline ? "Online" : "Offline"}
          </span>
        </div>
      </div>
      
      <Button 
        size="sm" 
        variant="outline" 
        className="w-full mt-2 text-xs"
        onClick={() => offlineStorage.clearAllCache()}
      >
        Clear Cache
      </Button>
    </div>
  );
};

export default {
  OfflineIndicator,
  OfflineBanner,
  CachedDataBadge,
  StorageUsage
};
