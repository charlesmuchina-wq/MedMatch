import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { LiveKitRoom, VideoConference, RoomAudioRenderer } from "@livekit/components-react";
import "@livekit/components-styles";
import { Loader2, AlertTriangle } from "lucide-react";
import WebinarHostControls from "@/components/KarauMeet/WebinarHostControls";
import RaiseHandButton from "@/components/KarauMeet/RaiseHandButton";
import LiveKitCaptions from "@/components/KarauMeet/LiveKitCaptions";

const API = process.env.REACT_APP_BACKEND_URL;

export default function LiveKitMeetingRoom({ user, meetingId, webinar = false }) {
  const navigate = useNavigate();
  const [token, setToken] = useState("");
  const [serverUrl, setServerUrl] = useState("");
  const [role, setRole] = useState("");
  const [isHost, setIsHost] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const headers = { "Content-Type": "application/json" };
        const t = localStorage.getItem("access_token");
        if (t) headers["Authorization"] = `Bearer ${t}`;
        const res = await fetch(`${API}/api/karau-meet/meetings/${meetingId}/livekit-token`, {
          method: "POST",
          headers,
          credentials: "include",
          body: JSON.stringify({ webinar }),
        });
        if (!res.ok) throw new Error("token");
        const d = await res.json();
        if (cancelled) return;
        setServerUrl(d.url);
        setRole(d.role || "");
        setIsHost(!!d.is_host);
        setToken(d.token);
      } catch (e) {
        if (!cancelled) setError("Could not connect to the meeting (LiveKit).");
      }
    })();
    return () => { cancelled = true; };
  }, [meetingId, webinar]);

  if (error) {
    return (
      <div className="min-h-screen bg-[#0c0d1a] flex items-center justify-center" data-testid="livekit-meeting-error">
        <div className="text-center">
          <AlertTriangle className="w-10 h-10 text-amber-400 mx-auto mb-3" />
          <p className="text-red-400 text-lg">{error}</p>
          <button onClick={() => navigate("/karau-meet")} className="mt-4 text-purple-400 hover:underline">
            Back to portal
          </button>
        </div>
      </div>
    );
  }

  if (!token) {
    return (
      <div className="min-h-screen bg-[#0c0d1a] flex items-center justify-center" data-testid="livekit-meeting-loading">
        <Loader2 className="w-8 h-8 animate-spin text-purple-400" />
      </div>
    );
  }

  return (
    <div className="h-screen w-full bg-[#0c0d1a]" data-testid="livekit-meeting-room" data-lk-theme="default">
      {webinar && role === "attendee" && (
        <div className="absolute top-2 left-1/2 -translate-x-1/2 z-50 px-3 py-1 rounded-full bg-purple-600/80 text-white text-xs" data-testid="webinar-attendee-badge">
          Webinar · view-only
        </div>
      )}
      <LiveKitRoom
        video={true}
        audio={true}
        token={token}
        serverUrl={serverUrl}
        connect={true}
        onDisconnected={() => navigate("/karau-meet")}
        style={{ height: "100%" }}
      >
        <VideoConference />
        <RoomAudioRenderer />
        <LiveKitCaptions canSpeak={!webinar || isHost} meetingId={meetingId} />
        {webinar && isHost && <WebinarHostControls meetingId={meetingId} />}
        {webinar && !isHost && role === "attendee" && <RaiseHandButton />}
      </LiveKitRoom>
    </div>
  );
}
