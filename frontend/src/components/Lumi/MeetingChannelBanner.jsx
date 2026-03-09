/**
 * MeetingChannelBanner — Shown in ENZI channels created from meetings
 * Displays meeting context, participants, and admin approval controls for external members
 */
import { useState, useEffect } from 'react';
import {
  Video, Users, Clock, ShieldCheck, UserPlus, X, Check, AlertTriangle,
  Loader2, ChevronDown, ChevronUp
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { API } from './constants';

const MeetingChannelBanner = ({ channel, token, isAdmin }) => {
  const [pendingApprovals, setPendingApprovals] = useState(channel?.external_pending || []);
  const [expanded, setExpanded] = useState(true);
  const [processing, setProcessing] = useState(null);

  if (!channel?.meeting_source_id) return null;

  const handleApprove = async (userId) => {
    setProcessing(userId);
    try {
      const res = await fetch(`${API}/api/lumi/meeting-sync/approve-external`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ meeting_id: channel.meeting_source_id, user_ids: [userId], channel_id: channel.id })
      });
      if (res.ok) {
        setPendingApprovals(prev => prev.filter(p => p.user_id !== userId));
        toast.success('External member approved');
      } else {
        toast.error('Approval failed');
      }
    } catch { toast.error('Connection error'); }
    setProcessing(null);
  };

  const handleDeny = async (userId) => {
    setProcessing(userId);
    try {
      const res = await fetch(`${API}/api/lumi/meeting-sync/deny-external`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ meeting_id: channel.meeting_source_id, user_ids: [userId], channel_id: channel.id })
      });
      if (res.ok) {
        setPendingApprovals(prev => prev.filter(p => p.user_id !== userId));
        toast.success('Request denied');
      }
    } catch { toast.error('Connection error'); }
    setProcessing(null);
  };

  return (
    <div className="mx-3 mt-2 rounded-xl border border-violet-500/20 bg-violet-500/5 overflow-hidden" data-testid="meeting-channel-banner">
      {/* Banner header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-violet-500/5 transition-colors"
      >
        <div className="w-7 h-7 rounded-lg bg-violet-500/20 flex items-center justify-center flex-shrink-0">
          <Video className="w-3.5 h-3.5 text-violet-400" />
        </div>
        <div className="flex-1 text-left">
          <p className="text-xs font-semibold text-violet-300">Meeting Follow-up Channel</p>
          <p className="text-[10px] text-slate-400">From: {channel.meeting_title || 'Meeting'}</p>
        </div>
        <div className="flex items-center gap-2">
          {pendingApprovals.length > 0 && isAdmin && (
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 font-medium">
              {pendingApprovals.length} pending
            </span>
          )}
          {expanded ? <ChevronUp className="w-3.5 h-3.5 text-slate-400" /> : <ChevronDown className="w-3.5 h-3.5 text-slate-400" />}
        </div>
      </button>

      {expanded && (
        <div className="px-4 pb-3 space-y-2">
          {/* Members info */}
          <div className="flex items-center gap-4 text-[10px] text-slate-400">
            <span className="flex items-center gap-1">
              <Users className="w-3 h-3" />
              {(channel.members || []).length} internal members
            </span>
            <span className="flex items-center gap-1">
              <ShieldCheck className="w-3 h-3 text-green-400" />
              Internal-only channel
            </span>
          </div>

          {/* External approval requests */}
          {pendingApprovals.length > 0 && isAdmin && (
            <div className="mt-2 space-y-1.5">
              <p className="text-[10px] font-semibold text-amber-300 flex items-center gap-1">
                <AlertTriangle className="w-3 h-3" />
                External members requesting access
              </p>
              {pendingApprovals.map(p => (
                <div key={p.user_id} className="flex items-center gap-2 p-2 rounded-lg bg-slate-800/40">
                  <div className="w-6 h-6 rounded-full bg-slate-700 flex items-center justify-center text-[10px] text-white flex-shrink-0">
                    {(p.name || p.email || '?').charAt(0).toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-white font-medium truncate">{p.name || 'External User'}</p>
                    <p className="text-[10px] text-slate-500 truncate">{p.email}</p>
                  </div>
                  <div className="flex gap-1 flex-shrink-0">
                    <Button
                      size="sm"
                      onClick={(e) => { e.stopPropagation(); handleApprove(p.user_id); }}
                      disabled={processing === p.user_id}
                      className="h-6 w-6 p-0 bg-green-600 hover:bg-green-500"
                      data-testid={`approve-${p.user_id}`}
                    >
                      {processing === p.user_id ? <Loader2 className="w-3 h-3 animate-spin" /> : <Check className="w-3 h-3" />}
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={(e) => { e.stopPropagation(); handleDeny(p.user_id); }}
                      disabled={processing === p.user_id}
                      className="h-6 w-6 p-0 border-red-500/30 text-red-400 hover:bg-red-500/10"
                      data-testid={`deny-${p.user_id}`}
                    >
                      <X className="w-3 h-3" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MeetingChannelBanner;
