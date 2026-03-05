import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import {
  X, Loader2, Shield, Lock, Clock, Hash, Trash2,
  AlertTriangle, Scale, FileText, Plus, Settings,
  CheckCircle, XCircle, Send, ChevronDown, ChevronRight,
  User, Mail, Building
} from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { API, ESY } from './constants';

const HOLD_TYPE_META = {
  legal: { label: 'Legal Hold', icon: Scale, color: ESY.deepRed, desc: 'Indefinite preservation until released', badge: 'INDEFINITE' },
  contractual: { label: 'Contractual Hold', icon: FileText, color: '#E17055', desc: 'Custom duration preservation', badge: 'CUSTOM' },
};

const STATUS_META = {
  pending: { label: 'Pending Approval', color: '#F59E0B', bg: '#FEF3C7', icon: Clock },
  approved: { label: 'Approved', color: '#10B981', bg: '#D1FAE5', icon: CheckCircle },
  rejected: { label: 'Rejected', color: '#EF4444', bg: '#FEE2E2', icon: XCircle },
};

const TAB_LIST = [
  { key: 'overview', label: 'Overview', icon: Shield },
  { key: 'requests', label: 'Requests', icon: Send },
  { key: 'settings', label: 'Admin Settings', icon: Settings },
];

export const RetentionPanel = ({ onClose, token }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState('overview');
  const [showHoldForm, setShowHoldForm] = useState(null);
  const [holdType, setHoldType] = useState('legal');
  const [holdReason, setHoldReason] = useState('');
  const [holdDays, setHoldDays] = useState(90);
  const [submitting, setSubmitting] = useState(false);
  const [orgSettings, setOrgSettings] = useState(null);
  const [settingsLoading, setSettingsLoading] = useState(false);
  const [savingSettings, setSavingSettings] = useState(false);
  const [expandedChannels, setExpandedChannels] = useState({});

  const hdrs = { 'Authorization': `Bearer ${token}` };
  const jhdrs = { ...hdrs, 'Content-Type': 'application/json' };

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/lumi/admin/retention`, { headers: hdrs });
      if (res.ok) setData(await res.json());
    } catch { toast.error('Failed to load'); }
    setLoading(false);
  };

  const loadOrgSettings = async () => {
    setSettingsLoading(true);
    try {
      const res = await fetch(`${API}/api/lumi/admin/org-settings`, { headers: hdrs });
      if (res.ok) setOrgSettings(await res.json());
    } catch { toast.error('Failed to load settings'); }
    setSettingsLoading(false);
  };

  useEffect(() => { loadData(); loadOrgSettings(); }, []);

  const saveOrgSettings = async () => {
    setSavingSettings(true);
    try {
      const res = await fetch(`${API}/api/lumi/admin/org-settings`, { method: 'PUT', headers: jhdrs, body: JSON.stringify(orgSettings) });
      if (res.ok) { toast.success('Admin settings saved'); loadData(); }
    } catch { toast.error('Save failed'); }
    setSavingSettings(false);
  };

  const submitHoldRequest = async (channelId) => {
    if (!holdReason.trim()) { toast.error('Reason is required'); return; }
    setSubmitting(true);
    try {
      const res = await fetch(`${API}/api/lumi/admin/hold`, {
        method: 'POST', headers: jhdrs,
        body: JSON.stringify({ channel_id: channelId, hold_type: holdType, reason: holdReason, duration_days: holdType === 'contractual' ? holdDays : 0 })
      });
      const result = await res.json();
      if (res.ok) {
        toast.success(result.message || 'Hold request submitted for approval');
        setShowHoldForm(null); setHoldReason(''); setHoldDays(90);
        loadData();
      } else {
        toast.error(result.detail || 'Submission failed');
        if (result.detail?.includes('admin settings')) setTab('settings');
      }
    } catch { toast.error('Submission failed'); }
    setSubmitting(false);
  };

  const reviewRequest = async (requestId, action, note = '') => {
    try {
      const res = await fetch(`${API}/api/lumi/admin/hold-requests/${requestId}`, {
        method: 'PUT', headers: jhdrs, body: JSON.stringify({ action, note })
      });
      if (res.ok) { toast.success(`Request ${action}d`); loadData(); }
    } catch { toast.error('Review failed'); }
  };

  const releaseHold = async (holdId) => {
    try {
      await fetch(`${API}/api/lumi/admin/hold/${holdId}`, { method: 'DELETE', headers: hdrs });
      toast.success('Hold released');
      loadData();
    } catch { toast.error('Release failed'); }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-white rounded-2xl w-full max-w-2xl max-h-[85vh] shadow-2xl border border-slate-200 flex flex-col overflow-hidden" onClick={e => e.stopPropagation()} data-testid="retention-panel">

        {/* Header */}
        <div className="px-6 py-5 border-b border-slate-100 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center shadow-sm" style={{ backgroundColor: ESY.deepRed }}>
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-black text-gray-900">Message Retention & Privacy</h2>
              <p className="text-xs text-gray-600 font-medium">90-day auto-delete policy with privileged hold management</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 hover:bg-slate-100 rounded-lg" data-testid="close-retention"><X className="w-5 h-5 text-gray-600" /></button>
        </div>

        {/* Tabs */}
        <div className="px-6 py-2 border-b border-slate-100 flex gap-1 bg-slate-50">
          {TAB_LIST.map(t => {
            const Icon = t.icon;
            const pendingCount = t.key === 'requests' ? (data?.pending_requests?.length || 0) : 0;
            return (
              <button key={t.key} onClick={() => setTab(t.key)}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-bold transition-all ${tab === t.key ? 'bg-white shadow-sm text-gray-900 border border-slate-200' : 'text-gray-500 hover:text-gray-700 hover:bg-white/50'}`}
                data-testid={`tab-${t.key}`}>
                <Icon className="w-3.5 h-3.5" />
                {t.label}
                {pendingCount > 0 && <span className="ml-1 w-5 h-5 rounded-full bg-amber-500 text-white text-[10px] flex items-center justify-center font-black">{pendingCount}</span>}
              </button>
            );
          })}
        </div>

        <ScrollArea className="flex-1">
          {loading ? (
            <div className="flex items-center justify-center py-10"><Loader2 className="w-6 h-6 animate-spin" style={{ color: ESY.turquoise }} /></div>
          ) : tab === 'overview' ? (
            <div className="p-5 space-y-4">
              {/* Global policy banner */}
              <div className="rounded-xl border-2 border-emerald-200 bg-emerald-50/50 p-4 flex items-center gap-3" data-testid="global-retention-banner">
                <div className="w-10 h-10 rounded-xl bg-emerald-500 flex items-center justify-center flex-shrink-0">
                  <Clock className="w-5 h-5 text-white" />
                </div>
                <div>
                  <p className="text-sm font-black text-gray-900">Global Auto-Delete: {data?.global_retention_days || 90} Days</p>
                  <p className="text-xs text-gray-600 mt-0.5">All messages are automatically deleted after {data?.global_retention_days || 90} days. Channels with active holds are exempt.</p>
                </div>
              </div>

              {!data?.org_settings_configured && (
                <div className="rounded-xl border-2 border-amber-200 bg-amber-50 p-3 flex items-center gap-3 cursor-pointer hover:border-amber-300 transition-colors" onClick={() => setTab('settings')} data-testid="settings-warning">
                  <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0" />
                  <div>
                    <p className="text-xs font-bold text-amber-800">Admin settings not configured</p>
                    <p className="text-[11px] text-amber-700">Set IT Admin and Manager contacts before creating hold requests.</p>
                  </div>
                </div>
              )}

              {/* Channels with hold status */}
              {data?.channels?.map(ch => {
                const holds = data.holds[ch.id] || [];
                const hasLegalHold = holds.some(h => h.hold_type === 'legal');
                const hasContractualHold = holds.some(h => h.hold_type === 'contractual');
                const isExpanded = expandedChannels[ch.id];

                return (
                  <div key={ch.id} className={`rounded-xl border-2 overflow-hidden transition-colors ${hasLegalHold ? 'border-red-200 bg-red-50/30' : hasContractualHold ? 'border-orange-200 bg-orange-50/20' : 'border-slate-100'}`} data-testid={`retention-ch-${ch.id}`}>
                    <div className="flex items-center gap-3 px-4 py-3">
                      <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center flex-shrink-0">
                        <Hash className="w-3.5 h-3.5 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-bold text-gray-900">{ch.name}</span>
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-gray-600 font-medium capitalize">{ch.channel_type}</span>
                          {hasLegalHold && <span className="text-[9px] px-2 py-0.5 rounded-full font-black text-white" style={{ backgroundColor: ESY.deepRed }} data-testid={`legal-badge-${ch.id}`}>LEGAL HOLD</span>}
                          {hasContractualHold && <span className="text-[9px] px-2 py-0.5 rounded-full font-black text-white" style={{ backgroundColor: '#E17055' }} data-testid={`contract-badge-${ch.id}`}>CONTRACT HOLD</span>}
                        </div>
                        <p className="text-[10px] text-gray-500 mt-0.5">
                          {hasLegalHold ? 'Auto-delete suspended (legal hold)' : hasContractualHold ? 'Auto-delete suspended (contractual hold)' : `Auto-deletes after ${data?.global_retention_days || 90} days`}
                        </p>
                      </div>

                      {holds.length > 0 && (
                        <button onClick={() => setExpandedChannels(prev => ({ ...prev, [ch.id]: !prev[ch.id] }))}
                          className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-slate-100 rounded-lg">
                          {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                        </button>
                      )}

                      <button onClick={() => setShowHoldForm(showHoldForm === ch.id ? null : ch.id)}
                        className="p-2 rounded-lg text-gray-500 hover:bg-slate-100 hover:text-gray-700 transition-colors"
                        title="Request Hold" data-testid={`add-hold-${ch.id}`}>
                        <Plus className="w-4 h-4" />
                      </button>
                    </div>

                    {/* Active holds (expanded) */}
                    {isExpanded && holds.length > 0 && (
                      <div className="px-4 pb-3 space-y-1.5">
                        {holds.map(hold => {
                          const meta = HOLD_TYPE_META[hold.hold_type] || HOLD_TYPE_META.legal;
                          const HoldIcon = meta.icon;
                          return (
                            <div key={hold.id} className="flex items-center gap-2.5 p-2.5 rounded-lg border" style={{ borderColor: `${meta.color}30`, backgroundColor: `${meta.color}08` }} data-testid={`hold-${hold.id}`}>
                              <HoldIcon className="w-4 h-4 flex-shrink-0" style={{ color: meta.color }} />
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-1.5">
                                  <span className="text-xs font-bold text-gray-900">{meta.label}</span>
                                  <span className="text-[9px] px-1.5 py-0.5 rounded font-bold text-white" style={{ backgroundColor: meta.color }}>{meta.badge}</span>
                                </div>
                                <p className="text-[10px] text-gray-600 mt-0.5">{hold.reason || 'No reason specified'}</p>
                                {hold.hold_type === 'contractual' && hold.duration_days > 0 && (
                                  <p className="text-[9px] text-gray-500 mt-0.5">Duration: {hold.duration_days} days {hold.expires_at ? `· Expires: ${new Date(hold.expires_at).toLocaleDateString()}` : ''}</p>
                                )}
                              </div>
                              <button onClick={() => releaseHold(hold.id)} className="p-1.5 rounded-lg text-red-400 hover:bg-red-50 hover:text-red-600 transition-colors" title="Release Hold" data-testid={`release-hold-${hold.id}`}>
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          );
                        })}
                      </div>
                    )}

                    {/* Hold request form */}
                    {showHoldForm === ch.id && (
                      <div className="px-4 pb-4 border-t border-slate-100 pt-3 bg-slate-50/50" data-testid={`hold-form-${ch.id}`}>
                        <p className="text-xs font-bold text-gray-900 mb-1">Request Hold for #{ch.name}</p>
                        <p className="text-[10px] text-gray-500 mb-3">This request will be sent to IT Admin and Manager for approval.</p>
                        <div className="flex gap-2 mb-2">
                          {Object.entries(HOLD_TYPE_META).map(([type, meta]) => {
                            const Icon = meta.icon;
                            return (
                              <button key={type} onClick={() => setHoldType(type)}
                                className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-bold transition-all border-2 ${holdType === type ? 'text-white border-transparent shadow-sm' : 'bg-white text-gray-600 border-slate-200 hover:border-slate-300'}`}
                                style={holdType === type ? { backgroundColor: meta.color } : {}}
                                data-testid={`hold-type-${type}`}>
                                <Icon className="w-3.5 h-3.5" />{meta.label}
                              </button>
                            );
                          })}
                        </div>
                        <Input value={holdReason} onChange={e => setHoldReason(e.target.value)} placeholder="Reason for hold request..."
                          className="mb-2 border-2 border-slate-200 text-sm font-medium" data-testid="hold-reason-input" />
                        {holdType === 'contractual' && (
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-xs text-gray-700 font-semibold">Duration:</span>
                            <Input type="number" value={holdDays} onChange={e => setHoldDays(parseInt(e.target.value) || 0)} min={1}
                              className="w-24 border-2 border-slate-200 text-sm font-medium" data-testid="hold-days-input" />
                            <span className="text-xs text-gray-600 font-medium">days</span>
                          </div>
                        )}
                        {holdType === 'legal' && (
                          <div className="flex items-center gap-2 mb-2 px-3 py-2 rounded-lg bg-red-50 border border-red-200">
                            <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" style={{ color: ESY.deepRed }} />
                            <span className="text-[11px] text-red-800 font-semibold">Legal holds are indefinite and prevent all message deletion until released.</span>
                          </div>
                        )}
                        <div className="flex gap-2">
                          <Button variant="ghost" onClick={() => setShowHoldForm(null)} className="flex-1 text-gray-500">Cancel</Button>
                          <Button onClick={() => submitHoldRequest(ch.id)} disabled={!holdReason.trim() || submitting}
                            className="flex-1 text-white font-bold" style={{ backgroundColor: HOLD_TYPE_META[holdType].color }}
                            data-testid="submit-hold-request-btn">
                            {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4 mr-1" />}
                            Submit Request
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          ) : tab === 'requests' ? (
            <div className="p-5 space-y-3">
              {data?.all_requests?.length === 0 ? (
                <div className="text-center py-10">
                  <Send className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-sm font-bold text-gray-600">No hold requests yet</p>
                  <p className="text-xs text-gray-500 mt-1">Submit a hold request from the Overview tab</p>
                </div>
              ) : data?.all_requests?.map(req => {
                const meta = HOLD_TYPE_META[req.hold_type] || HOLD_TYPE_META.legal;
                const statusMeta = STATUS_META[req.status] || STATUS_META.pending;
                const StatusIcon = statusMeta.icon;
                const HoldIcon = meta.icon;
                return (
                  <div key={req.id} className="rounded-xl border-2 border-slate-100 overflow-hidden" data-testid={`request-${req.id}`}>
                    <div className="flex items-center gap-3 px-4 py-3">
                      <HoldIcon className="w-5 h-5 flex-shrink-0" style={{ color: meta.color }} />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-sm font-bold text-gray-900">{meta.label}</span>
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-gray-600 font-medium">#{req.channel_name}</span>
                          <span className="text-[9px] px-2 py-0.5 rounded-full font-bold flex items-center gap-1" style={{ backgroundColor: statusMeta.bg, color: statusMeta.color }}>
                            <StatusIcon className="w-3 h-3" />{statusMeta.label}
                          </span>
                        </div>
                        <p className="text-[11px] text-gray-600 mt-1">{req.reason}</p>
                        <div className="flex items-center gap-3 mt-1.5 text-[10px] text-gray-500">
                          <span>By: {req.requested_by_name}</span>
                          <span>{new Date(req.created_at).toLocaleDateString()}</span>
                          {req.hold_type === 'contractual' && <span>{req.duration_days} days</span>}
                        </div>
                        <div className="flex items-center gap-2 mt-1 text-[10px] text-gray-400">
                          <Mail className="w-3 h-3" /><span>IT: {req.it_admin_email}</span>
                          <span>| Mgr: {req.manager_email}</span>
                        </div>
                        {req.review_note && <p className="text-[10px] text-gray-500 mt-1 italic">Note: {req.review_note}</p>}
                      </div>
                    </div>
                    {req.status === 'pending' && (
                      <div className="flex gap-2 px-4 pb-3">
                        <Button size="sm" onClick={() => reviewRequest(req.id, 'approve')}
                          className="flex-1 bg-emerald-500 hover:bg-emerald-600 text-white text-xs font-bold"
                          data-testid={`approve-${req.id}`}>
                          <CheckCircle className="w-3.5 h-3.5 mr-1" />Approve
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => reviewRequest(req.id, 'reject')}
                          className="flex-1 border-red-200 text-red-600 hover:bg-red-50 text-xs font-bold"
                          data-testid={`reject-${req.id}`}>
                          <XCircle className="w-3.5 h-3.5 mr-1" />Reject
                        </Button>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            /* Admin Settings Tab */
            <div className="p-5 space-y-5">
              <div className="rounded-xl border-2 border-slate-200 p-4">
                <h3 className="text-sm font-black text-gray-900 mb-1 flex items-center gap-2">
                  <Settings className="w-4 h-4" style={{ color: ESY.turquoise }} />
                  Organization Administration Settings
                </h3>
                <p className="text-[11px] text-gray-500 mb-4">Required for hold request approval workflow. Hold requests are routed to these contacts.</p>

                {settingsLoading ? (
                  <div className="flex items-center justify-center py-6"><Loader2 className="w-5 h-5 animate-spin" style={{ color: ESY.turquoise }} /></div>
                ) : orgSettings && (
                  <div className="space-y-4">
                    <div>
                      <p className="text-xs font-bold text-gray-800 mb-2 flex items-center gap-1.5"><User className="w-3.5 h-3.5" style={{ color: ESY.deepRed }} /> IT Admin</p>
                      <div className="grid grid-cols-2 gap-2">
                        <Input value={orgSettings.it_admin_name} onChange={e => setOrgSettings(p => ({ ...p, it_admin_name: e.target.value }))}
                          placeholder="IT Admin Name" className="text-sm border-2" data-testid="org-it-admin-name" />
                        <Input value={orgSettings.it_admin_email} onChange={e => setOrgSettings(p => ({ ...p, it_admin_email: e.target.value }))}
                          placeholder="IT Admin Email" type="email" className="text-sm border-2" data-testid="org-it-admin-email" />
                      </div>
                    </div>
                    <div>
                      <p className="text-xs font-bold text-gray-800 mb-2 flex items-center gap-1.5"><User className="w-3.5 h-3.5" style={{ color: ESY.pink }} /> Manager</p>
                      <div className="grid grid-cols-2 gap-2">
                        <Input value={orgSettings.manager_name} onChange={e => setOrgSettings(p => ({ ...p, manager_name: e.target.value }))}
                          placeholder="Manager Name" className="text-sm border-2" data-testid="org-manager-name" />
                        <Input value={orgSettings.manager_email} onChange={e => setOrgSettings(p => ({ ...p, manager_email: e.target.value }))}
                          placeholder="Manager Email" type="email" className="text-sm border-2" data-testid="org-manager-email" />
                      </div>
                    </div>
                    <div>
                      <p className="text-xs font-bold text-gray-800 mb-2 flex items-center gap-1.5"><Building className="w-3.5 h-3.5" style={{ color: ESY.turquoise }} /> Additional Info</p>
                      <div className="grid grid-cols-2 gap-2">
                        <Input value={orgSettings.department} onChange={e => setOrgSettings(p => ({ ...p, department: e.target.value }))}
                          placeholder="Department" className="text-sm border-2" data-testid="org-department" />
                        <Input value={orgSettings.compliance_officer} onChange={e => setOrgSettings(p => ({ ...p, compliance_officer: e.target.value }))}
                          placeholder="Compliance Officer" className="text-sm border-2" data-testid="org-compliance-officer" />
                      </div>
                    </div>
                    <Button onClick={saveOrgSettings} disabled={savingSettings || !orgSettings.it_admin_email}
                      className="w-full text-white font-bold" style={{ backgroundColor: ESY.turquoise }}
                      data-testid="save-org-settings-btn">
                      {savingSettings ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <CheckCircle className="w-4 h-4 mr-1" />}
                      Save Settings
                    </Button>
                  </div>
                )}
              </div>
            </div>
          )}
        </ScrollArea>
      </div>
    </div>
  );
};
