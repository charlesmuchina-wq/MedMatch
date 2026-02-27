import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { BarChart3, Plus, Loader2, FileText, TrendingUp, Download, Trash2, ArrowUpRight, ArrowDownRight, Users, DollarSign } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

function StatCard({ label, value, sub, trend, icon: Icon }) {
  const isUp = trend?.startsWith('+');
  return (
    <div className="p-3 rounded-lg bg-slate-700/30 border border-slate-700/40">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs text-slate-400">{label}</span>
        {Icon && <Icon className="w-3.5 h-3.5 text-slate-500" />}
      </div>
      <p className="text-lg font-bold text-white">{value}</p>
      {(sub || trend) && (
        <div className="flex items-center gap-2 mt-0.5">
          {trend && <span className={`text-[10px] flex items-center gap-0.5 ${isUp ? 'text-emerald-400' : 'text-red-400'}`}>
            {isUp ? <ArrowUpRight className="w-2.5 h-2.5" /> : <ArrowDownRight className="w-2.5 h-2.5" />} {trend}
          </span>}
          {sub && <span className="text-[10px] text-slate-500">{sub}</span>}
        </div>
      )}
    </div>
  );
}

function HorizontalBar({ data, colorMap }) {
  if (!data || typeof data !== 'object') return null;
  const entries = Object.entries(data);
  const max = Math.max(...entries.map(([, v]) => (typeof v === 'object' ? v.count || 0 : v)), 1);
  const colors = ['#14b8a6', '#3b82f6', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4', '#10b981', '#ec4899'];
  return (
    <div className="space-y-2">
      {entries.map(([key, val], i) => {
        const count = typeof val === 'object' ? val.count || 0 : val;
        const pct = (count / max) * 100;
        return (
          <div key={key} className="flex items-center gap-3">
            <span className="text-xs text-slate-400 w-24 truncate capitalize">{key.replace('_', ' ')}</span>
            <div className="flex-1 h-6 bg-slate-700/40 rounded overflow-hidden relative">
              <div className="h-full rounded transition-all duration-700 ease-out flex items-center"
                style={{ width: `${Math.max(pct, 2)}%`, background: colorMap?.[key] || colors[i % colors.length] }}>
                <span className="text-[10px] font-bold text-white ml-2">{count}</span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function FunnelChart({ stages }) {
  if (!stages?.length) return null;
  const max = Math.max(...stages.map(s => s.count), 1);
  const colors = ['#3b82f6', '#06b6d4', '#8b5cf6', '#f59e0b', '#14b8a6', '#10b981', '#ef4444'];
  return (
    <div className="space-y-1.5">
      {stages.map((s, i) => {
        const pct = (s.count / max) * 100;
        return (
          <div key={s.stage} className="flex items-center gap-3">
            <span className="text-xs text-slate-400 w-20 truncate capitalize">{s.stage}</span>
            <div className="flex-1 relative">
              <div className="h-7 rounded transition-all duration-700" style={{ width: `${Math.max(pct, 3)}%`, background: colors[i % colors.length], opacity: 0.85 }}>
                <span className="absolute inset-0 flex items-center ml-2 text-[11px] font-semibold text-white">{s.count} ({s.pct}%)</span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function TableView({ rows }) {
  if (!rows?.length) return null;
  const cols = Object.keys(rows[0]);
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-700">
            {cols.map(c => <th key={c} className="text-left py-2 px-3 text-xs text-slate-400 capitalize font-medium">{c.replace('_', ' ')}</th>)}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className="border-b border-slate-700/30 hover:bg-slate-700/20">
              {cols.map(c => <td key={c} className="py-2 px-3 text-slate-300 text-xs">{row[c]}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function TimeSeriesChart({ data }) {
  if (!data?.length) return null;
  const maxApps = Math.max(...data.map(d => d.applications), 1);
  return (
    <div className="flex items-end gap-2 h-40 px-2">
      {data.map((d, i) => (
        <div key={d.month} className="flex-1 flex flex-col items-center gap-1">
          <div className="w-full flex gap-0.5 items-end h-28">
            <div className="flex-1 rounded-t transition-all duration-500 bg-blue-500/70" style={{ height: `${(d.applications / maxApps) * 100}%` }} title={`Applications: ${d.applications}`} />
            <div className="flex-1 rounded-t transition-all duration-500 bg-teal-500/70" style={{ height: `${(d.interviews / maxApps) * 100}%` }} title={`Interviews: ${d.interviews}`} />
            <div className="flex-1 rounded-t transition-all duration-500 bg-emerald-500/70" style={{ height: `${(d.hires / maxApps) * 100}%` }} title={`Hires: ${d.hires}`} />
          </div>
          <span className="text-[10px] text-slate-500">{d.month}</span>
        </div>
      ))}
    </div>
  );
}

function ReportViewer({ report }) {
  const d = report.data || {};
  return (
    <div className="space-y-5">
      {/* Summary cards */}
      {d.summary && (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {Object.entries(d.summary).map(([k, v]) => (
            <StatCard key={k} label={k.replace(/_/g, ' ')} value={v} icon={k.includes('candidate') || k.includes('hire') ? Users : k.includes('cost') || k.includes('salary') ? DollarSign : TrendingUp} />
          ))}
        </div>
      )}
      {/* Funnel */}
      {d.stages && <FunnelChart stages={d.stages} />}
      {/* Bar charts */}
      {d.funnel && !d.stages && <HorizontalBar data={d.funnel} />}
      {d.gender_distribution && (
        <div>
          <h4 className="text-xs font-medium text-slate-400 mb-2">Gender Distribution</h4>
          <HorizontalBar data={d.gender_distribution} colorMap={{ Male: '#3b82f6', Female: '#ec4899', 'Non-binary': '#8b5cf6', 'Not specified': '#64748b' }} />
        </div>
      )}
      {d.sources && (
        <div>
          <h4 className="text-xs font-medium text-slate-400 mb-2">Source Breakdown</h4>
          <HorizontalBar data={d.sources} />
        </div>
      )}
      {d.by_status && (
        <div>
          <h4 className="text-xs font-medium text-slate-400 mb-2">Offers by Status</h4>
          <HorizontalBar data={Object.fromEntries(Object.entries(d.by_status).map(([k, v]) => [k, v.count]))} />
        </div>
      )}
      {/* Time series */}
      {d.monthly && (
        <div>
          <h4 className="text-xs font-medium text-slate-400 mb-2">Monthly Trend</h4>
          <div className="flex gap-3 mb-2">
            <span className="flex items-center gap-1 text-[10px] text-slate-400"><span className="w-2 h-2 rounded-full bg-blue-500" />Apps</span>
            <span className="flex items-center gap-1 text-[10px] text-slate-400"><span className="w-2 h-2 rounded-full bg-teal-500" />Interviews</span>
            <span className="flex items-center gap-1 text-[10px] text-slate-400"><span className="w-2 h-2 rounded-full bg-emerald-500" />Hires</span>
          </div>
          <TimeSeriesChart data={d.monthly} />
        </div>
      )}
      {/* Tables */}
      {d.source_quality && <TableView rows={d.source_quality} />}
      {d.department_diversity && <TableView rows={d.department_diversity} />}
    </div>
  );
}

export default function ReportBuilderPage() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [name, setName] = useState('');
  const [reportType, setReportType] = useState('hiring_funnel');
  const [dateRange, setDateRange] = useState('30d');
  const [selectedReport, setSelectedReport] = useState(null);
  const fetchOpts = { credentials: 'include' };
  const postOpts = { credentials: 'include', headers: { 'Content-Type': 'application/json' } };

  useEffect(() => {
    fetch(`${API}/api/advanced/reports`, fetchOpts).then(r => r.ok ? r.json() : { reports: [] }).then(d => { setReports(d.reports || []); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  const generateReport = async () => {
    if (!name) return;
    setGenerating(true);
    try {
      const res = await fetch(`${API}/api/advanced/reports`, {
        method: 'POST', ...postOpts,
        body: JSON.stringify({ name, report_type: reportType, date_range: dateRange, metrics: [], filters: {} })
      });
      if (res.ok) { const r = await res.json(); setReports([r, ...reports]); setSelectedReport(r); setName(''); }
    } catch (e) { console.error(e); }
    setGenerating(false);
  };

  const deleteReport = async (id) => {
    try {
      await fetch(`${API}/api/advanced/reports/${id}`, { method: 'DELETE', ...fetchOpts });
      setReports(reports.filter(r => r.id !== id));
      if (selectedReport?.id === id) setSelectedReport(null);
    } catch (e) { console.error(e); }
  };

  const typeLabels = { hiring_funnel: 'Hiring Funnel', dei: 'DEI Report', source: 'Source Analysis', time_series: 'Time Series', offer_analysis: 'Offer Analysis' };
  const typeColors = { hiring_funnel: 'bg-blue-500/20 text-blue-400', dei: 'bg-pink-500/20 text-pink-400', source: 'bg-amber-500/20 text-amber-400', time_series: 'bg-teal-500/20 text-teal-400', offer_analysis: 'bg-violet-500/20 text-violet-400' };

  return (
    <div className="min-h-screen bg-slate-900 p-4 md:p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500/20 to-violet-500/20 flex items-center justify-center">
            <BarChart3 className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <h1 className="text-xl md:text-2xl font-bold text-white" data-testid="report-builder-title">Report Builder</h1>
            <p className="text-xs text-slate-400">Create custom analytics reports with visual insights</p>
          </div>
        </div>

        {/* Builder Bar */}
        <Card className="bg-slate-800/60 border-slate-700/50 mb-6">
          <CardContent className="p-4">
            <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
              <Input value={name} onChange={e => setName(e.target.value)} placeholder="Report name *"
                className="bg-slate-700/50 border-slate-600 text-white md:col-span-2" data-testid="report-name-input" />
              <Select value={reportType} onValueChange={setReportType}>
                <SelectTrigger className="bg-slate-700/50 border-slate-600 text-white"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="hiring_funnel">Hiring Funnel</SelectItem>
                  <SelectItem value="dei">DEI Report</SelectItem>
                  <SelectItem value="source">Source Analysis</SelectItem>
                  <SelectItem value="time_series">Time Series</SelectItem>
                  <SelectItem value="offer_analysis">Offer Analysis</SelectItem>
                </SelectContent>
              </Select>
              <Select value={dateRange} onValueChange={setDateRange}>
                <SelectTrigger className="bg-slate-700/50 border-slate-600 text-white"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="7d">Last 7 days</SelectItem>
                  <SelectItem value="30d">Last 30 days</SelectItem>
                  <SelectItem value="90d">Last 90 days</SelectItem>
                  <SelectItem value="365d">Last year</SelectItem>
                </SelectContent>
              </Select>
              <Button onClick={generateReport} disabled={generating || !name} className="bg-blue-600 hover:bg-blue-500" data-testid="generate-report-btn">
                {generating ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Plus className="w-4 h-4 mr-2" />} Generate
              </Button>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-5">
          {/* Report List Sidebar */}
          <div className="lg:col-span-1 space-y-2">
            <h3 className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-2">Saved Reports ({reports.length})</h3>
            {loading && <Loader2 className="w-5 h-5 text-slate-500 animate-spin mx-auto" />}
            {reports.map(r => (
              <button key={r.id} onClick={() => setSelectedReport(r)}
                className={`w-full text-left p-3 rounded-lg border transition-all group ${selectedReport?.id === r.id ? 'bg-slate-700/60 border-blue-500/50' : 'bg-slate-800/40 border-slate-700/30 hover:border-slate-600'}`}
                data-testid={`report-${r.id}`}>
                <div className="flex items-start justify-between">
                  <p className="text-sm text-white font-medium truncate flex-1">{r.name}</p>
                  <button onClick={(e) => { e.stopPropagation(); deleteReport(r.id); }}
                    className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-red-400 transition-all ml-1">
                    <Trash2 className="w-3 h-3" />
                  </button>
                </div>
                <div className="flex items-center gap-2 mt-1">
                  <Badge className={`text-[9px] ${typeColors[r.report_type] || 'bg-slate-600'}`}>{typeLabels[r.report_type] || r.report_type}</Badge>
                  <span className="text-[10px] text-slate-500">{r.date_range}</span>
                </div>
              </button>
            ))}
            {!loading && reports.length === 0 && <p className="text-slate-500 text-xs text-center py-6">No reports yet</p>}
          </div>

          {/* Report Viewer */}
          <div className="lg:col-span-3">
            {selectedReport ? (
              <Card className="bg-slate-800/60 border-slate-700/50">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-white text-base">{selectedReport.name}</CardTitle>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge className={`text-[10px] ${typeColors[selectedReport.report_type] || 'bg-slate-600'}`}>{typeLabels[selectedReport.report_type] || selectedReport.report_type}</Badge>
                        <span className="text-[10px] text-slate-500">{selectedReport.date_range} | {new Date(selectedReport.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                    <Button size="sm" variant="ghost" className="text-slate-400 h-7" data-testid="export-report-btn" onClick={() => {
                      const blob = new Blob([JSON.stringify(selectedReport.data, null, 2)], { type: 'application/json' });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement('a'); a.href = url; a.download = `${selectedReport.name}.json`; a.click();
                    }}><Download className="w-3 h-3 mr-1" /> Export</Button>
                  </div>
                </CardHeader>
                <CardContent><ReportViewer report={selectedReport} /></CardContent>
              </Card>
            ) : (
              <div className="flex items-center justify-center h-72 text-slate-500 rounded-lg border border-dashed border-slate-700/50">
                <div className="text-center">
                  <BarChart3 className="w-10 h-10 mx-auto mb-3 opacity-15" />
                  <p className="text-sm">Select or generate a report to see insights</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
