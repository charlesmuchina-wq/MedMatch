import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Loader2 } from "lucide-react";
import WebinarLiveRoom from "@/pages/KarauMeet/WebinarLiveRoom";
import LiveKitMeetingRoom from "@/components/KarauMeet/LiveKitMeetingRoom";

const API = process.env.REACT_APP_BACKEND_URL;

// Dual-stack switch for the webinar /live path: LiveKit SFU (attendees subscribe-only)
// when media_backend is "livekit", otherwise the legacy P2P WebinarLiveRoom.
export default function WebinarLiveSwitch() {
  const { webinarId } = useParams();
  const [backend, setBackend] = useState(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch(`${API}/api/karau-meet/meetings/${webinarId}/info`);
        const d = res.ok ? await res.json() : {};
        if (!cancelled) setBackend(d.media_backend === "livekit" ? "livekit" : "p2p");
      } catch {
        if (!cancelled) setBackend("p2p");
      }
    })();
    return () => { cancelled = true; };
  }, [webinarId]);

  if (backend === null) {
    return (
      <div className="min-h-screen bg-[#0c0d1a] flex items-center justify-center" data-testid="webinar-switch-loading">
        <Loader2 className="w-8 h-8 animate-spin text-purple-400" />
      </div>
    );
  }
  if (backend === "livekit") {
    return <LiveKitMeetingRoom meetingId={webinarId} webinar={true} />;
  }
  return <WebinarLiveRoom />;
}
