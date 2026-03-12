/**
 * LumiBrand - ENZI branding using CSS-rendered icon + gradient text
 * The chat bubble icon is rendered from cropped PNG (icon-only) files
 * Uses transparent version for light backgrounds, dark version for dark backgrounds
 */

const GRADIENT = 'linear-gradient(135deg, #00CEC9, #6C5CE7, #E84393)';

// Icon-only crops (brain-network neural icon)
const ICON_DARK = '/enzi-logo-icon.png';
const ICON_LIGHT = '/enzi-logo-transparent.png';

// Full logos (brain icon + text)
const FULL_DARK = '/enzi-logo-icon.png';
const FULL_LIGHT = '/enzi-logo-transparent.png';

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

  // Full logo (bubble + text + tagline in one image)
  if (variant === 'full-dark' || variant === 'full-light') {
    return (
      <div className={`flex flex-col items-center ${className}`} data-testid="lumi-brand">
        <div className={`${s.icon} flex-shrink-0 flex items-center justify-center mb-2`}>
          <img src={isDark ? ICON_DARK : ICON_LIGHT} alt="ENZI" className="w-full h-full object-contain" />
        </div>
        <span className={`${s.text} font-black tracking-[0.15em] uppercase`}
          style={{ background: GRADIENT, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
          ENZI
        </span>
        <span className={`${s.tagline} font-medium mt-1 tracking-wide ${isDark ? 'text-white/90' : 'text-slate-500'}`}>
          Intelligence in Every Conversation
        </span>
      </div>
    );
  }

  // Just the bubble icon (cropped, no text)
  if (variant === 'icon-dark' || variant === 'icon-light') {
    return (
      <div className={`${s.icon} flex-shrink-0 flex items-center justify-center ${className}`} data-testid="lumi-brand-icon">
        <img src={isDark ? ICON_DARK : ICON_LIGHT} alt="ENZI" className="w-full h-full object-contain" />
      </div>
    );
  }

  // Gradient text only
  if (variant === 'text-dark' || variant === 'text-light') {
    return (
      <div className={`flex flex-col items-center ${className}`} data-testid="lumi-brand">
        <span className={`${s.text} font-black tracking-[0.15em] uppercase`}
          style={{ background: GRADIENT, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
          ENZI
        </span>
        {showTagline && (
          <span className={`${s.tagline} font-medium mt-0.5 tracking-wide ${isDark ? 'text-white/90' : 'text-slate-500'}`}>
            Intelligence in Every Conversation
          </span>
        )}
      </div>
    );
  }

  // Inline: bubble icon + gradient text (for sidebar/dashboard headers)
  if (variant === 'inline-dark' || variant === 'inline-light') {
    return (
      <div className={`flex items-center gap-2.5 ${className}`} data-testid="lumi-brand">
        <div className={`${s.icon} flex-shrink-0 flex items-center justify-center`}>
          <img src={isDark ? ICON_DARK : ICON_LIGHT} alt="ENZI" className="w-full h-full object-contain" />
        </div>
        <div className="flex flex-col">
          <span className={`${s.text} font-black tracking-[0.12em] uppercase leading-tight`}
            style={{ background: GRADIENT, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
            ENZI
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
