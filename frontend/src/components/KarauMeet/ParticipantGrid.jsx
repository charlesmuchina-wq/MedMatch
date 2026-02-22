import { useRef, useEffect, useMemo } from 'react';
import { Badge } from '@/components/ui/badge';
import { Video, VideoOff, MicOff, Hand, Circle } from 'lucide-react';

/**
 * Individual video participant tile component
 */
const VideoParticipant = ({ participant, isLocal, stream, isSpeaking, virtualBg }) => {
  const videoRef = useRef(null);

  useEffect(() => {
    if (videoRef.current && stream) {
      videoRef.current.srcObject = stream;
    }
  }, [stream]);

  // Blur filter style based on virtual background setting
  const videoStyle = useMemo(() => {
    if (isLocal && virtualBg === 'blur') {
      return { filter: 'blur(0px)' }; // Video itself isn't blurred - the background would be
    }
    return {};
  }, [virtualBg, isLocal]);

  return (
    <div className={`relative rounded-xl overflow-hidden bg-slate-900 ${isSpeaking ? 'ring-2 ring-turquoise' : ''}`}>
      {participant?.video_enabled && stream ? (
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted={isLocal}
          className="w-full h-full object-cover"
          style={videoStyle}
          data-testid={`video-${isLocal ? 'local' : participant?.user_id}`}
        />
      ) : (
        <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-slate-800 to-slate-900 min-h-[120px] md:min-h-[200px]">
          <div className="w-14 h-14 md:w-20 md:h-20 rounded-full bg-turquoise/20 flex items-center justify-center">
            <span className="text-xl md:text-3xl font-bold text-turquoise">
              {participant?.user_name?.charAt(0)?.toUpperCase() || '?'}
            </span>
          </div>
        </div>
      )}
      
      {/* Name badge */}
      <div className="absolute bottom-2 md:bottom-3 left-2 md:left-3 flex items-center gap-1 md:gap-2">
        <Badge className="bg-black/60 text-white border-0 text-xs md:text-sm px-1.5 md:px-2">
          {participant?.user_name || 'Unknown'} {isLocal && '(You)'}
        </Badge>
        {!participant?.audio_enabled && (
          <Badge variant="destructive" className="px-1 md:px-1.5">
            <MicOff className="w-3 h-3" />
          </Badge>
        )}
        {participant?.hand_raised && (
          <Badge className="bg-yellow-500 text-black px-1 md:px-1.5">
            <Hand className="w-3 h-3" />
          </Badge>
        )}
      </div>
      
      {/* Host badge */}
      {participant?.is_host && (
        <Badge className="absolute top-2 md:top-3 left-2 md:left-3 bg-turquoise text-white border-0 text-xs">
          Host
        </Badge>
      )}
      
      {/* Recording indicator */}
      {participant?.is_recording && (
        <Badge className="absolute top-2 md:top-3 right-2 md:right-3 bg-red-500 text-white border-0 animate-pulse text-xs">
          <Circle className="w-2 h-2 mr-1 fill-current" />
          REC
        </Badge>
      )}
    </div>
  );
};

/**
 * Grid layout for all participants in a meeting
 * Deduplicated participants by user_id
 */
const ParticipantGrid = ({ participants, localStream, remoteStreams, localUserId, virtualBackground }) => {
  // Deduplicate participants by user_id - keep only the most recent entry
  const uniqueParticipants = useMemo(() => {
    const seen = new Map();
    // Process in order - later entries override earlier ones
    participants.forEach(p => {
      if (p.user_id) {
        seen.set(p.user_id, p);
      }
    });
    return Array.from(seen.values());
  }, [participants]);
  
  const getGridClass = () => {
    const count = uniqueParticipants.length;
    if (count === 1) return 'grid-cols-1';
    if (count === 2) return 'grid-cols-2';
    if (count <= 4) return 'grid-cols-2';
    return 'grid-cols-2 md:grid-cols-3';
  };

  return (
    <div className={`h-full grid gap-2 md:gap-3 auto-rows-fr ${getGridClass()}`}>
      {uniqueParticipants.map((p, idx) => (
        <VideoParticipant
          key={p.user_id || `participant-${idx}`}
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
