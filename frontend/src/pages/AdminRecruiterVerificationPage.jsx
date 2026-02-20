import { useState, useEffect } from "react";
import { useTranslation } from "@/utils/i18n";
import { 
  Shield, Check, X, Building2, Linkedin, Clock, 
  User, Mail, Phone, AlertTriangle, Search, Filter,
  ChevronRight, ExternalLink, BadgeCheck, XCircle
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import axios from "axios";

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * Admin Recruiter Verification Dashboard
 * Allows admins to review and approve/reject recruiter verification requests
 */
const AdminRecruiterVerificationPage = () => {
  const [requests, setRequests] = useState([]);
  const [recruiters, setRecruiters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTab, setActiveTab] = useState("pending");

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("medmatch-token");
      const headers = { Authorization: `Bearer ${token}` };

      const [requestsRes, recruitersRes] = await Promise.all([
        axios.get(`${API}/api/admin/recruiter-verifications`, { headers }),
        axios.get(`${API}/api/admin/recruiters`, { headers })
      ]);

      setRequests(requestsRes.data.requests || []);
      setRecruiters(recruitersRes.data.recruiters || []);
    } catch (err) {
      console.error("Failed to fetch data:", err);
      // Use mock data for demo
      setRequests([
        {
          id: "req-1",
          recruiter_id: "user-1",
          company_name: "City Medical Center",
          business_email: "hr@citymedical.com",
          job_title: "HR Manager",
          linkedin_profile: "https://linkedin.com/in/johndoe",
          status: "pending_review",
          submitted_at: new Date().toISOString()
        },
        {
          id: "req-2",
          recruiter_id: "user-2",
          company_name: "Regional Hospital",
          business_email: "recruiting@regionalhospital.org",
          job_title: "Talent Acquisition Lead",
          linkedin_profile: "https://linkedin.com/in/janesmith",
          status: "pending_review",
          submitted_at: new Date(Date.now() - 86400000).toISOString()
        }
      ]);
      setRecruiters([
        {
          user_id: "user-3",
          company_name: "Healthcare Plus",
          business_email: "jobs@healthcareplus.com",
          job_title: "Recruiter",
          verification_status: "verified",
          mfa_enabled: true
        }
      ]);
    }
    setLoading(false);
  };

  const handleVerification = async (requestId, action, notes = "") => {
    setProcessing(true);
    try {
      const token = localStorage.getItem("medmatch-token");
      await axios.post(
        `${API}/api/admin/recruiter-verifications/${requestId}/${action}`,
        { notes },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      toast.success(`Recruiter ${action === 'approve' ? 'approved' : 'rejected'} successfully`);
      setSelectedRequest(null);
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || `Failed to ${action} recruiter`);
    }
    setProcessing(false);
  };

  const pendingRequests = requests.filter(r => r.status === "pending_review" || r.status === "under_review");
  const verifiedRecruiters = recruiters.filter(r => r.verification_status === "verified");
  const rejectedRequests = requests.filter(r => r.status === "rejected");

  const filteredRequests = (list) => {
    if (!searchQuery) return list;
    return list.filter(r => 
      r.company_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.business_email?.toLowerCase().includes(searchQuery.toLowerCase())
    );
  };

  if (loading) {
    return (
      <div className="p-6 max-w-6xl mx-auto">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-slate-200 dark:bg-slate-700 rounded w-1/3" />
          <div className="h-32 bg-slate-200 dark:bg-slate-700 rounded" />
          <div className="h-32 bg-slate-200 dark:bg-slate-700 rounded" />
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-6xl mx-auto" data-testid="admin-recruiter-verification">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900 dark:text-slate-100" style={{ fontFamily: 'IBM Plex Sans' }}>
            Recruiter Verification
          </h1>
          <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">
            Review and approve recruiter verification requests
          </p>
        </div>

        {/* Stats */}
        <div className="flex gap-4">
          <div className="text-center px-4 py-2 bg-amber-50 dark:bg-amber-900/20 rounded-lg">
            <div className="text-2xl font-bold text-amber-600">{pendingRequests.length}</div>
            <div className="text-xs text-amber-600">Pending</div>
          </div>
          <div className="text-center px-4 py-2 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg">
            <div className="text-2xl font-bold text-emerald-600">{verifiedRecruiters.length}</div>
            <div className="text-xs text-emerald-600">Verified</div>
          </div>
          <div className="text-center px-4 py-2 bg-slate-50 dark:bg-slate-800 rounded-lg">
            <div className="text-2xl font-bold text-slate-600">{rejectedRequests.length}</div>
            <div className="text-xs text-slate-500">Rejected</div>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input
            placeholder="Search by company name or email..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="pending" onValueChange={setActiveTab}>
        <TabsList className="mb-6">
          <TabsTrigger value="pending" className="flex items-center gap-2">
            <Clock className="w-4 h-4" />
            Pending ({pendingRequests.length})
          </TabsTrigger>
          <TabsTrigger value="verified" className="flex items-center gap-2">
            <BadgeCheck className="w-4 h-4" />
            Verified ({verifiedRecruiters.length})
          </TabsTrigger>
          <TabsTrigger value="rejected" className="flex items-center gap-2">
            <XCircle className="w-4 h-4" />
            Rejected ({rejectedRequests.length})
          </TabsTrigger>
        </TabsList>

        {/* Pending Requests */}
        <TabsContent value="pending">
          <div className="space-y-4">
            {filteredRequests(pendingRequests).length === 0 ? (
              <Card className="p-8 text-center">
                <BadgeCheck className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                <p className="text-slate-500">No pending verification requests</p>
              </Card>
            ) : (
              filteredRequests(pendingRequests).map((req) => (
                <VerificationRequestCard
                  key={req.id}
                  request={req}
                  onReview={() => setSelectedRequest(req)}
                />
              ))
            )}
          </div>
        </TabsContent>

        {/* Verified Recruiters */}
        <TabsContent value="verified">
          <div className="space-y-4">
            {filteredRequests(verifiedRecruiters).length === 0 ? (
              <Card className="p-8 text-center">
                <Building2 className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                <p className="text-slate-500">No verified recruiters yet</p>
              </Card>
            ) : (
              filteredRequests(verifiedRecruiters).map((recruiter) => (
                <VerifiedRecruiterCard key={recruiter.user_id} recruiter={recruiter} />
              ))
            )}
          </div>
        </TabsContent>

        {/* Rejected */}
        <TabsContent value="rejected">
          <div className="space-y-4">
            {filteredRequests(rejectedRequests).length === 0 ? (
              <Card className="p-8 text-center">
                <XCircle className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                <p className="text-slate-500">No rejected requests</p>
              </Card>
            ) : (
              filteredRequests(rejectedRequests).map((req) => (
                <VerificationRequestCard key={req.id} request={req} isRejected />
              ))
            )}
          </div>
        </TabsContent>
      </Tabs>

      {/* Review Dialog */}
      <Dialog open={!!selectedRequest} onOpenChange={(open) => !open && setSelectedRequest(null)}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-turquoise" />
              Review Verification Request
            </DialogTitle>
          </DialogHeader>

          {selectedRequest && (
            <div className="space-y-4 py-4">
              {/* Company Info */}
              <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
                <h4 className="font-medium mb-3 flex items-center gap-2">
                  <Building2 className="w-4 h-4" />
                  Company Information
                </h4>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <span className="text-slate-500">Company</span>
                    <p className="font-medium">{selectedRequest.company_name}</p>
                  </div>
                  <div>
                    <span className="text-slate-500">Job Title</span>
                    <p className="font-medium">{selectedRequest.job_title}</p>
                  </div>
                  <div className="col-span-2">
                    <span className="text-slate-500">Business Email</span>
                    <p className="font-medium">{selectedRequest.business_email}</p>
                  </div>
                </div>
              </div>

              {/* LinkedIn */}
              {selectedRequest.linkedin_profile && (
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <h4 className="font-medium mb-2 flex items-center gap-2">
                    <Linkedin className="w-4 h-4 text-blue-600" />
                    LinkedIn Profile
                  </h4>
                  <a 
                    href={selectedRequest.linkedin_profile}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline text-sm flex items-center gap-1"
                  >
                    {selectedRequest.linkedin_profile}
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              )}

              {/* Verification Checklist */}
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium mb-3">Verification Checklist</h4>
                <ul className="space-y-2 text-sm">
                  {[
                    "Business email domain matches company",
                    "LinkedIn profile shows current employment",
                    "Company is legitimate healthcare organization",
                    "Job title indicates HR/recruiting function"
                  ].map((item, i) => (
                    <li key={i} className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
                      <input type="checkbox" className="rounded" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Submitted Date */}
              <div className="text-xs text-slate-400">
                <Clock className="w-3 h-3 inline mr-1" />
                Submitted: {new Date(selectedRequest.submitted_at).toLocaleString()}
              </div>
            </div>
          )}

          <DialogFooter className="flex gap-3">
            <Button
              variant="outline"
              onClick={() => handleVerification(selectedRequest?.id, 'reject')}
              disabled={processing}
              className="border-red-200 text-red-600 hover:bg-red-50"
            >
              <X className="w-4 h-4 mr-2" />
              Reject
            </Button>
            <Button
              onClick={() => handleVerification(selectedRequest?.id, 'approve')}
              disabled={processing}
              className="bg-emerald-500 hover:bg-emerald-600"
            >
              <Check className="w-4 h-4 mr-2" />
              {processing ? "Processing..." : "Approve"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

/**
 * Verification Request Card
 */
const VerificationRequestCard = ({ request, onReview, isRejected = false }) => {
  return (
    <Card className="hover:shadow-md transition-shadow" data-testid={`verification-request-${request.id}`}>
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-turquoise/10 flex items-center justify-center">
              <Building2 className="w-6 h-6 text-turquoise" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-900 dark:text-slate-100">
                {request.company_name}
              </h3>
              <p className="text-sm text-slate-500">{request.business_email}</p>
              <div className="flex items-center gap-2 mt-1">
                <Badge variant="outline" className="text-xs">
                  {request.job_title}
                </Badge>
                {request.linkedin_profile && (
                  <a 
                    href={request.linkedin_profile}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-500 hover:text-blue-600"
                  >
                    <Linkedin className="w-4 h-4" />
                  </a>
                )}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right text-xs text-slate-400">
              {new Date(request.submitted_at).toLocaleDateString()}
            </div>
            {!isRejected && onReview && (
              <Button onClick={onReview} size="sm" className="bg-turquoise hover:bg-turquoise/90">
                Review
                <ChevronRight className="w-4 h-4 ml-1" />
              </Button>
            )}
            {isRejected && (
              <Badge className="bg-red-100 text-red-600">Rejected</Badge>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

/**
 * Verified Recruiter Card
 */
const VerifiedRecruiterCard = ({ recruiter }) => {
  return (
    <Card data-testid={`verified-recruiter-${recruiter.user_id}`}>
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
              <BadgeCheck className="w-6 h-6 text-emerald-500" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-900 dark:text-slate-100">
                {recruiter.company_name}
              </h3>
              <p className="text-sm text-slate-500">{recruiter.business_email}</p>
              <Badge variant="outline" className="text-xs mt-1">
                {recruiter.job_title}
              </Badge>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {recruiter.mfa_enabled && (
              <Badge className="bg-emerald-100 text-emerald-600">
                <Shield className="w-3 h-3 mr-1" />
                MFA Enabled
              </Badge>
            )}
            <Badge className="bg-emerald-500 text-white">Verified</Badge>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default AdminRecruiterVerificationPage;
