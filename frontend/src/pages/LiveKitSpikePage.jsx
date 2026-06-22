import { useState } from "react";
import { toast } from "sonner";
import { LiveKitRoom, VideoConference, RoomAudioRenderer } from "@livekit/components-react";
import "@livekit/components-styles";
import { Video, Loader2, LogIn, Copy } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { apiClient } from "@/utils/apiClient";

export default function LiveKitSpikePage() {
  const [room, setRoom] = useState(
    new URLSearchParams(window.location.search).get("room") || "spike-room"
  );
  const [token, setToken] = useState("");
  const [serverUrl, setServerUrl] = useState("");
  const [joining, setJoining] = useState(false);

  const join = async () => {
    if (!room.trim()) return toast.error("Enter a room name");
    setJoining(true);
    try {
      const r = await apiClient.post("/api/livekit/token", { room_name: room.trim() });
      const d = r.data || {};
      if (!d.token) throw new Error("No token");
      setServerUrl(d.url || process.env.REACT_APP_LIVEKIT_URL);
      setToken(d.token);
    } catch (e) {
      toast.error("Could not join — is LiveKit configured?");
    } finally {
      setJoining(false);
    }
  };

  const copyInvite = () => {
    navigator.clipboard?.writeText(`${window.location.origin}/livekit-spike?room=${encodeURIComponent(room)}`);
    toast.success("Invite link copied — open in another browser/device to test the SFU");
  };

  if (token) {
    return (
      <div className="h-[calc(100vh-64px)] w-full bg-slate-950" data-testid="livekit-room" data-lk-theme="default">
        <LiveKitRoom
          video={true}
          audio={true}
          token={token}
          serverUrl={serverUrl}
          connect={true}
          onDisconnected={() => setToken("")}
          style={{ height: "100%" }}
        >
          <VideoConference />
          <RoomAudioRenderer />
        </LiveKitRoom>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4" data-testid="livekit-spike-page">
      <Card className="w-full max-w-md border-slate-200 dark:border-white/10">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="rounded-2xl bg-gradient-to-br from-turquoise to-cyan-600 p-2.5">
              <Video className="w-6 h-6 text-white" />
            </div>
            <div>
              <CardTitle className="text-xl">LiveKit SFU Spike</CardTitle>
              <CardDescription>Phase-0 proof-of-concept — scalable video via SFU</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            data-testid="livekit-room-input"
            placeholder="Room name"
            value={room}
            onChange={(e) => setRoom(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !joining && join()}
          />
          <Button onClick={join} disabled={joining} className="w-full bg-turquoise hover:bg-turquoise/90 text-white" data-testid="livekit-join-btn">
            {joining ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <LogIn className="w-4 h-4 mr-2" />}
            Join room
          </Button>
          <Button onClick={copyInvite} variant="outline" className="w-full" data-testid="livekit-copy-btn">
            <Copy className="w-4 h-4 mr-2" /> Copy invite link
          </Button>
          <p className="text-xs text-slate-500 text-center">
            Open the invite in a second browser/device to verify two clients connect through the SFU (not P2P).
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
