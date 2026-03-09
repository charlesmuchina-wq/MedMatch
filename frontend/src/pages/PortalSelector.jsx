import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Video, Briefcase, ArrowRight, Sparkles, Users, FileText, Shield, MessageCircle, Hash, Megaphone, Crown, Package, Check, ChevronDown } from 'lucide-react';
import { Card } from '@/components/ui/card';
import GlobalLanguageSelector from '@/components/GlobalLanguageSelector';
import { useTranslation } from "@/utils/i18n";

const PACKAGES = [
  {
    id: 'standard',
    name: 'AI KARAU + ENZI',
    tagline: 'Communication Suite',
    description: 'Video meetings and intelligent messaging — everything your team needs to collaborate.',
    portals: ['karau', 'enzi'],
    gradient: 'from-violet-500 to-indigo-600',
    accentColor: '#6C5CE7',
    badge: 'Popular',
    badgeStyle: 'bg-violet-500/20 text-violet-300 border-violet-500/30',
    route: '/karau-meet',
    portalIcons: [
      { icon: Video, color: '#6C5CE7', name: 'AI KARAU' },
      { icon: MessageCircle, color: '#00CEC9', name: 'ENZI' },
    ],
    features: [
      { icon: Video, text: 'HD Video & Audio Calls' },
      { icon: MessageCircle, text: 'Team Channels & DMs' },
      { icon: Shield, text: 'End-to-End Encryption' },
    ],
  },
  {
    id: 'medmatch_standalone',
    name: 'MedMatch Job Toolkit',
    tagline: 'Career Intelligence',
    description: 'AI-powered job search, resume builder, and interview preparation tools.',
    portals: ['medmatch'],
    gradient: 'from-teal-400 to-emerald-500',
    accentColor: '#00B894',
    badge: 'Standalone',
    badgeStyle: 'bg-teal-500/20 text-teal-300 border-teal-500/30',
    route: '/login',
    portalIcons: [
      { icon: Briefcase, color: '#00B894', name: 'MedMatch' },
    ],
    features: [
      { icon: FileText, text: 'AI Resume Parser' },
      { icon: Sparkles, text: 'Smart Job Matching' },
      { icon: Users, text: 'Recruiter Network' },
    ],
    logo: 'https://customer-assets.emergentagent.com/job_f139deea-35f2-4b55-91b9-9aab4dc4c84b/artifacts/9uzkkm0w_MedMatch%20Logo%20-%201MB.png'
  },
  {
    id: 'enterprise',
    name: 'Enterprise Suite',
    tagline: 'Complete Platform',
    description: 'All three portals — recruit, meet, and message from one unified platform.',
    portals: ['medmatch', 'karau', 'enzi'],
    gradient: 'from-amber-400 to-orange-500',
    accentColor: '#F59E0B',
    badge: 'Full Access',
    badgeStyle: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
    route: '/login',
    portalIcons: [
      { icon: Briefcase, color: '#00B894', name: 'MedMatch' },
      { icon: Video, color: '#6C5CE7', name: 'AI KARAU' },
      { icon: MessageCircle, color: '#00CEC9', name: 'ENZI' },
    ],
    features: [
      { icon: Briefcase, text: 'Complete Job Toolkit' },
      { icon: Video, text: 'Video Meetings' },
      { icon: MessageCircle, text: 'Team Messaging' },
    ],
  },
];

