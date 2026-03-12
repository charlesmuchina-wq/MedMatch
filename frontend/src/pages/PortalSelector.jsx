import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Video, Briefcase, ArrowRight, Sparkles, Users, FileText, Shield, MessageCircle, Hash, Crown, ChevronDown, Globe, ExternalLink } from 'lucide-react';
import { Card } from '@/components/ui/card';
import GlobalLanguageSelector from '@/components/GlobalLanguageSelector';
import { useTranslation } from "@/utils/i18n";
import { useDomain } from '@/contexts/DomainContext';

/**
 * PortalSelector — Landing page
 * Users choose which app to open. KARAU and ENZI are auto-bundled.
 * Opening KARAU auto-includes ENZI in the dock, and vice versa.
 * MedMatch is standalone.
 */
const APPS = [
  {
    id: 'karau',
    name: 'AI KARAU',
    tagline: 'Meetings & Webinars',
    description: 'HD video meetings with AI transcription, screen sharing, and real-time collaboration.',
    companion: 'ENZI Messenger included',
    route: '/karau-meet',
    icon: Video,
    color: '#6C5CE7',
    gradient: 'from-violet-500 to-indigo-600',
    badgeStyle: 'bg-violet-500/20 text-violet-300 border-violet-500/30',
    logo: 'https://customer-assets.emergentagent.com/job_1fba32e3-e5a1-4174-b642-d1cd092309b3/artifacts/a7nojb8x_IMG_8477.jpeg',
    domains: ['connect.aikarau.com', 'meet.aikarau.com'],
    features: [
      { icon: Video, text: 'HD Video & Audio' },
      { icon: MessageCircle, text: 'Auto-includes ENZI Messenger' },
      { icon: Shield, text: 'Meeting-to-Channel Sync' },
    ],
  },
  {
    id: 'enzi',
    name: 'ENZI',
    tagline: 'Actionable Intelligence Messenger',
    description: 'Team messaging with channels, bots, AI writing tools, and end-to-end encryption.',
    companion: 'AI KARAU Meetings included',
    route: '/lumi',
    icon: MessageCircle,
    color: '#00CEC9',
    gradient: 'from-teal-400 to-cyan-500',
    badgeStyle: 'bg-teal-500/20 text-teal-300 border-teal-500/30',
    lumiIcon: true,
    domains: ['enzi.aikarau.com', 'enzilink.com'],
    features: [
      { icon: Hash, text: 'Channels, DMs & Bots' },
      { icon: Video, text: 'Auto-includes AI KARAU' },
      { icon: Sparkles, text: 'AI-Powered Collaboration' },
    ],
  },
  {
    id: 'medmatch',
    name: 'MedMatch AI',
    tagline: 'Career Intelligence Toolkit',
    description: 'AI-powered job search, resume builder, and interview preparation — your complete career toolkit.',
    companion: null,
    route: '/login',
    icon: Briefcase,
    color: '#00B894',
    gradient: 'from-teal-400 to-emerald-500',
    badgeStyle: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
    logo: 'https://customer-assets.emergentagent.com/job_f139deea-35f2-4b55-91b9-9aab4dc4c84b/artifacts/9uzkkm0w_MedMatch%20Logo%20-%201MB.png',
    domains: ['medmatch.aikarau.com', 'careers.aikarau.com', 'jobs.aikarau.com'],
    features: [
      { icon: FileText, text: 'AI Resume Parser' },
      { icon: Sparkles, text: 'Smart Job Matching' },
      { icon: Users, text: 'Recruiter Network' },
    ],
  },
];

