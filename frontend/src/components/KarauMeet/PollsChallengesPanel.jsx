import { useState, useEffect, useCallback } from 'react';
import { BarChart, ListChecks, MessageSquare, Clock, Plus, Check, Send, Star, Loader2, ChevronRight, Trophy, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

const POLL_TYPES = [
  { id: 'multiple_choice', label: 'Poll', icon: BarChart, desc: 'Multiple choice', gradient: 'from-yellow-500/20 to-amber-500/10' },
  { id: 'quiz', label: 'Quiz', icon: ListChecks, desc: 'With correct answer', gradient: 'from-emerald-500/20 to-green-500/10' },
  { id: 'word_cloud', label: 'Words', icon: MessageSquare, desc: 'Open responses', gradient: 'from-blue-500/20 to-cyan-500/10' },
  { id: 'rating', label: 'Rate', icon: Star, desc: 'Score 1-10', gradient: 'from-purple-500/20 to-violet-500/10' },
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
          meeting_id: meetingId, question: form.question, poll_type: form.type,
          options: opts, correct_answer_id: form.type === 'quiz' ? `opt-${form.correctIdx}` : null,
          time_limit_seconds: form.timeLimit, points: 5
        })
      });
      if (res.ok) {
        toast.success('Poll launched!');
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

  if (loading) return (
    <div className="flex-1 flex items-center justify-center">
      <Loader2 className="w-5 h-5 text-yellow-400 animate-spin" />
    </div>
  );

  return (
    <div className="flex-1 flex flex-col overflow-hidden" data-testid="polls-panel">
      {/* Header */}
      <div className="p-3 border-b border-white/[0.06]">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-yellow-500/20 to-amber-500/10 flex items-center justify-center">
            <BarChart className="w-3.5 h-3.5 text-yellow-400" />
          </div>
          <div>
            <h3 className="text-xs font-semibold text-white">Polls & Challenges</h3>
            <p className="text-[9px] text-slate-500">{polls.length} active</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {/* Create Toggle */}
        {!creating ? (
          <button onClick={() => setCreating(true)} data-testid="create-poll-btn"
            className="w-full flex items-center justify-center gap-2 p-3 rounded-xl border-2 border-dashed border-yellow-500/20 hover:border-yellow-500/40 bg-yellow-500/[0.03] hover:bg-yellow-500/[0.06] transition-all duration-300 group">
            <Plus className="w-4 h-4 text-yellow-400 group-hover:scale-110 transition-transform" />
            <span className="text-xs text-yellow-400 font-medium">Launch New Poll</span>
          </button>
        ) : (
          <div className="p-3 rounded-xl border border-yellow-500/15 bg-gradient-to-b from-yellow-500/[0.04] to-transparent space-y-3 animate-slide-up" data-testid="poll-form">
            {/* Type Selector Cards */}
            <div className="grid grid-cols-2 gap-1.5">
              {POLL_TYPES.map(pt => (
                <button key={pt.id} onClick={() => setForm({ ...form, type: pt.id })}
                  data-testid={`poll-type-${pt.id}`}
                  className={`p-2 rounded-xl border text-left transition-all duration-200 ${
                    form.type === pt.id
                      ? `bg-gradient-to-br ${pt.gradient} border-yellow-500/30 scale-[1.02]`
                      : 'border-white/[0.06] bg-white/[0.02] hover:bg-white/[0.04]'
                  }`}>
                  <pt.icon className={`w-4 h-4 mb-1 ${form.type === pt.id ? 'text-yellow-400' : 'text-slate-500'}`} />
                  <p className={`text-[10px] font-medium ${form.type === pt.id ? 'text-white' : 'text-slate-400'}`}>{pt.label}</p>
                  <p className="text-[8px] text-slate-500">{pt.desc}</p>
                </button>
              ))}
            </div>

            <Input value={form.question} onChange={e => setForm({ ...form, question: e.target.value })}
              placeholder="What's your question?" className="bg-karau-bg/60 border-white/10 text-white text-xs h-9 rounded-xl" data-testid="poll-question-input" />

            {(form.type === 'multiple_choice' || form.type === 'quiz') && (
              <div className="space-y-1.5">
                {form.options.map((opt, i) => (
                  <div key={i} className="flex items-center gap-2">
                    {form.type === 'quiz' && (
                      <button onClick={() => setForm({ ...form, correctIdx: i })}
                        className={`w-5 h-5 rounded-full border-2 flex items-center justify-center transition-all ${
                          form.correctIdx === i ? 'bg-emerald-500 border-emerald-400 scale-110' : 'border-white/20 hover:border-emerald-400/40'
                        }`}>
                        {form.correctIdx === i && <Check className="w-3 h-3 text-white" />}
                      </button>
                    )}
                    <Input value={opt} onChange={e => { const o = [...form.options]; o[i] = e.target.value; setForm({ ...form, options: o }); }}
                      placeholder={`Option ${i + 1}`} className="bg-karau-bg/60 border-white/10 text-white text-[10px] h-7 rounded-lg" />
                  </div>
                ))}
                <button onClick={() => setForm({ ...form, options: [...form.options, ''] })}
                  className="text-[10px] text-yellow-400 hover:text-yellow-300 font-medium">+ Add option</button>
              </div>
            )}

            <div className="flex gap-2">
              <Button size="sm" onClick={createPoll} className="flex-1 h-8 text-[10px] bg-gradient-to-r from-yellow-500 to-amber-500 hover:from-yellow-400 hover:to-amber-400 text-black font-semibold rounded-xl shadow-lg shadow-yellow-500/20" data-testid="submit-poll-btn">
                <Zap className="w-3 h-3 mr-1" />Launch
              </Button>
              <Button size="sm" variant="ghost" onClick={() => setCreating(false)} className="h-8 text-[10px] text-slate-400 rounded-xl">Cancel</Button>
            </div>
          </div>
        )}

        {/* Active Polls */}
        {polls.map((poll, i) => (
          <PollCard key={poll.poll_id} poll={poll} onVote={vote} onClose={closePoll} index={i} />
        ))}

        {polls.length === 0 && !creating && (
          <div className="text-center py-8">
            <div className="w-12 h-12 rounded-2xl bg-yellow-500/10 flex items-center justify-center mx-auto mb-3">
              <BarChart className="w-6 h-6 text-yellow-500/40" />
            </div>
            <p className="text-xs text-slate-500">No active polls</p>
            <p className="text-[10px] text-slate-600 mt-0.5">Launch one to engage participants</p>
          </div>
        )}
      </div>
    </div>
  );
}