const PortalSelector = () => {
  const navigate = useNavigate();
  const [hoveredCard, setHoveredCard] = useState(null);
  const { t } = useTranslation();

  const handleSelectPackage = (pkg) => {
    localStorage.setItem('selected_package_intent', pkg.id);
    navigate(pkg.route);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex flex-col">
      <style>{`
        @keyframes shimmer {
          0% { background-position: -200% 0; }
          100% { background-position: 200% 0; }
        }
        @keyframes icon-pulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.1); }
        }
        .shimmer-effect {
          background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.08) 50%, transparent 100%);
          background-size: 200% 100%;
          animation: shimmer 2s infinite linear;
        }
        .pkg-card {
          transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        .pkg-card:hover {
          transform: translateY(-10px) scale(1.02);
        }
        .pkg-card:hover .cta-btn::before {
          left: 100%;
        }
        .cta-btn {
          position: relative;
          overflow: hidden;
        }
        .cta-btn::before {
          content: '';
          position: absolute;
          top: 0; left: -100%;
          width: 100%; height: 100%;
          background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
          transition: left 0.5s ease;
        }
        .feature-item {
          transition: all 0.2s ease;
        }
        .pkg-card:hover .feature-item {
          transform: translateX(4px);
        }
        .pkg-card:hover .feature-item:nth-child(1) { transition-delay: 0ms; }
        .pkg-card:hover .feature-item:nth-child(2) { transition-delay: 50ms; }
        .pkg-card:hover .feature-item:nth-child(3) { transition-delay: 100ms; }
      `}</style>

      {/* Language Selector */}
      <div className="absolute top-4 right-4 z-20">
        <GlobalLanguageSelector compact={false} />
      </div>

      {/* BG effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-72 md:w-96 h-72 md:h-96 bg-violet-500/8 rounded-full blur-3xl animate-pulse" style={{ animationDuration: '4s' }} />
        <div className="absolute bottom-1/4 right-1/4 w-72 md:w-96 h-72 md:h-96 bg-teal-500/8 rounded-full blur-3xl animate-pulse" style={{ animationDuration: '5s', animationDelay: '1s' }} />
        <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-amber-500/5 rounded-full blur-3xl animate-pulse" style={{ animationDuration: '6s', animationDelay: '2s' }} />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col items-center justify-center p-4 sm:p-6 relative z-10">
        {/* Header */}
        <div className="text-center mb-8 md:mb-12">
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-3">
            {t('pages.portalSelector.welcomeTo')}{' '}
            <span className="text-transparent bg-clip-text" style={{ backgroundImage: 'linear-gradient(135deg, #00CEC9, #6C5CE7, #E84393)' }}>
              {t('pages.portalSelector.title')}
            </span>
          </h1>
          <p className="text-base sm:text-lg text-slate-200 max-w-xl mx-auto px-4">
            Choose a package to get started with the tools you need
          </p>
        </div>

        {/* Package Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 max-w-5xl w-full px-4">
          {PACKAGES.map((pkg) => {
            const isHovered = hoveredCard === pkg.id;

            return (
              <Card
                key={pkg.id}
                data-testid={`portal-${pkg.id}`}
                onMouseEnter={() => setHoveredCard(pkg.id)}
                onMouseLeave={() => setHoveredCard(null)}
                onClick={() => handleSelectPackage(pkg)}
                className={`
                  pkg-card relative overflow-hidden cursor-pointer
                  bg-slate-800/60 border-slate-700/50 backdrop-blur-md
                  hover:border-slate-500/50 active:scale-[0.98]
                `}
              >
                {/* Shimmer */}
                <div className={`absolute inset-0 pointer-events-none ${isHovered ? 'shimmer-effect' : 'opacity-0'}`} />

                {/* Badge */}
                <div className="absolute top-4 right-4 z-10">
                  <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold border ${pkg.badgeStyle}`}>
                    {pkg.id === 'enterprise' && <Crown className="w-3 h-3" />}
                    {pkg.badge}
                  </span>
                </div>

                <div className="relative p-6 sm:p-7">
                  {/* Portal Icons Row */}
                  <div className="flex items-center gap-2 mb-5">
                    {pkg.portalIcons.map((pi, i) => (
                      <div key={i} className="w-11 h-11 rounded-xl flex items-center justify-center border border-white/[0.06]"
                           style={{ backgroundColor: pi.color + '18' }}>
                        <pi.icon className="w-5 h-5" style={{ color: pi.color }} />
                      </div>
                    ))}
                    <div className="ml-2">
                      <h2 className="text-lg sm:text-xl font-bold text-white" style={{ fontFamily: "'Manrope', sans-serif" }}>{pkg.name}</h2>
                      <p className={`text-sm font-medium bg-gradient-to-r ${pkg.gradient} bg-clip-text text-transparent`}>{pkg.tagline}</p>
                    </div>
                  </div>

                  {/* Description */}
                  <p className="text-sm text-white/80 mb-5 leading-relaxed min-h-[44px]">
                    {pkg.description}
                  </p>

                  {/* Features */}
                  <div className="space-y-2.5 mb-6">
                    {pkg.features.map((feat, i) => (
                      <div key={i} className="feature-item flex items-center gap-2.5 text-sm text-white/85">
                        <div className={`w-6 h-6 rounded-md flex items-center justify-center bg-gradient-to-br ${pkg.gradient}`} style={{ opacity: 0.15 }}>
                          <feat.icon className="w-3.5 h-3.5 text-white/90" />
                        </div>
                        <span>{feat.text}</span>
                      </div>
                    ))}
                  </div>

                  {/* CTA */}
                  <button
                    data-testid={`select-${pkg.id}-btn`}
                    className={`cta-btn w-full py-3 px-5 rounded-xl font-semibold text-white text-sm bg-gradient-to-r ${pkg.gradient} flex items-center justify-center gap-2 transition-all duration-300 hover:shadow-lg hover:gap-3 active:scale-[0.98]`}
                  >
                    Get Started
                    <ArrowRight className={`w-4 h-4 transition-transform duration-300 ${isHovered ? 'translate-x-1' : ''}`} />
                  </button>
                </div>
              </Card>
            );
          })}
        </div>

        {/* Direct Portal Links for returning users */}
        <div className="mt-10 text-center" data-testid="direct-portal-links">
          <p className="text-sm text-slate-400 mb-3">Already have an account? Go directly to:</p>
          <div className="flex items-center justify-center gap-4 flex-wrap">
            <button
              onClick={() => navigate('/login')}
              className="text-sm text-teal-400 hover:text-teal-300 transition-colors underline underline-offset-4"
              data-testid="direct-medmatch-link"
            >
              MedMatch Jobs
            </button>
            <span className="text-slate-600">|</span>
            <button
              onClick={() => navigate('/karau-meet')}
              className="text-sm text-violet-400 hover:text-violet-300 transition-colors underline underline-offset-4"
              data-testid="direct-karau-link"
            >
              AI KARAU Meetings
            </button>
            <span className="text-slate-600">|</span>
            <button
              onClick={() => navigate('/lumi')}
              className="text-sm text-cyan-400 hover:text-cyan-300 transition-colors underline underline-offset-4"
              data-testid="direct-enzi-link"
            >
              ENZI Messenger
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 md:mt-12 text-center px-4">
          <p className="text-xs sm:text-sm text-slate-300">
            {t('pages.portalSelector.poweredByAI')} &bull; {t('pages.portalSelector.trustedBy')}
          </p>
        </div>
      </div>
    </div>
  );
};

export default PortalSelector;
