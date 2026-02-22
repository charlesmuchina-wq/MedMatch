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
const MeetingRoom = ({ user, meetingIdProp }) => {
  const params = useParams();
  // Use prop if provided, otherwise try params (for backward compatibility)
  const meetingId = meetingIdProp || params.meetingId;
  const navigate = useNavigate();
  
  // State - Decoupled media and API states
  const [meeting, setMeeting] = useState(null);
  const [participants, setParticipants] = useState([]);
  const [localStream, setLocalStream] = useState(null);
  const [remoteStreams, setRemoteStreams] = useState({});
  const [isMediaReady, setIsMediaReady] = useState(false);  // Media stream ready
  const [isApiConnected, setIsApiConnected] = useState(false);  // API/WebSocket connected
  const [isConnecting, setIsConnecting] = useState(true);  // Overall loading state
  const [connectionError, setConnectionError] = useState(null);  // Specific error message
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
  
  // Refs - MediaStream as single source of truth
  const wsRef = useRef(null);
  const peerConnectionsRef = useRef({});
  const localStreamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const recordedChunksRef = useRef([]);
  const mountedRef = useRef(true);
  const apiRetryCountRef = useRef(0);
  const maxApiRetries = 3;
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

  // Helper: Get specific error message for getUserMedia errors
  const getMediaErrorMessage = (error) => {
    const errorName = error.name || 'UnknownError';
    console.error(`Media error [${errorName}]:`, error.message);
    
    switch (errorName) {
      case 'NotAllowedError':
      case 'PermissionDeniedError':
        return {
          title: 'Camera/Microphone Access Denied',
          message: 'Please allow camera and microphone permissions in your browser settings and refresh the page.',
          canRetry: false
        };
      case 'NotFoundError':
      case 'DevicesNotFoundError':
        return {
          title: 'No Camera or Microphone Found',
          message: 'No camera or microphone was detected. Please connect a device and try again.',
          canRetry: true
        };
      case 'NotReadableError':
      case 'TrackStartError':
        return {
          title: 'Camera/Microphone In Use',
          message: 'Your camera or microphone is being used by another application. Please close other apps and try again.',
          canRetry: true
        };
      case 'OverconstrainedError':
        return {
          title: 'Camera Settings Not Supported',
          message: 'Your camera does not support the requested settings. Trying with default settings...',
          canRetry: true
        };
      case 'AbortError':
        return {
          title: 'Connection Aborted',
          message: 'The media connection was interrupted. Please try again.',
          canRetry: true
        };
      case 'SecurityError':
        return {
          title: 'Security Error',
          message: 'Media access is blocked due to security settings. Please use HTTPS.',
          canRetry: false
        };
      default:
        return {
          title: 'Media Error',
          message: `Unable to access camera/microphone: ${error.message}`,
          canRetry: true
        };
    }
  };

  // Pre-flight check: Verify device availability before joining
  const checkDeviceAvailability = async () => {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const hasVideo = devices.some(d => d.kind === 'videoinput');
      const hasAudio = devices.some(d => d.kind === 'audioinput');
      return { hasVideo, hasAudio, devices };
    } catch (error) {
      console.error('Device enumeration failed:', error);
      return { hasVideo: false, hasAudio: false, devices: [] };
    }
  };

  // Initialize media stream (decoupled from API)
  const initializeMedia = async () => {
    // Pre-flight device check
    const { hasVideo, hasAudio } = await checkDeviceAvailability();
    
    if (!hasVideo && !hasAudio) {
      console.warn('No media devices found during pre-flight check');
    }
    
    // Request both camera and microphone simultaneously
    const constraints = {
      video: hasVideo ? { 
        width: { ideal: 1280, max: 1920 }, 
        height: { ideal: 720, max: 1080 },
        facingMode: 'user'
      } : false,
      audio: hasAudio ? { 
        echoCancellation: true, 
        noiseSuppression: true,
        autoGainControl: true
      } : false
    };
    
    // If no devices at all, try anyway (browser might prompt for permission)
    if (!hasVideo && !hasAudio) {
      constraints.video = { facingMode: 'user' };
      constraints.audio = true;
    }
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      return { success: true, stream };
    } catch (error) {
      // If high-quality constraints fail, try basic constraints
      if (error.name === 'OverconstrainedError') {
        try {
          const basicStream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: true
          });
          return { success: true, stream: basicStream };
        } catch (fallbackError) {
          return { success: false, error: fallbackError };
        }
      }
      return { success: false, error };
    }
  };

  // Join meeting API with retry logic
  const joinMeetingApi = async (retryCount = 0) => {
    const token = localStorage.getItem('token');
    const isGuest = user?.is_guest || !token;
    
    try {
      let response;
      let joinData;
      
      if (isGuest) {
        response = await fetch(`${API}/api/karau-meet/meetings/${meetingId}/join-guest`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            guest_name: user?.name || 'Guest',
            video_enabled: true, 
            audio_enabled: true 
          })
        });
      } else {
        response = await fetch(`${API}/api/karau-meet/meetings/${meetingId}/join`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ video_enabled: true, audio_enabled: true })
        });
      }
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API ${response.status}: ${errorText}`);
      }
      
      joinData = await response.json();
      
      if (isGuest) {
        user.user_id = joinData.guest_user_id;
        user.name = joinData.guest_name;
      }
      
      return { success: true, data: joinData, isGuest };
      
    } catch (error) {
      console.error(`API join attempt ${retryCount + 1} failed:`, error);
      
      // Retry logic - don't tear down media stream
      if (retryCount < maxApiRetries && !error.message.includes('404')) {
        const delay = Math.min(1000 * Math.pow(2, retryCount), 5000);
        await new Promise(resolve => setTimeout(resolve, delay));
        return joinMeetingApi(retryCount + 1);
      }
      
      return { success: false, error };
    }
  };

  // Initialize media and join meeting
  useEffect(() => {
    let mounted = true;
    
    const initMeeting = async () => {
      // Step 1: Get camera/microphone access
      let stream;
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { width: 1280, height: 720, facingMode: 'user' },
          audio: { echoCancellation: true, noiseSuppression: true }
        });
        
        if (!mounted) {
          stream.getTracks().forEach(track => track.stop());
          return;
        }
        
        setLocalStream(stream);
        localStreamRef.current = stream;
        console.log('Camera/microphone initialized successfully');
        
      } catch (mediaError) {
        console.error('Media access error:', mediaError);
        if (mediaError.name === 'NotAllowedError') {
          toast.error('Camera/microphone access denied. Please allow permissions and refresh.');
        } else if (mediaError.name === 'NotFoundError') {
          toast.error('No camera or microphone found on this device.');
        } else {
          toast.error(`Media error: ${mediaError.message}`);
        }
        setIsConnecting(false);
        return;
      }
      
      // Step 2: Join the meeting via API
      const token = localStorage.getItem('token');
      const isGuest = user?.is_guest || !token;
      
      try {
        let response;
        let joinData;
        
        if (isGuest) {
          // Guest join - no authentication required
          response = await fetch(`${API}/api/karau-meet/meetings/${meetingId}/join-guest`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
              guest_name: user?.name || 'Guest',
              video_enabled: true, 
              audio_enabled: true 
            })
          });
          
          if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Meeting join failed: ${errorText}`);
          }
          
          joinData = await response.json();
          // Update user with guest ID from server
          user.user_id = joinData.guest_user_id;
          user.name = joinData.guest_name;
        } else {
          // Authenticated join
          response = await fetch(`${API}/api/karau-meet/meetings/${meetingId}/join`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ video_enabled: true, audio_enabled: true })
          });
          
          if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Meeting join failed: ${errorText}`);
          }
          joinData = await response.json();
        }
        
        if (!mounted) return;
        
        setMeeting(joinData.meeting);
        setParticipants(joinData.other_participants || []);
        
        // Step 3: Connect WebSocket - for guests, use guest ID instead of token
        connectWebSocket(isGuest ? null : token, false, isGuest ? user.user_id : null);
        setIsConnecting(false);
        toast.success('Joined meeting successfully!');
        
      } catch (joinError) {
        console.error('Meeting join error:', joinError);
        // Still show the video feed, just show an error about the meeting
        setIsConnecting(false);
        if (joinError.message.includes('404') || joinError.message.includes('not found')) {
          toast.error('Meeting not found. Please check the meeting ID.');
        } else {
          toast.error(`Failed to connect: ${joinError.message}`);
        }
      }
    };
    
    initMeeting();
    
    return () => {
      mounted = false;
      localStreamRef.current?.getTracks().forEach(track => track.stop());
      wsRef.current?.close();
      Object.values(peerConnectionsRef.current).forEach(pc => pc.close());
      if (mediaRecorderRef.current && isRecording) {
        mediaRecorderRef.current.stop();
      }
    };
  }, [meetingId]);

  // Reconnection state
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 10;
  const messageQueueRef = useRef([]);
  const sessionTokenRef = useRef(null);
  const processedEventsRef = useRef(new Set());
  const iceCandidateQueueRef = useRef({}); // Queue ICE candidates per peer
  const isReconnectingRef = useRef(false);
  const guestUserIdRef = useRef(null); // Store guest user ID for reconnection
  
  // Calculate exponential backoff with jitter
  const getReconnectDelay = useCallback(() => {
    const baseDelay = 1000; // 1 second
    const maxDelay = 30000; // 30 seconds max
    const exponentialDelay = Math.min(baseDelay * Math.pow(2, reconnectAttemptsRef.current), maxDelay);
    // Add 10-20% jitter
    const jitter = exponentialDelay * (0.1 + Math.random() * 0.1);
    return exponentialDelay + jitter;
  }, []);
  
  // WebSocket connection with reconnection support
  const connectWebSocket = useCallback((token, isReconnect = false, guestUserId = null) => {
    // Prevent multiple simultaneous reconnection attempts
    if (isReconnectingRef.current && isReconnect) {
      console.log('Reconnection already in progress, skipping');
      return;
    }
    
    if (isReconnect) {
      isReconnectingRef.current = true;
    }
    
    // Store guest user ID for reconnection
    if (guestUserId) {
      guestUserIdRef.current = guestUserId;
    }
    
    const isGuest = !token && (guestUserId || guestUserIdRef.current);
    const effectiveUserId = guestUserId || guestUserIdRef.current || user?.user_id;
    
    // Build WebSocket URL - guests use user_id param instead of token
    let wsUrl = `${API.replace('https://', 'wss://').replace('http://', 'ws://')}/api/karau-meet/ws/${meetingId}?user_name=${encodeURIComponent(user?.name || user?.email || 'Guest')}&is_host=${!isGuest}`;
    
    if (isGuest && effectiveUserId) {
      wsUrl += `&user_id=${effectiveUserId}`;
    } else if (token) {
      wsUrl += `&token=${token}`;
    }
    
    // Add session token for reconnection
    if (isReconnect && sessionTokenRef.current) {
      wsUrl += `&session_token=${sessionTokenRef.current}`;
    }
    
    // Close existing connection if any
    if (wsRef.current) {
      try {
        if (wsRef.current.readyState === WebSocket.OPEN || 
            wsRef.current.readyState === WebSocket.CONNECTING) {
          wsRef.current.close(1000, 'Reconnecting');
        }
      } catch (e) {
        console.warn('Error closing existing WebSocket:', e);
      }
    }
    
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
      reconnectAttemptsRef.current = 0;
      isReconnectingRef.current = false;
      
      // Flush message queue safely
      const queue = [...messageQueueRef.current];
      messageQueueRef.current = [];
      
      queue.forEach(queuedMessage => {
        try {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(queuedMessage));
          }
        } catch (e) {
          console.error('Failed to send queued message:', e);
          // Re-queue for next attempt
          messageQueueRef.current.push(queuedMessage);
        }
      });
    };
    
    ws.onclose = (event) => {
      console.log('WebSocket disconnected', event.code, event.reason);
      setIsConnected(false);
      isReconnectingRef.current = false;
      
      // Handle different close codes
      if (event.code === 4001) {
        // Duplicate connection - don't reconnect automatically
        console.log('Connection replaced by another session');
      } else if (event.code === 4002) {
        // Zombie detected - try to reconnect
        console.log('Connection timed out, attempting reconnect...');
        attemptReconnect(token);
      } else if (event.code !== 1000) {
        // Abnormal closure - attempt reconnect with backoff
        attemptReconnect(token);
      }
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      isReconnectingRef.current = false;
      // Don't show toast for every error - let onclose handle it
    };
    
    ws.onmessage = async (event) => {
      try {
        const message = JSON.parse(event.data);
        await handleWebSocketMessage(message);
      } catch (e) {
        console.error('Error processing WebSocket message:', e);
      }
    };
  }, [meetingId, user]);
  
  // Reconnection with exponential backoff
  const attemptReconnect = useCallback((token) => {
    if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
      toast.error('Unable to reconnect. Please refresh the page.');
      isReconnectingRef.current = false;
      return;
    }
    
    if (isReconnectingRef.current) {
      console.log('Reconnection already scheduled');
      return;
    }
    
    const delay = getReconnectDelay();
    reconnectAttemptsRef.current += 1;
    
    console.log(`Reconnecting in ${Math.round(delay / 1000)}s (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`);
    
    setTimeout(() => {
      if (!isConnected && !isReconnectingRef.current) {
        connectWebSocket(token, true);
      }
    }, delay);
  }, [getReconnectDelay, connectWebSocket, isConnected]);
  
  // App lifecycle awareness - handle visibility changes
  useEffect(() => {
    const handleVisibilityChange = () => {
      const token = localStorage.getItem('token');
      if (document.visibilityState === 'hidden') {
        // App going to background - save state
        console.log('App going to background');
      } else if (document.visibilityState === 'visible') {
        // App returning to foreground - check connection
        console.log('App returning to foreground');
        if (wsRef.current?.readyState !== WebSocket.OPEN && !isReconnectingRef.current) {
          console.log('Reconnecting after returning to foreground');
          reconnectAttemptsRef.current = 0; // Reset on visibility change
          connectWebSocket(token, true);
        }
      }
    };
    
    // Network status monitoring
    const handleOnline = () => {
      console.log('Network restored');
      const token = localStorage.getItem('token');
      if (wsRef.current?.readyState !== WebSocket.OPEN && !isReconnectingRef.current) {
        toast.info('Network restored. Reconnecting...');
        reconnectAttemptsRef.current = 0; // Reset backoff on network restore
        connectWebSocket(token, true);
      }
    };
    
    const handleOffline = () => {
      console.log('Network lost');
      toast.warning('Network connection lost');
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [connectWebSocket]);

  // Safe WebSocket send function with message queuing - NEVER throws
  const safeSend = useCallback((data) => {
    // Double-check WebSocket state before sending
    const ws = wsRef.current;
    
    if (!ws) {
      console.warn('WebSocket not initialized, queuing message:', data.type);
      messageQueueRef.current.push(data);
      return false;
    }
    
    // Check readyState synchronously right before send
    if (ws.readyState !== WebSocket.OPEN) {
      console.warn(`WebSocket state ${ws.readyState}, queuing message:`, data.type);
      messageQueueRef.current.push(data);
      return false;
    }
    
    try {
      ws.send(JSON.stringify(data));
      return true;
    } catch (error) {
      // Catch any synchronous errors (InvalidStateError, etc.)
      console.error('Error sending WebSocket message:', error.name, error.message);
      messageQueueRef.current.push(data);
      return false;
    }
  }, []);

  // WebSocket message handler with idempotency
  const handleWebSocketMessage = useCallback(async (message) => {
    // Check for idempotency - skip already processed events
    if (message.event_id) {
      if (processedEventsRef.current.has(message.event_id)) {
        console.log('Skipping duplicate event:', message.event_id);
        return;
      }
      processedEventsRef.current.add(message.event_id);
      // Clean up old event IDs (keep last 1000)
      if (processedEventsRef.current.size > 1000) {
        const events = Array.from(processedEventsRef.current);
        processedEventsRef.current = new Set(events.slice(-500));
      }
    }
    
    switch (message.type) {
      case 'room_state':
        setParticipants(message.participants || []);
        // Store session token for reconnection
        if (message.session_token) {
          sessionTokenRef.current = message.session_token;
        }
        if (message.is_reconnection) {
          toast.success('Reconnected to meeting');
        }
        break;
      
      case 'ping':
        // Respond to server heartbeat
        safeSend({ type: 'pong', timestamp: message.timestamp });
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
        // FIX: Update participant list from server (handles reconnections)
        if (message.participants) {
          setParticipants(message.participants);
        } else {
          setParticipants(prev => prev.map(p =>
            p.user_id === message.user_id ? { ...p, ...message.participant } : p
          ));
        }
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
        // Only add ICE candidate if remote description is set
        if (pc.remoteDescription && pc.remoteDescription.type) {
          await pc.addIceCandidate(new RTCIceCandidate(message.candidate));
          
          // Process any queued candidates for this peer
          const queuedCandidates = iceCandidateQueueRef.current[message.from_user] || [];
          for (const candidate of queuedCandidates) {
            try {
              await pc.addIceCandidate(new RTCIceCandidate(candidate));
            } catch (e) {
              console.warn('Error adding queued ICE candidate:', e);
            }
          }
          iceCandidateQueueRef.current[message.from_user] = [];
        } else {
          // Queue ICE candidate for later
          console.log('Remote description not set, queuing ICE candidate for', message.from_user);
          if (!iceCandidateQueueRef.current[message.from_user]) {
            iceCandidateQueueRef.current[message.from_user] = [];
          }
          iceCandidateQueueRef.current[message.from_user].push(message.candidate);
        }
      } catch (e) {
        // Ignore InvalidStateError - connection might be in wrong state
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
      safeSend({
        type: 'recording_request',
        requester_name: user?.name || user?.email || 'Host'
      });
      
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
    safeSend({ type: 'raise_hand', raised: newState });
  }, [isHandRaised, safeSend]);

  const sendChatMessage = useCallback((message) => {
    safeSend({ type: 'chat', message });
  }, [safeSend]);

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
