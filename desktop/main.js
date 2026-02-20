/**
 * MedMatch Desktop App - Main Process
 * Electron wrapper for the MedMatch web application
 * Features: System tray, notifications, auto-launch, offline detection, auto-update
 */

const { app, BrowserWindow, Menu, Tray, shell, ipcMain, Notification, nativeImage, dialog, session } = require('electron');
const path = require('path');
const { autoUpdater } = require('electron-updater');
const log = require('electron-log');
const Store = require('electron-store');

// Configure logging
log.transports.file.level = 'info';
autoUpdater.logger = log;
autoUpdater.autoDownload = true;
autoUpdater.autoInstallOnAppQuit = true;

// Persistent settings store
const store = new Store({
  defaults: {
    launchAtStartup: false,
    minimizeToTray: true,
    checkUpdatesAutomatically: true,
    lastNotificationTime: 0,
    windowBounds: { width: 1400, height: 900 }
  }
});

// Configuration
const APP_URL = process.env.MEDMATCH_URL || 'https://karau-meet.preview.emergentagent.com';
const isDev = process.env.NODE_ENV === 'development';

let mainWindow = null;
let tray = null;
let isQuitting = false;
let isOnline = true;
let updateAvailable = false;

// ============== Window Management ==============

function createWindow() {
  const bounds = store.get('windowBounds');
  
  mainWindow = new BrowserWindow({
    width: bounds.width,
    height: bounds.height,
    minWidth: 800,
    minHeight: 600,
    title: 'MedMatch - AI Job Search',
    icon: path.join(__dirname, 'assets', 'icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      spellcheck: true,
      webSecurity: true
    },
    show: false,
    backgroundColor: '#1a1a2e',
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    autoHideMenuBar: false,
    frame: true
  });

  // Remember window position
  mainWindow.on('resize', () => {
    const { width, height } = mainWindow.getBounds();
    store.set('windowBounds', { width, height });
  });

  // Load the web app with offline fallback
  loadApp();

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    
    // Check for updates on launch
    if (store.get('checkUpdatesAutomatically') && !isDev) {
      setTimeout(() => autoUpdater.checkForUpdatesAndNotify(), 3000);
    }
  });

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('http') && !url.includes(new URL(APP_URL).hostname)) {
      shell.openExternal(url);
      return { action: 'deny' };
    }
    return { action: 'allow' };
  });

  // Handle navigation errors (offline)
  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
    log.warn(`Failed to load: ${errorDescription}`);
    if (errorCode === -106 || errorCode === -105) { // NAME_NOT_RESOLVED or NAME_RESOLUTION_FAILED
      loadOfflinePage();
    }
  });

  // Handle window close
  mainWindow.on('close', (event) => {
    if (!isQuitting && store.get('minimizeToTray')) {
      event.preventDefault();
      mainWindow.hide();
      showTrayNotification('MedMatch', 'App minimized to system tray. Click the icon to restore.');
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Create application menu
  createMenu();
}

function loadApp() {
  if (isOnline) {
    mainWindow.loadURL(APP_URL);
  } else {
    loadOfflinePage();
  }
}

function loadOfflinePage() {
  const offlineHTML = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>MedMatch - Offline</title>
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
          color: white;
          display: flex;
          justify-content: center;
          align-items: center;
          height: 100vh;
          margin: 0;
          text-align: center;
        }
        .container {
          max-width: 400px;
          padding: 40px;
        }
        .icon { font-size: 64px; margin-bottom: 20px; }
        h1 { margin: 0 0 10px 0; color: #20b2aa; }
        p { color: #a0a0a0; margin: 10px 0; }
        button {
          background: #20b2aa;
          color: white;
          border: none;
          padding: 12px 24px;
          border-radius: 8px;
          font-size: 16px;
          cursor: pointer;
          margin-top: 20px;
        }
        button:hover { background: #1a8a84; }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="icon">📡</div>
        <h1>You're Offline</h1>
        <p>MedMatch requires an internet connection to search for jobs and access AI features.</p>
        <p>Please check your connection and try again.</p>
        <button onclick="location.reload()">Retry Connection</button>
      </div>
    </body>
    </html>
  `;
  mainWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(offlineHTML)}`);
}

// ============== System Tray ==============

function createTray() {
  const iconPath = path.join(__dirname, 'assets', 'tray-icon.png');
  let trayIcon;
  
  try {
    trayIcon = nativeImage.createFromPath(iconPath);
    if (trayIcon.isEmpty()) {
      // Create a simple colored icon as fallback
      trayIcon = createDefaultIcon();
    }
  } catch (e) {
    trayIcon = createDefaultIcon();
  }

  // Resize for tray (16x16 on most platforms)
  trayIcon = trayIcon.resize({ width: 16, height: 16 });
  
  tray = new Tray(trayIcon);
  tray.setToolTip('MedMatch - AI Job Search');
  updateTrayMenu();

  tray.on('double-click', () => {
    if (mainWindow) {
      mainWindow.show();
      mainWindow.focus();
    }
  });
}

function createDefaultIcon() {
  // Create a simple 16x16 icon programmatically
  const size = 16;
  const canvas = require('electron').nativeImage.createEmpty();
  return canvas;
}

function updateTrayMenu() {
  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Open MedMatch',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.focus();
        }
      }
    },
    { type: 'separator' },
    {
      label: 'Quick Actions',
      submenu: [
        {
          label: '🔍 Search Jobs',
          click: () => navigateTo('/search')
        },
        {
          label: '📄 My Resume',
          click: () => navigateTo('/resume')
        },
        {
          label: '📋 Applications',
          click: () => navigateTo('/applications')
        },
        {
          label: '📅 Interviews',
          click: () => navigateTo('/interview-calendar')
        },
        {
          label: '🤖 AI Assistant',
          click: () => navigateTo('/dashboard')
        }
      ]
    },
    { type: 'separator' },
    {
      label: `Status: ${isOnline ? '🟢 Online' : '🔴 Offline'}`,
      enabled: false
    },
    {
      label: updateAvailable ? '⬇️ Update Available' : '✓ Up to Date',
      enabled: updateAvailable,
      click: () => {
        if (updateAvailable) {
          autoUpdater.quitAndInstall();
        }
      }
    },
    { type: 'separator' },
    {
      label: 'Preferences',
      submenu: [
        {
          label: 'Launch at Startup',
          type: 'checkbox',
          checked: store.get('launchAtStartup'),
          click: (item) => {
            store.set('launchAtStartup', item.checked);
            app.setLoginItemSettings({ openAtLogin: item.checked });
          }
        },
        {
          label: 'Minimize to Tray',
          type: 'checkbox',
          checked: store.get('minimizeToTray'),
          click: (item) => store.set('minimizeToTray', item.checked)
        },
        {
          label: 'Auto-check for Updates',
          type: 'checkbox',
          checked: store.get('checkUpdatesAutomatically'),
          click: (item) => store.set('checkUpdatesAutomatically', item.checked)
        }
      ]
    },
    { type: 'separator' },
    {
      label: 'Check for Updates',
      click: () => {
        autoUpdater.checkForUpdatesAndNotify();
        showNotification('Checking for Updates', 'Looking for new versions...');
      }
    },
    { type: 'separator' },
    {
      label: 'Quit MedMatch',
      click: () => {
        isQuitting = true;
        app.quit();
      }
    }
  ]);

  tray.setContextMenu(contextMenu);
}

