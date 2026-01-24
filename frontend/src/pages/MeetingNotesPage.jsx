import { useState, useEffect, useRef, useCallback } from "react";
import { toast } from "sonner";
import { 
  FileText, Mic, MicOff, Plus, Trash2, Download, Sparkles,
  Clock, CheckCircle2, AlertCircle, Loader2, ChevronRight,
  Users, Building2, Briefcase, ListChecks, MessageSquare,
  Play, Square, RotateCcw, Copy, Search, Filter
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useTranslation } from "@/utils/i18n";
import { apiClient } from "@/utils/apiClient";

// Status badge styling
const getStatusBadge = (status) => {
  const styles = {
    draft: "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300",
    recording: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300 animate-pulse",
    processing: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300",
    transcribed: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300",
    completed: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300",
    error: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300"
  };
  return styles[status] || styles.draft;
};

// Meeting type icons
const getMeetingTypeIcon = (type) => {
  const icons = {
    interview: Briefcase,
    general: MessageSquare,
    follow_up: Users
  };
  const Icon = icons[type] || MessageSquare;
  return <Icon className="w-4 h-4" />;
};

// Meeting Card Component
const MeetingCard = ({ meeting, onSelect, onDelete }) => (
  <Card 
    className="cursor-pointer hover:border-turquoise/50 transition-all group"
    onClick={() => onSelect(meeting)}
    data-testid={`meeting-card-${meeting.id}`}
  >
    <CardContent className="p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            {getMeetingTypeIcon(meeting.meeting_type)}
            <h3 className="font-medium text-slate-900 dark:text-slate-100 truncate">
              {meeting.title}
            </h3>
          </div>
          
          {meeting.company && (
            <p className="text-sm text-slate-500 dark:text-slate-400 flex items-center gap-1">
              <Building2 className="w-3 h-3" />
              {meeting.company}
              {meeting.position && ` - ${meeting.position}`}
            </p>
          )}
          
          <div className="flex items-center gap-3 mt-2">
            <Badge className={getStatusBadge(meeting.status)}>
              {meeting.status}
            </Badge>
            <span className="text-xs text-slate-400 dark:text-slate-500">
              {new Date(meeting.created_at).toLocaleDateString()}
            </span>
            {meeting.word_count > 0 && (
              <span className="text-xs text-slate-400 dark:text-slate-500">
                {meeting.word_count} words
              </span>
            )}
          </div>
        </div>
        
        <Button
          variant="ghost"
          size="sm"
          onClick={(e) => { e.stopPropagation(); onDelete(meeting.id); }}
          className="opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-600"
        >
          <Trash2 className="w-4 h-4" />
        </Button>
      </div>
    </CardContent>
  </Card>
);

