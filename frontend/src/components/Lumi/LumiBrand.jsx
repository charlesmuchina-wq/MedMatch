/**
 * LumiBrand - LUMI branding component using the official logo
 * Uses the actual LUMI logo imagery with cyan/blue/pink chat bubble
 */

const GRADIENT = 'linear-gradient(135deg, #00CEC9, #6C5CE7, #E84393)';

export const LumiBrand = ({ variant = 'icon-dark', size = 'md', className = '', showTagline = false }) => {
  const sizes = {
    xs: { icon: 'w-7 h-7', text: 'text-sm', tagline: 'text-[8px]', logo: 'h-16' },
    sm: { icon: 'w-9 h-9', text: 'text-base', tagline: 'text-[9px]', logo: 'h-20' },
    md: { icon: 'w-12 h-12', text: 'text-xl', tagline: 'text-[10px]', logo: 'h-28' },
    lg: { icon: 'w-16 h-16', text: 'text-3xl', tagline: 'text-xs', logo: 'h-36' },
    xl: { icon: 'w-24 h-24', text: 'text-4xl', tagline: 'text-sm', logo: 'h-48' },
  };
  const s = sizes[size] || sizes.md;
  const isDark = variant.includes('dark');

  // Full logo (bubble + text + tagline)
  if (variant === 'full-dark' || variant === 'full-light') {
    return (
      <div className={`flex flex-col items-center ${className}`} data-testid="lumi-brand">
        <img src="/lumi-logo-official.png" alt="LUMI" className={`${s.logo} object-contain`} />
      </div>
    );
  }

  // Just the bubble icon
  if (variant === 'icon-dark' || variant === 'icon-light') {
    return (
      <div className={`${s.icon} flex-shrink-0 flex items-center justify-center ${className}`} data-testid="lumi-brand-icon">
        <img src="/lumi-bubble-official.png" alt="LUMI" className="w-full h-full object-contain" />
      </div>
    );
  }

  // Gradient text
  if (variant === 'text-dark' || variant === 'text-light') {
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

  // Inline: icon + gradient text (for sidebar headers)
  if (variant === 'inline-dark' || variant === 'inline-light') {
    return (
      <div className={`flex items-center gap-2 ${className}`} data-testid="lumi-brand">
        <div className={`${s.icon} flex-shrink-0 flex items-center justify-center`}>
          <img src="/lumi-bubble-official.png" alt="LUMI" className="w-full h-full object-contain" />
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