function navigateTo(path) {
  if (mainWindow) {
    mainWindow.show();
    mainWindow.loadURL(`${APP_URL}${path}`);
  }
}

function showTrayNotification(title, body) {
  // Rate limit notifications (max once per minute)
  const now = Date.now();
  if (now - store.get('lastNotificationTime') < 60000) return;
  store.set('lastNotificationTime', now);
  
  if (process.platform === 'win32' && tray) {
    tray.displayBalloon({ title, content: body });
  }
}

// ============== Notifications ==============

function showNotification(title, body, onClick) {
  if (!Notification.isSupported()) return;
  
  const notification = new Notification({
    title,
    body,
    icon: path.join(__dirname, 'assets', 'icon.png'),
    silent: false
  });
  
  if (onClick) {
    notification.on('click', onClick);
  }
  
  notification.show();
}

// ============== Application Menu ==============

function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'New Job Search',
          accelerator: 'CmdOrCtrl+N',
          click: () => navigateTo('/search')
        },
        {
          label: 'Upload Resume',
          accelerator: 'CmdOrCtrl+U',
          click: () => navigateTo('/resume')
        },
        { type: 'separator' },
        {
          label: 'Preferences',
          accelerator: 'CmdOrCtrl+,',
          click: () => navigateTo('/settings')
        },
        { type: 'separator' },
        {
          label: 'Quit',
          accelerator: 'CmdOrCtrl+Q',
          click: () => {
            isQuitting = true;
            app.quit();
          }
        }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
        { role: 'selectAll' }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' },
        { type: 'separator' },
        {
          label: 'Toggle Developer Tools',
          accelerator: 'CmdOrCtrl+Shift+I',
          click: () => mainWindow && mainWindow.webContents.toggleDevTools(),
          visible: isDev
        }
      ]
    },
    {
      label: 'Navigate',
      submenu: [
        { label: 'Dashboard', accelerator: 'CmdOrCtrl+1', click: () => navigateTo('/dashboard') },
        { label: 'Job Search', accelerator: 'CmdOrCtrl+2', click: () => navigateTo('/search') },
        { label: 'Applications', accelerator: 'CmdOrCtrl+3', click: () => navigateTo('/applications') },
        { label: 'Interviews', accelerator: 'CmdOrCtrl+4', click: () => navigateTo('/interview-calendar') },
        { label: 'AI Tools', accelerator: 'CmdOrCtrl+5', click: () => navigateTo('/interview-prep') },
        { type: 'separator' },
        { label: 'Back', accelerator: 'Alt+Left', click: () => mainWindow && mainWindow.webContents.goBack() },
        { label: 'Forward', accelerator: 'Alt+Right', click: () => mainWindow && mainWindow.webContents.goForward() }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'Getting Started',
          click: () => shell.openExternal('https://medmatch.com/help')
        },
        {
          label: 'Keyboard Shortcuts',
          accelerator: 'CmdOrCtrl+/',
          click: showShortcutsDialog
        },
        { type: 'separator' },
        {
          label: 'Check for Updates',
          click: () => autoUpdater.checkForUpdatesAndNotify()
        },
        { type: 'separator' },
        {
          label: 'Report Issue',
          click: () => shell.openExternal('https://github.com/medmatch/issues')
        },
        {
          label: 'About MedMatch',
          click: showAboutDialog
        }
      ]
    }
  ];

  // macOS specific menu
  if (process.platform === 'darwin') {
    template.unshift({
      label: app.name,
      submenu: [
        { role: 'about' },
        { type: 'separator' },
        { role: 'services' },
        { type: 'separator' },
        { role: 'hide' },
        { role: 'hideOthers' },
        { role: 'unhide' },
        { type: 'separator' },
        { role: 'quit' }
      ]
    });
  }

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

