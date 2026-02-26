/**
 * useVirtualBackground Hook
 * Real-time AI-powered background replacement using MediaPipe Image Segmenter
 */

import { useEffect, useRef, useState, useCallback } from 'react';

// MediaPipe WASM and model URLs - pinned version for stability
const WASM_CDN = 'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm';
const MODEL_URL = 'https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_segmenter/float16_quant/1/selfie_segmenter.tflite';

/**
 * Custom hook for virtual background effects
 * @param {HTMLVideoElement} videoElement - Source video element
 * @param {string} backgroundType - 'none' | 'blur' | 'blur-light' | 'blur-heavy' | background id
 * @param {string} backgroundUrl - URL for image backgrounds
 * @returns {Object} - { canvasRef, isLoading, error, isSupported, isActive }
 */
export const useVirtualBackground = (videoElement, backgroundType, backgroundUrl = null) => {
  const canvasRef = useRef(null);
  const segmenterRef = useRef(null);
  const animationFrameRef = useRef(null);
  const backgroundImageRef = useRef(null);
  const activeRef = useRef(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isSupported, setIsSupported] = useState(true);
  const [isActive, setIsActive] = useState(false);
  const backgroundTypeRef = useRef(backgroundType);

  // Keep ref in sync
  useEffect(() => {
    backgroundTypeRef.current = backgroundType;
  }, [backgroundType]);

  // Check browser support
  useEffect(() => {
    if (typeof WebAssembly !== 'object') {
      setIsSupported(false);
      setError('WebAssembly not supported');
    }
  }, []);

  // Load background image when URL changes
  useEffect(() => {
    if (backgroundUrl && backgroundType !== 'none' && !backgroundType.includes('blur')) {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = () => {
        backgroundImageRef.current = img;
        console.log('Background image loaded:', backgroundUrl);
      };
      img.onerror = () => {
        console.error('Failed to load background image:', backgroundUrl);
        backgroundImageRef.current = null;
      };
      img.src = backgroundUrl;
    } else if (backgroundType === 'none') {
      backgroundImageRef.current = null;
    }
  }, [backgroundUrl, backgroundType]);

  // Initialize MediaPipe segmenter
  const initializeSegmenter = useCallback(async () => {
    if (segmenterRef.current) return true;
    
    setIsLoading(true);
    setError(null);
    
    try {
      console.log('Initializing MediaPipe Image Segmenter...');
      const { ImageSegmenter, FilesetResolver } = await import('@mediapipe/tasks-vision');
      
      const filesetResolver = await FilesetResolver.forVisionTasks(WASM_CDN);
      
      segmenterRef.current = await ImageSegmenter.createFromOptions(filesetResolver, {
        baseOptions: {
          modelAssetPath: MODEL_URL,
          delegate: 'GPU'
        },
        runningMode: 'VIDEO',
        outputCategoryMask: true,
        outputConfidenceMasks: false
      });
      
      console.log('MediaPipe Image Segmenter ready');
      setIsLoading(false);
      return true;
    } catch (err) {
      console.error('Failed to initialize segmenter:', err);
      setError(`Failed to load AI model: ${err.message}`);
      setIsLoading(false);
      return false;
    }
  }, []);

  // Process a single video frame
  const processFrame = useCallback(() => {
    if (!activeRef.current) return;
    if (!segmenterRef.current || !videoElement || !canvasRef.current) {
      animationFrameRef.current = requestAnimationFrame(processFrame);
      return;
    }
    
    if (videoElement.readyState < 2 || videoElement.videoWidth === 0) {
      animationFrameRef.current = requestAnimationFrame(processFrame);
      return;
    }
    
    try {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d', { willReadFrequently: true });
      const bgType = backgroundTypeRef.current;
      
      if (canvas.width !== videoElement.videoWidth || canvas.height !== videoElement.videoHeight) {
        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;
      }
      
      const result = segmenterRef.current.segmentForVideo(videoElement, performance.now());
      
      if (result && result.categoryMask) {
        const width = canvas.width;
        const height = canvas.height;
        const maskData = result.categoryMask.getAsUint8Array();
        
        // Draw the video frame
        ctx.drawImage(videoElement, 0, 0, width, height);
        const imageData = ctx.getImageData(0, 0, width, height);
        const pixels = imageData.data;
        
        const isBlur = bgType.includes('blur');
        
        if (isBlur) {
          const blurAmount = bgType === 'blur-light' ? 8 : bgType === 'blur-heavy' ? 24 : 12;
          const tempCanvas = document.createElement('canvas');
          tempCanvas.width = width;
          tempCanvas.height = height;
          const tempCtx = tempCanvas.getContext('2d');
          tempCtx.filter = `blur(${blurAmount}px)`;
          tempCtx.drawImage(videoElement, 0, 0, width, height);
          tempCtx.filter = 'none';
          const blurredData = tempCtx.getImageData(0, 0, width, height);
          const blurredPixels = blurredData.data;
          
          for (let i = 0; i < maskData.length; i++) {
            const px = i * 4;
            const alpha = maskData[i] / 255;
            pixels[px] = pixels[px] * alpha + blurredPixels[px] * (1 - alpha);
            pixels[px + 1] = pixels[px + 1] * alpha + blurredPixels[px + 1] * (1 - alpha);
            pixels[px + 2] = pixels[px + 2] * alpha + blurredPixels[px + 2] * (1 - alpha);
          }
        } else if (backgroundImageRef.current) {
          const tempCanvas = document.createElement('canvas');
          tempCanvas.width = width;
          tempCanvas.height = height;
          const tempCtx = tempCanvas.getContext('2d');
          tempCtx.drawImage(backgroundImageRef.current, 0, 0, width, height);
          const bgData = tempCtx.getImageData(0, 0, width, height);
          const bgPixels = bgData.data;
          
          for (let i = 0; i < maskData.length; i++) {
            const px = i * 4;
            const alpha = maskData[i] / 255;
            pixels[px] = pixels[px] * alpha + bgPixels[px] * (1 - alpha);
            pixels[px + 1] = pixels[px + 1] * alpha + bgPixels[px + 1] * (1 - alpha);
            pixels[px + 2] = pixels[px + 2] * alpha + bgPixels[px + 2] * (1 - alpha);
          }
        }
        
        ctx.putImageData(imageData, 0, 0);
        result.categoryMask.close();
      } else {
        ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
      }
    } catch (err) {
      // Silently handle frame errors, they self-recover
    }
    
    animationFrameRef.current = requestAnimationFrame(processFrame);
  }, [videoElement]);

  // Start/stop processing based on background type
  useEffect(() => {
    const shouldProcess = backgroundType && backgroundType !== 'none' && isSupported;
    
    if (shouldProcess && !activeRef.current) {
      activeRef.current = true;
      setIsActive(true);
      
      const start = async () => {
        const initialized = await initializeSegmenter();
        if (initialized && activeRef.current) {
          processFrame();
        }
      };
      start();
    } else if (!shouldProcess && activeRef.current) {
      activeRef.current = false;
      setIsActive(false);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
    }
    
    return () => {
      if (!shouldProcess) {
        activeRef.current = false;
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current);
          animationFrameRef.current = null;
        }
      }
    };
  }, [backgroundType, isSupported, initializeSegmenter, processFrame]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      activeRef.current = false;
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (segmenterRef.current) {
        segmenterRef.current.close();
        segmenterRef.current = null;
      }
    };
  }, []);

  return {
    canvasRef,
    isLoading,
    error,
    isSupported,
    isActive
  };
};

export default useVirtualBackground;
