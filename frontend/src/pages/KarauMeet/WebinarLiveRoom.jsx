import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { toast } from 'sonner';
import {
  Radio, Users, Mic, MicOff, Video, VideoOff, MonitorUp,
  Hand, MessageCircleQuestion, Play, Square, Settings,
  Send, ThumbsUp, Loader2, Crown, UserPlus, UserMinus,
  Shield, Phone, Clipboard, ChevronLeft, ChevronRight,
  AudioLines, Captions, Save, Globe, ChevronDown as ChevDown,
  Building2, UserX, FileUp, FileDown, ShieldCheck, ShieldOff, Brain, Sparkles, Eye, PenLine,
  SmilePlus, Trophy, Headphones, Clapperboard, QrCode, BarChart3, BrainCircuit
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { useTranslation } from '@/utils/i18n';
import SlideRenderer from '@/components/KarauMeet/SlideRenderer';
import { useNoiseCancellation } from '@/hooks/useNoiseCancellation';
import { useLiveTranscription, CAPTION_LANGUAGES } from '@/hooks/useLiveTranscription';
import { useSpeakerDetection } from '@/hooks/useSpeakerDetection';
import { useSpatialAudio } from '@/hooks/useSpatialAudio';
import { useDirectorMode } from '@/hooks/useDirectorMode';
import { useGhostBooking } from '@/hooks/useGhostBooking';
import AIAssistantPanel from '@/components/KarauMeet/AIAssistantPanel';
import EnhancedWhiteboard from '@/components/KarauMeet/EnhancedWhiteboard';
import EmojiReactions from '@/components/KarauMeet/EmojiReactions';
import LeaderboardPanel from '@/components/KarauMeet/LeaderboardPanel';
import DirectorModePanel from '@/components/KarauMeet/DirectorModePanel';
import QRCodePanel from '@/components/KarauMeet/QRCodePanel';
import GhostBookingAlert from '@/components/KarauMeet/GhostBookingAlert';
import SentimentDashboard from '@/components/KarauMeet/SentimentDashboard';
import CopilotPanel from '@/components/KarauMeet/CopilotPanel';

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

  // Eye Contact Correction
  const [eyeContactOn, setEyeContactOn] = useState(false);

  // Whiteboard
  const [showWhiteboard, setShowWhiteboard] = useState(false);

  // Language picker
  const [showLangPicker, setShowLangPicker] = useState(false);

  // Engagement data
  const [engagementData, setEngagementData] = useState(null);

  // AI Coach
  const [coachTips, setCoachTips] = useState([]);
  const [showCoach, setShowCoach] = useState(false);
  const speakingStartRef = useRef(null);
  const meetingStartRef = useRef(Date.now());

  // Noise Cancellation
  const noiseCancellation = useNoiseCancellation();

  // Live Transcription
  const liveTranscription = useLiveTranscription();

  // Speaker Detection
  const speakerDetection = useSpeakerDetection();

  // Spatial Audio
  const spatialAudio = useSpatialAudio();

  // Gamification
  const [showReactions, setShowReactions] = useState(false);

  // Director Mode
  const directorMode = useDirectorMode(webinarId, speakerDetection, remoteStreams);

  // Ghost Booking Prevention
  const ghostBooking = useGhostBooking(webinarId);

  // Active Speaker Framing - track which user is "main stage"
  const [mainStageUserId, setMainStageUserId] = useState(null);
  const mainStageSwitchRef = useRef(null);

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

  // AI Video Framing: auto-promote active speaker to main stage with debounce
  useEffect(() => {
    const speaker = speakerDetection.activeSpeaker;
    if (!speaker) return;
    // Don't switch for local user or same user
    if (speaker.userId === '__local__' || speaker.userId === mainStageUserId) return;
    // Debounce: only switch after 1.5s of continuous speaking
    if (mainStageSwitchRef.current) clearTimeout(mainStageSwitchRef.current);
    mainStageSwitchRef.current = setTimeout(() => {
      setMainStageUserId(speaker.userId);
    }, 1500);
    return () => { if (mainStageSwitchRef.current) clearTimeout(mainStageSwitchRef.current); };
  }, [speakerDetection.activeSpeaker]);

  // Spatial Audio: connect/update remote streams with tile positions
  useEffect(() => {
    if (!spatialAudio.enabled) return;
    const entries = Object.entries(remoteStreams);
    const total = entries.length;
    entries.forEach(([uid, { stream }], idx) => {
      // Distribute positions across horizontal space (-1 to 1)
      const x = total > 1 ? ((idx / (total - 1)) * 2 - 1) : 0;
      spatialAudio.connectStream(uid, stream, { x, y: 0 });
    });
  }, [remoteStreams, spatialAudio.enabled]);
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
    spatialAudio.cleanup();
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

  // AI Coach - auto-request tips every 60s for host/presenter
  useEffect(() => {
    if (!webinarId || !roomInfo?.can_stream_video) return;
    const interval = setInterval(async () => {
      const captions = liveTranscription.captions;
      if (captions.length === 0) return;
      const recentText = captions.slice(-5).map(c => c.original || c.text).join(' ');
      const speakingDuration = speakingStartRef.current ? (Date.now() - speakingStartRef.current) / 1000 : 0;
      const totalDuration = (Date.now() - meetingStartRef.current) / 1000;
      const token = localStorage.getItem('token');
      try {
        const res = await fetch(`${API}/api/karau-features/ai-coach/tip`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify({
            meeting_id: webinarId,
            transcript_segment: recentText,
            speaker: 'You',
            speaking_duration_seconds: speakingDuration,
            total_meeting_seconds: totalDuration,
            engagement_score: engagementData?.engagement_score || 5,
            participant_count: Object.keys(remoteStreams).length + 1
          })
        });
        if (res.ok) {
          const tip = await res.json();
          if (tip.tip) setCoachTips(prev => [...prev.slice(-5), { ...tip, ts: Date.now() }]);
        }
      } catch {}
    }, 60000);
    return () => clearInterval(interval);
  }, [webinarId, roomInfo?.can_stream_video]);

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

      {/* Emoji Reactions Overlay */}
      <EmojiReactions webinarId={webinarId} senderName={roomInfo.host_name || 'User'} show={showReactions} onToggle={() => setShowReactions(!showReactions)} />

      {/* Main */}
      <div className="flex flex-1 overflow-hidden">
        {/* Video Stage */}
        <div className="flex-1 flex flex-col">
          <div className="flex-1 p-2 flex gap-2" data-testid="video-stage">
            {/* Enhanced Whiteboard (replaces video stage when active) */}
            {showWhiteboard ? (
              <div className="flex-1" data-testid="whiteboard-container">
                <EnhancedWhiteboard meetingId={webinarId} onClose={() => setShowWhiteboard(false)} />
              </div>
            ) : (
            <>
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

            {/* Video area with Active Speaker Framing */}
            <div className={`relative rounded-xl overflow-hidden bg-karau-card/40 border transition-all duration-500 ${showSlides ? 'w-56 shrink-0' : 'flex-1'} ${speakerDetection.speakers['__local__']?.speaking ? 'border-2' : 'border-white/5'}`}
              style={speakerDetection.speakers['__local__']?.speaking ? { borderColor: speakerDetection.speakers['__local__']?.color } : {}}>

              {/* Main Stage: Show active speaker's remote feed if framed */}
              {!showSlides && mainStageUserId && remoteStreams[mainStageUserId] && (
                <MainStageVideo
                  stream={remoteStreams[mainStageUserId].stream}
                  name={remoteStreams[mainStageUserId].name}
                  color={speakerDetection.speakers[mainStageUserId]?.color}
                  data-testid="main-stage-video"
                />
              )}

              {/* Local video (shows as main if no active remote speaker, or as PiP overlay) */}
              {canStream ? (
                <div className={mainStageUserId && remoteStreams[mainStageUserId] && !showSlides
                  ? 'absolute bottom-2 right-2 w-32 h-24 rounded-lg overflow-hidden border-2 border-white/20 shadow-xl z-10 transition-all duration-500'
                  : 'w-full h-full'}>
                  <video ref={localVideoRef} autoPlay muted playsInline className="w-full h-full object-cover"
                style={eyeContactOn ? {
                  transform: 'scaleX(-1) perspective(800px) rotateY(2deg) translateY(-2%)',
                  filter: 'contrast(1.02) brightness(1.01)'
                } : { transform: 'scaleX(-1)' }}
                data-testid="local-video" />
                  {!isCamOn && (
                    <div className="absolute inset-0 flex items-center justify-center bg-karau-card/80">
                      <div className={`${showSlides ? 'w-10 h-10' : mainStageUserId ? 'w-8 h-8' : 'w-16 h-16'} rounded-full bg-purple-500/20 flex items-center justify-center`}>
                        <span className={`${showSlides ? 'text-lg' : mainStageUserId ? 'text-sm' : 'text-2xl'} font-bold text-purple-400`}>{roomInfo.host_name?.[0] || 'H'}</span>
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
                </div>
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

            {/* Remote streams sidebar (excludes main-stage speaker) */}
            {remoteStreamEntries.length > 0 && (
              <div className="w-36 flex flex-col gap-1 overflow-y-auto shrink-0">
                {remoteStreamEntries
                  .filter(([uid]) => uid !== mainStageUserId || showSlides)
                  .map(([uid, { stream, name }]) => (
                  <RemoteVideo key={uid} stream={stream} name={name} userId={uid}
                    isSpeaking={speakerDetection.speakers[uid]?.speaking}
                    speakerColor={speakerDetection.speakers[uid]?.color}
                    isMainStage={uid === mainStageUserId}
                    onPromoteToStage={() => setMainStageUserId(uid)} />
                ))}
              </div>
            )}
            </>
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
                    {CA