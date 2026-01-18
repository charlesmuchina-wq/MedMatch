import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { useTheme } from "@/App";
import { 
  Calendar, Clock, Video, Phone, MapPin, User, Briefcase,
  Check, X, AlertCircle, Plus, ChevronRight, Loader2, 
  CalendarPlus, ExternalLink, Bell, RefreshCw
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useTranslation } from "@/utils/i18n";
import { apiClient } from "@/utils/apiClient";

const InterviewSchedulingPage = ({ user }) => {
  const navigate = useNavigate();
  const { isDark } = useTheme();
  const { t } = useTranslation();
  
  const [interviews, setInterviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("upcoming");
  
  // Schedule dialog state
  const [showScheduleDialog, setShowScheduleDialog] = useState(false);
  const [selectedApplicant, setSelectedApplicant] = useState(null);
  const [applicants, setApplicants] = useState([]);
  const [scheduleForm, setScheduleForm] = useState({
    applicant_id: "",
    job_id: "",
    interview_type: "video",
    date: "",
    start_time: "09:00",
    end_time: "10:00",
    timezone: "UTC",
    meeting_link: "",
    location: "",
    notes: ""
  });
  
  // Response dialog state (for candidates)
  const [showResponseDialog, setShowResponseDialog] = useState(false);
  const [selectedInterview, setSelectedInterview] = useState(null);
  const [responseMessage, setResponseMessage] = useState("");

  const isRecruiter = user?.role === "recruiter";

  useEffect(() => {
    fetchInterviews();
    if (isRecruiter) {
      fetchApplicants();
    }
  }, [user]);

  const fetchInterviews = async () => {
    try {
      const endpoint = isRecruiter 
        ? `/api/interviews/recruiter/upcoming`
        : `/api/interviews/candidate/upcoming`;
      
      const response = await apiClient.get(endpoint);
      setInterviews(response.data.interviews || []);
    } catch (e) {
      console.error("Failed to load interviews:", e);
    }
    setLoading(false);
  };

  const fetchApplicants = async () => {
    try {
      // Fetch applicants who are in "shortlisted" or "interviewing" status
      const response = await apiClient.get(`/api/recruiter/applicants?status=shortlisted`);
      setApplicants(response.data.applicants || []);
    } catch (e) {
      console.error("Failed to load applicants");
    }
  };

  const scheduleInterview = async () => {
    if (!scheduleForm.applicant_id || !scheduleForm.date || !scheduleForm.start_time) {
      toast.error(t("scheduling.fillRequired") || "Please fill in all required fields");
      return;
    }

    try {
      const response = await apiClient.post(`/api/interviews/schedule`, {
        applicant_id: scheduleForm.applicant_id,
        job_id: scheduleForm.job_id,
        interview_type: scheduleForm.interview_type,
        slot: {
          date: scheduleForm.date,
          start_time: scheduleForm.start_time,
          end_time: scheduleForm.end_time,
          timezone: scheduleForm.timezone
        },
        meeting_link: scheduleForm.meeting_link,
        location: scheduleForm.location,
        notes: scheduleForm.notes,
        notify_candidate: true
      });

      toast.success(t("scheduling.success") || "Interview scheduled successfully");
      setShowScheduleDialog(false);
      resetScheduleForm();
      fetchInterviews();

      // Offer to download ICS file
      if (response.data.ics_content) {
        const blob = new Blob([response.data.ics_content], { type: 'text/calendar' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `interview_${response.data.interview_id}.ics`;
        a.click();
      }
    } catch (e) {
      toast.error(e.data?.detail || t("scheduling.failed") || "Failed to schedule interview");
    }
  };

  const respondToInterview = async (interviewId, responseType) => {
    try {
      await apiClient.post(`/api/interviews/${interviewId}/respond`, {
        response: responseType,
        message: responseMessage
      });

      toast.success(`${t("scheduling.interview") || "Interview"} ${responseType}ed`);
      setShowResponseDialog(false);
      setSelectedInterview(null);
      setResponseMessage("");
      fetchInterviews();
    } catch (e) {
      toast.error(e.data?.detail || t("scheduling.respondFailed") || "Failed to respond");
    }
  };

  const cancelInterview = async (interviewId) => {
    if (!confirm(t("scheduling.confirmCancel") || "Are you sure you want to cancel this interview?")) return;

    try {
      await apiClient.put(`/api/interviews/${interviewId}/cancel`);
      toast.success(t("scheduling.cancelled") || "Interview cancelled");
      fetchInterviews();
    } catch (e) {
      toast.error(t("scheduling.cancelFailed") || "Failed to cancel interview");
    }
  };

  const openCalendarEvent = async (interviewId, format) => {
    try {
      const response = await apiClient.get(`/api/interviews/${interviewId}/calendar?format=${format}`);
      
      if (format === "google" && response.data.google_calendar_url) {
        window.open(response.data.google_calendar_url, "_blank");
      } else if (format === "ics" && response.data.ics_content) {
        const blob = new Blob([response.data.ics_content], { type: 'text/calendar' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = response.data.filename || 'interview.ics';
        a.click();
      }
    } catch (e) {
      toast.error("Failed to generate calendar event");
    }
  };

  const resetScheduleForm = () => {
    setScheduleForm({
      applicant_id: "",
      job_id: "",
      interview_type: "video",
      date: "",
      start_time: "09:00",
      end_time: "10:00",
      timezone: "UTC",
      meeting_link: "",
      location: "",
      notes: ""
    });
    setSelectedApplicant(null);
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: "bg-amber-100 text-amber-700",
      confirmed: "bg-emerald-100 text-emerald-700",
      declined: "bg-red-100 text-red-700",
      completed: "bg-slate-100 text-slate-700",
      cancelled: "bg-slate-100 text-slate-500",
      reschedule_requested: "bg-blue-100 text-blue-700"
    };
    return colors[status] || "bg-slate-100 text-slate-700";
  };

  const getInterviewTypeIcon = (type) => {
    switch (type) {
      case "video": return <Video className="w-4 h-4" />;
      case "phone": return <Phone className="w-4 h-4" />;
      case "in_person": return <MapPin className="w-4 h-4" />;
      default: return <Calendar className="w-4 h-4" />;
    }
  };

  const formatDate = (dateStr) => {
    try {
      return new Date(dateStr).toLocaleDateString('en-US', { 
        weekday: 'short', 
        month: 'short', 
        day: 'numeric' 
      });
    } catch {
      return dateStr;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 animate-spin text-turquoise" />
      </div>
    );
  }

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-6xl mx-auto animate-fade-in" data-testid="interview-scheduling">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl md:text-4xl font-semibold text-slate-900 dark:text-slate-100">
            Interview Scheduling
          </h1>
          <p className="text-slate-500 dark:text-slate-400 mt-2">
            {isRecruiter ? "Manage your interview schedule" : "View and respond to interview invitations"}
          </p>
        </div>
        
        {isRecruiter && (
          <Button onClick={() => setShowScheduleDialog(true)} className="gap-2">
            <Plus className="w-4 h-4" />
            Schedule Interview
          </Button>
        )}
      </div>

      {/* Interview List */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="upcoming">Upcoming</TabsTrigger>
          <TabsTrigger value="pending">Pending Response</TabsTrigger>
          <TabsTrigger value="past">Past</TabsTrigger>
        </TabsList>

        <TabsContent value="upcoming" className="mt-6">
          {interviews.filter(i => ["confirmed", "pending"].includes(i.status)).length > 0 ? (
            <div className="space-y-4">
              {interviews
                .filter(i => ["confirmed", "pending"].includes(i.status))
                .map((interview) => (
                  <InterviewCard
                    key={interview.id}
                    interview={interview}
                    isRecruiter={isRecruiter}
                    onRespond={() => {
                      setSelectedInterview(interview);
                      setShowResponseDialog(true);
                    }}
                    onCancel={() => cancelInterview(interview.id)}
                    onAddToCalendar={openCalendarEvent}
                    getStatusColor={getStatusColor}
                    getInterviewTypeIcon={getInterviewTypeIcon}
                    formatDate={formatDate}
                  />
                ))}
            </div>
          ) : (
            <EmptyState 
              icon={<Calendar className="w-12 h-12" />}
              title="No upcoming interviews"
              description={isRecruiter ? "Schedule an interview with a candidate" : "You don't have any scheduled interviews"}
            />
          )}
        </TabsContent>

        <TabsContent value="pending" className="mt-6">
          {interviews.filter(i => i.status === "pending" && !isRecruiter).length > 0 ? (
            <div className="space-y-4">
              {interviews
                .filter(i => i.status === "pending")
                .map((interview) => (
                  <InterviewCard
                    key={interview.id}
                    interview={interview}
                    isRecruiter={isRecruiter}
                    onRespond={() => {
                      setSelectedInterview(interview);
                      setShowResponseDialog(true);
                    }}
                    onCancel={() => cancelInterview(interview.id)}
                    onAddToCalendar={openCalendarEvent}
                    getStatusColor={getStatusColor}
                    getInterviewTypeIcon={getInterviewTypeIcon}
                    formatDate={formatDate}
                    showResponseButtons={!isRecruiter}
                  />
                ))}
            </div>
          ) : (
            <EmptyState 
              icon={<Bell className="w-12 h-12" />}
              title="No pending responses"
              description="All interview invitations have been responded to"
            />
          )}
        </TabsContent>

        <TabsContent value="past" className="mt-6">
          <EmptyState 
            icon={<Clock className="w-12 h-12" />}
            title="No past interviews"
            description="Completed interviews will appear here"
          />
        </TabsContent>
      </Tabs>

      {/* Schedule Interview Dialog (Recruiter) */}
      <Dialog open={showScheduleDialog} onOpenChange={setShowScheduleDialog}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Schedule Interview</DialogTitle>
            <DialogDescription>
              Set up an interview with a candidate
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            {/* Applicant Selection */}
            <div>
              <label className="text-sm font-medium mb-2 block">Candidate *</label>
              <Select
                value={scheduleForm.applicant_id}
                onValueChange={(value) => {
                  const applicant = applicants.find(a => a.id === value);
                  setSelectedApplicant(applicant);
                  setScheduleForm({
                    ...scheduleForm,
                    applicant_id: value,
                    job_id: applicant?.job_id || ""
                  });
                }}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a candidate" />
                </SelectTrigger>
                <SelectContent>
                  {applicants.map((applicant) => (
                    <SelectItem key={applicant.id} value={applicant.id}>
                      {applicant.applicant_name} - {applicant.job_title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Interview Type */}
            <div>
              <label className="text-sm font-medium mb-2 block">Interview Type *</label>
              <Select
                value={scheduleForm.interview_type}
                onValueChange={(value) => setScheduleForm({...scheduleForm, interview_type: value})}
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

            {/* Date & Time */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Date *</label>
                <Input
                  type="date"
                  value={scheduleForm.date}
                  onChange={(e) => setScheduleForm({...scheduleForm, date: e.target.value})}
                  min={new Date().toISOString().split('T')[0]}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">Start Time *</label>
                <Input
                  type="time"
                  value={scheduleForm.start_time}
                  onChange={(e) => setScheduleForm({...scheduleForm, start_time: e.target.value})}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">End Time</label>
                <Input
                  type="time"
                  value={scheduleForm.end_time}
                  onChange={(e) => setScheduleForm({...scheduleForm, end_time: e.target.value})}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">Timezone</label>
                <Select
                  value={scheduleForm.timezone}
                  onValueChange={(value) => setScheduleForm({...scheduleForm, timezone: value})}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="UTC">UTC</SelectItem>
                    <SelectItem value="America/New_York">Eastern Time</SelectItem>
                    <SelectItem value="America/Chicago">Central Time</SelectItem>
                    <SelectItem value="America/Denver">Mountain Time</SelectItem>
                    <SelectItem value="America/Los_Angeles">Pacific Time</SelectItem>
                    <SelectItem value="Europe/London">London</SelectItem>
                    <SelectItem value="Asia/Singapore">Singapore</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Meeting Link / Location */}
            {scheduleForm.interview_type === "video" && (
              <div>
                <label className="text-sm font-medium mb-2 block">Meeting Link</label>
                <Input
                  placeholder="https://zoom.us/j/..."
                  value={scheduleForm.meeting_link}
                  onChange={(e) => setScheduleForm({...scheduleForm, meeting_link: e.target.value})}
                />
              </div>
            )}

            {scheduleForm.interview_type === "in_person" && (
              <div>
                <label className="text-sm font-medium mb-2 block">Location</label>
                <Input
                  placeholder="Office address"
                  value={scheduleForm.location}
                  onChange={(e) => setScheduleForm({...scheduleForm, location: e.target.value})}
                />
              </div>
            )}

            {/* Notes */}
            <div>
              <label className="text-sm font-medium mb-2 block">Notes for Candidate</label>
              <Textarea
                placeholder="Any additional information..."
                value={scheduleForm.notes}
                onChange={(e) => setScheduleForm({...scheduleForm, notes: e.target.value})}
                rows={3}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowScheduleDialog(false)}>
              Cancel
            </Button>
            <Button onClick={scheduleInterview} className="gap-2">
              <CalendarPlus className="w-4 h-4" />
              Schedule
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Response Dialog (Candidate) */}
      <Dialog open={showResponseDialog} onOpenChange={setShowResponseDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Respond to Interview</DialogTitle>
            <DialogDescription>
              {selectedInterview?.job_title} at {selectedInterview?.company}
            </DialogDescription>
          </DialogHeader>

          {selectedInterview && (
            <div className="py-4">
              <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800 mb-4">
                <div className="flex items-center gap-2 mb-2">
                  {getInterviewTypeIcon(selectedInterview.interview_type)}
                  <span className="font-medium capitalize">{selectedInterview.interview_type} Interview</span>
                </div>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  {formatDate(selectedInterview.scheduled_date)} at {selectedInterview.start_time}
                </p>
                {selectedInterview.meeting_link && (
                  <a 
                    href={selectedInterview.meeting_link} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-sm text-turquoise hover:underline flex items-center gap-1 mt-2"
                  >
                    <ExternalLink className="w-3 h-3" />
                    Join Meeting
                  </a>
                )}
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Message (optional)</label>
                <Textarea
                  placeholder="Add a message to the recruiter..."
                  value={responseMessage}
                  onChange={(e) => setResponseMessage(e.target.value)}
                  rows={3}
                />
              </div>
            </div>
          )}

          <DialogFooter className="flex-col sm:flex-row gap-2">
            <Button 
              variant="outline" 
              onClick={() => respondToInterview(selectedInterview?.id, "decline")}
              className="text-red-600 hover:text-red-700 hover:bg-red-50"
            >
              <X className="w-4 h-4 mr-2" />
              Decline
            </Button>
            <Button 
              variant="outline"
              onClick={() => respondToInterview(selectedInterview?.id, "reschedule")}
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Request Reschedule
            </Button>
            <Button 
              onClick={() => respondToInterview(selectedInterview?.id, "accept")}
              className="bg-emerald-500 hover:bg-emerald-600"
            >
              <Check className="w-4 h-4 mr-2" />
              Accept
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// Interview Card Component
const InterviewCard = ({ 
  interview, 
  isRecruiter, 
  onRespond, 
  onCancel, 
  onAddToCalendar,
  getStatusColor,
  getInterviewTypeIcon,
  formatDate,
  showResponseButtons = false
}) => {
  return (
    <Card className="hover:border-turquoise/30 transition-colors" data-testid={`interview-card-${interview.id}`}>
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div className="flex gap-4">
            {/* Date Badge */}
            <div className="w-16 h-16 rounded-xl bg-turquoise/10 flex flex-col items-center justify-center">
              <span className="text-xs text-turquoise font-medium">
                {formatDate(interview.scheduled_date).split(' ')[0]}
              </span>
              <span className="text-2xl font-bold text-turquoise">
                {new Date(interview.scheduled_date).getDate()}
              </span>
            </div>

            {/* Details */}
            <div>
              <h3 className="font-semibold text-slate-900 dark:text-slate-100">
                {interview.job_title}
              </h3>
              <p className="text-sm text-slate-500">{interview.company}</p>
              
              <div className="flex items-center gap-4 mt-2 text-sm text-slate-500">
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {interview.start_time} - {interview.end_time}
                </span>
                <span className="flex items-center gap-1">
                  {getInterviewTypeIcon(interview.interview_type)}
                  <span className="capitalize">{interview.interview_type}</span>
                </span>
              </div>

              {isRecruiter && interview.applicant_name && (
                <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                  <User className="w-3 h-3 inline mr-1" />
                  {interview.applicant_name}
                </p>
              )}
            </div>
          </div>

          {/* Status & Actions */}
          <div className="flex flex-col items-end gap-2">
            <Badge className={getStatusColor(interview.status)}>
              {interview.status.replace("_", " ")}
            </Badge>

            <div className="flex items-center gap-2">
              {/* Add to Calendar */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onAddToCalendar(interview.id, "google")}
                title="Add to Google Calendar"
              >
                <CalendarPlus className="w-4 h-4" />
              </Button>

              {/* Candidate Response Buttons */}
              {showResponseButtons && interview.status === "pending" && (
                <Button size="sm" onClick={onRespond}>
                  Respond
                </Button>
              )}

              {/* Recruiter Cancel Button */}
              {isRecruiter && ["pending", "confirmed"].includes(interview.status) && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onCancel}
                  className="text-red-500 hover:text-red-600 hover:bg-red-50"
                >
                  <X className="w-4 h-4" />
                </Button>
              )}
            </div>
          </div>
        </div>

        {/* Meeting Link */}
        {interview.meeting_link && (
          <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800">
            <a 
              href={interview.meeting_link}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-turquoise hover:underline flex items-center gap-1"
            >
              <Video className="w-4 h-4" />
              Join Meeting
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Empty State Component
const EmptyState = ({ icon, title, description }) => (
  <Card>
    <CardContent className="py-12 text-center">
      <div className="text-slate-300 dark:text-slate-600 mx-auto mb-4">
        {icon}
      </div>
      <h3 className="text-lg font-medium text-slate-600 dark:text-slate-400">{title}</h3>
      <p className="text-sm text-slate-400 mt-1">{description}</p>
    </CardContent>
  </Card>
);

export default InterviewSchedulingPage;
