"""
ADB Manager
Handles ADB connection and command execution
"""

import subprocess
import json
import tempfile
import os
from typing import List, Optional, Dict, Any


class ADBDevice:
    """Represents an ADB device"""
    
    def __init__(self, device_id: str, state: str, model: str = "Unknown"):
        self.device_id = device_id
        self.state = state
        self.model = model
    
    def __repr__(self):
        return f"ADBDevice(id={self.device_id}, state={self.state}, model={self.model})"


class ADBManager:
    """Manage ADB connections and commands"""
    
    def __init__(self, device_id: Optional[str] = None):
        """
        Initialize ADB manager
        
        Args:
            device_id: Optional device ID to connect to
        """
        self.device_id = device_id
        self.target_path = "/data/local/tmp/system_stats.json"
    
    def is_adb_available(self) -> bool:
        """
        Check if ADB is available in system PATH
        
        Returns:
            True if ADB is available, False otherwise
        """
        try:
            result = subprocess.run(['adb', 'version'], 
                                  capture_output=True, 
                                  text=True,
                                  timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def get_devices(self) -> List[ADBDevice]:
        """
        List connected ADB devices
        
        Returns:
            List of ADBDevice objects
        """
        try:
            result = subprocess.run(['adb', 'devices', '-l'], 
                                  capture_output=True, 
                                  text=True,
                                  timeout=10)
            
            devices = []
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        device_id = parts[0]
                        state = parts[1]
                        
                        # Try to extract model
                        model = "Unknown"
                        for part in parts[2:]:
                            if part.startswith('model:'):
                                model = part.split(':')[1]
                                break
                        
                        devices.append(ADBDevice(device_id, state, model))
            
            return devices
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"Error getting devices: {e}")
            return []
    
    def connect(self, device_id: str) -> bool:
        """
        Connect to specific device
        
        Args:
            device_id: Device ID to connect to
            
        Returns:
            True if successful, False otherwise
        """
        self.device_id = device_id
        # Test connection
        return self._execute('echo "test"', silent=True) is not None
    
    def push_data(self, data: Dict[str, Any]) -> bool:
        """
        Push JSON data to device
        
        Args:
            data: Dictionary to send as JSON
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Write JSON to a temporary file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
                json.dump(data, f, indent=2)
                temp_file = f.name
            
            # Push the file to Android device
            cmd = ['adb']
            if self.device_id:
                cmd.extend(['-s', self.device_id])
            cmd.extend(['push', temp_file, self.target_path])
            
            result = subprocess.run(cmd, 
                                  capture_output=True, 
                                  timeout=10)
            
            # Clean up temp file
            os.unlink(temp_file)
            
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, IOError) as e:
            print(f"Failed to push data: {e}")
            return False

    def _send_wakeup_keyevent(self) -> bool:
        """Send the wakeup key event to the attached device"""
        return self._execute('input keyevent KEYCODE_WAKEUP') is not None
    
    def screen_on(self) -> bool:
        """
        Turn screen on
        
        Returns:
            True if successful, False otherwise
        """
        success = self._send_wakeup_keyevent()
        if success:
            self.unlock_device()
        return success
    
    def screen_off(self) -> bool:
        """
        Turn screen off/sleep
        
        Returns:
            True if successful, False otherwise
        """
        return self._execute('input keyevent KEYCODE_SLEEP') is not None
    
    def wake_device(self) -> bool:
        """
        Wake device (same as screen_on)
        
        Returns:
            True if successful, False otherwise
        """
        return self._send_wakeup_keyevent()
    
    def press_power(self) -> bool:
        """
        Press power button (toggles screen)
        
        Returns:
            True if successful, False otherwise
        """
        return self._execute('input keyevent KEYCODE_POWER') is not None
    
    def unlock_device(self) -> bool:
        """
        Unlock device (swipe up gesture)
        
        Returns:
            True if successful, False otherwise
        """
        return self._execute('input swipe 540 1500 540 500') is not None
    
    def volume_up(self) -> bool:
        """
        Increase volume
        
        Returns:
            True if successful, False otherwise
        """
        return self._execute('input keyevent KEYCODE_VOLUME_UP') is not None
    
    def volume_down(self) -> bool:
        """
        Decrease volume
        
        Returns:
            True if successful, False otherwise
        """
        return self._execute('input keyevent KEYCODE_VOLUME_DOWN') is not None
    
    def set_brightness(self, level: int) -> bool:
        """
        Set screen brightness level (0-255)
        
        Args:
            level: Brightness level (0-255)
            
        Returns:
            True if successful, False otherwise
        """
        # Clamp level to valid range
        level = max(0, min(255, level))
        return self._execute(f'settings put system screen_brightness {level}') is not None
    
    def get_brightness(self) -> Optional[int]:
        """
        Get current screen brightness level
        
        Returns:
            Brightness level (0-255) or None if failed
        """
        result = self._execute('settings get system screen_brightness')
        if result:
            try:
                return int(result.strip())
            except ValueError:
                pass
        return None
    
    def get_screen_state(self) -> Optional[bool]:
        """
        Check if screen is on
        
        Returns:
            True if screen is on, False if off, None if unknown
        """
        result = self._execute('dumpsys power | grep "mHoldingDisplaySuspendBlocker"')
        if result:
            return 'true' in result.lower()
        return None
    
    def execute_custom_command(self, command: str) -> Optional[str]:
        """
        Execute custom ADB shell command
        
        Args:
            command: Shell command to execute
            
        Returns:
            Command output or None if failed
        """
        return self._execute(command)
    
    def _execute(self, command: str, silent: bool = False) -> Optional[str]:
        """
        Execute ADB shell command
        
        Args:
            command: Shell command to execute
            silent: If True, suppress error messages
            
        Returns:
            Command output or None if failed
        """
        try:
            cmd = ['adb']
            if self.device_id:
                cmd.extend(['-s', self.device_id])
            cmd.extend(['shell', command])
            
            result = subprocess.run(cmd, 
                                  capture_output=True, 
                                  text=True,
                                  timeout=10)
            
            if result.returncode == 0:
                return result.stdout.strip()
            elif not silent:
                print(f"Command failed: {result.stderr}")
            return None
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            if not silent:
                print(f"Error executing command: {e}")
            return None
