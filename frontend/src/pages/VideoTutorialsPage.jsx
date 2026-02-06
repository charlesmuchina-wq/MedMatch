import React, { useState, useEffect } from 'react';
import { Play, FileText, Users, Briefcase, Search, ClipboardList, ChevronRight, ExternalLink, Loader2 } from 'lucide-react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

const VideoTutorialsPage = () => {
  const [activeTab, setActiveTab] = useState('videos');
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchVideos();
  }, []);

  const fetchVideos = async () => {
    try {
      const response = await axios.get(`${API}/api/tutorials/videos`);
      const videosData = response.data.videos.map(v => ({
        ...v,
        icon: v.category === 'job_seeker' ? Users : v.category === 'recruiter' ? Briefcase : Search,
        color: v.category === 'job_seeker' ? 'bg-teal-500' : 'bg-purple-500',
        file: `${API}${v.url}`
      }));
      setVideos(videosData);
    } catch (error) {
      console.error('Failed to fetch videos:', error);
      // Fallback to static data
      setVideos([
        {
          id: '01_jobseeker_intro',
          title: 'Getting Started as a Job Seeker',
          description: 'Overview of MedMatch platform for job seekers',
          duration: '4 seconds',
          category: 'job_seeker',
          icon: Users,
          file: `${API}/api/tutorials/videos/01_jobseeker_intro`,
          color: 'bg-teal-500'
        },
        {
          id: '02_recruiter_dashboard',
          title: 'Recruiter Dashboard Overview',
          description: 'Recruiter interface walkthrough',
          duration: '4 seconds',
          category: 'recruiter',
          icon: Briefcase,
          file: `${API}/api/tutorials/videos/02_recruiter_dashboard`,
          color: 'bg-purple-500'
        },
        {
          id: '03_job_search',
          title: 'Advanced Job Search',
          description: 'How to search and filter jobs effectively',
          duration: '4 seconds',
          category: 'job_seeker',
          icon: Search,
          file: `${API}/api/tutorials/videos/03_job_search`,
          color: 'bg-teal-500'
        },
        {
          id: '04_ats_system',
          title: 'Applicant Tracking System',
          description: 'Learn how to use the ATS for hiring',
          duration: '4 seconds',
          category: 'recruiter',
          icon: ClipboardList,
          file: `${API}/api/tutorials/videos/04_ats_system`,
          color: 'bg-purple-500'
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

  const VideoCard = ({ video }) => {
    const Icon = video.icon;
    return (
      <div 
        className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-all cursor-pointer group"
        onClick={() => setSelectedVideo(video)}
        data-testid={`video-card-${video.id}`}
      >
        <div className={`${video.color} h-32 flex items-center justify-center relative`}>
          <div className="absolute inset-0 bg-black/20 group-hover:bg-black/30 transition-colors" />
          <div className="relative z-10 w-16 h-16 bg-white/90 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform">
            <Play className="w-8 h-8 text-gray-800 ml-1" />
          </div>
          <span className="absolute bottom-2 right-2 bg-black/60 text-white text-xs px-2 py-1 rounded">
            {video.duration}
          </span>
        </div>
        <div className="p-4">
          <div className="flex items-center gap-2 mb-2">
            <Icon className="w-4 h-4 text-gray-500" />
            <span className="text-xs text-gray-500 font-medium">{video.category}</span>
          </div>
          <h3 className="font-semibold text-gray-900 mb-1">{video.title}</h3>
          <p className="text-sm text-gray-600 line-clamp-2">{video.description}</p>
        </div>
      </div>
    );
  };

  const VideoModal = ({ video, onClose }) => {
    if (!video) return null;
    
    return (
      <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" onClick={onClose}>
        <div className="bg-white rounded-xl max-w-4xl w-full overflow-hidden" onClick={e => e.stopPropagation()}>
          <div className="p-4 border-b flex justify-between items-center">
            <h3 className="font-semibold text-lg">{video.title}</h3>
            <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
              ✕
            </button>
          </div>
          <div className="aspect-video bg-black">
            <video 
              src={video.file} 
              controls 
              autoPlay 
              className="w-full h-full"
              data-testid="video-player"
            >
              Your browser does not support video playback.
            </video>
          </div>
          <div className="p-4">
            <p className="text-gray-600">{video.description}</p>
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
