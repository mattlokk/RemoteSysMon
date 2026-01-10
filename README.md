# Remote System Monitor

Monitor your Linux PC's system stats (CPU, Memory, GPU) in real-time on your Android device!

## 🏗️ Architecture

This project consists of two parts:

1. **Server** (`server/`) - Python script running on your Linux PC
   - Monitors CPU, Memory, and AMD GPU stats
   - Pushes data to Android device via ADB every 5 seconds

2. **Client** (`app/`) - Android app built with Jetpack Compose
   - Reads JSON data from device storage
   - Displays stats with auto-refresh every 2 seconds
   - Beautiful Material 3 UI with color-coded progress bars

## 🚀 Quick Start

### Step 1: Setup the Server (Linux PC)

```bash
# Navigate to server directory
cd server/

# Install Python dependencies
pip install -r requirements.txt

# Connect your Android device via USB
# Enable USB debugging on Android
adb devices  # Verify device is connected

# Run the monitor script
python monitor_and_push.py
```

### Step 2: Build & Run the Android App

1. Open the project in Android Studio
2. Sync Gradle (if prompted)
3. Click **Run** (or press Shift+F10)
4. The app will auto-refresh every 2 seconds! 📊

---

## 📱 What You'll See

The app displays three cards:

### 🔵 CPU Card
- Usage percentage
- Current, Min, Max frequency
- Color-coded progress bar

### 🟣 Memory Card  
- Total GB
- Used GB
- Usage percentage
- Color-coded progress bar

### 🟠 GPU Card
- Usage percentage (AMD GPU via sysfs)
- Temperature in Celsius
- Color-coded progress bar

**Color Guide:**
- 🟢 Green: < 50% usage
- 🟠 Orange: 50-74% usage
- 🔴 Red: ≥ 75% usage

---

## 📁 Project Structure

```
RemoteSysMon/
├── app/                    # Android app (Jetpack Compose)
│   └── src/main/
│       └── java/.../MainActivity.kt
├── server/                 # Python monitoring scripts
│   ├── monitor_and_push.py    # Main script
│   ├── requirements.txt       # Python dependencies
│   └── README.md             # Server documentation
├── README.md              # This file
└── .gitignore
```

---

## 🔧 Technical Details

### Android App
- **Language:** Kotlin
- **UI Framework:** Jetpack Compose with Material 3
- **Min SDK:** 23 (Android 6.0.1)
- **Target SDK:** 36
- **JSON Parsing:** Gson 2.10.1
- **Data Source:** `/data/local/tmp/system_stats.json`
- **Refresh Rate:** 2 seconds

### Server Script
- **Language:** Python 3.6+
- **Dependencies:** psutil
- **GPU Support:** AMD GPUs (via sysfs)
- **Transfer Method:** ADB shell commands
- **Update Interval:** 5 seconds

---

## ⚙️ Customization

### Change Android App Refresh Rate
Edit `MainActivity.kt` around line 83:
```kotlin
delay(2000L) // Change to 3000L for 3 seconds
```

### Change Server Push Interval
Edit `server/monitor_and_push.py` at the end:
```python
time.sleep(5)  # Change to desired interval in seconds
```

### Modify GPU Monitoring (for different GPUs)
Edit `get_amd_gpu_stats()` in `server/monitor_and_push.py`:
- For NVIDIA: Use `nvidia-smi` commands
- For Intel: Use appropriate sysfs paths or tools
- Current paths work for AMD GPUs on most Linux systems

---

## 🐛 Troubleshooting

### App shows "File not found" error
1. Check device connection: `adb devices`
2. Verify file exists: `adb shell ls -l /data/local/tmp/system_stats.json`
3. Check file content: `adb shell cat /data/local/tmp/system_stats.json`
4. Make sure server script is running

### GPU stats show error
- Check sysfs paths exist: `ls /sys/class/drm/card1/device/`
- Find your GPU card: `ls /sys/class/drm/`
- Update paths in `monitor_and_push.py` if needed
- See `server/README.md` for detailed GPU troubleshooting

### ADB connection fails
- Ensure USB debugging is enabled on Android
- Try `adb kill-server && adb start-server`
- Check USB cable and connection

---

## 📋 Requirements

### Linux PC
- Python 3.6+
- psutil library
- adb (Android Debug Bridge)
- AMD GPU (or modify script for your GPU type)

### Android Device
- Android 6.0.1 (API 23) or higher
- USB debugging enabled
- USB connection to PC (or ADB over WiFi)

---

## 🎯 Future Enhancements

Ideas for extending this project:
- [ ] Network transfer (HTTP/WebSocket) instead of ADB
- [ ] Historical data graphs
- [ ] Configurable refresh rate in UI
- [ ] Dark/Light theme toggle
- [ ] Notification for high usage alerts
- [ ] Disk usage statistics
- [ ] Network upload/download speeds
- [ ] Multiple PC monitoring
- [ ] Background service on Android

---

## 📄 License

This project is open source. Feel free to modify and distribute.

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

---

Enjoy monitoring your system! 🎉

For detailed server setup, see [`server/README.md`](server/README.md)
