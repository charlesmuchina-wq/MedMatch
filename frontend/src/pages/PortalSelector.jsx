import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Video, Briefcase, ArrowRight, Sparkles, Users, FileText, Shield, MessageCircle, Hash, Megaphone } from 'lucide-react';
import { Card } from '@/components/ui/card';
import GlobalLanguageSelector from '@/components/GlobalLanguageSelector';
import { useTranslation } from "@/utils/i18n";

/**
 * PortalSelector - Clean landing page for users to choose between platforms
 * Enhanced with animations: hover lift, gradient shimmer, icon pulse
 * Mobile responsive design
 */
const PortalSelector = () => {
  const navigate = useNavigate();
  const [hoveredCard, setHoveredCard] = useState(null);
  const { t, translationVersion } = useTranslation();

  const portals = [
    {
      id: 'job-toolkit',
      title: t('pages.portalSelector.medmatchAI'),
      subtitle: t('pages.portalSelector.jobToolkit') || 'Job Toolkit',
      description: t('pages.portalSelector.jobToolkitDesc'),
      icon: Briefcase,
      gradient: 'from-turquoise to-cyan-500',
      glowColor: 'turquoise',
      features: [
        { icon: FileText, text: t('pages.portalSelector.resumeParser') },
        { icon: Sparkles, text: t('pages.portalSelector.aiJobMatching') },
        { icon: Users, text: t('pages.portalSelector.recruiterNetwork') },
      ],
      route: '/login',
      buttonText: t('pages.portalSelector.enterJobToolkit'),
      // Official MedMatch AI logo
      logo: 'https://customer-assets.emergentagent.com/job_f139deea-35f2-4b55-91b9-9aab4dc4c84b/artifacts/9uzkkm0w_MedMatch%20Logo%20-%201MB.png'
    },
    {
      id: 'meeting',
      title: t('pages.portalSelector.aiKarau'),
      subtitle: t('pages.portalSelector.meetingPortal'),
      description: t('pages.portalSelector.meetingPortalDesc'),
      icon: Video,
      gradient: 'from-violet-500 to-purple-600',
      glowColor: 'violet',
      features: [
        { icon: Video, text: t('pages.portalSelector.hdVideoAudio') },
        { icon: Sparkles, text: t('pages.portalSelector.aiTranscription') },
        { icon: Shield, text: t('pages.portalSelector.e2eEncrypted') },
      ],
      route: '/karau-meet',
      buttonText: t('pages.portalSelector.enterMeetingPortal'),
      logo: 'https://customer-assets.emergentagent.com/job_1fba32e3-e5a1-4174-b642-d1cd092309b3/artifacts/a7nojb8x_IMG_8477.jpeg'
    },
    {
      id: 'lumi',
      title: 'LUMI',
      subtitle: t('pages.portalSelector.messenger') || 'Messenger',
      description: t('pages.portalSelector.lumiDesc') || 'Real-time team messaging with channels, groups, and project spaces.',
      icon: MessageCircle,
      gradient: 'from-violet-500 to-indigo-600',
      glowColor: 'indigo',
      lumiIcon: true,
      features: [
        { icon: Hash, text: t('pages.portalSelector.channels') || 'Channels & Groups' },
        { icon: MessageCircle, text: t('pages.portalSelector.realtimeChat') || 'Real-time Chat' },
        { icon: Megaphone, text: t('pages.portalSelector.projectSpaces') || 'Project Spaces' },
      ],
      route: '/lumi',
      buttonText: t('pages.portalSelector.enterLumi') || 'Open LUMI Messenger'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex flex-col">
      {/* Custom CSS for animations */}
      <style>{`
        @keyframes shimmer {
          0% { background-position: -200% 0; }
          100% { background-position: 200% 0; }
        }
        
        @keyframes pulse-glow {
          0%, 100% { box-shadow: 0 0 20px rgba(var(--glow-rgb), 0.3); }
          50% { box-shadow: 0 0 40px rgba(var(--glow-rgb), 0.6); }
        }
        
        @keyframes icon-pulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.1); }
        }
        
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-8px); }
        }
        
        .shimmer-effect {
          background: linear-gradient(
            90deg,
            transparent 0%,
            rgba(255, 255, 255, 0.1) 50%,
            transparent 100%
          );
          background-size: 200% 100%;
          animation: shimmer 2s infinite linear;
        }
        
        .portal-card {
          transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        
        .portal-card:hover {
          transform: translateY(-12px) scale(1.02);
        }
        
        .portal-card.turquoise:hover {
          box-shadow: 0 25px 50px -12px rgba(20, 184, 166, 0.4),
                      0 0 0 1px rgba(20, 184, 166, 0.3);
        }
        
        .portal-card.violet:hover {
          box-shadow: 0 25px 50px -12px rgba(139, 92, 246, 0.4),
                      0 0 0 1px rgba(139, 92, 246, 0.3);
        }
        
        .icon-container {
          transition: all 0.3s ease;
        }
        
        .portal-card:hover .icon-container {
          animation: icon-pulse 1s ease-in-out infinite;
        }
        
        .portal-card:hover .icon-container img,
        .portal-card:hover .icon-container > div {
          animation: float 2s ease-in-out infinite;
        }
        
        .cta-button {
          position: relative;
          overflow: hidden;
        }
        
        .cta-button::before {
          content: '';
          position: absolute;
          top: 0;
          left: -100%;
          width: 100%;
          height: 100%;
          background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.2),
            transparent
          );
          transition: left 0.5s ease;
        }
        
        .portal-card:hover .cta-button::before {
          left: 100%;
        }
        
        .feature-item {
          transition: all 0.2s ease;
        }
        
        .portal-card:hover .feature-item {
          transform: translateX(4px);
        }
        
        .portal-card:hover .feature-item:nth-child(1) { transition-delay: 0ms; }
        .portal-card:hover .feature-item:nth-child(2) { transition-delay: 50ms; }
        .portal-card:hover .feature-item:nth-child(3) { transition-delay: 100ms; }
      `}</style>

      {/* Language Selector */}
      <div className="absolute top-4 right-4 z-20">
        <GlobalLanguageSelector compact={false} />
      </div>

      {/* Animated Background Effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-72 md:w-96 h-72 md:h-96 bg-turquoise/10 rounded-full blur-3xl animate-pulse" 
             style={{ animationDuration: '4s' }} />
        <div className="absolute bottom-1/4 right-1/4 w-72 md:w-96 h-72 md:h-96 bg-violet-500/10 rounded-full blur-3xl animate-pulse" 
             style={{ animationDuration: '5s', animationDelay: '1s' }} />
        <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-amber-500/5 rounded-full blur-3xl animate-pulse" 
             style={{ animationDuration: '6s', animationDelay: '2s' }} />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col items-center justify-center p-4 sm:p-6 relative z-10">
        {/* Header */}
        <div className="text-center mb-8 md:mb-12">
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-3">
            {t('pages.portalSelector.welcomeTo')}{' '}
            <span className="text-transparent bg-clip-text"
                  style={{ backgroundImage: 'linear-gradient(135deg, #00CEC9, #6C5CE7, #E84393)' }}>
              {t('pages.portalSelector.title')}
            </span>
          </h1>
          <p className="text-base sm:text-lg text-slate-200 max-w-xl mx-auto px-4">
            {t('pages.portalSelector.subtitle')}
          </p>
        </div>

        {/* Portal Cards - Stack on mobile, 3 columns on lg+ */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 max-w-6xl w-full px-4">
          {portals.map((portal) => (
            <Card
              key={portal.id}
              data-testid={`portal-${portal.id}`}
              onMouseEnter={() => setHoveredCard(portal.id)}
              onMouseLeave={() => setHoveredCard(null)}
              onClick={() => navigate(portal.route)}
              className={`
                portal-card ${portal.glowColor}
                relative overflow-hidden cursor-pointer
                bg-slate-800/60 border-slate-700/50 backdrop-blur-md
                hover:border-slate-500/50
                active:scale-[0.98]
              `}
            >
              {/* Shimmer overlay on hover */}
              <div className={`
                absolute inset-0 pointer-events-none
                ${hoveredCard === portal.id ? 'shimmer-effect' : 'opacity-0'}
              `} />
              
              {/* Gradient glow overlay */}
              <div className={`
                absolute inset-0 opacity-0 transition-opacity duration-500 pointer-events-none
                ${hoveredCard === portal.id ? 'opacity-100' : ''}
                bg-gradient-to-br ${portal.gradient}
              `} style={{ opacity: hoveredCard === portal.id ? 0.05 : 0 }} />

              <div className="relative p-6 sm:p-8">
                {/* Icon/Logo with pulse animation */}
                <div className="flex items-center gap-3 sm:gap-4 mb-4 sm:mb-6">
                  <div className="icon-container">
                    {portal.lumiIcon ? (
                      <div className="w-14 h-14 sm:w-16 sm:h-16 rounded-xl bg-[#0B0F1A] flex items-center justify-center shadow-lg ring-2 ring-violet-500/30 p-1.5">
                        <img src="/lumi-bubble-official.png" alt="LUMI" className="w-full h-full object-contain" />
                      </div>
                    ) : portal.logo ? (
                      <img 
                        src={portal.logo} 
                        alt={portal.title}
                        className="w-14 h-14 sm:w-16 sm:h-16 rounded-xl object-cover shadow-lg ring-2 ring-white/10"
                      />
                    ) : portal.logoText ? (
                      <div className={`
                        w-14 h-14 sm:w-16 sm:h-16 rounded-xl 
                        bg-gradient-to-br ${portal.gradient} 
                        flex items-center justify-center shadow-lg
                        ring-2 ring-white/10
                      `}>
                        <span className="text-xl sm:text-2xl font-bold text-white">{portal.logoText}</span>
                      </div>
                    ) : (
                      <div className={`
                        w-14 h-14 sm:w-16 sm:h-16 rounded-xl 
                        bg-gradient-to-br ${portal.gradient} 
                        flex items-center justify-center shadow-lg
                        ring-2 ring-white/10
                      `}>
                        <portal.icon className="w-7 h-7 sm:w-8 sm:h-8 text-white" />
                      </div>
                    )}
                  </div>
                  <div>
                    <h2 className="text-xl sm:text-2xl font-bold text-white">{portal.title}</h2>
                    <p className={`text-base sm:text-lg font-medium bg-gradient-to-r ${portal.gradient} bg-clip-text text-transparent`}>
                      {portal.subtitle}
                    </p>
                  </div>
                </div>

                {/* Description */}
                <p className="text-white/90 text-sm sm:text-base mb-4 sm:mb-6 min-h-[40px] sm:min-h-[48px]">
                  {portal.description}
                </p>

                {/* Features with staggered animation */}
                <div className="space-y-2 sm:space-y-3 mb-6 sm:mb-8">
                  {portal.features.map((feature, idx) => (
                    <div 
                      key={idx} 
                      className="feature-item flex items-center gap-2 sm:gap-3 text-xs sm:text-sm text-white/90"
                    >
                      <div className={`
                        w-6 h-6 rounded-md flex items-center justify-center
                        bg-gradient-to-br ${portal.gradient} bg-opacity-10
                        ${hoveredCard === portal.id ? 'bg-opacity-20' : ''}
                        transition-all duration-300
                      `}>
                        <feature.icon className="w-3 h-3 sm:w-3.5 sm:h-3.5 text-white/90" />
                      </div>
                      <span>{feature.text}</span>
                    </div>
                  ))}
                </div>

                {/* CTA Button with shine effect */}
                <button
                  className={`
                    cta-button w-full py-3 px-6 rounded-xl font-semibold text-white
                    bg-gradient-to-r ${portal.gradient}
                    flex items-center justify-center gap-2
                    transition-all duration-300
                    hover:gap-3 hover:shadow-lg
                    active:scale-[0.98]
                    text-sm sm:text-base
                  `}
                >
                  {portal.buttonText}
                  <ArrowRight className={`
                    w-4 h-4 sm:w-5 sm:h-5 transition-transform duration-300
                    ${hoveredCard === portal.id ? 'translate-x-1' : ''}
                  `} />
                </button>
              </div>
            </Card>
          ))}
        </div>

        {/* Footer Info */}
        <div className="mt-8 md:mt-12 text-center px-4">
          <p className="text-xs sm:text-sm text-slate-300">
            {t('pages.portalSelector.poweredByAI')} • {t('pages.portalSelector.trustedBy')}
          </p>
        </div>
      </div>
    </div>
  );
};

export default PortalSelector;
