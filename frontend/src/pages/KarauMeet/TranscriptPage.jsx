import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Search, Loader2, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

const API = process.env.REACT_APP_BACKEND_URL;

export default function TranscriptPage() {
  const { meetingId } = useParams();
  const navigate = useNavigate();
  const [lines, setLines] = useState([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);

  const load = useCallback(async (q = '') => {
    setLoading(true);
    const headers = {};
    const t = localStorage.getItem('access_token');
    if (t) headers['Authorization'] = `Bearer ${t}`;
    try {
      const res = await fetch(`${API}/api/karau-meet/meetings/${meetingId}/captions?q=${encodeURIComponent(q)}`, {
        headers, credentials: 'include',
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

  return (
    <div className="max-w-3xl mx-auto px-6 py-8" data-testid="transcript-page">
      <div className="flex items-center gap-3 mb-6">
        <Button variant="ghost" size="sm" onClick={() => navigate(-1)} className="text-slate-400 hover:text-white" data-testid="transcript-back-btn">
          <ArrowLeft className="w-4 h-4" />
        </Button>
        <FileText className="w-5 h-5 text-purple-400" />
        <div>
          <h1 className="text-lg font-semibold text-white">Meeting Transcript</h1>
          <p className="text-xs text-slate-500">Live captions saved from meeting {meetingId}</p>
        </div>
      </div>
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
