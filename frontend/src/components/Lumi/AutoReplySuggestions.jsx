import { useState } from 'react';
import { Sparkles, Send, Loader2, X } from 'lucide-react';
import { API } from './constants';

const AutoReplySuggestions = ({ messageId, channelId, messageContent, bucketCategory, token, onSend, onClose }) => {
  const [suggestions, setSuggestions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(null);

  const loadSuggestions = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/lumi/ai/auto-reply/suggestions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ message_id: messageId, channel_id: channelId, message_content: messageContent, bucket_category: bucketCategory })
      });
      if (res.ok) {
        const data = await res.json();
        setSuggestions(data.suggestions);
      }
    } catch {}
    setLoading(false);
  };

  const handleSend = async (text) => {
    setSending(text);
    await onSend(text);
    setSending(null);
    onClose();
  };

  if (!suggestions) {
    return (
      <button onClick={loadSuggestions} disabled={loading}
        className="inline-flex items-center gap-1 px-2 py-1 text-[10px] font-medium rounded-md bg-[#00CEC9]/10 text-[#00CEC9] hover:bg-[#00CEC9]/20 transition-colors"
        data-testid="auto-reply-trigger">
        {loading ? <Loader2 className="w-3 h-3 animate-spin" /> : <Sparkles className="w-3 h-3" />}
        Quick Reply
      </button>
    );
  }

  return (
    <div className="flex items-center gap-1.5 flex-wrap" data-testid="auto-reply-suggestions">
      {suggestions.map((s, i) => (
        <button key={i} onClick={() => handleSend(s)} disabled={sending === s}
          className="inline-flex items-center gap-1 px-2.5 py-1 text-[10px] font-medium rounded-full bg-white/5 border border-white/10 text-white/80 hover:bg-[#00CEC9]/10 hover:text-[#00CEC9] hover:border-[#00CEC9]/20 transition-all"
          data-testid={`auto-reply-${i}`}>
          {sending === s ? <Loader2 className="w-2.5 h-2.5 animate-spin" /> : <Send className="w-2.5 h-2.5" />}
          {s}
        </button>
      ))}
      <button onClick={onClose} className="p-0.5 text-white/30 hover:text-white/60" data-testid="auto-reply-close">
        <X className="w-3 h-3" />
      </button>
    </div>
  );
};

export default AutoReplySuggestions;
