/**
 * EnziSidebar — ENZI channel navigation sidebar
 * Extracted from LumiMessenger for maintainability
 */
import {
  Plus, ArrowLeft, Hash, Users, Search, LogOut,
  Zap, Clock, Edit, X, Settings, BarChart3, Shield,
  ClipboardList, Globe, Sun, Moon, UserPlus, Building2, Keyboard
} from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useTranslation } from '@/utils/i18n';
import { ChannelIcon, LumiBrand, ESY, STATUS_COLORS } from '@/components/Lumi';

const EnziSidebar = ({
  mobileSidebar, sidebarView, setSidebarView,
  searchQuery, setSearchQuery, globalSearch, setGlobalSearch,
  showSearchResults, setShowSearchResults, searchResults,
  handleGlobalSearch,
  recentConversations, sortedChannels, discoverChannels, dms,
  activeChannel, setActiveChannel, setMobileSidebar,
  unreadCounts, presenceMap, predictedChannelIds,
  bucketCounts, openBucket,
  setShowNewMsgPanel, setShowCreateModal, setShowNewDmModal,
  setShowThread, setShowMembers, setShowAiPanel,
  showAdminTools, setShowAdminTools,
  isDark, toggleTheme, user, navigate, channels,
  setShowVisualizations, setShowRetention, setShowAuditLog,
  setShowCompliance, setShowShortcuts, setShowProfile,
  handleJoinChannel, handleStartDm, trackAction,
}) => {
  const { t } = useTranslation();

  const selectItem = (item) => {
    setActiveChannel(item);
    setMobileSidebar(false);
    setShowThread(null);
    setShowMembers(false);
    setShowAiPanel(false);
  };

  return (
    <div className={`${mobileSidebar ? 'flex' : 'hidden'} md:flex flex-col w-full md:w-[280px] bg-[#0D1117] flex-shrink-0 border-r border-white/5`}>
      {/* Header */}
      <div className="h-14 flex items-center justify-between px-4 border-b border-white/10">
        <div className="flex items-center gap-2.5">
          <LumiBrand variant="inline-dark" size="xs" showTagline />
        </div>
        <button onClick={() => navigate('/')} className="p-2 text-white/80 hover:text-white hover:bg-white/10 rounded-md transition-colors" data-testid="back-to-karau"><ArrowLeft className="w-4 h-4" /></button>
      </div>

      {/* Quick Actions: Recent / New Message */}
      <div className="px-3 pt-3 pb-2 flex gap-2">
        <button onClick={() => setSidebarView('recent')}
          className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-medium transition-all ${sidebarView === 'recent' ? 'bg-[#00CEC9]/10 text-[#00CEC9] border border-[#00CEC9]/20' : 'bg-white/5 text-white/70 hover:bg-white/10 border border-transparent'}`}
          data-testid="sidebar-recent-btn">
          <Clock className="w-3.5 h-3.5" />Recent
        </button>
        <button onClick={() => setShowNewMsgPanel(true)}
          className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-medium bg-white/5 text-white/70 hover:bg-white/10 border border-transparent hover:border-white/10 transition-all"
          data-testid="sidebar-new-msg-btn">
          <Edit className="w-3.5 h-3.5" />New Message
        </button>
      </div>

      {/* Search */}
      <div className="px-3 pb-1">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-white/50" />
          <input value={globalSearch || searchQuery} onChange={e => { setSearchQuery(e.target.value); handleGlobalSearch(e.target.value); setSidebarView('channels'); }}
            placeholder={t('lumi.searchChannels') || 'Search channels & people...'}
            className="w-full pl-9 h-8 bg-white/10 border-0 rounded-md text-sm text-white placeholder:text-white/40 outline-none focus:bg-white/15 transition-colors" data-testid="search-channels" />
          {globalSearch && <button onClick={() => { setGlobalSearch(''); setSearchQuery(''); setShowSearchResults(false); }} className="absolute right-2 top-1/2 -translate-y-1/2 text-white/60 hover:text-white"><X className="w-3.5 h-3.5" /></button>}
        </div>
        {showSearchResults && searchResults.length > 0 && (
          <div className="mt-1 max-h-48 overflow-y-auto bg-[#0F1923] border border-white/10 rounded-md shadow-lg" data-testid="search-results">
            {searchResults.map((r, i) => (
              <button key={i} onClick={() => { const ch = channels.find(c => c.id === r.channel_id) || dms.find(d => d.id === r.channel_id); if (ch) { selectItem(ch); } setShowSearchResults(false); setGlobalSearch(''); setSearchQuery(''); }}
                className="w-full px-3 py-2 text-left hover:bg-white/10 border-b border-white/5 last:border-0" data-testid={`search-result-${i}`}>
                <span className="text-[10px] text-[#00CEC9] font-medium">#{r.channel_name}</span>
                <p className="text-xs text-white/80 truncate">{r.content}</p>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Smart Buckets */}
      {(bucketCounts.urgent > 0 || bucketCounts.action_required > 0 || bucketCounts.meeting_request > 0) && (
        <div className="px-3 pb-2">
          <div className="bg-white/[0.02] rounded-lg border border-white/5 overflow-hidden">
            <div className="flex items-center gap-1.5 px-2.5 py-1.5">
              <Zap className="w-3 h-3 text-amber-400" />
              <span className="text-[10px] font-semibold text-white/60 uppercase tracking-wider flex-1">Priority</span>
            </div>
            <div className="px-1 pb-1 space-y-0.5">
              {[
                { key: 'urgent', label: 'Urgent', color: 'bg-red-500', textColor: 'text-red-400' },
                { key: 'action_required', label: 'Action Required', color: 'bg-amber-500', textColor: 'text-amber-400' },
                { key: 'meeting_request', label: 'Meetings', color: 'bg-blue-500', textColor: 'text-blue-400' },
              ].filter(b => bucketCounts[b.key] > 0).map(b => (
                <button key={b.key} onClick={() => { openBucket(b.key); setMobileSidebar(false); }}
                  className="w-full flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-white/5 transition-colors"
                  data-testid={`sidebar-bucket-${b.key}`}>
                  <div className={`w-1.5 h-1.5 rounded-full ${b.color}`} />
                  <span className="text-xs text-white/70 flex-1 text-left">{b.label}</span>
                  <span className={`text-[10px] font-bold ${b.textColor}`}>{bucketCounts[b.key]}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      <ScrollArea className="flex-1 py-1">
        <div className="px-3">
          {sidebarView === 'recent' ? (
            <>
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-[11px] font-bold text-white/90 uppercase tracking-widest">Recent</span>
                <button onClick={() => setSidebarView('channels')} className="text-[9px] text-[#00CEC9] hover:underline">All Channels</button>
              </div>
              {recentConversations.map(item => (
                <button key={item.id} onClick={() => selectItem(item)}
                  className={`w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md transition-colors mb-0.5 ${activeChannel?.id === item.id ? 'bg-white/15 text-white' : 'text-white/80 hover:bg-white/10 hover:text-white'}`}
                  data-testid={`recent-${item.id}`}>
                  {item._type === 'dm' ? (
                    <div className="relative">
                      <div className="w-6 h-6 rounded-full bg-slate-500 flex items-center justify-center text-[9px] font-semibold text-white">
                        {(item.dm_partner?.name || item.dm_partner?.email || '?')[0].toUpperCase()}
                      </div>
                      <span className={`absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full ring-1 ring-[#0D1117] ${STATUS_COLORS[presenceMap[item.dm_partner?.user_id] || 'offline']}`} />
                    </div>
                  ) : (
                    <ChannelIcon type={item.channel_type} />
                  )}
                  <span className="flex-1 text-sm truncate text-left">
                    {item._type === 'dm' ? (item.dm_partner?.name || item.dm_partner?.email || 'User') : item.name}
                  </span>
                  {unreadCounts[item.id] > 0 && <span className="min-w-[16px] h-[16px] flex items-center justify-center rounded-full text-[8px] font-bold text-white" style={{ backgroundColor: ESY.pink }}>{unreadCounts[item.id]}</span>}
                </button>
              ))}
              {recentConversations.length === 0 && <p className="text-[11px] text-white/50 px-2.5 py-3 text-center">No conversations yet</p>}
            </>
          ) : (
            <>
              {/* Channels */}
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-[11px] font-bold text-white/90 uppercase tracking-widest">Channels</span>
                <button onClick={() => setShowCreateModal(true)} className="p-1 text-white/80 hover:text-white hover:bg-white/10 rounded transition-colors" data-testid="add-channel-btn"><Plus className="w-3.5 h-3.5" /></button>
              </div>
              {sortedChannels.map(ch => (
                <button key={ch.id} onClick={() => { selectItem(ch); trackAction('channel_visit', ch.id, ch.name); }}
                  className={`w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md transition-colors mb-0.5 ${activeChannel?.id === ch.id ? 'bg-white/15 text-white font-semibold' : 'text-white/80 hover:bg-white/10 hover:text-white'}`} data-testid={`channel-${ch.id}`}>
                  <ChannelIcon type={ch.channel_type} /><span className="flex-1 text-sm truncate text-left">{ch.name}</span>
                  {predictedChannelIds.has(ch.id) && <Zap className="w-3 h-3 text-amber-400 flex-shrink-0" title="Predicted for you" />}
                  {unreadCounts[ch.id] > 0 && <span className="min-w-[18px] h-[18px] flex items-center justify-center rounded-full text-[9px] font-bold text-white" style={{ backgroundColor: ESY.pink }} data-testid={`unread-${ch.id}`}>{unreadCounts[ch.id]}</span>}
                </button>
              ))}

              {discoverChannels.length > 0 && (<>
                <div className="flex items-center mt-3 mb-1.5"><span className="text-[11px] font-bold text-white/90 uppercase tracking-widest">Discover</span></div>
                {discoverChannels.map(ch => (
                  <button key={ch.id} onClick={() => handleJoinChannel(ch)} className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md text-white/80 hover:bg-white/10 hover:text-white mb-0.5" data-testid={`discover-${ch.id}`}>
                    <ChannelIcon type={ch.channel_type} /><span className="flex-1 text-sm truncate text-left">{ch.name}</span><Plus className="w-3 h-3 opacity-70" />
                  </button>
                ))}
              </>)}

              {/* DMs */}
              <div className="flex items-center justify-between mt-3 mb-1.5">
                <span className="text-[11px] font-bold text-white/90 uppercase tracking-widest">Direct Messages</span>
                <button onClick={() => setShowNewMsgPanel(true)} className="p-1 text-white/80 hover:text-white hover:bg-white/10 rounded transition-colors" data-testid="new-dm-btn"><UserPlus className="w-3.5 h-3.5" /></button>
              </div>
              {dms.map(dm => (
                <button key={dm.id} onClick={() => { selectItem(dm); trackAction('dm_visit', dm.id, dm.dm_partner?.name); }}
                  className={`w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md transition-colors mb-0.5 ${activeChannel?.id === dm.id ? 'bg-white/15 text-white' : 'text-white/80 hover:bg-white/10 hover:text-white'}`}
                  data-testid={`dm-${dm.id}`}>
                  <div className="relative">
                    <div className="w-6 h-6 rounded-full bg-slate-500 flex items-center justify-center text-[9px] font-semibold text-white">
                      {(dm.dm_partner?.name || dm.dm_partner?.email || '?')[0].toUpperCase()}
                    </div>
                    <span className={`absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full ring-1 ring-[#0D1117] ${STATUS_COLORS[presenceMap[dm.dm_partner?.user_id] || 'offline']}`} />
                  </div>
                  <span className="flex-1 text-sm truncate text-left">{dm.dm_partner?.name || dm.dm_partner?.email || 'User'}</span>
                  {unreadCounts[dm.id] > 0 && <span className="min-w-[16px] h-[16px] flex items-center justify-center rounded-full text-[8px] font-bold text-white" style={{ backgroundColor: ESY.pink }}>{unreadCounts[dm.id]}</span>}
                </button>
              ))}
            </>
          )}
        </div>
      </ScrollArea>

      {/* Footer */}
      <div className="border-t border-white/10 p-3">
        <div className="flex items-center gap-2">
          <button onClick={() => setShowProfile(true)} className="flex items-center gap-2 flex-1 p-2 rounded-lg hover:bg-white/5 transition-colors" data-testid="sidebar-user-profile">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-violet-500 flex items-center justify-center text-xs font-bold text-white">
              {(user?.full_name || user?.email || '?')[0].toUpperCase()}
            </div>
            <div className="flex-1 min-w-0 text-left">
              <p className="text-xs text-white font-medium truncate">{user?.full_name || user?.email}</p>
              <p className="text-[10px] text-white/50 truncate">{user?.role || 'Member'}</p>
            </div>
          </button>
          <div className="flex items-center gap-0.5">
            <button onClick={toggleTheme} className="p-1.5 text-white/50 hover:text-white hover:bg-white/10 rounded-md transition-colors" data-testid="theme-toggle-btn" title={isDark ? 'Light Mode' : 'Dark Mode'}>
              {isDark ? <Sun className="w-3.5 h-3.5" /> : <Moon className="w-3.5 h-3.5" />}
            </button>
            <button onClick={() => setShowAdminTools(!showAdminTools)} className={`p-1.5 rounded-md transition-colors ${showAdminTools ? 'text-[#00CEC9] bg-white/10' : 'text-white/50 hover:text-white hover:bg-white/10'}`} data-testid="admin-tools-toggle" title="Admin & Tools">
              <Settings className="w-3.5 h-3.5" />
            </button>
            <button onClick={() => { localStorage.removeItem('token'); localStorage.removeItem('karau_user'); navigate('/'); }} className="p-1.5 text-white/50 hover:text-red-400 hover:bg-red-500/10 rounded-md transition-colors" data-testid="lumi-logout" title="Logout">
              <LogOut className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {showAdminTools && (
          <div className="px-3 pb-2 space-y-1 border-t border-white/5 pt-2" data-testid="admin-tools-panel">
            <div className="grid grid-cols-2 gap-1">
              <button onClick={() => setShowVisualizations(true)} className="flex items-center gap-1.5 px-2.5 py-2 bg-white/5 hover:bg-white/10 rounded-md transition-colors" data-testid="open-visualizations-btn">
                <BarChart3 className="w-3 h-3" style={{ color: ESY.pink }} /><span className="text-[10px] text-white/80">Analytics</span>
              </button>
              <button onClick={() => setShowRetention(true)} className="flex items-center gap-1.5 px-2.5 py-2 bg-white/5 hover:bg-white/10 rounded-md transition-colors" data-testid="open-retention-btn">
                <Shield className="w-3 h-3" style={{ color: ESY.deepRed }} /><span className="text-[10px] text-white/80">Retention</span>
              </button>
              <button onClick={() => setShowAuditLog(true)} className="flex items-center gap-1.5 px-2.5 py-2 bg-white/5 hover:bg-white/10 rounded-md transition-colors" data-testid="open-audit-btn">
                <ClipboardList className="w-3 h-3" style={{ color: ESY.turquoise }} /><span className="text-[10px] text-white/80">Audit Log</span>
              </button>
              <button onClick={() => setShowCompliance(true)} className="flex items-center gap-1.5 px-2.5 py-2 bg-white/5 hover:bg-white/10 rounded-md transition-colors" data-testid="open-compliance-btn">
                <Globe className="w-3 h-3" style={{ color: '#00B894' }} /><span className="text-[10px] text-white/80">Compliance</span>
              </button>
              <button onClick={() => setShowShortcuts(true)} className="flex items-center gap-1.5 px-2.5 py-2 bg-white/5 hover:bg-white/10 rounded-md transition-colors" data-testid="open-shortcuts-btn">
                <Keyboard className="w-3 h-3 text-white/60" /><span className="text-[10px] text-white/80">Shortcuts</span>
              </button>
              <button onClick={() => navigate('/karau-meet')} className="flex items-center gap-1.5 px-2.5 py-2 bg-white/5 hover:bg-white/10 rounded-md transition-colors" data-testid="switch-to-karau-footer">
                <Building2 className="w-3 h-3" style={{ color: ESY.turquoise }} /><span className="text-[10px] text-white/80">AI KARAU</span>
              </button>
            </div>
            <button onClick={() => navigate('/')} className="w-full flex items-center justify-center gap-1.5 px-2.5 py-1.5 bg-white/5 hover:bg-white/10 rounded-md transition-colors" data-testid="return-to-portal">
              <ArrowLeft className="w-3 h-3 text-white/60" /><span className="text-[10px] text-white/80">Return to Portal</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default EnziSidebar;
