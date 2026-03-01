import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { toast } from 'sonner';
import {
  Radio, Users, Mic, MicOff, Video, VideoOff, MonitorUp,
  Hand, MessageCircleQuestion, Play, Square, Settings,
  Send, ThumbsUp, Loader2, Crown, UserPlus, UserMinus,
  Shield, Phone, Clipboard, ChevronLeft, ChevronRight,
  AudioLines, Captions, Save, Globe, ChevronDown as ChevDown,
  Building2, UserX, FileUp, FileDown, ShieldCheck, ShieldOff, Brain
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { useTranslation } from '@/utils/i18n';
import SlideRenderer from '@/components/KarauMeet/SlideRenderer';
import { useNoiseCancellation } from '@/hooks/useNoiseCancellation';
import { useLiveTranscription, CAPTION_LANGUAGES } from '@/hooks/useLiveTranscription';
import { useSpeakerDetection } from '@/hooks/useSpeakerDetection';
import AIAssistantPanel from '@/components/KarauMeet/AIAssistantPanel';

const API = process.env.REACT_APP_BACKEND_URL;
const WS_URL = API.replace('https://', 'wss://').replace('http://', 'ws://');

const ROLE_COLORS = {
  host: 'text-amber-400',
  coordinator: 'text-cyan-400',
  presenter: 'text-emerald-400',
  panelist: 'text-blue-400',
  attendee: 'text-slate-400'
};
const ROLE_BG = {
  host: 'bg-amber-500/10 border-amber-500/20',
  coordinator: 'bg-cyan-500/10 border-cyan-500/20',
  presenter: 'bg-emerald-500/10 border-emerald-500/20',
  panelist: 'bg-blue-500/10 border-blue-500/20',
  attendee: 'bg-slate-500/10 border-slate-500/20'
};

const WebinarLiveRoom = () => {
  const { webinarId } = useParams();
  const { t } = useTranslation();
  const navigate = useNavigate();

  const [roomInfo, setRoomInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [myRole, setMyRole] = useState('attendee');

  // Media
  const [isMicOn, setIsMicOn] = useState(false);
  const [isCamOn, setIsCamOn] = useState(false);
  const [isHandRaised, setIsHandRaised] = useState(false);

  // Panels
  const [activePanel, setActivePanel] = useState(null);

  // Q&A
  const [questions, setQuestions] = useState([]);
  const [newQuestion, setNewQuestion] = useState('');
  const [answerTexts, setAnswerTexts] = useState({});

  // Participants
  const [handRaises, setHandRaises] = useState([]);
  const [activeRoles, setActiveRoles] = useState({});

  // Slide drive
  const [currentSlide, setCurrentSlide] = useState(0);
  const [showSlides, setShowSlides] = useState(true);

  // Language picker
  const [showLangPicker, setShowLangPicker] = useState(false);

  // Engagement data
  const [engagementData, setEngagementData] = useState(null);

  // Noise Cancellation
  const noiseCancellation = useNoiseCancellation();

  // Live Transcription
  const liveTranscription = useLiveTranscription();

  // Speaker Detection
  const speakerDetection = useSpeakerDetection();

  // WebRTC
  const localVideoRef = useRef(null);
  const localStreamRef = useRef(null);
  const peerConnectionsRef = useRef({});
  const remoteStreamsRef = useRef({});
  const [remoteStreams, setRemoteStreams] = useState({});
  const wsRef = useRef(null);
  const reconnectRef = useRef(null);

  useEffect(() => {
    fetchRoomInfo();
    return () => {
      cleanup();
    };
  }, [webinarId]);

  // Sync active speaker to transcription
  useEffect(() => {
    if (speakerDetection.activeSpeaker) {
      liveTranscription.setActiveSpeaker(speakerDetection.activeSpeaker);
    }
  }, [speakerDetection.activeSpeaker]);
  useEffect(() => {
    if (!roomInfo) return;
    const interval = setInterval(() => {
      fetchQA();
      if (roomInfo.can_control) fetchHandRaises();
    }, 4000);
    return () => clearInterval(interval);
  }, [roomInfo]);

  const cleanup = () => {
    if (liveTranscription.active) liveTranscription.stop();
    speakerDetection.cleanup();
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach(t => t.stop());
    }
    Object.values(peerConnectionsRef.current).forEach(pc => pc.close());
    peerConnectionsRef.current = {};
    if (wsRef.current) wsRef.current.close();
    if (reconnectRef.current) clearTimeout(reconnectRef.current);
  };

  const fetchRoomInfo = async () => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/webinar/${webinarId}/room-info`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setRoomInfo(data);
        setMyRole(data.my_role);
        setHandRaises(data.hand_raises || []);
        setActiveRoles(data.active_roles || {});
        if (data.can_stream_video) startLocalMedia(true, true);
        connectWebSocket(data);
      } else if (res.status === 403) {
        toast.error('Practice session in progress');
        navigate(-1);
      }
    } catch (e) { console.error('Room info error:', e); }
    setLoading(false);
  };

  // --- WebRTC Signaling ---
  const connectWebSocket = (info) => {
    const token = localStorage.getItem('token');
    const wsUrl = `${WS_URL}/api/karau-meet/ws/webinar-${webinarId}?token=${token}&user_name=${encodeURIComponent(info.host_name || 'User')}&is_host=${info.my_role === 'host'}`;
    
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => { console.log('WebRTC WS connected'); };

    ws.onmessage = async (event) => {
      try {
        const msg = JSON.parse(event.data);
        switch (msg.type) {
          case 'user_joined':
            if (info.can_stream_video) createPeerConnection(msg.user_id, msg.user_name, true);
            break;
          case 'user_left':
            closePeerConnection(msg.user_id);
            break;
          case 'offer':
            await handleOffer(msg);
            break;
          case 'answer':
            await handleAnswer(msg);
            break;
          case 'ice_candidate':
            await handleIceCandidate(msg);
            break;
          case 'role_changed':
            fetchRoomInfo();
            break;
          case 'slide_change':
            setCurrentSlide(msg.slide_index || 0);
            break;
          default:
            break;
        }
      } catch (e) { console.error('WS message error:', e); }
    };

    ws.onclose = () => {
      reconnectRef.current = setTimeout(() => connectWebSocket(info), 3000);
    };
  };

  const createPeerConnection = async (remoteUserId, remoteName, createOffer) => {
    if (peerConnectionsRef.current[remoteUserId]) return;

    const pc = new RTCPeerConnection({
      iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
    });
    peerConnectionsRef.current[remoteUserId] = pc;

    // Add local tracks
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach(track => {
        pc.addTrack(track, localStreamRef.current);
      });
    }

    // Handle remote stream
    pc.ontrack = (event) => {
      const [stream] = event.streams;
      remoteStreamsRef.current[remoteUserId] = stream;
      setRemoteStreams(prev => ({ ...prev, [remoteUserId]: { stream, name: remoteName } }));
      // Register for speaker detection
      speakerDetection.addStream(remoteUserId, remoteName, stream);
    };

    pc.onicecandidate = (event) => {
      if (event.candidate && wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'ice_candidate',
          target_user_id: remoteUserId,
          candidate: event.candidate.toJSON()
        }));
      }
    };

    if (createOffer) {
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      wsRef.current?.send(JSON.stringify({
        type: 'offer',
        target_user_id: remoteUserId,
        sdp: offer.sdp
      }));
    }
  };

  const handleOffer = async (msg) => {
    await createPeerConnection(msg.user_id, msg.user_name || 'Peer', false);
    const pc = peerConnectionsRef.current[msg.user_id];
    if (!pc) return;
    await pc.setRemoteDescription(new RTCSessionDescription({ type: 'offer', sdp: msg.sdp }));
    const answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);
    wsRef.current?.send(JSON.stringify({
      type: 'answer', target_user_id: msg.user_id, sdp: answer.sdp
    }));
  };

  const handleAnswer = async (msg) => {
    const pc = peerConnectionsRef.current[msg.user_id];
    if (pc) await pc.setRemoteDescription(new RTCSessionDescription({ type: 'answer', sdp: msg.sdp }));
  };

  const handleIceCandidate = async (msg) => {
    const pc = peerConnectionsRef.current[msg.user_id];
    if (pc && msg.candidate) await pc.addIceCandidate(new RTCIceCandidate(msg.candidate));
  };

  const closePeerConnection = (userId) => {
    if (peerConnectionsRef.current[userId]) {
      peerConnectionsRef.current[userId].close();
      delete peerConnectionsRef.current[userId];
    }
    delete remoteStreamsRef.current[userId];
    speakerDetection.removeStream(userId);
    setRemoteStreams(prev => {
      const next = { ...prev };
      delete next[userId];
      return next;
    });
  };

  // --- Media Controls ---
  const startLocalMedia = async (video, audio) => {
    try {
      let stream = await navigator.mediaDevices.getUserMedia({ video, audio });
      // Apply noise cancellation if supported
      if (noiseCancellation.isSupported && audio) {
        try {
          stream = await noiseCancellation.applyToStream(stream);
        } catch (e) { console.warn('Noise cancellation failed:', e); }
      }
      localStreamRef.current = stream;
      if (localVideoRef.current) localVideoRef.current.srcObject = stream;
      setIsCamOn(video);
      setIsMicOn(audio);
      // Register local stream for speaker detection
      speakerDetection.addLocalStream(roomInfo?.host_name || 'You', stream);
    } catch (e) {
      console.error('Media error:', e);
      toast.error('Camera/microphone access denied');
    }
  };

  const toggleNoiseCancellation = async () => {
    if (noiseCancellation.enabled) {
      const original = noiseCancellation.removeFromStream();
      if (original) {
        localStreamRef.current = original;
        if (localVideoRef.current) localVideoRef.current.srcObject = original;
      }
    } else if (localStreamRef.current) {
      const processed = await noiseCancellation.applyToStream(localStreamRef.current);
      if (processed) {
        localStreamRef.current = processed;
        if (localVideoRef.current) localVideoRef.current.srcObject = processed;
      }
    }
  };

  const grantGuestPermission = async (userId, permission) => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/webinar/${webinarId}/guest-permission/grant`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ user_id: userId, permission })
      });
      if (res.ok) toast.success(`${permission} permission granted`);
      else toast.error('Failed to grant permission');
    } catch { toast.error('Permission error'); }
  };

  const revokeGuestPermission = async (userId) => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/webinar/${webinarId}/guest-permission/revoke`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ user_id: userId, permission: '' })
      });
      if (res.ok) toast.success('Permission revoked');
    } catch { toast.error('Revoke error'); }
  };

  // Fetch engagement dashboard periodically
  useEffect(() => {
    if (!webinarId) return;
    const fetchEngagement = async () => {
      const token = localStorage.getItem('token');
      try {
        const res = await fetch(`${API}/api/karau-features/sentiment/dashboard/${webinarId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) setEngagementData(await res.json());
      } catch {}
    };
    fetchEngagement();
    const interval = setInterval(fetchEngagement, 30000);
    return () => clearInterval(interval);
  }, [webinarId]);

  // Auto-analyze sentiment from live captions
  useEffect(() => {
    if (!liveTranscription.captions.length || !webinarId) return;
    const last = liveTranscription.captions[liveTranscription.captions.length - 1];
    if (!last?.original || last.original.length < 20) return;

    const token = localStorage.getItem('token');
    fetch(`${API}/api/karau-features/sentiment/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ meeting_id: webinarId, text: last.original, speaker: last.speaker || 'Unknown' })
    }).catch(() => {});
  }, [liveTranscription.captions.length]);

  const toggleLiveCaptions = () => {
    if (liveTranscription.active) {
      liveTranscription.stop();
    } else if (localStreamRef.current) {
      liveTranscription.start(localStreamRef.current);
    }
  };

  const saveTranscript = async () => {
    if (!liveTranscription.fullTranscript.trim()) return;
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/webinar/${webinarId}/live-transcript/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ transcript: liveTranscription.fullTranscript.trim() })
      });
      if (res.ok) toast.success('Transcript saved');
      else toast.error('Failed to save transcript');
    } catch { toast.error('Save error'); }
  };

  const toggleMic = () => {
    if (!localStreamRef.current) return;
    const track = localStreamRef.current.getAudioTracks()[0];
    if (track) { track.enabled = !track.enabled; setIsMicOn(track.enabled); }
  };

  const toggleCam = () => {
    if (!localStreamRef.current) return;
    const track = localStreamRef.current.getVideoTracks()[0];
    if (track) { track.enabled = !track.enabled; setIsCamOn(track.enabled); }
  };

  // --- Webinar Actions ---
  const apiPost = async (path) => {
    const token = localStorage.getItem('token');
    return fetch(`${API}/api/karau/webinar/${webinarId}${path}`, {
      method: 'POST', headers: { 'Authorization': `Bearer ${token}` }
    });
  };

  const apiPostJson = async (path, body) => {
    const token = localStorage.getItem('token');
    return fetch(`${API}/api/karau/webinar/${webinarId}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify(body)
    });
  };

  const toggleHandRaise = async () => {
    await apiPost(isHandRaised ? '/hand-lower' : '/hand-raise');
    setIsHandRaised(!isHandRaised);
  };

  const promoteUser = async (userId, role) => {
    const res = await apiPostJson('/roles/promote', { user_id: userId, role });
    if (res.ok) { toast.success(`Promoted to ${role}`); fetchRoomInfo(); }
  };

  const demoteUser = async (userId) => {
    const res = await apiPostJson('/roles/demote', { user_id: userId });
    if (res.ok) { toast.success('Demoted'); fetchRoomInfo(); }
  };

  const startWebinar = async () => { const r = await apiPost('/start'); if (r.ok) { toast.success('LIVE!'); fetchRoomInfo(); } };
  const endWebinar = async () => { const r = await apiPost('/end'); if (r.ok) { toast.success('Ended'); navigate('/karau-meet/webinars'); } };
  const startPractice = async () => { const r = await apiPost('/practice/start'); if (r.ok) { toast.success('Practice started'); fetchRoomInfo(); } };
  const endPractice = async () => { const r = await apiPost('/practice/end'); if (r.ok) { toast.success('Practice ended'); fetchRoomInfo(); } };
  const muteAll = async () => { await apiPost('/controls/mute-all'); toast.success('All muted'); };

  // --- Slide Drive ---
  const changeSlide = (direction) => {
    const newIdx = direction === 'next' ? currentSlide + 1 : Math.max(0, currentSlide - 1);
    setCurrentSlide(newIdx);
    wsRef.current?.send(JSON.stringify({ type: 'slide_change', slide_index: newIdx }));
  };

  // --- Q&A ---
  const fetchQA = async () => {
    try {
      const res = await fetch(`${API}/api/karau/webinar/${webinarId}/qa`);
      if (res.ok) { const d = await res.json(); setQuestions(d.questions || []); }
    } catch {}
  };

  const fetchHandRaises = async () => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/webinar/${webinarId}/hand-raises`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) { const d = await res.json(); setHandRaises(d.hand_raises || []); }
    } catch {}
  };

  const submitQuestion = async () => {
    if (!newQuestion.trim()) return;
    const res = await apiPostJson('/qa/ask', { question: newQuestion, is_anonymous: false });
    if (res.ok) { setNewQuestion(''); fetchQA(); }
  };

  const answerQuestion = async (qId) => {
    if (!answerTexts[qId]?.trim()) return;
    const res = await apiPostJson(`/qa/${qId}/answer`, { answer: answerTexts[qId] });
    if (res.ok) { setAnswerTexts(p => ({ ...p, [qId]: '' })); fetchQA(); }
  };

  const upvoteQuestion = async (qId) => { await apiPost(`/qa/${qId}/upvote`); fetchQA(); };

  const leaveWebinar = () => { cleanup(); navigate('/karau-meet/webinars'); };

  const togglePanel = (panel) => setActivePanel(prev => prev === panel ? null : panel);

  if (loading) {
    return <div className="min-h-screen bg-karau-bg flex items-center justify-center"><Loader2 className="w-8 h-8 text-purple-400 animate-spin" /></div>;
  }
  if (!roomInfo) {
    return <div className="min-h-screen bg-karau-bg flex items-center justify-center"><p className="text-red-400">Unable to join webinar</p></div>;
  }

  const canStream = roomInfo.can_stream_video;
  const canControl = roomInfo.can_control;
  const canDriveSlides = roomInfo.can_drive_slides;
  const isHost = myRole === 'host';
  const isCoord = myRole === 'coordinator';
  const isAttendee = myRole === 'attendee';
  const pendingQs = questions.filter(q => q.status === 'pending');
  const remoteStreamEntries = Object.entries(remoteStreams);

  return (
    <div className="min-h-screen bg-karau-bg flex flex-col" style={{ fontFamily: "'IBM Plex Sans', sans-serif" }} data-testid="webinar-live-room">
      {/* Top Bar */}
      <div className="h-11 bg-karau-card/80 border-b border-white/5 flex items-center justify-between px-4 shrink-0">
        <div className="flex items-center gap-2.5">
          {roomInfo.status === 'live' ? (
            <Badge className="bg-red-500/20 text-red-400 border-red-500/20 animate-pulse text-[10px]" data-testid="live-badge"><Radio className="w-2.5 h-2.5 mr-1" />LIVE</Badge>
          ) : roomInfo.practice_mode ? (
            <Badge className="bg-amber-500/20 text-amber-400 border-amber-500/20 text-[10px]" data-testid="practice-badge"><Shield className="w-2.5 h-2.5 mr-1" />PRACTICE</Badge>
          ) : (
            <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/20 text-[10px]">{roomInfo.status}</Badge>
          )}
          <span className="text-sm font-medium text-white truncate max-w-[300px]">{roomInfo.title}</span>
        </div>
        <div className="flex items-center gap-2">
          <Badge className={`${ROLE_BG[myRole] || ROLE_BG.attendee} ${ROLE_COLORS[myRole]} border text-[10px]`} data-testid="role-badge">
            {isHost && <Crown className="w-2.5 h-2.5 mr-1" />}
            {isCoord && <Clipboard className="w-2.5 h-2.5 mr-1" />}
            {myRole === 'presenter' && <MonitorUp className="w-2.5 h-2.5 mr-1" />}
            {myRole.charAt(0).toUpperCase() + myRole.slice(1)}
          </Badge>
          {roomInfo.org_privacy?.has_org_domains && (
            <Badge className={`text-[9px] border ${roomInfo.is_internal
              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
              : 'bg-orange-500/10 text-orange-400 border-orange-500/20'}`}
              data-testid="attendee-type-badge">
              {roomInfo.is_internal
                ? <><Building2 className="w-2.5 h-2.5 mr-0.5" />Internal</>
                : <><UserX className="w-2.5 h-2.5 mr-0.5" />External</>}
            </Badge>
          )}
          <Button variant="destructive" size="sm" onClick={leaveWebinar} className="h-7 px-2 text-[11px] rounded-lg" data-testid="leave-webinar-btn">
            <Phone className="w-3 h-3 mr-1 rotate-[135deg]" />Leave
          </Button>
        </div>
      </div>

      {/* Main */}
      <div className="flex flex-1 overflow-hidden">
        {/* Video Stage */}
        <div className="flex-1 flex flex-col">
          <div className="flex-1 p-2 flex gap-2" data-testid="video-stage">
            {/* Presentation slides (main area when uploaded) */}
            {showSlides && (
              <div className="flex-1 relative rounded-xl overflow-hidden">
                <SlideRenderer
                  webinarId={webinarId}
                  currentSlide={currentSlide}
                  onSlideChange={(idx) => { setCurrentSlide(idx); wsRef.current?.send(JSON.stringify({ type: 'slide_change', slide_index: idx })); }}
                  canDrive={canDriveSlides}
                  ws={wsRef}
                />
              </div>
            )}

            {/* Video area (side when slides shown, full when not) */}
            <div className={`relative rounded-xl overflow-hidden bg-karau-card/40 border transition-all ${showSlides ? 'w-56 shrink-0' : 'flex-1'} ${speakerDetection.speakers['__local__']?.speaking ? 'border-2' : 'border-white/5'}`}
              style={speakerDetection.speakers['__local__']?.speaking ? { borderColor: speakerDetection.speakers['__local__']?.color } : {}}>
              {canStream ? (
                <>
                  <video ref={localVideoRef} autoPlay muted playsInline className="w-full h-full object-cover" data-testid="local-video" />
                  {!isCamOn && (
                    <div className="absolute inset-0 flex items-center justify-center bg-karau-card/80">
                      <div className={`${showSlides ? 'w-10 h-10' : 'w-16 h-16'} rounded-full bg-purple-500/20 flex items-center justify-center`}>
                        <span className={`${showSlides ? 'text-lg' : 'text-2xl'} font-bold text-purple-400`}>{roomInfo.host_name?.[0] || 'H'}</span>
                      </div>
                    </div>
                  )}
                  <div className="absolute bottom-1 left-1 bg-black/60 backdrop-blur-sm rounded px-1 py-0.5">
                    <span className="text-[8px] text-white flex items-center gap-0.5">
                      {isHost && <Crown className="w-2 h-2 text-amber-400" />}
                      {isCoord && <Clipboard className="w-2 h-2 text-cyan-400" />}
                      You
                    </span>
                  </div>
                </>
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <div className="text-center p-3">
                    <div className={`${showSlides ? 'w-12 h-12' : 'w-20 h-20'} rounded-full bg-purple-500/10 border border-purple-500/20 flex items-center justify-center mx-auto mb-2`}>
                      <Radio className={`${showSlides ? 'w-6 h-6' : 'w-10 h-10'} text-purple-400/60`} />
                    </div>
                    {!showSlides && <p className="text-white font-medium text-sm">{roomInfo.title}</p>}
                    <p className="text-[9px] text-karau-muted mt-0.5">
                      {roomInfo.status === 'live' ? roomInfo.host_name : 'Waiting...'}
                    </p>
                    {isCoord && !showSlides && (
                      <Badge className="mt-1 bg-cyan-500/10 text-cyan-400 border-cyan-500/20 text-[9px]">
                        <Clipboard className="w-2 h-2 mr-0.5" />Coordinator
                      </Badge>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Remote streams sidebar */}
            {remoteStreamEntries.length > 0 && (
              <div className="w-36 flex flex-col gap-1 overflow-y-auto shrink-0">
                {remoteStreamEntries.map(([uid, { stream, name }]) => (
                  <RemoteVideo key={uid} stream={stream} name={name} userId={uid}
                    isSpeaking={speakerDetection.speakers[uid]?.speaking}
                    speakerColor={speakerDetection.speakers[uid]?.color} />
                ))}
              </div>
            )}
          </div>

          {/* Live Caption Overlay */}
          {liveTranscription.captions.length > 0 && (
            <div className="px-4 py-1.5 bg-black/70 backdrop-blur-sm border-t border-white/5" data-testid="live-captions-bar">
              <div className="flex items-center gap-2">
                <Captions className="w-3 h-3 text-emerald-400 shrink-0" />
                <div className="flex-1 truncate">
                  {(() => {
                    const last = liveTranscription.captions[liveTranscription.captions.length - 1];
                    return (
                      <p className="text-[11px] text-white/90 truncate">
                        {last?.speaker && (
                          <span className="font-semibold mr-1" style={{ color: last.speakerColor }} data-testid="speaker-label">
                            {last.speaker}:
                          </span>
                        )}
                        {last?.text}
                      </p>
                    );
                  })()}
                </div>
                {liveTranscription.sourceLanguage !== liveTranscription.displayLanguage && (
                  <Badge className="bg-violet-500/10 text-violet-400 border-violet-500/20 text-[7px] shrink-0" data-testid="translation-badge">
                    {CAPTION_LANGUAGES[liveTranscription.sourceLanguage]?.substring(0, 2)}{' > '}
                    {CAPTION_LANGUAGES[liveTranscription.displayLanguage]?.substring(0, 2)}
                  </Badge>
                )}
              </div>
            </div>
          )}

          {/* Active Speaker Indicator */}
          {speakerDetection.activeSpeaker && (
            <div className="absolute top-12 left-3 flex items-center gap-1.5 bg-black/50 backdrop-blur-sm rounded-full px-2 py-0.5" data-testid="active-speaker-indicator">
              <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ backgroundColor: speakerDetection.activeSpeaker.color }} />
              <span className="text-[9px] text-white/80">{speakerDetection.activeSpeaker.name}</span>
            </div>
          )}

          {/* Language Picker Dropdown */}
          {showLangPicker && (
            <div className="px-4 py-2 bg-karau-card/90 backdrop-blur-md border-t border-white/5" data-testid="language-picker-panel">
              <div className="flex gap-6 items-start">
                <div>
                  <p className="text-[9px] text-slate-400 uppercase tracking-wider mb-1.5">Speaker Language</p>
                  <div className="flex flex-wrap gap-1">
                    {Object.entries(CAPTION_LANGUAGES).map(([code, name]) => (
                      <button key={`src-${code}`} onClick={() => liveTranscription.setSourceLanguage(code)}
                        data-testid={`src-lang-${code}`}
                        className={`px-2 py-0.5 rounded text-[9px] transition-colors ${liveTranscription.sourceLanguage === code
                          ? 'bg-purple-500/30 text-purple-300 border border-purple-500/30'
                          : 'bg-white/5 text-slate-400 hover:text-white hover:bg-white/10 border border-transparent'
                        }`}>{name}</button>
                    ))}
                  </div>
                </div>
                <div>
                  <p className="text-[9px] text-slate-400 uppercase tracking-wider mb-1.5">Display Language</p>
                  <div className="flex flex-wrap gap-1">
                    {Object.entries(CAPTION_LANGUAGES).map(([code, name]) => (
                      <button key={`dsp-${code}`} onClick={() => liveTranscription.setDisplayLanguage(code)}
                        data-testid={`dsp-lang-${code}`}
                        className={`px-2 py-0.5 rounded text-[9px] transition-colors ${liveTranscription.displayLanguage === code
                          ? 'bg-emerald-500/30 text-emerald-300 border border-emerald-500/30'
                          : 'bg-white/5 text-slate-400 hover:text-white hover:bg-white/10 border border-transparent'
                        }`}>{name}</button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Bottom Controls */}
          <div className="h-14 bg-karau-card/60 border-t border-white/5 flex items-center justify-center gap-1.5 px-4 shrink-0" data-testid="webinar-controls">
            {canStream && (
              <>
                <CtrlBtn on={isMicOn} onClick={toggleMic} icon={isMicOn ? Mic : MicOff} testId="mic-toggle" />
                <CtrlBtn on={isCamOn} onClick={toggleCam} icon={isCamOn ? Video : VideoOff} testId="cam-toggle" />
                {noiseCancellation.isSupported && (
                  <div className="relative">
                    <CtrlBtn on={noiseCancellation.enabled} onClick={toggleNoiseCancellation} icon={AudioLines} testId="noise-cancel-toggle" color={noiseCancellation.enabled ? 'emerald' : undefined} />
                    {noiseCancellation.enabled && (
                      <span className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                    )}
                  </div>
                )}
              </>
            )}
            {isAttendee && <CtrlBtn on={isHandRaised} onClick={toggleHandRaise} icon={Hand} testId="hand-raise-btn" color="amber" />}
            <div className="relative">
              <CtrlBtn on={liveTranscription.active} onClick={toggleLiveCaptions} icon={Captions} testId="captions-toggle" color={liveTranscription.active ? 'emerald' : undefined} />
              {liveTranscription.active && (
                <span className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              )}
            </div>
            {/* Language picker toggle */}
            <Button variant="ghost" size="sm" onClick={() => setShowLangPicker(!showLangPicker)} data-testid="lang-picker-toggle"
              className={`h-9 px-2 rounded-full text-[10px] ${showLangPicker ? 'bg-violet-500/20 text-violet-400' : 'bg-white/10 text-white hover:bg-white/15'}`}>
              <Globe className="w-3.5 h-3.5 mr-0.5" />
              {liveTranscription.sourceLanguage.toUpperCase()}
              {liveTranscription.sourceLanguage !== liveTranscription.displayLanguage && (
                <span className="text-emerald-400 ml-0.5">{liveTranscription.displayLanguage.toUpperCase()}</span>
              )}
            </Button>
            <CtrlBtn on={activePanel === 'qa'} onClick={() => togglePanel('qa')} icon={MessageCircleQuestion} testId="qa-toggle" badge={pendingQs.length || null} />
            <CtrlBtn on={activePanel === 'ai'} onClick={() => togglePanel('ai')} icon={Brain} testId="ai-toggle" />
            {canControl && (
              <>
                <CtrlBtn on={activePanel === 'participants'} onClick={() => togglePanel('participants')} icon={Users} testId="participants-toggle" />
                <CtrlBtn on={activePanel === 'controls'} onClick={() => togglePanel('controls')} icon={Settings} testId="controls-toggle" />
              </>
            )}
            <div className="w-px h-6 bg-white/10 mx-1" />
            {/* Host-only session controls */}
            {isHost && roomInfo.status === 'scheduled' && !roomInfo.practice_mode && (
              <>
                <Button size="sm" onClick={startPractice} className="h-8 px-2.5 text-[11px] bg-amber-500/80 hover:bg-amber-400 rounded-lg" data-testid="start-practice-btn">
                  <Shield className="w-3 h-3 mr-1" />Practice
                </Button>
                <Button size="sm" onClick={startWebinar} className="h-8 px-2.5 text-[11px] bg-emerald-500/80 hover:bg-emerald-400 rounded-lg" data-testid="go-live-btn">
                  <Play className="w-3 h-3 mr-1" />Go Live
                </Button>
              </>
            )}
            {isHost && roomInfo.practice_mode && (
              <>
                <Button size="sm" onClick={endPractice} className="h-8 px-2.5 text-[11px] bg-slate-500/80 hover:bg-slate-400 rounded-lg" data-testid="end-practice-btn">End Practice</Button>
                <Button size="sm" onClick={startWebinar} className="h-8 px-2.5 text-[11px] bg-emerald-500/80 hover:bg-emerald-400 rounded-lg" data-testid="go-live-from-practice-btn">
                  <Play className="w-3 h-3 mr-1" />Go Live
                </Button>
              </>
            )}
            {isHost && roomInfo.status === 'live' && (
              <>
                {liveTranscription.fullTranscript.trim() && (
                  <Button size="sm" onClick={saveTranscript} className="h-8 px-2.5 text-[11px] bg-violet-500/80 hover:bg-violet-400 rounded-lg" data-testid="save-transcript-btn">
                    <Save className="w-3 h-3 mr-1" />Save Transcript
                  </Button>
                )}
                <Button size="sm" variant="destructive" onClick={endWebinar} className="h-8 px-2.5 text-[11px] rounded-lg" data-testid="end-webinar-btn">
                  <Square className="w-3 h-3 mr-1" />End
                </Button>
              </>
            )}
          </div>
        </div>

        {/* Side Panel */}
        {activePanel && (
          <div className="w-72 bg-karau-card/60 border-l border-white/5 flex flex-col shrink-0 overflow-hidden" data-testid="side-panel">
            {activePanel === 'qa' && <QAPanel questions={questions} pendingQs={pendingQs} newQuestion={newQuestion} setNewQuestion={setNewQuestion} submitQuestion={submitQuestion} answerTexts={answerTexts} setAnswerTexts={setAnswerTexts} answerQuestion={answerQuestion} upvoteQuestion={upvoteQuestion} canControl={canControl} myRole={myRole} />}
            {activePanel === 'participants' && canControl && <ParticipantsPanel handRaises={handRaises} activeRoles={activeRoles} promoteUser={promoteUser} demoteUser={demoteUser} isHost={isHost} roomInfo={roomInfo} onGrantPermission={grantGuestPermission} onRevokePermission={revokeGuestPermission} />}
            {activePanel === 'ai' && <AIAssistantPanel meetingId={webinarId} webinarId={webinarId} engagementData={engagementData} />}
            {activePanel === 'controls' && canControl && <ControlsPanel muteAll={muteAll} roomInfo={roomInfo} />}
          </div>
        )}
      </div>
    </div>
  );
};

// --- Sub Components ---

const CtrlBtn = ({ on, onClick, icon: Icon, testId, color, badge }) => (
  <div className="relative">
    <Button variant="ghost" size="sm" onClick={onClick} data-testid={testId}
      className={`h-9 w-9 rounded-full ${on ? (color === 'amber' ? 'bg-amber-500/20 text-amber-400' : color === 'emerald' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-purple-500/20 text-purple-400') : 'bg-white/10 text-white hover:bg-white/15'}`}>
      <Icon className="w-4 h-4" />
    </Button>
    {badge && <span className="absolute -top-0.5 -right-0.5 w-3.5 h-3.5 rounded-full bg-red-500 text-[7px] text-white flex items-center justify-center">{badge}</span>}
  </div>
);

const RemoteVideo = ({ stream, name, userId, isSpeaking, speakerColor }) => {
  const ref = useRef(null);
  useEffect(() => { if (ref.current && stream) ref.current.srcObject = stream; }, [stream]);
  return (
    <div className={`relative rounded-lg overflow-hidden bg-karau-card/60 border aspect-video transition-all ${isSpeaking ? 'border-2' : 'border-white/5'}`}
      style={isSpeaking ? { borderColor: speakerColor } : {}}
      data-testid={`remote-${userId}`}>
      <video ref={ref} autoPlay playsInline className="w-full h-full object-cover" />
      <div className="absolute bottom-1 left-1 bg-black/60 backdrop-blur-sm rounded px-1 py-0.5 flex items-center gap-1">
        {isSpeaking && <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ backgroundColor: speakerColor }} />}
        <span className="text-[8px] text-white">{name}</span>
      </div>
    </div>
  );
};

