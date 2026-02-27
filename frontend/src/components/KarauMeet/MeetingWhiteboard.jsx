import { useState, useRef, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Pen, Eraser, Square, Circle, Type, Undo2, Trash2, Download, Palette, X, Minus, Loader2, Users, Wifi } from 'lucide-react';

const COLORS = ['#ffffff', '#20b2aa', '#ef4444', '#22c55e', '#3b82f6', '#f59e0b', '#a855f7', '#ec4899'];
const SIZES = [2, 4, 8, 12];
const CURSOR_COLORS = ['#20b2aa', '#ef4444', '#3b82f6', '#f59e0b', '#a855f7', '#ec4899', '#22c55e', '#06b6d4'];

const API = process.env.REACT_APP_BACKEND_URL;
const WS_URL = API.replace('https://', 'wss://').replace('http://', 'ws://');

const MeetingWhiteboard = ({ isOpen, onClose, meetingId, userId, userName }) => {
  const canvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [tool, setTool] = useState('pen');
  const [color, setColor] = useState('#ffffff');
  const [size, setSize] = useState(4);
  const [history, setHistory] = useState([]);
  const [saving, setSaving] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const [remoteCursors, setRemoteCursors] = useState({});
  const [connected, setConnected] = useState(false);
  const [peerCount, setPeerCount] = useState(0);
  const lastPos = useRef(null);
  const wsRef = useRef(null);
  const cursorTimeouts = useRef({});

  // WebSocket connection for real-time collaboration
  useEffect(() => {
    if (!isOpen || !meetingId) return;

    const wsUrl = `${WS_URL}/api/karau-meet/ws/${meetingId}?user_id=${userId || 'wb-' + Date.now()}&user_name=${encodeURIComponent(userName || 'User')}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);

        if (msg.type === 'whiteboard_stroke' && msg.stroke) {
          // Replay remote stroke on local canvas
          replayStroke(msg.stroke);
        } else if (msg.type === 'whiteboard_cursor') {
          // Update remote cursor position
          setRemoteCursors(prev => ({
            ...prev,
            [msg.from_user]: { x: msg.x, y: msg.y, name: msg.from_name, color: msg.color }
          }));
          // Auto-hide cursor after 3s of inactivity
          if (cursorTimeouts.current[msg.from_user]) clearTimeout(cursorTimeouts.current[msg.from_user]);
          cursorTimeouts.current[msg.from_user] = setTimeout(() => {
            setRemoteCursors(prev => { const n = { ...prev }; delete n[msg.from_user]; return n; });
          }, 3000);
        } else if (msg.type === 'whiteboard_clear') {
          clearCanvasLocal();
        } else if (msg.type === 'participant_list') {
          setPeerCount((msg.participants || []).length);
        }
      } catch {}
    };

    ws.onclose = () => setConnected(false);
    ws.onerror = () => setConnected(false);

    return () => {
      ws.close();
      wsRef.current = null;
      Object.values(cursorTimeouts.current).forEach(clearTimeout);
    };
  }, [isOpen, meetingId, userId, userName]);

  const sendWs = useCallback((data) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  const replayStroke = useCallback((stroke) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';

    if (stroke.tool === 'eraser') {
      ctx.globalCompositeOperation = 'destination-out';
      ctx.lineWidth = stroke.size * 4;
    } else {
      ctx.globalCompositeOperation = 'source-over';
      ctx.strokeStyle = stroke.color;
      ctx.lineWidth = stroke.size;
    }

    ctx.beginPath();
    ctx.moveTo(stroke.x1, stroke.y1);
    ctx.lineTo(stroke.x2, stroke.y2);
    ctx.stroke();
  }, []);

  // Initialize canvas and load saved state
  useEffect(() => {
    if (!isOpen || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height - 56;
    drawGrid(canvas);
    // Load saved snapshot
    if (meetingId && !loaded) {
      fetch(`${API}/api/karau-meet/ai/whiteboard/${meetingId}`)
        .then(r => r.json())
        .then(d => {
          if (d.snapshot?.snapshot_data) {
            const img = new Image();
            img.onload = () => {
              const ctx = canvas.getContext('2d');
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

  const drawGrid = (canvas) => {
    const ctx = canvas.getContext('2d');
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

    // Broadcast stroke to peers
    sendWs({
      type: 'whiteboard_stroke',
      stroke: { x1: lastPos.current.x, y1: lastPos.current.y, x2: pos.x, y2: pos.y, color, size, tool }
    });

    lastPos.current = pos;
  }, [isDrawing, tool, color, size, sendWs]);

  const handleMouseMove = useCallback((e) => {
    draw(e);
    // Broadcast cursor position (throttled via natural event rate)
    if (!isDrawing) {
      const pos = getPos(e);
      sendWs({ type: 'whiteboard_cursor', x: pos.x, y: pos.y, color });
    }
  }, [draw, isDrawing, sendWs, color]);

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

  const clearCanvasLocal = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    drawGrid(canvas);
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    setHistory(prev => [...prev, canvas.toDataURL()]);
    clearCanvasLocal();
    sendWs({ type: 'whiteboard_clear' });
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

  const downloadCanvas = () => {
    const link = document.createElement('a');
    link.download = 'whiteboard.png';
    link.href = canvasRef.current.toDataURL();
    link.click();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-karau-bg/95 flex flex-col" data-testid="whiteboard">
      {/* Toolbar */}
      <div className="h-14 bg-karau-card border-b border-karau-border flex items-center justify-between px-2 md:px-4 overflow-x-auto">
        <div className="flex items-center gap-1 md:gap-2 shrink-0">
          <span className="text-white font-semibold text-sm mr-2 hidden md:inline">Whiteboard</span>
          {/* Connection indicator */}
          <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-[10px] ${connected ? 'bg-emerald-500/15 text-emerald-400' : 'bg-slate-600/30 text-slate-400'}`} data-testid="collab-status">
            <Wifi className="w-3 h-3" />
            <span className="hidden sm:inline">{connected ? `Live` : 'Offline'}</span>
            {peerCount > 1 && <span className="flex items-center gap-0.5"><Users className="w-2.5 h-2.5" />{peerCount}</span>}
          </div>
          <div className="w-px h-6 bg-karau-border mx-1" />
          {/* Tools */}
          {[{ id: 'pen', icon: Pen, label: 'Pen' }, { id: 'eraser', icon: Eraser, label: 'Eraser' }].map(t => (
            <Button key={t.id} variant={tool === t.id ? 'default' : 'ghost'} size="sm"
              className={`h-8 ${tool === t.id ? 'bg-karau-accent text-karau-bg' : 'text-slate-400'}`}
              onClick={() => setTool(t.id)} data-testid={`tool-${t.id}`}>
              <t.icon className="w-3.5 h-3.5 mr-1" /> <span className="hidden sm:inline">{t.label}</span>
            </Button>
          ))}
          <div className="w-px h-6 bg-karau-border mx-1" />
          {/* Colors */}
          <div className="flex gap-1">
            {COLORS.map(c => (
              <button key={c} onClick={() => setColor(c)}
                className={`w-5 h-5 md:w-6 md:h-6 rounded-full border-2 transition-transform ${color === c ? 'border-white scale-110' : 'border-transparent'}`}
                style={{ backgroundColor: c }} data-testid={`color-${c.replace('#', '')}`} />
            ))}
          </div>
          <div className="w-px h-6 bg-karau-border mx-1" />
          {/* Sizes */}
          <div className="flex gap-0.5">
            {SIZES.map(s => (
              <button key={s} onClick={() => setSize(s)}
                className={`w-6 h-6 md:w-7 md:h-7 rounded flex items-center justify-center ${size === s ? 'bg-karau-surface' : ''}`}>
                <div className="rounded-full bg-white" style={{ width: s + 2, height: s + 2 }} />
              </button>
            ))}
          </div>
        </div>
        <div className="flex items-center gap-1 md:gap-2 shrink-0 ml-2">
          <Button variant="ghost" size="sm" className="h-8 text-slate-400" onClick={undo} data-testid="undo-btn">
            <Undo2 className="w-3.5 h-3.5" /><span className="hidden md:inline ml-1">Undo</span>
          </Button>
          <Button variant="ghost" size="sm" className="h-8 text-slate-400" onClick={clearCanvas} data-testid="clear-btn">
            <Trash2 className="w-3.5 h-3.5" /><span className="hidden md:inline ml-1">Clear</span>
          </Button>
          <Button variant="ghost" size="sm" className="h-8 text-slate-400" onClick={saveToCloud} disabled={saving} data-testid="cloud-save-btn">
            {saving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Download className="w-3.5 h-3.5" />}<span className="hidden md:inline ml-1">{saving ? 'Saving...' : 'Save'}</span>
          </Button>
          <Button variant="ghost" size="sm" className="h-8 text-slate-400" onClick={downloadCanvas} data-testid="download-btn">
            <Download className="w-3.5 h-3.5" /><span className="hidden md:inline ml-1">Export</span>
          </Button>
          <Button variant="ghost" size="sm" className="h-8 text-slate-400" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </div>
      </div>
      {/* Canvas */}
      <div className="flex-1 relative cursor-crosshair">
        <canvas ref={canvasRef}
          onMouseDown={startDraw} onMouseMove={handleMouseMove} onMouseUp={endDraw} onMouseLeave={endDraw}
          onTouchStart={startDraw} onTouchMove={draw} onTouchEnd={endDraw}
          className="absolute inset-0 w-full h-full touch-none" />
        {/* Remote Cursors Overlay */}
        {Object.entries(remoteCursors).map(([uid, cur]) => (
          <div key={uid} className="absolute pointer-events-none z-10 transition-all duration-75"
            style={{ left: cur.x, top: cur.y, transform: 'translate(-4px, -4px)' }}>
            <div className="w-3 h-3 rounded-full border-2" style={{ borderColor: cur.color, backgroundColor: cur.color + '40' }} />
            <span className="text-[9px] text-white bg-black/60 px-1 py-0.5 rounded ml-2 whitespace-nowrap absolute top-0 left-3">{cur.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MeetingWhiteboard;
