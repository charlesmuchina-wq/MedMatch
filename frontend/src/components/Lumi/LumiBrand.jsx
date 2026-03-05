/**
 * LumiBrand - Adaptive LUMI branding component
 * Uses CSS gradients matching the official logo: cyan (#00CEC9) → pink (#E84393)
 * 
 * Variants:
 * - "full-dark": Full logo image on dark bg (login hero, portal)
 * - "icon-dark": Small bubble icon for dark bg (sidebar header)
 * - "icon-light": Small bubble icon for light bg
 * - "text-dark": Gradient text on dark bg
 * - "text-light": Gradient text on light bg
 * - "inline-light": Inline icon + text for light bg
 * - "inline-dark": Inline icon + text for dark bg
 */

const GRADIENT = 'linear-gradient(135deg, #00CEC9, #6C5CE7, #E84393)';

export const LumiBrand = ({ variant = 'icon-dark', size = 'md', className = '', showTagline = false }) => {
  const sizes = {
    xs: { icon: 'w-6 h-6', text: 'text-sm', tagline: 'text-[8px]', logo: 'h-10' },
    sm: { icon: 'w-8 h-8', text: 'text-base', tagline: 'text-[9px]', logo: 'h-16' },
    md: { icon: 'w-12 h-12', text: 'text-xl', tagline: 'text-[10px]', logo: 'h-24' },
    lg: { icon: 'w-16 h-16', text: 'text-3xl', tagline: 'text-xs', logo: 'h-32' },
    xl: { icon: 'w-24 h-24', text: 'text-4xl', tagline: 'text-sm', logo: 'h-48' },
  };
  const s = sizes[size] || sizes.md;

  // Full logo image (for dark backgrounds)
  if (variant === 'full-dark') {
    return (
      <div className={`flex flex-col items-center ${className}`} data-testid="lumi-brand">
        <img src="/lumi-hero.png" alt="LUMI" className={`${s.logo} object-contain`} />
      </div>
    );
  }

  // Just the bubble icon
  if (variant === 'icon-dark' || variant === 'icon-light') {
    return (
      <div className={`${s.icon} rounded-xl overflow-hidden flex-shrink-0 ${variant === 'icon-light' ? 'bg-slate-800 p-1.5' : 'bg-white/20 p-1 ring-1 ring-white/10'} ${className}`} data-testid="lumi-brand-icon">
        <img src="/lumi-bubble.png" alt="LUMI" className="w-full h-full object-contain" />
      </div>
    );
  }

  // Gradient text (matches the logo's cyan→pink gradient)
  if (variant === 'text-dark' || variant === 'text-light') {
    const isDark = variant === 'text-dark';
    return (
      <div className={`flex flex-col items-center ${className}`} data-testid="lumi-brand">
        <span className={`${s.text} font-black tracking-[0.15em] uppercase`}
          style={{ background: GRADIENT, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
          LUMI
        </span>
        {showTagline && (
          <span className={`${s.tagline} font-medium mt-0.5 tracking-wide ${isDark ? 'text-white/90' : 'text-slate-500'}`}>
            Intelligence in Every Conversation
          </span>
        )}
      </div>
    );
  }

  // Inline: icon + gradient text
  if (variant === 'inline-dark' || variant === 'inline-light') {
    const isDark = variant === 'inline-dark';
    return (
      <div className={`flex items-center gap-3 ${className}`} data-testid="lumi-brand">
        <div className={`${s.icon} rounded-xl overflow-hidden flex-shrink-0 ${isDark ? 'bg-white/20 p-0.5 ring-1 ring-white/10' : 'bg-slate-800 p-1'}`}>
          <img src="/lumi-bubble.png" alt="LUMI" className="w-full h-full object-contain" />
        </div>
        <div className="flex flex-col">
          <span className={`${s.text} font-black tracking-[0.12em] uppercase leading-tight`}
            style={{ background: GRADIENT, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
            LUMI
          </span>
          {showTagline && (
            <span className={`${s.tagline} font-medium tracking-wide ${isDark ? 'text-white/90' : 'text-slate-500'}`}>
              Intelligence in Every Conversation
            </span>
          )}
        </div>
      </div>
    );
  }

  return null;
};
