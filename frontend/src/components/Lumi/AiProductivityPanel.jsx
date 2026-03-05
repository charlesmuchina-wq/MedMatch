import { useState } from 'react';
import { toast } from 'sonner';
import {
  Brain, Activity, ListTodo, FileBarChart, Sparkles,
  AlertTriangle, CheckCircle2, Loader2, X
} from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { API } from './constants';

export const AiProductivityPanel = ({ channelId, channelName, onClose, token }) => {
  const [activeTab, setActiveTab] = useState('sentiment');
  const [sentiment, setSentiment] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyzeSentiment = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/lumi/ai/sentiment/${channelId}`, { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) setSentiment(await res.json());
    } catch (e) { toast.error('Analysis failed'); }
    setLoading(false);
  };

  const extractTasks = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/lumi/ai/extract-tasks/${channelId}`, { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) { const d = await res.json(); setTasks(d.tasks || []); }
    } catch (e) { toast.error('Extraction failed'); }
    setLoading(false);
  };

  const generateReport = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/lumi/ai/report/${channelId}`, { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) setReport(await res.json());
    } catch (e) { toast.error('Report failed'); }
    setLoading(false);
  };

  const toggleTask = async (taskId, current) => {
    const newStatus = current === 'done' ? 'open' : 'done';
    try {
      await fetch(`${API}/api/lumi/ai/tasks/${taskId}`, { method: 'PUT', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }, body: JSON.stringify({ status: newStatus }) });
      setTasks(prev => prev.map(t => t.id === taskId ? { ...t, status: newStatus } : t));
    } catch (e) {}
  };

  const scoreColor = (score) => score >= 70 ? 'text-emerald-500' : score >= 40 ? 'text-amber-500' : 'text-red-500';
  const priorityBadge = { high: 'bg-red-50 text-red-600 border-red-200', medium: 'bg-amber-50 text-amber-600 border-amber-200', low: 'bg-slate-50 text-slate-500 border-slate-200' };
  const tabs = [{ key: 'sentiment', label: 'Sentiment', icon: Activity }, { key: 'tasks', label: 'Tasks', icon: ListTodo }, { key: 'report', label: 'Report', icon: FileBarChart }];

  return (
    <div className="w-[350px] border-l border-slate-200 bg-white flex flex-col h-full" data-testid="ai-panel">
      <div className="h-14 flex items-center justify-between px-4 border-b border-slate-200">
        <div className="flex items-center gap-2"><Brain className="w-4 h-4 text-[#008080]" /><h3 className="text-sm font-semibold text-slate-900">AI Insights</h3></div>
        <button onClick={onClose} className="p-1 hover:bg-slate-100 rounded-md"><X className="w-4 h-4 text-slate-500" /></button>
      </div>
      <div className="flex border-b border-slate-200">
        {tabs.map(tab => (
          <button key={tab.key} onClick={() => setActiveTab(tab.key)}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 text-xs font-medium transition-colors ${activeTab === tab.key ? 'text-[#008080] border-b-2 border-[#008080]' : 'text-slate-400 hover:text-slate-600'}`}
            data-testid={`ai-tab-${tab.key}`}><tab.icon className="w-3.5 h-3.5" />{tab.label}</button>
        ))}
      </div>
      <ScrollArea className="flex-1">
        <div className="p-4">
          {activeTab === 'sentiment' && (
            <div className="space-y-4">
              {!sentiment ? (
                <button onClick={analyzeSentiment} disabled={loading} className="w-full flex items-center justify-center gap-2 py-3 rounded-lg bg-[#008080]/5 border border-[#008080]/20 text-[#008080] text-sm font-medium hover:bg-[#008080]/10 transition-colors" data-testid="analyze-sentiment-btn">
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Activity className="w-4 h-4" />}{loading ? 'Analyzing...' : 'Analyze Channel Mood'}
                </button>
              ) : (<>
                <div className="flex items-center justify-between p-4 rounded-lg bg-slate-50 border border-slate-100">
                  <div><p className="text-xs text-slate-500 mb-1">Team Morale Score</p><p className={`text-3xl font-bold ${scoreColor(sentiment.score)}`}>{sentiment.score}</p></div>
                  <div className="text-right"><span className={`text-sm font-semibold ${scoreColor(sentiment.score)}`}>{sentiment.label}</span><p className="text-[10px] text-slate-400 mt-0.5">{sentiment.engagement_level} engagement</p></div>
                </div>
                <p className="text-xs text-slate-600 leading-relaxed">{sentiment.summary}</p>
                {sentiment.highlights?.length > 0 && (<div className="space-y-1"><span className="text-[10px] font-semibold text-emerald-600 uppercase tracking-wider">Highlights</span>{sentiment.highlights.map((h, i) => (<div key={i} className="flex items-start gap-2 text-xs text-slate-600"><CheckCircle2 className="w-3 h-3 text-emerald-500 mt-0.5 flex-shrink-0" /><span>{h}</span></div>))}</div>)}
                {sentiment.alerts?.length > 0 && (<div className="space-y-1"><span className="text-[10px] font-semibold text-amber-600 uppercase tracking-wider">Attention Needed</span>{sentiment.alerts.map((a, i) => (<div key={i} className="flex items-start gap-2 text-xs text-amber-700"><AlertTriangle className="w-3 h-3 text-amber-500 mt-0.5 flex-shrink-0" /><span>{a}</span></div>))}</div>)}
                <button onClick={() => { setSentiment(null); analyzeSentiment(); }} className="w-full text-xs text-slate-400 hover:text-[#008080] py-1 transition-colors">Refresh Analysis</button>
              </>)}
            </div>
          )}
          {activeTab === 'tasks' && (
            <div className="space-y-3">
              <button onClick={extractTasks} disabled={loading} className="w-full flex items-center justify-center gap-2 py-2.5 rounded-lg bg-[#008080]/5 border border-[#008080]/20 text-[#008080] text-sm font-medium hover:bg-[#008080]/10 transition-colors" data-testid="extract-tasks-btn">
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}{loading ? 'Extracting...' : 'Extract Tasks from Chat'}
              </button>
              {tasks.length > 0 && (<div className="space-y-2">
                <div className="flex items-center justify-between"><span className="text-xs font-semibold text-slate-700">{tasks.length} tasks found</span><span className="text-[10px] text-slate-400">{tasks.filter(t => t.status === 'done').length} done</span></div>
                {tasks.map(task => (
                  <div key={task.id} className={`p-3 rounded-lg border transition-all ${task.status === 'done' ? 'bg-slate-50 border-slate-100 opacity-70' : 'bg-white border-slate-200'}`} data-testid={`task-${task.id}`}>
                    <div className="flex items-start gap-2">
                      <button onClick={() => toggleTask(task.id, task.status)} className={`w-4 h-4 mt-0.5 rounded border flex-shrink-0 flex items-center justify-center ${task.status === 'done' ? 'bg-[#008080]/20 border-[#008080]/40 text-[#008080]' : 'border-slate-300 hover:border-[#008080]'}`} data-testid={`toggle-task-${task.id}`}>{task.status === 'done' && <CheckCircle2 className="w-3 h-3" />}</button>
                      <div className="flex-1 min-w-0">
                        <p className={`text-xs leading-relaxed ${task.status === 'done' ? 'text-slate-400 line-through' : 'text-slate-800'}`}>{task.task}</p>
                        <div className="flex flex-wrap items-center gap-1.5 mt-1.5">
                          {task.assignee && task.assignee !== 'Unassigned' && <span className="text-[9px] bg-[#008080]/10 text-[#008080] px-1.5 py-0.5 rounded font-medium">{task.assignee}</span>}
                          {task.deadline && task.deadline !== 'TBD' && <span className="text-[9px] text-slate-400 bg-slate-50 px-1.5 py-0.5 rounded">{task.deadline}</span>}
                          {task.priority && <span className={`text-[9px] px-1.5 py-0.5 rounded border ${priorityBadge[task.priority] || priorityBadge.low}`}>{task.priority}</span>}
                        </div>
                        {task.context && <p className="text-[10px] text-slate-400 mt-1 italic">"{task.context}"</p>}
                      </div>
                    </div>
                  </div>
                ))}
              </div>)}
            </div>
          )}
          {activeTab === 'report' && (
            <div className="space-y-3">
              {!report ? (
                <button onClick={generateReport} disabled={loading} className="w-full flex items-center justify-center gap-2 py-3 rounded-lg bg-[#008080]/5 border border-[#008080]/20 text-[#008080] text-sm font-medium hover:bg-[#008080]/10 transition-colors" data-testid="generate-report-btn">
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileBarChart className="w-4 h-4" />}{loading ? 'Generating...' : 'Generate Weekly Report'}
                </button>
              ) : (<div className="space-y-3">
                <div className="flex items-center justify-between"><span className="text-xs font-semibold text-slate-700">#{report.channel_name} Report</span><span className="text-[10px] text-slate-400">{report.stats?.messages || 0} msgs / {report.stats?.participants || 0} people</span></div>
                <div className="text-xs text-slate-700 leading-relaxed whitespace-pre-wrap bg-slate-50 p-4 rounded-lg border border-slate-100 max-h-[400px] overflow-auto" data-testid="report-content">{report.report}</div>
                <button onClick={() => setReport(null)} className="w-full text-xs text-slate-400 hover:text-[#008080] py-1 transition-colors">Generate New Report</button>
              </div>)}
            </div>
          )}
        </div>
      </ScrollArea>
    </div>
  );
};
