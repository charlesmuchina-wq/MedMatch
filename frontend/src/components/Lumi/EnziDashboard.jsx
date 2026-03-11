/**
 * EnziDashboard — ENZI Bento Grid Dashboard
 * Extracted from LumiMessenger for maintainability
 */
import {
  Plus, ArrowLeft, Hash, UserPlus, Video, Bell, Command,
  Sparkles, BarChart3, MessageCircle, Zap, ClipboardList,
  Clock, Settings, Crown, TrendingUp, ShieldCheck,
  ChevronRight, Globe, Loader2, X
} from 'lucide-react';
import { LumiBrand, ESY } from '@/components/Lumi';

const EnziDashboard = ({
  mobileSidebar, user, channels, dms, unreadCounts, presenceMap,
  bucketCounts, predictions, calendarStatus, pendingInvites,
  activeBucket, bucketMessages, bucketLoading,
  setActiveChannel, setMobileSidebar, setShowNewDmModal, setShowCommandBar,
  setShowVisualizations, setShowCreateModal, setShowMeetingModal,
  setShowBotStore, setShowChannelTools, setShowMeetingHistory,
  setShowPremium, setShowInsights, setShowTeamAnalytics,
  setShowAdminApprovals, openBucket, dismissBucketItem,
  setActiveBucket, setBucketMessages, handleInviteResponse, trackAction,
}) => {
  return (
    <div className={`${!mobileSidebar ? 'flex' : 'hidden'} md:flex flex-col flex-1 min-w-0 bg-[#0D1117] overflow-auto`}>
      <div className="flex-1 flex flex-col">
        <div className="max-w-5xl mx-auto w-full p-6 md:p-10 space-y-6">
          {/* Hero */}
          <div className="text-center mb-2">
            <LumiBrand variant="inline-dark" size="md" showTagline className="justify-center" />
            <p className="text-slate-400 text-sm mt-3 font-outfit">Your intelligent command center</p>
          </div>

          {/* Pending Invites */}
          {pendingInvites.length > 0 && (
            <div className="bento-tile col-span-full" data-testid="pending-invites-panel">
              <div className="flex items-center gap-2 mb-3">
                <Bell className="w-3.5 h-3.5 text-amber-400" />
                <p className="text-[10px] font-semibold text-amber-400 uppercase tracking-widest font-outfit">Pending Invites ({pendingInvites.length})</p>
              </div>
              <div className="space-y-2">
                {pendingInvites.map(inv => (
                  <div key={inv.id} className="flex items-center gap-3 px-3 py-2.5 rounded-xl bg-white/[0.03] border border-white/5" data-testid={`invite-${inv.id}`}>
                    <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center flex-shrink-0">
                      <Hash className="w-4 h-4 text-amber-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-white font-medium truncate">#{inv.channel_name}</p>
                      <p className="text-[11px] text-slate-500">Invited by {inv.invited_by_name}</p>
                    </div>
                    <button onClick={() => handleInviteResponse(inv.id, 'accept')}
                      className="px-3 py-1.5 rounded-lg bg-[#00CEC9]/10 text-[#00CEC9] text-xs font-medium hover:bg-[#00CEC9]/20 transition-colors" data-testid={`accept-invite-${inv.id}`}>
                      Accept
                    </button>
                    <button onClick={() => handleInviteResponse(inv.id, 'decline')}
                      className="px-3 py-1.5 rounded-lg bg-white/5 text-slate-400 text-xs font-medium hover:bg-white/10 transition-colors" data-testid={`decline-invite-${inv.id}`}>
                      Decline
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Quick Actions Row */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
            <button onClick={() => setShowNewDmModal(true)} className="bento-tile col-span-1 flex flex-col items-start gap-3 cursor-pointer group hover-lift animate-stagger-in-1" data-testid="bento-new-dm">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-teal-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
                <UserPlus className="w-5 h-5 text-white" />
              </div>
              <div><p className="text-white text-sm font-semibold font-outfit">Direct Message</p><p className="text-slate-500 text-[11px] mt-0.5">Reach someone directly</p></div>
            </button>
            <button onClick={() => setShowCommandBar(true)} className="bento-tile col-span-1 flex flex-col items-start gap-3 cursor-pointer group hover-lift animate-stagger-in-2" data-testid="bento-command">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-slate-600 to-slate-700 flex items-center justify-center shadow-lg shadow-slate-500/20">
                <Command className="w-5 h-5 text-white" />
              </div>
              <div><p className="text-white text-sm font-semibold font-outfit">Command Bar</p><p className="text-slate-500 text-[11px] mt-0.5">Ctrl+K to search</p></div>
            </button>
            <button onClick={() => setShowVisualizations(true)} className="bento-tile col-span-1 flex flex-col items-start gap-3 cursor-pointer group hover-lift animate-stagger-in-3" data-testid="bento-viz">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
                <BarChart3 className="w-5 h-5 text-white" />
              </div>
              <div><p className="text-white text-sm font-semibold font-outfit">Analytics</p><p className="text-slate-500 text-[11px] mt-0.5">View insights & data</p></div>
            </button>
            <button onClick={() => setShowCreateModal(true)} className="bento-tile col-span-1 flex flex-col items-start gap-3 cursor-pointer group hover-lift animate-stagger-in-4" data-testid="bento-create-channel">
              <div className="w-10 h-10 rounded-xl lumi-gradient flex items-center justify-center shadow-lg shadow-violet-500/20">
                <Plus className="w-5 h-5 text-white" />
              </div>
              <div><p className="text-white text-sm font-semibold font-outfit">New Channel</p><p className="text-slate-500 text-[11px] mt-0.5">Settings & invites</p></div>
            </button>
          </div>

          {/* KARAU Meeting Quick Action */}
          <button onClick={() => setShowMeetingModal(true)} className="bento-tile w-full flex items-center gap-4 cursor-pointer group hover:border-[#6C5CE7]/20 transition-all" data-testid="bento-start-meeting">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center shadow-lg flex-shrink-0" style={{ background: 'linear-gradient(135deg, #6C5CE7, #00CEC9)' }}>
              <Video className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-white text-sm font-semibold font-outfit">AI KARAU Meeting</p>
              <p className="text-slate-500 text-[11px] mt-0.5">Start an instant or scheduled meeting from ENZI</p>
            </div>
            <ArrowLeft className="w-4 h-4 text-slate-600 rotate-180 group-hover:translate-x-1 transition-transform" />
          </button>

          {/* Bot Store & Channel Tools Row */}
          <div className="grid grid-cols-2 gap-3">
            <button onClick={() => setShowBotStore(true)} className="bento-tile flex flex-col items-start gap-3 cursor-pointer group hover:border-[#00CEC9]/20 transition-all" data-testid="bento-bot-store">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center shadow-lg" style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` }}>
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div><p className="text-white text-sm font-semibold font-outfit">Bot Store</p><p className="text-slate-500 text-[11px] mt-0.5">18 bots across 4 categories</p></div>
            </button>
            <button onClick={() => setShowChannelTools(true)} className="bento-tile flex flex-col items-start gap-3 cursor-pointer group hover:border-[#6C5CE7]/20 transition-all" data-testid="bento-channel-tools">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center shadow-lg" style={{ background: 'linear-gradient(135deg, #6C5CE7, #A855F7)' }}>
                <Settings className="w-5 h-5 text-white" />
              </div>
              <div><p className="text-white text-sm font-semibold font-outfit">Channel Tools</p><p className="text-slate-500 text-[11px] mt-0.5">Templates & Webhooks</p></div>
            </button>
          </div>

          {/* Meeting History + Premium Row */}
          <div className="grid grid-cols-2 gap-3">
            <button onClick={() => setShowMeetingHistory(true)} className="bento-tile flex flex-col items-start gap-3 cursor-pointer group hover:border-[#6C5CE7]/20 transition-all" data-testid="bento-meeting-history">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center shadow-lg" style={{ background: 'linear-gradient(135deg, #6C5CE7, #E84393)' }}>
                <Clock className="w-5 h-5 text-white" />
              </div>
              <div><p className="text-white text-sm font-semibold font-outfit">Meeting History</p><p className="text-slate-500 text-[11px] mt-0.5">Past & scheduled meetings</p></div>
            </button>
            <button onClick={() => setShowPremium(true)} className="bento-tile flex flex-col items-start gap-3 cursor-pointer group hover:border-amber-500/20 transition-all" data-testid="bento-premium">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center shadow-lg" style={{ background: 'linear-gradient(135deg, #FFD700, #FFA500)' }}>
                <Crown className="w-5 h-5 text-white" />
              </div>
              <div><p className="text-white text-sm font-semibold font-outfit">Premium</p><p className="text-slate-500 text-[11px] mt-0.5">Upgrade features</p></div>
            </button>
          </div>

          {/* Insights & Analytics Row */}
          <div className="grid grid-cols-2 gap-3">
            <button onClick={() => setShowInsights(true)} className="bento-tile flex flex-col items-start gap-3 cursor-pointer group hover:border-[#6C5CE7]/20 transition-all" data-testid="bento-insights">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center shadow-lg" style={{ background: 'linear-gradient(135deg, #6C5CE7, #00CEC9)' }}>
                <BarChart3 className="w-5 h-5 text-white" />
              </div>
              <div><p className="text-white text-sm font-semibold font-outfit">Insights</p><p className="text-slate-500 text-[11px] mt-0.5">Usage analytics & tips</p></div>
            </button>
            <button onClick={() => setShowTeamAnalytics(true)} className="bento-tile flex flex-col items-start gap-3 cursor-pointer group hover:border-indigo-500/20 transition-all" data-testid="bento-team-analytics">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center shadow-lg" style={{ background: 'linear-gradient(135deg, #4F46E5, #7C3AED)' }}>
                <TrendingUp className="w-5 h-5 text-white" />
              </div>
              <div><p className="text-white text-sm font-semibold font-outfit">Team Analytics</p><p className="text-slate-500 text-[11px] mt-0.5">Activity & engagement</p></div>
            </button>
          </div>

          {/* Admin Approvals Tile */}
          <button onClick={() => setShowAdminApprovals(true)} className="bento-tile w-full flex items-center gap-4 cursor-pointer group hover:border-amber-500/20 transition-all" data-testid="bento-admin-approvals">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center shadow-lg" style={{ background: 'linear-gradient(135deg, #F59E0B, #D97706)' }}>
              <ShieldCheck className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1">
              <p className="text-white text-sm font-semibold font-outfit">Admin Approvals</p>
              <p className="text-slate-500 text-[11px] mt-0.5">Review external member requests for meeting channels</p>
            </div>
            <ChevronRight className="w-4 h-4 text-slate-500 group-hover:text-amber-400 transition-colors" />
          </button>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 md:gap-4">
            {/* Recent Conversations */}
            <div className="bento-tile" data-testid="recent-conversations-panel">
              <div className="flex items-center gap-2 mb-3">
                <MessageCircle className="w-3.5 h-3.5 text-cyan-400" />
                <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest font-outfit">Recent Conversations</p>
              </div>
              <div className="space-y-1">
                {[
                  ...channels.slice(0, 4).map(ch => ({ ...ch, _type: 'channel' })),
                  ...dms.slice(0, 3).map(dm => ({ ...dm, _type: 'dm' })),
                ].slice(0, 6).map(item => (
                  <button key={item.id} onClick={() => { setActiveChannel(item); setMobileSidebar(false); }}
                    className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-xl hover:bg-white/5 transition-all group text-left"
                    data-testid={`recent-conv-${item.id}`}>
                    {item._type === 'dm' ? (
                      <div className="relative w-7 h-7 flex-shrink-0">
                        <div className="w-7 h-7 rounded-full bg-slate-600 flex items-center justify-center text-[10px] font-semibold text-white">
                          {(item.dm_partner?.name || item.dm_partner?.email || '?')[0].toUpperCase()}
                        </div>
                        <span className={`absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full ring-1 ring-[#0D1117] ${
                          presenceMap[item.dm_partner?.user_id] === 'online' ? 'bg-emerald-500' : 'bg-slate-600'
                        }`} />
                      </div>
                    ) : (
                      <div className="w-7 h-7 rounded-lg bg-white/5 flex items-center justify-center flex-shrink-0 group-hover:bg-white/10 transition-colors">
                        <Hash className="w-3.5 h-3.5 text-violet-400" />
                      </div>
                    )}
                    <div className="flex-1 min-w-0">
                      <span className="text-sm text-white/80 group-hover:text-white truncate font-medium block">
                        {item._type === 'dm' ? (item.dm_partner?.name || item.dm_partner?.email || 'User') : item.name}
                      </span>
                      {item.last_message && (
                        <p className="text-[10px] text-slate-600 truncate">{typeof item.last_message === 'string' ? item.last_message : item.last_message?.content || ''}</p>
                      )}
                    </div>
                    {unreadCounts[item.id] > 0 && (
                      <span className="min-w-[18px] h-[18px] flex items-center justify-center rounded-full text-[9px] font-bold text-white" style={{ backgroundColor: ESY.pink }}>
                        {unreadCounts[item.id]}
                      </span>
                    )}
                  </button>
                ))}
                {channels.length === 0 && dms.length === 0 && (
                  <p className="text-slate-600 text-xs py-3 text-center">No conversations yet. Start a DM or join a channel!</p>
                )}
              </div>
            </div>

            {/* Right Column: AI Status + Smart Buckets */}
            <div className="space-y-3 md:space-y-4">
              <div className="bento-tile">
                <div className="flex items-center gap-2 mb-3">
                  <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                  <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest font-outfit">Status & Intelligence</p>
                </div>
                <div className="flex items-center gap-2.5 px-2.5 py-2 rounded-xl bg-white/[0.03] mb-2" data-testid="calendar-status">
                  <div className={`w-2.5 h-2.5 rounded-full ${
                    calendarStatus.status === 'in_meeting' ? 'bg-red-500 animate-pulse' :
                    calendarStatus.status === 'ooo' ? 'bg-amber-500' : 'bg-emerald-500'
                  }`} />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-white/80 font-medium capitalize">{calendarStatus.status.replace('_', ' ')}</p>
                    {calendarStatus.calendar_event && (
                      <p className="text-[10px] text-slate-500 truncate">{calendarStatus.calendar_event.subject}</p>
                    )}
                  </div>
                  {calendarStatus.microsoft_linked && (
                    <span className="text-[8px] px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400">MS Synced</span>
                  )}
                </div>
                <div className="grid grid-cols-3 gap-2">
                  <div className="text-center p-2 rounded-xl bg-white/[0.03]">
                    <p className="text-lg font-bold lumi-gradient-text font-outfit">92%</p>
                    <p className="text-[9px] text-slate-500 mt-0.5">Compliance</p>
                  </div>
                  <div className="text-center p-2 rounded-xl bg-white/[0.03]">
                    <p className="text-lg font-bold text-cyan-400 font-outfit">{channels.length}</p>
                    <p className="text-[9px] text-slate-500 mt-0.5">Channels</p>
                  </div>
                  <div className="text-center p-2 rounded-xl bg-white/[0.03]">
                    <p className="text-lg font-bold text-emerald-400 font-outfit">{dms.length}</p>
                    <p className="text-[9px] text-slate-500 mt-0.5">DMs</p>
                  </div>
                </div>
              </div>

              <div className="bento-tile">
                <div className="flex items-center gap-2 mb-3">
                  <ClipboardList className="w-3.5 h-3.5 text-pink-400" />
                  <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest font-outfit">Smart Buckets</p>
                </div>
                <div className="space-y-1.5">
                  {[
                    { key: 'urgent', label: 'Urgent', color: 'bg-red-500' },
                    { key: 'action_required', label: 'Action Required', color: 'bg-amber-500' },
                    { key: 'meeting_request', label: 'Meeting Requests', color: 'bg-blue-500' },
                  ].map(b => (
                    <button key={b.key} onClick={() => openBucket(b.key)}
                      className="w-full flex items-center gap-2.5 px-2 py-1.5 rounded-lg hover:bg-white/5 transition-colors text-left"
                      data-testid={`bucket-${b.key}`}>
                      <div className={`w-2 h-2 rounded-full ${b.color}`} />
                      <span className="text-xs text-white/70 flex-1">{b.label}</span>
                      <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${bucketCounts[b.key] > 0 ? 'bg-white/10 text-white font-medium' : 'bg-white/5 text-slate-600'}`}>
                        {bucketCounts[b.key] || 0}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Predicted Suggestions */}
          {(predictions.channels.length > 0 || predictions.dms.length > 0) && (
            <div className="bento-tile" data-testid="predicted-suggestions">
              <div className="flex items-center gap-2 mb-3">
                <Zap className="w-3.5 h-3.5 text-amber-400" />
                <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest font-outfit">Suggested for You</p>
              </div>
              <div className="flex gap-2 overflow-x-auto pb-1">
                {predictions.channels.slice(0, 3).map(s => {
                  const ch = channels.find(c => c.id === s.target_id);
                  return ch ? (
                    <button key={s.target_id} onClick={() => { setActiveChannel(ch); setMobileSidebar(false); trackAction('channel_visit', ch.id, ch.name); }}
                      className="flex-shrink-0 flex items-center gap-2 px-3 py-2 rounded-xl bg-white/[0.03] border border-white/5 hover:bg-white/5 transition-colors"
                      data-testid={`suggest-${s.target_id}`}>
                      <Hash className="w-3.5 h-3.5 text-violet-400" /><span className="text-xs text-white/80">{s.target_name}</span>
                    </button>
                  ) : null;
                })}
                {predictions.dms.slice(0, 3).map(s => {
                  const dm = dms.find(d => d.id === s.target_id);
                  return dm ? (
                    <button key={s.target_id} onClick={() => { setActiveChannel(dm); setMobileSidebar(false); trackAction('dm_visit', dm.id, s.target_name); }}
                      className="flex-shrink-0 flex items-center gap-2 px-3 py-2 rounded-xl bg-white/[0.03] border border-white/5 hover:bg-white/5 transition-colors"
                      data-testid={`suggest-${s.target_id}`}>
                      <div className="w-5 h-5 rounded-full bg-slate-600 flex items-center justify-center text-[9px] text-white font-semibold">
                        {(s.target_name || '?')[0].toUpperCase()}
                      </div>
                      <span className="text-xs text-white/80">{s.target_name}</span>
                    </button>
                  ) : null;
                })}
              </div>
            </div>
          )}

          {/* Bucket Detail Panel */}
          {activeBucket && (
            <div className="bento-tile" data-testid="bucket-detail-panel">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div className={`w-2.5 h-2.5 rounded-full ${
                    activeBucket === 'urgent' ? 'bg-red-500' : activeBucket === 'action_required' ? 'bg-amber-500' : 'bg-blue-500'
                  }`} />
                  <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest font-outfit">
                    {activeBucket.replace('_', ' ')} ({bucketMessages.length})
                  </p>
                </div>
                <button onClick={() => { setActiveBucket(null); setBucketMessages([]); }}
                  className="p-1 hover:bg-white/10 rounded"><X className="w-3.5 h-3.5 text-slate-500" /></button>
              </div>
              {bucketLoading ? (
                <div className="flex justify-center py-4"><Loader2 className="w-5 h-5 text-slate-500 animate-spin" /></div>
              ) : bucketMessages.length === 0 ? (
                <p className="text-xs text-slate-600 text-center py-4">No messages in this bucket</p>
              ) : (
                <div className="space-y-2 max-h-[200px] overflow-auto">
                  {bucketMessages.map(msg => (
                    <div key={msg.id} className="flex items-start gap-2.5 px-2.5 py-2 rounded-lg bg-white/[0.03] border border-white/5 group">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-1.5 mb-0.5">
                          <span className="text-[10px] font-semibold text-white/80">{msg.sender_name}</span>
                          <span className="text-[9px] text-slate-600">#{msg.channel_name}</span>
                        </div>
                        <p className="text-xs text-white/60 leading-relaxed">{msg.content}</p>
                      </div>
                      <button onClick={() => dismissBucketItem(activeBucket, msg.id)}
                        className="p-1 opacity-0 group-hover:opacity-100 hover:bg-white/10 rounded transition-opacity flex-shrink-0"
                        data-testid={`dismiss-${msg.id}`}>
                        <X className="w-3 h-3 text-slate-500" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Keyboard hint */}
          <p className="text-center text-[11px] text-slate-600 font-outfit">
            Press <kbd className="px-1.5 py-0.5 bg-white/5 border border-white/10 rounded text-[10px] text-slate-400 font-mono">Ctrl+K</kbd> to search anything
          </p>
        </div>
      </div>
    </div>
  );
};

export default EnziDashboard;