const PortalSelector = () => {
  const navigate = useNavigate();
  const [hoveredCard, setHoveredCard] = useState(null);
  const { t } = useTranslation();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex flex-col">
      <style>{`
        @keyframes shimmer {
          0% { background-position: -200% 0; }
          100% { background-position: 200% 0; }
        }
        .shimmer-effect {
          background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.08) 50%, transparent 100%);
          background-size: 200% 100%;
          animation: shimmer 2s infinite linear;
        }
        .app-card {
          transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        .app-card:hover {
          transform: translateY(-10px) scale(1.02);
        }
        .app-card:hover .cta-btn::before { left: 100%; }
        .cta-btn {
          position: relative; overflow: hidden;
        }
        .cta-btn::before {
          content: ''; position: absolute; top: 0; left: -100%;
          width: 100%; height: 100%;
          background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
          transition: left 0.5s ease;
        }
        .feature-item { transition: all 0.2s ease; }
        .app-card:hover .feature-item { transform: translateX(4px); }
        .app-card:hover .feature-item:nth-child(1) { transition-delay: 0ms; }
        .app-card:hover .feature-item:nth-child(2) { transition-delay: 50ms; }
        .app-card:hover .feature-item:nth-child(3) { transition-delay: 100ms; }
      `}</style>

      {/* Language Selector */}
      <div className="absolute top-4 right-4 z-20">
        <GlobalLanguageSelector compact={false} />
      </div>

      {/* BG effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-72 md:w-96 h-72 md:h-96 bg-violet-500/8 rounded-full blur-3xl animate-pulse" style={{ animationDuration: '4s' }} />
        <div className="absolute bottom-1/4 right-1/4 w-72 md:w-96 h-72 md:h-96 bg-teal-500/8 rounded-full blur-3xl animate-pulse" style={{ animationDuration: '5s', animationDelay: '1s' }} />
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
            Choose your app. KARAU and ENZI are auto-bundled — open one, get both.
          </p>
        </div>

        {/* App Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 max-w-5xl w-full px-4">
          {APPS.map((app) => {
            const isHovered = hoveredCard === app.id;
            const Icon = app.icon;

            return (
              <Card
                key={app.id}
                data-testid={`portal-${app.id}`}
                onMouseEnter={() => setHoveredCard(app.id)}
                onMouseLeave={() => setHoveredCard(null)}
                onClick={() => navigate(app.route)}
                className="app-card relative overflow-hidden cursor-pointer bg-slate-800/60 border-slate-700/50 backdrop-blur-md hover:border-slate-500/50 active:scale-[0.98]"
              >
                {/* Shimmer */}
                <div className={`absolute inset-0 pointer-events-none ${isHovered ? 'shimmer-effect' : 'opacity-0'}`} />

                {/* Companion badge */}
                {app.companion && (
                  <div className="absolute top-4 right-4 z-10">
                    <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-semibold border ${app.badgeStyle}`}>
                      Auto-bundled
                    </span>
                  </div>
                )}

                <div className="relative p-6 sm:p-7">
                  {/* Icon + Name */}
                  <div className="flex items-center gap-3 mb-5">
                    <div className="w-14 h-14 rounded-xl flex items-center justify-center overflow-hidden shadow-lg ring-2 ring-white/10"
                         style={{ backgroundColor: app.lumiIcon ? '#0B0F1A' : undefined }}>
                      {app.lumiIcon ? (
                        <img src="/lumi-icon-only.png" alt="ENZI" className="w-10 h-10 object-contain" />
                      ) : app.logo ? (
                        <img src={app.logo} alt={app.name} className="w-full h-full object-cover" />
                      ) : (
                        <div className={`w-full h-full bg-gradient-to-br ${app.gradient} flex items-center justify-center`}>
                          <Icon className="w-7 h-7 text-white" />
                        </div>
                      )}
                    </div>
                    <div>
                      <h2 className="text-lg sm:text-xl font-bold text-white" style={{ fontFamily: "'Manrope', sans-serif" }}>{app.name}</h2>
                      <p className={`text-sm font-medium bg-gradient-to-r ${app.gradient} bg-clip-text text-transparent`}>{app.tagline}</p>
                    </div>
                  </div>

                  {/* Description */}
                  <p className="text-sm text-white/80 mb-4 leading-relaxed min-h-[44px]">
                    {app.description}
                  </p>

                  {/* Companion note */}
                  {app.companion && (
                    <div className="mb-4 px-3 py-2 rounded-lg bg-white/[0.03] border border-white/[0.06]">
                      <p className="text-[11px] text-cyan-300/80 font-medium">{app.companion}</p>
                    </div>
                  )}

                  {/* Features */}
                  <div className="space-y-2 mb-4">
                    {app.features.map((feat, i) => (
                      <div key={i} className="feature-item flex items-center gap-2.5 text-sm text-white/85">
                        <div className={`w-6 h-6 rounded-md flex items-center justify-center bg-gradient-to-br ${app.gradient}`} style={{ opacity: 0.15 }}>
                          <feat.icon className="w-3.5 h-3.5 text-white/90" />
                        </div>
                        <span>{feat.text}</span>
                      </div>
                    ))}
                  </div>

                  {/* Domain URLs */}
                  {app.domains && app.domains.length > 0 && (
                    <div className="mb-5 px-3 py-2 rounded-lg bg-white/[0.02] border border-white/[0.05]">
                      <div className="flex items-center gap-1.5 mb-1.5">
                        <Globe className="w-3 h-3 text-slate-500" />
                        <span className="text-[10px] text-slate-500 font-medium uppercase tracking-wider">Direct Access</span>
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {app.domains.map((d) => (
                          <span key={d} className="inline-flex items-center gap-1 text-[10px] text-slate-400 bg-white/[0.04] px-2 py-0.5 rounded-md font-mono" data-testid={`domain-${d.replace(/\./g, '-')}`}>
                            {d}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* CTA */}
                  <button
                    data-testid={`open-${app.id}-btn`}
                    className={`cta-btn w-full py-3 px-5 rounded-xl font-semibold text-white text-sm bg-gradient-to-r ${app.gradient} flex items-center justify-center gap-2 transition-all duration-300 hover:shadow-lg hover:gap-3 active:scale-[0.98]`}
                  >
                    Open {app.name}
                    <ArrowRight className={`w-4 h-4 transition-transform duration-300 ${isHovered ? 'translate-x-1' : ''}`} />
                  </button>
                </div>
              </Card>
            );
          })}
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
