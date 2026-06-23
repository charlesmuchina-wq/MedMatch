import { useState, useEffect } from "react";
import { useDataChannel, useLocalParticipant } from "@livekit/components-react";
import { toast } from "sonner";
import { Hand } from "lucide-react";

const enc = (obj) => new TextEncoder().encode(JSON.stringify(obj));
const ordinal = (n) => {
  const s = ["th", "st", "nd", "rd"], v = n % 100;
  return n + (s[(v - 20) % 10] || s[v] || s[0]);
};

// Attendee-facing raise-hand control. Broadcasts raise/lower over the data channel
// (re-broadcasts every 4s so late-joining hosts sync), shows the attendee's queue
// position, and auto-lowers when the host triggers "lower all hands".
export default function RaiseHandButton() {
  const { send } = useDataChannel("handraise");
  const { localParticipant } = useLocalParticipant();
  const [raised, setRaised] = useState(false);
  const [queuePos, setQueuePos] = useState(0);

  const toggle = () => {
    const next = !raised;
    setRaised(next);
    try { send(enc({ raised: next }), { reliable: true }); } catch {}
    if (next) toast.success("✋ Hand raised — the host has been notified");
    else { toast("Hand lowered"); setQueuePos(0); }
  };

  useEffect(() => {
    if (!raised) return;
    const id = setInterval(() => {
      try { send(enc({ raised: true }), { reliable: true }); } catch {}
    }, 4000);
    return () => clearInterval(id);
  }, [raised, send]);

  // Receive the host's ordered queue → compute my position.
  useDataChannel("handqueue", (msg) => {
    try {
      const data = JSON.parse(new TextDecoder().decode(msg.payload));
      const idx = (data.queue || []).indexOf(localParticipant?.identity);
      setQueuePos(idx >= 0 ? idx + 1 : 0);
    } catch {}
  });

  // Host "lower all hands" command.
  useDataChannel("handcontrol", (msg) => {
    try {
      const data = JSON.parse(new TextDecoder().decode(msg.payload));
      if (data.lowerAll && raised) {
        setRaised(false);
        setQueuePos(0);
        toast("The host lowered all hands");
      }
    } catch {}
  });

  return (
    <>
      {raised && (
        <div
          data-testid="hand-raised-confirmation"
          className="absolute bottom-36 left-1/2 -translate-x-1/2 z-50 flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/90 text-white text-xs shadow"
        >
          <Hand className="w-3.5 h-3.5" />
          {queuePos > 0 ? `Hand raised · ${ordinal(queuePos)} in line` : "Hand raised · host notified"}
        </div>
      )}
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
    </>
  );
}
