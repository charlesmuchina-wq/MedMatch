/**
 * EnziChatView — The main chat view for ENZI messenger
 * Extracted from LumiMessenger.jsx for maintainability
 * Contains: channel header, messages, input bar, side panels
 */
import {
  Send, ArrowLeft, Hash, Users, Loader2, Paperclip, User, Phone, Video,
  Sparkles, Brain, AlertTriangle, Shield, Command, Network, Zap, TrendingDown,
  Bell, Smile, Clock, ClipboardList, BellOff
} from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useTranslation } from '@/utils/i18n';

import {
  ChannelIcon, StatusDot, MessageBubble, ThreadPanel, MembersPanel,
  AiProductivityPanel, AiChatPanel, AlertsPanel,
  KnowledgeGraphPanel, BottleneckPanel, SimulationPanel,
  NotificationsPanel, EmojiPicker, LumiBrand,
  ESY, STATUS_LABELS
} from '@/components/Lumi';
import AIWritingToolbar from '@/components/Lumi/AIWritingToolbar';
import ConversationSummary from '@/components/Lumi/ConversationSummary';
import BotActionsBar from '@/components/Lumi/BotActionsBar';
import SlashCommandAutocomplete from '@/components/Lumi/SlashCommandAutocomplete';
import E2EEIndicator from '@/components/Lumi/E2EEIndicator';
import MeetingChannelBanner from '@/components/Lumi/MeetingChannelBanner';

