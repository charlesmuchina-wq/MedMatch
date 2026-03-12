const GRADIENT = 'linear-gradient(135deg, #00CEC9, #6C5CE7, #E84393)';

const LumiFooter = ({ variant = 'default' }) => {
  const isCompact = variant === 'compact';
  const isOverlay = variant === 'overlay';

  if (isOverlay) {
    return (
      <div className="fixed bottom-0 left-0 right-0 z-20 pointer-events-none">
        <div className="flex items-center justify-center py-2">
          <span className="text-[10px] font-medium text-slate-500 tracking-widest uppercase pointer-events-auto" data-testid="lumi-footer-tagline">
            Intelligence in Every Conversation
          </span>
        </div>
      </div>
    );
  }

  return (
    <footer className={`flex-shrink-0 border-t ${isCompact ? 'py-2 px-4' : 'py-3 px-6'} bg-inherit`}
      style={{ borderColor: 'rgba(148,163,184,0.15)' }}
      data-testid="lumi-footer">
      <div className="flex items-center justify-center gap-2">
        {!isCompact && (
          <div className="w-5 h-5 rounded overflow-hidden flex-shrink-0">
            <img src="/enzi-logo-icon.png" alt="ENZI" className="w-5 h-5 object-contain" />
          </div>
        )}
        <span className={`font-semibold tracking-wide ${isCompact ? 'text-[9px]' : 'text-[10px]'}`}
          style={{ background: GRADIENT, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}
          data-testid="lumi-footer-tagline">
          Intelligence in Every Conversation
        </span>
      </div>
    </footer>
  );
};

export default LumiFooter;
