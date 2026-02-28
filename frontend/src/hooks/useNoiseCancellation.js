import { useState, useRef, useCallback, useEffect } from 'react';

/**
 * Enhanced Noise cancellation hook with dual-engine approach:
 * 1. RNNoise WASM - ML-based noise suppression (preferred)
 * 2. Web Audio API - noise gate + bandpass filter (fallback)
 */
export function useNoiseCancellation() {
  const [enabled, setEnabled] = useState(false);
  const [level, setLevel] = useState(50);
  const [engine, setEngine] = useState('auto'); // 'auto', 'rnnoise', 'webaudio'
  const [activeEngine, setActiveEngine] = useState(null);
  const audioCtxRef = useRef(null);
  const sourceRef = useRef(null);
  const destRef = useRef(null);
  const streamRef = useRef(null);
  const processedStreamRef = useRef(null);
  const rnnoiseRef = useRef(null);
  const workletNodeRef = useRef(null);
  const gainRef = useRef(null);
  const analyserRef = useRef(null);
  const rafRef = useRef(null);

  const cleanup = useCallback(() => {
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
    if (workletNodeRef.current) { try { workletNodeRef.current.disconnect(); } catch {} }
    if (sourceRef.current) { try { sourceRef.current.disconnect(); } catch {} }
    if (audioCtxRef.current?.state !== 'closed') {
      try { audioCtxRef.current?.close(); } catch {}
    }
    audioCtxRef.current = null;
    processedStreamRef.current = null;
    workletNodeRef.current = null;
    rnnoiseRef.current = null;
    setActiveEngine(null);
  }, []);

  useEffect(() => cleanup, [cleanup]);

  /**
   * Try to initialize RNNoise WASM engine
   */
  const initRnnoise = useCallback(async (ctx, source, dest) => {
    try {
      const { Rnnoise } = await import('@shiguredo/rnnoise-wasm');
      const rnnoise = await Rnnoise.load();
      rnnoiseRef.current = rnnoise;

      // Create ScriptProcessor for RNNoise processing
      // RNNoise needs 480 samples per frame at 48kHz
      const bufferSize = 4096;
      const processor = ctx.createScriptProcessor(bufferSize, 1, 1);
      const denoiseState = rnnoise.createDenoiseState();
      const frameSize = 480;

      processor.onaudioprocess = (e) => {
        const input = e.inputBuffer.getChannelData(0);
        const output = e.outputBuffer.getChannelData(0);

        // Process in 480-sample frames
        for (let offset = 0; offset < input.length; offset += frameSize) {
          const end = Math.min(offset + frameSize, input.length);
          const frame = new Float32Array(frameSize);

          // Copy and scale input (RNNoise expects [-32768, 32767] range)
          for (let i = 0; i < end - offset; i++) {
            frame[i] = input[offset + i] * 32768;
          }

          // Apply RNNoise
          denoiseState.processFrame(frame);

          // Scale back and copy to output
          for (let i = 0; i < end - offset; i++) {
            output[offset + i] = frame[i] / 32768;
          }
        }
      };

      source.connect(processor);
      processor.connect(dest);
      workletNodeRef.current = processor;
      setActiveEngine('rnnoise');
      return true;
    } catch (err) {
      console.warn('RNNoise init failed, falling back to Web Audio:', err);
      return false;
    }
  }, []);

  /**
   * Fallback: Web Audio API noise gate + bandpass filter
   */
  const initWebAudio = useCallback((ctx, source, dest) => {
    // High-pass filter to remove rumble (<80Hz)
    const hpFilter = ctx.createBiquadFilter();
    hpFilter.type = 'highpass';
    hpFilter.frequency.value = 80;
    hpFilter.Q.value = 0.7;

    // Bandpass focused on voice (300Hz - 3400Hz)
    const bpFilter = ctx.createBiquadFilter();
    bpFilter.type = 'bandpass';
    bpFilter.frequency.value = 1500;
    bpFilter.Q.value = 0.5;

    // Compressor
    const compressor = ctx.createDynamicsCompressor();
    compressor.threshold.value = -50;
    compressor.knee.value = 40;
    compressor.ratio.value = 12;
    compressor.attack.value = 0;
    compressor.release.value = 0.25;

    // Noise gate via gain
    const gain = ctx.createGain();
    gain.gain.value = 1;
    gainRef.current = gain;

    // Analyser for level detection
    const analyser = ctx.createAnalyser();
    analyser.fftSize = 2048;
    analyser.smoothingTimeConstant = 0.8;
    analyserRef.current = analyser;

    // Chain: source -> HP -> BP -> compressor -> gain -> analyser -> dest
    source.connect(hpFilter);
    hpFilter.connect(bpFilter);
    bpFilter.connect(compressor);
    compressor.connect(gain);
    gain.connect(analyser);
    analyser.connect(dest);

    // Noise gate loop
    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    const gateLoop = () => {
      if (!analyserRef.current) return;
      analyser.getByteFrequencyData(dataArray);
      const voiceStart = Math.floor(300 / (ctx.sampleRate / analyser.fftSize));
      const voiceEnd = Math.floor(3400 / (ctx.sampleRate / analyser.fftSize));
      let sum = 0;
      for (let i = voiceStart; i < voiceEnd && i < dataArray.length; i++) sum += dataArray[i];
      const avg = sum / Math.max(voiceEnd - voiceStart, 1);
      const threshold = 10 + (level / 100) * 70;

      if (avg < threshold) {
        gain.gain.setTargetAtTime(0.02, ctx.currentTime, 0.015);
      } else {
        gain.gain.setTargetAtTime(1, ctx.currentTime, 0.005);
      }
      rafRef.current = requestAnimationFrame(gateLoop);
    };
    gateLoop();

    setActiveEngine('webaudio');
  }, [level]);

  /**
   * Apply noise cancellation to a MediaStream
   */
  const applyToStream = useCallback(async (stream) => {
    if (!stream) return stream;
    cleanup();
    streamRef.current = stream;

    const ctx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 48000 });
    audioCtxRef.current = ctx;

    const source = ctx.createMediaStreamSource(stream);
    sourceRef.current = source;
    const dest = ctx.createMediaStreamDestination();
    destRef.current = dest;

    // Try RNNoise first if engine allows
    let useRnnoise = false;
    if (engine === 'auto' || engine === 'rnnoise') {
      useRnnoise = await initRnnoise(ctx, source, dest);
    }

    // Fallback to Web Audio
    if (!useRnnoise) {
      initWebAudio(ctx, source, dest);
    }

    // Combine processed audio with original video tracks
    const processedStream = new MediaStream();
    dest.stream.getAudioTracks().forEach(t => processedStream.addTrack(t));
    stream.getVideoTracks().forEach(t => processedStream.addTrack(t));

    processedStreamRef.current = processedStream;
    setEnabled(true);
    return processedStream;
  }, [engine, level, cleanup, initRnnoise, initWebAudio]);

  const removeFromStream = useCallback(() => {
    cleanup();
    setEnabled(false);
    return streamRef.current;
  }, [cleanup]);

  const updateLevel = useCallback((newLevel) => {
    setLevel(newLevel);
  }, []);

  const switchEngine = useCallback((newEngine) => {
    setEngine(newEngine);
    // If currently active, re-apply with new engine
    if (enabled && streamRef.current) {
      applyToStream(streamRef.current);
    }
  }, [enabled, applyToStream]);

  return {
    enabled,
    level,
    engine,
    activeEngine,
    applyToStream,
    removeFromStream,
    updateLevel,
    switchEngine,
    processedStream: processedStreamRef.current,
    isSupported: typeof window !== 'undefined' && (window.AudioContext || window.webkitAudioContext)
  };
}

export default useNoiseCancellation;