const EnziChatView = ({
  activeChannel, user, token, messages, messageText, setMessageText,
  sending, uploading, presenceMap, activeTyping,
  // Panel visibility
  showAiPanel, setShowAiPanel, showAiChat, setShowAiChat,
  showAlerts, setShowAlerts, showKnowledgeGraph, setShowKnowledgeGraph,
  showBottlenecks, setShowBottlenecks, showSimulation, setShowSimulation,
  showNotifications, setShowNotifications, showMembers, setShowMembers,
  showThread, setShowThread, showEmojiPicker, setShowEmojiPicker,
  showSummary, setShowSummary, showCommandBar, setShowCommandBar,
  setShowScheduleModal, setShowMeetingModal, setShowNotifSettings,
  // Handlers
  handleSend, handleReact, handleEditMessage, handleDeleteMessage,
  handleStartCall, handleFileShare, handleKeyDown, handleTyping,
  handleEmojiSelect, closeAllPanels,
  // Refs
  messagesEndRef, fileInputRef,
  // Navigation
  setMobileSidebar, mobileSidebar, channels, dms,
}) => {
  const { t } = useTranslation();

  return (
    <div className={`${!mobileSidebar ? 'flex' : 'hidden'} md:flex flex-col flex-1 min-w-0 bg-white lumi-light-panel`}>
      {/* Channel Header */}
      <div className="h-14 flex items-center justify-between px-5 border-b border-slate-200 flex-shrink-0 bg-white">
        <div className="flex items-center gap-3">
          <button className="md:hidden p-2 text-slate-500 hover:text-slate-900" onClick={() => setMobileSidebar(true)}><ArrowLeft className="w-4 h-4" /></button>
          {activeChannel.channel_type === 'dm' ? (<>
            <div className="relative"><div className="w-9 h-9 rounded-full bg-[#36454F] flex items-center justify-center"><User className="w-4 h-4 text-white" /></div><StatusDot status={presenceMap[activeChannel.dm_partner?.user_id] || 'offline'} /></div>
            <div><h2 className="text-sm font-semibold text-slate-900">{activeChannel.dm_partner?.name || activeChannel.name}</h2><p className="text-[11px] text-slate-500">{STATUS_LABELS[presenceMap[activeChannel.dm_partner?.user_id]] || 'Offline'}</p></div>
          </>) : (<>
            <div className="w-9 h-9 rounded-md bg-slate-100 flex items-center justify-center text-slate-600"><ChannelIcon type={activeChannel.channel_type} /></div>
            <div><h2 className="text-sm font-semibold text-slate-900">#{activeChannel.name}</h2><p className="text-[11px] text-slate-500">{activeChannel.members?.length || 0} members</p></div>
          </>)}
        </div>
        <div className="flex items-center gap-1">
          {activeChannel.channel_type === 'dm' && (
            <>
              <button onClick={() => handleStartCall('voice')} className="p-2 text-slate-500 hover:text-[#008080] hover:bg-[#008080]/5 rounded-md transition-colors" data-testid="voice-call-btn" title="Voice Call"><Phone className="w-4 h-4" /></button>
              <button onClick={() => handleStartCall('video')} className="p-2 text-slate-500 hover:text-[#008080] hover:bg-[#008080]/5 rounded-md transition-colors" data-testid="video-call-btn" title="Video Call"><Video className="w-4 h-4" /></button>
            </>
          )}
          <button onClick={() => setShowCommandBar(true)} className="p-2 rounded-md text-slate-500 hover:text-slate-700 hover:bg-slate-100 transition-colors" data-testid="command-bar-btn" title="Command Bar (Ctrl+K)"><Command className="w-4 h-4" /></button>
          <button onClick={() => { closeAllPanels(); setShowAiChat(!showAiChat); }} className={`p-2 rounded-md transition-colors ${showAiChat ? 'bg-[#00CEC9]/10' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100'}`} style={showAiChat ? { color: ESY.turquoise } : {}} data-testid="ai-chat-btn" title="Ask AI"><Sparkles className="w-4 h-4" /></button>
          <button onClick={() => { closeAllPanels(); setShowAlerts(!showAlerts); }} className={`p-2 rounded-md transition-colors ${showAlerts ? 'bg-[#D63031]/10' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100'}`} style={showAlerts ? { color: ESY.deepRed } : {}} data-testid="alerts-btn" title="Alerts & Decisions"><AlertTriangle className="w-4 h-4" /></button>
          <button onClick={() => { closeAllPanels(); setShowKnowledgeGraph(!showKnowledgeGraph); }} className={`p-2 rounded-md transition-colors ${showKnowledgeGraph ? 'bg-[#00CEC9]/10' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100'}`} style={showKnowledgeGraph ? { color: ESY.turquoise } : {}} data-testid="knowledge-graph-btn" title="Knowledge Graph"><Network className="w-4 h-4" /></button>
          <button onClick={() => { closeAllPanels(); setShowBottlenecks(!showBottlenecks); }} className={`p-2 rounded-md transition-colors ${showBottlenecks ? 'bg-[#D63031]/10' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100'}`} style={showBottlenecks ? { color: ESY.deepRed } : {}} data-testid="bottleneck-btn" title="Bottlenecks"><TrendingDown className="w-4 h-4" /></button>
          <button onClick={() => { closeAllPanels(); setShowSimulation(!showSimulation); }} className={`p-2 rounded-md transition-colors ${showSimulation ? 'bg-[#E84393]/10' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100'}`} style={showSimulation ? { color: ESY.pink } : {}} data-testid="simulation-btn" title="What-If Simulator"><Zap className="w-4 h-4" /></button>
          <button onClick={() => { closeAllPanels(); setShowNotifications(!showNotifications); }} className={`p-2 rounded-md transition-colors relative ${showNotifications ? 'bg-[#E84393]/10' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100'}`} style={showNotifications ? { color: ESY.pink } : {}} data-testid="notifications-btn" title="Smart Notifications"><Bell className="w-3.5 h-3.5" /><span className="absolute top-1 right-1 w-1.5 h-1.5 rounded-full" style={{ backgroundColor: ESY.deepRed }} /></button>
          <button onClick={() => { closeAllPanels(); setShowAiPanel(!showAiPanel); }} className={`p-2 rounded-md transition-colors ${showAiPanel ? 'text-[#008080] bg-[#008080]/5' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100'}`} data-testid="ai-panel-btn" title="AI Insights"><Brain className="w-4 h-4" /></button>
          <button onClick={() => setShowScheduleModal(true)} className="p-2 rounded-md text-slate-500 hover:text-amber-600 hover:bg-amber-50 transition-colors" data-testid="schedule-msg-btn" title="Schedule Message"><Clock className="w-4 h-4" /></button>
          <button onClick={() => setShowMeetingModal(true)} className="p-2 rounded-md text-slate-500 hover:text-[#6C5CE7] hover:bg-[#6C5CE7]/5 transition-colors" data-testid="start-meeting-btn" title="Start AI KARAU Meeting"><Video className="w-4 h-4" /></button>
          <button onClick={() => setShowSummary(!showSummary)} className={`p-2 rounded-md transition-colors ${showSummary ? 'text-violet-600 bg-violet-50' : 'text-slate-500 hover:text-violet-600 hover:bg-violet-50'}`} data-testid="summarize-channel-btn" title="Summarize Conversation"><ClipboardList className="w-4 h-4" /></button>
          <button onClick={() => setShowNotifSettings(true)} className="p-2 rounded-md text-slate-500 hover:text-slate-700 hover:bg-slate-100 transition-colors" data-testid="notif-settings-btn" title="Notification Settings"><BellOff className="w-4 h-4" /></button>
          <button onClick={() => setShowMembers(!showMembers)} className={`p-2 rounded-md transition-colors ${showMembers ? 'text-[#008080] bg-[#008080]/5' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100'}`} data-testid="channel-members-btn"><Users className="w-4 h-4" /></button>
        </div>
      </div>

      {/* Bot Actions Bar */}
      {activeChannel?.channel_type !== 'dm' && (
        <BotActionsBar channelId={activeChannel?.id} token={token} />
      )}

      {/* E2EE Status */}
      <E2EEIndicator channelId={activeChannel?.id} token={token} isDm={activeChannel?.channel_type === 'dm'} />

      {/* Meeting Follow-up Banner */}
      {activeChannel.channel_type === 'meeting-followup' && (
        <MeetingChannelBanner
          channel={activeChannel}
          token={token}
          isAdmin={activeChannel?.members?.some(m => m.user_id === user?.user_id && m.role === 'admin')}
        />
      )}

      <div className="flex flex-1 overflow-hidden">
        <div className="flex-1 flex flex-col min-w-0">
          {/* Conversation Summary */}
          {showSummary && activeChannel && (
            <div className="px-4 pt-3">
              <ConversationSummary channelId={activeChannel.id} token={token} onClose={() => setShowSummary(false)} />
            </div>
          )}

          {/* Messages */}
          <ScrollArea className="flex-1 py-3">
            <div
              role="log"
              aria-live="polite"
              aria-relevant="additions"
              aria-label={`Conversation with ${activeChannel?.channel_type === 'dm' ? activeChannel?.dm_partner?.name || 'contact' : '#' + (activeChannel?.name || 'channel')}`}
              data-testid="message-thread"
            >
            {messages.length === 0 && (
              <div className="flex flex-col items-center justify-center h-full text-center px-6">
                <LumiBrand variant="text-light" size="md" className="mb-4" />
                <p className="text-slate-600 text-sm">{t('lumi.noMessages') || 'No messages yet. Start the conversation!'}</p>
              </div>
            )}
            {messages.filter(m => !m.thread_parent_id).map((msg, i, arr) => {
              const prevSameSender = i > 0 && arr[i - 1].sender_id === msg.sender_id && arr[i - 1].type !== 'system';
              return <MessageBubble key={msg.id} msg={msg} isOwn={msg.sender_id === user?.user_id} prevSameSender={prevSameSender} onReact={handleReact} onThread={(id) => setShowThread(id)} onEdit={handleEditMessage} onDelete={handleDeleteMessage} token={token} />;
            })}
            <div ref={messagesEndRef} />
            </div>
          </ScrollArea>

          {/* Typing indicator */}
          {activeTyping.length > 0 && <div className="px-5 py-1"><span className="text-xs text-[#006666] font-medium animate-pulse">{activeTyping.join(', ')} typing...</span></div>}

          {/* AI Writing Toolbar */}
          <div className="px-4 py-1.5 border-t border-slate-100">
            <AIWritingToolbar
              messageText={messageText}
              onTextChange={setMessageText}
              messages={messages}
              channelName={activeChannel?.name || ''}
              token={token}
            />
          </div>

          {/* Message Input */}
          <div className="p-4 pt-2 border-t border-slate-100">
            <input type="file" ref={fileInputRef} className="hidden" onChange={handleFileShare} accept="image/*,.pdf,.doc,.docx,.txt,.csv" data-testid="file-input" aria-label="Attach file to message" />
            <form
              role="form"
              aria-label={`Send message in ${activeChannel?.channel_type === 'dm' ? activeChannel?.dm_partner?.name || 'conversation' : '#' + (activeChannel?.name || 'channel')}`}
              onSubmit={(e) => { e.preventDefault(); if (messageText.trim() && !sending) handleSend(); }}
              className="relative flex items-center gap-2 border border-slate-200 rounded-lg px-4 py-2.5 focus-within:ring-2 focus-within:ring-[#008080]/20 focus-within:border-[#008080] transition-all bg-white shadow-sm"
            >
              <SlashCommandAutocomplete channelId={activeChannel?.id} token={token} messageText={messageText} onSelect={(cmd) => setMessageText(cmd)} />
              <button type="button" onClick={() => fileInputRef.current?.click()} disabled={uploading} className="p-1 text-slate-500 hover:text-[#008080] rounded transition-colors" data-testid="attach-file-btn" aria-label="Attach a file">
                {uploading ? <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" /> : <Paperclip className="w-4 h-4" aria-hidden="true" />}
              </button>
              <div className="relative">
                <button type="button" onClick={() => setShowEmojiPicker(!showEmojiPicker)} className={`p-1 rounded transition-colors ${showEmojiPicker ? 'text-[#008080] bg-[#008080]/10' : 'text-slate-500 hover:text-[#008080]'}`} data-testid="emoji-picker-btn" aria-label="Insert emoji" aria-expanded={showEmojiPicker} aria-haspopup="dialog">
                  <Smile className="w-4 h-4" aria-hidden="true" />
                </button>
                <EmojiPicker isOpen={showEmojiPicker} onClose={() => setShowEmojiPicker(false)} onSelect={handleEmojiSelect} position="above" />
              </div>
              <label htmlFor="message-input" className="sr-only">
                Message {activeChannel?.channel_type === 'dm' ? activeChannel?.dm_partner?.name || '' : '#' + (activeChannel?.name || '')}
              </label>
              <input
                id="message-input"
                value={messageText}
                onChange={e => { setMessageText(e.target.value); handleTyping(); }}
                onKeyDown={handleKeyDown}
                placeholder={`Message ${activeChannel.channel_type === 'dm' ? activeChannel.dm_partner?.name || '' : '#' + activeChannel.name}`}
                className="flex-1 text-sm bg-transparent outline-none text-slate-900 placeholder:text-slate-500"
                data-testid="message-input"
                aria-describedby="message-input-hint"
              />
              <span id="message-input-hint" className="sr-only">
                Press Enter to send. Shift+Enter to insert a new line.
              </span>
              <button type="submit" onClick={handleSend} disabled={!messageText.trim() || sending}
                className={`p-2 rounded-md transition-colors ${messageText.trim() ? 'text-white hover:opacity-90' : 'text-slate-400'}`}
                style={messageText.trim() ? { background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` } : {}}
                data-testid="send-message-btn"
                aria-label="Send message"
              ><Send className="w-4 h-4" aria-hidden="true" /></button>
            </form>
          </div>
        </div>

        {/* Side Panels */}
        {showThread && <ThreadPanel messageId={showThread} onClose={() => setShowThread(null)} token={token} />}
        {showAiPanel && activeChannel && <AiProductivityPanel channelId={activeChannel.id} channelName={activeChannel.name} onClose={() => setShowAiPanel(false)} token={token} />}
        {showAiChat && activeChannel && <AiChatPanel channelId={activeChannel.id} onClose={() => setShowAiChat(false)} token={token} />}
        {showAlerts && <AlertsPanel onClose={() => setShowAlerts(false)} token={token} />}
        {showKnowledgeGraph && <KnowledgeGraphPanel onClose={() => setShowKnowledgeGraph(false)} token={token} />}
        {showBottlenecks && <BottleneckPanel onClose={() => setShowBottlenecks(false)} token={token} />}
        {showSimulation && <SimulationPanel onClose={() => setShowSimulation(false)} token={token} />}
        {showNotifications && <NotificationsPanel onClose={() => setShowNotifications(false)} token={token} onNavigate={(item) => { const ch = channels.find(c => c.id === item.id) || dms.find(d => d.id === item.id); if (ch) { setActiveChannel(ch); setMobileSidebar(false); } }} />}
        {showMembers && <MembersPanel channelId={activeChannel.id} onClose={() => setShowMembers(false)} token={token} />}
      </div>
    </div>
  );
};

export default EnziChatView;
