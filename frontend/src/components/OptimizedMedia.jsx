/**
 * Optimized Media Components & Utilities
 * 
 * Performance optimizations applied:
 * 1. Lazy loading with IntersectionObserver
 * 2. preload="metadata" for videos
 * 3. Skeleton placeholders for immediate feedback
 * 4. Memoized components to prevent re-renders
 * 5. Proper cleanup on unmount
 * 6. Hardware-accelerated transforms
 * 7. Efficient event handlers with useCallback
 */

import React, { useState, useEffect, useCallback, useRef, memo, forwardRef } from 'react';
import { Play, Pause, Loader2, Volume2, VolumeX } from 'lucide-react';

// ============== Skeleton Loaders ==============

export const VideoSkeleton = memo(({ className = "aspect-video" }) => (
  <div className={`${className} bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-800 animate-pulse rounded-lg flex items-center justify-center`}>
    <div className="w-16 h-16 bg-gray-300 dark:bg-gray-600 rounded-full flex items-center justify-center">
      <Play className="w-8 h-8 text-gray-400 dark:text-gray-500 ml-1" />
    </div>
  </div>
));

export const AudioSkeleton = memo(({ className = "h-12" }) => (
  <div className={`${className} bg-gradient-to-r from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-800 animate-pulse rounded-lg flex items-center gap-3 px-4`}>
    <div className="w-10 h-10 bg-gray-300 dark:bg-gray-600 rounded-full" />
    <div className="flex-1 space-y-2">
      <div className="h-2 bg-gray-300 dark:bg-gray-600 rounded w-3/4" />
      <div className="h-2 bg-gray-300 dark:bg-gray-600 rounded w-1/2" />
    </div>
  </div>
));

export const ThumbnailSkeleton = memo(({ className = "w-full h-40" }) => (
  <div className={`${className} bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-800 animate-pulse rounded-lg`} />
));

// ============== Lazy Image Component ==============

export const LazyImage = memo(({ 
  src, 
  alt, 
  className = "", 
  placeholder = null,
  onLoad,
  onError 
}) => {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);
  const [inView, setInView] = useState(false);
  const imgRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setInView(true);
            observer.unobserve(entry.target);
          }
        });
      },
      { rootMargin: '100px', threshold: 0.1 }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, []);

  const handleLoad = useCallback(() => {
    setLoaded(true);
    onLoad?.();
  }, [onLoad]);

  const handleError = useCallback(() => {
    setError(true);
    onError?.();
  }, [onError]);

  return (
    <div ref={imgRef} className={`relative ${className}`}>
      {/* Placeholder while loading */}
      {!loaded && !error && (
        placeholder || <ThumbnailSkeleton className="absolute inset-0" />
      )}
      
      {/* Actual image - only load when in view */}
      {inView && !error && (
        <img
          src={src}
          alt={alt}
          className={`${className} transition-opacity duration-300 ${loaded ? 'opacity-100' : 'opacity-0'}`}
          onLoad={handleLoad}
          onError={handleError}
          loading="lazy"
          decoding="async"
        />
      )}
      
      {/* Error state */}
      {error && (
        <div className={`${className} bg-gray-200 dark:bg-gray-700 flex items-center justify-center`}>
          <span className="text-gray-400 text-sm">Image unavailable</span>
        </div>
      )}
    </div>
  );
});

// ============== Optimized Video Player ==============

