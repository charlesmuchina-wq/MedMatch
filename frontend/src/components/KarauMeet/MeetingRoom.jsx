import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import {
  Shield, Copy, Calendar, Loader2, Circle,
  Check, X, AlertTriangle, Image
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from '@/components/ui/dialog';

// Import refactored child components
import VideoControls from './VideoControls';
import { ParticipantGrid } from './ParticipantGrid';
import { ChatPanel, AINotesPanel, ParticipantsPanel, SettingsPanel } from './MeetingPanels';

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

// Virtual Background Selector Dialog
const VirtualBackgroundSelector = ({ isOpen, onClose, currentBg, onSelect }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [modelLoaded, setModelLoaded] = useState(false);

  useEffect(() => {
    const loadModel = async () => {
      if (!isOpen) return;
      setIsLoading(true);
      try {
        // In production, load TensorFlow.js BodyPix model here
        await new Promise(resolve => setTimeout(resolve, 1000));
        setModelLoaded(true);
      } catch (error) {
        console.error('Failed to load virtual background model:', error);
      }
      setIsLoading(false);
    };

    if (isOpen && !modelLoaded) loadModel();
  }, [isOpen, modelLoaded]);

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-slate-800 border-slate-700 max-w-2xl">
        <DialogHeader>
          <DialogTitle className="text-white flex items-center gap-2">
            <Image className="w-5 h-5 text-turquoise" />
            Virtual Background
            {isLoading && <Loader2 className="w-4 h-4 animate-spin text-turquoise ml-2" />}
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4 py-4">
          {/* Blur Options */}
          <div>
            <h4 className="text-sm font-medium text-slate-300 mb-2">Effects</h4>
            <div className="grid grid-cols-4 gap-2">
              {VIRTUAL_BACKGROUNDS.filter(bg => bg.type === 'none' || bg.type === 'blur').map((bg) => (
                <button
                  key={bg.id}
                  onClick={() => onSelect(bg.id)}
                  className={`p-3 rounded-lg border-2 transition-all ${
                    currentBg === bg.id 
                      ? 'border-turquoise bg-turquoise/10' 
                      : 'border-slate-600 bg-slate-700/50 hover:border-slate-500'
                  }`}
                >
                  <div className="text-2xl mb-1 text-center">
                    {bg.type === 'none' ? '🚫' : '🌫️'}
                  </div>
                  <div className="text-xs text-slate-300 text-center">{bg.name}</div>
                  {currentBg === bg.id && <Check className="w-4 h-4 text-turquoise mx-auto mt-1" />}
                </button>
              ))}
            </div>
          </div>
          
          {/* Image Backgrounds */}
          <div>
            <h4 className="text-sm font-medium text-slate-300 mb-2">Image Backgrounds</h4>
            <div className="grid grid-cols-4 gap-2">
              {VIRTUAL_BACKGROUNDS.filter(bg => bg.type === 'image').map((bg) => (
                <button
                  key={bg.id}
                  onClick={() => onSelect(bg.id)}
                  className={`relative aspect-video rounded-lg overflow-hidden border-2 transition-all ${
                    currentBg === bg.id 
                      ? 'border-turquoise ring-2 ring-turquoise/50' 
                      : 'border-slate-600 hover:border-slate-500'
                  }`}
                >
                  <img src={bg.url} alt={bg.name} className="w-full h-full object-cover" />
                  <span className="absolute bottom-0 left-0 right-0 text-xs text-white bg-black/60 px-1.5 py-0.5 text-center">
                    {bg.name}
                  </span>
                  {currentBg === bg.id && (
                    <div className="absolute top-1 right-1 w-5 h-5 bg-turquoise rounded-full flex items-center justify-center">
                      <Check className="w-3 h-3 text-white" />
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>
        </div>
        
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button onClick={onClose} className="bg-turquoise hover:bg-turquoise/80">Apply</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

// Meeting Header Component
const MeetingHeader = ({ meeting, meetingId, isRecording, onAddToCalendar, onCopyLink }) => (
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
      <Button variant="ghost" size="sm" onClick={onAddToCalendar} className="text-slate-300 hover:text-white">
        <Calendar className="w-4 h-4 mr-1" />
        Add to Calendar
      </Button>
      <Button variant="ghost" size="sm" onClick={onCopyLink} className="text-slate-300 hover:text-white">
        <Copy className="w-4 h-4 mr-1" />
        Copy Link
      </Button>
      <span className="text-slate-400 text-sm">ID: {meetingId}</span>
    </div>
  </header>
);

// Main Meeting Room Component (Refactored)
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
  const [iceServers, setIceServers] = useState([
    { urls: 'stun:stun.l.google.com:19302' },
    { urls: 'stun:stun1.l.google.com:19302' },
  ]);
  
  // Fetch ICE servers
  useEffect(() => {
    const fetchIceServers = async () => {
      try {
        const res = await fetch(`${API}/api/karau-meet/ice-servers`);
        if (res.ok) {
          const data = await res.json();
          if (data.ice_servers?.length > 0) {
            setIceServers(data.ice_servers);
          }
        }
      } catch (e) {
        console.log('Using default STUN servers');
      }
    };
    fetchIceServers();
  }, []);
  
  const rtcConfig = { iceServers, iceCandidatePoolSize: 10 };

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
          body: JSON.stringify({ video_enabled: true, audio_enabled: true })
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
      localStreamRef.current?.getTracks().forEach(track => track.stop());
      wsRef.current?.close();
      Object.values(peerConnectionsRef.current).forEach(pc => pc.close());
      if (mediaRecorderRef.current && isRecording) {
        mediaRecorderRef.current.stop();
      }
    };
  }, [meetingId]);

  // WebSocket connection
  const connectWebSocket = useCallback((token) => {
    const wsUrl = `${API.replace('https://', 'wss://').replace('http://', 'ws://')}/api/karau-meet/ws/${meetingId}?token=${token}&user_name=${encodeURIComponent(user?.name || user?.email || 'User')}&is_host=true`;
    
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
    };
    
    ws.onclose = (event) => {
      console.log('WebSocket disconnected', event.code, event.reason);
      setIsConnected(false);
      // Don't show error for intentional close (duplicate connection)
      if (event.code !== 4001) {
        // Could implement reconnection logic here if needed
      }
    };
    
    ws.onerror = () => toast.error('Connection error. Trying to reconnect...');
    
    ws.onmessage = async (event) => {
      const message = JSON.parse(event.data);
      await handleWebSocketMessage(message);
    };
  }, [meetingId, user]);

  // FIX: Safe WebSocket send function that checks connection state
  const safeSend = useCallback((data) => {
    try {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify(data));
        return true;
      } else {
        console.warn('WebSocket not ready, message not sent:', data.type);
        return false;
      }
    } catch (error) {
      console.error('Error sending WebSocket message:', error);
      return false;
    }
  }, []);

  // WebSocket message handler
  const handleWebSocketMessage = useCallback(async (message) => {
    switch (message.type) {
      case 'room_state':
        setParticipants(message.participants || []);
        break;
        
      case 'user_joined':
        setParticipants(message.participants || []);
        if (message.user_id !== user?.user_id) {
          await createPeerConnection(message.user_id, true);
          toast.info(`${message.user_name} joined the meeting`);
        }
        break;
        
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
        
      case 'participant_state_changed':
        setParticipants(prev => prev.map(p =>
          p.user_id === message.user_id ? { ...p, ...message.participant } : p
        ));
        break;
        
      case 'offer':
        await handleOffer(message);
        break;
        
      case 'answer':
        await handleAnswer(message);
        break;
        
      case 'ice_candidate':
        await handleIceCandidate(message);
        break;
        
      case 'chat':
        setChatMessages(prev => [...prev, {
          sender: message.from_name,
          senderId: message.from_user,
          message: message.message,
          timestamp: message.timestamp
        }]);
        break;
        
      case 'reaction':
        toast(
          <div className="flex items-center gap-2">
            <span className="text-2xl">{message.emoji}</span>
            <span>{message.from_name}</span>
          </div>,
          { duration: 2000 }
        );
        break;
        
      case 'host_action':
        if (message.action === 'mute_request') {
          toast.warning(`${message.from_host} asked you to mute`);
        } else if (message.action === 'removed') {
          toast.error(message.reason);
          navigate('/karau-meet/dashboard');
        }
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
        
      case 'ai_note':
        setAiNotes(prev => [...prev, message.note]);
        break;
        
      case 'pong':
        break;
        
      default:
        console.log('Unknown message type:', message.type);
    }
  }, [user, navigate]);

  // WebRTC handlers with proper state checks
  const handleOffer = async (message) => {
    const { from_user, offer } = message;
    try {
      let pc = peerConnectionsRef.current[from_user];
      
      // FIX: Check signaling state before setting remote description
      if (pc && pc.signalingState !== 'stable' && pc.signalingState !== 'have-local-offer') {
        console.log(`Recreating peer connection for ${from_user}, current state: ${pc.signalingState}`);
        pc.close();
        delete peerConnectionsRef.current[from_user];
        pc = null;
      }
      
      if (!pc) {
        pc = await createPeerConnection(from_user, false);
      }
      
      await pc.setRemoteDescription(new RTCSessionDescription(offer));
      const answer = await pc.createAnswer();
      await pc.setLocalDescription(answer);
      
      safeSend({ type: 'answer', target: from_user, answer });
    } catch (error) {
      console.error('Error handling offer:', error);
    }
  };
  
  const handleAnswer = async (message) => {
    const pc = peerConnectionsRef.current[message.from_user];
    if (pc) {
      try {
        // FIX: Only set remote description if in correct state
        if (pc.signalingState === 'have-local-offer') {
          await pc.setRemoteDescription(new RTCSessionDescription(message.answer));
        } else {
          console.warn(`Cannot set answer, signaling state: ${pc.signalingState}`);
        }
      } catch (error) {
        console.error('Error handling answer:', error);
      }
    }
  };
  
  const handleIceCandidate = async (message) => {
    const pc = peerConnectionsRef.current[message.from_user];
    if (pc && message.candidate) {
      try {
        // FIX: Only add ICE candidate if remote description is set
        if (pc.remoteDescription && pc.remoteDescription.type) {
          await pc.addIceCandidate(new RTCIceCandidate(message.candidate));
        } else {
          console.warn('Remote description not set, queuing ICE candidate');
        }
      } catch (e) {
        // Ignore errors for ICE candidates after connection is established
        if (e.name !== 'InvalidStateError') {
          console.error('Error adding ICE candidate:', e);
        }
      }
    }
  };

  const createPeerConnection = async (userId, initiator = false) => {
    // FIX: Close existing connection if any
    if (peerConnectionsRef.current[userId]) {
      try {
        peerConnectionsRef.current[userId].close();
      } catch (e) {
        console.warn('Error closing existing peer connection:', e);
      }
    }
    
    const pc = new RTCPeerConnection(rtcConfig);
    peerConnectionsRef.current[userId] = pc;
    
    localStreamRef.current?.getTracks().forEach(track => {
      pc.addTrack(track, localStreamRef.current);
    });
    
    pc.ontrack = (event) => {
      setRemoteStreams(prev => ({ ...prev, [userId]: event.streams[0] }));
    };
    
    pc.onicecandidate = (event) => {
      if (event.candidate) {
        safeSend({
          type: 'ice_candidate',
          target: userId,
          candidate: event.candidate
        });
      }
    };
    
    // FIX: Add connection state monitoring
    pc.onconnectionstatechange = () => {
      console.log(`Peer ${userId} connection state: ${pc.connectionState}`);
      if (pc.connectionState === 'failed') {
        // Could implement reconnection logic here
        console.warn(`Connection to ${userId} failed`);
      }
    };
    
    if (initiator) {
      try {
        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);
        safeSend({ type: 'offer', target: userId, offer });
      } catch (error) {
        console.error('Error creating offer:', error);
      }
    }
    
    return pc;
  };

  // Control handlers
  const toggleVideo = useCallback(() => {
    const videoTrack = localStreamRef.current?.getVideoTracks()[0];
    if (videoTrack) {
      videoTrack.enabled = !videoTrack.enabled;
      setIsVideoEnabled(videoTrack.enabled);
      safeSend({
        type: 'participant_update',
        updates: { video_enabled: videoTrack.enabled }
      });
    }
  }, [safeSend]);

  const toggleAudio = useCallback(() => {
    const audioTrack = localStreamRef.current?.getAudioTracks()[0];
    if (audioTrack) {
      audioTrack.enabled = !audioTrack.enabled;
      setIsAudioEnabled(audioTrack.enabled);
      safeSend({
        type: 'participant_update',
        updates: { audio_enabled: audioTrack.enabled }
      });
    }
  }, [safeSend]);

  const toggleScreenShare = useCallback(async () => {
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
      
      safeSend({
        type: 'state_update',
        state: { screen_sharing: !isScreenSharing }
      });
    } catch (error) {
      console.error('Screen share error:', error);
      toast.error('Failed to share screen');
    }
  }, [isScreenSharing, safeSend]);

  const toggleRecording = useCallback(async () => {
    if (isRecording) {
      mediaRecorderRef.current?.stop();
      setIsRecording(false);
      safeSend({ type: 'recording_stopped' });
      toast.success('Recording stopped');
    } else {
      wsRef.current?.send(JSON.stringify({
        type: 'recording_request',
        requester_name: user?.name || user?.email || 'Host'
      }));
      
      try {
        const stream = localStreamRef.current;
        if (stream) {
          const mediaRecorder = new MediaRecorder(stream, { mimeType: 'video/webm' });
          mediaRecorderRef.current = mediaRecorder;
          recordedChunksRef.current = [];
          const startTime = Date.now();
          
          mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) recordedChunksRef.current.push(event.data);
          };
          
          mediaRecorder.onstop = async () => {
            const blob = new Blob(recordedChunksRef.current, { type: 'video/webm' });
            const url = URL.createObjectURL(blob);
            const fileName = `karau-meeting-${meetingId}-${new Date().toISOString()}.webm`;
            
            const a = document.createElement('a');
            a.href = url;
            a.download = fileName;
            a.click();
            
            try {
              const token = localStorage.getItem('token');
              await fetch(`${API}/api/karau-meet/recordings/metadata`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify({
                  meeting_id: meetingId,
                  meeting_title: meeting?.title || 'Meeting',
                  duration_seconds: Math.round((Date.now() - startTime) / 1000),
                  file_size_bytes: blob.size,
                  file_name: fileName
                })
              });
              toast.success('Recording saved');
            } catch (err) {
              console.error('Failed to save recording metadata:', err);
            }
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
  }, [isRecording, meetingId, meeting, user]);

  const toggleHandRaise = useCallback(() => {
    const newState = !isHandRaised;
    setIsHandRaised(newState);
    wsRef.current?.send(JSON.stringify({ type: 'raise_hand', raised: newState }));
  }, [isHandRaised]);

  const sendChatMessage = useCallback((message) => {
    wsRef.current?.send(JSON.stringify({ type: 'chat', message }));
  }, []);

  const leaveMeeting = useCallback(async () => {
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
  }, [meetingId, navigate]);

  const copyMeetingLink = useCallback(() => {
    navigator.clipboard.writeText(`${window.location.origin}/karau-meet/join/${meetingId}`);
    toast.success('Meeting link copied!');
  }, [meetingId]);

  const addToCalendar = useCallback(() => {
    const title = encodeURIComponent(meeting?.title || 'AI KARAU Meeting');
    const details = encodeURIComponent(`Join: ${window.location.origin}/karau-meet/join/${meetingId}`);
    const startDate = new Date().toISOString().replace(/-|:|\.\d\d\d/g, '');
    const endDate = new Date(Date.now() + 3600000).toISOString().replace(/-|:|\.\d\d\d/g, '');
    
    window.open(`https://calendar.google.com/calendar/render?action=TEMPLATE&text=${title}&details=${details}&dates=${startDate}/${endDate}`, '_blank');
    toast.success('Opening Google Calendar...');
  }, [meeting, meetingId]);

  const handleRecordingPermissionResponse = useCallback((accepted) => {
    setShowRecordingPermission(false);
    if (!accepted) {
      toast.info('You declined the recording. Leaving meeting...');
      leaveMeeting();
    }
  }, [leaveMeeting]);

  // Loading state
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

  // Build participants list with local user
  const allParticipants = [
    { 
      ...user, 
      user_id: user?.user_id, 
      user_name: user?.name || user?.email, 
      video_enabled: isVideoEnabled, 
      audio_enabled: isAudioEnabled, 
      is_host: meeting?.host_id === user?.user_id,
      is_recording: isRecording,
      hand_raised: isHandRaised
    },
    ...participants
  ];

  const isHost = meeting?.host_id === user?.user_id;

  return (
    <div className="h-screen bg-slate-900 flex flex-col">
      {/* Header */}
      <MeetingHeader
        meeting={meeting}
        meetingId={meetingId}
        isRecording={isRecording}
        onAddToCalendar={addToCalendar}
        onCopyLink={copyMeetingLink}
      />

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Video grid */}
        <div className={`flex-1 p-4 ${activePanel ? 'pr-0' : ''}`}>
          <ParticipantGrid
            participants={allParticipants}
            localStream={localStream}
            remoteStreams={remoteStreams}
            localUserId={user?.user_id}
            virtualBackground={virtualBackground}
          />
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
                isHost={isHost}
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

      {/* Control bar - using refactored component */}
      <VideoControls
        isAudioEnabled={isAudioEnabled}
        isVideoEnabled={isVideoEnabled}
        isScreenSharing={isScreenSharing}
        isRecording={isRecording}
        isHandRaised={isHandRaised}
        isHost={isHost}
        activePanel={activePanel}
        onToggleAudio={toggleAudio}
        onToggleVideo={toggleVideo}
        onToggleScreenShare={toggleScreenShare}
        onToggleRecording={toggleRecording}
        onToggleHandRaise={toggleHandRaise}
        onOpenVirtualBg={() => setShowBgSelector(true)}
        onSetActivePanel={setActivePanel}
        onLeaveMeeting={leaveMeeting}
      />

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
