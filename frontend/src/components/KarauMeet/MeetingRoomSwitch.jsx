import { useState, useEffect } from "react";
import { Loader2 } from "lucide-react";
import MeetingRoom from "@/components/KarauMeet/MeetingRoom";
import LiveKitMeetingRoom from "@/components/KarauMeet/LiveKitMeetingRoom";

const API = process.env.REACT_APP_BACKEND_URL;

// Dual-stack switch: routes a live meeting to the LiveKit SFU when the meeting's
// media_backend is "livekit", otherwise falls back to the legacy P2P MeetingRoom.
export default function MeetingRoomSwitch({ user, meetingId }) {
  const [backend, setBackend] = useState(null); // null = loading

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch(`${API}/api/karau-meet/meetings/${meetingId}/info`);
        const d = res.ok ? await res.json() : {};
        if (!cancelled) setBackend(d.media_backend === "livekit" ? "livekit" : "p2p");
      } catch {
        if (!cancelled) setBackend("p2p");
      }
    })();
    return () => { cancelled = true; };
  }, [meetingId]);

  if (backend === null) {
    return (
      <div className="min-h-screen bg-[#0c0d1a] flex items-center justify-center" data-testid="meeting-switch-loading">
        <Loader2 className="w-8 h-8 animate-spin text-purple-400" />
      </div>
    );
  }
  if (backend === "livekit") {
    return <LiveKitMeetingRoom user={user} meetingId={meetingId} />;
  }
  return <MeetingRoom user={user} meetingIdProp={meetingId} />;
}
