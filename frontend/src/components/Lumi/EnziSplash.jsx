import { useState, useEffect } from 'react';
import { LumiBrand } from './LumiBrand';

const EnziSplash = ({ onComplete }) => {
  const [phase, setPhase] = useState(0);

  useEffect(() => {
    const t1 = setTimeout(() => setPhase(1), 100);
    const t2 = setTimeout(() => setPhase(2), 600);
    const t3 = setTimeout(() => setPhase(3), 1400);
    const t4 = setTimeout(() => onComplete(), 2200);
    return () => { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3); clearTimeout(t4); };
  }, [onComplete]);

  return (
    <div className={`fixed inset-0 z-[100] bg-[#0D1117] flex items-center justify-center transition-opacity duration-500 ${phase >= 3 ? 'opacity-0 pointer-events-none' : 'opacity-100'}`}
      data-testid="enzi-splash">
      <div className="flex flex-col items-center gap-6">
        {/* Icon */}
        <div className={`transition-all duration-700 ease-out ${phase >= 1 ? 'opacity-100 scale-100' : 'opacity-0 scale-50'}`}>
          <div className="w-20 h-20 relative">
            <img src="/enzi-logo-icon.png" alt="ENZI" className="w-full h-full object-contain" />
            <div className={`absolute inset-0 rounded-full transition-opacity duration-1000 ${phase >= 2 ? 'opacity-0' : 'opacity-100'}`}
              style={{ boxShadow: '0 0 40px 10px rgba(0,206,201,0.3), 0 0 80px 30px rgba(108,92,231,0.15)' }} />
          </div>
        </div>

        {/* Text */}
        <div className={`transition-all duration-700 ease-out delay-200 ${phase >= 2 ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <h1 className="text-4xl font-black tracking-[0.2em] text-center"
            style={{ background: 'linear-gradient(135deg, #00CEC9, #6C5CE7, #E84393)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            ENZI
          </h1>
          <p className={`text-[11px] text-white/40 tracking-[0.3em] uppercase text-center mt-2 transition-all duration-500 delay-500 ${phase >= 2 ? 'opacity-100' : 'opacity-0'}`}>
            Intelligence in Every Conversation
          </p>
        </div>

        {/* Loading bar */}
        <div className={`w-32 h-0.5 bg-white/5 rounded-full overflow-hidden transition-opacity duration-300 ${phase >= 2 ? 'opacity-100' : 'opacity-0'}`}>
          <div className="h-full rounded-full transition-all duration-1000 ease-out"
            style={{ width: phase >= 2 ? '100%' : '0%', background: 'linear-gradient(90deg, #00CEC9, #6C5CE7, #E84393)' }} />
        </div>
      </div>
    </div>
  );
};

export default EnziSplash;
