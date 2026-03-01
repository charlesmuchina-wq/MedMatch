import { useState, useRef, useCallback, useEffect } from 'react';

/**
 * Spatial audio hook - positions audio in 3D space based on speaker video tile location.
 * Uses Web Audio API PannerNode for directional audio.
 */
export function useSpatialAudio() {
  const [enabled, setEnabled] = useState(false);
  const audioContextRef = useRef(null);
  const pannersRef = useRef({});
  const listenerPosRef = useRef({ x: 0, y: 0, z: 0 });

  const getContext = useCallback(() => {
    if (!audioContextRef.current || audioContextRef.current.state === 'closed') {
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioContextRef.current.state === 'suspended') {
      audioContextRef.current.resume();
    }
    return audioContextRef.current;
  }, []);

  /**
   * Connect a remote audio stream to spatial panner.
   * @param {string} userId - Unique ID for the remote participant
   * @param {MediaStream} stream - The remote audio stream
   * @param {Object} position - {x, y} normalized position (-1 to 1) of the video tile
   */
  const connectStream = useCallback((userId, stream, position = { x: 0, y: 0 }) => {
    if (!enabled || !stream) return;
    // Disconnect existing if any
    disconnectStream(userId);

    const ctx = getContext();
    try {
      const source = ctx.createMediaStreamSource(stream);
      const panner = ctx.createPanner();
      panner.panningModel = 'HRTF';
      panner.distanceModel = 'inverse';
      panner.refDistance = 1;
      panner.maxDistance = 10;
      panner.rolloffFactor = 1;
      panner.coneInnerAngle = 360;
      panner.coneOuterAngle = 0;
      panner.coneOuterGain = 0;

      // Position in 3D space (x = left/right, y = up/down, z = front/back)
      const x = (position.x || 0) * 3;
      const y = (position.y || 0) * 1;
      const z = -2;
      panner.positionX.setValueAtTime(x, ctx.currentTime);
      panner.positionY.setValueAtTime(y, ctx.currentTime);
      panner.positionZ.setValueAtTime(z, ctx.currentTime);

      source.connect(panner);
      panner.connect(ctx.destination);

      pannersRef.current[userId] = { source, panner, stream };
    } catch (e) {
      console.warn('Spatial audio connect error:', e);
    }
  }, [enabled, getContext]);

  /**
   * Update the spatial position of an existing stream.
   */
  const updatePosition = useCallback((userId, position) => {
    const entry = pannersRef.current[userId];
    if (!entry || !audioContextRef.current) return;

    const ctx = audioContextRef.current;
    const x = (position.x || 0) * 3;
    const y = (position.y || 0) * 1;

    // Smooth transition
    entry.panner.positionX.linearRampToValueAtTime(x, ctx.currentTime + 0.3);
    entry.panner.positionY.linearRampToValueAtTime(y, ctx.currentTime + 0.3);
  }, []);

  const disconnectStream = useCallback((userId) => {
    const entry = pannersRef.current[userId];
    if (entry) {
      try {
        entry.source.disconnect();
        entry.panner.disconnect();
      } catch {}
      delete pannersRef.current[userId];
    }
  }, []);

  const toggle = useCallback(() => {
    setEnabled(prev => {
      const next = !prev;
      if (!next) {
        // Disconnect all panners when disabling
        Object.keys(pannersRef.current).forEach(uid => disconnectStream(uid));
        if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
          try { audioContextRef.current.close(); } catch {}
        }
        audioContextRef.current = null;
      }
      return next;
    });
  }, [disconnectStream]);

  const cleanup = useCallback(() => {
    Object.keys(pannersRef.current).forEach(uid => disconnectStream(uid));
    if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
      try { audioContextRef.current.close(); } catch {}
    }
    audioContextRef.current = null;
    pannersRef.current = {};
  }, [disconnectStream]);

  useEffect(() => {
    return cleanup;
  }, [cleanup]);

  return {
    enabled,
    toggle,
    connectStream,
    updatePosition,
    disconnectStream,
    cleanup
  };
}

export default useSpatialAudio;
