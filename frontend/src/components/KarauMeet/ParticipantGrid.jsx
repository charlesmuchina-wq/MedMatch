import { useRef, useEffect, useMemo } from 'react';
import { Badge } from '@/components/ui/badge';
import { Video, VideoOff, MicOff, Hand, Circle } from 'lucide-react';

/**
 * Individual video participant tile component
 * Supports blur effects - image backgrounds require ML (TensorFlow.js BodyPix)
 */
const VideoParticipant = ({ participant, isLocal, stream, isSpeaking, virtualBg }) => {
  const videoRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    if (videoRef.current && stream) {
      videoRef.current.srcObject = stream;
    }
  }, [stream]);

  // Apply blur effect based on virtual background setting
  const getBlurStyles = useMemo(() => {
    if (!isLocal || !virtualBg) return {};
    
    switch (virtualBg) {
      case 'blur':
        // Standard blur - adds a frosted glass effect around the edges
        return {
          containerClass: 'blur-bg-active',
          videoStyle: {},
          overlayStyle: {
            position: 'absolute',
            inset: 0,
            backdropFilter: 'blur(8px)',
            WebkitBackdropFilter: 'blur(8px)',
            maskImage: 'radial-gradient(ellipse 70% 80% at 50% 40%, transparent 50%, black 70%)',
            WebkitMaskImage: 'radial-gradient(ellipse 70% 80% at 50% 40%, transparent 50%, black 70%)',
            pointerEvents: 'none',
          }
        };
      case 'blur-light':
        return {
          containerClass: 'blur-bg-light',
          videoStyle: {},
          overlayStyle: {
            position: 'absolute',
            inset: 0,
            backdropFilter: 'blur(4px)',
            WebkitBackdropFilter: 'blur(4px)',
            maskImage: 'radial-gradient(ellipse 75% 85% at 50% 40%, transparent 55%, black 75%)',
            WebkitMaskImage: 'radial-gradient(ellipse 75% 85% at 50% 40%, transparent 55%, black 75%)',
            pointerEvents: 'none',
          }
        };
      case 'blur-heavy':
        return {
          containerClass: 'blur-bg-heavy',
          videoStyle: {},
          overlayStyle: {
            position: 'absolute',
            inset: 0,
            backdropFilter: 'blur(16px)',
            WebkitBackdropFilter: 'blur(16px)',
            maskImage: 'radial-gradient(ellipse 60% 70% at 50% 40%, transparent 40%, black 60%)',
            WebkitMaskImage: 'radial-gradient(ellipse 60% 70% at 50% 40%, transparent 40%, black 60%)',
            pointerEvents: 'none',
          }
        };
      default:
        return {};
    }
  }, [virtualBg, isLocal]);

  const { containerClass = '', videoStyle = {}, overlayStyle } = getBlurStyles;

  return (
    <div 
      ref={containerRef}
      className={`relative rounded-xl overflow-hidden bg-slate-900 ${isSpeaking ? 'ring-2 ring-turquoise' : ''} ${containerClass}`}
    >
      {participant?.video_enabled && stream ? (
        <>
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted={isLocal}
            className="w-full h-full object-cover"
            style={videoStyle}
            data-testid={`video-${isLocal ? 'local' : participant?.user_id}`}
          />
          {/* Blur overlay for background effect */}
          {overlayStyle && <div style={overlayStyle} />}
        </>
      ) : (
        <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-slate-800 to-slate-900 min-h-[120px] md:min-h-[200px]">
          <div className="w-14 h-14 md:w-20 md:h-20 rounded-full bg-turquoise/20 flex items-center justify-center">
            <span className="text-xl md:text-3xl font-bold text-turquoise">
              {participant?.user_name?.charAt(0)?.toUpperCase() || '?'}
            </span>
          </div>
        </div>
      )}
      
      {/* Blur indicator badge */}
      {isLocal && virtualBg && virtualBg.includes('blur') && (
        <Badge className="absolute top-2 right-2 md:top-3 md:right-3 bg-blue-500/80 text-white border-0 text-xs">
          Blur On
        </Badge>
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
