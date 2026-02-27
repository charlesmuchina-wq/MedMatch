import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Shield, CheckCircle, Clock, AlertTriangle, Database, RefreshCw, Link2, Loader2, Settings } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

export default function PlatformSettingsPage() {
  const [tab, setTab] = useState('compliance');
  const [compliance, setCompliance] = useState(null);
  const [hrisConfig, setHrisConfig] = useState(null);
  const [syncs, setSyncs] = useState([]);
  const [bgChecks, setBgChecks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const token = localStorage.getItem('token');
  const headers = { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` };

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/platform/compliance/status`).then(r => r.json()),
      token ? fetch(`${API}/api/platform/hris/config`, { headers }).then(r => r.ok ? r.json() : {}) : Promise.resolve({}),
      token ? fetch(`${API}/api/platform/hris/sync-history`, { headers }).then(r => r.ok ? r.json() : { syncs: [] }) : Promise.resolve({ syncs: [] }),
      token ? fetch(`${API}/api/platform/background-checks`, { headers }).then(r => r.ok ? r.json() : { checks: [] }) : Promise.resolve({ checks: [] })
    ]).then(([c, h, s, b]) => {
      setCompliance(c);
      setHrisConfig(h.config);
      setSyncs(s.syncs || []);
      setBgChecks(b.checks || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [token]);

  const triggerSync = async () => {
    setSyncing(true);
    const res = await fetch(`${API}/api/platform/hris/sync`, { method: 'POST', headers });
    if (res.ok) { const s = await res.json(); setSyncs([s, ...syncs]); }
    setSyncing(false);
  };

  if (loading) return <div className="min-h-screen bg-slate-900 flex items-center justify-center"><Loader2 className="w-8 h-8 text-turquoise animate-spin" /></div>;

  const certs = compliance?.certifications || [];
  const statusIcon = { compliant: CheckCircle, in_progress: Clock, planned: AlertTriangle };
  const statusColor = { compliant: 'text-emerald-400', in_progress: 'text-yellow-400', planned: 'text-slate-400' };

  return (
    <div className="min-h-screen bg-slate-900 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center gap-3 mb-8">
          <div className="p-2 bg-turquoise/10 rounded-lg"><Settings className="w-6 h-6 text-turquoise" /></div>
          <div>
            <h1 className="text-2xl font-bold text-white" data-testid="platform-settings-title">Platform Settings</h1>
            <p className="text-slate-400 text-sm">Compliance, HRIS sync, and background checks</p>
          </div>
        </div>

        <div className="flex gap-2 mb-6 flex-wrap">
          {['compliance', 'hris', 'background-checks'].map(t => (
            <Button key={t} variant={tab === t ? 'default' : 'ghost'}
              className={tab === t ? 'bg-turquoise' : 'text-slate-400'}
              onClick={() => setTab(t)} data-testid={`tab-${t}`}>
              {t === 'compliance' ? <Shield className="w-4 h-4 mr-1.5" /> : t === 'hris' ? <Link2 className="w-4 h-4 mr-1.5" /> : <Database className="w-4 h-4 mr-1.5" />}
              {t === 'compliance' ? 'Compliance' : t === 'hris' ? 'HRIS Sync' : 'Background Checks'}
            </Button>
          ))}
        </div>

        {tab === 'compliance' && (
          <div className="space-y-4" data-testid="compliance-certs">
            {certs.map((cert, i) => {
              const Icon = statusIcon[cert.status] || Clock;
              return (
                <Card key={i} className="bg-slate-800 border-slate-700">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Icon className={`w-4 h-4 ${statusColor[cert.status]}`} />
                        <span className="text-white font-medium">{cert.name}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className={cert.status === 'compliant' ? 'bg-emerald-500/20 text-emerald-400' : cert.status === 'in_progress' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-slate-600 text-slate-300'}>
                          {cert.status.replace('_', ' ')}
                        </Badge>
                        <span className="text-xs text-slate-500">Target: {cert.target_date}</span>
                      </div>
                    </div>
                    <Progress value={cert.progress} className="h-2 bg-slate-700" />
                    <span className="text-xs text-slate-500 mt-1 block">{cert.progress}% complete</span>
                  </CardContent>
                </Card>
              );
            })}
            {compliance?.data_handling && (
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader><CardTitle className="text-white text-base">Data Handling</CardTitle></CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-3">
                    {Object.entries(compliance.data_handling).map(([k, v]) => (
                      <div key={k} className="flex items-center justify-between py-1.5">
                        <span className="text-sm text-slate-400 capitalize">{k.replace(/_/g, ' ')}</span>
                        <span className="text-sm text-white">{typeof v === 'boolean' ? (v ? 'Yes' : 'No') : v}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {tab === 'hris' && (
          <div className="space-y-4">
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader><div className="flex items-center justify-between">
                <CardTitle className="text-white text-base">HRIS Integration</CardTitle>
                <Button size="sm" className="bg-turquoise hover:bg-turquoise/80" onClick={triggerSync} disabled={syncing} data-testid="sync-hris-btn">
                  {syncing ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : <RefreshCw className="w-3 h-3 mr-1" />} Sync Now
                </Button>
              </div></CardHeader>
              <CardContent>
                <p className="text-sm text-slate-400 mb-3">
                  {hrisConfig ? `Connected to ${hrisConfig.provider} (${hrisConfig.sync_direction})` : 'No HRIS configured. Connect your HR system to sync employee data.'}
                </p>
                <p className="text-xs text-slate-500">Supports: Workday, BambooHR, ADP, SAP SuccessFactors</p>
              </CardContent>
            </Card>
            <h3 className="text-sm font-medium text-slate-400">Sync History</h3>
            {syncs.length === 0 ? <p className="text-slate-500 text-sm">No syncs yet</p> : syncs.map(s => (
              <Card key={s.id} className="bg-slate-800 border-slate-700">
                <CardContent className="p-3 flex items-center justify-between">
                  <span className="text-sm text-slate-300">Sync at {new Date(s.started_at).toLocaleString()}</span>
                  <Badge className="bg-emerald-500/20 text-emerald-400">{s.status}</Badge>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {tab === 'background-checks' && (
          <div className="space-y-3" data-testid="bg-checks">
            {bgChecks.length === 0 ? (
              <Card className="bg-slate-800 border-slate-700"><CardContent className="py-12 text-center text-slate-500"><Database className="w-10 h-10 mx-auto mb-2 opacity-30" /><p>No background checks initiated</p></CardContent></Card>
            ) : bgChecks.map(c => (
              <Card key={c.id} className="bg-slate-800 border-slate-700">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-medium">{c.candidate_name}</span>
                    <Badge className={c.status === 'completed' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-yellow-500/20 text-yellow-400'}>{c.status}</Badge>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {c.check_types?.map(t => <Badge key={t} className="text-xs bg-slate-700 text-slate-300">{t}</Badge>)}
                  </div>
                  <p className="text-xs text-slate-500 mt-2">Provider: {c.provider} | Est: {c.estimated_completion}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
