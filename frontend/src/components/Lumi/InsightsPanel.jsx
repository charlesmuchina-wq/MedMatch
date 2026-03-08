import { useState, useEffect } from 'react';
import { X, BarChart3, MessageSquare, Hash, Video, Clock, Loader2, Brain, Lightbulb, Bell, Shield, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { API, ESY } from './constants';

const TRIGGER_ICONS = { unread_overload: MessageSquare, inactive_channels: Hash, morning_routine: Clock, end_of_day: Clock, scheduled_messages: Bell };
const SUGGESTION_ICONS = { bot_suggestion: Brain, meeting_suggestion: Video, wellbeing: Clock, security: Shield };
const PRIORITY_COLORS = { high: 'bg-red-50 text-red-700 border-red-100', medium: 'bg-amber-50 text-amber-700 border-amber-100', low: 'bg-slate-50 text-slate-600 border-slate-100' };

const InsightsPanel = ({ token, onClose, onAction }) => {
  const [insights, setInsights] = useState(null);
  const [triggers, setTriggers] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadAll(); }, []);

  const loadAll = async () => {
    try {
      const [iRes, tRes, sRes] = await Promise.all([
        fetch(`${API}/api/lumi/behavior/usage-insights`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API}/api/lumi/behavior/context-triggers`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API}/api/lumi/behavior/smart-suggestions`, { headers: { Authorization: `Bearer ${token}` } })
      ]);
      if (iRes.ok) setInsights(await iRes.json());
      if (tRes.ok) setTriggers((await tRes.json()).triggers || []);
      if (sRes.ok) setSuggestions((await sRes.json()).suggestions || []);
    } catch {}
    setLoading(false);
  };

  const handleAction = (action) => {
    if (onAction) onAction(action);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 max-h-[85vh] flex flex-col overflow-hidden" onClick={e => e.stopPropagation()} data-testid="insights-panel">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #6C5CE7, #00CEC9)' }}>
              <BarChart3 className="w-4 h-4 text-white" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-900">Insights & Suggestions</h3>
              <p className="text-[11px] text-slate-500">Your personalized intelligence feed</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 hover:bg-slate-100 rounded-lg" data-testid="close-insights"><X className="w-4 h-4 text-slate-500" /></button>
        </div>

        <ScrollArea className="flex-1">
          {loading ? <div className="flex justify-center py-16"><Loader2 className="w-5 h-5 animate-spin text-slate-400" /></div> : (
            <div className="p-4 space-y-5">
              {/* Usage Stats */}
              {insights && (
                <div data-testid="usage-stats">
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">This Week</h4>
                  <div className="grid grid-cols-3 gap-2">
                    <div className="p-3 rounded-xl bg-slate-50 text-center">
                      <p className="text-lg font-bold text-slate-900">{insights.messages_sent}</p>
                      <p className="text-[10px] text-slate-500">Messages</p>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-50 text-center">
                      <p className="text-lg font-bold text-slate-900">{insights.active_channels}</p>
                      <p className="text-[10px] text-slate-500">Channels</p>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-50 text-center">
                      <p className="text-lg font-bold text-slate-900">{insights.meetings_attended}</p>
                      <p className="text-[10px] text-slate-500">Meetings</p>
                    </div>
                  </div>
                  <div className="mt-2 flex items-center gap-2 px-1">
                    <Zap className="w-3 h-3 text-amber-500" />
                    <span className="text-[11px] text-slate-600">Engagement Score: <strong>{insights.engagement_score}/100</strong></span>
                  </div>
                </div>
              )}

              {/* Context Triggers */}
              {triggers.length > 0 && (
                <div data-testid="context-triggers">
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Needs Attention</h4>
                  <div className="space-y-2">
                    {triggers.map(t => {
                      const Icon = TRIGGER_ICONS[t.type] || Bell;
                      const pc = PRIORITY_COLORS[t.priority] || PRIORITY_COLORS.low;
                      return (
                        <div key={t.trigger_id} className={`p-3 rounded-xl border ${pc} cursor-pointer hover:opacity-80 transition-opacity`}
                          onClick={() => handleAction(t.action)} data-testid={`trigger-${t.type}`}>
                          <div className="flex items-start gap-2.5">
                            <Icon className="w-4 h-4 mt-0.5 flex-shrink-0" />
                            <div>
                              <p className="text-xs font-semibold">{t.title}</p>
                              <p className="text-[11px] mt-0.5 opacity-80">{t.message}</p>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Smart Suggestions */}
              {suggestions.length > 0 && (
                <div data-testid="smart-suggestions">
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Suggestions</h4>
                  <div className="space-y-2">
                    {suggestions.map(s => {
                      const Icon = SUGGESTION_ICONS[s.type] || Lightbulb;
                      return (
                        <div key={s.id} className="p-3 rounded-xl border border-slate-100 hover:border-[#00CEC9]/30 cursor-pointer transition-all group"
                          onClick={() => handleAction(s.action)} data-testid={`suggestion-${s.type}`}>
                          <div className="flex items-start gap-2.5">
                            <div className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5" style={{ background: `${ESY.turquoise}15` }}>
                              <Icon className="w-3.5 h-3.5" style={{ color: ESY.turquoise }} />
                            </div>
                            <div>
                              <p className="text-xs font-semibold text-slate-800">{s.title}</p>
                              <p className="text-[11px] text-slate-500 mt-0.5">{s.description}</p>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {triggers.length === 0 && suggestions.length === 0 && (
                <div className="text-center py-8">
                  <BarChart3 className="w-8 h-8 text-slate-300 mx-auto mb-3" />
                  <p className="text-sm text-slate-500">All caught up! No triggers or suggestions right now.</p>
                </div>
              )}
            </div>
          )}
        </ScrollArea>
      </div>
    </div>
  );
};

export default InsightsPanel;
