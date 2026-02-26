/**
 * MeetingLobby - Teams-style Pre-Meeting Lobby
 * Camera/mic preview, device selection, virtual background, guest admission flow
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import {
  Shield, Mic, MicOff, Video, VideoOff, Settings2,
  Monitor, ChevronDown, Loader2, UserCheck, Clock,
  Image as ImageIcon, Check, Volume2, X, Users, Bell
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useVirtualBackground } from './useVirtualBackground';

const API = process.env.REACT_APP_BACKEND_URL;

const LOBBY_BACKGROUNDS = [
  { id: 'none', name: 'None', type: 'none' },
  { id: 'blur', name: 'Blur', type: 'blur' },
  { id: 'blur-light', name: 'Light Blur', type: 'blur', level: 'light' },
  { id: 'office', name: 'Office', type: 'image', url: 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800' },
  { id: 'nature', name: 'Forest', type: 'image', url: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800' },
  { id: 'city', name: 'City', type: 'image', url: 'https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?w=800' },
  { id: 'abstract', name: 'Abstract', type: 'image', url: 'https://images.unsplash.com/photo-1557682250-33bd709cbe85?w=800' },
];

const BACKGROUND_URLS = {
  office: 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=1280&q=80',
  nature: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1280&q=80',
  city: 'https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?w=1280&q=80',
  abstract: 'https://images.unsplash.com/photo-1557682250-33bd709cbe85?w=1280&q=80',
};

const MeetingLobby = ({ meetingId, user, isGuest = false, onJoinMeeting }) => {
  const navigate = useNavigate();
  const videoRef = useRef(null);
  const [videoElement, setVideoElement] = useState(null);
  const localStreamRef = useRef(null);

  // Media state
  const [isVideoEnabled, setIsVideoEnabled] = useState(true);
  const [isAudioEnabled, setIsAudioEnabled] = useState(true);
  const [localStream, setLocalStream] = useState(null);

  // Device state
  const [videoDevices, setVideoDevices] = useState([]);
  const [audioInputDevices, setAudioInputDevices] = useState([]);
  const [audioOutputDevices, setAudioOutputDevices] = useState([]);
  const [selectedVideoDevice, setSelectedVideoDevice] = useState('');
  const [selectedAudioInput, setSelectedAudioInput] = useState('');
  const [selectedAudioOutput, setSelectedAudioOutput] = useState('');

  // Background
  const [selectedBg, setSelectedBg] = useState('none');
  const [showBgPicker, setShowBgPicker] = useState(false);

  // Lobby state
  const [meetingInfo, setMeetingInfo] = useState(null);
  const [lobbyStatus, setLobbyStatus] = useState('loading'); // loading | preview | waiting | admitted | rejected
  const [lobbyUserId, setLobbyUserId] = useState(null);
  const [isJoining, setIsJoining] = useState(false);
  const [showDeviceSettings, setShowDeviceSettings] = useState(false);

  // Host lobby management
  const [waitingGuests, setWaitingGuests] = useState([]);

  // Virtual background
  const bgUrl = BACKGROUND_URLS[selectedBg] || null;
  const { canvasRef, isActive: bgActive } = useVirtualBackground(videoElement, selectedBg, bgUrl);
  const showProcessed = selectedBg !== 'none' && bgActive;

  // Fetch meeting info
  useEffect(() => {
    const fetchInfo = async () => {
      try {
        const res = await fetch(`${API}/api/karau-meet/meetings/${meetingId}/info`);
        if (res.ok) {
          const data = await res.json();
          setMeetingInfo(data);
          setLobbyStatus('preview');
        } else {
          toast.error('Meeting not found');
          setLobbyStatus('rejected');
        }
      } catch {
        toast.error('Unable to connect');
        setLobbyStatus('rejected');
      }
    };
    fetchInfo();
  }, [meetingId]);

  // Enumerate devices and start camera
  useEffect(() => {
    const initMedia = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { width: { ideal: 1280 }, height: { ideal: 720 }, frameRate: { ideal: 30 } },
          audio: { echoCancellation: true, noiseSuppression: true }
        });
        localStreamRef.current = stream;
        setLocalStream(stream);

        const devices = await navigator.mediaDevices.enumerateDevices();
        setVideoDevices(devices.filter(d => d.kind === 'videoinput'));
        setAudioInputDevices(devices.filter(d => d.kind === 'audioinput'));
        setAudioOutputDevices(devices.filter(d => d.kind === 'audiooutput'));

        const vt = stream.getVideoTracks()[0];
        const at = stream.getAudioTracks()[0];
        if (vt) setSelectedVideoDevice(vt.getSettings().deviceId || '');
        if (at) setSelectedAudioInput(at.getSettings().deviceId || '');
      } catch (err) {
        console.error('Media init error:', err);
        toast.error('Could not access camera/microphone');
      }
    };
    initMedia();

    return () => {
      localStreamRef.current?.getTracks().forEach(t => t.stop());
    };
  }, []);

  // Attach stream to video element
  useEffect(() => {
    if (videoRef.current && localStream) {
      videoRef.current.srcObject = localStream;
      setVideoElement(videoRef.current);
    }
  }, [localStream]);

  // Switch camera
  const switchCamera = useCallback(async (deviceId) => {
    if (!deviceId) return;
    try {
      const newStream = await navigator.mediaDevices.getUserMedia({
        video: { deviceId: { exact: deviceId }, width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: selectedAudioInput ? { deviceId: { exact: selectedAudioInput } } : true
      });
      localStreamRef.current?.getTracks().forEach(t => t.stop());
      localStreamRef.current = newStream;
      setLocalStream(newStream);
      setSelectedVideoDevice(deviceId);
    } catch {
      toast.error('Could not switch camera');
    }
  }, [selectedAudioInput]);

  // Switch mic
  const switchMic = useCallback(async (deviceId) => {
    if (!deviceId) return;
    try {
      const newStream = await navigator.mediaDevices.getUserMedia({
        video: selectedVideoDevice ? { deviceId: { exact: selectedVideoDevice } } : true,
        audio: { deviceId: { exact: deviceId } }
      });
      localStreamRef.current?.getTracks().forEach(t => t.stop());
      localStreamRef.current = newStream;
      setLocalStream(newStream);
      setSelectedAudioInput(deviceId);
    } catch {
      toast.error('Could not switch microphone');
    }
  }, [selectedVideoDevice]);

  // Toggle video/audio
  const toggleVideo = () => {
    const vt = localStreamRef.current?.getVideoTracks()[0];
    if (vt) { vt.enabled = !vt.enabled; setIsVideoEnabled(vt.enabled); }
  };
  const toggleAudio = () => {
    const at = localStreamRef.current?.getAudioTracks()[0];
    if (at) { at.enabled = !at.enabled; setIsAudioEnabled(at.enabled); }
  };

  // Poll lobby status for guests
  useEffect(() => {
    if (lobbyStatus !== 'waiting' || !lobbyUserId) return;
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API}/api/karau-meet/meetings/${meetingId}/lobby/status?user_id=${lobbyUserId}`);
        if (res.ok) {
          const data = await res.json();
          if (data.admitted) {
            setLobbyStatus('admitted');
            toast.success('You have been admitted!');
            clearInterval(interval);
          } else if (data.rejected) {
            setLobbyStatus('rejected');
            toast.error('Your request to join was denied');
            clearInterval(interval);
          }
        }
      } catch {}
    }, 2000);
    return () => clearInterval(interval);
  }, [lobbyStatus, lobbyUserId, meetingId]);

  // For host: poll waiting list
  const isHost = !isGuest && user && meetingInfo && meetingInfo.host_name;
  useEffect(() => {
    if (!isHost || lobbyStatus === 'loading') return;
    // Host doesn't need to poll in lobby, they get WS notifications in room
  }, [isHost, lobbyStatus]);

  // Join lobby (request admission)
  const requestAdmission = async () => {
    setIsJoining(true);
    try {
      const token = localStorage.getItem('token');
      let res;
      if (isGuest || !token) {
        res = await fetch(`${API}/api/karau-meet/meetings/${meetingId}/lobby/join`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ guest_name: user?.name || 'Guest', guest_email: user?.email || '', is_guest: true })
        });
      } else {
        res = await fetch(`${API}/api/karau-meet/meetings/${meetingId}/lobby/join-auth`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }
        });
      }

      if (res.ok) {
        const data = await res.json();
        setLobbyUserId(data.user_id);
        if (data.status === 'admitted' || data.is_host) {
          setLobbyStatus('admitted');
        } else {
          setLobbyStatus('waiting');
        }
      } else {
        toast.error('Could not join lobby');
      }
    } catch {
      toast.error('Connection error');
    }
    setIsJoining(false);
  };

  // Actually join the meeting room
  const handleJoinMeeting = () => {
    localStreamRef.current?.getTracks().forEach(t => t.stop());
    if (onJoinMeeting) {
      onJoinMeeting({
        userId: lobbyUserId || user?.user_id,
        userName: user?.name || 'Guest',
        isGuest,
        videoEnabled: isVideoEnabled,
        audioEnabled: isAudioEnabled,
        virtualBackground: selectedBg,
        selectedVideoDevice,
        selectedAudioInput,
      });
    }
  };

  // Auto-join for host or when admitted
  useEffect(() => {
    if (lobbyStatus === 'admitted' && lobbyUserId) {
      // Short delay to show the "admitted" message
      const t = setTimeout(handleJoinMeeting, 800);
      return () => clearTimeout(t);
    }
  }, [lobbyStatus, lobbyUserId]);

  // Loading state
  if (lobbyStatus === 'loading') {
    return (
      <div className="min-h-screen bg-[#1b1b1b] flex items-center justify-center" data-testid="lobby-loading">
        <div className="text-center">
          <Loader2 className="w-10 h-10 text-[#5b5fc7] animate-spin mx-auto mb-3" />
          <p className="text-white/80 text-sm">Loading meeting...</p>
        </div>
      </div>
    );
  }

  // Rejected state
  if (lobbyStatus === 'rejected') {
    return (
      <div className="min-h-screen bg-[#1b1b1b] flex items-center justify-center" data-testid="lobby-rejected">
        <div className="text-center max-w-md mx-auto px-6">
          <div className="w-16 h-16 rounded-full bg-red-500/20 flex items-center justify-center mx-auto mb-4">
            <X className="w-8 h-8 text-red-400" />
          </div>
          <h2 className="text-xl font-semibold text-white mb-2">Unable to Join</h2>
          <p className="text-white/60 text-sm mb-6">The meeting was not found or your request was denied.</p>
          <Button onClick={() => navigate('/karau-meet')} variant="outline" className="border-white/20 text-white hover:bg-white/10">
            Back to Portal
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#1b1b1b] flex flex-col" data-testid="meeting-lobby">
      {/* Top bar */}
      <header className="h-12 flex items-center justify-between px-4 border-b border-white/10 flex-shrink-0">
        <div className="flex items-center gap-2">
          <Shield className="w-4 h-4 text-[#5b5fc7]" />
          <span className="text-white font-medium text-sm">AI KARAU</span>
        </div>
        <Badge variant="outline" className="text-white/50 border-white/20 text-xs">
          {meetingId}
        </Badge>
      </header>

      {/* Main lobby area */}
      <div className="flex-1 flex flex-col lg:flex-row items-center justify-center gap-8 p-4 lg:p-8 max-w-6xl mx-auto w-full">
        {/* Video preview */}
        <div className="w-full max-w-2xl lg:flex-1">
          <div className="relative aspect-video bg-[#292929] rounded-2xl overflow-hidden shadow-2xl border border-white/5">
            {isVideoEnabled ? (
              <>
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className={`absolute inset-0 w-full h-full object-cover mirror-video ${showProcessed ? 'hidden' : ''}`}
                  data-testid="lobby-video-preview"
                />
                {selectedBg !== 'none' && (
                  <canvas
                    ref={canvasRef}
                    className={`absolute inset-0 w-full h-full object-cover ${showProcessed ? '' : 'hidden'}`}
                    data-testid="lobby-video-canvas"
                  />
                )}
              </>
            ) : (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-24 h-24 rounded-full bg-[#5b5fc7]/30 flex items-center justify-center">
                  <span className="text-4xl font-bold text-white">
                    {(user?.name || 'G').charAt(0).toUpperCase()}
                  </span>
                </div>
              </div>
            )}

            {/* Skin tone protection badge */}
            {isVideoEnabled && selectedBg !== 'none' && bgActive && (
              <Badge className="absolute top-3 left-3 bg-emerald-600/80 text-white border-0 text-[10px] z-10" data-testid="skin-tone-badge">
                Skin Tone Protection Active
              </Badge>
            )}

            {/* Control overlay */}
            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-2 z-10">
              <Button
                size="sm"
                variant={isAudioEnabled ? 'secondary' : 'destructive'}
                className="rounded-full w-10 h-10 p-0"
                onClick={toggleAudio}
                data-testid="lobby-toggle-audio"
              >
                {isAudioEnabled ? <Mic className="w-4 h-4" /> : <MicOff className="w-4 h-4" />}
              </Button>
              <Button
                size="sm"
                variant={isVideoEnabled ? 'secondary' : 'destructive'}
                className="rounded-full w-10 h-10 p-0"
                onClick={toggleVideo}
                data-testid="lobby-toggle-video"
              >
                {isVideoEnabled ? <Video className="w-4 h-4" /> : <VideoOff className="w-4 h-4" />}
              </Button>
              <Button
                size="sm"
                variant="secondary"
                className={`rounded-full w-10 h-10 p-0 ${showBgPicker ? 'ring-2 ring-[#5b5fc7]' : ''}`}
                onClick={() => setShowBgPicker(!showBgPicker)}
                data-testid="lobby-toggle-bg"
              >
                <ImageIcon className="w-4 h-4" />
              </Button>
              <Button
                size="sm"
                variant="secondary"
                className={`rounded-full w-10 h-10 p-0 ${showDeviceSettings ? 'ring-2 ring-[#5b5fc7]' : ''}`}
                onClick={() => setShowDeviceSettings(!showDeviceSettings)}
                data-testid="lobby-toggle-settings"
              >
                <Settings2 className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Background picker strip */}
          {showBgPicker && (
            <div className="mt-3 flex gap-2 overflow-x-auto pb-1 px-1" data-testid="lobby-bg-picker">
              {LOBBY_BACKGROUNDS.map(bg => (
                <button
                  key={bg.id}
                  onClick={() => setSelectedBg(bg.id)}
                  className={`flex-shrink-0 rounded-lg border-2 transition-all ${
                    selectedBg === bg.id ? 'border-[#5b5fc7] ring-1 ring-[#5b5fc7]/50' : 'border-white/10 hover:border-white/30'
                  } ${bg.url ? 'w-16 h-10 overflow-hidden' : 'w-16 h-10 flex items-center justify-center bg-[#292929]'}`}
                >
                  {bg.url ? (
                    <img src={bg.url} alt={bg.name} className="w-full h-full object-cover" />
                  ) : (
                    <span className="text-[10px] text-white/70">{bg.name}</span>
                  )}
                  {selectedBg === bg.id && (
                    <div className="absolute inset-0 flex items-center justify-center bg-black/30">
                      <Check className="w-3 h-3 text-white" />
                    </div>
                  )}
                </button>
              ))}
            </div>
          )}

          {/* Device settings */}
          {showDeviceSettings && (
            <div className="mt-3 bg-[#292929] rounded-xl p-4 space-y-3 border border-white/5" data-testid="lobby-device-settings">
              {videoDevices.length > 0 && (
                <div>
                  <label className="text-xs text-white/50 mb-1 block">Camera</label>
                  <Select value={selectedVideoDevice} onValueChange={switchCamera}>
                    <SelectTrigger className="bg-[#1b1b1b] border-white/10 text-white text-sm h-9">
                      <SelectValue placeholder="Select camera" />
                    </SelectTrigger>
                    <SelectContent className="bg-[#292929] border-white/10">
                      {videoDevices.map(d => (
                        <SelectItem key={d.deviceId} value={d.deviceId} className="text-white text-sm">
                          {d.label || `Camera ${d.deviceId.slice(0, 8)}`}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}
              {audioInputDevices.length > 0 && (
                <div>
                  <label className="text-xs text-white/50 mb-1 block">Microphone</label>
                  <Select value={selectedAudioInput} onValueChange={switchMic}>
                    <SelectTrigger className="bg-[#1b1b1b] border-white/10 text-white text-sm h-9">
                      <SelectValue placeholder="Select microphone" />
                    </SelectTrigger>
                    <SelectContent className="bg-[#292929] border-white/10">
                      {audioInputDevices.map(d => (
                        <SelectItem key={d.deviceId} value={d.deviceId} className="text-white text-sm">
                          {d.label || `Mic ${d.deviceId.slice(0, 8)}`}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}
              {audioOutputDevices.length > 0 && (
                <div>
                  <label className="text-xs text-white/50 mb-1 block">Speaker</label>
                  <Select value={selectedAudioOutput} onValueChange={setSelectedAudioOutput}>
                    <SelectTrigger className="bg-[#1b1b1b] border-white/10 text-white text-sm h-9">
                      <SelectValue placeholder="Select speaker" />
                    </SelectTrigger>
                    <SelectContent className="bg-[#292929] border-white/10">
                      {audioOutputDevices.map(d => (
                        <SelectItem key={d.deviceId} value={d.deviceId} className="text-white text-sm">
                          {d.label || `Speaker ${d.deviceId.slice(0, 8)}`}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Join panel */}
        <div className="w-full max-w-sm lg:w-80 text-center lg:text-left">
          <h1 className="text-2xl font-semibold text-white mb-1" data-testid="lobby-meeting-title">
            {meetingInfo?.title || 'AI KARAU Meeting'}
          </h1>
          <p className="text-white/50 text-sm mb-6">
            Hosted by {meetingInfo?.host_name || 'Host'}
          </p>

          {/* Preview state — ready to join */}
          {lobbyStatus === 'preview' && (
            <div className="space-y-3">
              <Button
                className="w-full bg-[#5b5fc7] hover:bg-[#4e52b5] text-white h-11 rounded-lg font-medium"
                onClick={requestAdmission}
                disabled={isJoining}
                data-testid="lobby-join-btn"
              >
                {isJoining ? (
                  <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Joining...</>
                ) : (
                  'Join now'
                )}
              </Button>
              <div className="flex items-center justify-center gap-4 text-xs text-white/40">
                <span className="flex items-center gap-1">
                  <Shield className="w-3 h-3" /> E2E Encrypted
                </span>
                <span className="flex items-center gap-1">
                  <Monitor className="w-3 h-3" /> HD Video
                </span>
              </div>
            </div>
          )}

          {/* Waiting state — waiting for host admission */}
          {lobbyStatus === 'waiting' && (
            <div className="space-y-4" data-testid="lobby-waiting">
              <div className="bg-[#292929] rounded-xl p-5 border border-white/5">
                <div className="flex items-center justify-center gap-2 mb-3">
                  <Clock className="w-5 h-5 text-amber-400 animate-pulse" />
                  <span className="text-white font-medium text-sm">Waiting for host</span>
                </div>
                <p className="text-white/50 text-xs leading-relaxed">
                  The host has been notified. You'll be admitted shortly.
                </p>
                <div className="mt-4">
                  <div className="h-1 bg-white/10 rounded-full overflow-hidden">
                    <div className="h-full bg-[#5b5fc7] rounded-full animate-pulse" style={{ width: '60%' }} />
                  </div>
                </div>
              </div>
              <Button
                variant="outline"
                className="w-full border-white/20 text-white/70 hover:bg-white/5 h-9"
                onClick={() => {
                  localStreamRef.current?.getTracks().forEach(t => t.stop());
                  navigate('/karau-meet');
                }}
                data-testid="lobby-cancel-btn"
              >
                Leave lobby
              </Button>
            </div>
          )}

          {/* Admitted state — brief transition */}
          {lobbyStatus === 'admitted' && (
            <div className="space-y-3" data-testid="lobby-admitted">
              <div className="bg-emerald-500/10 rounded-xl p-4 border border-emerald-500/20">
                <div className="flex items-center justify-center gap-2">
                  <UserCheck className="w-5 h-5 text-emerald-400" />
                  <span className="text-emerald-400 font-medium text-sm">Admitted! Joining...</span>
                </div>
              </div>
              <Loader2 className="w-6 h-6 text-[#5b5fc7] animate-spin mx-auto" />
            </div>
          )}
        </div>
      </div>

      {/* Mirror CSS */}
      <style>{`.mirror-video { transform: scaleX(-1); }`}</style>
    </div>
  );
};

export default MeetingLobby;
