/**
import { useTranslation } from "@/utils/i18n";
 * Admin Review Moderation Page
 * Allows admins to approve or reject pending employer reviews
 */
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Shield, Star, Check, X, AlertTriangle, RefreshCw,
  User, Building2, Calendar, MessageSquare, ChevronLeft,
  Eye, ThumbsUp, Flag, Filter, Search
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import axios from "axios";

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * Star Rating Display
 */
const StarRating = ({ rating }) => (
  <div className="flex items-center gap-0.5">
    {[1, 2, 3, 4, 5].map((star) => (
      <Star
        key={star}
        className={`w-4 h-4 ${
          star <= rating
            ? "fill-amber-400 text-amber-400"
            : "fill-slate-200 text-slate-200"
        }`}
      />
    ))}
    <span className="ml-2 text-sm font-medium">{rating}/5</span>
  </div>
);

/**
 * Review Card for Moderation
 */
const ReviewModerationCard = ({ review, onApprove, onReject, onViewDetails }) => {
  const reviewDate = review.created_at 
    ? new Date(review.created_at).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    : 'Unknown date';

  return (
    <Card className="overflow-hidden" data-testid={`review-mod-card-${review.id}`}>
      <CardContent className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
              <Building2 className="w-5 h-5 text-turquoise" />
            </div>
            <div>
              <p className="font-medium text-slate-900 dark:text-slate-100">
                {review.recruiter_name || "Anonymous Recruiter"}
              </p>
              <p className="text-xs text-slate-500">
                {review.recruiter_company || "Company not specified"}
              </p>
            </div>
          </div>
          <Badge variant="outline" className="bg-amber-50 text-amber-600 border-amber-200">
            Pending Review
          </Badge>
        </div>

        {/* Review Target */}
        <div className="flex items-center gap-2 mb-3 p-2 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
          <User className="w-4 h-4 text-slate-400" />
          <span className="text-sm text-slate-600 dark:text-slate-400">
            Review for: <strong>{review.candidate_name || review.candidate_id}</strong>
          </span>
          <Badge variant="outline" className="ml-auto text-xs capitalize">
            {review.review_type || 'general'}
          </Badge>
        </div>

        {/* Rating */}
        <div className="mb-3">
          <StarRating rating={review.rating} />
        </div>

        {/* Comment */}
        {review.comment && (
          <div className="mb-3">
            <p className="text-sm text-slate-600 dark:text-slate-400 line-clamp-3">
              &ldquo;{review.comment}&rdquo;
            </p>
          </div>
        )}

        {/* Strengths Preview */}
        {review.strengths?.length > 0 && (
          <div className="mb-3">
            <div className="flex flex-wrap gap-1">
              {review.strengths.slice(0, 3).map((s, i) => (
                <Badge key={i} variant="secondary" className="text-xs bg-emerald-50 text-emerald-700">
                  {s}
                </Badge>
              ))}
              {review.strengths.length > 3 && (
                <Badge variant="secondary" className="text-xs">
                  +{review.strengths.length - 3} more
                </Badge>
              )}
            </div>
          </div>
        )}

        {/* Metadata */}
        <div className="flex items-center gap-4 text-xs text-slate-400 mb-4">
          <span className="flex items-center gap-1">
            <Calendar className="w-3 h-3" />
            {reviewDate}
          </span>
          {review.would_hire_again && (
            <span className="flex items-center gap-1 text-emerald-500">
              <ThumbsUp className="w-3 h-3" />
              Would hire again
            </span>
          )}
          {review.is_anonymous && (
            <span className="flex items-center gap-1">
              <Eye className="w-3 h-3" />
              Anonymous
            </span>
          )}
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 pt-3 border-t">
          <Button
            size="sm"
            onClick={() => onApprove(review)}
            className="flex-1 bg-emerald-500 hover:bg-emerald-600"
            data-testid={`approve-review-${review.id}`}
          >
            <Check className="w-4 h-4 mr-1" />
            Approve
          </Button>
          <Button
            size="sm"
            variant="destructive"
            onClick={() => onReject(review)}
            className="flex-1"
            data-testid={`reject-review-${review.id}`}
          >
            <X className="w-4 h-4 mr-1" />
            Reject
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => onViewDetails(review)}
          >
            <Eye className="w-4 h-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

/**
 * Review Details Dialog
 */
const ReviewDetailsDialog = ({ review, isOpen, onClose }) => {
  if (!review) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-turquoise" />
            Review Details
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Reviewer Info */}
          <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
            <h4 className="text-sm font-medium text-slate-500 mb-2">Reviewer</h4>
            <p className="font-medium">{review.recruiter_name || "Anonymous"}</p>
            <p className="text-sm text-slate-500">{review.recruiter_company || "N/A"}</p>
            <p className="text-xs text-slate-400 mt-1">ID: {review.recruiter_id}</p>
          </div>

          {/* Candidate Info */}
          <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
            <h4 className="text-sm font-medium text-slate-500 mb-2">Candidate</h4>
            <p className="font-medium">{review.candidate_name || "N/A"}</p>
            <p className="text-xs text-slate-400">ID: {review.candidate_id}</p>
          </div>

          {/* Rating & Type */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h4 className="text-sm font-medium text-slate-500 mb-2">Rating</h4>
              <StarRating rating={review.rating} />
            </div>
            <div>
              <h4 className="text-sm font-medium text-slate-500 mb-2">Review Type</h4>
              <Badge className="capitalize">{review.review_type || 'general'}</Badge>
            </div>
          </div>

          {/* Full Comment */}
          <div>
            <h4 className="text-sm font-medium text-slate-500 mb-2">Comment</h4>
            <p className="text-sm text-slate-700 dark:text-slate-300 p-3 bg-white dark:bg-slate-900 rounded-lg border">
              {review.comment || "No comment provided"}
            </p>
          </div>

          {/* Detailed Scores */}
          {review.detailed_scores && (
            <div>
              <h4 className="text-sm font-medium text-slate-500 mb-2">Detailed Scores</h4>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(review.detailed_scores).map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between p-2 bg-slate-50 dark:bg-slate-800/50 rounded">
                    <span className="text-sm capitalize">{key.replace(/_/g, ' ')}</span>
                    <span className="font-medium">{value}/5</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Strengths */}
          {review.strengths?.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-slate-500 mb-2">Strengths</h4>
              <div className="flex flex-wrap gap-1">
                {review.strengths.map((s, i) => (
                  <Badge key={i} variant="secondary" className="bg-emerald-50 text-emerald-700">
                    {s}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Areas for Improvement */}
          {review.areas_for_improvement?.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-slate-500 mb-2">Areas for Improvement</h4>
              <div className="flex flex-wrap gap-1">
                {review.areas_for_improvement.map((a, i) => (
                  <Badge key={i} variant="secondary" className="bg-amber-50 text-amber-700">
                    {a}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Would Hire Again */}
          <div className="flex items-center gap-2">
            <h4 className="text-sm font-medium text-slate-500">Would Hire Again:</h4>
            <Badge className={review.would_hire_again ? "bg-emerald-100 text-emerald-700" : "bg-slate-100 text-slate-600"}>
              {review.would_hire_again ? "Yes" : review.would_hire_again === false ? "No" : "Not specified"}
            </Badge>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Close</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

/**
 * Reject Dialog with Reason
 */
const RejectDialog = ({ review, isOpen, onClose, onConfirm }) => {
  const [reason, setReason] = useState("");
  const [loading, setLoading] = useState(false);

  const handleReject = async () => {
    setLoading(true);
    await onConfirm(review, reason);
    setLoading(false);
    setReason("");
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-red-600">
            <AlertTriangle className="w-5 h-5" />
            Reject Review
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <p className="text-sm text-slate-600">
            Are you sure you want to reject this review? This action cannot be undone.
          </p>
          
          <div>
            <label className="text-sm font-medium text-slate-700 block mb-2">
              Rejection Reason (optional)
            </label>
            <Textarea
              placeholder={t("adminReviewModeration.rejectionReasonPlaceholder")}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              rows={3}
            />
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button 
            variant="destructive" 
            onClick={handleReject}
            disabled={loading}
          >
            {loading ? "Rejecting..." : "Reject Review"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

/**
 * Main Admin Review Moderation Page
 */
const AdminReviewModerationPage = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [pendingReviews, setPendingReviews] = useState([]);
  const [approvedCount, setApprovedCount] = useState(0);
  const [rejectedCount, setRejectedCount] = useState(0);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedReview, setSelectedReview] = useState(null);
  const [detailsDialog, setDetailsDialog] = useState(false);
  const [rejectDialog, setRejectDialog] = useState({ open: false, review: null });
  const [activeTab, setActiveTab] = useState("pending");

  useEffect(() => {
    fetchPendingReviews();
    fetchStats();
  }, []);

  const fetchPendingReviews = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("medmatch-token");
      const response = await axios.get(`${API}/api/reviews/admin/pending`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPendingReviews(response.data.pending_reviews || []);
    } catch (err) {
      if (err.response?.status === 403) {
        toast.error("Admin access required");
        navigate("/dashboard");
      } else {
        toast.error("Failed to fetch pending reviews");
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem("medmatch-token");
      const response = await axios.get(`${API}/api/reviews/admin/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setApprovedCount(response.data.approved_count || 0);
      setRejectedCount(response.data.rejected_count || 0);
    } catch (err) {
      // Stats are optional
    }
  };

  const handleApprove = async (review) => {
    try {
      const token = localStorage.getItem("medmatch-token");
      await axios.post(
        `${API}/api/reviews/admin/approve/${review.id}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      toast.success("Review approved successfully");
      setPendingReviews(prev => prev.filter(r => r.id !== review.id));
      setApprovedCount(prev => prev + 1);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to approve review");
    }
  };

  const handleReject = async (review, reason) => {
    try {
      const token = localStorage.getItem("medmatch-token");
      await axios.post(
        `${API}/api/reviews/admin/reject/${review.id}`,
        { reason },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      toast.success("Review rejected");
      setPendingReviews(prev => prev.filter(r => r.id !== review.id));
      setRejectedCount(prev => prev + 1);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to reject review");
    }
  };

  const filteredReviews = pendingReviews.filter(review => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      review.recruiter_name?.toLowerCase().includes(query) ||
      review.candidate_name?.toLowerCase().includes(query) ||
      review.comment?.toLowerCase().includes(query) ||
      review.recruiter_company?.toLowerCase().includes(query)
    );
  });

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900" data-testid="admin-review-moderation">
      {/* Header */}
      <div className="bg-white dark:bg-slate-800 border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center gap-4 mb-4">
            <Button variant="ghost" size="sm" onClick={() => navigate("/admin")}>
              <ChevronLeft className="w-4 h-4 mr-1" />
              Back to Admin
            </Button>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-3">
                <Shield className="w-7 h-7 text-turquoise" />
                Review Moderation
              </h1>
              <p className="text-slate-500 mt-1">
                Approve or reject employer reviews before they appear on candidate profiles
              </p>
            </div>
            <Button onClick={fetchPendingReviews} variant="outline">
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-3xl font-bold text-amber-500">{pendingReviews.length}</p>
              <p className="text-sm text-slate-500">Pending</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-3xl font-bold text-emerald-500">{approvedCount}</p>
              <p className="text-sm text-slate-500">Approved (All Time)</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-3xl font-bold text-red-500">{rejectedCount}</p>
              <p className="text-sm text-slate-500">Rejected (All Time)</p>
            </CardContent>
          </Card>
        </div>

        {/* Search */}
        <div className="mb-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <Input
              placeholder={t("adminReviewModeration.searchPlaceholder")}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        {/* Reviews Grid */}
        {loading ? (
          <div className="text-center py-12">
            <RefreshCw className="w-8 h-8 animate-spin text-turquoise mx-auto mb-4" />
            <p className="text-slate-500">Loading pending reviews...</p>
          </div>
        ) : filteredReviews.length === 0 ? (
          <Card>
            <CardContent className="p-12 text-center">
              <Check className="w-16 h-16 text-emerald-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-2">
                All Caught Up!
              </h3>
              <p className="text-slate-500">
                {searchQuery 
                  ? "No reviews match your search criteria." 
                  : "No pending reviews to moderate. Great job!"}
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredReviews.map((review) => (
              <ReviewModerationCard
                key={review.id}
                review={review}
                onApprove={handleApprove}
                onReject={(r) => setRejectDialog({ open: true, review: r })}
                onViewDetails={(r) => {
                  setSelectedReview(r);
                  setDetailsDialog(true);
                }}
              />
            ))}
          </div>
        )}
      </div>

      {/* Details Dialog */}
      <ReviewDetailsDialog
        review={selectedReview}
        isOpen={detailsDialog}
        onClose={() => setDetailsDialog(false)}
      />

      {/* Reject Dialog */}
      <RejectDialog
        review={rejectDialog.review}
        isOpen={rejectDialog.open}
        onClose={() => setRejectDialog({ open: false, review: null })}
        onConfirm={handleReject}
      />
    </div>
  );
};

export default AdminReviewModerationPage;
