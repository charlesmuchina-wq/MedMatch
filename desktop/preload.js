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
  
  // Notifications
  showNotification: (title, body) => ipcRenderer.invoke('show-notification', { title, body }),
  
  // Platform check
  isElectron: true,
  isDesktop: true,
  
  // Window controls
  minimize: () => ipcRenderer.send('window-minimize'),
  maximize: () => ipcRenderer.send('window-maximize'),
  close: () => ipcRenderer.send('window-close')
});

// Inject desktop indicator CSS
window.addEventListener('DOMContentLoaded', () => {
  // Add desktop class to body
  document.body.classList.add('desktop-app');
  
  // Create desktop indicator badge
  const badge = document.createElement('div');
  badge.id = 'desktop-badge';
  badge.innerHTML = '🖥️ Desktop';
  badge.style.cssText = `
    position: fixed;
    bottom: 10px;
    left: 10px;
    background: linear-gradient(135deg, #20b2aa, #1a8a84);
    color: white;
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
    z-index: 9999;
    opacity: 0.8;
    pointer-events: none;
  `;
  document.body.appendChild(badge);
  
  // Auto-hide badge after 5 seconds
  setTimeout(() => {
    badge.style.transition = 'opacity 0.5s';
    badge.style.opacity = '0';
    setTimeout(() => badge.remove(), 500);
  }, 5000);
});
