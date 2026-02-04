/**
 * Employer Review Form Component
 * For recruiters to submit reviews for candidates
 */
import { useState, useEffect } from "react";
import { Star, ThumbsUp, Send, X, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { toast } from "sonner";
import axios from "axios";

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * Interactive Star Rating Input
 */
const StarRatingInput = ({ value, onChange, label }) => {
  const [hovered, setHovered] = useState(0);
  
  return (
    <div>
      <label className="text-sm font-medium text-slate-700 dark:text-slate-300 block mb-2">
        {label}
      </label>
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            onMouseEnter={() => setHovered(star)}
            onMouseLeave={() => setHovered(0)}
            onClick={() => onChange(star)}
            className="p-1 transition-transform hover:scale-110"
          >
            <Star
              className={`w-6 h-6 transition-colors ${
                star <= (hovered || value)
                  ? "fill-amber-400 text-amber-400"
                  : "fill-slate-200 text-slate-200 dark:fill-slate-600 dark:text-slate-600"
              }`}
            />
          </button>
        ))}
        {value > 0 && (
          <span className="ml-2 text-sm text-slate-500">
            {value === 5 ? "Excellent" : value === 4 ? "Very Good" : value === 3 ? "Good" : value === 2 ? "Fair" : "Poor"}
          </span>
        )}
      </div>
    </div>
  );
};

/**
 * Tag Selector Component
 */
const TagSelector = ({ label, options, selected, onChange, variant = "default" }) => {
  const toggleTag = (tag) => {
    if (selected.includes(tag)) {
      onChange(selected.filter(t => t !== tag));
    } else {
      onChange([...selected, tag]);
    }
  };

  const variantClasses = {
    default: "bg-turquoise/10 text-turquoise border-turquoise/30",
    success: "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-900/20 dark:text-emerald-400",
    warning: "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-900/20 dark:text-amber-400"
  };

  return (
    <div>
      <label className="text-sm font-medium text-slate-700 dark:text-slate-300 block mb-2">
        {label}
      </label>
      <div className="flex flex-wrap gap-2">
        {options.map((option) => (
          <button
            key={option}
            type="button"
            onClick={() => toggleTag(option)}
            className={`px-3 py-1.5 text-xs rounded-full border transition-all ${
              selected.includes(option)
                ? variantClasses[variant]
                : "bg-slate-50 text-slate-600 border-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700 hover:border-slate-300"
            }`}
          >
            {option}
          </button>
        ))}
      </div>
    </div>
  );
};

/**
 * Employer Review Form Dialog
 */
