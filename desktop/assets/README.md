# MedMatch Desktop - Icon Assets

This directory should contain the following icon files for building:

## Required Icons

| File | Size | Platform | Format |
|------|------|----------|--------|
| `icon.png` | 512x512 | All | PNG (source) |
| `icon.ico` | 256x256 | Windows | ICO |
| `icon.icns` | 512x512 | macOS | ICNS |
| `tray-icon.png` | 32x32 | All | PNG (system tray) |

## Linux Icons (in icons/ subdirectory)

For Linux builds, create icons at these sizes:
- `icons/16x16.png`
- `icons/32x32.png`
- `icons/48x48.png`
- `icons/64x64.png`
- `icons/128x128.png`
- `icons/256x256.png`
- `icons/512x512.png`

## Generating Icons

### From SVG source:
```bash
# Install dependencies
npm install -g electron-icon-maker

# Generate all formats from PNG
electron-icon-maker --input=icon-source.png --output=./
```

### Using ImageMagick:
```bash
# PNG to ICO (Windows)
convert icon.png -define icon:auto-resize=256,128,64,48,32,16 icon.ico

# PNG to ICNS (macOS) - requires icns tools
png2icns icon.icns icon.png
```

### Online Tools:
- https://icoconvert.com/ (PNG to ICO)
- https://cloudconvert.com/png-to-icns (PNG to ICNS)

## Design Guidelines

- Use a simple, recognizable design
- Ensure the icon is visible at small sizes (16x16)
- Match the app's teal color scheme (#20b2aa)
- Include adequate padding for rounded corners on macOS
