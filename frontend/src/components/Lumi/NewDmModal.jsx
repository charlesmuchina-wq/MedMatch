import { useState, useEffect } from 'react';
import { Search, X, Loader2 } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { useTranslation } from '@/utils/i18n';
import { API, STATUS_COLORS } from './constants';

export const NewDmModal = ({ onClose, onSelect, token }) => {
  const { t } = useTranslation();
  const [query, setQuery] = useState('');
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const search = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${API}/api/lumi/users/search?q=${encodeURIComponent(query)}`, { headers: { 'Authorization': `Bearer ${token}` } });
        if (res.ok) { setUsers((await res.json()).users || []); }
      } catch (e) {}
      setLoading(false);
    };
    const timer = setTimeout(search, 300);
    return () => clearTimeout(timer);
  }, [query, token]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-white border border-slate-200 rounded-lg w-full max-w-md p-6 shadow-lg" onClick={e => e.stopPropagation()} data-testid="new-dm-modal">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-slate-900">{t('lumi.newMessage') || 'New Message'}</h3>
          <button onClick={onClose} className="p-1 hover:bg-slate-100 rounded-md"><X className="w-5 h-5 text-slate-400" /></button>
        </div>
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input value={query} onChange={e => setQuery(e.target.value)} placeholder={t('lumi.searchUsers') || 'Search by name or email...'}
            className="pl-10 border-slate-200 rounded-md" autoFocus data-testid="dm-search-input" />
        </div>
        <div className="max-h-64 overflow-y-auto space-y-1">
          {loading && <div className="flex justify-center py-4"><Loader2 className="w-5 h-5 text-[#008080] animate-spin" /></div>}
          {!loading && users.length === 0 && <p className="text-sm text-slate-400 text-center py-4">{t('lumi.noUsersFound') || 'No users found'}</p>}
          {!loading && users.map(u => (
            <button key={u.user_id} onClick={() => onSelect(u.user_id)}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-md hover:bg-slate-50 transition-colors" data-testid={`dm-user-${u.user_id}`}>
              <div className="relative">
                <div className="w-9 h-9 rounded-full bg-[#36454F] flex items-center justify-center">
                  <span className="text-xs font-semibold text-white">{(u.name || u.email || '?')[0].toUpperCase()}</span>
                </div>
                <span className={`absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full ring-2 ring-white ${STATUS_COLORS[u.status] || STATUS_COLORS.offline}`} />
              </div>
              <div className="text-left"><p className="text-sm font-medium text-slate-900">{u.name || 'Unknown'}</p><p className="text-[11px] text-slate-400">{u.email}</p></div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
