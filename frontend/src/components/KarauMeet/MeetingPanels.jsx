import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import {
  MessageSquare, Users, Sparkles, Settings,
  FileText, Download, MoreVertical, Circle,
  Mic, MicOff, Volume2, VolumeX
} from 'lucide-react';
import { useTranslation } from '@/utils/i18n';

/**
 * Chat panel component for in-meeting messaging
 */
export const ChatPanel = ({ messages, onSendMessage }) => {
  const { t } = useTranslation();
  const [message, setMessage] = useState('');
  const scrollRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = () => {
    if (message.trim()) {
      onSendMessage(message);
      setMessage('');
      // Keep focus on input for continuous typing
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="p-3 border-b border-karau-border hidden">
        <h3 className="font-semibold text-white flex items-center gap-2">
          <MessageSquare className="w-4 h-4" />
          Chat
        </h3>
      </div>
      
      <ScrollArea ref={scrollRef} className="flex-1 p-3">
        <div className="space-y-3">
          {messages.length === 0 ? (
            <div className="text-center py-4 text-slate-500 text-sm">
              No messages yet. Start the conversation!
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div key={idx} className="text-sm" data-testid={`chat-message-${idx}`}>
                <span className="font-medium text-purple-400">{msg.sender || msg.user_name}: </span>
                <span className="text-slate-300">{msg.message}</span>
                <span className="text-xs text-slate-500 ml-2">
                  {msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString() : ''}
                </span>
              </div>
            ))
          )}
        </div>
      </ScrollArea>
      
      <div className="p-3 border-t border-karau-border">
        <div className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a message..."
            className="flex-1 bg-karau-card border border-karau-border text-white rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-turquoise focus:border-transparent"
            inputMode="text"
            enterKeyHint="send"
            autoComplete="off"
            autoCorrect="on"
            spellCheck="true"
            data-testid="chat-input"
          />
          <Button 
            onClick={handleSend} 
            size="sm" 
            className="bg-purple-500 hover:bg-purple-400 px-4" 
            data-testid="chat-send"
          >
            Send
          </Button>
        </div>
      </div>
    </div>
  );
};

/**
 * AI Notes panel with transcription and summaries
 */
