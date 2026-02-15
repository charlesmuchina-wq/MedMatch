import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Video, Briefcase, ArrowRight, Sparkles, Users, FileText, Shield } from 'lucide-react';
import { Card } from '@/components/ui/card';
import GlobalLanguageSelector from '@/components/GlobalLanguageSelector';

/**
 * PortalSelector - Clean landing page for users to choose between platforms
 * 
 * Two options:
 * 1. MedMatch AI Job Toolkit - Recruiting platform
 * 2. AI KARAU Meeting - Video conferencing
 */
const PortalSelector = () => {
  const navigate = useNavigate();
  const [hoveredCard, setHoveredCard] = useState(null);

  const portals = [
    {
      id: 'job-toolkit',
      title: 'MedMatch AI',
      subtitle: 'Job Toolkit',
      description: 'AI-powered job search and career tools for life sciences professionals',
      icon: Briefcase,
      gradient: 'from-turquoise to-cyan-500',
      bgGlow: 'bg-turquoise/20',
      features: [
        { icon: FileText, text: 'Resume Parser & Builder' },
        { icon: Sparkles, text: 'AI Job Matching' },
        { icon: Users, text: 'Recruiter Network' },
      ],
      route: '/login',
      buttonText: 'Enter Job Toolkit'
    },
    {
      id: 'meeting',
      title: 'AI KARAU',
      subtitle: 'Meeting',
      description: 'Secure video conferencing with AI transcription and collaboration tools',
      icon: Video,
      gradient: 'from-violet-500 to-purple-600',
      bgGlow: 'bg-violet-500/20',
      features: [
        { icon: Video, text: 'HD Video & Audio' },
        { icon: Sparkles, text: 'AI Transcription' },
        { icon: Shield, text: 'E2E Encrypted' },
      ],
      route: '/karau-meet',
      buttonText: 'Enter Meeting Portal',
      logo: 'https://customer-assets.emergentagent.com/job_1fba32e3-e5a1-4174-b642-d1cd092309b3/artifacts/a7nojb8x_IMG_8477.jpeg'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex flex-col">
      {/* Language Selector */}
      <div className="absolute top-4 right-4 z-20">
        <GlobalLanguageSelector compact={false} />
      </div>

      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-turquoise/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-violet-500/10 rounded-full blur-3xl" />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col items-center justify-center p-6 relative z-10">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-3">
            Welcome to <span className="bg-gradient-to-r from-turquoise to-cyan-400 bg-clip-text text-transparent">MedMatch-AI KARAU</span>
          </h1>
          <p className="text-lg text-slate-400 max-w-xl mx-auto">
            Choose your destination
          </p>
        </div>

        {/* Portal Cards */}
        <div className="grid md:grid-cols-2 gap-6 max-w-4xl w-full">
          {portals.map((portal) => (
            <Card
              key={portal.id}
              data-testid={`portal-${portal.id}`}
              onMouseEnter={() => setHoveredCard(portal.id)}
              onMouseLeave={() => setHoveredCard(null)}
              onClick={() => navigate(portal.route)}
              className={`
                relative overflow-hidden cursor-pointer
                bg-slate-800/50 border-slate-700 backdrop-blur-sm
                transition-all duration-300 ease-out
                hover:scale-[1.02] hover:border-slate-600
                ${hoveredCard === portal.id ? 'shadow-2xl' : 'shadow-lg'}
              `}
            >
              {/* Glow effect on hover */}
              <div className={`
                absolute inset-0 opacity-0 transition-opacity duration-300
                ${hoveredCard === portal.id ? 'opacity-100' : ''}
                ${portal.bgGlow}
              `} />

              <div className="relative p-8">
                {/* Icon/Logo */}
                <div className="flex items-center gap-4 mb-6">
                  {portal.logo ? (
                    <img 
                      src={portal.logo} 
                      alt={portal.title}
                      className="w-16 h-16 rounded-xl object-cover shadow-lg"
                    />
                  ) : (
                    <div className={`w-16 h-16 rounded-xl bg-gradient-to-br ${portal.gradient} flex items-center justify-center shadow-lg`}>
                      <portal.icon className="w-8 h-8 text-white" />
                    </div>
                  )}
                  <div>
                    <h2 className="text-2xl font-bold text-white">{portal.title}</h2>
                    <p className={`text-lg font-medium bg-gradient-to-r ${portal.gradient} bg-clip-text text-transparent`}>
                      {portal.subtitle}
                    </p>
                  </div>
                </div>

                {/* Description */}
                <p className="text-slate-300 mb-6 min-h-[48px]">
                  {portal.description}
                </p>

                {/* Features */}
                <div className="space-y-3 mb-8">
                  {portal.features.map((feature, idx) => (
                    <div key={idx} className="flex items-center gap-3 text-sm text-slate-400">
                      <feature.icon className="w-4 h-4 text-slate-500" />
                      <span>{feature.text}</span>
                    </div>
                  ))}
                </div>

                {/* CTA Button */}
                <button
                  className={`
                    w-full py-3 px-6 rounded-xl font-semibold text-white
                    bg-gradient-to-r ${portal.gradient}
                    flex items-center justify-center gap-2
                    transition-all duration-200
                    hover:opacity-90 hover:gap-3
                  `}
                >
                  {portal.buttonText}
                  <ArrowRight className="w-5 h-5" />
                </button>
              </div>
            </Card>
          ))}
        </div>

        {/* Footer Info */}
        <div className="mt-12 text-center">
          <p className="text-sm text-slate-500">
            Powered by AI • Trusted by Life Sciences Professionals
          </p>
        </div>
      </div>
    </div>
  );
};

export default PortalSelector;
