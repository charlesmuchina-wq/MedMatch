import { useState, useEffect } from "react";
import { useDataChannel } from "@livekit/components-react";
import { Hand } from "lucide-react";

const enc = (obj) => new TextEncoder().encode(JSON.stringify(obj));

// Attendee-facing button: broadcasts a raise/lower-hand signal over the LiveKit
// data channel. Re-broadcasts while raised so a host who joins later still sees it.
export default function RaiseHandButton() {
  const { send } = useDataChannel("handraise");
  const [raised, setRaised] = useState(false);

  const toggle = () => {
    const next = !raised;
    setRaised(next);
    try { send(enc({ raised: next }), { reliable: true }); } catch {}
  };

  useEffect(() => {
    if (!raised) return;
    const id = setInterval(() => {
      try { send(enc({ raised: true }), { reliable: true }); } catch {}
    }, 4000);
    return () => clearInterval(id);
  }, [raised, send]);

  return (
    <button
      onClick={toggle}
      data-testid="raise-hand-btn"
      className={`absolute bottom-24 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium shadow-lg transition-colors ${
        raised ? "bg-amber-500 text-white" : "bg-white/10 text-white hover:bg-white/20 backdrop-blur"
      }`}
    >
      <Hand className={`w-4 h-4 ${raised ? "animate-bounce" : ""}`} />
      {raised ? "Lower hand" : "Raise hand"}
    </button>
  );
}
