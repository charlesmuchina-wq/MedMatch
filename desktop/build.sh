#!/bin/bash
# MedMatch Desktop App Build Script
# Builds desktop applications for Windows, macOS, and Linux

set -e

echo "🖥️ MedMatch Desktop Build Script"
echo "================================"

# Check if we're in the desktop directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Must run from /app/desktop directory"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    yarn install
fi

# Check for required icon files
echo "🎨 Checking icon files..."
ICONS_MISSING=false

if [ ! -f "assets/icon.png" ]; then
    echo "⚠️  Missing: assets/icon.png (512x512 PNG)"
    ICONS_MISSING=true
fi

if [ ! -f "assets/icon.ico" ]; then
    echo "⚠️  Missing: assets/icon.ico (Windows)"
    ICONS_MISSING=true
fi

if [ ! -f "assets/icon.icns" ]; then
    echo "⚠️  Missing: assets/icon.icns (macOS)"
    ICONS_MISSING=true
fi

if [ "$ICONS_MISSING" = true ]; then
    echo ""
    echo "📝 To generate icons from a source PNG (512x512), use:"
    echo "   npm install -g electron-icon-maker"
    echo "   electron-icon-maker --input=source-icon.png --output=assets/"
    echo ""
    echo "Or provide placeholder icons to continue..."
fi

# Build based on argument
case "$1" in
    "win"|"windows")
        echo "🪟 Building for Windows..."
        yarn build:win
        ;;
    "mac"|"macos")
        echo "🍎 Building for macOS..."
        yarn build:mac
        ;;
    "linux")
        echo "🐧 Building for Linux..."
        yarn build:linux
        ;;
    "all"|"dist")
        echo "🌍 Building for all platforms..."
        yarn dist
        ;;
    "pack")
        echo "📦 Creating unpacked build..."
        yarn pack
        ;;
    *)
        echo ""
        echo "Usage: ./build.sh [platform]"
        echo ""
        echo "Platforms:"
        echo "  win, windows  - Build for Windows (NSIS installer + portable)"
        echo "  mac, macos    - Build for macOS (DMG + ZIP)"
        echo "  linux         - Build for Linux (AppImage + DEB + RPM)"
        echo "  all, dist     - Build for all platforms"
        echo "  pack          - Create unpacked directory build"
        echo ""
        echo "Output will be in: ./dist/"
        echo ""
        echo "Build requirements:"
        echo "  - Windows: Wine (for cross-compilation on Linux/macOS)"
        echo "  - macOS: Xcode Command Line Tools"
        echo "  - Linux: rpm, dpkg-dev (for package formats)"
        ;;
esac

echo ""
echo "✅ Build script completed"
