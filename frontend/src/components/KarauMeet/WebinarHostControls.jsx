import { useState } from "react";
import { useParticipants } from "@livekit/components-react";
import { toast } from "sonner";
import { Users, UserPlus, UserMinus, Loader2, ChevronDown } from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL;

// Host-only panel (rendered inside <LiveKitRoom>) to promote attendees to panelist
// or move panelists back to audience — flips can_publish live via the LiveKit server API.
export default function WebinarHostControls({ meetingId }) {
  const participants = useParticipants();
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(null);

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
      toast.success(can_publish ? "Promoted to panelist" : "Moved to audience");
    } catch {
      toast.error("Action failed");
    } finally {
      setBusy(null);
    }
  };

  const remote = participants.filter((p) => !p.isLocal);

  return (
    <div className="absolute top-3 right-3 z-50">
      <button
        onClick={() => setOpen(!open)}
        data-testid="host-controls-toggle"
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-purple-600 hover:bg-purple-700 text-white text-xs font-medium shadow-lg"
      >
        <Users className="w-3.5 h-3.5" /> Manage ({remote.length})
        <ChevronDown className={`w-3.5 h-3.5 transition-transform ${open ? "rotate-180" : ""}`} />
      </button>
      {open && (
        <div
          data-testid="host-controls-panel"
          className="mt-2 w-72 max-h-80 overflow-y-auto rounded-xl bg-slate-900/95 border border-white/10 backdrop-blur p-2 shadow-2xl"
        >
          {remote.length === 0 ? (
            <p className="text-xs text-slate-400 text-center py-6">No other participants yet.</p>
          ) : (
            remote.map((p) => {
              const canPublish = !!p.permissions?.canPublish;
              return (
                <div key={p.identity} className="flex items-center gap-2 px-2 py-2 rounded-lg hover:bg-white/5" data-testid={`host-participant-${p.identity}`}>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm text-slate-100 truncate">{p.name || p.identity}</div>
                    <div className={`text-[10px] ${canPublish ? "text-emerald-400" : "text-slate-500"}`}>
                      {canPublish ? "Panelist" : "Audience"}
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
