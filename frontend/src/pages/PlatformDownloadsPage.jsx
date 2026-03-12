import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Monitor, Smartphone, Globe, Apple, Chrome, Download, ExternalLink, CheckCircle, Laptop } from 'lucide-react';
import { Card } from '@/components/ui/card';

const PLATFORMS = [
  {
    id: 'web',
    name: 'Web (PWA)',
    description: 'Install directly from your browser. Works on any device with full offline support.',
    icon: Globe,
    color: '#14b8a6',
    gradient: 'from-teal-400 to-cyan-500',
    status: 'available',
    features: ['Offline support', 'Push notifications', 'App shortcuts', 'Share target'],
    instructions: [
      'Visit ai-suite-test.preview.emergentagent.com in Chrome, Edge, or Safari',
      'Click the install icon in the address bar (or menu > "Install app")',
      'The app will be added to your home screen / desktop',
    ],
    cta: 'Open Web App',
    ctaLink: '/',
  },
  {
    id: 'windows',
    name: 'Windows',
    description: 'Native desktop app with system tray, auto-updates, and keyboard shortcuts.',
    icon: Monitor,
    color: '#6C5CE7',
    gradient: 'from-violet-500 to-indigo-600',
    status: 'available',
    features: ['System tray integration', 'Auto-updates', 'Offline detection', 'Deep linking'],
    instructions: [
      'Download the .exe installer from the Releases page',
      'Run the installer — no admin rights needed for portable version',
      'Launch AI Suite from the Start Menu or desktop shortcut',
    ],
    cta: 'Download for Windows',
    ctaLink: 'https://github.com/charlesmuchina-wq/MedMatch/releases',
  },
  {
    id: 'macos',
    name: 'macOS',
    description: 'Universal binary supporting Intel and Apple Silicon. Clean DMG installer.',
    icon: Apple,
    color: '#E84393',
    gradient: 'from-pink-500 to-rose-600',
    status: 'available',
    features: ['Apple Silicon native', 'Hidden title bar', 'Touch Bar support', 'Notarized'],
    instructions: [
      'Download the .dmg file from the Releases page',
      'Open the DMG and drag AI Suite to Applications',
      'Right-click > Open on first launch (Gatekeeper)',
    ],
    cta: 'Download for macOS',
    ctaLink: 'https://github.com/charlesmuchina-wq/MedMatch/releases',
  },
  {
    id: 'linux',
    name: 'Linux',
    description: 'AppImage format — no installation required. Works on all major distributions.',
    icon: Laptop,
    color: '#00B894',
    gradient: 'from-emerald-400 to-green-500',
    status: 'available',
    features: ['AppImage (portable)', 'System tray', 'Auto-updates', 'No root needed'],
    instructions: [
      'Download the .AppImage file from the Releases page',
      'Make it executable: chmod +x AI-Suite.AppImage',
      'Double-click or run from terminal to launch',
    ],
    cta: 'Download for Linux',
    ctaLink: 'https://github.com/charlesmuchina-wq/MedMatch/releases',
  },
  {
    id: 'android',
    name: 'Android',
    description: 'Full native experience with push notifications, biometrics, and camera access.',
    icon: Smartphone,
    color: '#00CEC9',
    gradient: 'from-teal-400 to-cyan-500',
    status: 'available',
    features: ['Push notifications', 'Biometric auth', 'Camera & mic', 'Background sync'],
    instructions: [
      'Download the APK from the Releases page or install from Google Play',
      'Enable "Install from unknown sources" if using APK',
      'Open the app and sign in with your account',
    ],
    cta: 'Download APK',
    ctaLink: 'https://github.com/charlesmuchina-wq/MedMatch/releases',
  },
  {
    id: 'ios',
    name: 'iOS / iPadOS',
    description: 'Available via TestFlight for beta testing. Full App Store release coming soon.',
    icon: Apple,
    color: '#6C5CE7',
    gradient: 'from-violet-500 to-purple-600',
    status: 'beta',
    features: ['TestFlight beta', 'Push notifications', 'Face ID / Touch ID', 'iPad optimized'],
    instructions: [
      'Install TestFlight from the App Store',
      'Request a TestFlight invite from your admin',
      'Open the TestFlight link to install the beta',
    ],
    cta: 'Join TestFlight',
    ctaLink: 'https://testflight.apple.com/join/medmatch',
  },
  {
    id: 'teams',
    name: 'Microsoft Teams',
    description: 'Access AI KARAU meetings, ENZI messenger, and MedMatch jobs inside Teams.',
    icon: Monitor,
    color: '#6264A7',
    gradient: 'from-indigo-500 to-violet-600',
    status: 'available',
    features: ['Personal tabs for all portals', 'Schedule meetings from compose', 'Search jobs inline'],
    instructions: [
      'Go to Teams > Apps > Manage your apps',
      'Click "Upload a custom app" at the bottom',
      'Upload the AI Suite Teams package (.zip)',
    ],
    cta: 'Setup Guide',
    ctaLink: null,
  },
  {
    id: 'outlook',
    name: 'Microsoft Outlook',
    description: 'Schedule and join AI KARAU meetings directly from your Outlook calendar.',
    icon: Chrome,
    color: '#0078D4',
    gradient: 'from-blue-500 to-cyan-600',
    status: 'available',
    features: ['Add meetings from calendar', 'Join from event view', 'Create from email'],
    instructions: [
      'Go to Outlook Web > Settings > Manage Integrations',
      'Click "My add-ins" > "Add a custom add-in" > "Add from file"',
      'Upload the outlook-addin.xml file',
    ],
    cta: 'Setup Guide',
    ctaLink: null,
  },
];