function showShortcutsDialog() {
  const shortcuts = `
MedMatch Keyboard Shortcuts:

Navigation:
  Ctrl+1  Dashboard
  Ctrl+2  Job Search
  Ctrl+3  Applications
  Ctrl+4  Interviews
  Ctrl+5  AI Tools

Actions:
  Ctrl+N  New Job Search
  Ctrl+U  Upload Resume
  Ctrl+,  Preferences

Window:
  Ctrl+R  Reload
  Ctrl++  Zoom In
  Ctrl+-  Zoom Out
  F11     Full Screen
  Ctrl+Q  Quit
  `;
  
  dialog.showMessageBox(mainWindow, {
    type: 'info',
    title: 'Keyboard Shortcuts',
    message: shortcuts,
    buttons: ['OK']
  });
}

function showAboutDialog() {
  dialog.showMessageBox(mainWindow, {
    type: 'info',
    title: 'About MedMatch',
    message: `MedMatch Desktop v${app.getVersion()}`,
    detail: `AI-Powered Job Search Platform

Features:
• Resume parsing & AI matching
• Multi-source job aggregation
• AI interview preparation
• Voice coaching & video practice
• Real-time transcription
• Interview calendar sync

Platform: ${process.platform} (${process.arch})
Electron: ${process.versions.electron}
Chrome: ${process.versions.chrome}

© 2026 MedMatch. All rights reserved.`
  });
}

// ============== Auto Updater ==============

autoUpdater.on('checking-for-update', () => {
  log.info('Checking for update...');
});

autoUpdater.on('update-available', (info) => {
  log.info('Update available:', info);
  updateAvailable = true;
  updateTrayMenu();
  showNotification(
    'Update Available',
    `Version ${info.version} is available. It will be downloaded automatically.`,
    () => mainWindow && mainWindow.show()
  );
});

