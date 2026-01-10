# Server Scripts

Python scripts for collecting system stats and pushing them to the Android device.

## Requirements

- Python 3.6+
- `psutil` library
- `adb` (Android Debug Bridge)
- Android device connected via USB with USB debugging enabled

## Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Connect your Android device:**
   - Enable USB debugging on your Android device
   - Connect via USB
   - Verify connection: `adb devices`

3. **Run the monitor script:**
   ```bash
   python monitor_and_push.py
   ```

## Scripts

### `monitor_and_push.py`
The main script that:
- Monitors CPU usage and frequency
- Monitors memory usage
- Monitors AMD GPU usage and temperature (reads from `/sys/class/drm/card1/device/`)
- Pushes stats to Android device every 5 seconds via ADB
- Writes JSON to `/data/local/tmp/system_stats.json` on the Android device

## GPU Support

This script is configured for **AMD GPUs** and reads directly from sysfs:
- GPU usage: `/sys/class/drm/card1/device/gpu_busy_percent`
- GPU temp: `/sys/class/drm/card1/device/hwmon/hwmon5/temp1_input`

**Note:** The paths may vary depending on your GPU and system configuration. Adjust the paths in `get_amd_gpu_stats()` if needed.

For **NVIDIA GPUs**, replace `get_amd_gpu_stats()` with nvidia-smi based queries.

## JSON Format

The script generates JSON in this format:
```json
{
    "cpu": {
        "cpu_percent": 15.2,
        "cpu_freq": {
            "current": 2800.0,
            "min": 1000.0,
            "max": 4000.0
        }
    },
    "memory": {
        "total": 31.25,
        "used": 8.5,
        "percent": 27.2
    },
    "gpu": {
        "gpu_usage_percent": 12,
        "gpu_temp_celsius": 65.0
    }
}
```

## Troubleshooting

**GPU stats show error:**
- Check if paths exist: `ls /sys/class/drm/card1/device/`
- Find your GPU card: `ls /sys/class/drm/`
- Find hwmon path: `ls /sys/class/drm/card1/device/hwmon/`
- Update paths in script accordingly

**ADB fails:**
- Check device connection: `adb devices`
- Restart ADB: `adb kill-server && adb start-server`
- Check USB debugging is enabled on Android

**Permission denied on GPU files:**
- You may need to run with appropriate permissions
- Or add your user to the video group: `sudo usermod -a -G video $USER`
