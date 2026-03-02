import { memo, useRef, useEffect, useMemo } from 'react';
import { Crown, Clipboard, Radio } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import SlideRenderer from '@/components/KarauMeet/SlideRenderer';
import EnhancedWhiteboard from '@/components/KarauMeet/EnhancedWhiteboard';

const RemoteVideo = memo(function RemoteVideo({ stream, name, userId, isSpeaking, speakerColor, onPromoteToStage }) {
  const ref = useRef(null);
  useEffect(() => { if (ref.current && stream) ref.current.srcObject = stream; }, [stream]);
  return (
    <div className={`relative rounded-lg overflow-hidden bg-karau-card/60 border aspect-video transition-all cursor-pointer ${isSpeaking ? 'border-2' : 'border-white/5'}`}
      style={isSpeaking ? { borderColor: speakerColor } : {}}
      onClick={onPromoteToStage} title="Click to spotlight" data-testid={`remote-${userId}`}>
      <video ref={ref} autoPlay playsInline className="w-full h-full object-cover" />
      <div className="absolute bottom-1 left-1 bg-black/60 backdrop-blur-sm rounded px-1 py-0.5 flex items-center gap-1">
        {isSpeaking && <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ backgroundColor: speakerColor }} />}
        <span className="text-[8px] text-white">{name}</span>
      </div>
    </div>
  );
});

const MainStageVideo = memo(function MainStageVideo({ stream, name, color }) {
  const ref = useRef(null);
  useEffect(() => { if (ref.current && stream) ref.current.srcObject = stream; }, [stream]);
  return (
    <div className="absolute inset-0 z-0" data-testid="main-stage-video">
      <video ref={ref} autoPlay playsInline className="w-full h-full object-cover" />
      <div className="absolute bottom-3 left-3 flex items-center gap-2 bg-black/50 backdrop-blur-md rounded-full px-3 py-1.5">
        <span className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: color || '#a78bfa' }} />
        <span className="text-xs text-white font-medium">{name}</span>
        <Badge className="bg-purple-500/20 text-purple-300 border-purple-500/30 text-[8px]">Speaking</Badge>
      </div>
    </div>
  );
});

export const VideoStage = memo(function VideoStage({
  showWhiteboard, webinarId, onCloseWhiteboard,
  showSlides, currentSlide, onSlideChange, canDriveSlides, wsRef,
  localVideoRef, canStream, isCamOn, eyeContactOn,
  myRole, hostName, roomInfo,
  mainStageUserId, remoteStreams, speakerDetection,
  onSetMainStage,
}) {
  const isHost = myRole === 'host';
  const isCoord = myRole === 'coordinator';
  const remoteStreamEntries = useMemo(() => Object.entries(remoteStreams), [remoteStreams]);

  return (
    <div className="flex-1 p-2 flex gap-2" data-testid="video-stage">
      {showWhiteboard ? (
        <div className="flex-1" data-testid="whiteboard-container">
          <EnhancedWhiteboard meetingId={webinarId} onClose={onCloseWhiteboard} />
        </div>
      ) : (
        <>
          {showSlides && (
            <div className="flex-1 relative rounded-xl overflow-hidden">
              <SlideRenderer webinarId={webinarId} currentSlide={currentSlide}
                onSlideChange={(idx) => { onSlideChange(idx); wsRef.current?.send(JSON.stringify({ type: 'slide_change', slide_index: idx })); }}
                canDrive={canDriveSlides} ws={wsRef} />
            </div>
          )}

          <div className={`relative rounded-xl overflow-hidden bg-karau-card/40 border transition-all duration-500 ${showSlides ? 'w-56 shrink-0' : 'flex-1'} ${speakerDetection.speakers['__local__']?.speaking ? 'border-2' : 'border-white/5'}`}
            style={speakerDetection.speakers['__local__']?.speaking ? { borderColor: speakerDetection.speakers['__local__']?.color } : {}}>

            {!showSlides && mainStageUserId && remoteStreams[mainStageUserId] && (
              <MainStageVideo stream={remoteStreams[mainStageUserId].stream} name={remoteStreams[mainStageUserId].name}
                color={speakerDetection.speakers[mainStageUserId]?.color} />
            )}

            {canStream ? (
              <div className={mainStageUserId && remoteStreams[mainStageUserId] && !showSlides
                ? 'absolute bottom-2 right-2 w-32 h-24 rounded-lg overflow-hidden border-2 border-white/20 shadow-xl z-10 transition-all duration-500'
                : 'w-full h-full'}>
                <video ref={localVideoRef} autoPlay muted playsInline className="w-full h-full object-cover"
                  style={eyeContactOn ? { transform: 'scaleX(-1) perspective(800px) rotateY(2deg) translateY(-2%)', filter: 'contrast(1.02) brightness(1.01)' } : { transform: 'scaleX(-1)' }}
                  data-testid="local-video" />
                {!isCamOn && (
                  <div className="absolute inset-0 flex items-center justify-center bg-karau-card/80">
                    <div className={`${showSlides ? 'w-10 h-10' : mainStageUserId ? 'w-8 h-8' : 'w-16 h-16'} rounded-full bg-purple-500/20 flex items-center justify-center`}>
                      <span className={`${showSlides ? 'text-lg' : mainStageUserId ? 'text-sm' : 'text-2xl'} font-bold text-purple-400`}>{hostName?.[0] || 'H'}</span>
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
                  {!showSlides && <p className="text-white font-medium text-sm">{roomInfo?.title}</p>}
                  <p className="text-[9px] text-karau-muted mt-0.5">{roomInfo?.status === 'live' ? hostName : 'Waiting...'}</p>
                </div>
              </div>
            )}
          </div>

          {remoteStreamEntries.length > 0 && (
            <div className="w-36 flex flex-col gap-1 overflow-y-auto shrink-0">
              {remoteStreamEntries
                .filter(([uid]) => uid !== mainStageUserId || showSlides)
                .map(([uid, { stream, name }]) => (
                  <RemoteVideo key={uid} stream={stream} name={name} userId={uid}
                    isSpeaking={speakerDetection.speakers[uid]?.speaking}
                    speakerColor={speakerDetection.speakers[uid]?.color}
                    onPromoteToStage={() => onSetMainStage(uid)} />
                ))}
            </div>
          )}
        </>
      )}
    </div>
  );
});
