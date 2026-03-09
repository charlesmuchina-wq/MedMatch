import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import {
  Briefcase, Video, MessageCircle, Package, Check, ArrowRight, Crown,
  FileText, Sparkles, Users, Shield, Hash, Megaphone, Loader2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

const API = process.env.REACT_APP_BACKEND_URL;

const PACKAGES = [
  {
    id: 'standard',
    name: 'AI KARAU + ENZI',
    tagline: 'Communication Suite',
    description: 'Video meetings and intelligent messaging bundled together for seamless team collaboration.',
    portals: [
      { key: 'karau', name: 'AI KARAU', icon: Video, color: '#6C5CE7', features: ['HD Video & Audio', 'AI Transcription', 'Screen Sharing'] },
      { key: 'enzi', name: 'ENZI Messenger', icon: MessageCircle, color: '#00CEC9', features: ['Channels & Groups', 'Real-time Chat', 'Bot Store'] },
    ],
    gradient: 'from-violet-500 to-indigo-600',
    accentColor: '#6C5CE7',
    isDefault: true,
    badge: 'Popular',
  },
  {
    id: 'medmatch_standalone',
    name: 'MedMatch Job Toolkit',
    tagline: 'Career Intelligence',
    description: 'AI-powered job search, resume builder, and interview preparation — your complete career toolkit.',
    portals: [
      { key: 'medmatch', name: 'MedMatch AI', icon: Briefcase, color: '#00B894', features: ['AI Resume Parser', 'Job Matching', 'Interview Prep'] },
    ],
    gradient: 'from-teal-400 to-emerald-500',
    accentColor: '#00B894',
    isDefault: false,
    badge: 'Standalone',
  },
  {
    id: 'enterprise',
    name: 'Enterprise Suite',
    tagline: 'Complete Platform',
    description: 'All three portals in one — recruit, meet, and message from a single unified platform.',
    portals: [
      { key: 'medmatch', name: 'MedMatch AI', icon: Briefcase, color: '#00B894', features: ['Full Job Toolkit'] },
      { key: 'karau', name: 'AI KARAU', icon: Video, color: '#6C5CE7', features: ['Video Meetings'] },
      { key: 'enzi', name: 'ENZI Messenger', icon: MessageCircle, color: '#00CEC9', features: ['Team Messaging'] },
    ],
    gradient: 'from-amber-400 to-orange-500',
    accentColor: '#F59E0B',
    isDefault: false,
    badge: 'Full Access',
  },
];

const PackageSelector = ({ onPackageSelected, currentPackage }) => {
  const navigate = useNavigate();
  const [selectedPkg, setSelectedPkg] = useState(currentPackage || null);
  const [saving, setSaving] = useState(false);
  const [hoveredPkg, setHoveredPkg] = useState(null);

  const handleSelect = async (pkgId) => {
    setSelectedPkg(pkgId);
    setSaving(true);
    try {
      const token = localStorage.getItem('medmatch-token') || localStorage.getItem('token') || localStorage.getItem('session_token');
      const headers = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const res = await fetch(`${API}/api/portal/set-package`, {
        method: 'POST',
        headers,
        credentials: 'include',
        body: JSON.stringify({ package_id: pkgId }),
      });

      if (res.ok) {
        const data = await res.json();
        localStorage.setItem('portal_package', pkgId);
        localStorage.setItem('portal_access', JSON.stringify(data.portals));
        toast.success(`Package selected: ${PACKAGES.find(p => p.id === pkgId)?.name}`);
        if (onPackageSelected) onPackageSelected(pkgId, data.portals);
      } else {
        toast.error('Failed to save package selection');
        setSelectedPkg(currentPackage);
      }
    } catch (e) {
      toast.error('Connection error');
      setSelectedPkg(currentPackage);
    }
    setSaving(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex flex-col" data-testid="package-selector">
      <style>{`
        .pkg-card {
          transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        .pkg-card:hover {
          transform: translateY(-8px) scale(1.01);
        }
        .pkg-card.selected {
          ring: 2px solid white;
        }
      `}</style>

      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/6 w-80 h-80 bg-violet-500/8 rounded-full blur-3xl animate-pulse" style={{ animationDuration: '5s' }} />
        <div className="absolute bottom-1/3 right-1/4 w-72 h-72 bg-teal-500/8 rounded-full blur-3xl animate-pulse" style={{ animationDuration: '6s', animationDelay: '1s' }} />
        <div className="absolute top-1/2 right-1/6 w-64 h-64 bg-amber-500/5 rounded-full blur-3xl animate-pulse" style={{ animationDuration: '7s', animationDelay: '2s' }} />
      </div>

      <div className="flex-1 flex flex-col items-center justify-center p-4 sm:p-6 relative z-10">
        {/* Header */}
        <div className="text-center mb-8 md:mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 text-slate-300 text-sm mb-6">
            <Package className="w-4 h-4" />
            Choose Your Package
          </div>
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-3" style={{ fontFamily: "'Manrope', sans-serif" }}>
            Select Your{' '}
            <span className="text-transparent bg-clip-text" style={{ backgroundImage: 'linear-gradient(135deg, #00CEC9, #6C5CE7, #F59E0B)' }}>
              Experience
            </span>
          </h1>
          <p className="text-base sm:text-lg text-slate-300 max-w-xl mx-auto">
            Pick the tools that fit your workflow. You can change your package anytime.
          </p>
        </div>

        {/* Package Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 max-w-5xl w-full px-4">
          {PACKAGES.map((pkg) => {
            const isSelected = selectedPkg === pkg.id;
            const isHovered = hoveredPkg === pkg.id;

            return (
              <Card
                key={pkg.id}
                data-testid={`package-${pkg.id}`}
                onMouseEnter={() => setHoveredPkg(pkg.id)}
                onMouseLeave={() => setHoveredPkg(null)}
                onClick={() => !saving && handleSelect(pkg.id)}
                className={`
                  pkg-card relative overflow-hidden cursor-pointer
                  bg-slate-800/60 backdrop-blur-md
                  ${isSelected
                    ? 'border-2 ring-1 ring-white/20'
                    : 'border border-slate-700/50 hover:border-slate-500/50'
                  }
                  active:scale-[0.98]
                `}
                style={isSelected ? { borderColor: pkg.accentColor } : {}}
              >
                {/* Badge */}
                <div className="absolute top-4 right-4">
                  <span className={`
                    inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold
                    ${pkg.id === 'enterprise'
                      ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                      : pkg.id === 'standard'
                        ? 'bg-violet-500/20 text-violet-300 border border-violet-500/30'
                        : 'bg-teal-500/20 text-teal-300 border border-teal-500/30'
                    }
                  `}>
                    {pkg.id === 'enterprise' && <Crown className="w-3 h-3" />}
                    {pkg.badge}
                  </span>
                </div>

                {/* Selected check */}
                {isSelected && (
                  <div className="absolute top-4 left-4 w-7 h-7 rounded-full flex items-center justify-center" style={{ backgroundColor: pkg.accentColor }}>
                    <Check className="w-4 h-4 text-white" />
                  </div>
                )}

                <div className="relative p-6">
                  {/* Package Header */}
                  <div className="mb-5 mt-4">
                    <h2 className="text-xl font-bold text-white mb-1" style={{ fontFamily: "'Manrope', sans-serif" }}>{pkg.name}</h2>
                    <p className={`text-sm font-medium bg-gradient-to-r ${pkg.gradient} bg-clip-text text-transparent`}>
                      {pkg.tagline}
                    </p>
                  </div>

                  {/* Description */}
                  <p className="text-sm text-slate-300 mb-5 leading-relaxed min-h-[48px]">
                    {pkg.description}
                  </p>

                  {/* Included Portals */}
                  <div className="space-y-3 mb-6">
                    <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Included Portals</p>
                    {pkg.portals.map((portal) => (
                      <div key={portal.key} className="flex items-start gap-3 p-2.5 rounded-lg bg-white/[0.03] border border-white/[0.04]">
                        <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" style={{ backgroundColor: portal.color + '20' }}>
                          <portal.icon className="w-4 h-4" style={{ color: portal.color }} />
                        </div>
                        <div className="min-w-0">
                          <p className="text-sm font-medium text-white">{portal.name}</p>
                          <p className="text-xs text-slate-400">{portal.features.join(' · ')}</p>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* CTA */}
                  <button
                    data-testid={`select-package-${pkg.id}`}
                    disabled={saving}
                    className={`
                      w-full py-3 px-5 rounded-xl font-semibold text-white text-sm
                      bg-gradient-to-r ${pkg.gradient}
                      flex items-center justify-center gap-2
                      transition-all duration-300 hover:shadow-lg
                      disabled:opacity-60
                    `}
                  >
                    {saving && selectedPkg === pkg.id ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : isSelected ? (
                      <>
                        <Check className="w-4 h-4" />
                        Selected
                      </>
                    ) : (
                      <>
                        Select Package
                        <ArrowRight className="w-4 h-4" />
                      </>
                    )}
                  </button>
                </div>
              </Card>
            );
          })}
        </div>

        {/* Footer */}
        <div className="mt-8 text-center">
          <p className="text-xs text-slate-400">
            All packages are free during beta. You can switch packages anytime from your settings.
          </p>
        </div>
      </div>
    </div>
  );
};

export default PackageSelector;
