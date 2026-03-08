import { useState, useEffect } from 'react';
import { X, Search, UserPlus, Loader2, Mail, MessageSquare, Send, Share2 } from 'lucide-react';
import { toast } from 'sonner';
import { API } from './constants';

const NewMessagePanel = ({ onClose, onSelectUser, onInvite, token }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [noResults, setNoResults] = useState(false);

  useEffect(() => {
    if (query.length < 2) { setResults([]); setNoResults(false); return; }
    const timer = setTimeout(async () => {
      setSearching(true);
      setNoResults(false);
      try {
        // Search registered users
        const res = await fetch(`${API}/api/lumi/users/search?q=${encodeURIComponent(query)}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          const users = data.users || [];
          setResults(users);
          setNoResults(users.length === 0);
        }
      } catch { setResults([]); setNoResults(true); }
      setSearching(false);
    }, 300);
    return () => clearTimeout(timer);
  }, [query, token]);

  const isEmail = query.includes('@') && query.includes('.');

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-16 bg-black/60 backdrop-blur-sm" data-testid="new-message-panel">
      <div className="w-full max-w-md mx-4 bg-[#131920] border border-white/10 rounded-2xl shadow-2xl overflow-hidden"
        style={{ animation: 'fadeInUp 0.2s ease-out' }}>
        {/* Header */}
        <div className="flex items-center gap-3 px-5 py-4 border-b border-white/10">
          <UserPlus className="w-4 h-4 text-[#00CEC9]" />
          <h2 className="text-sm font-semibold text-white flex-1">New Message</h2>
          <button onClick={onClose} className="p-1 hover:bg-white/10 rounded-lg" data-testid="close-new-msg">
            <X className="w-4 h-4 text-slate-400" />
          </button>
        </div>

        {/* Search */}
        <div className="px-5 py-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input value={query} onChange={e => setQuery(e.target.value)} autoFocus
              placeholder="Search by name or email..."
              className="w-full pl-10 pr-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-white placeholder:text-slate-600 outline-none focus:border-[#00CEC9]/50 transition-colors"
              data-testid="new-msg-search" />
          </div>
        </div>

        {/* Results */}
        <div className="max-h-[300px] overflow-auto px-3 pb-3">
          {searching && (
            <div className="flex items-center justify-center py-4">
              <Loader2 className="w-5 h-5 text-slate-500 animate-spin" />
            </div>
          )}

          {!searching && results.map(u => (
            <button key={u.user_id} onClick={() => { onSelectUser(u.user_id); onClose(); }}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-white/5 transition-colors text-left"
              data-testid={`new-msg-user-${u.user_id}`}>
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500/20 to-violet-500/20 flex items-center justify-center text-xs font-semibold text-white">
                {(u.name || u.email || '?')[0].toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-white font-medium truncate">{u.name || 'User'}</p>
                <p className="text-[10px] text-slate-500 truncate">{u.email}</p>
              </div>
              <Send className="w-3.5 h-3.5 text-slate-600" />
            </button>
          ))}

          {/* No results — offer invite */}
          {!searching && noResults && query.length >= 2 && (
            <div className="px-3 py-4 text-center space-y-3">
              <p className="text-xs text-slate-400">No registered user found for "{query}"</p>
              <p className="text-[10px] text-slate-600">Invite them to join ENZI</p>

              <div className="grid grid-cols-2 gap-2 mt-3">
                {isEmail && (
                  <button onClick={() => { onInvite('email', query); }}
                    className="flex items-center justify-center gap-1.5 py-2 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
                    data-testid="invite-email-btn">
                    <Mail className="w-3.5 h-3.5 text-cyan-400" />
                    <span className="text-[10px] text-white/70">Email</span>
                  </button>
                )}
                <button onClick={() => { onInvite('sms', query); }}
                  className="flex items-center justify-center gap-1.5 py-2 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
                  data-testid="invite-sms-btn">
                  <MessageSquare className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-[10px] text-white/70">SMS</span>
                </button>
                <button onClick={() => { onInvite('whatsapp', query); }}
                  className="flex items-center justify-center gap-1.5 py-2 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
                  data-testid="invite-whatsapp-btn">
                  <svg className="w-3.5 h-3.5 text-green-400" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
                  <span className="text-[10px] text-white/70">WhatsApp</span>
                </button>
                <button onClick={() => { onInvite('linkedin', query); }}
                  className="flex items-center justify-center gap-1.5 py-2 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
                  data-testid="invite-linkedin-btn">
                  <svg className="w-3.5 h-3.5 text-blue-400" viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
                  <span className="text-[10px] text-white/70">LinkedIn</span>
                </button>
                <button onClick={() => { onInvite('instagram', query); }}
                  className="flex items-center justify-center gap-1.5 py-2 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
                  data-testid="invite-instagram-btn">
                  <svg className="w-3.5 h-3.5 text-pink-400" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>
                  <span className="text-[10px] text-white/70">Instagram</span>
                </button>
                <button onClick={() => { onInvite('share', query); }}
                  className="flex items-center justify-center gap-1.5 py-2 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
                  data-testid="invite-share-btn">
                  <Share2 className="w-3.5 h-3.5 text-violet-400" />
                  <span className="text-[10px] text-white/70">Copy Link</span>
                </button>
              </div>
            </div>
          )}

          {!searching && !noResults && query.length < 2 && (
            <p className="text-[10px] text-slate-600 text-center py-4">Type a name or email to find users or invite them</p>
          )}
        </div>
      </div>

      <style>{`
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(-8px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
};

export default NewMessagePanel;
