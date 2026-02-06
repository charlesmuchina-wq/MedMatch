/**
 * ATS Management Page
 * Recruiters can create application links, view invitations, and manage ATS settings
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { useTheme } from '@/App';
import { useTranslation } from '@/utils/i18n';
import { apiClient } from '@/utils/apiClient';
import {
  Link2, Plus, Copy, Trash2, Mail, Send, Users, BarChart3,
  Calendar, Loader2, ExternalLink, Eye, RefreshCw, CheckCircle,
  Clock, AlertCircle, ChevronRight
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';

export default function ATSManagementPage() {
  const navigate = useNavigate();
  const { isDark } = useTheme();
  const { t } = useTranslation();
  
  const [loading, setLoading] = useState(true);
  const [links, setLinks] = useState([]);
  const [invitations, setInvitations] = useState([]);
  const [stats, setStats] = useState(null);
  const [jobs, setJobs] = useState([]);
  
  // Create link dialog
  const [showCreateLink, setShowCreateLink] = useState(false);
  const [creatingLink, setCreatingLink] = useState(false);
  const [newLink, setNewLink] = useState({
    job_id: '',
    expires_in_days: 30,
    max_applications: '',
    require_resume: true
  });
  
  // Invite dialog
  const [showInviteDialog, setShowInviteDialog] = useState(false);
  const [sendingInvite, setSendingInvite] = useState(false);
  const [inviteData, setInviteData] = useState({
    job_id: '',
    candidate_email: '',
    candidate_name: '',
    personal_message: ''
  });

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [linksRes, statsRes, jobsRes, invitationsRes] = await Promise.all([
        apiClient.get('/api/ats/links'),
        apiClient.get('/api/ats/stats'),
        apiClient.get('/api/recruiter/jobs'),
        apiClient.get('/api/ats/invitations')
      ]);
      
      setLinks(linksRes.data.links || []);
      setStats(statsRes.data);
      setJobs(jobsRes.data.jobs || []);
      setInvitations(invitationsRes.data.invitations || []);
    } catch (err) {
      toast.error('Failed to load ATS data');
      console.error(err);
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const createApplicationLink = async () => {
    if (!newLink.job_id) {
      toast.error('Please select a job');
      return;
    }
    
    setCreatingLink(true);
    try {
      const response = await apiClient.post('/api/ats/links', {
        job_id: newLink.job_id,
        expires_in_days: newLink.expires_in_days,
        max_applications: newLink.max_applications ? parseInt(newLink.max_applications) : null,
        require_resume: newLink.require_resume
      });
      
      toast.success('Application link created!');
      navigator.clipboard.writeText(response.data.application_url);
      toast.info('Link copied to clipboard');
      
      setShowCreateLink(false);
      setNewLink({ job_id: '', expires_in_days: 30, max_applications: '', require_resume: true });
      loadData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create link');
    }
    setCreatingLink(false);
  };

  const deactivateLink = async (linkId) => {
    try {
      await apiClient.delete(`/api/ats/links/${linkId}`);
      toast.success('Link deactivated');
      loadData();
    } catch (err) {
      toast.error('Failed to deactivate link');
    }
  };

  const copyLink = (url) => {
    navigator.clipboard.writeText(url);
    toast.success('Link copied to clipboard!');
  };

  const sendInvitation = async () => {
    if (!inviteData.job_id || !inviteData.candidate_email) {
      toast.error('Please fill in required fields');
      return;
    }
    
    setSendingInvite(true);
    try {
      await apiClient.post(`/api/ats/invite?job_id=${inviteData.job_id}`, {
        candidate_email: inviteData.candidate_email,
        candidate_name: inviteData.candidate_name,
        personal_message: inviteData.personal_message
      });
      
      toast.success('Invitation sent!');
      setShowInviteDialog(false);
      setInviteData({ job_id: '', candidate_email: '', candidate_name: '', personal_message: '' });
      loadData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to send invitation');
    }
    setSendingInvite(false);
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 animate-spin text-turquoise" />
      </div>
    );
  }

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-7xl mx-auto animate-fade-in" data-testid="ats-management">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl md:text-3xl font-semibold text-slate-900 dark:text-slate-100">
          Applicant Tracking System
        </h1>
        <p className="text-slate-500 dark:text-slate-400 mt-1">
          Manage application links, track candidates, and send invitations
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-900/30">
                <Users className="h-5 w-5 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats?.total_applications || 0}</p>
                <p className="text-xs text-muted-foreground">Total Applications</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-green-100 dark:bg-green-900/30">
                <Clock className="h-5 w-5 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats?.recent_applications || 0}</p>
                <p className="text-xs text-muted-foreground">This Week</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-purple-100 dark:bg-purple-900/30">
                <Link2 className="h-5 w-5 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats?.active_links || 0}</p>
                <p className="text-xs text-muted-foreground">Active Links</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-amber-100 dark:bg-amber-900/30">
                <Mail className="h-5 w-5 text-amber-600 dark:text-amber-400" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats?.invitations_sent || 0}</p>
                <p className="text-xs text-muted-foreground">Invitations Sent</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="links" className="space-y-6">
        <TabsList>
          <TabsTrigger value="links" className="gap-2">
            <Link2 className="h-4 w-4" />
            Application Links
          </TabsTrigger>
          <TabsTrigger value="invitations" className="gap-2">
            <Mail className="h-4 w-4" />
            Invitations
          </TabsTrigger>
          <TabsTrigger value="status" className="gap-2">
            <BarChart3 className="h-4 w-4" />
            Status Breakdown
          </TabsTrigger>
        </TabsList>

        {/* Application Links Tab */}
        <TabsContent value="links" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-semibold">Shareable Application Links</h2>
            <Button onClick={() => setShowCreateLink(true)} className="gap-2">
              <Plus className="h-4 w-4" />
              Create Link
            </Button>
          </div>

          {links.length > 0 ? (
            <div className="space-y-3">
              {links.map((link) => (
                <Card key={link.id} className={!link.active ? 'opacity-60' : ''}>
                  <CardContent className="p-4">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-semibold">{link.job_title}</h3>
                          {link.active ? (
                            <Badge className="bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">
                              Active
                            </Badge>
                          ) : (
                            <Badge variant="secondary">Inactive</Badge>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground">{link.company}</p>
                        <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <Eye className="h-3 w-3" />
                            {link.views || 0} views
                          </span>
                          <span className="flex items-center gap-1">
                            <Users className="h-3 w-3" />
                            {link.current_applications || 0} applications
                          </span>
                          {link.expires_at && (
                            <span className="flex items-center gap-1">
                              <Calendar className="h-3 w-3" />
                              Expires {formatDate(link.expires_at)}
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => copyLink(`${window.location.origin}/apply/${link.token}`)}
                          className="gap-1"
                        >
                          <Copy className="h-3 w-3" />
                          Copy
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => window.open(`/apply/${link.token}`, '_blank')}
                          className="gap-1"
                        >
                          <ExternalLink className="h-3 w-3" />
                          Preview
                        </Button>
                        {link.active && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => deactivateLink(link.id)}
                            className="text-red-500 hover:text-red-600 hover:bg-red-50"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="py-12 text-center">
                <Link2 className="h-12 w-12 mx-auto text-slate-300 mb-4" />
                <h3 className="text-lg font-medium">No Application Links Yet</h3>
                <p className="text-sm text-muted-foreground mt-1 mb-4">
                  Create shareable links to invite candidates to apply
                </p>
                <Button onClick={() => setShowCreateLink(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Create Your First Link
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Invitations Tab */}
        <TabsContent value="invitations" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-semibold">Candidate Invitations</h2>
            <Button onClick={() => setShowInviteDialog(true)} className="gap-2">
              <Send className="h-4 w-4" />
              Send Invitation
            </Button>
          </div>

          {invitations.length > 0 ? (
            <div className="space-y-3">
              {invitations.map((inv) => (
                <Card key={inv.id}>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-medium">{inv.candidate_name || inv.candidate_email}</h3>
                          <Badge variant="outline" className="text-xs">
                            {inv.status}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">{inv.candidate_email}</p>
                        <p className="text-xs text-muted-foreground mt-1">
                          Sent {formatDate(inv.sent_at)}
                        </p>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => window.open(inv.application_url, '_blank')}
                      >
                        <ExternalLink className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="py-12 text-center">
                <Mail className="h-12 w-12 mx-auto text-slate-300 mb-4" />
                <h3 className="text-lg font-medium">No Invitations Sent</h3>
                <p className="text-sm text-muted-foreground mt-1 mb-4">
                  Send personalized invitations to candidates
                </p>
                <Button onClick={() => setShowInviteDialog(true)}>
                  <Send className="h-4 w-4 mr-2" />
                  Send First Invitation
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Status Breakdown Tab */}
        <TabsContent value="status" className="space-y-4">
          <h2 className="text-lg font-semibold">Applications by Status</h2>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {stats?.available_statuses && Object.entries(stats.available_statuses).map(([status, config]) => (
              <Card key={status}>
                <CardContent className="p-4 text-center">
                  <div className="text-3xl mb-2">{config.emoji}</div>
                  <p className="font-medium">{config.label}</p>
                  <p className="text-2xl font-bold text-turquoise">
                    {stats.by_status?.[status] || 0}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>

      {/* Create Link Dialog */}
      <Dialog open={showCreateLink} onOpenChange={setShowCreateLink}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create Application Link</DialogTitle>
            <DialogDescription>
              Generate a shareable link for candidates to apply
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div>
              <Label>Select Job *</Label>
              <Select
                value={newLink.job_id}
                onValueChange={(v) => setNewLink({ ...newLink, job_id: v })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a job posting" />
                </SelectTrigger>
                <SelectContent>
                  {jobs.map((job) => (
                    <SelectItem key={job.id} value={job.id}>
                      {job.title} - {job.company}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Expires In (Days)</Label>
                <Input
                  type="number"
                  value={newLink.expires_in_days}
                  onChange={(e) => setNewLink({ ...newLink, expires_in_days: parseInt(e.target.value) || 30 })}
                />
              </div>
              <div>
                <Label>Max Applications</Label>
                <Input
                  type="number"
                  placeholder="Unlimited"
                  value={newLink.max_applications}
                  onChange={(e) => setNewLink({ ...newLink, max_applications: e.target.value })}
                />
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <Label>Require Resume</Label>
              <Switch
                checked={newLink.require_resume}
                onCheckedChange={(v) => setNewLink({ ...newLink, require_resume: v })}
              />
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCreateLink(false)}>
              Cancel
            </Button>
            <Button onClick={createApplicationLink} disabled={creatingLink}>
              {creatingLink ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  Creating...
                </>
              ) : (
                <>
                  <Link2 className="h-4 w-4 mr-2" />
                  Create Link
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Send Invitation Dialog */}
      <Dialog open={showInviteDialog} onOpenChange={setShowInviteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Invite Candidate to Apply</DialogTitle>
            <DialogDescription>
              Send a personalized invitation email with application link
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div>
              <Label>Select Job *</Label>
              <Select
                value={inviteData.job_id}
                onValueChange={(v) => setInviteData({ ...inviteData, job_id: v })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a job posting" />
                </SelectTrigger>
                <SelectContent>
                  {jobs.map((job) => (
                    <SelectItem key={job.id} value={job.id}>
                      {job.title} - {job.company}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label>Candidate Email *</Label>
              <Input
                type="email"
                placeholder="candidate@example.com"
                value={inviteData.candidate_email}
                onChange={(e) => setInviteData({ ...inviteData, candidate_email: e.target.value })}
              />
            </div>
            
            <div>
              <Label>Candidate Name</Label>
              <Input
                placeholder="John Doe"
                value={inviteData.candidate_name}
                onChange={(e) => setInviteData({ ...inviteData, candidate_name: e.target.value })}
              />
            </div>
            
            <div>
              <Label>Personal Message</Label>
              <Textarea
                placeholder="Add a personal note to your invitation..."
                rows={3}
                value={inviteData.personal_message}
                onChange={(e) => setInviteData({ ...inviteData, personal_message: e.target.value })}
              />
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowInviteDialog(false)}>
              Cancel
            </Button>
            <Button onClick={sendInvitation} disabled={sendingInvite}>
              {sendingInvite ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  Sending...
                </>
              ) : (
                <>
                  <Send className="h-4 w-4 mr-2" />
                  Send Invitation
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
