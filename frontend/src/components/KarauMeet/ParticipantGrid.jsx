import { useRef, useEffect, useMemo, useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Video, VideoOff, MicOff, Hand, Circle, Loader2 } from 'lucide-react';
import { useVirtualBackground } from './useVirtualBackground';

// Get background URL from background ID
const BACKGROUND_URLS = {
  'office': 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800',
  'modern-office': 'https://images.unsplash.com/photo-1497366811353-6870744d04b2?w=800',
  'home-office': 'https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=800',
  'library': 'https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=800',
  'conference': 'https://images.unsplash.com/photo-1431540015161-0bf868a2d407?w=800',
  'nature': 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800',
  'beach': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800',
  'mountains': 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800',
  'sunset': 'https://images.unsplash.com/photo-1495616811223-4d98c6e9c869?w=800',
  'garden': 'https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=800',
  'city': 'https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?w=800',
  'night-city': 'https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=800',
  'coffee-shop': 'https://images.unsplash.com/photo-1445116572660-236099ec97a0?w=800',
  'abstract': 'https://images.unsplash.com/photo-1557682250-33bd709cbe85?w=800',
  'gradient-blue': 'https://images.unsplash.com/photo-1557683316-973673baf926?w=800',
  'geometric': 'https://images.unsplash.com/photo-1558591710-4b4a1ae0f04d?w=800',
  'space': 'https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=800',
  'karau-branded': 'https://images.unsplash.com/photo-1639322537228-f710d846310a?w=800',
  'medical': 'https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=800',
};

/**
 * Individual video participant tile component with AI background support
 */
const VideoParticipant = ({ participant, isLocal, stream, isSpeaking, virtualBg }) => {
  const videoRef = useRef(null);
  const [videoElement, setVideoElement] = useState(null);

  // Determine background type and URL
  const backgroundType = isLocal ? virtualBg : 'none';
  const backgroundUrl = BACKGROUND_URLS[virtualBg] || null;
  
  // Use AI background hook for local video
  const { canvasRef, isLoading: bgLoading, isActive: bgActive } = useVirtualBackground(
    videoElement,
    backgroundType,
    backgroundUrl
  );

  useEffect(() => {
    if (videoRef.current && stream) {
      videoRef.current.srcObject = stream;
      setVideoElement(videoRef.current);
    }
  }, [stream]);

  // Determine if we should show the canvas (AI processed) or direct video
  const showProcessedVideo = isLocal && virtualBg && virtualBg !== 'none' && bgActive;

  return (
    <div className={`relative rounded-xl overflow-hidden bg-slate-900 ${isSpeaking ? 'ring-2 ring-turquoise' : ''}`}>
      {participant?.video_enabled && stream ? (
        <>
          {/* Original video (hidden when using AI background) */}
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted={isLocal}
            className={`w-full h-full object-cover ${showProcessedVideo ? 'hidden' : ''}`}
            data-testid={`video-${isLocal ? 'local' : participant?.user_id}`}
          />
          
          {/* AI processed canvas (shown when background is active) */}
          {isLocal && virtualBg && virtualBg !== 'none' && (
            <canvas
              ref={canvasRef}
              className={`w-full h-full object-cover ${showProcessedVideo ? '' : 'hidden'}`}
              data-testid="video-processed"
            />
          )}
          
          {/* Loading indicator for AI model */}
          {isLocal && bgLoading && (
            <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
              <div className="text-center">
                <Loader2 className="w-8 h-8 text-turquoise animate-spin mx-auto mb-2" />
                <span className="text-white text-sm">Loading AI model...</span>
              </div>
            </div>
          )}
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
      
      {/* Background effect badge */}
      {isLocal && virtualBg && virtualBg !== 'none' && (
        <Badge className="absolute top-2 right-2 md:top-3 md:right-3 bg-blue-500/80 text-white border-0 text-xs">
          {bgActive ? (virtualBg.includes('blur') ? 'Blur On' : 'BG On') : 'Loading...'}
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