const MeetingNotesPage = () => {
  const { t } = useTranslation();
  
  // Service status
  const [serviceStatus, setServiceStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  
  // Meetings list
  const [meetings, setMeetings] = useState([]);
  const [selectedMeeting, setSelectedMeeting] = useState(null);
  const [filterType, setFilterType] = useState("all");
  
  // Create meeting dialog
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newMeeting, setNewMeeting] = useState({
    title: "",
    meeting_type: "interview",
    company: "",
    position: ""
  });
  
  // Recording state
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [liveTranscript, setLiveTranscript] = useState("");
  
  // Summary generation
  const [isGeneratingSummary, setIsGeneratingSummary] = useState(false);
  
  // Stats
  const [stats, setStats] = useState(null);
  
  // Refs
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const timerRef = useRef(null);
  const wsRef = useRef(null);

  const checkServiceStatus = useCallback(async () => {
    try {
      const response = await apiClient.get('/api/meeting-notes/status');
      setServiceStatus(response.data);
    } catch (e) {
      console.error('Failed to check service status:', e);
      setServiceStatus({ available: false });
    }
    setIsLoading(false);
  }, []);

  const loadMeetings = useCallback(async () => {
    try {
      const response = await apiClient.get('/api/meeting-notes/list', {
        params: { limit: 50 }
      });
      setMeetings(response.data.meetings || []);
    } catch (e) {
      console.error('Failed to load meetings:', e);
    }
  }, []);

  const loadStats = useCallback(async () => {
    try {
      const response = await apiClient.get('/api/meeting-notes/stats/overview');
      setStats(response.data);
    } catch (e) {
      console.error('Failed to load stats:', e);
    }
  }, []);

  // Load data on mount
  useEffect(() => {
    checkServiceStatus();
    loadMeetings();
    loadStats();
  }, [checkServiceStatus, loadMeetings, loadStats]);

  // Recording timer
  useEffect(() => {
    if (isRecording) {
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isRecording]);

  const createMeeting = async () => {
    if (!newMeeting.title.trim()) {
      toast.error('Please enter a meeting title');
      return;
    }
    
    try {
      const response = await apiClient.post('/api/meeting-notes/create', newMeeting);
      setMeetings(prev => [response.data.meeting, ...prev]);
      setSelectedMeeting(response.data.meeting);
      setShowCreateDialog(false);
      setNewMeeting({ title: "", meeting_type: "interview", company: "", position: "" });
      toast.success('Meeting created!');
    } catch (e) {
      toast.error('Failed to create meeting');
    }
  };

  const deleteMeeting = async (meetingId) => {
    if (!confirm('Delete this meeting?')) return;
    
    try {
      await apiClient.delete(`/api/meeting-notes/${meetingId}`);
      setMeetings(prev => prev.filter(m => m.id !== meetingId));
      if (selectedMeeting?.id === meetingId) {
        setSelectedMeeting(null);
      }
      toast.success('Meeting deleted');
    } catch (e) {
      toast.error('Failed to delete meeting');
    }
  };

  const startRecording = async () => {
    if (!selectedMeeting) {
      toast.error('Please select or create a meeting first');
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      const chunks = [];
      
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.push(e.data);
        }
      };
      
      mediaRecorder.onstop = async () => {
        const blob = new Blob(chunks, { type: 'audio/webm' });
        await uploadAndTranscribe(blob);
      };
      
      // Try to connect to real-time STT WebSocket for live transcription
      try {
        const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/realtime-stt/stream`;
        wsRef.current = new WebSocket(wsUrl);
        
        wsRef.current.onmessage = (event) => {
          const data = JSON.parse(event.data);
          if (data.type === 'transcription') {
            setLiveTranscript(prev => prev + ' ' + data.text);
          }
        };
      } catch (wsError) {
        console.log('WebSocket not available, using batch transcription');
      }
      
      mediaRecorder.start(1000);
      mediaRecorderRef.current = mediaRecorder;
      setIsRecording(true);
      setRecordingTime(0);
      setLiveTranscript("");
      
      // Update meeting status
      await apiClient.put(`/api/meeting-notes/${selectedMeeting.id}`, {
        status: "recording"
      });
      
    } catch (err) {
      console.error('Recording error:', err);
      toast.error('Failed to access microphone');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }
    
    if (wsRef.current) {
      wsRef.current.close();
    }
    
    setIsRecording(false);
  };

  const uploadAndTranscribe = async (blob) => {
    if (!selectedMeeting) return;
    
    toast.loading('Transcribing audio...', { id: 'transcribe' });
    
    try {
      const formData = new FormData();
      formData.append('file', blob, 'recording.webm');
      
      const response = await apiClient.post(
        `/api/meeting-notes/${selectedMeeting.id}/transcribe`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      
      if (response.data.success) {
        toast.success(`Transcribed ${response.data.word_count} words!`, { id: 'transcribe' });
        
        // Reload meeting data
        const meetingResponse = await apiClient.get(`/api/meeting-notes/${selectedMeeting.id}`);
        setSelectedMeeting(meetingResponse.data);
        loadMeetings();
      }
    } catch (e) {
      toast.error('Transcription failed', { id: 'transcribe' });
    }
  };

  const generateSummary = async () => {
    if (!selectedMeeting?.transcript) {
      toast.error('No transcript available');
      return;
    }
    
    setIsGeneratingSummary(true);
    
    try {
      const response = await apiClient.post(`/api/meeting-notes/${selectedMeeting.id}/generate-summary`);
      
      if (response.data.success) {
        toast.success('Summary generated!');
        
        // Reload meeting data
        const meetingResponse = await apiClient.get(`/api/meeting-notes/${selectedMeeting.id}`);
        setSelectedMeeting(meetingResponse.data);
        loadMeetings();
      }
    } catch (e) {
      toast.error('Failed to generate summary');
    }
    
    setIsGeneratingSummary(false);
  };

  const exportMeeting = async (format = 'markdown') => {
    if (!selectedMeeting) return;
    
    try {
      const response = await apiClient.get(`/api/meeting-notes/${selectedMeeting.id}/export`, {
        params: { format }
      });
      
      const content = format === 'json' 
        ? JSON.stringify(response.data.content, null, 2)
        : response.data.content;
      
      const blob = new Blob([content], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = response.data.filename;
      a.click();
      URL.revokeObjectURL(url);
      
      toast.success('Meeting exported!');
    } catch (e) {
      toast.error('Failed to export meeting');
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const filteredMeetings = filterType === "all" 
    ? meetings 
    : meetings.filter(m => m.meeting_type === filterType);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-turquoise" />
      </div>
    );
  }

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-7xl mx-auto animate-fade-in" data-testid="meeting-notes-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 bg-gradient-to-br from-amber-500 to-orange-600 rounded-xl flex items-center justify-center">
              <FileText className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-3xl font-semibold text-slate-900 dark:text-slate-100 tracking-tight" style={{ fontFamily: 'IBM Plex Sans' }}>
              Meeting Notes
            </h1>
          </div>
          <p className="text-slate-500 dark:text-slate-400">
            AI-powered meeting transcription with automatic summaries and action items
          </p>
        </div>

        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogTrigger asChild>
            <Button className="bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700">
              <Plus className="w-4 h-4 mr-2" /> New Meeting
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Meeting</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Title *</label>
                <Input
                  placeholder="e.g., Interview with Acme Corp"
                  value={newMeeting.title}
                  onChange={(e) => setNewMeeting(prev => ({ ...prev, title: e.target.value }))}
                  data-testid="meeting-title-input"
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">Type</label>
                <Select 
                  value={newMeeting.meeting_type} 
                  onValueChange={(v) => setNewMeeting(prev => ({ ...prev, meeting_type: v }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="interview">Job Interview</SelectItem>
                    <SelectItem value="general">General Meeting</SelectItem>
                    <SelectItem value="follow_up">Follow-up Call</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Company</label>
                  <Input
                    placeholder="Company name"
                    value={newMeeting.company}
                    onChange={(e) => setNewMeeting(prev => ({ ...prev, company: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Position</label>
                  <Input
                    placeholder="Job title"
                    value={newMeeting.position}
                    onChange={(e) => setNewMeeting(prev => ({ ...prev, position: e.target.value }))}
                  />
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowCreateDialog(false)}>Cancel</Button>
              <Button onClick={createMeeting} data-testid="create-meeting-btn">Create Meeting</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-turquoise">{stats.total_meetings}</p>
              <p className="text-sm text-slate-500 dark:text-slate-400">Total Meetings</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-emerald-500">{stats.completed_meetings}</p>
              <p className="text-sm text-slate-500 dark:text-slate-400">Completed</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-violet-500">{(stats.total_words_transcribed || 0).toLocaleString()}</p>
              <p className="text-sm text-slate-500 dark:text-slate-400">Words Transcribed</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-amber-500">{stats.meetings_by_type?.interview || 0}</p>
              <p className="text-sm text-slate-500 dark:text-slate-400">Interviews</p>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Meetings List */}
        <div className="lg:col-span-1 space-y-4">
          <div className="flex items-center gap-2">
            <Select value={filterType} onValueChange={setFilterType}>
              <SelectTrigger className="w-40">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="interview">Interviews</SelectItem>
                <SelectItem value="general">General</SelectItem>
                <SelectItem value="follow_up">Follow-ups</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-3 max-h-[600px] overflow-y-auto">
            {filteredMeetings.length > 0 ? (
              filteredMeetings.map(meeting => (
                <MeetingCard
                  key={meeting.id}
                  meeting={meeting}
                  onSelect={setSelectedMeeting}
                  onDelete={deleteMeeting}
                />
              ))
            ) : (
              <div className="text-center py-12 text-slate-400 dark:text-slate-500">
                <FileText className="w-12 h-12 mx-auto mb-4 opacity-40" />
                <p>No meetings yet</p>
                <p className="text-sm mt-1">Create your first meeting to get started</p>
              </div>
            )}
          </div>
        </div>

        {/* Meeting Details / Recording */}
        <div className="lg:col-span-2">
          {selectedMeeting ? (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      {getMeetingTypeIcon(selectedMeeting.meeting_type)}
                      {selectedMeeting.title}
                    </CardTitle>
                    {selectedMeeting.company && (
                      <CardDescription className="mt-1">
                        {selectedMeeting.company}
                        {selectedMeeting.position && ` - ${selectedMeeting.position}`}
                      </CardDescription>
                    )}
                  </div>
                  <Badge className={getStatusBadge(selectedMeeting.status)}>
                    {selectedMeeting.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="record" className="space-y-4">
                  <TabsList>
                    <TabsTrigger value="record">Record</TabsTrigger>
                    <TabsTrigger value="transcript">Transcript</TabsTrigger>
                    <TabsTrigger value="summary">Summary</TabsTrigger>
                  </TabsList>

                  {/* Record Tab */}
                  <TabsContent value="record" className="space-y-4">
                    <div className="text-center py-8">
                      {/* Recording Timer */}
                      <div className="mb-6">
                        <Badge 
                          variant="outline" 
                          className={`text-lg px-4 py-2 ${isRecording ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300 animate-pulse' : ''}`}
                        >
                          <Clock className="w-4 h-4 mr-2" />
                          {formatTime(recordingTime)}
                        </Badge>
                      </div>

                      {/* Record Button */}
                      <div className="flex items-center justify-center gap-4">
                        {!isRecording ? (
                          <Button
                            size="lg"
                            onClick={startRecording}
                            disabled={!serviceStatus?.available}
                            className="w-20 h-20 rounded-full bg-gradient-to-r from-red-500 to-rose-600 hover:from-red-600 hover:to-rose-700"
                            data-testid="start-recording-btn"
                          >
                            <Mic className="w-10 h-10" />
                          </Button>
                        ) : (
                          <Button
                            size="lg"
                            onClick={stopRecording}
                            className="w-20 h-20 rounded-full bg-slate-800 hover:bg-slate-700"
                            data-testid="stop-recording-btn"
                          >
                            <Square className="w-8 h-8" />
                          </Button>
                        )}
                      </div>

                      <p className="mt-4 text-sm text-slate-500 dark:text-slate-400">
                        {isRecording 
                          ? 'Recording... Click to stop and transcribe' 
                          : 'Click to start recording your meeting'}
                      </p>

                      {/* Live transcript preview */}
                      {liveTranscript && (
                        <div className="mt-6 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg text-left">
                          <p className="text-sm text-slate-600 dark:text-slate-400">
                            {liveTranscript}
                          </p>
                        </div>
                      )}
                    </div>
                  </TabsContent>

                  {/* Transcript Tab */}
                  <TabsContent value="transcript" className="space-y-4">
                    {selectedMeeting.transcript ? (
                      <>
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-slate-500 dark:text-slate-400">
                            {selectedMeeting.word_count || 0} words
                          </span>
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => copyToClipboard(selectedMeeting.transcript)}
                          >
                            <Copy className="w-4 h-4 mr-1" /> Copy
                          </Button>
                        </div>
                        <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg max-h-[400px] overflow-y-auto">
                          <p className="text-sm text-slate-700 dark:text-slate-300 whitespace-pre-wrap">
                            {selectedMeeting.transcript}
                          </p>
                        </div>
                      </>
                    ) : (
                      <div className="text-center py-12 text-slate-400 dark:text-slate-500">
                        <Mic className="w-12 h-12 mx-auto mb-4 opacity-40" />
                        <p>No transcript yet</p>
                        <p className="text-sm mt-1">Record your meeting to generate a transcript</p>
                      </div>
                    )}
                  </TabsContent>

                  {/* Summary Tab */}
                  <TabsContent value="summary" className="space-y-4">
                    {selectedMeeting.summary ? (
                      <div className="space-y-6">
                        {/* Summary */}
                        <div>
                          <h4 className="font-medium text-slate-900 dark:text-slate-100 mb-2 flex items-center gap-2">
                            <Sparkles className="w-4 h-4 text-amber-500" />
                            Summary
                          </h4>
                          <p className="text-sm text-slate-600 dark:text-slate-400">
                            {selectedMeeting.summary}
                          </p>
                        </div>

                        {/* Key Points */}
                        {selectedMeeting.key_points?.length > 0 && (
                          <div>
                            <h4 className="font-medium text-slate-900 dark:text-slate-100 mb-2 flex items-center gap-2">
                              <ListChecks className="w-4 h-4 text-blue-500" />
                              Key Points
                            </h4>
                            <ul className="space-y-1">
                              {selectedMeeting.key_points.map((point, i) => (
                                <li key={i} className="text-sm text-slate-600 dark:text-slate-400 flex items-start gap-2">
                                  <span className="text-turquoise">•</span>
                                  {point}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {/* Action Items */}
                        {selectedMeeting.action_items?.length > 0 && (
                          <div>
                            <h4 className="font-medium text-slate-900 dark:text-slate-100 mb-2 flex items-center gap-2">
                              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                              Action Items
                            </h4>
                            <ul className="space-y-1">
                              {selectedMeeting.action_items.map((item, i) => (
                                <li key={i} className="text-sm text-slate-600 dark:text-slate-400 flex items-start gap-2">
                                  <span className="text-emerald-500">☐</span>
                                  {item}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {/* Next Steps */}
                        {selectedMeeting.next_steps && (
                          <div>
                            <h4 className="font-medium text-slate-900 dark:text-slate-100 mb-2 flex items-center gap-2">
                              <ChevronRight className="w-4 h-4 text-violet-500" />
                              Next Steps
                            </h4>
                            <p className="text-sm text-slate-600 dark:text-slate-400">
                              {selectedMeeting.next_steps}
                            </p>
                          </div>
                        )}

                        {/* Sentiment Badge */}
                        {selectedMeeting.sentiment && (
                          <Badge variant="outline" className="capitalize">
                            Sentiment: {selectedMeeting.sentiment}
                          </Badge>
                        )}
                      </div>
                    ) : (
                      <div className="text-center py-12">
                        {selectedMeeting.transcript ? (
                          <>
                            <Sparkles className="w-12 h-12 mx-auto mb-4 text-amber-500 opacity-60" />
                            <p className="text-slate-500 dark:text-slate-400 mb-4">
                              Ready to generate AI summary
                            </p>
                            <Button 
                              onClick={generateSummary}
                              disabled={isGeneratingSummary}
                              className="bg-gradient-to-r from-amber-500 to-orange-600"
                              data-testid="generate-summary-btn"
                            >
                              {isGeneratingSummary ? (
                                <>
                                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                  Generating...
                                </>
                              ) : (
                                <>
                                  <Sparkles className="w-4 h-4 mr-2" />
                                  Generate Summary
                                </>
                              )}
                            </Button>
                          </>
                        ) : (
                          <>
                            <Sparkles className="w-12 h-12 mx-auto mb-4 text-slate-300 dark:text-slate-600" />
                            <p className="text-slate-400 dark:text-slate-500">
                              Record and transcribe your meeting first
                            </p>
                          </>
                        )}
                      </div>
                    )}
                  </TabsContent>
                </Tabs>

                {/* Export Actions */}
                {selectedMeeting.status === 'completed' && (
                  <div className="mt-6 pt-4 border-t border-slate-200 dark:border-slate-700 flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => exportMeeting('markdown')}>
                      <Download className="w-4 h-4 mr-1" /> Export Markdown
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => exportMeeting('json')}>
                      <Download className="w-4 h-4 mr-1" /> Export JSON
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="p-12 text-center">
                <FileText className="w-16 h-16 mx-auto mb-4 text-slate-300 dark:text-slate-600" />
                <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100 mb-2">
                  Select or Create a Meeting
                </h3>
                <p className="text-slate-500 dark:text-slate-400 mb-6">
                  Choose a meeting from the list or create a new one to start recording
                </p>
                <Button onClick={() => setShowCreateDialog(true)}>
                  <Plus className="w-4 h-4 mr-2" /> Create Meeting
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Tips */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle className="text-lg" style={{ fontFamily: 'IBM Plex Sans' }}>
            Tips for Better Meeting Notes
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-4 gap-4">
            {[
              { icon: Mic, title: 'Use a Good Mic', desc: 'External microphones capture clearer audio' },
              { icon: Users, title: 'Minimize Background', desc: 'Record in a quiet environment' },
              { icon: Clock, title: 'Speak Clearly', desc: 'Natural pace improves transcription accuracy' },
              { icon: Sparkles, title: 'Review & Edit', desc: 'AI summaries work best with accurate transcripts' }
            ].map(({ icon: Icon, title, desc }) => (
              <div key={title} className="text-center p-4">
                <Icon className="w-8 h-8 text-amber-500 mx-auto mb-2" />
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

export default MeetingNotesPage;
