import { useRef, useEffect } from 'react';
import { Badge } from '@/components/ui/badge';
import { Video, VideoOff, MicOff, Hand, Circle } from 'lucide-react';

/**
 * Individual video participant tile component
 */
const VideoParticipant = ({ participant, isLocal, stream, isSpeaking, virtualBg }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    if (videoRef.current && stream) {
      videoRef.current.srcObject = stream;
    }
  }, [stream]);

  // Apply virtual background effect (simplified - real implementation would use ML)
  useEffect(() => {
    if (isLocal && virtualBg && virtualBg !== 'none' && canvasRef.current && videoRef.current) {
      if (virtualBg === 'blur') {
        canvasRef.current.style.filter = 'blur(0px)';
        canvasRef.current.style.backdropFilter = 'blur(10px)';
      }
    }
  }, [virtualBg, isLocal]);

  return (
    <div className={`relative rounded-xl overflow-hidden bg-slate-900 ${isSpeaking ? 'ring-2 ring-turquoise' : ''}`}>
      {participant?.video_enabled && stream ? (
        <>
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted={isLocal}
            className="w-full h-full object-cover"
            data-testid={`video-${isLocal ? 'local' : participant?.user_id}`}
          />
          <canvas ref={canvasRef} className="hidden" />
        </>
      ) : (
        <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-slate-800 to-slate-900 min-h-[200px]">
          <div className="w-20 h-20 rounded-full bg-turquoise/20 flex items-center justify-center">
            <span className="text-3xl font-bold text-turquoise">
              {participant?.user_name?.charAt(0)?.toUpperCase() || '?'}
            </span>
          </div>
        </div>
      )}
      
      {/* Name badge */}
      <div className="absolute bottom-3 left-3 flex items-center gap-2">
        <Badge className="bg-black/60 text-white border-0">
          {participant?.user_name || 'Unknown'} {isLocal && '(You)'}
        </Badge>
        {!participant?.audio_enabled && (
          <Badge variant="destructive" className="px-1.5">
            <MicOff className="w-3 h-3" />
          </Badge>
        )}
        {participant?.hand_raised && (
          <Badge className="bg-yellow-500 text-black px-1.5">
            <Hand className="w-3 h-3" />
          </Badge>
        )}
      </div>
      
      {/* Host badge */}
      {participant?.is_host && (
        <Badge className="absolute top-3 left-3 bg-turquoise text-white border-0">
          Host
        </Badge>
      )}
      
      {/* Recording indicator */}
      {participant?.is_recording && (
        <Badge className="absolute top-3 right-3 bg-red-500 text-white border-0 animate-pulse">
          <Circle className="w-2 h-2 mr-1 fill-current" />
          REC
        </Badge>
      )}
    </div>
  );
};

/**
 * Grid layout for all participants in a meeting
 */
const ParticipantGrid = ({ participants, localStream, remoteStreams, localUserId, virtualBackground }) => {
  const getGridClass = () => {
    const count = participants.length;
    if (count === 1) return 'grid-cols-1';
    if (count === 2) return 'grid-cols-2';
    if (count <= 4) return 'grid-cols-2 grid-rows-2';
    return 'grid-cols-3 grid-rows-2';
  };

  return (
    <div className={`h-full grid gap-3 ${getGridClass()}`}>
      {participants.map((p, idx) => (
        <VideoParticipant
          key={p.user_id || idx}
          participant={p}
          isLocal={p.user_id === localUserId}
          stream={p.user_id === localUserId ? localStream : remoteStreams[p.user_id]}
          virtualBg={p.user_id === localUserId ? virtualBackground : null}
        />
      ))}
    </div>
  );
};

export { VideoParticipant, ParticipantGrid };
export default ParticipantGrid;
