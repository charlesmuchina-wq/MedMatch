import { useState, useRef, useCallback, useEffect } from 'react';

/**
 * Noise cancellation hook using Web Audio API with noise gate + bandpass filter.
 * Works entirely in-browser — no external WASM or third-party service required.
 */
export function useNoiseCancellation() {
  const [enabled, setEnabled] = useState(false);
  const [level, setLevel] = useState(50); // 0-100 threshold
  const audioCtxRef = useRef(null);
  const analyserRef = useRef(null);
  const gainRef = useRef(null);
  const bpFilterRef = useRef(null);
  const hpFilterRef = useRef(null);
  const compressorRef = useRef(null);
  const sourceRef = useRef(null);
  const destRef = useRef(null);
  const rafRef = useRef(null);
  const streamRef = useRef(null);

  const processedStreamRef = useRef(null);

  const cleanup = useCallback(() => {
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
    if (sourceRef.current) { try { sourceRef.current.disconnect(); } catch {} }
    if (audioCtxRef.current?.state !== 'closed') {
      try { audioCtxRef.current?.close(); } catch {}
    }
    audioCtxRef.current = null;
    processedStreamRef.current = null;
  }, []);

  useEffect(() => { return cleanup; }, [cleanup]);

  /**
   * Apply noise cancellation to a MediaStream.
   * Returns a new processed MediaStream.
   */
  const applyToStream = useCallback(async (stream) => {
    if (!stream) return stream;
    cleanup();
    streamRef.current = stream;

    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    audioCtxRef.current = ctx;

    const source = ctx.createMediaStreamSource(stream);
    sourceRef.current = source;

    // High-pass filter to remove low-frequency rumble (<80Hz)
    const hpFilter = ctx.createBiquadFilter();
    hpFilter.type = 'highpass';
    hpFilter.frequency.value = 80;
    hpFilter.Q.value = 0.7;
    hpFilterRef.current = hpFilter;

    // Bandpass filter focused on human voice range (300Hz - 3400Hz)
    const bpFilter = ctx.createBiquadFilter();
    bpFilter.type = 'bandpass';
    bpFilter.frequency.value = 1500;
    bpFilter.Q.value = 0.5;
    bpFilterRef.current = bpFilter;

    // Compressor to reduce dynamic range and suppress spikes
    const compressor = ctx.createDynamicsCompressor();
    compressor.threshold.value = -50;
    compressor.knee.value = 40;
    compressor.ratio.value = 12;
    compressor.attack.value = 0;
    compressor.release.value = 0.25;
    compressorRef.current = compressor;

    // Gain node for noise gate
    const gain = ctx.createGain();
    gain.gain.value = 1;
    gainRef.current = gain;

    // Analyser for level detection
    const analyser = ctx.createAnalyser();
    analyser.fftSize = 2048;
    analyser.smoothingTimeConstant = 0.8;
    analyserRef.current = analyser;

    // Destination
    const dest = ctx.createMediaStreamDestination();
    destRef.current = dest;

    // Chain: source -> highpass -> bandpass -> compressor -> gain (gate) -> analyser -> dest
    source.connect(hpFilter);
    hpFilter.connect(bpFilter);
    bpFilter.connect(compressor);
    compressor.connect(gain);
    gain.connect(analyser);
    analyser.connect(dest);

    // Noise gate processing loop
    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    const gateLoop = () => {
      if (!analyserRef.current) return;
      analyser.getByteFrequencyData(dataArray);

      // Calculate average volume in voice frequency range
      const voiceStart = Math.floor(300 / (ctx.sampleRate / analyser.fftSize));
      const voiceEnd = Math.floor(3400 / (ctx.sampleRate / analyser.fftSize));
      let sum = 0;
      for (let i = voiceStart; i < voiceEnd && i < dataArray.length; i++) {
        sum += dataArray[i];
      }
      const avg = sum / Math.max(voiceEnd - voiceStart, 1);

      // Noise gate threshold (maps 0-100 level to 10-80 dB threshold)
      const threshold = 10 + (level / 100) * 70;

      if (avg < threshold) {
        // Below threshold = noise, fade out quickly
        gain.gain.setTargetAtTime(0.02, ctx.currentTime, 0.015);
      } else {
        // Above threshold = speech, keep open
        gain.gain.setTargetAtTime(1, ctx.currentTime, 0.005);
      }

      rafRef.current = requestAnimationFrame(gateLoop);
    };

    gateLoop();

    // Combine processed audio with original video tracks
    const processedStream = new MediaStream();
    dest.stream.getAudioTracks().forEach(t => processedStream.addTrack(t));
    stream.getVideoTracks().forEach(t => processedStream.addTrack(t));

    processedStreamRef.current = processedStream;
    setEnabled(true);
    return processedStream;
  }, [level, cleanup]);

  /**
   * Remove noise cancellation and return original stream
   */
  const removeFromStream = useCallback(() => {
    cleanup();
    setEnabled(false);
    return streamRef.current;
  }, [cleanup]);

  /**
   * Update noise gate level in real-time
   */
  const updateLevel = useCallback((newLevel) => {
    setLevel(newLevel);
  }, []);

  return {
    enabled,
    level,
    applyToStream,
    removeFromStream,
    updateLevel,
    processedStream: processedStreamRef.current,
    isSupported: typeof window !== 'undefined' && (window.AudioContext || window.webkitAudioContext)
  };
}

export default useNoiseCancellation;
