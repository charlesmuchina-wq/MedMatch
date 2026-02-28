/**
 * Virtual Background Component for AI KARAU Meeting
 * Uses TensorFlow.js BodyPix for person segmentation
 * Supports: Blur, Custom Images, Solid Colors
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { X, Image, Palette, Loader2, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';

// Predefined background options
const PRESET_BACKGROUNDS = [
  { id: 'none', type: 'none', label: 'None', preview: null },
  { id: 'blur-light', type: 'blur', level: 6, label: 'Light Blur', preview: '🌫️' },
  { id: 'blur-medium', type: 'blur', level: 12, label: 'Medium Blur', preview: '🌁' },
  { id: 'blur-heavy', type: 'blur', level: 20, label: 'Heavy Blur', preview: '☁️' },
  { id: 'office', type: 'image', url: 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=1280&h=720&fit=crop', label: 'Office' },
  { id: 'nature', type: 'image', url: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1280&h=720&fit=crop', label: 'Nature' },
  { id: 'city', type: 'image', url: 'https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?w=1280&h=720&fit=crop', label: 'City' },
  { id: 'abstract', type: 'image', url: 'https://images.unsplash.com/photo-1557683316-973673baf926?w=1280&h=720&fit=crop', label: 'Abstract' },
  { id: 'color-teal', type: 'color', color: '#14b8a6', label: 'Teal' },
  { id: 'color-violet', type: 'color', color: '#8b5cf6', label: 'Violet' },
  { id: 'color-slate', type: 'color', color: '#334155', label: 'Slate' },
];

const VirtualBackground = ({ 
  videoRef, 
  onBackgroundChange, 
  onClose,
  isOpen 
}) => {
  const [selectedBg, setSelectedBg] = useState('none');
  const [isLoading, setIsLoading] = useState(false);
  const [modelLoaded, setModelLoaded] = useState(false);
  const [customImage, setCustomImage] = useState(null);
  
  const canvasRef = useRef(null);
  const bodyPixRef = useRef(null);
  const animationRef = useRef(null);
  const bgImageRef = useRef(null);

  // Load BodyPix model
  useEffect(() => {
    const loadModel = async () => {
      if (bodyPixRef.current) return;
      
      setIsLoading(true);
      try {
        // Dynamic import to avoid SSR issues
        const bodyPix = await import('@tensorflow-models/body-pix');
        const tf = await import('@tensorflow/tfjs');
        
        // Set backend
        await tf.setBackend('webgl');
        await tf.ready();
        
        // Load model with lower resolution for performance
        const net = await bodyPix.load({
          architecture: 'MobileNetV1',
          outputStride: 16,
          multiplier: 0.75,
          quantBytes: 2
        });
        
        bodyPixRef.current = net;
        setModelLoaded(true);
        console.log('BodyPix model loaded');
      } catch (error) {
        console.error('Failed to load BodyPix:', error);
        toast.error('Failed to load virtual background model');
      }
      setIsLoading(false);
    };

    if (isOpen && !modelLoaded) {
      loadModel();
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isOpen, modelLoaded]);

  // Apply background effect
  const applyBackground = useCallback(async () => {
    if (!bodyPixRef.current || !videoRef?.current || !canvasRef.current) return;
    
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    if (video.readyState !== 4) return;
    
    // Set canvas size to match video
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    
    const bg = PRESET_BACKGROUNDS.find(b => b.id === selectedBg) || 
               (customImage ? { type: 'image', url: customImage } : { type: 'none' });
    
    if (bg.type === 'none') {
      // No background effect - just draw video
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    } else {
      try {
        // Perform person segmentation
        const segmentation = await bodyPixRef.current.segmentPerson(video, {
          flipHorizontal: false,
          internalResolution: 'medium',
          segmentationThreshold: 0.7
        });
        
        // Create mask
        const mask = segmentation.data;
        
        // Draw background first
        if (bg.type === 'blur') {
          // Draw blurred video as background
          ctx.filter = `blur(${bg.level}px)`;
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
          ctx.filter = 'none';
        } else if (bg.type === 'color') {
          ctx.fillStyle = bg.color;
          ctx.fillRect(0, 0, canvas.width, canvas.height);
        } else if (bg.type === 'image' && bgImageRef.current) {
          ctx.drawImage(bgImageRef.current, 0, 0, canvas.width, canvas.height);
        }
        
        // Get video frame
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = canvas.width;
        tempCanvas.height = canvas.height;
        const tempCtx = tempCanvas.getContext('2d');
        tempCtx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Get image data
        const imageData = tempCtx.getImageData(0, 0, canvas.width, canvas.height);
        const bgImageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        
        // Composite: show person from video, background from effect
        for (let i = 0; i < mask.length; i++) {
          const pixelIndex = i * 4;
          if (mask[i] === 1) {
            // Person pixel - use video
            bgImageData.data[pixelIndex] = imageData.data[pixelIndex];
            bgImageData.data[pixelIndex + 1] = imageData.data[pixelIndex + 1];
            bgImageData.data[pixelIndex + 2] = imageData.data[pixelIndex + 2];
            bgImageData.data[pixelIndex + 3] = 255;
          }
          // Background pixels already have the effect
        }
        
        ctx.putImageData(bgImageData, 0, 0);
      } catch (error) {
        // Fallback: just draw video
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      }
    }
    
    // Continue animation loop
    animationRef.current = requestAnimationFrame(applyBackground);
  }, [selectedBg, customImage, videoRef]);

  // Start/stop effect when selection changes
  useEffect(() => {
    if (selectedBg === 'none') {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
        animationRef.current = null;
      }
      onBackgroundChange?.(null);
      return;
    }
    
    const bg = PRESET_BACKGROUNDS.find(b => b.id === selectedBg);
    
    // Load background image if needed
    if (bg?.type === 'image' || customImage) {
      const img = new window.Image();
      img.crossOrigin = 'anonymous';
      img.onload = () => {
        bgImageRef.current = img;
        applyBackground();
      };
      img.src = bg?.url || customImage;
    } else {
      applyBackground();
    }
    
    // Pass canvas stream to parent
    if (canvasRef.current) {
      const stream = canvasRef.current.captureStream(30);
      onBackgroundChange?.(stream);
    }
    
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [selectedBg, customImage, applyBackground, onBackgroundChange]);

  // Handle custom image upload
  const handleImageUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setCustomImage(event.target.result);
        setSelectedBg('custom');
      };
      reader.readAsDataURL(file);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <Card className="w-full max-w-2xl bg-karau-card border-karau-border max-h-[90vh] overflow-auto">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-white flex items-center gap-2">
            <Image className="w-5 h-5 text-purple-400" />
            Virtual Background
          </CardTitle>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-5 h-5" />
          </Button>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Loading State */}
          {isLoading && (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-8 h-8 text-purple-400 animate-spin" />
              <span className="ml-3 text-slate-300">Loading AI model...</span>
            </div>
          )}
          
          {/* Preview */}
          <div className="relative aspect-video bg-karau-bg rounded-lg overflow-hidden">
            <canvas 
              ref={canvasRef}
              className="w-full h-full object-cover"
            />
            {selectedBg === 'none' && videoRef?.current && (
              <video 
                ref={videoRef}
                autoPlay 
                muted 
                playsInline
                className="w-full h-full object-cover"
              />
            )}
            {!modelLoaded && !isLoading && (
              <div className="absolute inset-0 flex items-center justify-center bg-karau-bg/80">
                <p className="text-slate-400">Camera preview will appear here</p>
              </div>
            )}
          </div>
          
          {/* Background Options */}
          <div>
            <h3 className="text-sm font-medium text-slate-300 mb-3">Blur Effects</h3>
            <div className="grid grid-cols-4 gap-2">
              {PRESET_BACKGROUNDS.filter(bg => bg.type === 'none' || bg.type === 'blur').map((bg) => (
                <button
                  key={bg.id}
                  onClick={() => setSelectedBg(bg.id)}
                  disabled={!modelLoaded && bg.type !== 'none'}
                  className={`
                    p-3 rounded-lg border-2 transition-all
                    ${selectedBg === bg.id 
                      ? 'border-purple-500 bg-purple-500/10' 
                      : 'border-white/10 bg-karau-surface hover:border-purple-500/40'}
                    ${!modelLoaded && bg.type !== 'none' ? 'opacity-50 cursor-not-allowed' : ''}
                  `}
                >
                  <div className="text-2xl mb-1">{bg.preview || '🚫'}</div>
                  <div className="text-xs text-slate-300">{bg.label}</div>
                  {selectedBg === bg.id && (
                    <Check className="w-4 h-4 text-purple-400 mx-auto mt-1" />
                  )}
                </button>
              ))}
            </div>
          </div>
          
          <div>
            <h3 className="text-sm font-medium text-slate-300 mb-3">Image Backgrounds</h3>
            <div className="grid grid-cols-4 gap-2">
              {PRESET_BACKGROUNDS.filter(bg => bg.type === 'image').map((bg) => (
                <button
                  key={bg.id}
                  onClick={() => setSelectedBg(bg.id)}
                  disabled={!modelLoaded}
                  className={`
                    relative aspect-video rounded-lg border-2 overflow-hidden transition-all
                    ${selectedBg === bg.id 
                      ? 'border-purple-500' 
                      : 'border-white/10 hover:border-purple-500/40'}
                    ${!modelLoaded ? 'opacity-50 cursor-not-allowed' : ''}
                  `}
                >
                  <img 
                    src={bg.url} 
                    alt={bg.label}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute bottom-0 left-0 right-0 bg-black/60 py-1 px-2">
                    <span className="text-xs text-white">{bg.label}</span>
                  </div>
                  {selectedBg === bg.id && (
                    <div className="absolute top-1 right-1 w-5 h-5 bg-purple-500 rounded-full flex items-center justify-center">
                      <Check className="w-3 h-3 text-white" />
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>
          
          <div>
            <h3 className="text-sm font-medium text-slate-300 mb-3">Solid Colors</h3>
            <div className="flex gap-2">
              {PRESET_BACKGROUNDS.filter(bg => bg.type === 'color').map((bg) => (
                <button
                  key={bg.id}
                  onClick={() => setSelectedBg(bg.id)}
                  disabled={!modelLoaded}
                  className={`
                    w-12 h-12 rounded-lg border-2 transition-all
                    ${selectedBg === bg.id 
                      ? 'border-purple-500 ring-2 ring-purple-500/50' 
                      : 'border-white/10 hover:border-purple-500/40'}
                    ${!modelLoaded ? 'opacity-50 cursor-not-allowed' : ''}
                  `}
                  style={{ backgroundColor: bg.color }}
                  title={bg.label}
                >
                  {selectedBg === bg.id && (
                    <Check className="w-5 h-5 text-white mx-auto" />
                  )}
                </button>
              ))}
              
              {/* Custom Image Upload */}
              <label className={`
                w-12 h-12 rounded-lg border-2 border-dashed border-white/10 
                flex items-center justify-center cursor-pointer
                hover:border-purple-500/40 transition-all
                ${!modelLoaded ? 'opacity-50 cursor-not-allowed' : ''}
              `}>
                <input 
                  type="file" 
                  accept="image/*"
                  onChange={handleImageUpload}
                  disabled={!modelLoaded}
                  className="hidden"
                />
                <Palette className="w-5 h-5 text-slate-400" />
              </label>
            </div>
          </div>
          
          {/* Custom Image Preview */}
          {customImage && (
            <div className="flex items-center gap-3 p-3 bg-karau-surface rounded-lg">
              <img 
                src={customImage} 
                alt="Custom" 
                className="w-16 h-12 object-cover rounded"
              />
              <div className="flex-1">
                <p className="text-sm text-white">Custom Background</p>
                <p className="text-xs text-slate-400">Your uploaded image</p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setCustomImage(null);
                  if (selectedBg === 'custom') setSelectedBg('none');
                }}
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          )}
          
          {/* Apply Button */}
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button 
              className="bg-purple-500 hover:bg-purple-500/90"
              onClick={onClose}
            >
              Apply Background
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default VirtualBackground;