export const OptimizedVideoPlayer = memo(forwardRef(({ 
  src,
  poster,
  controls = true,
  autoPlay = false,
  muted = false,
  loop = false,
  playsInline = true,
  className = "",
  onLoadedMetadata,
  onCanPlay,
  onPlay,
  onPause,
  onEnded,
  onError,
  showLoadingOverlay = true,
  "data-testid": testId
}, ref) => {
  const [loading, setLoading] = useState(true);
  const [buffering, setBuffering] = useState(false);
  const [hasError, setHasError] = useState(false);
  const internalRef = useRef(null);
  const videoRef = ref || internalRef;

  const handleLoadedMetadata = useCallback((e) => {
    setLoading(false);
    onLoadedMetadata?.(e);
  }, [onLoadedMetadata]);

  const handleCanPlay = useCallback((e) => {
    setBuffering(false);
    onCanPlay?.(e);
  }, [onCanPlay]);

  const handleWaiting = useCallback(() => {
    setBuffering(true);
  }, []);

  const handlePlaying = useCallback(() => {
    setBuffering(false);
  }, []);

  const handleError = useCallback((e) => {
    setHasError(true);
    setLoading(false);
    onError?.(e);
  }, [onError]);

  // Cleanup on unmount to prevent memory leaks
  useEffect(() => {
    const video = videoRef.current;
    return () => {
      if (video) {
        video.pause();
        video.src = '';
        video.load();
      }
    };
  }, [videoRef]);

  return (
    <div className={`relative ${className}`}>
      {/* Loading/Buffering overlay */}
      {showLoadingOverlay && (loading || buffering) && !hasError && (
        <div className="absolute inset-0 bg-black/60 flex items-center justify-center z-10 rounded-lg">
          <div className="text-center text-white">
            <Loader2 className="w-10 h-10 animate-spin mx-auto mb-2" />
            <p className="text-sm">{loading ? 'Loading video...' : 'Buffering...'}</p>
          </div>
        </div>
      )}

      {/* Poster image while loading */}
      {loading && poster && (
        <div className="absolute inset-0 z-5">
          <img 
            src={poster} 
            alt="Video thumbnail" 
            className="w-full h-full object-cover rounded-lg opacity-50"
          />
        </div>
      )}

      {/* Error state */}
      {hasError && (
        <div className="absolute inset-0 bg-gray-900 flex items-center justify-center rounded-lg">
          <div className="text-center text-white">
            <p className="text-sm">Failed to load video</p>
            <button 
              onClick={() => { setHasError(false); setLoading(true); videoRef.current?.load(); }}
              className="mt-2 text-xs text-teal-400 hover:underline"
            >
              Retry
            </button>
          </div>
        </div>
      )}

      <video
        ref={videoRef}
        src={src}
        poster={poster}
        controls={controls}
        autoPlay={autoPlay}
        muted={muted}
        loop={loop}
        playsInline={playsInline}
        preload="metadata"
        className={`w-full h-full rounded-lg ${loading ? 'opacity-0' : 'opacity-100'} transition-opacity duration-300`}
        onLoadedMetadata={handleLoadedMetadata}
        onCanPlay={handleCanPlay}
        onWaiting={handleWaiting}
        onPlaying={handlePlaying}
        onPlay={onPlay}
        onPause={onPause}
        onEnded={onEnded}
        onError={handleError}
        data-testid={testId}
      />
    </div>
  );
}));

// ============== Optimized Audio Player ==============