const QAPanel = ({ questions, pendingQs, newQuestion, setNewQuestion, submitQuestion, answerTexts, setAnswerTexts, answerQuestion, upvoteQuestion, canControl, myRole }) => (
  <div className="flex-1 flex flex-col overflow-hidden">
    <div className="p-2.5 border-b border-white/5">
      <h3 className="text-xs font-semibold text-white flex items-center gap-1.5">
        <MessageCircleQuestion className="w-3.5 h-3.5 text-amber-400" />Q&A ({pendingQs.length} pending)
      </h3>
    </div>
    <div className="flex-1 overflow-y-auto p-2 space-y-1.5">
      {questions.length === 0 ? (
        <p className="text-[10px] text-slate-500 text-center py-6">No questions yet</p>
      ) : questions.map(q => (
        <div key={q.question_id} className={`p-2 rounded-lg ${q.status === 'answered' ? 'bg-emerald-500/5 border border-emerald-500/10' : 'bg-karau-bg/40'}`}>
          <p className="text-[11px] text-white leading-tight">{q.question}</p>
          <div className="flex items-center gap-2 mt-1 text-[9px] text-slate-500">
            <span>{q.asked_by}</span>
            <button onClick={() => upvoteQuestion(q.question_id)} className="flex items-center gap-0.5 hover:text-purple-400"><ThumbsUp className="w-2 h-2" />{q.upvotes}</button>
            <Badge className={`text-[7px] ${q.status === 'answered' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'}`}>{q.status}</Badge>
          </div>
          {q.answer && <div className="mt-1 p-1 bg-emerald-500/5 rounded text-[9px] text-emerald-300"><b>A:</b> {q.answer}</div>}
          {canControl && q.status === 'pending' && (
            <div className="flex gap-1 mt-1">
              <Input value={answerTexts[q.question_id] || ''} onChange={e => setAnswerTexts(p => ({ ...p, [q.question_id]: e.target.value }))}
                placeholder="Answer..." className="bg-karau-card border-white/10 text-white text-[9px] h-5 rounded" />
              <Button size="sm" onClick={() => answerQuestion(q.question_id)} className="h-5 w-5 p-0 bg-emerald-500/80 rounded"><Send className="w-2 h-2" /></Button>
            </div>
          )}
        </div>
      ))}
    </div>
    <div className="p-2 border-t border-white/5">
      <div className="flex gap-1">
        <Input value={newQuestion} onChange={e => setNewQuestion(e.target.value)} placeholder="Ask a question..."
          onKeyDown={e => e.key === 'Enter' && submitQuestion()} className="bg-karau-bg/60 border-white/10 text-white text-[10px] h-7 rounded-lg" data-testid="question-input" />
        <Button size="sm" onClick={submitQuestion} className="h-7 px-2 bg-purple-500/80 rounded-lg" data-testid="submit-question-btn"><Send className="w-3 h-3" /></Button>
      </div>
    </div>
  </div>
);

