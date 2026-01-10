"""
System Monitor Module
Handles CPU, Memory, and GPU monitoring
"""

import os
import time
from typing import Dict, Optional

import psutil


class SystemMonitor:
    """Monitor system resources including CPU, Memory, and GPU"""
    
    def __init__(self):
        self.rapl_path = '/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj'
        self.gpu_usage_path = "/sys/class/drm/card1/device/gpu_busy_percent"
        self.gpu_temp_path = "/sys/class/drm/card1/device/hwmon/hwmon5/temp1_input"
        self.gpu_power_path = "/sys/class/drm/card1/device/hwmon/hwmon5/power1_average"
        
    def get_cpu_stats(self) -> Dict[str, float]:
        """Get CPU-related stats including temperature and usage"""
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
            "cpu_percent": float(psutil.cpu_percent(interval=1)),  # CPU usage %
            "cpu_temp_celsius": float(cpu_temp) if cpu_temp is not None else 0.0,
        }
    
    def get_cpu_power_watts(self, interval: float = 1.0) -> Optional[float]:
        """Get CPU package power consumption in watts using RAPL"""
        try:
            # Read energy twice with specified interval
            with open(self.rapl_path, 'r') as f:
                energy1 = int(f.read().strip())
            
            time.sleep(interval)
            
            with open(self.rapl_path, 'r') as f:
                energy2 = int(f.read().strip())
            
            # Calculate power in watts
            energy_diff = energy2 - energy1  # microjoules
            power_watts = energy_diff / 1_000_000  # convert to watts (J/s)
            
            return power_watts
        except (FileNotFoundError, PermissionError) as e:
            # Return None if RAPL is not available or no permissions
            return None
    
    def get_memory_stats(self) -> Dict[str, float]:
        """Get memory stats"""
        mem = psutil.virtual_memory()
        return {
            "total_gb": round(mem.total / (1024 ** 3), 2),      # Total memory in GB
            "used_gb": round(mem.used / (1024 ** 3), 2),        # Used memory in GB
            "percent": float(mem.percent),                              # Memory usage %
        }
    
    def get_gpu_stats(self) -> Dict[str, float]:
        """Get AMD GPU stats"""
        try:
            with open(self.gpu_usage_path, 'r') as gpu_usage_file:
                gpu_usage = float(int(gpu_usage_file.read().strip()))

            with open(self.gpu_temp_path, 'r') as gpu_temp_file:
                gpu_temp = float(int(gpu_temp_file.read().strip()) / 1000)

            gpu_power_watts: Optional[float] = None
            try:
                with open(self.gpu_power_path, 'r') as gpu_power_file:
                    gpu_power_watts = round(
                        int(gpu_power_file.read().strip()) / 1_000_000,
                        2,
                    )
            except (FileNotFoundError, PermissionError):
                pass

            stats: Dict[str, float] = {
                "gpu_usage_percent": gpu_usage,
                "gpu_temp_celsius": gpu_temp,
            }

            if gpu_power_watts is not None:
                stats["gpu_power_watts"] = gpu_power_watts

            return stats
        except FileNotFoundError as e:
            print(f"GPU stats unavailable: {e}")
            return {
                "gpu_usage_percent": 0.0,
                "gpu_temp_celsius": 0.0,
            }
    
    def get_all_stats(self, interval: float = 1.0) -> Dict[str, Dict[str, float]]:
        """
        Get all system stats combined
        
        Args:
            interval: Measurement interval for power calculations
            
        Returns:
            Dictionary with cpu, memory, and gpu stats
        """
        # Get CPU power first (this includes the interval measurement)
        cpu_power_watts = self.get_cpu_power_watts(interval=interval)
        
        # Gather other stats
        cpu_stats = self.get_cpu_stats()
        memory_stats = self.get_memory_stats()
        gpu_stats = self.get_gpu_stats()
        
        # Add CPU power to CPU stats if available
        if cpu_power_watts is not None:
            cpu_stats["cpu_power_watts"] = round(cpu_power_watts, 2)
        
        return {
            "cpu": cpu_stats,
            "memory": memory_stats,
            "gpu": gpu_stats
        }
    
    def is_running_as_root(self) -> bool:
        """Check if running with root privileges"""
        return os.geteuid() == 0
