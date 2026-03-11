/**
 * AdminApprovalPanel — Global panel for managing external member approval requests
 * Shows all pending approvals across all meeting-generated channels
 */
import { useState, useEffect, useCallback } from 'react';
import {
  ShieldCheck, UserPlus, X, Check, Loader2, AlertTriangle,
  Video, Users, RefreshCw, Inbox, ChevronRight
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { API } from './constants';

const AdminApprovalPanel = ({ token, onClose }) => {
  const [approvals, setApprovals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(null);

  const loadApprovals = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/lumi/meeting-sync/pending-approvals`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setApprovals(data.approvals || []);
      }
    } catch {
      toast.error('Failed to load approvals');
    }
    setLoading(false);
  }, [token]);

  useEffect(() => { loadApprovals(); }, [loadApprovals]);

  const handleAction = async (approval, action) => {
    const key = `${approval.channel_id}-${approval.user_id}`;
    setProcessing(key);
    try {
      const endpoint = action === 'approve' ? 'approve-external' : 'deny-external';
      const res = await fetch(`${API}/api/lumi/meeting-sync/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          meeting_id: approval.meeting_id,
          user_ids: [approval.user_id],
          channel_id: approval.channel_id
        })
      });
      if (res.ok) {
        setApprovals(prev => prev.filter(a => !(a.channel_id === approval.channel_id && a.user_id === approval.user_id)));
        toast.success(action === 'approve' ? 'Member approved' : 'Request denied');
      } else {
        toast.error(`Failed to ${action}`);
      }
    } catch {
      toast.error('Connection error');
    }
    setProcessing(null);
  };

  const handleApproveAll = async (channelId, meetingId) => {
    const channelApprovals = approvals.filter(a => a.channel_id === channelId);
    setProcessing(`all-${channelId}`);
    try {
      const res = await fetch(`${API}/api/lumi/meeting-sync/approve-external`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          meeting_id: meetingId,
          user_ids: channelApprovals.map(a => a.user_id),
          channel_id: channelId
        })
      });
      if (res.ok) {
        setApprovals(prev => prev.filter(a => a.channel_id !== channelId));
        toast.success(`All ${channelApprovals.length} members approved`);
      }
    } catch {
      toast.error('Connection error');
    }
    setProcessing(null);
  };

  // Group approvals by channel
  const grouped = approvals.reduce((acc, a) => {
    if (!acc[a.channel_id]) acc[a.channel_id] = { channel_name: a.channel_name, meeting_id: a.meeting_id, items: [] };
    acc[a.channel_id].items.push(a);
    return acc;
  }, {});

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" data-testid="admin-approval-panel">
      <div className="w-full max-w-lg mx-4 max-h-[80vh] flex flex-col rounded-2xl border border-slate-700/50 bg-slate-900 shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-700/50">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-amber-500/20 flex items-center justify-center">
              <ShieldCheck className="w-4.5 h-4.5 text-amber-400" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-white font-outfit" data-testid="admin-approval-title">Admin Approvals</h2>
              <p className="text-xs text-slate-400">{approvals.length} pending request{approvals.length !== 1 ? 's' : ''}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={loadApprovals} className="h-8 w-8 p-0 text-slate-400 hover:text-white" data-testid="refresh-approvals">
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </Button>
            <Button variant="ghost" size="sm" onClick={onClose} className="h-8 w-8 p-0 text-slate-400 hover:text-white" data-testid="close-admin-approvals">
              <X className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-6 h-6 animate-spin text-slate-400" />
            </div>
          ) : Object.keys(grouped).length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center" data-testid="no-pending-approvals">
              <div className="w-14 h-14 rounded-2xl bg-slate-800 flex items-center justify-center mb-4">
                <Inbox className="w-7 h-7 text-slate-500" />
              </div>
              <p className="text-sm font-medium text-slate-400">No pending approvals</p>
              <p className="text-xs text-slate-500 mt-1">External member requests will appear here</p>
            </div>
          ) : (
            Object.entries(grouped).map(([channelId, group]) => (
              <div key={channelId} className="rounded-xl border border-slate-700/40 bg-slate-800/40 overflow-hidden" data-testid={`approval-group-${channelId}`}>
                {/* Channel header */}
                <div className="flex items-center justify-between px-4 py-3 bg-slate-800/60">
                  <div className="flex items-center gap-2.5">
                    <div className="w-7 h-7 rounded-lg bg-violet-500/20 flex items-center justify-center">
                      <Video className="w-3.5 h-3.5 text-violet-400" />
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-white">#{group.channel_name || channelId}</p>
                      <p className="text-[10px] text-slate-500">{group.items.length} external member{group.items.length !== 1 ? 's' : ''} waiting</p>
                    </div>
                  </div>
                  {group.items.length > 1 && (
                    <Button
                      size="sm"
                      onClick={() => handleApproveAll(channelId, group.meeting_id)}
                      disabled={processing === `all-${channelId}`}
                      className="h-7 text-[11px] bg-green-600 hover:bg-green-500 px-3"
                      data-testid={`approve-all-${channelId}`}
                    >
                      {processing === `all-${channelId}` ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : <Check className="w-3 h-3 mr-1" />}
                      Approve All
                    </Button>
                  )}
                </div>

                {/* Pending members */}
                <div className="divide-y divide-slate-700/30">
                  {group.items.map(approval => {
                    const key = `${approval.channel_id}-${approval.user_id}`;
                    return (
                      <div key={key} className="flex items-center gap-3 px-4 py-2.5" data-testid={`approval-item-${approval.user_id}`}>
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-slate-600 to-slate-700 flex items-center justify-center text-xs font-semibold text-white flex-shrink-0">
                          {(approval.user_name || approval.user_email || '?').charAt(0).toUpperCase()}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-white font-medium truncate">{approval.user_name || 'External User'}</p>
                          <p className="text-[10px] text-slate-500 truncate">{approval.user_email}</p>
                        </div>
                        <div className="flex gap-1.5 flex-shrink-0">
                          <Button
                            size="sm"
                            onClick={() => handleAction(approval, 'approve')}
                            disabled={processing === key}
                            className="h-7 px-3 text-[11px] bg-green-600 hover:bg-green-500"
                            data-testid={`approve-btn-${approval.user_id}`}
                          >
                            {processing === key ? <Loader2 className="w-3 h-3 animate-spin" /> : <Check className="w-3 h-3 mr-1" />}
                            Approve
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleAction(approval, 'deny')}
                            disabled={processing === key}
                            className="h-7 px-3 text-[11px] border-red-500/30 text-red-400 hover:bg-red-500/10"
                            data-testid={`deny-btn-${approval.user_id}`}
                          >
                            <X className="w-3 h-3 mr-1" />
                            Deny
                          </Button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminApprovalPanel;
