/**
 * PortalWorkspace — Unified multi-portal workspace
 * After login with a bundle, users see their portals in a dock bar.
 * They can run portals side-by-side, toggle, minimize, and swap main/side.
 *
 * Layout states for side panel:
 *   null     → dock only (main portal full width)
 *   narrow   → 320px column on the left/right
 *   wide     → 440px column
 *   half     → 50/50 split
 */
import { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Video, MessageCircle, Briefcase, Maximize2, Minimize2,
  ArrowLeftRight, X, GripVertical, PanelLeftClose, PanelLeftOpen,
  ChevronUp, ChevronDown
} from 'lucide-react';

const PORTAL_META = {
  karau: { name: 'AI KARAU', icon: Video, color: '#6C5CE7', bgColor: '#6C5CE720', path: '/karau-meet', shortName: 'KARAU' },
  enzi: { name: 'ENZI', icon: MessageCircle, color: '#00CEC9', bgColor: '#00CEC920', path: '/lumi', shortName: 'ENZI' },
  medmatch: { name: 'MedMatch', icon: Briefcase, color: '#00B894', bgColor: '#00B89420', path: '/', shortName: 'MedMatch' },
};

const SIDE_SIZES = { narrow: 320, wide: 440, half: '50%' };
const MIN_PANEL_WIDTH = 280;
const MAX_PANEL_RATIO = 0.65;

/* ═══════════════════════════════════════════
   DragHandle — Draggable divider between side and main
   ═══════════════════════════════════════════ */
