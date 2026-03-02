import { memo } from 'react';
import { Users, Hand, Crown, Clipboard, UserPlus, UserMinus, Building2, ShieldCheck, ShieldOff, FileUp, FileDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

const ROLE_COLORS = {
  host: 'text-amber-400', coordinator: 'text-cyan-400',
  presenter: 'text-emerald-400', panelist: 'text-blue-400', attendee: 'text-slate-400'
};
const ROLE_BG = {
  host: 'bg-amber-500/10 border-amber-500/20', coordinator: 'bg-cyan-500/10 border-cyan-500/20',
  presenter: 'bg-emerald-500/10 border-emerald-500/20', panelist: 'bg-blue-500/10 border-blue-500/20',
  attendee: 'bg-slate-500/10 border-slate-500/20'
};

const ParticipantsPanel = memo(function ParticipantsPanel({ handRaises, activeRoles, promoteUser, demoteUser, isHost, roomInfo, onGrantPermission, onRevokePermission }) {
  return (
    <div className="flex-1 overflow-y-auto space-y-3" data-testid="participants-panel">
      <div className="p-3 border-b border-white/[0.06]">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-emerald-500/20 to-green-500/10 flex items-center justify-center">
            <Users className="w-3.5 h-3.5 text-emerald-400" />
          </div>
          <div>
            <h3 className="text-xs font-semibold text-white">Participants</h3>
            <p className="text-[9px] text-slate-500">{Object.keys(activeRoles).length} active</p>
          </div>
        </div>
      </div>
      <div className="px-3 space-y-3">
        {roomInfo?.org_privacy?.has_org_domains && (
          <div className="p-1.5 bg-karau-bg/40 rounded-lg border border-white/5" data-testid="org-privacy-status">
            <div className="flex items-center gap-1.5 mb-1">
              <Building2 className="w-3 h-3 text-violet-400" />
              <span className="text-[9px] text-violet-400 font-semibold uppercase tracking-wider">Org Privacy Active</span>
            </div>
            <div className="text-[8px] text-slate-500 space-y-0.5">
              <p className="flex items-center gap-1">
                {roomInfo.org_privacy.internal_only_docs ? <ShieldCheck className="w-2 h-2 text-emerald-400" /> : <ShieldOff className="w-2 h-2 text-orange-400" />}
                Docs: {roomInfo.org_privacy.internal_only_docs ? 'Internal only' : 'Open'}
              </p>
              <p className="flex items-center gap-1">
                {roomInfo.org_privacy.external_download_blocked ? <ShieldCheck className="w-2 h-2 text-emerald-400" /> : <ShieldOff className="w-2 h-2 text-orange-400" />}
                External download: {roomInfo.org_privacy.external_download_blocked ? 'Blocked' : 'Allowed'}
              </p>
            </div>
          </div>
        )}

        {handRaises.length > 0 && (
          <div className="space-y-1">
            <p className="text-[9px] text-amber-400 font-semibold uppercase tracking-wider flex items-center gap-1"><Hand className="w-2.5 h-2.5" />Raised Hands ({handRaises.length})</p>
            {handRaises.map(h => (
              <div key={h.user_id} className="flex items-center justify-between p-1.5 bg-amber-500/5 rounded-lg border border-amber-500/10" data-testid={`hand-${h.user_id}`}>
                <span className="text-[10px] text-white">{h.name}</span>
                <div className="flex gap-0.5">
                  {isHost && <Button size="sm" onClick={() => promoteUser(h.user_id, 'coordinator')} className="h-5 px-1.5 text-[8px] bg-cyan-500/80 rounded" data-testid={`promote-coord-${h.user_id}`}>Coord</Button>}
                  <Button size="sm" onClick={() => promoteUser(h.user_id, 'presenter')} className="h-5 px-1.5 text-[8px] bg-emerald-500/80 rounded" data-testid={`promote-presenter-${h.user_id}`}>Presenter</Button>
                  <Button size="sm" onClick={() => promoteUser(h.user_id, 'panelist')} className="h-5 px-1.5 text-[8px] bg-blue-500/80 rounded" data-testid={`promote-panelist-${h.user_id}`}>Panel</Button>
                </div>
              </div>
            ))}
          </div>
        )}
        <div className="space-y-1">
          <p className="text-[9px] text-purple-400 font-semibold uppercase tracking-wider">Active Roles</p>
          {Object.entries(activeRoles).length === 0 ? (
            <p className="text-[9px] text-slate-500 py-2">No promoted participants</p>
          ) : Object.entries(activeRoles).map(([uid, info]) => (
            <div key={uid} className={`flex items-center justify-between p-1.5 rounded-lg border ${ROLE_BG[info.role] || 'bg-white/5 border-white/10'}`} data-testid={`role-${uid}`}>
              <div className="flex items-center gap-1.5">
                <span className="text-[10px] text-white">{uid.substring(0, 12)}</span>
                <Badge className={`text-[7px] ${ROLE_COLORS[info.role]}`}>{info.role}</Badge>
              </div>
              <div className="flex items-center gap-0.5">
                {isHost && roomInfo?.org_privacy?.has_org_domains && (
                  <>
                    <Button size="sm" variant="ghost" onClick={() => onGrantPermission?.(uid, 'upload')} className="h-5 px-1 text-emerald-400 hover:bg-emerald-500/10" data-testid={`grant-upload-${uid}`} title="Grant upload"><FileUp className="w-2.5 h-2.5" /></Button>
                    <Button size="sm" variant="ghost" onClick={() => onGrantPermission?.(uid, 'download')} className="h-5 px-1 text-blue-400 hover:bg-blue-500/10" data-testid={`grant-download-${uid}`} title="Grant download"><FileDown className="w-2.5 h-2.5" /></Button>
                  </>
                )}
                <Button size="sm" variant="ghost" onClick={() => demoteUser(uid)} className="h-5 px-1 text-red-400 hover:bg-red-500/10" data-testid={`demote-${uid}`}><UserMinus className="w-2.5 h-2.5" /></Button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
});

export default ParticipantsPanel;
