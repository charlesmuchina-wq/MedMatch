import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { BarChart3, Plus, Loader2, FileText, Calendar, TrendingUp, Download } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

export default function ReportBuilderPage() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [name, setName] = useState('');
  const [reportType, setReportType] = useState('hiring_funnel');
  const [dateRange, setDateRange] = useState('30d');
  const [selectedReport, setSelectedReport] = useState(null);
  const token = localStorage.getItem('token');
  const headers = { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` };

  useEffect(() => {
    if (token) fetch(`${API}/api/advanced/reports`, { headers }).then(r => r.ok ? r.json() : { reports: [] }).then(d => { setReports(d.reports || []); setLoading(false); }).catch(() => setLoading(false));
    else setLoading(false);
  }, [token]);

  const generateReport = async () => {
    if (!name) return;
    setGenerating(true);
    const res = await fetch(`${API}/api/advanced/reports`, {
      method: 'POST', headers,
      body: JSON.stringify({ name, report_type: reportType, date_range: dateRange, metrics: [], filters: {} })
    });
    if (res.ok) { const r = await res.json(); setReports([r, ...reports]); setSelectedReport(r); setName(''); }
    setGenerating(false);
  };

  const typeLabels = { hiring_funnel: 'Hiring Funnel', dei: 'DEI Report', source: 'Source Analysis', time_series: 'Time Series' };

  return (
    <div className="min-h-screen bg-slate-900 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center gap-3 mb-8">
          <div className="p-2 bg-turquoise/10 rounded-lg"><BarChart3 className="w-6 h-6 text-turquoise" /></div>
          <div>
            <h1 className="text-2xl font-bold text-white" data-testid="report-builder-title">Report Builder</h1>
            <p className="text-slate-400 text-sm">Create custom analytics reports</p>
          </div>
        </div>

        {/* Builder */}
        <Card className="bg-slate-800 border-slate-700 mb-6">
          <CardContent className="p-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
              <Input value={name} onChange={e => setName(e.target.value)} placeholder="Report name *" className="bg-slate-700 border-slate-600 text-white" data-testid="report-name-input" />
              <Select value={reportType} onValueChange={setReportType}>
                <SelectTrigger className="bg-slate-700 border-slate-600 text-white"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="hiring_funnel">Hiring Funnel</SelectItem>
                  <SelectItem value="dei">DEI Report</SelectItem>
                  <SelectItem value="source">Source Analysis</SelectItem>
                  <SelectItem value="time_series">Time Series</SelectItem>
                </SelectContent>
              </Select>
              <Select value={dateRange} onValueChange={setDateRange}>
                <SelectTrigger className="bg-slate-700 border-slate-600 text-white"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="7d">Last 7 days</SelectItem>
                  <SelectItem value="30d">Last 30 days</SelectItem>
                  <SelectItem value="90d">Last 90 days</SelectItem>
                  <SelectItem value="365d">Last year</SelectItem>
                </SelectContent>
              </Select>
              <Button onClick={generateReport} disabled={generating || !name} className="bg-turquoise hover:bg-turquoise/80" data-testid="generate-report-btn">
                {generating ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Plus className="w-4 h-4 mr-2" />} Generate
              </Button>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Report List */}
          <div className="space-y-2">
            <h3 className="text-sm font-medium text-slate-400 mb-3">Saved Reports</h3>
            {reports.map(r => (
              <button key={r.id} onClick={() => setSelectedReport(r)}
                className={`w-full text-left p-3 rounded-lg border transition-colors ${selectedReport?.id === r.id ? 'bg-slate-700 border-turquoise' : 'bg-slate-800 border-slate-700 hover:border-slate-600'}`}
                data-testid={`report-${r.id}`}>
                <p className="text-sm text-white font-medium">{r.name}</p>
                <div className="flex items-center gap-2 mt-1">
                  <Badge className="text-[10px] bg-slate-600">{typeLabels[r.report_type] || r.report_type}</Badge>
                  <span className="text-xs text-slate-500">{r.date_range}</span>
                </div>
              </button>
            ))}
            {reports.length === 0 && <p className="text-slate-500 text-sm text-center py-4">No reports yet</p>}
          </div>

          {/* Report Preview */}
          <div className="lg:col-span-2">
            {selectedReport ? (
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-white text-base">{selectedReport.name}</CardTitle>
                    <Button size="sm" variant="ghost" className="text-slate-400" onClick={() => {
                      const blob = new Blob([JSON.stringify(selectedReport.data, null, 2)], { type: 'application/json' });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url; a.download = `${selectedReport.name}.json`; a.click();
                    }}><Download className="w-3 h-3 mr-1" /> Export</Button>
                  </div>
                </CardHeader>
                <CardContent>
                  {/* Render data based on type */}
                  {selectedReport.data && Object.entries(selectedReport.data).map(([key, value]) => (
                    <div key={key} className="mb-4">
                      <h4 className="text-sm font-medium text-slate-300 capitalize mb-2">{key.replace('_', ' ')}</h4>
                      {typeof value === 'object' && !Array.isArray(value) ? (
                        <div className="space-y-2">
                          {Object.entries(value).map(([k, v]) => (
                            <div key={k} className="flex items-center justify-between py-1.5">
                              <span className="text-sm text-slate-400 capitalize">{k}</span>
                              <span className="text-sm font-medium text-white">{v}</span>
                            </div>
                          ))}
                        </div>
                      ) : Array.isArray(value) ? (
                        <div className="overflow-auto">
                          <table className="w-full text-sm">
                            <thead><tr className="border-b border-slate-700">
                              {value[0] && Object.keys(value[0]).map(h => <th key={h} className="text-left py-2 px-3 text-slate-400 capitalize">{h}</th>)}
                            </tr></thead>
                            <tbody>{value.map((row, i) => (
                              <tr key={i} className="border-b border-slate-700/50">
                                {Object.values(row).map((v, j) => <td key={j} className="py-2 px-3 text-slate-300">{v}</td>)}
                              </tr>
                            ))}</tbody>
                          </table>
                        </div>
                      ) : <p className="text-slate-300">{String(value)}</p>}
                    </div>
                  ))}
                </CardContent>
              </Card>
            ) : (
              <div className="flex items-center justify-center h-64 text-slate-500">
                <div className="text-center"><BarChart3 className="w-12 h-12 mx-auto mb-3 opacity-30" /><p>Select or generate a report</p></div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
