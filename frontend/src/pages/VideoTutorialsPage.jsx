import React, { useState, useEffect, useCallback, useMemo, useRef, memo } from 'react';
import { Play, FileText, Users, Briefcase, Search, ClipboardList, ChevronRight, ExternalLink, Loader2, Globe, Subtitles } from 'lucide-react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

const LANGUAGES = [
  { code: 'en', name: 'English' },
  { code: 'es', name: 'Spanish' },
  { code: 'fr', name: 'French' },
  { code: 'de', name: 'German' },
  { code: 'zh', name: 'Chinese' },
  { code: 'ja', name: 'Japanese' },
  { code: 'pt', name: 'Portuguese' },
  { code: 'ar', name: 'Arabic' },
  { code: 'hi', name: 'Hindi' },
  { code: 'ko', name: 'Korean' },
  { code: 'it', name: 'Italian' },
  { code: 'ru', name: 'Russian' },
  { code: 'sw', name: 'Swahili' },
  { code: 'tl', name: 'Tagalog' },
  { code: 'vi', name: 'Vietnamese' }
];

// Presenter images for each video - diverse presenters
const PRESENTER_IMAGES = {
  "01_jobseeker_features": "/images/presenter_1_black_woman.jpeg",
  "02_recruiter_features": "/images/presenter_2_pacific_islander.jpeg",
  "03_privacy_matters": "/images/presenter_3_asian_male.jpeg",
  "04_faq_ai_compliance": "/images/presenter_4_native_american.jpeg",
  "05_complete_overview": "/images/presenter_main.jpeg"
};

// Custom category labels for display
const CATEGORY_LABELS = {
  "job_seeker": "Job Seeker",
  "recruiter": "Recruiter",
  "03_privacy_matters": "Data Privacy",
  "04_faq_ai_compliance": "FAQs - AI",
  "05_complete_overview": "Overview"
};

// Skeleton loader for video cards - provides immediate visual feedback
const VideoCardSkeleton = memo(() => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden animate-pulse">
    <div className="h-40 bg-gray-200 relative">
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="w-14 h-14 bg-gray-300 rounded-full" />
      </div>
    </div>
    <div className="p-4 space-y-2">
      <div className="h-4 bg-gray-200 rounded w-3/4" />
      <div className="h-3 bg-gray-200 rounded w-full" />
      <div className="h-3 bg-gray-200 rounded w-2/3" />
    </div>
  </div>
));

// Optimized Image component with lazy loading and placeholder
const LazyImage = memo(({ src, alt, className, onLoad }) => {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);
  const imgRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && imgRef.current) {
            imgRef.current.src = src;
            observer.unobserve(entry.target);
          }
        });
      },
      { rootMargin: '50px' }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, [src]);

  const handleLoad = useCallback(() => {
    setLoaded(true);
    onLoad?.();
  }, [onLoad]);

  const handleError = useCallback(() => {
    setError(true);
  }, []);

  return (
    <div className={`relative ${className}`}>
      {/* Low-res placeholder / skeleton */}
      {!loaded && !error && (
        <div className="absolute inset-0 bg-gradient-to-br from-gray-200 to-gray-300 animate-pulse" />
      )}
      <img
        ref={imgRef}
        alt={alt}
        className={`${className} transition-opacity duration-300 ${loaded ? 'opacity-100' : 'opacity-0'}`}
        onLoad={handleLoad}
        onError={handleError}
        loading="lazy"
        decoding="async"
      />
      {error && (
        <div className="absolute inset-0 bg-gray-200 flex items-center justify-center">
          <span className="text-gray-400 text-sm">Image unavailable</span>
        </div>
      )}
    </div>
  );
});

// Memoized VideoCard component to prevent unnecessary re-renders
const VideoCard = memo(({ video, onSelect }) => {
  const presenterImage = PRESENTER_IMAGES[video.id] || "/images/presenter.jpeg";
  
  const getCategoryLabel = useCallback(() => {
    if (CATEGORY_LABELS[video.id]) {
      return CATEGORY_LABELS[video.id];
    }
    return video.category === 'job_seeker' ? 'Job Seeker' : video.category === 'recruiter' ? 'Recruiter' : 'Everyone';
  }, [video.id, video.category]);

  const handleClick = useCallback(() => {
    onSelect(video);
  }, [video, onSelect]);
  
  return (
    <div 
      className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-all cursor-pointer group"
      onClick={handleClick}
      data-testid={`video-card-${video.id}`}
    >
      <div className="h-40 relative overflow-hidden">
        <LazyImage 
          src={presenterImage} 
          alt="Tutorial Presenter"
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-14 h-14 bg-white/90 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform shadow-lg">
            <Play className="w-7 h-7 text-teal-600 ml-1" />
          </div>
        </div>
        <span className="absolute bottom-2 right-2 bg-black/60 text-white text-xs px-2 py-1 rounded">
          {video.duration}
        </span>
        <span className={`absolute top-2 left-2 ${video.color} text-white text-xs px-2 py-1 rounded-full`}>
          {getCategoryLabel()}
        </span>
      </div>
      <div className="p-4">
        <h3 className="font-semibold text-gray-900 mb-1">{video.title}</h3>
        <p className="text-sm text-gray-600 line-clamp-2">{video.description}</p>
      </div>
    </div>
  );
});

