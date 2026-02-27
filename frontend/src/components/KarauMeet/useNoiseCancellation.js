import { useRef, useCallback, useState } from 'react';

/**
 * AI Noise Cancellation Hook
 * Uses Web Audio API to apply noise gate and suppression
 */
export const useNoiseCancellation = () => {
  const audioContextRef = useRef(null);
  const sourceRef = useRef(null);
  const gainRef = useRef(null);
  const analyserRef = useRef(null);
  const [isActive, setIsActive] = useState(false);
  const [noiseLevel, setNoiseLevel] = useState(0);

  const enableNoiseCancellation = useCallback(async (stream) => {
    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      audioContextRef.current = audioContext;

      const source = audioContext.createMediaStreamSource(stream);
      sourceRef.current = source;

      // Create analyser for noise level monitoring
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 2048;
      analyser.smoothingTimeConstant = 0.8;
      analyserRef.current = analyser;

      // Noise gate - suppresses audio below threshold
      const compressor = audioContext.createDynamicsCompressor();
      compressor.threshold.setValueAtTime(-50, audioContext.currentTime);
      compressor.knee.setValueAtTime(40, audioContext.currentTime);
      compressor.ratio.setValueAtTime(12, audioContext.currentTime);
      compressor.attack.setValueAtTime(0, audioContext.currentTime);
      compressor.release.setValueAtTime(0.25, audioContext.currentTime);

      // High-pass filter to remove low-frequency rumble (AC, fans)
      const highPass = audioContext.createBiquadFilter();
      highPass.type = 'highpass';
      highPass.frequency.setValueAtTime(85, audioContext.currentTime);
      highPass.Q.setValueAtTime(0.7, audioContext.currentTime);

      // Low-pass filter to remove high-frequency hiss
      const lowPass = audioContext.createBiquadFilter();
      lowPass.type = 'lowpass';
      lowPass.frequency.setValueAtTime(14000, audioContext.currentTime);
      lowPass.Q.setValueAtTime(0.7, audioContext.currentTime);

      // Notch filter for common electrical hum (50/60Hz)
      const notch = audioContext.createBiquadFilter();
      notch.type = 'notch';
      notch.frequency.setValueAtTime(60, audioContext.currentTime);
      notch.Q.setValueAtTime(10, audioContext.currentTime);

      // Gain node for final output
      const gain = audioContext.createGain();
      gain.gain.setValueAtTime(1.0, audioContext.currentTime);
      gainRef.current = gain;

      // Create destination to get processed stream
      const destination = audioContext.createMediaStreamDestination();

      // Chain: source -> highPass -> notch -> lowPass -> compressor -> gain -> analyser -> destination
      source.connect(highPass);
      highPass.connect(notch);
      notch.connect(lowPass);
      lowPass.connect(compressor);
      compressor.connect(gain);
      gain.connect(analyser);
      analyser.connect(destination);

      setIsActive(true);

      // Monitor noise level
      const dataArray = new Uint8Array(analyser.frequencyBinCount);
      const updateLevel = () => {
        if (!analyserRef.current) return;
        analyser.getByteFrequencyData(dataArray);
        const avg = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
        setNoiseLevel(Math.round(avg));
        if (isActive) requestAnimationFrame(updateLevel);
      };
      updateLevel();

      // Return processed stream (replace audio track)
      return destination.stream;
    } catch (e) {
      console.warn('Noise cancellation not supported:', e);
      return stream;
    }
  }, [isActive]);

  const disableNoiseCancellation = useCallback(() => {
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    sourceRef.current = null;
    gainRef.current = null;
    analyserRef.current = null;
    setIsActive(false);
    setNoiseLevel(0);
  }, []);

  return {
    isActive,
    noiseLevel,
    enableNoiseCancellation,
    disableNoiseCancellation
  };
};

export default useNoiseCancellation;
