import { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import {
  X, Loader2, Shield, Globe, CheckCircle, AlertTriangle,
  Lock, Eye, FileText, RefreshCw, ChevronDown, ChevronRight
} from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { API, ESY } from './constants';

const REGION_FLAGS = {
  'United States': '🇺🇸',
  'European Union': '🇪🇺',
  'United Kingdom': '🇬🇧',
  'Australia': '🇦🇺',
  'China': '🇨🇳',
  'Japan': '🇯🇵',
};

const TAB_LIST = [
  { key: 'overview', label: 'Posture', icon: Shield },
  { key: 'frameworks', label: 'Frameworks', icon: Globe },
  { key: 'controls', label: 'Controls', icon: Lock },
];

export const CompliancePanel = ({ isOpen, onClose, token }) => {
  const [tab, setTab] = useState('overview');
  const [frameworks, setFrameworks] = useState([]);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState({});

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [fwRes, stRes] = await Promise.all([
        fetch(`${API}/api/lumi/compliance/frameworks`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API}/api/lumi/compliance/status`, { headers: { Authorization: `Bearer ${token}` } }),
      ]);
      if (fwRes.ok) setFrameworks((await fwRes.json()).frameworks || []);
      if (stRes.ok) setStatus(await stRes.json());
    } catch (e) {
      toast.error('Failed to load compliance data');
    }
    setLoading(false);
  }, [token]);

  useEffect(() => { if (isOpen) load(); }, [isOpen, load]);

  const toggleExpand = (id) => setExpanded(prev => ({ ...prev, [id]: !prev[id] }));

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center" onClick={onClose}>
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" />
      <div className="relative bg-white rounded-2xl w-full max-w-2xl shadow-2xl border border-slate-200 overflow-hidden max-h-[85vh] flex flex-col" onClick={e => e.stopPropagation()} data-testid="compliance-panel">

        <div className="px-6 py-5 border-b border-slate-100 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: `linear-gradient(135deg, #00B894, ${ESY.turquoise})` }}>
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-black text-gray-900">Privacy & Compliance</h2>
              <p className="text-xs text-gray-600 font-medium">HIPAA, GDPR, PIPL, APPI, UK DPA, AU Privacy</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 hover:bg-slate-100 rounded-lg" data-testid="close-compliance">
            <X className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex items-center gap-1 px-6 pt-3 flex-shrink-0">
          {TAB_LIST.map(t => (
            <button key={t.key} onClick={() => setTab(t.key)}
              className={`flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-semibold transition-all ${tab === t.key ? 'bg-slate-900 text-white' : 'text-slate-600 hover:bg-slate-100'}`}
              data-testid={`compliance-tab-${t.key}`}>
              <t.icon className="w-3.5 h-3.5" />{t.label}
            </button>
          ))}
        </div>

        <ScrollArea className="flex-1 min-h-0">
          <div className="p-6">
            {loading ? (
              <div className="flex items-center justify-center py-12"><Loader2 className="w-6 h-6 animate-spin text-slate-400" /></div>
            ) : tab === 'overview' && status ? (
              <div className="space-y-5">
                {/* Score card */}
                <div className="bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-200 rounded-xl p-5">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-sm font-black text-gray-900">Compliance Score</h3>
                    <span className="text-3xl font-black text-emerald-600">{status.overall_score}%</span>
                  </div>
                  <div className="w-full bg-emerald-200 rounded-full h-2">
                    <div className="bg-emerald-500 h-2 rounded-full transition-all" style={{ width: `${status.overall_score}%` }} />
                  </div>
                  <p className="text-xs text-emerald-700 mt-2 font-medium">{status.frameworks_covered} regulatory frameworks covered</p>
                </div>

                {/* AI KARAU Reference */}
                {status.karau_compliance_reference && (
                  <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Shield className="w-4 h-4" style={{ color: ESY.turquoise }} />
                      <h3 className="text-sm font-bold text-gray-900">{status.karau_compliance_reference.name}</h3>
                    </div>
                    <p className="text-xs text-slate-600 mb-2">{status.karau_compliance_reference.description}</p>
                    <div className="flex flex-wrap gap-1.5">
                      {status.karau_compliance_reference.shared_controls.map(ctrl => (
                        <span key={ctrl} className="px-2 py-0.5 bg-white border border-slate-200 rounded text-[10px] font-semibold text-slate-600">{ctrl}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : tab === 'frameworks' ? (
              <div className="space-y-3">
                {frameworks.map(fw => (
                  <div key={fw.id} className="border border-slate-200 rounded-xl overflow-hidden" data-testid={`framework-${fw.id}`}>
                    <button onClick={() => toggleExpand(fw.id)} className="w-full flex items-center justify-between px-4 py-3.5 hover:bg-slate-50 transition-colors">
                      <div className="flex items-center gap-3">
                        <span className="text-xl">{REGION_FLAGS[fw.region] || '🌍'}</span>
                        <div className="text-left">
                          <h4 className="text-sm font-bold text-gray-900">{fw.name}</h4>
                          <p className="text-[11px] text-slate-500">{fw.description}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {fw.enabled ? (
                          <span className="flex items-center gap-1 px-2 py-0.5 bg-emerald-50 text-emerald-600 rounded-full text-[10px] font-bold"><CheckCircle className="w-3 h-3" />Active</span>
                        ) : (
                          <span className="flex items-center gap-1 px-2 py-0.5 bg-amber-50 text-amber-600 rounded-full text-[10px] font-bold"><AlertTriangle className="w-3 h-3" />Review</span>
                        )}
                        {expanded[fw.id] ? <ChevronDown className="w-4 h-4 text-slate-400" /> : <ChevronRight className="w-4 h-4 text-slate-400" />}
                      </div>
                    </button>
                    {expanded[fw.id] && (
                      <div className="px-4 pb-4 border-t border-slate-100">
                        <h5 className="text-xs font-bold text-slate-700 mt-3 mb-2">Requirements</h5>
                        <ul className="space-y-1.5">
                          {fw.requirements?.map((req, i) => (
                            <li key={i} className="flex items-start gap-2 text-xs text-slate-600">
                              <CheckCircle className="w-3 h-3 text-emerald-500 mt-0.5 flex-shrink-0" />
                              <span>{req}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : tab === 'controls' && status ? (
              <div className="space-y-2">
                <h3 className="text-sm font-black text-gray-900 mb-3">Platform Security Controls</h3>
                {Object.entries(status.platform_controls || {}).map(([key, ctrl]) => (
                  <div key={key} className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100">
                    <div className="flex items-center gap-2.5">
                      {ctrl.status === 'active' ? (
                        <div className="w-6 h-6 rounded-full bg-emerald-100 flex items-center justify-center"><CheckCircle className="w-3.5 h-3.5 text-emerald-600" /></div>
                      ) : (
                        <div className="w-6 h-6 rounded-full bg-amber-100 flex items-center justify-center"><AlertTriangle className="w-3.5 h-3.5 text-amber-600" /></div>
                      )}
                      <div>
                        <p className="text-xs font-bold text-gray-800">{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</p>
                        <p className="text-[10px] text-slate-500">{ctrl.details}</p>
                      </div>
                    </div>
                    <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold uppercase ${ctrl.status === 'active' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}`}>{ctrl.status}</span>
                  </div>
                ))}
              </div>
            ) : null}
          </div>
        </ScrollArea>
      </div>
    </div>
  );
};
