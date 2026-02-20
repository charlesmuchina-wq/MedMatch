/**
import { useTranslation } from "@/utils/i18n";
 * Employer Review Card Component
 * Displays employer reviews for candidates
 */
import { useState } from "react";
import { Star, ThumbsUp, MessageSquare, User, Building2, Calendar, Shield } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

/**
 * Star Rating Display
 */
const StarRating = ({ rating, size = "md" }) => {
  const sizeClass = size === "sm" ? "w-3 h-3" : size === "lg" ? "w-5 h-5" : "w-4 h-4";
  
  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((star) => (
        <Star
          key={star}
          className={`${sizeClass} ${
            star <= rating 
              ? "fill-amber-400 text-amber-400" 
              : "fill-slate-200 text-slate-200 dark:fill-slate-600 dark:text-slate-600"
          }`}
        />
      ))}
    </div>
  );
};

/**
 * Score Breakdown Bar
 */
const ScoreBar = ({ label, score, maxScore = 5 }) => {
  if (!score) return null;
  const percentage = (score / maxScore) * 100;
  
  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-slate-500 w-24">{label}</span>
      <div className="flex-1 h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
        <div 
          className="h-full bg-turquoise rounded-full transition-all"
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className="text-xs font-medium text-slate-600 dark:text-slate-400 w-4">{score}</span>
    </div>
  );
};

/**
 * Employer Review Card
 */
