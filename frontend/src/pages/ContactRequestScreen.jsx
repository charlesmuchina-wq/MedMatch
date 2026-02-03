import { useState, useEffect } from "react";
import { 
  Shield, Building2, MapPin, Briefcase, Mail, Phone, 
  Lock, Check, X, MessageSquare, Clock, ExternalLink,
  ChevronRight, Bell, User, Loader2, RefreshCw
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { useTranslation } from "@/utils/i18n";
import { toast } from "sonner";
import axios from "axios";

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * Contact Request Notification Screen
 * Allows candidates to review and respond to recruiter contact requests
 */
const ContactRequestScreen = ({ requests: propRequests, onRequestUpdate }) => {
  const { t } = useTranslation();
  const [requests, setRequests] = useState(propRequests || []);
  const [loading, setLoading] = useState(true);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [responding, setResponding] = useState(false);
  const [declineMessage, setDeclineMessage] = useState("");

  // Fetch contact requests on mount
  useEffect(() => {
    fetchContactRequests();
  }, []);

  const fetchContactRequests = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("medmatch-token");
      const response = await axios.get(`${API}/api/mutual-match/requests/received`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setRequests(response.data.requests || []);
    } catch (err) {
      console.error("Failed to fetch contact requests:", err);
      // If propRequests provided, use those as fallback
      if (propRequests && propRequests.length > 0) {
        setRequests(propRequests);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRespond = async (requestId, action) => {
    setResponding(true);
    try {
      const token = localStorage.getItem("medmatch-token");
      const response = await axios.post(
        `${API}/api/mutual-match/respond`,
        {
          request_id: requestId,
          action: action,
          message: action === "decline" ? declineMessage : undefined
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (action === "accept") {
        toast.success("Contact accepted! You can now chat with the recruiter.");
      } else {
        toast.success("Request declined. Your information remains private.");
      }

      setSelectedRequest(null);
      setDeclineMessage("");
      // Refresh the list
      fetchContactRequests();
      if (onRequestUpdate) onRequestUpdate();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to respond");
    } finally {
      setResponding(false);
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="p-6 max-w-2xl mx-auto">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-turquoise" />
        </div>
      </div>
    );
  }

  // Empty state
  if (!requests || requests.length === 0) {
    return (
      <div className="p-6 max-w-2xl mx-auto">
        <Card className="text-center p-8">
          <Bell className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-slate-700 dark:text-slate-300">
            No Contact Requests
          </h3>
          <p className="text-sm text-slate-500 mt-2">
            When recruiters want to contact you, their requests will appear here.
          </p>
          <Button 
            variant="outline" 
            className="mt-4"
            onClick={fetchContactRequests}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-3xl mx-auto" data-testid="contact-requests-screen">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900 dark:text-slate-100" style={{ fontFamily: 'IBM Plex Sans' }}>
            Contact Requests
          </h1>
          <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">
            Review and respond to recruiter requests. Your contact details are only shared when you accept.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={fetchContactRequests}>
          <RefreshCw className="w-4 h-4 mr-1" />
          Refresh
        </Button>
      </div>

      {/* Pending Requests */}
      <div className="space-y-4">
        {requests.filter(r => r.status === "pending").map((req) => (
          <ContactRequestCard
            key={req.id}
            request={req}
            onAccept={() => setSelectedRequest({ ...req, action: "accept" })}
            onDecline={() => setSelectedRequest({ ...req, action: "decline" })}
          />
        ))}

        {/* Past Requests */}
        {requests.filter(r => r.status !== "pending").length > 0 && (
          <>
            <h3 className="text-sm font-medium text-slate-500 mt-8 mb-3">Past Requests</h3>
            {requests.filter(r => r.status !== "pending").map((req) => (
              <ContactRequestCard
                key={req.id}
                request={req}
                isPast
              />
            ))}
          </>
        )}
      </div>

      {/* Response Dialog */}
      <Dialog open={!!selectedRequest} onOpenChange={(open) => !open && setSelectedRequest(null)}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {selectedRequest?.action === "accept" ? (
                <>
                  <Check className="w-5 h-5 text-emerald-500" />
                  Accept Contact Request
                </>
              ) : (
                <>
                  <X className="w-5 h-5 text-slate-500" />
                  Decline Request
                </>
              )}
            </DialogTitle>
          </DialogHeader>

          <div className="py-4">
            {selectedRequest?.action === "accept" ? (
              <div className="space-y-4">
                <div className="p-4 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg border border-emerald-200 dark:border-emerald-800">
                  <p className="text-sm text-emerald-800 dark:text-emerald-200">
                    <strong>By accepting:</strong>
                  </p>
                  <ul className="mt-2 space-y-1 text-sm text-emerald-700 dark:text-emerald-300">
                    <li className="flex items-center gap-2">
                      <Mail className="w-4 h-4" />
                      Your email will be shared with this recruiter
                    </li>
                    <li className="flex items-center gap-2">
                      <Phone className="w-4 h-4" />
                      Your phone number will be shared
                    </li>
                    <li className="flex items-center gap-2">
                      <MessageSquare className="w-4 h-4" />
                      You can chat securely in-app
                    </li>
                  </ul>
                </div>

                <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg text-xs text-slate-500">
                  <Clock className="w-3 h-3 inline mr-1" />
                  Data retention: Your information will be accessible for 60 days.
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  The recruiter will be notified anonymously. Your personal information will remain private.
                </p>
                <div>
                  <label className="text-sm font-medium">Reason (optional)</label>
                  <textarea
                    className="w-full mt-1.5 p-3 border rounded-lg resize-none"
                    rows={2}
                    placeholder="e.g., Not looking for new opportunities right now"
                    value={declineMessage}
                    onChange={(e) => setDeclineMessage(e.target.value)}
                  />
                </div>
              </div>
            )}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setSelectedRequest(null)} disabled={responding}>
              Cancel
            </Button>
            <Button
              onClick={() => handleRespond(selectedRequest?.id, selectedRequest?.action)}
              disabled={responding}
              className={selectedRequest?.action === "accept" ? "bg-emerald-500 hover:bg-emerald-600" : "bg-slate-500 hover:bg-slate-600"}
            >
              {responding ? "Processing..." : selectedRequest?.action === "accept" ? "Accept & Share Contact" : "Decline"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

/**
 * Individual Contact Request Card
 */
const ContactRequestCard = ({ request, onAccept, onDecline, isPast = false }) => {
  const statusColors = {
    pending: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
    accepted: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400",
    declined: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400",
    expired: "bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-500"
  };

  return (
    <Card className={`${isPast ? "opacity-70" : ""}`} data-testid={`contact-request-${request.id}`}>
      <CardContent className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-turquoise/10 flex items-center justify-center">
              <Building2 className="w-6 h-6 text-turquoise" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-900 dark:text-slate-100">
                {request.company_name}
              </h3>
              <p className="text-sm text-slate-500">
                {request.recruiter_name}
              </p>
            </div>
          </div>
          <Badge className={statusColors[request.status]}>
            {request.status.charAt(0).toUpperCase() + request.status.slice(1)}
          </Badge>
        </div>

        {/* Job Details */}
        <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg mb-3">
          <div className="flex items-center gap-2 mb-2">
            <Briefcase className="w-4 h-4 text-turquoise" />
            <span className="font-medium text-slate-900 dark:text-slate-100">
              {request.job_title || request.job_details?.title}
            </span>
          </div>
          {request.job_details && (
            <>
              {request.job_details.location && (
                <div className="flex items-center gap-2 text-sm text-slate-500">
                  <MapPin className="w-3 h-3" />
                  {request.job_details.location}
                </div>
              )}
              <p className="text-xs text-slate-500 mt-2 line-clamp-2">
                {request.job_details.description?.slice(0, 150)}...
              </p>
            </>
          )}
        </div>

        {/* Recruiter Message */}
        {request.message && (
          <div className="p-3 bg-turquoise/5 border border-turquoise/20 rounded-lg mb-3">
            <p className="text-sm text-slate-700 dark:text-slate-300 italic">
              "{request.message}"
            </p>
          </div>
        )}

        {/* Privacy Notice */}
        <div className="flex items-center gap-2 text-xs text-slate-400 mb-4">
          <Lock className="w-3 h-3" />
          Your contact details (email, phone) are hidden until you accept.
        </div>

        {/* Actions for pending requests */}
        {!isPast && request.status === "pending" && (
          <div className="flex gap-3 pt-3 border-t">
            <Button
              className="flex-1 bg-emerald-500 hover:bg-emerald-600"
              onClick={onAccept}
              data-testid={`accept-request-${request.id}`}
            >
              <Check className="w-4 h-4 mr-2" />
              Accept Contact & Start Chat
            </Button>
            <Button
              variant="outline"
              className="flex-1"
              onClick={onDecline}
              data-testid={`decline-request-${request.id}`}
            >
              <X className="w-4 h-4 mr-2" />
              Decline
            </Button>
          </div>
        )}

        {/* View job link */}
        {request.job_details?.url && (
          <div className="mt-3 pt-3 border-t">
            <a 
              href={request.job_details.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-turquoise hover:underline flex items-center gap-1"
            >
              View full job description
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        )}

        {/* Timestamp */}
        <div className="mt-2 text-xs text-slate-400">
          <Clock className="w-3 h-3 inline mr-1" />
          Received {new Date(request.created_at).toLocaleDateString()}
        </div>
      </CardContent>
    </Card>
  );
};

export default ContactRequestScreen;
