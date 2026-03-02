import { memo, lazy, Suspense } from 'react';
import { Loader2 } from 'lucide-react';

// Lazy load ALL panel components - only load when actually opened
const AIAssistantPanel = lazy(() => import('@/components/KarauMeet/AIAssistantPanel'));
const LeaderboardPanel = lazy(() => import('@/components/KarauMeet/LeaderboardPanel'));
const DirectorModePanel = lazy(() => import('@/components/KarauMeet/DirectorModePanel'));
const QRCodePanel = lazy(() => import('@/components/KarauMeet/QRCodePanel'));
const SentimentDashboard = lazy(() => import('@/components/KarauMeet/SentimentDashboard'));
const CopilotPanel = lazy(() => import('@/components/KarauMeet/CopilotPanel'));
const SpatialTrackingPanel = lazy(() => import('@/components/KarauMeet/SpatialTrackingPanel'));
const PanoramicFramingPanel = lazy(() => import('@/components/KarauMeet/PanoramicFramingPanel'));
const SpatialMeetingPanel = lazy(() => import('@/components/KarauMeet/SpatialMeetingPanel'));
const RoomControlPanel = lazy(() => import('@/components/KarauMeet/RoomControlPanel'));
const BeamformingPanel = lazy(() => import('@/components/KarauMeet/BeamformingPanel'));
const HardwareDiscoveryPanel = lazy(() => import('@/components/KarauMeet/HardwareDiscoveryPanel'));
const BreakoutLoungePanel = lazy(() => import('@/components/KarauMeet/BreakoutLoungePanel'));
const PollsChallengesPanel = lazy(() => import('@/components/KarauMeet/PollsChallengesPanel'));
const BiometricVerifyPanel = lazy(() => import('@/components/KarauMeet/BiometricVerifyPanel'));
const QAPanel = lazy(() => import('@/components/KarauMeet/QAPanel'));
const ParticipantsPanel = lazy(() => import('@/components/KarauMeet/ParticipantsPanel'));
const ControlsPanel = lazy(() => import('@/components/KarauMeet/ControlsPanel'));

const PanelLoader = () => (
  <div className="flex-1 flex items-center justify-center">
    <Loader2 className="w-5 h-5 text-purple-400 animate-spin" />
  </div>
);

export const SidePanel = memo(function SidePanel({ activePanel, onClose, webinarId, roomInfo, qaProps, participantsProps, controlsProps }) {
  if (!activePanel) return null;

  return (
    <div className="relative w-80 bg-karau-card/80 backdrop-blur-xl border-l border-white/[0.06] flex flex-col shrink-0 overflow-hidden animate-panel-slide-in" data-testid="side-panel">
      <button onClick={onClose} data-testid="close-panel-btn"
        className="absolute top-2 right-2 z-10 w-6 h-6 rounded-lg bg-white/[0.06] hover:bg-white/[0.12] flex items-center justify-center text-slate-500 hover:text-white transition-colors">
        <span className="text-xs">&times;</span>
      </button>
      <Suspense fallback={<PanelLoader />}>
        {activePanel === 'qa' && <QAPanel {...qaProps} />}
        {activePanel === 'participants' && <ParticipantsPanel {...participantsProps} />}
        {activePanel === 'controls' && <ControlsPanel {...controlsProps} />}
        {activePanel === 'ai' && <AIAssistantPanel meetingId={webinarId} webinarId={webinarId} />}
        {activePanel === 'leaderboard' && <LeaderboardPanel webinarId={webinarId} />}
        {activePanel === 'director' && <DirectorModePanel meetingId={webinarId} />}
        {activePanel === 'qr' && <QRCodePanel meetingId={webinarId} meetingTitle={roomInfo?.title} />}
        {activePanel === 'sentiment' && <SentimentDashboard meetingId={webinarId} />}
        {activePanel === 'copilot' && <CopilotPanel meetingId={webinarId} />}
        {activePanel === 'slam' && <SpatialTrackingPanel meetingId={webinarId} />}
        {activePanel === 'panoramic' && <PanoramicFramingPanel meetingId={webinarId} />}
        {activePanel === 'webxr' && <SpatialMeetingPanel meetingId={webinarId} />}
        {activePanel === 'iot' && <RoomControlPanel meetingId={webinarId} />}
        {activePanel === 'beamforming' && <BeamformingPanel meetingId={webinarId} />}
        {activePanel === 'hardware' && <HardwareDiscoveryPanel meetingId={webinarId} />}
        {activePanel === 'breakout' && <BreakoutLoungePanel meetingId={webinarId} userName={roomInfo?.host_name} userId={roomInfo?.host_id} />}
        {activePanel === 'polls' && <PollsChallengesPanel meetingId={webinarId} />}
        {activePanel === 'biometric' && <BiometricVerifyPanel meetingId={webinarId} />}
      </Suspense>
    </div>
  );
});