const EmployerReviewCard = ({ review, showResponse = true, onRespond }) => {
  const [showFullComment, setShowFullComment] = useState(false);
  
  const reviewDate = review.created_at ? new Date(review.created_at).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  }) : '';

  return (
    <Card className="overflow-hidden" data-testid={`review-card-${review.id}`}>
      <CardContent className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            {/* Reviewer Info */}
            <div className="w-10 h-10 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
              {review.is_anonymous ? (
                <User className="w-5 h-5 text-slate-400" />
              ) : (
                <Building2 className="w-5 h-5 text-turquoise" />
              )}
            </div>
            <div>
              <p className="font-medium text-slate-900 dark:text-slate-100">
                {review.recruiter_name || "Anonymous Employer"}
              </p>
              {review.recruiter_company && !review.is_anonymous && (
                <p className="text-xs text-slate-500">{review.recruiter_company}</p>
              )}
            </div>
          </div>

          {/* Rating & Date */}
          <div className="text-right">
            <StarRating rating={review.rating} />
            <p className="text-xs text-slate-400 mt-1 flex items-center justify-end gap-1">
              <Calendar className="w-3 h-3" />
              {reviewDate}
            </p>
          </div>
        </div>

        {/* Review Type Badge */}
        <div className="flex items-center gap-2 mb-3">
          <Badge variant="outline" className="text-xs capitalize">
            {review.review_type || 'general'} review
          </Badge>
          {review.would_hire_again && (
            <Badge className="bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 text-xs">
              <ThumbsUp className="w-3 h-3 mr-1" />
              Would hire again
            </Badge>
          )}
          {review.status === 'approved' && (
            <Badge variant="outline" className="text-xs text-green-600 border-green-200">
              <Shield className="w-3 h-3 mr-1" />
              Verified
            </Badge>
          )}
        </div>

        {/* Comment */}
        {review.comment && (
          <div className="mb-3">
            <p className={`text-sm text-slate-600 dark:text-slate-400 ${!showFullComment && 'line-clamp-3'}`}>
              &ldquo;{review.comment}&rdquo;
            </p>
            {review.comment.length > 200 && (
              <button 
                onClick={() => setShowFullComment(!showFullComment)}
                className="text-xs text-turquoise hover:underline mt-1"
              >
                {showFullComment ? 'Show less' : 'Read more'}
              </button>
            )}
          </div>
        )}

        {/* Strengths */}
        {review.strengths?.length > 0 && (
          <div className="mb-3">
            <p className="text-xs font-medium text-slate-500 mb-1">Strengths</p>
            <div className="flex flex-wrap gap-1">
              {review.strengths.map((strength, idx) => (
                <Badge 
                  key={idx} 
                  variant="secondary" 
                  className="text-xs bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-400"
                >
                  {strength}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Areas for Improvement */}
        {review.areas_for_improvement?.length > 0 && (
          <div className="mb-3">
            <p className="text-xs font-medium text-slate-500 mb-1">Areas for Growth</p>
            <div className="flex flex-wrap gap-1">
              {review.areas_for_improvement.map((area, idx) => (
                <Badge 
                  key={idx} 
                  variant="secondary" 
                  className="text-xs bg-amber-50 text-amber-700 dark:bg-amber-900/20 dark:text-amber-400"
                >
                  {area}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Detailed Scores */}
        {review.detailed_scores && (
          <div className="pt-3 border-t space-y-2">
            <p className="text-xs font-medium text-slate-500 mb-2">Detailed Scores</p>
            <ScoreBar label="Professionalism" score={review.detailed_scores.professionalism} />
            <ScoreBar label="Communication" score={review.detailed_scores.communication} />
            <ScoreBar label="Technical Skills" score={review.detailed_scores.technical_skills} />
            <ScoreBar label="Reliability" score={review.detailed_scores.reliability} />
          </div>
        )}

        {/* Candidate Response */}
        {showResponse && review.candidate_response && (
          <div className="mt-3 pt-3 border-t">
            <div className="flex items-center gap-2 mb-2">
              <MessageSquare className="w-4 h-4 text-turquoise" />
              <span className="text-xs font-medium text-slate-600 dark:text-slate-400">Candidate&apos;s Response</span>
            </div>
            <p className="text-sm text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-slate-800/50 p-3 rounded-lg">
              &ldquo;{review.candidate_response.text}&rdquo;
            </p>
          </div>
        )}

        {/* Respond Button (for candidates viewing their own reviews) */}
        {onRespond && !review.candidate_response && (
          <div className="mt-3 pt-3 border-t">
            <Button 
              size="sm" 
              variant="outline" 
              onClick={() => onRespond(review)}
              className="w-full"
            >
              <MessageSquare className="w-4 h-4 mr-2" />
              Respond to this review
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

/**
 * Review Summary Header
 */
export const ReviewSummary = ({ summary }) => {
  if (!summary) return null;
  
  return (
    <div className="bg-gradient-to-r from-turquoise/5 to-turquoise/10 p-4 rounded-xl mb-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="text-3xl font-bold text-slate-900 dark:text-slate-100">
            {summary.average_rating?.toFixed(1) || '0.0'}
          </div>
          <div>
            <StarRating rating={Math.round(summary.average_rating || 0)} size="lg" />
            <p className="text-xs text-slate-500 mt-1">
              Based on {summary.total_reviews} review{summary.total_reviews !== 1 ? 's' : ''}
            </p>
          </div>
        </div>
        
        {summary.would_hire_again_percentage > 0 && (
          <div className="text-right">
            <div className="text-2xl font-bold text-emerald-600">
              {summary.would_hire_again_percentage}%
            </div>
            <p className="text-xs text-slate-500">would hire again</p>
          </div>
        )}
      </div>
      
      {/* Rating Distribution */}
      {summary.rating_distribution && (
        <div className="space-y-1 mb-3">
          {[5, 4, 3, 2, 1].map((rating) => {
            const count = summary.rating_distribution[rating] || 0;
            const percentage = summary.total_reviews > 0 ? (count / summary.total_reviews) * 100 : 0;
            return (
              <div key={rating} className="flex items-center gap-2 text-xs">
                <span className="w-3">{rating}</span>
                <Star className="w-3 h-3 fill-amber-400 text-amber-400" />
                <div className="flex-1 h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-amber-400 rounded-full"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
                <span className="w-4 text-slate-400">{count}</span>
              </div>
            );
          })}
        </div>
      )}

      {/* Top Strengths */}
      {summary.top_strengths?.length > 0 && (
        <div>
          <p className="text-xs font-medium text-slate-500 mb-2">Top Mentioned Strengths</p>
          <div className="flex flex-wrap gap-1">
            {summary.top_strengths.slice(0, 5).map((item, idx) => (
              <Badge 
                key={idx}
                variant="secondary"
                className="text-xs"
              >
                {item.strength} ({item.count})
              </Badge>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default EmployerReviewCard;
export { StarRating, ScoreBar };
