/**
 * EnziCompactPanel — Compact ENZI messenger for workspace side panel
 * Shows channel list + active chat, no full sidebar
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import { toast } from 'sonner';
import {
  Hash, MessageCircle, Send, Users, Search, Plus, Loader2, Lock
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { StatusDot, MessageBubble } from '@/components/Lumi';
import { API } from '@/components/Lumi/constants';

const EnziCompactPanel = () => {
  const [user, setUser] = useState(null);
  const [channels, setChannels] = useState([]);
  const [dms, setDms] = useState([]);
  const [activeChannel, setActiveChannel] = useState(null);
  const [messages, setMessages] = useState([]);
  const [messageText, setMessageText] = useState('');
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState('list'); // 'list' | 'chat'
  const messagesEndRef = useRef(null);
  const token = localStorage.getItem('token');

  // Auth check
  useEffect(() => {
    const savedUser = localStorage.getItem('karau_user');
    if (savedUser && token) {
      setUser(JSON.parse(savedUser));
    } else {
      setLoading(false);
    }
  }, [token]);

  // Load channels
  useEffect(() => {
    if (!user || !token) return;
    const load = async () => {
      try {
        const [chRes, dmRes] = await Promise.all([
          fetch(`${API}/api/lumi/channels`, { headers: { Authorization: `Bearer ${token}` } }),
          fetch(`${API}/api/lumi/dm/list`, { headers: { Authorization: `Bearer ${token}` } }),
        ]);
        if (chRes.ok) {
          const chData = await chRes.json();
          setChannels(chData.my_channels || chData || []);
        }
        if (dmRes.ok) setDms(await dmRes.json());
      } catch (e) { console.error('Failed to load channels', e); }
      setLoading(false);
    };
    load();
  }, [user, token]);

  // Load messages for active channel
  useEffect(() => {
    if (!activeChannel || !token) return;
    const load = async () => {
      try {
        const endpoint = activeChannel.is_dm
          ? `${API}/api/lumi/dm/${activeChannel.id}/messages`
          : `${API}/api/lumi/channels/${activeChannel.id}/messages`;
        const res = await fetch(endpoint, { headers: { Authorization: `Bearer ${token}` } });
        if (res.ok) {
          const data = await res.json();
          setMessages(Array.isArray(data) ? data : data.messages || []);
        }
      } catch (e) { console.error('Failed to load messages', e); }
    };
    load();
  }, [activeChannel, token]);

  // Scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!messageText.trim() || !activeChannel || !token) return;
    setSending(true);
    try {
      const endpoint = activeChannel.is_dm
        ? `${API}/api/lumi/dm/${activeChannel.id}/messages`
        : `${API}/api/lumi/channels/${activeChannel.id}/messages`;
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: messageText }),
      });
      if (res.ok) {
        const msg = await res.json();
        setMessages(prev => [...prev, msg]);
        setMessageText('');
      }
    } catch (e) { toast.error('Failed to send'); }
    setSending(false);
  };

  const selectChannel = (ch, isDm = false) => {
    setActiveChannel({ ...ch, is_dm: isDm });
    setView('chat');
  };

  if (!user) {
    return (
      <div className="h-full flex items-center justify-center p-4">
        <p className="text-xs text-slate-400 text-center">
          Sign in to ENZI to use messaging.
          <br />
          <a href="/lumi" className="text-cyan-400 hover:underline mt-1 inline-block">Open ENZI</a>
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <Loader2 className="w-5 h-5 text-cyan-400 animate-spin" />
      </div>
    );
  }

  // Chat view
  if (view === 'chat' && activeChannel) {
    return (
      <div className="h-full flex flex-col bg-[#0c0d1a]" data-testid="enzi-compact-chat">
        {/* Chat header */}
        <div className="flex items-center gap-2 px-3 py-2 border-b border-slate-700/30 flex-shrink-0">
          <button onClick={() => setView('list')} className="text-slate-400 hover:text-white text-xs">
            &larr;
          </button>
          <Hash className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-sm font-medium text-white truncate">
            {activeChannel.name || activeChannel.other_user?.name || 'Chat'}
          </span>
          {activeChannel.is_dm && activeChannel.e2ee && (
            <Lock className="w-3 h-3 text-green-400" />
          )}
        </div>

        {/* Messages */}
        <ScrollArea className="flex-1 px-3 py-2">
          <div className="space-y-2">
            {messages.slice(-50).map((msg, i) => (
              <div key={msg.id || i} className="text-xs">
                <span className="font-semibold text-slate-300">{msg.sender_name || msg.user_name || 'User'}</span>
                <span className="text-slate-500 ml-1.5 text-[10px]">
                  {msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                </span>
                <p className="text-slate-200 mt-0.5 leading-relaxed">{msg.content}</p>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>

        {/* Input */}
        <div className="px-3 py-2 border-t border-slate-700/30 flex-shrink-0">
          <div className="flex gap-2">
            <input
              type="text"
              value={messageText}
              onChange={(e) => setMessageText(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
              placeholder="Message..."
              className="flex-1 bg-slate-800/60 border border-slate-700/30 rounded-lg px-3 py-1.5 text-xs text-white placeholder:text-slate-500 outline-none focus:border-cyan-500/40"
              data-testid="enzi-compact-input"
            />
            <Button
              size="sm"
              onClick={handleSend}
              disabled={!messageText.trim() || sending}
              className="bg-cyan-600 hover:bg-cyan-500 h-8 w-8 p-0"
              data-testid="enzi-compact-send"
            >
              <Send className="w-3.5 h-3.5" />
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // Channel list view
  return (
    <div className="h-full flex flex-col bg-[#0c0d1a]" data-testid="enzi-compact-list">
      {/* Search */}
      <div className="px-3 py-2 border-b border-slate-700/30 flex-shrink-0">
        <div className="flex items-center gap-2 bg-slate-800/60 rounded-lg px-2 py-1.5">
          <Search className="w-3.5 h-3.5 text-slate-500" />
          <input type="text" placeholder="Search..." className="bg-transparent text-xs text-white placeholder:text-slate-500 outline-none flex-1" />
        </div>
      </div>

      <ScrollArea className="flex-1">
        {/* Channels */}
        {channels.length > 0 && (
          <div className="px-2 py-2">
            <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 px-2 mb-1">Channels</p>
            {channels.slice(0, 15).map((ch) => (
              <button
                key={ch.id}
                onClick={() => selectChannel(ch)}
                className="w-full flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-white/[0.04] transition-colors text-left"
                data-testid={`compact-channel-${ch.id}`}
              >
                <Hash className="w-3.5 h-3.5 text-slate-500 flex-shrink-0" />
                <span className="text-xs text-slate-300 truncate">{ch.name}</span>
              </button>
            ))}
          </div>
        )}

        {/* DMs */}
        {dms.length > 0 && (
          <div className="px-2 py-2">
            <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 px-2 mb-1">Direct Messages</p>
            {dms.slice(0, 10).map((dm) => (
              <button
                key={dm.id}
                onClick={() => selectChannel(dm, true)}
                className="w-full flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-white/[0.04] transition-colors text-left"
                data-testid={`compact-dm-${dm.id}`}
              >
                <div className="w-5 h-5 rounded-full bg-slate-700 flex items-center justify-center text-[10px] text-slate-300 flex-shrink-0">
                  {(dm.other_user?.name || dm.name || '?').charAt(0)}
                </div>
                <span className="text-xs text-slate-300 truncate">{dm.other_user?.name || dm.name || 'DM'}</span>
              </button>
            ))}
          </div>
        )}

        {channels.length === 0 && dms.length === 0 && (
          <div className="p-4 text-center">
            <p className="text-xs text-slate-500">No channels yet</p>
            <a href="/lumi" className="text-xs text-cyan-400 hover:underline mt-1 inline-block">Open full ENZI</a>
          </div>
        )}
      </ScrollArea>
    </div>
  );
};

export default EnziCompactPanel;
