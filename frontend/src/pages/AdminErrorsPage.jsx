import { useState, useEffect, useCallback } from "react";
import { toast } from "sonner";
import { AlertTriangle, Bug, CheckCircle2, Trash2, RefreshCw, Server, Monitor, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { apiClient } from "@/utils/apiClient";

const LEVEL_STYLES = {
  error: "bg-rose-500/15 text-rose-300 border-rose-500/30",
  warning: "bg-amber-500/15 text-amber-300 border-amber-500/30",
  info: "bg-sky-500/15 text-sky-300 border-sky-500/30",
};

const Stat = ({ label, value, accent, testid }) => (
  <div data-testid={testid} className="rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-white/[0.03] px-5 py-4">
    <div className={`text-3xl font-semibold ${accent}`}>{value}</div>
    <div className="text-xs uppercase tracking-wider text-slate-500 mt-1">{label}</div>
  </div>
);

export default function AdminErrorsPage() {
  const [errors, setErrors] = useState([]);
  const [stats, setStats] = useState({ total: 0, unresolved: 0, last_24h: 0 });
  const [loading, setLoading] = useState(true);
  const [source, setSource] = useState("all");
  const [resolved, setResolved] = useState("all");

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (source !== "all") params.source = source;
      if (resolved !== "all") params.resolved = resolved === "resolved";
      const [e, s] = await Promise.all([
        apiClient.get("/api/observability/errors", params, { skipCache: true }),
        apiClient.get("/api/observability/errors/stats", {}, { skipCache: true }),
      ]);
      setErrors(e.data?.errors || []);
      setStats(s.data || {});
    } catch {
      toast.error("Failed to load error logs");
    } finally {
      setLoading(false);
    }
  }, [source, resolved]);

  useEffect(() => { refresh(); }, [refresh]);

  const resolveErr = async (id, val) => {
    try {
      await apiClient.request(`/api/observability/errors/${id}`, { method: "PATCH", body: JSON.stringify({ resolved: val }) });
      refresh();
    } catch { toast.error("Update failed"); }
  };
  const deleteErr = async (id) => {
    try { await apiClient.delete(`/api/observability/errors/${id}`); refresh(); }
    catch { toast.error("Delete failed"); }
  };

  return (
    <div className="min-h-screen text-slate-900 dark:text-slate-100" data-testid="admin-errors-page">
      <div className="max-w-6xl mx-auto px-5 py-8">
        <div className="flex items-center gap-3 mb-6">
          <div className="rounded-2xl bg-gradient-to-br from-rose-500 to-orange-500 p-2.5">
            <Bug className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-semibold tracking-tight">Error Logs</h1>
            <p className="text-sm text-slate-500">In-house error tracking — no third-party service</p>
          </div>
          <Button variant="ghost" size="sm" className="ml-auto text-slate-500" onClick={refresh} data-testid="errors-refresh-btn">
            <RefreshCw className="w-4 h-4 mr-1" /> Refresh
          </Button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-6">
          <Stat testid="stat-total" label="Total" value={stats.total || 0} accent="text-slate-700 dark:text-slate-200" />
          <Stat testid="stat-unresolved" label="Unresolved" value={stats.unresolved || 0} accent="text-rose-500" />
          <Stat testid="stat-24h" label="Last 24h" value={stats.last_24h || 0} accent="text-amber-500" />
        </div>

        <div className="flex flex-wrap gap-3 mb-4">
          <Select value={source} onValueChange={setSource}>
            <SelectTrigger className="w-40" data-testid="filter-source"><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All sources</SelectItem>
              <SelectItem value="frontend">Frontend</SelectItem>
              <SelectItem value="backend">Backend</SelectItem>
            </SelectContent>
          </Select>
          <Select value={resolved} onValueChange={setResolved}>
            <SelectTrigger className="w-40" data-testid="filter-resolved"><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All statuses</SelectItem>
              <SelectItem value="unresolved">Unresolved</SelectItem>
              <SelectItem value="resolved">Resolved</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {loading ? (
          <div className="flex justify-center py-12"><Loader2 className="w-6 h-6 animate-spin text-rose-500" /></div>
        ) : errors.length === 0 ? (
          <div className="text-center py-12 text-slate-500" data-testid="errors-empty">No errors logged 🎉</div>
        ) : (
          <div className="space-y-2" data-testid="errors-list">
            {errors.map((err) => (
              <Card key={err.id} data-testid={`error-row-${err.id}`} className={`border-slate-200 dark:border-white/10 ${err.resolved ? "opacity-60" : ""}`}>
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    {err.source === "backend" ? <Server className="w-4 h-4 mt-1 text-slate-400" /> : <Monitor className="w-4 h-4 mt-1 text-slate-400" />}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <Badge variant="outline" className={LEVEL_STYLES[err.level] || LEVEL_STYLES.error}>{err.level}</Badge>
                        <Badge variant="outline" className="border-slate-300 dark:border-white/15 text-slate-500">{err.source}</Badge>
                        {err.resolved && <Badge variant="outline" className="border-emerald-500/30 text-emerald-400">resolved</Badge>}
                        <span className="text-xs text-slate-400">{(err.created_at || "").replace("T", " ").slice(0, 19)}</span>
                      </div>
                      <div className="font-medium mt-1 break-words">{err.message}</div>
                      {err.url ? <div className="text-xs text-slate-500 mt-0.5 break-all">{err.url}</div> : null}
                      {err.stack ? (
                        <pre className="text-[11px] text-slate-500 mt-2 max-h-32 overflow-auto whitespace-pre-wrap bg-slate-50 dark:bg-black/30 rounded p-2">{err.stack}</pre>
                      ) : null}
                    </div>
                    <div className="flex flex-col gap-2">
                      <button data-testid={`error-resolve-${err.id}`} onClick={() => resolveErr(err.id, !err.resolved)} title={err.resolved ? "Reopen" : "Resolve"} className="text-slate-400 hover:text-emerald-500">
                        <CheckCircle2 className="w-4 h-4" />
                      </button>
                      <button data-testid={`error-delete-${err.id}`} onClick={() => deleteErr(err.id)} title="Delete" className="text-slate-400 hover:text-rose-500">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
