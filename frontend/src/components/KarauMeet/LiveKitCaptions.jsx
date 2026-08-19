import { useState, useEffect, useRef, useCallback } from "react";
import { useDataChannel, useLocalParticipant } from "@livekit/components-react";
import { Subtitles } from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL;
const enc = (obj) => new TextEncoder().encode(JSON.stringify(obj));

const blobToBase64 = (blob) =>
  new Promise((resolve) => {
    const r = new FileReader();
    r.onloadend = () => resolve(String(r.result).split(",")[1]);
    r.readAsDataURL(blob);
  });

// LiveKit live captions: speakers transcribe their own mic via Whisper and broadcast
// text over the "captions" data channel; every viewer renders it translated (or
// original) in their chosen language via the translation engine.
export default function LiveKitCaptions({ canSpeak = true, meetingId = "" }) {
  const [enabled, setEnabled] = useState(false);
  const [lang, setLang] = useState("original");
  const [languages, setLanguages] = useState([]);
  const [lines, setLines] = useState([]);
  const { localParticipant } = useLocalParticipant();
  const enabledRef = useRef(false);
  const langRef = useRef("original");
  const stopRef = useRef(null);

  useEffect(() => { enabledRef.current = enabled; }, [enabled]);
  useEffect(() => { langRef.current = lang; }, [lang]);

  useEffect(() => {
    fetch(`${API}/api/translate/languages`)
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => setLanguages(d?.languages || []))
      .catch(() => {});
  }, []);

  const pushLine = (speaker, text) =>
    setLines((prev) => [...prev.slice(-1), { id: Date.now() + Math.random(), speaker, text }]);

  const showCaption = useCallback(async (speaker, text) => {
    const target = langRef.current;
    if (target !== "original") {
      try {
        const r = await fetch(`${API}/api/lumi/ai/translate`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text, target_language: target }),
        });
        if (r.ok) {
          const d = await r.json();
          text = d.translated_text || text;
        }
      } catch {}
    }
    if (enabledRef.current) pushLine(speaker, text);
  }, []);

  const { send } = useDataChannel("captions", (msg) => {
    if (!enabledRef.current) return;
    try {
      const d = JSON.parse(new TextDecoder().decode(msg.payload));
      if (d.text) showCaption(d.speaker || "Speaker", d.text);
    } catch {}
  });

  const transcribe = useCallback(async (blob) => {
    const b64 = await blobToBase64(blob);
    const headers = { "Content-Type": "application/json" };
    const t = localStorage.getItem("access_token");
    if (t) headers["Authorization"] = `Bearer ${t}`;
    try {
      const r = await fetch(`${API}/api/realtime-stt/transcribe-base64`, {
        method: "POST",
        headers,
        credentials: "include",
        body: JSON.stringify({ audio: b64, format: "webm", language: "auto" }),
      });
      if (!r.ok) return;
      const d = await r.json();
      const text = (d.text || "").trim();
      if (!text) return;
      const speaker = localParticipant?.name || localParticipant?.identity || "Me";
      try { send(enc({ speaker, text }), { reliable: true }); } catch {}
      showCaption(speaker, text);
      if (meetingId) {
        fetch(`${API}/api/karau-meet/meetings/${meetingId}/captions`, {
          method: "POST",
          headers,
          credentials: "include",
          body: JSON.stringify({ speaker, text }),
        }).catch(() => {});
      }
    } catch {}
  }, [localParticipant, send, showCaption, meetingId]);

  // Mic recorder cycle: 4s standalone webm blobs → Whisper.
  useEffect(() => {
    if (!enabled || !canSpeak) return;
    let stopped = false;
    let rec = null;
    let stream = null;
    (async () => {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const cycle = () => {
          if (stopped) return;
          const chunks = [];
          rec = new MediaRecorder(stream, { mimeType: "audio/webm" });
          rec.ondataavailable = (e) => { if (e.data.size) chunks.push(e.data); };
          rec.onstop = () => {
            const blob = new Blob(chunks, { type: "audio/webm" });
            if (blob.size > 4000 && enabledRef.current) transcribe(blob);
            cycle();
          };
          rec.start();
          setTimeout(() => { if (rec && rec.state === "recording") rec.stop(); }, 4000);
        };
        cycle();
      } catch {}
    })();
    stopRef.current = () => {
      stopped = true;
      try { if (rec && rec.state === "recording") { rec.onstop = null; rec.stop(); } } catch {}
      try { stream?.getTracks().forEach((tr) => tr.stop()); } catch {}
    };
    return () => stopRef.current?.();
  }, [enabled, canSpeak, transcribe]);

  return (
    <>
      <div className="absolute top-2 right-2 z-50 flex items-center gap-2" data-testid="captions-controls">
        {enabled && (
          <select
            value={lang}
            onChange={(e) => setLang(e.target.value)}
            className="bg-black/60 backdrop-blur text-white text-xs rounded-md px-2 py-1.5 border border-white/20 outline-none max-w-[160px]"
            data-testid="captions-language-select"
            aria-label="Caption language"
          >
            <option value="original">Original (no translation)</option>
            {languages.map((l) => (
              <option key={l.code} value={l.name}>{l.flag ? `${l.flag} ` : ""}{l.name}</option>
            ))}
          </select>
        )}
        <button
          onClick={() => { setEnabled((v) => { if (v) setLines([]); return !v; }); }}
          data-testid="captions-toggle-btn"
          aria-pressed={enabled}
          title={enabled ? "Turn off live captions" : "Turn on live captions"}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium shadow transition-colors ${
            enabled ? "bg-teal-500 text-white" : "bg-white/10 text-white hover:bg-white/20 backdrop-blur"
          }`}
        >
          <Subtitles className="w-4 h-4" aria-hidden="true" />
          {enabled ? "CC on" : "CC"}
        </button>
      </div>
      {enabled && lines.length > 0 && (
        <div
          className="absolute bottom-32 left-1/2 -translate-x-1/2 z-40 w-full max-w-2xl px-4 pointer-events-none"
          data-testid="captions-overlay"
          aria-live="polite"
        >
          {lines.map((l) => (
            <div key={l.id} className="mt-1 mx-auto w-fit max-w-full bg-black/70 backdrop-blur rounded-lg px-3 py-1.5 text-center" data-testid="caption-line">
              <span className="text-teal-300 text-xs font-semibold mr-2">{l.speaker}</span>
              <span className="text-white text-sm">{l.text}</span>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
