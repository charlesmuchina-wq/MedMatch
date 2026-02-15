import { Button } from '@/components/ui/button';
import {
  Video, VideoOff, Mic, MicOff, PhoneOff,
  Monitor, MonitorOff, Hand, Image,
  MessageSquare, Users, Settings, Sparkles,
  Circle, Square
} from 'lucide-react';

/**
 * Video call control bar component
 * Handles audio, video, screen share, recording, and panel toggles
 */
const VideoControls = ({
  isAudioEnabled,
  isVideoEnabled,
  isScreenSharing,
  isRecording,
  isHandRaised,
  isHost,
  activePanel,
  onToggleAudio,
  onToggleVideo,
  onToggleScreenShare,
  onToggleRecording,
  onToggleHandRaise,
  onOpenVirtualBg,
  onSetActivePanel,
  onLeaveMeeting
}) => {
  return (
    <div className="h-20 bg-slate-800 border-t border-slate-700 flex items-center justify-center gap-2">
      {/* Audio */}
      <Button
        variant={isAudioEnabled ? 'secondary' : 'destructive'}
        size="lg"
        className="rounded-full w-12 h-12"
        onClick={onToggleAudio}
        title={isAudioEnabled ? 'Mute' : 'Unmute'}
        data-testid="control-audio"
      >
        {isAudioEnabled ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5" />}
      </Button>

      {/* Video */}
      <Button
        variant={isVideoEnabled ? 'secondary' : 'destructive'}
        size="lg"
        className="rounded-full w-12 h-12"
        onClick={onToggleVideo}
        title={isVideoEnabled ? 'Stop Video' : 'Start Video'}
        data-testid="control-video"
      >
        {isVideoEnabled ? <Video className="w-5 h-5" /> : <VideoOff className="w-5 h-5" />}
      </Button>

      {/* Virtual Background */}
      <Button
        variant="secondary"
        size="lg"
        className="rounded-full w-12 h-12"
        onClick={onOpenVirtualBg}
        title="Virtual Background"
        data-testid="control-virtual-bg"
      >
        <Image className="w-5 h-5" />
      </Button>

      {/* Screen share */}
      <Button
        variant={isScreenSharing ? 'default' : 'secondary'}
        size="lg"
        className={`rounded-full w-12 h-12 ${isScreenSharing ? 'bg-turquoise' : ''}`}
        onClick={onToggleScreenShare}
        title={isScreenSharing ? 'Stop Sharing' : 'Share Screen'}
        data-testid="control-screen-share"
      >
        {isScreenSharing ? <MonitorOff className="w-5 h-5" /> : <Monitor className="w-5 h-5" />}
      </Button>

      {/* Record */}
      {isHost && (
        <Button
          variant={isRecording ? 'destructive' : 'secondary'}
          size="lg"
          className={`rounded-full w-12 h-12 ${isRecording ? 'animate-pulse' : ''}`}
          onClick={onToggleRecording}
          title={isRecording ? 'Stop Recording' : 'Start Recording'}
          data-testid="control-record"
        >
          {isRecording ? <Square className="w-5 h-5" /> : <Circle className="w-5 h-5" />}
        </Button>
      )}

      {/* Raise hand */}
      <Button
        variant={isHandRaised ? 'default' : 'secondary'}
        size="lg"
        className={`rounded-full w-12 h-12 ${isHandRaised ? 'bg-yellow-500' : ''}`}
        onClick={onToggleHandRaise}
        title={isHandRaised ? 'Lower Hand' : 'Raise Hand'}
        data-testid="control-raise-hand"
      >
        <Hand className="w-5 h-5" />
      </Button>

      <div className="w-px h-8 bg-slate-600 mx-1" />

      {/* Chat */}
      <Button
        variant={activePanel === 'chat' ? 'default' : 'secondary'}
        size="lg"
        className="rounded-full w-12 h-12"
        onClick={() => onSetActivePanel(activePanel === 'chat' ? null : 'chat')}
        title="Chat"
        data-testid="control-chat"
      >
        <MessageSquare className="w-5 h-5" />
      </Button>

      {/* Participants */}
      <Button
        variant={activePanel === 'participants' ? 'default' : 'secondary'}
        size="lg"
        className="rounded-full w-12 h-12"
        onClick={() => onSetActivePanel(activePanel === 'participants' ? null : 'participants')}
        title="Participants"
        data-testid="control-participants"
      >
        <Users className="w-5 h-5" />
      </Button>

      {/* AI Notes */}
      <Button
        variant={activePanel === 'ai-notes' ? 'default' : 'secondary'}
        size="lg"
        className={`rounded-full w-12 h-12 ${activePanel === 'ai-notes' ? 'bg-turquoise' : ''}`}
        onClick={() => onSetActivePanel(activePanel === 'ai-notes' ? null : 'ai-notes')}
        title="AI Notes"
        data-testid="control-ai-notes"
      >
        <Sparkles className="w-5 h-5" />
      </Button>

      {/* Settings */}
      <Button
        variant={activePanel === 'settings' ? 'default' : 'secondary'}
        size="lg"
        className="rounded-full w-12 h-12"
        onClick={() => onSetActivePanel(activePanel === 'settings' ? null : 'settings')}
        title="Settings"
        data-testid="control-settings"
      >
        <Settings className="w-5 h-5" />
      </Button>

      <div className="w-px h-8 bg-slate-600 mx-1" />

      {/* Leave */}
      <Button
        variant="destructive"
        size="lg"
        className="rounded-full w-12 h-12"
        onClick={onLeaveMeeting}
        title="Leave Meeting"
        data-testid="control-leave"
      >
        <PhoneOff className="w-5 h-5" />
      </Button>
    </div>
  );
};

export default VideoControls;
