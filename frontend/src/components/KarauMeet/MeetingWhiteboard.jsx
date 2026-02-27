import { useState, useRef, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Pen, Eraser, Square, Circle, Type, Undo2, Trash2, Download, Palette, X, Minus } from 'lucide-react';

const COLORS = ['#ffffff', '#20b2aa', '#ef4444', '#22c55e', '#3b82f6', '#f59e0b', '#a855f7', '#ec4899'];
const SIZES = [2, 4, 8, 12];

const API = process.env.REACT_APP_BACKEND_URL;

const MeetingWhiteboard = ({ isOpen, onClose, meetingId }) => {
  const canvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [tool, setTool] = useState('pen');
  const [color, setColor] = useState('#ffffff');
  const [size, setSize] = useState(4);
  const [history, setHistory] = useState([]);
  const [saving, setSaving] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const lastPos = useRef(null);

  // Initialize canvas and load saved state
  useEffect(() => {
    if (!isOpen || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height - 56;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#1a1b2e';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    // Draw grid
    ctx.strokeStyle = '#2e303e';
    ctx.lineWidth = 0.5;
    for (let x = 0; x < canvas.width; x += 40) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
    }
    for (let y = 0; y < canvas.height; y += 40) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
    }
    // Load saved snapshot
    if (meetingId && !loaded) {
      fetch(`${API}/api/karau-meet/ai/whiteboard/${meetingId}`)
        .then(r => r.json())
        .then(d => {
          if (d.snapshot?.snapshot_data) {
            const img = new Image();
            img.onload = () => {
              ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
              setLoaded(true);
            };
            img.src = d.snapshot.snapshot_data;
          } else {
            setLoaded(true);
          }
        })
        .catch(() => setLoaded(true));
    }
  }, [isOpen, meetingId, loaded]);

  const getPos = (e) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;
    return { x: clientX - rect.left, y: clientY - rect.top };
  };

  const startDraw = useCallback((e) => {
    e.preventDefault();
    setIsDrawing(true);
    lastPos.current = getPos(e);
    // Save state for undo
    const canvas = canvasRef.current;
    setHistory(prev => [...prev.slice(-20), canvas.toDataURL()]);
  }, []);

  const draw = useCallback((e) => {
    if (!isDrawing || !canvasRef.current) return;
    e.preventDefault();
    const pos = getPos(e);
    const ctx = canvasRef.current.getContext('2d');
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';

    if (tool === 'eraser') {
      ctx.globalCompositeOperation = 'destination-out';
      ctx.lineWidth = size * 4;
    } else {
      ctx.globalCompositeOperation = 'source-over';
      ctx.strokeStyle = color;
      ctx.lineWidth = size;
    }

    ctx.beginPath();
    ctx.moveTo(lastPos.current.x, lastPos.current.y);
    ctx.lineTo(pos.x, pos.y);
    ctx.stroke();
    lastPos.current = pos;
  }, [isDrawing, tool, color, size]);

  const endDraw = useCallback(() => setIsDrawing(false), []);

  const undo = () => {
    if (history.length === 0) return;
    const img = new Image();
    img.onload = () => {
      const ctx = canvasRef.current.getContext('2d');
      ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
      ctx.drawImage(img, 0, 0);
    };
    img.src = history[history.length - 1];
    setHistory(prev => prev.slice(0, -1));
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    setHistory(prev => [...prev, canvas.toDataURL()]);
    ctx.fillStyle = '#1a1b2e';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = '#2e303e';
    ctx.lineWidth = 0.5;
    for (let x = 0; x < canvas.width; x += 40) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
    }
    for (let y = 0; y < canvas.height; y += 40) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
    }
  };

  const saveToCloud = async () => {
    if (!canvasRef.current || !meetingId) return;
    setSaving(true);
    try {
      const snapshot_data = canvasRef.current.toDataURL('image/png', 0.7);
      await fetch(`${API}/api/karau-meet/ai/whiteboard/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ meeting_id: meetingId, snapshot_data, name: 'Whiteboard' })
      });
    } catch (e) { console.error('Save failed:', e); }
    setSaving(false);
  };

  const download = () => {
    const link = document.createElement('a');
    link.download = 'whiteboard.png';
    link.href = canvasRef.current.toDataURL();
    link.click();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-karau-bg/95 flex flex-col" data-testid="whiteboard">
      {/* Toolbar */}
      <div className="h-14 bg-karau-card border-b border-karau-border flex items-center justify-between px-4">
        <div className="flex items-center gap-2">
          <span className="text-white font-semibold text-sm mr-3">Whiteboard</span>
          {/* Tools */}
          {[{ id: 'pen', icon: Pen, label: 'Pen' }, { id: 'eraser', icon: Eraser, label: 'Eraser' }].map(t => (
            <Button key={t.id} variant={tool === t.id ? 'default' : 'ghost'} size="sm"
              className={`h-8 ${tool === t.id ? 'bg-karau-accent text-karau-bg' : 'text-slate-400'}`}
              onClick={() => setTool(t.id)} data-testid={`tool-${t.id}`}>
              <t.icon className="w-3.5 h-3.5 mr-1" /> {t.label}
            </Button>
          ))}
          <div className="w-px h-6 bg-karau-border mx-1" />
          {/* Colors */}
          <div className="flex gap-1">
            {COLORS.map(c => (
              <button key={c} onClick={() => setColor(c)}
                className={`w-6 h-6 rounded-full border-2 transition-transform ${color === c ? 'border-white scale-110' : 'border-transparent'}`}
                style={{ backgroundColor: c }} data-testid={`color-${c.replace('#', '')}`} />
            ))}
          </div>
          <div className="w-px h-6 bg-karau-border mx-1" />
          {/* Sizes */}
          <div className="flex gap-1">
            {SIZES.map(s => (
              <button key={s} onClick={() => setSize(s)}
                className={`w-7 h-7 rounded flex items-center justify-center ${size === s ? 'bg-karau-surface' : ''}`}>
                <div className="rounded-full bg-white" style={{ width: s + 2, height: s + 2 }} />
              </button>
            ))}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" className="h-8 text-slate-400" onClick={undo} data-testid="undo-btn">
            <Undo2 className="w-3.5 h-3.5 mr-1" /> Undo
          </Button>
          <Button variant="ghost" size="sm" className="h-8 text-slate-400" onClick={clearCanvas} data-testid="clear-btn">
            <Trash2 className="w-3.5 h-3.5 mr-1" /> Clear
          </Button>
          <Button variant="ghost" size="sm" className="h-8 text-slate-400" onClick={saveToCloud} disabled={saving} data-testid="cloud-save-btn">
            {saving ? <Loader2 className="w-3.5 h-3.5 animate-spin mr-1" /> : <Download className="w-3.5 h-3.5 mr-1" />} {saving ? 'Saving...' : 'Save'}
          </Button>
          <Button variant="ghost" size="sm" className="h-8 text-slate-400" onClick={download} data-testid="download-btn">
            <Download className="w-3.5 h-3.5 mr-1" /> Export
          </Button>
          <Button variant="ghost" size="sm" className="h-8 text-slate-400" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </div>
      </div>
      {/* Canvas */}
      <div className="flex-1 relative cursor-crosshair">
        <canvas ref={canvasRef}
          onMouseDown={startDraw} onMouseMove={draw} onMouseUp={endDraw} onMouseLeave={endDraw}
          onTouchStart={startDraw} onTouchMove={draw} onTouchEnd={endDraw}
          className="absolute inset-0 w-full h-full touch-none" />
      </div>
    </div>
  );
};

export default MeetingWhiteboard;
