import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import {
  MessageSquare, Users, Sparkles, Settings,
  FileText, Download, MoreVertical, Circle
} from 'lucide-react';

/**
 * Chat panel component for in-meeting messaging
 */
export const ChatPanel = ({ messages, onSendMessage }) => {
  const [message, setMessage] = useState('');
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = () => {
    if (message.trim()) {
      onSendMessage(message);
      setMessage('');
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="p-3 border-b border-slate-700">
        <h3 className="font-semibold text-white flex items-center gap-2">
          <MessageSquare className="w-4 h-4" />
          Chat
        </h3>
      </div>
      
      <ScrollArea ref={scrollRef} className="flex-1 p-3">
        <div className="space-y-3">
          {messages.map((msg, idx) => (
            <div key={idx} className="text-sm" data-testid={`chat-message-${idx}`}>
              <span className="font-medium text-turquoise">{msg.sender || msg.user_name}: </span>
              <span className="text-slate-300">{msg.message}</span>
              <span className="text-xs text-slate-500 ml-2">
                {msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString() : ''}
              </span>
            </div>
          ))}
        </div>
      </ScrollArea>
      
      <div className="p-3 border-t border-slate-700">
        <div className="flex gap-2">
          <Input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Type a message..."
            className="bg-slate-800 border-slate-600 text-white"
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            data-testid="chat-input"
          />
          <Button onClick={handleSend} size="sm" className="bg-turquoise hover:bg-turquoise/80" data-testid="chat-send">
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
export const AINotesPanel = ({ notes, isTranscribing }) => {
  return (
    <div className="flex flex-col h-full">
      <div className="p-3 border-b border-slate-700">
        <h3 className="font-semibold text-white flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-turquoise" />
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
              <p className="text-slate-500 text-xs mt-1">Transcription, summaries, and action items</p>
            </div>
          ) : (
            notes.map((note, idx) => (
              <div key={idx} className="p-2 bg-slate-800 rounded-lg text-sm">
                <Badge className={`mb-1 text-xs ${
                  note.type === 'transcription' ? 'bg-blue-500/20 text-blue-400' :
                  note.type === 'summary' ? 'bg-purple-500/20 text-purple-400' :
                  note.type === 'action_item' ? 'bg-orange-500/20 text-orange-400' :
                  'bg-slate-500/20 text-slate-400'
                }`} variant="outline">
                  {note.type}
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
      
      <div className="p-3 border-t border-slate-700 space-y-2">
        <Button variant="outline" size="sm" className="w-full text-slate-300 border-slate-600" data-testid="generate-summary">
          <FileText className="w-4 h-4 mr-2" />
          Generate Summary
        </Button>
        <Button variant="outline" size="sm" className="w-full text-slate-300 border-slate-600" data-testid="export-notes">
          <Download className="w-4 h-4 mr-2" />
          Export Notes
        </Button>
      </div>
    </div>
  );
};

/**
 * Participants panel showing all meeting attendees
 */
export const ParticipantsPanel = ({ participants, onMuteParticipant, isHost }) => {
  return (
    <div className="flex flex-col h-full">
      <div className="p-3 border-b border-slate-700">
        <h3 className="font-semibold text-white flex items-center gap-2">
          <Users className="w-4 h-4" />
          Participants ({participants.length})
        </h3>
      </div>
      
      <ScrollArea className="flex-1 p-3">
        <div className="space-y-2">
          {participants.map((p, idx) => (
            <div key={idx} className="flex items-center justify-between p-2 bg-slate-800 rounded-lg" data-testid={`participant-${idx}`}>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-turquoise/20 flex items-center justify-center">
                  <span className="text-sm font-medium text-turquoise">
                    {p.user_name?.charAt(0)?.toUpperCase()}
                  </span>
                </div>
                <div>
                  <span className="text-sm text-white">{p.user_name}</span>
                  {p.is_host && <Badge className="text-xs ml-2">Host</Badge>}
                </div>
              </div>
              <div className="flex items-center gap-1">
                {isHost && !p.is_host && (
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="h-6 w-6 p-0 text-slate-400 hover:text-white"
                    onClick={() => onMuteParticipant(p.user_id)}
                  >
                    <MoreVertical className="w-4 h-4" />
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>
      
      {isHost && (
        <div className="p-3 border-t border-slate-700">
          <Button variant="outline" size="sm" className="w-full text-slate-300 border-slate-600">
            <Users className="w-4 h-4 mr-2" />
            Create Breakout Rooms
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
      <div className="p-3 border-b border-slate-700">
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
