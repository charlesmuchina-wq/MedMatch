import { useState, useEffect } from "react";
import { 
  MessageSquare, Send, AlertTriangle, Check, 
  ChevronDown, Loader2, HelpCircle, X
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";
import { useTranslation } from "@/utils/i18n";
import { apiClient } from "@/utils/apiClient";

/**
 * Rejection Feedback Form Component for Recruiters
 * Allows recruiters to submit feedback when rejecting candidates
 */
const RejectionFeedbackForm = ({ 
  applicationId, 
  candidateId, 
  jobId, 
  candidateName,
  isOpen,
  onClose,
  onSubmit 
}) => {
  const { t } = useTranslation();
  const [feedbackType, setFeedbackType] = useState("");
  const [missingSkills, setMissingSkills] = useState("");
  const [experienceGap, setExperienceGap] = useState("");
  const [additionalNotes, setAdditionalNotes] = useState("");
  const [wouldConsider, setWouldConsider] = useState(false);
  const [suggestions, setSuggestions] = useState("");
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingCategories, setLoadingCategories] = useState(true);

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await apiClient.get("/feedback/categories");
      setCategories(response.categories || []);
    } catch (error) {
      console.error("Failed to fetch categories:", error);
    } finally {
      setLoadingCategories(false);
    }
  };

  const handleSubmit = async () => {
    if (!feedbackType) {
      toast.error(t("feedback.selectCategory") || "Please select a feedback category");
      return;
    }

    setLoading(true);
    try {
      await apiClient.post("/feedback/rejection", {
        application_id: applicationId,
        candidate_id: candidateId,
        job_id: jobId,
        feedback_type: feedbackType,
        specific_skills_missing: missingSkills ? missingSkills.split(",").map(s => s.trim()) : [],
        experience_gap: experienceGap || null,
        additional_notes: additionalNotes || null,
        would_consider_for_other_roles: wouldConsider,
        suggested_improvements: suggestions ? suggestions.split(",").map(s => s.trim()) : []
      });

      toast.success(t("feedback.submitted") || "Feedback submitted successfully");
      if (onSubmit) onSubmit();
      onClose();
    } catch (error) {
      toast.error(t("feedback.submitFailed") || "Failed to submit feedback");
    } finally {
      setLoading(false);
    }
  };

  const getCategoryIcon = (category) => {
    const id = category.toLowerCase();
    if (id.includes("skill")) return "🎯";
    if (id.includes("experience")) return "📈";
    if (id.includes("culture")) return "🤝";
    if (id.includes("salary")) return "💰";
    if (id.includes("overqualified")) return "⬆️";
    if (id.includes("underqualified")) return "⬇️";
    if (id.includes("location")) return "📍";
    if (id.includes("communication")) return "💬";
    if (id.includes("portfolio")) return "📁";
    return "📋";
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-lg max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-turquoise" />
            {t("feedback.provideTitle") || "Provide Rejection Feedback"}
          </DialogTitle>
          <DialogDescription>
            {candidateName 
              ? (t("feedback.forCandidate", { name: candidateName }) || `For candidate: ${candidateName}`)
              : (t("feedback.helpImprove") || "Help candidates improve with anonymous feedback")}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 mt-4">
          {/* Feedback Category */}
          <div className="space-y-2">
            <Label className="text-sm font-medium">
              {t("feedback.category") || "Primary Reason for Rejection"} *
            </Label>
            {loadingCategories ? (
              <div className="h-10 flex items-center">
                <Loader2 className="w-4 h-4 animate-spin text-turquoise" />
              </div>
            ) : (
              <Select value={feedbackType} onValueChange={setFeedbackType}>
                <SelectTrigger>
                  <SelectValue placeholder={t("feedback.selectCategory") || "Select a category"} />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((cat) => (
                    <SelectItem key={cat.id} value={cat.id}>
                      <span className="flex items-center gap-2">
                        <span>{getCategoryIcon(cat.name)}</span>
                        <span>{cat.name}</span>
                      </span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
            {feedbackType && (
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {categories.find(c => c.id === feedbackType)?.description}
              </p>
            )}
          </div>

          {/* Skills Gap Details */}
          {(feedbackType === "skills_gap" || feedbackType === "underqualified") && (
            <div className="space-y-2">
              <Label className="text-sm font-medium">
                {t("feedback.missingSkills") || "Missing Skills (comma-separated)"}
              </Label>
              <Textarea
                value={missingSkills}
                onChange={(e) => setMissingSkills(e.target.value)}
                placeholder="e.g., Python, AWS, Team Leadership"
                className="h-20"
              />
            </div>
          )}

          {/* Experience Gap Details */}
          {feedbackType === "experience_mismatch" && (
            <div className="space-y-2">
              <Label className="text-sm font-medium">
                {t("feedback.experienceGap") || "Experience Gap Description"}
              </Label>
              <Textarea
                value={experienceGap}
                onChange={(e) => setExperienceGap(e.target.value)}
                placeholder="e.g., Needed 5+ years in similar role, candidate has 2 years"
                className="h-20"
              />
            </div>
          )}

          {/* Additional Notes */}
          <div className="space-y-2">
            <Label className="text-sm font-medium">
              {t("feedback.additionalNotes") || "Additional Notes (Optional)"}
            </Label>
            <Textarea
              value={additionalNotes}
              onChange={(e) => setAdditionalNotes(e.target.value)}
              placeholder={t("feedback.notesPlaceholder") || "Any additional context that could help the candidate..."}
              className="h-20"
            />
          </div>

          {/* Improvement Suggestions */}
          <div className="space-y-2">
            <Label className="text-sm font-medium">
              {t("feedback.suggestions") || "Suggested Improvements (comma-separated)"}
            </Label>
            <Textarea
              value={suggestions}
              onChange={(e) => setSuggestions(e.target.value)}
              placeholder="e.g., Get AWS certification, More project management experience"
              className="h-20"
            />
          </div>

          {/* Would Consider for Other Roles */}
          <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
            <div className="flex items-center gap-2">
              <HelpCircle className="w-4 h-4 text-slate-400" />
              <Label className="text-sm">
                {t("feedback.wouldConsider") || "Would consider for other roles?"}
              </Label>
            </div>
            <Switch
              checked={wouldConsider}
              onCheckedChange={setWouldConsider}
            />
          </div>

          {/* Privacy Notice */}
          <div className="p-3 bg-turquoise/10 rounded-lg">
            <p className="text-xs text-turquoise-700 dark:text-turquoise-300 flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              {t("feedback.privacyNotice") || "This feedback will be shared anonymously with the candidate to help them improve. Your identity and company will not be revealed."}
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-2 mt-6">
          <Button variant="outline" onClick={onClose} disabled={loading}>
            {t("common.cancel") || "Cancel"}
          </Button>
          <Button onClick={handleSubmit} disabled={loading || !feedbackType}>
            {loading ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Send className="w-4 h-4 mr-2" />
            )}
            {t("feedback.submit") || "Submit Feedback"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default RejectionFeedbackForm;
