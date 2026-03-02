import { useState, useEffect, useCallback } from 'react';
import { BarChart, ListChecks, MessageSquare, Clock, Plus, Check, Send, Star, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

const POLL_TYPES = [
  { id: 'multiple_choice', label: 'Poll', icon: BarChart },
  { id: 'quiz', label: 'Quiz', icon: ListChecks },
  { id: 'word_cloud', label: 'Word Cloud', icon: MessageSquare },
  { id: 'rating', label: 'Rating', icon: Star },
];

export default function PollsChallengesPanel({ meetingId }) {
  const [polls, setPolls] = useState([]);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({ type: 'multiple_choice', question: '', options: ['', ''], correctIdx: 0, timeLimit: 0 });
  const [loading, setLoading] = useState(true);

  const fetchPolls = useCallback(async () => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/polls/${meetingId}/active`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) setPolls((await res.json()).polls || []);
    } catch {}
    setLoading(false);
  }, [meetingId]);

  useEffect(() => { fetchPolls(); const i = setInterval(fetchPolls, 8000); return () => clearInterval(i); }, [fetchPolls]);

  const createPoll = async () => {
    const token = localStorage.getItem('token');
    const opts = form.options.filter(o => o.trim()).map((text, i) => ({ text, id: `opt-${i}` }));
    if (!form.question.trim()) return toast.error('Question required');
    if ((form.type === 'multiple_choice' || form.type === 'quiz') && opts.length < 2) return toast.error('Need at least 2 options');

    try {
      const res = await fetch(`${API}/api/karau/polls/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({
          meeting_id: meetingId,
          question: form.question,
          poll_type: form.type,
          options: opts,
          correct_answer_id: form.type === 'quiz' ? `opt-${form.correctIdx}` : null,
          time_limit_seconds: form.timeLimit,
          points: 5
        })
      });
      if (res.ok) {
        toast.success('Poll created');
        setCreating(false);
        setForm({ type: 'multiple_choice', question: '', options: ['', ''], correctIdx: 0, timeLimit: 0 });
        fetchPolls();
      }
    } catch {}
  };

  const vote = async (pollId, optionId, textResponse, rating) => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/polls/${pollId}/vote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ option_id: optionId, text_response: textResponse, rating })
      });
      if (res.ok) {
        const d = await res.json();
        if (d.is_correct === true) toast.success(`Correct! +${d.points_earned} pts`);
        else if (d.is_correct === false) toast.error('Incorrect');
        else toast.success('Vote recorded');
        fetchPolls();
      } else {
        const err = await res.json().catch(() => ({}));
        toast.info(err.detail || 'Vote failed');
      }
    } catch {}
  };

  const closePoll = async (pollId) => {
    const token = localStorage.getItem('token');
    await fetch(`${API}/api/karau/polls/${pollId}/close`, {
      method: 'POST', headers: { 'Authorization': `Bearer ${token}` }
    });
    fetchPolls();
  };

  if (loading) return <div className="p-3 text-[9px] text-slate-500">Loading polls...</div>;

  return (
    <div className="flex-1 flex flex-col overflow-hidden" data-testid="polls-panel">
      <div className="p-2.5 border-b border-white/5">
        <h3 className="text-xs font-semibold text-white flex items-center gap-1.5">
          <BarChart className="w-3.5 h-3.5 text-yellow-400" />
          Polls & Challenges
        </h3>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {/* Create Toggle */}
        {!creating ? (
          <Button size="sm" onClick={() => setCreating(true)}
            className="w-full h-6 text-[9px] bg-yellow-500/80 hover:bg-yellow-400 rounded-lg" data-testid="create-poll-btn">
            <Plus className="w-3 h-3 mr-1" />New Poll / Challenge
          </Button>
        ) : (
          <div className="p-2 bg-yellow-500/5 border border-yellow-500/15 rounded-lg space-y-1.5" data-testid="poll-form">
            {/* Type selector */}
            <div className="flex gap-1">
              {POLL_TYPES.map(pt => (
                <button key={pt.id} onClick={() => setForm({ ...form, type: pt.id })}
                  className={`flex-1 p-1 rounded-lg border text-center text-[8px] ${
                    form.type === pt.id ? 'bg-yellow-500/10 border-yellow-500/20 text-yellow-300' : 'border-white/5 text-slate-400'
                  }`} data-testid={`poll-type-${pt.id}`}>
                  <pt.icon className="w-3 h-3 mx-auto mb-0.5" />{pt.label}
                </button>
              ))}
            </div>

            <Input value={form.question} onChange={e => setForm({ ...form, question: e.target.value })}
              placeholder="Your question..." className="bg-karau-bg/60 border-white/10 text-white text-[9px] h-6 rounded-lg" data-testid="poll-question-input" />

            {(form.type === 'multiple_choice' || form.type === 'quiz') && (
              <div className="space-y-0.5">
                {form.options.map((opt, i) => (
                  <div key={i} className="flex items-center gap-1">
                    {form.type === 'quiz' && (
                      <button onClick={() => setForm({ ...form, correctIdx: i })}
                        className={`w-4 h-4 rounded-full border ${form.correctIdx === i ? 'bg-emerald-500 border-emerald-400' : 'border-white/20'}`} />
                    )}
                    <Input value={opt} onChange={e => { const o = [...form.options]; o[i] = e.target.value; setForm({ ...form, options: o }); }}
                      placeholder={`Option ${i + 1}`} className="bg-karau-bg/60 border-white/10 text-white text-[8px] h-5 rounded" />
                  </div>
                ))}
                <button onClick={() => setForm({ ...form, options: [...form.options, ''] })}
                  className="text-[8px] text-yellow-400 hover:text-yellow-300">+ Add option</button>
              </div>
            )}

            <div className="flex gap-1">
              <Button size="sm" onClick={createPoll} className="flex-1 h-5 text-[8px] bg-yellow-500/80 rounded-lg" data-testid="submit-poll-btn">Create</Button>
              <Button size="sm" variant="ghost" onClick={() => setCreating(false)} className="h-5 text-[8px] text-slate-400">Cancel</Button>
            </div>
          </div>
        )}

        {/* Active Polls */}
        {polls.map(poll => (
          <PollCard key={poll.poll_id} poll={poll} onVote={vote} onClose={closePoll} />
        ))}

        {polls.length === 0 && !creating && (
          <p className="text-[9px] text-slate-500 text-center py-4">No active polls. Create one above.</p>
        )}
      </div>
    </div>
  );
}

