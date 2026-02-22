/**
 * useVirtualBackground Hook
 * Real-time AI-powered background replacement using MediaPipe Image Segmenter
 * 
 * Supports:
 * - Blur backgrounds (light, standard, heavy)
 * - Image replacement backgrounds
 * - Real-time video processing at ~30fps
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import { ImageSegmenter, FilesetResolver } from '@mediapipe/tasks-vision';

// MediaPipe WASM and model URLs
const WASM_CDN = 'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm';
const MODEL_URL = 'https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_segmenter/float16_quant/1/selfie_segmenter.tflite';

/**
 * Custom hook for virtual background effects
 * @param {HTMLVideoElement} videoElement - Source video element
 * @param {string} backgroundType - 'none' | 'blur' | 'blur-light' | 'blur-heavy' | image URL
 * @param {string} backgroundUrl - URL for image backgrounds
 * @returns {Object} - { canvasRef, isLoading, error, isSupported }
 */
export const useVirtualBackground = (videoElement, backgroundType, backgroundUrl = null) => {
  const canvasRef = useRef(null);
  const segmenterRef = useRef(null);
  const animationFrameRef = useRef(null);
  const backgroundImageRef = useRef(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isSupported, setIsSupported] = useState(true);
  const [isActive, setIsActive] = useState(false);

  // Check browser support
  useEffect(() => {
    const checkSupport = () => {
      // Check for WebAssembly support
      if (typeof WebAssembly !== 'object') {
        setIsSupported(false);
        setError('WebAssembly not supported');
        return false;
      }
      // Check for OffscreenCanvas (optional, for better performance)
      const hasOffscreen = typeof OffscreenCanvas !== 'undefined';
      console.log(`Virtual Background: OffscreenCanvas ${hasOffscreen ? 'supported' : 'not supported'}`);
      return true;
    };
    checkSupport();
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
      img.onerror = (e) => {
        console.error('Failed to load background image:', e);
        backgroundImageRef.current = null;
      };
      img.src = backgroundUrl;
    } else {
      backgroundImageRef.current = null;
    }
  }, [backgroundUrl, backgroundType]);

  // Initialize MediaPipe segmenter
  const initializeSegmenter = useCallback(async () => {
    if (segmenterRef.current) return; // Already initialized
    
    setIsLoading(true);
    setError(null);
    
    try {
      console.log('Initializing MediaPipe Image Segmenter...');
      
      const filesetResolver = await FilesetResolver.forVisionTasks(WASM_CDN);
      
      segmenterRef.current = await ImageSegmenter.createFromOptions(filesetResolver, {
        baseOptions: {
          modelAssetPath: MODEL_URL,
          delegate: 'GPU' // Use GPU acceleration if available
        },
        runningMode: 'VIDEO',
        outputCategoryMask: true,
        outputConfidenceMasks: false
      });
      
      console.log('MediaPipe Image Segmenter initialized successfully');
      setIsLoading(false);
      return true;
    } catch (err) {
      console.error('Failed to initialize segmenter:', err);
      setError(`Failed to load AI model: ${err.message}`);
      setIsLoading(false);
      return false;
    }
  }, []);

  // Composite frame with background
  const compositeFrame = useCallback((video, canvas, mask, ctx) => {
    const width = canvas.width;
    const height = canvas.height;
    
    // Get mask data
    const maskData = mask.getAsUint8Array();
    
    // Draw the video frame first
    ctx.drawImage(video, 0, 0, width, height);
    
    // Get the frame data
    const imageData = ctx.getImageData(0, 0, width, height);
    const pixels = imageData.data;
    
    // Determine blur level or background type
    const isBlur = backgroundType.includes('blur');
    const blurAmount = backgroundType === 'blur-light' ? 8 : 
                       backgroundType === 'blur-heavy' ? 24 : 12;
    
    if (isBlur) {
      // For blur, we'll create a blurred version and blend
      const tempCanvas = document.createElement('canvas');
      tempCanvas.width = width;
      tempCanvas.height = height;
      const tempCtx = tempCanvas.getContext('2d');
      
      // Apply blur filter
      tempCtx.filter = `blur(${blurAmount}px)`;
      tempCtx.drawImage(video, 0, 0, width, height);
      tempCtx.filter = 'none';
      
      // Get blurred pixels
      const blurredData = tempCtx.getImageData(0, 0, width, height);
      const blurredPixels = blurredData.data;
      
      // Blend based on mask
      for (let i = 0; i < maskData.length; i++) {
        const pixelIndex = i * 4;
        // Mask value: 0 = background, 255 = person
        const maskValue = maskData[i];
        const alpha = maskValue / 255;
        
        // Blend original (person) with blurred (background)
        pixels[pixelIndex] = pixels[pixelIndex] * alpha + blurredPixels[pixelIndex] * (1 - alpha);
        pixels[pixelIndex + 1] = pixels[pixelIndex + 1] * alpha + blurredPixels[pixelIndex + 1] * (1 - alpha);
        pixels[pixelIndex + 2] = pixels[pixelIndex + 2] * alpha + blurredPixels[pixelIndex + 2] * (1 - alpha);
      }
    } else if (backgroundImageRef.current) {
      // For image background
      const tempCanvas = document.createElement('canvas');
      tempCanvas.width = width;
      tempCanvas.height = height;
      const tempCtx = tempCanvas.getContext('2d');
      
      // Draw background image (scaled to fit)
      tempCtx.drawImage(backgroundImageRef.current, 0, 0, width, height);
      const bgData = tempCtx.getImageData(0, 0, width, height);
      const bgPixels = bgData.data;
      
      // Blend based on mask
      for (let i = 0; i < maskData.length; i++) {
        const pixelIndex = i * 4;
        const maskValue = maskData[i];
        const alpha = maskValue / 255;
        
        // Blend background with person
        pixels[pixelIndex] = pixels[pixelIndex] * alpha + bgPixels[pixelIndex] * (1 - alpha);
        pixels[pixelIndex + 1] = pixels[pixelIndex + 1] * alpha + bgPixels[pixelIndex + 1] * (1 - alpha);
        pixels[pixelIndex + 2] = pixels[pixelIndex + 2] * alpha + bgPixels[pixelIndex + 2] * (1 - alpha);
      }
    }
    
    // Put the composited image back
    ctx.putImageData(imageData, 0, 0);
  }, [backgroundType]);

  // Process video frame
  const processFrame = useCallback(async () => {
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
      
      // Ensure canvas matches video dimensions
      if (canvas.width !== videoElement.videoWidth || canvas.height !== videoElement.videoHeight) {
        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;
      }
      
      // Run segmentation
      const result = segmenterRef.current.segmentForVideo(videoElement, performance.now());
      
      if (result && result.categoryMask) {
        compositeFrame(videoElement, canvas, result.categoryMask, ctx);
        result.categoryMask.close(); // Free memory
      } else {
        // No mask, just draw video
        ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
      }
    } catch (err) {
      console.error('Frame processing error:', err);
    }
    
    animationFrameRef.current = requestAnimationFrame(processFrame);
  }, [videoElement, compositeFrame]);

  // Start/stop processing based on background type
  useEffect(() => {
    const shouldProcess = backgroundType && backgroundType !== 'none' && isSupported;
    
    if (shouldProcess && !isActive) {
      // Start processing
      const start = async () => {
        const initialized = await initializeSegmenter();
        if (initialized) {
          setIsActive(true);
          processFrame();
        }
      };
      start();
    } else if (!shouldProcess && isActive) {
      // Stop processing
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
      setIsActive(false);
    }
    
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [backgroundType, isSupported, isActive, initializeSegmenter, processFrame]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
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
