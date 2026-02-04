/**
 * My Reviews Section Component
 * Displays reviews received by a candidate with response capability
 */
import { useState, useEffect } from "react";
import { Star, MessageSquare, TrendingUp, RefreshCw, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import axios from "axios";
import EmployerReviewCard, { ReviewSummary } from "./EmployerReviewCard";

const API = process.env.REACT_APP_BACKEND_URL;

const MyReviewsSection = ({ userId }) => {
  const [loading, setLoading] = useState(true);
  const [reviewData, setReviewData] = useState(null);
  const [responseDialog, setResponseDialog] = useState({ open: false, review: null });
  const [responseText, setResponseText] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchMyReviews();
  }, [userId]);

  const fetchMyReviews = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("medmatch-token");
      const response = await axios.get(
        `${API}/api/reviews/my-reviews`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setReviewData(response.data);
    } catch (err) {
      console.error("Failed to fetch reviews:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRespond = (review) => {
    setResponseDialog({ open: true, review });
    setResponseText("");
  };

  const submitResponse = async () => {
    if (!responseText.trim()) {
      toast.error("Please write a response");
      return;
    }

    setSubmitting(true);
    try {
      const token = localStorage.getItem("medmatch-token");
      await axios.post(
        `${API}/api/reviews/respond/${responseDialog.review.id}`,
        {
          candidate_id: userId,
          response_text: responseText,
          is_public: true
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      toast.success("Response submitted successfully!");
      setResponseDialog({ open: false, review: null });
      fetchMyReviews(); // Refresh to show response
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to submit response");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <RefreshCw className="w-8 h-8 animate-spin text-slate-400 mx-auto mb-2" />
          <p className="text-slate-500">Loading reviews...</p>
        </CardContent>
      </Card>
    );
  }

  if (!reviewData || reviewData.total_reviews === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <Star className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100 mb-2">
            No Reviews Yet
          </h3>
          <p className="text-slate-500 text-sm">
            Reviews from employers will appear here once they&apos;re approved.
            Getting positive reviews can boost your Trust Score!
          </p>
        </CardContent>
      </Card>
    );
  }

  // Build summary object for ReviewSummary component
  const summaryData = {
    average_rating: reviewData.average_rating,
    total_reviews: reviewData.approved_reviews,
    would_hire_again_percentage: 0, // Would need to calculate from reviews
    rating_distribution: {},
    top_strengths: []
  };

  // Calculate rating distribution and strengths from reviews
  const strengthCounts = {};
  reviewData.reviews?.forEach(r => {
    // Rating distribution
    const rating = r.rating;
    summaryData.rating_distribution[rating] = (summaryData.rating_distribution[rating] || 0) + 1;
    
    // Strengths
    r.strengths?.forEach(s => {
      strengthCounts[s] = (strengthCounts[s] || 0) + 1;
    });
    
    // Would hire again
    if (r.would_hire_again) {
      summaryData.would_hire_again_percentage++;
    }
  });

  // Convert to percentage
  if (reviewData.reviews?.length > 0) {
    summaryData.would_hire_again_percentage = Math.round(
      (summaryData.would_hire_again_percentage / reviewData.reviews.length) * 100
    );
  }

  // Top strengths
  summaryData.top_strengths = Object.entries(strengthCounts)
    .map(([strength, count]) => ({ strength, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 5);

  return (
    <div className="space-y-6" data-testid="my-reviews-section">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100" style={{ fontFamily: 'IBM Plex Sans' }}>
            Employer Reviews
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            {reviewData.approved_reviews} approved review{reviewData.approved_reviews !== 1 ? 's' : ''}
            {reviewData.pending_count > 0 && (
              <span className="ml-2 text-amber-500">
                ({reviewData.pending_count} pending)
              </span>
            )}
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={fetchMyReviews}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Summary */}
      <ReviewSummary summary={summaryData} />

      {/* Impact on Trust Score */}
      <Card className="bg-gradient-to-r from-turquoise/5 to-emerald-50 dark:from-turquoise/10 dark:to-emerald-900/10 border-turquoise/20">
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <TrendingUp className="w-8 h-8 text-turquoise" />
            <div>
              <p className="font-medium text-slate-900 dark:text-slate-100">
                Reviews Boost Your Trust Score
              </p>
              <p className="text-xs text-slate-500">
                Each positive review (4+ stars) adds 10 points to your Trust Score, up to 50 points maximum
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Reviews List */}
      <div className="space-y-4">
        {reviewData.reviews?.map((review) => (
          <EmployerReviewCard
            key={review.id}
            review={review}
            showResponse={true}
            onRespond={handleRespond}
          />
        ))}
      </div>

      {/* Response Dialog */}
      <Dialog 
        open={responseDialog.open} 
        onOpenChange={(open) => setResponseDialog({ open, review: responseDialog.review })}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-turquoise" />
              Respond to Review
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4 py-4">
            {/* Original Review Preview */}
            {responseDialog.review && (
              <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <div className="flex">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <Star
                        key={star}
                        className={`w-4 h-4 ${
                          star <= responseDialog.review.rating
                            ? "fill-amber-400 text-amber-400"
                            : "fill-slate-200 text-slate-200"
                        }`}
                      />
                    ))}
                  </div>
                  <span className="text-sm text-slate-500">
                    by {responseDialog.review.recruiter_name || "Anonymous"}
                  </span>
                </div>
                <p className="text-sm text-slate-600 dark:text-slate-400 line-clamp-3">
                  &ldquo;{responseDialog.review.comment || "No comment provided"}&rdquo;
                </p>
              </div>
            )}

            {/* Response Input */}
            <div>
              <label className="text-sm font-medium text-slate-700 dark:text-slate-300 block mb-2">
                Your Response
              </label>
              <Textarea
                placeholder="Thank the reviewer, provide context, or address any feedback professionally..."
                value={responseText}
                onChange={(e) => setResponseText(e.target.value)}
                rows={4}
                className="resize-none"
              />
              <p className="text-xs text-slate-400 mt-1">
                Your response will be visible to recruiters viewing your profile
              </p>
            </div>
          </div>

          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => setResponseDialog({ open: false, review: null })}
            >
              Cancel
            </Button>
            <Button 
              onClick={submitResponse}
              disabled={submitting || !responseText.trim()}
              className="bg-turquoise hover:bg-turquoise/90"
            >
              {submitting ? (
                "Submitting..."
              ) : (
                <>
                  <Send className="w-4 h-4 mr-2" />
                  Post Response
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default MyReviewsSection;
