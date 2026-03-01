import { AlertTriangle, Clock, X, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function GhostBookingAlert({ ghostBooking, onClose }) {
  if (!ghostBooking?.showWarning) return null;

  const isIdle = ghostBooking.ghostStatus?.is_idle;
  const approaching = ghostBooking.ghostStatus?.approaching_idle;

  return (
    <div className={`absolute top-14 left-1/2 -translate-x-1/2 z-50 w-80 rounded-xl border backdrop-blur-xl shadow-2xl transition-all ${
      isIdle
        ? 'bg-red-500/10 border-red-500/20'
        : 'bg-amber-500/10 border-amber-500/20'
    }`} data-testid="ghost-booking-alert">
      <div className="p-3">
        <div className="flex items-start gap-2">
          <AlertTriangle className={`w-4 h-4 shrink-0 mt-0.5 ${isIdle ? 'text-red-400' : 'text-amber-400'}`} />
          <div className="flex-1">
            <p className={`text-xs font-semibold ${isIdle ? 'text-red-300' : 'text-amber-300'}`}>
              {isIdle ? 'Meeting Room Idle' : 'Low Activity Detected'}
            </p>
            <p className="text-[9px] text-slate-400 mt-0.5">
              {isIdle
                ? 'No activity detected. This room will be auto-released shortly.'
                : 'Activity is dropping. The room may be released if no action is taken.'}
            </p>
            {ghostBooking.ghostStatus?.active_users !== undefined && (
              <div className="flex items-center gap-1.5 mt-1 text-[8px] text-slate-500">
                <Clock className="w-2 h-2" />
                Active users: {ghostBooking.ghostStatus.active_users}
              </div>
            )}
          </div>
          <button onClick={onClose} className="text-slate-500 hover:text-white">
            <X className="w-3 h-3" />
          </button>
        </div>

        <div className="flex gap-1.5 mt-2">
          <Button size="sm" onClick={ghostBooking.keepAlive}
            className="flex-1 h-6 text-[9px] bg-emerald-500/80 hover:bg-emerald-400 rounded-lg" data-testid="ghost-keep-alive-btn">
            <Check className="w-2.5 h-2.5 mr-0.5" />Still Here
          </Button>
          {isIdle && (
            <Button size="sm" variant="destructive" onClick={ghostBooking.releaseMeeting}
              className="h-6 px-2 text-[9px] rounded-lg" data-testid="ghost-release-btn">
              Release Room
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
