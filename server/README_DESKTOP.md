# RemoteSysMon Desktop Application

A desktop application for monitoring system resources (CPU, Memory, GPU) and pushing stats to Android devices via ADB.

## Features

- 🖥️ **Real-time System Monitoring**
  - CPU usage, temperature, and power consumption
  - Memory usage statistics
  - AMD GPU usage, temperature, and power consumption

- 📱 **Android Integration**
  - Push stats to Android device via ADB
  - Screen controls (on/off, wake, unlock)
  - Volume controls
  - Custom ADB commands

- 🎨 **Customizable Appearance**
  - Dark/Light themes
  - Configurable colors (background, text, accent)
  - Adjustable font size
  - Configurable refresh rate

- 🔧 **System Tray Support**
  - Minimize to tray
  - Background monitoring
  - Quick access controls

## Requirements

- Python 3.8+
- Linux (for power monitoring features)
- Root/sudo access (for CPU power monitoring via RAPL)
- ADB (Android Debug Bridge)
- PyQt6

## Installation

1. **Install dependencies:**
   ```bash
   cd server
   pip install -r requirements.txt
   ```

2. **Install ADB (if not already installed):**
   ```bash
   # Ubuntu/Debian
   sudo apt install adb
   
   # Arch Linux
   sudo pacman -S android-tools
   ```

3. **Enable USB debugging on your Android device:**
   - Go to Settings → About Phone
   - Tap "Build Number" 7 times to enable Developer Options
   - Go to Settings → Developer Options
   - Enable "USB Debugging"

## Usage

### Running the Desktop App

**With GUI (recommended):**
```bash
cd server
sudo python3 main.py
```

**Legacy command-line mode:**
```bash
cd server
sudo ./monitor_and_push.py
```

> **Note:** Root access is required for CPU power monitoring via RAPL. The app will work without it but CPU power stats will be unavailable.

### First Time Setup

1. **Connect your Android device:**
   ```bash
   adb devices
   ```

2. **Launch the app:**
   ```bash
   sudo python3 main.py
   ```

3. **Select your device** from the dropdown in the ADB section

4. **Click "Start Monitoring"** to begin pushing stats

### Features Guide

#### System Tray
- **Double-click** tray icon to show/hide window
- **Right-click** for menu:
  - Show Window
  - Start/Stop Monitoring
  - Quit

#### ADB Commands
- **Screen ON/OFF** - Control device screen
- **Wake** - Wake device from sleep
- **Unlock** - Swipe up gesture to unlock
- **Volume +/-** - Adjust device volume
- **Custom Command** - Execute any ADB shell command

#### Settings
- **Appearance Tab:**
  - Choose theme (dark/light/custom)
  - Customize colors
  - Adjust font size
  - Set refresh rate (100-10000ms)
  
- **Monitoring Tab:**
  - Auto-start monitoring on launch
  - Minimize to tray on close
  - Start minimized

- **ADB Tab:**
  - Set target file path on device
  - Auto-connect to first device

## JSON Output Format

The app sends data to your Android device in this format:

```json
{
  "stats": {
    "cpu": {
      "cpu_percent": 25.5,
      "cpu_temp_celsius": 55.0,
      "cpu_power_watts": 45.23
    },
    "memory": {
      "total_gb": 16.0,
      "used_gb": 8.5,
      "percent": 53.1
    },
    "gpu": {
      "gpu_usage_percent": 15,
      "gpu_temp_celsius": 65.0,
      "gpu_power_watts": 37.50
    }
  },
  "appearance": {
    "background_color": "#1e1e1e",
    "text_color": "#ffffff",
    "accent_color": "#0078d4",
    "font_size": 14,
    "theme": "dark",
    "show_graphs": true,
    "refresh_rate_ms": 1000
  },
  "metadata": {
    "timestamp": "2026-01-09T12:34:56",
    "version": "2.0.0",
    "warning": null
  }
}
```

## Building Distributable Packages

### Linux

```bash
cd server
python3 build.py
```

Output: `dist/RemoteSysMon`

### Windows (on Windows)

```bash
cd server
python build.py
```

Output: `dist\RemoteSysMon.exe`

### Build Commands

- `python3 build.py` - Build for current platform
- `python3 build.py clean` - Clean build artifacts
- `python3 build.py spec` - Generate custom .spec file

## Project Structure

```
server/
├── core/                    # Core functionality
│   ├── __init__.py
│   ├── monitor.py          # System monitoring
│   ├── adb_manager.py      # ADB commands
│   └── config.py           # Configuration management
├── gui/                     # GUI components
│   ├── __init__.py
│   ├── main_window.py      # Main application window
│   ├── tray_icon.py        # System tray icon
│   └── settings_dialog.py  # Settings dialog
├── assets/                  # Icons and resources
├── main.py                  # Desktop app entry point
├── monitor_and_push.py      # Legacy CLI script
├── config.json              # User configuration
├── requirements.txt         # Python dependencies
└── build.py                 # Build script
```

## Configuration

Configuration is stored in `server/config.json`. The app will create this file with defaults on first run. You can edit it manually or use the Settings dialog in the app.

## Troubleshooting

### CPU Power Monitoring Not Working

- **Cause:** Not running as root
- **Solution:** Run with `sudo python3 main.py`

### ADB Device Not Found

- **Cause:** USB debugging not enabled or device not connected
- **Solutions:**
  1. Enable USB debugging on Android device
  2. Connect device via USB
  3. Run `adb devices` to verify connection
  4. Click "Refresh" in the app

### GPU Stats Not Available

- **Cause:** Wrong GPU paths (currently configured for AMD)
- **Solution:** Update paths in `core/monitor.py` for your GPU

### App Won't Start

- **Cause:** Missing dependencies
- **Solution:** Run `pip install -r requirements.txt`

## AMD vs NVIDIA GPU

Currently configured for AMD GPUs. For NVIDIA:

1. Edit `core/monitor.py`
2. Replace AMD sysfs paths with NVIDIA equivalents:
   - Use `nvidia-smi` or
   - Read from `/sys/class/hwmon/` for NVIDIA paths

## License

[Your License Here]

## Contributing

Contributions welcome! Please open an issue or PR.

## Changelog

### v2.0.0 (Current)
- ✨ Desktop GUI application with PyQt6
- ✨ System tray support
- ✨ Settings dialog with appearance customization
- ✨ Comprehensive ADB command controls
- ✨ New JSON format with stats/appearance separation
- ✨ Build scripts for Windows/Linux

### v1.0.0
- Initial command-line version
- Basic monitoring and ADB push functionality