const EmployerReviewForm = ({ 
  isOpen, 
  onClose, 
  candidateId, 
  candidateName,
  jobId = null,
  onSubmitSuccess 
}) => {
  const [loading, setLoading] = useState(false);
  const [strengthOptions, setStrengthOptions] = useState([]);
  const [improvementOptions, setImprovementOptions] = useState([]);
  
  // Form state
  const [formData, setFormData] = useState({
    rating: 0,
    review_type: "general",
    comment: "",
    strengths: [],
    areas_for_improvement: [],
    would_hire_again: null,
    professionalism: 0,
    communication: 0,
    technical_skills: 0,
    reliability: 0,
    is_anonymous: false
  });

  useEffect(() => {
    fetchSuggestions();
  }, []);

  const fetchSuggestions = async () => {
    try {
      const response = await axios.get(`${API}/api/reviews/strength-suggestions`);
      setStrengthOptions(response.data.strengths || []);
      setImprovementOptions(response.data.areas_for_improvement || []);
    } catch (err) {
      // Use defaults if API fails
      setStrengthOptions([
        "Strong communication skills",
        "Technical expertise",
        "Problem solver",
        "Team player",
        "Reliable and punctual"
      ]);
      setImprovementOptions([
        "Communication could improve",
        "Time management",
        "Technical skills development"
      ]);
    }
  };

  const handleSubmit = async () => {
    // Validation
    if (formData.rating === 0) {
      toast.error("Please provide an overall rating");
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem("medmatch-token");
      const payload = {
        candidate_id: candidateId,
        job_id: jobId,
        rating: formData.rating,
        review_type: formData.review_type,
        comment: formData.comment || null,
        strengths: formData.strengths,
        areas_for_improvement: formData.areas_for_improvement,
        would_hire_again: formData.would_hire_again,
        professionalism: formData.professionalism > 0 ? formData.professionalism : null,
        communication: formData.communication > 0 ? formData.communication : null,
        technical_skills: formData.technical_skills > 0 ? formData.technical_skills : null,
        reliability: formData.reliability > 0 ? formData.reliability : null,
        is_anonymous: formData.is_anonymous
      };

      await axios.post(
        `${API}/api/reviews/create`,
        payload,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      toast.success("Review submitted! It will be visible after moderation.");
      onSubmitSuccess?.();
      onClose();
      
      // Reset form
      setFormData({
        rating: 0,
        review_type: "general",
        comment: "",
        strengths: [],
        areas_for_improvement: [],
        would_hire_again: null,
        professionalism: 0,
        communication: 0,
        technical_skills: 0,
        reliability: 0,
        is_anonymous: false
      });
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to submit review");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Star className="w-5 h-5 text-amber-500" />
            Write a Review
          </DialogTitle>
          {candidateName && (
            <p className="text-sm text-slate-500">
              for {candidateName}
            </p>
          )}
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Overall Rating */}
          <StarRatingInput
            value={formData.rating}
            onChange={(rating) => setFormData({ ...formData, rating })}
            label="Overall Rating *"
          />

          {/* Review Type */}
          <div>
            <label className="text-sm font-medium text-slate-700 dark:text-slate-300 block mb-2">
              Review Type
            </label>
            <div className="flex gap-2">
              {["interview", "placement", "general"].map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => setFormData({ ...formData, review_type: type })}
                  className={`px-4 py-2 rounded-lg text-sm font-medium capitalize transition-colors ${
                    formData.review_type === type
                      ? "bg-turquoise text-white"
                      : "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 hover:bg-slate-200"
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>

          {/* Written Review */}
          <div>
            <label className="text-sm font-medium text-slate-700 dark:text-slate-300 block mb-2">
              Your Review
            </label>
            <Textarea
              placeholder="Share your experience working with this candidate..."
              value={formData.comment}
              onChange={(e) => setFormData({ ...formData, comment: e.target.value })}
              rows={4}
              className="resize-none"
            />
          </div>

          {/* Strengths */}
          <TagSelector
            label="Strengths (select all that apply)"
            options={strengthOptions}
            selected={formData.strengths}
            onChange={(strengths) => setFormData({ ...formData, strengths })}
            variant="success"
          />

          {/* Areas for Improvement */}
          <TagSelector
            label="Areas for Growth (optional)"
            options={improvementOptions}
            selected={formData.areas_for_improvement}
            onChange={(areas) => setFormData({ ...formData, areas_for_improvement: areas })}
            variant="warning"
          />

          {/* Would Hire Again */}
          <div>
            <label className="text-sm font-medium text-slate-700 dark:text-slate-300 block mb-2">
              Would you hire this candidate again?
            </label>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setFormData({ ...formData, would_hire_again: true })}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  formData.would_hire_again === true
                    ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400"
                    : "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 hover:bg-slate-200"
                }`}
              >
                <ThumbsUp className="w-4 h-4" />
                Yes
              </button>
              <button
                type="button"
                onClick={() => setFormData({ ...formData, would_hire_again: false })}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  formData.would_hire_again === false
                    ? "bg-slate-200 text-slate-700 dark:bg-slate-700 dark:text-slate-300"
                    : "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 hover:bg-slate-200"
                }`}
              >
                Maybe not
              </button>
            </div>
          </div>

          {/* Detailed Ratings */}
          <div className="pt-4 border-t">
            <p className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">
              Detailed Ratings (optional)
            </p>
            <div className="grid grid-cols-2 gap-4">
              <StarRatingInput
                value={formData.professionalism}
                onChange={(v) => setFormData({ ...formData, professionalism: v })}
                label="Professionalism"
              />
              <StarRatingInput
                value={formData.communication}
                onChange={(v) => setFormData({ ...formData, communication: v })}
                label="Communication"
              />
              <StarRatingInput
                value={formData.technical_skills}
                onChange={(v) => setFormData({ ...formData, technical_skills: v })}
                label="Technical Skills"
              />
              <StarRatingInput
                value={formData.reliability}
                onChange={(v) => setFormData({ ...formData, reliability: v })}
                label="Reliability"
              />
            </div>
          </div>

          {/* Anonymous Toggle */}
          <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
            <div>
              <p className="font-medium text-slate-900 dark:text-slate-100">Submit Anonymously</p>
              <p className="text-xs text-slate-500">Your name and company will be hidden</p>
            </div>
            <Switch
              checked={formData.is_anonymous}
              onCheckedChange={(checked) => setFormData({ ...formData, is_anonymous: checked })}
            />
          </div>

          {/* Moderation Notice */}
          <div className="flex items-start gap-2 p-3 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 rounded-lg text-xs">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <p>
              Reviews are moderated before publication to ensure quality and compliance with our guidelines.
              The candidate will be notified once your review is approved.
            </p>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button 
            onClick={handleSubmit} 
            disabled={loading || formData.rating === 0}
            className="bg-turquoise hover:bg-turquoise/90"
          >
            {loading ? (
              "Submitting..."
            ) : (
              <>
                <Send className="w-4 h-4 mr-2" />
                Submit Review
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default EmployerReviewForm;
