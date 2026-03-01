import { useState, useRef, useCallback } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;

export const CAPTION_LANGUAGES = {
  en: 'English', es: 'Spanish', fr: 'French', de: 'German',
  it: 'Italian', pt: 'Portuguese', ja: 'Japanese', ko: 'Korean',
  zh: 'Chinese', nl: 'Dutch', ar: 'Arabic', hi: 'Hindi',
  ru: 'Russian', tr: 'Turkish', pl: 'Polish', sv: 'Swedish'
};

/**
 * Live transcription hook with multi-language support.
 * Captures audio, sends to Whisper, optionally translates captions.
 */
export function useLiveTranscription() {
  const [active, setActive] = useState(false);
  const [captions, setCaptions] = useState([]);
  const [fullTranscript, setFullTranscript] = useState('');
  const [sourceLanguage, setSourceLanguage] = useState('en');
  const [displayLanguage, setDisplayLanguage] = useState('en');
  const recorderRef = useRef(null);
  const intervalRef = useRef(null);
  const chunksRef = useRef([]);
  const srcLangRef = useRef('en');
  const dspLangRef = useRef('en');

  // Keep refs in sync with state for use inside callbacks
  const updateSourceLang = useCallback((lang) => {
    setSourceLanguage(lang);
    srcLangRef.current = lang;
  }, []);

  const updateDisplayLang = useCallback((lang) => {
    setDisplayLanguage(lang);
    dspLangRef.current = lang;
  }, []);

  const translateText = useCallback(async (text, src, tgt) => {
    if (src === tgt || !text.trim()) return text;
    const token = localStorage.getItem('token') || localStorage.getItem('karau_token');
    try {
      const res = await fetch(`${API}/api/karau/webinar/translate-caption`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ text, source_language: src, target_language: tgt })
      });
      if (res.ok) {
        const data = await res.json();
        return data.translated || text;
      }
    } catch (e) { console.warn('Translation error:', e); }
    return text;
  }, []);

  const activeSpeakerRef = useRef(null);

  const setActiveSpeaker = useCallback((speaker) => {
    activeSpeakerRef.current = speaker;
  }, []);

  const transcribeChunk = useCallback(async (blob) => {
    if (blob.size < 1000) return;
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
        body: JSON.stringify({ audio: base64, format: 'webm', language: srcLangRef.current })
      });
      if (res.ok) {
        const data = await res.json();
        if (data.text?.trim()) {
          const originalText = data.text.trim();
          setFullTranscript(prev => prev + ' ' + originalText);

          // Translate if display language differs
          let displayText = originalText;
          if (srcLangRef.current !== dspLangRef.current) {
            displayText = await translateText(originalText, srcLangRef.current, dspLangRef.current);
          }

          const caption = {
            text: displayText,
            original: originalText,
            ts: Date.now(),
            lang: dspLangRef.current
          };
          setCaptions(prev => [...prev.slice(-20), caption]);
        }
      }
    } catch (e) { console.warn('Transcription chunk error:', e); }
  }, [translateText]);

  const start = useCallback((stream) => {
    if (!stream || active) return;
    try {
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

      intervalRef.current = setInterval(() => {
        if (chunksRef.current.length > 0) {
          const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
          chunksRef.current = [];
          transcribeChunk(blob);
        }
      }, 8000);

      recorder.start(1000);
      setActive(true);
    } catch (e) { console.error('Live transcription start error:', e); }
  }, [active, transcribeChunk]);

  const stop = useCallback(() => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    if (recorderRef.current?.state !== 'inactive') {
      try { recorderRef.current?.stop(); } catch {}
    }
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

  return {
    active, captions, fullTranscript,
    sourceLanguage, displayLanguage,
    setSourceLanguage: updateSourceLang,
    setDisplayLanguage: updateDisplayLang,
    start, stop, clear
  };
}

export default useLiveTranscription;