export const OptimizedAudioPlayer = memo(forwardRef(({
  src,
  className = "",
  showWaveform = false,
  onPlay,
  onPause,
  onEnded,
  onError,
  "data-testid": testId
}, ref) => {
  const [loading, setLoading] = useState(true);
  const [playing, setPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  const [muted, setMuted] = useState(false);
  const internalRef = useRef(null);
  const audioRef = ref || internalRef;

  const handleLoadedMetadata = useCallback(() => {
    setLoading(false);
    setDuration(audioRef.current?.duration || 0);
  }, [audioRef]);

  const handleTimeUpdate = useCallback(() => {
    const audio = audioRef.current;
    if (audio && audio.duration) {
      setProgress((audio.currentTime / audio.duration) * 100);
    }
  }, [audioRef]);

  const handlePlay = useCallback(() => {
    setPlaying(true);
    onPlay?.();
  }, [onPlay]);

  const handlePause = useCallback(() => {
    setPlaying(false);
    onPause?.();
  }, [onPause]);

  const handleEnded = useCallback(() => {
    setPlaying(false);
    setProgress(0);
    onEnded?.();
  }, [onEnded]);

  const togglePlay = useCallback(() => {
    const audio = audioRef.current;
    if (audio) {
      if (playing) {
        audio.pause();
      } else {
        audio.play();
      }
    }
  }, [playing, audioRef]);

  const toggleMute = useCallback(() => {
    const audio = audioRef.current;
    if (audio) {
      audio.muted = !muted;
      setMuted(!muted);
    }
  }, [muted, audioRef]);

  const seekTo = useCallback((e) => {
    const audio = audioRef.current;
    const rect = e.currentTarget.getBoundingClientRect();
    const percent = (e.clientX - rect.left) / rect.width;
    if (audio && audio.duration) {
      audio.currentTime = percent * audio.duration;
    }
  }, [audioRef]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Cleanup
  useEffect(() => {
    const audio = audioRef.current;
    return () => {
      if (audio) {
        audio.pause();
        audio.src = '';
      }
    };
  }, [audioRef]);

  return (
    <div className={`flex items-center gap-3 p-3 bg-gray-100 dark:bg-gray-800 rounded-lg ${className}`}>
      {/* Play/Pause Button */}
      <button
        onClick={togglePlay}
        disabled={loading}
        className="w-10 h-10 flex items-center justify-center bg-teal-500 hover:bg-teal-600 text-white rounded-full transition-colors disabled:opacity-50"
        data-testid={testId ? `${testId}-play` : undefined}
      >
        {loading ? (
          <Loader2 className="w-5 h-5 animate-spin" />
        ) : playing ? (
          <Pause className="w-5 h-5" />
        ) : (
          <Play className="w-5 h-5 ml-0.5" />
        )}
      </button>

      {/* Progress Bar */}
      <div className="flex-1 flex flex-col gap-1">
        <div 
          className="h-2 bg-gray-300 dark:bg-gray-600 rounded-full cursor-pointer overflow-hidden"
          onClick={seekTo}
        >
          <div 
            className="h-full bg-teal-500 rounded-full transition-all duration-100"
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
          <span>{formatTime((progress / 100) * duration)}</span>
          <span>{formatTime(duration)}</span>
        </div>
      </div>

      {/* Mute Button */}
      <button
        onClick={toggleMute}
        className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
      >
        {muted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
      </button>

      {/* Hidden Audio Element */}
      <audio
        ref={audioRef}
        src={src}
        preload="metadata"
        onLoadedMetadata={handleLoadedMetadata}
        onTimeUpdate={handleTimeUpdate}
        onPlay={handlePlay}
        onPause={handlePause}
        onEnded={handleEnded}
        onError={onError}
        className="hidden"
      />
    </div>
  );
}));

// ============== Play Button Component ==============

export const PlayButton = memo(({ 
  onClick, 
  isPlaying = false, 
  isLoading = false,
  disabled = false,
  size = "md",
  variant = "default",
  className = "",
  "data-testid": testId
}) => {
  const sizeClasses = {
    sm: "w-8 h-8",
    md: "w-12 h-12",
    lg: "w-16 h-16",
    xl: "w-20 h-20"
  };

  const iconSizes = {
    sm: "w-4 h-4",
    md: "w-6 h-6",
    lg: "w-8 h-8",
    xl: "w-10 h-10"
  };

  const variantClasses = {
    default: "bg-white/90 hover:bg-white text-teal-600 shadow-lg",
    primary: "bg-teal-500 hover:bg-teal-600 text-white",
    outline: "border-2 border-white/80 hover:bg-white/20 text-white",
    ghost: "bg-black/40 hover:bg-black/60 text-white"
  };

  const handleClick = useCallback((e) => {
    e.stopPropagation();
    if (!disabled && !isLoading) {
      onClick?.(e);
    }
  }, [onClick, disabled, isLoading]);

  return (
    <button
      onClick={handleClick}
      disabled={disabled || isLoading}
      className={`
        ${sizeClasses[size]} 
        ${variantClasses[variant]}
        rounded-full flex items-center justify-center 
        transition-all duration-200 transform hover:scale-110
        disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none
        ${className}
      `}
      data-testid={testId}
    >
      {isLoading ? (
        <Loader2 className={`${iconSizes[size]} animate-spin`} />
      ) : isPlaying ? (
        <Pause className={iconSizes[size]} />
      ) : (
        <Play className={`${iconSizes[size]} ml-0.5`} />
      )}
    </button>
  );
});

// ============== Media Card Component ==============

export const MediaCard = memo(({ 
  title,
  description,
  thumbnail,
  duration,
  category,
  categoryColor = "bg-teal-500",
  onClick,
  className = "",
  "data-testid": testId
}) => {
  const [imageLoaded, setImageLoaded] = useState(false);

  const handleClick = useCallback(() => {
    onClick?.();
  }, [onClick]);

  return (
    <div 
      className={`bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden hover:shadow-md transition-all cursor-pointer group ${className}`}
      onClick={handleClick}
      data-testid={testId}
    >
      <div className="h-40 relative overflow-hidden">
        {/* Skeleton while image loads */}
        {!imageLoaded && (
          <div className="absolute inset-0 bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-800 animate-pulse" />
        )}
        
        <LazyImage 
          src={thumbnail} 
          alt={title}
          className={`w-full h-full object-cover group-hover:scale-105 transition-transform duration-300 ${imageLoaded ? 'opacity-100' : 'opacity-0'}`}
          onLoad={() => setImageLoaded(true)}
        />
        
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" />
        
        {/* Play button overlay */}
        <div className="absolute inset-0 flex items-center justify-center">
          <PlayButton 
            size="md" 
            variant="default"
            className="group-hover:scale-110 transition-transform"
          />
        </div>
        
        {/* Duration badge */}
        {duration && (
          <span className="absolute bottom-2 right-2 bg-black/60 text-white text-xs px-2 py-1 rounded">
            {duration}
          </span>
        )}
        
        {/* Category badge */}
        {category && (
          <span className={`absolute top-2 left-2 ${categoryColor} text-white text-xs px-2 py-1 rounded-full`}>
            {category}
          </span>
        )}
      </div>
      
      <div className="p-4">
        <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-1 line-clamp-1">{title}</h3>
        {description && (
          <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">{description}</p>
        )}
      </div>
    </div>
  );
});

// Display names for debugging
VideoSkeleton.displayName = 'VideoSkeleton';
AudioSkeleton.displayName = 'AudioSkeleton';
ThumbnailSkeleton.displayName = 'ThumbnailSkeleton';
LazyImage.displayName = 'LazyImage';
OptimizedVideoPlayer.displayName = 'OptimizedVideoPlayer';
OptimizedAudioPlayer.displayName = 'OptimizedAudioPlayer';
PlayButton.displayName = 'PlayButton';
MediaCard.displayName = 'MediaCard';

export default {
  VideoSkeleton,
  AudioSkeleton,
  ThumbnailSkeleton,
  LazyImage,
  OptimizedVideoPlayer,
  OptimizedAudioPlayer,
  PlayButton,
  MediaCard
};