export const AINotesPanel = ({ notes, isTranscribing, onGenerateSummary, isSummarizing, meetingId }) => {
  return (
    <div className="flex flex-col h-full">
      <div className="p-3 border-b border-karau-border hidden">
        <h3 className="font-semibold text-white flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-purple-400" />
          AI Notes
          {isTranscribing && (
            <Badge className="bg-green-500/20 text-green-400 border-green-500/30 text-xs">
              <Circle className="w-2 h-2 mr-1 fill-current animate-pulse" />
              Live
            </Badge>
          )}
        </h3>
      </div>
      
      <ScrollArea className="flex-1 p-3">
        <div className="space-y-3">
          {notes.length === 0 ? (
            <div className="text-center py-8">
              <Sparkles className="w-8 h-8 text-slate-600 mx-auto mb-2" />
              <p className="text-slate-400 text-sm">AI notes will appear here during the meeting...</p>
              <p className="text-slate-500 text-xs mt-1">Enable CC to start live transcription, then generate AI summary</p>
            </div>
          ) : (
            notes.map((note, idx) => (
              <div key={idx} className="p-2 bg-karau-card rounded-lg text-sm">
                <Badge className={`mb-1 text-xs ${
                  note.type === 'transcription' ? 'bg-blue-500/20 text-blue-400' :
                  note.type === 'summary' ? 'bg-purple-500/20 text-purple-400' :
                  note.type === 'action_item' ? 'bg-orange-500/20 text-orange-400' :
                  note.type === 'key_decision' ? 'bg-green-500/20 text-green-400' :
                  'bg-slate-500/20 text-slate-400'
                }`} variant="outline">
                  {note.type === 'key_decision' ? 'decision' : note.type}
                </Badge>
                <p className="text-slate-300">{note.content}</p>
                <span className="text-xs text-slate-500">
                  {new Date(note.timestamp).toLocaleTimeString()}
                </span>
              </div>
            ))
          )}
        </div>
      </ScrollArea>
      
      <div className="p-3 border-t border-karau-border space-y-2">
        <Button 
          variant="outline" 
          size="sm" 
          className="w-full text-slate-300 border-karau-border" 
          data-testid="generate-summary"
          onClick={onGenerateSummary}
          disabled={isSummarizing}
        >
          {isSummarizing ? (
            <>
              <Circle className="w-4 h-4 mr-2 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <FileText className="w-4 h-4 mr-2" />
              Generate AI Summary
            </>
          )}
        </Button>
        <Button variant="outline" size="sm" className="w-full text-slate-300 border-karau-border" data-testid="export-notes"
          onClick={() => {
            const text = notes.map(n => `[${n.type}] ${n.content}`).join('\n');
            const blob = new Blob([text], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url; a.download = 'meeting-notes.txt'; a.click();
          }}
        >
          <Download className="w-4 h-4 mr-2" />
          Export Notes
        </Button>
        {meetingId && (
          <Button variant="outline" size="sm" className="w-full text-purple-400 border-purple-500/30 hover:bg-purple-500/10" data-testid="export-pdf-summary"
            onClick={() => {
              const API = process.env.REACT_APP_BACKEND_URL;
              window.open(`${API}/api/karau-meet/meetings/${meetingId}/summary/pdf`, '_blank');
            }}
          >
            <FileText className="w-4 h-4 mr-2" />
            Download PDF Summary
          </Button>
        )}
      </div>
    </div>
  );
};

/**
 * Participants panel showing all meeting attendees with host controls
 */
export const ParticipantsPanel = ({ participants, onMuteParticipant, onMuteAll, onPassMic, isHost, activeSpeakerId, onOpenBreakoutRooms }) => {
  const [openMenu, setOpenMenu] = useState(null);

  return (
    <div className="flex flex-col h-full">
      <div className="p-3 border-b border-karau-border hidden">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-white flex items-center gap-2">
            <Users className="w-4 h-4" />
            Participants ({participants.length})
          </h3>
          {isHost && participants.length > 1 && (
            <Button
              variant="ghost"
              size="sm"
              className="h-7 text-xs text-slate-400 hover:text-white hover:bg-karau-surface"
              onClick={onMuteAll}
              data-testid="mute-all-btn"
            >
              <VolumeX className="w-3 h-3 mr-1" />
              Mute All
            </Button>
          )}
        </div>
      </div>
      
      <ScrollArea className="flex-1 p-3">
        <div className="space-y-2">
          {participants.map((p, idx) => {
            const isSpeaking = activeSpeakerId === p.user_id;
            return (
              <div
                key={idx}
                className={`flex items-center justify-between p-2 rounded-lg transition-all ${
                  isSpeaking
                    ? 'bg-emerald-500/10 ring-1 ring-emerald-500/50'
                    : 'bg-karau-card'
                }`}
                data-testid={`participant-${idx}`}
              >
                <div className="flex items-center gap-2 min-w-0">
                  <div className={`relative w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                    isSpeaking ? 'bg-emerald-500/30' : 'bg-purple-500/20'
                  }`}>
                    <span className={`text-sm font-medium ${isSpeaking ? 'text-emerald-400' : 'text-purple-400'}`}>
                      {p.user_name?.charAt(0)?.toUpperCase()}
                    </span>
                    {isSpeaking && (
                      <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-emerald-500 rounded-full flex items-center justify-center" data-testid="speaking-indicator">
                        <Volume2 className="w-2 h-2 text-white" />
                      </span>
                    )}
                  </div>
                  <div className="min-w-0">
                    <span className="text-sm text-white truncate block">{p.user_name}</span>
                    <div className="flex items-center gap-1">
                      {p.is_host && <Badge className="text-[10px] px-1 py-0">Host</Badge>}
                      {isSpeaking && <span className="text-[10px] text-emerald-400">Speaking</span>}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-1 flex-shrink-0 relative">
                  {isHost && !p.is_host && (
                    <>
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        className="h-6 w-6 p-0 text-slate-400 hover:text-white"
                        onClick={() => setOpenMenu(openMenu === p.user_id ? null : p.user_id)}
                        data-testid={`participant-menu-${idx}`}
                      >
                        <MoreVertical className="w-4 h-4" />
                      </Button>
                      {openMenu === p.user_id && (
                        <div className="absolute top-7 right-0 bg-karau-surface border border-karau-border rounded-lg shadow-xl z-20 w-36 py-1">
                          <button
                            className="flex items-center gap-2 w-full px-3 py-1.5 text-xs text-slate-300 hover:bg-slate-600 hover:text-white"
                            onClick={() => { onMuteParticipant(p.user_id); setOpenMenu(null); }}
                            data-testid={`mute-participant-${idx}`}
                          >
                            <MicOff className="w-3 h-3" /> Mute
                          </button>
                          <button
                            className="flex items-center gap-2 w-full px-3 py-1.5 text-xs text-slate-300 hover:bg-slate-600 hover:text-white"
                            onClick={() => { onPassMic(p.user_id); setOpenMenu(null); }}
                            data-testid={`pass-mic-${idx}`}
                          >
                            <Mic className="w-3 h-3" /> Pass Mic
                          </button>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </ScrollArea>
      
      {isHost && (
        <div className="p-3 border-t border-karau-border space-y-2">
          {participants.length > 1 && (
            <Button
              variant="outline"
              size="sm"
              className="w-full text-slate-300 border-karau-border"
              onClick={onMuteAll}
              data-testid="mute-all-btn"
            >
              <VolumeX className="w-4 h-4 mr-2" />
              Mute All
            </Button>
          )}
          <Button
            variant="outline"
            size="sm"
            className="w-full text-slate-300 border-karau-border"
            onClick={onOpenBreakoutRooms}
            data-testid="open-breakout-rooms-btn"
          >
            <Users className="w-4 h-4 mr-2" />
            Breakout Rooms
          </Button>
        </div>
      )}
    </div>
  );
};

/**
 * Settings panel for meeting preferences
 */
export const SettingsPanel = ({ settings, onUpdateSettings }) => {
  return (
    <div className="flex flex-col h-full">
      <div className="p-3 border-b border-karau-border hidden">
        <h3 className="font-semibold text-white flex items-center gap-2">
          <Settings className="w-4 h-4" />
          Settings
        </h3>
      </div>
      
      <ScrollArea className="flex-1 p-3">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label className="text-white">AI Transcription</Label>
              <p className="text-xs text-slate-500">Real-time speech to text</p>
            </div>
            <Switch 
              checked={settings.ai_transcription} 
              onCheckedChange={(checked) => onUpdateSettings({ ai_transcription: checked })}
              data-testid="setting-transcription"
            />
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <Label className="text-white">Auto-generate Summary</Label>
              <p className="text-xs text-slate-500">Create meeting summary at end</p>
            </div>
            <Switch 
              checked={settings.auto_summary} 
              onCheckedChange={(checked) => onUpdateSettings({ auto_summary: checked })}
              data-testid="setting-summary"
            />
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <Label className="text-white">Noise Cancellation</Label>
              <p className="text-xs text-slate-500">Reduce background noise</p>
            </div>
            <Switch 
              checked={settings.noise_cancellation} 
              onCheckedChange={(checked) => onUpdateSettings({ noise_cancellation: checked })}
              data-testid="setting-noise"
            />
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <Label className="text-white">HD Video</Label>
              <p className="text-xs text-slate-500">Higher quality video (uses more bandwidth)</p>
            </div>
            <Switch 
              checked={settings.hd_video} 
              onCheckedChange={(checked) => onUpdateSettings({ hd_video: checked })}
              data-testid="setting-hd"
            />
          </div>
        </div>
      </ScrollArea>
    </div>
  );
};
