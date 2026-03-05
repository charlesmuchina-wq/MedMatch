import { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import {
  X, Loader2, Shield, Clock, Filter, User,
  FileText, ChevronDown, Search, RefreshCw
} from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { API, ESY } from './constants';

const CATEGORY_COLORS = {
  retention: '#E17055',
  hold: ESY.deepRed,
  channel: ESY.turquoise,
  user: ESY.pink,
  moderation: '#6C5CE7',
  compliance: '#00B894',
  all: '#636E72',
};

export const AdminAuditPanel = ({ isOpen, onClose, token }) => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState('all');
  const [categories, setCategories] = useState([]);
  const [stats, setStats] = useState({});
  const [searchTerm, setSearchTerm] = useState('');

  const loadLogs = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/lumi/admin/audit-log?limit=200&category=${category}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setLogs(data.logs || []);
        setCategories(data.categories || []);
        setStats(data.stats || {});
      }
    } catch (e) {
      toast.error('Failed to load audit logs');
    }
    setLoading(false);
  }, [token, category]);

  useEffect(() => {
    if (isOpen) loadLogs();
  }, [isOpen, loadLogs]);

  const filtered = searchTerm
    ? logs.filter(l =>
        l.action?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        l.user_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        JSON.stringify(l.details || {}).toLowerCase().includes(searchTerm.toLowerCase())
      )
    : logs;

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center" onClick={onClose}>
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" />
      <div className="relative bg-white rounded-2xl w-full max-w-2xl shadow-2xl border border-slate-200 overflow-hidden max-h-[85vh] flex flex-col" onClick={e => e.stopPropagation()} data-testid="audit-panel">

        <div className="px-6 py-5 border-b border-slate-100 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.deepRed})` }}>
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-black text-gray-900">Admin Audit Log</h2>
              <p className="text-xs text-gray-600 font-medium">Track all administrative actions</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={loadLogs} className="p-1.5 hover:bg-slate-100 rounded-lg" data-testid="refresh-audit">
              <RefreshCw className={`w-4 h-4 text-gray-600 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <button onClick={onClose} className="p-1.5 hover:bg-slate-100 rounded-lg" data-testid="close-audit">
              <X className="w-5 h-5 text-gray-600" />
            </button>
          </div>
        </div>

        {/* Stats bar */}
        <div className="px-6 py-3 border-b border-slate-100 bg-slate-50/50 flex items-center gap-3 overflow-x-auto flex-shrink-0">
          <button onClick={() => setCategory('all')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold transition-all whitespace-nowrap ${category === 'all' ? 'bg-slate-700 text-white' : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-100'}`}
            data-testid="audit-filter-all">
            All ({Object.values(stats).reduce((a, b) => a + b, 0) || logs.length})
          </button>
          {categories.map(cat => (
            <button key={cat} onClick={() => setCategory(cat)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold transition-all whitespace-nowrap ${category === cat ? 'text-white' : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-100'}`}
              style={category === cat ? { backgroundColor: CATEGORY_COLORS[cat] || '#636E72' } : {}}
              data-testid={`audit-filter-${cat}`}>
              <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: CATEGORY_COLORS[cat] || '#636E72' }} />
              {cat} ({stats[cat] || 0})
            </button>
          ))}
        </div>

        {/* Search */}
        <div className="px-6 py-3 flex-shrink-0">
          <div className="flex items-center gap-2 bg-slate-50 rounded-lg px-3 py-2 border border-slate-200">
            <Search className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
            <input value={searchTerm} onChange={e => setSearchTerm(e.target.value)}
              placeholder="Search audit logs..."
              className="flex-1 text-xs bg-transparent outline-none text-slate-700 placeholder:text-slate-400"
              data-testid="audit-search" />
          </div>
        </div>

        {/* Log entries */}
        <ScrollArea className="flex-1 min-h-0">
          <div className="px-6 pb-4 space-y-1.5">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-6 h-6 animate-spin text-slate-400" />
              </div>
            ) : filtered.length === 0 ? (
              <div className="text-center py-12">
                <FileText className="w-10 h-10 text-slate-300 mx-auto mb-3" />
                <p className="text-sm text-slate-500 font-medium">No audit logs found</p>
                <p className="text-xs text-slate-400 mt-1">Admin actions will appear here</p>
              </div>
            ) : (
              filtered.map(log => (
                <div key={log.id} className="flex items-start gap-3 p-3 rounded-xl hover:bg-slate-50 transition-colors border border-transparent hover:border-slate-100" data-testid={`audit-entry-${log.id}`}>
                  <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5"
                    style={{ backgroundColor: `${CATEGORY_COLORS[log.category] || '#636E72'}15` }}>
                    <Shield className="w-3.5 h-3.5" style={{ color: CATEGORY_COLORS[log.category] || '#636E72' }} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className="text-sm font-semibold text-gray-900">{log.action}</span>
                      <span className="px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider"
                        style={{ backgroundColor: `${CATEGORY_COLORS[log.category] || '#636E72'}15`, color: CATEGORY_COLORS[log.category] || '#636E72' }}>
                        {log.category}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-slate-500">
                      <User className="w-3 h-3" />
                      <span>{log.user_name || log.user_id}</span>
                      <span className="text-slate-300">|</span>
                      <Clock className="w-3 h-3" />
                      <span>{new Date(log.timestamp).toLocaleString()}</span>
                    </div>
                    {log.details && Object.keys(log.details).length > 0 && (
                      <div className="mt-1.5 text-[11px] text-slate-500 bg-slate-50 rounded-lg px-2.5 py-1.5 font-mono">
                        {Object.entries(log.details).map(([k, v]) => (
                          <div key={k}><span className="text-slate-400">{k}:</span> <span className="text-slate-700">{typeof v === 'object' ? JSON.stringify(v) : String(v)}</span></div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </ScrollArea>
      </div>
    </div>
  );
};
