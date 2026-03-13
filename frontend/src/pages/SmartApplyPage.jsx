import { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import { useTranslation } from '@/utils/i18n';
import {
  Zap, Search, FileText, CheckCircle, XCircle, Loader2, ExternalLink,
  Briefcase, MapPin, Clock, Star, ChevronDown, ChevronUp, Sparkles,
  Settings, History, Play, ArrowLeft, AlertCircle, Copy, Target
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function SmartApplyPage({ resume }) {
  const { t } = useTranslation();
  const token = localStorage.getItem('token');
  const [tab, setTab] = useState('apply'); // apply | history | settings
  const [jobTitle, setJobTitle] = useState('');
  const [location, setLocation] = useState('Remote');
  const [maxJobs, setMaxJobs] = useState(10);
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState(null);
  const [history, setHistory] = useState([]);
  const [config, setConfig] = useState(null);
  const [expandedJob, setExpandedJob] = useState(null);
  const [hasResume, setHasResume] = useState(!!resume);

  const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };

  const loadConfig = useCallback(async () => {
    try {
      const res = await fetch(`${API}/smart-apply/config`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) setConfig(await res.json());
    } catch {}
  }, [token]);

  const loadHistory = useCallback(async () => {
    try {
      const res = await fetch(`${API}/smart-apply/history`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) {
        const data = await res.json();
        setHistory(data.runs || []);
      }
    } catch {}
  }, [token]);

  const checkResume = useCallback(async () => {
    try {
      const res = await fetch(`${API}/resume`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) {
        const data = await res.json();
        setHasResume(!!data?.skills?.length || !!data?.full_name);
      }
    } catch {}
  }, [token]);

  useEffect(() => {
    loadConfig();
    loadHistory();
    if (!resume) checkResume();
  }, [loadConfig, loadHistory, checkResume, resume]);

  const handleRun = async () => {
    if (!jobTitle.trim()) { toast.error('Enter a job title'); return; }
    setRunning(true);
    setResults(null);
    try {
      const res = await fetch(`${API}/smart-apply/run`, {
        method: 'POST', headers,
        body: JSON.stringify({ job_title: jobTitle, location, max_jobs: maxJobs })
      });
      if (res.ok) {
        const data = await res.json();
        setResults(data);
        toast.success(`Applied to ${data.total_applied} jobs!`);
        loadHistory();
      } else {
        const err = await res.json();
        toast.error(err.detail || 'Smart Apply failed');
      }
    } catch {
      toast.error('Network error');
    }
    setRunning(false);
  };

  const saveConfig = async (updates) => {
    const newConfig = { ...config, ...updates };
    setConfig(newConfig);
    try {
      await fetch(`${API}/smart-apply/config`, {
        method: 'PUT', headers,
        body: JSON.stringify(newConfig)
      });
    } catch {}
  };

  const scoreColor = (score) => {
    if (score >= 70) return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
    if (score >= 40) return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
    return 'text-slate-400 bg-slate-500/10 border-slate-500/20';
  };

  return (
    <div className="space-y-6" data-testid="smart-apply-page">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-white flex items-center gap-2">
            <Zap className="w-6 h-6 text-amber-400" />
            Quick Apply Bot
          </h1>
          <p className="text-sm text-slate-400 mt-1">AI finds & applies to matching jobs posted in the last 24h</p>
        </div>
        <div className="flex gap-2">
          {[
            { id: 'apply', icon: Play, label: 'Apply' },
            { id: 'history', icon: History, label: 'History' },
            { id: 'settings', icon: Settings, label: 'Settings' },
          ].map(t => (
            <button key={t.id} onClick={() => setTab(t.id)} data-testid={`tab-${t.id}`}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                tab === t.id ? 'bg-white/10 text-white border border-white/20' : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`}>
              <t.icon className="w-3.5 h-3.5" />{t.label}
            </button>
          ))}
        </div>
      </div>

      {/* Resume Check */}
      {!hasResume && (
        <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-start gap-3" data-testid="no-resume-warning">
          <AlertCircle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-amber-300">Resume Required</p>
            <p className="text-xs text-amber-200/80 mt-1">Upload your resume first for the AI to match jobs to your skills and experience.</p>
          </div>
        </div>
      )}

      {/* Apply Tab */}
      {tab === 'apply' && (
        <div className="space-y-5">
          {/* Search Form */}
          <Card className="bg-white/[0.04] border-white/10">
            <CardContent className="p-5 space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="sm:col-span-2">
                  <label className="text-xs font-semibold text-slate-300 mb-1.5 block">Desired Job Title</label>
                  <div className="relative">
                    <Target className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                    <Input value={jobTitle} onChange={e => setJobTitle(e.target.value)}
                      placeholder="e.g. Senior Software Engineer"
                      className="pl-10 bg-white/5 border-white/10 text-white placeholder:text-slate-500"
                      data-testid="smart-apply-job-title" />
                  </div>
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-300 mb-1.5 block">Location</label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                    <Input value={location} onChange={e => setLocation(e.target.value)}
                      placeholder="Remote, New York, etc."
                      className="pl-10 bg-white/5 border-white/10 text-white placeholder:text-slate-500"
                      data-testid="smart-apply-location" />
                  </div>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <label className="text-xs text-slate-400">Max jobs:</label>
                  <select value={maxJobs} onChange={e => setMaxJobs(Number(e.target.value))}
                    className="bg-white/5 border border-white/10 rounded-md px-2 py-1 text-xs text-white"
                    data-testid="smart-apply-max-jobs">
                    {[5, 10, 15, 20].map(n => <option key={n} value={n}>{n}</option>)}
                  </select>
                  <span className="text-[10px] text-slate-500 hidden sm:inline">
                    <Clock className="w-3 h-3 inline mr-1" />Only jobs posted in last 24h
                  </span>
                </div>
                <Button onClick={handleRun} disabled={running || !hasResume || !jobTitle.trim()}
                  className="gap-2 font-bold text-white"
                  style={{ background: 'linear-gradient(135deg, #14b8a6, #6C5CE7)' }}
                  data-testid="smart-apply-run-btn">
                  {running ? <Loader2 className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
                  {running ? 'Searching & Applying...' : 'Find & Apply'}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Running Animation */}
          {running && (
            <div className="text-center py-10" data-testid="smart-apply-running">
              <div className="relative inline-flex">
                <div className="w-16 h-16 rounded-full border-4 border-teal-500/20 border-t-teal-500 animate-spin" />
                <Sparkles className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-6 h-6 text-teal-400" />
              </div>
              <p className="text-sm text-slate-300 mt-4 font-medium">Scanning job boards, matching your resume, generating cover letters...</p>
              <p className="text-xs text-slate-500 mt-1">This may take 30-60 seconds</p>
            </div>
          )}

          {/* Results */}
          {results && !running && (
            <div className="space-y-4" data-testid="smart-apply-results">
              {/* Summary */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {[
                  { label: 'Jobs Found', value: results.total_jobs_found, icon: Search, color: 'text-blue-400' },
                  { label: 'Matched', value: results.total_matched, icon: Target, color: 'text-teal-400' },
                  { label: 'Applied', value: results.total_applied, icon: CheckCircle, color: 'text-emerald-400' },
                  { label: 'Skipped', value: results.total_skipped, icon: XCircle, color: 'text-slate-400' },
                ].map(s => (
                  <div key={s.label} className="p-3 rounded-lg bg-white/[0.03] border border-white/5 text-center">
                    <s.icon className={`w-5 h-5 mx-auto ${s.color}`} />
                    <p className="text-lg font-bold text-white mt-1">{s.value}</p>
                    <p className="text-[10px] text-slate-400">{s.label}</p>
                  </div>
                ))}
              </div>

              {/* Job Cards */}
              <div className="space-y-2">
                {(results.results || []).map((job, idx) => (
                  <div key={idx} className={`p-4 rounded-lg border transition-all ${
                    job.already_applied ? 'bg-white/[0.02] border-white/5 opacity-60' : 'bg-white/[0.04] border-white/10 hover:border-white/20'
                  }`} data-testid={`smart-apply-result-${idx}`}>
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <h3 className="text-sm font-bold text-white truncate">{job.title}</h3>
                          {job.already_applied && <Badge variant="outline" className="text-[9px] border-slate-500 text-slate-400">Already Applied</Badge>}
                        </div>
                        <div className="flex items-center gap-3 mt-1 text-xs text-slate-400">
                          <span className="flex items-center gap-1"><Briefcase className="w-3 h-3" />{job.company}</span>
                          {job.location && <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{job.location}</span>}
                        </div>
                        {job.matched_skills?.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-2">
                            {job.matched_skills.slice(0, 5).map(s => (
                              <span key={s} className="text-[9px] px-1.5 py-0.5 rounded bg-teal-500/10 text-teal-300 border border-teal-500/20">{s}</span>
                            ))}
                            {job.matched_skills.length > 5 && <span className="text-[9px] text-slate-500">+{job.matched_skills.length - 5} more</span>}
                          </div>
                        )}
                      </div>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <div className={`px-2 py-1 rounded-md border text-xs font-bold ${scoreColor(job.match_score)}`}>
                          {job.match_score}%
                        </div>
                        {job.url && (
                          <a href={job.url} target="_blank" rel="noopener noreferrer"
                            className="p-1.5 rounded-md text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
                            data-testid={`view-job-${idx}`}>
                            <ExternalLink className="w-4 h-4" />
                          </a>
                        )}
                      </div>
                    </div>

                    {/* Cover Letter Toggle */}
                    {job.cover_letter_generated && (
                      <div className="mt-3">
                        <button onClick={() => setExpandedJob(expandedJob === idx ? null : idx)}
                          className="flex items-center gap-1.5 text-xs text-teal-400 hover:text-teal-300 transition-colors"
                          data-testid={`toggle-cover-letter-${idx}`}>
                          <FileText className="w-3 h-3" />
                          {expandedJob === idx ? 'Hide' : 'View'} Cover Letter
                          {expandedJob === idx ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                        </button>
                        {expandedJob === idx && (
                          <div className="mt-2 p-3 rounded-md bg-white/[0.03] border border-white/5">
                            <p className="text-xs text-slate-300 whitespace-pre-wrap leading-relaxed">
                              {job.cover_letter_preview || 'Cover letter generated and saved.'}
                            </p>
                            <button onClick={() => { navigator.clipboard.writeText(job.cover_letter_preview || ''); toast.success('Copied!'); }}
                              className="mt-2 flex items-center gap-1 text-[10px] text-teal-400 hover:text-teal-300">
                              <Copy className="w-3 h-3" />Copy
                            </button>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
                {(results.results || []).length === 0 && (
                  <div className="text-center py-8">
                    <Search className="w-8 h-8 text-slate-600 mx-auto mb-2" />
                    <p className="text-sm text-slate-400">No matching jobs found in the last 24h</p>
                    <p className="text-xs text-slate-500 mt-1">Try a broader job title or different location</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* History Tab */}
      {tab === 'history' && (
        <div className="space-y-3" data-testid="smart-apply-history">
          {history.length === 0 ? (
            <div className="text-center py-12">
              <History className="w-8 h-8 text-slate-600 mx-auto mb-2" />
              <p className="text-sm text-slate-400">No Smart Apply runs yet</p>
            </div>
          ) : (
            history.map((run, idx) => (
              <Card key={run.id || idx} className="bg-white/[0.04] border-white/10" data-testid={`history-run-${idx}`}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-sm font-bold text-white flex items-center gap-2">
                      <Briefcase className="w-4 h-4 text-teal-400" />
                      {run.job_title}
                    </h3>
                    <span className="text-[10px] text-slate-500">
                      {run.created_at ? new Date(run.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : ''}
                    </span>
                  </div>
                  <div className="flex gap-4 text-xs text-slate-400">
                    <span><Search className="w-3 h-3 inline mr-1" />{run.total_found} found</span>
                    <span><CheckCircle className="w-3 h-3 inline mr-1 text-emerald-400" />{run.total_applied} applied</span>
                    <span><XCircle className="w-3 h-3 inline mr-1" />{run.total_skipped} skipped</span>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      )}

      {/* Settings Tab */}
      {tab === 'settings' && config && (
        <div className="space-y-5" data-testid="smart-apply-settings">
          <Card className="bg-white/[0.04] border-white/10">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm text-white flex items-center gap-2">
                <Settings className="w-4 h-4 text-slate-400" />Preferences
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-slate-300 mb-1.5 block">Target Roles (comma-separated)</label>
                <Input value={(config.target_roles || []).join(', ')}
                  onChange={e => saveConfig({ target_roles: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
                  placeholder="Senior Engineer, Staff Engineer, Tech Lead"
                  className="bg-white/5 border-white/10 text-white placeholder:text-slate-500 text-sm"
                  data-testid="config-target-roles" />
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-300 mb-1.5 block">Preferred Locations (comma-separated)</label>
                <Input value={(config.locations || []).join(', ')}
                  onChange={e => saveConfig({ locations: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
                  placeholder="Remote, New York, San Francisco"
                  className="bg-white/5 border-white/10 text-white placeholder:text-slate-500 text-sm"
                  data-testid="config-locations" />
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-300 mb-1.5 block">Exclude Companies (comma-separated)</label>
                <Input value={(config.exclude_companies || []).join(', ')}
                  onChange={e => saveConfig({ exclude_companies: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
                  placeholder="Company A, Company B"
                  className="bg-white/5 border-white/10 text-white placeholder:text-slate-500 text-sm"
                  data-testid="config-exclude-companies" />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold text-slate-300">Auto-generate Cover Letters</p>
                  <p className="text-[10px] text-slate-500 mt-0.5">AI creates tailored cover letters for each matched job</p>
                </div>
                <button onClick={() => saveConfig({ auto_generate_cover_letter: !config.auto_generate_cover_letter })}
                  className={`w-10 h-5 rounded-full transition-colors flex items-center ${config.auto_generate_cover_letter ? 'bg-teal-500 justify-end' : 'bg-slate-600 justify-start'}`}
                  data-testid="config-cover-letter-toggle">
                  <div className="w-4 h-4 mx-0.5 rounded-full bg-white shadow" />
                </button>
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-300 mb-1.5 block">Max Applications Per Run</label>
                <select value={config.max_applications_per_run || 10}
                  onChange={e => saveConfig({ max_applications_per_run: Number(e.target.value) })}
                  className="bg-white/5 border border-white/10 rounded-md px-3 py-2 text-sm text-white w-full"
                  data-testid="config-max-apps">
                  {[5, 10, 15, 20, 25].map(n => <option key={n} value={n}>{n} jobs</option>)}
                </select>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
