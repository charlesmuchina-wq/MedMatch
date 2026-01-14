import { useState } from "react";
import { CheckSquare, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

const ApplicationsPage = ({ applications, onUpdateStatus, onDelete }) => {
  const [filter, setFilter] = useState("all");
  const filteredApps = filter === "all" ? applications : applications.filter(a => a.status === filter);
  const statusOptions = ["Applied", "Interview", "Offer", "Rejected"];

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-6xl mx-auto animate-fade-in" data-testid="applications-page">
      <h1 className="text-3xl font-semibold text-slate-900 dark:text-slate-100 tracking-tight mb-8" style={{ fontFamily: 'IBM Plex Sans' }}>
        Applications
      </h1>

      <Tabs value={filter} onValueChange={setFilter} className="mb-6">
        <TabsList>
          <TabsTrigger value="all" data-testid="filter-all">All ({applications.length})</TabsTrigger>
          {statusOptions.map(status => (
            <TabsTrigger key={status} value={status} data-testid={`filter-${status.toLowerCase()}`}>
              {status} ({applications.filter(a => a.status === status).length})
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>

      {filteredApps.length === 0 ? (
        <div className="empty-state">
          <CheckSquare className="w-12 h-12 text-slate-300 mb-4" />
          <h3 className="text-lg font-medium text-slate-700 dark:text-slate-300">No applications</h3>
          <p className="text-slate-500">Start applying to jobs to track them here</p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredApps.map(app => (
            <Card key={app.id} data-testid={`application-${app.id}`}>
              <CardContent className="p-6">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="flex-1">
                    <h3 className="font-semibold text-slate-900 dark:text-slate-100" style={{ fontFamily: 'IBM Plex Sans' }}>
                      {app.job.title}
                    </h3>
                    <p className="text-slate-600 text-sm">{app.job.company}</p>
                    <p className="text-slate-500 text-xs mt-1">
                      Applied {new Date(app.applied_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <Select value={app.status} onValueChange={(value) => onUpdateStatus(app.id, value)}>
                      <SelectTrigger className="w-32" data-testid={`status-select-${app.id}`}>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {statusOptions.map(status => (
                          <SelectItem key={status} value={status}>{status}</SelectItem>
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