autoUpdater.on('update-not-available', () => {
  log.info('Update not available.');
  updateAvailable = false;
});

autoUpdater.on('download-progress', (progressObj) => {
  log.info(`Download progress: ${progressObj.percent.toFixed(1)}%`);
});

autoUpdater.on('update-downloaded', (info) => {
  log.info('Update downloaded');
  showNotification(
    'Update Ready',
    `Version ${info.version} has been downloaded. Restart to install.`,
    () => autoUpdater.quitAndInstall()
  );
  
  dialog.showMessageBox(mainWindow, {
    type: 'info',
    title: 'Update Ready',
    message: 'A new version has been downloaded.',
    detail: `Version ${info.version} is ready to install. Would you like to restart now?`,
    buttons: ['Restart Now', 'Later'],
    defaultId: 0
  }).then(({ response }) => {
    if (response === 0) {
      autoUpdater.quitAndInstall();
    }
  });
});

autoUpdater.on('error', (err) => {
  log.error('Auto-updater error:', err);
});

// ============== Online/Offline Detection ==============

function setupNetworkMonitoring() {
  // Check network status periodically
  setInterval(async () => {
    try {
      const response = await fetch(APP_URL, { method: 'HEAD', timeout: 5000 });
      const wasOffline = !isOnline;
      isOnline = response.ok;
      
      if (wasOffline && isOnline) {
        // Back online - reload the app
        showNotification('Back Online', 'Connection restored. Reloading...');
        if (mainWindow) {
          loadApp();
        }
      }
      
      updateTrayMenu();
    } catch (e) {
      if (isOnline) {
        isOnline = false;
        showNotification('Connection Lost', 'You appear to be offline.');
        updateTrayMenu();
      }
    }
  }, 30000); // Check every 30 seconds
}

// ============== IPC Handlers ==============

ipcMain.handle('get-version', () => app.getVersion());
ipcMain.handle('get-platform', () => process.platform);
ipcMain.handle('get-settings', () => store.store);
ipcMain.handle('set-setting', (event, { key, value }) => {
  store.set(key, value);
  return true;
});
ipcMain.handle('show-notification', (event, { title, body }) => {
  showNotification(title, body);
});
ipcMain.handle('check-for-updates', () => {
  autoUpdater.checkForUpdatesAndNotify();
});
ipcMain.handle('is-online', () => isOnline);

ipcMain.on('window-minimize', () => mainWindow && mainWindow.minimize());
ipcMain.on('window-maximize', () => {
  if (mainWindow) {
    mainWindow.isMaximized() ? mainWindow.unmaximize() : mainWindow.maximize();
  }
});
ipcMain.on('window-close', () => mainWindow && mainWindow.close());

// ============== App Lifecycle ==============

app.whenReady().then(() => {
  createWindow();
  createTray();
  setupNetworkMonitoring();

  // Set app user model id for Windows notifications
  if (process.platform === 'win32') {
    app.setAppUserModelId('com.medmatch.desktop');
  }

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    } else if (mainWindow) {
      mainWindow.show();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  isQuitting = true;
});

// Single instance lock
const gotTheLock = app.requestSingleInstanceLock();
if (!gotTheLock) {
  app.quit();
} else {
  app.on('second-instance', (event, commandLine) => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.show();
      mainWindow.focus();
      
      // Handle deep links
      const deepLink = commandLine.find(arg => arg.startsWith('medmatch://'));
      if (deepLink) {
        handleDeepLink(deepLink);
      }
    }
  });
}

// Deep link handler
function handleDeepLink(url) {
  try {
    const parsed = new URL(url);
    const path = parsed.pathname;
    
    if (path) {
      navigateTo(path);
    }
  } catch (e) {
    log.error('Invalid deep link:', url);
  }
}

// Register deep link protocol
if (process.defaultApp) {
  if (process.argv.length >= 2) {
    app.setAsDefaultProtocolClient('medmatch', process.execPath, [path.resolve(process.argv[1])]);
  }
} else {
  app.setAsDefaultProtocolClient('medmatch');
}

// Handle protocol on macOS
app.on('open-url', (event, url) => {
  event.preventDefault();
  handleDeepLink(url);
});