const ParticipantsPanel = ({ handRaises, activeRoles, promoteUser, demoteUser, isHost, roomInfo, onGrantPermission, onRevokePermission }) => (
  <div className="flex-1 overflow-y-auto p-2.5 space-y-3">
    <h3 className="text-xs font-semibold text-white flex items-center gap-1.5"><Users className="w-3.5 h-3.5 text-emerald-400" />Participants</h3>

    {/* Org Privacy Status */}
    {roomInfo?.org_privacy?.has_org_domains && (
      <div className="p-1.5 bg-karau-bg/40 rounded-lg border border-white/5" data-testid="org-privacy-status">
        <div className="flex items-center gap-1.5 mb-1">
          <Building2 className="w-3 h-3 text-violet-400" />
          <span className="text-[9px] text-violet-400 font-semibold uppercase tracking-wider">Org Privacy Active</span>
        </div>
        <div className="text-[8px] text-slate-500 space-y-0.5">
          <p className="flex items-center gap-1">
            {roomInfo.org_privacy.internal_only_docs ? <ShieldCheck className="w-2 h-2 text-emerald-400" /> : <ShieldOff className="w-2 h-2 text-orange-400" />}
            Docs: {roomInfo.org_privacy.internal_only_docs ? 'Internal only' : 'Open'}
          </p>
          <p className="flex items-center gap-1">
            {roomInfo.org_privacy.external_download_blocked ? <ShieldCheck className="w-2 h-2 text-emerald-400" /> : <ShieldOff className="w-2 h-2 text-orange-400" />}
            External download: {roomInfo.org_privacy.external_download_blocked ? 'Blocked' : 'Allowed'}
          </p>
        </div>
      </div>
    )}

    {handRaises.length > 0 && (
      <div className="space-y-1">
        <p className="text-[9px] text-amber-400 font-semibold uppercase tracking-wider flex items-center gap-1"><Hand className="w-2.5 h-2.5" />Raised Hands ({handRaises.length})</p>
        {handRaises.map(h => (
          <div key={h.user_id} className="flex items-center justify-between p-1.5 bg-amber-500/5 rounded-lg border border-amber-500/10" data-testid={`hand-${h.user_id}`}>
            <span className="text-[10px] text-white">{h.name}</span>
            <div className="flex gap-0.5">
              {isHost && <Button size="sm" onClick={() => promoteUser(h.user_id, 'coordinator')} className="h-5 px-1.5 text-[8px] bg-cyan-500/80 rounded" data-testid={`promote-coord-${h.user_id}`}>Coord</Button>}
              <Button size="sm" onClick={() => promoteUser(h.user_id, 'presenter')} className="h-5 px-1.5 text-[8px] bg-emerald-500/80 rounded" data-testid={`promote-presenter-${h.user_id}`}>Presenter</Button>
              <Button size="sm" onClick={() => promoteUser(h.user_id, 'panelist')} className="h-5 px-1.5 text-[8px] bg-blue-500/80 rounded" data-testid={`promote-panelist-${h.user_id}`}>Panel</Button>
            </div>
          </div>
        ))}
      </div>
    )}
    <div className="space-y-1">
      <p className="text-[9px] text-purple-400 font-semibold uppercase tracking-wider">Active Roles</p>
      {Object.entries(activeRoles).length === 0 ? (
        <p className="text-[9px] text-slate-500 py-2">No promoted participants</p>
      ) : Object.entries(activeRoles).map(([uid, info]) => (
        <div key={uid} className={`flex items-center justify-between p-1.5 rounded-lg border ${ROLE_BG[info.role] || 'bg-white/5 border-white/10'}`} data-testid={`role-${uid}`}>
          <div className="flex items-center gap-1.5">
            <span className="text-[10px] text-white">{uid.substring(0, 12)}</span>
            <Badge className={`text-[7px] ${ROLE_COLORS[info.role]}`}>{info.role}</Badge>
          </div>
          <div className="flex items-center gap-0.5">
            {isHost && roomInfo?.org_privacy?.has_org_domains && (
              <>
                <Button size="sm" variant="ghost" onClick={() => onGrantPermission?.(uid, 'upload')}
                  className="h-5 px-1 text-emerald-400 hover:bg-emerald-500/10" data-testid={`grant-upload-${uid}`} title="Grant upload">
                  <FileUp className="w-2.5 h-2.5" />
                </Button>
                <Button size="sm" variant="ghost" onClick={() => onGrantPermission?.(uid, 'download')}
                  className="h-5 px-1 text-blue-400 hover:bg-blue-500/10" data-testid={`grant-download-${uid}`} title="Grant download">
                  <FileDown className="w-2.5 h-2.5" />
                </Button>
              </>
            )}
            <Button size="sm" variant="ghost" onClick={() => demoteUser(uid)} className="h-5 px-1 text-red-400 hover:bg-red-500/10" data-testid={`demote-${uid}`}>
              <UserMinus className="w-2.5 h-2.5" />
            </Button>
          </div>
        </div>
      ))}
    </div>
  </div>
);

