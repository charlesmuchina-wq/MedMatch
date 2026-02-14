import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import {
  Video, VideoOff, Mic, MicOff, Phone, PhoneOff,
  Monitor, MonitorOff, MessageSquare, Users, Settings,
  Hand, MoreVertical, Grid, Maximize, Minimize,
  Copy, Share2, Shield, Sparkles, FileText, Loader2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';

const API = process.env.REACT_APP_BACKEND_URL;

// Video participant component
const VideoParticipant = ({ participant, isLocal, stream, isSpeaking }) => {
  const videoRef = useRef(null);

  useEffect(() => {
    if (videoRef.current && stream) {
      videoRef.current.srcObject = stream;
    }
  }, [stream]);

  return (
    <div className={`relative rounded-xl overflow-hidden bg-slate-900 ${isSpeaking ? 'ring-2 ring-turquoise' : ''}`}>
      {participant?.video_enabled && stream ? (
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted={isLocal}
          className="w-full h-full object-cover"
        />
      ) : (
        <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-slate-800 to-slate-900">
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
    </div>
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

// AI Notes panel
const AINotesPanel = ({ notes }) => {
  return (
    <div className="flex flex-col h-full">
      <div className="p-3 border-b border-slate-700">
        <h3 className="font-semibold text-white flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-turquoise" />
          AI Notes
        </h3>
      </div>
      
      <ScrollArea className="flex-1 p-3">
        <div className="space-y-3">
          {notes.length === 0 ? (
            <p className="text-slate-400 text-sm">AI notes will appear here during the meeting...</p>
          ) : (
            notes.map((note, idx) => (
              <div key={idx} className="p-2 bg-slate-800 rounded-lg text-sm">
                <Badge className="mb-1 text-xs" variant="outline">
                  {note.type}
                </Badge>
                <p className="text-slate-300">{note.content}</p>
              </div>
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
};

// Participants panel
const ParticipantsPanel = ({ participants }) => {
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
                <span className="text-sm text-white">{p.user_name}</span>
                {p.is_host && <Badge className="text-xs">Host</Badge>}
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
              </div>
            </div>
          ))}
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
  const [chatMessages, setChatMessages] = useState([]);
  const [aiNotes, setAiNotes] = useState([]);
  const [activePanel, setActivePanel] = useState(null); // 'chat', 'participants', 'ai-notes'
  const [isFullscreen, setIsFullscreen] = useState(false);
  
  // Refs
  const wsRef = useRef(null);
  const peerConnectionsRef = useRef({});
  const localStreamRef = useRef(null);
  
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
        // Get user media
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true
        });
        setLocalStream(stream);
        localStreamRef.current = stream;
        
        // Join meeting via API
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
        
        if (!response.ok) {
          throw new Error('Failed to join meeting');
        }
        
        const data = await response.json();
        setMeeting(data.meeting);
        setParticipants(data.other_participants || []);
        
        // Connect WebSocket
        connectWebSocket(token);
        
        setIsConnecting(false);
        toast.success('Joined meeting successfully!');
        
      } catch (error) {
        console.error('Error joining meeting:', error);
        toast.error('Failed to join meeting');
        setIsConnecting(false);
      }
    };
    
    initMeeting();
    
    return () => {
      // Cleanup
      if (localStreamRef.current) {
        localStreamRef.current.getTracks().forEach(track => track.stop());
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
      Object.values(peerConnectionsRef.current).forEach(pc => pc.close());
    };
  }, [meetingId]);

  // WebSocket connection
  const connectWebSocket = (token) => {
    const wsUrl = `${API.replace('https://', 'wss://').replace('http://', 'ws://')}/api/karau-meet/ws/${meetingId}?token=${token}&user_id=${user?.user_id}&user_name=${encodeURIComponent(user?.name || user?.email || 'User')}`;
    
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;
    
    ws.onopen = () => {
      console.log('WebSocket connected');
    };
    
    ws.onmessage = async (event) => {
      const message = JSON.parse(event.data);
      handleWebSocketMessage(message);
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  };

  // Handle WebSocket messages
  const handleWebSocketMessage = async (message) => {
    switch (message.type) {
      case 'participant_joined':
        setParticipants(prev => [...prev, {
          user_id: message.user_id,
          user_name: message.user_name,
          video_enabled: true,
          audio_enabled: true
        }]);
        // Create peer connection for new participant
        await createPeerConnection(message.user_id, true);
        toast.info(`${message.user_name} joined the meeting`);
        break;
        
      case 'participant_left':
        setParticipants(prev => prev.filter(p => p.user_id !== message.user_id));
        // Close peer connection
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
        
      case 'hand_raised':
        toast.info(`${message.user_name} raised their hand`);
        break;
        
      case 'meeting_ended':
        toast.info('Meeting has ended');
        navigate('/karau-meet');
        break;
    }
  };

  // Create peer connection
  const createPeerConnection = async (userId, initiator = false) => {
    const pc = new RTCPeerConnection(rtcConfig);
    peerConnectionsRef.current[userId] = pc;
    
    // Add local tracks
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach(track => {
        pc.addTrack(track, localStreamRef.current);
      });
    }
    
    // Handle incoming tracks
    pc.ontrack = (event) => {
      setRemoteStreams(prev => ({
        ...prev,
        [userId]: event.streams[0]
      }));
    };
    
    // Handle ICE candidates
    pc.onicecandidate = (event) => {
      if (event.candidate && wsRef.current) {
        wsRef.current.send(JSON.stringify({
          type: 'webrtc_signal',
          target_user_id: userId,
          signal_type: 'ice-candidate',
          signal_data: event.candidate
        }));
      }
    };
    
    // Create and send offer if initiator
    if (initiator) {
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      
      if (wsRef.current) {
        wsRef.current.send(JSON.stringify({
          type: 'webrtc_signal',
          target_user_id: userId,
          signal_type: 'offer',
          signal_data: offer
        }));
      }
    }
    
    return pc;
  };

  // Handle WebRTC signaling
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

  // Toggle video
  const toggleVideo = () => {
    if (localStreamRef.current) {
      const videoTrack = localStreamRef.current.getVideoTracks()[0];
      if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled;
        setIsVideoEnabled(videoTrack.enabled);
        
        // Notify others
        if (wsRef.current) {
          wsRef.current.send(JSON.stringify({
            type: 'participant_update',
            updates: { video_enabled: videoTrack.enabled }
          }));
        }
      }
    }
  };

  // Toggle audio
  const toggleAudio = () => {
    if (localStreamRef.current) {
      const audioTrack = localStreamRef.current.getAudioTracks()[0];
      if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled;
        setIsAudioEnabled(audioTrack.enabled);
        
        // Notify others
        if (wsRef.current) {
          wsRef.current.send(JSON.stringify({
            type: 'participant_update',
            updates: { audio_enabled: audioTrack.enabled }
          }));
        }
      }
    }
  };

  // Toggle screen share
  const toggleScreenShare = async () => {
    try {
      if (isScreenSharing) {
        // Stop screen sharing
        const videoTrack = localStreamRef.current?.getVideoTracks()[0];
        if (videoTrack) {
          videoTrack.stop();
        }
        
        // Get new camera stream
        const newStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        const newVideoTrack = newStream.getVideoTracks()[0];
        
        // Replace track in all peer connections
        Object.values(peerConnectionsRef.current).forEach(pc => {
          const sender = pc.getSenders().find(s => s.track?.kind === 'video');
          if (sender) {
            sender.replaceTrack(newVideoTrack);
          }
        });
        
        localStreamRef.current = newStream;
        setLocalStream(newStream);
        setIsScreenSharing(false);
      } else {
        // Start screen sharing
        const screenStream = await navigator.mediaDevices.getDisplayMedia({ video: true });
        const screenTrack = screenStream.getVideoTracks()[0];
        
        // Replace track in all peer connections
        Object.values(peerConnectionsRef.current).forEach(pc => {
          const sender = pc.getSenders().find(s => s.track?.kind === 'video');
          if (sender) {
            sender.replaceTrack(screenTrack);
          }
        });
        
        screenTrack.onended = () => {
          toggleScreenShare();
        };
        
        setIsScreenSharing(true);
      }
      
      // Notify others
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

  // Toggle hand raise
  const toggleHandRaise = () => {
    const newState = !isHandRaised;
    setIsHandRaised(newState);
    
    if (wsRef.current) {
      wsRef.current.send(JSON.stringify({
        type: newState ? 'raise_hand' : 'lower_hand'
      }));
    }
  };

  // Send chat message
  const sendChatMessage = (message) => {
    if (wsRef.current) {
      wsRef.current.send(JSON.stringify({
        type: 'chat_message',
        message: message,
        message_type: 'text'
      }));
    }
  };

  // Leave meeting
  const leaveMeeting = async () => {
    try {
      const token = localStorage.getItem('token');
      await fetch(`${API}/api/karau-meet/meetings/${meetingId}/leave`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
    } catch (error) {
      console.error('Error leaving meeting:', error);
    }
    
    navigate('/karau-meet');
  };

  // Copy meeting link
  const copyMeetingLink = () => {
    const link = `${window.location.origin}/karau-meet/join/${meetingId}`;
    navigator.clipboard.writeText(link);
    toast.success('Meeting link copied!');
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
    { ...user, user_id: user?.user_id, user_name: user?.name || user?.email, video_enabled: isVideoEnabled, audio_enabled: isAudioEnabled, is_host: meeting?.host_id === user?.user_id },
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
            Encrypted
          </Badge>
        </div>
        
        <div className="flex items-center gap-2">
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
              <ParticipantsPanel participants={allParticipants} />
            )}
            {activePanel === 'ai-notes' && (
              <AINotesPanel notes={aiNotes} />
            )}
          </div>
        )}
      </div>

      {/* Control bar */}
      <div className="h-20 bg-slate-800 border-t border-slate-700 flex items-center justify-center gap-3">
        {/* Audio */}
        <Button
          variant={isAudioEnabled ? 'secondary' : 'destructive'}
          size="lg"
          className="rounded-full w-14 h-14"
          onClick={toggleAudio}
        >
          {isAudioEnabled ? <Mic className="w-6 h-6" /> : <MicOff className="w-6 h-6" />}
        </Button>

        {/* Video */}
        <Button
          variant={isVideoEnabled ? 'secondary' : 'destructive'}
          size="lg"
          className="rounded-full w-14 h-14"
          onClick={toggleVideo}
        >
          {isVideoEnabled ? <Video className="w-6 h-6" /> : <VideoOff className="w-6 h-6" />}
        </Button>

        {/* Screen share */}
        <Button
          variant={isScreenSharing ? 'default' : 'secondary'}
          size="lg"
          className={`rounded-full w-14 h-14 ${isScreenSharing ? 'bg-turquoise' : ''}`}
          onClick={toggleScreenShare}
        >
          {isScreenSharing ? <MonitorOff className="w-6 h-6" /> : <Monitor className="w-6 h-6" />}
        </Button>

        {/* Raise hand */}
        <Button
          variant={isHandRaised ? 'default' : 'secondary'}
          size="lg"
          className={`rounded-full w-14 h-14 ${isHandRaised ? 'bg-yellow-500' : ''}`}
          onClick={toggleHandRaise}
        >
          <Hand className="w-6 h-6" />
        </Button>

        <div className="w-px h-10 bg-slate-600 mx-2" />

        {/* Chat */}
        <Button
          variant={activePanel === 'chat' ? 'default' : 'secondary'}
          size="lg"
          className="rounded-full w-14 h-14"
          onClick={() => setActivePanel(activePanel === 'chat' ? null : 'chat')}
        >
          <MessageSquare className="w-6 h-6" />
        </Button>

        {/* Participants */}
        <Button
          variant={activePanel === 'participants' ? 'default' : 'secondary'}
          size="lg"
          className="rounded-full w-14 h-14"
          onClick={() => setActivePanel(activePanel === 'participants' ? null : 'participants')}
        >
          <Users className="w-6 h-6" />
        </Button>

        {/* AI Notes */}
        <Button
          variant={activePanel === 'ai-notes' ? 'default' : 'secondary'}
          size="lg"
          className={`rounded-full w-14 h-14 ${activePanel === 'ai-notes' ? 'bg-turquoise' : ''}`}
          onClick={() => setActivePanel(activePanel === 'ai-notes' ? null : 'ai-notes')}
        >
          <Sparkles className="w-6 h-6" />
        </Button>

        <div className="w-px h-10 bg-slate-600 mx-2" />

        {/* Leave */}
        <Button
          variant="destructive"
          size="lg"
          className="rounded-full w-14 h-14"
          onClick={leaveMeeting}
        >
          <PhoneOff className="w-6 h-6" />
        </Button>
      </div>
    </div>
  );
};

export default MeetingRoom;
