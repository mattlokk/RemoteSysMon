#!/usr/bin/env python3
"""
System Monitor & ADB Push Script
Monitors CPU, Memory, and GPU stats and pushes them to Android device via ADB
"""

import psutil
import json
import subprocess
import time

# Function to get CPU-related stats
def get_cpu_stats():
    # Get CPU temperature
    cpu_temp = None
    try:
        # Try to read from thermal zones (common on Linux)
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            cpu_temp = int(f.read().strip()) / 1000  # Convert from millidegree to Celsius
    except (FileNotFoundError, PermissionError):
        # If thermal zone doesn't work, try psutil (if available)
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                # Try to find CPU temp from common sensor names
                for name in ['coretemp', 'k10temp', 'cpu_thermal', 'cpu-thermal']:
                    if name in temps and temps[name]:
                        cpu_temp = temps[name][0].current
                        break
        except (AttributeError, KeyError):
            pass
    
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),  # CPU usage %
        "cpu_temp_celsius": cpu_temp if cpu_temp is not None else 0.0,  # CPU temperature
    }

# Function to get memory stats
def get_memory_stats():
    mem = psutil.virtual_memory()
    return {
        "total": mem.total / (1024 ** 3),      # Total memory in GB
        "used": mem.used / (1024 ** 3),        # Used memory in GB
        "percent": mem.percent,                # Memory usage %
    }

# Function to get AMD GPU stats
def get_amd_gpu_stats():
    try:
        gpu_usage_path = "/sys/class/drm/card1/device/gpu_busy_percent"
        gpu_temp_path = "/sys/class/drm/card1/device/hwmon/hwmon5/temp1_input"
        gpu_power_path = "/sys/class/drm/card1/device/hwmon/hwmon5/power1_average"

        # Read GPU usage percentage
        with open(gpu_usage_path, 'r') as gpu_usage_file:
            gpu_usage = int(gpu_usage_file.read().strip())

        # Read GPU temperature in millidegree Celsius
        with open(gpu_temp_path, 'r') as gpu_temp_file:
            gpu_temp = int(gpu_temp_file.read().strip()) / 1000

        # Read GPU power in microwatts and convert to watts
        gpu_power_watts = None
        try:
            with open(gpu_power_path, 'r') as gpu_power_file:
                gpu_power_watts = int(gpu_power_file.read().strip()) / 1_000_000
        except (FileNotFoundError, PermissionError):
            pass

        stats = {
            "gpu_usage_percent": gpu_usage,
            "gpu_temp_celsius": gpu_temp,
        }
        
        if gpu_power_watts is not None:
            stats["gpu_power_watts"] = round(gpu_power_watts, 2)
        
        return stats
    except FileNotFoundError as e:
        return {"error": str(e)}

# Function to send data via ADB
def send_data_to_android(data):
    try:
        # Write JSON to a temporary file first
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(data, f, indent=2)
            temp_file = f.name
        
        # Push the file to Android device
        subprocess.run(['adb', 'push', temp_file, '/data/local/tmp/system_stats.json'], 
                      check=True, capture_output=True)
        
        # Clean up temp file
        os.unlink(temp_file)
        
        print("Data sent to Android successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to send data over ADB. Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

def get_cpu_power_watts(interval=1.0):
    """Get CPU package power consumption in watts using RAPL"""
    energy_file = '/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj'
    
    try:
        # Read energy twice with specified interval
        with open(energy_file, 'r') as f:
            energy1 = int(f.read().strip())
        
        time.sleep(interval)
        
        with open(energy_file, 'r') as f:
            energy2 = int(f.read().strip())
        
        # Calculate power in watts
        energy_diff = energy2 - energy1  # microjoules
        power_watts = energy_diff / 1_000_000  # convert to watts (J/s)
        
        return power_watts
    except (FileNotFoundError, PermissionError) as e:
        # Return None if RAPL is not available or no permissions
        return None

# Main monitoring loop
def monitor_system():
    import os
    
    # Check if running as root for RAPL access
    is_root = os.geteuid() == 0
    if not is_root:
        print("WARNING: Not running as root. CPU power monitoring may not be available.")
        print("Run with: sudo ./monitor_and_push.py")
        print()
    
    while True:
        # Get CPU power first (this includes a 1-second interval measurement)
        cpu_power_watts = get_cpu_power_watts(interval=1.0)
        
        # Gather system stats
        cpu_stats = get_cpu_stats()
        memory_stats = get_memory_stats()
        gpu_stats = get_amd_gpu_stats()
        
        # Add CPU power to CPU stats if available
        if cpu_power_watts is not None:
            cpu_stats["cpu_power_watts"] = round(cpu_power_watts, 2)

        # Combine all stats into one dictionary
        combined_stats = {
            "cpu": cpu_stats,
            "memory": memory_stats,
            "gpu": gpu_stats,
        }
        
        # Add warning if not running as root and power data is missing
        if not is_root and cpu_power_watts is None:
            combined_stats["warning"] = "CPU power unavailable - run with sudo"

        # Optional: Print stats locally for debugging
        print(json.dumps(combined_stats, indent=4))

        # Send the data to Android over ADB
        send_data_to_android(combined_stats)

        # Wait for 2 seconds before the next iteration
        time.sleep(10)

if __name__ == "__main__":
    monitor_system()
