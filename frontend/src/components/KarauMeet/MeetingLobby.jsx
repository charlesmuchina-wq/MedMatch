/**
 * MeetingLobby - Pre-Meeting Lobby with Camera/Mic Preview
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { MEETING_E2EE_ENABLED } from '@/config/features';
import {
  Shield, Mic, MicOff, Video, VideoOff, Settings2,
  Monitor, Loader2, UserCheck, Clock,
  Image as ImageIcon, Check, X, Brain, Eye, Globe, Wand2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useVirtualBackground } from './useVirtualBackground';
import { useTranslation } from '@/utils/i18n';

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

const AI_BADGES = [
  { icon: Brain, label: 'AI Coach' },
  { icon: Eye, label: 'Eye Contact' },
  { icon: Globe, label: 'Live Captions' },
  { icon: Wand2, label: 'Director Mode' },
];

const MeetingLobby = ({ meetingId, user, isGuest = false, onJoinMeeting }) => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const videoRef = useRef(null);
  const [videoElement, setVideoElement] = useState(null);
  const localStreamRef = useRef(null);

  const [isVideoEnabled, setIsVideoEnabled] = useState(true);
  const [isAudioEnabled, setIsAudioEnabled] = useState(true);
  const [localStream, setLocalStream] = useState(null);

  const [videoDevices, setVideoDevices] = useState([]);
  const [audioInputDevices, setAudioInputDevices] = useState([]);
  const [audioOutputDevices, setAudioOutputDevices] = useState([]);
  const [selectedVideoDevice, setSelectedVideoDevice] = useState('');
  const [selectedAudioInput, setSelectedAudioInput] = useState('');
  const [selectedAudioOutput, setSelectedAudioOutput] = useState('');

  const [selectedBg, setSelectedBg] = useState('none');
  const [showBgPicker, setShowBgPicker] = useState(false);

  const [meetingInfo, setMeetingInfo] = useState(null);
  const [lobbyStatus, setLobbyStatus] = useState('loading');
  const [lobbyUserId, setLobbyUserId] = useState(null);
  const [isJoining, setIsJoining] = useState(false);
  const [showDeviceSettings, setShowDeviceSettings] = useState(false);

  const bgUrl = BACKGROUND_URLS[selectedBg] || null;
  const { canvasRef, isActive: bgActive } = useVirtualBackground(videoElement, selectedBg, bgUrl);
  const showProcessed = selectedBg !== 'none' && bgActive;

  useEffect(() => {
    const fetchInfo = async () => {
      try {
        const res = await fetch(`${API}/api/karau-meet/meetings/${meetingId}/info`);
        if (res.ok) {
          setMeetingInfo(await res.json());
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
        setIsVideoEnabled(false);
        setIsAudioEnabled(false);
        toast.error('Could not access camera/microphone');
      }
    };
    initMedia();
    return () => { localStreamRef.current?.getTracks().forEach(t => t.stop()); };
  }, []);

  useEffect(() => {
    if (videoRef.current && localStream) {
      videoRef.current.srcObject = localStream;
      setVideoElement(videoRef.current);
    }
  }, [localStream]);

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
    } catch { toast.error('Could not switch camera'); }
  }, [selectedAudioInput]);

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
    } catch { toast.error('Could not switch microphone'); }
  }, [selectedVideoDevice]);

  const toggleVideo = () => {
    const vt = localStreamRef.current?.getVideoTracks()[0];
    if (vt) { vt.enabled = !vt.enabled; setIsVideoEnabled(vt.enabled); }
  };
  const toggleAudio = () => {
    const at = localStreamRef.current?.getAudioTracks()[0];
    if (at) { at.enabled = !at.enabled; setIsAudioEnabled(at.enabled); }
  };

  useEffect(() => {
    if (lobbyStatus !== 'waiting' || !lobbyUserId) return;
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API}/api/karau-meet/meetings/${meetingId}/lobby/status?user_id=${lobbyUserId}`);
        if (res.ok) {
          const data = await res.json();
          if (data.admitted) { setLobbyStatus('admitted'); toast.success('You have been admitted!'); clearInterval(interval); }
          else if (data.rejected) { setLobbyStatus('rejected'); toast.error('Your request was denied'); clearInterval(interval); }
        }
      } catch {}
    }, 2000);
    return () => clearInterval(interval);
  }, [lobbyStatus, lobbyUserId, meetingId]);

  const requestAdmission = async () => {
    setIsJoining(true);
    try {
      const token = localStorage.getItem('token');
      let res;
      if (isGuest || !token) {
        res = await fetch(`${API}/api/karau-meet/meetings/${meetingId}/lobby/join`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ guest_name: user?.name || 'Guest', guest_email: user?.email || '', is_guest: true })
        });
      } else {
        res = await fetch(`${API}/api/karau-meet/meetings/${meetingId}/lobby/join-auth`, {
          method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }
        });
      }
      if (res.ok) {
        const data = await res.json();
        setLobbyUserId(data.user_id);
        if (data.status === 'admitted' || data.is_host) setLobbyStatus('admitted');
        else setLobbyStatus('waiting');
      } else { toast.error('Could not join lobby'); }
    } catch { toast.error('Connection error'); }
    setIsJoining(false);
  };

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

  useEffect(() => {
    if (lobbyStatus === 'admitted' && lobbyUserId) {
      const t = setTimeout(handleJoinMeeting, 800);
      return () => clearTimeout(t);
    }
  }, [lobbyStatus, lobbyUserId]);

  if (lobbyStatus === 'loading') {
    return (
      <div className="min-h-screen bg-[#0c0d1a] flex items-center justify-center" data-testid="lobby-loading">
        <div className="text-center">
          <Loader2 className="w-10 h-10 text-purple-400 animate-spin mx-auto mb-3" />
          <p className="text-slate-400 text-sm">{t("karauMeet.connectingToMeeting")}</p>
        </div>
      </div>
    );
  }

  if (lobbyStatus === 'rejected') {
    return (
      <div className="min-h-screen bg-[#0c0d1a] flex items-center justify-center" data-testid="lobby-rejected">
        <div className="text-center max-w-md mx-auto px-6">
          <div className="w-16 h-16 rounded-2xl bg-red-500/10 border border-red-500/20 flex items-center justify-center mx-auto mb-4">
            <X className="w-8 h-8 text-red-400" />
          </div>
          <h2 className="text-xl font-semibold text-white mb-2">{t("karauMeet.unableToJoin")}</h2>
          <p className="text-slate-500 text-sm mb-6">{t("karauMeet.meetingNotFoundOrDenied")}</p>
          <Button onClick={() => navigate('/karau-meet')} className="bg-white/[0.06] hover:bg-white/[0.1] text-white border border-white/[0.08] rounded-full px-6">
            {t("karauMeet.backToPortalBtn")}
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0c0d1a] flex flex-col" data-testid="meeting-lobby" style={{ fontFamily: "'IBM Plex Sans', sans-serif" }}>
      {/* Top bar */}
      <header className="h-14 flex items-center justify-between px-6 border-b border-white/[0.04] flex-shrink-0">
        <div className="flex items-center gap-3">
          <img
            src="https://customer-assets.emergentagent.com/job_1fba32e3-e5a1-4174-b642-d1cd092309b3/artifacts/a7nojb8x_IMG_8477.jpeg"
            alt="AI KARAU"
            className="w-8 h-8 rounded-xl object-cover ring-1 ring-white/10"
          />
          <span className="text-white font-semibold text-sm">AI KARAU</span>
        </div>
        <Badge className="bg-white/[0.04] text-slate-400 border-white/[0.06] font-mono text-xs tracking-wider">
          {meetingId}
        </Badge>
      </header>

      {/* Main lobby area */}
      <div className="flex-1 flex flex-col lg:flex-row items-center justify-center gap-10 p-6 lg:p-12 max-w-7xl mx-auto w-full">
        {/* Video preview */}
        <div className="w-full max-w-2xl lg:flex-1">
          <div className="relative aspect-video bg-[#13142a] rounded-3xl overflow-hidden shadow-2xl shadow-black/40 border border-white/[0.06]">
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
                <div className="w-28 h-28 rounded-3xl bg-gradient-to-br from-purple-600/30 to-indigo-600/20 border border-purple-500/20 flex items-center justify-center">
                  <span className="text-5xl font-bold text-white/80">
                    {(user?.name || 'G').charAt(0).toUpperCase()}
                  </span>
                </div>
              </div>
            )}

            {/* Skin tone badge */}
            {isVideoEnabled && selectedBg !== 'none' && bgActive && (
              <Badge className="absolute top-4 left-4 bg-emerald-600/80 text-white border-0 text-[10px] z-10 rounded-full" data-testid="skin-tone-badge">
                {t("karauMeet.skinToneProtection")}
              </Badge>
            )}

            {/* Control overlay */}
            <div className="absolute bottom-5 left-1/2 -translate-x-1/2 flex items-center gap-3 z-10">
              <Button
                size="sm"
                className={`rounded-full w-12 h-12 p-0 shadow-lg transition-all duration-200 ${
                  isAudioEnabled
                    ? 'bg-white/[0.1] hover:bg-white/[0.15] border border-white/[0.1] text-white'
                    : 'bg-red-500/80 hover:bg-red-500 border-0 text-white'
                }`}
                onClick={toggleAudio}
                data-testid="lobby-toggle-audio"
              >
                {isAudioEnabled ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5" />}
              </Button>
              <Button
                size="sm"
                className={`rounded-full w-12 h-12 p-0 shadow-lg transition-all duration-200 ${
                  isVideoEnabled
                    ? 'bg-white/[0.1] hover:bg-white/[0.15] border border-white/[0.1] text-white'
                    : 'bg-red-500/80 hover:bg-red-500 border-0 text-white'
                }`}
                onClick={toggleVideo}
                data-testid="lobby-toggle-video"
              >
                {isVideoEnabled ? <Video className="w-5 h-5" /> : <VideoOff className="w-5 h-5" />}
              </Button>
              <Button
                size="sm"
                className={`rounded-full w-12 h-12 p-0 shadow-lg bg-white/[0.1] hover:bg-white/[0.15] border border-white/[0.1] text-white ${showBgPicker ? 'ring-2 ring-purple-500/50' : ''}`}
                onClick={() => setShowBgPicker(!showBgPicker)}
                data-testid="lobby-toggle-bg"
              >
                <ImageIcon className="w-5 h-5" />
              </Button>
              <Button
                size="sm"
                className={`rounded-full w-12 h-12 p-0 shadow-lg bg-white/[0.1] hover:bg-white/[0.15] border border-white/[0.1] text-white ${showDeviceSettings ? 'ring-2 ring-purple-500/50' : ''}`}
                onClick={() => setShowDeviceSettings(!showDeviceSettings)}
                data-testid="lobby-toggle-settings"
              >
                <Settings2 className="w-5 h-5" />
              </Button>
            </div>
          </div>

          {/* Background picker */}
          {showBgPicker && (
            <div className="mt-4 flex gap-2 overflow-x-auto pb-1 px-1" data-testid="lobby-bg-picker">
              {LOBBY_BACKGROUNDS.map(bg => (
                <button
                  key={bg.id}
                  onClick={() => setSelectedBg(bg.id)}
                  className={`flex-shrink-0 rounded-xl border-2 transition-all ${
                    selectedBg === bg.id ? 'border-purple-500 ring-1 ring-purple-500/30' : 'border-white/[0.06] hover:border-white/[0.15]'
                  } ${bg.url ? 'w-16 h-10 overflow-hidden' : 'w-16 h-10 flex items-center justify-center bg-white/[0.03]'}`}
                >
                  {bg.url ? (
                    <img src={bg.url} alt={bg.name} className="w-full h-full object-cover" />
                  ) : (
                    <span className="text-[10px] text-slate-500">{bg.name}</span>
                  )}
                  {selectedBg === bg.id && (
                    <div className="absolute inset-0 flex items-center justify-center bg-black/30 rounded-xl">
                      <Check className="w-3 h-3 text-white" />
                    </div>
                  )}
                </button>
              ))}
            </div>
          )}

          {/* Device settings */}
          {showDeviceSettings && (
            <div className="mt-4 bg-white/[0.03] rounded-2xl p-5 space-y-4 border border-white/[0.06]" data-testid="lobby-device-settings">
              {videoDevices.length > 0 && (
                <div>
                  <label className="text-xs text-slate-500 mb-1.5 block uppercase tracking-wider">{t("karauMeet.camera")}</label>
                  <Select value={selectedVideoDevice} onValueChange={switchCamera}>
                    <SelectTrigger className="bg-black/30 border-white/[0.08] text-white text-sm h-10 rounded-xl">
                      <SelectValue placeholder={t("karauMeet.selectCamera")} />
                    </SelectTrigger>
                    <SelectContent className="bg-[#1a1b2e] border-white/[0.08]">
                      {videoDevices.map(d => (
                        <SelectItem key={d.deviceId} value={d.deviceId} className="text-white text-sm">{d.label || `Camera ${d.deviceId.slice(0, 8)}`}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}
              {audioInputDevices.length > 0 && (
                <div>
                  <label className="text-xs text-slate-500 mb-1.5 block uppercase tracking-wider">{t("karauMeet.microphone")}</label>
                  <Select value={selectedAudioInput} onValueChange={switchMic}>
                    <SelectTrigger className="bg-black/30 border-white/[0.08] text-white text-sm h-10 rounded-xl">
                      <SelectValue placeholder={t("karauMeet.selectMicrophone")} />
                    </SelectTrigger>
                    <SelectContent className="bg-[#1a1b2e] border-white/[0.08]">
                      {audioInputDevices.map(d => (
                        <SelectItem key={d.deviceId} value={d.deviceId} className="text-white text-sm">{d.label || `Mic ${d.deviceId.slice(0, 8)}`}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}
              {audioOutputDevices.length > 0 && (
                <div>
                  <label className="text-xs text-slate-500 mb-1.5 block uppercase tracking-wider">{t("karauMeet.speaker")}</label>
                  <Select value={selectedAudioOutput} onValueChange={setSelectedAudioOutput}>
                    <SelectTrigger className="bg-black/30 border-white/[0.08] text-white text-sm h-10 rounded-xl">
                      <SelectValue placeholder={t("karauMeet.selectSpeaker")} />
                    </SelectTrigger>
                    <SelectContent className="bg-[#1a1b2e] border-white/[0.08]">
                      {audioOutputDevices.map(d => (
                        <SelectItem key={d.deviceId} value={d.deviceId} className="text-white text-sm">{d.label || `Speaker ${d.deviceId.slice(0, 8)}`}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Join panel */}
        <div className="w-full max-w-sm lg:w-80 text-center lg:text-left space-y-6">
          <div>
            <h1 className="text-2xl font-bold text-white mb-1" data-testid="lobby-meeting-title">
              {meetingInfo?.title || 'AI KARAU Meeting'}
            </h1>
            <p className="text-slate-500 text-sm">
              {t("karauMeet.hostedBy", { name: meetingInfo?.host_name || 'Host' })}
            </p>
          </div>

          {/* AI Features available */}
          <div className="flex flex-wrap gap-2 justify-center lg:justify-start">
            {AI_BADGES.map((badge, i) => (
              <div key={i} className="flex items-center gap-1.5 px-2.5 py-1.5 bg-white/[0.04] rounded-lg border border-white/[0.06]">
                <badge.icon className="w-3 h-3 text-purple-400" />
                <span className="text-[10px] text-slate-400 font-medium">{badge.label}</span>
              </div>
            ))}
          </div>

          {/* Preview state */}
          {lobbyStatus === 'preview' && (
            <div className="space-y-4">
              <Button
                className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white h-12 rounded-full font-semibold shadow-lg shadow-purple-500/25 transition-all duration-300 hover:scale-[1.02] active:scale-[0.98]"
                onClick={requestAdmission}
                disabled={isJoining}
                data-testid="lobby-join-btn"
              >
                {isJoining ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> {t("karauMeet.joining")}</> : t("karauMeet.joinNow")}
              </Button>
              <div className="flex items-center justify-center gap-5 text-xs text-slate-600">
                {MEETING_E2EE_ENABLED && (
                  <span className="flex items-center gap-1.5"><Shield className="w-3.5 h-3.5" /> {t("karauMeet.e2eEncrypted")}</span>
                )}
                <span className="flex items-center gap-1.5"><Monitor className="w-3.5 h-3.5" /> {t("karauMeet.hdVideo")}</span>
              </div>
            </div>
          )}

          {/* Waiting state */}
          {lobbyStatus === 'waiting' && (
            <div className="space-y-4" data-testid="lobby-waiting">
              <div className="bg-white/[0.03] rounded-2xl p-6 border border-white/[0.06]">
                <div className="flex items-center justify-center gap-2 mb-3">
                  <Clock className="w-5 h-5 text-amber-400 animate-pulse" />
                  <span className="text-white font-medium text-sm">{t("karauMeet.waitingForHost")}</span>
                </div>
                <p className="text-slate-500 text-xs leading-relaxed text-center">
                  {t("karauMeet.hostNotified")}
                </p>
                <div className="mt-4">
                  <div className="h-1.5 bg-white/[0.04] rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-purple-500 to-indigo-500 rounded-full animate-pulse" style={{ width: '60%' }} />
                  </div>
                </div>
              </div>
              <Button
                variant="outline"
                className="w-full border-white/[0.08] text-slate-400 hover:bg-white/[0.04] h-10 rounded-full"
                onClick={() => { localStreamRef.current?.getTracks().forEach(t => t.stop()); navigate('/karau-meet'); }}
                data-testid="lobby-cancel-btn"
              >
                {t("karauMeet.leaveLobby")}
              </Button>
            </div>
          )}

          {/* Admitted state */}
          {lobbyStatus === 'admitted' && (
            <div className="space-y-3" data-testid="lobby-admitted">
              <div className="bg-emerald-500/10 rounded-2xl p-5 border border-emerald-500/20">
                <div className="flex items-center justify-center gap-2">
                  <UserCheck className="w-5 h-5 text-emerald-400" />
                  <span className="text-emerald-400 font-medium text-sm">{t("karauMeet.admittedJoining")}</span>
                </div>
              </div>
              <Loader2 className="w-6 h-6 text-purple-400 animate-spin mx-auto" />
            </div>
          )}
        </div>
      </div>

      <style>{`.mirror-video { transform: scaleX(-1); }`}</style>
    </div>
  );
};

export default MeetingLobby;
