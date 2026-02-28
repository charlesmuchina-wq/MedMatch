import { useState, useEffect, useRef, useCallback } from 'react';

const EMOJI_OPTIONS = [
  { emoji: '\ud83d\udc4d', label: 'Thumbs Up' },
  { emoji: '\ud83d\udc4f', label: 'Clap' },
  { emoji: '\u2764\ufe0f', label: 'Heart' },
  { emoji: '\ud83d\ude02', label: 'Laugh' },
  { emoji: '\ud83c\udf89', label: 'Celebrate' },
  { emoji: '\ud83d\ude2e', label: 'Surprise' },
  { emoji: '\ud83d\ude4f', label: 'Thanks' },
  { emoji: '\ud83d\udd25', label: 'Fire' }
];

const FloatingEmoji = ({ emoji, id, onDone }) => {
  const [style, setStyle] = useState({});

  useEffect(() => {
    const left = 10 + Math.random() * 80;
    const size = 1.5 + Math.random() * 1.5;
    const duration = 2 + Math.random() * 1.5;
    const drift = -30 + Math.random() * 60;
    const rotation = -20 + Math.random() * 40;

    setStyle({
      position: 'absolute',
      left: `${left}%`,
      bottom: '10%',
      fontSize: `${size}rem`,
      animation: `floatReaction ${duration}s ease-out forwards`,
      '--drift': `${drift}px`,
      '--rotation': `${rotation}deg`,
      pointerEvents: 'none',
      zIndex: 50,
      filter: 'drop-shadow(0 2px 8px rgba(0,0,0,0.3))'
    });
    const timer = setTimeout(() => onDone(id), duration * 1000 + 100);
    return () => clearTimeout(timer);
  }, [id, onDone]);

  return <div style={style}>{emoji}</div>;
};

const BurstParticle = ({ emoji, id, onDone }) => {
  const [style, setStyle] = useState({});

  useEffect(() => {
    const angle = Math.random() * Math.PI * 2;
    const distance = 60 + Math.random() * 100;
    const dx = Math.cos(angle) * distance;
    const dy = Math.sin(angle) * distance;

    setStyle({
      position: 'absolute',
      left: '50%',
      top: '50%',
      fontSize: `${0.8 + Math.random() * 0.8}rem`,
      animation: 'burstOut 0.8s ease-out forwards',
      '--bx': `${dx}px`,
      '--by': `${dy}px`,
      pointerEvents: 'none',
      zIndex: 50
    });
    const timer = setTimeout(() => onDone(id), 900);
    return () => clearTimeout(timer);
  }, [id, onDone]);

  return <div style={style}>{emoji}</div>;
};

const MeetingReactions = ({ onSendReaction, incomingReaction, showBar, onToggleBar }) => {
  const [floatingEmojis, setFloatingEmojis] = useState([]);
  const [burstParticles, setBurstParticles] = useState([]);
  const nextId = useRef(0);

  const addFloating = useCallback((emoji) => {
    const id = nextId.current++;
    setFloatingEmojis(prev => [...prev, { id, emoji }]);

    if (emoji === '\ud83c\udf89' || emoji === '\ud83d\udd25') {
      for (let i = 0; i < 6; i++) {
        const pid = nextId.current++;
        setTimeout(() => {
          setBurstParticles(prev => [...prev, { id: pid, emoji }]);
        }, i * 50);
      }
    }
  }, []);

  const removeFloating = useCallback((id) => {
    setFloatingEmojis(prev => prev.filter(e => e.id !== id));
  }, []);

  const removeBurst = useCallback((id) => {
    setBurstParticles(prev => prev.filter(e => e.id !== id));
  }, []);

  useEffect(() => {
    if (incomingReaction) addFloating(incomingReaction.emoji);
  }, [incomingReaction, addFloating]);

  const handleReaction = (emoji) => {
    addFloating(emoji);
    onSendReaction?.(emoji);
    onToggleBar?.(false);
  };

  return (
    <>
      {/* Floating emojis overlay */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none" data-testid="reaction-overlay">
        {floatingEmojis.map(({ id, emoji }) => (
          <FloatingEmoji key={id} id={id} emoji={emoji} onDone={removeFloating} />
        ))}
        {burstParticles.map(({ id, emoji }) => (
          <BurstParticle key={id} id={id} emoji={emoji} onDone={removeBurst} />
        ))}
      </div>

      {/* Reaction picker bar */}
      {showBar && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-40 bg-karau-card/95 backdrop-blur-xl rounded-2xl px-2 py-1.5 flex gap-0.5 border border-white/10/50 shadow-2xl shadow-black/30"
          data-testid="reaction-bar">
          {EMOJI_OPTIONS.map(({ emoji, label }) => (
            <button
              key={label}
              onClick={() => handleReaction(emoji)}
              className="w-10 h-10 rounded-xl hover:bg-karau-surface/60 flex items-center justify-center text-xl transition-all duration-150 hover:scale-125 active:scale-95"
              title={label}
              data-testid={`reaction-${label.toLowerCase().replace(' ', '-')}`}
            >
              {emoji}
            </button>
          ))}
        </div>
      )}

      <style>{`
        @keyframes floatReaction {
          0% { transform: translateY(0) translateX(0) rotate(0deg) scale(1); opacity: 1; }
          30% { opacity: 1; }
          100% { transform: translateY(-350px) translateX(var(--drift)) rotate(var(--rotation)) scale(1.3); opacity: 0; }
        }
        @keyframes burstOut {
          0% { transform: translate(-50%, -50%) scale(0.5); opacity: 1; }
          100% { transform: translate(calc(-50% + var(--bx)), calc(-50% + var(--by))) scale(1); opacity: 0; }
        }
      `}</style>
    </>
  );
};

export default MeetingReactions;
