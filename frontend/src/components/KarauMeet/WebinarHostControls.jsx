import { useState, useRef, useEffect, useCallback } from "react";
import { useParticipants, useDataChannel } from "@livekit/components-react";
import { toast } from "sonner";
import { Users, UserPlus, UserMinus, Loader2, ChevronDown, Hand, HandMetal } from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL;
const enc = (obj) => new TextEncoder().encode(JSON.stringify(obj));

function playChime() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const o = ctx.createOscillator();
    const g = ctx.createGain();
    o.connect(g); g.connect(ctx.destination);
    o.type = "sine"; o.frequency.value = 880;
    g.gain.setValueAtTime(0.0001, ctx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.18, ctx.currentTime + 0.01);
    g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.28);
    o.start();
    o.stop(ctx.currentTime + 0.3);
    o.onended = () => ctx.close();
  } catch { /* audio not available */ }
}

// Host-only panel: promote/demote attendees (live can_publish via LiveKit server API),
// surface raised hands (toast + chime, deduped), broadcast the ordered hand-raise queue,
// and lower all hands in one click.
export default function WebinarHostControls({ meetingId }) {
  const participants = useParticipants();
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(null);
  const [hands, setHands] = useState({});       // identity -> raised(bool)
  const prevHands = useRef({});                 // dedup notifications
  const handOrder = useRef({});                 // identity -> first-raise timestamp
  const { send: sendQueue } = useDataChannel("handqueue");
  const { send: sendControl } = useDataChannel("handcontrol");

  const broadcastQueue = useCallback(() => {
    const ordered = Object.entries(handOrder.current)
      .sort((a, b) => a[1] - b[1])
      .map(([id]) => id);
    try { sendQueue(enc({ queue: ordered }), { reliable: true }); } catch {}
  }, [sendQueue]);

  useDataChannel("handraise", (msg) => {
    try {
      const data = JSON.parse(new TextDecoder().decode(msg.payload));
      const id = msg.from?.identity;
      if (!id) return;
      const name = msg.from?.name || "A participant";
      const raised = !!data.raised;
      if (raised && !prevHands.current[id]) {
        toast(`✋ ${name} raised their hand`, { description: "Open Manage to bring them on stage." });
        playChime();
        handOrder.current[id] = Date.now();
      }
      if (!raised && prevHands.current[id]) {
        delete handOrder.current[id];
      }
      prevHands.current[id] = raised;
      setHands((prev) => ({ ...prev, [id]: raised }));
      broadcastQueue();
    } catch { /* ignore malformed */ }
  });

  // Periodically rebroadcast the queue so late-joining attendees sync their position.
  useEffect(() => {
    const t = setInterval(broadcastQueue, 3000);
    return () => clearInterval(t);
  }, [broadcastQueue]);

  const setRole = async (identity, can_publish) => {
    setBusy(identity);
    try {
      const headers = { "Content-Type": "application/json" };
      const t = localStorage.getItem("access_token");
      if (t) headers["Authorization"] = `Bearer ${t}`;
      const res = await fetch(
        `${API}/api/karau-meet/meetings/${meetingId}/participants/${encodeURIComponent(identity)}/role`,
        { method: "POST", headers, credentials: "include", body: JSON.stringify({ can_publish }) }
      );
      if (!res.ok) throw new Error();
      if (can_publish) {
        prevHands.current[identity] = false;
        delete handOrder.current[identity];
        setHands((prev) => ({ ...prev, [identity]: false }));
        broadcastQueue();
      }
      toast.success(can_publish ? "Promoted to panelist" : "Moved to audience");
    } catch {
      toast.error("Action failed");
    } finally {
      setBusy(null);
    }
  };

  const lowerAllHands = () => {
    try { sendControl(enc({ lowerAll: true }), { reliable: true }); } catch {}
    handOrder.current = {};
    prevHands.current = {};
    setHands({});
    broadcastQueue();
    toast("All hands lowered");
  };

  const remote = participants
    .filter((p) => !p.isLocal)
    .sort((a, b) => (hands[b.identity] ? 1 : 0) - (hands[a.identity] ? 1 : 0));
  const raisedCount = remote.filter((p) => hands[p.identity]).length;

  return (
    <div className="absolute top-3 right-3 z-50">
      <button
        onClick={() => setOpen(!open)}
        data-testid="host-controls-toggle"
        className="relative flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-purple-600 hover:bg-purple-700 text-white text-xs font-medium shadow-lg"
      >
        <Users className="w-3.5 h-3.5" /> Manage ({remote.length})
        {raisedCount > 0 && (
          <span data-testid="raised-hands-badge" className="flex items-center gap-0.5 ml-1 px-1.5 py-0.5 rounded-full bg-amber-400 text-amber-950 text-[10px] font-bold">
            <Hand className="w-2.5 h-2.5" />{raisedCount}
          </span>
        )}
        <ChevronDown className={`w-3.5 h-3.5 transition-transform ${open ? "rotate-180" : ""}`} />
      </button>
      {open && (
        <div
          data-testid="host-controls-panel"
          className="mt-2 w-72 max-h-80 overflow-y-auto rounded-xl bg-slate-900/95 border border-white/10 backdrop-blur p-2 shadow-2xl"
        >
          {raisedCount > 0 && (
            <button
              onClick={lowerAllHands}
              data-testid="lower-all-hands-btn"
              className="w-full mb-2 flex items-center justify-center gap-1.5 text-[11px] px-2 py-1.5 rounded-md bg-amber-500/20 text-amber-300 hover:bg-amber-500/30"
            >
              <HandMetal className="w-3.5 h-3.5" /> Lower all hands ({raisedCount})
            </button>
          )}
          {remote.length === 0 ? (
            <p className="text-xs text-slate-400 text-center py-6">No other participants yet.</p>
          ) : (
            remote.map((p) => {
              const canPublish = !!p.permissions?.canPublish;
              return (
                <div key={p.identity} className="flex items-center gap-2 px-2 py-2 rounded-lg hover:bg-white/5" data-testid={`host-participant-${p.identity}`}>
                  {hands[p.identity] && (
                    <Hand className="w-4 h-4 text-amber-400 animate-bounce flex-shrink-0" data-testid={`hand-${p.identity}`} />
                  )}
                  <div className="flex-1 min-w-0">
                    <div className="text-sm text-slate-100 truncate">{p.name || p.identity}</div>
                    <div className={`text-[10px] ${canPublish ? "text-emerald-400" : hands[p.identity] ? "text-amber-400" : "text-slate-500"}`}>
                      {canPublish ? "Panelist" : hands[p.identity] ? "Hand raised" : "Audience"}
                    </div>
                  </div>
                  {canPublish ? (
                    <button
                      onClick={() => setRole(p.identity, false)}
                      disabled={busy === p.identity}
                      data-testid={`demote-${p.identity}`}
                      className="flex items-center gap-1 text-[11px] px-2 py-1 rounded-md bg-white/5 text-slate-300 hover:bg-white/10"
                    >
                      {busy === p.identity ? <Loader2 className="w-3 h-3 animate-spin" /> : <UserMinus className="w-3 h-3" />}
                      Audience
                    </button>
                  ) : (
                    <button
                      onClick={() => setRole(p.identity, true)}
                      disabled={busy === p.identity}
                      data-testid={`promote-${p.identity}`}
                      className="flex items-center gap-1 text-[11px] px-2 py-1 rounded-md bg-purple-600 text-white hover:bg-purple-700"
                    >
                      {busy === p.identity ? <Loader2 className="w-3 h-3 animate-spin" /> : <UserPlus className="w-3 h-3" />}
                      Promote
                    </button>
                  )}
                </div>
              );
            })
          )}
        </div>
      )}
    </div>
  );
}
