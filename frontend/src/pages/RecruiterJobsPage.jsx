import { useState, useEffect } from "react";
import { useTranslation } from "@/utils/i18n";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import { useTheme } from "@/App";
import { 
  Briefcase, Plus, Trash2, Edit3, MapPin, Clock, DollarSign,
  Loader2, Building2, FileText, Tag, Globe, CheckCircle2, X,
  Users, Eye, Calendar
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";

const API = process.env.REACT_APP_BACKEND_URL;

const RecruiterJobsPage = ({ user }) => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { isDark } = useTheme();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showPostDialog, setShowPostDialog] = useState(false);
  const [posting, setPosting] = useState(false);
  const [editingJob, setEditingJob] = useState(null);
  
  // Form state
  const [formData, setFormData] = useState({
    title: "",
    company: "",
    location: "",
    description: "",
    salary: "",
    url: "",
    tags: ""
  });

  useEffect(() => {
    // Check if user is a recruiter or admin
    if (user?.role !== "recruiter" && !user?.is_admin) {
      toast.error("Only recruiters can access this page");
      navigate("/");
      return;
    }
    fetchJobs();
  }, [user, navigate]);

  const fetchJobs = async () => {
    try {
      const response = await axios.get(`${API}/api/recruiter/jobs`, {
        withCredentials: true
      });
      // API returns {jobs: [...]} so extract the jobs array
      setJobs(response.data?.jobs || response.data || []);
    } catch (e) {
      console.error("Failed to fetch jobs");
    }
    setLoading(false);
  };

  const resetForm = () => {
    setFormData({
      title: "",
      company: "",
      location: "",
      description: "",
      salary: "",
      url: "",
      tags: ""
    });
    setEditingJob(null);
  };

  const handleOpenPostDialog = (job = null) => {
    if (job) {
      setEditingJob(job);
      setFormData({
        title: job.title || "",
        company: job.company || "",
        location: job.location || "",
        description: job.description || "",
        salary: job.salary || "",
        url: job.url || "",
        tags: job.tags?.join(", ") || ""
      });
    } else {
      resetForm();
    }
    setShowPostDialog(true);
  };

  const handleSubmit = async () => {
    if (!formData.title || !formData.company || !formData.location || !formData.description) {
      toast.error("Please fill in all required fields");
      return;
    }

    setPosting(true);
    try {
      const payload = {
        ...formData,
        tags: formData.tags ? formData.tags.split(",").map(t => t.trim()).filter(Boolean) : []
      };

      if (editingJob) {
        await axios.put(`${API}/api/recruiter/jobs/${editingJob.id}`, payload, {
          withCredentials: true
        });
        toast.success("Job updated successfully");
      } else {
        await axios.post(`${API}/api/recruiter/jobs`, payload, {
          withCredentials: true
        });
        toast.success("Job posted successfully!");
      }
      
      setShowPostDialog(false);
      resetForm();
      fetchJobs();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Failed to post job");
    }
    setPosting(false);
  };

  const handleDelete = async (jobId) => {
    if (!window.confirm("Are you sure you want to delete this job posting?")) return;
    
    try {
      await axios.delete(`${API}/api/recruiter/jobs/${jobId}`, {
        withCredentials: true
      });
      toast.success("Job deleted");
      fetchJobs();
    } catch (e) {
      toast.error("Failed to delete job");
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "";
    return new Date(dateStr).toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-turquoise" />
      </div>
    );
  }

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-6xl mx-auto animate-fade-in" data-testid="recruiter-jobs-page">
      {/* Header */}
      <div className="flex items-center justify-between mb-8 flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-semibold text-slate-900 dark:text-slate-100 tracking-tight" style={{ fontFamily: 'IBM Plex Sans' }}>
            Job Postings
          </h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">
            Manage your job listings and reach qualified candidates
          </p>
        </div>
        <Button 
          onClick={() => handleOpenPostDialog()}
          className="bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700"
          data-testid="post-job-btn"
        >
          <Plus className="w-4 h-4 mr-2" /> Post New Job
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[
          { label: "Active Jobs", value: jobs.filter(j => j.status === "active").length, icon: Briefcase, color: "text-emerald-500" },
          { label: "Total Posted", value: jobs.length, icon: FileText, color: "text-blue-500" },
          { label: "This Month", value: jobs.filter(j => {
            const posted = new Date(j.posted_at);
            const now = new Date();
            return posted.getMonth() === now.getMonth() && posted.getFullYear() === now.getFullYear();
          }).length, icon: Calendar, color: "text-amber-500" },
          { label: "Views", value: jobs.reduce((sum, j) => sum + (j.views || 0), 0), icon: Eye, color: "text-violet-500" }
        ].map(({ label, value, icon: Icon, color }) => (
          <Card key={label}>
            <CardContent className="p-4 flex items-center gap-3">
              <div className={`w-10 h-10 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center ${color}`}>
                <Icon className="w-5 h-5" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">{value}</p>
                <p className="text-xs text-slate-500 dark:text-slate-400">{label}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Job Listings */}
      {jobs.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <div className="w-16 h-16 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4">
              <Briefcase className="w-8 h-8 text-slate-400" />
            </div>
            <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100 mb-2">No jobs posted yet</h3>
            <p className="text-slate-500 dark:text-slate-400 mb-6">
              Start posting jobs to find qualified candidates
            </p>
            <Button onClick={() => handleOpenPostDialog()}>
              <Plus className="w-4 h-4 mr-2" /> Post Your First Job
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {jobs.map((job) => (
            <Card key={job.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-semibold text-lg text-slate-900 dark:text-slate-100" style={{ fontFamily: 'IBM Plex Sans' }}>
                        {job.title}
                      </h3>
                      <Badge className={job.status === "active" ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400" : "bg-slate-100 text-slate-600"}>
                        {job.status || "active"}
                      </Badge>
                    </div>
                    
                    <div className="flex flex-wrap items-center gap-4 text-sm text-slate-500 dark:text-slate-400 mb-3">
                      <span className="flex items-center gap-1">
                        <Building2 className="w-4 h-4" /> {job.company}
                      </span>
                      <span className="flex items-center gap-1">
                        <MapPin className="w-4 h-4" /> {job.location}
                      </span>
                      {job.salary && (
                        <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400">
                          <DollarSign className="w-4 h-4" /> {job.salary}
                        </span>
                      )}
                      <span className="flex items-center gap-1">
                        <Clock className="w-4 h-4" /> {formatDate(job.posted_at)}
                      </span>
                      <span className="flex items-center gap-1 text-violet-600 dark:text-violet-400 font-medium">
                        <Users className="w-4 h-4" /> {job.applicant_count || 0} applicants
                      </span>
                    </div>

                    <p className="text-sm text-slate-600 dark:text-slate-400 line-clamp-2 mb-3">
                      {job.description}
                    </p>

                    {job.tags?.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {job.tags.slice(0, 5).map((tag, i) => (
                          <Badge key={i} variant="outline" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className="flex flex-col items-end gap-2">
                    <Button
                      size="sm"
                      onClick={() => navigate(`/recruiter/jobs/${job.id}/applicants`)}
                      className="bg-gradient-to-r from-violet-500 to-purple-600"
                      data-testid={`view-applicants-${job.id}`}
                    >
                      <Users className="w-4 h-4 mr-1" />
                      View Applicants
                    </Button>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleOpenPostDialog(job)}
                      >
                        <Edit3 className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDelete(job.id)}
                        className="text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Post/Edit Job Dialog */}
      <Dialog open={showPostDialog} onOpenChange={setShowPostDialog}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Briefcase className="w-5 h-5 text-turquoise" />
              {editingJob ? "Edit Job Posting" : "Post New Job"}
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="title">Job Title *</Label>
                <Input
                  id="title"
                  placeholder="e.g., Senior Quality Engineer"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  data-testid="job-title-input"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="company">Company *</Label>
                <Input
                  id="company"
                  placeholder="Your company name"
                  value={formData.company}
                  onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                  data-testid="job-company-input"
                />
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="location">Location *</Label>
                <Input
                  id="location"
                  placeholder="e.g., Remote, USA"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  data-testid="job-location-input"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="salary">Salary Range</Label>
                <Input
                  id="salary"
                  placeholder="e.g., $80,000 - $120,000"
                  value={formData.salary}
                  onChange={(e) => setFormData({ ...formData, salary: e.target.value })}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Job Description *</Label>
              <Textarea
                id="description"
                placeholder="Describe the role, responsibilities, and requirements..."
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="min-h-[150px]"
                data-testid="job-description-input"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="url">Application URL</Label>
              <Input
                id="url"
                placeholder="https://your-company.com/careers/apply"
                value={formData.url}
                onChange={(e) => setFormData({ ...formData, url: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="tags">Tags (comma separated)</Label>
              <Input
                id="tags"
                placeholder="e.g., Remote, Full-time, Quality, Medical Device"
                value={formData.tags}
                onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowPostDialog(false)}>
              Cancel
            </Button>
            <Button 
              onClick={handleSubmit} 
              disabled={posting}
              className="bg-gradient-to-r from-violet-500 to-purple-600"
            >
              {posting ? (
                <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Posting...</>
              ) : (
                <><CheckCircle2 className="w-4 h-4 mr-2" /> {editingJob ? "Update Job" : "Post Job"}</>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default RecruiterJobsPage;
