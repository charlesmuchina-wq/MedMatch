# MedMatch Desktop App

Cross-platform desktop application for MedMatch - AI-Powered Job Search.

## Features

- 🖥️ Native desktop experience on Windows, macOS, and Linux
- 📌 System tray with quick actions
- ⌨️ Keyboard shortcuts for fast navigation
- 🔔 Native notifications for job alerts
- 🔄 Auto-updates support
- 🌐 Works offline with cached data

## Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Development
```bash
cd /app/desktop
npm install
npm start
```

### Build for Distribution

**Windows:**
```bash
npm run build:win
```

**macOS:**
```bash
npm run build:mac
```

**Linux:**
```bash
npm run build:linux
```

**All Platforms:**
```bash
npm run dist
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+N | New Job Search |
| Ctrl+U | Upload Resume |
| Ctrl+1 | Dashboard |
| Ctrl+2 | Job Search |
| Ctrl+3 | Applications |
| Ctrl+4 | Interview Calendar |
| Ctrl+5 | AI Tools |
| Ctrl+Q | Quit |
| Alt+Left | Go Back |
| Alt+Right | Go Forward |
| Ctrl+Shift+I | Developer Tools |

## System Tray

The app minimizes to system tray when you close the window. Right-click the tray icon for quick actions:

- Open MedMatch
- Search Jobs
- Interview Calendar
- AI Dragon Assistant
- Quit

## Configuration

The app connects to the MedMatch web service. To change the server URL, edit `main.js`:

```javascript
const APP_URL = 'https://your-server.com';
```

## Build Output

After building, find the installers in the `dist/` folder:

- **Windows**: `MedMatch Setup.exe` (installer) or `MedMatch.exe` (portable)
- **macOS**: `MedMatch.dmg`
- **Linux**: `MedMatch.AppImage` or `medmatch.deb`

## License

MIT License - © 2026 MedMatch