// Optimized Video Modal with preload="metadata" and efficient loading
const VideoModal = memo(({ video, onClose, selectedLanguage, setSelectedLanguage, showSubtitles, setShowSubtitles }) => {
  const [translating, setTranslating] = useState(false);
  const [videoLoaded, setVideoLoaded] = useState(false);
  const [buffering, setBuffering] = useState(true);
  const videoRef = useRef(null);

  // Handle video events for loading states - defined before early return
  const handleLoadedMetadata = useCallback(() => {
    setVideoLoaded(true);
  }, []);

  const handleCanPlay = useCallback(() => {
    setBuffering(false);
  }, []);

  const handleWaiting = useCallback(() => {
    setBuffering(true);
  }, []);

  const handlePlaying = useCallback(() => {
    setBuffering(false);
  }, []);

  // Cleanup on unmount - defined before early return
  useEffect(() => {
    return () => {
      if (videoRef.current) {
        videoRef.current.pause();
        videoRef.current.src = '';
        videoRef.current.load();
      }
    };
  }, []);

  // Early return AFTER all hooks
  if (!video) return null;
  
  const videoUrl = selectedLanguage === 'en' 
    ? video.file 
    : `${video.file}?lang=${selectedLanguage}`;
  
  const subtitleUrl = `${API}/api/tutorials/subtitles/${video.id}?lang=${selectedLanguage}`;
  
  const requestTranslation = async () => {
    setTranslating(true);
    try {
      await axios.post(`${API}/api/tutorials/translate/${video.id}?lang=${selectedLanguage}`);
      const checkStatus = async () => {
        const res = await axios.get(`${API}/api/tutorials/translate/${video.id}/status?lang=${selectedLanguage}`);
        if (res.data.status === 'ready') {
          setTranslating(false);
        } else if (res.data.status === 'generating') {
          setTimeout(checkStatus, 3000);
        } else {
          setTranslating(false);
        }
      };
      checkStatus();
    } catch (error) {
      console.error('Translation request failed:', error);
      setTranslating(false);
    }
  };
  
  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-white rounded-xl max-w-4xl w-full overflow-hidden" onClick={e => e.stopPropagation()}>
        <div className="p-4 border-b flex justify-between items-center">
          <h3 className="font-semibold text-lg">{video.title}</h3>
          <div className="flex items-center gap-4">
            {/* Language Selector */}
            <div className="flex items-center gap-2">
              <Globe className="w-4 h-4 text-gray-500" />
              <select 
                value={selectedLanguage}
                onChange={(e) => setSelectedLanguage(e.target.value)}
                className="text-sm border rounded px-2 py-1"
              >
                {LANGUAGES.map(lang => (
                  <option key={lang.code} value={lang.code}>{lang.name}</option>
                ))}
              </select>
            </div>
            {/* Subtitles Toggle */}
            <button 
              onClick={() => setShowSubtitles(!showSubtitles)}
              className={`flex items-center gap-1 text-sm px-2 py-1 rounded ${showSubtitles ? 'bg-teal-100 text-teal-700' : 'bg-gray-100 text-gray-600'}`}
            >
              <Subtitles className="w-4 h-4" />
              CC
            </button>
            <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
              ✕
            </button>
          </div>
        </div>
        <div className="aspect-video bg-black relative">
          {/* Loading/Buffering overlay */}
          {(translating || buffering) && (
            <div className="absolute inset-0 bg-black/80 flex flex-col items-center justify-center text-white z-10">
              <Loader2 className="w-8 h-8 animate-spin mb-2" />
              <p>{translating 
                ? `Generating ${LANGUAGES.find(l => l.code === selectedLanguage)?.name} version...`
                : 'Loading video...'
              }</p>
              {translating && <p className="text-sm text-gray-400">This may take a minute</p>}
            </div>
          )}
          
          {/* Poster/Thumbnail while video loads */}
          {!videoLoaded && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-900">
              <img 
                src={PRESENTER_IMAGES[video.id] || "/images/presenter.jpeg"}
                alt="Video thumbnail"
                className="w-full h-full object-contain opacity-50"
              />
            </div>
          )}
          
          <video 
            ref={videoRef}
            src={videoUrl} 
            controls 
            autoPlay
            preload="metadata"
            playsInline
            className={`w-full h-full ${videoLoaded ? 'opacity-100' : 'opacity-0'}`}
            data-testid="video-player"
            crossOrigin="anonymous"
            onLoadedMetadata={handleLoadedMetadata}
            onCanPlay={handleCanPlay}
            onWaiting={handleWaiting}
            onPlaying={handlePlaying}
            poster={PRESENTER_IMAGES[video.id] || "/images/presenter.jpeg"}
          >
            {showSubtitles && (
              <track 
                kind="subtitles" 
                src={subtitleUrl}
                srcLang={selectedLanguage}
                label={LANGUAGES.find(l => l.code === selectedLanguage)?.name || 'English'}
                default
              />
            )}
            Your browser does not support video playback.
          </video>
        </div>
        <div className="p-4">
          <p className="text-gray-600 mb-3">{video.description}</p>
          {selectedLanguage !== 'en' && (
            <button
              onClick={requestTranslation}
              disabled={translating}
              className="text-sm bg-teal-500 text-white px-3 py-1 rounded hover:bg-teal-600 disabled:opacity-50"
            >
              {translating ? 'Generating...' : `Generate ${LANGUAGES.find(l => l.code === selectedLanguage)?.name} Audio`}
            </button>
          )}
        </div>
      </div>
    </div>
  );
});

