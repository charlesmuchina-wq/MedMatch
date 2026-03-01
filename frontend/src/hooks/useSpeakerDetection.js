import { useState, useRef, useCallback, useEffect } from 'react';

const SPEAKER_COLORS = [
  '#a78bfa', '#34d399', '#fbbf24', '#f87171', '#38bdf8',
  '#fb923c', '#e879f9', '#22d3ee', '#a3e635', '#f472b6'
];

/**
 * Detects active speakers from WebRTC audio streams using Web Audio API.
 * Maps stream audio levels to participant names.
 */
export function useSpeakerDetection() {
  const [activeSpeaker, setActiveSpeaker] = useState(null);
  const [speakers, setSpeakers] = useState({});
  const audioContextRef = useRef(null);
  const analysersRef = useRef({});
  const intervalRef = useRef(null);
  const colorMapRef = useRef({});
  const colorIndexRef = useRef(0);

  const getColor = useCallback((name) => {
    if (!colorMapRef.current[name]) {
      colorMapRef.current[name] = SPEAKER_COLORS[colorIndexRef.current % SPEAKER_COLORS.length];
      colorIndexRef.current++;
    }
    return colorMapRef.current[name];
  }, []);

  const addStream = useCallback((userId, name, stream) => {
    if (!stream || analysersRef.current[userId]) return;

    if (!audioContextRef.current) {
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
    }
    const ctx = audioContextRef.current;

    try {
      const source = ctx.createMediaStreamSource(stream);
      const analyser = ctx.createAnalyser();
      analyser.fftSize = 256;
      analyser.smoothingTimeConstant = 0.5;
      source.connect(analyser);

      analysersRef.current[userId] = { analyser, name, source };
      setSpeakers(prev => ({
        ...prev,
        [userId]: { name, color: getColor(name), level: 0, speaking: false }
      }));
    } catch (e) { console.warn('Speaker detection addStream error:', e); }
  }, [getColor]);

  const addLocalStream = useCallback((name, stream) => {
    addStream('__local__', name || 'You', stream);
  }, [addStream]);

  const removeStream = useCallback((userId) => {
    if (analysersRef.current[userId]) {
      try { analysersRef.current[userId].source.disconnect(); } catch {}
      delete analysersRef.current[userId];
    }
    setSpeakers(prev => {
      const next = { ...prev };
      delete next[userId];
      return next;
    });
  }, []);

  // Poll audio levels
  useEffect(() => {
    intervalRef.current = setInterval(() => {
      const entries = Object.entries(analysersRef.current);
      if (entries.length === 0) return;

      let maxLevel = 0;
      let maxSpeaker = null;
      const updates = {};

      for (const [uid, { analyser, name }] of entries) {
        const data = new Uint8Array(analyser.frequencyBinCount);
        analyser.getByteFrequencyData(data);
        const avg = data.reduce((a, b) => a + b, 0) / data.length;
        const speaking = avg > 15; // threshold
        updates[uid] = { name, color: getColor(name), level: avg, speaking };
        if (avg > maxLevel) { maxLevel = avg; maxSpeaker = { userId: uid, name, color: getColor(name) }; }
      }

      setSpeakers(prev => ({ ...prev, ...updates }));
      setActiveSpeaker(maxLevel > 15 ? maxSpeaker : null);
    }, 200);

    return () => { if (intervalRef.current) clearInterval(intervalRef.current); };
  }, [getColor]);

  const cleanup = useCallback(() => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    Object.values(analysersRef.current).forEach(({ source }) => {
      try { source.disconnect(); } catch {}
    });
    analysersRef.current = {};
    if (audioContextRef.current?.state !== 'closed') {
      try { audioContextRef.current?.close(); } catch {}
    }
    audioContextRef.current = null;
  }, []);

  return { activeSpeaker, speakers, addStream, addLocalStream, removeStream, cleanup };
}

export default useSpeakerDetection;
