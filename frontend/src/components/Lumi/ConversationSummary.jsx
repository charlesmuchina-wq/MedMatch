import { useState } from 'react';
import { Brain, Loader2, X, ClipboardList } from 'lucide-react';
import { toast } from 'sonner';
import { API } from './constants';

const ConversationSummary = ({ channelId, token, onClose }) => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [msgCount, setMsgCount] = useState(0);

  const generateSummary = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/lumi/ai/summarize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ channel_id: channelId, message_count: 50 })
      });
      if (res.ok) {
        const data = await res.json();
        setSummary(data.summary);
        setMsgCount(data.message_count);
      } else {
        toast.error('Failed to generate summary');
      }
    } catch {
      toast.error('Summary unavailable');
    }
    setLoading(false);
  };

  const copyToClipboard = () => {
    if (summary) {
      navigator.clipboard.writeText(summary);
      toast.success('Summary copied!');
    }
  };

  if (!summary && !loading) {
    return (
      <button onClick={generateSummary}
        className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-violet-500/10 text-violet-400 hover:bg-violet-500/20 transition-colors border border-violet-500/10"
        data-testid="summarize-btn">
        <Brain className="w-3.5 h-3.5" />Summarize
      </button>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-violet-500/10 border border-violet-500/10">
        <Loader2 className="w-4 h-4 text-violet-400 animate-spin" />
        <span className="text-xs text-violet-300">Generating summary...</span>
      </div>
    );
  }

  return (
    <div className="bg-[#131920] border border-white/10 rounded-xl p-4 space-y-3" data-testid="conversation-summary"
      style={{ animation: 'fadeInUp 0.3s ease-out' }}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Brain className="w-4 h-4 text-violet-400" />
          <span className="text-xs font-semibold text-white">AI Summary</span>
          <span className="text-[9px] text-slate-500">({msgCount} messages)</span>
        </div>
        <div className="flex items-center gap-1">
          <button onClick={copyToClipboard} className="p-1 hover:bg-white/10 rounded" title="Copy">
            <ClipboardList className="w-3 h-3 text-slate-400" />
          </button>
          <button onClick={onClose} className="p-1 hover:bg-white/10 rounded" data-testid="close-summary">
            <X className="w-3 h-3 text-slate-400" />
          </button>
        </div>
      </div>
      <div className="text-xs text-white/80 leading-relaxed whitespace-pre-wrap">
        {summary}
      </div>
      <style>{`
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
};

export default ConversationSummary;
