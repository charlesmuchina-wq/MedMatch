import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { toast } from 'sonner';
import {
  Radio, Users, Mic, MicOff, Video, VideoOff, MonitorUp,
  Hand, MessageCircleQuestion, Play, Square, Settings,
  ChevronUp, ChevronDown, Send, ThumbsUp, X, Loader2,
  Crown, UserPlus, UserMinus, Shield, Phone
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { useTranslation } from '@/utils/i18n';

const API = process.env.REACT_APP_BACKEND_URL;
const WS_URL = API.replace('https://', 'wss://').replace('http://', 'ws://');

const WebinarLiveRoom = () => {
  const { webinarId } = useParams();
  const [searchParams] = useSearchParams();
  const regId = searchParams.get('reg');
  const { t } = useTranslation();
  const navigate = useNavigate();

  // Room state
  const [roomInfo, setRoomInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [myRole, setMyRole] = useState('attendee');

  // Media state
  const [isMicOn, setIsMicOn] = useState(false);
  const [isCamOn, setIsCamOn] = useState(false);
  const [isScreenSharing, setIsScreenSharing] = useState(false);
  const [isHandRaised, setIsHandRaised] = useState(false);

  // Panels
  const [showQA, setShowQA] = useState(false);
  const [showParticipants, setShowParticipants] = useState(false);
  const [showControls, setShowControls] = useState(false);

  // Q&A
  const [questions, setQuestions] = useState([]);
  const [newQuestion, setNewQuestion] = useState('');
  const [answerTexts, setAnswerTexts] = useState({});

  // Participants & hands
  const [handRaises, setHandRaises] = useState([]);
  const [activeRoles, setActiveRoles] = useState({});
  const [attendeeCount, setAttendeeCount] = useState(0);

  // Media refs
  const localVideoRef = useRef(null);
  const localStreamRef = useRef(null);
  const wsRef = useRef(null);

  // Fetch room info and determine permissions
  useEffect(() => {
    fetchRoomInfo();
    const interval = setInterval(() => { fetchQA(); fetchHandRaises(); }, 5000);
    return () => clearInterval(interval);
  }, [webinarId]);

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
        // Auto-start media if host/presenter
        if (data.can_stream_video) {
          startLocalMedia(true, true);
        }
      } else if (res.status === 403) {
        toast.error('Practice session in progress');
        navigate(-1);
      }
    } catch (e) { console.error('Room info error:', e); }
    setLoading(false);
  };

  const fetchQA = async () => {
    try {
      const res = await fetch(`${API}/api/karau/webinar/${webinarId}/qa`);
      if (res.ok) { const d = await res.json(); setQuestions(d.questions || []); }
    } catch {}
  };

  const fetchHandRaises = async () => {
    if (myRole !== 'host') return;
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/webinar/${webinarId}/hand-raises`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) { const d = await res.json(); setHandRaises(d.hand_raises || []); }
    } catch {}
  };

  const startLocalMedia = async (video, audio) => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video, audio });
      localStreamRef.current = stream;
      if (localVideoRef.current) localVideoRef.current.srcObject = stream;
      setIsCamOn(video);
      setIsMicOn(audio);
    } catch (e) {
      console.error('Media error:', e);
      toast.error('Camera/microphone access denied');
    }
  };

  const toggleMic = () => {
    if (!localStreamRef.current) return;
    const track = localStreamRef.current.getAudioTracks()[0];
    if (track) {
      track.enabled = !track.enabled;
      setIsMicOn(track.enabled);
    }
  };

  const toggleCam = () => {
    if (!localStreamRef.current) return;
    const track = localStreamRef.current.getVideoTracks()[0];
    if (track) {
      track.enabled = !track.enabled;
      setIsCamOn(track.enabled);
    }
  };

  const toggleHandRaise = async () => {
    const token = localStorage.getItem('token');
    const endpoint = isHandRaised ? 'hand-lower' : 'hand-raise';
    await fetch(`${API}/api/karau/webinar/${webinarId}/${endpoint}`, {
      method: 'POST', headers: { 'Authorization': `Bearer ${token}` }
    });
    setIsHandRaised(!isHandRaised);
  };

  // Host controls
  const promoteUser = async (userId, role = 'presenter') => {
    const token = localStorage.getItem('token');
    const res = await fetch(`${API}/api/karau/webinar/${webinarId}/roles/promote`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ user_id: userId, role })
    });
    if (res.ok) { toast.success(`Promoted to ${role}`); fetchRoomInfo(); }
  };

  const demoteUser = async (userId) => {
    const token = localStorage.getItem('token');
    const res = await fetch(`${API}/api/karau/webinar/${webinarId}/roles/demote`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ user_id: userId })
    });
    if (res.ok) { toast.success('Demoted to attendee'); fetchRoomInfo(); }
  };

  const startWebinar = async () => {
    const token = localStorage.getItem('token');
    const res = await fetch(`${API}/api/karau/webinar/${webinarId}/start`, {
      method: 'POST', headers: { 'Authorization': `Bearer ${token}` }
    });
    if (res.ok) { toast.success('Webinar is LIVE!'); fetchRoomInfo(); }
  };

  const endWebinar = async () => {
    const token = localStorage.getItem('token');
    const res = await fetch(`${API}/api/karau/webinar/${webinarId}/end`, {
      method: 'POST', headers: { 'Authorization': `Bearer ${token}` }
    });
    if (res.ok) { toast.success('Webinar ended'); navigate('/karau-meet/webinars'); }
  };

  const startPractice = async () => {
    const token = localStorage.getItem('token');
    const res = await fetch(`${API}/api/karau/webinar/${webinarId}/practice/start`, {
      method: 'POST', headers: { 'Authorization': `Bearer ${token}` }
    });
    if (res.ok) { toast.success('Practice session started'); fetchRoomInfo(); }
  };

  const endPractice = async () => {
    const token = localStorage.getItem('token');
    const res = await fetch(`${API}/api/karau/webinar/${webinarId}/practice/end`, {
      method: 'POST', headers: { 'Authorization': `Bearer ${token}` }
    });
    if (res.ok) { toast.success('Practice session ended'); fetchRoomInfo(); }
  };

  const muteAll = async () => {
    const token = localStorage.getItem('token');
    await fetch(`${API}/api/karau/webinar/${webinarId}/controls/mute-all`, {
      method: 'POST', headers: { 'Authorization': `Bearer ${token}` }
    });
    toast.success('All attendees muted');
  };

  const submitQuestion = async () => {
    if (!newQuestion.trim()) return;
    const token = localStorage.getItem('token');
    const res = await fetch(`${API}/api/karau/webinar/${webinarId}/qa/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ question: newQuestion, is_anonymous: false })
    });
    if (res.ok) { setNewQuestion(''); fetchQA(); toast.success('Question submitted'); }
  };

  const answerQuestion = async (qId) => {
    if (!answerTexts[qId]?.trim()) return;
    const token = localStorage.getItem('token');
    const res = await fetch(`${API}/api/karau/webinar/${webinarId}/qa/${qId}/answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ answer: answerTexts[qId] })
    });
    if (res.ok) { setAnswerTexts(p => ({ ...p, [qId]: '' })); fetchQA(); }
  };

  const upvoteQuestion = async (qId) => {
    const token = localStorage.getItem('token');
    await fetch(`${API}/api/karau/webinar/${webinarId}/qa/${qId}/upvote`, {
      method: 'POST', headers: { 'Authorization': `Bearer ${token}` }
    });
    fetchQA();
  };

  const leaveWebinar = () => {
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach(t => t.stop());
    }
    navigate('/karau-meet/webinars');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-karau-bg flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-purple-400 animate-spin" />
      </div>
    );
  }

  if (!roomInfo) {
    return (
      <div className="min-h-screen bg-karau-bg flex items-center justify-center">
        <p className="text-red-400">Unable to join webinar</p>
      </div>
    );
  }

  const canStream = roomInfo.can_stream_video;
  const isHost = myRole === 'host';
  const isPresenter = myRole === 'presenter';
  const isPanelist = myRole === 'panelist';
  const isAttendee = myRole === 'attendee';
  const pendingQs = questions.filter(q => q.status === 'pending');

  return (
    <div className="min-h-screen bg-karau-bg flex flex-col" style={{ fontFamily: "'IBM Plex Sans', sans-serif" }} data-testid="webinar-live-room">
      {/* Top Bar */}
      <div className="h-12 bg-karau-card/80 border-b border-white/5 flex items-center justify-between px-4 shrink-0">
        <div className="flex items-center gap-3">
          {roomInfo.status === 'live' ? (
            <Badge className="bg-red-500/20 text-red-400 border-red-500/20 animate-pulse text-[10px]" data-testid="live-badge">
              <Radio className="w-2.5 h-2.5 mr-1" />LIVE
            </Badge>
          ) : roomInfo.practice_mode ? (
            <Badge className="bg-amber-500/20 text-amber-400 border-amber-500/20 text-[10px]" data-testid="practice-badge">
              <Shield className="w-2.5 h-2.5 mr-1" />PRACTICE
            </Badge>
          ) : (
            <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/20 text-[10px]">{roomInfo.status}</Badge>
          )}
          <span className="text-sm font-medium text-white truncate max-w-xs">{roomInfo.title}</span>
        </div>

        <div className="flex items-center gap-2">
          <Badge className="bg-white/5 text-slate-300 border-white/10 text-[10px]" data-testid="role-badge">
            {isHost && <Crown className="w-2.5 h-2.5 mr-1 text-amber-400" />}
            {isPresenter && <MonitorUp className="w-2.5 h-2.5 mr-1 text-emerald-400" />}
            {myRole.charAt(0).toUpperCase() + myRole.slice(1)}
          </Badge>
          <Button variant="destructive" size="sm" onClick={leaveWebinar}
            className="h-7 px-2.5 text-[11px] rounded-lg" data-testid="leave-webinar-btn">
            <Phone className="w-3 h-3 mr-1 rotate-[135deg]" />Leave
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Video Area */}
        <div className="flex-1 flex flex-col">
          {/* Stage */}
          <div className="flex-1 p-3 flex items-center justify-center relative" data-testid="video-stage">
            {canStream ? (
              <div className="relative w-full h-full max-w-4xl">
                <video ref={localVideoRef} autoPlay muted playsInline
                  className="w-full h-full object-cover rounded-2xl bg-karau-card/60" data-testid="local-video" />
                {!isCamOn && (
                  <div className="absolute inset-0 flex items-center justify-center bg-karau-card/80 rounded-2xl">
                    <div className="w-20 h-20 rounded-full bg-purple-500/20 flex items-center justify-center">
                      <span className="text-3xl font-bold text-purple-400">
                        {roomInfo.host_name?.[0] || 'H'}
                      </span>
                    </div>
                  </div>
                )}
                {/* Role label */}
                <div className="absolute bottom-3 left-3 bg-black/60 backdrop-blur-sm rounded-lg px-2 py-1">
                  <span className="text-[10px] text-white font-medium flex items-center gap-1">
                    {isHost && <Crown className="w-2.5 h-2.5 text-amber-400" />}
                    {roomInfo.host_name || 'Host'}
                    {isPresenter && ' (Presenter)'}
                  </span>
                </div>
              </div>
            ) : (
              /* Attendee view - watching stream */
              <div className="w-full h-full max-w-4xl flex items-center justify-center bg-karau-card/40 rounded-2xl border border-white/5">
                <div className="text-center">
                  <div className="w-24 h-24 rounded-full bg-purple-500/10 border border-purple-500/20 flex items-center justify-center mx-auto mb-4">
                    <Radio className="w-12 h-12 text-purple-400/60" />
                  </div>
                  <p className="text-white font-medium">{roomInfo.title}</p>
                  <p className="text-xs text-karau-muted mt-1">
                    {roomInfo.status === 'live' 
                      ? `${t("karauMeet.watchingLive") || "Watching live"} · Hosted by ${roomInfo.host_name}`
                      : roomInfo.status === 'scheduled'
                        ? t("karauMeet.waitingToStart") || "Waiting for host to start..."
                        : 'Webinar has ended'}
                  </p>
                  <Badge className="mt-3 bg-slate-500/10 text-slate-400 border-slate-500/15 text-[10px]">
                    View Only
                  </Badge>
                </div>
              </div>
            )}
          </div>

          {/* Bottom Controls */}
          <div className="h-16 bg-karau-card/60 border-t border-white/5 flex items-center justify-center gap-2 px-4 shrink-0" data-testid="webinar-controls">
            {/* Mic/Cam for streamers */}
            {canStream && (
              <>
                <Button variant="ghost" size="sm" onClick={toggleMic}
                  className={`h-10 w-10 rounded-full ${isMicOn ? 'bg-white/10 text-white' : 'bg-red-500/20 text-red-400'}`}
                  data-testid="mic-toggle">
                  {isMicOn ? <Mic className="w-4 h-4" /> : <MicOff className="w-4 h-4" />}
                </Button>
                <Button variant="ghost" size="sm" onClick={toggleCam}
                  className={`h-10 w-10 rounded-full ${isCamOn ? 'bg-white/10 text-white' : 'bg-red-500/20 text-red-400'}`}
                  data-testid="cam-toggle">
                  {isCamOn ? <Video className="w-4 h-4" /> : <VideoOff className="w-4 h-4" />}
                </Button>
              </>
            )}

            {/* Hand raise for attendees */}
            {isAttendee && (
              <Button variant="ghost" size="sm" onClick={toggleHandRaise}
                className={`h-10 w-10 rounded-full ${isHandRaised ? 'bg-amber-500/20 text-amber-400' : 'bg-white/10 text-white'}`}
                data-testid="hand-raise-btn">
                <Hand className="w-4 h-4" />
              </Button>
            )}

            {/* Q&A toggle */}
            <Button variant="ghost" size="sm" onClick={() => { setShowQA(!showQA); setShowParticipants(false); setShowControls(false); }}
              className={`h-10 w-10 rounded-full ${showQA ? 'bg-purple-500/20 text-purple-400' : 'bg-white/10 text-white'}`}
              data-testid="qa-toggle">
              <MessageCircleQuestion className="w-4 h-4" />
              {pendingQs.length > 0 && (
                <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-red-500 text-[8px] text-white flex items-center justify-center">{pendingQs.length}</span>
              )}
            </Button>

            {/* Participants panel for host */}
            {isHost && (
              <Button variant="ghost" size="sm" onClick={() => { setShowParticipants(!showParticipants); setShowQA(false); setShowControls(false); }}
                className={`h-10 w-10 rounded-full ${showParticipants ? 'bg-emerald-500/20 text-emerald-400' : 'bg-white/10 text-white'}`}
                data-testid="participants-toggle">
                <Users className="w-4 h-4" />
              </Button>
            )}

            {/* Host controls */}
            {isHost && (
              <Button variant="ghost" size="sm" onClick={() => { setShowControls(!showControls); setShowQA(false); setShowParticipants(false); }}
                className={`h-10 w-10 rounded-full ${showControls ? 'bg-violet-500/20 text-violet-400' : 'bg-white/10 text-white'}`}
                data-testid="controls-toggle">
                <Settings className="w-4 h-4" />
              </Button>
            )}

            <div className="w-px h-6 bg-white/10 mx-1" />

            {/* Host actions */}
            {isHost && roomInfo.status === 'scheduled' && !roomInfo.practice_mode && (
              <>
                <Button size="sm" onClick={startPractice}
                  className="h-9 px-3 text-[11px] bg-amber-500/80 hover:bg-amber-400 rounded-lg" data-testid="start-practice-btn">
                  <Shield className="w-3.5 h-3.5 mr-1" />Practice
                </Button>
                <Button size="sm" onClick={startWebinar}
                  className="h-9 px-3 text-[11px] bg-emerald-500/80 hover:bg-emerald-400 rounded-lg" data-testid="go-live-btn">
                  <Play className="w-3.5 h-3.5 mr-1" />Go Live
                </Button>
              </>
            )}
            {isHost && roomInfo.practice_mode && (
              <>
                <Button size="sm" onClick={endPractice}
                  className="h-9 px-3 text-[11px] bg-slate-500/80 hover:bg-slate-400 rounded-lg" data-testid="end-practice-btn">
                  End Practice
                </Button>
                <Button size="sm" onClick={startWebinar}
                  className="h-9 px-3 text-[11px] bg-emerald-500/80 hover:bg-emerald-400 rounded-lg" data-testid="go-live-from-practice-btn">
                  <Play className="w-3.5 h-3.5 mr-1" />Go Live
                </Button>
              </>
            )}
            {isHost && roomInfo.status === 'live' && (
              <Button size="sm" variant="destructive" onClick={endWebinar}
                className="h-9 px-3 text-[11px] rounded-lg" data-testid="end-webinar-btn">
                <Square className="w-3.5 h-3.5 mr-1" />End Webinar
              </Button>
            )}
          </div>
        </div>

        {/* Side Panel */}
        {(showQA || showParticipants || showControls) && (
          <div className="w-80 bg-karau-card/60 border-l border-white/5 flex flex-col shrink-0" data-testid="side-panel">
            {/* Q&A Panel */}
            {showQA && (
              <div className="flex-1 flex flex-col overflow-hidden">
                <div className="p-3 border-b border-white/5">
                  <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                    <MessageCircleQuestion className="w-4 h-4 text-amber-400" />
                    Q&A ({pendingQs.length} pending)
                  </h3>
                </div>
                <div className="flex-1 overflow-y-auto p-3 space-y-2">
                  {questions.length === 0 ? (
                    <p className="text-xs text-slate-500 text-center py-4">No questions yet</p>
                  ) : (
                    questions.map(q => (
                      <div key={q.question_id} className={`p-2.5 rounded-lg ${q.status === 'answered' ? 'bg-emerald-500/5 border border-emerald-500/10' : 'bg-karau-bg/40'}`}
                        data-testid={`qa-item-${q.question_id}`}>
                        <p className="text-xs text-white">{q.question}</p>
                        <div className="flex items-center gap-2 mt-1 text-[10px] text-slate-500">
                          <span>{q.asked_by}</span>
                          <button onClick={() => upvoteQuestion(q.question_id)} className="flex items-center gap-0.5 hover:text-purple-400">
                            <ThumbsUp className="w-2.5 h-2.5" />{q.upvotes}
                          </button>
                          <Badge className={`text-[8px] ${q.status === 'answered' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'}`}>
                            {q.status}
                          </Badge>
                        </div>
                        {q.answer && (
                          <div className="mt-1.5 p-1.5 bg-emerald-500/5 rounded text-[10px] text-emerald-300">
                            <span className="font-medium">A: </span>{q.answer}
                          </div>
                        )}
                        {(isHost || isPresenter) && q.status === 'pending' && (
                          <div className="flex gap-1 mt-1.5">
                            <Input value={answerTexts[q.question_id] || ''} 
                              onChange={e => setAnswerTexts(p => ({ ...p, [q.question_id]: e.target.value }))}
                              placeholder="Answer..." className="bg-karau-card border-white/10 text-white text-[10px] h-6 rounded" />
                            <Button size="sm" onClick={() => answerQuestion(q.question_id)} className="h-6 w-6 p-0 bg-emerald-500/80 rounded">
                              <Send className="w-2.5 h-2.5" />
                            </Button>
                          </div>
                        )}
                      </div>
                    ))
                  )}
                </div>
                <div className="p-3 border-t border-white/5">
                  <div className="flex gap-1.5">
                    <Input value={newQuestion} onChange={e => setNewQuestion(e.target.value)}
                      placeholder="Ask a question..." onKeyDown={e => e.key === 'Enter' && submitQuestion()}
                      className="bg-karau-bg/60 border-white/10 text-white text-xs h-8 rounded-lg" data-testid="question-input" />
                    <Button size="sm" onClick={submitQuestion} className="h-8 px-2.5 bg-purple-500/80 rounded-lg" data-testid="submit-question-btn">
                      <Send className="w-3.5 h-3.5" />
                    </Button>
                  </div>
                </div>
              </div>
            )}

            {/* Participants / Hand Raises (Host only) */}
            {showParticipants && isHost && (
              <div className="flex-1 overflow-y-auto p-3 space-y-3">
                <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                  <Users className="w-4 h-4 text-emerald-400" />Participants & Roles
                </h3>

                {/* Hand Raises */}
                {handRaises.length > 0 && (
                  <div className="space-y-1.5">
                    <p className="text-[10px] text-amber-400 font-semibold uppercase tracking-wider flex items-center gap-1">
                      <Hand className="w-3 h-3" />Raised Hands ({handRaises.length})
                    </p>
                    {handRaises.map(h => (
                      <div key={h.user_id} className="flex items-center justify-between p-2 bg-amber-500/5 rounded-lg border border-amber-500/10"
                        data-testid={`hand-${h.user_id}`}>
                        <span className="text-xs text-white">{h.name}</span>
                        <div className="flex gap-1">
                          <Button size="sm" onClick={() => promoteUser(h.user_id, 'presenter')}
                            className="h-6 px-2 text-[9px] bg-emerald-500/80 rounded" data-testid={`promote-presenter-${h.user_id}`}>
                            <MonitorUp className="w-2.5 h-2.5 mr-0.5" />Presenter
                          </Button>
                          <Button size="sm" onClick={() => promoteUser(h.user_id, 'panelist')}
                            className="h-6 px-2 text-[9px] bg-blue-500/80 rounded" data-testid={`promote-panelist-${h.user_id}`}>
                            <UserPlus className="w-2.5 h-2.5 mr-0.5" />Panelist
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Active Roles */}
                <div className="space-y-1.5">
                  <p className="text-[10px] text-purple-400 font-semibold uppercase tracking-wider">Active Roles</p>
                  {Object.entries(activeRoles).length === 0 ? (
                    <p className="text-[10px] text-slate-500 py-2">No promoted participants</p>
                  ) : (
                    Object.entries(activeRoles).map(([uid, info]) => (
                      <div key={uid} className="flex items-center justify-between p-2 bg-purple-500/5 rounded-lg border border-purple-500/10"
                        data-testid={`role-${uid}`}>
                        <div>
                          <span className="text-xs text-white">{uid}</span>
                          <Badge className="ml-1.5 text-[8px] bg-purple-500/10 text-purple-400">{info.role}</Badge>
                        </div>
                        <Button size="sm" variant="ghost" onClick={() => demoteUser(uid)}
                          className="h-6 px-1.5 text-red-400 hover:bg-red-500/10" data-testid={`demote-${uid}`}>
                          <UserMinus className="w-3 h-3" />
                        </Button>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}

            {/* Host Controls Panel */}
            {showControls && isHost && (
              <div className="flex-1 overflow-y-auto p-3 space-y-3">
                <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                  <Settings className="w-4 h-4 text-violet-400" />Host Controls
                </h3>
                <div className="space-y-2">
                  <button onClick={muteAll} className="w-full flex items-center gap-2 p-2.5 bg-karau-bg/40 rounded-lg hover:bg-white/5 transition-colors text-left"
                    data-testid="mute-all-control">
                    <MicOff className="w-4 h-4 text-red-400" />
                    <span className="text-xs text-slate-300">Mute All Attendees</span>
                  </button>
                  <div className="p-2.5 bg-karau-bg/40 rounded-lg">
                    <p className="text-[10px] text-karau-muted mb-1">Webinar Status</p>
                    <p className="text-xs text-white font-medium">{roomInfo.status} {roomInfo.practice_mode && '(Practice)'}</p>
                  </div>
                  <div className="p-2.5 bg-karau-bg/40 rounded-lg">
                    <p className="text-[10px] text-karau-muted mb-1">Settings</p>
                    <div className="space-y-1 text-[10px] text-slate-400">
                      <p>Chat: {roomInfo.settings?.chat_enabled ? 'Enabled' : 'Disabled'}</p>
                      <p>Q&A: {roomInfo.settings?.q_and_a_enabled ? 'Enabled' : 'Disabled'}</p>
                      <p>Attendee Video: {roomInfo.settings?.attendee_video ? 'Allowed' : 'Disabled'}</p>
                      <p>Attendee Audio: {roomInfo.settings?.attendee_audio ? 'Allowed' : 'Disabled'}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default WebinarLiveRoom;
