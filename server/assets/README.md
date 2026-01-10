# Icon Placeholder

Place your application icons here:

- `icon.png` - For Linux (PNG format, recommended 256x256 or 512x512)
- `icon.ico` - For Windows (ICO format, multi-size recommended)

## Creating Icons

You can create icons using:
- GIMP (export as PNG/ICO)
- Inkscape (export as PNG)
- Online tools like favicon.io
- ImageMagick: `convert icon.png -resize 256x256 icon.ico`

## Recommended Sizes

**Linux (PNG):**
- 256x256 or 512x512 pixels

**Windows (ICO):**
- Multi-size ICO containing: 16x16, 32x32, 48x48, 64x64, 128x128, 256x256

## Default Behavior

If no icon is provided:
- Linux: Uses system default "utilities-system-monitor" icon
- Windows: Uses PyInstaller default icon
- System tray will use the same icon
