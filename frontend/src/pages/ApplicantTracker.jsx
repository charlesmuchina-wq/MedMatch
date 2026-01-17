import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import { useTheme } from "@/App";
import { 
  Users, ChevronLeft, Mail, Phone, Briefcase, Award, Clock,
  Loader2, Brain, MessageSquare, Check, X, Star, FileText,
  ChevronDown, Filter, Search, UserCheck, UserX, Calendar
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const API = process.env.REACT_APP_BACKEND_URL;

const STATUS_OPTIONS = [
  { value: "new", label: "New", color: "bg-blue-500" },
  { value: "reviewing", label: "Reviewing", color: "bg-amber-500" },
  { value: "shortlisted", label: "Shortlisted", color: "bg-emerald-500" },
  { value: "interviewing", label: "Interviewing", color: "bg-violet-500" },
  { value: "offered", label: "Offered", color: "bg-cyan-500" },
  { value: "hired", label: "Hired", color: "bg-green-600" },
  { value: "rejected", label: "Rejected", color: "bg-slate-400" }
];

const ApplicantTracker = ({ user }) => {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const { isDark } = useTheme();
  
  const [job, setJob] = useState(null);
  const [applicants, setApplicants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedApplicant, setSelectedApplicant] = useState(null);
  const [showDetailDialog, setShowDetailDialog] = useState(false);
  const [prescreening, setPrescreening] = useState(false);
  const [filterStatus, setFilterStatus] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [noteText, setNoteText] = useState("");
  const [addingNote, setAddingNote] = useState(false);

  useEffect(() => {
    if (user?.role !== "recruiter") {
      navigate("/");
      return;
    }
    fetchApplicants();
  }, [user, jobId, navigate]);

  const fetchApplicants = async () => {
    try {
      const response = await axios.get(`${API}/api/recruiter/jobs/${jobId}/applicants`);
      setJob(response.data.job);
      setApplicants(response.data.applicants || []);
    } catch (e) {
      toast.error("Failed to fetch applicants");
      console.error(e);
    }
    setLoading(false);
  };

  const updateStatus = async (applicantId, newStatus) => {
    try {
      await axios.put(`${API}/api/recruiter/applicants/${applicantId}/status`, {
        status: newStatus
      });
      toast.success(`Status updated to ${newStatus}`);
      fetchApplicants();
    } catch (e) {
      toast.error("Failed to update status");
    }
  };

  const addNote = async (applicantId) => {
    if (!noteText.trim()) return;
    setAddingNote(true);
    try {
      await axios.post(`${API}/api/recruiter/applicants/${applicantId}/notes`, {
        note: noteText
      });
      toast.success("Note added");
      setNoteText("");
      fetchApplicants();
      // Refresh selected applicant
      const updated = applicants.find(a => a.id === applicantId);
      if (updated) {
        setSelectedApplicant({...updated, notes: [...(updated.notes || []), {text: noteText}]});
      }
    } catch (e) {
      toast.error("Failed to add note");
    }
    setAddingNote(false);
  };

  const runAIPrescreen = async (applicant) => {
    setPrescreening(true);
    try {
      const response = await axios.post(`${API}/api/recruiter/ai-prescreen`, {
        candidate_id: applicant.resume_snapshot?.id || applicant.id,
        job_id: jobId
      });
      toast.success("AI analysis complete");
      setSelectedApplicant({
        ...applicant,
        ai_analysis: response.data.analysis
      });
      fetchApplicants();
    } catch (e) {
      toast.error("AI prescreening failed");
      console.error(e);
    }
    setPrescreening(false);
  };

  const sendMessage = (applicant) => {
    navigate(`/messages/new?recipient=${applicant.applicant_id}&name=${encodeURIComponent(applicant.applicant_name)}`);
  };

  const filteredApplicants = applicants.filter(a => {
    const matchesStatus = filterStatus === "all" || a.status === filterStatus;
    const matchesSearch = !searchQuery || 
      a.applicant_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      a.applicant_email?.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  const getStatusColor = (status) => {
    return STATUS_OPTIONS.find(s => s.value === status)?.color || "bg-slate-500";
  };

  const getScoreColor = (score) => {
    if (score >= 80) return "text-emerald-500";
    if (score >= 60) return "text-amber-500";
    return "text-red-500";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 animate-spin text-turquoise" />
      </div>
    );
  }

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-7xl mx-auto animate-fade-in" data-testid="applicant-tracker">
      {/* Header */}
      <div className="mb-6">
        <Button 
          variant="ghost" 
          onClick={() => navigate('/recruiter/jobs')}
          className="mb-4"
        >
          <ChevronLeft className="w-4 h-4 mr-1" />
          Back to Jobs
        </Button>
        
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-2xl md:text-3xl font-semibold text-slate-900 dark:text-slate-100">
              {job?.title || "Job Applicants"}
            </h1>
            <p className="text-slate-500 dark:text-slate-400">
              {job?.company} • {applicants.length} applicants
            </p>
          </div>
          
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input 
                placeholder="Search applicants..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 w-64"
              />
            </div>
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" className="gap-2">
                  <Filter className="w-4 h-4" />
                  {filterStatus === "all" ? "All Status" : filterStatus}
                  <ChevronDown className="w-4 h-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                <DropdownMenuItem onClick={() => setFilterStatus("all")}>
                  All Status
                </DropdownMenuItem>
                {STATUS_OPTIONS.map(status => (
                  <DropdownMenuItem 
                    key={status.value}
                    onClick={() => setFilterStatus(status.value)}
                  >
                    <div className={`w-2 h-2 rounded-full ${status.color} mr-2`} />
                    {status.label}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>

      {/* Applicants List */}
      {filteredApplicants.length > 0 ? (
        <div className="space-y-4">
          {filteredApplicants.map((applicant) => (
            <Card 
              key={applicant.id}
              className="hover:border-turquoise/50 transition-all cursor-pointer"
              onClick={() => {
                setSelectedApplicant(applicant);
                setShowDetailDialog(true);
              }}
            >
              <CardContent className="p-4">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-turquoise to-emerald-500 
                      flex items-center justify-center text-white font-semibold text-lg">
                      {(applicant.applicant_name || applicant.applicant_email || "?")[0].toUpperCase()}
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-900 dark:text-slate-100">
                        {applicant.applicant_name || "Anonymous"}
                      </h3>
                      <p className="text-sm text-slate-500">{applicant.applicant_email}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <Clock className="w-3 h-3 text-slate-400" />
                        <span className="text-xs text-slate-400">
                          Applied {new Date(applicant.applied_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    {/* AI Score Badge */}
                    {applicant.ai_analysis && (
                      <div className="flex items-center gap-1 px-3 py-1 rounded-full bg-slate-100 dark:bg-slate-800">
                        <Brain className="w-4 h-4 text-violet-500" />
                        <span className={`font-semibold ${getScoreColor(applicant.ai_analysis.overall_score)}`}>
                          {applicant.ai_analysis.overall_score}%
                        </span>
                      </div>
                    )}

                    {/* Skills Preview */}
                    <div className="hidden md:flex items-center gap-1">
                      {applicant.resume_snapshot?.skills?.slice(0, 3).map((skill, idx) => (
                        <Badge key={idx} variant="secondary" className="text-xs">
                          {skill}
                        </Badge>
                      ))}
                      {applicant.resume_snapshot?.skills?.length > 3 && (
                        <Badge variant="secondary" className="text-xs">
                          +{applicant.resume_snapshot.skills.length - 3}
                        </Badge>
                      )}
                    </div>

                    {/* Status Dropdown */}
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                        <Button variant="outline" size="sm" className="gap-2">
                          <div className={`w-2 h-2 rounded-full ${getStatusColor(applicant.status)}`} />
                          {applicant.status}
                          <ChevronDown className="w-3 h-3" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent>
                        {STATUS_OPTIONS.map(status => (
                          <DropdownMenuItem 
                            key={status.value}
                            onClick={(e) => {
                              e.stopPropagation();
                              updateStatus(applicant.id, status.value);
                            }}
                          >
                            <div className={`w-2 h-2 rounded-full ${status.color} mr-2`} />
                            {status.label}
                          </DropdownMenuItem>
                        ))}
                      </DropdownMenuContent>
                    </DropdownMenu>

                    {/* Quick Actions */}
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        sendMessage(applicant);
                      }}
                    >
                      <MessageSquare className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="py-12 text-center">
            <Users className="w-12 h-12 mx-auto mb-3 text-slate-300" />
            <h3 className="text-lg font-medium text-slate-600 dark:text-slate-400">
              No applicants yet
            </h3>
            <p className="text-sm text-slate-500 mt-1">
              Share your job posting to start receiving applications
            </p>
          </CardContent>
        </Card>
      )}

      {/* Applicant Detail Dialog */}
      <Dialog open={showDetailDialog} onOpenChange={setShowDetailDialog}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          {selectedApplicant && (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-turquoise to-emerald-500 
                    flex items-center justify-center text-white font-semibold">
                    {(selectedApplicant.applicant_name || "?")[0].toUpperCase()}
                  </div>
                  <div>
                    <span>{selectedApplicant.applicant_name || "Anonymous"}</span>
                    <p className="text-sm font-normal text-slate-500">
                      {selectedApplicant.applicant_email}
                    </p>
                  </div>
                </DialogTitle>
              </DialogHeader>

              <div className="space-y-6 py-4">
                {/* AI Analysis Section */}
                <div className="p-4 rounded-lg bg-gradient-to-br from-violet-50 to-violet-100/50 
                  dark:from-violet-900/20 dark:to-violet-800/10 border border-violet-200 dark:border-violet-800">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold text-violet-900 dark:text-violet-100 flex items-center gap-2">
                      <Brain className="w-5 h-5" />
                      AI Prescreening
                    </h4>
                    <Button
                      size="sm"
                      variant={selectedApplicant.ai_analysis ? "outline" : "default"}
                      onClick={() => runAIPrescreen(selectedApplicant)}
                      disabled={prescreening}
                      className="gap-2"
                    >
                      {prescreening ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Brain className="w-4 h-4" />
                      )}
                      {selectedApplicant.ai_analysis ? "Re-analyze" : "Run Analysis"}
                    </Button>
                  </div>

                  {selectedApplicant.ai_analysis ? (
                    <div className="space-y-4">
                      {/* Score */}
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-slate-600 dark:text-slate-400">Match Score</span>
                        <span className={`text-2xl font-bold ${getScoreColor(selectedApplicant.ai_analysis.overall_score)}`}>
                          {selectedApplicant.ai_analysis.overall_score}%
                        </span>
                      </div>
                      
                      {/* Recommendation */}
                      <div className="p-3 rounded-lg bg-white dark:bg-slate-800">
                        <Badge className={
                          selectedApplicant.ai_analysis.recommendation?.includes("Strong") ? "bg-emerald-500" :
                          selectedApplicant.ai_analysis.recommendation?.includes("Good") ? "bg-blue-500" :
                          selectedApplicant.ai_analysis.recommendation?.includes("Potential") ? "bg-amber-500" :
                          "bg-slate-500"
                        }>
                          {selectedApplicant.ai_analysis.recommendation}
                        </Badge>
                        <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
                          {selectedApplicant.ai_analysis.summary}
                        </p>
                      </div>

                      {/* Skills Analysis */}
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <p className="text-xs font-medium text-emerald-600 dark:text-emerald-400 mb-1">
                            Matched Skills
                          </p>
                          <div className="flex flex-wrap gap-1">
                            {selectedApplicant.ai_analysis.skills_analysis?.matched_skills?.map((skill, i) => (
                              <Badge key={i} variant="secondary" className="bg-emerald-100 text-emerald-700 text-xs">
                                <Check className="w-3 h-3 mr-1" />{skill}
                              </Badge>
                            ))}
                          </div>
                        </div>
                        <div>
                          <p className="text-xs font-medium text-amber-600 dark:text-amber-400 mb-1">
                            Transferable Skills
                          </p>
                          <div className="flex flex-wrap gap-1">
                            {selectedApplicant.ai_analysis.skills_analysis?.transferable_skills?.slice(0, 4).map((skill, i) => (
                              <Badge key={i} variant="secondary" className="bg-amber-100 text-amber-700 text-xs">
                                {typeof skill === 'string' ? skill.split(' - ')[0] : skill}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* Interview Questions */}
                      {selectedApplicant.ai_analysis.interview_questions?.length > 0 && (
                        <div>
                          <p className="text-xs font-medium text-slate-600 dark:text-slate-400 mb-2">
                            Suggested Interview Questions
                          </p>
                          <ul className="space-y-1">
                            {selectedApplicant.ai_analysis.interview_questions.map((q, i) => (
                              <li key={i} className="text-sm text-slate-600 dark:text-slate-300 flex items-start gap-2">
                                <span className="text-turquoise">•</span>
                                {q}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ) : (
                    <p className="text-sm text-slate-500 text-center py-4">
                      Run AI analysis to get prescreening insights, match scores, and interview questions
                    </p>
                  )}
                </div>

                {/* Skills */}
                <div>
                  <h4 className="font-semibold text-slate-900 dark:text-slate-100 mb-2 flex items-center gap-2">
                    <Award className="w-4 h-4 text-turquoise" />
                    Skills
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedApplicant.resume_snapshot?.skills?.map((skill, idx) => (
                      <Badge key={idx} variant="outline">{skill}</Badge>
                    ))}
                    {(!selectedApplicant.resume_snapshot?.skills || selectedApplicant.resume_snapshot.skills.length === 0) && (
                      <span className="text-sm text-slate-500">No skills listed</span>
                    )}
                  </div>
                </div>

                {/* Experience */}
                <div>
                  <h4 className="font-semibold text-slate-900 dark:text-slate-100 mb-2 flex items-center gap-2">
                    <Briefcase className="w-4 h-4 text-turquoise" />
                    Experience
                  </h4>
                  {selectedApplicant.resume_snapshot?.experience?.length > 0 ? (
                    <div className="space-y-3">
                      {selectedApplicant.resume_snapshot.experience.slice(0, 3).map((exp, idx) => (
                        <div key={idx} className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50">
                          <p className="font-medium text-slate-900 dark:text-slate-100">{exp.title}</p>
                          <p className="text-sm text-slate-500">{exp.company} • {exp.duration}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-slate-500">No experience listed</p>
                  )}
                </div>

                {/* Notes */}
                <div>
                  <h4 className="font-semibold text-slate-900 dark:text-slate-100 mb-2 flex items-center gap-2">
                    <FileText className="w-4 h-4 text-turquoise" />
                    Notes
                  </h4>
                  <div className="space-y-2 mb-3">
                    {selectedApplicant.notes?.map((note, idx) => (
                      <div key={idx} className="p-2 rounded-lg bg-slate-50 dark:bg-slate-800/50 text-sm">
                        <p className="text-slate-700 dark:text-slate-300">{note.text}</p>
                        <p className="text-xs text-slate-400 mt-1">
                          {note.created_by} • {new Date(note.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <Textarea
                      placeholder="Add a note..."
                      value={noteText}
                      onChange={(e) => setNoteText(e.target.value)}
                      className="flex-1"
                      rows={2}
                    />
                    <Button
                      onClick={() => addNote(selectedApplicant.id)}
                      disabled={addingNote || !noteText.trim()}
                    >
                      {addingNote ? <Loader2 className="w-4 h-4 animate-spin" /> : "Add"}
                    </Button>
                  </div>
                </div>
              </div>

              <DialogFooter>
                <Button variant="outline" onClick={() => setShowDetailDialog(false)}>
                  Close
                </Button>
                <Button onClick={() => sendMessage(selectedApplicant)} className="gap-2">
                  <MessageSquare className="w-4 h-4" />
                  Message Candidate
                </Button>
              </DialogFooter>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ApplicantTracker;
