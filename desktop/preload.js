/**
 * MedMatch Desktop - Preload Script
 * Exposes safe APIs to the renderer process
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods to the renderer
contextBridge.exposeInMainWorld('electronAPI', {
  // App info
  getVersion: () => ipcRenderer.invoke('get-version'),
  getPlatform: () => ipcRenderer.invoke('get-platform'),
  isOnline: () => ipcRenderer.invoke('is-online'),
  
  // Settings
  getSettings: () => ipcRenderer.invoke('get-settings'),
  setSetting: (key, value) => ipcRenderer.invoke('set-setting', { key, value }),
  
  // Notifications
  showNotification: (title, body) => ipcRenderer.invoke('show-notification', { title, body }),
  
  // Updates
  checkForUpdates: () => ipcRenderer.invoke('check-for-updates'),
  
  // Platform detection
  isElectron: true,
  isDesktop: true,
  isMac: process.platform === 'darwin',
  isWindows: process.platform === 'win32',
  isLinux: process.platform === 'linux',
  
  // Window controls
  minimize: () => ipcRenderer.send('window-minimize'),
  maximize: () => ipcRenderer.send('window-maximize'),
  close: () => ipcRenderer.send('window-close'),
  
  // Event listeners
  onUpdateAvailable: (callback) => ipcRenderer.on('update-available', callback),
  onUpdateDownloaded: (callback) => ipcRenderer.on('update-downloaded', callback),
  onOnlineStatusChange: (callback) => ipcRenderer.on('online-status-change', callback)
});

// Desktop-specific UI enhancements
window.addEventListener('DOMContentLoaded', () => {
  // Add desktop class to body for CSS targeting
  document.body.classList.add('desktop-app');
  document.body.classList.add(`platform-${process.platform}`);
  
  // Create desktop indicator badge (temporary)
  const badge = document.createElement('div');
  badge.id = 'desktop-badge';
  badge.innerHTML = `
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
      <line x1="8" y1="21" x2="16" y2="21"></line>
      <line x1="12" y1="17" x2="12" y2="21"></line>
    </svg>
    <span>Desktop</span>
  `;
  badge.style.cssText = `
    position: fixed;
    bottom: 12px;
    left: 12px;
    background: linear-gradient(135deg, #20b2aa, #1a8a84);
    color: white;
    padding: 6px 12px;
    border-radius: 16px;
    font-size: 11px;
    font-weight: 600;
    z-index: 9999;
    display: flex;
    align-items: center;
    gap: 6px;
    box-shadow: 0 2px 8px rgba(32, 178, 170, 0.3);
    opacity: 0.9;
    pointer-events: none;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  `;
  document.body.appendChild(badge);
  
  // Auto-hide badge after 5 seconds
  setTimeout(() => {
    badge.style.transition = 'opacity 0.5s ease-out';
    badge.style.opacity = '0';
    setTimeout(() => badge.remove(), 500);
  }, 5000);

  // Add custom CSS for desktop-specific styling
  const style = document.createElement('style');
  style.textContent = `
    /* Desktop-specific scrollbar styling */
    .desktop-app ::-webkit-scrollbar {
      width: 10px;
      height: 10px;
    }
    .desktop-app ::-webkit-scrollbar-track {
      background: rgba(255, 255, 255, 0.05);
    }
    .desktop-app ::-webkit-scrollbar-thumb {
      background: rgba(255, 255, 255, 0.2);
      border-radius: 5px;
    }
    .desktop-app ::-webkit-scrollbar-thumb:hover {
      background: rgba(255, 255, 255, 0.3);
    }
    
    /* Hide mobile-only elements on desktop */
    .desktop-app .mobile-only {
      display: none !important;
    }
    
    /* Show desktop-only elements */
    .desktop-app .desktop-only {
      display: block !important;
    }
    
    /* Adjust layout for desktop */
    .desktop-app .pwa-install-banner {
      display: none !important;
    }
    
    /* Custom title bar area for macOS */
    .platform-darwin .app-header {
      -webkit-app-region: drag;
    }
    .platform-darwin .app-header button,
    .platform-darwin .app-header a,
    .platform-darwin .app-header input {
      -webkit-app-region: no-drag;
    }
  `;
  document.head.appendChild(style);

  // Keyboard shortcut enhancements
  document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Shift + D for dev tools
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
      // This will be handled by main process
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
      const modal = document.querySelector('[role="dialog"]:not([hidden])');
      if (modal) {
        const closeButton = modal.querySelector('[data-close], .close-button, [aria-label="Close"]');
        if (closeButton) closeButton.click();
      }
    }
  });

  // Detect theme preference changes
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    document.body.classList.toggle('system-dark', e.matches);
    document.body.classList.toggle('system-light', !e.matches);
  });

  // Set initial theme class
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  document.body.classList.add(prefersDark ? 'system-dark' : 'system-light');

  console.log('🖥️ MedMatch Desktop loaded');
  console.log(`Platform: ${process.platform}`);
  console.log('Desktop features enabled');
});