const DragHandle = ({ onDrag, onDragEnd }) => {
  const handleRef = useRef(null);
  const [dragging, setDragging] = useState(false);

  useEffect(() => {
    if (!dragging) return;
    const onMove = (e) => { e.preventDefault(); onDrag(e.clientX); };
    const onUp = () => { setDragging(false); onDragEnd(); };
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
    return () => {
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('mouseup', onUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [dragging, onDrag, onDragEnd]);

  // Touch support
  useEffect(() => {
    if (!dragging) return;
    const onTouchMove = (e) => { if (e.touches[0]) onDrag(e.touches[0].clientX); };
    const onTouchEnd = () => { setDragging(false); onDragEnd(); };
    window.addEventListener('touchmove', onTouchMove, { passive: false });
    window.addEventListener('touchend', onTouchEnd);
    return () => {
      window.removeEventListener('touchmove', onTouchMove);
      window.removeEventListener('touchend', onTouchEnd);
    };
  }, [dragging, onDrag, onDragEnd]);

  return (
    <div
      ref={handleRef}
      onMouseDown={(e) => { e.preventDefault(); setDragging(true); }}
      onTouchStart={() => setDragging(true)}
      className={`
        flex-shrink-0 w-[6px] cursor-col-resize flex items-center justify-center
        group relative transition-colors duration-150
        ${dragging ? 'bg-cyan-500/40' : 'bg-transparent hover:bg-slate-600/40'}
      `}
      data-testid="drag-handle"
      title="Drag to resize"
    >
      <div className={`
        w-[3px] h-10 rounded-full transition-all duration-150
        ${dragging ? 'bg-cyan-400 scale-y-125' : 'bg-slate-600 group-hover:bg-slate-400'}
      `} />
    </div>
  );
};

/* ═══════════════════════════════════════════
   Portal Dock — Persistent footer bar
   ═══════════════════════════════════════════ */
const PortalDock = ({ portals, mainPortal, sidePortal, onSelectMain, onToggleSide, onSwap }) => {
  const [expanded, setExpanded] = useState(true);
  const isMobile = typeof window !== 'undefined' && window.innerWidth < 768;

  if (!portals || portals.length <= 1) return null;

  return (
    <div
      className="fixed bottom-0 left-0 right-0 z-[60] flex justify-center pointer-events-none"
      data-testid="portal-dock"
    >
      <div className={`pointer-events-auto transition-all duration-300 ${expanded ? 'mb-3' : 'mb-0'}`}>
        {/* Collapse toggle */}
        <button
          onClick={() => setExpanded(!expanded)}
          className="mx-auto flex items-center justify-center w-8 h-5 rounded-t-lg bg-slate-800/90 border border-b-0 border-slate-600/40 text-slate-400 hover:text-white transition-colors"
          data-testid="dock-collapse-btn"
        >
          {expanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
        </button>

        {expanded && (
          <div className="flex items-center gap-1 px-3 py-2 rounded-2xl bg-slate-900/95 backdrop-blur-xl border border-slate-700/40 shadow-2xl shadow-black/40">
            {portals.map((portalKey) => {
              const meta = PORTAL_META[portalKey];
              if (!meta) return null;
              const Icon = meta.icon;
              const isMain = mainPortal === portalKey;
              const isSide = sidePortal?.portal === portalKey;

              return (
                <div key={portalKey} className="relative group">
                  <button
                    onClick={() => {
                      if (isMain) return; // already main
                      if (isSide) onToggleSide(null); // close side if already open
                      else onToggleSide({ portal: portalKey, size: 'narrow' });
                    }}
                    onDoubleClick={() => {
                      if (!isMain) onSelectMain(portalKey);
                    }}
                    className={`
                      flex items-center gap-2 px-3 py-2 rounded-xl transition-all duration-200
                      ${isMain
                        ? 'bg-white/10 ring-1 ring-white/20'
                        : isSide
                          ? 'bg-white/5 ring-1'
                          : 'hover:bg-white/5'
                      }
                    `}
                    style={isSide ? { ringColor: meta.color + '60' } : {}}
                    data-testid={`dock-${portalKey}`}
                    title={isMain ? `${meta.name} (Main)` : `Click to open ${meta.name} side panel · Double-click to set as main`}
                  >
                    <div
                      className="w-8 h-8 rounded-lg flex items-center justify-center transition-transform group-hover:scale-110"
                      style={{ backgroundColor: meta.bgColor }}
                    >
                      <Icon className="w-4 h-4" style={{ color: meta.color }} />
                    </div>
                    <div className="hidden sm:block">
                      <p className="text-xs font-semibold text-white leading-tight">{meta.shortName}</p>
                      <p className="text-[10px] text-slate-400 leading-tight">
                        {isMain ? 'Main' : isSide ? 'Side' : ''}
                      </p>
                    </div>
                  </button>

                  {/* Active indicator dot */}
                  {isMain && (
                    <div className="absolute -top-0.5 left-1/2 -translate-x-1/2 w-1.5 h-1.5 rounded-full" style={{ backgroundColor: meta.color }} />
                  )}
                </div>
              );
            })}

            {/* Swap button (only when side panel is open) */}
            {sidePortal && (
              <>
                <div className="w-px h-8 bg-slate-700/40 mx-1" />
                <button
                  onClick={onSwap}
                  className="p-2 rounded-lg hover:bg-white/5 text-slate-400 hover:text-white transition-colors"
                  data-testid="dock-swap-btn"
                  title="Swap main and side portals"
                >
                  <ArrowLeftRight className="w-4 h-4" />
                </button>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

/* ═══════════════════════════════════════════
   Side Panel Controls — resize/close bar
   ═══════════════════════════════════════════ */
const SidePanelControls = ({ portalKey, size, customWidth, onResize, onClose, onSwapToMain }) => {
  const meta = PORTAL_META[portalKey];
  if (!meta) return null;
  const Icon = meta.icon;

  const sizes = ['narrow', 'wide', 'half'];
  const nextSize = sizes[(sizes.indexOf(size) + 1) % sizes.length];
  const sizeLabel = customWidth ? `${customWidth}px` : size;

  return (
    <div className="flex items-center justify-between px-3 py-2 border-b border-slate-700/30 bg-slate-900/80 backdrop-blur-sm flex-shrink-0">
      <div className="flex items-center gap-2">
        <div className="w-6 h-6 rounded-md flex items-center justify-center" style={{ backgroundColor: meta.bgColor }}>
          <Icon className="w-3 h-3" style={{ color: meta.color }} />
        </div>
        <span className="text-xs font-semibold text-white">{meta.name}</span>
        <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-slate-400 capitalize">{sizeLabel}</span>
      </div>
      <div className="flex items-center gap-1">
        <button
          onClick={() => onResize(nextSize)}
          className="p-1.5 rounded-md hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
          title={`Resize to ${nextSize}`}
          data-testid="side-panel-resize"
        >
          {size === 'half' ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
        </button>
        <button
          onClick={onSwapToMain}
          className="p-1.5 rounded-md hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
          title="Make main portal"
          data-testid="side-panel-swap"
        >
          <ArrowLeftRight className="w-3.5 h-3.5" />
        </button>
        <button
          onClick={onClose}
          className="p-1.5 rounded-md hover:bg-red-500/20 text-slate-400 hover:text-red-400 transition-colors"
          title="Close panel"
          data-testid="side-panel-close"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};

/* ═══════════════════════════════════════════
   Portal Hub — Initial portal selection view
   Shows all portals in the bundle as cards
   ═══════════════════════════════════════════ */
const PortalHub = ({ portals, onSelectMain }) => {
  const [hovered, setHovered] = useState(null);

  return (
    <div className="min-h-screen bg-[#0a0b14] flex flex-col items-center justify-center p-6" data-testid="portal-hub">
      <style>{`
        .hub-card {
          transition: all 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        .hub-card:hover {
          transform: translateY(-8px) scale(1.03);
        }
      `}</style>

      <div className="text-center mb-10">
        <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2" style={{ fontFamily: "'Manrope', sans-serif" }}>
          Your Workspace
        </h1>
        <p className="text-sm sm:text-base text-slate-400">
          Select a portal to start. You can run others side-by-side from the dock below.
        </p>
      </div>

      <div className={`grid gap-5 ${portals.length === 3 ? 'grid-cols-1 sm:grid-cols-3' : portals.length === 2 ? 'grid-cols-1 sm:grid-cols-2' : 'grid-cols-1'} max-w-3xl w-full`}>
        {portals.map((portalKey) => {
          const meta = PORTAL_META[portalKey];
          if (!meta) return null;
          const Icon = meta.icon;
          const isHovered = hovered === portalKey;

          return (
            <button
              key={portalKey}
              onMouseEnter={() => setHovered(portalKey)}
              onMouseLeave={() => setHovered(null)}
              onClick={() => onSelectMain(portalKey)}
              className="hub-card bg-slate-800/50 border border-slate-700/40 rounded-2xl p-8 text-center cursor-pointer hover:border-slate-500/50 active:scale-[0.97]"
              data-testid={`hub-portal-${portalKey}`}
            >
              <div
                className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 transition-all"
                style={{ backgroundColor: meta.bgColor, boxShadow: isHovered ? `0 0 30px ${meta.color}30` : 'none' }}
              >
                <Icon className="w-8 h-8" style={{ color: meta.color }} />
              </div>
              <h3 className="text-lg font-bold text-white mb-1">{meta.name}</h3>
              <p className="text-xs text-slate-400">
                {portalKey === 'karau' && 'Video meetings & webinars'}
                {portalKey === 'enzi' && 'Team messaging & channels'}
                {portalKey === 'medmatch' && 'Job search & career tools'}
              </p>
            </button>
          );
        })}
      </div>

      <p className="text-xs text-slate-500 mt-8">
        Tip: Once you pick a main portal, the others appear in the dock bar for quick side-by-side access.
      </p>
    </div>
  );
};

/* ═══════════════════════════════════════════
   PortalWorkspace — Main export
   ═══════════════════════════════════════════ */
const PortalWorkspace = ({ portals: propPortals, children, renderPortal }) => {
  const navigate = useNavigate();
  const location = useLocation();
  
  // Read portals from localStorage directly (reactive to login changes)
  const [portals, setPortals] = useState(() => {
    const cached = localStorage.getItem('portal_access');
    if (cached) {
      try { return JSON.parse(cached); } catch(e) {}
    }
    return propPortals || [];
  });

  // Poll localStorage for portal_access changes (triggered by login)
  useEffect(() => {
    const check = () => {
      const cached = localStorage.getItem('portal_access');
      if (cached) {
        try {
          const parsed = JSON.parse(cached);
          if (JSON.stringify(parsed) !== JSON.stringify(portals)) {
            setPortals(parsed);
          }
        } catch(e) {}
      }
    };
    const interval = setInterval(check, 1000);
    return () => clearInterval(interval);
  }, [portals]);

  // Also update when props change
  useEffect(() => {
    if (propPortals && propPortals.length > 0 && JSON.stringify(propPortals) !== JSON.stringify(portals)) {
      setPortals(propPortals);
    }
  }, [propPortals]);

  // Determine main portal from current URL
  const getMainFromPath = useCallback(() => {
    if (location.pathname.startsWith('/karau-meet')) return 'karau';
    if (location.pathname.startsWith('/lumi')) return 'enzi';
    return 'medmatch';
  }, [location.pathname]);

  const [mainPortal, setMainPortal] = useState(() => {
    const saved = sessionStorage.getItem('workspace_main');
    return saved && portals.includes(saved) ? saved : null;
  });
  const [sidePanel, setSidePanel] = useState(null);
  // Skip hub if user is already on a portal path
  const currentFromPath = getMainFromPath();
  const [showHub, setShowHub] = useState(() => {
    if (sessionStorage.getItem('workspace_main')) return false;
    // If already navigated to a specific portal, don't show hub
    if (location.pathname.startsWith('/karau-meet') || location.pathname.startsWith('/lumi')) return false;
    return true;
  });

  // Sync main portal from URL changes
  useEffect(() => {
    const current = getMainFromPath();
    if (portals.includes(current)) {
      if (!mainPortal || current !== mainPortal) {
        setMainPortal(current);
        sessionStorage.setItem('workspace_main', current);
        setShowHub(false);
      }
    }
  }, [location.pathname, getMainFromPath, portals, mainPortal]);

  const handleSelectMain = useCallback((portalKey) => {
    setMainPortal(portalKey);
    setShowHub(false);
    sessionStorage.setItem('workspace_main', portalKey);
    // Navigate to the portal's path
    const meta = PORTAL_META[portalKey];
    if (meta) navigate(meta.path);
  }, [navigate]);

  const handleToggleSide = useCallback((panelConfig) => {
    if (!panelConfig) {
      setSidePanel(null);
      return;
    }
    // If opening the same portal that's already side, close it
    if (sidePanel?.portal === panelConfig.portal) {
      setSidePanel(null);
      return;
    }
    setSidePanel(panelConfig);
  }, [sidePanel]);

  const handleSwap = useCallback(() => {
    if (!sidePanel) return;
    const oldMain = mainPortal;
    const newMain = sidePanel.portal;
    setMainPortal(newMain);
    setSidePanel({ portal: oldMain, size: sidePanel.size });
    sessionStorage.setItem('workspace_main', newMain);
    const meta = PORTAL_META[newMain];
    if (meta) navigate(meta.path);
  }, [mainPortal, sidePanel, navigate]);

  const handleResizeSide = useCallback((newSize) => {
    setSidePanel(prev => prev ? { ...prev, size: newSize, customWidth: null } : null);
  }, []);

  // Custom drag width state
  const [customDragWidth, setCustomDragWidth] = useState(null);

  const handleDrag = useCallback((clientX) => {
    const maxW = window.innerWidth * MAX_PANEL_RATIO;
    const w = Math.min(Math.max(clientX, MIN_PANEL_WIDTH), maxW);
    setCustomDragWidth(Math.round(w));
  }, []);

  const handleDragEnd = useCallback(() => {
    if (customDragWidth) {
      setSidePanel(prev => prev ? { ...prev, size: 'custom', customWidth: customDragWidth } : null);
    }
  }, [customDragWidth]);

  // Single portal package or no portals — no workspace needed, just pass through
  if (portals.length <= 1) {
    return children;
  }

  // Show portal hub if user hasn't selected a main portal yet and not on a specific portal path
  if (showHub && portals.length > 1) {
    return (
      <>
        <PortalHub portals={portals} onSelectMain={handleSelectMain} />
        <PortalDock
          portals={portals}
          mainPortal={null}
          sidePortal={null}
          onSelectMain={handleSelectMain}
          onToggleSide={() => {}}
          onSwap={() => {}}
        />
      </>
    );
  }

  const sideWidth = sidePanel
    ? (customDragWidth || sidePanel.customWidth || SIDE_SIZES[sidePanel.size] || 320)
    : 0;
  const sideWidthStyle = typeof sideWidth === 'string' ? sideWidth : `${sideWidth}px`;

  const isMobile = typeof window !== 'undefined' && window.innerWidth < 768;

  return (
    <div className="h-screen flex flex-col overflow-hidden" data-testid="portal-workspace">
      {/* Main content area with optional side panel */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Side panel - overlay on mobile, split on desktop */}
        {sidePanel && (
          <div
            className={`
              flex-shrink-0 flex flex-col border-r border-slate-700/30 bg-[#0c0d1a] overflow-hidden
              ${isMobile ? 'absolute inset-0 z-30' : ''}
              ${customDragWidth ? '' : 'transition-all duration-300'}
            `}
            style={isMobile ? {} : { width: sideWidthStyle }}
            data-testid="side-panel"
          >
            <SidePanelControls
              portalKey={sidePanel.portal}
              size={sidePanel.size}
              customWidth={sidePanel.customWidth || customDragWidth}
              onResize={handleResizeSide}
              onClose={() => { setSidePanel(null); setCustomDragWidth(null); }}
              onSwapToMain={() => handleSwap()}
            />
            <div className="flex-1 overflow-auto">
              {renderPortal(sidePanel.portal, true)}
            </div>
          </div>
        )}

        {/* Drag handle (between side and main) — hidden on mobile */}
        {sidePanel && !isMobile && (
          <DragHandle onDrag={handleDrag} onDragEnd={handleDragEnd} />
        )}

        {/* Main portal */}
        <div className="flex-1 overflow-auto min-w-0">
          {children}
        </div>
      </div>

      {/* Dock bar (bottom) */}
      <PortalDock
        portals={portals}
        mainPortal={mainPortal || getMainFromPath()}
        sidePortal={sidePanel}
        onSelectMain={handleSelectMain}
        onToggleSide={handleToggleSide}
        onSwap={handleSwap}
      />
    </div>
  );
};

export default PortalWorkspace;
export { PortalHub, PortalDock, PORTAL_META };