function PollCard({ poll, onVote, onClose, index }) {
  const [wordInput, setWordInput] = useState('');
  const [selectedRating, setSelectedRating] = useState(0);
  const [justVoted, setJustVoted] = useState(null);
  const total = Math.max(poll.total_votes || 0, 1);

  const handleVote = (pollId, optionId, text, rating) => {
    setJustVoted(optionId || 'text');
    onVote(pollId, optionId, text, rating);
    setTimeout(() => setJustVoted(null), 1500);
  };

  const typeConfig = {
    multiple_choice: { color: 'yellow', label: 'Poll', icon: BarChart },
    quiz: { color: 'emerald', label: 'Quiz', icon: Trophy },
    word_cloud: { color: 'blue', label: 'Word Cloud', icon: MessageSquare },
    rating: { color: 'purple', label: 'Rating', icon: Star },
  };
  const cfg = typeConfig[poll.poll_type] || typeConfig.multiple_choice;

  return (
    <div className="rounded-xl border border-white/[0.06] overflow-hidden animate-slide-up" 
      style={{ animationDelay: `${index * 80}ms` }}
      data-testid={`poll-${poll.poll_id}`}>
      {/* Poll Header */}
      <div className={`px-3 py-2 bg-gradient-to-r from-${cfg.color}-500/10 to-transparent border-b border-white/[0.04]`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <cfg.icon className={`w-3.5 h-3.5 text-${cfg.color}-400`} />
            <Badge className={`text-[7px] bg-${cfg.color}-500/10 text-${cfg.color}-400 border-${cfg.color}-500/20`}>{cfg.label}</Badge>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-[9px] text-slate-500">{poll.total_votes || 0} votes</span>
          </div>
        </div>
      </div>

      {/* Question */}
      <div className="px-3 pt-2.5 pb-2">
        <p className="text-[12px] text-white font-medium leading-snug">{poll.question}</p>
      </div>

      {/* Options */}
      <div className="px-3 pb-3">
        {(poll.poll_type === 'multiple_choice' || poll.poll_type === 'quiz') && (
          <div className="space-y-1.5">
            {(poll.options || []).map(opt => {
              const pct = total > 0 ? Math.round((opt.votes / total) * 100) : 0;
              const isJustVoted = justVoted === opt.id;
              return (
                <button key={opt.id} onClick={() => handleVote(poll.poll_id, opt.id)}
                  data-testid={`vote-${opt.id}`}
                  className={`w-full relative overflow-hidden rounded-lg p-2 text-left transition-all duration-300 group border ${
                    isJustVoted ? 'border-yellow-500/40 animate-vote-flash' : 'border-white/[0.06] hover:border-white/[0.12]'
                  }`}>
                  {/* Progress bar background */}
                  <div className="absolute inset-0 transition-all duration-700 ease-out rounded-lg"
                    style={{ width: `${pct}%`, background: `linear-gradient(90deg, rgba(234,179,8,0.08), rgba(234,179,8,0.03))` }} />
                  <div className="relative flex items-center justify-between">
                    <span className="text-[11px] text-white group-hover:text-white/90">{opt.text}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-semibold text-yellow-400/80 tabular-nums">{pct}%</span>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        )}

        {poll.poll_type === 'word_cloud' && (
          <div className="flex gap-2">
            <Input value={wordInput} onChange={e => setWordInput(e.target.value)}
              placeholder="Type your response..." onKeyDown={e => { if (e.key === 'Enter' && wordInput.trim()) { handleVote(poll.poll_id, null, wordInput); setWordInput(''); } }}
              className="bg-karau-bg/60 border-white/10 text-white text-[10px] h-8 rounded-lg" data-testid="word-cloud-input" />
            <Button size="sm" onClick={() => { if (wordInput.trim()) { handleVote(poll.poll_id, null, wordInput); setWordInput(''); } }}
              className="h-8 px-3 bg-blue-500/80 rounded-lg"><Send className="w-3 h-3" /></Button>
          </div>
        )}

        {poll.poll_type === 'rating' && (
          <div className="flex items-center gap-1 justify-center py-1">
            {[1,2,3,4,5,6,7,8,9,10].map(r => (
              <button key={r} onClick={() => { setSelectedRating(r); handleVote(poll.poll_id, null, null, r); }}
                data-testid={`rating-${r}`}
                className={`w-7 h-7 rounded-lg text-[10px] font-bold transition-all duration-200 ${
                  r <= selectedRating
                    ? 'bg-gradient-to-b from-purple-500 to-violet-600 text-white scale-105 shadow-lg shadow-purple-500/30'
                    : 'bg-white/[0.04] text-slate-500 hover:bg-white/[0.08] hover:text-white hover:scale-105'
                }`}>{r}</button>
            ))}
          </div>
        )}
      </div>

      {/* Close button */}
      <div className="px-3 pb-2">
        <button onClick={() => onClose(poll.poll_id)} className="text-[9px] text-red-400/60 hover:text-red-400 transition-colors" data-testid={`close-poll-${poll.poll_id}`}>
          Close poll
        </button>
      </div>
    </div>
  );
}
