import { useRef, useCallback, useState } from 'react';

/**
 * Enhanced AI Noise Cancellation Hook
 * Dual-engine approach:
 * - Primary: RNNoise WASM (ML-based, superior quality)
 * - Fallback: Multi-stage Web Audio API pipeline
 */
export const useNoiseCancellation = () => {
  const audioContextRef = useRef(null);
  const sourceRef = useRef(null);
  const gainRef = useRef(null);
  const analyserRef = useRef(null);
  const noiseFloorRef = useRef(-60);
  const animFrameRef = useRef(null);
  const processorRef = useRef(null);
  const [isActive, setIsActive] = useState(false);
  const [noiseLevel, setNoiseLevel] = useState(0);
  const [suppressionStrength, setSuppressionStrength] = useState('medium');
  const [activeEngine, setActiveEngine] = useState(null);

  const PROFILES = {
    low: { threshold: -55, hpFreq: 60, lpFreq: 16000, ratio: 6, gain: 1.0 },
    medium: { threshold: -45, hpFreq: 85, lpFreq: 14000, ratio: 12, gain: 1.0 },
    high: { threshold: -35, hpFreq: 120, lpFreq: 12000, ratio: 20, gain: 0.9 },
  };

  const tryRnnoise = async (audioContext, source, destination) => {
    try {
      const { Rnnoise } = await import('@shiguredo/rnnoise-wasm');
      const rnnoise = await Rnnoise.load();
      const denoiseState = rnnoise.createDenoiseState();
      const frameSize = 480;
      const processor = audioContext.createScriptProcessor(4096, 1, 1);

      processor.onaudioprocess = (e) => {
        const input = e.inputBuffer.getChannelData(0);
        const output = e.outputBuffer.getChannelData(0);
        for (let offset = 0; offset < input.length; offset += frameSize) {
          const end = Math.min(offset + frameSize, input.length);
          const frame = new Float32Array(frameSize);
          for (let i = 0; i < end - offset; i++) frame[i] = input[offset + i] * 32768;
          denoiseState.processFrame(frame);
          for (let i = 0; i < end - offset; i++) output[offset + i] = frame[i] / 32768;
        }
      };

      source.connect(processor);
      processor.connect(destination);
      processorRef.current = processor;
      setActiveEngine('rnnoise');
      return true;
    } catch (err) {
      console.warn('RNNoise unavailable, using Web Audio fallback:', err);
      return false;
    }
  };

  const useWebAudioPipeline = (audioContext, source, destination, profile) => {
    const highPass = audioContext.createBiquadFilter();
    highPass.type = 'highpass';
    highPass.frequency.setValueAtTime(profile.hpFreq, audioContext.currentTime);
    highPass.Q.setValueAtTime(0.71, audioContext.currentTime);

    const notch50 = audioContext.createBiquadFilter();
    notch50.type = 'notch';
    notch50.frequency.setValueAtTime(50, audioContext.currentTime);
    notch50.Q.setValueAtTime(15, audioContext.currentTime);

    const notch60 = audioContext.createBiquadFilter();
    notch60.type = 'notch';
    notch60.frequency.setValueAtTime(60, audioContext.currentTime);
    notch60.Q.setValueAtTime(15, audioContext.currentTime);

    const lowPass = audioContext.createBiquadFilter();
    lowPass.type = 'lowpass';
    lowPass.frequency.setValueAtTime(profile.lpFreq, audioContext.currentTime);
    lowPass.Q.setValueAtTime(0.71, audioContext.currentTime);

    const voiceBoost = audioContext.createBiquadFilter();
    voiceBoost.type = 'peaking';
    voiceBoost.frequency.setValueAtTime(3000, audioContext.currentTime);
    voiceBoost.Q.setValueAtTime(1.0, audioContext.currentTime);
    voiceBoost.gain.setValueAtTime(2, audioContext.currentTime);

    const compressor = audioContext.createDynamicsCompressor();
    compressor.threshold.setValueAtTime(profile.threshold, audioContext.currentTime);
    compressor.knee.setValueAtTime(30, audioContext.currentTime);
    compressor.ratio.setValueAtTime(profile.ratio, audioContext.currentTime);
    compressor.attack.setValueAtTime(0.003, audioContext.currentTime);
    compressor.release.setValueAtTime(0.15, audioContext.currentTime);

    const gain = audioContext.createGain();
    gain.gain.setValueAtTime(profile.gain, audioContext.currentTime);
    gainRef.current = gain;

    source.connect(highPass);
    highPass.connect(notch50);
    notch50.connect(notch60);
    notch60.connect(lowPass);
    lowPass.connect(voiceBoost);
    voiceBoost.connect(compressor);
    compressor.connect(gain);
    gain.connect(destination);
    setActiveEngine('webaudio');
  };

  const enableNoiseCancellation = useCallback(async (stream, strength = 'medium') => {
    try {
      setSuppressionStrength(strength);
      const profile = PROFILES[strength] || PROFILES.medium;
      const audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 48000 });
      audioContextRef.current = audioContext;

      const source = audioContext.createMediaStreamSource(stream);
      sourceRef.current = source;

      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 4096;
      analyser.smoothingTimeConstant = 0.85;
      analyserRef.current = analyser;

      const destination = audioContext.createMediaStreamDestination();

      // Create an intermediate gain to connect analyser
      const monitorGain = audioContext.createGain();
      monitorGain.gain.value = 1;

      // Try RNNoise first, fallback to Web Audio
      const rnnoiseOk = await tryRnnoise(audioContext, source, monitorGain);
      if (!rnnoiseOk) {
        useWebAudioPipeline(audioContext, source, monitorGain, profile);
      }

      monitorGain.connect(analyser);
      analyser.connect(destination);

      setIsActive(true);

      // Noise level monitoring
      const dataArray = new Float32Array(analyser.frequencyBinCount);
      const updateLevel = () => {
        if (!analyserRef.current) return;
        analyser.getFloatFrequencyData(dataArray);
        const binWidth = audioContext.sampleRate / analyser.fftSize;
        const startBin = Math.floor(300 / binWidth);
        const endBin = Math.ceil(3400 / binWidth);
        let sum = 0, count = 0;
        for (let i = startBin; i < endBin && i < dataArray.length; i++) { sum += dataArray[i]; count++; }
        const avgDb = count > 0 ? sum / count : -100;
        if (avgDb < noiseFloorRef.current + 5) noiseFloorRef.current = noiseFloorRef.current * 0.99 + avgDb * 0.01;
        setNoiseLevel(Math.round(Math.max(0, Math.min(100, ((avgDb + 100) / 60) * 100))));
        animFrameRef.current = requestAnimationFrame(updateLevel);
      };
      updateLevel();

      return destination.stream;
    } catch (e) {
      console.warn('Noise cancellation not supported:', e);
      return stream;
    }
  }, []);

  const disableNoiseCancellation = useCallback(() => {
    if (animFrameRef.current) { cancelAnimationFrame(animFrameRef.current); animFrameRef.current = null; }
    if (processorRef.current) { try { processorRef.current.disconnect(); } catch {} processorRef.current = null; }
    if (audioContextRef.current) { audioContextRef.current.close(); audioContextRef.current = null; }
    sourceRef.current = null;
    gainRef.current = null;
    analyserRef.current = null;
    noiseFloorRef.current = -60;
    setIsActive(false);
    setNoiseLevel(0);
    setActiveEngine(null);
  }, []);

  const setStrength = useCallback((strength) => {
    setSuppressionStrength(strength);
  }, []);

  return {
    isActive,
    noiseLevel,
    suppressionStrength,
    activeEngine,
    setStrength,
    enableNoiseCancellation,
    disableNoiseCancellation
  };
};

export default useNoiseCancellation;
