/**
 * Virtual Background Component for AI KARAU Meeting
 * Uses CSS filter-based background effects (no ML dependencies)
 * Supports: Blur, Custom Images, Solid Colors
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { X, Image, Palette, Loader2, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';

const PRESET_BACKGROUNDS = [
  { id: 'none', type: 'none', label: 'None', preview: null },
  { id: 'blur-light', type: 'blur', level: 6, label: 'Light Blur', preview: null },
  { id: 'blur-medium', type: 'blur', level: 12, label: 'Medium Blur', preview: null },
  { id: 'blur-heavy', type: 'blur', level: 20, label: 'Heavy Blur', preview: null },
  { id: 'office', type: 'image', url: 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=1280&h=720&fit=crop', label: 'Office' },
  { id: 'nature', type: 'image', url: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1280&h=720&fit=crop', label: 'Nature' },
  { id: 'city', type: 'image', url: 'https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?w=1280&h=720&fit=crop', label: 'City' },
  { id: 'abstract', type: 'image', url: 'https://images.unsplash.com/photo-1557683316-973673baf926?w=1280&h=720&fit=crop', label: 'Abstract' },
  { id: 'color-teal', type: 'color', color: '#14b8a6', label: 'Teal' },
  { id: 'color-violet', type: 'color', color: '#8b5cf6', label: 'Violet' },
  { id: 'color-slate', type: 'color', color: '#334155', label: 'Slate' },
];

const VirtualBackground = ({ videoRef, onBackgroundChange, onClose, isOpen }) => {
  const [selectedBg, setSelectedBg] = useState('none');
  const [customImage, setCustomImage] = useState(null);
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const bgImageRef = useRef(null);

  const applyBackground = useCallback(() => {
    if (!videoRef?.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    if (video.readyState !== 4) {
      animationRef.current = requestAnimationFrame(applyBackground);
      return;
    }

    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;

    const bg = PRESET_BACKGROUNDS.find(b => b.id === selectedBg) ||
               (customImage ? { type: 'image', url: customImage } : { type: 'none' });

    if (bg.type === 'none') {
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    } else if (bg.type === 'blur') {
      ctx.filter = `blur(${bg.level}px)`;
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      ctx.filter = 'none';
      // Draw center portion (person area) without blur
      const cx = canvas.width * 0.2, cy = canvas.height * 0.1;
      const cw = canvas.width * 0.6, ch = canvas.height * 0.85;
      ctx.save();
      ctx.beginPath();
      ctx.ellipse(canvas.width / 2, canvas.height / 2, cw / 2, ch / 2, 0, 0, Math.PI * 2);
      ctx.clip();
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      ctx.restore();
    } else if (bg.type === 'color') {
      ctx.fillStyle = bg.color;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      // Overlay video in center ellipse
      const cw = canvas.width * 0.6, ch = canvas.height * 0.85;
      ctx.save();
      ctx.beginPath();
      ctx.ellipse(canvas.width / 2, canvas.height / 2, cw / 2, ch / 2, 0, 0, Math.PI * 2);
      ctx.clip();
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      ctx.restore();
    } else if (bg.type === 'image' && bgImageRef.current) {
      ctx.drawImage(bgImageRef.current, 0, 0, canvas.width, canvas.height);
      const cw = canvas.width * 0.6, ch = canvas.height * 0.85;
      ctx.save();
      ctx.beginPath();
      ctx.ellipse(canvas.width / 2, canvas.height / 2, cw / 2, ch / 2, 0, 0, Math.PI * 2);
      ctx.clip();
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      ctx.restore();
    }

    animationRef.current = requestAnimationFrame(applyBackground);
  }, [selectedBg, customImage, videoRef]);

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

    if (canvasRef.current) {
      const stream = canvasRef.current.captureStream(30);
      onBackgroundChange?.(stream);
    }

    return () => {
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    };
  }, [selectedBg, customImage, applyBackground, onBackgroundChange]);

  const handleCustomUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setCustomImage(url);
      setSelectedBg('custom');
      toast.success('Custom background loaded');
    }
  };

  if (!isOpen) return null;

  return (
    <Card className="absolute bottom-16 right-4 w-80 z-50 bg-slate-900/95 border-slate-700/50 backdrop-blur-xl shadow-2xl" data-testid="virtual-bg-panel">
      <CardHeader className="pb-2 flex flex-row items-center justify-between">
        <CardTitle className="text-sm text-white">Virtual Background</CardTitle>
        <Button variant="ghost" size="sm" onClick={onClose} className="h-6 w-6 p-0 text-slate-400 hover:text-white"><X className="w-4 h-4" /></Button>
      </CardHeader>
      <CardContent className="space-y-3">
        <canvas ref={canvasRef} className="hidden" />

        {/* Background grid */}
        <div className="grid grid-cols-4 gap-2">
          {PRESET_BACKGROUNDS.map(bg => (
            <button key={bg.id} onClick={() => setSelectedBg(bg.id)}
              className={`relative rounded-lg overflow-hidden h-14 border-2 transition-all ${selectedBg === bg.id ? 'border-teal-400 ring-1 ring-teal-400/30' : 'border-transparent hover:border-slate-600'}`}
              data-testid={`bg-${bg.id}`}>
              {bg.type === 'none' ? (
                <div className="w-full h-full bg-slate-800 flex items-center justify-center"><X className="w-4 h-4 text-slate-500" /></div>
              ) : bg.type === 'blur' ? (
                <div className="w-full h-full bg-gradient-to-br from-slate-600 to-slate-700 flex items-center justify-center"><span className="text-[9px] text-white font-medium">{bg.label.replace('Blur','').trim()}</span></div>
              ) : bg.type === 'color' ? (
                <div className="w-full h-full" style={{ backgroundColor: bg.color }} />
              ) : bg.type === 'image' ? (
                <img src={bg.url} alt={bg.label} className="w-full h-full object-cover" loading="lazy" />
              ) : null}
              {selectedBg === bg.id && <div className="absolute inset-0 bg-teal-400/20 flex items-center justify-center"><Check className="w-4 h-4 text-teal-400" /></div>}
              <span className="absolute bottom-0 inset-x-0 bg-black/60 text-[8px] text-white text-center py-0.5 truncate">{bg.label}</span>
            </button>
          ))}
        </div>

        {/* Custom upload */}
        <div className="flex gap-2">
          <label className="flex-1 cursor-pointer" data-testid="custom-bg-upload">
            <div className="flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg border border-dashed border-slate-600 text-slate-400 hover:text-white hover:border-slate-500 transition-colors text-xs">
              <Image className="w-3.5 h-3.5" /> Upload Image
            </div>
            <input type="file" accept="image/*" onChange={handleCustomUpload} className="hidden" />
          </label>
        </div>
      </CardContent>
    </Card>
  );
};

export default VirtualBackground;
