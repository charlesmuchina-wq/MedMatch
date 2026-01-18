import { useState, useEffect, useCallback } from "react";
import axios from "axios";
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

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const NotificationsPage = ({ user }) => {
  const { isDark } = useTheme();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [preferences, setPreferences] = useState(null);
  const [subscriptions, setSubscriptions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubscribing, setIsSubscribing] = useState(false);
  const [pushSupported, setPushSupported] = useState(false);
  const [pushPermission, setPushPermission] = useState('default');

  useEffect(() => {
    // Check push notification support
    if ('Notification' in window && 'serviceWorker' in navigator) {
      setPushSupported(true);
      setPushPermission(Notification.permission);
    }
    
    fetchData();
  }, []);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [historyRes, prefsRes, subsRes] = await Promise.all([
        axios.get(`${API}/notifications/history?limit=50`),
        axios.get(`${API}/notifications/preferences`),
        axios.get(`${API}/notifications/subscriptions`)
      ]);
      
      setNotifications(historyRes.data.notifications || []);
      setUnreadCount(historyRes.data.unread_count || 0);
      setPreferences(prefsRes.data);
      setSubscriptions(subsRes.data.subscriptions || []);
    } catch (e) {
      console.error("Failed to fetch notifications:", e);
    }
    setIsLoading(false);
  };

  const requestPushPermission = async () => {
    if (!pushSupported) {
      toast.error("Push notifications not supported in this browser");
      return;
    }

    setIsSubscribing(true);
    try {
      const permission = await Notification.requestPermission();
      setPushPermission(permission);
      
      if (permission === 'granted') {
        // Register service worker and subscribe
        const registration = await navigator.serviceWorker.ready;
        
        // Generate VAPID keys would be needed for production
        // For now, we'll just store the subscription intent
        const subscription = {
          endpoint: `${window.location.origin}/push-endpoint-${Date.now()}`,
          keys: {
            p256dh: 'placeholder-key',
            auth: 'placeholder-auth'
          },
          user_agent: navigator.userAgent
        };

        await axios.post(`${API}/notifications/subscribe`, subscription);
        toast.success("Push notifications enabled!");
        fetchData();
      } else {
        toast.error("Push notification permission denied");
      }
    } catch (e) {
      toast.error("Failed to enable push notifications");
      console.error(e);
    }
    setIsSubscribing(false);
  };

  const unsubscribe = async (endpoint) => {
    try {
      await axios.delete(`${API}/notifications/unsubscribe?endpoint=${encodeURIComponent(endpoint)}`);
      toast.success("Unsubscribed from push notifications");
      fetchData();
    } catch (e) {
      toast.error("Failed to unsubscribe");
    }
  };

  const updatePreference = async (key, value) => {
    const newPrefs = { ...preferences, [key]: value };
    setPreferences(newPrefs);
    
    try {
      await axios.put(`${API}/notifications/preferences`, newPrefs);
      toast.success("Preferences updated");
    } catch (e) {
      toast.error("Failed to update preferences");
      setPreferences(preferences); // Revert
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      await axios.put(`${API}/notifications/mark-read/${notificationId}`);
      setNotifications(prev => 
        prev.map(n => n.notification_id === notificationId ? { ...n, read: true } : n)
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (e) {
      toast.error("Failed to mark as read");
    }
  };

  const markAllAsRead = async () => {
    try {
      await axios.put(`${API}/notifications/mark-all-read`);
      setNotifications(prev => prev.map(n => ({ ...n, read: true })));
      setUnreadCount(0);
      toast.success("All notifications marked as read");
    } catch (e) {
      toast.error("Failed to mark all as read");
    }
  };

  const sendTestNotification = async () => {
    try {
      await axios.post(`${API}/notifications/send-test`);
      toast.success("Test notification sent!");
      fetchData();
    } catch (e) {
      toast.error("Failed to send test notification");
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
    { key: 'job_alerts', icon: Briefcase, label: 'Job Alerts', desc: 'Get notified about new matching jobs' },
    { key: 'application_updates', icon: CheckCircle2, label: 'Application Updates', desc: 'Status changes on your applications' },
    { key: 'messages', icon: MessageSquare, label: 'Messages', desc: 'New messages from recruiters' },
    { key: 'interview_reminders', icon: Calendar, label: 'Interview Reminders', desc: 'Upcoming interview notifications' },
    { key: 'weekly_digest', icon: Mail, label: 'Weekly Digest', desc: 'Weekly summary of job matches' },
    { key: 'marketing', icon: Megaphone, label: 'Marketing', desc: 'Tips, news, and promotions' }
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
            Notifications
          </h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">
            Manage your notification preferences and history
          </p>
        </div>
        {unreadCount > 0 && (
          <Badge className="bg-turquoise text-white">{unreadCount} unread</Badge>
        )}
      </div>

      <Tabs defaultValue="history" className="space-y-6">
        <TabsList>
          <TabsTrigger value="history" className="flex items-center gap-2">
            <Bell className="w-4 h-4" /> History
          </TabsTrigger>
          <TabsTrigger value="preferences" className="flex items-center gap-2">
            <Settings className="w-4 h-4" /> Preferences
          </TabsTrigger>
        </TabsList>

        {/* Notification History */}
        <TabsContent value="history">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Notification History</CardTitle>
                <CardDescription>Your recent notifications</CardDescription>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={fetchData}>
                  <RefreshCw className="w-4 h-4 mr-1" /> Refresh
                </Button>
                {unreadCount > 0 && (
                  <Button variant="outline" size="sm" onClick={markAllAsRead}>
                    <Check className="w-4 h-4 mr-1" /> Mark All Read
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {notifications.length === 0 ? (
                <div className="text-center py-12 text-slate-400">
                  <BellOff className="w-12 h-12 mx-auto mb-4 opacity-40" />
                  <p>No notifications yet</p>
                  <Button 
                    variant="outline" 
                    className="mt-4"
                    onClick={sendTestNotification}
                  >
                    Send Test Notification
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
                  Push Notifications
                </CardTitle>
                <CardDescription>
                  Receive instant notifications on this device
                </CardDescription>
              </CardHeader>
              <CardContent>
                {!pushSupported ? (
                  <p className="text-amber-600 dark:text-amber-400 text-sm">
                    Push notifications are not supported in this browser
                  </p>
                ) : pushPermission === 'granted' && subscriptions.length > 0 ? (
                  <div className="space-y-4">
                    <div className="flex items-center gap-3 p-3 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg">
                      <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                      <span className="text-emerald-700 dark:text-emerald-300 font-medium">
                        Push notifications enabled
                      </span>
                    </div>
                    
                    <div className="space-y-2">
                      <p className="text-sm text-slate-500 dark:text-slate-400">Subscribed devices:</p>
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
                              Added {new Date(sub.created_at).toLocaleDateString()}
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
                    >
                      <Bell className="w-4 h-4 mr-2" />
                      Send Test Notification
                    </Button>
                  </div>
                ) : (
                  <div className="text-center py-4">
                    <p className="text-slate-500 dark:text-slate-400 mb-4">
                      Enable push notifications to receive instant updates
                    </p>
                    <Button 
                      onClick={requestPushPermission}
                      disabled={isSubscribing}
                      className="bg-turquoise hover:bg-turquoise/90"
                    >
                      {isSubscribing ? (
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      ) : (
                        <Bell className="w-4 h-4 mr-2" />
                      )}
                      Enable Push Notifications
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Notification Preferences */}
            <Card>
              <CardHeader>
                <CardTitle>Notification Preferences</CardTitle>
                <CardDescription>Choose what notifications you want to receive</CardDescription>
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
