/**
 * LumiMiniMessenger - Compact LUMI messenger for use inside AI KARAU meetings
 * Opens as a side panel allowing users to chat in LUMI channels while in a meeting
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
import {
  MessageCircle, Hash, Send, ArrowLeft, Users, Circle, Loader2
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const LumiMiniMessenger = () => {
  const [channels, setChannels] = useState([]);
  const [selectedChannel, setSelectedChannel] = useState(null);
  const [messages, setMessages] = useState([]);
  const [messageText, setMessageText] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const scrollRef = useRef(null);
  const wsRef = useRef(null);
  const inputRef = useRef(null);

  const token = localStorage.getItem('token');
  const user = (() => { try { return JSON.parse(localStorage.getItem('karau_user')); } catch { return null; } })();

  const headers = { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) };

  // Fetch channels
  useEffect(() => {
    const fetchChannels = async () => {
      try {
        const res = await fetch(`${API}/api/lumi/channels`, { headers });
        if (res.ok) {
          const data = await res.json();
          setChannels(data.channels || []);
        }
      } catch (e) {
        console.error('Failed to fetch LUMI channels:', e);
      } finally {
        setLoading(false);
      }
    };
    if (token) fetchChannels();
    else setLoading(false);
  }, [token]);

  // Fetch messages when channel selected
  useEffect(() => {
    if (!selectedChannel) return;
    const fetchMessages = async () => {
      try {
        const res = await fetch(`${API}/api/lumi/channels/${selectedChannel.id}/messages?limit=30`, { headers });
        if (res.ok) {
          const data = await res.json();
          setMessages(data.messages || []);
          setTimeout(() => scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight }), 100);
        }
      } catch (e) {
        console.error('Failed to fetch messages:', e);
      }
    };
    fetchMessages();
  }, [selectedChannel]);

  // WebSocket for real-time
  useEffect(() => {
    if (!user?.id) return;
    const wsUrl = `${API.replace('https://', 'wss://').replace('http://', 'ws://')}/api/lumi/ws/${user.id}`;
    try {
      const ws = new WebSocket(wsUrl);
      ws.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data);
          if (data.type === 'new_message' && selectedChannel && data.channel_id === selectedChannel.id) {
            setMessages(prev => [...prev, data.message]);
            setTimeout(() => scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight }), 100);
          }
        } catch {}
      };
      wsRef.current = ws;
    } catch {}
    return () => wsRef.current?.close();
  }, [user?.id, selectedChannel?.id]);

  const sendMessage = useCallback(async () => {
    if (!messageText.trim() || !selectedChannel || sending) return;
    setSending(true);
    try {
      const res = await fetch(`${API}/api/lumi/channels/${selectedChannel.id}/messages`, {
        method: 'POST', headers,
        body: JSON.stringify({ content: messageText.trim() })
      });
      if (res.ok) {
        const data = await res.json();
        setMessages(prev => [...prev, data]);
        setMessageText('');
        setTimeout(() => scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight }), 100);
        inputRef.current?.focus();
      }
    } catch (e) {
      console.error('Failed to send:', e);
    } finally {
      setSending(false);
    }
  }, [messageText, selectedChannel, sending]);

  if (!token) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-4 text-center">
        <MessageCircle className="w-8 h-8 text-slate-500 mb-2" />
        <p className="text-sm text-slate-400">Log in to LUMI to use the messenger</p>
      </div>
    );
  }

  // Channel list view
  if (!selectedChannel) {
    return (
      <div className="flex flex-col h-full" data-testid="lumi-mini-messenger">
        <div className="p-3 border-b border-karau-border">
          <div className="flex items-center gap-2">
            <div className="w-5 h-5 flex-shrink-0">
              <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
                <defs><linearGradient id="lm-grad" x1="0" y1="0" x2="64" y2="64" gradientUnits="userSpaceOnUse"><stop offset="0%" stopColor="#00CEC9"/><stop offset="50%" stopColor="#6C5CE7"/><stop offset="100%" stopColor="#E84393"/></linearGradient></defs>
                <rect x="6" y="10" width="52" height="34" rx="10" stroke="url(#lm-grad)" strokeWidth="4" fill="none"/>
                <polygon points="16,44 24,44 18,54" fill="url(#lm-grad)"/>
                <circle cx="24" cy="27" r="3" fill="#00CEC9"/><circle cx="32" cy="27" r="3" fill="#6C5CE7"/><circle cx="40" cy="27" r="3" fill="#E84393"/>
              </svg>
            </div>
            <span className="text-sm font-bold tracking-wide"
              style={{ background: 'linear-gradient(135deg, #00CEC9, #6C5CE7, #E84393)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              LUMI
            </span>
            <span className="text-[10px] text-slate-500 ml-auto">Messenger</span>
          </div>
        </div>

        <ScrollArea className="flex-1">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-5 h-5 text-slate-500 animate-spin" />
            </div>
          ) : channels.length === 0 ? (
            <div className="text-center py-8 px-4">
              <Hash className="w-6 h-6 text-slate-600 mx-auto mb-2" />
              <p className="text-xs text-slate-500">No channels yet. Open LUMI to create one.</p>
            </div>
          ) : (
            <div className="py-1">
              {channels.map(ch => (
                <button
                  key={ch.id}
                  onClick={() => setSelectedChannel(ch)}
                  className="w-full flex items-center gap-2.5 px-3 py-2.5 hover:bg-white/5 transition-colors text-left"
                  data-testid={`lumi-mini-channel-${ch.id}`}
                >
                  <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-violet-500/20 to-indigo-500/20 flex items-center justify-center flex-shrink-0">
                    {ch.type === 'dm' ? <Users className="w-3.5 h-3.5 text-indigo-400" /> : <Hash className="w-3.5 h-3.5 text-violet-400" />}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-white truncate">{ch.name}</p>
                    <p className="text-[10px] text-slate-500 truncate">{ch.type === 'dm' ? 'Direct Message' : `${ch.members?.length || 0} members`}</p>
                  </div>
                  <Circle className="w-2 h-2 text-emerald-400 fill-emerald-400 flex-shrink-0" />
                </button>
              ))}
            </div>
          )}
        </ScrollArea>
      </div>
    );
  }

  // Chat view
  return (
    <div className="flex flex-col h-full" data-testid="lumi-mini-chat">
      {/* Header */}
      <div className="p-2.5 border-b border-karau-border flex items-center gap-2">
        <button onClick={() => { setSelectedChannel(null); setMessages([]); }} className="p-1 hover:bg-white/10 rounded transition-colors" data-testid="lumi-mini-back">
          <ArrowLeft className="w-4 h-4 text-slate-400" />
        </button>
        <Hash className="w-3.5 h-3.5 text-violet-400" />
        <span className="text-sm font-semibold text-white truncate">{selectedChannel.name}</span>
      </div>

      {/* Messages */}
      <ScrollArea ref={scrollRef} className="flex-1 p-3">
        <div className="space-y-2.5">
          {messages.length === 0 ? (
            <p className="text-xs text-slate-500 text-center py-4">No messages yet</p>
          ) : messages.map((msg, i) => {
            const isOwn = msg.sender_id === user?.id || msg.sender === user?.name;
            return (
              <div key={msg.id || i} className={`flex flex-col ${isOwn ? 'items-end' : 'items-start'}`}>
                {!isOwn && <span className="text-[10px] text-slate-500 mb-0.5 px-1">{msg.sender || 'User'}</span>}
                <div className={`max-w-[85%] px-2.5 py-1.5 rounded-lg text-xs ${
                  isOwn ? 'bg-violet-500/20 text-violet-100' : 'bg-white/5 text-slate-200'
                }`}>
                  {msg.content}
                </div>
                <span className="text-[9px] text-slate-600 mt-0.5 px-1">
                  {msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                </span>
              </div>
            );
          })}
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="p-2 border-t border-karau-border flex items-center gap-1.5">
        <Input
          ref={inputRef}
          value={messageText}
          onChange={e => setMessageText(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
          placeholder="Message..."
          className="flex-1 h-8 text-xs bg-white/5 border-white/10 text-white placeholder:text-slate-500"
          data-testid="lumi-mini-input"
        />
        <button
          onClick={sendMessage}
          disabled={!messageText.trim() || sending}
          className="p-1.5 rounded-md transition-colors disabled:opacity-30 text-violet-400 hover:bg-violet-500/20"
          data-testid="lumi-mini-send"
        >
          {sending ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
        </button>
      </div>
    </div>
  );
};

export default LumiMiniMessenger;
