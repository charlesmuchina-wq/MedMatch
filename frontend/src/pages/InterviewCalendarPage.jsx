import { useState, useEffect, useCallback } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { 
  Calendar as CalendarIcon, Plus, Trash2, Clock, MapPin, Video, Phone,
  Building2, Briefcase, Sparkles, ChevronLeft, ChevronRight, Settings,
  ExternalLink, RefreshCw, CheckCircle2, AlertCircle, Loader2,
  User, Mail, FileText, Target, MessageSquare, ListChecks, Unlink, Link2
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Calendar } from "@/components/ui/calendar";
import { useTranslation } from "@/utils/i18n";
import { apiClient } from "@/utils/apiClient";

// Google Calendar OAuth Configuration
const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID || "";
const GOOGLE_CALENDAR_SCOPES = "https://www.googleapis.com/auth/calendar.readonly https://www.googleapis.com/auth/calendar.events";

// Google Calendar Connection Component
const GoogleCalendarConnect = ({ onConnect, onSync, isConnected, connectedEmail, onDisconnect }) => {
  const [isConnecting, setIsConnecting] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const hasProcessedCallback = React.useRef(false);
  const location = useLocation();
  const navigate = useNavigate();

  // Handle OAuth callback - process code from URL
  useEffect(() => {
    if (hasProcessedCallback.current) return;
    
    const searchParams = new URLSearchParams(location.search);
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    
    if (code && state === 'google_calendar') {
      hasProcessedCallback.current = true;
      
      // Process the OAuth callback
      const processCallback = async () => {
        setIsConnecting(true);
        try {
          // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
          const redirectUri = window.location.origin + '/interview-calendar';
          
          const response = await apiClient.post('/api/auth/google-calendar/connect', {
            code,
            redirect_uri: redirectUri
          });
          
          if (response.data.success) {
            toast.success(`Connected to Google Calendar: ${response.data.email}`);
            onConnect(response.data.email);
          }
        } catch (e) {
          toast.error(e.response?.data?.detail || "Failed to connect Google Calendar");
        }
        setIsConnecting(false);
        // Clear URL params
        navigate(location.pathname, { replace: true });
      };
      
      processCallback();
    }
  }, [location, navigate, onConnect]);

  const initiateGoogleOAuth = () => {
    if (!GOOGLE_CLIENT_ID) {
      toast.error("Google Calendar integration not configured. Please contact admin.");
      return;
    }
    
    // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    const redirectUri = window.location.origin + '/interview-calendar';
    
    const params = new URLSearchParams({
      client_id: GOOGLE_CLIENT_ID,
      redirect_uri: redirectUri,
      response_type: 'code',
      scope: GOOGLE_CALENDAR_SCOPES,
      access_type: 'offline',
      prompt: 'consent',
      state: 'google_calendar'
    });
    
    window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?${params.toString()}`;
  };

  const handleSync = async () => {
    setIsSyncing(true);
    try {
      // Get fresh token
      const tokenResponse = await apiClient.get('/api/auth/google-calendar/token');
      const accessToken = tokenResponse.data.access_token;
      
      // Sync events
      const syncResponse = await apiClient.post('/api/interview-calendar/sync/google', {
        access_token: accessToken,
        sync_direction: 'import'
      });
      
      toast.success(`Synced ${syncResponse.data.imported} interviews from Google Calendar`);
      onSync();
    } catch (e) {
      if (e.response?.status === 401) {
        toast.error("Calendar connection expired. Please reconnect.");
        onDisconnect();
      } else {
        toast.error(e.response?.data?.detail || "Failed to sync calendar");
      }
    }
    setIsSyncing(false);
  };

  const handleDisconnect = async () => {
    if (!confirm("Disconnect Google Calendar?")) return;
    
    try {
      await apiClient.delete('/api/auth/google-calendar/disconnect');
      toast.success("Google Calendar disconnected");
      onDisconnect();
    } catch (e) {
      toast.error("Failed to disconnect");
    }
  };

  if (isConnected) {
    return (
      <div className="flex items-center gap-2 flex-wrap">
        <Badge variant="outline" className="text-emerald-600 border-emerald-300 dark:border-emerald-700">
          <CheckCircle2 className="w-3 h-3 mr-1" />
          {connectedEmail}
        </Badge>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={handleSync}
          disabled={isSyncing}
          data-testid="sync-calendar-btn"
        >
          {isSyncing ? <Loader2 className="w-4 h-4 mr-1 animate-spin" /> : <RefreshCw className="w-4 h-4 mr-1" />}
          Sync
        </Button>
        <Button 
          variant="ghost" 
          size="sm"
          onClick={handleDisconnect}
          className="text-slate-500 hover:text-red-500"
        >
          <Unlink className="w-4 h-4" />
        </Button>
      </div>
    );
  }

  return (
    <Button 
      variant="outline" 
      onClick={initiateGoogleOAuth}
      disabled={isConnecting}
      data-testid="connect-google-calendar-btn"
    >
      {isConnecting ? (
        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
      ) : (
        <svg className="w-4 h-4 mr-2" viewBox="0 0 24 24">
          <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
          <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
          <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
          <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
        </svg>
      )}
      Connect Google Calendar
    </Button>
  );
};

// Interview type icons and colors
const INTERVIEW_TYPES = {
  video: { icon: Video, color: "bg-blue-500", label: "Video Call" },
  phone: { icon: Phone, color: "bg-green-500", label: "Phone Call" },
  in_person: { icon: MapPin, color: "bg-purple-500", label: "In Person" }
};

// Status badges
const STATUS_STYLES = {
  scheduled: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300",
  completed: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300",
  cancelled: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300",
  rescheduled: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300"
};

// Event Card Component
const EventCard = ({ event, onSelect, onDelete, isSelected }) => {
  const type = INTERVIEW_TYPES[event.interview_type] || INTERVIEW_TYPES.video;
  const TypeIcon = type.icon;
  
  const startDate = new Date(event.start_time);
  const isToday = new Date().toDateString() === startDate.toDateString();
  const isPast = startDate < new Date();
  
  return (
    <Card 
      className={`cursor-pointer transition-all hover:shadow-md ${
        isSelected ? 'ring-2 ring-turquoise' : ''
      } ${isPast ? 'opacity-60' : ''}`}
      onClick={() => onSelect(event)}
      data-testid={`event-card-${event.id}`}
    >
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          <div className={`w-10 h-10 ${type.color} rounded-lg flex items-center justify-center flex-shrink-0`}>
            <TypeIcon className="w-5 h-5 text-white" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-2">
              <h3 className="font-medium text-slate-900 dark:text-slate-100 truncate">
                {event.position || "Interview"}
              </h3>
              <Badge className={STATUS_STYLES[event.status] || STATUS_STYLES.scheduled}>
                {event.status}
              </Badge>
            </div>
            <p className="text-sm text-slate-500 dark:text-slate-400 flex items-center gap-1 mt-1">
              <Building2 className="w-3 h-3" />
              {event.company || "Company"}
            </p>
            <div className="flex items-center gap-3 mt-2 text-xs text-slate-500 dark:text-slate-400">
              <span className="flex items-center gap-1">
                <CalendarIcon className="w-3 h-3" />
                {isToday ? "Today" : startDate.toLocaleDateString()}
              </span>
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {startDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
            {event.preparation && (
              <Badge variant="outline" className="mt-2 text-xs">
                <Sparkles className="w-3 h-3 mr-1" /> AI Prep Ready
              </Badge>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// AI Preparation Display Component
const PreparationDisplay = ({ preparation, onRegenerate, isLoading }) => {
  if (!preparation) {
    return (
      <div className="text-center py-8">
        <Sparkles className="w-12 h-12 mx-auto mb-4 text-amber-500 opacity-60" />
        <p className="text-slate-500 dark:text-slate-400 mb-4">
          Generate AI-powered preparation materials
        </p>
        <Button onClick={onRegenerate} disabled={isLoading}>
          {isLoading ? (
            <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Generating...</>
          ) : (
            <><Sparkles className="w-4 h-4 mr-2" /> Generate Preparation</>
          )}
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Talking Points */}
      {preparation.talking_points?.length > 0 && (
        <div>
          <h4 className="font-medium text-slate-900 dark:text-slate-100 mb-2 flex items-center gap-2">
            <Target className="w-4 h-4 text-turquoise" />
            Key Talking Points
          </h4>
          <ul className="space-y-1">
            {preparation.talking_points.map((point, i) => (
              <li key={i} className="text-sm text-slate-600 dark:text-slate-400 flex items-start gap-2">
                <span className="text-turquoise mt-0.5">•</span>
                {point}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Company Insights */}
      {preparation.company_insights && (
        <div>
          <h4 className="font-medium text-slate-900 dark:text-slate-100 mb-2 flex items-center gap-2">
            <Building2 className="w-4 h-4 text-violet-500" />
            Company Insights
          </h4>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            {preparation.company_insights}
          </p>
        </div>
      )}

      {/* Potential Questions */}
      {preparation.potential_questions?.length > 0 && (
        <div>
          <h4 className="font-medium text-slate-900 dark:text-slate-100 mb-2 flex items-center gap-2">
            <MessageSquare className="w-4 h-4 text-blue-500" />
            Likely Questions
          </h4>
          <ul className="space-y-1">
            {preparation.potential_questions.slice(0, 5).map((q, i) => (
              <li key={i} className="text-sm text-slate-600 dark:text-slate-400">
                {i + 1}. {q}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Questions to Ask */}
      {preparation.questions_to_ask?.length > 0 && (
        <div>
          <h4 className="font-medium text-slate-900 dark:text-slate-100 mb-2 flex items-center gap-2">
            <ListChecks className="w-4 h-4 text-emerald-500" />
            Questions to Ask
          </h4>
          <ul className="space-y-1">
            {preparation.questions_to_ask.map((q, i) => (
              <li key={i} className="text-sm text-slate-600 dark:text-slate-400 flex items-start gap-2">
                <span className="text-emerald-500 mt-0.5">✓</span>
                {q}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Tips */}
      {preparation.tips?.length > 0 && (
        <div>
          <h4 className="font-medium text-slate-900 dark:text-slate-100 mb-2 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-amber-500" />
            Tips
          </h4>
          <ul className="space-y-1">
            {preparation.tips.map((tip, i) => (
              <li key={i} className="text-sm text-slate-600 dark:text-slate-400 flex items-start gap-2">
                <span className="text-amber-500">💡</span>
                {tip}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Regenerate Button */}
      <div className="pt-4 border-t border-slate-200 dark:border-slate-700">
        <Button variant="outline" size="sm" onClick={onRegenerate} disabled={isLoading}>
          {isLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <RefreshCw className="w-4 h-4 mr-2" />}
          Regenerate
        </Button>
      </div>
    </div>
  );
};

const InterviewCalendarPage = () => {
  const { t } = useTranslation();
  
  // State
  const [isLoading, setIsLoading] = useState(true);
  const [events, setEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [stats, setStats] = useState(null);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [isGeneratingPrep, setIsGeneratingPrep] = useState(false);
  
  // Google Calendar state
  const [googleCalendarConnected, setGoogleCalendarConnected] = useState(false);
  const [googleCalendarEmail, setGoogleCalendarEmail] = useState(null);
  
  // New event form
  const [newEvent, setNewEvent] = useState({
    title: "",
    company: "",
    position: "",
    interview_type: "video",
    start_time: "",
    end_time: "",
    location: "",
    meeting_link: "",
    notes: "",
    interviewer_name: "",
    interviewer_email: ""
  });

  // Load Google Calendar connection status
  const loadGoogleCalendarStatus = useCallback(async () => {
    try {
      const response = await apiClient.get('/api/auth/google-calendar/config');
      setGoogleCalendarConnected(response.data.connected);
      setGoogleCalendarEmail(response.data.connected_email);
    } catch (e) {
      console.error('Failed to load Google Calendar status:', e);
    }
  }, []);

  // Load data
  const loadEvents = useCallback(async () => {
    try {
      const response = await apiClient.get('/api/interview-calendar/events');
      setEvents(response.data.events || []);
    } catch (e) {
      console.error('Failed to load events:', e);
    }
  }, []);

  const loadStats = useCallback(async () => {
    try {
      const response = await apiClient.get('/api/interview-calendar/stats');
      setStats(response.data);
    } catch (e) {
      console.error('Failed to load stats:', e);
    }
  }, []);

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      await Promise.all([loadEvents(), loadStats(), loadGoogleCalendarStatus()]);
      setIsLoading(false);
    };
    loadData();
  }, [loadEvents, loadStats, loadGoogleCalendarStatus]);

  // Create event
  const createEvent = async () => {
    if (!newEvent.company || !newEvent.position || !newEvent.start_time) {
      toast.error('Please fill in required fields');
      return;
    }

    try {
      const response = await apiClient.post('/api/interview-calendar/events', newEvent);
      setEvents(prev => [...prev, response.data.event]);
      setSelectedEvent(response.data.event);
      setShowCreateDialog(false);
      setNewEvent({
        title: "", company: "", position: "", interview_type: "video",
        start_time: "", end_time: "", location: "", meeting_link: "",
        notes: "", interviewer_name: "", interviewer_email: ""
      });
      toast.success('Interview scheduled!');
      loadStats();
    } catch (e) {
      toast.error('Failed to create event');
    }
  };

  // Delete event
  const deleteEvent = async (eventId) => {
    if (!confirm('Delete this interview?')) return;

    try {
      await apiClient.delete(`/api/interview-calendar/events/${eventId}`);
      setEvents(prev => prev.filter(e => e.id !== eventId));
      if (selectedEvent?.id === eventId) {
        setSelectedEvent(null);
      }
      toast.success('Interview deleted');
      loadStats();
    } catch (e) {
      toast.error('Failed to delete event');
    }
  };

  // Generate AI preparation
  const generatePreparation = async () => {
    if (!selectedEvent) return;

    setIsGeneratingPrep(true);
    try {
      const response = await apiClient.post(`/api/interview-calendar/events/${selectedEvent.id}/generate-preparation`);
      
      if (response.data.success) {
        setSelectedEvent(prev => ({
          ...prev,
          preparation: response.data.preparation
        }));
        // Update in events list
        setEvents(prev => prev.map(e => 
          e.id === selectedEvent.id 
            ? { ...e, preparation: response.data.preparation }
            : e
        ));
        toast.success('AI preparation generated!');
      }
    } catch (e) {
      toast.error('Failed to generate preparation');
    }
    setIsGeneratingPrep(false);
  };

  // Update event status
  const updateEventStatus = async (status) => {
    if (!selectedEvent) return;

    try {
      await apiClient.put(`/api/interview-calendar/events/${selectedEvent.id}`, { status });
      setSelectedEvent(prev => ({ ...prev, status }));
      setEvents(prev => prev.map(e => 
        e.id === selectedEvent.id ? { ...e, status } : e
      ));
      toast.success(`Status updated to ${status}`);
      loadStats();
    } catch (e) {
      toast.error('Failed to update status');
    }
  };

  // Get events for selected date
  const eventsForSelectedDate = events.filter(e => {
    const eventDate = new Date(e.start_time).toDateString();
    return eventDate === selectedDate.toDateString();
  });

  // Get upcoming events
  const upcomingEvents = events
    .filter(e => new Date(e.start_time) >= new Date() && e.status !== 'cancelled')
    .sort((a, b) => new Date(a.start_time) - new Date(b.start_time))
    .slice(0, 5);

  // Dates with events for calendar highlighting
  const datesWithEvents = events.reduce((acc, e) => {
    const date = new Date(e.start_time).toDateString();
    acc[date] = true;
    return acc;
  }, {});

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-turquoise" />
      </div>
    );
  }

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-7xl mx-auto animate-fade-in" data-testid="interview-calendar-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center">
              <CalendarIcon className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-3xl font-semibold text-slate-900 dark:text-slate-100 tracking-tight" style={{ fontFamily: 'IBM Plex Sans' }}>
              Interview Calendar
            </h1>
          </div>
          <p className="text-slate-500 dark:text-slate-400">
            Schedule interviews and get AI-powered preparation with talking points
          </p>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          {/* Google Calendar Integration */}
          <GoogleCalendarConnect 
            isConnected={googleCalendarConnected}
            connectedEmail={googleCalendarEmail}
            onConnect={(email) => {
              setGoogleCalendarConnected(true);
              setGoogleCalendarEmail(email);
            }}
            onSync={() => {
              loadEvents();
              loadStats();
            }}
            onDisconnect={() => {
              setGoogleCalendarConnected(false);
              setGoogleCalendarEmail(null);
            }}
          />

          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
            <DialogTrigger asChild>
              <Button className="bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700">
                <Plus className="w-4 h-4 mr-2" /> Schedule Interview
              </Button>
            </DialogTrigger>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>Schedule New Interview</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4 max-h-[60vh] overflow-y-auto">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Company *</label>
                  <Input
                    placeholder="e.g., Google"
                    value={newEvent.company}
                    onChange={(e) => setNewEvent(prev => ({ ...prev, company: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Position *</label>
                  <Input
                    placeholder="e.g., Software Engineer"
                    value={newEvent.position}
                    onChange={(e) => setNewEvent(prev => ({ ...prev, position: e.target.value }))}
                  />
                </div>
              </div>
              
              <div>
                <label className="text-sm font-medium mb-2 block">Interview Type</label>
                <Select 
                  value={newEvent.interview_type} 
                  onValueChange={(v) => setNewEvent(prev => ({ ...prev, interview_type: v }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="video">Video Call</SelectItem>
                    <SelectItem value="phone">Phone Call</SelectItem>
                    <SelectItem value="in_person">In Person</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Start Time *</label>
                  <Input
                    type="datetime-local"
                    value={newEvent.start_time}
                    onChange={(e) => setNewEvent(prev => ({ ...prev, start_time: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">End Time</label>
                  <Input
                    type="datetime-local"
                    value={newEvent.end_time}
                    onChange={(e) => setNewEvent(prev => ({ ...prev, end_time: e.target.value }))}
                  />
                </div>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Meeting Link / Location</label>
                <Input
                  placeholder="https://meet.google.com/... or office address"
                  value={newEvent.meeting_link || newEvent.location}
                  onChange={(e) => setNewEvent(prev => ({ 
                    ...prev, 
                    meeting_link: e.target.value.startsWith('http') ? e.target.value : '',
                    location: !e.target.value.startsWith('http') ? e.target.value : ''
                  }))}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Interviewer Name</label>
                  <Input
                    placeholder="John Smith"
                    value={newEvent.interviewer_name}
                    onChange={(e) => setNewEvent(prev => ({ ...prev, interviewer_name: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Interviewer Email</label>
                  <Input
                    type="email"
                    placeholder="john@company.com"
                    value={newEvent.interviewer_email}
                    onChange={(e) => setNewEvent(prev => ({ ...prev, interviewer_email: e.target.value }))}
                  />
                </div>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Notes</label>
                <Textarea
                  placeholder="Any additional details about the interview..."
                  value={newEvent.notes}
                  onChange={(e) => setNewEvent(prev => ({ ...prev, notes: e.target.value }))}
                  rows={3}
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowCreateDialog(false)}>Cancel</Button>
              <Button onClick={createEvent} data-testid="create-interview-btn">Schedule Interview</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-indigo-500">{stats.upcoming}</p>
              <p className="text-sm text-slate-500 dark:text-slate-400">Upcoming</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-emerald-500">{stats.completed}</p>
              <p className="text-sm text-slate-500 dark:text-slate-400">Completed</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-amber-500">{stats.this_week}</p>
              <p className="text-sm text-slate-500 dark:text-slate-400">This Week</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-violet-500">{stats.total_interviews}</p>
              <p className="text-sm text-slate-500 dark:text-slate-400">Total</p>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Calendar & Events List */}
        <div className="lg:col-span-1 space-y-6">
          {/* Calendar */}
          <Card>
            <CardContent className="p-4">
              <Calendar
                mode="single"
                selected={selectedDate}
                onSelect={(date) => date && setSelectedDate(date)}
                className="rounded-md"
                modifiers={{
                  hasEvent: (date) => datesWithEvents[date.toDateString()]
                }}
                modifiersStyles={{
                  hasEvent: { fontWeight: 'bold', textDecoration: 'underline', color: 'var(--turquoise, #20b2aa)' }
                }}
              />
            </CardContent>
          </Card>

          {/* Upcoming Interviews */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center gap-2">
                <Clock className="w-5 h-5 text-indigo-500" />
                Upcoming Interviews
              </CardTitle>
            </CardHeader>
            <CardContent>
              {upcomingEvents.length > 0 ? (
                <div className="space-y-3">
                  {upcomingEvents.map(event => (
                    <EventCard
                      key={event.id}
                      event={event}
                      onSelect={setSelectedEvent}
                      onDelete={deleteEvent}
                      isSelected={selectedEvent?.id === event.id}
                    />
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-slate-400 dark:text-slate-500">
                  <CalendarIcon className="w-10 h-10 mx-auto mb-3 opacity-40" />
                  <p>No upcoming interviews</p>
                  <p className="text-sm mt-1">Schedule your next interview</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Interview Details */}
        <div className="lg:col-span-2">
          {selectedEvent ? (
            <Card>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      {(() => {
                        const type = INTERVIEW_TYPES[selectedEvent.interview_type] || INTERVIEW_TYPES.video;
                        const TypeIcon = type.icon;
                        return <TypeIcon className="w-5 h-5" />;
                      })()}
                      {selectedEvent.position}
                    </CardTitle>
                    <CardDescription className="flex items-center gap-2 mt-1">
                      <Building2 className="w-4 h-4" />
                      {selectedEvent.company}
                    </CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className={STATUS_STYLES[selectedEvent.status]}>
                      {selectedEvent.status}
                    </Badge>
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => deleteEvent(selectedEvent.id)}
                      className="text-red-500 hover:text-red-600"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="details" className="space-y-4">
                  <TabsList>
                    <TabsTrigger value="details">Details</TabsTrigger>
                    <TabsTrigger value="preparation">AI Preparation</TabsTrigger>
                  </TabsList>

                  {/* Details Tab */}
                  <TabsContent value="details" className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                        <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Date & Time</p>
                        <p className="font-medium text-slate-900 dark:text-slate-100 flex items-center gap-1">
                          <CalendarIcon className="w-4 h-4" />
                          {new Date(selectedEvent.start_time).toLocaleDateString()}
                        </p>
                        <p className="text-sm text-slate-600 dark:text-slate-400 flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {new Date(selectedEvent.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </p>
                      </div>
                      <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                        <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Interview Type</p>
                        <p className="font-medium text-slate-900 dark:text-slate-100 capitalize">
                          {selectedEvent.interview_type?.replace('_', ' ')}
                        </p>
                      </div>
                    </div>

                    {(selectedEvent.meeting_link || selectedEvent.location) && (
                      <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                        <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Location / Link</p>
                        {selectedEvent.meeting_link ? (
                          <a 
                            href={selectedEvent.meeting_link} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-turquoise hover:underline flex items-center gap-1"
                          >
                            <ExternalLink className="w-4 h-4" />
                            Join Meeting
                          </a>
                        ) : (
                          <p className="text-slate-900 dark:text-slate-100 flex items-center gap-1">
                            <MapPin className="w-4 h-4" />
                            {selectedEvent.location}
                          </p>
                        )}
                      </div>
                    )}

                    {selectedEvent.interviewer_name && (
                      <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                        <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Interviewer</p>
                        <p className="text-slate-900 dark:text-slate-100 flex items-center gap-1">
                          <User className="w-4 h-4" />
                          {selectedEvent.interviewer_name}
                        </p>
                        {selectedEvent.interviewer_email && (
                          <p className="text-sm text-slate-600 dark:text-slate-400 flex items-center gap-1">
                            <Mail className="w-3 h-3" />
                            {selectedEvent.interviewer_email}
                          </p>
                        )}
                      </div>
                    )}

                    {selectedEvent.notes && (
                      <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                        <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Notes</p>
                        <p className="text-slate-700 dark:text-slate-300 text-sm">
                          {selectedEvent.notes}
                        </p>
                      </div>
                    )}

                    {/* Status Actions */}
                    <div className="pt-4 border-t border-slate-200 dark:border-slate-700">
                      <p className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Update Status</p>
                      <div className="flex gap-2 flex-wrap">
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => updateEventStatus('completed')}
                          disabled={selectedEvent.status === 'completed'}
                        >
                          <CheckCircle2 className="w-4 h-4 mr-1 text-emerald-500" /> Completed
                        </Button>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => updateEventStatus('cancelled')}
                          disabled={selectedEvent.status === 'cancelled'}
                        >
                          <AlertCircle className="w-4 h-4 mr-1 text-red-500" /> Cancelled
                        </Button>
                      </div>
                    </div>
                  </TabsContent>

                  {/* Preparation Tab */}
                  <TabsContent value="preparation">
                    <PreparationDisplay
                      preparation={selectedEvent.preparation}
                      onRegenerate={generatePreparation}
                      isLoading={isGeneratingPrep}
                    />
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="p-12 text-center">
                <CalendarIcon className="w-16 h-16 mx-auto mb-4 text-slate-300 dark:text-slate-600" />
                <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100 mb-2">
                  Select an Interview
                </h3>
                <p className="text-slate-500 dark:text-slate-400 mb-6">
                  Choose an interview from the list or schedule a new one
                </p>
                <Button onClick={() => setShowCreateDialog(true)}>
                  <Plus className="w-4 h-4 mr-2" /> Schedule Interview
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Tips Section */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle className="text-lg" style={{ fontFamily: 'IBM Plex Sans' }}>
            Interview Success Tips
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-4 gap-4">
            {[
              { icon: Sparkles, title: 'Use AI Prep', desc: 'Generate talking points before each interview' },
              { icon: Clock, title: 'Be Early', desc: 'Join video calls 5 minutes early' },
              { icon: FileText, title: 'Research', desc: 'Review company news and culture' },
              { icon: Target, title: 'Prepare Questions', desc: 'Have thoughtful questions ready to ask' }
            ].map(({ icon: Icon, title, desc }) => (
              <div key={title} className="text-center p-4">
                <Icon className="w-8 h-8 text-indigo-500 mx-auto mb-2" />
                <h4 className="font-medium text-slate-900 dark:text-slate-100 mb-1">{title}</h4>
                <p className="text-xs text-slate-500 dark:text-slate-400">{desc}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default InterviewCalendarPage;
