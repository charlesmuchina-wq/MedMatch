import { useState } from "react";
import { CheckSquare, Trash2, Briefcase, Calendar } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useTranslation } from "@/utils/i18n";

const ApplicationsPage = ({ applications, onUpdateStatus, onDelete }) => {
  const { t } = useTranslation();
  const [filter, setFilter] = useState("all");
  
  // Status options with translation keys
  const statusOptions = [
    { value: "Applied", labelKey: "applications.applied" },
    { value: "Interview", labelKey: "applications.interviewing" },
    { value: "Offer", labelKey: "applications.offered" },
    { value: "Rejected", labelKey: "applications.rejected" }
  ];
  
  const filteredApps = filter === "all" ? applications : applications.filter(a => a.status === filter);

  const getStatusColor = (status) => {
    switch (status) {
      case "Applied": return "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300";
      case "Interview": return "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300";
      case "Offer": return "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300";
      case "Rejected": return "bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-300";
      default: return "bg-slate-100 text-slate-700";
    }
  };

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-6xl mx-auto animate-fade-in" data-testid="applications-page">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold text-slate-900 dark:text-slate-100 tracking-tight" style={{ fontFamily: 'IBM Plex Sans' }}>
          {t("applications.myApplications")}
        </h1>
        <p className="text-slate-600 dark:text-slate-400 mt-2">
          {t("applications.trackApplications")}
        </p>
      </div>

      <Tabs value={filter} onValueChange={setFilter} className="mb-6">
        <TabsList className="flex-wrap">
          <TabsTrigger value="all" data-testid="filter-all">
            {t("common.all") || "All"} ({applications.length})
          </TabsTrigger>
          {statusOptions.map(status => (
            <TabsTrigger key={status.value} value={status.value} data-testid={`filter-${status.value.toLowerCase()}`}>
              {t(status.labelKey)} ({applications.filter(a => a.status === status.value).length})
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>

      {filteredApps.length === 0 ? (
        <div className="empty-state">
          <CheckSquare className="w-12 h-12 text-slate-300 mb-4" />
          <h3 className="text-lg font-medium text-slate-700 dark:text-slate-300">
            {t("applications.noApplications")}
          </h3>
          <p className="text-slate-500">{t("applications.startApplying")}</p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredApps.map(app => (
            <Card key={app.id} className="hover:shadow-md transition-shadow" data-testid={`application-${app.id}`}>
              <CardContent className="p-6">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-start gap-3">
                      <div className="w-10 h-10 rounded-lg bg-turquoise/10 flex items-center justify-center flex-shrink-0">
                        <Briefcase className="w-5 h-5 text-turquoise" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-slate-900 dark:text-slate-100" style={{ fontFamily: 'IBM Plex Sans' }}>
                          {app.job.title}
                        </h3>
                        <p className="text-slate-600 dark:text-slate-400 text-sm">{app.job.company}</p>
                        <div className="flex items-center gap-2 mt-2">
                          <Badge className={getStatusColor(app.status)}>
                            {t(`applications.${app.status.toLowerCase()}`) || app.status}
                          </Badge>
                          <span className="text-slate-400 text-xs flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            {t("applications.appliedOn")} {new Date(app.applied_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Select value={app.status} onValueChange={(value) => onUpdateStatus(app.id, value)}>
                      <SelectTrigger className="w-36" data-testid={`status-select-${app.id}`}>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {statusOptions.map(status => (
                          <SelectItem key={status.value} value={status.value}>
                            {t(status.labelKey)}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Button 
                      variant="ghost" size="sm"
                      onClick={() => onDelete(app.id)}
                      className="text-slate-400 hover:text-rose-500"
                      data-testid={`delete-app-${app.id}`}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default ApplicationsPage;
