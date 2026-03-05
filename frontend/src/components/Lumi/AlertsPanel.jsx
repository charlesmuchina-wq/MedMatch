import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { AlertTriangle, Activity, CheckCircle2, Sparkles, Loader2, X } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { API, ESY } from './constants';

export const AlertsPanel = ({ onClose, token }) => {
  const [alerts, setAlerts] = useState([]);
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('alerts');

  const loadAlerts = async () => { try { const res = await fetch(`${API}/api/lumi/ai/anomalies`, { headers: { 'Authorization': `Bearer ${token}` } }); if (res.ok) { const d = await res.json(); setAlerts(d.alerts || []); } } catch (e) {} };
  const loadDecisionCards = async () => { setLoading(true); try { const res = await fetch(`${API}/api/lumi/ai/decision-card`, { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } }); if (res.ok) { const d = await res.json(); setCards(d.cards || []); } } catch (e) {} setLoading(false); };
  const executeCardAction = async (cardId, actionType, payload) => { try { const res = await fetch(`${API}/api/lumi/ai/decision-card/${cardId}/action`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }, body: JSON.stringify({ action_type: actionType, payload }) }); if (res.ok) { const d = await res.json(); toast.success(d.message || 'Action executed'); setCards(prev => prev.map(c => c.id === cardId ? { ...c, status: 'resolved' } : c)); } } catch (e) { toast.error('Action failed'); } };

  useEffect(() => { loadAlerts(); }, []);

  const severityStyles = {
    critical: { bg: `${ESY.deepRed}10`, border: `${ESY.deepRed}25`, text: ESY.deepRed, icon: AlertTriangle },
    warning: { bg: '#FFF3E0', border: '#FFB74D40', text: '#E65100', icon: AlertTriangle },
    info: { bg: `${ESY.turquoise}10`, border: `${ESY.turquoise}25`, text: ESY.turquoise, icon: Activity },
  };
  const cardSeverityStyles = {
    critical: { gradient: `linear-gradient(135deg, ${ESY.deepRed}10, ${ESY.deepRedLight}05)`, border: `${ESY.deepRed}30` },
    warning: { gradient: `linear-gradient(135deg, ${ESY.pink}08, #FFF3E005)`, border: `${ESY.pink}30` },
    info: { gradient: `linear-gradient(135deg, ${ESY.turquoise}08, ${ESY.turquoiseLight}05)`, border: `${ESY.turquoise}30` },
  };

  return (
    <div className="w-[350px] border-l border-slate-200 bg-white flex flex-col h-full" data-testid="alerts-panel">
      <div className="h-14 flex items-center justify-between px-4 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-4 h-4" style={{ color: ESY.deepRed }} /><h3 className="text-sm font-semibold text-slate-900">Alerts & Decisions</h3>
          {alerts.length > 0 && <span className="min-w-[18px] h-[18px] flex items-center justify-center rounded-full text-[9px] font-bold text-white" style={{ backgroundColor: ESY.deepRed }}>{alerts.length}</span>}
        </div>
        <button onClick={onClose} className="p-1 hover:bg-slate-100 rounded-md"><X className="w-4 h-4 text-slate-500" /></button>
      </div>
      <div className="flex border-b border-slate-200">
        <button onClick={() => setActiveTab('alerts')} className={`flex-1 py-2.5 text-xs font-medium transition-colors ${activeTab === 'alerts' ? 'border-b-2 text-slate-900' : 'text-slate-400'}`} style={activeTab === 'alerts' ? { borderColor: ESY.deepRed, color: ESY.deepRed } : {}} data-testid="tab-alerts">Anomaly Alerts</button>
        <button onClick={() => { setActiveTab('cards'); if (cards.length === 0) loadDecisionCards(); }} className={`flex-1 py-2.5 text-xs font-medium transition-colors ${activeTab === 'cards' ? 'border-b-2 text-slate-900' : 'text-slate-400'}`} style={activeTab === 'cards' ? { borderColor: ESY.pink, color: ESY.pink } : {}} data-testid="tab-decisions">Decision Cards</button>
      </div>
      <ScrollArea className="flex-1">
        <div className="p-4 space-y-3">
          {activeTab === 'alerts' && (<>
            {alerts.length === 0 ? (<div className="text-center py-8"><CheckCircle2 className="w-10 h-10 mx-auto mb-2" style={{ color: ESY.turquoise }} /><p className="text-sm font-medium text-slate-700">All Clear</p><p className="text-xs text-slate-400 mt-1">No anomalies detected at this time</p></div>) : (
              alerts.map((alert) => { const s = severityStyles[alert.severity] || severityStyles.info; const Icon = s.icon; return (
                <div key={alert.id} className="p-3 rounded-lg border" style={{ backgroundColor: s.bg, borderColor: s.border }} data-testid={`alert-${alert.id}`}>
                  <div className="flex items-start gap-2"><Icon className="w-4 h-4 mt-0.5 flex-shrink-0" style={{ color: s.text }} /><div className="flex-1 min-w-0"><p className="text-xs font-semibold" style={{ color: s.text }}>{alert.title}</p><p className="text-[11px] text-slate-600 mt-1 leading-relaxed">{alert.description}</p>{alert.suggested_action && <p className="text-[10px] mt-2 font-medium" style={{ color: ESY.turquoise }}>Suggested: {alert.suggested_action}</p>}</div></div>
                </div>); })
            )}
            <button onClick={loadAlerts} className="w-full text-xs py-1.5 rounded-md hover:bg-slate-50 transition-colors" style={{ color: ESY.turquoise }}>Refresh Alerts</button>
          </>)}
          {activeTab === 'cards' && (<>
            {loading ? (<div className="flex items-center justify-center py-8"><Loader2 className="w-5 h-5 animate-spin" style={{ color: ESY.pink }} /></div>) : cards.length === 0 ? (
              <div className="text-center py-8"><button onClick={loadDecisionCards} className="w-full py-3 rounded-lg border text-sm font-medium transition-colors hover:opacity-90" style={{ borderColor: `${ESY.pink}30`, color: ESY.pink, backgroundColor: `${ESY.pink}05` }} data-testid="generate-cards-btn"><Sparkles className="w-4 h-4 inline mr-2" />Generate Decision Cards</button></div>
            ) : (cards.map((card) => { const cs = cardSeverityStyles[card.severity] || cardSeverityStyles.info; return (
              <div key={card.id} className={`rounded-xl border overflow-hidden ${card.status === 'resolved' ? 'opacity-50' : ''}`} style={{ background: cs.gradient, borderColor: cs.border }} data-testid={`card-${card.id}`}>
                <div className="p-4"><div className="flex items-center justify-between mb-2"><h4 className="text-xs font-bold text-slate-800">{card.title}</h4>{card.metric && <span className="text-lg font-bold" style={{ color: ESY.deepRed }}>{card.metric.value}</span>}</div><p className="text-[11px] text-slate-600 leading-relaxed">{card.description}</p>{card.metric?.label && <p className="text-[9px] text-slate-400 mt-1">{card.metric.label}</p>}</div>
                {card.actions?.length > 0 && card.status !== 'resolved' && (<div className="px-4 pb-3 flex flex-wrap gap-2">{card.actions.map((action, j) => (<button key={j} onClick={() => executeCardAction(card.id, action.action_type, action.payload)} className="px-3 py-1.5 rounded-md text-[10px] font-semibold text-white transition-all hover:opacity-90" style={{ background: action.action_type === 'escalate' ? ESY.deepRed : action.action_type === 'resolve' ? ESY.turquoise : ESY.pink }} data-testid={`card-action-${card.id}-${j}`}>{action.label}</button>))}</div>)}
                {card.status === 'resolved' && (<div className="px-4 pb-3"><span className="text-[10px] font-medium" style={{ color: ESY.turquoise }}>Resolved</span></div>)}
              </div>); }))}
          </>)}
        </div>
      </ScrollArea>
    </div>
  );
};
