import { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
import {
  BarChart3, Plus, Check, X, Vote, ChevronDown
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * Polls panel for creating and voting on meeting polls
 */
export const PollsPanel = ({ meetingId, isHost }) => {
  const [polls, setPolls] = useState([]);
  const [showCreate, setShowCreate] = useState(false);
  const [question, setQuestion] = useState('');
  const [options, setOptions] = useState(['', '']);
  const [loading, setLoading] = useState(false);

  const fetchPolls = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/karau-meet/ai/polls/${meetingId}`);
      if (res.ok) {
        const data = await res.json();
        setPolls(data.polls || []);
      }
    } catch {}
  }, [meetingId]);

  useEffect(() => {
    fetchPolls();
    const interval = setInterval(fetchPolls, 5000);
    return () => clearInterval(interval);
  }, [fetchPolls]);

  const createPoll = async () => {
    const validOptions = options.filter(o => o.trim());
    if (!question.trim() || validOptions.length < 2) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/karau-meet/ai/polls`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ meeting_id: meetingId, question, options: validOptions })
      });
      if (res.ok) {
        setQuestion('');
        setOptions(['', '']);
        setShowCreate(false);
        fetchPolls();
      }
    } catch {}
    setLoading(false);
  };

  const vote = async (pollId, optIdx) => {
    try {
      await fetch(`${API}/api/karau-meet/ai/polls/${pollId}/vote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ option_index: optIdx })
      });
      fetchPolls();
    } catch {}
  };

  const closePoll = async (pollId) => {
    try {
      await fetch(`${API}/api/karau-meet/ai/polls/${pollId}/close`, { method: 'POST' });
      fetchPolls();
    } catch {}
  };

  return (
    <div className="flex flex-col h-full">
      <div className="p-3 border-b border-karau-border">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-white flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-turquoise" />
            Polls
          </h3>
          {isHost && (
            <Button size="sm" variant="ghost" className="h-7 text-xs text-turquoise"
              onClick={() => setShowCreate(!showCreate)} data-testid="create-poll-btn">
              <Plus className="w-3 h-3 mr-1" /> New Poll
            </Button>
          )}
        </div>
      </div>

      <ScrollArea className="flex-1 p-3">
        {/* Create Poll Form */}
        {showCreate && (
          <div className="mb-4 p-3 bg-karau-card rounded-lg border border-karau-border space-y-2">
            <Input
              value={question}
              onChange={e => setQuestion(e.target.value)}
              placeholder="Poll question..."
              className="bg-karau-surface border-karau-border text-white text-sm"
              data-testid="poll-question-input"
            />
            {options.map((opt, i) => (
              <div key={i} className="flex gap-2">
                <Input
                  value={opt}
                  onChange={e => {
                    const newOpts = [...options];
                    newOpts[i] = e.target.value;
                    setOptions(newOpts);
                  }}
                  placeholder={`Option ${i + 1}`}
                  className="bg-karau-surface border-karau-border text-white text-sm"
                  data-testid={`poll-option-${i}`}
                />
                {options.length > 2 && (
                  <Button size="sm" variant="ghost" className="h-9 w-9 p-0 text-slate-400"
                    onClick={() => setOptions(options.filter((_, j) => j !== i))}>
                    <X className="w-3 h-3" />
                  </Button>
                )}
              </div>
            ))}
            <Button size="sm" variant="ghost" className="text-xs text-slate-400 w-full"
              onClick={() => setOptions([...options, ''])} data-testid="add-poll-option">
              <Plus className="w-3 h-3 mr-1" /> Add Option
            </Button>
            <div className="flex gap-2">
              <Button size="sm" className="flex-1 bg-turquoise hover:bg-turquoise/80"
                onClick={createPoll} disabled={loading} data-testid="submit-poll">
                <Check className="w-3 h-3 mr-1" /> Launch Poll
              </Button>
              <Button size="sm" variant="ghost" className="text-slate-400"
                onClick={() => setShowCreate(false)}>Cancel</Button>
            </div>
          </div>
        )}

        {/* Poll List */}
        <div className="space-y-3">
          {polls.length === 0 ? (
            <div className="text-center py-8">
              <Vote className="w-8 h-8 text-slate-600 mx-auto mb-2" />
              <p className="text-slate-400 text-sm">No polls yet</p>
              {isHost && <p className="text-slate-500 text-xs mt-1">Create a poll to engage participants</p>}
            </div>
          ) : (
            polls.map((poll) => {
              const maxVotes = Math.max(...poll.options.map(o => o.votes), 1);
              return (
                <div key={poll.poll_id} className="p-3 bg-karau-card rounded-lg" data-testid={`poll-${poll.poll_id}`}>
                  <div className="flex items-start justify-between mb-2">
                    <p className="text-white text-sm font-medium">{poll.question}</p>
                    {!poll.is_active && (
                      <Badge className="text-[10px] bg-slate-600 text-slate-300">Closed</Badge>
                    )}
                  </div>
                  <div className="space-y-1.5">
                    {poll.options.map((opt, i) => {
                      const pct = poll.total_votes > 0 ? Math.round((opt.votes / poll.total_votes) * 100) : 0;
                      return (
                        <button
                          key={i}
                          onClick={() => poll.is_active && vote(poll.poll_id, i)}
                          disabled={!poll.is_active}
                          className="w-full text-left"
                          data-testid={`vote-option-${poll.poll_id}-${i}`}
                        >
                          <div className="relative bg-karau-surface rounded overflow-hidden h-8">
                            <div
                              className="absolute inset-y-0 left-0 bg-turquoise/20 transition-all"
                              style={{ width: `${pct}%` }}
                            />
                            <div className="relative flex items-center justify-between px-3 h-full">
                              <span className="text-xs text-slate-200">{opt.text}</span>
                              <span className="text-xs text-slate-400">{opt.votes} ({pct}%)</span>
                            </div>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-[10px] text-slate-500">{poll.total_votes} total votes</span>
                    {isHost && poll.is_active && (
                      <Button size="sm" variant="ghost" className="h-6 text-[10px] text-slate-400"
                        onClick={() => closePoll(poll.poll_id)} data-testid={`close-poll-${poll.poll_id}`}>
                        Close Poll
                      </Button>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </ScrollArea>
    </div>
  );
};

export default PollsPanel;
