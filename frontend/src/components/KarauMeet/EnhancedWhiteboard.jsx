import { useState, useRef, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Pencil, Square, Circle, Type, StickyNote, Eraser,
  Undo2, Redo2, Download, Trash2, Palette, Minus, Plus,
  MousePointer, Move
} from 'lucide-react';

const COLORS = ['#a78bfa', '#34d399', '#fbbf24', '#f87171', '#38bdf8', '#fb923c', '#e879f9', '#ffffff'];
const TOOLS = [
  { id: 'select', icon: MousePointer, label: 'Select' },
  { id: 'pen', icon: Pencil, label: 'Pen' },
  { id: 'rect', icon: Square, label: 'Rectangle' },
  { id: 'circle', icon: Circle, label: 'Circle' },
  { id: 'text', icon: Type, label: 'Text' },
  { id: 'sticky', icon: StickyNote, label: 'Sticky Note' },
  { id: 'eraser', icon: Eraser, label: 'Eraser' },
];

const EnhancedWhiteboard = ({ meetingId, onClose }) => {
  const canvasRef = useRef(null);
  const [tool, setTool] = useState('pen');
  const [color, setColor] = useState('#a78bfa');
  const [brushSize, setBrushSize] = useState(3);
  const [isDrawing, setIsDrawing] = useState(false);
  const [elements, setElements] = useState([]);
  const [undoStack, setUndoStack] = useState([]);
  const [panOffset, setPanOffset] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [stickyNotes, setStickyNotes] = useState([]);
  const [textInputPos, setTextInputPos] = useState(null);
  const lastPosRef = useRef(null);

  const getCanvasPos = useCallback((e) => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };
    const rect = canvas.getBoundingClientRect();
    return {
      x: (e.clientX - rect.left - panOffset.x) / zoom,
      y: (e.clientY - rect.top - panOffset.y) / zoom
    };
  }, [panOffset, zoom]);

  const redraw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.save();
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // Grid
    ctx.strokeStyle = 'rgba(255,255,255,0.03)';
    ctx.lineWidth = 1;
    const gridSize = 40 * zoom;
    for (let x = panOffset.x % gridSize; x < canvas.width; x += gridSize) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
    }
    for (let y = panOffset.y % gridSize; y < canvas.height; y += gridSize) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
    }
    ctx.restore();

    ctx.save();
    ctx.translate(panOffset.x, panOffset.y);
    ctx.scale(zoom, zoom);
    elements.forEach(el => {
      ctx.strokeStyle = el.color;
      ctx.lineWidth = el.size || 3;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      if (el.type === 'path') {
        ctx.beginPath();
        el.points.forEach((p, i) => { i === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y); });
        ctx.stroke();
      } else if (el.type === 'rect') {
        ctx.strokeRect(el.x, el.y, el.w, el.h);
      } else if (el.type === 'circle') {
        ctx.beginPath();
        ctx.arc(el.x + el.w / 2, el.y + el.h / 2, Math.abs(el.w) / 2, 0, Math.PI * 2);
        ctx.stroke();
      } else if (el.type === 'text') {
        ctx.fillStyle = el.color;
        ctx.font = `${el.size * 4}px sans-serif`;
        ctx.fillText(el.text, el.x, el.y);
      }
    });
    ctx.restore();
  }, [elements, panOffset, zoom]);

  useEffect(() => { redraw(); }, [redraw]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const resize = () => { canvas.width = canvas.parentElement.clientWidth; canvas.height = canvas.parentElement.clientHeight; redraw(); };
    resize();
    window.addEventListener('resize', resize);
    return () => window.removeEventListener('resize', resize);
  }, [redraw]);

  const handleMouseDown = (e) => {
    const pos = getCanvasPos(e);
    if (tool === 'pen' || tool === 'eraser') {
      setIsDrawing(true);
      const newPath = { type: 'path', color: tool === 'eraser' ? '#0f172a' : color, size: tool === 'eraser' ? brushSize * 4 : brushSize, points: [pos] };
      setElements(prev => [...prev, newPath]);
    } else if (tool === 'rect' || tool === 'circle') {
      setIsDrawing(true);
      setElements(prev => [...prev, { type: tool === 'rect' ? 'rect' : 'circle', color, size: brushSize, x: pos.x, y: pos.y, w: 0, h: 0 }]);
    } else if (tool === 'text') {
      setTextInputPos(pos);
    } else if (tool === 'sticky') {
      setStickyNotes(prev => [...prev, { id: Date.now(), x: pos.x, y: pos.y, text: 'New note...', color: '#fbbf24' }]);
    }
    lastPosRef.current = pos;
  };

  const handleMouseMove = (e) => {
    if (!isDrawing) return;
    const pos = getCanvasPos(e);
    if (tool === 'pen' || tool === 'eraser') {
      setElements(prev => {
        const copy = [...prev];
        copy[copy.length - 1].points.push(pos);
        return copy;
      });
    } else if (tool === 'rect' || tool === 'circle') {
      setElements(prev => {
        const copy = [...prev];
        const el = copy[copy.length - 1];
        el.w = pos.x - el.x;
        el.h = pos.y - el.y;
        return copy;
      });
    }
  };

  const handleMouseUp = () => { setIsDrawing(false); };

  const handleTextInput = (e) => {
    if (e.key === 'Enter' && textInputPos) {
      setElements(prev => [...prev, { type: 'text', color, size: brushSize, x: textInputPos.x, y: textInputPos.y, text: e.target.value }]);
      setTextInputPos(null);
    }
  };

  const undo = () => {
    if (elements.length === 0) return;
    setUndoStack(prev => [...prev, elements[elements.length - 1]]);
    setElements(prev => prev.slice(0, -1));
  };

  const redo = () => {
    if (undoStack.length === 0) return;
    setElements(prev => [...prev, undoStack[undoStack.length - 1]]);
    setUndoStack(prev => prev.slice(0, -1));
  };

  const exportCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const link = document.createElement('a');
    link.download = `whiteboard-${meetingId || 'export'}.png`;
    link.href = canvas.toDataURL();
    link.click();
  };

  return (
    <div className="flex flex-col h-full bg-[#0f172a] rounded-xl overflow-hidden border border-white/5" data-testid="enhanced-whiteboard">
      {/* Toolbar */}
      <div className="flex items-center gap-1 px-2 py-1.5 bg-karau-card/60 border-b border-white/5">
        {TOOLS.map(t => (
          <Button key={t.id} size="sm" variant="ghost" onClick={() => setTool(t.id)}
            className={`h-7 w-7 p-0 rounded-lg ${tool === t.id ? 'bg-violet-500/20 text-violet-400' : 'text-slate-400 hover:text-white'}`}
            data-testid={`wb-tool-${t.id}`} title={t.label}>
            <t.icon className="w-3.5 h-3.5" />
          </Button>
        ))}
        <div className="w-px h-5 bg-white/10 mx-1" />
        {COLORS.map(c => (
          <button key={c} onClick={() => setColor(c)}
            className={`w-4 h-4 rounded-full border-2 transition-transform ${color === c ? 'border-white scale-125' : 'border-transparent'}`}
            style={{ backgroundColor: c }} data-testid={`wb-color-${c.slice(1)}`} />
        ))}
        <div className="w-px h-5 bg-white/10 mx-1" />
        <Button size="sm" variant="ghost" onClick={() => setBrushSize(Math.max(1, brushSize - 1))} className="h-6 w-6 p-0 text-slate-400"><Minus className="w-3 h-3" /></Button>
        <span className="text-[9px] text-slate-400 w-4 text-center">{brushSize}</span>
        <Button size="sm" variant="ghost" onClick={() => setBrushSize(Math.min(20, brushSize + 1))} className="h-6 w-6 p-0 text-slate-400"><Plus className="w-3 h-3" /></Button>
        <div className="w-px h-5 bg-white/10 mx-1" />
        <Button size="sm" variant="ghost" onClick={undo} className="h-7 w-7 p-0 text-slate-400" data-testid="wb-undo"><Undo2 className="w-3 h-3" /></Button>
        <Button size="sm" variant="ghost" onClick={redo} className="h-7 w-7 p-0 text-slate-400" data-testid="wb-redo"><Redo2 className="w-3 h-3" /></Button>
        <Button size="sm" variant="ghost" onClick={exportCanvas} className="h-7 w-7 p-0 text-slate-400" data-testid="wb-export"><Download className="w-3 h-3" /></Button>
        <Button size="sm" variant="ghost" onClick={() => { setElements([]); setStickyNotes([]); }} className="h-7 w-7 p-0 text-red-400" data-testid="wb-clear"><Trash2 className="w-3 h-3" /></Button>
        <div className="flex-1" />
        <Badge className="text-[7px] bg-violet-500/10 text-violet-400 border-violet-500/20">
          {elements.length} objects | {zoom.toFixed(1)}x
        </Badge>
      </div>

      {/* Canvas */}
      <div className="flex-1 relative cursor-crosshair overflow-hidden">
        <canvas ref={canvasRef} onMouseDown={handleMouseDown} onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp} onMouseLeave={handleMouseUp}
          onWheel={(e) => { e.preventDefault(); setZoom(z => Math.max(0.25, Math.min(4, z + (e.deltaY > 0 ? -0.1 : 0.1)))); }}
          className="w-full h-full" data-testid="wb-canvas" />
        {/* Text input */}
        {textInputPos && (
          <input autoFocus type="text" onKeyDown={handleTextInput} onBlur={() => setTextInputPos(null)}
            className="absolute bg-black/80 border border-violet-500/30 text-white text-xs px-1 py-0.5 rounded"
            style={{ left: textInputPos.x * zoom + panOffset.x, top: textInputPos.y * zoom + panOffset.y }}
            data-testid="wb-text-input" />
        )}
        {/* Sticky Notes */}
        {stickyNotes.map(note => (
          <div key={note.id} className="absolute w-28 p-1.5 rounded shadow-lg text-[9px] text-karau-bg cursor-move"
            style={{ left: note.x * zoom + panOffset.x, top: note.y * zoom + panOffset.y, backgroundColor: note.color }}
            data-testid={`sticky-${note.id}`}>
            <textarea className="w-full bg-transparent text-[9px] text-karau-bg resize-none outline-none"
              defaultValue={note.text} rows={3}
              onChange={e => setStickyNotes(prev => prev.map(n => n.id === note.id ? { ...n, text: e.target.value } : n))} />
          </div>
        ))}
      </div>
    </div>
  );
};

export default EnhancedWhiteboard;
