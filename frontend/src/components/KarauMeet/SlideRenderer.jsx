import { useState, useRef, useEffect, useCallback } from 'react';
import {
  ChevronLeft, ChevronRight, Upload, Loader2, Pen,
  Highlighter, Eraser, MousePointer2, X
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

const API = process.env.REACT_APP_BACKEND_URL;

const TOOLS = [
  { id: 'pointer', icon: MousePointer2, label: 'Laser', color: '#ef4444' },
  { id: 'pen', icon: Pen, label: 'Pen', color: '#a855f7' },
  { id: 'highlight', icon: Highlighter, label: 'Highlight', color: '#eab308' },
  { id: 'eraser', icon: Eraser, label: 'Eraser', color: '#64748b' },
];

const SlideRenderer = ({ webinarId, currentSlide, onSlideChange, canDrive, ws }) => {
  const [slides, setSlides] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [activeTool, setActiveTool] = useState('pointer');
  const [isDrawing, setIsDrawing] = useState(false);
  const [laserPos, setLaserPos] = useState(null);

  const canvasRef = useRef(null);
  const overlayRef = useRef(null);
  const containerRef = useRef(null);
  const fileInputRef = useRef(null);
  const drawingsRef = useRef([]);

  useEffect(() => { fetchSlides(); }, [webinarId]);

  const fetchSlides = async () => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/webinar/${webinarId}/presentation/slides`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setSlides(data);
      }
    } catch {}
    setLoading(false);
  };

  // Load slide image
  useEffect(() => {
    if (!slides || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const token = localStorage.getItem('token');

    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => {
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      ctx.drawImage(img, 0, 0);
    };
    img.src = `${API}/api/karau/webinar/${webinarId}/presentation/slide/${currentSlide}?t=${token}`;

    // Clear annotations on slide change
    if (overlayRef.current) {
      const octx = overlayRef.current.getContext('2d');
      octx.clearRect(0, 0, overlayRef.current.width, overlayRef.current.height);
    }
    drawingsRef.current = [];
  }, [slides, currentSlide, webinarId]);

  // Resize overlay to match canvas
  useEffect(() => {
    if (canvasRef.current && overlayRef.current) {
      overlayRef.current.width = canvasRef.current.width;
      overlayRef.current.height = canvasRef.current.height;
    }
  }, [slides, currentSlide]);

  const getCanvasPos = (e) => {
    const rect = overlayRef.current.getBoundingClientRect();
    const scaleX = overlayRef.current.width / rect.width;
    const scaleY = overlayRef.current.height / rect.height;
    return {
      x: (e.clientX - rect.left) * scaleX,
      y: (e.clientY - rect.top) * scaleY
    };
  };

  const handleMouseDown = (e) => {
    if (activeTool === 'pointer') return;
    setIsDrawing(true);
    const pos = getCanvasPos(e);
    const ctx = overlayRef.current.getContext('2d');
    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y);

    if (activeTool === 'eraser') {
      ctx.globalCompositeOperation = 'destination-out';
      ctx.lineWidth = 30;
    } else {
      ctx.globalCompositeOperation = 'source-over';
      ctx.strokeStyle = activeTool === 'highlight' ? 'rgba(234,179,8,0.3)' : '#a855f7';
      ctx.lineWidth = activeTool === 'highlight' ? 20 : 3;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
    }
  };

  const handleMouseMove = (e) => {
    const pos = getCanvasPos(e);

    if (activeTool === 'pointer') {
      setLaserPos(pos);
      // Broadcast laser position
      if (ws?.current?.readyState === WebSocket.OPEN) {
        ws.current.send(JSON.stringify({ type: 'laser_pointer', x: pos.x, y: pos.y }));
      }
      return;
    }

    if (!isDrawing) return;
    const ctx = overlayRef.current.getContext('2d');
    ctx.lineTo(pos.x, pos.y);
    ctx.stroke();
  };

  const handleMouseUp = () => {
    setIsDrawing(false);
    if (overlayRef.current) {
      const ctx = overlayRef.current.getContext('2d');
      ctx.globalCompositeOperation = 'source-over';
    }
  };

  const handleMouseLeave = () => {
    setLaserPos(null);
    setIsDrawing(false);
  };

  const clearAnnotations = () => {
    if (overlayRef.current) {
      const ctx = overlayRef.current.getContext('2d');
      ctx.clearRect(0, 0, overlayRef.current.width, overlayRef.current.height);
    }
  };

  const uploadPresentation = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);

    const token = localStorage.getItem('token');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API}/api/karau/webinar/${webinarId}/presentation/upload`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });
      if (res.ok) {
        const data = await res.json();
        fetchSlides();
        if (onSlideChange) onSlideChange(0);
      }
    } catch (err) { console.error('Upload error:', err); }
    setUploading(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full bg-karau-card/40 rounded-xl">
        <Loader2 className="w-5 h-5 text-purple-400 animate-spin" />
      </div>
    );
  }

  if (!slides) {
    return (
      <div className="flex flex-col items-center justify-center h-full bg-karau-card/40 rounded-xl border border-dashed border-white/10 p-6">
        <Upload className="w-8 h-8 text-slate-500 mb-2" />
        <p className="text-xs text-slate-400 mb-3">No presentation uploaded</p>
        {canDrive && (
          <>
            <Button size="sm" onClick={() => fileInputRef.current?.click()}
              className="bg-purple-500/80 hover:bg-purple-400 rounded-lg text-[11px]" data-testid="upload-pres-btn">
              <Upload className="w-3 h-3 mr-1" />{uploading ? 'Uploading...' : 'Upload PDF/PPTX'}
            </Button>
            <input ref={fileInputRef} type="file" accept=".pdf,.pptx,.ppt" onChange={uploadPresentation} className="hidden" />
          </>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full" ref={containerRef} data-testid="slide-renderer">
      {/* Slide canvas area */}
      <div className="flex-1 relative bg-karau-card/20 rounded-xl overflow-hidden flex items-center justify-center"
        onMouseDown={canDrive ? handleMouseDown : undefined}
        onMouseMove={canDrive ? handleMouseMove : undefined}
        onMouseUp={canDrive ? handleMouseUp : undefined}
        onMouseLeave={canDrive ? handleMouseLeave : undefined}>
        <canvas ref={canvasRef} className="max-w-full max-h-full object-contain" data-testid="slide-canvas" />
        <canvas ref={overlayRef} className="absolute top-0 left-0 max-w-full max-h-full object-contain pointer-events-none" style={{ mixBlendMode: 'normal' }} />

        {/* Laser pointer */}
        {laserPos && activeTool === 'pointer' && (
          <div className="absolute pointer-events-none animate-pulse"
            style={{
              left: `${(laserPos.x / (canvasRef.current?.width || 1)) * 100}%`,
              top: `${(laserPos.y / (canvasRef.current?.height || 1)) * 100}%`,
              width: 12, height: 12, borderRadius: '50%',
              background: 'radial-gradient(circle, #ef4444 0%, transparent 70%)',
              boxShadow: '0 0 12px 4px rgba(239,68,68,0.5)',
              transform: 'translate(-50%, -50%)'
            }} />
        )}

        {/* Slide counter */}
        <div className="absolute bottom-2 right-2 bg-black/60 backdrop-blur-sm rounded-lg px-2 py-0.5">
          <span className="text-[9px] text-white">{currentSlide + 1} / {slides.total_slides}</span>
        </div>
      </div>

      {/* Toolbar */}
      {canDrive && (
        <div className="flex items-center justify-between mt-1.5 px-1" data-testid="slide-toolbar">
          <div className="flex items-center gap-1">
            <Button variant="ghost" size="sm" onClick={() => onSlideChange(Math.max(0, currentSlide - 1))}
              disabled={currentSlide === 0} className="h-7 w-7 p-0 text-slate-300 hover:text-white" data-testid="slide-prev-btn">
              <ChevronLeft className="w-4 h-4" />
            </Button>
            <span className="text-[10px] text-slate-400 min-w-[60px] text-center">Slide {currentSlide + 1}</span>
            <Button variant="ghost" size="sm" onClick={() => onSlideChange(Math.min(slides.total_slides - 1, currentSlide + 1))}
              disabled={currentSlide >= slides.total_slides - 1} className="h-7 w-7 p-0 text-slate-300 hover:text-white" data-testid="slide-next-btn">
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
          <div className="flex items-center gap-0.5">
            {TOOLS.map(tool => (
              <Button key={tool.id} variant="ghost" size="sm" onClick={() => setActiveTool(tool.id)}
                className={`h-7 w-7 p-0 rounded-lg ${activeTool === tool.id ? 'bg-white/15 text-white' : 'text-slate-400 hover:text-white'}`}
                data-testid={`tool-${tool.id}`} title={tool.label}>
                <tool.icon className="w-3.5 h-3.5" style={activeTool === tool.id ? { color: tool.color } : {}} />
              </Button>
            ))}
            <Button variant="ghost" size="sm" onClick={clearAnnotations}
              className="h-7 w-7 p-0 text-slate-400 hover:text-red-400" data-testid="clear-annotations" title="Clear all">
              <X className="w-3.5 h-3.5" />
            </Button>
          </div>
          <Button size="sm" variant="ghost" onClick={() => fileInputRef.current?.click()}
            className="h-7 px-2 text-[9px] text-slate-400 hover:text-white" data-testid="replace-pres-btn">
            <Upload className="w-3 h-3 mr-0.5" />Replace
            <input ref={fileInputRef} type="file" accept=".pdf,.pptx,.ppt" onChange={uploadPresentation} className="hidden" />
          </Button>
        </div>
      )}
    </div>
  );
};

export default SlideRenderer;
