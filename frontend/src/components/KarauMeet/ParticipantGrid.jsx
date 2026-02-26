import { useRef, useEffect, useMemo, useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { MicOff, Hand, Circle, Loader2, Pin, PinOff, Grid3X3, User } from 'lucide-react';
import { useVirtualBackground } from './useVirtualBackground';

// Get background URL from background ID
const BACKGROUND_URLS = {
  'office': 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=1280&q=80',
  'modern-office': 'https://images.unsplash.com/photo-1497366811353-6870744d04b2?w=1280&q=80',
  'home-office': 'https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=1280&q=80',
  'library': 'https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=1280&q=80',
  'conference': 'https://images.unsplash.com/photo-1431540015161-0bf868a2d407?w=1280&q=80',
  'nature': 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1280&q=80',
  'beach': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1280&q=80',
  'mountains': 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=1280&q=80',
  'sunset': 'https://images.unsplash.com/photo-1495616811223-4d98c6e9c869?w=1280&q=80',
  'garden': 'https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=1280&q=80',
  'city': 'https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?w=1280&q=80',
  'night-city': 'https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=1280&q=80',
  'coffee-shop': 'https://images.unsplash.com/photo-1445116572660-236099ec97a0?w=1280&q=80',
  'abstract': 'https://images.unsplash.com/photo-1557682250-33bd709cbe85?w=1280&q=80',
  'gradient-blue': 'https://images.unsplash.com/photo-1557683316-973673baf926?w=1280&q=80',
  'geometric': 'https://images.unsplash.com/photo-1558591710-4b4a1ae0f04d?w=1280&q=80',
  'space': 'https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=1280&q=80',
  'karau-branded': 'https://images.unsplash.com/photo-1639322537228-f710d846310a?w=1280&q=80',
  'medical': 'https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=1280&q=80',
};

/**
 * Individual video participant tile component with AI background support
 */
const VideoParticipant = ({ 
  participant, 
  isLocal, 
  stream, 
  isSpeaking, 
  virtualBg,
  isPinned,
  onPin,
  onUnpin,
  isMinimized,
  showControls = true
}) => {
  const videoRef = useRef(null);
  const [videoElement, setVideoElement] = useState(null);
  const [showActions, setShowActions] = useState(false);

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

  // Minimized view - small circle avatar
  if (isMinimized) {
    return (
      <div 
        className="w-12 h-12 md:w-14 md:h-14 rounded-full overflow-hidden bg-slate-800 border-2 border-slate-600 cursor-pointer hover:border-turquoise transition-colors flex-shrink-0"
        onClick={() => onPin && onPin(participant.user_id)}
        title={`Click to view ${participant?.user_name}`}
      >
        {participant?.video_enabled && stream ? (
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted={isLocal}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-slate-700 to-slate-800">
            <span className="text-sm font-bold text-turquoise">
              {participant?.user_name?.charAt(0)?.toUpperCase() || '?'}
            </span>
          </div>
        )}
      </div>
    );
  }

  return (
    <div 
      className={`relative w-full h-full rounded-xl overflow-hidden bg-slate-900 transition-all duration-200 ${isSpeaking ? 'ring-[3px] ring-emerald-500 shadow-lg shadow-emerald-500/20' : ''} ${isPinned ? 'ring-2 ring-yellow-500' : ''}`}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
      onTouchStart={() => setShowActions(true)}
    >
      {participant?.video_enabled && stream ? (
        <>
          {/* Original video (hidden when using AI background) */}
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted={isLocal}
            className={`absolute inset-0 w-full h-full object-cover ${showProcessedVideo ? 'hidden' : ''}`}
            data-testid={`video-${isLocal ? 'local' : participant?.user_id}`}
          />
          
          {/* AI processed canvas (shown when background is active) */}
          {isLocal && virtualBg && virtualBg !== 'none' && (
            <canvas
              ref={canvasRef}
              className={`absolute inset-0 w-full h-full object-cover ${showProcessedVideo ? '' : 'hidden'}`}
              data-testid="video-processed"
            />
          )}
          
          {/* Loading indicator for AI model */}
          {isLocal && bgLoading && (
            <div className="absolute inset-0 bg-black/50 flex items-center justify-center z-10">
              <div className="text-center">
                <Loader2 className="w-6 h-6 text-turquoise animate-spin mx-auto mb-1" />
                <span className="text-white text-xs">Loading AI...</span>
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-slate-800 to-slate-900">
          <div className="w-16 h-16 md:w-20 md:h-20 rounded-full bg-turquoise/20 flex items-center justify-center">
            <span className="text-2xl md:text-3xl font-bold text-turquoise">
              {participant?.user_name?.charAt(0)?.toUpperCase() || '?'}
            </span>
          </div>
        </div>
      )}

      {/* Pin/Unpin actions - show on hover */}
      {showControls && showActions && !isLocal && (
        <div className="absolute top-2 right-2 z-20 flex gap-1">
          {isPinned ? (
            <Button
              size="sm"
              variant="secondary"
              className="h-7 w-7 p-0 bg-yellow-500 hover:bg-yellow-600"
              onClick={() => onUnpin && onUnpin()}
              title="Unpin"
            >
              <PinOff className="w-3.5 h-3.5" />
            </Button>
          ) : (
            <Button
              size="sm"
              variant="secondary"
              className="h-7 w-7 p-0 bg-slate-700/80 hover:bg-slate-600"
              onClick={() => onPin && onPin(participant.user_id)}
              title="Pin to spotlight"
            >
              <Pin className="w-3.5 h-3.5" />
            </Button>
          )}
        </div>
      )}
      
      {/* Background effect badge */}
      {isLocal && virtualBg && virtualBg !== 'none' && (
        <Badge className="absolute top-2 right-2 md:top-3 md:right-3 bg-blue-500/80 text-white border-0 text-xs z-10">
          {bgActive ? (virtualBg.includes('blur') ? 'Blur' : 'BG') : '...'}
        </Badge>
      )}
      
      {/* Pinned badge */}
      {isPinned && (
        <Badge className="absolute top-2 left-2 bg-yellow-500 text-black border-0 text-xs z-10">
          <Pin className="w-3 h-3 mr-1" />
          Pinned
        </Badge>
      )}
      
      {/* Name badge */}
      <div className="absolute bottom-2 md:bottom-3 left-2 md:left-3 flex items-center gap-1 md:gap-2 z-10">
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
      {participant?.is_host && !isPinned && (
        <Badge className="absolute top-2 md:top-3 left-2 md:left-3 bg-turquoise text-white border-0 text-xs z-10">
          Host
        </Badge>
      )}
      
      {/* Recording indicator */}
      {participant?.is_recording && (
        <Badge className="absolute top-2 md:top-3 right-2 md:right-3 bg-red-500 text-white border-0 animate-pulse text-xs z-10">
          <Circle className="w-2 h-2 mr-1 fill-current" />
          REC
        </Badge>
      )}
    </div>
  );
};

/**
 * Grid layout for all participants in a meeting
 * Supports: Gallery view, Spotlight view, Pin participant, Focus mode
 */
const ParticipantGrid = ({ participants, localStream, remoteStreams, localUserId, virtualBackground, activeSpeakerId }) => {
  const [viewMode, setViewMode] = useState('gallery'); // 'gallery' | 'spotlight' | 'focus'
  const [pinnedUserId, setPinnedUserId] = useState(null);

  // Deduplicate participants by user_id
  const uniqueParticipants = useMemo(() => {
    const seen = new Map();
    participants.forEach(p => {
      if (p.user_id) {
        seen.set(p.user_id, p);
      }
    });
    return Array.from(seen.values());
  }, [participants]);
  
  const count = uniqueParticipants.length;

  // Handle pin/unpin
  const handlePin = (userId) => {
    setPinnedUserId(userId);
    setViewMode('spotlight');
  };

  const handleUnpin = () => {
    setPinnedUserId(null);
    setViewMode('gallery');
  };

  // Show all in gallery
  const showGallery = () => {
    setViewMode('gallery');
    setPinnedUserId(null);
  };

  // Focus on self, minimize others
  const showFocus = () => {
    setViewMode('focus');
    setPinnedUserId(null);
  };

  // Get pinned participant
  const pinnedParticipant = pinnedUserId 
    ? uniqueParticipants.find(p => p.user_id === pinnedUserId) 
    : null;

  // Other participants (not pinned, not local for focus mode)
  const otherParticipants = uniqueParticipants.filter(p => p.user_id !== pinnedUserId);
  const localParticipant = uniqueParticipants.find(p => p.user_id === localUserId);
  const remoteParticipants = uniqueParticipants.filter(p => p.user_id !== localUserId);

  // Gallery view grid classes based on count
  const getGalleryGridClass = () => {
    if (count === 1) return 'flex justify-center items-center';
    if (count === 2) return 'grid grid-cols-2 gap-2';
    if (count <= 4) return 'grid grid-cols-2 gap-2';
    if (count <= 6) return 'grid grid-cols-2 md:grid-cols-3 gap-2';
    if (count <= 9) return 'grid grid-cols-3 gap-2';
    return 'grid grid-cols-3 md:grid-cols-4 gap-1.5';
  };

  return (
    <div className="w-full h-full flex flex-col">
      {/* View mode controls */}
      <div className="flex items-center justify-between px-2 py-1.5 flex-shrink-0">
        <div className="flex items-center gap-1">
          <Button
            size="sm"
            variant={viewMode === 'gallery' ? 'default' : 'ghost'}
            className={`h-7 px-2 text-xs ${viewMode === 'gallery' ? 'bg-turquoise' : 'text-slate-400'}`}
            onClick={showGallery}
          >
            <Grid3X3 className="w-3.5 h-3.5 mr-1" />
            Gallery
          </Button>
          {count > 1 && (
            <Button
              size="sm"
              variant={viewMode === 'focus' ? 'default' : 'ghost'}
              className={`h-7 px-2 text-xs ${viewMode === 'focus' ? 'bg-turquoise' : 'text-slate-400'}`}
              onClick={showFocus}
            >
              <User className="w-3.5 h-3.5 mr-1" />
              Focus
            </Button>
          )}
        </div>
        <span className="text-xs text-slate-500">{count} participant{count !== 1 ? 's' : ''}</span>
      </div>

      {/* Main content */}
      <div className="flex-1 overflow-hidden p-1 min-h-0">
        {/* Spotlight view - pinned user large, others as thumbnails */}
        {viewMode === 'spotlight' && pinnedParticipant && (
          <div className="h-full flex flex-col gap-2">
            {/* Main pinned video */}
            <div className="flex-1 min-h-0">
              <VideoParticipant
                participant={pinnedParticipant}
                isLocal={pinnedParticipant.user_id === localUserId}
                stream={pinnedParticipant.user_id === localUserId ? localStream : remoteStreams[pinnedParticipant.user_id]}
                virtualBg={pinnedParticipant.user_id === localUserId ? virtualBackground : null}
                isPinned={true}
                onUnpin={handleUnpin}
                isSpeaking={activeSpeakerId === pinnedParticipant.user_id}
              />
            </div>
            
            {/* Thumbnail strip */}
            {otherParticipants.length > 0 && (
              <div className="h-20 md:h-24 flex gap-2 overflow-x-auto py-1 px-1 flex-shrink-0">
                {otherParticipants.map((p) => (
                  <div key={p.user_id} className="w-28 md:w-36 h-full flex-shrink-0">
                    <VideoParticipant
                      participant={p}
                      isLocal={p.user_id === localUserId}
                      stream={p.user_id === localUserId ? localStream : remoteStreams[p.user_id]}
                      virtualBg={p.user_id === localUserId ? virtualBackground : null}
                      onPin={handlePin}
                      showControls={true}
                      isSpeaking={activeSpeakerId === p.user_id}
                    />
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Focus view - local user large, others minimized as circles */}
        {viewMode === 'focus' && (
          <div className="h-full flex flex-col gap-2">
            {/* Local user large */}
            <div className="flex-1 min-h-0">
              {localParticipant && (
                <VideoParticipant
                  participant={localParticipant}
                  isLocal={true}
                  stream={localStream}
                  virtualBg={virtualBackground}
                  showControls={false}
                  isSpeaking={activeSpeakerId === localParticipant.user_id}
                />
              )}
            </div>
            
            {/* Minimized participants strip */}
            {remoteParticipants.length > 0 && (
              <div className="flex gap-2 justify-center py-2 flex-shrink-0 flex-wrap">
                {remoteParticipants.map((p) => (
                  <VideoParticipant
                    key={p.user_id}
                    participant={p}
                    isLocal={false}
                    stream={remoteStreams[p.user_id]}
                    isMinimized={true}
                    onPin={handlePin}
                    isSpeaking={activeSpeakerId === p.user_id}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Gallery view - all participants in grid */}
        {viewMode === 'gallery' && (
          <div className={`h-full ${getGalleryGridClass()}`}>
            {uniqueParticipants.map((p) => (
              <div 
                key={p.user_id} 
                className={count === 1 ? 'w-full max-w-3xl aspect-video mx-auto' : 'aspect-video'}
              >
                <VideoParticipant
                  participant={p}
                  isLocal={p.user_id === localUserId}
                  stream={p.user_id === localUserId ? localStream : remoteStreams[p.user_id]}
                  virtualBg={p.user_id === localUserId ? virtualBackground : null}
                  onPin={handlePin}
                  showControls={count > 1}
                  isSpeaking={activeSpeakerId === p.user_id}
                />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export { VideoParticipant, ParticipantGrid };
export default ParticipantGrid;