const VideoTutorialsPage = () => {
  const [activeTab, setActiveTab] = useState('videos');
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [showSubtitles, setShowSubtitles] = useState(true);

  useEffect(() => {
    fetchVideos();
  }, []);

  const fetchVideos = async () => {
    try {
      const response = await axios.get(`${API}/api/tutorials/videos`);
      const videosData = response.data.videos.map(v => ({
        ...v,
        icon: v.category === 'job_seeker' ? Users : v.category === 'recruiter' ? Briefcase : Search,
        color: v.category === 'job_seeker' ? 'bg-teal-500' : v.category === 'recruiter' ? 'bg-purple-500' : v.category === 'overview' ? 'bg-emerald-500' : 'bg-blue-500',
        file: `${API}${v.url}`
      }));
      setVideos(videosData);
    } catch (error) {
      console.error('Failed to fetch videos:', error);
      // Fallback to static data
      setVideos([
        {
          id: '01_jobseeker_features',
          title: 'Job Seeker Features',
          description: 'Complete guide to dashboard, job search, resume, applications, and interview prep',
          duration: '40 seconds',
          category: 'job_seeker',
          icon: Users,
          file: `${API}/api/tutorials/videos/01_jobseeker_features`,
          color: 'bg-teal-500'
        },
        {
          id: '02_recruiter_features',
          title: 'Recruiter Features',
          description: 'Dashboard, applicant tracking, job postings, and hiring tools',
          duration: '28 seconds',
          category: 'recruiter',
          icon: Briefcase,
          file: `${API}/api/tutorials/videos/02_recruiter_features`,
          color: 'bg-purple-500'
        },
        {
          id: '03_privacy_matters',
          title: 'Your Privacy Matters',
          description: 'How we protect your data and keep your job search secure',
          duration: '34 seconds',
          category: 'general',
          icon: Search,
          file: `${API}/api/tutorials/videos/03_privacy_matters`,
          color: 'bg-blue-500'
        },
        {
          id: '04_faq_ai_compliance',
          title: 'FAQs: AI Compliance & Data Rights',
          description: 'Understanding AI usage, data ownership, GDPR compliance',
          duration: '52 seconds',
          category: 'general',
          icon: Search,
          file: `${API}/api/tutorials/videos/04_faq_ai_compliance`,
          color: 'bg-blue-500'
        },
        {
          id: '05_complete_overview',
          title: 'Complete MedMatch Overview',
          description: 'Comprehensive summary of all MedMatch features',
          duration: '85 seconds',
          category: 'overview',
          icon: Search,
          file: `${API}/api/tutorials/videos/05_complete_overview`,
          color: 'bg-emerald-500'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Memoize quick guides data
  const quickGuides = useMemo(() => [
    {
      title: 'For Job Seekers',
      items: [
        { step: '1', title: 'Sign In', desc: 'Use Google, Apple, Email, or Phone to create your account' },
        { step: '2', title: 'Upload Resume', desc: 'Drag & drop your resume or import from cloud storage' },
        { step: '3', title: 'Complete Profile', desc: 'Add credentials, skills, and preferences to boost your Trust Score' },
        { step: '4', title: 'Search Jobs', desc: 'Use filters and AI matching to find perfect opportunities' },
        { step: '5', title: 'Apply & Track', desc: 'Submit applications and monitor your pipeline' }
      ]
    },
    {
      title: 'For Recruiters',
      items: [
        { step: '1', title: 'Access Dashboard', desc: 'View hiring metrics, active postings, and candidate pipeline' },
        { step: '2', title: 'Create Job Posting', desc: 'Add job details, requirements, and screening questions' },
        { step: '3', title: 'Generate Application Links', desc: 'Create shareable links for candidates to apply' },
        { step: '4', title: 'Review Applications', desc: 'Screen candidates, update statuses, send notifications' },
        { step: '5', title: 'Hire Top Talent', desc: 'Move candidates through your pipeline to successful hires' }
      ]
    }
  ], []);

  // Memoize video selection handler
  const handleVideoSelect = useCallback((video) => {
    setSelectedVideo(video);
  }, []);

  // Memoize modal close handler
  const handleCloseModal = useCallback(() => {
    setSelectedVideo(null);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-teal-600 to-teal-700 text-white py-12 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row items-center gap-8">
            <div className="flex-1">
              <h1 className="text-3xl md:text-4xl font-bold mb-4">Help & Tutorials</h1>
              <p className="text-teal-100 text-lg mb-6">
                Learn how to make the most of MedMatch with our video guides and quick-start tutorials.
              </p>
              <div className="flex gap-3">
                <button 
                  onClick={() => setActiveTab('getting-started')}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${activeTab === 'getting-started' ? 'bg-white text-teal-700' : 'bg-teal-500 text-white hover:bg-teal-400'}`}
                >
                  🎬 Getting Started
                </button>
                <button 
                  onClick={() => setActiveTab('videos')}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${activeTab === 'videos' ? 'bg-white text-teal-700' : 'bg-teal-500 text-white hover:bg-teal-400'}`}
                >
                  Video Tutorials
                </button>
                <button 
                  onClick={() => setActiveTab('guides')}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${activeTab === 'guides' ? 'bg-white text-teal-700' : 'bg-teal-500 text-white hover:bg-teal-400'}`}
                >
                  Quick Guides
                </button>
              </div>
            </div>
            <div className="w-48 h-48 rounded-full overflow-hidden border-4 border-white/30 shadow-xl">
              <LazyImage 
                src="/images/presenter.jpeg" 
                alt="MedMatch Guide"
                className="w-full h-full object-cover"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div className="max-w-6xl mx-auto py-8 px-4">
        {/* Getting Started - AI Avatar Tutorials */}
        {activeTab === 'getting-started' && (
          <GettingStartedSection />
        )}

        {activeTab === 'videos' ? (
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Video Tutorials</h2>
            
            {loading ? (
              // Skeleton loading state
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[1, 2, 3, 4, 5].map(i => (
                  <VideoCardSkeleton key={i} />
                ))}
              </div>
            ) : (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {videos.map(video => (
                  <VideoCard 
                    key={video.id} 
                    video={video} 
                    onSelect={handleVideoSelect}
                  />
                ))}
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-8">
            {quickGuides.map((guide, idx) => (
              <div key={idx} className="bg-white rounded-xl shadow-sm p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                  {idx === 0 ? <Users className="w-5 h-5 text-teal-500" /> : <Briefcase className="w-5 h-5 text-purple-500" />}
                  {guide.title}
                </h2>
                <div className="space-y-4">
                  {guide.items.map((item, i) => (
                    <div key={i} className="flex gap-4 items-start">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm ${idx === 0 ? 'bg-teal-500' : 'bg-purple-500'}`}>
                        {item.step}
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{item.title}</h3>
                        <p className="text-sm text-gray-600">{item.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Video Modal */}
      {selectedVideo && (
        <VideoModal 
          video={selectedVideo} 
          onClose={handleCloseModal}
          selectedLanguage={selectedLanguage}
          setSelectedLanguage={setSelectedLanguage}
          showSubtitles={showSubtitles}
          setShowSubtitles={setShowSubtitles}
        />
      )}
    </div>
  );
};

export default VideoTutorialsPage;
