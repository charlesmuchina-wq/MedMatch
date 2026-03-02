import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { Loader2, Captions, Clapperboard, Sparkles } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { useTranslation } from '@/utils/i18n';
import { useNoiseCancellation } from '@/hooks/useNoiseCancellation';
import { useLiveTranscription, CAPTION_LANGUAGES } from '@/hooks/useLiveTranscription';
import { useSpeakerDetection } from '@/hooks/useSpeakerDetection';
import { useSpatialAudio } from '@/hooks/useSpatialAudio';
import { useDirectorMode } from '@/hooks/useDirectorMode';
import { useGhostBooking } from '@/hooks/useGhostBooking';
import { useWebRTC } from '@/hooks/useWebRTC';
import { useWebinarActions } from '@/hooks/useWebinarActions';
import { TopBar } from '@/components/KarauMeet/TopBar';
import { VideoStage } from '@/components/KarauMeet/VideoStage';
import { SidePanel } from '@/components/KarauMeet/SidePanel';
import FeatureToolbar from '@/components/KarauMeet/FeatureToolbar';
import FeatureCommandBar from '@/components/KarauMeet/FeatureCommandBar';
import EmojiReactions from '@/components/KarauMeet/EmojiReactions';
import GhostBookingAlert from '@/components/KarauMeet/GhostBookingAlert';

const API = process.env.REACT_APP_BACKEND_URL;

