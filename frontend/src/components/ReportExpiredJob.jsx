import { useState } from "react";
import { Flag, AlertTriangle, CheckCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { toast } from "sonner";
import api from "@/utils/apiClient";

const ReportExpiredJob = ({ jobId, jobTitle, variant = "ghost", className = "" }) => {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [reported, setReported] = useState(false);

  const handleReport = async () => {
    setLoading(true);
    try {
      const response = await api.client.post("/api/jobs/verify/report", {
        job_id: jobId,
        reason: "expired",
      });

      if (response.data.status === "job_hidden") {
        toast.success("Job has been hidden. Thank you for your feedback!");
      } else {
        toast.success("Report submitted. Thank you for helping keep job listings accurate!");
      }
      
      setReported(true);
      setOpen(false);
    } catch (error) {
      toast.error("Failed to submit report. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  if (reported) {
    return (
      <Button variant="ghost" size="sm" disabled className={className}>
        <CheckCircle className="h-4 w-4 mr-1 text-green-500" />
        Reported
      </Button>
    );
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button
          variant={variant}
          size="sm"
          className={`text-slate-500 hover:text-orange-500 ${className}`}
          data-testid={`report-job-${jobId}`}
        >
          <Flag className="h-4 w-4 mr-1" />
          Report
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-orange-500" />
            Report Ghost Job
          </DialogTitle>
          <DialogDescription className="text-left">
            Is this job listing no longer available or accepting applications?
          </DialogDescription>
        </DialogHeader>
        
        <div className="py-4">
          <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
            <p className="font-medium text-sm">{jobTitle}</p>
            <p className="text-xs text-slate-500 mt-1">
              Reporting this job will help improve search quality for all users.
            </p>
          </div>
          
          <div className="mt-4 space-y-2 text-sm text-slate-600 dark:text-slate-400">
            <p>Common reasons for expired job listings:</p>
            <ul className="list-disc list-inside space-y-1 ml-2">
              <li>Position has been filled</li>
              <li>Application deadline has passed</li>
              <li>Page shows "job not found" error</li>
              <li>Company is no longer hiring</li>
            </ul>
          </div>
        </div>

        <DialogFooter className="flex gap-2">
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button
            className="bg-orange-500 hover:bg-orange-600"
            onClick={handleReport}
            disabled={loading}
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Reporting...
              </>
            ) : (
              <>
                <Flag className="mr-2 h-4 w-4" />
                Report as Expired
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default ReportExpiredJob;
