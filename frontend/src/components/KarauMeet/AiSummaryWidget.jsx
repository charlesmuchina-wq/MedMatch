/**
 * AiSummaryWidget — AI Meeting Intelligence summary for KARAU dashboard
 * Extracted from KarauMeetDashboard.jsx
 */
import { useState, useEffect } from 'react';
import { Loader2, Sparkles, AlertCircle, CheckCircle2 } from 'lucide-react';
import { useTranslation } from '@/utils/i18n';

const API = process.env.REACT_APP_BACKEND_URL;

const AiSummaryWidget = () => {
  const { t } = useTranslation();
  const [aiSummary, setAiSummary] = useState(null);
  const [loadingAi, setLoadingAi] = useState(false);
  const [actionItems, setActionItems] = useState([]);

  const generateAiSummary = async () => {
    setLoadingAi(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API}/api/karau-meet/ai/enhanced-summary`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setAiSummary(data);
        setActionItems(data.action_items || []);
      }
    } catch (e) { console.error('AI summary error:', e); }
    setLoadingAi(false);
  };

  const loadActionItems = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API}/api/karau-meet/ai/action-items`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        if (data.items?.length > 0) setActionItems(data.items);
      }
    } catch (e) {}
  };

  const toggleItemStatus = async (itemId, currentStatus) => {
    const newStatus = currentStatus === 'done' ? 'open' : 'done';
    try {
      const token = localStorage.getItem('token');
      await fetch(`${API}/api/karau-meet/ai/action-items/${itemId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ status: newStatus })
      });
      setActionItems(prev => prev.map(i => i.id === itemId ? { ...i, status: newStatus } : i));
    } catch (e) {}
  };

  useEffect(() => { loadActionItems(); }, []);

  const priorityColors = {
    high: 'text-red-400 bg-red-500/10 border-red-500/20',
    medium: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
    low: 'text-slate-400 bg-slate-500/10 border-slate-500/20',
  };

  return (
    <div className="mt-3 pt-3 border-t border-white/[0.04]" data-testid="ai-summary-section">
      {!aiSummary ? (
        <button onClick={generateAiSummary} disabled={loadingAi}
          className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-gradient-to-r from-amber-600/10 to-orange-600/5 border border-amber-500/15 text-amber-300 text-xs font-medium hover:from-amber-600/15 hover:to-orange-600/10 transition-all"
          data-testid="generate-ai-summary">
          {loadingAi ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
          {loadingAi ? 'Analyzing meetings...' : 'Generate AI Meeting Intelligence'}
        </button>
      ) : (
        <div className="space-y-3">
          <div className="flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-xs font-semibold text-amber-300">AI Intelligence Report</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">{aiSummary.summary}</p>
          {aiSummary.key_decisions?.length > 0 && (
            <div className="space-y-1">
              <span className="text-[10px] font-semibold text-emerald-400 uppercase tracking-wider">Decisions</span>
              {aiSummary.key_decisions.map((d, i) => (
                <div key={i} className="flex items-start gap-2 text-xs text-slate-400">
                  <CheckCircle2 className="w-3 h-3 text-emerald-500 mt-0.5 flex-shrink-0" />
                  <span>{d}</span>
                </div>
              ))}
            </div>
          )}
          {aiSummary.risk_alerts?.length > 0 && (
            <div className="space-y-1">
              <span className="text-[10px] font-semibold text-red-400 uppercase tracking-wider">Risk Alerts</span>
              {aiSummary.risk_alerts.map((r, i) => (
                <div key={i} className="flex items-start gap-2 text-xs text-red-300/80">
                  <AlertCircle className="w-3 h-3 text-red-500 mt-0.5 flex-shrink-0" />
                  <span>{r}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
      {actionItems.length > 0 && (
        <div className="mt-3 pt-3 border-t border-white/[0.04]">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-semibold text-amber-400 uppercase tracking-wider">Action Items</span>
            <span className="text-[10px] text-slate-500">{actionItems.filter(i => i.status === 'done').length}/{actionItems.length} done</span>
          </div>
          <div className="space-y-1.5 max-h-40 overflow-auto">
            {actionItems.slice(0, 10).map((item) => (
              <div key={item.id} className={`flex items-start gap-2 p-2 rounded-lg border transition-all ${item.status === 'done' ? 'bg-white/[0.01] border-white/[0.03] opacity-60' : 'bg-white/[0.02] border-white/[0.05]'}`} data-testid={`action-item-${item.id}`}>
                <button onClick={() => toggleItemStatus(item.id, item.status)}
                  className={`w-4 h-4 mt-0.5 rounded border flex-shrink-0 flex items-center justify-center transition-colors ${item.status === 'done' ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-400' : 'border-slate-600 hover:border-amber-500/40'}`}
                  data-testid={`toggle-action-${item.id}`}>
                  {item.status === 'done' && <CheckCircle2 className="w-3 h-3" />}
                </button>
                <div className="flex-1 min-w-0">
                  <p className={`text-xs leading-relaxed ${item.status === 'done' ? 'text-slate-500 line-through' : 'text-slate-300'}`}>{item.task}</p>
                  <div className="flex items-center gap-2 mt-1">
                    {item.assignee && item.assignee !== 'Unassigned' && (
                      <span className="text-[9px] text-teal-400 bg-teal-500/10 px-1.5 py-0.5 rounded">{item.assignee}</span>
                    )}
                    {item.deadline && item.deadline !== 'TBD' && (
                      <span className="text-[9px] text-slate-500">{item.deadline}</span>
                    )}
                    {item.priority && (
                      <span className={`text-[9px] px-1.5 py-0.5 rounded border ${priorityColors[item.priority] || priorityColors.low}`}>{item.priority}</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AiSummaryWidget;