export default function PlatformDownloadsPage() {
  const navigate = useNavigate();
  const [expanded, setExpanded] = useState(null);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      <style>{`
        .platform-card { transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
        .platform-card:hover { transform: translateY(-4px); }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        .fade-in { animation: fadeIn 0.3s ease-out forwards; }
      `}</style>

      {/* Header */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 pt-6 pb-4">
        <button
          data-testid="downloads-back-btn"
          onClick={() => navigate('/')}
          className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Portal
        </button>

        <div className="text-center mb-10">
          <h1 className="text-3xl sm:text-4xl font-bold mb-3">
            Get{' '}
            <span className="text-transparent bg-clip-text" style={{ backgroundImage: 'linear-gradient(135deg, #00CEC9, #6C5CE7, #E84393)' }}>
              AI Suite
            </span>
            {' '}on Every Device
          </h1>
          <p className="text-base text-slate-300 max-w-lg mx-auto">
            Download for desktop, mobile, or integrate with Microsoft apps. Same account, everywhere.
          </p>
        </div>
      </div>

      {/* Platform Grid */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 pb-12">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {PLATFORMS.map((platform, idx) => {
            const Icon = platform.icon;
            const isExpanded = expanded === platform.id;

            return (
              <Card
                key={platform.id}
                data-testid={`platform-${platform.id}`}
                className="platform-card relative overflow-hidden cursor-pointer bg-slate-800/60 border-slate-700/50 backdrop-blur-md hover:border-slate-500/50"
                onClick={() => setExpanded(isExpanded ? null : platform.id)}
                style={{ animationDelay: `${idx * 50}ms` }}
              >
                {/* Status badge */}
                <div className="absolute top-3 right-3">
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                    platform.status === 'available'
                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                      : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                  }`}>
                    {platform.status === 'available' ? 'Available' : 'Beta'}
                  </span>
                </div>

                <div className="p-5">
                  {/* Icon + Name */}
                  <div className="flex items-center gap-3 mb-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center bg-gradient-to-br ${platform.gradient}`}>
                      <Icon className="w-5 h-5 text-white" />
                    </div>
                    <h3 className="text-base font-bold text-white">{platform.name}</h3>
                  </div>

                  <p className="text-xs text-white/70 mb-3 leading-relaxed">{platform.description}</p>

                  {/* Features */}
                  <div className="flex flex-wrap gap-1.5 mb-3">
                    {platform.features.map((feat) => (
                      <span key={feat} className="inline-flex items-center gap-1 text-[10px] text-slate-300 bg-white/[0.05] px-2 py-0.5 rounded-md">
                        <CheckCircle className="w-2.5 h-2.5 text-emerald-400" />
                        {feat}
                      </span>
                    ))}
                  </div>

                  {/* Expanded instructions */}
                  {isExpanded && (
                    <div className="fade-in mt-3 pt-3 border-t border-white/10">
                      <p className="text-[11px] text-slate-400 font-semibold uppercase tracking-wider mb-2">Installation Steps</p>
                      <ol className="space-y-1.5">
                        {platform.instructions.map((step, i) => (
                          <li key={i} className="flex gap-2 text-xs text-white/80">
                            <span className="flex-shrink-0 w-4 h-4 rounded-full bg-white/10 flex items-center justify-center text-[10px] font-bold text-slate-300">
                              {i + 1}
                            </span>
                            <span>{step}</span>
                          </li>
                        ))}
                      </ol>
                    </div>
                  )}

                  {/* CTA */}
                  {platform.ctaLink ? (
                    <a
                      href={platform.ctaLink}
                      target={platform.ctaLink.startsWith('http') ? '_blank' : undefined}
                      rel="noopener noreferrer"
                      data-testid={`download-${platform.id}-btn`}
                      onClick={(e) => e.stopPropagation()}
                      className={`mt-3 w-full py-2 px-4 rounded-lg font-semibold text-white text-xs bg-gradient-to-r ${platform.gradient} flex items-center justify-center gap-2 transition-all duration-200 hover:shadow-lg hover:brightness-110 active:scale-[0.98]`}
                    >
                      {platform.cta}
                      {platform.ctaLink.startsWith('http') ? <ExternalLink className="w-3 h-3" /> : <Download className="w-3 h-3" />}
                    </a>
                  ) : (
                    <button
                      data-testid={`download-${platform.id}-btn`}
                      onClick={(e) => { e.stopPropagation(); setExpanded(isExpanded ? null : platform.id); }}
                      className={`mt-3 w-full py-2 px-4 rounded-lg font-semibold text-white text-xs bg-gradient-to-r ${platform.gradient} flex items-center justify-center gap-2 transition-all duration-200 hover:shadow-lg hover:brightness-110 active:scale-[0.98]`}
                    >
                      {isExpanded ? 'Hide Steps' : platform.cta}
                      <Download className="w-3 h-3" />
                    </button>
                  )}
                </div>
              </Card>
            );
          })}
        </div>

        {/* System Requirements */}
        <div className="mt-10 p-6 rounded-xl bg-slate-800/40 border border-slate-700/40 backdrop-blur-sm">
          <h2 className="text-lg font-bold text-white mb-4">System Requirements</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs text-slate-300">
            <div>
              <h3 className="font-semibold text-white mb-1">Desktop</h3>
              <p>Windows 10+ / macOS 11+ / Ubuntu 20.04+</p>
              <p>4 GB RAM, 200 MB disk space</p>
            </div>
            <div>
              <h3 className="font-semibold text-white mb-1">Android</h3>
              <p>Android 8.0 (Oreo) or later</p>
              <p>2 GB RAM, 100 MB storage</p>
            </div>
            <div>
              <h3 className="font-semibold text-white mb-1">iOS</h3>
              <p>iOS 15.0 or later</p>
              <p>iPhone 8 or newer, iPad (6th gen+)</p>
            </div>
            <div>
              <h3 className="font-semibold text-white mb-1">Web (PWA)</h3>
              <p>Chrome 90+, Edge 90+, Safari 15+</p>
              <p>Any device with a modern browser</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