const ControlsPanel = ({ muteAll, roomInfo }) => (
  <div className="flex-1 overflow-y-auto p-2.5 space-y-2">
    <h3 className="text-xs font-semibold text-white flex items-center gap-1.5"><Settings className="w-3.5 h-3.5 text-violet-400" />Controls</h3>
    <button onClick={muteAll} className="w-full flex items-center gap-2 p-2 bg-karau-bg/40 rounded-lg hover:bg-white/5 transition-colors" data-testid="mute-all-control">
      <MicOff className="w-3.5 h-3.5 text-red-400" /><span className="text-[10px] text-slate-300">Mute All</span>
    </button>
    <div className="p-2 bg-karau-bg/40 rounded-lg space-y-1">
      <p className="text-[9px] text-karau-muted">Settings</p>
      <div className="text-[9px] text-slate-400 space-y-0.5">
        <p>Chat: {roomInfo.settings?.chat_enabled ? 'On' : 'Off'}</p>
        <p>Q&A: {roomInfo.settings?.q_and_a_enabled ? 'On' : 'Off'}</p>
        <p>Attendee Video: {roomInfo.settings?.attendee_video ? 'On' : 'Off'}</p>
        <p>Attendee Audio: {roomInfo.settings?.attendee_audio ? 'On' : 'Off'}</p>
      </div>
    </div>
  </div>
);

export default WebinarLiveRoom;
