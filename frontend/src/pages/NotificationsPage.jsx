import { useState, useEffect, useCallback } from "react";
import { toast } from "sonner";
import { useTheme } from "@/App";
import { 
  Bell, BellOff, Check, Trash2, RefreshCw, Settings, 
  Briefcase, MessageSquare, Calendar, Mail, Megaphone,
  Loader2, CheckCircle2, Circle, BellRing
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useTranslation } from "@/utils/i18n";
import { apiClient } from "@/utils/apiClient";

const NotificationsPage = ({ user }) => {
  const { isDark } = useTheme();
  const { t } = useTranslation();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [preferences, setPreferences] = useState(null);
  const [subscriptions, setSubscriptions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubscribing, setIsSubscribing] = useState(false);
  const [pushSupported, setPushSupported] = useState(false);
  const [pushPermission, setPushPermission] = useState('default');

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [historyRes, prefsRes, subsRes] = await Promise.all([
        apiClient.get("/api/notifications/history?limit=50"),
        apiClient.get("/api/notifications/preferences"),
        apiClient.get("/api/notifications/subscriptions")
      ]);
      
      setNotifications(historyRes.data.notifications || []);
      setUnreadCount(historyRes.data.unread_count || 0);
      setPreferences(prefsRes.data);
      setSubscriptions(subsRes.data.subscriptions || []);
    } catch (e) {
      console.error("Failed to fetch notifications:", e);
    }
    setIsLoading(false);
  }, []);

  useEffect(() => {
    // Check push notification support
    if ('Notification' in window && 'serviceWorker' in navigator) {
      setPushSupported(true);
      setPushPermission(Notification.permission);
    }
    
    fetchData();
  }, [fetchData]);

  const requestPushPermission = async () => {
    if (!pushSupported) {
      toast.error(t("notifications.notSupported") || "Push notifications not supported in this browser");
      return;
    }

    setIsSubscribing(true);
    try {
      const permission = await Notification.requestPermission();
      setPushPermission(permission);
      
      if (permission === 'granted') {
        // Register service worker and subscribe
        const subscription = {
          endpoint: `${window.location.origin}/push-endpoint-${Date.now()}`,
          keys: {
            p256dh: 'placeholder-key',
            auth: 'placeholder-auth'
          },
          user_agent: navigator.userAgent
        };

        await apiClient.post("/api/notifications/subscribe", subscription);
        toast.success(t("notifications.pushEnabled") || "Push notifications enabled!");
        fetchData();
      } else {
        toast.error(t("notifications.permissionDenied") || "Push notification permission denied");
      }
    } catch (e) {
      toast.error(t("notifications.enableFailed") || "Failed to enable push notifications");
      console.error(e);
    }
    setIsSubscribing(false);
  };

  const unsubscribe = async (endpoint) => {
    try {
      await apiClient.delete(`/api/notifications/unsubscribe?endpoint=${encodeURIComponent(endpoint)}`);
      toast.success(t("notifications.unsubscribed") || "Unsubscribed from push notifications");
      fetchData();
    } catch (e) {
      toast.error(t("notifications.unsubscribeFailed") || "Failed to unsubscribe");
    }
  };

  const updatePreference = async (key, value) => {
    const newPrefs = { ...preferences, [key]: value };
    setPreferences(newPrefs);
    
    try {
      await apiClient.put("/api/notifications/preferences", newPrefs);
      toast.success(t("notifications.prefsUpdated") || "Preferences updated");
    } catch (e) {
      toast.error(t("notifications.prefsFailed") || "Failed to update preferences");
      setPreferences(preferences); // Revert
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      await apiClient.put(`/api/notifications/mark-read/${notificationId}`);
      setNotifications(prev => 
        prev.map(n => n.notification_id === notificationId ? { ...n, read: true } : n)
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (e) {
      toast.error(t("notifications.markReadFailed") || "Failed to mark as read");
    }
  };

  const markAllAsRead = async () => {
    try {
      await apiClient.put("/api/notifications/mark-all-read");
      setNotifications(prev => prev.map(n => ({ ...n, read: true })));
      setUnreadCount(0);
      toast.success(t("notifications.allMarkedRead") || "All notifications marked as read");
    } catch (e) {
      toast.error(t("notifications.markAllFailed") || "Failed to mark all as read");
    }
  };

  const sendTestNotification = async () => {
    try {
      await apiClient.post("/api/notifications/send-test");
      toast.success(t("notifications.testSent") || "Test notification sent!");
      fetchData();
    } catch (e) {
      toast.error(t("notifications.testFailed") || "Failed to send test notification");
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'job_alert': return <Briefcase className="w-5 h-5 text-turquoise" />;
      case 'message': return <MessageSquare className="w-5 h-5 text-blue-500" />;
      case 'interview_reminder': return <Calendar className="w-5 h-5 text-purple-500" />;
      default: return <Bell className="w-5 h-5 text-slate-500" />;
    }
  };

  const preferenceItems = [
    { key: 'job_alerts', icon: Briefcase, label: t("notifications.jobAlerts") || 'Job Alerts', desc: t("notifications.jobAlertsDesc") || 'Get notified about new matching jobs' },
    { key: 'application_updates', icon: CheckCircle2, label: t("notifications.appUpdates") || 'Application Updates', desc: t("notifications.appUpdatesDesc") || 'Status changes on your applications' },
    { key: 'messages', icon: MessageSquare, label: t("notifications.messages") || 'Messages', desc: t("notifications.messagesDesc") || 'New messages from recruiters' },
    { key: 'interview_reminders', icon: Calendar, label: t("notifications.interviewReminders") || 'Interview Reminders', desc: t("notifications.interviewRemindersDesc") || 'Upcoming interview notifications' },
    { key: 'weekly_digest', icon: Mail, label: t("notifications.weeklyDigest") || 'Weekly Digest', desc: t("notifications.weeklyDigestDesc") || 'Weekly summary of job matches' },
    { key: 'marketing', icon: Megaphone, label: t("notifications.marketing") || 'Marketing', desc: t("notifications.marketingDesc") || 'Tips, news, and promotions' }
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-turquoise" />
      </div>
    );
  }

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-5xl mx-auto" data-testid="notifications-page">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-semibold text-slate-900 dark:text-slate-100" style={{ fontFamily: 'IBM Plex Sans' }}>
            {t("notifications.title") || "Notifications"}
          </h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">
            {t("notifications.subtitle") || "Manage your notification preferences and history"}
          </p>
        </div>
        {unreadCount > 0 && (
          <Badge className="bg-turquoise text-white">{unreadCount} {t("notifications.unread") || "unread"}</Badge>
        )}
      </div>

      <Tabs defaultValue="history" className="space-y-6">
        <TabsList>
          <TabsTrigger value="history" className="flex items-center gap-2">
            <Bell className="w-4 h-4" /> {t("notifications.history") || "History"}
          </TabsTrigger>
          <TabsTrigger value="preferences" className="flex items-center gap-2">
            <Settings className="w-4 h-4" /> {t("notifications.preferences") || "Preferences"}
          </TabsTrigger>
        </TabsList>

        {/* Notification History */}
        <TabsContent value="history">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>{t("notifications.historyTitle") || "Notification History"}</CardTitle>
                <CardDescription>{t("notifications.historyDesc") || "Your recent notifications"}</CardDescription>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={fetchData} data-testid="refresh-notifications">
                  <RefreshCw className="w-4 h-4 mr-1" /> {t("common.refresh") || "Refresh"}
                </Button>
                {unreadCount > 0 && (
                  <Button variant="outline" size="sm" onClick={markAllAsRead} data-testid="mark-all-read">
                    <Check className="w-4 h-4 mr-1" /> {t("notifications.markAllRead") || "Mark All Read"}
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {notifications.length === 0 ? (
                <div className="text-center py-12 text-slate-400">
                  <BellOff className="w-12 h-12 mx-auto mb-4 opacity-40" />
                  <p>{t("notifications.noNotifications") || "No notifications yet"}</p>
                  <Button 
                    variant="outline" 
                    className="mt-4"
                    onClick={sendTestNotification}
                    data-testid="send-test-notification"
                  >
                    {t("notifications.sendTest") || "Send Test Notification"}
                  </Button>
                </div>
              ) : (
                <div className="space-y-3">
                  {notifications.map((notification) => (
                    <div
                      key={notification.notification_id}
                      className={`flex items-start gap-4 p-4 rounded-lg transition-colors cursor-pointer ${
                        notification.read 
                          ? 'bg-slate-50 dark:bg-slate-800/50' 
                          : 'bg-turquoise/5 dark:bg-turquoise/10 border-l-4 border-turquoise'
                      }`}
                      onClick={() => !notification.read && markAsRead(notification.notification_id)}
                      data-testid={`notification-${notification.notification_id}`}
                    >
                      <div className="mt-0.5">
                        {getNotificationIcon(notification.data?.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <p className={`font-medium ${notification.read ? 'text-slate-600 dark:text-slate-400' : 'text-slate-900 dark:text-slate-100'}`}>
                            {notification.title}
                          </p>
                          {!notification.read && (
                            <Circle className="w-2 h-2 fill-turquoise text-turquoise" />
                          )}
                        </div>
                        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                          {notification.body}
                        </p>
                        <p className="text-xs text-slate-400 mt-2">
                          {new Date(notification.created_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Preferences */}
        <TabsContent value="preferences">
          <div className="space-y-6">
            {/* Push Notifications Card */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BellRing className="w-5 h-5 text-turquoise" />
                  {t("notifications.pushNotifications") || "Push Notifications"}
                </CardTitle>
                <CardDescription>
                  {t("notifications.pushDesc") || "Receive instant notifications on this device"}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {!pushSupported ? (
                  <p className="text-amber-600 dark:text-amber-400 text-sm">
                    {t("notifications.notSupported") || "Push notifications are not supported in this browser"}
                  </p>
                ) : pushPermission === 'granted' && subscriptions.length > 0 ? (
                  <div className="space-y-4">
                    <div className="flex items-center gap-3 p-3 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg">
                      <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                      <span className="text-emerald-700 dark:text-emerald-300 font-medium">
                        {t("notifications.pushEnabled") || "Push notifications enabled"}
                      </span>
                    </div>
                    
                    <div className="space-y-2">
                      <p className="text-sm text-slate-500 dark:text-slate-400">{t("notifications.subscribedDevices") || "Subscribed devices"}:</p>
                      {subscriptions.map((sub) => (
                        <div 
                          key={sub.subscription_id}
                          className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800 rounded-lg"
                        >
                          <div>
                            <p className="text-sm font-medium text-slate-700 dark:text-slate-300">
                              {sub.user_agent?.split(' ')[0] || 'Device'}
                            </p>
                            <p className="text-xs text-slate-500">
                              {t("notifications.added") || "Added"} {new Date(sub.created_at).toLocaleDateString()}
                            </p>
                          </div>
                          <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => unsubscribe(sub.endpoint)}
                            className="text-red-500 hover:text-red-600"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      ))}
                    </div>

                    <Button 
                      variant="outline" 
                      onClick={sendTestNotification}
                      className="w-full"
                      data-testid="test-push-notification"
                    >
                      <Bell className="w-4 h-4 mr-2" />
                      {t("notifications.sendTest") || "Send Test Notification"}
                    </Button>
                  </div>
                ) : (
                  <div className="text-center py-4">
                    <p className="text-slate-500 dark:text-slate-400 mb-4">
                      {t("notifications.enablePushDesc") || "Enable push notifications to receive instant updates"}
                    </p>
                    <Button 
                      onClick={requestPushPermission}
                      disabled={isSubscribing}
                      className="bg-turquoise hover:bg-turquoise/90"
                      data-testid="enable-push-btn"
                    >
                      {isSubscribing ? (
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      ) : (
                        <Bell className="w-4 h-4 mr-2" />
                      )}
                      {t("notifications.enablePush") || "Enable Push Notifications"}
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Notification Preferences */}
            <Card>
              <CardHeader>
                <CardTitle>{t("notifications.preferencesTitle") || "Notification Preferences"}</CardTitle>
                <CardDescription>{t("notifications.preferencesDesc") || "Choose what notifications you want to receive"}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {preferenceItems.map(({ key, icon: Icon, label, desc }) => (
                    <div 
                      key={key}
                      className="flex items-center justify-between py-3 border-b border-slate-100 dark:border-slate-800 last:border-0"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
                          <Icon className="w-5 h-5 text-slate-600 dark:text-slate-400" />
                        </div>
                        <div>
                          <p className="font-medium text-slate-900 dark:text-slate-100">{label}</p>
                          <p className="text-sm text-slate-500 dark:text-slate-400">{desc}</p>
                        </div>
                      </div>
                      <Switch
                        checked={preferences?.[key] ?? true}
                        onCheckedChange={(checked) => updatePreference(key, checked)}
                        data-testid={`pref-${key}`}
                      />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default NotificationsPage;
