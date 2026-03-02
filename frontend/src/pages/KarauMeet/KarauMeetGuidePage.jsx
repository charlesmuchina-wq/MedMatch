import { useState } from 'react';
import {
  BookOpen, Video, Radio, Brain, Eye, Globe, Wand2, Volume2,
  Mic, Shield, Users, Settings, Monitor, ChevronRight, ChevronDown,
  Zap, Building2, UserCog, Presentation, User, Search,
  Cpu, Wifi, Smartphone, Layers, Fingerprint
} from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useTranslation } from '@/utils/i18n';

const GUIDE_SECTIONS = [
  {
    id: 'getting-started',
    title: 'Getting Started',
    icon: Zap,
    accent: 'text-amber-400',
    bg: 'bg-amber-500/10',
    roles: ['all'],
    items: [
      { title: 'Creating Your Account', content: 'Sign up with email or use Google/Apple SSO. After registration, you\'ll be taken to the AI KARAU dashboard where you can start or join meetings instantly.' },
      { title: 'Joining a Meeting', content: 'Enter a meeting code on the login page or click a shared meeting link. You\'ll enter the lobby where you can preview your camera, select devices, and apply virtual backgrounds before joining.' },
      { title: 'Starting Your First Meeting', content: 'Click "New Meeting" from the dashboard. Give it a title, optionally schedule it for later, and toggle AI Notes and Recording. Click "Start Now" to enter the meeting room.' },
      { title: 'Navigating the Dashboard', content: 'The dashboard shows your meeting stats, upcoming meetings, AI insights, and trending topics. Use the sidebar to access Meetings, Schedule, Recordings, Webinars, and Settings.' },
    ]
  },
  {
    id: 'ai-features',
    title: 'AI Features',
    icon: Brain,
    accent: 'text-purple-400',
    bg: 'bg-purple-500/10',
    roles: ['host', 'presenter', 'attendee'],
    items: [
      { title: 'AI Meeting Coach', icon: Brain, content: 'Provides real-time presentation tips during your meeting. Monitors pace, filler words, engagement, and body language. Access it from the AI Suite in the Feature Toolbar. Tips appear as subtle notifications during your presentation.' },
      { title: 'Eye Contact Correction', icon: Eye, content: 'AI-powered gaze alignment that adjusts your video feed so you appear to be looking directly at the camera, even when reading notes on screen. Toggle it from the AI Suite panel. Works in real-time with minimal latency.' },
      { title: 'Live Transcription & Captions', icon: Globe, content: 'Automatic speech-to-text transcription supporting 40+ languages. Captions appear at the bottom of the video feed. Enable multi-language captions so each participant sees captions in their preferred language.' },
      { title: 'Cinematic Director Mode', icon: Wand2, content: 'Automatically switches camera angles and applies cinematic framing based on who is speaking. Creates a professional broadcast feel. The AI selects optimal shots, zooms, and transitions between speakers.' },
      { title: 'Spatial Audio', icon: Volume2, content: '3D positional audio that places each participant\'s voice in a distinct spatial location, creating a natural meeting feel. Participants on the left of the screen sound like they\'re on your left. Enhances multi-speaker discussions.' },
      { title: 'Noise Cancellation', icon: Mic, content: 'AI-powered background noise removal using rnnoise-wasm. Eliminates keyboard clicks, background chatter, construction noise, and other distractions. Works locally on your device for privacy. Toggle from the Media controls.' },
      { title: 'AI Notes & Summarization', icon: BookOpen, content: 'Automatic meeting summarization powered by OpenAI. Generates key points, action items, and decisions after each meeting. Summaries appear in the Meeting Insights card on your dashboard and can be exported as PDF.' },
      { title: 'AI Assistant', icon: Zap, content: 'Your in-meeting AI assistant accessible via the Feature Command Bar (Cmd+K). Ask questions about the meeting, get summaries of what you missed, or request action item tracking. Works with voice commands too.' },
    ]
  },
  {
    id: 'meetings',
    title: 'Meetings',
    icon: Video,
    accent: 'text-blue-400',
    bg: 'bg-blue-500/10',
    roles: ['host', 'presenter', 'attendee'],
    items: [
      { title: 'Creating & Scheduling Meetings', content: 'From the dashboard, click "New Meeting" to create an instant or scheduled meeting. Set a title, date/time, and optionally choose a meeting template. Templates pre-configure settings for standup, workshop, interview, and more.' },
      { title: 'The Meeting Lobby', content: 'Before joining, you enter the lobby where you can: preview your camera feed, toggle mic/camera, select audio/video devices, apply virtual backgrounds (blur, office, nature, city, abstract), and see meeting details.' },
      { title: 'In-Meeting Controls', content: 'The Feature Toolbar at the bottom organizes controls into groups: Media (mic, camera, screen share), AI Suite (coach, eye contact, captions, director), Interactive (polls, Q&A, reactions), and More Tools (whiteboard, breakout rooms, recordings).' },
      { title: 'Feature Command Bar', content: 'Press Cmd+K (or Ctrl+K) to open the spotlight-style command bar. Quickly search and activate any feature by name. Much faster than navigating through menus during a live meeting.' },
      { title: 'Breakout Rooms', content: 'Split participants into smaller groups for focused discussions. AI can auto-assign participants based on topics or interests. Set timers and broadcast messages to all rooms. Participants return to the main room when breakout ends.' },
      { title: 'Sharing & Invitations', content: 'Share meeting links via email, copy link to clipboard, or generate QR codes for touchless entry. Each meeting has a unique code that can be entered on the login page.' },
      { title: 'Meeting Recordings', content: 'Enable cloud recording to capture the full meeting with automatic transcription via OpenAI Whisper. Recordings are available in the Recordings section with searchable transcripts and AI-generated highlights.' },
    ]
  },
  {
    id: 'webinars',
    title: 'Webinars',
    icon: Radio,
    accent: 'text-violet-400',
    bg: 'bg-violet-500/10',
    roles: ['host', 'presenter'],
    items: [
      { title: 'Creating a Webinar', content: 'Navigate to the Webinars section from the sidebar. Click "Create Webinar" and configure: title, description, scheduled time, max attendees, registration settings, auto-recording, Q&A, and chat options.' },
      { title: 'Registration & Attendee Management', content: 'Enable registration to collect attendee info (name, email, organization). Share the registration URL. Monitor registrations from the webinar management page. Set max attendees (10-10,000).' },
      { title: 'Panelist & Coordinator Roles', content: 'Add panelists by email who can present and share their camera. Add coordinators who help manage Q&A and chat. Promote attendees to panelist during the live session.' },
      { title: 'Live Q&A', content: 'Attendees submit questions that appear in a moderated queue. Upvote popular questions. Host and panelists can answer, dismiss, or pin questions. Questions can be answered live on-air or via text.' },
      { title: 'Practice Sessions', content: 'Run a practice session before going live. Only panelists and coordinators can see the practice. Test audio, video, screen sharing, and slides before the audience joins.' },
      { title: 'Webinar Analytics', content: 'After the webinar, view detailed analytics: peak attendees, average watch time, engagement score, questions asked, poll responses, and attendee demographics.' },
    ]
  },
  {
    id: 'hardware',
    title: 'Hardware Integrations',
    icon: Cpu,
    accent: 'text-teal-400',
    bg: 'bg-teal-500/10',
    roles: ['enterprise', 'admin'],
    items: [
      { title: 'SLAM Spatial Tracking', icon: Layers, content: 'Simultaneous Localization and Mapping (SLAM) integration for spatial awareness in meeting rooms. Tracks participant positions and creates a 3D room map for enhanced spatial audio positioning.' },
      { title: '360-Degree Cameras', icon: Monitor, content: 'Connect 360-degree cameras for panoramic meeting room views. AI automatically crops and follows the active speaker. Ideal for conference rooms where multiple participants share a single camera.' },
      { title: 'Beamforming Microphones', icon: Mic, content: 'Smart microphone arrays that use beamforming to isolate individual speakers in a room. Reduces cross-talk and echo. Pairs with speaker detection (hark.js) for automatic speaker identification.' },
      { title: 'IoT Room Controls', icon: Smartphone, content: 'Control meeting room devices: lighting, displays, whiteboards, and environmental sensors. Integrate with smart building systems for automatic room preparation before scheduled meetings.' },
      { title: 'Biometric Verification', icon: Fingerprint, content: 'Optional biometric verification for high-security meetings. Supports fingerprint and facial recognition for participant identity confirmation. Ideal for compliance-heavy industries.' },
      { title: 'Hardware Discovery', icon: Wifi, content: 'Automatic detection and configuration of compatible hardware in the meeting room. Plug in devices and AI KARAU configures them automatically. View connected devices in the Hardware panel.' },
    ]
  },
  {
    id: 'enterprise',
    title: 'Enterprise Administration',
    icon: Building2,
    accent: 'text-indigo-400',
    bg: 'bg-indigo-500/10',
    roles: ['enterprise', 'admin'],
    items: [
      { title: 'Organization Setup', content: 'Create your organization from the Enterprise panel. Configure company name, domain(s) for automatic user association, default meeting settings, and branding (logo, colors for meeting rooms and recordings).' },
      { title: 'SSO / SAML Integration', content: 'Configure Single Sign-On via SAML 2.0. Supports major identity providers. Once configured, users from your domain are automatically authenticated without separate AI KARAU credentials.' },
      { title: 'User Management', content: 'Manage users, assign roles (admin, host, member), set department groups, and control permissions. Bulk import users via CSV. View usage analytics per user.' },
      { title: 'Compliance & Security', content: 'E2E encryption for all meetings. Configure data retention policies, audit logs, and regional data storage. SOC 2 compliant infrastructure with regular security audits.' },
      { title: 'Meeting Policies', content: 'Set organization-wide defaults: require recording consent, enforce waiting rooms, set maximum meeting duration, restrict guest access, and configure auto-lock timers.' },
      { title: 'Analytics & Reporting', content: 'Enterprise-wide dashboards showing meeting volume, average duration, AI feature adoption, engagement scores, and cost metrics. Export reports for stakeholders.' },
    ]
  },
  {
    id: 'admin',
    title: 'Admin Controls',
    icon: UserCog,
    accent: 'text-rose-400',
    bg: 'bg-rose-500/10',
    roles: ['admin'],
    items: [
      { title: 'Moderation Tools', content: 'Mute all participants, remove disruptive users, lock meetings, and control who can share screens or use chat. Real-time sentiment monitoring alerts admins to potential issues.' },
      { title: 'Recording Management', content: 'Access all organization recordings. Set retention policies, manage storage, and configure who can download or share recordings. Automatic transcription and summarization for all recordings.' },
      { title: 'AI Feature Configuration', content: 'Enable or disable specific AI features for your organization. Configure AI coach sensitivity, transcription languages, and director mode preferences.' },
      { title: 'Integration Management', content: 'Manage calendar integrations (Google Calendar), communication tools (Slack, Teams), and storage providers. Configure webhooks for meeting events.' },
    ]
  },
  {
    id: 'host-presenter',
    title: 'Host & Presenter Guide',
    icon: Presentation,
    accent: 'text-emerald-400',
    bg: 'bg-emerald-500/10',
    roles: ['host', 'presenter'],
    items: [
      { title: 'Hosting Best Practices', content: 'Start meetings 1-2 minutes early. Use the practice session for webinars. Enable AI Coach for presentation feedback. Record important meetings for team members who can\'t attend.' },
      { title: 'Managing Participants', content: 'View participant list, mute individuals or all, promote attendees to panelist, create breakout rooms, and admit guests from the waiting room. Pin important speakers for all participants.' },
      { title: 'Screen Sharing & Presentations', content: 'Share your entire screen, a specific window, or a browser tab. For presentations, use Cinematic Director Mode for professional transitions. Upload slides for built-in slideshow with audience navigation.' },
      { title: 'Polls & Quizzes', content: 'Create live polls to gauge audience opinion. Run quizzes with correct answers and leaderboards. Results appear in real-time. Export poll data after the meeting.' },
      { title: 'Action Item Tracking', content: 'AI automatically identifies action items from the conversation. Manually add items during the meeting. Assign to specific participants with due dates. Track completion from the dashboard.' },
    ]
  },
  {
    id: 'attendee',
    title: 'Attendee Guide',
    icon: User,
    accent: 'text-sky-400',
    bg: 'bg-sky-500/10',
    roles: ['attendee'],
    items: [
      { title: 'Joining as a Guest', content: 'Enter the meeting code on the login page. No account needed. You\'ll enter the lobby where you can set up your camera and microphone. The host will admit you from the waiting room.' },
      { title: 'Using Reactions & Chat', content: 'Send emoji reactions during the meeting for quick feedback. Use the chat panel for text communication. Messages can be sent to everyone or privately to specific participants.' },
      { title: 'Q&A Participation', content: 'In webinars, submit questions through the Q&A panel. Upvote other attendees\' questions to prioritize them. Questions may be answered live or via text by the host/panelists.' },
      { title: 'Accessibility Features', content: 'AI KARAU supports screen readers, keyboard navigation, high contrast mode, and adjustable text sizes. Live captions with multi-language support make meetings accessible to all.' },
    ]
  },
];

