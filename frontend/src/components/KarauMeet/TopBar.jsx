import { memo } from 'react';
import { Radio, Crown, Clipboard, MonitorUp, Phone, Shield, Building2, UserX } from 'lucide-react';
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

export const TopBar = memo(function TopBar({ roomInfo, myRole, onLeave }) {
  const isHost = myRole === 'host';
  const isCoord = myRole === 'coordinator';

  return (
    <div className="h-11 bg-karau-card/80 border-b border-white/5 flex items-center justify-between px-4 shrink-0" data-testid="webinar-top-bar">
      <div className="flex items-center gap-2.5">
        {roomInfo.status === 'live' ? (
          <Badge className="bg-red-500/20 text-red-400 border-red-500/20 animate-pulse text-[10px]" data-testid="live-badge"><Radio className="w-2.5 h-2.5 mr-1" />LIVE</Badge>
        ) : roomInfo.practice_mode ? (
          <Badge className="bg-amber-500/20 text-amber-400 border-amber-500/20 text-[10px]" data-testid="practice-badge"><Shield className="w-2.5 h-2.5 mr-1" />PRACTICE</Badge>
        ) : (
          <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/20 text-[10px]">{roomInfo.status}</Badge>
        )}
        <span className="text-sm font-medium text-white truncate max-w-[300px]">{roomInfo.title}</span>
      </div>
      <div className="flex items-center gap-2">
        <Badge className={`${ROLE_BG[myRole] || ROLE_BG.attendee} ${ROLE_COLORS[myRole]} border text-[10px]`} data-testid="role-badge">
          {isHost && <Crown className="w-2.5 h-2.5 mr-1" />}
          {isCoord && <Clipboard className="w-2.5 h-2.5 mr-1" />}
          {myRole === 'presenter' && <MonitorUp className="w-2.5 h-2.5 mr-1" />}
          {myRole.charAt(0).toUpperCase() + myRole.slice(1)}
        </Badge>
        {roomInfo.org_privacy?.has_org_domains && (
          <Badge className={`text-[9px] border ${roomInfo.is_internal
            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
            : 'bg-orange-500/10 text-orange-400 border-orange-500/20'}`} data-testid="attendee-type-badge">
            {roomInfo.is_internal ? <><Building2 className="w-2.5 h-2.5 mr-0.5" />Internal</> : <><UserX className="w-2.5 h-2.5 mr-0.5" />External</>}
          </Badge>
        )}
        <Button variant="destructive" size="sm" onClick={onLeave} className="h-7 px-2 text-[11px] rounded-lg" data-testid="leave-webinar-btn">
          <Phone className="w-3 h-3 mr-1 rotate-[135deg]" />Leave
        </Button>
      </div>
    </div>
  );
});