const WebinarLiveRoom = () => {
  const { webinarId } = useParams();
  const { t } = useTranslation();
  const navigate = useNavigate();

  // Core state
  const [roomInfo, setRoomInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [myRole, setMyRole] = useState('attendee');
  const [isMicOn, setIsMicOn] = useState(false);
  const [isCamOn, setIsCamOn] = useState(false);
  const [isHandRaised, setIsHandRaised] = useState(false);
  const [activePanel, setActivePanel] = useState(null);
  const [commandBarOpen, setCommandBarOpen] = useState(false);

  // Q&A state
  const [questions, setQuestions] = useState([]);
  const [newQuestion, setNewQuestion] = useState('');
  const [answerTexts, setAnswerTexts] = useState({});

  // Participants
  const [handRaises, setHandRaises] = useState([]);
  const [activeRoles, setActiveRoles] = useState({});

  // UI toggles
  const [currentSlide, setCurrentSlide] = useState(0);
  const [showSlides, setShowSlides] = useState(true);
  const [eyeContactOn, setEyeContactOn] = useState(false);
  const [showWhiteboard, setShowWhiteboard] = useState(false);
  const [showLangPicker, setShowLangPicker] = useState(false);
  const [showReactions, setShowReactions] = useState(false);
  const [showCoach, setShowCoach] = useState(false);
  const [coachTips, setCoachTips] = useState([]);
  const [mainStageUserId, setMainStageUserId] = useState(null);

  // Engagement
  const [engagementData, setEngagementData] = useState(null);
  const speakingStartRef = useRef(null);
  const meetingStartRef = useRef(Date.now());
  const mainStageSwitchRef = useRef(null);

  // Hooks
  const noiseCancellation = useNoiseCancellation();
  const liveTranscription = useLiveTranscription();
  const speakerDetection = useSpeakerDetection();
  const spatialAudio = useSpatialAudio();
  const webrtc = useWebRTC(webinarId, speakerDetection);
  const ghostBooking = useGhostBooking(webinarId);

  // Director Mode
  const directorMode = useDirectorMode(webinarId, speakerDetection, webrtc.remoteStreams);

  // Derived state (memoized)
  const canStream = useMemo(() => roomInfo?.can_stream_video, [roomInfo]);
  const canControl = useMemo(() => roomInfo?.can_control, [roomInfo]);
  const canDriveSlides = useMemo(() => roomInfo?.can_drive_slides, [roomInfo]);
  const isHost = useMemo(() => myRole === 'host', [myRole]);
  const isAttendee = useMemo(() => myRole === 'attendee', [myRole]);
  const pendingQs = useMemo(() => questions.filter(q => q.status === 'pending'), [questions]);

  // Stable fetchRoomInfo
  const fetchRoomInfo = useCallback(async () => {
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
        return data;
      } else if (res.status === 403) {
        toast.error('Practice session in progress');
        navigate(-1);
      }
    } catch (e) { console.error('Room info error:', e); }
    setLoading(false);
    return null;
  }, [webinarId, navigate]);

  // Actions hook
  const actions = useWebinarActions(webinarId, navigate, fetchRoomInfo);

  // Init: fetch room, start media, connect WS
  useEffect(() => {
    let cancelled = false;
    (async () => {
      const data = await fetchRoomInfo();
      if (cancelled || !data) { setLoading(false); return; }
      if (data.can_stream_video) {
        const result = await webrtc.startLocalMedia(true, true, noiseCancellation, data.host_name);
        if (result) { setIsCamOn(result.video); setIsMicOn(result.audio); }
      }
      webrtc.connectWebSocket(data, setCurrentSlide, fetchRoomInfo);
      setLoading(false);
    })();
    return () => { cancelled = true; webrtc.cleanup(); liveTranscription.stop?.(); speakerDetection.cleanup(); spatialAudio.cleanup(); };
  }, [webinarId]);

  // Sync speaker detection -> transcription
  useEffect(() => {
    if (speakerDetection.activeSpeaker) liveTranscription.setActiveSpeaker(speakerDetection.activeSpeaker);
  }, [speakerDetection.activeSpeaker]);

  // Auto-promote active speaker to main stage (debounced)
  useEffect(() => {
    const speaker = speakerDetection.activeSpeaker;
    if (!speaker || speaker.userId === '__local__' || speaker.userId === mainStageUserId) return;
    if (mainStageSwitchRef.current) clearTimeout(mainStageSwitchRef.current);
    mainStageSwitchRef.current = setTimeout(() => setMainStageUserId(speaker.userId), 1500);
    return () => { if (mainStageSwitchRef.current) clearTimeout(mainStageSwitchRef.current); };
  }, [speakerDetection.activeSpeaker, mainStageUserId]);

  // Spatial audio: connect remote streams
  useEffect(() => {
    if (!spatialAudio.enabled) return;
    const entries = Object.entries(webrtc.remoteStreams);
    const total = entries.length;
    entries.forEach(([uid, { stream }], idx) => {
      const x = total > 1 ? ((idx / (total - 1)) * 2 - 1) : 0;
      spatialAudio.connectStream(uid, stream, { x, y: 0 });
    });
  }, [webrtc.remoteStreams, spatialAudio.enabled]);

  // Polling: Q&A + hand raises (4s interval)
  useEffect(() => {
    if (!roomInfo) return;
    const poll = async () => {
      const qa = await actions.fetchQA();
      if (qa) setQuestions(qa);
      if (roomInfo.can_control) {
        const hr = await actions.fetchHandRaises();
        if (hr) setHandRaises(hr);
      }
    };
    const interval = setInterval(poll, 4000);
    return () => clearInterval(interval);
  }, [roomInfo, actions]);

  // Engagement dashboard polling (30s)
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

  // Auto-analyze sentiment from captions (throttled)
  const lastSentimentRef = useRef(0);
  useEffect(() => {
    if (!liveTranscription.captions.length || !webinarId) return;
    const now = Date.now();
    if (now - lastSentimentRef.current < 10000) return; // Throttle to every 10s
    lastSentimentRef.current = now;
    const last = liveTranscription.captions[liveTranscription.captions.length - 1];
    if (!last?.original || last.original.length < 20) return;
    const token = localStorage.getItem('token');
    fetch(`${API}/api/karau-features/sentiment/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ meeting_id: webinarId, text: last.original, speaker: last.speaker || 'Unknown' })
    }).catch(() => {});
  }, [liveTranscription.captions.length, webinarId]);

  // AI Coach tips (60s interval, only for streamers)
  useEffect(() => {
    if (!webinarId || !canStream) return;
    const interval = setInterval(async () => {
      const captions = liveTranscription.captions;
      if (captions.length === 0) return;
      const recentText = captions.slice(-5).map(c => c.original || c.text).join(' ');
      const token = localStorage.getItem('token');
      try {
        const res = await fetch(`${API}/api/karau-features/ai-coach/tip`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify({
            meeting_id: webinarId, transcript_segment: recentText, speaker: 'You',
            speaking_duration_seconds: speakingStartRef.current ? (Date.now() - speakingStartRef.current) / 1000 : 0,
            total_meeting_seconds: (Date.now() - meetingStartRef.current) / 1000,
            engagement_score: engagementData?.engagement_score || 5,
            participant_count: Object.keys(webrtc.remoteStreams).length + 1
          })
        });
        if (res.ok) {
          const tip = await res.json();
          if (tip.tip) setCoachTips(prev => [...prev.slice(-5), { ...tip, ts: Date.now() }]);
        }
      } catch {}
    }, 60000);
    return () => clearInterval(interval);
  }, [webinarId, canStream, engagementData, webrtc.remoteStreams]);

  // --- Stable callbacks ---
  const toggleNoiseCancellation = useCallback(async () => {
    if (noiseCancellation.enabled) {
      const original = noiseCancellation.removeFromStream();
      if (original) { webrtc.localStreamRef.current = original; if (webrtc.localVideoRef.current) webrtc.localVideoRef.current.srcObject = original; }
    } else if (webrtc.localStreamRef.current) {
      const processed = await noiseCancellation.applyToStream(webrtc.localStreamRef.current);
      if (processed) { webrtc.localStreamRef.current = processed; if (webrtc.localVideoRef.current) webrtc.localVideoRef.current.srcObject = processed; }
    }
  }, [noiseCancellation, webrtc]);

  const toggleMic = useCallback(() => {
    if (!webrtc.localStreamRef.current) return;
    const track = webrtc.localStreamRef.current.getAudioTracks()[0];
    if (track) { track.enabled = !track.enabled; setIsMicOn(track.enabled); }
  }, [webrtc]);

  const toggleCam = useCallback(() => {
    if (!webrtc.localStreamRef.current) return;
    const track = webrtc.localStreamRef.current.getVideoTracks()[0];
    if (track) { track.enabled = !track.enabled; setIsCamOn(track.enabled); }
  }, [webrtc]);

  const toggleLiveCaptions = useCallback(() => {
    if (liveTranscription.active) liveTranscription.stop();
    else if (webrtc.localStreamRef.current) liveTranscription.start(webrtc.localStreamRef.current);
  }, [liveTranscription, webrtc]);

  const handleSaveTranscript = useCallback(() => {
    const text = liveTranscription.fullTranscript?.trim();
    if (text) actions.saveTranscript(text);
  }, [liveTranscription, actions]);

  const togglePanel = useCallback((panel) => setActivePanel(prev => prev === panel ? null : panel), []);

  const handleToggleHandRaise = useCallback(async () => {
    await actions.toggleHandRaise(isHandRaised);
    setIsHandRaised(prev => !prev);
  }, [actions, isHandRaised]);

  const handleCommandSelect = useCallback((featureId) => {
    if (featureId === '__open_command__') { setCommandBarOpen(true); return; }
    const toggleMap = {
      mic: toggleMic, cam: toggleCam, noise: toggleNoiseCancellation,
      eye: () => setEyeContactOn(v => !v), captions: toggleLiveCaptions,
      spatial: spatialAudio.toggle, reactions: () => setShowReactions(v => !v),
      coach: () => setShowCoach(v => !v), whiteboard: () => setShowWhiteboard(v => !v),
      hand: handleToggleHandRaise,
    };
    if (toggleMap[featureId]) toggleMap[featureId]();
    else togglePanel(featureId);
  }, [toggleMic, toggleCam, toggleNoiseCancellation, toggleLiveCaptions, spatialAudio, handleToggleHandRaise, togglePanel]);

  const leaveWebinar = useCallback(() => { webrtc.cleanup(); navigate('/karau-meet/webinars'); }, [webrtc, navigate]);

  const handleSubmitQuestion = useCallback(async () => {
    if (!newQuestion.trim()) return;
    const ok = await actions.submitQuestion(newQuestion);
    if (ok) { setNewQuestion(''); const qa = await actions.fetchQA(); if (qa) setQuestions(qa); }
  }, [newQuestion, actions]);

  const handleAnswerQuestion = useCallback(async (qId) => {
    if (!answerTexts[qId]?.trim()) return;
    const ok = await actions.answerQuestion(qId, answerTexts[qId]);
    if (ok) { setAnswerTexts(p => ({ ...p, [qId]: '' })); const qa = await actions.fetchQA(); if (qa) setQuestions(qa); }
  }, [answerTexts, actions]);

  const handleUpvoteQuestion = useCallback(async (qId) => {
    await actions.upvoteQuestion(qId);
    const qa = await actions.fetchQA();
    if (qa) setQuestions(qa);
  }, [actions]);

  // Stable toggle callbacks (must be before early returns)
  const toggleEyeContact = useCallback(() => setEyeContactOn(v => !v), []);
  const toggleReactionsUI = useCallback(() => setShowReactions(v => !v), []);
  const toggleCoachUI = useCallback(() => setShowCoach(v => !v), []);
  const toggleWhiteboardUI = useCallback(() => setShowWhiteboard(v => !v), []);
  const openCommandBar = useCallback(() => setCommandBarOpen(true), []);
  const closeCommandBar = useCallback(() => setCommandBarOpen(false), []);
  const closePanel = useCallback(() => setActivePanel(null), []);
  const toggleLangUI = useCallback(() => setShowLangPicker(v => !v), []);

  // Memoized props for sub-panels
  const qaProps = useMemo(() => ({
    questions, pendingQs, newQuestion, setNewQuestion,
    submitQuestion: handleSubmitQuestion, answerTexts, setAnswerTexts,
    answerQuestion: handleAnswerQuestion, upvoteQuestion: handleUpvoteQuestion,
    canControl, myRole,
  }), [questions, pendingQs, newQuestion, answerTexts, handleSubmitQuestion, handleAnswerQuestion, handleUpvoteQuestion, canControl, myRole]);

  const participantsProps = useMemo(() => ({
    handRaises, activeRoles, promoteUser: actions.promoteUser, demoteUser: actions.demoteUser,
    isHost, roomInfo, onGrantPermission: actions.grantGuestPermission, onRevokePermission: actions.revokeGuestPermission,
  }), [handRaises, activeRoles, actions, isHost, roomInfo]);

  const controlsProps = useMemo(() => ({ muteAll: actions.muteAll, roomInfo }), [actions, roomInfo]);

  // --- Loading states ---
  if (loading) return <div className="min-h-screen bg-karau-bg flex items-center justify-center"><Loader2 className="w-8 h-8 text-purple-400 animate-spin" /></div>;
  if (!roomInfo) return <div className="min-h-screen bg-karau-bg flex items-center justify-center"><p className="text-red-400">Unable to join webinar</p></div>;

  return (
    <div className="min-h-screen bg-karau-bg flex flex-col" style={{ fontFamily: "'IBM Plex Sans', sans-serif" }} data-testid="webinar-live-room">
      <TopBar roomInfo={roomInfo} myRole={myRole} onLeave={leaveWebinar} />

      <EmojiReactions webinarId={webinarId} senderName={roomInfo.host_name || 'User'} show={showReactions} onToggle={() => setShowReactions(v => !v)} />
      <GhostBookingAlert ghostBooking={ghostBooking} onClose={() => {}} />

      {/* Director Mode Indicator */}
      {directorMode.enabled && directorMode.mode === 'auto' && directorMode.activeView !== 'panoramic' && (
        <div className="absolute top-12 left-1/2 -translate-x-1/2 z-30 flex items-center gap-1.5 bg-violet-500/10 backdrop-blur-sm border border-violet-500/20 rounded-full px-3 py-1" data-testid="director-mode-indicator">
          <Clapperboard className="w-3 h-3 text-violet-400" />
          <span className="text-[9px] text-violet-300 font-medium">Director: {directorMode.activeView}</span>
        </div>
      )}

      <div className="flex flex-1 overflow-hidden">
        <div className="flex-1 flex flex-col">
          <VideoStage
            showWhiteboard={showWhiteboard} webinarId={webinarId} onCloseWhiteboard={() => setShowWhiteboard(false)}
            showSlides={showSlides} currentSlide={currentSlide} onSlideChange={setCurrentSlide} canDriveSlides={canDriveSlides} wsRef={webrtc.wsRef}
            localVideoRef={webrtc.localVideoRef} canStream={canStream} isCamOn={isCamOn} eyeContactOn={eyeContactOn}
            myRole={myRole} hostName={roomInfo.host_name} roomInfo={roomInfo}
            mainStageUserId={mainStageUserId} remoteStreams={webrtc.remoteStreams} speakerDetection={speakerDetection}
            onSetMainStage={setMainStageUserId}
          />

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
                        {last?.speaker && <span className="font-semibold mr-1" style={{ color: last.speakerColor }} data-testid="speaker-label">{last.speaker}:</span>}
                        {last?.text}
                      </p>
                    );
                  })()}
                </div>
                {liveTranscription.sourceLanguage !== liveTranscription.displayLanguage && (
                  <Badge className="bg-violet-500/10 text-violet-400 border-violet-500/20 text-[7px] shrink-0" data-testid="translation-badge">
                    {CAPTION_LANGUAGES[liveTranscription.sourceLanguage]?.substring(0, 2)}{' > '}{CAPTION_LANGUAGES[liveTranscription.displayLanguage]?.substring(0, 2)}
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

          {/* AI Coach Tips */}
          {showCoach && coachTips.length > 0 && (
            <div className="absolute top-12 right-3 w-64 max-h-48 overflow-y-auto space-y-1.5 z-10" data-testid="coach-tips-panel">
              {coachTips.slice(-3).map((tip, i) => (
                <div key={i} className={`p-2 rounded-lg backdrop-blur-md border transition-all ${
                  tip.urgency === 'high' ? 'bg-red-500/10 border-red-500/20' : tip.urgency === 'medium' ? 'bg-amber-500/10 border-amber-500/20' : 'bg-emerald-500/10 border-emerald-500/20'
                }`} data-testid={`coach-tip-${i}`}>
                  <div className="flex items-start gap-1.5">
                    <span className="text-sm">{tip.emoji}</span>
                    <div>
                      <p className="text-[9px] text-white/90 leading-relaxed">{tip.tip}</p>
                      <Badge className={`mt-1 text-[7px] ${tip.category === 'engagement' ? 'bg-violet-500/10 text-violet-400' : tip.category === 'pacing' ? 'bg-blue-500/10 text-blue-400' : 'bg-teal-500/10 text-teal-400'}`}>{tip.category}</Badge>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Language Picker */}
          {showLangPicker && (
            <div className="px-4 py-2 bg-karau-card/90 backdrop-blur-md border-t border-white/5" data-testid="language-picker-panel">
              <div className="flex gap-6 items-start">
                {[['Speaker Language', liveTranscription.sourceLanguage, liveTranscription.setSourceLanguage, 'src', 'purple'],
                  ['Display Language', liveTranscription.displayLanguage, liveTranscription.setDisplayLanguage, 'dsp', 'emerald']
                ].map(([label, current, setter, prefix, color]) => (
                  <div key={prefix}>
                    <p className="text-[9px] text-slate-400 uppercase tracking-wider mb-1.5">{label}</p>
                    <div className="flex flex-wrap gap-1">
                      {Object.entries(CAPTION_LANGUAGES).map(([code, name]) => (
                        <button key={`${prefix}-${code}`} onClick={() => setter(code)} data-testid={`${prefix}-lang-${code}`}
                          className={`px-2 py-0.5 rounded text-[9px] transition-colors ${current === code
                            ? `bg-${color}-500/30 text-${color}-300 border border-${color}-500/30`
                            : 'bg-white/5 text-slate-400 hover:text-white hover:bg-white/10 border border-transparent'
                          }`}>{name}</button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Feature Toolbar */}
          <FeatureToolbar
            isMicOn={isMicOn} onToggleMic={toggleMic}
            isCamOn={isCamOn} onToggleCam={toggleCam}
            noiseEnabled={noiseCancellation.enabled} onToggleNoise={toggleNoiseCancellation} noiseSupported={noiseCancellation.isSupported}
            eyeContactOn={eyeContactOn} onToggleEye={toggleEyeContact}
            captionsActive={liveTranscription.active} onToggleCaptions={toggleLiveCaptions}
            spatialEnabled={spatialAudio.enabled} onToggleSpatial={spatialAudio.toggle}
            activePanel={activePanel} onTogglePanel={togglePanel}
            showReactions={showReactions} onToggleReactions={toggleReactionsUI}
            showCoach={showCoach} onToggleCoach={toggleCoachUI} coachTipsCount={coachTips.length || null}
            showWhiteboard={showWhiteboard} onToggleWhiteboard={toggleWhiteboardUI}
            isHandRaised={isHandRaised} onToggleHand={handleToggleHandRaise} isAttendee={isAttendee}
            pendingQCount={pendingQs.length || null}
            canStream={canStream} canControl={canControl}
            onOpenCommandBar={openCommandBar}
            isHost={isHost} roomStatus={roomInfo.status} practiceMode={roomInfo.practice_mode}
            onStartPractice={actions.startPractice} onEndPractice={actions.endPractice}
            onStartWebinar={actions.startWebinar} onEndWebinar={actions.endWebinar}
            onSaveTranscript={handleSaveTranscript} hasTranscript={!!liveTranscription.fullTranscript?.trim()}
            onToggleLang={toggleLangUI} showLangPicker={showLangPicker}
            sourceLanguage={liveTranscription.sourceLanguage} displayLanguage={liveTranscription.displayLanguage}
          />
        </div>

        <SidePanel
          activePanel={activePanel}
          onClose={useCallback(() => setActivePanel(null), [])}
          webinarId={webinarId}
          roomInfo={roomInfo}
          qaProps={useMemo(() => ({
            questions, pendingQs, newQuestion, setNewQuestion,
            submitQuestion: handleSubmitQuestion, answerTexts, setAnswerTexts,
            answerQuestion: handleAnswerQuestion, upvoteQuestion: handleUpvoteQuestion,
            canControl, myRole,
          }), [questions, pendingQs, newQuestion, answerTexts, handleSubmitQuestion, handleAnswerQuestion, handleUpvoteQuestion, canControl, myRole])}
          participantsProps={useMemo(() => ({
            handRaises, activeRoles, promoteUser: actions.promoteUser, demoteUser: actions.demoteUser,
            isHost, roomInfo, onGrantPermission: actions.grantGuestPermission, onRevokePermission: actions.revokeGuestPermission,
          }), [handRaises, activeRoles, actions, isHost, roomInfo])}
          controlsProps={useMemo(() => ({ muteAll: actions.muteAll, roomInfo }), [actions, roomInfo])}
        />
      </div>

      <FeatureCommandBar isOpen={commandBarOpen} onClose={useCallback(() => setCommandBarOpen(false), [])} onSelectFeature={handleCommandSelect} />
    </div>
  );
};

export default WebinarLiveRoom;