const KarauMeetGuidePage = () => {
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedSection, setExpandedSection] = useState('getting-started');
  const [expandedItem, setExpandedItem] = useState(null);
  const [roleFilter, setRoleFilter] = useState('all');

  const roles = [
    { id: 'all', label: t('karauMeet.allRoles'), icon: Users },
    { id: 'host', label: t('karauMeet.host'), icon: Presentation },
    { id: 'attendee', label: t('karauMeet.attendee'), icon: User },
    { id: 'admin', label: t('karauMeet.admin'), icon: UserCog },
    { id: 'enterprise', label: t('karauMeet.enterprise'), icon: Building2 },
  ];

  const filteredSections = GUIDE_SECTIONS.filter(section => {
    if (roleFilter !== 'all' && !section.roles.includes(roleFilter) && !section.roles.includes('all')) return false;
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return section.title.toLowerCase().includes(q) ||
      section.items.some(item => item.title.toLowerCase().includes(q) || item.content.toLowerCase().includes(q));
  });

  const filteredItems = (section) => {
    if (!searchQuery) return section.items;
    const q = searchQuery.toLowerCase();
    return section.items.filter(item => item.title.toLowerCase().includes(q) || item.content.toLowerCase().includes(q));
  };

  return (
    <div className="h-full flex flex-col overflow-hidden" style={{ fontFamily: "'IBM Plex Sans', sans-serif" }} data-testid="guide-page">
      {/* Header */}
      <header className="flex items-center justify-between px-8 py-5 flex-shrink-0 border-b border-white/[0.04]">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-3">
            <BookOpen className="w-6 h-6 text-purple-400" />
            {t("karauMeet.guideTitle")}
          </h1>
          <p className="text-slate-500 text-sm mt-0.5">{t("karauMeet.guideDescription")}</p>
        </div>
        <Badge className="bg-white/[0.04] text-slate-400 border-white/[0.06] text-xs">
          {GUIDE_SECTIONS.reduce((acc, s) => acc + s.items.length, 0)} articles
        </Badge>
      </header>

      {/* Search + Role Filter */}
      <div className="px-8 py-4 flex items-center gap-4 flex-shrink-0 border-b border-white/[0.04]">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-600" />
          <Input
            placeholder={t("karauMeet.searchGuides")}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="bg-black/30 border-white/[0.08] text-white pl-10 h-10 rounded-xl focus:border-purple-500/40 placeholder-slate-600"
            data-testid="guide-search"
          />
        </div>
        <div className="flex gap-1.5">
          {roles.map(role => (
            <button
              key={role.id}
              onClick={() => setRoleFilter(role.id)}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-full text-xs font-medium transition-all duration-200 ${
                roleFilter === role.id
                  ? 'bg-purple-500/15 text-purple-300 border border-purple-500/30'
                  : 'text-slate-500 hover:text-slate-300 hover:bg-white/[0.04] border border-transparent'
              }`}
              data-testid={`role-filter-${role.id}`}
            >
              <role.icon className="w-3.5 h-3.5" />
              {role.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-8">
        <div className="max-w-4xl space-y-3">
          {filteredSections.length === 0 ? (
            <div className="text-center py-16">
              <Search className="w-10 h-10 text-slate-700 mx-auto mb-3" />
              <p className="text-slate-500 text-sm">{t("karauMeet.noGuidesFound")}</p>
            </div>
          ) : (
            filteredSections.map(section => {
              const isExpanded = expandedSection === section.id;
              const items = filteredItems(section);
              return (
                <div key={section.id} className="rounded-2xl bg-white/[0.02] border border-white/[0.06] overflow-hidden" data-testid={`guide-section-${section.id}`}>
                  <button
                    onClick={() => setExpandedSection(isExpanded ? null : section.id)}
                    className="w-full flex items-center justify-between px-6 py-4 hover:bg-white/[0.02] transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-9 h-9 rounded-xl ${section.bg} flex items-center justify-center`}>
                        <section.icon className={`w-4.5 h-4.5 ${section.accent}`} />
                      </div>
                      <div className="text-left">
                        <h2 className="text-sm font-semibold text-white">{section.title}</h2>
                        <p className="text-[11px] text-slate-500">{items.length} articles</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {section.roles.filter(r => r !== 'all').map(r => (
                        <Badge key={r} className="bg-white/[0.04] text-slate-500 border-white/[0.06] text-[9px] capitalize">{r}</Badge>
                      ))}
                      {isExpanded ? <ChevronDown className="w-4 h-4 text-slate-600" /> : <ChevronRight className="w-4 h-4 text-slate-600" />}
                    </div>
                  </button>
                  {isExpanded && (
                    <div className="px-6 pb-4 space-y-1">
                      {items.map((item, idx) => {
                        const itemKey = `${section.id}-${idx}`;
                        const isItemExpanded = expandedItem === itemKey;
                        return (
                          <div key={idx} data-testid={`guide-item-${section.id}-${idx}`}>
                            <button
                              onClick={() => setExpandedItem(isItemExpanded ? null : itemKey)}
                              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-left transition-all duration-200 ${
                                isItemExpanded ? 'bg-white/[0.04] border border-white/[0.06]' : 'hover:bg-white/[0.02]'
                              }`}
                            >
                              <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${isItemExpanded ? 'bg-purple-400' : 'bg-slate-700'}`} />
                              <span className={`text-sm ${isItemExpanded ? 'text-white font-medium' : 'text-slate-400'}`}>{item.title}</span>
                              {isItemExpanded ? <ChevronDown className="w-3.5 h-3.5 text-slate-500 ml-auto" /> : <ChevronRight className="w-3.5 h-3.5 text-slate-600 ml-auto" />}
                            </button>
                            {isItemExpanded && (
                              <div className="ml-8 mr-4 mt-1 mb-2 p-4 rounded-xl bg-white/[0.02] border border-white/[0.04]">
                                <p className="text-sm text-slate-300 leading-relaxed">{item.content}</p>
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};

export default KarauMeetGuidePage;
