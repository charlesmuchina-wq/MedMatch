import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useTranslation } from '@/utils/i18n';
import { API, STATUS_COLORS, STATUS_LABELS } from './constants';

export const MembersPanel = ({ channelId, onClose, token }) => {
  const { t } = useTranslation();
  const [members, setMembers] = useState([]);

  useEffect(() => {
    fetch(`${API}/api/lumi/channels/${channelId}/members`, { headers: { 'Authorization': `Bearer ${token}` } })
      .then(r => r.json()).then(d => setMembers(d.members || []));
  }, [channelId, token]);

  return (
    <div className="w-[280px] border-l border-slate-200 bg-white flex flex-col h-full" data-testid="members-panel">
      <div className="h-14 flex items-center justify-between px-4 border-b border-slate-200">
        <h3 className="text-sm font-semibold text-slate-900">{t('lumi.members') || 'Members'} ({members.length})</h3>
        <button onClick={onClose} className="p-1 hover:bg-slate-100 rounded-md"><X className="w-4 h-4 text-slate-500" /></button>
      </div>
      <ScrollArea className="flex-1 py-2">
        {members.map(m => (
          <div key={m.user_id} className="flex items-center gap-3 px-4 py-2 hover:bg-slate-50" data-testid={`member-${m.user_id}`}>
            <div className="relative">
              <div className="w-8 h-8 rounded-full bg-[#36454F] flex items-center justify-center">
                <span className="text-[10px] font-semibold text-white">{(m.name || '?')[0].toUpperCase()}</span>
              </div>
              <span className={`absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full ring-2 ring-white ${STATUS_COLORS[m.status] || STATUS_COLORS.offline}`} />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm text-slate-900 truncate">{m.name || 'User'}</p>
              <p className="text-[10px] text-slate-400">{m.role === 'admin' ? 'Admin' : STATUS_LABELS[m.status] || 'Offline'}</p>
            </div>
          </div>
        ))}
      </ScrollArea>
    </div>
  );
};
