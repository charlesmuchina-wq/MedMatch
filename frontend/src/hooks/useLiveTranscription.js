import { useState, useRef, useCallback } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * Live transcription hook - captures audio from a MediaStream,
 * sends chunks to Whisper via REST, and returns captions.
 */
export function useLiveTranscription() {
  const [active, setActive] = useState(false);
  const [captions, setCaptions] = useState([]);
  const [fullTranscript, setFullTranscript] = useState('');
  const recorderRef = useRef(null);
  const intervalRef = useRef(null);
  const chunksRef = useRef([]);

  const transcribeChunk = useCallback(async (blob) => {
    if (blob.size < 1000) return; // skip tiny chunks
    const token = localStorage.getItem('token') || localStorage.getItem('karau_token');
    try {
      const reader = new FileReader();
      const base64 = await new Promise((resolve) => {
        reader.onloadend = () => resolve(reader.result.split(',')[1]);
        reader.readAsDataURL(blob);
      });

      const res = await fetch(`${API}/api/realtime-stt/transcribe-base64`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ audio: base64, format: 'webm', language: 'en' })
      });
      if (res.ok) {
        const data = await res.json();
        if (data.text?.trim()) {
          const caption = { text: data.text.trim(), ts: Date.now() };
          setCaptions(prev => [...prev.slice(-20), caption]);
          setFullTranscript(prev => prev + ' ' + data.text.trim());
        }
      }
    } catch (e) { console.warn('Transcription chunk error:', e); }
  }, []);

  const start = useCallback((stream) => {
    if (!stream || active) return;
    try {
      // Extract audio-only stream
      const audioTracks = stream.getAudioTracks();
      if (audioTracks.length === 0) return;
      const audioStream = new MediaStream(audioTracks);

      const recorder = new MediaRecorder(audioStream, {
        mimeType: MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
          ? 'audio/webm;codecs=opus' : 'audio/webm'
      });
      recorderRef.current = recorder;
      chunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      // Every 8 seconds, collect chunks and transcribe
      intervalRef.current = setInterval(() => {
        if (chunksRef.current.length > 0) {
          const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
          chunksRef.current = [];
          transcribeChunk(blob);
        }
      }, 8000);

      recorder.start(1000); // timeslice 1s
      setActive(true);
    } catch (e) { console.error('Live transcription start error:', e); }
  }, [active, transcribeChunk]);

  const stop = useCallback(() => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    if (recorderRef.current?.state !== 'inactive') {
      try { recorderRef.current?.stop(); } catch {}
    }
    // Transcribe remaining chunks
    if (chunksRef.current.length > 0) {
      const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
      chunksRef.current = [];
      transcribeChunk(blob);
    }
    recorderRef.current = null;
    setActive(false);
  }, [transcribeChunk]);

  const clear = useCallback(() => {
    setCaptions([]);
    setFullTranscript('');
  }, []);

  return { active, captions, fullTranscript, start, stop, clear };
}

export default useLiveTranscription;
