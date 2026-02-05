import { Bookmark, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { JobCard } from "@/components/shared/JobCard";
import { useTranslation } from "@/utils/i18n";

const SavedJobsPage = ({ savedJobs, onRemove, onApply, onAnalyze }) => {
  const { t } = useTranslation();
  
  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-6xl mx-auto animate-fade-in" data-testid="saved-jobs-page">
      <h1 className="text-3xl font-semibold text-slate-900 dark:text-slate-100 tracking-tight mb-8" style={{ fontFamily: 'IBM Plex Sans' }}>
        {t("nav.savedJobs")}
      </h1>

      {savedJobs.length === 0 ? (
        <div className="empty-state">
          <Bookmark className="w-12 h-12 text-slate-300 mb-4" />
          <h3 className="text-lg font-medium text-slate-700 dark:text-slate-300">{t("savedJobs.noSavedJobs") || "No saved jobs"}</h3>
          <p className="text-slate-500">{t("savedJobs.saveJobsHint") || "Save jobs while searching to review them later"}</p>
        </div>
      ) : (
        <div className="space-y-4">
          {savedJobs.map(saved => saved?.job ? (
            <div key={saved.id || saved.job?.id || Math.random()} className="relative">
              <JobCard job={saved.job} onSave={() => {}} onApply={onApply} onAnalyze={onAnalyze} isSaved={true} />
              <Button
                variant="ghost" size="sm"
                className="absolute top-4 right-4 text-slate-400 hover:text-rose-500"
                onClick={() => onRemove(saved.id)}
                data-testid={`remove-saved-${saved.id}`}
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          ) : null)}
        </div>
      )}
    </div>
  );
};

export default SavedJobsPage;
