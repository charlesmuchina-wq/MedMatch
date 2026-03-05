import { MessageCircle } from 'lucide-react';

const LUMI_ICON = '/lumi-icon.png';

const LumiFooter = ({ variant = 'default' }) => {
  const isCompact = variant === 'compact';
  const isOverlay = variant === 'overlay';

  if (isOverlay) {
    return (
      <div className="fixed bottom-0 left-0 right-0 z-20 pointer-events-none">
        <div className="flex items-center justify-center py-2">
          <span className="text-[10px] font-medium text-slate-400/60 tracking-widest uppercase pointer-events-auto" data-testid="lumi-footer-tagline">
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
          <div className="w-5 h-5 rounded overflow-hidden bg-slate-900 flex-shrink-0">
            <img src="/lumi-icon.png" alt="LUMI" className="w-5 h-5" />
          </div>
        )}
        <span className={`font-medium tracking-wide ${isCompact ? 'text-[9px] text-slate-500' : 'text-[10px] text-slate-600'}`}
          data-testid="lumi-footer-tagline">
          Intelligence in Every Conversation
        </span>
      </div>
    </footer>
  );
};

export default LumiFooter;
