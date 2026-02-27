import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { Shield, Copy, Calendar, Loader2, Circle,
  Check, X, AlertTriangle, Image as ImageIcon,
  Mic, MicOff, Video, VideoOff, Monitor, MonitorOff,
  Hand, PhoneOff, Square, MessageSquare, Users, Sparkles, Share2,
  Captions, CaptionsOff, BarChart3, PenTool
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from '@/components/ui/dialog';

// Import refactored child components
import { ParticipantGrid } from './ParticipantGrid';
import { ChatPanel, AINotesPanel, ParticipantsPanel, SettingsPanel } from './MeetingPanels';
import ShareMeetingDialog from './ShareMeetingDialog';
import BreakoutRoomManager from './BreakoutRoomManager';
import LiveCaptions from './LiveCaptions';
import MeetingReactions from './MeetingReactions';
import { PollsPanel } from './PollsPanel';
import MeetingWhiteboard from './MeetingWhiteboard';

const API = process.env.REACT_APP_BACKEND_URL;

// Virtual Background Options - Expanded with AI backgrounds
const VIRTUAL_BACKGROUNDS = [
  // Basic Effects (Available Now)
  { id: 'none', name: 'None', type: 'none' },
  { id: 'blur', name: 'Blur', type: 'blur' },
  { id: 'blur-light', name: 'Light Blur', type: 'blur', level: 'light' },
  { id: 'blur-heavy', name: 'Heavy Blur', type: 'blur', level: 'heavy' },
  
  // Professional Backgrounds
  { id: 'office', name: 'Office', type: 'image', url: 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800' },
  { id: 'modern-office', name: 'Modern Office', type: 'image', url: 'https://images.unsplash.com/photo-1497366811353-6870744d04b2?w=800' },
  { id: 'home-office', name: 'Home Office', type: 'image', url: 'https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=800' },
  { id: 'library', name: 'Library', type: 'image', url: 'https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=800' },
  { id: 'conference', name: 'Conference Room', type: 'image', url: 'https://images.unsplash.com/photo-1431540015161-0bf868a2d407?w=800' },
  
  // Nature & Scenic
  { id: 'nature', name: 'Forest', type: 'image', url: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800' },
  { id: 'beach', name: 'Beach', type: 'image', url: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800' },
  { id: 'mountains', name: 'Mountains', type: 'image', url: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800' },
  { id: 'sunset', name: 'Sunset', type: 'image', url: 'https://images.unsplash.com/photo-1495616811223-4d98c6e9c869?w=800' },
  { id: 'garden', name: 'Garden', type: 'image', url: 'https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=800' },
  
  // Urban & City
  { id: 'city', name: 'City Skyline', type: 'image', url: 'https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?w=800' },
  { id: 'night-city', name: 'Night City', type: 'image', url: 'https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=800' },
  { id: 'coffee-shop', name: 'Coffee Shop', type: 'image', url: 'https://images.unsplash.com/photo-1445116572660-236099ec97a0?w=800' },
  
  // Abstract & Creative
  { id: 'abstract', name: 'Abstract Purple', type: 'image', url: 'https://images.unsplash.com/photo-1557682250-33bd709cbe85?w=800' },
  { id: 'gradient-blue', name: 'Blue Gradient', type: 'image', url: 'https://images.unsplash.com/photo-1557683316-973673baf926?w=800' },
  { id: 'geometric', name: 'Geometric', type: 'image', url: 'https://images.unsplash.com/photo-1558591710-4b4a1ae0f04d?w=800' },
  { id: 'space', name: 'Space', type: 'image', url: 'https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=800' },
  
  // MedMatch/KARAU Branded (placeholder - replace with actual branded images)
  { id: 'karau-branded', name: 'AI KARAU', type: 'image', url: 'https://images.unsplash.com/photo-1639322537228-f710d846310a?w=800' },
  { id: 'medical', name: 'Medical Lab', type: 'image', url: 'https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=800' },
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
const VirtualBackgroundSelector = ({ isOpen, onClose, currentBg, onSelect, onApply }) => {
  const [selectedBg, setSelectedBg] = useState(currentBg);
  const [activeCategory, setActiveCategory] = useState('effects');

  useEffect(() => {
    if (isOpen) {
      setSelectedBg(currentBg);
    }
  }, [isOpen, currentBg]);

  const handleApply = () => {
    onSelect(selectedBg);
    if (onApply) onApply(selectedBg);
    onClose();
    
    // Show feedback based on selection
    if (selectedBg === 'none') {
      // No toast needed
    } else if (selectedBg.includes('blur')) {
      toast.info('Applying blur...', { duration: 1500 });
    } else {
      toast.info('Loading background...', { duration: 1500 });
    }
  };

  // Group backgrounds by category
  const categories = {
    effects: { label: 'Effects', icon: '🌫️', items: VIRTUAL_BACKGROUNDS.filter(bg => bg.type === 'none' || bg.type === 'blur') },
    professional: { label: 'Professional', icon: '🏢', items: VIRTUAL_BACKGROUNDS.filter(bg => ['office', 'modern-office', 'home-office', 'library', 'conference'].includes(bg.id)) },
    nature: { label: 'Nature', icon: '🌲', items: VIRTUAL_BACKGROUNDS.filter(bg => ['nature', 'beach', 'mountains', 'sunset', 'garden'].includes(bg.id)) },
    urban: { label: 'Urban', icon: '🌆', items: VIRTUAL_BACKGROUNDS.filter(bg => ['city', 'night-city', 'coffee-shop'].includes(bg.id)) },
    creative: { label: 'Creative', icon: '🎨', items: VIRTUAL_BACKGROUNDS.filter(bg => ['abstract', 'gradient-blue', 'geometric', 'space'].includes(bg.id)) },
    branded: { label: 'Branded', icon: '⚗️', items: VIRTUAL_BACKGROUNDS.filter(bg => ['karau-branded', 'medical'].includes(bg.id)) },
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-slate-800 border-slate-700 max-w-lg mx-4 max-h-[85vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="text-white flex items-center gap-2">
            <ImageIcon className="w-5 h-5 text-turquoise" />
            AI Virtual Background
          </DialogTitle>
          <DialogDescription className="text-slate-400 text-sm">
            Powered by MediaPipe AI. First use may take a few seconds to load the model.
          </DialogDescription>
        </DialogHeader>
        
        {/* Category Tabs */}
        <div className="flex gap-1 overflow-x-auto py-2 border-b border-slate-700">
          {Object.entries(categories).map(([key, { label, icon }]) => (
            <button
              key={key}
              onClick={() => setActiveCategory(key)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all ${
                activeCategory === key
                  ? 'bg-turquoise text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              {icon} {label}
            </button>
          ))}
        </div>
        
        {/* Background Options */}
        <div className="flex-1 overflow-y-auto py-4">
          {activeCategory === 'effects' ? (
            <div className="grid grid-cols-2 gap-3">
              {categories.effects.items.map((bg) => (
                <button
                  key={bg.id}
                  onClick={() => setSelectedBg(bg.id)}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    selectedBg === bg.id 
                      ? 'border-turquoise bg-turquoise/10' 
                      : 'border-slate-600 bg-slate-700/50 hover:border-slate-500'
                  }`}
                >
                  <div className="text-3xl mb-2 text-center">
                    {bg.type === 'none' ? '🚫' : bg.level === 'light' ? '💨' : bg.level === 'heavy' ? '🌫️' : '🌀'}
                  </div>
                  <div className="text-sm text-slate-300 text-center font-medium">{bg.name}</div>
                  {selectedBg === bg.id && <Check className="w-5 h-5 text-turquoise mx-auto mt-2" />}
                </button>
              ))}
            </div>
          ) : (
            <div className="space-y-2">
              <div className="flex items-center gap-2 mb-3">
                <Badge variant="outline" className="text-xs text-turquoise border-turquoise/50">
                  AI-Powered
                </Badge>
                <span className="text-xs text-slate-500">First use loads ~5MB model</span>
              </div>
              <div className="grid grid-cols-3 gap-2">
                {categories[activeCategory]?.items.map((bg) => (
                  <button
                    key={bg.id}
                    onClick={() => setSelectedBg(bg.id)}
                    className={`relative aspect-video rounded-lg overflow-hidden border-2 transition-all ${
                      selectedBg === bg.id 
                        ? 'border-turquoise ring-2 ring-turquoise/50' 
                        : 'border-slate-600 hover:border-slate-500'
                    }`}
                  >
                    <img src={bg.url} alt={bg.name} className="w-full h-full object-cover" />
                    <span className="absolute bottom-0 left-0 right-0 text-xs text-white bg-black/70 px-1 py-0.5 text-center truncate">
                      {bg.name}
                    </span>
                    {selectedBg === bg.id && (
                      <div className="absolute top-1 right-1 w-5 h-5 bg-turquoise rounded-full flex items-center justify-center">
                        <Check className="w-3 h-3 text-white" />
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
        
        <DialogFooter className="gap-2 border-t border-slate-700 pt-4">
          <Button variant="outline" onClick={onClose} className="text-slate-300">Cancel</Button>
          <Button onClick={handleApply} className="bg-turquoise hover:bg-turquoise/80">Apply</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

// Meeting Header Component - Mobile Responsive
const MeetingHeader = ({ meeting, meetingId, isRecording, onAddToCalendar, onCopyLink, onShare }) => (
  <header className="min-h-[48px] md:h-16 bg-slate-800 border-b border-slate-700 flex items-center justify-between px-2 md:px-4 py-2">
    <div className="flex items-center gap-1 md:gap-3 flex-wrap">
      <div className="flex items-center gap-1 md:gap-2">
        <Shield className="w-4 h-4 md:w-5 md:h-5 text-turquoise flex-shrink-0" />
        <span className="text-white font-semibold text-sm md:text-base hidden sm:inline">AI KARAU Meeting</span>
        <span className="text-white font-semibold text-sm md:text-base sm:hidden">KARAU</span>
      </div>
      <Badge variant="outline" className="text-slate-300 border-slate-600 text-xs md:text-sm max-w-[100px] md:max-w-none truncate">
        {meeting?.title || 'Meeting'}
      </Badge>
      <Badge className="bg-green-500/20 text-green-400 border-green-500/30 text-xs">
        <Shield className="w-3 h-3 mr-0.5 md:mr-1" />
        <span className="hidden xs:inline">E2E </span>Encrypted
      </Badge>
      {isRecording && (
        <Badge className="bg-red-500/20 text-red-400 border-red-500/30 animate-pulse text-xs">
          <Circle className="w-2 h-2 mr-0.5 fill-current" />
          REC
        </Badge>
      )}
    </div>
    
    <div className="flex items-center gap-1 md:gap-2">
      <Button variant="ghost" size="sm" onClick={onShare} className="text-slate-300 hover:text-turquoise px-1.5 md:px-3" data-testid="meeting-share-btn">
        <Share2 className="w-4 h-4" />
        <span className="hidden md:inline ml-1">Share</span>
      </Button>
      <Button variant="ghost" size="sm" onClick={onAddToCalendar} className="text-slate-300 hover:text-white px-1.5 md:px-3">
        <Calendar className="w-4 h-4" />
        <span className="hidden md:inline ml-1">Add to Calendar</span>
      </Button>
      <Button variant="ghost" size="sm" onClick={onCopyLink} className="text-slate-300 hover:text-white px-1.5 md:px-3">
        <Copy className="w-4 h-4" />
        <span className="hidden md:inline ml-1">Copy Link</span>
      </Button>
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
  const [showShareDialog, setShowShareDialog] = useState(false);
  const [activeSpeakerId, setActiveSpeakerId] = useState(null);
  const [showBreakoutManager, setShowBreakoutManager] = useState(false);
  const [orgBranding, setOrgBranding] = useState(null);
  const [isCaptionsEnabled, setIsCaptionsEnabled] = useState(false);
  const [transcriptSegments, setTranscriptSegments] = useState([]);
  const [incomingReaction, setIncomingReaction] = useState(null);
  const [isSummarizing, setIsSummarizing] = useState(false);
  const [showWhiteboard, setShowWhiteboard] = useState(false);
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
  const audioContextRef = useRef(null);
  const analyserIntervalRef = useRef(null);
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
        width: { min: 640, ideal: 1280, max: 1920 }, 
        height: { min: 480, ideal: 720, max: 1080 },
        frameRate: { ideal: 30, max: 30 },
        facingMode: 'user'
      } : false,
      audio: hasAudio ? { 
        echoCancellation: true, 
        noiseSuppression: true,
        autoGainControl: true,
        sampleRate: 48000
      } : false
    };
    
    // If no devices at all, try anyway (browser might prompt for permission)
    if (!hasVideo && !hasAudio) {
      constraints.video = { 
        width: { ideal: 1280 },
        height: { ideal: 720 },
        facingMode: 'user' 
      };
      constraints.audio = true;
    }
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      return { success: true, stream };
    } catch (error) {
      // If high-quality constraints fail, try medium quality
      if (error.name === 'OverconstrainedError') {
        try {
          const mediumStream = await navigator.mediaDevices.getUserMedia({
            video: { 
              width: { ideal: 640 }, 
              height: { ideal: 480 },
              frameRate: { ideal: 24 }
            },
            audio: true
          });
          return { success: true, stream: mediumStream };
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

  // Initialize media and join meeting - DECOUPLED APPROACH
  useEffect(() => {
    mountedRef.current = true;
    
    const initMeeting = async () => {
      // STEP 1: Initialize Media (Independent of API)
      // Prioritize getting the video stream first
      console.log('Step 1: Initializing media devices...');
      const mediaResult = await initializeMedia();
      
      if (!mountedRef.current) {
        mediaResult.stream?.getTracks().forEach(track => track.stop());
        return;
      }
      
      if (mediaResult.success && mediaResult.stream) {
        // Store stream in ref as single source of truth
        localStreamRef.current = mediaResult.stream;
        setLocalStream(mediaResult.stream);
        setIsMediaReady(true);
        console.log('Media initialized successfully');
      } else {
        // Show specific error but continue - user might still want to join audio-only
        const errorInfo = getMediaErrorMessage(mediaResult.error);
        setConnectionError(errorInfo);
        toast.error(errorInfo.message, { duration: 4000 });
        
        // If permission denied, stop here
        if (!errorInfo.canRetry) {
          setIsConnecting(false);
          return;
        }
      }
      
      // STEP 2: Join Meeting API (Independent - doesn't affect video display)
      console.log('Step 2: Joining meeting via API...');
      const apiResult = await joinMeetingApi();
      
      if (!mountedRef.current) return;
      
      if (apiResult.success) {
        setMeeting(apiResult.data.meeting);
        setParticipants(apiResult.data.other_participants || []);
        setIsApiConnected(true);
        
        // STEP 3: Connect WebSocket
        console.log('Step 3: Connecting WebSocket...');
        const token = localStorage.getItem('token');
        connectWebSocket(
          apiResult.isGuest ? null : token, 
          false, 
          apiResult.isGuest ? user.user_id : null
        );
        
        setIsConnecting(false);
        // No toast needed - the UI shows connection status
        console.log('Joined meeting successfully');
      } else {
        // API failed but video should still display
        setIsConnecting(false);
        
        const errorMsg = apiResult.error?.message || 'Unknown error';
        if (errorMsg.includes('404')) {
          toast.error('Meeting not found', { duration: 3000 });
        } else if (errorMsg.includes('401')) {
          toast.error('Session expired', { duration: 3000 });
        } else {
          console.error('Connection error:', errorMsg);
        }
        
        // Set partial connection state - video works but not connected to meeting
        setConnectionError({
          title: 'Connection Issue',
          message: 'Unable to connect to meeting server. Your video is active locally.',
          canRetry: true
        });
      }
    };
    
    initMeeting();
    
    // Cleanup: Properly stop all tracks when component unmounts
    return () => {
      mountedRef.current = false;
      
      // Stop all media tracks
      if (localStreamRef.current) {
        localStreamRef.current.getTracks().forEach(track => {
          track.stop();
          console.log(`Stopped track: ${track.kind}`);
        });
        localStreamRef.current = null;
      }
      
      // Close WebSocket
      if (wsRef.current) {
        wsRef.current.close(1000, 'Component unmounting');
        wsRef.current = null;
      }
      
      // Close all peer connections
      Object.values(peerConnectionsRef.current).forEach(pc => {
        pc.close();
      });
      peerConnectionsRef.current = {};
      
      // Stop recording if active
      if (mediaRecorderRef.current && isRecording) {
        mediaRecorderRef.current.stop();
      }
    };
  }, [meetingId]);

  // Fetch organization branding for meeting footer
  useEffect(() => {
    const fetchBranding = async () => {
      const email = user?.email || '';
      if (!email) return;
      try {
        const res = await fetch(`${API}/api/karau-meet/organizations/branding/by-domain?email=${encodeURIComponent(email)}`);
        if (res.ok) {
          const data = await res.json();
          if (data.has_branding) setOrgBranding(data);
        }
      } catch {}
    };
    fetchBranding();
  }, [user?.email]);

  // Active speaker detection via audio level analysis
  useEffect(() => {
    if (!localStreamRef.current) return;
    
    const detectActiveSpeaker = () => {
      try {
        if (!audioContextRef.current || audioContextRef.current.state === 'closed') {
          audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
        }
        const ctx = audioContextRef.current;
        
        // Analyze remote streams for active speaker
        const checkLevels = () => {
          let maxLevel = 0;
          let maxId = null;
          
          // Check local stream
          if (localStreamRef.current && isAudioEnabled) {
            try {
              const analyser = ctx.createAnalyser();
              analyser.fftSize = 256;
              const source = ctx.createMediaStreamSource(localStreamRef.current);
              source.connect(analyser);
              const data = new Uint8Array(analyser.frequencyBinCount);
              analyser.getByteFrequencyData(data);
              const avg = data.reduce((a, b) => a + b, 0) / data.length;
              if (avg > maxLevel && avg > 15) { // Threshold to avoid noise
                maxLevel = avg;
                maxId = effectiveUserId;
              }
              source.disconnect();
            } catch {}
          }
          
          // Check remote peer streams
          for (const [peerId, pc] of Object.entries(peerConnectionsRef.current)) {
            try {
              const receivers = pc.getReceivers();
              const audioReceiver = receivers.find(r => r.track && r.track.kind === 'audio');
              if (audioReceiver && audioReceiver.track) {
                const stream = new MediaStream([audioReceiver.track]);
                const analyser = ctx.createAnalyser();
                analyser.fftSize = 256;
                const source = ctx.createMediaStreamSource(stream);
                source.connect(analyser);
                const data = new Uint8Array(analyser.frequencyBinCount);
                analyser.getByteFrequencyData(data);
                const avg = data.reduce((a, b) => a + b, 0) / data.length;
                if (avg > maxLevel && avg > 15) {
                  maxLevel = avg;
                  maxId = peerId;
                }
                source.disconnect();
              }
            } catch {}
          }
          
          setActiveSpeakerId(prev => maxId !== prev ? maxId : prev);
        };
        
        analyserIntervalRef.current = setInterval(checkLevels, 500);
      } catch (e) {
        console.warn('Active speaker detection failed:', e);
      }
    };
    
    const timer = setTimeout(detectActiveSpeaker, 2000);
    
    return () => {
      clearTimeout(timer);
      if (analyserIntervalRef.current) clearInterval(analyserIntervalRef.current);
    };
  }, [isAudioEnabled, effectiveUserId]);

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
      toast.error('Unable to reconnect. Please refresh.', { duration: 5000 });
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
        // Silent reconnection - no toast
        reconnectAttemptsRef.current = 0;
        connectWebSocket(token, true);
      }
    };
    
    const handleOffline = () => {
      console.log('Network lost');
      // Only show this if user is actively in meeting
      if (isConnected) {
        toast.warning('Connection lost', { duration: 2000 });
      }
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [connectWebSocket, isConnected]);

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
        // Don't show reconnection toast - it's too noisy
        break;
      
      case 'ping':
        // Respond to server heartbeat
        safeSend({ type: 'pong', timestamp: message.timestamp });
        break;
        
      case 'user_joined':
        setParticipants(message.participants || []);
        if (message.user_id !== user?.user_id) {
          try {
            await createPeerConnection(message.user_id, true);
          } catch (err) {
            console.error('Failed to create peer connection:', err);
          }
          // Only show join notification if not in a reconnection scenario
          if (!message.is_reconnection) {
            toast.info(`${message.user_name} joined`, { duration: 2000 });
          }
        }
        break;
        
      case 'user_left':
        setParticipants(message.participants || []);
        if (peerConnectionsRef.current[message.user_id]) {
          try {
            peerConnectionsRef.current[message.user_id].close();
          } catch (err) {
            console.error('Error closing peer connection:', err);
          }
          delete peerConnectionsRef.current[message.user_id];
        }
        setRemoteStreams(prev => {
          const updated = { ...prev };
          delete updated[message.user_id];
          return updated;
        });
        // Brief notification
        toast.info(`${message.user_name} left`, { duration: 2000 });
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
        try {
          await handleOffer(message);
        } catch (err) {
          console.error('Error handling offer:', err);
        }
        break;
        
      case 'answer':
        try {
          await handleAnswer(message);
        } catch (err) {
          console.error('Error handling answer:', err);
        }
        break;
        
      case 'ice_candidate':
        try {
          await handleIceCandidate(message);
        } catch (err) {
          console.error('Error handling ICE candidate:', err);
        }
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
        setIncomingReaction({ emoji: message.emoji, ts: Date.now() });
        if (message.from_user !== user?.user_id) {
          toast(
            <div className="flex items-center gap-2">
              <span className="text-2xl">{message.emoji}</span>
              <span>{message.from_name}</span>
            </div>,
            { duration: 1500 }
          );
        }
        break;
        
      case 'host_action':
        if (message.action === 'force_mute') {
          // Host force-muted this participant
          const audioTrack = localStreamRef.current?.getAudioTracks()[0];
          if (audioTrack) {
            audioTrack.enabled = false;
            setIsAudioEnabled(false);
          }
          toast.warning(`${message.from_host} muted you`, { duration: 3000 });
        } else if (message.action === 'pass_mic') {
          // Host passed the mic to this participant - auto-unmute
          const audioTrack2 = localStreamRef.current?.getAudioTracks()[0];
          if (audioTrack2) {
            audioTrack2.enabled = true;
            setIsAudioEnabled(true);
          }
          toast.success(`${message.from_host} passed the mic to you`, { duration: 3000 });
        } else if (message.action === 'removed') {
          toast.error(message.reason, { duration: 5000 });
          navigate('/karau-meet/dashboard');
        }
        break;
        
      case 'recording_request':
        setRecordingRequester(message.requester_name);
        setShowRecordingPermission(true);
        break;
        
      case 'recording_started':
        setIsRecording(true);
        // Small indicator, not blocking
        break;
        
      case 'recording_stopped':
        setIsRecording(false);
        // Small indicator, not blocking
        break;
        
      case 'meeting_ended':
        toast.info('Meeting ended', { duration: 3000 });
        navigate('/karau-meet');
        break;
        
      case 'ai_note':
        setAiNotes(prev => [...prev, message.note]);
        break;
        
      case 'lobby_guest_waiting':
        // Host notification: guest is waiting in the lobby
        toast(
          <div className="flex items-center gap-3">
            <div className="flex-1">
              <p className="font-medium text-sm">{message.user_name} is waiting in the lobby</p>
              <p className="text-xs text-slate-400">Click to manage</p>
            </div>
          </div>,
          {
            duration: 10000,
            action: {
              label: 'Admit',
              onClick: async () => {
                try {
                  const token = localStorage.getItem('token');
                  await fetch(`${API}/api/karau-meet/meetings/${meetingId}/lobby/admit`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                    body: JSON.stringify({ user_id: message.user_id })
                  });
                  toast.success(`${message.user_name} admitted`);
                } catch {
                  toast.error('Failed to admit');
                }
              }
            }
          }
        );
        break;
        
      case 'pong':
        break;

      case 'breakout_session_started':
        toast.info('Breakout rooms opened!', { duration: 4000 });
        break;

      case 'breakout_session_closed':
        toast.info(`Everyone returned to main room`, { duration: 4000 });
        setShowBreakoutManager(false);
        break;

      case 'breakout_room_assigned':
        toast.info(`You've been assigned to ${message.room?.room_name || 'a breakout room'}`, { duration: 4000 });
        break;

      case 'breakout_room_moved':
        toast.info('You were moved to a different room', { duration: 3000 });
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
      const sender = pc.addTrack(track, localStreamRef.current);
      // Enterprise-grade encoding: H.264 at 1.4Mbps for 720p (Zoom/Teams benchmark)
      if (track.kind === 'video') {
        setTimeout(async () => {
          try {
            const params = sender.getParameters();
            if (!params.encodings || params.encodings.length === 0) {
              params.encodings = [{}];
            }
            params.encodings[0].maxBitrate = 1500000; // 1.5 Mbps for 720p HD
            params.encodings[0].maxFramerate = 30;
            params.encodings[0].scaleResolutionDownBy = 1.0; // No downscale
            await sender.setParameters(params);
          } catch (e) {
            // Non-critical: browser may not support all params
          }
        }, 200);
      }
      if (track.kind === 'audio') {
        setTimeout(async () => {
          try {
            const params = sender.getParameters();
            if (!params.encodings || params.encodings.length === 0) {
              params.encodings = [{}];
            }
            params.encodings[0].maxBitrate = 128000; // 128kbps for clear audio
            await sender.setParameters(params);
          } catch (e) {
            // Non-critical
          }
        }, 200);
      }
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

  // Host: Mute all participants
  const muteAll = useCallback(() => {
    safeSend({ type: 'mute_all' });
    toast.success('All participants muted');
  }, [safeSend]);

  // Host: Force-mute a specific participant
  const muteParticipant = useCallback((targetUserId) => {
    safeSend({ type: 'mute_participant', target: targetUserId });
  }, [safeSend]);

  // Host: Pass mic to a specific participant (auto-unmutes them, mutes others)
  const passMic = useCallback((targetUserId) => {
    safeSend({ type: 'pass_mic', target: targetUserId });
    toast.success('Mic passed');
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

  // Handle transcript segment from LiveCaptions
  const handleTranscriptUpdate = useCallback((segment) => {
    setTranscriptSegments(prev => [...prev, segment]);
    // Also add to AI notes
    setAiNotes(prev => [...prev, {
      type: 'transcription',
      content: `${segment.speaker}: ${segment.text}`,
      timestamp: segment.timestamp
    }]);
  }, []);

  // Send emoji reaction via WebSocket
  const sendReaction = useCallback((emoji) => {
    safeSend({ type: 'reaction', emoji, from_name: user?.name || 'You' });
  }, [safeSend, user]);

  // Generate AI summary from transcript
  const generateSummary = useCallback(async () => {
    if (transcriptSegments.length === 0) {
      toast.info('No transcript available yet. Enable captions to start recording the conversation.');
      return;
    }
    setIsSummarizing(true);
    try {
      const res = await fetch(`${API}/api/karau-meet/ai/summarize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          meeting_id: meetingId,
          meeting_title: meeting?.title || 'Meeting',
          transcript: transcriptSegments
        })
      });
      if (res.ok) {
        const data = await res.json();
        // Add summary to AI notes
        setAiNotes(prev => [
          ...prev,
          { type: 'summary', content: data.summary, timestamp: new Date().toISOString() },
          ...data.action_items.map(item => ({
            type: 'action_item', content: item, timestamp: new Date().toISOString()
          })),
          ...data.key_decisions.map(d => ({
            type: 'key_decision', content: d, timestamp: new Date().toISOString()
          }))
        ]);
        toast.success('Meeting summary generated!');
      } else {
        toast.error('Failed to generate summary');
      }
    } catch (e) {
      toast.error('Summary generation failed');
    }
    setIsSummarizing(false);
  }, [transcriptSegments, meetingId, meeting]);

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
      <div className="min-h-screen bg-karau-bg flex items-center justify-center">
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
    <div className="h-screen bg-karau-bg flex flex-col overflow-hidden" data-testid="meeting-room">
      {/* Compact Header */}
      <header className="h-12 bg-slate-800/90 backdrop-blur border-b border-slate-700 flex items-center justify-between px-3 flex-shrink-0">
        <div className="flex items-center gap-2">
          <Shield className="w-4 h-4 text-turquoise" />
          <span className="text-white font-medium text-sm">AI KARAU</span>
          {isRecording && (
            <Badge className="bg-red-500 text-white border-0 text-xs animate-pulse">
              <Circle className="w-2 h-2 mr-1 fill-current" />
              REC
            </Badge>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" onClick={() => setShowShareDialog(true)} className="text-slate-300 hover:text-turquoise h-8 px-2" data-testid="meeting-share-btn">
            <Share2 className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm" onClick={addToCalendar} className="text-slate-300 hover:text-white h-8 px-2">
            <Calendar className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm" onClick={copyMeetingLink} className="text-slate-300 hover:text-white h-8 px-2">
            <Copy className="w-4 h-4" />
          </Button>
          <Badge variant="outline" className="text-slate-400 border-slate-600 text-xs">
            {meetingId}
          </Badge>
        </div>
      </header>

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Video Area - Zoom-style horizontal layout */}
        <div className={`flex-1 flex flex-col transition-all duration-300 ${activePanel ? 'md:mr-80' : ''}`}>
          {/* Video Grid Container */}
          <div className="flex-1 p-2 md:p-3 overflow-hidden relative">
            <div className="h-full flex items-center justify-center">
              <ParticipantGrid
                participants={allParticipants}
                localStream={localStream}
                remoteStreams={remoteStreams}
                localUserId={user?.user_id}
                virtualBackground={virtualBackground}
                activeSpeakerId={activeSpeakerId}
              />
            </div>
            {/* Live Captions Overlay */}
            <LiveCaptions
              isEnabled={isCaptionsEnabled}
              onTranscriptUpdate={handleTranscriptUpdate}
              onToggle={() => setIsCaptionsEnabled(!isCaptionsEnabled)}
            />
            {/* Floating Reactions */}
            <MeetingReactions
              onSendReaction={sendReaction}
              incomingReaction={incomingReaction}
            />
          </div>

          {/* Quick Actions Bar - Above main controls */}
          <div className="px-3 pb-2 flex justify-center gap-2 flex-shrink-0 flex-wrap">
            <Button
              variant={activePanel === 'chat' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setActivePanel(activePanel === 'chat' ? null : 'chat')}
              className={`h-9 ${activePanel === 'chat' ? 'bg-turquoise' : 'border-slate-600 text-slate-300'}`}
            >
              <MessageSquare className="w-4 h-4 mr-1.5" />
              Chat
              {chatMessages.length > 0 && (
                <Badge className="ml-1.5 bg-red-500 text-white text-xs px-1.5 py-0">{chatMessages.length}</Badge>
              )}
            </Button>
            <Button
              variant={activePanel === 'participants' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setActivePanel(activePanel === 'participants' ? null : 'participants')}
              className={`h-9 ${activePanel === 'participants' ? 'bg-turquoise' : 'border-slate-600 text-slate-300'}`}
            >
              <Users className="w-4 h-4 mr-1.5" />
              {allParticipants.length}
            </Button>
            <Button
              variant={activePanel === 'ai-notes' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setActivePanel(activePanel === 'ai-notes' ? null : 'ai-notes')}
              className={`h-9 ${activePanel === 'ai-notes' ? 'bg-turquoise' : 'border-slate-600 text-slate-300'}`}
            >
              <Sparkles className="w-4 h-4 mr-1.5" />
              AI Notes
            </Button>
            <Button
              variant={activePanel === 'polls' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setActivePanel(activePanel === 'polls' ? null : 'polls')}
              className={`h-9 ${activePanel === 'polls' ? 'bg-turquoise' : 'border-slate-600 text-slate-300'}`}
              data-testid="polls-panel-btn"
            >
              <BarChart3 className="w-4 h-4 mr-1.5" />
              Polls
            </Button>
            <Button
              variant={isCaptionsEnabled ? 'default' : 'outline'}
              size="sm"
              onClick={() => setIsCaptionsEnabled(!isCaptionsEnabled)}
              className={`h-9 ${isCaptionsEnabled ? 'bg-turquoise' : 'border-slate-600 text-slate-300'}`}
              data-testid="captions-toggle-btn"
            >
              {isCaptionsEnabled ? <Captions className="w-4 h-4 mr-1.5" /> : <CaptionsOff className="w-4 h-4 mr-1.5" />}
              CC
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowBgSelector(true)}
              className="h-9 border-slate-600 text-slate-300"
            >
              <ImageIcon className="w-4 h-4 mr-1.5" />
              Background
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowWhiteboard(true)}
              className="h-9 border-slate-600 text-slate-300"
              data-testid="whiteboard-btn"
            >
              <PenTool className="w-4 h-4 mr-1.5" />
              Whiteboard
            </Button>
          </div>

          {/* Main Control Bar - Zoom style */}
          <div className="h-16 bg-slate-800 border-t border-slate-700 flex items-center justify-center gap-3 px-4 flex-shrink-0 relative">
            {/* Org branding footer (left side) */}
            {orgBranding && (
              <div className="absolute left-4 flex items-center gap-2" data-testid="org-branding-footer">
                {orgBranding.logo_url ? (
                  <img src={orgBranding.logo_url} alt="" className="h-5 object-contain opacity-70" />
                ) : (
                  <div className="w-5 h-5 rounded flex items-center justify-center text-white text-[9px] font-bold opacity-70" style={{ backgroundColor: orgBranding.primary_color }}>
                    {orgBranding.org_name?.charAt(0)}
                  </div>
                )}
                <span className="text-[10px] text-slate-500">{orgBranding.watermark_text}</span>
              </div>
            )}
            {/* Audio Control */}
            <div className="flex flex-col items-center">
              <Button
                variant={isAudioEnabled ? 'secondary' : 'destructive'}
                size="lg"
                className="rounded-full w-11 h-11"
                onClick={toggleAudio}
                data-testid="control-audio"
              >
                {isAudioEnabled ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5" />}
              </Button>
              <span className="text-xs text-slate-400 mt-1">{isAudioEnabled ? 'Mute' : 'Unmute'}</span>
            </div>

            {/* Video Control */}
            <div className="flex flex-col items-center">
              <Button
                variant={isVideoEnabled ? 'secondary' : 'destructive'}
                size="lg"
                className="rounded-full w-11 h-11"
                onClick={toggleVideo}
                data-testid="control-video"
              >
                {isVideoEnabled ? <Video className="w-5 h-5" /> : <VideoOff className="w-5 h-5" />}
              </Button>
              <span className="text-xs text-slate-400 mt-1">{isVideoEnabled ? 'Stop' : 'Start'}</span>
            </div>

            {/* Screen Share */}
            <div className="flex flex-col items-center">
              <Button
                variant={isScreenSharing ? 'default' : 'secondary'}
                size="lg"
                className={`rounded-full w-11 h-11 ${isScreenSharing ? 'bg-green-500 hover:bg-green-600' : ''}`}
                onClick={toggleScreenShare}
                data-testid="control-screen-share"
              >
                {isScreenSharing ? <MonitorOff className="w-5 h-5" /> : <Monitor className="w-5 h-5" />}
              </Button>
              <span className="text-xs text-slate-400 mt-1">Share</span>
            </div>

            {/* Record (Host only) */}
            {isHost && (
              <div className="flex flex-col items-center">
                <Button
                  variant={isRecording ? 'destructive' : 'secondary'}
                  size="lg"
                  className={`rounded-full w-11 h-11 ${isRecording ? 'animate-pulse' : ''}`}
                  onClick={toggleRecording}
                  data-testid="control-record"
                >
                  {isRecording ? <Square className="w-5 h-5" /> : <Circle className="w-5 h-5" />}
                </Button>
                <span className="text-xs text-slate-400 mt-1">{isRecording ? 'Stop' : 'Record'}</span>
              </div>
            )}

            {/* Raise Hand */}
            <div className="flex flex-col items-center">
              <Button
                variant={isHandRaised ? 'default' : 'secondary'}
                size="lg"
                className={`rounded-full w-11 h-11 ${isHandRaised ? 'bg-yellow-500 hover:bg-yellow-600' : ''}`}
                onClick={toggleHandRaise}
                data-testid="control-hand"
              >
                <Hand className="w-5 h-5" />
              </Button>
              <span className="text-xs text-slate-400 mt-1">Raise</span>
            </div>

            {/* Leave Button */}
            <div className="flex flex-col items-center ml-4">
              <Button
                variant="destructive"
                size="lg"
                className="rounded-full w-11 h-11 bg-red-600 hover:bg-red-700"
                onClick={leaveMeeting}
                data-testid="control-leave"
              >
                <PhoneOff className="w-5 h-5" />
              </Button>
              <span className="text-xs text-red-400 mt-1">Leave</span>
            </div>
          </div>
        </div>

        {/* Side Panel - Desktop only, slides in */}
        {activePanel && (
          <div className="hidden md:flex absolute right-0 top-12 bottom-0 w-80 bg-slate-800 border-l border-slate-700 flex-col z-10">
            {/* Panel Header */}
            <div className="flex items-center justify-between p-3 border-b border-slate-700">
              <span className="text-white font-medium capitalize">{activePanel === 'ai-notes' ? 'AI Notes' : activePanel}</span>
              <button 
                onClick={() => setActivePanel(null)}
                className="p-1 text-slate-400 hover:text-white rounded"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="flex-1 overflow-hidden">
              {activePanel === 'chat' && (
                <ChatPanel messages={chatMessages} onSendMessage={sendChatMessage} />
              )}
              {activePanel === 'participants' && (
                <ParticipantsPanel 
                  participants={allParticipants} 
                  isHost={isHost}
                  onMuteParticipant={muteParticipant}
                  onMuteAll={muteAll}
                  onPassMic={passMic}
                  activeSpeakerId={activeSpeakerId}
                  onOpenBreakoutRooms={() => setShowBreakoutManager(true)}
                />
              )}
              {activePanel === 'ai-notes' && (
                <AINotesPanel notes={aiNotes} isTranscribing={isCaptionsEnabled} onGenerateSummary={generateSummary} isSummarizing={isSummarizing} />
              )}
              {activePanel === 'polls' && (
                <PollsPanel meetingId={meetingId} isHost={isHost} />
              )}
              {activePanel === 'settings' && (
                <SettingsPanel 
                  settings={meetingSettings} 
                  onUpdateSettings={(updates) => setMeetingSettings(prev => ({ ...prev, ...updates }))}
                />
              )}
              {showBreakoutManager && (
                <BreakoutRoomManager
                  meetingId={meetingId}
                  participants={allParticipants}
                  isHost={isHost}
                  onClose={() => setShowBreakoutManager(false)}
                />
              )}
            </div>
          </div>
        )}
      </div>

      {/* Mobile Bottom Sheet Panel */}
      {activePanel && (
        <div className="md:hidden fixed inset-x-0 bottom-0 h-[60vh] bg-slate-800 border-t border-slate-700 z-20 rounded-t-xl">
          <div className="flex items-center justify-between p-3 border-b border-slate-700">
            <span className="text-white font-medium capitalize">{activePanel === 'ai-notes' ? 'AI Notes' : activePanel}</span>
            <button 
              onClick={() => setActivePanel(null)}
              className="p-1 text-slate-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          <div className="h-[calc(60vh-48px)] overflow-hidden">
            {activePanel === 'chat' && (
              <ChatPanel messages={chatMessages} onSendMessage={sendChatMessage} />
            )}
            {activePanel === 'participants' && (
              <ParticipantsPanel 
                participants={allParticipants} 
                isHost={isHost}
                onMuteParticipant={muteParticipant}
                onMuteAll={muteAll}
                onPassMic={passMic}
                activeSpeakerId={activeSpeakerId}
                onOpenBreakoutRooms={() => setShowBreakoutManager(true)}
              />
            )}
            {activePanel === 'ai-notes' && (
              <AINotesPanel notes={aiNotes} isTranscribing={isCaptionsEnabled} onGenerateSummary={generateSummary} isSummarizing={isSummarizing} />
            )}
            {activePanel === 'polls' && (
              <PollsPanel meetingId={meetingId} isHost={isHost} />
            )}
            {showBreakoutManager && (
              <BreakoutRoomManager
                meetingId={meetingId}
                participants={allParticipants}
                isHost={isHost}
                onClose={() => setShowBreakoutManager(false)}
              />
            )}
          </div>
        </div>
      )}

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

      <ShareMeetingDialog
        isOpen={showShareDialog}
        onClose={() => setShowShareDialog(false)}
        meetingId={meetingId}
        meetingTitle={meeting?.title}
      />

      <MeetingWhiteboard
        isOpen={showWhiteboard}
        onClose={() => setShowWhiteboard(false)}
      />
    </div>
  );
};

export default MeetingRoom;