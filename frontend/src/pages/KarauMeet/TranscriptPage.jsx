import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { ArrowLeft, Search, Loader2, FileText, Sparkles, Download, ListChecks, CheckCircle2, Circle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

const API = process.env.REACT_APP_BACKEND_URL;

const authHeaders = () => {
  const h = {};
  const t = localStorage.getItem('access_token');
  if (t) h['Authorization'] = `Bearer ${t}`;
  return h;
};

export default function TranscriptPage() {
  const { meetingId } = useParams();
  const navigate = useNavigate();
  const [lines, setLines] = useState([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState('');
  const [summarizing, setSummarizing] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [tasks, setTasks] = useState([]);
  const [extracting, setExtracting] = useState(false);

  const load = useCallback(async (q = '') => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/karau-meet/meetings/${meetingId}/captions?q=${encodeURIComponent(q)}`, {
        headers: authHeaders(), credentials: 'include',
      });
      if (res.ok) {
        const d = await res.json();
        setLines(d.lines || []);
      }
    } catch {}
    setLoading(false);
  }, [meetingId]);

  useEffect(() => { load(); }, [load]);

  useEffect(() => {
    const id = setTimeout(() => load(query), 400);
    return () => clearTimeout(id);
  }, [query, load]);

  const generateSummary = async () => {
    setSummarizing(true);
    try {
      const res = await fetch(`${API}/api/karau-meet/meetings/${meetingId}/captions/summary`, {
        method: 'POST', headers: authHeaders(), credentials: 'include',
      });
      const d = await res.json();
      if (res.ok) setSummary(d.summary);
      else toast.error(d.detail || 'Summary failed');
    } catch { toast.error('Summary failed'); }
    setSummarizing(false);
  };

  const exportPdf = async () => {
    setExporting(true);
    try {
      const res = await fetch(`${API}/api/karau-meet/meetings/${meetingId}/captions/export.pdf`, {
        headers: authHeaders(), credentials: 'include',
      });
      if (!res.ok) { const d = await res.json().catch(() => ({})); toast.error(d.detail || 'Export failed'); }
      else {
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url; a.download = `transcript_${meetingId}.pdf`; a.click();
        URL.revokeObjectURL(url);
      }
    } catch { toast.error('Export failed'); }
    setExporting(false);
  };

  const extractTasks = async () => {
    setExtracting(true);
    try {
      const res = await fetch(`${API}/api/karau-meet/meetings/${meetingId}/captions`, {
        headers: authHeaders(), credentials: 'include',
      });
      const all = res.ok ? (await res.json()).lines || [] : [];
      const transcript = all.map(l => `${l.speaker}: ${l.text}`).join('\n');
      const r2 = await fetch(`${API}/api/agents/extract-worklist`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeaders() },
        credentials: 'include',
        body: JSON.stringify({ transcript, source_label: `Meeting ${meetingId}` }),
      });
      const d = await r2.json();
      if (r2.ok) {
        setTasks(d.tasks || []);
        toast.success(`${d.extracted} task${d.extracted === 1 ? '' : 's'} created — also visible in your Agents worklist`);
      } else toast.error(d.detail || 'Task extraction failed');
    } catch { toast.error('Task extraction failed'); }
    setExtracting(false);
  };

  const toggleTask = async (task) => {
    const status = task.status === 'done' ? 'open' : 'done';
    setTasks(prev => prev.map(t => t.id === task.id ? { ...t, status } : t));
    try {
      await fetch(`${API}/api/agents/tasks/${task.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', ...authHeaders() },
        credentials: 'include',
        body: JSON.stringify({ status }),
      });
    } catch {}
  };


  return (
    <div className="max-w-3xl mx-auto px-6 py-8" data-testid="transcript-page">
      <div className="flex items-center gap-3 mb-6">
        <Button variant="ghost" size="sm" onClick={() => navigate(-1)} className="text-slate-400 hover:text-white" data-testid="transcript-back-btn">
          <ArrowLeft className="w-4 h-4" />
        </Button>
        <FileText className="w-5 h-5 text-purple-400" />
        <div className="flex-1">
          <h1 className="text-lg font-semibold text-white">Meeting Transcript</h1>
          <p className="text-xs text-slate-500">Live captions saved from meeting {meetingId}</p>
        </div>
        <Button size="sm" onClick={generateSummary} disabled={summarizing || lines.length === 0}
          className="bg-gradient-to-r from-purple-600 to-violet-600 rounded-xl text-xs" data-testid="transcript-summary-btn">
          {summarizing ? <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5 mr-1.5" />}
          AI Summary
        </Button>
        <Button size="sm" variant="outline" onClick={extractTasks} disabled={extracting || lines.length === 0}
          className="border-white/10 text-teal-300 hover:bg-teal-500/10 rounded-xl text-xs" data-testid="transcript-tasks-btn">
          {extracting ? <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" /> : <ListChecks className="w-3.5 h-3.5 mr-1.5" />}
          Extract Tasks
        </Button>
        <Button size="sm" variant="outline" onClick={exportPdf} disabled={exporting || lines.length === 0}
          className="border-white/10 text-slate-300 hover:bg-white/5 rounded-xl text-xs" data-testid="transcript-export-btn">
          {exporting ? <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" /> : <Download className="w-3.5 h-3.5 mr-1.5" />}
          PDF
        </Button>
      </div>
      {tasks.length > 0 && (
        <div className="mb-6 p-4 rounded-2xl bg-teal-500/10 border border-teal-500/20" data-testid="transcript-tasks-panel">
          <div className="flex items-center gap-2 mb-3">
            <ListChecks className="w-4 h-4 text-teal-400" />
            <span className="text-sm font-semibold text-teal-300">Action Items ({tasks.length})</span>
          </div>
          <div className="space-y-2">
            {tasks.map((t) => (
              <button key={t.id} onClick={() => toggleTask(t)} className="w-full flex items-start gap-2.5 text-left group" data-testid={`transcript-task-${t.id}`}>
                {t.status === 'done'
                  ? <CheckCircle2 className="w-4 h-4 text-teal-400 mt-0.5 flex-shrink-0" />
                  : <Circle className="w-4 h-4 text-slate-500 mt-0.5 flex-shrink-0 group-hover:text-teal-400" />}
                <div>
                  <span className={`text-sm ${t.status === 'done' ? 'text-slate-500 line-through' : 'text-slate-200'}`}>{t.title}</span>
                  {t.assignee && <span className="ml-2 text-[11px] px-1.5 py-0.5 rounded bg-white/5 text-teal-300">@{t.assignee}</span>}
                  {t.priority && t.priority !== 'medium' && <span className={`ml-1.5 text-[11px] ${t.priority === 'high' ? 'text-rose-400' : 'text-slate-500'}`}>{t.priority}</span>}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
      {summary && (
        <div className="mb-6 p-4 rounded-2xl bg-purple-500/10 border border-purple-500/20" data-testid="transcript-summary-panel">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="w-4 h-4 text-purple-400" />
            <span className="text-sm font-semibold text-purple-300">AI Summary</span>
          </div>
          <div className="text-sm text-slate-200 whitespace-pre-wrap">{summary.replace(/\*\*/g, '')}</div>
        </div>
      )}
      <div className="relative mb-5">
        <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search the transcript…"
          className="pl-9 bg-white/5 border-white/10 text-white placeholder:text-slate-500 rounded-xl"
          data-testid="transcript-search-input"
        />
      </div>
      {loading ? (
        <div className="flex justify-center py-16"><Loader2 className="w-6 h-6 animate-spin text-purple-400" /></div>
      ) : lines.length === 0 ? (
        <div className="text-center py-16 text-slate-500 text-sm" data-testid="transcript-empty">
          {query ? 'No caption lines match your search.' : 'No captions saved yet. Turn on CC during a live meeting to build the transcript.'}
        </div>
      ) : (
        <div className="space-y-3" data-testid="transcript-lines">
          {lines.map((l) => (
            <div key={l.id} className="flex gap-3 items-baseline" data-testid={`transcript-line-${l.id}`}>
              <span className="text-[11px] text-slate-500 w-16 flex-shrink-0 tabular-nums">
                {new Date(l.ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
              <div>
                <span className="text-teal-400 text-xs font-semibold mr-2">{l.speaker}</span>
                <span className="text-slate-200 text-sm">{l.text}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
