import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Shield, CheckCircle, Clock, AlertTriangle, Database, RefreshCw, Link2,
  Loader2, Settings, UserCheck, FileSearch, Lock, Globe, Plus, ChevronRight,
  Server, ArrowUpRight, Zap, Eye
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const STATUS_ICONS = { compliant: CheckCircle, in_progress: Clock, planned: AlertTriangle };
const STATUS_COLORS = {
  compliant: { badge: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30', icon: 'text-emerald-400', bar: 'bg-emerald-500' },
  in_progress: { badge: 'bg-amber-500/20 text-amber-400 border-amber-500/30', icon: 'text-amber-400', bar: 'bg-amber-500' },
  planned: { badge: 'bg-slate-500/20 text-slate-400 border-slate-500/30', icon: 'text-slate-400', bar: 'bg-slate-500' }
};
const CATEGORY_ICONS = { security: Lock, healthcare: Shield, privacy: Globe };
const CHECK_STATUSES = { pending: 'bg-amber-500/20 text-amber-400', completed: 'bg-emerald-500/20 text-emerald-400', failed: 'bg-red-500/20 text-red-400', in_progress: 'bg-blue-500/20 text-blue-400' };

function StatCard({ label, value, icon: Icon, accent }) {
  return (
    <div className="p-3 rounded-lg bg-slate-700/30 border border-slate-700/40">
      <div className="flex items-center gap-2 mb-1">
        {Icon && <Icon className={`w-3.5 h-3.5 ${accent || 'text-slate-500'}`} />}
        <span className="text-[10px] text-slate-400 uppercase tracking-wider">{label}</span>
      </div>
      <p className="text-lg font-bold text-white">{value}</p>
    </div>
  );
}

export default function PlatformSettingsPage() {
  const [tab, setTab] = useState('compliance');
  const [compliance, setCompliance] = useState(null);
  const [hrisConfig, setHrisConfig] = useState(null);
  const [syncs, setSyncs] = useState([]);
  const [bgChecks, setBgChecks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [showHrisConfig, setShowHrisConfig] = useState(false);
  const [showBgCheck, setShowBgCheck] = useState(false);
  const [configuring, setConfiguring] = useState(false);
  const [initiatingCheck, setInitiatingCheck] = useState(false);
  const [selectedCheck, setSelectedCheck] = useState(null);

  const [hrisForm, setHrisForm] = useState({
    provider: 'workday', api_url: '', api_key: '',
    sync_direction: 'bidirectional', sync_fields: ['employees', 'positions', 'departments']
  });
  const [bgForm, setBgForm] = useState({
    candidate_name: '', candidate_id: '', provider: 'checkr',
    check_types: ['identity', 'criminal', 'education', 'employment']
  });

  const fetchOpts = { credentials: 'include' };
  const postOpts = { credentials: 'include', headers: { 'Content-Type': 'application/json' } };

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/platform/compliance/status`).then(r => r.json()),
      fetch(`${API}/api/platform/hris/config`, fetchOpts).then(r => r.ok ? r.json() : {}).catch(() => ({})),
      fetch(`${API}/api/platform/hris/sync-history`, fetchOpts).then(r => r.ok ? r.json() : { syncs: [] }).catch(() => ({ syncs: [] })),
      fetch(`${API}/api/platform/background-checks`, fetchOpts).then(r => r.ok ? r.json() : { checks: [] }).catch(() => ({ checks: [] }))
    ]).then(([c, h, s, b]) => {
      setCompliance(c);
      setHrisConfig(h.config);
      setSyncs(s.syncs || []);
      setBgChecks(b.checks || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const triggerSync = async () => {
    setSyncing(true);
    try {
      const res = await fetch(`${API}/api/platform/hris/sync`, { method: 'POST', ...fetchOpts });
      if (res.ok) { const s = await res.json(); setSyncs([s, ...syncs]); }
    } catch (e) { console.error(e); }
    setSyncing(false);
  };

  const configureHris = async () => {
    if (!hrisForm.api_url.trim()) return;
    setConfiguring(true);
    try {
      const res = await fetch(`${API}/api/platform/hris/configure`, {
        method: 'POST', ...postOpts,
        body: JSON.stringify(hrisForm)
      });
      if (res.ok) {
        const config = await res.json();
        setHrisConfig(config);
        setShowHrisConfig(false);
      }
    } catch (e) { console.error(e); }
    setConfiguring(false);
  };

  const initiateBackgroundCheck = async () => {
    if (!bgForm.candidate_name.trim()) return;
    setInitiatingCheck(true);
    try {
      const res = await fetch(`${API}/api/platform/background-checks`, {
        method: 'POST', ...postOpts,
        body: JSON.stringify(bgForm)
      });
      if (res.ok) {
        const check = await res.json();
        setBgChecks([check, ...bgChecks]);
        setShowBgCheck(false);
        setBgForm({ candidate_name: '', candidate_id: '', provider: 'checkr', check_types: ['identity', 'criminal', 'education', 'employment'] });
      }
    } catch (e) { console.error(e); }
    setInitiatingCheck(false);
  };

  const toggleCheckType = (type) => {
    setBgForm(prev => ({
      ...prev,
      check_types: prev.check_types.includes(type)
        ? prev.check_types.filter(t => t !== type)
        : [...prev.check_types, type]
    }));
  };

  const toggleSyncField = (field) => {
    setHrisForm(prev => ({
      ...prev,
      sync_fields: prev.sync_fields.includes(field)
        ? prev.sync_fields.filter(f => f !== field)
        : [...prev.sync_fields, field]
    }));
  };

  if (loading) return <div className="min-h-screen bg-slate-900 flex items-center justify-center"><Loader2 className="w-8 h-8 text-teal-400 animate-spin" /></div>;

  const certs = compliance?.certifications || [];
  const compliantCount = certs.filter(c => c.status === 'compliant').length;
  const overallProgress = certs.length > 0 ? Math.round(certs.reduce((s, c) => s + c.progress, 0) / certs.length) : 0;

  const tabs = [
    { id: 'compliance', label: 'Compliance', icon: Shield, count: `${compliantCount}/${certs.length}` },
    { id: 'hris', label: 'HRIS Sync', icon: Link2, count: hrisConfig ? 'Connected' : 'Setup' },
    { id: 'background-checks', label: 'Background Checks', icon: UserCheck, count: bgChecks.length }
  ];

  return (
    <div className="min-h-screen bg-slate-900 p-4 md:p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-teal-500/20 to-blue-500/20 flex items-center justify-center">
            <Settings className="w-5 h-5 text-teal-400" />
          </div>
          <div>
            <h1 className="text-xl md:text-2xl font-bold text-white" data-testid="platform-settings-title">Platform Settings</h1>
            <p className="text-xs text-slate-400">Compliance, HRIS integration & background verification</p>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-2 mb-6 flex-wrap">
          {tabs.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-all border ${tab === t.id ? 'bg-teal-600/15 text-teal-400 border-teal-500/30 font-medium' : 'text-slate-400 border-slate-700/50 hover:border-slate-600'}`}
              data-testid={`tab-${t.id}`}>
              <t.icon className="w-4 h-4" /> {t.label}
              <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${tab === t.id ? 'bg-teal-500/20' : 'bg-slate-700/50'}`}>{t.count}</span>
            </button>
          ))}
        </div>

        {/* ============ COMPLIANCE TAB ============ */}
        {tab === 'compliance' && (
          <div className="space-y-5" data-testid="compliance-certs">
            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <StatCard label="Overall Progress" value={`${overallProgress}%`} icon={Shield} accent="text-teal-400" />
              <StatCard label="Compliant" value={compliantCount} icon={CheckCircle} accent="text-emerald-400" />
              <StatCard label="In Progress" value={certs.filter(c => c.status === 'in_progress').length} icon={Clock} accent="text-amber-400" />
              <StatCard label="Audit Events (24h)" value={compliance?.audit_trail?.last_24h || 0} icon={FileSearch} accent="text-blue-400" />
            </div>

            {/* Certifications */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
              {certs.map((cert, i) => {
                const Icon = STATUS_ICONS[cert.status] || Clock;
                const colors = STATUS_COLORS[cert.status] || STATUS_COLORS.planned;
                const CatIcon = CATEGORY_ICONS[cert.category] || Shield;
                return (
                  <Card key={i} className="bg-slate-800/60 border-slate-700/50 hover:border-slate-600/60 transition-all">
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2.5">
                          <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${cert.status === 'compliant' ? 'bg-emerald-500/15' : cert.status === 'in_progress' ? 'bg-amber-500/15' : 'bg-slate-700/50'}`}>
                            <CatIcon className={`w-4 h-4 ${colors.icon}`} />
                          </div>
                          <div>
                            <span className="text-white font-medium text-sm">{cert.name}</span>
                            <span className="text-[10px] text-slate-500 block capitalize">{cert.category}</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge className={`text-[10px] ${colors.badge}`}>{cert.status.replace('_', ' ')}</Badge>
                        </div>
                      </div>
                      <div className="relative">
                        <Progress value={cert.progress} className="h-2 bg-slate-700/50" />
                        <div className="flex items-center justify-between mt-1.5">
                          <span className="text-[10px] text-slate-500">{cert.progress}% complete</span>
                          <span className="text-[10px] text-slate-500">Target: {cert.target_date}</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            {/* Data Handling */}
            {compliance?.data_handling && (
              <Card className="bg-slate-800/60 border-slate-700/50">
                <CardHeader className="pb-3">
                  <CardTitle className="text-white text-sm flex items-center gap-2"><Lock className="w-4 h-4 text-teal-400" /> Data Handling & Privacy</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {Object.entries(compliance.data_handling).map(([k, v]) => (
                      <div key={k} className="flex items-center justify-between p-2.5 rounded-lg bg-slate-700/30 border border-slate-700/30">
                        <span className="text-xs text-slate-400 capitalize">{k.replace(/_/g, ' ')}</span>
                        {typeof v === 'boolean' ? (
                          <div className={`w-5 h-5 rounded-full flex items-center justify-center ${v ? 'bg-emerald-500/20' : 'bg-red-500/20'}`}>
                            {v ? <CheckCircle className="w-3 h-3 text-emerald-400" /> : <AlertTriangle className="w-3 h-3 text-red-400" />}
                          </div>
                        ) : <span className="text-xs text-white font-medium">{v}</span>}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* ============ HRIS TAB ============ */}
        {tab === 'hris' && (
          <div className="space-y-5">
            {/* Connection Status */}
            <Card className="bg-slate-800/60 border-slate-700/50">
              <CardContent className="p-5">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${hrisConfig ? 'bg-emerald-500/15' : 'bg-slate-700/50'}`}>
                      <Server className={`w-5 h-5 ${hrisConfig ? 'text-emerald-400' : 'text-slate-500'}`} />
                    </div>
                    <div>
                      <h3 className="text-white font-medium">HRIS Integration</h3>
                      <p className="text-xs text-slate-400">
                        {hrisConfig ? `Connected to ${hrisConfig.provider} (${hrisConfig.sync_direction})` : 'No HRIS system configured'}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    {hrisConfig && (
                      <Button size="sm" className="bg-teal-600 hover:bg-teal-500 h-8 text-xs" onClick={triggerSync} disabled={syncing} data-testid="sync-hris-btn">
                        {syncing ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : <RefreshCw className="w-3 h-3 mr-1" />} Sync Now
                      </Button>
                    )}
                    <Button size="sm" variant="outline" className="border-slate-600 text-slate-300 h-8 text-xs" onClick={() => setShowHrisConfig(true)} data-testid="configure-hris-btn">
                      <Settings className="w-3 h-3 mr-1" /> {hrisConfig ? 'Reconfigure' : 'Configure'}
                    </Button>
                  </div>
                </div>

                {hrisConfig && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div className="p-2.5 rounded-lg bg-slate-700/30 border border-slate-700/30">
                      <span className="text-[10px] text-slate-500">Provider</span>
                      <p className="text-sm text-white capitalize">{hrisConfig.provider}</p>
                    </div>
                    <div className="p-2.5 rounded-lg bg-slate-700/30 border border-slate-700/30">
                      <span className="text-[10px] text-slate-500">Status</span>
                      <p className="text-sm text-emerald-400">{hrisConfig.status || 'configured'}</p>
                    </div>
                    <div className="p-2.5 rounded-lg bg-slate-700/30 border border-slate-700/30">
                      <span className="text-[10px] text-slate-500">Direction</span>
                      <p className="text-sm text-white capitalize">{hrisConfig.sync_direction}</p>
                    </div>
                    <div className="p-2.5 rounded-lg bg-slate-700/30 border border-slate-700/30">
                      <span className="text-[10px] text-slate-500">Sync Fields</span>
                      <p className="text-sm text-white">{hrisConfig.sync_fields?.length || 0} fields</p>
                    </div>
                  </div>
                )}

                <p className="text-[10px] text-slate-500 mt-3">Supports: Workday, BambooHR, ADP, SAP SuccessFactors</p>
              </CardContent>
            </Card>

            {/* Sync History */}
            <div>
              <h3 className="text-sm font-medium text-slate-400 mb-3">Sync History ({syncs.length})</h3>
              {syncs.length === 0 ? (
                <div className="text-center py-8 text-slate-500 text-sm">No syncs yet. Configure HRIS and trigger a sync.</div>
              ) : (
                <div className="space-y-2">
                  {syncs.map(s => (
                    <Card key={s.id} className="bg-slate-800/40 border-slate-700/30">
                      <CardContent className="p-3 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="w-7 h-7 rounded-full bg-emerald-500/15 flex items-center justify-center">
                            <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                          </div>
                          <div>
                            <span className="text-sm text-white">Sync at {new Date(s.started_at).toLocaleString()}</span>
                            <span className="text-xs text-slate-500 block">
                              Imported: {s.records_synced?.imported || 0} | Updated: {s.records_synced?.updated || 0} | Duration: {s.sync_time_ms}ms
                            </span>
                          </div>
                        </div>
                        <Badge className="bg-emerald-500/20 text-emerald-400 text-[10px]">{s.status}</Badge>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </div>

            {/* HRIS Config Dialog */}
            <Dialog open={showHrisConfig} onOpenChange={setShowHrisConfig}>
              <DialogContent className="bg-slate-800 border-slate-700 text-white max-w-lg">
                <DialogHeader><DialogTitle>Configure HRIS Integration</DialogTitle></DialogHeader>
                <div className="space-y-4">
                  <div>
                    <label className="text-xs text-slate-400 mb-1 block">Provider</label>
                    <Select value={hrisForm.provider} onValueChange={v => setHrisForm({ ...hrisForm, provider: v })}>
                      <SelectTrigger className="bg-slate-700 border-slate-600 text-white"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="workday">Workday</SelectItem>
                        <SelectItem value="bamboohr">BambooHR</SelectItem>
                        <SelectItem value="adp">ADP</SelectItem>
                        <SelectItem value="successfactors">SAP SuccessFactors</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-xs text-slate-400 mb-1 block">API Endpoint URL *</label>
                    <Input value={hrisForm.api_url} onChange={e => setHrisForm({ ...hrisForm, api_url: e.target.value })}
                      placeholder="https://your-hris.example.com/api" className="bg-slate-700 border-slate-600 text-white" data-testid="hris-api-url" />
                  </div>
                  <div>
                    <label className="text-xs text-slate-400 mb-1 block">API Key</label>
                    <Input type="password" value={hrisForm.api_key} onChange={e => setHrisForm({ ...hrisForm, api_key: e.target.value })}
                      placeholder="sk-..." className="bg-slate-700 border-slate-600 text-white" />
                  </div>
                  <div>
                    <label className="text-xs text-slate-400 mb-1 block">Sync Direction</label>
                    <Select value={hrisForm.sync_direction} onValueChange={v => setHrisForm({ ...hrisForm, sync_direction: v })}>
                      <SelectTrigger className="bg-slate-700 border-slate-600 text-white"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="import">Import Only</SelectItem>
                        <SelectItem value="export">Export Only</SelectItem>
                        <SelectItem value="bidirectional">Bidirectional</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-xs text-slate-400 mb-2 block">Sync Fields</label>
                    <div className="flex gap-2 flex-wrap">
                      {['employees', 'positions', 'departments', 'locations', 'compensation', 'benefits'].map(f => (
                        <button key={f} onClick={() => toggleSyncField(f)}
                          className={`px-2.5 py-1 text-xs rounded-full border transition-all capitalize ${hrisForm.sync_fields.includes(f) ? 'border-teal-500 text-teal-400 bg-teal-500/10' : 'border-slate-600 text-slate-500'}`}>
                          {f}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="ghost" className="text-slate-400" onClick={() => setShowHrisConfig(false)}>Cancel</Button>
                  <Button className="bg-teal-600 hover:bg-teal-500" onClick={configureHris} disabled={configuring || !hrisForm.api_url.trim()} data-testid="save-hris-config">
                    {configuring ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : <Zap className="w-3 h-3 mr-1" />} Connect
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        )}

        {/* ============ BACKGROUND CHECKS TAB ============ */}
        {tab === 'background-checks' && (
          <div className="space-y-5" data-testid="bg-checks">
            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <StatCard label="Total Checks" value={bgChecks.length} icon={UserCheck} accent="text-blue-400" />
              <StatCard label="Pending" value={bgChecks.filter(c => c.status === 'pending').length} icon={Clock} accent="text-amber-400" />
              <StatCard label="Completed" value={bgChecks.filter(c => c.status === 'completed').length} icon={CheckCircle} accent="text-emerald-400" />
              <StatCard label="Providers" value="2" icon={Database} accent="text-violet-400" />
            </div>

            <div className="flex justify-end">
              <Button size="sm" className="bg-blue-600 hover:bg-blue-500 h-8 text-xs" onClick={() => setShowBgCheck(true)} data-testid="new-bg-check-btn">
                <Plus className="w-3 h-3 mr-1" /> New Background Check
              </Button>
            </div>

            {/* Checks List */}
            {bgChecks.length === 0 ? (
              <div className="text-center py-12 text-slate-500">
                <UserCheck className="w-10 h-10 mx-auto mb-3 opacity-15" />
                <p className="text-sm">No background checks initiated yet</p>
              </div>
            ) : (
              <div className="space-y-2">
                {bgChecks.map(c => (
                  <Card key={c.id} className="bg-slate-800/50 border-slate-700/40 hover:border-slate-600/60 transition-all cursor-pointer group"
                    onClick={() => setSelectedCheck(selectedCheck?.id === c.id ? null : c)}>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-500/30 to-violet-500/30 flex items-center justify-center text-sm font-bold text-blue-300">
                            {c.candidate_name?.charAt(0)?.toUpperCase()}
                          </div>
                          <div>
                            <span className="text-sm text-white font-medium">{c.candidate_name}</span>
                            <span className="text-xs text-slate-500 block">Provider: {c.provider} | Est: {c.estimated_completion}</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge className={`text-[10px] ${CHECK_STATUSES[c.status] || CHECK_STATUSES.pending}`}>{c.status}</Badge>
                          <ChevronRight className={`w-3.5 h-3.5 text-slate-500 transition-transform ${selectedCheck?.id === c.id ? 'rotate-90' : ''}`} />
                        </div>
                      </div>
                      <div className="flex gap-1.5 flex-wrap">
                        {c.check_types?.map(t => <span key={t} className="px-2 py-0.5 text-[10px] bg-slate-700/50 text-slate-300 rounded capitalize">{t}</span>)}
                      </div>

                      {/* Expanded Detail */}
                      {selectedCheck?.id === c.id && c.results && (
                        <div className="mt-3 pt-3 border-t border-slate-700/40 space-y-2">
                          <h4 className="text-xs font-medium text-slate-400">Check Results</h4>
                          {Object.entries(c.results).map(([type, result]) => (
                            <div key={type} className="flex items-center justify-between p-2 rounded-lg bg-slate-700/20">
                              <span className="text-xs text-slate-300 capitalize">{type} Verification</span>
                              <Badge className={`text-[10px] ${CHECK_STATUSES[result.status] || 'bg-slate-600'}`}>{result.status}</Badge>
                            </div>
                          ))}
                          <p className="text-[10px] text-slate-500">Requested: {new Date(c.requested_at).toLocaleDateString()}</p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}

            {/* New BG Check Dialog */}
            <Dialog open={showBgCheck} onOpenChange={setShowBgCheck}>
              <DialogContent className="bg-slate-800 border-slate-700 text-white max-w-lg">
                <DialogHeader><DialogTitle>Initiate Background Check</DialogTitle></DialogHeader>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="text-xs text-slate-400 mb-1 block">Candidate Name *</label>
                      <Input value={bgForm.candidate_name} onChange={e => setBgForm({ ...bgForm, candidate_name: e.target.value })}
                        placeholder="John Smith" className="bg-slate-700 border-slate-600 text-white" data-testid="bg-candidate-name" />
                    </div>
                    <div>
                      <label className="text-xs text-slate-400 mb-1 block">Candidate ID</label>
                      <Input value={bgForm.candidate_id} onChange={e => setBgForm({ ...bgForm, candidate_id: e.target.value })}
                        placeholder="CRM contact ID" className="bg-slate-700 border-slate-600 text-white" />
                    </div>
                  </div>
                  <div>
                    <label className="text-xs text-slate-400 mb-1 block">Verification Provider</label>
                    <Select value={bgForm.provider} onValueChange={v => setBgForm({ ...bgForm, provider: v })}>
                      <SelectTrigger className="bg-slate-700 border-slate-600 text-white"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="checkr">Checkr</SelectItem>
                        <SelectItem value="sterling">Sterling</SelectItem>
                        <SelectItem value="hireright">HireRight</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-xs text-slate-400 mb-2 block">Check Types</label>
                    <div className="grid grid-cols-2 gap-2">
                      {['identity', 'criminal', 'education', 'employment', 'credit', 'drug_test', 'reference', 'professional_license'].map(t => (
                        <button key={t} onClick={() => toggleCheckType(t)}
                          className={`flex items-center gap-2 px-3 py-2 rounded-lg border text-xs transition-all capitalize ${bgForm.check_types.includes(t) ? 'border-blue-500 text-blue-400 bg-blue-500/10' : 'border-slate-600 text-slate-500'}`}>
                          <div className={`w-3.5 h-3.5 rounded border ${bgForm.check_types.includes(t) ? 'bg-blue-500 border-blue-500' : 'border-slate-500'} flex items-center justify-center`}>
                            {bgForm.check_types.includes(t) && <CheckCircle className="w-2.5 h-2.5 text-white" />}
                          </div>
                          {t.replace('_', ' ')}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="ghost" className="text-slate-400" onClick={() => setShowBgCheck(false)}>Cancel</Button>
                  <Button className="bg-blue-600 hover:bg-blue-500" onClick={initiateBackgroundCheck}
                    disabled={initiatingCheck || !bgForm.candidate_name.trim() || bgForm.check_types.length === 0} data-testid="submit-bg-check">
                    {initiatingCheck ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : <UserCheck className="w-3 h-3 mr-1" />} Initiate Check
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        )}
      </div>
    </div>
  );
}
