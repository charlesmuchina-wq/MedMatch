import { useState, useEffect, useRef } from 'react';
import { Send, X, Loader2 } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useTranslation } from '@/utils/i18n';
import { API, ESY } from './constants';

export const ThreadPanel = ({ messageId, onClose, token }) => {
  const { t } = useTranslation();
  const [thread, setThread] = useState(null);
  const [replyText, setReplyText] = useState('');
  const [sending, setSending] = useState(false);
  const repliesEndRef = useRef(null);

  const loadThread = () => {
    if (!messageId) return;
    fetch(`${API}/api/lumi/messages/${messageId}/thread`, { headers: { 'Authorization': `Bearer ${token}` } })
      .then(r => r.json()).then(setThread);
  };

  useEffect(() => { loadThread(); }, [messageId, token]);
  useEffect(() => { repliesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [thread?.replies]);

  const sendReply = async () => {
    if (!replyText.trim()) return;
    setSending(true);
    try {
      await fetch(`${API}/api/lumi/messages/${messageId}/thread`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ content: replyText.trim() })
      });
      setReplyText('');
      loadThread();
    } catch (e) {}
    setSending(false);
  };

  if (!thread) return null;

  return (
    <div className="w-[320px] border-l border-slate-200 bg-white flex flex-col h-full" data-testid="thread-panel">
      <div className="h-14 flex items-center justify-between px-4 border-b border-slate-200 flex-shrink-0">
        <h3 className="text-sm font-semibold text-slate-900">{t('lumi.thread') || 'Thread'}</h3>
        <button onClick={onClose} className="p-1 hover:bg-slate-100 rounded-md"><X className="w-4 h-4 text-slate-500" /></button>
      </div>

      <ScrollArea className="flex-1 py-3">
        {/* Parent */}
        <div className="px-4 pb-3 border-b border-slate-100 mb-3">
          <p className="text-xs font-semibold text-slate-800">{thread.parent?.sender_name}</p>
          <p className="text-sm text-slate-700 mt-1">{thread.parent?.content}</p>
        </div>
        {/* Replies */}
        <div className="px-4 space-y-3">
          {thread.replies?.map(reply => (
            <div key={reply.id} className="flex gap-2" data-testid={`reply-${reply.id}`}>
              <div className="w-7 h-7 rounded-full bg-[#36454F] flex items-center justify-center flex-shrink-0">
                <span className="text-[9px] font-semibold text-white">{(reply.sender_name || '?')[0].toUpperCase()}</span>
              </div>
              <div>
                <div className="flex items-baseline gap-1.5">
                  <span className="text-xs font-semibold text-slate-800">{reply.sender_name}</span>
                  <span className="text-[10px] text-slate-400">{new Date(reply.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                </div>
                <p className="text-xs text-slate-600 mt-0.5">{reply.content}</p>
              </div>
            </div>
          ))}
          <div ref={repliesEndRef} />
        </div>
      </ScrollArea>

      {/* Reply input */}
      <div className="p-3 border-t border-slate-200">
        <div className="flex items-center gap-2">
          <input value={replyText} onChange={e => setReplyText(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && sendReply()}
            placeholder={t('lumi.reply') || 'Reply...'}
            className="flex-1 h-9 px-3 text-xs bg-slate-50 border border-slate-200 rounded-md outline-none focus:border-[#008080]"
            data-testid="thread-reply-input" />
          <button onClick={sendReply} disabled={!replyText.trim() || sending}
            className="h-9 w-9 flex items-center justify-center rounded-md text-white"
            style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` }}
            data-testid="thread-send-btn">
            {sending ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>
    </div>
  );
};
