import { memo } from 'react';
import { MessageCircleQuestion, ThumbsUp, Send } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';

const QAPanel = memo(function QAPanel({ questions, pendingQs, newQuestion, setNewQuestion, submitQuestion, answerTexts, setAnswerTexts, answerQuestion, upvoteQuestion, canControl }) {
  return (
    <div className="flex-1 flex flex-col overflow-hidden" data-testid="qa-panel">
      <div className="p-3 border-b border-white/[0.06]">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-amber-500/20 to-orange-500/10 flex items-center justify-center">
            <MessageCircleQuestion className="w-3.5 h-3.5 text-amber-400" />
          </div>
          <div>
            <h3 className="text-xs font-semibold text-white">Q&A</h3>
            <p className="text-[9px] text-slate-500">{pendingQs.length} pending</p>
          </div>
        </div>
      </div>
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {questions.length === 0 ? (
          <div className="text-center py-8">
            <div className="w-12 h-12 rounded-2xl bg-amber-500/10 flex items-center justify-center mx-auto mb-3">
              <MessageCircleQuestion className="w-6 h-6 text-amber-500/30" />
            </div>
            <p className="text-xs text-slate-500">No questions yet</p>
            <p className="text-[10px] text-slate-600 mt-0.5">Be the first to ask!</p>
          </div>
        ) : questions.map((q, i) => (
          <div key={q.question_id} className={`p-2.5 rounded-xl border transition-all animate-slide-up ${
            q.status === 'answered' ? 'bg-emerald-500/[0.04] border-emerald-500/15' : 'bg-white/[0.02] border-white/[0.06]'
          }`} style={{ animationDelay: `${i * 50}ms` }}>
            <p className="text-[11px] text-white leading-snug">{q.question}</p>
            <div className="flex items-center gap-2 mt-1.5 text-[9px] text-slate-500">
              <span>{q.asked_by}</span>
              <button onClick={() => upvoteQuestion(q.question_id)} className="flex items-center gap-0.5 hover:text-purple-400 transition-colors">
                <ThumbsUp className="w-2.5 h-2.5" /><span className="font-semibold">{q.upvotes}</span>
              </button>
              <Badge className={`text-[7px] ${q.status === 'answered' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-amber-500/10 text-amber-400 border-amber-500/20'}`}>{q.status}</Badge>
            </div>
            {q.answer && <div className="mt-2 p-2 bg-emerald-500/[0.04] rounded-lg text-[10px] text-emerald-300 border border-emerald-500/10"><b>A:</b> {q.answer}</div>}
            {canControl && q.status === 'pending' && (
              <div className="flex gap-2 mt-2">
                <Input value={answerTexts[q.question_id] || ''} onChange={e => setAnswerTexts(p => ({ ...p, [q.question_id]: e.target.value }))}
                  placeholder="Type your answer..." className="bg-karau-bg/60 border-white/10 text-white text-[10px] h-7 rounded-lg" />
                <Button size="sm" onClick={() => answerQuestion(q.question_id)} className="h-7 w-7 p-0 bg-emerald-500/80 hover:bg-emerald-400 rounded-lg"><Send className="w-3 h-3" /></Button>
              </div>
            )}
          </div>
        ))}
      </div>
      <div className="p-3 border-t border-white/[0.06]">
        <div className="flex gap-2">
          <Input value={newQuestion} onChange={e => setNewQuestion(e.target.value)} placeholder="Ask a question..."
            onKeyDown={e => e.key === 'Enter' && submitQuestion()} className="bg-karau-bg/60 border-white/10 text-white text-[10px] h-8 rounded-xl" data-testid="question-input" />
          <Button size="sm" onClick={submitQuestion} className="h-8 px-3 bg-gradient-to-r from-purple-500 to-violet-500 hover:from-purple-400 hover:to-violet-400 rounded-xl shadow-lg shadow-purple-500/15" data-testid="submit-question-btn"><Send className="w-3 h-3" /></Button>
        </div>
      </div>
    </div>
  );
});

export default QAPanel;