function PollCard({ poll, onVote, onClose }) {
  const [wordInput, setWordInput] = useState('');
  const [selectedRating, setSelectedRating] = useState(0);
  const total = Math.max(poll.total_votes || 0, 1);

  return (
    <div className="p-2 bg-karau-bg/40 rounded-lg border border-white/5" data-testid={`poll-${poll.poll_id}`}>
      <div className="flex items-center justify-between mb-1.5">
        <p className="text-[10px] text-white font-medium flex-1">{poll.question}</p>
        <div className="flex items-center gap-1">
          <Badge className="text-[6px] bg-yellow-500/10 text-yellow-400">{poll.poll_type}</Badge>
          <Badge className="text-[6px] bg-white/5 text-slate-300">{poll.total_votes || 0} votes</Badge>
        </div>
      </div>

      {(poll.poll_type === 'multiple_choice' || poll.poll_type === 'quiz') && (
        <div className="space-y-0.5">
          {(poll.options || []).map(opt => {
            const pct = total > 0 ? Math.round((opt.votes / total) * 100) : 0;
            return (
              <button key={opt.id} onClick={() => onVote(poll.poll_id, opt.id)}
                className="w-full flex items-center gap-1.5 p-1 rounded bg-karau-bg/30 hover:bg-white/5 transition-all text-left"
                data-testid={`vote-${opt.id}`}>
                <span className="text-[8px] text-white flex-1">{opt.text}</span>
                <div className="w-16 h-1.5 bg-white/5 rounded-full overflow-hidden">
                  <div className="h-full bg-yellow-500/60 rounded-full transition-all" style={{ width: `${pct}%` }} />
                </div>
                <span className="text-[7px] text-slate-400 w-6 text-right">{pct}%</span>
              </button>
            );
          })}
        </div>
      )}

      {poll.poll_type === 'word_cloud' && (
        <div className="flex gap-1">
          <Input value={wordInput} onChange={e => setWordInput(e.target.value)}
            placeholder="Your response..." onKeyDown={e => { if (e.key === 'Enter') { onVote(poll.poll_id, null, wordInput); setWordInput(''); } }}
            className="bg-karau-bg/60 border-white/10 text-white text-[8px] h-5 rounded" data-testid="word-cloud-input" />
          <Button size="sm" onClick={() => { onVote(poll.poll_id, null, wordInput); setWordInput(''); }}
            className="h-5 px-1.5 bg-yellow-500/80 rounded"><Send className="w-2.5 h-2.5" /></Button>
        </div>
      )}

      {poll.poll_type === 'rating' && (
        <div className="flex items-center gap-0.5">
          {[1,2,3,4,5,6,7,8,9,10].map(r => (
            <button key={r} onClick={() => { setSelectedRating(r); onVote(poll.poll_id, null, null, r); }}
              className={`w-5 h-5 rounded text-[7px] font-bold ${
                r <= selectedRating ? 'bg-yellow-500 text-white' : 'bg-white/5 text-slate-400 hover:bg-white/10'
              }`} data-testid={`rating-${r}`}>{r}</button>
          ))}
        </div>
      )}

      <button onClick={() => onClose(poll.poll_id)} className="text-[7px] text-red-400 hover:text-red-300 mt-1" data-testid={`close-poll-${poll.poll_id}`}>Close poll</button>
    </div>
  );
}
