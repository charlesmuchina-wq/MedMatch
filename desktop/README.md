# MedMatch Desktop Application

Cross-platform desktop application for MedMatch - AI-Powered Job Search Platform.

## Features

- **System Tray Integration**: Quick access to key features without opening the full app
- **Auto-Updates**: Automatic background updates with user notification
- **Offline Detection**: Graceful handling when internet connection is lost
- **Native Notifications**: System-level notifications for job alerts and updates
- **Deep Linking**: Open specific pages via `medmatch://` protocol
- **Keyboard Shortcuts**: Full keyboard navigation support
- **Persistent Settings**: Remember window size, preferences, and startup options

## Supported Platforms

| Platform | Architectures | Formats |
|----------|---------------|---------|
| Windows | x64, ia32 | NSIS Installer, Portable |
| macOS | x64, arm64 (Apple Silicon) | DMG, ZIP |
| Linux | x64 | AppImage, DEB, RPM |

## Development

### Prerequisites

- Node.js 18+
- npm or yarn

### Setup

```bash
cd /app/desktop
npm install
```

### Run in Development

```bash
npm start
```

### Build for Current Platform

```bash
npm run build
```

### Build for Specific Platforms

```bash
# Windows
npm run build:win

# macOS
npm run build:mac

# Linux
npm run build:linux

# All platforms
npm run dist
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+1 | Dashboard |
| Ctrl+2 | Job Search |
| Ctrl+3 | Applications |
| Ctrl+4 | Interview Calendar |
| Ctrl+5 | AI Tools |
| Ctrl+N | New Job Search |
| Ctrl+U | Upload Resume |
| Ctrl+, | Preferences |
| Ctrl+/ | Show Shortcuts |
| Ctrl+R | Reload |
| Ctrl+Q | Quit |
| Alt+Left | Go Back |
| Alt+Right | Go Forward |
| F11 | Toggle Fullscreen |

## Configuration

The app stores user preferences in:

- **Windows**: `%APPDATA%/medmatch-desktop/config.json`
- **macOS**: `~/Library/Application Support/medmatch-desktop/config.json`
- **Linux**: `~/.config/medmatch-desktop/config.json`

### Available Settings

```json
{
  "launchAtStartup": false,
  "minimizeToTray": true,
  "checkUpdatesAutomatically": true
}
```

## Auto-Updates

The app automatically checks for updates on launch (configurable). Updates are downloaded in the background and installed on restart.

Update distribution is configured for GitHub Releases. To enable:

1. Create a GitHub repository for releases
2. Update `publish` settings in `package.json`
3. Create releases with built assets attached

## Deep Linking

The app registers the `medmatch://` protocol for deep linking:

```
medmatch://dashboard
medmatch://search?q=software+engineer
medmatch://job/12345
medmatch://interview/abc123
```

## Building Icons

For production builds, you'll need platform-specific icons:

- `assets/icon.ico` - Windows (256x256)
- `assets/icon.icns` - macOS (512x512)
- `assets/icon.png` - Linux (512x512)
- `assets/tray-icon.png` - Tray icon (16x16 or 32x32)

### Generate Icons

You can use tools like:
- [electron-icon-maker](https://www.npmjs.com/package/electron-icon-maker)
- [png2icons](https://www.npmjs.com/package/png2icons)

## Troubleshooting

### App won't start

1. Check if another instance is running
2. Delete config file and restart
3. Run from terminal to see error messages

### Auto-update not working

1. Ensure GitHub releases are public
2. Check network connectivity
3. Review logs in app data directory

### High CPU usage

1. Disable hardware acceleration in settings
2. Check for infinite loop in web content
3. Update to latest version

## License

MIT License - © 2026 MedMatch
