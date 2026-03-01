import { useState, useEffect, useRef, useCallback } from 'react';
import { Button } from '@/components/ui/button';

const API = process.env.REACT_APP_BACKEND_URL;

const REACTIONS = [
  { key: 'thumbsup', emoji: '👍', label: 'Thumbs Up' },
  { key: 'clap', emoji: '👏', label: 'Clap' },
  { key: 'heart', emoji: '❤️', label: 'Heart' },
  { key: 'laugh', emoji: '😂', label: 'Laugh' },
  { key: 'fire', emoji: '🔥', label: 'Fire' },
  { key: 'mindblown', emoji: '🤯', label: 'Mind Blown' },
  { key: 'wave', emoji: '👋', label: 'Wave' },
  { key: '100', emoji: '💯', label: '100' },
];

/**
 * Floating emoji reactions: a picker bar + animated floating bubbles.
 */
export function EmojiReactions({ webinarId, senderName, show, onToggle }) {
  const [floatingEmojis, setFloatingEmojis] = useState([]);
  const [cooldown, setCooldown] = useState(false);
  const pollRef = useRef(null);
  const seenRef = useRef(new Set());

  // Poll for recent reactions from others
  useEffect(() => {
    if (!webinarId) return;
    const poll = async () => {
      try {
        const res = await fetch(`${API}/api/karau/webinar/${webinarId}/reactions/recent?limit=10`);
        if (res.ok) {
          const data = await res.json();
          const newOnes = (data.reactions || []).filter(r => !seenRef.current.has(r.reaction_id));
          newOnes.forEach(r => {
            seenRef.current.add(r.reaction_id);
            addFloater(r.emoji, r.sender_name);
          });
          // Keep seen set manageable
          if (seenRef.current.size > 200) {
            const arr = [...seenRef.current];
            seenRef.current = new Set(arr.slice(-100));
          }
        }
      } catch {}
    };
    poll();
    pollRef.current = setInterval(poll, 3000);
    return () => clearInterval(pollRef.current);
  }, [webinarId]);

  const addFloater = useCallback((emoji, name) => {
    const id = Date.now() + Math.random();
    const x = 10 + Math.random() * 80; // random horizontal position %
    setFloatingEmojis(prev => [...prev.slice(-15), { id, emoji, name, x }]);
    // Auto-remove after animation
    setTimeout(() => {
      setFloatingEmojis(prev => prev.filter(f => f.id !== id));
    }, 3000);
  }, []);

  const sendReaction = async (reactionKey) => {
    if (cooldown) return;
    setCooldown(true);
    setTimeout(() => setCooldown(false), 800);

    const emoji = REACTIONS.find(r => r.key === reactionKey)?.emoji || reactionKey;
    addFloater(emoji, 'You');

    const token = localStorage.getItem('token') || localStorage.getItem('karau_token');
    try {
      await fetch(`${API}/api/karau/webinar/${webinarId}/reaction`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ reaction: reactionKey, sender_name: senderName || '' })
      });
    } catch {}
  };

  return (
    <>
      {/* Floating emoji bubbles */}
      <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden" data-testid="floating-reactions-container">
        {floatingEmojis.map(f => (
          <div
            key={f.id}
            className="absolute animate-float-up"
            style={{
              left: `${f.x}%`,
              bottom: '80px',
            }}
            data-testid="floating-reaction"
          >
            <div className="flex flex-col items-center">
              <span className="text-3xl drop-shadow-lg">{f.emoji}</span>
              {f.name && <span className="text-[8px] text-white/60 mt-0.5 whitespace-nowrap">{f.name}</span>}
            </div>
          </div>
        ))}
      </div>

      {/* Reaction picker bar */}
      {show && (
        <div className="absolute bottom-16 left-1/2 -translate-x-1/2 z-40" data-testid="reaction-picker">
          <div className="flex items-center gap-1 px-3 py-2 bg-karau-card/95 backdrop-blur-xl rounded-2xl border border-white/10 shadow-2xl">
            {REACTIONS.map(r => (
              <button
                key={r.key}
                onClick={() => sendReaction(r.key)}
                disabled={cooldown}
                className="w-9 h-9 flex items-center justify-center rounded-xl hover:bg-white/10 active:scale-90 transition-all disabled:opacity-50"
                title={r.label}
                data-testid={`reaction-btn-${r.key}`}
              >
                <span className="text-xl">{r.emoji}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </>
  );
}

export default EmojiReactions;
