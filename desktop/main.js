/**
 * MedMatch Desktop App - Main Process
 * Electron wrapper for the MedMatch web application
 * Features: System tray, notifications, auto-launch, offline detection
 */

const { app, BrowserWindow, Menu, Tray, shell, ipcMain, Notification, nativeImage } = require('electron');
const path = require('path');

// Configuration
const APP_URL = 'https://resume-match-64.preview.emergentagent.com';
const isDev = process.env.NODE_ENV === 'development';

let mainWindow = null;
let tray = null;
let isQuitting = false;

// Create the main application window
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 800,
    minHeight: 600,
    title: 'MedMatch - AI Job Search',
    icon: path.join(__dirname, 'assets', 'icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      spellcheck: true
    },
    show: false, // Don't show until ready
    backgroundColor: '#1a1a2e', // Match app theme
    titleBarStyle: 'default',
    autoHideMenuBar: false
  });

  // Load the web app
  mainWindow.loadURL(APP_URL);

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    
    // Show welcome notification on first launch
    if (Notification.isSupported()) {
      new Notification({
        title: 'MedMatch Desktop',
        body: 'Your AI-powered job search assistant is ready!',
        icon: path.join(__dirname, 'assets', 'icon.png')
      }).show();
    }
  });

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    // Open external links in default browser
    if (url.startsWith('http') && !url.includes('career-ai-28.preview.emergentagent.com')) {
      shell.openExternal(url);
      return { action: 'deny' };
    }
    return { action: 'allow' };
  });

  // Handle window close - minimize to tray instead
  mainWindow.on('close', (event) => {
    if (!isQuitting) {
      event.preventDefault();
      mainWindow.hide();
      
      // Show tray notification on first minimize
      if (tray && !app.isHidden) {
        tray.displayBalloon({
          title: 'MedMatch',
          content: 'App minimized to system tray. Click the icon to restore.',
          icon: path.join(__dirname, 'assets', 'icon.png')
        });
      }
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Create application menu
  createMenu();
}

// Create system tray
function createTray() {
  const iconPath = path.join(__dirname, 'assets', 'tray-icon.png');
  
  // Create a simple tray icon if file doesn't exist
  let trayIcon;
  try {
    trayIcon = nativeImage.createFromPath(iconPath);
    if (trayIcon.isEmpty()) {
      trayIcon = nativeImage.createEmpty();
    }
  } catch (e) {
    trayIcon = nativeImage.createEmpty();
  }

  tray = new Tray(trayIcon);
  tray.setToolTip('MedMatch - AI Job Search');

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
    {
      label: 'Search Jobs',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.loadURL(`${APP_URL}/search`);
        }
      }
    },
    {
      label: 'Interview Calendar',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.loadURL(`${APP_URL}/interview-calendar`);
        }
      }
    },
    { type: 'separator' },
    {
      label: 'AI Dragon Assistant',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.webContents.executeJavaScript('window.openDragonAssistant && window.openDragonAssistant()');
        }
      }
    },
    { type: 'separator' },
    {
      label: 'Check for Updates',
      click: () => {
        shell.openExternal('https://medmatch.com/download');
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

  // Double-click to show window
  tray.on('double-click', () => {
    if (mainWindow) {
      mainWindow.show();
      mainWindow.focus();
    }
  });
}

// Create application menu
function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'New Job Search',
          accelerator: 'CmdOrCtrl+N',
          click: () => mainWindow.loadURL(`${APP_URL}/search`)
        },
        {
          label: 'Upload Resume',
          accelerator: 'CmdOrCtrl+U',
          click: () => mainWindow.loadURL(`${APP_URL}/resume`)
        },
        { type: 'separator' },
        {
          label: 'Preferences',
          accelerator: 'CmdOrCtrl+,',
          click: () => mainWindow.loadURL(`${APP_URL}/settings`)
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
          click: () => mainWindow.webContents.toggleDevTools()
        }
      ]
    },
    {
      label: 'Navigate',
      submenu: [
        {
          label: 'Dashboard',
          accelerator: 'CmdOrCtrl+1',
          click: () => mainWindow.loadURL(`${APP_URL}/dashboard`)
        },
        {
          label: 'Job Search',
          accelerator: 'CmdOrCtrl+2',
          click: () => mainWindow.loadURL(`${APP_URL}/search`)
        },
        {
          label: 'My Applications',
          accelerator: 'CmdOrCtrl+3',
          click: () => mainWindow.loadURL(`${APP_URL}/applications`)
        },
        {
          label: 'Interview Calendar',
          accelerator: 'CmdOrCtrl+4',
          click: () => mainWindow.loadURL(`${APP_URL}/interview-calendar`)
        },
        {
          label: 'AI Tools',
          accelerator: 'CmdOrCtrl+5',
          click: () => mainWindow.loadURL(`${APP_URL}/interview-prep`)
        },
        { type: 'separator' },
        {
          label: 'Go Back',
          accelerator: 'Alt+Left',
          click: () => mainWindow.webContents.goBack()
        },
        {
          label: 'Go Forward',
          accelerator: 'Alt+Right',
          click: () => mainWindow.webContents.goForward()
        }
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
          click: () => {
            const shortcuts = `
MedMatch Keyboard Shortcuts:

Ctrl+N - New Job Search
Ctrl+U - Upload Resume
Ctrl+1 - Dashboard
Ctrl+2 - Job Search
Ctrl+3 - Applications
Ctrl+4 - Interview Calendar
Ctrl+5 - AI Tools
Ctrl+Q - Quit
            `;
            require('electron').dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'Keyboard Shortcuts',
              message: shortcuts
            });
          }
        },
        { type: 'separator' },
        {
          label: 'Report Issue',
          click: () => shell.openExternal('https://github.com/medmatch/issues')
        },
        {
          label: 'About MedMatch',
          click: () => {
            require('electron').dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About MedMatch',
              message: 'MedMatch Desktop v1.0.0',
              detail: 'AI-Powered Job Search Platform\n\nFeatures:\n• Resume parsing & matching\n• Multi-source job aggregation\n• AI interview preparation\n• Voice coaching\n• Video practice with analysis\n\n© 2026 MedMatch. All rights reserved.'
            });
          }
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

// App ready
app.whenReady().then(() => {
  createWindow();
  createTray();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    } else {
      mainWindow.show();
    }
  });
});

// Quit when all windows are closed (except on macOS)
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Handle before quit
app.on('before-quit', () => {
  isQuitting = true;
});

// Handle second instance - focus existing window
const gotTheLock = app.requestSingleInstanceLock();
if (!gotTheLock) {
  app.quit();
} else {
  app.on('second-instance', () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.show();
      mainWindow.focus();
    }
  });
}

// IPC handlers for communication with renderer
ipcMain.handle('get-version', () => app.getVersion());
ipcMain.handle('get-platform', () => process.platform);
ipcMain.handle('show-notification', (event, { title, body }) => {
  if (Notification.isSupported()) {
    new Notification({ title, body }).show();
  }
});
