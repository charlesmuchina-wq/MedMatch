import { useState, useEffect, useRef } from 'react';

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

/**
 * Floating reaction animation component
 */
const FloatingEmoji = ({ emoji, id, onDone }) => {
  const [style, setStyle] = useState({});

  useEffect(() => {
    const left = 20 + Math.random() * 60;
    setStyle({
      position: 'absolute',
      left: `${left}%`,
      bottom: '0',
      fontSize: '2rem',
      animation: 'floatUp 2.5s ease-out forwards',
      pointerEvents: 'none',
      zIndex: 50
    });
    const timer = setTimeout(() => onDone(id), 2600);
    return () => clearTimeout(timer);
  }, [id, onDone]);

  return <div style={style}>{emoji}</div>;
};

/**
 * Reactions bar + floating emoji overlay
 */
const MeetingReactions = ({ onSendReaction, incomingReaction }) => {
  const [showBar, setShowBar] = useState(false);
  const [floatingEmojis, setFloatingEmojis] = useState([]);
  const nextId = useRef(0);

  const addFloating = (emoji) => {
    const id = nextId.current++;
    setFloatingEmojis(prev => [...prev, { id, emoji }]);
  };

  const removeFloating = (id) => {
    setFloatingEmojis(prev => prev.filter(e => e.id !== id));
  };

  // Handle incoming reactions from other participants
  useEffect(() => {
    if (incomingReaction) {
      addFloating(incomingReaction.emoji);
    }
  }, [incomingReaction]);

  const handleReaction = (emoji) => {
    addFloating(emoji);
    onSendReaction?.(emoji);
    setShowBar(false);
  };

  return (
    <>
      {/* Floating emoji container */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none" data-testid="reaction-overlay">
        {floatingEmojis.map(({ id, emoji }) => (
          <FloatingEmoji key={id} id={id} emoji={emoji} onDone={removeFloating} />
        ))}
      </div>

      {/* Reaction bar */}
      {showBar && (
        <div className="absolute bottom-28 left-1/2 -translate-x-1/2 z-40 bg-slate-800/95 backdrop-blur rounded-full px-3 py-2 flex gap-1 border border-slate-600 shadow-xl animate-in slide-in-from-bottom-2 duration-200"
          data-testid="reaction-bar">
          {EMOJI_OPTIONS.map(({ emoji, label }) => (
            <button
              key={label}
              onClick={() => handleReaction(emoji)}
              className="w-10 h-10 rounded-full hover:bg-slate-700 flex items-center justify-center text-xl transition-transform hover:scale-125"
              title={label}
              data-testid={`reaction-${label.toLowerCase().replace(' ', '-')}`}
            >
              {emoji}
            </button>
          ))}
        </div>
      )}

      {/* Toggle button - render as part of the control bar */}
      <button
        onClick={() => setShowBar(!showBar)}
        className={`rounded-full w-12 h-12 flex items-center justify-center text-lg transition-colors ${
          showBar ? 'bg-turquoise text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
        }`}
        title="Reactions"
        data-testid="control-reactions"
      >
        {'\ud83d\udc4d'}
      </button>

      {/* CSS for float animation */}
      <style>{`
        @keyframes floatUp {
          0% { transform: translateY(0) scale(1); opacity: 1; }
          50% { opacity: 1; }
          100% { transform: translateY(-300px) scale(1.5); opacity: 0; }
        }
      `}</style>
    </>
  );
};

export default MeetingReactions;
