/**
 * useVirtualBackground Hook - Enterprise Grade
 * Real-time AI-powered background replacement using MediaPipe Image Segmenter
 * Benchmarked against Zoom/Teams/Webex standards
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
  const offscreenCanvasRef = useRef(null);
  const segmenterRef = useRef(null);
  const animationFrameRef = useRef(null);
  const backgroundImageRef = useRef(null);
  const activeRef = useRef(false);
  const backgroundTypeRef = useRef(backgroundType);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isSupported, setIsSupported] = useState(true);
  const [isActive, setIsActive] = useState(false);

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
      
      setIsLoading(false);
      return true;
    } catch (err) {
      console.error('Failed to initialize segmenter:', err);
      setError(`Failed to load AI model: ${err.message}`);
      setIsLoading(false);
      return false;
    }
  }, []);

  /**
   * Skin Tone Protection - Automatic AI Enhancement
   * Adjusts luminance and saturation of skin-tone color ranges to ensure
   * inclusive, natural rendering for all skin tones without overexposure.
   * Inspired by Agora SDK skinProtectLevel and Zoom/Teams rendering.
   */
  const applySkinToneProtection = useCallback((pixels, maskData) => {
    for (let i = 0; i < maskData.length; i++) {
      if (maskData[i] === 0) continue; // Skip background pixels

      const px = i * 4;
      const r = pixels[px];
      const g = pixels[px + 1];
      const b = pixels[px + 2];

      // Fast RGB-to-HSL inline (avoid function call overhead per pixel)
      const rn = r / 255, gn = g / 255, bn = b / 255;
      const max = Math.max(rn, gn, bn), min = Math.min(rn, gn, bn);
      const delta = max - min;
      let h = 0, s = 0, l = (max + min) / 2;

      if (delta > 0) {
        s = l > 0.5 ? delta / (2 - max - min) : delta / (max + min);
        if (max === rn) h = ((gn - bn) / delta + (gn < bn ? 6 : 0)) * 60;
        else if (max === gn) h = ((bn - rn) / delta + 2) * 60;
        else h = ((rn - gn) / delta + 4) * 60;
      }

      // Detect skin tone: hue 8-50 (orange-yellow range), saturation > 0.15, lightness 0.15-0.85
      if (h >= 8 && h <= 50 && s > 0.15 && l > 0.15 && l < 0.85) {
        // Boost saturation slightly for vibrancy (stronger for darker tones)
        const darkBoost = l < 0.4 ? 0.08 : l < 0.55 ? 0.05 : 0.02;
        s = Math.min(s + darkBoost, 1.0);

        // Lift shadows on darker skin without washing out mid/light tones
        if (l < 0.35) {
          l = l + 0.03;
        } else if (l < 0.5) {
          l = l + 0.015;
        }
        // Prevent overexposure on lighter skin
        if (l > 0.75) {
          l = l - 0.01;
        }

        // HSL back to RGB
        const c = (1 - Math.abs(2 * l - 1)) * s;
        const x = c * (1 - Math.abs((h / 60) % 2 - 1));
        const m = l - c / 2;
        let r1, g1, b1;
        if (h < 60)       { r1 = c; g1 = x; b1 = 0; }
        else if (h < 120) { r1 = x; g1 = c; b1 = 0; }
        else if (h < 180) { r1 = 0; g1 = c; b1 = x; }
        else if (h < 240) { r1 = 0; g1 = x; b1 = c; }
        else if (h < 300) { r1 = x; g1 = 0; b1 = c; }
        else               { r1 = c; g1 = 0; b1 = x; }

        pixels[px]     = Math.round((r1 + m) * 255);
        pixels[px + 1] = Math.round((g1 + m) * 255);
        pixels[px + 2] = Math.round((b1 + m) * 255);
      }
    }
  }, []);

  // Composite a frame with background effect
  const compositeFrame = useCallback(() => {
    if (!activeRef.current) return;
    
    const video = videoElement;
    const canvas = canvasRef.current;
    const segmenter = segmenterRef.current;
    const bgType = backgroundTypeRef.current;
    
    if (!segmenter || !video || !canvas || video.readyState < 2 || video.videoWidth === 0) {
      animationFrameRef.current = requestAnimationFrame(compositeFrame);
      return;
    }
    
    try {
      const width = video.videoWidth;
      const height = video.videoHeight;
      
      if (canvas.width !== width || canvas.height !== height) {
        canvas.width = width;
        canvas.height = height;
      }
      
      const ctx = canvas.getContext('2d', { willReadFrequently: true });
      
      // Run segmentation
      const result = segmenter.segmentForVideo(video, performance.now());
      
      if (result && result.categoryMask) {
        const maskData = result.categoryMask.getAsUint8Array();
        const isBlur = bgType.includes('blur');
        
        // Draw original video first
        ctx.drawImage(video, 0, 0, width, height);
        const originalFrame = ctx.getImageData(0, 0, width, height);
        const origPixels = originalFrame.data;
        
        // Create background frame
        let bgPixels = null;
        
        if (isBlur) {
          // Create blurred version
          const blurAmount = bgType === 'blur-light' ? 10 : bgType === 'blur-heavy' ? 28 : 16;
          if (!offscreenCanvasRef.current) {
            offscreenCanvasRef.current = document.createElement('canvas');
          }
          const offCanvas = offscreenCanvasRef.current;
          offCanvas.width = width;
          offCanvas.height = height;
          const offCtx = offCanvas.getContext('2d');
          offCtx.filter = `blur(${blurAmount}px)`;
          offCtx.drawImage(video, 0, 0, width, height);
          offCtx.filter = 'none';
          bgPixels = offCtx.getImageData(0, 0, width, height).data;
        } else if (backgroundImageRef.current) {
          // Draw background image
          if (!offscreenCanvasRef.current) {
            offscreenCanvasRef.current = document.createElement('canvas');
          }
          const offCanvas = offscreenCanvasRef.current;
          offCanvas.width = width;
          offCanvas.height = height;
          const offCtx = offCanvas.getContext('2d');
          offCtx.drawImage(backgroundImageRef.current, 0, 0, width, height);
          bgPixels = offCtx.getImageData(0, 0, width, height).data;
        }
        
        if (bgPixels) {
          for (let i = 0; i < maskData.length; i++) {
            const isPerson = maskData[i] > 0;
            
            if (!isPerson) {
              const px = i * 4;
              origPixels[px] = bgPixels[px];
              origPixels[px + 1] = bgPixels[px + 1];
              origPixels[px + 2] = bgPixels[px + 2];
            }
          }
        }
        
        // Apply automatic skin tone protection on person pixels
        applySkinToneProtection(origPixels, maskData);
        
        ctx.putImageData(originalFrame, 0, 0);
        
        result.categoryMask.close();
      } else {
        // No mask available — just draw original video
        ctx.drawImage(video, 0, 0, width, height);
      }
    } catch (err) {
      // Frame error — silently skip, next frame will retry
    }
    
    animationFrameRef.current = requestAnimationFrame(compositeFrame);
  }, [videoElement, applySkinToneProtection]);

  // Start/stop processing based on background type
  useEffect(() => {
    const shouldProcess = backgroundType && backgroundType !== 'none' && isSupported;
    
    if (shouldProcess && !activeRef.current) {
      activeRef.current = true;
      setIsActive(true);
      
      const start = async () => {
        const initialized = await initializeSegmenter();
        if (initialized && activeRef.current) {
          compositeFrame();
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
  }, [backgroundType, isSupported, initializeSegmenter, compositeFrame]);

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
