import React, { useState, useEffect } from 'react';
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

const VideoTutorialsPage = () => {
  const [activeTab, setActiveTab] = useState('videos');
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [showSubtitles, setShowSubtitles] = useState(true);
  const [translating, setTranslating] = useState(false);

  useEffect(() => {
    fetchVideos();
  }, []);

  const fetchVideos = async () => {
    try {
      const response = await axios.get(`${API}/api/tutorials/videos`);
      const videosData = response.data.videos.map(v => ({
        ...v,
        icon: v.category === 'job_seeker' ? Users : v.category === 'recruiter' ? Briefcase : Search,
        color: v.category === 'job_seeker' ? 'bg-teal-500' : v.category === 'recruiter' ? 'bg-purple-500' : 'bg-blue-500',
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
          duration: '34 seconds',
          category: 'job_seeker',
          icon: Users,
          file: `${API}/api/tutorials/videos/01_jobseeker_features`,
          color: 'bg-teal-500'
        },
        {
          id: '02_recruiter_features',
          title: 'Recruiter Features',
          description: 'Dashboard, applicant tracking, job postings, and hiring tools',
          duration: '30 seconds',
          category: 'recruiter',
          icon: Briefcase,
          file: `${API}/api/tutorials/videos/02_recruiter_features`,
          color: 'bg-purple-500'
        },
        {
          id: '03_privacy_matters',
          title: 'Your Privacy Matters',
          description: 'How we protect your data and keep your job search secure',
          duration: '31 seconds',
          category: 'general',
          icon: Search,
          file: `${API}/api/tutorials/videos/03_privacy_matters`,
          color: 'bg-blue-500'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const quickGuides = [
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

  const VideoCard = ({ video }) => {
    const Icon = video.icon;
    const presenterImage = PRESENTER_IMAGES[video.id] || "/images/presenter.jpeg";
    
    // Get custom label for this video, or default to category-based label
    const getCategoryLabel = () => {
      if (CATEGORY_LABELS[video.id]) {
        return CATEGORY_LABELS[video.id];
      }
      return video.category === 'job_seeker' ? 'Job Seeker' : video.category === 'recruiter' ? 'Recruiter' : 'Everyone';
    };
    
    return (
      <div 
        className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-all cursor-pointer group"
        onClick={() => setSelectedVideo(video)}
        data-testid={`video-card-${video.id}`}
      >
        <div className="h-40 relative overflow-hidden">
          <img 
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
  };

  const VideoModal = ({ video, onClose }) => {
    if (!video) return null;
    
    const videoUrl = selectedLanguage === 'en' 
      ? video.file 
      : `${video.file}?lang=${selectedLanguage}`;
    
    const subtitleUrl = `${API}/api/tutorials/subtitles/${video.id}?lang=${selectedLanguage}`;
    
    const requestTranslation = async () => {
      setTranslating(true);
      try {
        await axios.post(`${API}/api/tutorials/translate/${video.id}?lang=${selectedLanguage}`);
        // Poll for completion
        const checkStatus = async () => {
          const res = await axios.get(`${API}/api/tutorials/translate/${video.id}/status?lang=${selectedLanguage}`);
          if (res.data.status === 'ready') {
            setTranslating(false);
            // Refresh to load translated video
            setSelectedVideo({...video});
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
            {translating && (
              <div className="absolute inset-0 bg-black/80 flex flex-col items-center justify-center text-white z-10">
                <Loader2 className="w-8 h-8 animate-spin mb-2" />
                <p>Generating {LANGUAGES.find(l => l.code === selectedLanguage)?.name} version...</p>
                <p className="text-sm text-gray-400">This may take a minute</p>
              </div>
            )}
            <video 
              src={videoUrl} 
              controls 
              autoPlay 
              className="w-full h-full"
              data-testid="video-player"
              crossOrigin="anonymous"
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
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6" data-testid="video-tutorials-page">
      <div className="max-w-6xl mx-auto">
        {/* Header with Presenter */}
        <div className="mb-8 bg-gradient-to-r from-teal-600 to-teal-500 rounded-2xl p-6 text-white">
          <div className="flex flex-col md:flex-row items-center gap-6">
            <div className="flex-shrink-0">
              <img 
                src="/images/presenter.jpeg" 
                alt="Tutorial Host" 
                className="w-24 h-24 md:w-32 md:h-32 rounded-full border-4 border-white/30 object-cover shadow-lg"
              />
            </div>
            <div className="text-center md:text-left">
              <h1 className="text-3xl font-bold mb-2">Help & Tutorials</h1>
              <p className="text-teal-100 text-lg mb-3">
                Welcome! I'm here to help you get the most out of MedMatch.
              </p>
              <p className="text-teal-200 text-sm">
                Watch our video tutorials and follow step-by-step guides to master the platform.
              </p>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActiveTab('videos')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === 'videos' 
                ? 'bg-teal-500 text-white' 
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
            data-testid="tab-videos"
          >
            <Play className="w-4 h-4 inline mr-2" />
            Video Tutorials
          </button>
          <button
            onClick={() => setActiveTab('guides')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === 'guides' 
                ? 'bg-teal-500 text-white' 
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
            data-testid="tab-guides"
          >
            <FileText className="w-4 h-4 inline mr-2" />
            Quick Guides
          </button>
        </div>

        {/* Video Grid */}
        {activeTab === 'videos' && (
          loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-teal-500" />
              <span className="ml-2 text-gray-600">Loading videos...</span>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {videos.map(video => (
                <VideoCard key={video.id} video={video} />
              ))}
            </div>
          )
        )}

        {/* Quick Guides */}
        {activeTab === 'guides' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {quickGuides.map((guide, idx) => (
              <div key={idx} className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                  {guide.title === 'For Job Seekers' ? (
                    <Users className="w-5 h-5 text-teal-500" />
                  ) : (
                    <Briefcase className="w-5 h-5 text-purple-500" />
                  )}
                  {guide.title}
                </h2>
                <div className="space-y-4">
                  {guide.items.map((item, i) => (
                    <div key={i} className="flex gap-4 items-start">
                      <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0 font-semibold text-gray-600">
                        {item.step}
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-900">{item.title}</h4>
                        <p className="text-sm text-gray-600">{item.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Additional Resources */}
        <div className="mt-8 bg-gradient-to-r from-teal-500 to-teal-600 rounded-xl p-6 text-white">
          <h2 className="text-xl font-semibold mb-2">Need More Help?</h2>
          <p className="text-teal-100 mb-4">
            Check out our comprehensive documentation or contact our support team.
          </p>
          <div className="flex gap-4">
            <a 
              href="/docs/guides/NAVIGATION_GUIDE.md" 
              target="_blank"
              className="inline-flex items-center gap-2 bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg transition-colors"
            >
              <FileText className="w-4 h-4" />
              Full Documentation
              <ExternalLink className="w-3 h-3" />
            </a>
            <a 
              href="mailto:support@medmatch.com"
              className="inline-flex items-center gap-2 bg-white text-teal-600 hover:bg-teal-50 px-4 py-2 rounded-lg transition-colors"
            >
              Contact Support
              <ChevronRight className="w-4 h-4" />
            </a>
          </div>
        </div>
      </div>

      {/* Video Modal */}
      {selectedVideo && (
        <VideoModal video={selectedVideo} onClose={() => setSelectedVideo(null)} />
      )}
    </div>
  );
};

export default VideoTutorialsPage;
