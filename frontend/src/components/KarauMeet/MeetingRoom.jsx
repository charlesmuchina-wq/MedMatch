import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import {
  Video, VideoOff, Mic, MicOff, Phone, PhoneOff,
  Monitor, MonitorOff, MessageSquare, Users, Settings,
  Hand, MoreVertical, Grid, Maximize, Minimize,
  Copy, Share2, Shield, Sparkles, FileText, Loader2,
  Circle, Square, Image, Calendar, Download,
  AlertTriangle, Check, X, Palette
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from '@/components/ui/dialog';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';

const API = process.env.REACT_APP_BACKEND_URL;

// Virtual Background Options
const VIRTUAL_BACKGROUNDS = [
  { id: 'none', name: 'None', type: 'none' },
  { id: 'blur', name: 'Blur', type: 'blur' },
  { id: 'office', name: 'Office', type: 'image', url: 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800' },
  { id: 'nature', name: 'Nature', type: 'image', url: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800' },
  { id: 'abstract', name: 'Abstract', type: 'image', url: 'https://images.unsplash.com/photo-1557682250-33bd709cbe85?w=800' },
  { id: 'city', name: 'City', type: 'image', url: 'https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?w=800' },
];

// Video participant component with virtual background support
const VideoParticipant = ({ participant, isLocal, stream, isSpeaking, virtualBg }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    if (videoRef.current && stream) {
      videoRef.current.srcObject = stream;
    }
  }, [stream]);

  // Apply virtual background effect (simplified - real implementation would use ML)
  useEffect(() => {
    if (isLocal && virtualBg && virtualBg !== 'none' && canvasRef.current && videoRef.current) {
      // In production, use TensorFlow.js or MediaPipe for segmentation
      // This is a placeholder for the blur effect
      if (virtualBg === 'blur') {
        canvasRef.current.style.filter = 'blur(0px)';
        canvasRef.current.style.backdropFilter = 'blur(10px)';
      }
    }
  }, [virtualBg, isLocal]);

  return (
    <div className={`relative rounded-xl overflow-hidden bg-slate-900 ${isSpeaking ? 'ring-2 ring-turquoise' : ''}`}>
      {participant?.video_enabled && stream ? (
        <>
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted={isLocal}
            className="w-full h-full object-cover"
          />
          <canvas ref={canvasRef} className="hidden" />
        </>
      ) : (
        <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-slate-800 to-slate-900 min-h-[200px]">
          <div className="w-20 h-20 rounded-full bg-turquoise/20 flex items-center justify-center">
            <span className="text-3xl font-bold text-turquoise">
              {participant?.user_name?.charAt(0)?.toUpperCase() || '?'}
            </span>
          </div>
        </div>
      )}
      
      {/* Name badge */}
      <div className="absolute bottom-3 left-3 flex items-center gap-2">
        <Badge className="bg-black/60 text-white border-0">
          {participant?.user_name || 'Unknown'} {isLocal && '(You)'}
        </Badge>
        {!participant?.audio_enabled && (
          <Badge variant="destructive" className="px-1.5">
            <MicOff className="w-3 h-3" />
          </Badge>
        )}
        {participant?.hand_raised && (
          <Badge className="bg-yellow-500 text-black px-1.5">
            <Hand className="w-3 h-3" />
          </Badge>
        )}
      </div>
      
      {/* Host badge */}
      {participant?.is_host && (
        <Badge className="absolute top-3 left-3 bg-turquoise text-white border-0">
          Host
        </Badge>
      )}
      
      {/* Recording indicator */}
      {participant?.is_recording && (
        <Badge className="absolute top-3 right-3 bg-red-500 text-white border-0 animate-pulse">
          <Circle className="w-2 h-2 mr-1 fill-current" />
          REC
        </Badge>
      )}
    </div>
  );
};

// Recording Permission Dialog
const RecordingPermissionDialog = ({ isOpen, onAccept, onDecline, requesterName }) => {
  return (
    <Dialog open={isOpen} onOpenChange={() => {}}>
      <DialogContent className="bg-slate-800 border-slate-700">
        <DialogHeader>
          <DialogTitle className="text-white flex items-center gap-2">
            <Circle className="w-4 h-4 text-red-500 fill-red-500 animate-pulse" />
            Recording Permission Request
          </DialogTitle>
          <DialogDescription className="text-slate-300">
            <strong>{requesterName}</strong> wants to record this meeting. 
            The recording will capture video, audio, and screen shares.
          </DialogDescription>
        </DialogHeader>
        <div className="py-4">
          <div className="flex items-start gap-3 p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
            <AlertTriangle className="w-5 h-5 text-yellow-500 mt-0.5" />
            <div className="text-sm text-slate-300">
              <p className="font-medium text-yellow-500 mb-1">Privacy Notice</p>
              <p>By accepting, you consent to being recorded. You can leave the meeting if you don't wish to be recorded.</p>
            </div>
          </div>
        </div>
        <DialogFooter className="gap-2">
          <Button variant="outline" onClick={onDecline} className="text-slate-300 border-slate-600">
            <X className="w-4 h-4 mr-2" />
            Decline & Leave
          </Button>
          <Button onClick={onAccept} className="bg-turquoise hover:bg-turquoise/80">
            <Check className="w-4 h-4 mr-2" />
            Accept Recording
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

// Virtual Background Selector
const VirtualBackgroundSelector = ({ isOpen, onClose, currentBg, onSelect }) => {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-slate-800 border-slate-700 max-w-lg">
        <DialogHeader>
          <DialogTitle className="text-white flex items-center gap-2">
            <Image className="w-5 h-5 text-turquoise" />
            Virtual Background
          </DialogTitle>
        </DialogHeader>
        <div className="grid grid-cols-3 gap-3 py-4">
          {VIRTUAL_BACKGROUNDS.map((bg) => (
            <button
              key={bg.id}
              onClick={() => onSelect(bg.id)}
              className={`relative aspect-video rounded-lg overflow-hidden border-2 transition-all ${
                currentBg === bg.id 
                  ? 'border-turquoise ring-2 ring-turquoise/50' 
                  : 'border-slate-600 hover:border-slate-500'
              }`}
            >
              {bg.type === 'none' ? (
                <div className="w-full h-full bg-slate-700 flex items-center justify-center">
                  <X className="w-6 h-6 text-slate-400" />
                </div>
              ) : bg.type === 'blur' ? (
                <div className="w-full h-full bg-gradient-to-br from-slate-600 to-slate-800 flex items-center justify-center">
                  <Palette className="w-6 h-6 text-slate-300" />
                </div>
              ) : (
                <img src={bg.url} alt={bg.name} className="w-full h-full object-cover" />
              )}
              <span className="absolute bottom-1 left-1 text-xs text-white bg-black/60 px-1.5 py-0.5 rounded">
                {bg.name}
              </span>
            </button>
          ))}
        </div>
        <DialogFooter>
          <Button onClick={onClose} className="bg-turquoise hover:bg-turquoise/80">
            Apply
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

// Chat panel component
const ChatPanel = ({ messages, onSendMessage }) => {
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
            <div key={idx} className="text-sm">
              <span className="font-medium text-turquoise">{msg.user_name}: </span>
              <span className="text-slate-300">{msg.message}</span>
              <span className="text-xs text-slate-500 ml-2">
                {new Date(msg.timestamp).toLocaleTimeString()}
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
          />
          <Button onClick={handleSend} size="sm" className="bg-turquoise hover:bg-turquoise/80">
            Send
          </Button>
        </div>
      </div>
    </div>
  );
};

// AI Notes panel with transcription
const AINotesPanel = ({ notes, isTranscribing }) => {
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
        <Button variant="outline" size="sm" className="w-full text-slate-300 border-slate-600">
          <FileText className="w-4 h-4 mr-2" />
          Generate Summary
        </Button>
        <Button variant="outline" size="sm" className="w-full text-slate-300 border-slate-600">
          <Download className="w-4 h-4 mr-2" />
          Export Notes
        </Button>
      </div>
    </div>
  );
};

// Participants panel
const ParticipantsPanel = ({ participants, onMuteParticipant, isHost }) => {
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
            <div key={idx} className="flex items-center justify-between p-2 bg-slate-800 rounded-lg">
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
                {p.video_enabled ? (
                  <Video className="w-4 h-4 text-slate-400" />
                ) : (
                  <VideoOff className="w-4 h-4 text-red-400" />
                )}
                {p.audio_enabled ? (
                  <Mic className="w-4 h-4 text-slate-400" />
                ) : (
                  <MicOff className="w-4 h-4 text-red-400" />
                )}
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

// Settings panel
const SettingsPanel = ({ settings, onUpdateSettings }) => {
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
            />
          </div>
        </div>
      </ScrollArea>
    </div>
  );
};

// Main Meeting Room Component
const MeetingRoom = ({ user }) => {
  const { meetingId } = useParams();
  const navigate = useNavigate();
  
  // State
  const [meeting, setMeeting] = useState(null);
  const [participants, setParticipants] = useState([]);
  const [localStream, setLocalStream] = useState(null);
  const [remoteStreams, setRemoteStreams] = useState({});
  const [isConnecting, setIsConnecting] = useState(true);
  const [isVideoEnabled, setIsVideoEnabled] = useState(true);
  const [isAudioEnabled, setIsAudioEnabled] = useState(true);
  const [isScreenSharing, setIsScreenSharing] = useState(false);
  const [isHandRaised, setIsHandRaised] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [aiNotes, setAiNotes] = useState([]);
  const [activePanel, setActivePanel] = useState(null);
  const [virtualBackground, setVirtualBackground] = useState('none');
  const [showBgSelector, setShowBgSelector] = useState(false);
  const [showRecordingPermission, setShowRecordingPermission] = useState(false);
  const [recordingRequester, setRecordingRequester] = useState('');
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [meetingSettings, setMeetingSettings] = useState({
    ai_transcription: true,
    auto_summary: true,
    noise_cancellation: true,
    hd_video: false
  });
  
  // Refs
  const wsRef = useRef(null);
  const peerConnectionsRef = useRef({});
  const localStreamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const recordedChunksRef = useRef([]);
  
  // WebRTC configuration
  const rtcConfig = {
    iceServers: [
      { urls: 'stun:stun.l.google.com:19302' },
      { urls: 'stun:stun1.l.google.com:19302' },
    ]
  };

  // Initialize media and join meeting
  useEffect(() => {
    const initMeeting = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { width: 1280, height: 720 },
          audio: { echoCancellation: true, noiseSuppression: true }
        });
        setLocalStream(stream);
        localStreamRef.current = stream;
        
        const token = localStorage.getItem('token');
        const response = await fetch(`${API}/api/karau-meet/meetings/${meetingId}/join`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            video_enabled: true,
            audio_enabled: true
          })
        });
        
        if (!response.ok) throw new Error('Failed to join meeting');
        
        const data = await response.json();
        setMeeting(data.meeting);
        setParticipants(data.other_participants || []);
        
        connectWebSocket(token);
        setIsConnecting(false);
        toast.success('Joined meeting successfully!');
        
      } catch (error) {
        console.error('Error joining meeting:', error);
        toast.error('Failed to join meeting. Please check camera/microphone permissions.');
        setIsConnecting(false);
      }
    };
    
    initMeeting();
    
    return () => {
      if (localStreamRef.current) {
        localStreamRef.current.getTracks().forEach(track => track.stop());
      }
      if (wsRef.current) wsRef.current.close();
      Object.values(peerConnectionsRef.current).forEach(pc => pc.close());
      if (mediaRecorderRef.current && isRecording) {
        mediaRecorderRef.current.stop();
      }
    };
  }, [meetingId]);

  // WebSocket connection
  const connectWebSocket = (token) => {
    const wsUrl = `${API.replace('https://', 'wss://').replace('http://', 'ws://')}/api/karau-meet/ws/${meetingId}?token=${token}&user_name=${encodeURIComponent(user?.name || user?.email || 'User')}&is_host=true`;
    
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;
    
    ws.onopen = () => {
      console.log('WebSocket connected to meeting:', meetingId);
      setIsConnected(true);
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      toast.error('Connection error. Trying to reconnect...');
    };
    
    ws.onmessage = async (event) => {
      const message = JSON.parse(event.data);
      handleWebSocketMessage(message);
    };
  };

  const handleWebSocketMessage = async (message) => {
    switch (message.type) {
      // Room state when joining
      case 'room_state':
        setParticipants(message.participants || []);
        break;
        
      // User joined (from backend signaling)
      case 'user_joined':
        setParticipants(message.participants || []);
        if (message.user_id !== user?.user_id) {
          await createPeerConnection(message.user_id, true);
          toast.info(`${message.user_name} joined the meeting`);
        }
        break;
        
      // User left
      case 'user_left':
        setParticipants(message.participants || []);
        if (peerConnectionsRef.current[message.user_id]) {
          peerConnectionsRef.current[message.user_id].close();
          delete peerConnectionsRef.current[message.user_id];
        }
        setRemoteStreams(prev => {
          const updated = { ...prev };
          delete updated[message.user_id];
          return updated;
        });
        toast.info(`${message.user_name} left the meeting`);
        break;
        
      // Participant state changed (audio/video/screen)
      case 'participant_state_changed':
        setParticipants(prev => prev.map(p =>
          p.user_id === message.user_id ? { ...p, ...message.participant } : p
        ));
        break;
        
      // WebRTC signaling - offer
      case 'offer':
        await handleOffer(message);
        break;
        
      // WebRTC signaling - answer
      case 'answer':
        await handleAnswer(message);
        break;
        
      // WebRTC signaling - ICE candidate
      case 'ice_candidate':
        await handleIceCandidate(message);
        break;
        
      // Chat message
      case 'chat':
        setChatMessages(prev => [...prev, {
          sender: message.from_name,
          senderId: message.from_user,
          message: message.message,
          timestamp: message.timestamp
        }]);
        break;
        
      // Emoji reaction
      case 'reaction':
        toast(
          <div className="flex items-center gap-2">
            <span className="text-2xl">{message.emoji}</span>
            <span>{message.from_name}</span>
          </div>,
          { duration: 2000 }
        );
        break;
        
      // Host actions
      case 'host_action':
        if (message.action === 'mute_request') {
          toast.warning(`${message.from_host} asked you to mute`);
        } else if (message.action === 'removed') {
          toast.error(message.reason);
          navigate('/karau-meet/dashboard');
        }
        break;
        
      // Legacy support
      case 'participant_joined':
        setParticipants(prev => [...prev, {
          user_id: message.user_id,
          user_name: message.user_name,
          video_enabled: true,
          audio_enabled: true
        }]);
        await createPeerConnection(message.user_id, true);
        toast.info(`${message.user_name} joined the meeting`);
        break;
        
      case 'participant_left':
        setParticipants(prev => prev.filter(p => p.user_id !== message.user_id));
        if (peerConnectionsRef.current[message.user_id]) {
          peerConnectionsRef.current[message.user_id].close();
          delete peerConnectionsRef.current[message.user_id];
        }
        setRemoteStreams(prev => {
          const updated = { ...prev };
          delete updated[message.user_id];
          return updated;
        });
        break;
        
      case 'participant_updated':
        setParticipants(prev => prev.map(p =>
          p.user_id === message.user_id ? { ...p, ...message.updates } : p
        ));
        break;
        
      case 'chat_message':
        setChatMessages(prev => [...prev, message.message]);
        break;
        
      case 'ai_note':
        setAiNotes(prev => [...prev, message.note]);
        break;
        
      case 'webrtc_signal':
        await handleWebRTCSignal(message);
        break;
        
      case 'recording_request':
        setRecordingRequester(message.requester_name);
        setShowRecordingPermission(true);
        break;
        
      case 'recording_started':
        setIsRecording(true);
        toast.info('Recording has started');
        break;
        
      case 'recording_stopped':
        setIsRecording(false);
        toast.info('Recording has stopped');
        break;
        
      case 'meeting_ended':
        toast.info('Meeting has ended');
        navigate('/karau-meet');
        break;
        
      case 'pong':
        // Keep-alive response - ignore
        break;
        
      default:
        console.log('Unknown message type:', message.type);
    }
  };
  
  // Handle incoming WebRTC offer
  const handleOffer = async (message) => {
    const { from_user, from_name, offer } = message;
    let pc = peerConnectionsRef.current[from_user];
    
    if (!pc) {
      pc = await createPeerConnection(from_user, false);
    }
    
    await pc.setRemoteDescription(new RTCSessionDescription(offer));
    const answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);
    
    if (wsRef.current) {
      wsRef.current.send(JSON.stringify({
        type: 'answer',
        target: from_user,
        answer: answer
      }));
    }
  };
  
  // Handle incoming WebRTC answer
  const handleAnswer = async (message) => {
    const { from_user, answer } = message;
    const pc = peerConnectionsRef.current[from_user];
    
    if (pc) {
      await pc.setRemoteDescription(new RTCSessionDescription(answer));
    }
  };
  
  // Handle incoming ICE candidate
  const handleIceCandidate = async (message) => {
    const { from_user, candidate } = message;
    const pc = peerConnectionsRef.current[from_user];
    
    if (pc && candidate) {
      try {
        await pc.addIceCandidate(new RTCIceCandidate(candidate));
      } catch (e) {
        console.error('Error adding ICE candidate:', e);
      }
    }
  };

  const createPeerConnection = async (userId, initiator = false) => {
    const pc = new RTCPeerConnection(rtcConfig);
    peerConnectionsRef.current[userId] = pc;
    
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach(track => {
        pc.addTrack(track, localStreamRef.current);
      });
    }
    
    pc.ontrack = (event) => {
      setRemoteStreams(prev => ({ ...prev, [userId]: event.streams[0] }));
    };
    
    pc.onicecandidate = (event) => {
      if (event.candidate && wsRef.current) {
        wsRef.current.send(JSON.stringify({
          type: 'ice_candidate',
          target: userId,
          candidate: event.candidate
        }));
      }
    };
    
    if (initiator) {
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      
      if (wsRef.current) {
        wsRef.current.send(JSON.stringify({
          type: 'offer',
          target: userId,
          offer: offer
        }));
      }
    }
    
    return pc;
  };

  const handleWebRTCSignal = async (message) => {
    const { from_user_id, signal_type, signal_data } = message;
    let pc = peerConnectionsRef.current[from_user_id];
    
    if (!pc && signal_type === 'offer') {
      pc = await createPeerConnection(from_user_id, false);
    }
    
    if (!pc) return;
    
    switch (signal_type) {
      case 'offer':
        await pc.setRemoteDescription(new RTCSessionDescription(signal_data));
        const answer = await pc.createAnswer();
        await pc.setLocalDescription(answer);
        if (wsRef.current) {
          wsRef.current.send(JSON.stringify({
            type: 'webrtc_signal',
            target_user_id: from_user_id,
            signal_type: 'answer',
            signal_data: answer
          }));
        }
        break;
      case 'answer':
        await pc.setRemoteDescription(new RTCSessionDescription(signal_data));
        break;
      case 'ice-candidate':
        await pc.addIceCandidate(new RTCIceCandidate(signal_data));
        break;
    }
  };

  const toggleVideo = () => {
    if (localStreamRef.current) {
      const videoTrack = localStreamRef.current.getVideoTracks()[0];
      if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled;
        setIsVideoEnabled(videoTrack.enabled);
        if (wsRef.current) {
          wsRef.current.send(JSON.stringify({
            type: 'participant_update',
            updates: { video_enabled: videoTrack.enabled }
          }));
        }
      }
    }
  };

  const toggleAudio = () => {
    if (localStreamRef.current) {
      const audioTrack = localStreamRef.current.getAudioTracks()[0];
      if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled;
        setIsAudioEnabled(audioTrack.enabled);
        if (wsRef.current) {
          wsRef.current.send(JSON.stringify({
            type: 'participant_update',
            updates: { audio_enabled: audioTrack.enabled }
          }));
        }
      }
    }
  };

  const toggleScreenShare = async () => {
    try {
      if (isScreenSharing) {
        const newStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        const newVideoTrack = newStream.getVideoTracks()[0];
        
        Object.values(peerConnectionsRef.current).forEach(pc => {
          const sender = pc.getSenders().find(s => s.track?.kind === 'video');
          if (sender) sender.replaceTrack(newVideoTrack);
        });
        
        localStreamRef.current = newStream;
        setLocalStream(newStream);
        setIsScreenSharing(false);
      } else {
        const screenStream = await navigator.mediaDevices.getDisplayMedia({ video: true });
        const screenTrack = screenStream.getVideoTracks()[0];
        
        Object.values(peerConnectionsRef.current).forEach(pc => {
          const sender = pc.getSenders().find(s => s.track?.kind === 'video');
          if (sender) sender.replaceTrack(screenTrack);
        });
        
        screenTrack.onended = () => toggleScreenShare();
        setIsScreenSharing(true);
      }
      
      if (wsRef.current) {
        wsRef.current.send(JSON.stringify({
          type: 'participant_update',
          updates: { screen_sharing: !isScreenSharing }
        }));
      }
    } catch (error) {
      console.error('Screen share error:', error);
      toast.error('Failed to share screen');
    }
  };

  const toggleRecording = async () => {
    if (isRecording) {
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.stop();
      }
      setIsRecording(false);
      
      if (wsRef.current) {
        wsRef.current.send(JSON.stringify({ type: 'recording_stopped' }));
      }
      toast.success('Recording stopped');
    } else {
      // Request permission from all participants
      if (wsRef.current) {
        wsRef.current.send(JSON.stringify({
          type: 'recording_request',
          requester_name: user?.name || user?.email || 'Host'
        }));
      }
      
      // Start recording locally
      try {
        const stream = localStreamRef.current;
        if (stream) {
          const mediaRecorder = new MediaRecorder(stream, { mimeType: 'video/webm' });
          mediaRecorderRef.current = mediaRecorder;
          recordedChunksRef.current = [];
          
          mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
              recordedChunksRef.current.push(event.data);
            }
          };
          
          mediaRecorder.onstop = () => {
            const blob = new Blob(recordedChunksRef.current, { type: 'video/webm' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `karau-meeting-${meetingId}-${new Date().toISOString()}.webm`;
            a.click();
          };
          
          mediaRecorder.start(1000);
          setIsRecording(true);
          toast.success('Recording started');
        }
      } catch (error) {
        console.error('Recording error:', error);
        toast.error('Failed to start recording');
      }
    }
  };

  const handleRecordingPermissionResponse = (accepted) => {
    setShowRecordingPermission(false);
    if (!accepted) {
      toast.info('You declined the recording. Leaving meeting...');
      leaveMeeting();
    }
  };

  const toggleHandRaise = () => {
    setIsHandRaised(!isHandRaised);
    if (wsRef.current) {
      wsRef.current.send(JSON.stringify({
        type: isHandRaised ? 'lower_hand' : 'raise_hand'
      }));
    }
  };

  const sendChatMessage = (message) => {
    if (wsRef.current) {
      wsRef.current.send(JSON.stringify({
        type: 'chat_message',
        message: message,
        message_type: 'text'
      }));
    }
  };

  const leaveMeeting = async () => {
    try {
      const token = localStorage.getItem('token');
      await fetch(`${API}/api/karau-meet/meetings/${meetingId}/leave`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
    } catch (error) {
      console.error('Error leaving meeting:', error);
    }
    navigate('/karau-meet');
  };

  const copyMeetingLink = () => {
    const link = `${window.location.origin}/karau-meet/join/${meetingId}`;
    navigator.clipboard.writeText(link);
    toast.success('Meeting link copied!');
  };

  const addToCalendar = () => {
    const title = encodeURIComponent(meeting?.title || 'AI KARAU Meeting');
    const details = encodeURIComponent(`Join: ${window.location.origin}/karau-meet/join/${meetingId}`);
    const startDate = new Date().toISOString().replace(/-|:|\.\d\d\d/g, '');
    const endDate = new Date(Date.now() + 3600000).toISOString().replace(/-|:|\.\d\d\d/g, '');
    
    const googleCalUrl = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${title}&details=${details}&dates=${startDate}/${endDate}`;
    window.open(googleCalUrl, '_blank');
    toast.success('Opening Google Calendar...');
  };

  if (isConnecting) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-turquoise animate-spin mx-auto mb-4" />
          <h2 className="text-xl text-white font-medium">Joining meeting...</h2>
          <p className="text-slate-400 mt-2">Setting up your video and audio</p>
        </div>
      </div>
    );
  }

  const allParticipants = [
    { 
      ...user, 
      user_id: user?.user_id, 
      user_name: user?.name || user?.email, 
      video_enabled: isVideoEnabled, 
      audio_enabled: isAudioEnabled, 
      is_host: meeting?.host_id === user?.user_id,
      is_recording: isRecording 
    },
    ...participants
  ];

  return (
    <div className="h-screen bg-slate-900 flex flex-col">
      {/* Header */}
      <header className="h-16 bg-slate-800 border-b border-slate-700 flex items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-turquoise" />
            <span className="text-white font-semibold">AI KARAU Meeting</span>
          </div>
          <Badge variant="outline" className="text-slate-300 border-slate-600">
            {meeting?.title || 'Meeting'}
          </Badge>
          <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
            <Shield className="w-3 h-3 mr-1" />
            E2E Encrypted
          </Badge>
          {isRecording && (
            <Badge className="bg-red-500/20 text-red-400 border-red-500/30 animate-pulse">
              <Circle className="w-2 h-2 mr-1 fill-current" />
              Recording
            </Badge>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" onClick={addToCalendar} className="text-slate-300 hover:text-white">
            <Calendar className="w-4 h-4 mr-1" />
            Add to Calendar
          </Button>
          <Button variant="ghost" size="sm" onClick={copyMeetingLink} className="text-slate-300 hover:text-white">
            <Copy className="w-4 h-4 mr-1" />
            Copy Link
          </Button>
          <span className="text-slate-400 text-sm">ID: {meetingId}</span>
        </div>
      </header>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Video grid */}
        <div className={`flex-1 p-4 ${activePanel ? 'pr-0' : ''}`}>
          <div className={`h-full grid gap-3 ${
            allParticipants.length === 1 ? 'grid-cols-1' :
            allParticipants.length === 2 ? 'grid-cols-2' :
            allParticipants.length <= 4 ? 'grid-cols-2 grid-rows-2' :
            'grid-cols-3 grid-rows-2'
          }`}>
            {allParticipants.map((p, idx) => (
              <VideoParticipant
                key={p.user_id || idx}
                participant={p}
                isLocal={p.user_id === user?.user_id}
                stream={p.user_id === user?.user_id ? localStream : remoteStreams[p.user_id]}
                virtualBg={p.user_id === user?.user_id ? virtualBackground : null}
              />
            ))}
          </div>
        </div>

        {/* Side panel */}
        {activePanel && (
          <div className="w-80 bg-slate-800 border-l border-slate-700">
            {activePanel === 'chat' && (
              <ChatPanel messages={chatMessages} onSendMessage={sendChatMessage} />
            )}
            {activePanel === 'participants' && (
              <ParticipantsPanel 
                participants={allParticipants} 
                isHost={meeting?.host_id === user?.user_id}
                onMuteParticipant={() => {}}
              />
            )}
            {activePanel === 'ai-notes' && (
              <AINotesPanel notes={aiNotes} isTranscribing={isTranscribing} />
            )}
            {activePanel === 'settings' && (
              <SettingsPanel 
                settings={meetingSettings} 
                onUpdateSettings={(updates) => setMeetingSettings(prev => ({ ...prev, ...updates }))}
              />
            )}
          </div>
        )}
      </div>

      {/* Control bar */}
      <div className="h-20 bg-slate-800 border-t border-slate-700 flex items-center justify-center gap-2">
        {/* Audio */}
        <Button
          variant={isAudioEnabled ? 'secondary' : 'destructive'}
          size="lg"
          className="rounded-full w-12 h-12"
          onClick={toggleAudio}
          title={isAudioEnabled ? 'Mute' : 'Unmute'}
        >
          {isAudioEnabled ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5" />}
        </Button>

        {/* Video */}
        <Button
          variant={isVideoEnabled ? 'secondary' : 'destructive'}
          size="lg"
          className="rounded-full w-12 h-12"
          onClick={toggleVideo}
          title={isVideoEnabled ? 'Stop Video' : 'Start Video'}
        >
          {isVideoEnabled ? <Video className="w-5 h-5" /> : <VideoOff className="w-5 h-5" />}
        </Button>

        {/* Virtual Background */}
        <Button
          variant="secondary"
          size="lg"
          className="rounded-full w-12 h-12"
          onClick={() => setShowBgSelector(true)}
          title="Virtual Background"
        >
          <Image className="w-5 h-5" />
        </Button>

        {/* Screen share */}
        <Button
          variant={isScreenSharing ? 'default' : 'secondary'}
          size="lg"
          className={`rounded-full w-12 h-12 ${isScreenSharing ? 'bg-turquoise' : ''}`}
          onClick={toggleScreenShare}
          title={isScreenSharing ? 'Stop Sharing' : 'Share Screen'}
        >
          {isScreenSharing ? <MonitorOff className="w-5 h-5" /> : <Monitor className="w-5 h-5" />}
        </Button>

        {/* Record */}
        {meeting?.host_id === user?.user_id && (
          <Button
            variant={isRecording ? 'destructive' : 'secondary'}
            size="lg"
            className={`rounded-full w-12 h-12 ${isRecording ? 'animate-pulse' : ''}`}
            onClick={toggleRecording}
            title={isRecording ? 'Stop Recording' : 'Start Recording'}
          >
            {isRecording ? <Square className="w-5 h-5" /> : <Circle className="w-5 h-5" />}
          </Button>
        )}

        {/* Raise hand */}
        <Button
          variant={isHandRaised ? 'default' : 'secondary'}
          size="lg"
          className={`rounded-full w-12 h-12 ${isHandRaised ? 'bg-yellow-500' : ''}`}
          onClick={toggleHandRaise}
          title={isHandRaised ? 'Lower Hand' : 'Raise Hand'}
        >
          <Hand className="w-5 h-5" />
        </Button>

        <div className="w-px h-8 bg-slate-600 mx-1" />

        {/* Chat */}
        <Button
          variant={activePanel === 'chat' ? 'default' : 'secondary'}
          size="lg"
          className="rounded-full w-12 h-12"
          onClick={() => setActivePanel(activePanel === 'chat' ? null : 'chat')}
          title="Chat"
        >
          <MessageSquare className="w-5 h-5" />
        </Button>

        {/* Participants */}
        <Button
          variant={activePanel === 'participants' ? 'default' : 'secondary'}
          size="lg"
          className="rounded-full w-12 h-12"
          onClick={() => setActivePanel(activePanel === 'participants' ? null : 'participants')}
          title="Participants"
        >
          <Users className="w-5 h-5" />
        </Button>

        {/* AI Notes */}
        <Button
          variant={activePanel === 'ai-notes' ? 'default' : 'secondary'}
          size="lg"
          className={`rounded-full w-12 h-12 ${activePanel === 'ai-notes' ? 'bg-turquoise' : ''}`}
          onClick={() => setActivePanel(activePanel === 'ai-notes' ? null : 'ai-notes')}
          title="AI Notes"
        >
          <Sparkles className="w-5 h-5" />
        </Button>

        {/* Settings */}
        <Button
          variant={activePanel === 'settings' ? 'default' : 'secondary'}
          size="lg"
          className="rounded-full w-12 h-12"
          onClick={() => setActivePanel(activePanel === 'settings' ? null : 'settings')}
          title="Settings"
        >
          <Settings className="w-5 h-5" />
        </Button>

        <div className="w-px h-8 bg-slate-600 mx-1" />

        {/* Leave */}
        <Button
          variant="destructive"
          size="lg"
          className="rounded-full w-12 h-12"
          onClick={leaveMeeting}
          title="Leave Meeting"
        >
          <PhoneOff className="w-5 h-5" />
        </Button>
      </div>

      {/* Dialogs */}
      <RecordingPermissionDialog
        isOpen={showRecordingPermission}
        onAccept={() => handleRecordingPermissionResponse(true)}
        onDecline={() => handleRecordingPermissionResponse(false)}
        requesterName={recordingRequester}
      />
      
      <VirtualBackgroundSelector
        isOpen={showBgSelector}
        onClose={() => setShowBgSelector(false)}
        currentBg={virtualBackground}
        onSelect={setVirtualBackground}
      />
    </div>
  );
};

export default MeetingRoom;
